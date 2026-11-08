#!/usr/bin/env python3
"""Draw a livery template (the UV1 layout of a car's livery-layer materials).

Usage:
    py -3 livery_template.py <model.yft.xml> [-o out/prefix] [--size 2048]
                             [--format png|svg|both] [--lod high|med|low]
                             [--checker] [--json]

Input: a CodeWalker or Sollumz XML export of the car (.yft.xml; .ydr.xml also
works). In CodeWalker: RPF Explorer / Folder, right-click the .yft > Export XML.

Output (standard library only, nothing is installed, the input is only read):
- <prefix>_template.png / .svg: every triangle of the materials that have a
  livery sampler (DiffuseSampler2 = livery, DiffuseSampler3 = roof livery
  vehicle_paint3_lvr), filled by side: red = driver side (x < 0, left),
  blue = passenger side (x > 0), green = centre (roof, hood, bumpers).
  Big islands get a number, the bone name, a yellow arrow to the car's front
  (+Y) and a white arrow to "up" (+Z) on vertical panels, so you can see where
  text must be rotated. Hidden helper layer: put it under your design, never
  export it into the livery.
- <prefix>_checker.png (--checker): an orientation test texture. Convert it to
  DDS, put it in as the livery (_sign_1 or the livery yft texture) and look at
  the car: letters that read backwards = mirrored island, upside down = the
  island is rotated; every yellow arrow must point to the car's front.
- A report (Chinese): materials and texture names, islands per side, which
  big islands are rotated or mirrored, islands that share the same texture
  pixels, UVs outside 0..1, texel density (px/cm) at 1024/2048/4096, and
  whether the Medium/Low LODs still carry the livery layer.

GTA axes: +Y = front, +Z = up, x < 0 = driver (left) side (door_dside_f
x = -0.93 on vanilla polgauntlet). UV1 = TexCoord1 = Sollumz "UVMap 1".
"""
import argparse
import json
import math
import os
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

LIVERY_SAMPLERS = ('DiffuseSampler2', 'DiffuseSampler3')
SHADER_NAMES = [
    'vehicle_paint1', 'vehicle_paint1_enveff', 'vehicle_paint2', 'vehicle_paint2_enveff',
    'vehicle_paint3', 'vehicle_paint3_enveff', 'vehicle_paint3_lvr', 'vehicle_paint4',
    'vehicle_paint4_enveff', 'vehicle_paint4_emissive', 'vehicle_paint5_enveff', 'vehicle_paint6',
    'vehicle_paint6_enveff', 'vehicle_paint7', 'vehicle_paint7_enveff', 'vehicle_paint8',
    'vehicle_paint9', 'vehicle_mesh', 'vehicle_mesh_enveff', 'vehicle_shuts', 'vehicle_badges',
    'vehicle_decal', 'vehicle_decal2', 'vehicle_generic', 'vehicle_interior', 'vehicle_interior2',
]
SIDE_X = 0.15          # |mean x| below this = centre panel
COLORS = {'L': (221, 51, 51), 'R': (51, 102, 255), 'C': (34, 170, 34)}
SIDE_ZH = {'L': '驾驶座侧(左)', 'R': '副驾侧(右)', 'C': '中间'}
LOD_TAGS = {'high': 'DrawableModelsHigh', 'med': 'DrawableModelsMedium', 'low': 'DrawableModelsLow',
            'vlow': 'DrawableModelsVeryLow'}


def joaat(text):
    h = 0
    for c in text.lower().encode():
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= h >> 6
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= h >> 11
    return (h + (h << 15)) & 0xFFFFFFFF


HASH_NAMES = {f'hash_{joaat(n):08X}': n for n in SHADER_NAMES}


def shader_name(raw):
    raw = (raw or '').strip()
    return HASH_NAMES.get(raw.upper().replace('HASH_', 'hash_'), raw)


# ---------------------------------------------------------------- XML reading

def _floats(text):
    return [float(x) for x in text.split()]


def read_model(path, lods=('high', 'med', 'low')):
    """Return dict(shaders=[...], bones=[...], lods={lod: [geometry, ...]}).

    geometry = dict(shader=int, verts=[(pos, normal|None, uv1|None, bone)], tris=[(a, b, c)]).
    Streams the XML (iterparse) so 100 MB exports stay manageable; only the main
    drawable is read (fragment children / cloth are skipped)."""
    want = {LOD_TAGS[k]: k for k in lods}
    shaders, bones = [], []
    out = {k: [] for k in lods}
    stack = []
    root_tag = None
    for event, el in ET.iterparse(path, events=('start', 'end')):
        if event == 'start':
            stack.append(el.tag)
            if root_tag is None:
                root_tag = el.tag
            continue
        depth = len(stack)
        main = (root_tag == 'Drawable' and depth >= 1) or (stack[:2] == ['Fragment', 'Drawable'])
        top = 1 if root_tag == 'Drawable' else 2       # depth of the main <Drawable>
        if main and el.tag == 'ShaderGroup' and depth == top + 1:
            for s in el.findall('Shaders/Item'):
                samplers = {}
                for p in s.findall('Parameters/Item'):
                    if p.get('type') == 'Texture':
                        samplers[p.get('name')] = (p.findtext('Name') or '').strip()
                shaders.append({'name': shader_name(s.findtext('Name')), 'samplers': samplers})
            el.clear()
        elif main and el.tag == 'Skeleton' and depth == top + 1:
            bones = [(b.findtext('Name') or '').strip() for b in el.findall('Bones/Item')]
            el.clear()
        elif main and el.tag == 'Item' and depth == top + 4 and stack[top] in want and stack[top + 2] == 'Geometries':
            g = _read_geometry(el, shaders)
            if g is not None:
                out[want[stack[top]]].append(g)
            el.clear()
        elif el.tag in ('Physics', 'Bounds') and depth == 2:
            el.clear()
        stack.pop()
    return {'shaders': shaders, 'bones': bones, 'lods': out}


def _read_geometry(el, shaders):
    try:
        si = int(el.find('ShaderIndex').get('value'))
    except (AttributeError, TypeError, ValueError):
        return None
    vb = el.find('VertexBuffer')
    if vb is None or vb.find('Layout') is None:
        return None
    cols = [c.tag for c in vb.find('Layout')]
    bone_ids = [int(x) for x in (el.findtext('BoneIDs') or '').replace(',', ' ').split()]
    has_uv1 = 'TexCoord1' in cols
    livery = si < len(shaders) and any(s in shaders[si]['samplers'] for s in LIVERY_SAMPLERS)
    g = {'shader': si, 'has_uv1': has_uv1, 'livery': livery, 'verts': [], 'tris': []}
    if not livery:
        return g                                   # only count it; don't keep vertices
    ip, inn, iuv, iw, ib = (cols.index(c) if c in cols else None for c in
                            ('Position', 'Normal', 'TexCoord1', 'BlendWeights', 'BlendIndices'))
    for line in (vb.findtext('Data') or vb.findtext('Data2') or '').strip().split('\n'):
        grp = line.strip().split('   ')
        if len(grp) != len(cols):
            continue
        pos = tuple(_floats(grp[ip])[:3])
        nrm = tuple(_floats(grp[inn])[:3]) if inn is not None else None
        uv = tuple(_floats(grp[iuv])[:2]) if iuv is not None else None
        bone = None
        if ib is not None:
            idx = [int(float(x)) for x in grp[ib].split()]
            wts = [float(x) for x in grp[iw].split()] if iw is not None else [1, 0, 0, 0]
            k = max(range(len(idx)), key=lambda i: wts[i] if i < len(wts) else 0)
            bone = bone_ids[idx[k]] if bone_ids and idx[k] < len(bone_ids) else idx[k]
        g['verts'].append((pos, nrm, uv, bone))
    idx = [int(x) for x in (el.findtext('IndexBuffer/Data') or '').split()]
    n = len(g['verts'])
    g['tris'] = [(idx[t], idx[t + 1], idx[t + 2]) for t in range(0, len(idx) - 2, 3)
                 if max(idx[t], idx[t + 1], idx[t + 2]) < n]
    return g


# ---------------------------------------------------------------- analysis

def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


class _UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        p = self.p
        p.setdefault(x, x)
        root = x
        while p[root] != root:
            root = p[root]
        while p[x] != root:
            p[x], x = root, p[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def samplers_present(model, lod='high'):
    found = []
    for g in model['lods'].get(lod, []):
        if g['livery']:
            for s in LIVERY_SAMPLERS:
                if s in model['shaders'][g['shader']]['samplers'] and s not in found:
                    found.append(s)
    return sorted(found)


def analyse(model, lod='high', sampler='DiffuseSampler2'):
    """Triangles + islands of one livery layer (DiffuseSampler2 = livery, DiffuseSampler3 = roof
    livery - a separate texture with its own UV1 layout) for one LOD."""
    shaders, bones = model['shaders'], model['bones']
    geoms = model['lods'].get(lod, [])
    tris, uf = [], _UF()
    materials = {}
    no_uv1 = 0
    for g in geoms:
        if not g['livery'] or sampler not in shaders[g['shader']]['samplers']:
            continue
        sh = shaders[g['shader']]
        key = (sh['name'], sh['samplers'].get(sampler) or '')
        m = materials.setdefault(key, {'shader': sh['name'], 'texture': key[1], 'sampler': sampler, 'triangles': 0})
        if not g['has_uv1']:
            no_uv1 += len(g['tris']) or 1
            continue
        vs = g['verts']
        for a, b, c in g['tris']:
            va, vb, vc = vs[a], vs[b], vs[c]
            if va[2] is None:
                continue
            side = _side(va, vb, vc)
            # Islands are split by side: a body unwrap that runs over the roof is one UV island,
            # but its left half, right half and roof need their own orientation hints.
            keys = [(side, round(v[2][0], 5), round(v[2][1], 5), round(v[0][0], 4), round(v[0][1], 4), round(v[0][2], 4))
                    for v in (va, vb, vc)]
            uf.union(keys[0], keys[1])
            uf.union(keys[0], keys[2])
            tris.append(_tri_info(va, vb, vc, keys[0], bones))
            m['triangles'] += 1
    groups = {}
    for t in tris:
        groups.setdefault(uf.find(t['key']), []).append(t)
    islands = [_island(ts) for ts in groups.values()]
    islands.sort(key=lambda i: -i['uv_area'])
    for n, isl in enumerate(islands, 1):
        isl['id'] = n
        for t in isl['tris']:
            t['island'] = n
    return {'materials': list(materials.values()), 'tris': tris, 'islands': islands, 'no_uv1': no_uv1}


def _side(va, vb, vc):
    """'L' / 'R' for panels facing the sides, 'C' for roof/hood/trunk/bumpers (facing up, down, front, back)."""
    xm = (va[0][0] + vb[0][0] + vc[0][0]) / 3
    n = _cross(_sub(vb[0], va[0]), _sub(vc[0], va[0]))
    ln = math.sqrt(_dot(n, n))
    if ln > 1e-12 and (abs(n[2]) / ln > 0.7 or abs(n[1]) > abs(n[0])):
        return 'C'
    return 'L' if xm < -SIDE_X else ('R' if xm > SIDE_X else 'C')


def _grad(p, uv, axis):
    """Direction in UV space in which world coordinate `axis` grows (per triangle)."""
    du1, dv1 = uv[1][0] - uv[0][0], uv[1][1] - uv[0][1]
    du2, dv2 = uv[2][0] - uv[0][0], uv[2][1] - uv[0][1]
    det = du1 * dv2 - dv1 * du2
    if abs(det) < 1e-14:
        return (0.0, 0.0)
    d1, d2 = p[1][axis] - p[0][axis], p[2][axis] - p[0][axis]
    return ((d1 * dv2 - d2 * dv1) / det, (du1 * d2 - du2 * d1) / det)


def _tri_info(va, vb, vc, key, bones):
    p = (va[0], vb[0], vc[0])
    uv = (va[2], vb[2], vc[2])
    nw = _cross(_sub(p[1], p[0]), _sub(p[2], p[0]))
    warea = 0.5 * math.sqrt(_dot(nw, nw))
    c = (uv[1][0] - uv[0][0]) * (uv[2][1] - uv[0][1]) - (uv[1][1] - uv[0][1]) * (uv[2][0] - uv[0][0])
    mirrored = None
    if va[1] is not None:
        n = tuple(va[1][i] + vb[1][i] + vc[1][i] for i in range(3))
        facing = _dot(nw, n)
        if abs(facing) > 1e-12 and abs(c) > 1e-14:
            # UV v runs down the image. Seen from outside, a non-mirrored island keeps the
            # winding with v flipped, so (uv cross) and (winding . normal) have opposite signs.
            mirrored = (c > 0) == (facing > 0)
    bone = va[3]
    bname = bones[bone] if isinstance(bone, int) and 0 <= bone < len(bones) else (str(bone) if bone is not None else '')
    nz = 0.0
    if warea > 0:
        nz = abs(nw[2]) / (2 * warea)
    return {'key': key, 'uv': uv, 'x': (p[0][0] + p[1][0] + p[2][0]) / 3, 'warea': warea, 'uvarea': abs(c) / 2,
            'mirrored': mirrored, 'gy': _grad(p, uv, 1), 'gz': _grad(p, uv, 2), 'nz': nz, 'bone': bname,
            'outside': any(not (-1e-4 <= q <= 1 + 1e-4) for xy in uv for q in xy)}


def _norm(v):
    ln = math.hypot(v[0], v[1])
    return (v[0] / ln, v[1] / ln) if ln > 1e-12 else (0.0, 0.0)


def _island(ts):
    wa = sum(t['warea'] for t in ts) or 1e-12
    x = sum(t['x'] * t['warea'] for t in ts) / wa
    side = ts[0]['key'][0]
    gy = [0.0, 0.0]
    gz = [0.0, 0.0]
    mir = known = 0.0
    bones = {}
    cu = cv = 0.0
    uva = 0.0
    for t in ts:
        ny, nz = _norm(t['gy']), _norm(t['gz'])
        gy[0] += ny[0] * t['warea']
        gy[1] += ny[1] * t['warea']
        gz[0] += nz[0] * t['warea']
        gz[1] += nz[1] * t['warea']
        if t['mirrored'] is not None:
            known += t['warea']
            mir += t['warea'] if t['mirrored'] else 0
        bones[t['bone']] = bones.get(t['bone'], 0) + t['warea']
        a = t['uvarea']
        uva += a
        cu += a * sum(q[0] for q in t['uv']) / 3
        cv += a * sum(q[1] for q in t['uv']) / 3
    us = [q[0] for t in ts for q in t['uv']]
    vs = [q[1] for t in ts for q in t['uv']]
    if uva > 0:
        centre = (cu / uva, cv / uva)
    else:
        centre = ((min(us) + max(us)) / 2, (min(vs) + max(vs)) / 2)
    horizontal = sum(t['nz'] * t['warea'] for t in ts) / wa > 0.7
    fwd, up = _norm(gy), _norm(gz)
    return {'tris': ts, 'side': side, 'mean_x': x, 'world_area': wa if wa > 1e-11 else 0.0, 'uv_area': uva,
            'centre': centre, 'bbox': (min(us), min(vs), max(us), max(vs)),
            'front': fwd, 'up': None if horizontal else up, 'horizontal': horizontal,
            'mirrored': (mir / known > 0.5) if known else None,
            'bone': max(bones, key=bones.get) if bones else '', 'outside': sum(1 for t in ts if t['outside'])}


def rotation_hint(vec):
    """Angle (deg) of a UV-space direction relative to 'image up', snapped to 0/90/180/-90."""
    if vec is None or vec == (0.0, 0.0):
        return None
    ang = math.degrees(math.atan2(vec[0], -vec[1]))
    snap = min((0, 90, 180, -90, -180), key=lambda a: abs(ang - a))
    return 180 if snap == -180 else snap


def overlaps(islands, grid=512, min_share=0.0005):
    """Groups of islands that use the same texture pixels (shared / stacked UVs).

    Returns [(ids, sides, left_right_mirror_differs)] - one entry per group, tiny islands ignored."""
    big = [i for i in islands if i['uv_area'] >= min_share]
    cells = []
    for isl in big:
        s = set()
        for t in isl['tris']:
            _cover(s, [(u * grid, v * grid) for u, v in t['uv']], grid)
        cells.append(s)
    uf = _UF()
    for i in range(len(big)):
        for j in range(i + 1, len(big)):
            if not cells[i] or not cells[j]:
                continue
            if len(cells[i] & cells[j]) > 0.3 * min(len(cells[i]), len(cells[j])):
                uf.union(big[i]['id'], big[j]['id'])
    groups = {}
    for isl in big:
        if isl['id'] in uf.p:
            groups.setdefault(uf.find(isl['id']), []).append(isl)
    return [(sorted(i['id'] for i in g), ''.join(sorted({i['side'] for i in g})),
             len({bool(i['mirrored']) for i in g if i['side'] in 'LR'}) > 1)
            for g in groups.values() if len(g) > 1]


def _cover(s, pts, grid):
    ys = [p[1] for p in pts]
    for y in range(max(0, int(min(ys))), min(grid, int(max(ys)) + 1)):
        xs = _span(pts, y + 0.5)
        if xs:
            for x in range(max(0, int(xs[0])), min(grid, int(xs[1]) + 1)):
                s.add((x, y))


def _span(pts, yc):
    xs = []
    for i in range(3):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % 3]
        if (y0 <= yc < y1) or (y1 <= yc < y0):
            xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
    return (min(xs), max(xs)) if xs else None


def density(tris):
    """Texels per cm at 1024/2048/4096 for a set of triangles."""
    wa = sum(t['warea'] for t in tris)
    ua = sum(t['uvarea'] for t in tris)
    if wa <= 0 or ua <= 0:
        return None
    k = math.sqrt(ua / wa) / 100.0
    return {'world_m2': wa, 'uv_share': ua, 'px_per_cm_per_texel_size': k, 1024: 1024 * k, 2048: 2048 * k, 4096: 4096 * k}


# ---------------------------------------------------------------- raster output (stdlib PNG)

FONT = {
    '0': '01110 10001 10011 10101 11001 10001 01110', '1': '00100 01100 00100 00100 00100 00100 01110',
    '2': '01110 10001 00001 00010 00100 01000 11111', '3': '11111 00010 00100 00010 00001 10001 01110',
    '4': '00010 00110 01010 10010 11111 00010 00010', '5': '11111 10000 11110 00001 00001 10001 01110',
    '6': '00110 01000 10000 11110 10001 10001 01110', '7': '11111 00001 00010 00100 01000 01000 01000',
    '8': '01110 10001 10001 01110 10001 10001 01110', '9': '01110 10001 10001 01111 00001 00010 01100',
    'A': '01110 10001 10001 11111 10001 10001 10001', 'B': '11110 10001 10001 11110 10001 10001 11110',
    'C': '01110 10001 10000 10000 10000 10001 01110', 'D': '11100 10010 10001 10001 10001 10010 11100',
    'E': '11111 10000 10000 11110 10000 10000 11111', 'F': '11111 10000 10000 11110 10000 10000 10000',
    'G': '01110 10001 10000 10111 10001 10001 01111', 'H': '10001 10001 10001 11111 10001 10001 10001',
    'I': '01110 00100 00100 00100 00100 00100 01110', 'J': '00111 00010 00010 00010 00010 10010 01100',
    'K': '10001 10010 10100 11000 10100 10010 10001', 'L': '10000 10000 10000 10000 10000 10000 11111',
    'M': '10001 11011 10101 10101 10001 10001 10001', 'N': '10001 10001 11001 10101 10011 10001 10001',
    'O': '01110 10001 10001 10001 10001 10001 01110', 'P': '11110 10001 10001 11110 10000 10000 10000',
    'Q': '01110 10001 10001 10001 10101 10010 01101', 'R': '11110 10001 10001 11110 10100 10010 10001',
    'S': '01111 10000 10000 01110 00001 00001 11110', 'T': '11111 00100 00100 00100 00100 00100 00100',
    'U': '10001 10001 10001 10001 10001 10001 01110', 'V': '10001 10001 10001 10001 10001 01010 00100',
    'W': '10001 10001 10001 10101 10101 10101 01010', 'X': '10001 10001 01010 00100 01010 10001 10001',
    'Y': '10001 10001 01010 00100 00100 00100 00100', 'Z': '11111 00001 00010 00100 01000 10000 11111',
    '-': '00000 00000 00000 11111 00000 00000 00000', '_': '00000 00000 00000 00000 00000 00000 11111',
    '.': '00000 00000 00000 00000 00000 01100 01100', ':': '00000 01100 01100 00000 01100 01100 00000',
    '/': '00001 00010 00010 00100 01000 01000 10000', '>': '01000 00100 00010 00001 00010 00100 01000',
    '<': '00010 00100 01000 10000 01000 00100 00010', '#': '01010 01010 11111 01010 11111 01010 01010',
    '+': '00000 00100 00100 11111 00100 00100 00000', ' ': '00000 00000 00000 00000 00000 00000 00000',
}


class Canvas:
    def __init__(self, w, h, bg=(34, 34, 34)):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def put(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(col)

    def rect(self, x0, y0, x1, y1, col):
        x0, x1 = max(0, x0), min(self.w, x1)
        if x1 <= x0:
            return
        row = bytes(col) * (x1 - x0)
        for y in range(max(0, y0), min(self.h, y1)):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def tri(self, pts, col):
        ys = [p[1] for p in pts]
        for y in range(max(0, math.ceil(min(ys) - 0.5)), min(self.h, math.floor(max(ys) - 0.5) + 1)):
            xs = _span(pts, y + 0.5)
            if not xs:
                continue
            x0, x1 = max(0, math.ceil(xs[0] - 0.5)), min(self.w - 1, math.floor(xs[1] - 0.5))
            if x1 >= x0:
                i = (y * self.w + x0) * 3
                self.px[i:i + (x1 - x0 + 1) * 3] = bytes(col) * (x1 - x0 + 1)

    def line(self, x0, y0, x1, y1, col, width=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        r = width // 2
        for k in range(n + 1):
            t = k / n
            x, y = int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))
            if r:
                self.rect(x - r, y - r, x + r + 1, y + r + 1, col)
            else:
                self.put(x, y, col)

    def arrow(self, x, y, d, length, col, width=1):
        ex, ey = x + d[0] * length, y + d[1] * length
        self.line(x, y, ex, ey, col, width)
        for s in (0.5, -0.5):
            c, sn = math.cos(math.pi - s), math.sin(math.pi - s)
            hx, hy = d[0] * c - d[1] * sn, d[0] * sn + d[1] * c
            self.line(ex, ey, ex + hx * length * 0.35, ey + hy * length * 0.35, col, width)

    def text(self, x, y, s, col, scale=1, shadow=None):
        if shadow:
            self.text(x + scale, y + scale, s, shadow, scale)
        for ch in s.upper():
            g = FONT.get(ch, FONT[' ']).split()
            for gy, row in enumerate(g):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        self.rect(x + gx * scale, y + gy * scale, x + (gx + 1) * scale, y + (gy + 1) * scale, col)
            x += 6 * scale

    def save_png(self, path):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * stride:(y + 1) * stride]

        def chunk(tag, data):
            return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        with open(path, 'wb') as fh:
            fh.write(b'\x89PNG\r\n\x1a\n')
            fh.write(chunk(b'IHDR', struct.pack('>IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0)))
            fh.write(chunk(b'IDAT', zlib.compress(bytes(raw), 6)))
            fh.write(chunk(b'IEND', b''))


def _mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def _labelled(res, size, min_share):
    return [i for i in res['islands'] if i['uv_area'] >= min_share and i['uv_area'] * size * size >= 900]


def render_png(res, size, path, min_share=0.002):
    bg = (34, 34, 34)
    cv = Canvas(size, size, bg)
    for t in res['tris']:
        isl = res['islands'][t['island'] - 1]
        cv.tri([(u * size, v * size) for u, v in t['uv']], _mix(bg, COLORS[isl['side']], 0.45))
    edge = (235, 235, 235)
    seen = set()
    for t in res['tris']:
        for i in range(3):
            a, b = t['uv'][i], t['uv'][(i + 1) % 3]
            k = (a, b) if a < b else (b, a)
            if k in seen:
                continue
            seen.add(k)
            cv.line(a[0] * size, a[1] * size, b[0] * size, b[1] * size, edge)
    sc = max(1, size // 1024)
    for isl in _labelled(res, size, min_share):
        x, y = isl['centre'][0] * size, isl['centre'][1] * size
        ln = max(18, min(90, math.sqrt(isl['uv_area']) * size * 0.25))
        if isl['front'] != (0.0, 0.0):
            cv.arrow(x, y, isl['front'], ln, (255, 210, 0), 1 + sc)
        if isl['up']:
            cv.arrow(x, y, isl['up'], ln * 0.7, (255, 255, 255), sc)
        label = f"{isl['id']} {isl['side']}" + (' M' if isl['mirrored'] else '')
        cv.text(int(x + 4), int(y + 4), label, (255, 255, 255), sc * 2, shadow=(0, 0, 0))
        if isl['bone']:
            cv.text(int(x + 4), int(y + 4 + 18 * sc), isl['bone'][:22], (200, 200, 200), sc, shadow=(0, 0, 0))
    _legend_png(cv, sc)
    cv.save_png(path)


def _legend_png(cv, sc):
    y = 6 * sc
    for side, txt in (('L', 'L DRIVER SIDE  X<0'), ('R', 'R PASSENGER SIDE  X>0'), ('C', 'C CENTRE')):
        cv.rect(6 * sc, y, 16 * sc, y + 8 * sc, COLORS[side])
        cv.text(20 * sc, y, txt, (255, 255, 255), sc, shadow=(0, 0, 0))
        y += 11 * sc
    cv.line(6 * sc, y + 4 * sc, 20 * sc, y + 4 * sc, (255, 210, 0), sc + 1)
    cv.text(24 * sc, y, 'YELLOW = TO CAR FRONT  WHITE = UP  M = MIRRORED', (255, 255, 255), sc, shadow=(0, 0, 0))


def render_svg(res, size, path, min_share=0.002):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">',
           '<rect width="100%" height="100%" fill="#222"/>']
    for side in 'LRC':
        col = '#%02x%02x%02x' % COLORS[side]
        out.append(f'<g id="side_{side}" fill="{col}" fill-opacity="0.45" stroke="#eee" stroke-width="0.6">')
        for t in res['tris']:
            if res['islands'][t['island'] - 1]['side'] == side:
                out.append('<polygon points="%s"/>' % ' '.join(f'{u * size:.1f},{v * size:.1f}' for u, v in t['uv']))
        out.append('</g>')
    out.append('<g id="labels" font-family="sans-serif" font-size="%d" fill="#fff">' % max(12, size // 110))
    for isl in _labelled(res, size, min_share):
        x, y = isl['centre'][0] * size, isl['centre'][1] * size
        ln = max(18, min(90, math.sqrt(isl['uv_area']) * size * 0.25))
        for vec, col, k in ((isl['front'], '#ffd200', 1.0), (isl['up'], '#ffffff', 0.7)):
            if vec and vec != (0.0, 0.0):
                out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + vec[0] * ln * k:.1f}" y2="{y + vec[1] * ln * k:.1f}" '
                           f'stroke="{col}" stroke-width="3" marker-end="url(#a)"/>')
        txt = f"{isl['id']} {isl['side']}" + (' M' if isl['mirrored'] else '') + (f" {isl['bone']}" if isl['bone'] else '')
        out.append(f'<text x="{x + 4:.1f}" y="{y - 4:.1f}" stroke="#000" stroke-width="0.4">{txt}</text>')
    out.append('</g>')
    out.insert(1, '<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" '
                  'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')
    out.append('</svg>')
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out))


def render_checker(res, size, path):
    """Orientation test texture: grid with cell names, side colours, L/R letters and FRONT arrows.
    Letters are drawn upright in texture space, exactly like livery text you would type in a template."""
    cv = Canvas(size, size, (128, 128, 128))
    cells = 8
    step = size // cells
    for gy in range(cells):
        for gx in range(cells):
            cv.rect(gx * step, gy * step, (gx + 1) * step, (gy + 1) * step,
                    (200, 200, 200) if (gx + gy) % 2 == 0 else (90, 90, 90))
    for t in res['tris']:
        isl = res['islands'][t['island'] - 1]
        cv.tri([(u * size, v * size) for u, v in t['uv']], _mix((150, 150, 150), COLORS[isl['side']], 0.6))
    sc = max(1, size // 512)
    for gy in range(cells):
        for gx in range(cells):
            cv.text(gx * step + 3 * sc, gy * step + 3 * sc, f'{"ABCDEFGH"[gx]}{gy + 1}', (0, 0, 0), sc * 2)
    for isl in _labelled(res, size, 0.001):
        x, y = isl['centre'][0] * size, isl['centre'][1] * size
        span = min(isl['bbox'][2] - isl['bbox'][0], isl['bbox'][3] - isl['bbox'][1]) * size
        big = max(1, min(int(span / 18), size // 200))
        if isl['front'] != (0.0, 0.0):
            cv.arrow(x, y, isl['front'], max(12, span * 0.4), (255, 220, 0), max(2, big // 2))
        cv.text(int(x - 3 * big), int(y - 3.5 * big), {'L': 'L', 'R': 'R', 'C': 'C'}[isl['side']] + str(isl['id']),
                (255, 255, 255), big, shadow=(0, 0, 0))
    cv.save_png(path)


# ---------------------------------------------------------------- report

def report(path, model, res, lod_counts, size):
    lines = [f'模型: {os.path.basename(path)}  (LOD {res["lod"]})']
    if not res['materials']:
        lines.append('✘ 没找到有涂装层的材质（没有 DiffuseSampler2/3）。车身是 vehicle_paint1/2 或贴图直接画在车身上：'
                     '要做可换的涂装，先在 Blender 里把车身 UVMap 1 展开、材质改成 vehicle_paint3，再用 Sollumz 导出')
        return lines
    for m in res['materials']:
        lines.append(f'  材质 {m["shader"]}  {m["sampler"]} = {m["texture"] or "(空)"}  三角面 {m["triangles"]}')
    for o in res.get('other_samplers', []):
        lines.append(f'  另有 {o} 材质（{"车顶涂装，另一张贴图、另一套 UV" if o.endswith("3") else "车身涂装"}）：'
                     f'加 --sampler {o[-1]} 另出一张模板')
    if res['no_uv1']:
        lines.append(f'✘ 有涂装层材质的网格没有 TexCoord1（UVMap 1），约 {res["no_uv1"]} 个三角面：这些面上涂装不会显示')
    by_side = {s: [t for t in res['tris'] if res['islands'][t['island'] - 1]['side'] == s] for s in 'LRC'}
    lines.append(f'  UV 岛 {len(res["islands"])} 个：' + '，'.join(
        f'{SIDE_ZH[s]} {sum(1 for i in res["islands"] if i["side"] == s)}' for s in 'LRC'))
    for s in 'LRC':
        d = density(by_side[s])
        if d:
            share = f'{d["uv_share"] * 100:.1f}%' if d['uv_share'] <= 1 else '>100%（UV 超出 0..1，贴图平铺重复）'
            lines.append(f'  {SIDE_ZH[s]}: 车身 {d["world_m2"]:.2f} m²，占贴图 {share}，'
                         f'密度 1024={d[1024]:.1f} / 2048={d[2048]:.1f} / 4096={d[4096]:.1f} px/cm')
    d = density(res['tris'])
    if d:
        px = d['px_per_cm_per_texel_size'] * size
        lines.append(f'  在 {size} 贴图上：25 cm 高的 "POLICE" ≈ {25 * px:.0f} px，8 cm 的小字 ≈ {8 * px:.0f} px'
                     + ('（小字低于约 40 px 会被压缩和 mip 糊掉，放大字或别放在这块）' if 8 * px < 40 else ''))
    for isl in [i for i in res['islands'] if i['uv_area'] >= 0.002][:40]:
        notes = []
        if isl['horizontal'] and isl['uv_area'] < 0.01 and not isl['mirrored'] and not isl['outside']:
            continue
        rot = rotation_hint(isl['up'])
        if rot == 180:
            notes.append('字要转 180°（这块在贴图里是倒的）')
        elif rot == 90:
            notes.append('字要顺时针转 90°')
        elif rot == -90:
            notes.append('字要逆时针转 90°')
        if isl['horizontal']:
            fr = rotation_hint(isl['front'])
            notes.append({0: '水平面，车头朝图上方', 180: '水平面，车头朝图下方', 90: '水平面，车头朝图右边',
                          -90: '水平面，车头朝图左边'}.get(fr, '水平面'))
        if isl['mirrored']:
            notes.append('镜像岛：正常打的字在车上会反过来')
        if isl['outside']:
            notes.append(f'{isl["outside"]} 个三角面的 UV 超出 0..1（贴图会重复，模板上看不到）')
        if notes:
            lines.append(f'  #{isl["id"]} {SIDE_ZH[isl["side"]]} {isl["bone"]}: ' + '；'.join(notes))
    mirrored = [i for i in res['islands'] if i['mirrored'] and i['uv_area'] >= 0.001]
    if mirrored:
        area = sum(i['world_area'] for i in mirrored) / (sum(i['world_area'] for i in res['islands']) or 1)
        lines.append(f'⚠ 镜像的 UV 岛 {len(mirrored)} 个（约占涂装面积 {area * 100:.0f}%）：模板上正着写的字在这些面上会左右反。'
                     '字要在这些岛上水平翻转，或在 Blender 里把岛翻过来重新导出')
    shown = {'warn': 0, 'lr': 0, 'info': 0}
    hidden = {'warn': 0, 'lr': 0, 'info': 0}
    for ids, sides, mirror_differs in res['overlaps']:
        names = '、'.join(f'#{i}' for i in ids[:8]) + ('…' if len(ids) > 8 else '')
        kind = ('warn' if mirror_differs else 'lr') if ('L' in sides and 'R' in sides) else 'info'
        if shown[kind] >= 3:
            hidden[kind] += 1
            continue
        shown[kind] += 1
        if kind == 'warn':
            lines.append(f'⚠ UV 岛 {names} 左右两侧共用同一块贴图像素，而且其中一侧是镜像：贴图上的字在那一侧会左右反。'
                         '这块只放没有字、左右对称的图形；要放字，得在 Blender 里把一侧的岛移开（或翻正）重新导出')
        elif kind == 'lr':
            lines.append(f'ℹ UV 岛 {names} 左右两侧共用同一块贴图像素（都没镜像）：字两边都读得正，但两边内容一定相同；'
                         '有方向的图形（箭头、斜条、往前的弧线）在一侧朝车头、另一侧会朝车尾')
        else:
            lines.append(f'ℹ UV 岛 {names}（{"/".join(SIDE_ZH[c] for c in sides)}）共用同一块贴图像素：'
                         '画在这里的东西会同时出现在这几块上（重复的小零件很常见）')
    for kind, n in hidden.items():
        if n:
            what = {'warn': '左右共用且一侧镜像', 'lr': '左右共用（没镜像）', 'info': '同侧/中间共用'}[kind]
            lines.append(f'  …另有 {n} 组「{what}」（--json 看全部）')
    outside = sum(i['outside'] for i in res['islands'])
    if outside:
        lines.append(f'⚠ {outside} 个三角面的 UV 超出 0..1：Blender Export UV Layout 也只画 0..1，这些面会重复用贴图别处的像素')
    if lod_counts:
        hi = lod_counts.get('high', 0)
        for k, n in lod_counts.items():
            if k != 'high' and hi and n == 0:
                lines.append(f'⚠ {k} LOD 有网格但没有涂装层材质：车开远一点涂装就消失。每个 LOD 的车身都要 vehicle_paint3/4 + UVMap 1')
    return lines


def main():
    ap = argparse.ArgumentParser(description='Draw a livery (UV1) template from a CodeWalker/Sollumz yft XML')
    ap.add_argument('xml')
    ap.add_argument('-o', '--out', help='output prefix (default: next to the XML)')
    ap.add_argument('--size', type=int, default=2048)
    ap.add_argument('--format', choices=('png', 'svg', 'both'), default='both')
    ap.add_argument('--lod', choices=('high', 'med', 'low'), default='high')
    ap.add_argument('--sampler', choices=('2', '3'), help='2 = livery (DiffuseSampler2, default), 3 = roof livery (DiffuseSampler3)')
    ap.add_argument('--checker', action='store_true', help='also write an orientation test texture')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if args.size < 64 or args.size > 8192:
        ap.error('--size must be 64..8192')
    model = read_model(args.xml)
    present = samplers_present(model, args.lod)
    sampler = 'DiffuseSampler' + args.sampler if args.sampler else (present[0] if present else 'DiffuseSampler2')
    res = analyse(model, args.lod, sampler)
    res['lod'] = args.lod
    res['other_samplers'] = [x for x in present if x != sampler]
    res['overlaps'] = overlaps(res['islands'])
    lod_counts = {k: sum(1 for g in v if g['livery']) for k, v in model['lods'].items() if v}
    prefix = args.out or os.path.splitext(os.path.splitext(args.xml)[0])[0]
    if sampler == 'DiffuseSampler3':
        prefix += '_roof'
    if os.path.dirname(prefix):
        os.makedirs(os.path.dirname(prefix), exist_ok=True)
    written = []
    if res['tris']:
        if args.format in ('png', 'both'):
            render_png(res, args.size, prefix + '_template.png')
            written.append(prefix + '_template.png')
        if args.format in ('svg', 'both'):
            render_svg(res, args.size, prefix + '_template.svg')
            written.append(prefix + '_template.svg')
        if args.checker:
            render_checker(res, args.size, prefix + '_checker.png')
            written.append(prefix + '_checker.png')
    if args.json:
        print(json.dumps({
            'materials': res['materials'], 'no_uv1': res['no_uv1'], 'lod_livery_geometries': lod_counts,
            'islands': [{k: v for k, v in i.items() if k != 'tris'} for i in res['islands']],
            'overlaps': res['overlaps'], 'density': density(res['tris']), 'written': written,
        }, ensure_ascii=False, indent=1, default=str))
    else:
        for line in report(args.xml, model, res, lod_counts, args.size):
            print(line)
        for w in written:
            print('写出:', w)
    sys.exit(0 if res['tris'] else 1)


if __name__ == '__main__':
    main()
