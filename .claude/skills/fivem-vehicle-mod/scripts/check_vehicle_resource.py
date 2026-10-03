#!/usr/bin/env python3
"""Cross-check FiveM add-on vehicle resources.

Covers what fivem-vehicle-validator does not: names that must match across
files (modelName / .yft, txdName / .ytd, handlingId / handlingName, kit names),
modkit / siren / light id collisions and ranges between resources, handlingName
overrides between resources, invalid data_file types, vehiclelayouts
declarations, and files{} / data_file entries written with globs.

Usage:
    python check_vehicle_resource.py <resource-or-folder> [more paths] [--json]

A path can be one resource (has fxmanifest.lua) or a folder such as
resources/[cars]; every resource below it is scanned, so id collisions between
resources are found. Standard library only. Exit code 1 when errors are found.
"""
import argparse
import fnmatch
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

DATA_FILE_TYPES = {
    'vehicles.meta': 'VEHICLE_METADATA_FILE',
    'handling.meta': 'HANDLING_FILE',
    'carcols.meta': 'CARCOLS_FILE',
    'carvariations.meta': 'VEHICLE_VARIATION_FILE',
    'vehiclelayouts.meta': 'VEHICLE_LAYOUTS_FILE',
}
# Valid data_file types, from citizenfx/fivem-docs game-references/data-files.md (commit c2b2125, 2026-10-01).
# FiveM ignores any other type and logs "Could not add data_file ... invalid type".
KNOWN_DATA_FILE_TYPES = {
    'ACTION_TABLE_DEFINITIONS', 'ALTERNATE_VARIATIONS_FILE', 'AMBIENT_PED_MODEL_SET_FILE',
    'AMBIENT_PROP_MODEL_SET_FILE', 'AMBIENT_VEHICLE_MODEL_SET_FILE',
    'AMB_PROCEDURAL_BLOOD_FILE', 'AUDIO_CURVEDATA', 'AUDIO_DYNAMIXDATA', 'AUDIO_GAMEDATA',
    'AUDIO_SOUNDDATA', 'AUDIO_SPEECHDATA', 'AUDIO_SYNTHDATA', 'AUDIO_WAVEPACK', 'CARCOLS_FILE',
    'CLIP_SETS_FILE', 'COMBAT_BEHAVIOUR_OVERRIDE_FILE', 'CONDITIONAL_ANIMS_FILE',
    'CONTENT_UNLOCKING_META_FILE', 'DLC_ITYP_REQUEST', 'DLC_POP_GROUPS', 'DLC_SCRIPT_METAFILE',
    'DLC_WEAPON_PICKUPS', 'DRIVER_RULES_STD_FILE', 'EVENTS_OVERRIDE_FILE', 'EXPLOSIONFX_FILE',
    'EXPLOSION_INFO_FILE', 'EXPRESSION_SETS_FILE', 'EXTRA_FOLDER_MOUNT_DATA',
    'EXTRA_TITLE_UPDATE_DATA', 'FACIAL_CLIPSET_GROUPS_FILE', 'FIVEM_LOVES_YOU_1F764C843460150',
    'FIVEM_LOVES_YOU_447B37BE29496FA0', 'FIVEM_LOVES_YOU_9605D14551590909',
    'GTXD_PARENTING_DATA', 'HANDLING_FILE', 'INTERIOR_PROXY_ORDER_FILE',
    'LEVEL_STREAMING_FILE', 'LOADOUTS_FILE', 'MOVE_NETWORK_DEFS', 'MP_STATS_DISPLAY_LIST_FILE',
    'MP_STATS_UI_LIST_FILE', 'NM_TUNING_FILE', 'OVERLAY_INFO_FILE', 'PEDSTREAM_FILE',
    'PED_BOUNDS_FILE', 'PED_BRAWLING_STYLE_FILE', 'PED_COMPONENT_SETS_FILE',
    'PED_DAMAGE_APPEND_FILE', 'PED_DAMAGE_OVERRIDE_FILE', 'PED_FIRST_PERSON_ALTERNATE_DATA',
    'PED_FIRST_PERSON_ASSET_DATA', 'PED_METADATA_FILE', 'PED_OVERLAY_FILE',
    'PED_PERCEPTION_FILE', 'PED_PERSONALITY_FILE', 'PED_TASK_DATA_FILE', 'POPSCHED_FILE',
    'PTFXASSETINFO_FILE', 'SCALEFORM_DLC_FILE', 'SCALEFORM_PREALLOC_FILE',
    'SCENARIO_INFO_FILE', 'SCENARIO_POINTS_FILE', 'SCENARIO_POINTS_OVERRIDE_FILE',
    'SCENARIO_POINTS_OVERRIDE_PSO_FILE', 'SCENARIO_POINTS_PSO_FILE', 'SCRIPTFX_FILE',
    'SCRIPT_BRAIN_FILE', 'SHOP_PED_APPAREL_META_FILE', 'SP_STATS_DISPLAY_LIST_FILE',
    'SP_STATS_UI_LIST_FILE', 'STREAMING_REQUEST_LISTS_FILE', 'TATTOO_SHOP_DLC_FILE',
    'TEXTFILE_METAFILE', 'TIMECYCLEMOD_FILE', 'TRAINCONFIGS_FILE', 'TRAINTRACK_FILE',
    'VEHICLEEXTRAS_FILE', 'VEHICLE_LAYOUTS_FILE', 'VEHICLE_METADATA_FILE',
    'VEHICLE_SHOP_DLC_FILE', 'VEHICLE_VARIATION_FILE', 'VFXVEHICLEINFO_FILE',
    'WEAPONCOMPONENTSINFO_FILE', 'WEAPONINFO_FILE', 'WEAPONINFO_FILE_PATCH',
    'WEAPON_ANIMATIONS_FILE', 'WEAPON_METADATA_FILE', 'WEAPON_SHOP_INFO_METADATA_FILE',
    'ZONEBIND_FILE',
}
# FXServer warns when a streamed asset uses more than 16 MiB of physical or virtual memory and adds
# "Oversized assets can and WILL lead to streaming issues" above 48 MiB (ResourceStreamComponent.cpp).
# It measures the virtual and physical memory decoded from the RSC7 header (ConvertRSC7Size), not
# the compressed file size, so a 15 MB .ytd on disk can be a 30 MiB asset. Decode it the same way.
ASSET_WARN_MB = 16.0
ASSET_ERROR_MB = 48.0
STREAM_EXTS = ('.yft', '.ytd', '.ydr', '.ydd')


def rsc_page_size(flags):
    # FXServer ConvertRSC7Size / CodeWalker RpfFile.GetSizeFromFlags
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


def rsc_memory(path):
    """(virtual, physical) bytes from an RSC7/RSC8 header, or None."""
    with open(path, 'rb') as fh:
        head = fh.read(16)
    if len(head) < 16 or head[:4] not in (b'RSC7', b'RSC8'):
        return None
    _, _, virt, phys = struct.unpack('<4sIII', head)
    return rsc_page_size(virt), rsc_page_size(phys)


def find_resources(paths):
    found = []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(os.path.join(p, 'fxmanifest.lua')) or os.path.isfile(os.path.join(p, '__resource.lua')):
            found.append(p)
            continue
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if 'fxmanifest.lua' in files or '__resource.lua' in files:
                found.append(root)
                dirs[:] = []
    return sorted(set(found))


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def parse_manifest(res):
    path = os.path.join(res, 'fxmanifest.lua')
    if not os.path.isfile(path):
        path = os.path.join(res, '__resource.lua')
    text = strip_lua_comments(open(path, encoding='utf-8', errors='replace').read())
    files = []
    for block in re.findall(r'\bfiles\s*\{(.*?)\}', text, flags=re.S):
        files += re.findall(r'["\']([^"\']+)["\']', block)
    files += re.findall(r'\bfile\s+["\']([^"\']+)["\']', text)
    data_files = re.findall(r'\bdata_file\s*\(?\s*["\']([A-Z0-9_]+)["\']\s*\)?\s*\(?\s*["\']([^"\']+)["\']', text)
    return os.path.basename(path), files, data_files


def rel_files(res):
    out = []
    for root, dirs, files in os.walk(res):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            out.append(os.path.relpath(os.path.join(root, f), res).replace(os.sep, '/'))
    return out


def glob_match(pattern, relpath):
    pattern = pattern.replace('\\', '/')
    if '**' in pattern:
        regex = re.escape(pattern).replace(r'\*\*/', '(?:.*/)?').replace(r'\*\*', '.*').replace(r'\*', '[^/]*').replace(r'\?', '[^/]')
        return re.fullmatch(regex, relpath, flags=re.I) is not None
    return fnmatch.fnmatch(relpath.lower(), pattern.lower())


def xml_root(path):
    try:
        return ET.parse(path).getroot()
    except ET.ParseError as e:
        return e


def texts(root, tag):
    return [(el.text or '').strip() for el in root.iter(tag) if (el.text or '').strip()]


def value_attr(el):
    if el is None:
        return None
    return el.get('value') if el.get('value') is not None else (el.text or '').strip() or None


def check(paths):
    findings = []

    def add(level, code, res, msg):
        findings.append({'level': level, 'code': code, 'resource': os.path.basename(res) if res else '', 'message': msg})

    resources = find_resources(paths)
    if not resources:
        add('error', 'NO_RESOURCE', '', '找不到 fxmanifest.lua，路径要指向一个资源，或包含资源的文件夹')
        return findings, resources

    kit_ids, siren_ids, light_ids, model_owner, handling_owner = {}, {}, {}, {}, {}
    siren_uses = []

    for res in resources:
        manifest_name, files_decl, data_files = parse_manifest(res)
        allrel = rel_files(res)
        metas = {}
        for rp in allrel:
            base = rp.split('/')[-1].lower()
            if base in DATA_FILE_TYPES:
                metas.setdefault(base, []).append(rp)
        if not metas:
            continue  # not a vehicle resource
        if manifest_name == '__resource.lua':
            add('warn', 'LEGACY_MANIFEST', res, '用的是旧的 __resource.lua，建议改成 fxmanifest.lua')

        declared_types = {}
        for dtype, pattern in data_files:
            declared_types.setdefault(dtype, []).append(pattern)
        for dtype in declared_types:
            if dtype == 'TEXTFILE_METAFILE':
                add('warn', 'DATA_FILE_REFUSED', res, "data_file 'TEXTFILE_METAFILE'（dlctext.meta）FiveM 会直接拒绝，删掉；显示名用 AddTextEntry")
            elif dtype not in KNOWN_DATA_FILE_TYPES:
                add('warn', 'DATA_FILE_INVALID_TYPE', res, f"data_file 类型 '{dtype}' 不是有效类型，FiveM 会忽略（常见的错误写法：DLCTEXT_FILE、CARCONTENTUNLOCKS_FILE）")
        for dtype, patterns in declared_types.items():
            for pattern in patterns:
                if not any(glob_match(pattern, rp) for rp in allrel):
                    add('error', 'DATA_FILE_NO_MATCH', res, f"data_file '{dtype}' '{pattern}' 对不上任何文件（路径或大小写写错）")

        for base, rps in metas.items():
            dtype = DATA_FILE_TYPES[base]
            for rp in rps:
                if not any(glob_match(p, rp) for p in files_decl):
                    add('error', 'META_NOT_IN_FILES', res, f'{rp} 没有写进 files {{}}，游戏读不到')
                if not any(glob_match(p, rp) for p in declared_types.get(dtype, [])):
                    add('error', 'META_NO_DATA_FILE', res, f"{rp} 缺少 data_file '{dtype}' 声明")

        stream = {}
        for rp in allrel:
            name = rp.split('/')[-1]
            stem, ext = os.path.splitext(name.lower())
            if ext not in STREAM_EXTS:
                continue
            full = os.path.join(res, rp)
            stream.setdefault(ext, {})[stem] = full
            # Legacy RAGE resources start with the 'RSC7' magic (0x37435352, CodeWalker ResourceBuilder.cs).
            # Gen9 files for the Enhanced client (stream_enhanced/) use another format, so only check stream/.
            if not rp.lower().startswith('stream_enhanced/'):
                with open(full, 'rb') as fh:
                    magic = fh.read(4)
                if magic != b'RSC7':
                    add('warn', 'NOT_RSC7', res, f'{rp} 开头不是 RSC7，不像有效的 GTA V（Legacy）资源文件：可能损坏、只是占位、是 CodeWalker XML，或是放错到 stream/ 的 Gen9 文件。用 CodeWalker 或 OpenIV 打开确认')
            mem = rsc_memory(full)
            if mem:
                size, what = max((mem[0], '虚拟内存'), (mem[1], '物理（显存）内存'))
            else:
                size, what = os.path.getsize(full), '文件大小'
            mb = size / 1024 / 1024
            if mb > ASSET_ERROR_MB:
                add('error', 'ASSET_OVER_48MIB', res, f'{name} 的{what}是 {mb:.1f} MiB，超过 48MiB，FXServer 会明确警告一定会出串流问题（模型不加载、贴图掉）')
            elif mb > ASSET_WARN_MB:
                add('warn', 'ASSET_OVER_16MIB', res, f'{name} 的{what}是 {mb:.1f} MiB（按 RSC 头算，不是磁盘上的文件大小），FXServer 启动时会出现超过 16MiB 的警告，建议压缩贴图或拆出 +hi')

        handling_names, layout_names, kit_names = set(), set(), set()
        vehicles = []
        variations = []
        for base, rps in metas.items():
            for rp in rps:
                root = xml_root(os.path.join(res, rp))
                if isinstance(root, ET.ParseError):
                    add('error', 'XML_INVALID', res, f'{rp} 不是合法的 XML：{root}')
                    continue
                if base == 'handling.meta':
                    for item in root.iter('Item'):
                        hn = (item.findtext('handlingName') or '').strip()
                        if hn and item.get('type', 'CHandlingData') == 'CHandlingData':
                            fields = [c.tag for c in item if c.tag.startswith(('f', 'n', 'vec', 'str'))]
                            if len(fields) < 20:
                                add('warn', 'HANDLING_SPARSE', res, f"handling '{hn}' 只有 {len(fields)} 个字段（原版车通常有几十个），缺的会用默认值；建议从相似的原版车复制完整条目再调")
                    names = {t.upper() for t in texts(root, 'handlingName')}
                    handling_names |= names
                    for hn in names:
                        owner = handling_owner.setdefault(hn, os.path.basename(res))
                        if owner != os.path.basename(res):
                            add('warn', 'HANDLING_NAME_DUPLICATE', res, f"handlingName '{hn}' 也在 {owner} 里，后加载的会覆盖前面的")
                elif base == 'vehiclelayouts.meta':
                    layout_names |= {t.upper() for t in texts(root, 'Name')}
                elif base == 'carcols.meta':
                    kits = root.find('Kits')
                    for item in (kits if kits is not None else []):
                        kname = (item.findtext('kitName') or '').strip()
                        kid = value_attr(item.find('id'))
                        if kname:
                            kit_names.add(kname.lower())
                        if kid is not None:
                            kit_ids.setdefault(kid, []).append((os.path.basename(res), kname))
                    for section, bucket in (('Sirens', siren_ids), ('Lights', light_ids)):
                        sec = root.find(section)
                        for item in (sec if sec is not None else []):
                            sid = value_attr(item.find('id'))
                            if sid is not None:
                                bucket.setdefault(sid, []).append(os.path.basename(res))
                            if section == 'Sirens':
                                lights = item.find('sirens')
                                n = len(list(lights)) if lights is not None else 0
                                if n > 20:
                                    add('warn', 'SIREN_LIGHTS_OVER_20', res, f"siren 设置 {sid}（{(item.findtext('name') or '').strip()}）有 {n} 个灯，原版上限是 20 个（siren1…siren20），多出来的要靠玩家装 SSLA，Enhanced 不能用")
                elif base == 'vehicles.meta':
                    for item in root.iter('Item'):
                        model = (item.findtext('modelName') or '').strip()
                        if not model:
                            continue
                        missing = [f for f in ('layout', 'lodDistances', 'vehicleClass', 'type') if item.find(f) is None]
                        if missing:
                            add('warn', 'VEHICLES_META_SPARSE', res, f"'{model}' 的 vehicles.meta 缺少 {', '.join(missing)}，会用默认值；建议从相似的原版车复制完整条目再改")
                        vehicles.append({
                            'model': model,
                            'txd': (item.findtext('txdName') or '').strip(),
                            'handling': (item.findtext('handlingId') or '').strip(),
                            'layout': (item.findtext('layout') or '').strip(),
                            'audio': (item.findtext('audioNameHash') or '').strip(),
                            'class': (item.findtext('vehicleClass') or '').strip().upper(),
                            'flags': set((item.findtext('flags') or '').upper().split()),
                        })
                elif base == 'carvariations.meta':
                    for item in root.iter('Item'):
                        model = (item.findtext('modelName') or '').strip()
                        if not model:
                            continue
                        kits_el = item.find('kits')
                        kits = [(k.text or '').strip() for k in kits_el] if kits_el is not None else []
                        variations.append({'model': model, 'kits': [k for k in kits if k],
                                           'siren': value_attr(item.find('sirenSettings')),
                                           'light': value_attr(item.find('lightSettings'))})

        yfts, ytds = stream.get('.yft', {}), stream.get('.ytd', {})
        model_set = set()
        for v in vehicles:
            m = v['model'].lower()
            model_set.add(m)
            if m in model_owner and model_owner[m] != os.path.basename(res):
                add('error', 'MODEL_DUPLICATE', res, f"modelName '{v['model']}' 也在 {model_owner[m]} 里，两个资源会互相覆盖")
            model_owner.setdefault(m, os.path.basename(res))
            if m not in yfts:
                add('error', 'YFT_MISSING', res, f"vehicles.meta 的 modelName '{v['model']}' 找不到 {m}.yft，车会生成不了")
            if m + '_hi' not in yfts:
                add('info', 'YFT_HI_MISSING', res, f"没有 {m}_hi.yft（近距离高模）。Sollumz 只在模型有 Very High LOD 时才导出它，没有也能用")
            if v['txd'] and v['txd'].lower() not in ytds:
                add('warn', 'YTD_MISSING', res, f"txdName '{v['txd']}' 找不到 {v['txd'].lower()}.ytd，车可能没有贴图")
            if not v['handling']:
                add('error', 'NO_HANDLING_ID', res, f"'{v['model']}' 没有 handlingId")
            elif handling_names and v['handling'].upper() not in handling_names:
                add('error', 'HANDLING_ID_MISMATCH', res, f"'{v['model']}' 的 handlingId '{v['handling']}' 在 handling.meta 里找不到（有：{', '.join(sorted(handling_names))}），handling 不会生效")
            elif not handling_names:
                add('info', 'HANDLING_VANILLA', res, f"'{v['model']}' 用 handlingId '{v['handling']}'，这个资源没有 handling.meta，只有它是原版名字才会生效")
            if v['layout'] and layout_names and v['layout'].upper() not in layout_names and not v['layout'].upper().startswith('LAYOUT_'):
                add('warn', 'LAYOUT_UNKNOWN', res, f"layout '{v['layout']}' 不在本资源的 vehiclelayouts.meta 里，也不像原版 LAYOUT_*")
            if v['class'] == 'VC_EMERGENCY' and not v['flags'] & {'FLAG_EMERGENCY_SERVICE', 'FLAG_LAW_ENFORCEMENT'}:
                add('info', 'EMERGENCY_FLAGS', res, f"'{v['model']}' 是 VC_EMERGENCY，但 flags 里没有 FLAG_LAW_ENFORCEMENT / FLAG_EMERGENCY_SERVICE（警车通常两个都加，影响 NPC 反应和通缉逻辑）")
            if not v['audio'] or v['audio'] == '0':
                add('warn', 'NO_AUDIO', res, f"'{v['model']}' 的 audioNameHash 是空的，可能没有引擎声")
        for var in variations:
            if model_set and var['model'].lower() not in model_set:
                add('error', 'VARIATION_MODEL_UNKNOWN', res, f"carvariations.meta 的 modelName '{var['model']}' 不在 vehicles.meta 里")
            if var['siren'] not in (None, '0', ''):
                siren_uses.append((res, var['model'], var['siren']))
            for k in var['kits']:
                if k.lower() not in kit_names and not k.lower().startswith('0_default'):
                    add('warn', 'KIT_NOT_DEFINED', res, f"carvariations 用了改装套件 '{k}'，但本资源的 carcols.meta 里没有定义")

    for kid, owners in kit_ids.items():
        try:
            kid_num = int(kid)
        except ValueError:
            kid_num = None
        if kid_num is not None and kid_num > 65535:
            add('error', 'MODKIT_ID_RANGE', None, f'改装套件 id {kid} 超过 65535（FiveM 的上限）')
        elif kid_num is not None and kid_num < 1024:
            add('info', 'MODKIT_ID_LOW', None, f'改装套件 id {kid} 小于 1024，可能和原版或别的车撞号，建议用 1024 以上并在服务器上统一登记')
        if len(owners) > 1:
            who = ', '.join(f'{r}:{k}' for r, k in owners)
            add('error', 'MODKIT_ID_DUPLICATE', None, f'改装套件 id {kid} 被用了 {len(owners)} 次（{who}），改装菜单会错乱或消失')
    for res, model, sid in siren_uses:
        if sid not in siren_ids:
            add('info', 'SIREN_ID_UNDEFINED', res, f"'{model}' 的 carvariations sirenSettings={sid}，扫描到的 carcols.meta 里没有这个 siren id：用原版的 siren 设置就没问题；如果是自定义的，要把定义它的资源一起扫，或检查 id 有没有写错")
    for label, bucket, code in (('警笛 siren', siren_ids, 'SIREN_ID_DUPLICATE'), ('灯光 light', light_ids, 'LIGHT_ID_DUPLICATE')):
        for sid, owners in bucket.items():
            try:
                if int(sid) > 255:
                    add('error', code.replace('DUPLICATE', 'RANGE'), None, f'{label} id {sid} 超过 255（这个 id 只有一个字节，会溢出和别的撞号）')
            except ValueError:
                pass
            if len(owners) > 1:
                add('error', code, None, f'{label} id {sid} 重复：{", ".join(owners)}')
    return findings, resources


def main():
    ap = argparse.ArgumentParser(description='Cross-check FiveM add-on vehicle resources')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    findings, resources = check(args.paths)
    if args.json:
        print(json.dumps({'resources': [os.path.basename(r) for r in resources], 'findings': findings}, ensure_ascii=False, indent=2))
    else:
        print(f'扫描了 {len(resources)} 个资源')
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for f in [x for x in findings if x['level'] == level]:
                where = f"[{f['resource']}] " if f['resource'] else ''
                print(f"{icons[level]} {f['code']}: {where}{f['message']}")
        if not findings:
            print('✓ 没发现问题')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
