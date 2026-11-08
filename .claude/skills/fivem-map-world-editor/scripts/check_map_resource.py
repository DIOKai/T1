#!/usr/bin/env python3
"""Check FiveM outdoor map resources (ymap placements, vanilla overrides, collision, paths) - read-only.

Usage:
    py -3 -I check_map_resource.py <resource | folder of resources | XML export folder> [more]
        [--xml DIR] [--orig DIR] [--vanilla-list FILE] [--names FILE] [--json]

<path> may be one map resource, a whole server resources folder (cross-resource checks need the
other resources in the same run) or a folder of CodeWalker/Sollumz XML exports. Standard library
only; never writes. Exit code 1 when an error is found.

  --xml DIR           extra folder of CodeWalker/Sollumz XML (*.ymap.xml, *.ybn.xml, *.ydr.xml, *.ynd.xml,
                      *.ytyp.xml) - same as passing it as a path
  --orig DIR          untouched vanilla *.ymap.xml exports (user: vanilla_ref/<area>/ymap_xml, made with
                      ymap_xml.ps1 or CodeWalker RPF Explorer) -> diff mode (group D) against the edited
                      copies with the same names (XML found in the paths, else the compiled ymaps)
  --vanilla-list FILE file names that exist in the game, one per line or CSV first column (exact
                      vanilla-override and hei_ pairing instead of the name heuristic)
  --names FILE        extra names (one per line) to turn hash_XXXXXXXX back into readable names

Groups (see ../references/troubleshooting.md "checker"):
  A  resource / manifest: this_is_a_map, XML in stream, RSC7 / PSIN headers, 16/48 MiB (FXServer formula),
     ytyp never loaded, water / timecycle xml not loaded, HD txd, ynd / ynv names, ybn siblings
  B  across resources: same stream file in two resources, vanilla files each resource overrides,
     hei_ pairs, duplicate [category] folders, occluder overrides missing for an edited area
  C  ymaps (compiled binaries decoded directly, and XML): extents, CodeWalker CalcFlags, name,
     LOD links (CodeWalker YmapFile: parentIndex points into the PARENT ymap when entity flag 8 is set,
     when it is past the own list, or when the own entry is not a higher LOD level; else into the same
     ymap), LOD rank, index shifted by one, lodDist, duplicate entities, MLO instances, archetypes
  D  --orig diff: removed / buried / moved entities, orphaned children, shifted indices, stale
     numChildren, LOD left behind, occluders / collision / car generators / hei_ copy not edited
  E  other XML: ybn polygons per BVH (> 32767 failed Sollumz export on the user's server), BVH without
     composite flags, ydr |UV| > 50 (half floats), missing vertex colours, texture sizes, ynd area ids

Binary ymap layout (meta CMapData 0xD3593FA6, CEntityDef 0xCE501483, CMloInstanceDef 0x09CC28BE) was
read from CodeWalker MetaTypes and checked 2026-11-08 against CodeWalker XML of the same files
(kt1_lod, lpt_t3, kt1_occl_00, qbx_density car generators, lodlights / grass ymaps).
"""
import argparse
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'fivem-prop-creator', 'scripts'))
try:
    import rsc_probe  # noqa: E402  shared stdlib RSC7 reader (fivem-prop-creator)
except ImportError:   # pragma: no cover - XML and manifest checks still run
    rsc_probe = None

MIB = 1024 * 1024
RSC_EXT = ('.ymap', '.ytyp', '.ybn', '.ydr', '.ydd', '.yft', '.ytd', '.ynd', '.ynv')
MAP_EXT = ('.ymap', '.ytyp', '.ybn', '.ymt', '.ynd', '.ynv')
OWNER_ERROR_EXT = ('.ymap', '.ybn', '.ytyp', '.ynd', '.ynv')       # two owners = one silently loses
LEVELS = {0: 'HD', 1: 'LOD', 2: 'SLOD1', 3: 'SLOD2', 4: 'SLOD3', 5: 'ORPHANHD', 6: 'SLOD4'}
RANK = {'HD': 0, 'ORPHANHD': 0, 'LOD': 1, 'SLOD1': 2, 'SLOD2': 3, 'SLOD3': 4, 'SLOD4': 5}
META_CMAPDATA, META_CENTITYDEF, META_CMLOINSTANCEDEF = 0xD3593FA6, 0xCE501483, 0x09CC28BE
F_LOD_IN_PARENT = 8
BURIED_Z = -100.0
VANILLA_RE = re.compile(r'^(?:hei_|lr_)?(?:[a-z]{2,3}\d{1,2}_|(?:vb|sm|vw)_|(?:dist)?lodlights_|woccl_|minimap_)'
                        r'|^nodes\d+$|^navmesh\[', re.I)
# Rockstar asset prefixes (props, interiors, DLC packs) - heuristic, --vanilla-list is exact
VANILLA_PREFIXES = ('prop_', 'p_', 'v_', 'des_', 'apa_', 'bkr_', 'ba_', 'ex_', 'imp_', 'gr_', 'xm_', 'xm3_', 'ch_', 'h4_',
                    'tr_', 'sf_', 'sum_', 'lux_', 'ind_', 'csx_', 'xs_', 'stt_', 'sr_', 'as_', 'reh_', 'm23_', 'm24_',
                    'rc12b_', 'int_', 'mp2023_', 'mp2024_')
LEVEL_NAME = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}


# ---------------------------------------------------------------- helpers
def joaat(s):
    h = 0
    for c in s.lower().encode('utf-8'):
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= h >> 6
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= h >> 11
    return (h + (h << 15)) & 0xFFFFFFFF


def name_key(text):
    """CodeWalker XML writes unknown names as hash_XXXXXXXX; compare everything as joaat hashes."""
    t = (text or '').strip()
    if not t:
        return 0
    if t.lower().startswith('hash_'):
        try:
            return int(t[5:], 16)
        except ValueError:
            pass
    if t.isdigit():
        return int(t)
    return joaat(t)


class Names:
    def __init__(self):
        self.by_hash = {}

    def add(self, name):
        n = (name or '').strip()
        if n and not n.lower().startswith('hash_'):
            self.by_hash.setdefault(joaat(n), n.lower())

    def __call__(self, h):
        return self.by_hash.get(h, f'hash_{h:08X}') if h else '（空）'


def page_size(flags):
    """FXServer ConvertRSC7Size / CodeWalker RpfFile.GetSizeFromFlags."""
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


def head(path, n=16):
    try:
        with open(path, 'rb') as fh:
            return fh.read(n)
    except OSError:
        return b''


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def stem_of(path):
    b = os.path.basename(path).lower()
    for ext in ('.ymap.xml', '.ybn.xml', '.ydr.xml', '.ynd.xml', '.ytyp.xml', '.xml'):
        if b.endswith(ext):
            return b[:-len(ext)]
    return os.path.splitext(b)[0]


def base_stem(stem):
    """kt1_13 for hei_kt1_13 / hi@kt1_13_0 -> kt1_13_0."""
    s = stem.lower()
    for p in ('hi@', 'ma@'):
        if s.startswith(p):
            s = s[len(p):]
    return s[4:] if s.startswith('hei_') else s


def looks_vanilla(stem, vanilla_set=None):
    s = stem.lower()
    if vanilla_set is not None:
        return s in vanilla_set
    b = base_stem(s)
    return bool(VANILLA_RE.search(b)) or b.startswith(VANILLA_PREFIXES)


def area_prefix(stem):
    s = base_stem(stem)
    if s.startswith('lr_'):
        s = s[3:]
    return s.split('_')[0]


def in_stream(rel):
    return any(p.startswith('stream') for p in rel.lower().split('/')[:-1])


def enhanced(rel):
    return 'stream_enhanced' in rel.lower().split('/')


def vec_xml(el, tag):
    c = el.find(tag)
    if c is None:
        return None
    try:
        return tuple(float(c.get(k, 0)) for k in 'xyz')
    except ValueError:
        return None


def ival(el, tag, default=0):
    c = el.find(tag)
    if c is None:
        return default
    v = c.get('value', c.text)
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def fval(el, tag, default=0.0):
    c = el.find(tag)
    if c is None:
        return default
    try:
        return float(c.get('value', c.text))
    except (TypeError, ValueError):
        return default


def count_items(el, path):
    c = el.find(path)
    return len(list(c)) if c is not None else 0


def dist3(a, b):
    return sum((u - v) ** 2 for u, v in zip(a, b)) ** 0.5


def overlap2d(a_min, a_max, b_min, b_max):
    return a_min[0] <= b_max[0] and b_min[0] <= a_max[0] and a_min[1] <= b_max[1] and b_min[1] <= a_max[1]


# ---------------------------------------------------------------- ymap model
class Ent:
    __slots__ = ('arch', 'flags', 'guid', 'pos', 'pidx', 'lod', 'child_lod', 'level', 'nch', 'mlo', 'idx')

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))


class Ymap:
    def __init__(self, path, rel, resource, source):
        self.path, self.rel, self.resource, self.source = path, rel, resource, source
        self.stem = stem_of(path)
        self.key = joaat(self.stem)
        self.name_hash = self.parent = self.flags = self.cflags = 0
        self.smin = self.smax = self.emin = self.emax = (0.0, 0.0, 0.0)
        self.ents = []
        self.cargens = []          # positions
        self.tcboxes = []          # (min, max) - XML only
        self.n = dict(box=0, model=0, cargen=0, tc=0, grass=0, phys=0, lodlights=0, distlights=0)

    def has_content(self):
        return bool(self.ents) or any(self.n.values())


def read_ymap_bin(path):
    """Decode a compiled (RSC7 meta) ymap. Raises on anything unexpected."""
    res = rsc_probe.Resource.load(path)
    d = res.d
    if res.u32(0x10) != 0x50524430:
        raise ValueError('not a meta resource')
    n_blocks = struct.unpack_from('<h', d, 0x4C)[0]
    base = res.at(res.u64(0x30))
    blocks = [struct.unpack_from('<IiQ', d, base + 16 * i) for i in range(n_blocks)]
    root = res.u32(0x1C)
    if not (1 <= root <= len(blocks)) or blocks[root - 1][0] != META_CMAPDATA:
        raise ValueError('root block is not CMapData')

    def block_off(ptr):
        bi, off = (ptr & 0xFFF) - 1, (ptr >> 12) & 0xFFFFF
        if not (0 <= bi < len(blocks)):
            raise ValueError('bad meta pointer')
        return res.at(blocks[bi][2]) + off, blocks[bi][0]

    m = res.at(blocks[root - 1][2])
    out = {'name': res.u32(m + 8), 'parent': res.u32(m + 12), 'flags': res.u32(m + 16), 'cflags': res.u32(m + 20),
           'smin': struct.unpack_from('<3f', d, m + 32), 'smax': struct.unpack_from('<3f', d, m + 48),
           'emin': struct.unpack_from('<3f', d, m + 64), 'emax': struct.unpack_from('<3f', d, m + 80), 'ents': [],
           'cargens': []}
    cnt = lambda o: res.u16(m + o + 8) if res.u32(m + o) else 0   # noqa: E731  Array_Structure count
    out['n'] = dict(box=cnt(128), model=cnt(144), phys=cnt(160), grass=cnt(208), tc=cnt(224), cargen=cnt(240),
                    lodlights=cnt(264), distlights=cnt(400))
    ptr, n = res.u32(m + 96), cnt(96)
    if ptr and n:
        arr, _ = block_off(ptr)
        for i in range(n):
            eo, sh = block_off(res.u32(arr + 8 * i))
            if sh not in (META_CENTITYDEF, META_CMLOINSTANCEDEF):
                continue
            out['ents'].append(Ent(arch=res.u32(eo + 8), flags=res.u32(eo + 12), guid=res.u32(eo + 16),
                                   pos=struct.unpack_from('<3f', d, eo + 32), pidx=struct.unpack_from('<i', d, eo + 72)[0],
                                   lod=res.f32(eo + 76), child_lod=res.f32(eo + 80), level=LEVELS.get(res.u32(eo + 84), '?'),
                                   nch=res.u32(eo + 88), mlo=sh == META_CMLOINSTANCEDEF, idx=i))
    if out['n']['cargen']:
        o, _ = block_off(res.u32(m + 240))
        out['cargens'] = [struct.unpack_from('<3f', d, o + 80 * k + 16) for k in range(out['n']['cargen'])]
    return out


def read_ymap_xml(root):
    ents = []
    for i, e in enumerate(list(root.find('entities') if root.find('entities') is not None else [])):
        lvl = (e.findtext('lodLevel') or '').strip().upper().replace('LODTYPES_DEPTH_', '')
        ents.append(Ent(arch=name_key(e.findtext('archetypeName')), flags=ival(e, 'flags'), guid=ival(e, 'guid'),
                        pos=vec_xml(e, 'position') or (0.0, 0.0, 0.0), pidx=ival(e, 'parentIndex', -1),
                        lod=fval(e, 'lodDist'), child_lod=fval(e, 'childLodDist'), level=lvl or '?',
                        nch=ival(e, 'numChildren'), mlo=e.get('type') == 'CMloInstanceDef', idx=i))
    cg = root.find('carGenerators')
    tcs = root.find('timeCycleModifiers')
    return {'name': name_key(root.findtext('name')), 'parent': name_key(root.findtext('parent')),
            'flags': ival(root, 'flags'), 'cflags': ival(root, 'contentFlags'),
            'smin': vec_xml(root, 'streamingExtentsMin') or (0.0,) * 3, 'smax': vec_xml(root, 'streamingExtentsMax') or (0.0,) * 3,
            'emin': vec_xml(root, 'entitiesExtentsMin') or (0.0,) * 3, 'emax': vec_xml(root, 'entitiesExtentsMax') or (0.0,) * 3,
            'ents': ents,
            'cargens': [vec_xml(c, 'position') for c in (cg if cg is not None else []) if vec_xml(c, 'position')],
            'tcboxes': [(vec_xml(t, 'minExtents'), vec_xml(t, 'maxExtents')) for t in (tcs if tcs is not None else [])
                        if vec_xml(t, 'minExtents') and vec_xml(t, 'maxExtents')],
            'n': dict(box=count_items(root, 'boxOccluders'), model=count_items(root, 'occludeModels'),
                      phys=count_items(root, 'physicsDictionaries'), grass=count_items(root, 'instancedData/GrassInstanceList'),
                      tc=count_items(root, 'timeCycleModifiers'), cargen=count_items(root, 'carGenerators'),
                      lodlights=count_items(root, 'LODLightsSOA/direction'),
                      distlights=count_items(root, 'DistantLODLightsSOA/position'))}


def fill(y, data):
    y.name_hash, y.parent, y.flags, y.cflags = data['name'], data['parent'], data['flags'], data['cflags']
    y.smin, y.smax, y.emin, y.emax = data['smin'], data['smax'], data['emin'], data['emax']
    y.ents, y.cargens, y.n = data['ents'], data['cargens'], data['n']
    y.tcboxes = data.get('tcboxes', [])
    return y


def resolve_parent(y, e, by_key):
    """Where does e.parentIndex point?  CodeWalker YmapFile: the entity is a 'root' whose parent lives in
    the PARENT ymap (CMapData.parent) when flag 8 'LOD in parent map' is set, when the index is past this
    ymap's own list, or when the entity at that index in this ymap is not a higher LOD level; otherwise
    the parent is in the same ymap.  Returns (kind, target ymap or parent hash, parent Ent or None) with
    kind 'none' | 'same' | 'parent' | 'missing' (parent ymap not in the set) | 'noparent' (no CMapData.parent).
    """
    if e.pidx < 0:
        return 'none', None, None
    if not (e.flags & F_LOD_IN_PARENT) and e.pidx < len(y.ents):
        p = y.ents[e.pidx]
        if p.level != 'ORPHANHD' and RANK.get(p.level, 0) > RANK.get(e.level, 0):
            return 'same', y, p
    if not y.parent:
        return 'noparent', None, None
    t = by_key.get(y.parent)
    if t is None:
        return 'missing', y.parent, None
    return 'parent', t, (t.ents[e.pidx] if e.pidx < len(t.ents) else None)


def calc_flags(y):
    """CodeWalker YmapFile.CalcFlags (flags bit 2, contentFlags bits 1..1024 except 512 critical)."""
    flags = cflags = 0
    for e in y.ents:
        lv = e.level
        if lv in ('HD', 'ORPHANHD'):
            cflags |= 1
        elif lv == 'LOD':
            cflags |= 2
            flags |= 2
        elif lv == 'SLOD1':
            cflags |= 16
            flags |= 2
        elif lv in ('SLOD2', 'SLOD3', 'SLOD4'):
            cflags |= 4 | 16
            flags |= 2
        if e.mlo:
            cflags |= 8
    if y.n['phys']:
        cflags |= 64
    if y.n['grass']:
        cflags |= 1024
    if y.n['lodlights']:
        cflags |= 128
    if y.n['distlights']:
        flags |= 2
        cflags |= 256
    if y.n['box'] or y.n['model']:
        cflags |= 32
    return flags, cflags


# ---------------------------------------------------------------- collection
class Resource:
    def __init__(self, root, loose=False):
        self.root, self.loose = root, loose
        self.name = os.path.basename(root)
        self.files, self.rels = [], []
        for r, dirs, fs in os.walk(root):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in fs:
                p = os.path.join(r, f)
                self.files.append(p)
                self.rels.append(os.path.relpath(p, root).replace(os.sep, '/'))
        self.manifest = ''
        for mn in ('fxmanifest.lua', '__resource.lua'):
            mp = os.path.join(root, mn)
            if os.path.isfile(mp):
                with open(mp, encoding='utf-8', errors='replace') as fh:
                    self.manifest = strip_lua_comments(fh.read())
                break

    def streamed(self):
        return [(f, r) for f, r in zip(self.files, self.rels) if in_stream(r)]


def find_resources(paths):
    found, loose = [], []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            loose.append(os.path.dirname(p))
            continue
        hit = False
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if 'fxmanifest.lua' in files or '__resource.lua' in files:
                found.append(root)
                hit = True
                dirs[:] = []
        if not hit:
            loose.append(p)
    roots = sorted(set(found))
    loose = [x for x in dict.fromkeys(loose) if not any(x == r or x.startswith(r + os.sep) for r in roots)]
    return [Resource(r) for r in roots] + [Resource(x, loose=True) for x in loose]


def load_list(path):
    out = set()
    with open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            t = re.split(r'[,;\t]', line.strip())[0].strip().strip('"').lower()
            if t:
                out.add(stem_of(t) if '.' in t else t)
    return out


# ---------------------------------------------------------------- checks
class Checker:
    def __init__(self, args_paths, xml_dirs=(), orig=None, vanilla=None, names_file=None):
        self.findings = []
        self.names = Names()
        self.vanilla = vanilla
        self.resources = find_resources(list(args_paths) + list(xml_dirs))
        self.orig_dir = orig
        self.bin_ymaps, self.xml_ymaps = [], []
        self.local_arch = {}       # resource name -> set of archetype hashes defined by its ytyps
        self.model_stems = {}      # resource name -> set of model stem hashes
        if names_file:
            for n in load_list(names_file):
                self.names.add(n)

    def add(self, level, code, where, msg):
        self.findings.append({'level': level, 'code': code, 'file': where, 'message': msg})

    def where(self, res, rel):
        return f'{res.name}/{rel}'

    # ---- A: resource / manifest
    def check_resource(self, res):
        man = res.manifest
        streamed = res.streamed()
        lows = [r.lower() for _, r in streamed]
        for f, r in zip(res.files, res.rels):
            self.names.add(stem_of(f))
        if not any(x.endswith(MAP_EXT + ('.ymf',)) for x in lows) and not any(
                re.search(r'(^|/)(water|timecycle)[^/]*\.xml$|\.(ymap|ybn|ytyp)\.xml$', r.lower()) for r in res.rels):
            return   # vehicles, clothing, texture packs: only the cross-resource checks look at them
        placed = ('.ymap', '.ybn', '.ynd', '.ynv')   # a spawn-only prop library (.ytyp only) does not need it
        if not res.loose and any(x.endswith(placed) for x in lows) and not re.search(r'\bthis_is_a_map\b', man):
            first = next(x for x in lows if x.endswith(placed))
            self.add('warn', 'NO_THIS_IS_A_MAP', res.name, f"stream 里有地图文件（{first} 等），fxmanifest 没写 this_is_a_map 'yes'。"
                     'Cfx 文档：它让资源载入时重载地图存储；只覆盖原版文件的资源没有它也常能用，但新 ymap 要加上')
        ymf = [x for x in lows if x.endswith('.ymf')]
        requests = {os.path.basename(p.replace('\\', '/')).lower().rsplit('.', 1)[0]
                    for t, p in re.findall(r"data_file\s*\(?\s*['\"]([A-Z0-9_]+)['\"]\s*\)?\s*\(?\s*['\"]([^'\"]+)['\"]", man)
                    if t == 'DLC_ITYP_REQUEST'}
        arch, models, mlo_ytyps = set(), set(), []
        arch_complete = True
        for f, r in streamed:
            low = os.path.basename(r).lower()
            where = self.where(res, r)
            st = stem_of(low)
            if low.endswith('.xml'):
                self.add('error', 'XML_IN_STREAM', where, 'XML 放在 stream 里不会被载入。用 CodeWalker RPF Explorer（Import XML）或 Sollumz 导出成二进制再放进去')
                continue
            h = head(f)
            if low.endswith('.ymf'):
                if h[:1] == b'<':
                    self.add('warn', 'YMF_IS_XML', where, '.ymf 是 XML 文本，不是编译好的 PSIN 文件（未验证 FiveM 能不能读文本 ymf）。在 CodeWalker 用 Manifest Generator 存成二进制')
                elif h[:4] not in (b'PSIN', b'FXAP'):
                    self.add('warn', 'NOT_RSC7', where, '.ymf 开头不是 PSIN，可能损坏')
                continue
            if not low.endswith(RSC_EXT):
                continue
            if h[:4] == b'FXAP':
                if low.endswith('.ytyp'):
                    arch_complete = False
                continue   # escrow: content unreadable, the gate reports ESCROWED
            if h[:4] not in (b'RSC7', b'RSC8') or len(h) < 16:
                if not enhanced(r):
                    self.add('warn', 'NOT_RSC7', where, '开头不是 RSC7，不像编译好的 GTA 文件（改了扩展名的 XML 或损坏）')
                continue
            v, p = struct.unpack_from('<II', h, 8)
            size, what = max((page_size(v), '虚拟'), (page_size(p), '物理（显存）'))
            if size > 48 * MIB:
                self.add('error', 'ASSET_OVER_48MIB', where, f'{what}内存 {size / MIB:.1f} MiB > 48 MiB，FXServer 说这样一定会出串流问题')
            elif size > 16 * MIB:
                self.add('warn', 'ASSET_OVER_16MIB', where, f'{what}内存 {size / MIB:.1f} MiB > 16 MiB（FXServer 警告线）')
            if low.endswith(('.ydr', '.ydd', '.yft')):
                models.add(joaat(st))
            if low.endswith('.ytyp') and rsc_probe is not None and h[:4] == b'RSC7':
                try:
                    info = rsc_probe.read_ytyp(f)
                    arch |= {a['name_hash'] for a in info['archetypes']}
                    if info['mlo']:
                        mlo_ytyps.append(st)
                    if not info['archetypes']:
                        arch_complete = False   # e.g. CTimeArchetypeDef (night-only emissive) - not decoded
                except Exception:   # noqa: BLE001 - unreadable ytyp is reported by the prop checker
                    arch_complete = False
                if st not in requests and not ymf and not enhanced(r) and not looks_vanilla(st, self.vanilla):
                    self.add('warn', 'YTYP_NOT_LOADED', where, f"自定义 ytyp '{st}' 没有 DLC_ITYP_REQUEST，资源里也没有 .ymf。"
                             'Cfx 文档：用 CodeWalker Tools > Manifest Generator 生成 _manifest.ymf（或给道具 ytyp 写 DLC_ITYP_REQUEST），否则 archetype 不载入、东西看不见')
            if low.endswith('.ymap'):
                self.load_bin_ymap(res, f, r)
            if low.endswith('.ynd'):
                m = re.fullmatch(r'nodes(\d+)', st)
                if not m or int(m.group(1)) >= 1024:
                    self.add('warn', 'YND_NAME', where, f"路径节点文件要叫 nodes<0-1023>.ynd（32×32 格，每格 512 m，从 -8192 起；CodeWalker YndFile），'{low}' 不会被当成哪一格")
            if low.endswith('.ynv') and not re.fullmatch(r'navmesh\[\d+\]\[\d+\]', st):
                self.add('info', 'YNV_NAME', where, f"原版 navmesh 文件名是 navmesh[X][Y].ynv（150 m 一格）；'{low}' 不是这个格式，确认它是覆盖哪一格")
        if mlo_ytyps:
            self.add('info', 'MLO_HERE', res.name, f"{len(mlo_ytyps)} 个 ytyp 里有 MLO（{', '.join(mlo_ytyps[:4])}）。室内规则（portal、_milo_ ymap、.ymf）用 fivem-mlo-housing 的 check_mlo_resource.py 检查")
        self.local_arch[res.name] = arch if arch_complete else None
        self.model_stems[res.name] = models
        # hd texture dictionaries
        hd = [x for x in lows if re.search(r'\+hi(dr|fr|dd)?\.ytd$', x)    # vanilla +hi dictionaries are bound already
              and not looks_vanilla(re.sub(r'\+hi(dr|fr|dd)?$', '', stem_of(x)), self.vanilla)]
        if hd:
            self.add('info', 'HD_TXD_PRESENT', res.name, f"有 HD 贴图字典（{os.path.basename(hd[0])} 等）。Sollumz 文档：自己新做的 +hi 字典要写进 _manifest.ymf 的 HDTxdBindingArray"
                     + ('' if ymf else '，这个资源没有 .ymf') + '；只是替换原版同名 +hi 字典的话不用')
        # water / timecycle xml
        all_low = [r.lower() for r in res.rels]
        lua = ''
        for f, r in zip(res.files, res.rels):
            if r.lower().endswith('.lua') and os.path.getsize(f) < 2 * MIB:
                with open(f, encoding='utf-8', errors='replace') as fh:
                    lua += fh.read()
        for r in all_low:
            b = os.path.basename(r)
            if b.endswith('.xml') and b.startswith('water') and not in_stream(r):
                if b not in man.lower() or 'loadwaterfrompath' not in lua.lower():
                    self.add('warn', 'WATER_XML_NOT_LOADED', self.where(res, r), "水的 xml 要写进 fxmanifest 的 files{}，再在 client 脚本里 LoadWaterFromPath('资源名', '文件名')（Cfx natives）；CodeWalker 和 Sollumz 都不能编辑水")
            if b.endswith('.xml') and b.startswith('timecycle') and 'TIMECYCLEMOD_FILE' not in man:
                self.add('warn', 'TIMECYCLE_NOT_DECLARED', self.where(res, r), "timecycle xml 要用 data_file 'TIMECYCLEMOD_FILE' 声明，ymap 里的 timecycle 方框才找得到这个 modifier")
        # ybn siblings for vanilla collision overrides
        ybn = {stem_of(r) for _, r in streamed if r.lower().endswith('.ybn')}
        for st in sorted(ybn):
            if st.startswith(('hi@', 'ma@')) or not looks_vanilla(st, self.vanilla):
                continue
            missing = [p + st for p in ('hi@', 'ma@') if p + st not in ybn]
            if missing:
                self.add('info', 'YBN_SIBLINGS', res.name, f"覆盖了原版碰撞 {st}.ybn，但没有 {', '.join(m + '.ybn' for m in missing)}。原版常有三份：普通、hi@（子弹）、ma@（程序生成草/垃圾），挖掉一块要三份一起改（原版没有那份就不用）")

    def load_bin_ymap(self, res, f, r):
        y = Ymap(f, self.where(res, r), res.name, 'bin')
        if rsc_probe is None:
            return
        try:
            fill(y, read_ymap_bin(f))
        except Exception as e:   # noqa: BLE001
            self.add('info', 'YMAP_UNREADABLE', y.rel, f'读不出这个 ymap 的内容（{e}），只做了文件检查')
            return
        if not enhanced(r):
            self.bin_ymaps.append(y)

    # ---- XML files (C input + E)
    def load_xml(self):
        for res in self.resources:
            for f, r in zip(res.files, res.rels):
                low = r.lower()
                if in_stream(r) or not low.endswith('.xml'):
                    continue
                kind = next((k for k in ('.ymap.xml', '.ytyp.xml', '.ybn.xml', '.ydr.xml', '.ynd.xml') if low.endswith(k)), None)
                if not kind:
                    continue
                try:
                    root = ET.parse(f).getroot()
                except (ET.ParseError, OSError) as e:
                    self.add('error', 'XML_INVALID', self.where(res, r), f'不是合法的 XML：{e}')
                    continue
                where = self.where(res, r)
                if kind == '.ymap.xml' and root.tag == 'CMapData':
                    y = fill(Ymap(f, where, res.name, 'xml'), read_ymap_xml(root))
                    self.names.add(root.findtext('name'))
                    self.names.add(root.findtext('parent'))
                    self.xml_ymaps.append(y)
                elif kind == '.ytyp.xml' and root.tag == 'CMapTypes':
                    archs = root.find('archetypes')
                    for a in (archs if archs is not None else []):
                        nm = a.findtext('name')
                        self.names.add(nm)
                        if self.local_arch.get(res.name, set()) is not None:
                            self.local_arch.setdefault(res.name, set()).add(name_key(nm))
                elif kind == '.ybn.xml':
                    self.check_ybn_xml(root, where)
                elif kind == '.ydr.xml':
                    self.check_ydr_xml(root, where)
                elif kind == '.ynd.xml':
                    self.check_ynd_xml(root, where, stem_of(f))

    def check_ybn_xml(self, root, where):
        bounds = root.find('Bounds')
        if bounds is None:
            return
        kids = list(bounds.find('Children')) if bounds.find('Children') is not None else []
        if bounds.get('type') == 'Composite' and not kids:
            self.add('warn', 'YBN_EMPTY', where, '碰撞 Composite 里没有任何子碰撞（用户在 La Puerta 把空的 ma@ 当成闪退嫌疑，未验证）。整块挖空时删掉这个 ybn 覆盖或留一小块')
        for i, b in enumerate([bounds] if bounds.get('type') != 'Composite' else kids):
            if b.get('type') in ('GeometryBVH', 'Geometry'):
                polys = b.find('Polygons')
                n = len(list(polys)) if polys is not None else 0
                if n > 32767:
                    self.add('warn', 'BVH_TOO_MANY_POLYS', where, f'第 {i} 个 {b.get("type")} 有 {n} 个多边形 > 32767。用户实测 37 292 个时 Sollumz 导出失败（官方没写上限）：拆成几个 BVH 或简化')
            if bounds.get('type') == 'Composite':
                f1 = (b.findtext('CompositeFlags1') or '').strip().upper()
                f2 = (b.findtext('CompositeFlags2') or '').strip().upper()
                if f1 in ('', 'NONE') and f2 in ('', 'NONE'):
                    self.add('error', 'BVH_NO_FLAGS', where, f'第 {i} 个子碰撞（{b.get("type")}）没有碰撞 flag，什么都会穿过去。Sollumz 文档："very common mistake" - 选中 BVH 套用 Flag Preset（General 等）')

    def check_ydr_xml(self, root, where):
        worst, has_colour, n_geo = 0.0, False, 0
        for vb in root.iter('VertexBuffer'):
            layout = vb.find('Layout')
            data = vb.find('Data')
            if data is None:
                data = vb.find('Data2')
            if layout is None or data is None or not (data.text or '').strip():
                continue
            n_geo += 1
            comps = [c.tag for c in layout]
            if any(c.startswith('Colour') for c in comps):
                has_colour = True
            tc = [i for i, c in enumerate(comps) if c.startswith('TexCoord')]
            if not tc:
                continue
            for line in data.text.strip().splitlines():
                parts = re.split(r'\s{3,}', line.strip())
                for i in tc:
                    if i < len(parts):
                        try:
                            worst = max([worst] + [abs(float(x)) for x in parts[i].split()])
                        except ValueError:
                            pass
        if worst > 50:
            self.add('warn', 'UV_TOO_LARGE', where, f'最大 |UV| = {worst:.0f} > 50。GTA 把 UV 存成半精度浮点，数值大了会一格一格跳（条纹、贴图糊掉）。每块面把 UV 移回 0 附近（用户的 center_uvs），用较小的重复次数')
        if n_geo and not has_colour:
            self.add('info', 'NO_VERTEX_COLOUR', where, 'Layout 里没有 Colour0。Sollumz FAQ：户外模型要刷顶点色（户外用红色），不然晚上会发粉红光')
        for t in root.iter('TextureDictionary'):
            for it in t:
                w, h = ival(it, 'Width'), ival(it, 'Height')
                nm = it.findtext('Name') or '?'
                if w and h and (w & (w - 1) or h & (h - 1) or max(w, h) > 2048):
                    self.add('warn', 'TEXTURE_SIZE', where, f"贴图 '{nm}' 是 {w}×{h}。Sollumz FAQ：用 2 的次方，建议最大 2048")

    def check_ynd_xml(self, root, where, stem):
        """CodeWalker YndFile XML (format from CodeWalker source, not checked on a real export)."""
        m = re.fullmatch(r'nodes(\d+)', stem)
        nodes = root.find('Nodes')
        if not m or nodes is None:
            return
        area = int(m.group(1))
        bad = 0
        for it in nodes:
            p = vec_xml(it, 'Position')
            aid = ival(it, 'AreaID', -1)
            if p is None:
                continue
            cx, cy = int((p[0] + 8192) // 512), int((p[1] + 8192) // 512)
            if aid != area or cy * 32 + cx != area:
                bad += 1
        if bad:
            self.add('warn', 'YND_AREA_MISMATCH', where, f'{bad} 个节点的 AreaID 或位置不属于 nodes{area}（第 y*32+x 格，512 m，从 -8192 起）。在 CodeWalker 里移动节点跨格后要让它重新分区再存（格式未用真文件验证）')

    # ---- C: ymaps
    def check_ymap_set(self, ymaps, label):
        by_key = {}
        for y in ymaps:
            by_key.setdefault(y.key, y)
        dup_ent = {}
        missing_parents = {}
        empty_names, mlo_maps, no_parent_flag8 = {}, {}, {}
        for y in ymaps:
            self.names.add(y.stem)
            vanilla = looks_vanilla(y.stem, self.vanilla)
            # extents
            if y.has_content() and all(v == 0 for v in y.smin + y.smax):
                self.add('error', 'ZERO_EXTENTS', y.rel, 'streaming extents 全是 0：没有按 Calculate Extents，游戏里 ymap 不会载入（东西不见）。CodeWalker 选中 ymap 按 Calculate Extents + Calculate All Flags 再存')
            elif y.ents:
                live = [e for e in y.ents if e.pos[2] > BURIED_Z and not e.mlo and RANK.get(e.level, 0) == 0]
                # the pivot may sit outside the model's box; 50 m tolerance catches only stale extents
                out = [e for e in live if any(not (y.emin[k] - 50 <= e.pos[k] <= y.emax[k] + 50) for k in range(3))]
                if out:
                    self.add('warn', 'EXTENTS_DONT_COVER', y.rel, f'{len(out)} 个 HD 实体离 entitiesExtents 超过 50 m（移动后没重算）。重新 Calculate Extents，不然靠近时可能不载入')
                if any(not (y.smin[k] - 1 <= y.emin[k] and y.emax[k] <= y.smax[k] + 1) for k in range(3)):
                    self.add('warn', 'EXTENTS_DONT_COVER', y.rel, 'entitiesExtents 超出 streamingExtents，重新 Calculate Extents')
                hd_only = all(RANK.get(e.level, 0) == 0 for e in y.ents)
                width = max(y.smax[0] - y.smin[0], y.smax[1] - y.smin[1])
                has_origin = y.smin[0] <= 0 <= y.smax[0] and y.smin[1] <= 0 <= y.smax[1]
                ent_origin = y.emin[0] <= 0 <= y.emax[0] and y.emin[1] <= 0 <= y.emax[1]
                if hd_only and not vanilla and (width > 4000 or (has_origin and not ent_origin and width > 1000)):
                    self.add('warn', 'HUGE_STREAMING_EXTENTS', y.rel, f'streaming 范围宽 {width:.0f} m' + ('，包含地图原点 (0,0)' if has_origin and not ent_origin else '')
                             + '：lodDist 太大（CalcExtents 会按 lodDist 往外扩），整个地图载入时都会先读它。用户 La Puerta 的 lodDist 1500 就是这样；单栋楼用较小的 lodDist + 模型自己的 LOD')
            # flags
            want_f, want_c = calc_flags(y)
            if (y.flags & 2) != want_f or (y.cflags & ~512) != want_c:
                missing = (want_f & ~y.flags) or (want_c & ~y.cflags)
                self.add('warn' if missing else 'info', 'FLAGS_MISMATCH', y.rel, f'flags={y.flags} contentFlags={y.cflags}，按内容应该是 flags={want_f | (y.flags & 1)} contentFlags={want_c | (y.cflags & 512)}（CodeWalker CalcFlags）。按 Calculate All Flags 再存'
                         + ('；它会清掉 scripted（flags 1）和 critical（512），存完要改回来' if (y.flags & 1) or (y.cflags & 512) else ''))
            if y.name_hash != y.key:
                if y.name_hash == 0:
                    empty_names.setdefault(y.resource, []).append(y.stem)
                else:
                    self.add('warn', 'YMAP_NAME_MISMATCH', y.rel, f"CMapData 的 name 是 '{self.names(y.name_hash)}'，文件名是 '{y.stem}'（存档后改了文件名？）。别的 ymap 用 parent 指向它时会对不上，在 CodeWalker 里改名后重存")
            # entities
            far = [e for e in y.ents if RANK.get(e.level, 0) == 0 and e.lod > 1500]
            if far and not vanilla:
                self.add('warn', 'LOD_DIST_SUSPICIOUS', y.rel, f'{len(far)} 个 HD 实体 lodDist > 1500（最大 {max(e.lod for e in far):.0f}）。太远会一直被串流；单栋建筑用几百米 + 模型 LOD，地标才用 LOD 父子')
            bad_child = [e for e in y.ents if e.nch and e.child_lod > e.lod > 0]
            if bad_child:
                self.add('warn', 'LOD_DIST_SUSPICIOUS', y.rel, f'{len(bad_child)} 个父实体 childLodDist 比自己的 lodDist 还大（Cfx part 6：LOD 的 childLodDist = HD 的 lodDist，自己的 lodDist 更大）')
            if any(e.mlo for e in y.ents):
                mlo_maps.setdefault(y.resource, []).append(y.stem)
            # LOD links (one finding per ymap and problem, first examples listed)
            shift_hits, linked = {}, {}
            lod_bad = {}

            def bad(code, text):
                lod_bad.setdefault(code, []).append(text)
            for e in y.ents:
                if e.level == 'ORPHANHD' and e.pidx >= 0:
                    self.add('warn', 'LOD_FLAG_WITHOUT_PARENT', y.rel, f'实体 #{e.idx}（{self.names(e.arch)}）是 ORPHANHD 却有 parentIndex {e.pidx}。ORPHANHD 就是没有 LOD 父的 HD')
                    continue
                if e.pidx < 0:
                    if e.flags & F_LOD_IN_PARENT and y.parent:
                        no_parent_flag8.setdefault(y.rel, []).append(e.idx)
                    continue
                kind, target, p = resolve_parent(y, e, by_key)
                if kind == 'missing':
                    missing_parents.setdefault(y.rel, set()).add(target)
                    continue
                if kind == 'noparent':
                    if e.pidx >= len(y.ents):
                        bad('LOD_INDEX_OUT_OF_RANGE', f'#{e.idx}（{self.names(e.arch)}）parentIndex {e.pidx}，这个 ymap 只有 {len(y.ents)} 个实体，也没设 parent ymap')
                    else:
                        bad('LOD_NO_PARENT_MAP', f'#{e.idx}（{e.level}）parentIndex {e.pidx} 指到同一个 ymap 的 {y.ents[e.pidx].level}')
                    continue
                if p is None:
                    bad('LOD_INDEX_OUT_OF_RANGE', f'#{e.idx}（{self.names(e.arch)}）parentIndex {e.pidx}，父 ymap {target.stem} 只有 {len(target.ents)} 个实体')
                    continue
                if p.level == 'ORPHANHD' or RANK.get(p.level, 0) <= RANK.get(e.level, 0):
                    bad('LOD_RANK', f'#{e.idx}（{e.level}）的父 {target.stem} #{e.pidx} 是 {p.level}')
                    continue
                # index shifted: the parent is far away but a neighbouring entry sits right on the child
                if e.pos[2] > BURIED_Z and p.pos[2] > BURIED_Z:   # a buried parent is far away on purpose
                    linked[target.stem] = linked.get(target.stem, 0) + 1
                    d_p = dist3(e.pos, p.pos)
                    if d_p > 5:
                        for off in (-1, 1, -2, 2):
                            j = e.pidx + off
                            if 0 <= j < len(target.ents) and d_p > 4 * max(dist3(e.pos, target.ents[j].pos), 1.0):
                                shift_hits.setdefault((target.stem, off), []).append(e.idx)
                                break
            why = {'LOD_INDEX_OUT_OF_RANGE': ('error', 'parentIndex 超出父 ymap 的实体数。在 LOD ymap 里删实体会让后面的索引全部错位：被别人指向的父实体不要删，移到地下（z -500）'),
                   'LOD_RANK': ('error', '父的 LOD 等级要比子高（HD < LOD < SLOD1 < SLOD2 < SLOD3），多半是索引错位'),
                   'LOD_NO_PARENT_MAP': ('warn', 'parentIndex 指到同一个 ymap 里不比它高级的实体，ymap 又没设 parent：CodeWalker 会当它没有 LOD 父（链接是坏的）。不需要 LOD 就把 parentIndex 改成 -1')}
            for code, items in lod_bad.items():
                lvl, text = why[code]
                self.add(lvl, code, y.rel, f"{len(items)} 个实体：{'；'.join(items[:3])}{'…' if len(items) > 3 else ''}。{text}")
            for (tstem, off), idxs in shift_hits.items():
                if len(idxs) >= 3 and len(idxs) * 2 >= linked.get(tstem, 0):
                    self.add('error', 'LOD_INDEX_SHIFTED', y.rel, f'{len(idxs)} 个实体的 parentIndex 都差了 {-off:+d}：指到的 LOD 离它们很远，而 {tstem} 里旁边那一格的 LOD 近得多、几乎就在原地（例如实体 #{idxs[0]}）。'
                             'LOD 会在错的位置切换（远处一棵树不见、另一棵出现两次）。父 ymap 删/插了实体后没重新对应索引')
            for e in y.ents:
                if e.pos[2] <= BURIED_Z:
                    continue
                k = (e.arch, round(e.pos[0], 2), round(e.pos[1], 2), round(e.pos[2], 2))
                dup_ent.setdefault(k, []).append(y)
            # custom LOD pair without manifest
            if y.parent and not vanilla and y.parent in by_key and not looks_vanilla(by_key[y.parent].stem, self.vanilla):
                res = next((r for r in self.resources if r.name == y.resource), None)
                if res is not None and not any(x.lower().endswith('.ymf') for x in res.rels):
                    self.add('warn', 'CUSTOM_LOD_NO_MANIFEST', y.rel, f"自定义 HD/LOD 一对（parent = {by_key[y.parent].stem}）但资源里没有 .ymf。Cfx part 6：LOD 设置做完要用 Manifest Generator 生成 _manifest.ymf")
            # archetypes
            local = self.local_arch.get(y.resource, set())
            models = self.model_stems.get(y.resource, set())
            if local is None:      # a ytyp could not be decoded: archetype checks would be guesses
                local, models = set(), set()
            no_arch = sorted({self.names(e.arch) for e in y.ents if e.arch in models and e.arch not in local and not e.mlo
                              and not looks_vanilla(self.names(e.arch), self.vanilla)})
            if no_arch:
                self.add('warn', 'CUSTOM_MODEL_NO_ARCHETYPE', y.rel, f"放了本资源自带的模型 {', '.join(no_arch[:5])}，但本资源的 ytyp 没定义这个 archetype：游戏里看不见（CodeWalker 的 Calculate Extents 也会算成一个小球）")
            if local and not vanilla:
                unknown = [e for e in y.ents if e.arch not in local and not e.mlo]
                if unknown:
                    shown = sorted({self.names(e.arch) for e in unknown})[:6]
                    self.add('info', 'ARCHETYPE_NOT_LOCAL', y.rel, f"{len(unknown)} 个实体用的 archetype 不在本资源的 ytyp 里（{', '.join(shown)}…）。原版道具正常；自定义的要确认拼写和 ytyp 已载入")
        for rel, parents in missing_parents.items():
            self.add('info', 'LOD_PARENT_MISSING', rel, f"有实体用 flag 8 指向父 ymap {', '.join(self.names(p) for p in sorted(parents))}，那个 ymap 不在这次检查里（原版父 ymap 很正常）。改父 ymap 时要连子 ymap 一起检查")
        for rel, idxs in no_parent_flag8.items():
            self.add('info', 'LOD_FLAG_WITHOUT_PARENT', rel, f'{len(idxs)} 个实体勾了 flag 8 "LOD in parent map" 但 parentIndex 是 -1（例如 #{idxs[0]}）：没有 LOD 父，flag 没作用。确认不是删父实体时漏改')
        for res, stems in empty_names.items():
            self.add('info', 'YMAP_NAME_EMPTY', res, f"{len(stems)} 个 ymap 的 CMapData name 是空的（{', '.join(stems[:5])}{'…' if len(stems) > 5 else ''}）。"
                     '用 CodeWalker.Core 写代码存档时没设 Name 会这样；用户 La Puerta 的覆盖档这样也能用，但设成文件名比较保险（occluders.ps1 已这样做）')
        for res, stems in mlo_maps.items():
            self.add('info', 'MLO_HERE', res, f"{len(stems)} 个 ymap 放了 MLO 实例（{', '.join(stems[:4])}{'…' if len(stems) > 4 else ''}）。室内规则用 fivem-mlo-housing 的 check_mlo_resource.py 检查")
        # the same entity in X and hei_X (base and mpheist copy) is normal, so compare by base name
        dups = {k: v for k, v in dup_ent.items()
                if len({base_stem(y.stem) for y in v}) > 1 or len(v) > len({id(y) for y in v})}
        if dups:
            k, ys = next(iter(dups.items()))
            places = sorted({y.rel for y in ys})
            self.add('warn', 'DUPLICATE_ENTITY', places[0], f"{len(dups)} 处同一个 archetype 放在同一位置两次（例如 {self.names(k[0])} 在 {k[1]:.1f},{k[2]:.1f},{k[3]:.1f}，见 {', '.join(places[:3])}）：会闪烁（z-fighting）或双份道具。两个资源都放了同一批东西时最常见")

    # ---- B: across resources
    def check_cross(self):
        owners = {}
        for res in self.resources:
            if res.loose:
                continue
            for f, r in res.streamed():
                low = os.path.basename(r).lower()
                if enhanced(r) or not (low.endswith(RSC_EXT) or low.endswith('.ymf')):
                    continue
                owners.setdefault(low, []).append((res, r, f))
        for low, lst in sorted(owners.items()):
            if len(lst) < 2:
                continue
            res_names = list(dict.fromkeys(x[0].name for x in lst))
            detail = '；'.join(f"{x[0].name}/{x[1]}（{os.path.getsize(x[2]) // 1024} KB）" for x in lst[:4])
            if len(res_names) == 1:
                self.add('warn', 'DUPLICATE_STREAM_FILE', lst[0][0].name, f"'{low}' 在同一个资源里有 {len(lst)} 份：{detail}。只有一份会生效")
                continue
            if low.endswith('.ymf'):
                lvl, why = 'warn', '（同名 .ymf 会不会互相顶掉没有官方说明，未验证；改成 <资源名>_manifest.ymf 最保险）'
            elif low.endswith(OWNER_ERROR_EXT) or low.startswith('minimap_'):
                lvl, why = 'error', '。同一个原版/地图文件只能有一个主人：后载入的赢，另一个资源的修改会消失（东西又出现、闪烁、漂浮道具）。把两边的修改合并进一份，只留在一个资源里'
            else:
                lvl, why = 'warn', '。只有一个会生效（载入顺序决定），模型/贴图被别人的版本顶掉'
            self.add(lvl, 'DUPLICATE_STREAM_FILE', ', '.join(res_names[:4]), f"'{low}' 在 {len(res_names)} 个资源里串流：{detail}{why}")
        # vanilla overrides, hei_ pairs, occluder overrides per resource
        all_streamed = {}
        for res in self.resources:
            for f, r in res.streamed():
                all_streamed.setdefault(stem_of(r), set()).add(res.name)
        for res in self.resources:
            if res.loose:
                continue
            stems = sorted({stem_of(r) for _, r in res.streamed()
                            if r.lower().endswith(('.ymap', '.ybn', '.ynd', '.ynv', '.ytd')) and not enhanced(r)})
            van = [s for s in stems if looks_vanilla(s, self.vanilla)]
            if van:
                how = '按 --vanilla-list' if self.vanilla is not None else '按文件名猜的，--vanilla-list 才准确'
                self.add('info', 'VANILLA_OVERRIDE', res.name, f"覆盖了 {len(van)} 个原版文件（{how}）：{', '.join(van[:10])}{'…' if len(van) > 10 else ''}。别的资源不能再改这些文件")
            ymaps = {stem_of(r) for _, r in res.streamed() if r.lower().endswith('.ymap') and not enhanced(r)}
            lone_base = sorted(s for s in ymaps if not s.startswith('hei_') and looks_vanilla(s, self.vanilla)
                               and 'hei_' + s not in ymaps and 'lodlights' not in s)
            lone_hei = sorted(s for s in ymaps if s.startswith('hei_') and s[4:] not in ymaps)
            if lone_hei:
                self.add('info', 'HEI_PAIR_MISSING', res.name, f"只改了 hei_ 版（{', '.join(lone_hei[:6])}），没有基础版。FiveM 一直载入 mpheist，hei_ 那份才是游戏用的，这样通常没问题；单人模式才会看到基础版")
            if lone_base:
                known = self.vanilla is not None
                hits = [s for s in lone_base if not known or 'hei_' + s in self.vanilla]
                if hits:
                    lvl = 'warn' if known else 'info'
                    self.add(lvl, 'HEI_PAIR_MISSING', res.name, f"改了 {', '.join(hits[:6])}{'…' if len(hits) > 6 else ''} 但没有 hei_ 版本。"
                             + ('游戏里有 hei_ 版（mpheist DLC），多人模式载入的是 hei_ 那份：两份都要改' if known else
                                '如果游戏里有同名 hei_ 版（CodeWalker 开 DLC 搜一下），多人模式载入的是 hei_ 那份：两份都要改'))
            # occluders for edited areas (no diff available)
            if not self.orig_dir:
                areas = sorted({area_prefix(s) for s in ymaps if looks_vanilla(s, self.vanilla) and 'occl' not in s
                                and 'lodlights' not in s and '_critical' not in s})
                occl = {area_prefix(s) for s in all_streamed if 'occl' in s}
                lacking = [a for a in areas if a not in occl]
                if lacking:
                    self.add('info', 'OCCLUDER_CHECK', res.name, f"改了 {', '.join(lacking[:6])} 区的原版 ymap，但没有任何资源覆盖那区的 *_occl_* ymap。"
                             '如果是删掉/搬走建筑，原版遮挡体还在，站在那里背后的城市会不画（天空+黑点）。只是加东西或改车生成点可以忽略')
        # duplicate [category] folders
        cats = {}
        for res in self.resources:
            parts = res.root.replace('\\', '/').split('/')
            for i, p in enumerate(parts[:-1]):
                if p.startswith('[') and p.endswith(']'):
                    cats.setdefault(p.lower(), set()).add('/'.join(parts[:i + 1]))
        for c, where in sorted(cats.items()):
            if len(where) > 1:
                self.add('warn', 'CATEGORY_NAME_CLASH', c, f"有 {len(where)} 个同名分类文件夹 {c}：{'；'.join(sorted(where)[:3])}。"
                         'ensure [分类] 会把两个都启动（用户的 [maps] 撞到 [cfx-default] 的 [maps]，把示例出生点地图也开了）。分类名在整个伺服器要唯一')

    # ---- D: diff with vanilla
    def check_diff(self):
        orig = []
        for f in sorted(os.listdir(self.orig_dir)):
            if f.lower().endswith('.ymap.xml'):
                p = os.path.join(self.orig_dir, f)
                try:
                    root = ET.parse(p).getroot()
                except ET.ParseError as e:
                    self.add('error', 'XML_INVALID', p, f'原版 XML 读不出：{e}')
                    continue
                y = fill(Ymap(p, 'orig/' + f, 'orig', 'xml'), read_ymap_xml(root))
                self.names.add(root.findtext('name'))
                orig.append(y)
        if not orig:
            self.add('warn', 'ORIG_EMPTY', self.orig_dir, '--orig 文件夹里没有 *.ymap.xml')
            return
        edited_xml = {y.stem: y for y in self.xml_ymaps}
        edited_bin = {y.stem: y for y in self.bin_ymaps}
        o_by_key = {y.key: y for y in orig}
        pairs = []
        for o in orig:
            e = edited_xml.get(o.stem) or edited_bin.get(o.stem)
            if e is not None:
                pairs.append((o, e))
        if not pairs:
            self.add('warn', 'ORIG_NO_MATCH', self.orig_dir, '--orig 里的 ymap 在检查的资源里一个同名的都没有（文件名要一样，例如 kt1_13.ymap.xml 对 kt1_13.ymap）')
            return
        e_by_key = {e.key: e for _, e in pairs}

        def ident(ent):
            return ent.guid if ent.guid else (ent.arch, round(ent.pos[0], 1), round(ent.pos[1], 1), round(ent.pos[2], 1))

        def parent_of(y, ent, by_key):
            kind, t, p = resolve_parent(y, ent, by_key)
            return (t, p) if kind in ('same', 'parent') and p is not None else None

        # children of each original parent (by identity) inside the set
        o_children, e_children = {}, {}
        for o in orig:
            for c in o.ents:
                p = parent_of(o, c, o_by_key)
                if p:
                    o_children.setdefault((p[0].stem, ident(p[1])), []).append((o.stem, ident(c)))
        for _, e in pairs:
            for c in e.ents:
                p = parent_of(e, c, e_by_key)
                if p:
                    e_children.setdefault((p[0].stem, ident(p[1])), []).append((e.stem, ident(c)))
        e_index = {(e.stem, ident(x)): (e, x) for _, e in pairs for x in e.ents}
        removed_pos, removed_stems = [], set()
        removed_sets = {}
        for o, e in pairs:
            e_ids = {ident(x): x for x in e.ents}
            gone, buried, moved = [], [], []
            for x in o.ents:
                y = e_ids.get(ident(x))
                if y is None:
                    gone.append(x)
                elif y.pos[2] < x.pos[2] - 5 and (y.pos[2] <= BURIED_Z or (abs(y.pos[0] - x.pos[0]) < 1 and abs(y.pos[1] - x.pos[1]) < 1)):
                    buried.append(x)
                elif max(abs(a - b) for a, b in zip(x.pos, y.pos)) > 0.05:
                    moved.append(x)
            added = len(e.ents) - (len(o.ents) - len(gone))
            removed_sets[o.stem] = {ident(x) for x in gone + buried}
            if gone or buried or moved or added:
                self.add('info', 'DIFF_SUMMARY', e.rel, f'对比原版：删掉 {len(gone)}、移到地下 {len(buried)}、移动 {len(moved)}、新增 {max(added, 0)} 个实体；'
                         f'车生成点 {o.n["cargen"]}→{e.n["cargen"]}，timecycle 方框 {o.n["tc"]}→{e.n["tc"]}')
            for x in gone + buried:
                if x.pos[2] > BURIED_Z:
                    removed_pos.append(x.pos)
                    removed_stems.add(o.stem)
            for x in gone:
                kids = o_children.get((o.stem, ident(x)), [])
                alive = [k for k in kids if k in e_index and e_index[k][1].pos[2] > BURIED_Z]
                if alive:
                    self.add('error', 'REMOVED_HAS_LOD_CHILDREN', e.rel, f'删掉的 {self.names(x.arch)}（{x.level}）还有 {len(alive)} 个子实体留着（例如 {alive[0][0]}）：子实体变孤儿/指到别人。父实体不要删，移到地下')
            # parents that lost children but kept numChildren
            for x in o.ents:
                y = e_ids.get(ident(x))
                if y is None:
                    continue
                before = len(o_children.get((o.stem, ident(x)), []))
                after = len(e_children.get((e.stem, ident(y)), []))
                if after < before and y.nch == x.nch and x.nch:
                    self.add('warn', 'NUMCHILDREN_STALE', e.rel, f'{self.names(x.arch)}（{x.level}）原本 {before} 个子实体在这批文件里，现在 {after} 个，但 numChildren 还是 {y.nch}。用户的做法：子实体删掉几个就减几个（例如 SLOD2 17→16）')
                kids = o_children.get((o.stem, ident(x)), [])
                if kids and y.pos[2] > BURIED_Z and abs(y.pos[2] - x.pos[2]) < 5:
                    left = [k for k in kids if k in e_index and e_index[k][1].pos[2] > BURIED_Z]
                    if not left:
                        self.add('warn', 'LOD_LEFT_BEHIND', e.rel, f'{self.names(x.arch)}（{x.level}）的 {len(kids)} 个子实体都删掉/移走了，它自己还在原地：从远处还会看到旧建筑。把它也移到地下（被别人指向时不要删）')
        # children that now point at a different parent
        for o, e in pairs:
            o_ids = {ident(x): x for x in o.ents}
            for c in e.ents:
                oc = o_ids.get(ident(c))
                if oc is None or c.pidx < 0:
                    continue
                po, pe = parent_of(o, oc, o_by_key), parent_of(e, c, e_by_key)
                if po and pe and (po[0].stem, ident(po[1])) != (pe[0].stem, ident(pe[1])):
                    self.add('error', 'INDEX_SHIFT', e.rel, f'子实体 {self.names(c.arch)} #{c.idx} 原本的父是 {po[0].stem} 的 {self.names(po[1].arch)}，现在 parentIndex {c.pidx} 指到 {self.names(pe[1].arch)}：'
                             '父 ymap 里删了前面的实体，索引往前移了。删了的要把所有子实体的 parentIndex 重新对应，或不要删、改成移到地下')
        if not removed_pos:
            return
        lo = (min(p[0] for p in removed_pos) - 10, min(p[1] for p in removed_pos) - 10)
        hi = (max(p[0] for p in removed_pos) + 10, max(p[1] for p in removed_pos) + 10)
        area = f'x {lo[0]:.0f}..{hi[0]:.0f}, y {lo[1]:.0f}..{hi[1]:.0f}'
        occl = [y for y in self.bin_ymaps + self.xml_ymaps if (y.n['box'] or y.n['model'] or y.cflags & 32)]
        if not any(overlap2d(lo, hi, y.emin, y.emax) for y in occl):
            prefixes = sorted({area_prefix(s) for s in removed_stems})
            self.add('warn', 'OCCLUDER_NOT_EDITED', ', '.join(sorted(removed_stems))[:120], f'删掉/移走的实体在 {area}，但这批资源里没有覆盖到那里的遮挡体 ymap（{", ".join(p + "_occl_*" for p in prefixes)}、hei_ 版）。'
                     '原版遮挡体还在 → 站在那里背后的城市不画（天空+黑点）。用 CodeWalker 选 Occluders 删掉那栋楼的，或用户的 occluders.ps1')
        ybn = {stem_of(r) for res in self.resources for _, r in res.streamed() if r.lower().endswith('.ybn')}
        blocks = sorted({base_stem(s).split('_strm')[0].split('_long')[0] for s in removed_stems})
        no_col = [b for b in blocks if not any(base_stem(s).startswith(b + '_') for s in ybn)]
        if no_col:
            self.add('info', 'COLLISION_NOT_EDITED', ', '.join(no_col), f"删了 {', '.join(no_col)} 的实体，但没有覆盖它的碰撞（{no_col[0]}_N.ybn、hi@、ma@）。很多原版楼的碰撞在独立的 ybn 里，不改会留下隐形墙")
        stale = []
        for o, e in pairs:
            for c in e.cargens:
                if lo[0] <= c[0] <= hi[0] and lo[1] <= c[1] <= hi[1]:
                    stale.append(e.rel)
                    break
        if stale:
            self.add('warn', 'CARGEN_IN_REMOVED_AREA', stale[0], f"清掉的区域（{area}）里还有车生成点（{', '.join(sorted(set(stale))[:4])}）：车会生成在新建筑里。一起删掉或移走")
        tcs = [e.rel for _, e in pairs if any(t[0] and lo[0] <= (t[0][0] + t[1][0]) / 2 <= hi[0] and lo[1] <= (t[0][1] + t[1][1]) / 2 <= hi[1] for t in e.tcboxes)]
        if tcs:
            self.add('info', 'TCMOD_IN_REMOVED_AREA', tcs[0], f"清掉的区域里还有 timecycle 方框（{', '.join(sorted(set(tcs))[:4])}），会让新建筑附近的光线/颜色怪怪的")
        for o, e in pairs:
            if o.stem.startswith('hei_'):
                continue
            h = 'hei_' + o.stem
            if h in removed_sets and removed_sets[h] != removed_sets.get(o.stem, set()):
                diff = len(removed_sets[h] ^ removed_sets.get(o.stem, set()))
                self.add('warn', 'HEI_EDIT_DIFFERS', e.rel, f'{o.stem} 和 {h} 删掉/移走的实体不一样（相差 {diff} 个）。单人和多人会看到不同的东西：两份要做一样的修改')
            elif o.stem in removed_sets and removed_sets[o.stem] and h not in removed_sets and any(y.stem == h for y in orig):
                self.add('warn', 'HEI_EDIT_DIFFERS', e.rel, f'原版有 {h}，但这批资源没有改它：多人模式载入 hei_ 那份，删掉的东西会回来')
        self.add('info', 'SLOD_REMINDER', ', '.join(sorted(removed_stems))[:120], '远处（约 750 m 以外）显示的是 SLOD2/SLOD3 合并模型（一块覆盖好几个街区），改 ymap 去不掉；要编辑那个 SLOD 模型（ydd/ydr）。用户 La Puerta 留着这个已知问题')

    def run(self):
        for res in self.resources:
            self.check_resource(res)
        self.load_xml()
        if self.bin_ymaps:
            self.check_ymap_set(self.bin_ymaps, 'bin')
        if self.xml_ymaps:
            self.check_ymap_set(self.xml_ymaps, 'xml')
        self.check_cross()
        if self.orig_dir:
            self.check_diff()
        return self.findings


def check(paths, xml_dirs=(), orig=None, vanilla_list=None, names_file=None):
    vanilla = load_list(vanilla_list) if vanilla_list else None
    return Checker(paths, xml_dirs, orig, vanilla, names_file).run()


def main():
    ap = argparse.ArgumentParser(description='Check FiveM outdoor map resources (read-only)')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--xml', action='append', default=[], help='folder with CodeWalker/Sollumz XML exports')
    ap.add_argument('--orig', help='folder with the untouched vanilla *.ymap.xml (diff mode)')
    ap.add_argument('--vanilla-list', help='file names that exist in the game, one per line / CSV first column')
    ap.add_argument('--names', help='extra names to resolve hash_XXXXXXXX')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')   # Windows consoles default to cp1252
    findings = check(args.paths, args.xml, args.orig, args.vanilla_list, args.names)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                print(f"{LEVEL_NAME[level]} {x['code']}: [{x['file']}] {x['message']}")
        if not findings:
            print('✓ 没发现问题')
        n = {lv: sum(1 for f in findings if f['level'] == lv) for lv in LEVEL_NAME}
        print(f"\n错误 {n['error']} / 警告 {n['warn']} / 提示 {n['info']}。静态检查通过 ≠ 游戏里没问题：照 references/troubleshooting.md 的测试清单进游戏看")
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
