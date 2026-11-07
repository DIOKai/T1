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
  custom .ytyp without a .ymf manifest (fivem-docs part 4: the manifest "is
  necessary to load the models correctly"); DLC_ITYP_REQUEST of a ytyp that
  holds an MLO archetype (crashed clients on the user's server - the .ymf
  loads MLO ytyps); data_file paths that match nothing (AUDIO_GAMEDATA .dat ->
  .dat151.rel convention); .xml files left in stream/.
- binary .ytyp/.ymap/.ybn/.ydr/.ytd: RSC7 header, memory over 16/48 MiB
  decoded from the header like FXServer; duplicate file names.
- .ytyp.xml MLO archetypes (CodeWalker/Sollumz XML, szio cwxml/ytyp.py):
  room 0 should be limbo, portals' roomFrom/roomTo in range, 4 corners,
  room portalCount equals the portals touching it, rooms without portals,
  attachedObjects indices past the entity list, entities in no room,
  duplicate room / entity set names, doors with special attribute but no
  door flags, portal facing (normal (c1-c0)x(c2-c0) must point away from
  roomFrom, judged by points 0.3 m either side against the room boxes),
  entities attached to both a portal and a room.
- .ymap.xml: CMloInstanceDef archetypes not defined in a local .ytyp.xml,
  zero streaming extents (Calculate Extents not run), duplicate archetype
  names across .ytyp.xml files, more than one MLO instance per ymap, an MLO
  instance mixed with other entities, an MLO ymap not named *_milo_.
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


def vec(el, tag=None):
    child = el if tag is None else el.find(tag)
    if child is None:
        return None
    try:
        if child.get('x') is not None:
            return tuple(float(child.get(k)) for k in 'xyz')
        parts = re.split(r'[,\s]+', (child.text or '').strip())   # portal corners: <Item>6.0,-25.0,0.0</Item>
        return tuple(float(x) for x in parts) if len(parts) == 3 else None
    except (TypeError, ValueError):
        return None


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def inside(box, p):
    lo, hi = box
    return all(lo[i] <= p[i] <= hi[i] for i in range(3))


def portal_facing(corners, box_from, box_to, step=0.3):
    """'ok', 'flipped' or None (can't tell). Normal (c1-c0)x(c2-c0) must point from roomFrom to roomTo."""
    if len(corners) != 4 or any(c is None for c in corners):
        return None
    n = cross(sub(corners[1], corners[0]), sub(corners[2], corners[0]))
    ln = sum(x * x for x in n) ** 0.5
    if ln < 1e-9:
        return None
    n = tuple(x / ln for x in n)
    c = tuple(sum(k[i] for k in corners) / 4 for i in range(3))
    ahead = tuple(c[i] + n[i] * step for i in range(3))
    behind = tuple(c[i] - n[i] * step for i in range(3))
    for box, want_behind in ((box_from, True), (box_to, False)):
        if box is None:
            continue
        a, b = inside(box, ahead), inside(box, behind)
        if a == b:
            continue  # box covers both sides or neither: undecidable from this room
        return 'ok' if b == want_behind else 'flipped'
    return None


def room_box(room):
    lo, hi = vec(room, 'bbMin'), vec(room, 'bbMax')
    if lo is None or hi is None or (all(v == 0 for v in lo) and all(v == 0 for v in hi)):
        return None  # limbo / unset
    return lo, hi


def kids(el, tag):
    child = el.find(tag)
    return list(child) if child is not None else []


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
    ityp_requests = []      # (manifest rel path, requested ytyp path)
    ymf_resources = []      # manifests whose resource streams a .ymf and also uses DLC_ITYP_REQUEST

    # ---------- manifests ----------
    for man in [f for f in files if os.path.basename(f) in ('fxmanifest.lua', '__resource.lua')]:
        res = os.path.dirname(man)
        r = rel(man, paths)
        with open(man, encoding='utf-8', errors='replace') as fh:
            text = strip_lua_comments(fh.read())
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
        reqs = [(r, p) for t, p in data_files if t == 'DLC_ITYP_REQUEST']
        ityp_requests += reqs
        if has_ymf and reqs:
            ymf_resources.append(r)
        if custom_ytyp and not has_ymf:
            add('warn', 'NO_YTYP_MANIFEST', r, f"有自定义 .ytyp（{custom_ytyp[0]}），但 stream 里没有 .ymf。FiveM 文档说要在 CodeWalker 用 Tools > Manifest Generator 生成 _manifest.ymf，模型才会正确加载；MLO 的 ytyp 一定要靠 .ymf 载入，不要改用 DLC_ITYP_REQUEST（只是覆盖同名原版 ytyp 的话可以不用）")
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
    mlo_names, archetype_owner, mlo_ytyp_stems = set(), {}, set()
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
            mlo_ytyp_stems.add(low[:-len('.ytyp.xml')])
            ents = a.find('entities')
            n_ent = len(list(ents)) if ents is not None else 0
            rooms = kids(a, 'rooms')
            portals = kids(a, 'portals')
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
                corners = kids(p, 'corners')
                if len(corners) != 4:
                    add('error', 'PORTAL_CORNERS', r, f"MLO '{name}' 的 portal {i} 有 {len(corners)} 个角，要 4 个")
                elif 0 <= a_ < len(rooms) and 0 <= b_ < len(rooms) and a_ != b_:
                    face = portal_facing([vec(c) for c in corners], room_box(rooms[a_]), room_box(rooms[b_]))
                    if face == 'flipped':
                        add('warn', 'PORTAL_FACING', r, f"MLO '{name}' 的 portal {i}（{a_}→{b_}）朝向反了：法线 (c1-c0)×(c2-c0) 指向 roomFrom，应该指离 roomFrom、指向 roomTo。朝向混乱会让室内从某些角度整个消失（灰地板加天空）。在 Sollumz 里按 Flip Direction 再导出")
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
            in_rooms = set(attached)
            for i, p in enumerate(portals):
                both = sorted(set(ints(p, 'attachedObjects')) & in_rooms)
                if both:
                    add('warn', 'PORTAL_AND_ROOM', r, f"MLO '{name}' 的实体 {both[:8]} 同时挂在 portal {i} 和房间里（Sollumz 同时设了 attached room 和 attached portal 就会这样）。门只挂 portal，把房间那边清掉")
                attached.update(ints(p, 'attachedObjects'))
            sets = kids(a, 'entitySets')
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
        ent_list = list(ents) if ents is not None else []
        n_mlo = sum(1 for e in ent_list if e.get('type') == 'CMloInstanceDef')
        if n_mlo > 1:
            add('error', 'YMAP_MULTI_MLO', r, f"一个 ymap 里有 {n_mlo} 个 MLO 实例。这个伺服器上多个 MLO 放同一个 ymap，玩家靠近就闪退：每个 MLO 单独一个 *_milo_.ymap")
        elif n_mlo == 1:
            if len(ent_list) > 1:
                add('warn', 'YMAP_MLO_MIXED', r, f"MLO 实例和 {len(ent_list) - 1} 个普通实体放在同一个 ymap。MLO 的 ymap 只放那一个 MLO 实例，门、道具放进 ytyp 的 MLO 实体，其他东西另开 ymap")
            if '_milo_' not in os.path.basename(r).lower():
                add('warn', 'YMAP_MLO_NAME', r, "放 MLO 实例的 ymap 名字里没有 _milo_。这个伺服器上能用的 MLO 都是 <名字>_milo_.ymap，加上 .ymf 里 INTERIOR_DATA 指到 MLO 的 ytyp")
        for e in ent_list:
            if e.get('type') == 'CMloInstanceDef':
                an = (e.findtext('archetypeName') or '').strip()
                if archetype_owner and an.lower() not in mlo_names:
                    add('info', 'MLO_ARCHETYPE_NOT_LOCAL', r, f"MLO 实例 '{an}' 没在这里的 .ytyp.xml 里找到 MLO archetype：原版内饰没问题，自定义的要检查名字是否和 ytyp 里一致")
    def ytyp_stem(path):
        b = os.path.basename(path.replace('\\', '/')).lower()
        return b[:-len('.ytyp')] if b.endswith('.ytyp') else b

    flagged = set()
    for r, p in ityp_requests:
        if ytyp_stem(p) in mlo_ytyp_stems:
            flagged.add(r)
            add('error', 'ITYP_REQUEST_MLO', r, f"data_file 'DLC_ITYP_REQUEST' '{p}' 载入的是放 MLO 的 ytyp。这个伺服器上这样做会让客户端闪退：删掉这一行，MLO 的 ytyp 交给 .ymf 载入（普通道具 ytyp 可以留着）")
    for r in ymf_resources:
        if r not in flagged:
            add('info', 'ITYP_REQUEST_CHECK', r, "资源里有 .ymf 又有 DLC_ITYP_REQUEST：确认被 request 的只是道具或外观的 ytyp，不是 MLO 的（没有 XML 时脚本分不出来）")
    return findings


def main():
    ap = argparse.ArgumentParser(description='Check a FiveM MLO / map resource')
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
        if not findings:
            print('✓ 没发现问题')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
