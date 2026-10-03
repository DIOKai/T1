#!/usr/bin/env python3
"""Check a FiveM MLO / map resource and the CodeWalker/Sollumz XML it was built from.

Usage:
    python check_mlo_resource.py <path> [more paths] [--json]

<path> can be a map resource, a folder of resources, or an export folder with
.ytyp.xml / .ymap.xml files. Standard library only, read-only.
Exit code 1 when errors are found.

Checks
- fxmanifest.lua: this_is_a_map missing when stream/ has map files (.ymap,
  .ytyp, .ybn, .ymt - fivem-docs assets manual part 4, ht_mlotool guide; a
  warning, since resources that only override vanilla files work without it);
  custom .ytyp with neither _manifest.ymf nor data_file 'DLC_ITYP_REQUEST'
  (fivem-docs part 4: the manifest "is necessary to load the models
  correctly"); data_file paths that match nothing (AUDIO_GAMEDATA .dat ->
  .dat151.rel convention); .xml files left in stream/.
- binary .ytyp/.ymap/.ybn/.ydr/.ytd: RSC7 header, memory over 16/48 MiB
  decoded from the header like FXServer; duplicate file names.
- .ytyp.xml MLO archetypes (CodeWalker/Sollumz XML, szio cwxml/ytyp.py):
  room 0 should be limbo, portals' roomFrom/roomTo in range, 4 corners,
  room portalCount equals the portals touching it, rooms without portals,
  attachedObjects indices past the entity list, entities in no room,
  duplicate room / entity set names, doors with special attribute but no
  door flags.
- .ymap.xml: CMloInstanceDef archetypes not defined in a local .ytyp.xml,
  zero streaming extents (Calculate Extents not run), duplicate archetype
  names across .ytyp.xml files.
"""
import argparse
import fnmatch
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

MIB = 1024 * 1024
MAP_EXT = ('.ymap', '.ytyp', '.ybn', '.ymt')
RSC_EXT = ('.ymap', '.ytyp', '.ybn', '.ydr', '.ydd', '.yft', '.ytd')
DOOR_ATTRS = {'5': 'Garage Door', '7': 'Normal Door', '8': 'Sliding Door'}  # fivem-docs part 8


def rsc_page_size(flags):
    # FXServer ConvertRSC7Size / CodeWalker RpfFile.GetSizeFromFlags
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


def rsc_memory(path):
    with open(path, 'rb') as fh:
        head = fh.read(16)
    if len(head) < 16 or head[:4] not in (b'RSC7', b'RSC8'):
        return None
    _, _, virt, phys = struct.unpack('<4sIII', head)
    return rsc_page_size(virt), rsc_page_size(phys)


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


def rel(path, bases):
    for b in bases:
        b = os.path.abspath(b)
        if path.startswith(b + os.sep):
            return os.path.relpath(path, b).replace(os.sep, '/')
    return os.path.basename(path)


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def val(el, tag, default=None):
    child = el.find(tag)
    if child is None:
        return default
    v = child.get('value')
    return v if v is not None else (child.text or '').strip()


def ints(el, tag):
    child = el.find(tag)
    if child is None or not (child.text or '').strip():
        return []
    try:
        return [int(x) for x in child.text.split()]
    except ValueError:
        return []


def check(paths):
    findings = []

    def add(level, code, where, msg):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg})

    files = walk(paths)

    # ---------- manifests ----------
    for man in [f for f in files if os.path.basename(f) in ('fxmanifest.lua', '__resource.lua')]:
        res = os.path.dirname(man)
        r = rel(man, paths)
        text = strip_lua_comments(open(man, encoding='utf-8', errors='replace').read())
        res_files = [os.path.relpath(x, res).replace(os.sep, '/') for x in files if x.startswith(res + os.sep)]
        low_files = [x.lower() for x in res_files]
        streamed = [x for x in low_files if x.split('/')[0].startswith('stream')]
        map_files = [x for x in streamed if x.endswith(MAP_EXT)]
        if map_files and not re.search(r'\bthis_is_a_map\b', text):
            add('warn', 'NO_THIS_IS_A_MAP', r, f"stream 里有地图文件（{map_files[0]} 等），但 fxmanifest 没写 this_is_a_map 'yes'。FiveM 文档要求地图资源加上它（加载时会重载地图存储），音频遮挡的 .ymt 也靠它")
        data_files = re.findall(r"data_file\s*\(?\s*['\"]([A-Z0-9_]+)['\"]\s*\)?\s*\(?\s*['\"]([^'\"]+)['\"]", text)
        for t, p in data_files:
            pl = p.replace('\\', '/').lower()
            if ':/' in pl or (t == 'DLC_ITYP_REQUEST' and '/' not in pl):
                continue  # game path (x64c:/...) or a .ytyp streamed by another resource
            if t == 'AUDIO_GAMEDATA' or t == 'AUDIO_SOUNDDATA' or t == 'AUDIO_DYNAMIXDATA':
                ok = any(x == pl or x.startswith(pl) for x in low_files)
            else:
                ok = any(x == pl or fnmatch.fnmatch(x, pl) for x in low_files)
            if not ok:
                add('error', 'DATA_FILE_NO_MATCH', r, f"data_file '{t}' '{p}' 在资源里找不到对应的文件（音频 .dat 要对应 .dat151.rel 这类文件）")
        custom_ytyp = [x for x in streamed if x.endswith('.ytyp')]
        has_ymf = any(x.endswith('.ymf') for x in streamed)
        has_ityp_req = any(t == 'DLC_ITYP_REQUEST' for t, _ in data_files)
        if custom_ytyp and not has_ymf and not has_ityp_req:
            add('warn', 'NO_YTYP_MANIFEST', r, f"有自定义 .ytyp（{custom_ytyp[0]}），但没有 _manifest.ymf，也没有 data_file 'DLC_ITYP_REQUEST'。FiveM 文档说要在 CodeWalker 用 Tools > Manifest Generator 生成 _manifest.ymf，模型才会正确加载（只是覆盖同名原版 ytyp 的话可以不用）")
        for x in streamed:
            if x.endswith('.xml'):
                add('error', 'XML_IN_STREAM', r, f"{x} 是 XML，放在 stream 里不会被加载。先用 CodeWalker RPF Explorer 导入成二进制（.ytyp/.ymap/.ydr）")
        if any(x.endswith('.dat151.rel') for x in low_files) and not any(t == 'AUDIO_GAMEDATA' for t, _ in data_files):
            add('warn', 'AUDIO_NOT_DECLARED', r, "有 .dat151.rel（音频遮挡）但没有 data_file 'AUDIO_GAMEDATA' 'audio/…/xxx_game.dat'（路径写到 .dat 为止），声音遮挡不会生效")

    # ---------- binaries ----------
    seen_names = {}
    for f in files:
        low = os.path.basename(f).lower()
        r = rel(f, paths)
        parts = r.lower().split('/')
        if not low.endswith(RSC_EXT) or not any(x.startswith('stream') for x in parts[:-1]):
            continue
        seen_names.setdefault(low, []).append(r)
        mem = rsc_memory(f)
        if mem is None:
            if 'stream_enhanced' not in parts:
                add('warn', 'NOT_RSC7', r, '开头不是 RSC7，不像编译好的 GTA 文件（可能是改了扩展名的 XML 或损坏）')
            continue
        size, what = max((mem[0], '虚拟'), (mem[1], '物理（显存）'))
        if size > 48 * MIB:
            add('error', 'ASSET_OVER_48MIB', r, f'{what}内存 {size / MIB:.1f} MiB，超过 48 MiB，FXServer 会警告一定会出串流问题（模型/贴图不加载）')
        elif size > 16 * MIB:
            add('warn', 'ASSET_OVER_16MIB', r, f'{what}内存 {size / MIB:.1f} MiB，超过 16 MiB 警告线（按 RSC 头算）。拆分贴图字典或降到 2K')
    for name, where in seen_names.items():
        legacy = [w for w in where if '/stream_enhanced/' not in '/' + w.lower()]
        if len(legacy) > 1:
            add('error', 'DUPLICATE_ASSET', legacy[0], f"'{name}' 出现在 {len(legacy)} 个地方（{', '.join(legacy)}），只有一个会生效，两个 MLO 撞名会互相覆盖")

    # ---------- XML ----------
    mlo_names, archetype_owner = set(), {}
    ymaps = []
    for f in files:
        low = os.path.basename(f).lower()
        r = rel(f, paths)
        if not (low.endswith('.ytyp.xml') or low.endswith('.ymap.xml')):
            continue
        try:
            root = ET.parse(f).getroot()
        except ET.ParseError as e:
            add('error', 'XML_INVALID', r, f'不是合法的 XML：{e}')
            continue
        if root.tag == 'CMapData':
            ymaps.append((r, root))
            continue
        if root.tag != 'CMapTypes':
            continue
        archs = root.find('archetypes')
        for a in (archs if archs is not None else []):
            name = (a.findtext('name') or '').strip()
            if name.lower() in archetype_owner:
                add('error', 'ARCHETYPE_DUPLICATE', r, f"archetype '{name}' 也在 {archetype_owner[name.lower()]} 里定义，会互相覆盖")
            archetype_owner[name.lower()] = r
            attr = val(a, 'specialAttribute', '0')
            if attr in DOOR_ATTRS:
                try:
                    flags = int(val(a, 'flags', '0'))
                except ValueError:
                    flags = 0
                # Sollumz ArchetypeFlags: Dynamic = bit 18 (flag18 -> 1<<17), Enable Door Physics = bit 27 (1<<26)
                if not (flags & (1 << 17)) or not (flags & (1 << 26)):
                    add('warn', 'DOOR_FLAGS', r, f"'{name}' 的 special attribute 是 {DOOR_ATTRS[attr]}，但 flags 里没同时勾 Dynamic 和 Enable Door Physics，门不会动（FiveM 文档 part 8）")
            if a.get('type') != 'CMloArchetypeDef':
                continue
            mlo_names.add(name.lower())
            ents = a.find('entities')
            n_ent = len(list(ents)) if ents is not None else 0
            rooms = list(a.find('rooms') or [])
            portals = list(a.find('portals') or [])
            if not rooms:
                add('error', 'MLO_NO_ROOMS', r, f"MLO '{name}' 没有房间。至少要 limbo + 一个房间")
                continue
            if (rooms[0].findtext('name') or '').strip().lower() != 'limbo':
                add('warn', 'NO_LIMBO', r, f"MLO '{name}' 的第 0 个房间是 '{rooms[0].findtext('name')}'，不是 limbo。Sollumz 教程：先 Create Limbo Room，再加其他房间")
            names = [(x.findtext('name') or '').strip().lower() for x in rooms]
            for nm in {n for n in names if names.count(n) > 1 and n}:
                add('warn', 'ROOM_NAME_DUPLICATE', r, f"MLO '{name}' 有重名房间 '{nm}'")
            touch = [0] * len(rooms)
            for i, p in enumerate(portals):
                try:
                    a_, b_ = int(val(p, 'roomFrom', '-1')), int(val(p, 'roomTo', '-1'))
                except ValueError:
                    a_, b_ = -1, -1
                if not (0 <= a_ < len(rooms)) or not (0 <= b_ < len(rooms)):
                    add('error', 'PORTAL_ROOM_RANGE', r, f"MLO '{name}' 的 portal {i} 连到不存在的房间（roomFrom={a_}, roomTo={b_}，只有 {len(rooms)} 个房间）")
                else:
                    if a_ == b_:
                        add('error', 'PORTAL_SAME_ROOM', r, f"MLO '{name}' 的 portal {i} 从房间 {a_} 连到它自己")
                    touch[a_] += 1
                    if b_ != a_:
                        touch[b_] += 1
                corners = list(p.find('corners') or [])
                if len(corners) != 4:
                    add('error', 'PORTAL_CORNERS', r, f"MLO '{name}' 的 portal {i} 有 {len(corners)} 个角，要 4 个")
                for idx in ints(p, 'attachedObjects'):
                    if idx >= n_ent:
                        add('error', 'ATTACHED_INDEX', r, f"MLO '{name}' 的 portal {i} 挂了实体 {idx}，但只有 {n_ent} 个实体")
            attached = set()
            for i, room in enumerate(rooms):
                rn = names[i] or str(i)
                try:
                    pc = int(val(room, 'portalCount', '-1'))
                except ValueError:
                    pc = -1
                if pc >= 0 and pc != touch[i]:
                    add('warn', 'PORTAL_COUNT', r, f"MLO '{name}' 房间 '{rn}' 的 portalCount={pc}，但实际有 {touch[i]} 个 portal 连到它（在 Sollumz/CodeWalker 里重新导出会自动算）")
                if i > 0 and touch[i] == 0:
                    add('error', 'ROOM_NO_PORTAL', r, f"MLO '{name}' 房间 '{rn}' 没有任何 portal，进不去也看不到（至少要一个 portal 连到 limbo 或别的房间）")
                for idx in ints(room, 'attachedObjects'):
                    if idx >= n_ent:
                        add('error', 'ATTACHED_INDEX', r, f"MLO '{name}' 房间 '{rn}' 挂了实体 {idx}，但只有 {n_ent} 个实体")
                    attached.add(idx)
            for p in portals:
                attached.update(ints(p, 'attachedObjects'))
            sets = list(a.find('entitySets') or [])
            set_names = [(s.findtext('name') or '').strip().lower() for s in sets]
            for nm in {n for n in set_names if set_names.count(n) > 1 and n}:
                add('error', 'ENTITYSET_DUPLICATE', r, f"MLO '{name}' 的 entity set '{nm}' 重名，ActivateInteriorEntitySet 只能找到一个")
            missing = [i for i in range(n_ent) if i not in attached]
            if missing:
                add('warn', 'ENTITY_NO_ROOM', r, f"MLO '{name}' 有 {len(missing)} 个实体没放进任何房间或 portal（索引 {missing[:8]}{'…' if len(missing) > 8 else ''}），进屋后会看不到")

    for r, root in ymaps:
        mins = root.find('streamingExtentsMin')
        maxs = root.find('streamingExtentsMax')
        if mins is not None and maxs is not None and all(float(mins.get(k, 0)) == 0 and float(maxs.get(k, 0)) == 0 for k in 'xyz'):
            add('warn', 'YMAP_NO_EXTENTS', r, 'streaming extents 全是 0，ymap 可能不会加载。CodeWalker 里选中 ymap 按 Calculate Extents 和 Calculate All Flags 再存')
        ents = root.find('entities')
        for e in (ents if ents is not None else []):
            if e.get('type') == 'CMloInstanceDef':
                an = (e.findtext('archetypeName') or '').strip()
                if archetype_owner and an.lower() not in mlo_names:
                    add('info', 'MLO_ARCHETYPE_NOT_LOCAL', r, f"MLO 实例 '{an}' 没在这里的 .ytyp.xml 里找到 MLO archetype：原版内饰没问题，自定义的要检查名字是否和 ytyp 里一致")
    return findings


def main():
    ap = argparse.ArgumentParser(description='Check a FiveM MLO / map resource')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    findings = check(args.paths)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                print(f"{icons[level]} {x['code']}: [{x['file']}] {x['message']}")
        if not findings:
            print('✓ 没发现问题')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
