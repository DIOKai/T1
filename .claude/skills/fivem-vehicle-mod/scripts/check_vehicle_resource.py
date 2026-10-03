#!/usr/bin/env python3
"""Cross-check FiveM add-on vehicle resources.

Covers what fivem-vehicle-validator does not: names that must match across
files (modelName / .yft, txdName / .ytd, handlingId / handlingName, kit names),
modkit / siren / light id collisions between resources, vehiclelayouts
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
import sys
import xml.etree.ElementTree as ET

DATA_FILE_TYPES = {
    'vehicles.meta': 'VEHICLE_METADATA_FILE',
    'handling.meta': 'HANDLING_FILE',
    'carcols.meta': 'CARCOLS_FILE',
    'carvariations.meta': 'VEHICLE_VARIATION_FILE',
    'vehiclelayouts.meta': 'VEHICLE_LAYOUTS_FILE',
}
YTD_LIMIT_MB = 16.0
YTD_WARN_MB = 12.0


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

    kit_ids, siren_ids, light_ids, model_owner = {}, {}, {}, {}

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
            if ext in ('.yft', '.ytd'):
                stream.setdefault(ext, {})[stem] = os.path.join(res, rp)
        for stem, full in stream.get('.ytd', {}).items():
            mb = os.path.getsize(full) / 1024 / 1024
            if mb > YTD_LIMIT_MB:
                add('error', 'YTD_OVER_16MB', res, f'{stem}.ytd 有 {mb:.1f}MB，超过 FiveM 16MB 串流上限')
            elif mb > YTD_WARN_MB:
                add('warn', 'YTD_NEAR_16MB', res, f'{stem}.ytd 有 {mb:.1f}MB，接近 16MB 上限')

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
                    handling_names |= {t.upper() for t in texts(root, 'handlingName')}
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
                elif base == 'vehicles.meta':
                    for item in root.iter('Item'):
                        model = (item.findtext('modelName') or '').strip()
                        if not model:
                            continue
                        vehicles.append({
                            'model': model,
                            'txd': (item.findtext('txdName') or '').strip(),
                            'handling': (item.findtext('handlingId') or '').strip(),
                            'layout': (item.findtext('layout') or '').strip(),
                            'audio': (item.findtext('audioNameHash') or '').strip(),
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
                add('warn', 'YFT_HI_MISSING', res, f"没有 {m}_hi.yft（近距离高模），确认是不是故意的")
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
            if not v['audio'] or v['audio'] == '0':
                add('warn', 'NO_AUDIO', res, f"'{v['model']}' 的 audioNameHash 是空的，可能没有引擎声")
        for var in variations:
            if model_set and var['model'].lower() not in model_set:
                add('error', 'VARIATION_MODEL_UNKNOWN', res, f"carvariations.meta 的 modelName '{var['model']}' 不在 vehicles.meta 里")
            for k in var['kits']:
                if k.lower() not in kit_names and not k.lower().startswith('0_default'):
                    add('warn', 'KIT_NOT_DEFINED', res, f"carvariations 用了改装套件 '{k}'，但本资源的 carcols.meta 里没有定义")

    for kid, owners in kit_ids.items():
        if len(owners) > 1:
            who = ', '.join(f'{r}:{k}' for r, k in owners)
            add('error', 'MODKIT_ID_DUPLICATE', None, f'改装套件 id {kid} 被用了 {len(owners)} 次（{who}），改装菜单会错乱或消失')
    for label, bucket, code in (('警笛 siren', siren_ids, 'SIREN_ID_DUPLICATE'), ('灯光 light', light_ids, 'LIGHT_ID_DUPLICATE')):
        for sid, owners in bucket.items():
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
