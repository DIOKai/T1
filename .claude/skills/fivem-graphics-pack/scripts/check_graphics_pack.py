#!/usr/bin/env python3
"""Check a FiveM graphics pack: timecycle modifiers, manifest, texture assets, ReShade files.

Usage:
    python check_graphics_pack.py <path> [more paths] [--json]

<path> can be a FiveM resource, a folder of resources, a timecycle XML, or a
ReShade folder (preset .ini, LUT .png). Standard library only, read-only.
Exit code 1 when errors are found.

Checks
- timecycle modifier XML: well formed, numMods equals the number of variables
  (the game reads numMods entries), variable names exist in the vanilla list
  (assets/timecycle_vars.txt, from w_extrasunny.xml), values are numbers,
  duplicate modifier names, names that look like vanilla names (overriding).
- fxmanifest.lua: timecycle XML not declared as TIMECYCLEMOD_FILE or not in
  files{}; WEATHER_FILE / TIME_FILE (unverified on Legacy, broken on Enhanced);
  visualsettings.dat with no script calling SET_VISUAL_SETTING_FLOAT (there
  is no data_file type for it; VisualSettingsNatives.cpp).
- streamed assets: virtual or physical memory over 16 MiB / 48 MiB, decoded
  from the RSC7 header exactly like FXServer's warning (ResourceStreamComponent
  ConvertRSC7Size) - the file size on disk is compressed and understates it;
  .ytd/.ydr/.yft without an RSC7 header.
- ReShade: preset .ini with no Techniques= line; LUT png not tiles^2 x tiles.
"""
import argparse
import fnmatch
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
VARS_FILE = os.path.join(HERE, '..', 'assets', 'timecycle_vars.txt')
MIB = 1024 * 1024
RSC_EXT = ('.ytd', '.ydr', '.yft', '.ydd', '.ybn', '.ymap', '.ytyp')


def load_vars():
    try:
        with open(VARS_FILE, encoding='utf-8') as fh:
            return {l.strip() for l in fh if l.strip()}
    except OSError:
        return set()


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


def rsc_page_size(flags):
    # same maths as FXServer ConvertRSC7Size (ResourceStreamComponent.cpp) and CodeWalker GetSizeFromFlags
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


def rsc_memory(path):
    """(virtual, physical) bytes from an RSC7/RSC8 header - what FXServer's 16/48 MiB warning measures."""
    with open(path, 'rb') as fh:
        head = fh.read(16)
    if len(head) < 16 or head[:4] not in (b'RSC7', b'RSC8'):
        return None
    _, _, virt, phys = struct.unpack('<4sIII', head)
    return rsc_page_size(virt), rsc_page_size(phys)


def png_size(path):
    with open(path, 'rb') as fh:
        head = fh.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    return struct.unpack('>II', head[16:24])


def check(paths):
    findings = []
    known = load_vars()

    def add(level, code, where, msg):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg})

    files = walk(paths)
    tc_files = {}
    all_mods = {}

    for f in files:
        name = os.path.basename(f)
        low = name.lower()
        r = rel(f, paths)
        if low.endswith('.xml'):
            try:
                root = ET.parse(f).getroot()
            except ET.ParseError as e:
                if 'timecycle' in low:
                    add('error', 'XML_INVALID', r, f'不是合法的 XML：{e}')
                continue
            if root.tag != 'timecycle_modifier_data':
                continue
            tc_files[f] = r
            for m in root.findall('modifier'):
                mname = m.get('name') or ''
                if not mname:
                    add('error', 'MODIFIER_NO_NAME', r, '有个 <modifier> 没有 name')
                    continue
                if mname.lower() in all_mods:
                    add('error', 'MODIFIER_DUPLICATE', r, f"modifier '{mname}' 重复（也在 {all_mods[mname.lower()]}），后加载的会盖掉前面的")
                all_mods[mname.lower()] = r
                if '_' not in mname:
                    add('warn', 'MODIFIER_NAME_GENERIC', r, f"modifier '{mname}' 名字太通用，可能和原版或别的资源撞名。加个前缀，例如 dio_gfx_warm")
                kids = list(m)
                try:
                    num = int(m.get('numMods', '-1'))
                except ValueError:
                    num = -1
                if num != len(kids):
                    add('error', 'NUMMODS_MISMATCH', r, f"modifier '{mname}' 的 numMods={m.get('numMods')}，但实际有 {len(kids)} 个变量。要改成 {len(kids)}")
                seen = set()
                for k in kids:
                    if k.tag in seen:
                        add('warn', 'VAR_DUPLICATE', r, f"modifier '{mname}' 里 {k.tag} 写了两次")
                    seen.add(k.tag)
                    if known and k.tag not in known:
                        add('error', 'VAR_UNKNOWN', r, f"modifier '{mname}' 的变量 '{k.tag}' 不在原版 timecycle 变量列表里（拼错了？）")
                    parts = (k.text or '').split()
                    try:
                        [float(x) for x in parts]
                        if not parts:
                            raise ValueError
                    except ValueError:
                        add('error', 'VAR_VALUE', r, f"modifier '{mname}' 的 {k.tag} 值 '{(k.text or '').strip()}' 不是数字（格式：<变量>值1 值2</变量>，生效的是第一个）")

    # manifests
    manifests = [f for f in files if os.path.basename(f) == 'fxmanifest.lua' or os.path.basename(f) == '__resource.lua']
    for man in manifests:
        res = os.path.dirname(man)
        r = rel(man, paths)
        text = strip_lua_comments(open(man, encoding='utf-8', errors='replace').read())
        data_files = re.findall(r"data_file\s*\(?\s*['\"]([A-Z_]+)['\"]\s*\)?\s*\(?\s*['\"]([^'\"]+)['\"]", text)
        declared = {(t, p.replace('\\', '/').lower()) for t, p in data_files}
        files_block = ' '.join(re.findall(r'files\s*\{(.*?)\}', text, flags=re.S)) + ' ' + ' '.join(re.findall(r"\bfile\s*['\"]([^'\"]+)['\"]", text))
        file_entries = [e.replace('\\', '/').lower() for e in re.findall(r"['\"]([^'\"]+)['\"]", files_block)]

        def in_files(p):
            p = p.replace('\\', '/').lower()
            return any(e == p or fnmatch.fnmatch(p, e) or fnmatch.fnmatch(p, e.replace('**', '*')) for e in file_entries)
        for t, p in data_files:
            if t in ('WEATHER_FILE', 'TIME_FILE'):
                add('warn', 'WEATHER_FILE_UNVERIFIED', r, f"data_file '{t}'：在 Legacy 上没查到可靠的成功例子，Enhanced 有已知问题（fivem issue #4240）。画质包用 TIMECYCLEMOD_FILE + SetExtraTimecycleModifier 更稳")
            res_files = [os.path.relpath(x, res).replace(os.sep, '/').lower() for x in files if x.startswith(res + os.sep)]
            pl = p.replace('\\', '/').lower()
            if not any(x == pl or fnmatch.fnmatch(x, pl) for x in res_files):
                add('error', 'DATA_FILE_NO_MATCH', r, f"data_file '{t}' '{p}' 在资源里找不到对应的文件")
            if '*' not in p and not in_files(p):
                add('error', 'DATA_FILE_NOT_IN_FILES', r, f"data_file '{t}' '{p}' 没有写进 files {{}}，客户端拿不到这个文件")
        for f, fr in tc_files.items():
            if not f.startswith(res + os.sep):
                continue
            relp = os.path.relpath(f, res).replace(os.sep, '/').lower()
            if ('TIMECYCLEMOD_FILE', relp) not in declared and not any(t == 'TIMECYCLEMOD_FILE' and ('*' in p or p.split('/')[-1] == relp.split('/')[-1]) for t, p in declared):
                add('error', 'TIMECYCLE_NOT_DECLARED', fr, f"这个 timecycle XML 没有用 data_file 'TIMECYCLEMOD_FILE' '{relp}' 注册，游戏不会加载它")
        scripts_text = ''
        for f in files:
            if f.startswith(res + os.sep) and f.lower().endswith(('.lua', '.js')) and os.path.basename(f) != 'fxmanifest.lua':
                scripts_text += open(f, encoding='utf-8', errors='replace').read()
        applies_vs = re.search(r'SET_VISUAL_SETTING_FLOAT|SetVisualSettingFloat', scripts_text)
        for f in files:
            if f.startswith(res + os.sep) and os.path.basename(f).lower() == 'visualsettings.dat' and not applies_vs:
                add('warn', 'VISUALSETTINGS_FILE', rel(f, paths), 'FiveM 没有 visualsettings.dat 的 data_file 类型，资源里也没有脚本调用 SetVisualSettingFloat，这个文件不会生效。要用客户端脚本读它（LoadResourceFile）再逐行 SetVisualSettingFloat(名字, 值)')

    # streamed assets and ReShade
    for f in files:
        low = os.path.basename(f).lower()
        r = rel(f, paths)
        parts = r.lower().split('/')
        if low.endswith(RSC_EXT) and any(x.startswith('stream') for x in parts[:-1]):
            mem = rsc_memory(f)
            if mem:
                size, what = max((mem[0], '虚拟（CPU）'), (mem[1], '物理（显存）'))
            else:
                size, what = os.path.getsize(f), '文件'
                if 'stream_enhanced' not in parts:
                    add('warn', 'NOT_RSC7', r, '开头不是 RSC7，不像编译好的 GTA 资源（改了扩展名的 XML 或损坏）')
            if size > 48 * MIB:
                add('error', 'ASSET_OVER_48MIB', r, f'{what}内存 {size / MIB:.1f} MiB，超过 48 MiB：FXServer 会警告这种文件"一定会"出串流问题（模型/贴图不加载）。贴图降到 2K 或拆开')
            elif size > 16 * MIB:
                add('warn', 'ASSET_OVER_16MIB', r, f'{what}内存 {size / MIB:.1f} MiB，超过 16 MiB（FXServer 警告线，按 RSC 头算，不是文件大小）。4K 贴图（4096² DXT5 约 21 MiB）很容易超')
        elif low.endswith('.ini') and ('reshade' in r.lower() or 'preset' in low):
            text = open(f, encoding='utf-8', errors='replace').read()
            if '[' in text and 'techniques=' not in text.lower() and 'effectsearchpaths' not in text.lower():
                add('warn', 'RESHADE_NO_TECHNIQUES', r, '像 ReShade 预设但没有 Techniques= 行，加载后不会开任何效果')
        elif low.endswith('.png') and 'lut' in low:
            size = png_size(f)
            if size:
                w, h = size
                if w != h * h:
                    add('warn', 'LUT_SIZE', r, f'LUT 是 {w}x{h}，LUT.fx 要横条：宽 = 高²（32 → 1024x32，64 → 4096x64）')
                elif h != 32:
                    add('info', 'LUT_TILES', r, f'LUT 是 {h} 格，LUT.fx 预设是 32：要在 PreprocessorDefinitions 设 fLUT_TileSizeXY={h},fLUT_TileAmount={h}')
    return findings


def main():
    ap = argparse.ArgumentParser(description='Check a FiveM graphics pack')
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
