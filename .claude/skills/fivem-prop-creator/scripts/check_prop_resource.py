#!/usr/bin/env python3
"""Check a FiveM prop resource (custom .ydr/.yft + .ytyp + .ytd) before it goes on the server.

Usage:
    py -3 -I check_prop_resource.py <resource | folder of resources | export folder> [more] [--json]

Standard library only, read-only (never writes, renames or decrypts). Exit code 1 when
errors are found. Reads compiled RSC7 files directly through rsc_probe.py (texture size /
format / mips, YDR LOD triangles / embedded collision, YTYP archetypes) and Sollumz /
CodeWalker XML exports (.ytyp.xml, .ydr.xml, .yft.xml, .ytd.xml, .ymap.xml) when present.

Sources (see ../references/sources.md): FiveM LoadStreamingFile.cpp ParseBaseName (DLC_ITYP_REQUEST
matches the .ytyp by file name only), ResourceStreamComponent.cpp (16 / 48 MiB), ResourcesTest.cpp
(this_is_a_map only reloads the map store), Sollumz 2.9 ytyp.py / flags.py (special attributes,
flag bits, default lodDist 200 / hdTextureDist 100), Sollumz collision docs (Flag Preset on the
GeometryBVH), Cfx asset-escrow doc (FXAP), and vanilla Legacy props measured with CodeWalker.Core
(budgets in ../references/lods-textures-budgets.md). Budget findings are info: they compare with
what Rockstar shipped, they are not engine limits.

Not checked: .yft internals (fragment layout not probed - use XML), collision flags inside
binary bounds (XML only), which vanilla texture dictionaries exist, behaviour in game.
"""
import argparse
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rsc_probe as rp  # noqa: E402

MIB = 1024 * 1024
MODEL_EXT = ('.ydr', '.yft', '.ydd')
RSC_EXT = ('.ydr', '.yft', '.ydd', '.ytd', '.ytyp', '.ybn', '.ycd', '.ymap')
SOURCE_EXT = ('.blend', '.blend1', '.fbx', '.obj', '.dds', '.png', '.tga', '.psd', '.spp', '.max', '.mb', '.ma', '.jpg')
XML_KINDS = ('.ytyp.xml', '.ydr.xml', '.yft.xml', '.ytd.xml', '.ymap.xml', '.ydd.xml', '.ybn.xml')

# Sollumz ArchetypeFlags: flagN = 1 << (N - 1)
F_STATIC, F_HAS_ANIM, F_UV_ANIM, F_DYNAMIC, F_DOOR_PHYSICS = 1 << 5, 1 << 9, 1 << 10, 1 << 17, 1 << 26
DOOR_ATTRS = {5: 'Garage Door', 7: 'Normal Door', 8: 'Sliding Door', 9: 'Barrier Door',
              10: 'Sliding Vertical Door', 12: 'Rail Crossing Barrier Door'}   # Sollumz SpecialAttribute
# (max bsRadius, label, High tris top of the vanilla band, archetype lodDist top of the band)
BANDS = ((0.35, '手持', 450, 30), (1.5, '小道具/家具', 2300, 140), (4.0, '大型街道道具', 3700, 260),
         (float('inf'), '超大道具', 5300, 260))
SOLLUMZ_DEFAULT_LOD, SOLLUMZ_DEFAULT_HD = 200.0, 100.0
MERGE_CODES = {'LODDIST_DEFAULT', 'LODDIST_VS_SIZE', 'LODDIST_SHORT', 'FLAGS_ZERO', 'TXD_NOT_LOCAL', 'CLIP_NOT_LOCAL'}
# Rockstar name prefixes (base game + DLC packs); a streamed model with such a name and no ytyp is
# probably a replacement of the vanilla model, which needs no ytyp. Heuristic only.
VANILLA_PREFIXES = ('prop_', 'p_', 'v_', 'des_', 'hei_', 'apa_', 'bkr_', 'ba_', 'ex_', 'imp_', 'gr_', 'sm_', 'xm_',
                    'ch_', 'h4_', 'tr_', 'sf_', 'sum_', 'vw_', 'lr_', 'lux_', 'ind_', 'csx_', 'w_', 'xs_', 'stt_',
                    'sr_', 'as_', 'reh_', 'tr_', 'm23_', 'm24_', 'bzzz_v_', 'ng_', 'cs_', 'hw1_', 'ss1_', 'dt1_')


def band(radius):
    for top, label, tris, lod in BANDS:
        if radius < top:
            return label, tris, lod
    return BANDS[-1][1:]


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def parse_base_name(path):
    """FiveM LoadStreamingFile.cpp ParseBaseName: text after the last '/', cut at the last '.'."""
    base = path.replace('\\', '/').rsplit('/', 1)[-1]
    return base[:base.rfind('.')] if '.' in base else base


def glob_to_re(pattern):
    """Cfx manifest globbing: '*' within one folder, '**' across folders; brackets are literal (assumed)."""
    out, i = '', 0
    while i < len(pattern):
        if pattern.startswith('**/', i):
            out += '(?:.*/)?'
            i += 3
        elif pattern.startswith('**', i):
            out += '.*'
            i += 2
        elif pattern[i] == '*':
            out += '[^/]*'
            i += 1
        elif pattern[i] == '?':
            out += '[^/]'
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(out + r'\Z')


def find_units(paths):
    """Resources (folders with a manifest) plus, per scanned path, the loose files outside any resource."""
    units, claimed = [], set()
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            units.append({'root': os.path.dirname(p), 'manifest': None, 'files': [p], 'name': os.path.basename(p)})
            claimed.add(p)
            continue
        loose = []
        for root, dirs, fs in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            man = next((f for f in ('fxmanifest.lua', '__resource.lua') if f in fs), None)
            if man:
                files = []
                for r2, d2, f2 in os.walk(root):
                    d2[:] = [d for d in d2 if not d.startswith('.')]
                    files += [os.path.join(r2, f) for f in f2]
                units.append({'root': root, 'manifest': os.path.join(root, man), 'files': files,
                              'name': os.path.basename(root)})
                claimed.update(files)
                dirs[:] = []
                continue
            loose += [os.path.join(root, f) for f in fs]
        loose = [f for f in loose if f not in claimed]
        if loose:
            units.append({'root': p, 'manifest': None, 'files': loose, 'name': os.path.basename(p) + '（无 manifest）'})
    return units


def relp(unit, path):
    return os.path.relpath(path, unit['root']).replace(os.sep, '/')


def label(unit, path):
    return f"{unit['name']}/{relp(unit, path)}" if unit['manifest'] else relp(unit, path) if path != unit['root'] else unit['name']


def streamed(unit, path):
    parts = relp(unit, path).lower().split('/')[:-1]
    return any(x.startswith('stream') for x in parts) or unit['manifest'] is None


def legacy_stream(unit, path):
    return 'stream_enhanced' not in relp(unit, path).lower().split('/')[:-1]


def xml_kind(low):
    return next((k for k in XML_KINDS if low.endswith(k)), None)


def stem_of(path):
    low = os.path.basename(path).lower()
    k = xml_kind(low)
    return low[:-len(k)] if k else os.path.splitext(low)[0]


def xval(el, tag, default=None):
    child = el.find(tag)
    if child is None:
        return default
    v = child.get('value')
    return v if v is not None else (child.text or '').strip()


def xnum(el, tag, default=0.0, cast=float):
    try:
        return cast(xval(el, tag, default))
    except (TypeError, ValueError):
        return default


def tex_checks(add, where, textures, is_prop=True):
    """One finding per problem kind and file (a pack with 40 uncompressed textures is one line)."""
    groups = {}

    def note(code, t):
        groups.setdefault(code, []).append(f"{t['name'] or '?'} {t['width']}×{t['height']} {t['format']}")

    for t in textures:
        w, h, mips = t['width'], t['height'], t['mips']
        if w <= 0 or h <= 0 or w & (w - 1) or h & (h - 1):
            note('TEX_NOT_POW2', t)
        if max(w, h) > 2048:
            note('TEX_TOO_BIG', t)
        elif is_prop and max(w, h) > 1024:
            note('TEX_LARGE', t)
        if not t['compressed'] and w * h > 512 * 256:
            note('TEX_UNCOMPRESSED', t)
        if mips <= 1 and max(w, h) > 64:
            note('TEX_NO_MIPS', t)
    text = {
        'TEX_NOT_POW2': ('warn', '不是 2 的次方（256/512/1024…）。Sollumz FAQ 要求 2 的次方的 DDS；不是的话 mipmap 和显示可能出错（游戏内表现未验证）'),
        'TEX_TOO_BIG': ('warn', '超过 2048（Sollumz FAQ 建议最大 2048；原版道具最大 1024）'),
        'TEX_LARGE': ('info', '大于 1024。原版道具几乎都是 256²，大面 512²，只有货柜、树、摩天轮用到 1024²（实测）'),
        'TEX_UNCOMPRESSED': ('warn', '没压缩（A8R8G8B8 这类，显存是 DXT1 的 8 倍）。原版只在 256×4 调色板和电视屏幕用未压缩格式；'
                             '不透明用 DXT1，有透明用 DXT5，法线可用 BC5。要不要重新压缩由你决定，脚本不改文件'),
        'TEX_NO_MIPS': ('warn', '没有 mipmap，远处会闪烁、浪费串流。原版每张贴图都有完整 mip 链'),
    }
    for code, items in groups.items():
        level, why = text[code]
        more = f' 等 {len(items)} 张' if len(items) > 3 else ''
        add(level, code, where, f"贴图 {'; '.join(items[:3])}{more}：{why}")


def tris_xml(drawable, tag):
    total = 0
    for item in drawable.findall(f'{tag}/Item'):
        for geo in item.findall('Geometries/Item'):
            data = geo.findtext('IndexBuffer/Data') or ''
            total += len(data.split()) // 3
    return total


def xml_textures(parent):
    out = []
    for it in parent.findall('Item'):
        fmt = (it.findtext('Format') or '').replace('D3DFMT_', '').strip()
        out.append({'name': (it.findtext('Name') or '').strip(), 'width': int(xnum(it, 'Width', 0)),
                    'height': int(xnum(it, 'Height', 0)), 'format': fmt or '?', 'mips': int(xnum(it, 'MipLevels', 0)),
                    'compressed': fmt.upper().startswith(('DXT', 'ATI', 'BC'))})
    return out


def parse_drawable_xml(path):
    root = ET.parse(path).getroot()
    d = root if root.tag == 'Drawable' else root.find('.//Drawable')
    if d is None:
        return None
    lods = {k: {'tris': tris_xml(d, tag)} for k, tag in (('high', 'DrawableModelsHigh'), ('med', 'DrawableModelsMedium'),
                                                          ('low', 'DrawableModelsLow'), ('vlow', 'DrawableModelsVeryLow'))}
    td = d.find('ShaderGroup/TextureDictionary')
    bounds = root.findall('.//Bounds') + [x for x in root.iter() if x.get('type') in ('GeometryBVH', 'Geometry')]
    bvh_no_flags, heavy = [], []
    for el in root.iter():
        if el.get('type') not in ('GeometryBVH', 'Geometry'):
            continue
        f1, f2 = el.find('CompositeFlags1'), el.find('CompositeFlags2')
        if f1 is not None or f2 is not None:
            txt = ' '.join((x.text or '').strip() for x in (f1, f2) if x is not None).strip()
            if not txt or txt.upper().replace(',', ' ').split() in (['NONE'], ['NONE', 'NONE']):
                bvh_no_flags.append(el)
        polys = el.find('Polygons')
        if polys is not None and len(list(polys)) > 300:
            heavy.append(len(list(polys)))
    return {'lods': lods, 'lod_dist': {k: xnum(d, f'LodDist{t}', 9998.0) for k, t in
                                       (('high', 'High'), ('med', 'Med'), ('low', 'Low'), ('vlow', 'Vlow'))},
            'bs_radius': xnum(d, 'BoundingSphereRadius', 0.0), 'bound': 'xml' if bounds else None,
            'textures': xml_textures(td) if td is not None else [], 'bvh_no_flags': len(bvh_no_flags),
            'heavy_polys': heavy, 'fragment': root.tag == 'Fragment'}


def sig(a):
    return (round(a['lod_dist'], 2), a['flags'], a['special_attribute'], a['txd_hash'], a['clip_hash'], a['asset_type'])


def looks_vanilla(name):
    # also Rockstar map-area pieces such as id1_32_land01, kt1_rd_02, cs6_roadsc26, sc1_19_sheriff
    return name.startswith(VANILLA_PREFIXES) or re.match(r'[a-z]{2,3}\d{1,2}_', name) is not None


def merge_similar(findings):
    """Fold repeated per-archetype notes of one ytyp into one line; drop exact duplicates."""
    out, groups, seen = [], {}, set()
    for f in findings:
        key = (f['level'], f['code'], f['file'], f['message'])
        if key in seen:
            continue
        seen.add(key)
        if f['code'] in MERGE_CODES and f.get('subject'):
            groups.setdefault((f['code'], f['file']), []).append(f)
        else:
            out.append(f)
    for (_, _), items in groups.items():
        first = dict(items[0])
        if len(items) > 3:
            names = ', '.join(x['subject'] for x in items[1:6])
            first['message'] += f"（这个文件里还有 {len(items) - 1} 个同样情况，例如 {names}{'…' if len(items) > 6 else ''}）"
            out.append(first)
        else:
            out += items
    for f in out:
        f.pop('subject', None)
    return out


def check(paths):
    findings = []

    def add(level, code, where, msg, subject=None):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg, 'subject': subject})

    units = find_units(paths)
    entries = []        # (unit, abs path, lower basename)
    for u in units:
        entries += [(u, f, os.path.basename(f).lower()) for f in u['files']]

    # ---------- name tables ----------
    hash_names = {}
    stems = {}          # stem -> list of (unit, path, kind) kind = ext or xml kind
    for u, f, low in entries:
        k = xml_kind(low) or os.path.splitext(low)[1]
        if k in RSC_EXT or k in XML_KINDS:
            if k in XML_KINDS or streamed(u, f):
                s = stem_of(f)
                stems.setdefault(s, []).append((u, f, k))
                hash_names[rp.joaat(s)] = s

    def have(stem, *kinds):
        return [x for x in stems.get(stem, []) if x[2] in kinds]

    # ---------- archetypes ----------
    archetypes = []     # dicts: name (or None), hash fields, unit, file, xml, ytyp_stem
    mlo_ytyp_stems = set()
    for u, f, low in entries:
        if low.endswith('.ytyp') and streamed(u, f):
            hdr = rp.read_header(f)
            if hdr['kind'] != 'rsc':
                continue
            try:
                y = rp.read_ytyp(f)
            except (rp.ProbeError, struct.error, IndexError, OSError) as e:
                add('info', 'PARSE_FAILED', label(u, f), f'读不懂这个 ytyp（{e}），跳过 archetype 检查。用 CodeWalker 打开确认')
                continue
            if y['mlo']:
                mlo_ytyp_stems.add(stem_of(f))
            for a in y['archetypes']:
                a = dict(a, unit=u, file=f, xml=False, ytyp_stem=stem_of(f),
                         name=hash_names.get(a['name_hash']), asset_name=hash_names.get(a['asset_name_hash']),
                         txd=hash_names.get(a['txd_hash']), clip=hash_names.get(a['clip_hash']),
                         ddict=hash_names.get(a['drawable_dict_hash']))
                archetypes.append(a)
        elif low.endswith('.ytyp.xml'):
            try:
                root = ET.parse(f).getroot()
            except ET.ParseError as e:
                add('error', 'XML_INVALID', label(u, f), f'不是合法的 XML：{e}')
                continue
            for it in root.findall('archetypes/Item'):
                typ = it.get('type', '')
                if typ == 'CMloArchetypeDef':
                    mlo_ytyp_stems.add(stem_of(f))
                nm = (it.findtext('name') or '').strip().lower()

                def h(tag):
                    t = (it.findtext(tag) or '').strip().lower()
                    return (rp.joaat(t) if t else 0), (t or None)
                txd_h, txd = h('textureDictionary')
                clip_h, clip = h('clipDictionary')
                dd_h, dd = h('drawableDictionary')
                at = (it.findtext('assetType') or '').strip().upper().replace('ASSET_TYPE_', '')
                archetypes.append({'name': nm, 'name_hash': rp.joaat(nm), 'asset_name': (it.findtext('assetName') or '').strip().lower(),
                                   'asset_name_hash': rp.joaat((it.findtext('assetName') or '').strip()),
                                   'lod_dist': xnum(it, 'lodDist'), 'flags': int(xnum(it, 'flags', 0, int)),
                                   'special_attribute': int(xnum(it, 'specialAttribute', 0, int)),
                                   'bs_radius': xnum(it, 'bsRadius'), 'hd_texture_dist': xnum(it, 'hdTextureDist'),
                                   'txd_hash': txd_h, 'txd': txd, 'clip_hash': clip_h, 'clip': clip,
                                   'drawable_dict_hash': dd_h, 'ddict': dd, 'asset_type': at or 'DRAWABLE',
                                   'mlo': typ == 'CMloArchetypeDef', 'unit': u, 'file': f, 'xml': True,
                                   'ytyp_stem': stem_of(f)})
    by_name = {}
    for a in archetypes:
        by_name.setdefault(a['name_hash'], []).append(a)

    # ---------- per unit: manifest, stream content ----------
    requested_stems = set()
    for u in units:
        files = u['files']
        rels = {relp(u, f).lower(): f for f in files}
        streamed_files = [f for f in files if streamed(u, f)]
        uname = u['name']
        if not u['manifest']:
            game = [f for f in files if f.lower().endswith(RSC_EXT) and 'stream' in relp(u, f).lower().split('/')[:-1]]
            if game:
                add('error', 'NO_MANIFEST', uname, f'有 stream 文件夹和游戏文件（{relp(u, game[0])} 等），但没有 fxmanifest.lua，伺服器不会把它当资源载入')
            text = ''
        else:
            with open(u['manifest'], encoding='utf-8', errors='replace') as fh:
                text = strip_lua_comments(fh.read())
        data_files = re.findall(r"data_file\s*\(?\s*['\"]([A-Za-z0-9_]+)['\"]\s*\)?\s*\(?\s*['\"]([^'\"]+)['\"]", text)
        ytyps_here = {stem_of(f): f for f in streamed_files if f.lower().endswith('.ytyp')}
        for t, p in data_files:
            if t.upper() != 'DLC_ITYP_REQUEST':
                continue
            pl = p.replace('\\', '/').lower().strip()
            if any(c in pl for c in '*?'):
                rx = glob_to_re(pl)
                hit = [r for r in rels if rx.match(r)]
                if not hit:
                    add('warn', 'ITYP_REQUEST_GLOB', uname, f"data_file 'DLC_ITYP_REQUEST' '{p}' 用了通配符，但匹配不到任何文件（例如 '*ytyp.' 应该写成 '*.ytyp'）。这些 ytyp 等于没有载入（DLC_ITYP_REQUEST 的通配符行为未在游戏里验证）")
                for r in hit:
                    requested_stems.add(stem_of(r))
                continue
            st = parse_base_name(pl)
            requested_stems.add(st)
            if st in mlo_ytyp_stems:
                add('error', 'ITYP_REQUEST_MLO', uname, f"DLC_ITYP_REQUEST '{p}' 载入的是放 MLO 的 ytyp。这个伺服器上这样会让客户端闪退：删掉这行，MLO 的 ytyp 交给 .ymf")
            if st in ytyps_here:
                if relp(u, ytyps_here[st]).lower() != pl and '/' in pl:
                    add('info', 'ITYP_REQUEST_PATH', uname, f"DLC_ITYP_REQUEST 写的是 '{p}'，文件其实在 {relp(u, ytyps_here[st])}。FiveM 只看文件名（LoadStreamingFile.cpp ParseBaseName），能用；想整齐可以改成实际路径")
            elif have(st, '.ytyp'):
                add('info', 'ITYP_REQUEST_OTHER', uname, f"DLC_ITYP_REQUEST '{p}' 的 {st}.ytyp 在别的资源里串流（{label(*have(st, '.ytyp')[0][:2])}）。FiveM 按文件名找，能用，但两个资源都要启动")
            elif '/' not in pl:
                add('info', 'ITYP_REQUEST_EXTERNAL', uname, f"DLC_ITYP_REQUEST '{p}' 没写路径，应该是别的资源串流的 ytyp；确认那个资源有启动")
            else:
                add('error', 'ITYP_REQUEST_MISSING', uname, f"DLC_ITYP_REQUEST '{p}' 找不到 {st}.ytyp（这里和其他扫描的资源都没有）。道具会生成失败或隐形")
        if u['manifest']:
            has_ymf = any(f.lower().endswith('.ymf') for f in streamed_files)
            ymaps = [f for f in streamed_files if f.lower().endswith('.ymap')]
            if ymaps and not re.search(r'\bthis_is_a_map\b', text):
                add('warn', 'NO_THIS_IS_A_MAP', uname, "stream 里有 .ymap，但 fxmanifest 没写 this_is_a_map 'yes'（加载时要重载地图存储，ymap 才会出现）")
            if re.search(r'\bthis_is_a_map\b', text) and not ymaps:
                add('info', 'MAP_FLAG_NOT_NEEDED', uname, "写了 this_is_a_map，但没有 .ymap。FiveM 源码里它只负责重载地图存储（ymap）；只给脚本生成的道具库不需要它（留着无害）")
            if ymaps and ytyps_here and not has_ymf:
                add('info', 'YMAP_NO_YMF', uname, '有 ymap 放自制道具，但没有 _manifest.ymf。Cfx 教程 part 4 用 CodeWalker Tools > Manifest Generator 生成它，ymap 里的道具才会正确加载')
        # ytyp loaded at all?
        for st, f in ytyps_here.items():
            if st in mlo_ytyp_stems:
                continue
            own = [a for a in archetypes if a['file'] == f]
            custom = any(have(a['name'] or '', *MODEL_EXT) for a in own)
            if st not in requested_stems and custom and u['manifest']:
                has_ymf = any(x.lower().endswith('.ymf') for x in streamed_files)
                if has_ymf:
                    add('info', 'ITYP_ONLY_YMF', label(u, f), f"{st}.ytyp 没有 DLC_ITYP_REQUEST，只靠 .ymf：ymap 放的道具可以，脚本 CreateObject 生成的可能看不到（未验证），要生成就加 data_file 'DLC_ITYP_REQUEST' 'stream/{st}.ytyp'")
                else:
                    add('warn', 'ITYP_NOT_REQUESTED', label(u, f), f"{st}.ytyp 放着自制道具，但 fxmanifest 没有 data_file 'DLC_ITYP_REQUEST' 'stream/{st}.ytyp'，也没有 .ymf。道具会生成失败或隐形")
        # loose files in stream
        escrowed = 0
        for f in streamed_files:
            low = os.path.basename(f).lower()
            r = label(u, f)
            in_stream = any(x.startswith('stream') for x in relp(u, f).lower().split('/')[:-1])
            if low.endswith('.xml') and in_stream:
                add('error', 'XML_IN_STREAM', r, 'XML 放在 stream 里不会被加载。用 Sollumz 导出成二进制，或用 CodeWalker 导入（改扩展名不是转换）')
                continue
            if low.endswith(SOURCE_EXT) and u['manifest']:
                add('warn', 'SOURCE_IN_STREAM', r, '源文件/散装贴图放在 stream 里不会被游戏使用，只会被下载。贴图要打包进 .ytd 或嵌入模型')
                continue
            if not low.endswith(RSC_EXT):
                continue
            base = os.path.basename(f)
            if ' ' in base:
                add('warn', 'NAME_CASE', r, f"文件名 '{base}' 有空格。FiveM 按文件名串流，名字要和 archetype 一致，统一小写、不要空格")
            elif base != base.lower():
                add('info', 'NAME_CASE', r, f"文件名 '{base}' 有大写。哈希不分大小写所以一般能用，但统一小写比较不会和 archetype 名搞混")
            hdr = rp.read_header(f)
            if hdr['kind'] == 'fxap':
                escrowed += 1
                continue
            if hdr['kind'] != 'rsc':
                add('warn', 'NOT_RSC7', r, '开头不是 RSC7（也不是 FXAP 加密），不像编译好的 GTA 文件：可能是改了扩展名的 XML、缺了文件头的原始数据或损坏。用 CodeWalker 打开确认')
                continue
            size, what = max((hdr['virt'], '虚拟'), (hdr['phys'], '物理（显存）'))
            if size > 48 * MIB:
                add('error', 'ASSET_OVER_48MIB', r, f'{what}内存 {size / MIB:.1f} MiB，超过 48 MiB。FXServer 会警告“一定会”出串流问题（模型不加载/不显示）')
            elif size > 16 * MIB:
                add('warn', 'ASSET_OVER_16MIB', r, f'{what}内存 {size / MIB:.1f} MiB，超过 FXServer 16 MiB 警告线（按 RSC 头算，和 FXServer 同一公式）')
            elif (low.endswith(('.ydr', '.yft')) and hdr['phys'] > 2 * MIB) or (low.endswith('.ytd') and hdr['phys'] > 4 * MIB):
                add('info', 'PROP_HEAVY', r, f"物理内存 {hdr['phys'] / MIB:.1f} MiB。原版街道道具通常 < 1 MiB，最大的货柜约 3 MiB（实测，经验值）")
        if escrowed:
            add('info', 'ESCROWED', uname, f'{escrowed} 个文件是 Cfx Asset Escrow 加密（开头 FXAP）：内容、大小、LOD 都看不到，只能在有授权的伺服器 key 上用。不要尝试解密')

    # ---------- duplicates ----------
    seen = {}
    for u, f, low in entries:
        if low.endswith(RSC_EXT) and u['manifest'] and streamed(u, f) and legacy_stream(u, f):
            seen.setdefault(low, []).append(label(u, f))
    for name, where in seen.items():
        if len(where) > 1:
            add('error', 'DUPLICATE_ASSET', where[0], f"'{name}' 出现在 {len(where)} 个地方（{', '.join(where[:4])}），只有一个会生效")
    owners = {}
    for a in archetypes:
        owners.setdefault(a['name_hash'], {}).setdefault(a['ytyp_stem'], a)
    dup_groups = {}
    for hsh, by_stem in owners.items():
        if len(by_stem) > 1:
            recs = list(by_stem.values())
            same = all(sig(r) == sig(recs[0]) for r in recs)
            dup_groups.setdefault((tuple(sorted(by_stem)), same), []).append(hash_names.get(hsh, f'{hsh:#010x}'))
    for (stems_, same), names in dup_groups.items():
        where = ', '.join(f'{x}.ytyp' for x in stems_)
        ex = ', '.join(names[:5]) + (f' 等 {len(names)} 个' if len(names) > 5 else '')
        if same:
            add('warn', 'ARCHETYPE_DUPLICATE', where, f"{ex} 在 {where} 里重复定义（内容一样，暂时无害，但只有最后载入的那份生效，以后改其中一份会出怪问题）。删掉重复的 ytyp 或那几条")
        else:
            add('warn', 'ARCHETYPE_DUPLICATE', where, f"{ex} 在 {where} 里重复定义，而且 lodDist/flags/贴图字典不一样：只有最后载入的那份生效，道具表现会随载入顺序变")

    # ---------- archetype checks ----------
    anonymous = {}
    for a in archetypes:
        if a['mlo']:
            continue
        u, where = a['unit'], label(a['unit'], a['file'])
        nm = a['name']
        if nm is None:
            anonymous.setdefault(where, []).append(a)
            continue
        if a['name_hash'] != a['asset_name_hash'] and a['asset_type'] != 'DRAWABLEDICTIONARY':
            add('error', 'NAME_MISMATCH', where, f"archetype '{nm}' 的 assetName 是 '{a['asset_name'] or hex(a['asset_name_hash'])}'，两者要一样（Sollumz Auto-Create 会设成一样，手改容易弄坏）")
        at = a['asset_type']
        want = {'DRAWABLE': ('.ydr', '.ydr.xml'), 'FRAGMENT': ('.yft', '.yft.xml')}.get(at)
        if want and not have(nm, *want):
            other = have(nm, *MODEL_EXT)
            if other:
                add('error', 'ASSET_TYPE_MISMATCH', where, f"archetype '{nm}' 的 assetType 是 {at}，但模型是 {other[0][2]}。ydr 用 ASSET_TYPE_DRAWABLE，yft 用 ASSET_TYPE_FRAGMENT")
            else:
                add('error' if a['xml'] else 'warn', 'ARCHETYPE_NO_MODEL', where, f"archetype '{nm}' 找不到同名的 {want[0]}（扫描的资源里都没有）。生成会失败或隐形，除非模型在别的资源")
        if at == 'DRAWABLEDICTIONARY' and a['drawable_dict_hash'] and not have(a['ddict'] or '', '.ydd', '.ydd.xml'):
            add('warn', 'YDD_MISSING', where, f"archetype '{nm}' 指向 drawable dictionary '{a['ddict'] or hex(a['drawable_dict_hash'])}'，但没有这个 .ydd")
        lod, hd, flags, attr, rad = a['lod_dist'], a['hd_texture_dist'], a['flags'], a['special_attribute'], a['bs_radius']
        blabel, btris, blod = band(rad)
        if lod <= 0:
            add('error', 'LODDIST_ZERO', where, f"archetype '{nm}' 的 lodDist 是 {lod:g}，道具会一直看不到")
        elif abs(lod - SOLLUMZ_DEFAULT_LOD) < 0.01 and abs(hd - SOLLUMZ_DEFAULT_HD) < 0.01:
            add('info', 'LODDIST_DEFAULT', where, f"archetype '{nm}' 的 lodDist 200 / hdTextureDist 100 正好是 Sollumz 预设值，像是没调过。原版{blabel}（bsRadius {rad:.2f} m）大约 lodDist ≤ {blod}，手持道具 10–30", nm)
        elif lod > 500 and rad < 5:
            add('warn', 'LODDIST_HIGH', where, f"archetype '{nm}' lodDist {lod:g} m，但 bsRadius 只有 {rad:.2f} m。原版最远的 12 m 树也只有 260 m，太远会一直占串流")
        elif lod > 2 * blod:
            add('info', 'LODDIST_VS_SIZE', where, f"archetype '{nm}' lodDist {lod:g} m，原版{blabel}一般 ≤ {blod} m（实测，经验值）", nm)
        elif lod < 10 and rad >= 0.35:
            add('info', 'LODDIST_SHORT', where, f"archetype '{nm}' lodDist 只有 {lod:g} m，走近才会出现", nm)
        if flags & F_STATIC and flags & F_DYNAMIC:
            add('warn', 'STATIC_AND_DYNAMIC', where, f"archetype '{nm}' 同时勾了 Static 和 Dynamic。可推动的道具只勾 Dynamic；Static 只给永远不动的 MLO 家具")
        if at == 'FRAGMENT' and not flags & F_DYNAMIC:
            add('warn', 'FRAGMENT_NOT_DYNAMIC', where, f"archetype '{nm}' 是 fragment（yft），但没勾 Dynamic（flag 18）。Sollumz prop-setup：物理/会断的道具必须 Dynamic")
        if flags == 0:
            add('info', 'FLAGS_ZERO', where, f"archetype '{nm}' flags 是 0。原版街道道具勾 Dynamic(18) + 不提供掩体(23/24) + Use Ambient Scale(30)；MLO 家具勾 Static(6)。按用途选", nm)
        if attr in DOOR_ATTRS and (not flags & F_DYNAMIC or not flags & F_DOOR_PHYSICS):
            add('warn', 'DOOR_FLAGS', where, f"archetype '{nm}' 的 special attribute 是 {DOOR_ATTRS[attr]} ({attr})，但没同时勾 Dynamic(18) 和 Enable Door Physics(27)，门不会动（Cfx 教程 part 8）")
        if flags & F_DOOR_PHYSICS and attr == 0:
            add('info', 'DOOR_ATTR_ZERO', where, f"archetype '{nm}' 勾了 Enable Door Physics，但 special attribute 是 0。原版 v_ilev_bl_door_l 和大门就是这样；Sollumz 文档说这样旗标无效——两种说法冲突，游戏里测一下，或照 Cfx part 8 设 7/8/10/5")
        if flags & (F_HAS_ANIM | F_UV_ANIM) and not a['clip_hash']:
            add('error', 'ANIM_NO_CLIP', where, f"archetype '{nm}' 勾了 Has Anim / UV Anims，但没有 clip dictionary，动画不会播")
        if a['clip_hash']:
            if not flags & (F_HAS_ANIM | F_UV_ANIM):
                add('warn', 'CLIP_NO_FLAG', where, f"archetype '{nm}' 设了 clip dictionary，但没勾 Has Anim(10) 或 UV Anims(11)（再加 Auto Start Anim(20) 才会自动播）")
            if not have(a['clip'] or '', '.ycd'):
                add('info', 'CLIP_NOT_LOCAL', where, f"archetype '{nm}' 的 clip dictionary '{a['clip'] or hex(a['clip_hash'])}' 没有本地 .ycd（原版字典如 v_industrial 也可以）", nm)
        # textures
        if a['txd_hash'] and not have(a['txd'] or '', '.ytd', '.ytd.xml'):
            embedded = a['txd_hash'] == a['name_hash']
            if not embedded:
                add('info', 'TXD_NOT_LOCAL', where, f"archetype '{nm}' 的贴图字典 '{a['txd'] or hex(a['txd_hash'])}' 不在这里，应该是原版共享字典；不是的话道具会没贴图", nm)

    for where, recs in anonymous.items():
        in_mlo_ytyp = recs[0]['ytyp_stem'] in mlo_ytyp_stems   # interiors list many vanilla models by name
        serious = not in_mlo_ytyp and any(r['asset_type'] in ('DRAWABLE', 'FRAGMENT') for r in recs)
        add('warn' if serious else 'info', 'ARCHETYPE_UNNAMED', where,
            f'有 {len(recs)} 个 archetype 的名字（哈希）对不上任何扫描到的模型文件，例如 {recs[0]["name_hash"]:#010x}。模型可能没放进来、在别的资源，或者是原版名字；生成这些道具会失败')

    # ---------- models ----------
    map_units = {}      # resources that place a map (ymap / MLO / loose map collision)
    for u in units:
        lows = [os.path.basename(x).lower() for x in u['files']]
        model_stems = {stem_of(x) for x in lows if x.endswith(MODEL_EXT)}
        map_units[id(u)] = any(x.endswith(('.ymap', '.ymap.xml')) for x in lows) \
            or any(a['unit'] is u and a['mlo'] for a in archetypes) \
            or any(x.endswith('.ybn') and stem_of(x) not in model_stems for x in lows)
    for u, f, low in entries:
        k = xml_kind(low) or os.path.splitext(low)[1]
        if k not in ('.ydr', '.yft', '.ydr.xml', '.yft.xml') or not (k.endswith('.xml') or streamed(u, f)):
            continue
        where, st = label(u, f), stem_of(f)
        arch = next((a for a in by_name.get(rp.joaat(st), []) if not a['mlo']), None)
        unit_has_ytyp = any(x.lower().endswith(('.ytyp', '.ytyp.xml')) for x in u['files'])
        if arch is None and not k.endswith('.xml'):
            if looks_vanilla(st):
                add('info', 'MODEL_REPLACES_VANILLA', where, f"'{st}' 没有 ytyp 定义它，名字像原版模型：替换原版可以没有 ytyp；如果是自制的，要放进 ytyp 并 DLC_ITYP_REQUEST")
            elif unit_has_ytyp or any(a['unit'] is u for a in archetypes):
                add('warn', 'MODEL_NO_ARCHETYPE', where, f"'{st}' 没有任何 ytyp 定义它。CreateObject 会失败或隐形（只有替换同名原版模型时可以没有）")
            elif not low.endswith('_hi.ydr'):
                add('info', 'NO_YTYP', where, f"'{st}' 所在资源没有 ytyp：只能替换同名原版模型；自制道具要有 ytyp + DLC_ITYP_REQUEST")
        info = None
        if k == '.ydr':
            hdr = rp.read_header(f)
            if hdr['kind'] != 'rsc':
                continue
            try:
                info = rp.read_ydr(f)
            except (rp.ProbeError, struct.error, IndexError, OSError) as e:
                add('info', 'PARSE_FAILED', where, f'读不懂这个 ydr（{e}），只检查了文件头。用 CodeWalker 打开确认')
                continue
        elif k in ('.ydr.xml', '.yft.xml'):
            try:
                info = parse_drawable_xml(f)
            except ET.ParseError as e:
                add('error', 'XML_INVALID', where, f'不是合法的 XML：{e}')
                continue
        if info is None:
            continue   # binary .yft: header and size only
        rad = arch['bs_radius'] if arch else info['bs_radius']
        flags = arch['flags'] if arch else 0
        blabel, btris, blod = band(rad)
        hi, med = info['lods']['high']['tris'], info['lods']['med']['tris']
        static_decor = bool(flags & F_STATIC)
        if hi == 0:
            add('warn', 'NO_HIGH_LOD', where, '模型的 High LOD 没有面（模型挂在别的 LOD 槽了？）。Sollumz 里把网格放进 High')
        elif med == 0 and rad >= 0.5 and hi > 300 and not static_decor:
            add('info', 'NO_LOD', where, f"只有 High（{hi} 面），没有 Medium LOD。原版{blabel}有一个 Medium（High 的 15–30%），在 15–50 m 切换；手持道具和 MLO 家具才只有一级")
        elif med and med >= 0.8 * hi:
            add('warn', 'LOD_NOT_REDUCED', where, f'Medium LOD {med} 面，几乎和 High {hi} 面一样，没有省到。原版 Medium 约是 High 的 15–30%')
        if hi > 3 * btris:
            add('info', 'TRIS_HIGH', where, f'High {hi} 面。原版{blabel}最多约 {btris} 面（实测，经验值，不是引擎上限）')
        if arch and med and info['lod_dist']['high'] < 9000 and info['lod_dist']['high'] >= arch['lod_dist'] > 0:
            add('info', 'LOD_SWITCH_BEYOND_UNLOAD', where, f"模型在 {info['lod_dist']['high']:g} m 才切到 Medium，但 archetype lodDist {arch['lod_dist']:g} m 就卸载了：Medium 永远看不到")
        # collision
        if not info.get('fragment') and info['bound'] is None and not k.startswith('.yft'):
            ybn = have(st, '.ybn', '.ybn.xml')
            if ybn:
                add('info', 'EXTERNAL_YBN', where, f"模型没有嵌入碰撞，只有单独的 {st}.ybn。单独 ybn 是放在世界坐标的地图碰撞（Sollumz 文档）；CreateObject 生成的道具能不能用它未验证——游戏里走过去/开枪测，或改成嵌入碰撞（Convert to Composite 后放在 Drawable 下）")
            elif rad < 0.35:
                add('info', 'NO_COLLISION', where, '没有碰撞。手持道具可以没有（原版手持道具也只放一个 Bound Box）')
            elif map_units.get(id(u)):
                add('info', 'NO_COLLISION', where, '没有嵌入碰撞。这是地图/MLO 资源，房子和地面的碰撞通常在单独的 .ybn 里；能推动或单独生成的道具才需要嵌入碰撞')
            else:
                add('warn', 'NO_COLLISION', where, '没有嵌入碰撞，也没有同名 .ybn：人和车会直接穿过去。用 Bound Box/Cylinder 这类基本形状做，套 Flag Preset “General (Default)”')
        if info.get('bvh_no_flags'):
            add('error', 'BVH_NO_FLAGS', where, f"{info['bvh_no_flags']} 个 Bound GeometryBVH 没有 Composite Flags。Sollumz 文档说这是最常见的错误：碰撞完全没作用。选 BVH 套 Flag Preset “General (Default)” 再导出")
        for n in info.get('heavy_polys', []):
            add('warn', 'POLY_COLLISION_HEAVY', where, f'碰撞网格有 {n} 个多边形。原版道具最多约 126 个，其余都用 Box/Cylinder；把碰撞拆成几个基本形状')
        # textures embedded in the model
        tex_checks(add, where + '（嵌入贴图）', info['textures'])

    # ---------- texture dictionaries ----------
    for u, f, low in entries:
        if low.endswith('.ytd') and streamed(u, f):
            if rp.read_header(f)['kind'] != 'rsc':
                continue
            try:
                tex = rp.read_ytd(f)
            except (rp.ProbeError, struct.error, IndexError, OSError) as e:
                add('info', 'PARSE_FAILED', label(u, f), f'读不懂这个 ytd（{e}）。用 CodeWalker 打开确认')
                continue
            tex_checks(add, label(u, f), tex)
        elif low.endswith('.ytd.xml'):
            try:
                root = ET.parse(f).getroot()
            except ET.ParseError as e:
                add('error', 'XML_INVALID', label(u, f), f'不是合法的 XML：{e}')
                continue
            tex_checks(add, label(u, f), xml_textures(root))

    # ---------- ymap XML ----------
    for u, f, low in entries:
        if not low.endswith('.ymap.xml'):
            continue
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as e:
            add('error', 'XML_INVALID', label(u, f), f'不是合法的 XML：{e}')
            continue
        mins, maxs = root.find('streamingExtentsMin'), root.find('streamingExtentsMax')
        if mins is not None and maxs is not None and all(float(mins.get(c, 0)) == 0 and float(maxs.get(c, 0)) == 0 for c in 'xyz'):
            add('warn', 'YMAP_NO_EXTENTS', label(u, f), 'streaming extents 全是 0，ymap 可能不会加载。CodeWalker 选中 ymap 按 Calculate Extents 和 Calculate All Flags 再存')
        names = [(e.findtext('archetypeName') or '').strip().lower() for e in root.findall('entities/Item')]
        unknown = sorted({n for n in names if n and rp.joaat(n) not in by_name and not have(n, *MODEL_EXT)})
        if unknown and archetypes:
            add('info', 'YMAP_ARCHETYPE_NOT_LOCAL', label(u, f), f"ymap 放了 {len(unknown)} 种这里没定义的 archetype（{', '.join(unknown[:5])}…）：原版道具没问题，自制的要检查名字")

    # ---------- summary ----------
    for u in units:
        models = [f for f in u['files'] if f.lower().endswith(MODEL_EXT) and streamed(u, f)]
        own = [a for a in archetypes if a['unit'] is u and not a['mlo']]
        if models or own:
            add('info', 'SUMMARY', u['name'], f'{len(models)} 个模型，{len(own)} 个 archetype（{sum(1 for a in own if a["name"])} 个对上文件名）。'
                '未验证：yft 内部结构、二进制碰撞的旗标、游戏内表现——上服前照 references/acceptance.md 在测试服走一遍')
    return merge_similar(findings)


def main():
    ap = argparse.ArgumentParser(description='Check a FiveM prop resource (read-only)')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    findings = check(args.paths)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                print(f"{icons[level]} {x['code']}: [{x['file']}] {x['message']}")
        if not any(f['level'] in ('error', 'warn') for f in findings):
            print('✓ 没发现错误或警告')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
