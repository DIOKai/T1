#!/usr/bin/env python3
"""Read-only livery checker for FiveM add-on vehicles.

Usage:
    py -3 check_livery.py <resource-or-folder> [more paths] [--json] [--all-textures]

A path can be one vehicle resource, a whole folder such as resources/[vehicles],
or a loose mod folder (stream files without fxmanifest). Standard library only,
nothing is written. Exit code 1 when errors are found.

Reads
- binary .yft / .ytd (RSC7, GTA V Legacy): the file is inflated in memory and the
  shader group / texture dictionary are walked (layout from CodeWalker.Core
  Drawable.cs / ShaderGroup / Texture.cs, checked on vanilla police, polgauntlet,
  tornado5 and ambulance). RSC8 (Enhanced) and escrow-encrypted files are skipped
  with a note.
- CodeWalker / Sollumz .yft.xml / .ytd.xml exports, when there is no binary of the
  same name next to them.
- vehicles.meta (modelName, txdName, flags), carcols.meta (kits: VMT_LIVERY_MOD
  parts, modShopLabel, liveryNames), carvariations.meta (which model uses which
  kit), and every .lua file under the given paths for AddTextEntry labels.

Checks
- the texture named in a livery sampler (DiffuseSampler2, roof DiffuseSampler3)
  exists in the model's .ytd / +hi.ytd / the yft's own embedded dictionary;
- FLAG_HAS_LIVERY vs the _sign_N textures: flag without a livery layer or without
  more than one _sign_N, several _sign_N but no flag, gaps in the numbering,
  _sign_0, the shader pointing at a sign other than _sign_1, more than 30;
- the livery layer is missing in the Medium/Low/VLow LOD (livery disappears at
  distance) - binary yft only;
- VMT_LIVERY_MOD parts: the part .yft exists, its embedded texture matches its
  DiffuseSampler2, the kit is used by some model in carvariations;
- liveryNames / modShopLabel keys without an AddTextEntry (menus show NULL);
- livery textures: not a power of two, larger than 2048, uncompressed
  (A8R8G8B8 etc.), BC7 (Legacy support unverified), no mip levels, junk names
  ("Untitled design", spaces), the same livery texture in both <name>.ytd and
  <name>+hi.ytd or in two ytds, and the total livery memory per model.

Cannot check: how the livery looks (alpha, colours, mirrored or upside-down text,
stretching - use livery_template.py and look in game), real brands or agency
marks in the artwork, UV1 presence in binary files, whether a menu uses
SetVehicleLivery or SetVehicleMod, labels defined in resources outside the given
paths, whether _sign_0 or numbering gaps really break cycling (unverified).
"""
import argparse
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

MIB = 1024 * 1024
LIVERY_SAMPLERS = ('DiffuseSampler2', 'DiffuseSampler3')
FORMATS = {0x31545844: 'DXT1', 0x33545844: 'DXT3', 0x35545844: 'DXT5', 0x31495441: 'ATI1',
           0x32495441: 'ATI2', 0x20374342: 'BC7', 21: 'A8R8G8B8', 22: 'X8R8G8B8', 25: 'A1R5G5B5',
           28: 'A8', 32: 'A8B8G8R8', 50: 'L8'}
BLOCK = {'DXT1': 8, 'ATI1': 8, 'DXT3': 16, 'DXT5': 16, 'BC7': 16, 'ATI2': 16}
BPP = {'A8R8G8B8': 4, 'X8R8G8B8': 4, 'A8B8G8R8': 4, 'A1R5G5B5': 2, 'A8': 1, 'L8': 1}
UNCOMPRESSED = {'A8R8G8B8', 'X8R8G8B8', 'A8B8G8R8', 'A1R5G5B5'}
SIGN_RE = re.compile(r'^(.*)_sign_(\d+)$', re.I)
LIVERYISH_RE = re.compile(r'(_sign_\d+|_lvr_\d+|_livery_?\d+|_liv\d+)$', re.I)
JUNK_RE = re.compile(r'(untitled|design\s*-|copy of|new layer|^image\d*$|^layer\s*\d*$)', re.I)
SPACE_RE = re.compile(r'\s')
SHARED_NAMES = re.compile(r'^(blank|vehicle_generic.*|vehicle_genericmud.*)$', re.I)
VANILLA_LABEL = re.compile(r'^POLSHARED_LIV\d+$', re.I)   # vanilla police livery labels (mp2023_02 carcols)


# ---------------------------------------------------------------- RSC7 reading

def rsc_page_size(flags):
    # FXServer ConvertRSC7Size / CodeWalker RpfFile.GetSizeFromFlags
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


def joaat(text):
    h = 0
    for c in text.lower().encode():
        h = (h + c) & 0xFFFFFFFF
        h = (h + (h << 10)) & 0xFFFFFFFF
        h ^= h >> 6
    h = (h + (h << 3)) & 0xFFFFFFFF
    h ^= h >> 11
    return (h + (h << 15)) & 0xFFFFFFFF


PARAM_NAMES = {joaat(n): n for n in ('DiffuseSampler', 'DiffuseSampler2', 'DiffuseSampler3', 'BumpSampler',
                                     'SpecSampler', 'DirtSampler', 'DamageSampler', 'DetailSampler',
                                     'EnvironmentSampler', 'PlateBgSampler', 'PlateBgBumpSampler', 'FontSampler',
                                     'FontNormalSampler')}


class Rsc:
    """Inflated RSC7 resource with virtual (0x5...) and physical (0x6...) pointer lookup."""

    def __init__(self, path):
        with open(path, 'rb') as fh:
            head = fh.read(16)
            if len(head) < 16:
                raise ValueError('文件太小')
            if head[:4] == b'RSC8':
                raise ValueError('RSC8（GTA V Enhanced 格式），这个脚本只读 Legacy 的 RSC7')
            if head[:4] != b'RSC7':
                raise ValueError('开头不是 RSC7（可能是 escrow 加密、改了扩展名或损坏）')
            _, self.version, vflags, pflags = struct.unpack('<4sIII', head)
            self.vsize, self.psize = rsc_page_size(vflags), rsc_page_size(pflags)
            # Only the virtual (system) part is needed: names, shaders, texture headers. It comes
            # first in the stream, so inflate chunk by chunk and stop - pixel data is never read.
            dec, out, raw = zlib.decompressobj(-15), bytearray(), bytearray()
            try:
                while len(out) < self.vsize:
                    chunk = fh.read(1 << 20)
                    if not chunk:
                        break
                    raw += chunk if not out else b''
                    out += dec.decompress(chunk, self.vsize - len(out))
                    while dec.unconsumed_tail and len(out) < self.vsize:
                        out += dec.decompress(dec.unconsumed_tail, self.vsize - len(out))
            except zlib.error:                            # stored uncompressed
                out = (raw + fh.read(max(0, self.vsize - len(raw))))[:self.vsize]
        self.d = bytes(out)
        if len(self.d) < self.vsize:
            raise ValueError('解压后长度不对（损坏或加密）')

    def off(self, ptr):
        if ptr >> 28 == 5:
            o = ptr & 0x0FFFFFFF
        elif ptr >> 28 == 6:
            o = self.vsize + (ptr & 0x0FFFFFFF)
        else:
            return None
        return o if o < len(self.d) else None

    def q(self, o):
        return struct.unpack_from('<Q', self.d, o)[0]

    def h(self, o):
        return struct.unpack_from('<H', self.d, o)[0]

    def i(self, o):
        return struct.unpack_from('<I', self.d, o)[0]

    def cstr(self, o):
        e = self.d.index(b'\0', o, o + 256)
        return self.d[o:e].decode('ascii', 'replace')


def read_texture_dict(r, base):
    """pgDictionary<grcTexture> at offset `base` -> list of texture dicts."""
    out = []
    lst = base + 0x30
    ptr, count = r.q(lst), r.h(lst + 8)
    arr = r.off(ptr)
    if arr is None:
        return out
    for k in range(count):
        t = r.off(r.q(arr + 8 * k))
        if t is None:
            continue
        name_o = r.off(r.q(t + 0x28))
        w, h = r.h(t + 0x50), r.h(t + 0x52)
        fmt = r.i(t + 0x58)
        out.append({'name': r.cstr(name_o) if name_o is not None else '?', 'width': w, 'height': h,
                    'format': FORMATS.get(fmt, f'0x{fmt:X}'), 'levels': r.d[t + 0x5D]})
    return out


def read_ytd(path):
    r = Rsc(path)
    return read_texture_dict(r, 0)


def read_yft(path):
    """Shaders (sampler -> texture name), per-LOD shader use, embedded textures."""
    r = Rsc(path)
    drw = r.off(r.q(0x30))
    if drw is None:
        raise ValueError('没有 drawable（不像车辆 yft）')
    sg = r.off(r.q(drw + 0x10))
    if sg is None:
        raise ValueError('没有 shader group')
    shaders = []
    sp, sc = r.off(r.q(sg + 0x10)), r.h(sg + 0x18)
    for k in range(sc if sp is not None else 0):
        s = r.off(r.q(sp + 8 * k))
        pp = r.off(r.q(s)) if s is not None else None
        if pp is None:
            shaders.append({'name_hash': 0, 'samplers': {}})
            continue
        pc = r.d[s + 0x10]
        params = [(r.d[pp + 16 * j], r.q(pp + 16 * j + 8)) for j in range(pc)]
        hoff = pp + 16 * pc + sum(16 * dt for dt, _ in params if dt > 0)
        samplers = {}
        for j, (dt, dp) in enumerate(params):
            if dt != 0 or not dp:
                continue
            name_hash = r.i(hoff + 4 * j)
            to = r.off(dp)
            no = r.off(r.q(to + 0x28)) if to is not None else None
            samplers[PARAM_NAMES.get(name_hash, f'0x{name_hash:08X}')] = r.cstr(no) if no is not None else ''
        shaders.append({'name_hash': r.i(s + 8), 'samplers': samplers})
    embedded = []
    td = r.off(r.q(sg + 0x08))
    if td is not None:
        embedded = read_texture_dict(r, td)
    lods = {}
    for k, lod in enumerate(('high', 'med', 'low', 'vlow')):
        lp = r.off(r.q(drw + 0x50 + 8 * k))
        if lp is None:
            continue
        ep, cnt = r.off(r.q(lp)), r.h(lp + 8)
        used = set()
        for m in range(cnt if ep is not None else 0):
            mo = r.off(r.q(ep + 8 * m))
            if mo is None:
                continue
            gc, smp = r.h(mo + 0x10), r.off(r.q(mo + 0x20))
            if smp is not None:
                used.update(r.h(smp + 2 * g) for g in range(gc))
        lods[lod] = used
    return {'shaders': shaders, 'embedded': embedded, 'lods': lods}


# ---------------------------------------------------------------- XML exports

def _fmt_xml(text):
    return (text or '').strip().upper().replace('D3DFMT_', '')


def _xml_textures(td):
    out = []
    for it in (td if td is not None else []):
        def num(tag):
            el = it.find(tag)
            try:
                return int(el.get('value')) if el is not None else 0
            except (TypeError, ValueError):
                return 0
        out.append({'name': (it.findtext('Name') or '').strip(), 'width': num('Width'), 'height': num('Height'),
                    'format': _fmt_xml(it.findtext('Format')), 'levels': num('MipLevels')})
    return out


def read_ytd_xml(path):
    root = ET.parse(path).getroot()
    td = root if root.tag == 'TextureDictionary' else root.find('TextureDictionary')
    return _xml_textures(td)


def read_yft_xml(path):
    """Only the main drawable's ShaderGroup is read (stops there), so huge exports stay fast.
    LOD use is not read from XML (the binary check covers it)."""
    stack = []
    for event, el in ET.iterparse(path, events=('start', 'end')):
        if event == 'start':
            stack.append(el.tag)
            continue
        if el.tag == 'ShaderGroup' and stack[:-1] in (['Fragment', 'Drawable'], ['Drawable']):
            shaders = []
            for s in el.findall('Shaders/Item'):
                samplers = {p.get('name'): (p.findtext('Name') or '').strip()
                            for p in s.findall('Parameters/Item') if p.get('type') == 'Texture'}
                shaders.append({'name_hash': 0, 'samplers': samplers})
            return {'shaders': shaders, 'embedded': _xml_textures(el.find('TextureDictionary')), 'lods': {}}
        stack.pop()
    raise ValueError('XML 里没找到 ShaderGroup')


# ---------------------------------------------------------------- meta files

def _parse_meta(path):
    with open(path, 'rb') as fh:
        raw = fh.read()
    text = raw.decode('utf-8-sig', errors='replace')
    try:
        return ET.fromstring(raw), text
    except ET.ParseError:
        return None, text


def _items(text, tag):
    return re.findall(r'<%s>\s*(.*?)\s*</%s>' % (tag, tag), text, re.S | re.I)


def read_vehicles_meta(path):
    root, text = _parse_meta(path)
    out = []
    if root is not None:
        for it in root.iter('Item'):
            mn = it.findtext('modelName')
            if mn is None:
                continue
            out.append({'model': mn.strip(), 'txd': (it.findtext('txdName') or mn).strip(),
                        'flags': (it.findtext('flags') or '').split()})
    else:
        for block in re.findall(r'<Item>(.*?)</Item>', text, re.S):
            mn = re.search(r'<modelName>\s*([^<\s]+)', block)
            if mn:
                txd = re.search(r'<txdName>\s*([^<\s]+)', block)
                fl = re.search(r'<flags>(.*?)</flags>', block, re.S)
                out.append({'model': mn.group(1), 'txd': txd.group(1) if txd else mn.group(1),
                            'flags': fl.group(1).split() if fl else []})
    return out


def read_carcols(path):
    root, text = _parse_meta(path)
    kits = []
    if root is None:
        return kits, False
    for kit in root.iter('Item'):
        name = kit.findtext('kitName')
        if name is None:
            continue
        mods, parts = [], []
        for tag in ('visibleMods', 'linkMods'):
            el = kit.find(tag)
            parts += [(it.findtext('modelName') or '').strip().lower() for it in (el if el is not None else [])]
        vm = kit.find('visibleMods')
        for it in (vm if vm is not None else []):
            if (it.findtext('type') or '').strip() == 'VMT_LIVERY_MOD':
                mods.append({'model': (it.findtext('modelName') or '').strip(),
                             'label': (it.findtext('modShopLabel') or '').strip()})
        names = []
        for tag in ('liveryNames', 'livery2Names'):
            ln = kit.find(tag)
            names += [(x.text or '').strip() for x in (ln if ln is not None else []) if (x.text or '').strip()]
        kits.append({'name': name.strip(), 'livery_mods': mods, 'livery_names': names, 'parts': parts})
    return kits, True


def read_carvariations(path):
    root, text = _parse_meta(path)
    out = {}
    if root is not None:
        for it in root.iter('Item'):
            mn = it.findtext('modelName')
            if mn is None:
                continue
            kits = it.find('kits')
            out[mn.strip().lower()] = [(k.text or '').strip() for k in (kits if kits is not None else [])]
    else:
        for block in re.findall(r'<Item>\s*<modelName>(.*?)</kits>', text, re.S):
            mn = block.split('<')[0].strip().lower()
            out[mn] = [k.strip() for k in re.findall(r'<Item>([^<]+)</Item>', block)]
    return out


def meta_kind(path):
    try:
        with open(path, 'rb') as fh:
            head = fh.read(4096).decode('utf-8', errors='replace')
    except OSError:
        return None
    for tag, kind in (('CVehicleModelInfo__InitDataList', 'vehicles'), ('CVehicleModelInfoVarGlobal', 'carcols'),
                      ('CVehicleModelInfoVariation', 'carvariations')):
        if tag in head:
            return kind
    return None


# ---------------------------------------------------------------- helpers

def tex_mib(t):
    w, h, levels = max(1, t['width']), max(1, t['height']), max(1, t['levels'] or 1)
    total = 0
    for k in range(levels):
        mw, mh = max(1, w >> k), max(1, h >> k)
        if t['format'] in BLOCK:
            total += ((mw + 3) // 4) * ((mh + 3) // 4) * BLOCK[t['format']]
        else:
            total += mw * mh * BPP.get(t['format'], 4)
    return total / MIB


def pow2(n):
    return n > 0 and (n & (n - 1)) == 0


def walk(paths):
    out = []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            out.append(p)
            continue
        for root, dirs, fs in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            out += [os.path.join(root, f) for f in fs]
    return out


def unit_of(path, manifests):
    d = os.path.dirname(path)
    probe = d
    while True:
        if probe in manifests:
            return probe
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent
    if os.path.basename(d).lower() in ('stream', 'data') or os.path.basename(d).lower().startswith('stream'):
        return os.path.dirname(d)
    return d


def rel(path, bases):
    for b in bases:
        b = os.path.abspath(b)
        if path == b:
            return os.path.basename(path)
        if path.startswith(b + os.sep):
            return os.path.relpath(path, b).replace(os.sep, '/')
    return path


def strip_ext(name):
    low = name.lower()
    for ext in ('.yft.xml', '.ytd.xml', '.yft', '.ytd'):
        if low.endswith(ext):
            return name[:-len(ext)]
    return name


# ---------------------------------------------------------------- main check

def check(paths, all_textures=False):
    findings = []

    def add(level, code, where, msg, tex=None):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg, **({'tex': tex} if tex else {})})

    files = walk(paths)
    manifests = {os.path.dirname(f) for f in files if os.path.basename(f).lower() in ('fxmanifest.lua', '__resource.lua')}
    units = {}
    labels = set()
    for f in files:
        low = os.path.basename(f).lower()
        if low.endswith('.lua'):
            try:
                with open(f, encoding='utf-8', errors='replace') as fh:
                    labels.update(x.upper() for x in re.findall(r"AddTextEntry\s*\(\s*['\"]([^'\"]+)['\"]", fh.read()))
            except OSError:
                pass
            continue
        kind = None
        if low.endswith(('.yft', '.ytd', '.yft.xml', '.ytd.xml')):
            kind = low.rsplit('.', 2)[-2] + '.xml' if low.endswith('.xml') else low.rsplit('.', 1)[-1]
        elif low.endswith('.meta'):
            kind = meta_kind(f)
        if kind:
            u = units.setdefault(unit_of(f, manifests), {'yft': {}, 'ytd': {}, 'yft.xml': {}, 'ytd.xml': {},
                                                         'vehicles': [], 'carcols': [], 'carvariations': []})
            if kind in ('vehicles', 'carcols', 'carvariations'):
                u[kind].append(f)
            else:
                u[kind].setdefault(strip_ext(os.path.basename(f)).lower(), []).append(f)

    # global maps for kits (kits and liveries can live in different resources)
    all_variation_kits = set()
    all_livery_yfts = {}
    for u in units.values():
        for f in u['carvariations']:
            for kits in read_carvariations(f).values():
                all_variation_kits.update(k.lower() for k in kits)
        for stem, fs in list(u['yft'].items()) + list(u['yft.xml'].items()):
            all_livery_yfts.setdefault(stem, []).extend(fs)

    gcache = {}
    for udir, u in sorted(units.items()):
        _check_unit(udir, u, paths, labels, all_variation_kits, all_livery_yfts, add, all_textures, gcache)
    index = {}
    for path, texs in gcache.items():
        for t in texs:
            index.setdefault(t['name'].lower(), []).append(path)
    for f in findings:
        tex = f.pop('tex', None)
        if tex and index.get(tex):
            f['message'] += f"（同名贴图在别的车的 {rel(index[tex][0], paths)} 里，但游戏只在这台车自己的字典里找）"
    return findings


def _load(fs, reader, xml_fs, xml_reader, add, paths):
    """Read the first readable binary; fall back to the XML export."""
    for f in fs:
        try:
            return reader(f), f
        except (ValueError, struct.error, IndexError, OSError) as e:
            add('info', 'READ_SKIPPED', rel(f, paths), f'读不了，跳过：{e}')
    for f in xml_fs:
        try:
            return xml_reader(f), f
        except (ValueError, ET.ParseError, OSError) as e:
            add('info', 'READ_SKIPPED', rel(f, paths), f'XML 读不了，跳过：{e}')
    return None, None


def _check_unit(udir, u, paths, labels, all_variation_kits, all_livery_yfts, add, all_textures, gcache):
    where = rel(udir, paths)
    vehicles = []
    for f in u['vehicles']:
        vehicles += read_vehicles_meta(f)
    meta_by_model = {v['model'].lower(): v for v in vehicles}
    kits = []
    for f in u['carcols']:
        k, ok = read_carcols(f)
        if not ok:
            add('warn', 'META_INVALID', rel(f, paths), 'carcols.meta 不是合法的 XML，没法检查涂装 kit（游戏也可能读不进去）')
        kits += k
    variations = {}
    for f in u['carvariations']:
        variations.update(read_carvariations(f))

    # ytd cache
    ytd_cache = {}

    def ytd(stem):
        if stem not in ytd_cache:
            got, path = _load(u['ytd'].get(stem, []), read_ytd, u['ytd.xml'].get(stem, []), read_ytd_xml, add, paths)
            ytd_cache[stem] = (got or [], path)
            if path:
                gcache[path] = got or []
        return ytd_cache[stem]

    part_stems = {p for k in kits for p in k['parts']}
    models = set(meta_by_model)
    if not meta_by_model:
        # loose mod folder without vehicles.meta: a yft with a ytd of the same name is a vehicle;
        # other yfts are tuning / livery parts that use the car's texture dictionary
        for stem in list(u['yft']) + list(u['yft.xml']):
            base = stem[:-3] if stem.endswith('_hi') else stem
            if base not in part_stems and (base in u['ytd'] or base in u['ytd.xml']):
                models.add(base)

    for model in sorted(models):
        meta = meta_by_model.get(model)
        txd = (meta['txd'] if meta else model).lower()
        yft_stem = model if (model in u['yft'] or model in u['yft.xml']) else model + '_hi'
        info, yft_path = _load(u['yft'].get(yft_stem, []), read_yft, u['yft.xml'].get(yft_stem, []), read_yft_xml, add, paths)
        hi_info = None
        if yft_stem == model:
            hi_info, _ = _load(u['yft'].get(model + '_hi', []), read_yft, u['yft.xml'].get(model + '_hi', []),
                               read_yft_xml, add, paths)
        flags = meta['flags'] if meta else []
        has_flag = 'FLAG_HAS_LIVERY' in flags
        base_tex, base_path = ytd(txd)
        hi_tex, hi_path = ytd(txd + '+hi')
        if info is None:
            if meta and (u['ytd'].get(txd) or u['ytd.xml'].get(txd)) and has_flag:
                add('info', 'NO_YFT', where, f"'{model}' 有 FLAG_HAS_LIVERY 但这里找不到能读的 {model}.yft，只检查了贴图")
            if not base_tex:
                continue
        ywhere = rel(yft_path, paths) if yft_path else where
        shaders = info['shaders'] if info else []
        embedded = {t['name'].lower(): t for t in (info['embedded'] if info else [])}
        pool = {}
        for src, texs in (('ytd', base_tex), ('+hi.ytd', hi_tex)):
            for t in texs:
                pool.setdefault(t['name'].lower(), []).append((src, t))
        livery_idx = [i for i, s in enumerate(shaders) if any(k in s['samplers'] for k in LIVERY_SAMPLERS)]
        refs = _livery_refs(shaders)
        if hi_info:
            hi_refs = _livery_refs(hi_info['shaders'])
            if set(hi_refs) != set(refs):
                only_hi = sorted(set(hi_refs) - set(refs))
                only_lo = sorted(set(refs) - set(hi_refs))
                add('warn', 'HI_SAMPLER_DIFFERS', ywhere, f"'{model}' 的 {model}.yft 和 {model}_hi.yft 涂装层指向的贴图不一样"
                    f"（只在 _hi：{only_hi or '无'}；只在普通版：{only_lo or '无'}）：近看和远看的涂装会不同")
            for k, v in hi_refs.items():
                refs.setdefault(k, v)

        # 1. sampler texture exists
        for low, (sampler, name) in sorted(refs.items()):
            if low in pool or low in embedded or SHARED_NAMES.match(name):
                continue
            other = [s for s in u['ytd'] if s not in (txd, txd + '+hi') and any(
                t['name'].lower() == low for t in ytd(s)[0])]
            if other:
                add('warn', 'LIVERY_TEX_OTHER_YTD', ywhere, f"'{model}' 的 {sampler} 指向 '{name}'，它不在 {txd}.ytd，"
                    f"而在 {other[0]}.ytd：要有 txdRelationships 把两个字典连起来，不然涂装是空白/白色")
            else:
                add('error', 'LIVERY_TEX_MISSING', ywhere, f"'{model}' 的 {sampler} 指向 '{name}'，但 {txd}.ytd / "
                    f"{txd}+hi.ytd / yft 内嵌字典里都没有这张贴图：涂装不显示。贴图名字要和 shader 里的名字完全一样"
                    f"（字典里现有的涂装贴图：{', '.join(sorted(t for t in pool if LIVERYISH_RE.search(t))[:5]) or '无'}）", tex=low)

        # 2. livery layer and LODs
        baked = sorted({v for sh in shaders for k, v in sh['samplers'].items()
                        if k == 'DiffuseSampler' and SIGN_RE.match(v or '')})
        if info and has_flag and not livery_idx:
            extra = (f"。'{baked[0]}' 是当成车身主贴图（DiffuseSampler）用的，等于把涂装直接画在车身上（方法 C，固定涂装）"
                     if baked else '')
            add('warn', 'FLAG_NO_LIVERY_LAYER', ywhere, f"'{model}' 有 FLAG_HAS_LIVERY，但模型没有带涂装层的材质"
                f"（DiffuseSampler2，vehicle_paint3/4…）：换涂装不会有任何变化{extra}。要能换：车身材质改成 vehicle_paint3 并有 UVMap 1")
        elif info and baked and not livery_idx:
            add('info', 'BAKED_LIVERY', ywhere, f"'{model}' 把 '{baked[0]}' 当车身主贴图用（方法 C，固定涂装，不能切换）")
        if info and livery_idx and info['lods'].get('high'):
            hi_use = info['lods']['high'] & set(livery_idx)
            bad = [lod for lod in ('med', 'low', 'vlow')
                   if hi_use and info['lods'].get(lod) and not (info['lods'][lod] & set(livery_idx))]
            if bad:
                add('warn', 'LOD_NO_LIVERY', ywhere, f"'{model}' 的 {'/'.join(bad)} LOD 没有涂装层材质：开远一点涂装就不见了"
                    "（原版 polgauntlet 每级 LOD 都有 vehicle_paint3）。在 Blender 里给这几级的车身也用 vehicle_paint3/4 + UVMap 1")

        # 3. _sign_N numbering vs FLAG_HAS_LIVERY
        sign_refs = [(SIGN_RE.match(n), n) for _, (k, n) in refs.items() if k == 'DiffuseSampler2']
        sign_refs = [(m.group(1).lower(), int(m.group(2)), n) for m, n in sign_refs if m]
        for prefix, num, name in sign_refs:
            nums = sorted({int(SIGN_RE.match(t).group(2)) for t in pool
                           if SIGN_RE.match(t) and SIGN_RE.match(t).group(1).lower() == prefix})
            if num != 1:
                add('warn', 'SIGN_NOT_FIRST', ywhere, f"'{model}' 的 shader 用的是 '{name}'，不是 {prefix}_sign_1。"
                    "原版都是 shader 指 _sign_1、涂装 k 显示 _sign_(k+1)；_sign_0 或从 2 开始会怎样切换没验证过，最好改成 _sign_1 起算")
            if 0 in nums:
                add('warn', 'SIGN_ZERO', ywhere, f"'{model}' 的字典里有 {prefix}_sign_0。原版从 _sign_1 开始，_sign_0 会不会被当成一套涂装没验证")
            n_pos = [n for n in nums if n >= 1]
            if n_pos and n_pos != list(range(1, n_pos[-1] + 1)):
                missing = [n for n in range(1, n_pos[-1] + 1) if n not in n_pos]
                add('warn', 'SIGN_GAP', ywhere, f"'{model}' 的 {prefix}_sign_ 编号有缺口（缺 {missing[:6]}）。"
                    "社群说法是只认连续的编号，缺口后面的涂装可能切不到（未验证），把编号补成连续的")
            if len(n_pos) > 30:
                add('warn', 'SIGN_OVER_30', ywhere, f"'{model}' 有 {len(n_pos)} 张 _sign_N，FLAG_HAS_LIVERY 最多切 30 套（FiveM 文档）")
            if meta and not has_flag and len(n_pos) > 1:
                add('warn', 'SIGNS_NO_FLAG', ywhere, f"'{model}' 有 {len(n_pos)} 张 {prefix}_sign_N，但 vehicles.meta 没有 FLAG_HAS_LIVERY："
                    "只会一直显示 _sign_1，换不了涂装。要能换就加这个 flag（meta 部分见 fivem-vehicle-mod）")
            elif meta and not has_flag and len(n_pos) == 1:
                add('info', 'FIXED_LIVERY', ywhere, f"'{model}' 只有一张 {prefix}_sign_1 而且没有 FLAG_HAS_LIVERY：等于固定涂装（不能切换）")
            elif meta and has_flag and len(n_pos) <= 1:
                mod_kits = {k['name'].lower() for k in kits if k['livery_mods']}
                level = 'info' if mod_kits & {k.lower() for k in variations.get(model, [])} else 'warn'
                add(level, 'FLAG_ONE_SIGN', ywhere, f"'{model}' 有 FLAG_HAS_LIVERY，但字典里只有 {len(n_pos)} 张 {prefix}_sign_N，"
                    "菜单里换不了别的。新涂装照编号加 _sign_2、_sign_3…")
            firsts = [t for src, t in pool.get(f'{prefix}_sign_1', [])]
            others = [t for n in n_pos if n > 1 for src, t in pool.get(f'{prefix}_sign_{n}', [])]
            if firsts and others and max(firsts[0]['width'], firsts[0]['height']) <= 256 < max(
                    max(t['width'], t['height']) for t in others):
                add('info', 'SIGN_1_PLACEHOLDER', ywhere, f"'{model}' 的 {prefix}_sign_1 只有 {firsts[0]['width']}×{firsts[0]['height']}："
                    "第一套涂装是空白（无标志/便衣车）。车默认显示它；警用 job 设定 livery 时记得选对编号")
        if meta and has_flag and livery_idx and not sign_refs and info:
            names = ', '.join(n for _, (k, n) in refs.items())
            add('warn', 'FLAG_NO_SIGN_NAME', ywhere, f"'{model}' 有 FLAG_HAS_LIVERY，但涂装层贴图叫 '{names}'，"
                "不是 <名字>_sign_1：游戏按 _sign_N 找其他涂装，可能只有这一套")

        # 4. texture quality / memory of livery textures
        livery_names = {n for n in ({n for n in refs if n in pool} | {n for n in pool if LIVERYISH_RE.search(n)})
                        if not SHARED_NAMES.match(n)}
        total = 0.0
        for low in sorted(livery_names):
            for src, t in pool.get(low, []):
                total += tex_mib(t)
                _texture_checks(t, f"{txd}{'' if src == 'ytd' else '+hi'}.ytd", model, ywhere, add)
        for low in livery_names:
            srcs = {s for s, _ in pool.get(low, [])}
            if srcs == {'ytd', '+hi.ytd'}:
                add('warn', 'HI_DUPLICATE', ywhere, f"'{pool[low][0][1]['name']}' 同时在 {txd}.ytd 和 {txd}+hi.ytd：近看用 +hi 那张。"
                    "换涂装时两个字典都要换，不然近看还是旧涂装")
        for low in sorted(livery_names):
            twins = [s for s in u['ytd'] if s > txd and not s.endswith('+hi') and any(
                t['name'].lower() == low for t in ytd(s)[0])]
            if twins:
                add('info', 'DUPLICATE_SET', ywhere, f"'{pool[low][0][1]['name']}' 在 {txd}.ytd 和 {twins[0]}.ytd 都有："
                    "两个车型各带一份同样的涂装，内存算两次（共用的话可以用 txdRelationships，原车照 1:1 规则先问用户）")
                break
        if total > 48:
            add('warn', 'LIVERY_MEMORY', ywhere, f"'{model}' 的涂装贴图合计约 {total:.0f} MiB（含 mip）。ytd 是整个一起串流的，"
                "车一出现就全部载入；超过 48 MiB 很容易让别的贴图掉级、树和贴图消失。新做的涂装用 2048 DXT5；"
                "原车贴图照 1:1 规则不要自己压缩，报告给用户决定")
        elif total > 0:
            add('info', 'LIVERY_MEMORY', ywhere, f"'{model}' 的涂装贴图合计约 {total:.1f} MiB（含 mip）")
        scan = pool if all_textures else {k: v for k, v in pool.items() if k not in livery_names}
        for low, entries in scan.items():
            name = entries[0][1]['name']
            if JUNK_RE.search(name) and low not in refs and not _used_by(name, info, hi_info):
                add('warn', 'JUNK_TEXTURE', ywhere, f"{txd}.ytd 里有 '{name}'（{entries[0][1]['width']}×{entries[0][1]['height']}，"
                    f"约 {tex_mib(entries[0][1]):.1f} MiB）：像是设计软件的默认名、没被涂装层用到，多半是忘了删的草稿（删之前先问用户）")
        for low, t in embedded.items():
            _texture_checks(t, f'{yft_stem}.yft 内嵌', model, ywhere, add)

    # 5. VMT_LIVERY_MOD kits
    for kit in kits:
        mods = kit['livery_mods']
        if not mods and not kit['livery_names']:
            continue
        users = [m for m, ks in variations.items() if kit['name'].lower() in (k.lower() for k in ks)]
        if mods and kit['name'].lower() not in all_variation_kits:
            add('warn', 'LIVERY_KIT_UNUSED', where, f"kit '{kit['name']}' 有 {len(mods)} 个 VMT_LIVERY_MOD 涂装，但没有任何车在 "
                "carvariations.meta 的 <kits> 里用它：改装/涂装菜单看不到")
        for m in mods:
            stem = m['model'].lower()
            fs = all_livery_yfts.get(stem, [])
            local = [f for f in fs if f.startswith(udir + os.sep)]
            if not fs:
                add('error', 'LIVERY_MOD_YFT_MISSING', where, f"kit '{kit['name']}' 的涂装零件 '{m['model']}' 找不到 {m['model']}.yft："
                    "菜单里选了也没东西。涂装 yft 放进 stream/，名字和 modelName 一样")
                continue
            if not local:
                add('info', 'LIVERY_MOD_ELSEWHERE', where, f"'{m['model']}.yft' 在别的资源里（{rel(fs[0], paths)}），确认两个资源都会启动")
            bins = [f for f in fs if f.lower().endswith('.yft')]
            xmls = [f for f in fs if f.lower().endswith('.xml')]
            part, ppath = _load(bins, read_yft, xmls, read_yft_xml, lambda *a: None, paths)
            if part is None:
                continue
            emb = {t['name'].lower() for t in part['embedded']}
            for s in part['shaders']:
                name = s['samplers'].get('DiffuseSampler2')
                if name and name.lower() not in emb and not SHARED_NAMES.match(name):
                    add('error', 'LIVERY_MOD_TEX_MISSING', rel(ppath, paths), f"涂装零件 '{m['model']}' 的 DiffuseSampler2 = '{name}'，"
                        f"但它内嵌的贴图字典里没有这个名字（有：{', '.join(sorted(emb)) or '空'}）：装上这个涂装车身会是空白")
            if users:
                for user in users:
                    if 'FLAG_HAS_LIVERY' in meta_by_model.get(user, {}).get('flags', []):
                        add('info', 'LIVERY_BOTH_SYSTEMS', where, f"'{user}' 同时有 FLAG_HAS_LIVERY 和 VMT_LIVERY_MOD 涂装："
                            "两套系统会叠在一起（菜单分别用 SetVehicleLivery 和 SetVehicleMod 48）。原版 2023 后的警车只用 VMT_LIVERY_MOD")
                        break
        keys = [m['label'] for m in mods if m['label']] + kit['livery_names']
        missing = [k for k in keys if k.upper() not in labels and not VANILLA_LABEL.match(k)]
        if missing:
            add('warn', 'LABEL_NO_TEXT', where, f"kit '{kit['name']}' 的涂装名称 key 找不到 AddTextEntry（{', '.join(missing[:6])}"
                f"{'…' if len(missing) > 6 else ''}）：菜单会显示 NULL 或 key 本身。在 client 脚本加 AddTextEntry('{missing[0]}', 'LSPD 巡逻')；"
                "如果是从原版车抄来的 key（游戏自带文字）可以忽略。定义在别的资源里的话，把那个资源也一起给本脚本检查")


def _livery_refs(shaders):
    refs = {}
    for s in shaders:
        for k in LIVERY_SAMPLERS:
            name = s['samplers'].get(k)
            if name:
                refs.setdefault(name.lower(), (k, name))
    return refs


def _used_by(name, *infos):
    low = name.lower()
    return any(v.lower() == low for info in infos if info for s in info['shaders'] for v in s['samplers'].values())


def _texture_checks(t, src, model, where, add):
    w, h, f = t['width'], t['height'], t['format']
    name = t['name']
    if not (pow2(w) and pow2(h)):
        add('warn', 'TEX_NOT_POW2', where, f"'{name}'（{src}）是 {w}×{h}，不是 2 的次方：mip 会出问题、有的显卡会糊或报错。"
            "新做的涂装用 2048×2048；原车贴图照 1:1 规则只报告")
    if max(w, h) > 2048:
        add('warn', 'TEX_OVER_2048', where, f"'{name}'（{src}）是 {w}×{h} {f}，约 {tex_mib(t):.1f} MiB：涂装 4096 很吃内存，"
            "原版警车涂装是 1024–2048 DXT5。新做的在 4096 画、导出 2048；原车贴图照 1:1 规则只报告，用户要求才缩")
    if f in UNCOMPRESSED and max(w, h) > 256:
        add('warn', 'TEX_UNCOMPRESSED', where, f"'{name}'（{src}）是未压缩的 {f}（{w}×{h}，约 {tex_mib(t):.1f} MiB，是 DXT5 的 4 倍）："
            "导出时选 BC3/DXT5。原车贴图照 1:1 规则只报告")
    if f == 'BC7':
        add('info', 'TEX_BC7', where, f"'{name}'（{src}）是 BC7：CodeWalker 支持，但 Legacy 游戏里是否都正常没验证过；有问题就改存 DXT5")
    if (t['levels'] or 1) <= 1 and max(w, h) > 256:
        add('warn', 'TEX_NO_MIPS', where, f"'{name}'（{src}）{w}×{h} 只有 1 级 mip：近看清楚，远看会闪烁、锯齿，而且整张一直占内存。"
            "网上「mip 改成 1 修模糊」的做法不要用；导出时勾 Generate mipmaps")
    if JUNK_RE.search(name) or SPACE_RE.search(name):
        add('warn', 'TEX_JUNK_NAME', where, f"涂装贴图 '{name}'（{src}）名字像设计软件的默认名：游戏按名字找贴图，"
            "名字要和 shader 里的完全一样（如 <车名>_sign_2）")


def main():
    ap = argparse.ArgumentParser(description='Read-only livery checker for FiveM add-on vehicles')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--all-textures', action='store_true', help='also flag junk names on non-livery textures')
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    findings = check(args.paths, args.all_textures)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                print(f"{icons[level]} {x['code']}: [{x['file']}] {x['message']}")
        if not findings:
            print('✓ 没发现问题')
        counts = {lv: sum(1 for f in findings if f['level'] == lv) for lv in ('error', 'warn', 'info')}
        print(f"共 {counts['error']} 个错误、{counts['warn']} 个警告、{counts['info']} 个提示")
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
