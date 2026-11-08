#!/usr/bin/env python3
"""Check a FiveM add-on / replacement weapon resource before it goes on the server.

Usage:
    py -3 -I check_weapon_resource.py <resource or folder of resources> [more paths]
        [--ox <ox_inventory folder>] [--xml <folder with Sollumz/CodeWalker .ydr.xml>] [--json]

Standard library only, read-only (never writes). Exit code 1 when errors are found.
Made for single add-on resources; pointing it at a whole vanilla dump gives
cross-reference noise because vanilla data is split over many DLC packs.

Checks
- fxmanifest.lua: data_file types (typos such as WEAPON_ANIMATION_FILE), globs that
  match nothing, metas mounted but missing from files {} (clients never download
  them), WEAPONINFO_FILE not last (2019 community load-order advice), .meta files
  nobody mounts, root tag of each meta vs the data_file type it is mounted as.
- stream/: .xml / .blend / .dds left in stream, duplicate names, _hi.ydr without
  its base .ydr ("HD-only cannot be streamed"), models outside a stream folder,
  RSC7 header (magic, version 165 ydr / 13 ytd from vanilla), memory decoded from
  the header like FXServer (16 MiB warning, 48 MiB error).
- cross references (case-insensitive): weapons.meta Model -> weaponarchetypes
  modelName -> .ydr; txdName -> .ytd; every AttachPoints component defined here or
  vanilla; component Model -> archetype + .ydr (missing mag archetype = crash on
  reload, reported 2019); AttachBone prefixes (WAP* on the weapon, AAP* on the
  component); Slot listed in SlotNavigateOrder, unique Slot / OrderNumber;
  weaponanimations + pedpersonality entries; AddTextEntry for HumanNameHash.
- --xml (and any *.ydr.xml inside the resource): skeleton has Gun_Root, Gun_GripR,
  Gun_Main_Bone (+ Gun_Muzzle for guns), every AttachPoints bone exists, component
  root bone equals its AttachBone, base drawable has embedded bounds, triangle
  counts against vanilla-derived budgets (rule of thumb, not an engine limit).
- --ox: item key (or model) equals the weapons.meta Name, ammoname exists, image in
  web/images, non-default components listed in some Components client.component.
"""
import argparse
import difflib
import glob
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

MIB = 1024 * 1024
META_ROOT = {   # docs.fivem.net/docs/game-references/data-files/ + vanilla files
    'WEAPONINFO_FILE': 'CWeaponInfoBlob',
    'WEAPONINFO_FILE_PATCH': 'CWeaponInfoBlob',
    'WEAPON_METADATA_FILE': 'CWeaponModelInfo__InitDataList',
    'WEAPON_ANIMATIONS_FILE': 'CWeaponAnimationsSets',
    'WEAPONCOMPONENTSINFO_FILE': 'CWeaponComponentInfoBlob',
    'PED_PERSONALITY_FILE': 'CPedModelInfo__PersonalityDataList',
}
KNOWN_TYPES = set(META_ROOT) | {
    'LOADOUTS_FILE', 'CONTENT_UNLOCKING_META_FILE', 'WEAPON_SHOP_INFO_METADATA_FILE', 'DLC_WEAPON_PICKUPS',
    'CLIP_SETS_FILE', 'PTFXASSETINFO_FILE', 'EXPLOSION_INFO_FILE',
    'AUDIO_GAMEDATA', 'AUDIO_SOUNDDATA', 'AUDIO_WAVEPACK', 'AUDIO_SYNTHDATA', 'AUDIO_SPEECHDATA', 'AUDIO_DYNAMIXDATA',
    'HANDLING_FILE', 'VEHICLE_METADATA_FILE', 'CARCOLS_FILE', 'VEHICLE_VARIATION_FILE', 'VEHICLE_LAYOUTS_FILE',
    'CARCONTENTUNLOCKS_FILE', 'VEHICLE_SHOP_DLC_FILE', 'DLC_ITYP_REQUEST', 'PED_METADATA_FILE', 'TIMECYCLEMOD_FILE',
    'SCALEFORM_DLC_FILE', 'GTXD_PARENTING_DATA', 'DLC_POP_GROUPS', 'INTERIOR_PROXY_ORDER_FILE',
    'SCENARIO_POINTS_OVERRIDE_PSO_FILE', 'CARCOLS_GEN9_FILE', 'CARMODCOLS_GEN9_FILE', 'FIVEM_LOVES_YOU_4B38E96CC036038F',
    'FIVEM_LOVES_YOU_341B23A2F0E0F131', 'DISPATCH_TUNING_FILE',
}
WEAPON_ORDER = ['WEAPONCOMPONENTSINFO_FILE', 'WEAPON_METADATA_FILE', 'WEAPON_ANIMATIONS_FILE',
                'PED_PERSONALITY_FILE', 'WEAPONINFO_FILE']
RSC_VERSION = {'.ydr': 165, '.ytd': 13}          # vanilla weapon files read with CodeWalker.Core
MODEL_EXT = ('.ydr', '.ytd', '.yft', '.ydd')
REQUIRED_BONES = ('gun_root', 'gun_gripr', 'gun_main_bone')
# triangle budgets: ~1.5x the largest vanilla value seen (base 4,031 musket; _hi 9,165 carbine; parts 744)
TRI_BUDGET = {'base': 6000, 'hi': 15000, 'part': 1500}


def load_vanilla():
    names = {'weapons': set(), 'components': set()}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vanilla_weapon_names.txt')
    section = None
    try:
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('['):
                    section = line.strip('[]')
                elif section in names:
                    names[section].add(line.lower())
    except OSError:
        pass
    return names


VANILLA = load_vanilla()


def rsc_page_size(flags):
    # FXServer ConvertRSC7Size / CodeWalker RpfFile.GetSizeFromFlags (carbine ytd -> 16,777,216 physical)
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


def rsc_header(path):
    """(magic, version, virtual bytes, physical bytes) or None if not an RSC7/RSC8 file."""
    with open(path, 'rb') as fh:
        head = fh.read(16)
    if len(head) < 16 or head[:4] not in (b'RSC7', b'RSC8'):
        return None
    magic, ver, virt, phys = struct.unpack('<4sIII', head)
    return magic, ver, rsc_page_size(virt), rsc_page_size(phys)


def is_escrowed(path):
    """Cfx Asset Escrow encrypts files; they start with FXAP (seen on the user's server, read-only)."""
    with open(path, 'rb') as fh:
        return fh.read(4) == b'FXAP'


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def read_text(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        return fh.read()


def find_resources(paths):
    out = []
    for p in paths:
        p = os.path.abspath(p)
        if any(os.path.isfile(os.path.join(p, m)) for m in ('fxmanifest.lua', '__resource.lua')):
            out.append(p)
            continue
        found = False
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            if 'fxmanifest.lua' in files or '__resource.lua' in files:
                out.append(root)
                found = True
                dirs[:] = []
        if not found:
            out.append(p)   # reported as NO_MANIFEST
    return out


def all_files(root):
    out = []
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        out += [os.path.join(r, f) for f in files]
    return out


def glob_hits(root, pattern):
    pattern = pattern.replace('\\', '/')
    base = glob.escape(root)                 # server folders are named like [assets] - brackets are glob syntax
    hits = glob.glob(os.path.join(base, pattern), recursive=True)
    if not hits and pattern.lower().endswith('.dat'):          # AUDIO_GAMEDATA 'x_game.dat' -> x_game.dat151.rel
        hits = glob.glob(os.path.join(base, pattern + '*.rel'), recursive=True)
    return hits


def low(x):
    return (x or '').strip().lower()


def parse_meta(path):
    with open(path, 'rb') as fh:
        raw = fh.read()
    raw = re.sub(rb'encoding="UTF\s*-\s*8"', b'encoding="UTF-8"', raw, count=1)   # public packs write "UTF - 8"
    raw = re.sub(rb'<!--.*?-->', b'', raw, flags=re.S)   # <!------> banners are invalid XML but the game accepts them
    return ET.fromstring(raw)


def ydr_xml_info(path):
    """Bones, bounds, triangle count of a CodeWalker/Sollumz .ydr.xml."""
    root = ET.parse(path).getroot()
    bones = [low(b.findtext('Name')) for b in root.findall('./Skeleton/Bones/Item')]
    tris = 0
    for data in root.findall('./DrawableModelsHigh/Item/Geometries/Item/IndexBuffer/Data'):
        tris += len((data.text or '').split()) // 3
    return {'bones': bones, 'bounds': root.find('Bounds') is not None, 'tris': tris,
            'embedded_txd': root.find('TextureDictionary') is not None}


def check(paths, ox=None, xml_dirs=()):
    findings = []
    vanilla_w, vanilla_c = VANILLA['weapons'], VANILLA['components']
    order_seen = {}          # OrderNumber -> (slot, resource) across all checked resources

    def add(level, code, where, msg):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg})

    xml_index = {}
    for d in xml_dirs:
        for f in all_files(os.path.abspath(d)):
            if f.lower().endswith('.ydr.xml'):
                xml_index[os.path.basename(f).lower()[:-8]] = f

    ox_text = None
    if ox:
        wl = os.path.join(ox, 'data', 'weapons.lua')
        if os.path.isfile(wl):
            ox_text = read_text(wl)
        else:
            add('error', 'OX_NOT_FOUND', ox, '找不到 data/weapons.lua，--ox 要指到 ox_inventory 资源的根目录')

    for res in find_resources(paths):
        name = os.path.basename(res)
        man = next((os.path.join(res, m) for m in ('fxmanifest.lua', '__resource.lua')
                    if os.path.isfile(os.path.join(res, m))), None)
        files = all_files(res)

        lua_text = '\n'.join(strip_lua_comments(read_text(f)) for f in files if f.lower().endswith('.lua'))

        def rel(p):
            return name + '/' + os.path.relpath(p, res).replace(os.sep, '/')

        # ---------- manifest ----------
        data_files, file_globs = [], []
        if not man:
            add('error', 'NO_MANIFEST', name, '没有 fxmanifest.lua，FiveM 不会把它当资源载入')
        else:
            txt = strip_lua_comments(read_text(man))
            if not re.search(r"\bgame\s*\(?\s*['\"]gta5['\"]", txt) and 'games' not in txt:
                add('info', 'NO_GAME', rel(man), "fxmanifest 没写 game 'gta5'")
            data_files = re.findall(
                r"data_file\s*\(?\s*['\"]([A-Za-z0-9_]+)['\"]\s*\)?\s*\(?\s*['\"]([^'\"]+)['\"]", txt)
            for m in re.finditer(r"\bfiles?\s*\(?\s*\{(.*?)\}", txt, flags=re.S):
                file_globs += re.findall(r"['\"]([^'\"]+)['\"]", m.group(1))
            file_globs += re.findall(r"\bfiles?\s*\(?\s*['\"]([^'\"]+)['\"]", txt)
        covered = set()
        for g in file_globs:
            covered |= {os.path.normcase(os.path.abspath(p)) for p in glob_hits(res, g) if os.path.isfile(p)}

        mounted = {}
        for typ, g in data_files:
            if typ not in KNOWN_TYPES:
                close = difflib.get_close_matches(typ, sorted(KNOWN_TYPES), n=1, cutoff=0.75)
                hint = f'，是不是 {close[0]}？' if close else ''
                lvl = 'error' if 'WEAPON' in typ.upper() else 'warn'
                add(lvl, 'DATA_FILE_UNKNOWN', rel(man), f"data_file 类型 '{typ}' 不认识{hint}（拼错的类型会被忽略，meta 不会载入）")
            hits = glob_hits(res, g)
            if not hits and typ == 'DLC_ITYP_REQUEST':    # names a streamed ytyp, the path is not literal
                if not any(os.path.basename(f).lower() == os.path.basename(g).lower() for f in files):
                    add('warn', 'DATA_FILE_NO_MATCH', rel(man), f"DLC_ITYP_REQUEST '{g}' 在这个资源里找不到同名 .ytyp")
            elif not hits:
                add('error', 'DATA_FILE_NO_MATCH', rel(man), f"data_file '{typ}' '{g}' 找不到对应的文件")
            for h in hits:
                if os.path.isdir(h):
                    continue
                key = os.path.normcase(os.path.abspath(h))
                mounted[key] = typ
                if h.lower().endswith('.meta') and key not in covered:
                    add('error', 'NOT_IN_FILES', rel(h), "有 data_file 但没写进 files {}，客户端不会下载，等于没装（武器会用原版数值或不存在）")
        wtypes = [t for t, _ in data_files if t in WEAPON_ORDER]
        if 'WEAPONINFO_FILE' in wtypes and wtypes[-1] != 'WEAPONINFO_FILE':
            add('warn', 'WEAPONINFO_NOT_LAST', rel(man), '社区经验：weaponcomponents 先载入、WEAPONINFO_FILE（weapons.meta）放最后，否则有些东西不生效')

        # ---------- metas ----------
        weapons, archetypes, components, anim_keys, persona = {}, {}, {}, set(), set()
        slots_nav, escrowed = [], []
        for f in files:
            if not f.lower().endswith('.meta'):
                continue
            key = os.path.normcase(os.path.abspath(f))
            typ = mounted.get(key)
            if is_escrowed(f):
                escrowed.append(f)
                continue
            try:
                r = parse_meta(f)
            except ET.ParseError as e:
                weaponish = (typ in META_ROOT) or 'weapon' in os.path.basename(f).lower()
                tail = '（武器 meta 格式坏掉，整个文件都不会载入）' if weaponish else '（不是武器 meta；游戏的解析器比较宽松，未必真的有问题）'
                add('error' if weaponish else 'warn', 'META_PARSE', rel(f), f'XML 格式错误：{e}{tail}')
                continue
            except OSError as e:
                add('error', 'META_PARSE', rel(f), f'读不到：{e}')
                continue
            if typ is None:
                wanted = [t for t, root_tag in META_ROOT.items() if root_tag == r.tag and t != 'WEAPONINFO_FILE_PATCH']
                hint = f"（应该用 data_file '{wanted[0]}'）" if wanted else ''
                add('warn', 'META_NOT_MOUNTED', rel(f), f'这个 meta 没有任何 data_file 载入{hint}')
                continue
            want = META_ROOT.get(typ)
            if want and r.tag != want:
                add('error', 'META_TYPE_MISMATCH', rel(f), f"根节点是 <{r.tag}>，却用 '{typ}' 载入（要 <{want}>）")
                continue
            if r.tag == 'CWeaponInfoBlob':
                for it in r.iter('Item'):
                    if it.get('type') != 'CWeaponInfo' or not it.findtext('Name'):
                        continue
                    aps = []
                    for ap in it.findall('./AttachPoints/Item'):
                        bone = (ap.findtext('AttachBone') or '').strip()
                        for c in ap.findall('./Components/Item'):
                            d = c.find('Default')
                            aps.append((bone, low(c.findtext('Name')), d is not None and low(d.get('value')) == 'true'))
                    flags = (it.findtext('WeaponFlags') or '').split()
                    weapons[low(it.findtext('Name'))] = dict(
                        model=low(it.findtext('Model')), slot=low(it.findtext('Slot')),
                        label=(it.findtext('HumanNameHash') or '').strip(), aps=aps, file=rel(f),
                        gun='Gun' in flags or low(it.findtext('DamageType')) not in ('melee', ''))
                for e in r.findall('./SlotNavigateOrder/Item/WeaponSlots/Item'):
                    on = e.find('OrderNumber')
                    slots_nav.append((low(e.findtext('Entry')), on.get('value') if on is not None else None))
            elif r.tag == 'CWeaponModelInfo__InitDataList':
                for it in r.findall('./InitDatas/Item'):
                    archetypes[low(it.findtext('modelName'))] = low(it.findtext('txdName'))
            elif r.tag == 'CWeaponComponentInfoBlob':
                for it in r.iter('Item'):
                    if (it.get('type') or '').startswith('CWeaponComponent') and it.findtext('Name'):
                        components[low(it.findtext('Name'))] = dict(
                            model=low(it.findtext('Model')), bone=(it.findtext('AttachBone') or '').strip(), file=rel(f))
            elif r.tag == 'CWeaponAnimationsSets':
                for it in r.iter('Item'):
                    if low(it.get('key')).startswith('weapon_'):
                        anim_keys.add(low(it.get('key')))
            elif r.tag == 'CPedModelInfo__PersonalityDataList':
                for w in r.iter('Item'):
                    if low(w.text).startswith('weapon_'):
                        persona.add(low(w.text))

        # ---------- stream files ----------
        stream, xml_local = {}, {}
        for f in files:
            b = os.path.basename(f).lower()
            parts = os.path.relpath(f, res).lower().replace(os.sep, '/').split('/')
            in_stream = any(x.startswith('stream') for x in parts[:-1])
            enhanced = 'stream_enhanced' in parts
            if b.endswith('.ydr.xml'):
                xml_local[b[:-8]] = f
            ext = os.path.splitext(b)[1]
            if in_stream and ext in ('.xml', '.blend', '.dds', '.png', '.fbx', '.obj'):
                code = 'XML_IN_STREAM' if ext == '.xml' else 'SOURCE_IN_STREAM'
                add('error' if ext == '.xml' else 'warn', code, rel(f),
                    '放在 stream 里不会被游戏载入（XML 要先用 CodeWalker/Sollumz 转成二进制 .ydr/.ytd，源文件挪到 stream 外）')
                continue
            if ext not in MODEL_EXT:
                continue
            if not in_stream:
                add('warn', 'NOT_IN_STREAM', rel(f), '模型/贴图不在 stream 文件夹里，FiveM 不会串流它（枪会看不见）')
                continue
            if enhanced:
                continue
            if b in stream:
                add('error', 'DUPLICATE_ASSET', rel(f), f'{b} 在资源里出现两次，只有一个会生效')
            stream[b] = f
            head = rsc_header(f)
            if head is None and is_escrowed(f):
                escrowed.append(f)
                continue
            if head is None:
                add('error', 'NOT_RSC7', rel(f), '开头不是 RSC7，不是编译好的 GTA 文件（改了扩展名的 XML 或坏档）')
                continue
            _, ver, virt, phys = head
            if ext in RSC_VERSION and ver != RSC_VERSION[ext]:
                add('warn', 'RSC_VERSION', rel(f), f'RSC 版本 {ver}，原版武器 {ext} 是 {RSC_VERSION[ext]}（Enhanced 档或别的工具导出？）')
            size, what = max((virt, '虚拟'), (phys, '物理（显存）'))
            if size > 48 * MIB:
                add('error', 'ASSET_OVER_48MIB', rel(f), f'{what}内存 {size / MIB:.1f} MiB，超过 48 MiB，一定会出串流问题')
            elif size > 16 * MIB:
                add('warn', 'ASSET_OVER_16MIB', rel(f), f'{what}内存 {size / MIB:.1f} MiB，超过 16 MiB 警告线（原版卡宾枪 ytd 正好 16 MiB，2048² 贴图）；武器用 2K 就够，自己做的可以降级，买来/转换的先报告给用户')
        if escrowed:
            add('info', 'ESCROWED', name, f'{len(escrowed)} 个文件是 Asset Escrow 加密（开头 FXAP），这些文件没检查；加密的资源只能用不能改')
        for b in stream:
            if b.endswith('_hi.ydr') and b[:-7] + '.ydr' not in stream:
                add('error', 'HI_WITHOUT_BASE', rel(stream[b]), f'只有 {b} 没有本体 {b[:-7]}.ydr：只串流 _hi 是不行的，枪会看不见')

        # ---------- cross references ----------
        stream_models = {b[:-4] for b in stream if b.endswith('.ydr')}
        for w, d in weapons.items():
            m = d['model']
            vanilla_name = w in vanilla_w
            if m and m not in archetypes and m not in stream_models:
                if vanilla_name:
                    add('info', 'VANILLA_RETUNE', d['file'], f'{w.upper()} 用原版模型 {m}，看起来是只改数值（meta-only）')
                else:
                    add('warn', 'MODEL_NOT_HERE', d['file'], f'{w.upper()} 的 Model {m} 在这个资源里既没有 .ydr 也没有 archetype：只有它是原版模型名时才正常，否则枪会看不见')
            elif m and m not in archetypes:
                add('error', 'MODEL_NO_ARCHETYPE', d['file'], f'{w.upper()} 的模型 {m}.ydr 有串流，但 weaponarchetypes.meta 没有 modelName {m}（枪会看不见）')
            elif m and m not in stream_models:
                add('error', 'MODEL_NOT_STREAMED', d['file'], f'{w.upper()} 的模型 {m} 写进了 archetype，但 stream 里没有 {m}.ydr')
            if vanilla_name and m in stream_models:
                add('info', 'OVERRIDES_VANILLA', d['file'], f'{w.upper()} 是原版武器名：这会改掉所有人手上的原版 {w.upper()}（替换，不是 add-on）')
            if d['slot'] and slots_nav and d['slot'] not in {s for s, _ in slots_nav}:
                add('warn', 'SLOT_NOT_IN_NAV', d['file'], f"{w.upper()} 的 Slot {d['slot'].upper()} 没写进 SlotNavigateOrder，武器轮盘可能不显示")
            if d['label'] and not vanilla_name and not (
                    re.search(re.escape(d['label']), lua_text, re.I) and 'addtextentry' in lua_text.lower()):
                add('warn', 'NO_TEXT_ENTRY', d['file'], f"HumanNameHash {d['label']} 没有对应的 AddTextEntry，名字会显示成 NULL（故意沿用原版 WT_ 名字可以忽略）")
            if w not in anim_keys and not vanilla_name:
                add('warn', 'NO_ANIMATION', d['file'], f'{w.upper()} 在 weaponanimations.meta 没有条目：持枪/换弹动作会错或不显示，复制模板枪的条目改 key')
            if persona and w not in persona and not vanilla_name:
                add('info', 'NO_UNHOLSTER', d['file'], f'{w.upper()} 不在 pedpersonality.meta 的拔枪列表里，拔枪动作会用默认的')
            for bone, c, default in d['aps']:
                if not (bone.upper().startswith('WAP') or low(bone) in ('gun_root', 'gun_gripr')):
                    add('warn', 'ATTACHPOINT_BONE', d['file'], f"AttachPoints 的 AttachBone '{bone}' 不是 WAP* 骨骼（原版用 WAPClip/WAPScop/WAPSupp/WAPGrip/WAPFlshLasr，皮肤用 gun_root）")
                if c not in components and c not in vanilla_c:
                    add('warn', 'COMPONENT_UNDEFINED', d['file'], f'{c.upper()}（挂在 {bone}）没在这个资源的 weaponcomponents.meta 定义，也不在原版配件名单里：拼错就会装不上')
        for s, on in slots_nav:
            prev = order_seen.get(on)
            if on is not None and prev and prev[0] != s:
                add('warn', 'ORDER_DUPLICATE', name, f'OrderNumber {on} 同时给了 {prev[0].upper()}（{prev[1]}）和 {s.upper()}，重复的编号可能让武器从背包/轮盘消失')
            order_seen.setdefault(on, (s, name))
        slots = [d['slot'] for d in weapons.values() if d['slot']]
        for s in {x for x in slots if slots.count(x) > 1}:
            add('warn', 'SLOT_DUPLICATE', name, f'两把武器用同一个 Slot {s.upper()}，每把 add-on 要有自己的 SLOT_')
        used = {c for d in weapons.values() for _, c, _ in d['aps']}
        for c, d in components.items():
            if not d['bone'].upper().startswith('AAP') and d['bone']:
                add('warn', 'COMPONENT_BONE', d['file'], f"{c.upper()} 的 AttachBone 是 '{d['bone']}'：配件这边要写自己的根骨骼 AAP*（AAPClip/AAPScop/AAPSupp/AAPGrip/AAPFlsh），WAP* 写在 weapons.meta")
            if d['model']:
                if d['model'] not in archetypes and d['model'] + '.ydr' in stream:
                    add('error', 'COMPONENT_NO_ARCHETYPE', d['file'], f"{c.upper()} 的模型 {d['model']} 没写进 weaponarchetypes.meta：2019 年的回报是换弹时闪退")
                elif d['model'] + '.ydr' not in stream and d['model'] not in archetypes:
                    add('warn', 'COMPONENT_MODEL_NOT_HERE', d['file'], f"{c.upper()} 的模型 {d['model']} 不在这个资源（原版配件模型可以忽略）")
            if weapons and c not in used:
                add('info', 'COMPONENT_UNUSED', d['file'], f'{c.upper()} 定义了但没有任何武器的 AttachPoints 用到它')
        weapon_models = {d['model'] for d in weapons.values()}
        for m, txd in archetypes.items():
            if m + '.ydr' not in stream and m + '.yft' not in stream and m not in weapon_models:
                add('error' if stream else 'warn', 'ARCHETYPE_NO_MODEL', name, f'weaponarchetypes 有 {m}，但 stream 里没有 {m}.ydr')
            if txd and txd != 'null' and txd + '.ytd' not in stream:
                add('warn', 'TXD_MISSING', name, f'{m} 的 txdName {txd}.ytd 不在 stream（贴图会掉，除非是故意共用原版贴图字典）')
        for w in sorted(persona - set(weapons)):
            add('info', 'PERSONA_OTHER', name, f'pedpersonality 提到 {w.upper()}，这个资源没定义它')
        weapon_files = sorted(b for b in stream_models if b.startswith('w_'))
        if not weapons and weapon_files and not archetypes:
            add('info', 'REPLACEMENT_PACK', name, f'有武器模型（{weapon_files[0]}…）但没有 weapons.meta：这是替换包，文件名要和原版完全一样（w_xx_xxx.ydr/_hi.ydr/.ytd/_mag1），会改掉所有人的原版枪')
        for b in stream_models:
            if not b.endswith('_hi') and b in archetypes and b + '_hi' not in stream_models and any(b == d['model'] for d in weapons.values()):
                add('info', 'NO_HI_MODEL', name, f'{b} 没有 {b}_hi.ydr：原版枪都有 _hi（近距离/第一人称更细的一版），没有也能用')

        # ---------- drawable XML (optional) ----------
        xmls = dict(xml_index)
        xmls.update(xml_local)
        comp_by_model = {d['model']: (c, d['bone']) for c, d in components.items() if d['model']}
        for w, d in weapons.items():
            for suffix, kind in (('', 'base'), ('_hi', 'hi')):
                x = xmls.get(d['model'] + suffix)
                if not x:
                    continue
                try:
                    info = ydr_xml_info(x)
                except (ET.ParseError, OSError) as e:
                    add('error', 'XML_PARSE', os.path.basename(x), f'读不了：{e}')
                    continue
                if not info['bones']:
                    add('error', 'XML_NO_SKELETON', os.path.basename(x), '这个武器模型没有骨架：网格要挂在原版武器骨架（Gun_Root…）下面、顶点组用骨骼名')
                    continue
                need = list(REQUIRED_BONES) + (['gun_muzzle'] if d['gun'] else [])
                miss = [b for b in need if b not in info['bones']]
                if miss:
                    add('error', 'XML_BONES_MISSING', os.path.basename(x), f"缺少骨骼 {', '.join(miss)}：从最接近的原版枪导入骨架，不要自己新建")
                for bone, c, _ in d['aps']:
                    if low(bone) not in info['bones']:
                        add('error', 'XML_ATTACH_BONE_MISSING', os.path.basename(x), f'AttachPoints 用了 {bone}，但骨架里没有这根骨骼：{c.upper()} 会装不上或飘在原点')
                if kind == 'base' and not info['bounds']:
                    add('warn', 'XML_NO_BOUNDS', os.path.basename(x), '本体没有碰撞（Bounds）：原版本体都有 1–5 个 Box 碰撞，丢在地上会穿地')
                if kind == 'hi' and info['bounds']:
                    add('info', 'XML_HI_BOUNDS', os.path.basename(x), '原版 _hi 没有碰撞，碰撞只放本体')
                if info['tris'] > TRI_BUDGET[kind]:
                    add('warn', 'XML_TRIS_HIGH', os.path.basename(x), f"{info['tris']} 个三角面，超过经验上限 {TRI_BUDGET[kind]}（原版本体 0.8k–4k、_hi 3k–9k）")
                if info['embedded_txd']:
                    add('info', 'XML_EMBEDDED_TXD', os.path.basename(x), '贴图嵌在模型里；原版武器都用外部 .ytd（archetype 的 txdName）')
        for model, (c, bone) in comp_by_model.items():
            x = xmls.get(model)
            if not x:
                continue
            try:
                info = ydr_xml_info(x)
            except (ET.ParseError, OSError) as e:
                add('error', 'XML_PARSE', os.path.basename(x), f'读不了：{e}')
                continue
            if info['bones'] and bone and info['bones'][0] != low(bone):
                add('warn', 'XML_COMPONENT_ROOT', os.path.basename(x), f"{c.upper()} 的骨架第一根骨骼是 {info['bones'][0]}，要和 AttachBone {bone} 一样（原版弹匣只有一根 AAPClip）")
            if not info['bones']:
                add('warn', 'XML_COMPONENT_ROOT', os.path.basename(x), f'{c.upper()} 的模型没有骨架：配件要有一根 {bone or "AAP*"} 骨骼、全部顶点放进同名顶点组')
            if info['tris'] > TRI_BUDGET['part']:
                add('warn', 'XML_TRIS_HIGH', os.path.basename(x), f"配件 {info['tris']} 个三角面，超过经验上限 {TRI_BUDGET['part']}（原版弹匣/配件 38–744）")

        # ---------- ox_inventory ----------
        if ox_text is not None:
            for w, d in weapons.items():
                entry = ox_entry(ox_text, w)
                if entry is None:
                    add('error', 'OX_MISSING', d['file'], f"ox_inventory data/weapons.lua 没有 ['{w.upper()}']（key 或 model 要和 weapons.meta 的 Name 完全一样，否则装备时手上是空的）")
                    continue
                am = re.search(r"ammoname\s*=\s*['\"]([^'\"]+)['\"]", entry)
                if am and not re.search(r"\[\s*['\"]" + re.escape(am.group(1)) + r"['\"]\s*\]\s*=", ox_text):
                    add('error', 'OX_AMMO_MISSING', d['file'], f"ox 的 ammoname '{am.group(1)}' 没有对应的弹药物品")
                img_dir = os.path.join(ox, 'web', 'images')
                if not re.search(r'image\s*=', entry) and not any(
                        os.path.isfile(os.path.join(img_dir, n + ext)) for n in (w.upper(), w) for ext in ('.png', '.webp')):
                    add('warn', 'OX_IMAGE_MISSING', d['file'], f'ox_inventory/web/images 没有 {w.upper()}.png，背包里没图片')
                for bone, c, default in d['aps']:
                    if not default and ('`' + c.upper() + '`') not in ox_text.upper():
                        add('warn', 'OX_COMPONENT_MISSING', d['file'], f'{c.upper()} 不在 ox 任何配件物品的 client.component 列表里，玩家装不上这个配件')
    return findings


def ox_entry(text, weapon):
    """Body of the ox_inventory Weapons entry whose key or model equals the weapon name, else None."""
    for m in re.finditer(r"\[\s*['\"]([A-Za-z0-9_]+)['\"]\s*\]\s*=\s*\{", text):
        start, depth, i = m.end(), 1, m.end()
        while i < len(text) and depth:
            depth += {'{': 1, '}': -1}.get(text[i], 0)
            i += 1
        body = text[start:i - 1]
        mm = re.search(r"\bmodel\s*=\s*['\"]([^'\"]+)['\"]", body)
        if m.group(1).lower() == weapon or (mm and mm.group(1).lower() == weapon):
            return body
    return None


def main():
    ap = argparse.ArgumentParser(description='Check a FiveM add-on / replacement weapon resource (read-only)')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--ox', help='ox_inventory resource folder (checks data/weapons.lua and web/images)')
    ap.add_argument('--xml', action='append', default=[], help='folder with exported .ydr.xml (bones, bounds, triangles)')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows consoles default to cp1252
    findings = check(args.paths, ox=args.ox, xml_dirs=args.xml)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                print(f"{icons[level]} {x['code']}: [{x['file']}] {x['message']}")
        n = {lv: sum(f['level'] == lv for f in findings) for lv in icons}
        print(f"共 {n['error']} 个错误、{n['warn']} 个警告、{n['info']} 个提示" if findings else '✓ 没发现问题')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
