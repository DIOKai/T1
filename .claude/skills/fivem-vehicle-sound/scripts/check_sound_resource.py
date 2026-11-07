#!/usr/bin/env python3
"""Check FiveM add-on vehicle sound resources (and the cars that use them). Read-only, standard library only.

Usage:
    python check_sound_resource.py <folder> [more folders] [--json]

<folder> can be one sound resource, a folder of resources (e.g. resources/[sounds]) or a whole server
resources folder; vehicles.meta files found anywhere in the scanned folders are checked against the packs.
Exit code 1 when errors are found.

Checks (sources in the skill's references/sources.md):
- fxmanifest: audio data_file lines must not use globs (silent cars); the .dat convention (data_file points to
  xxx_game.dat while the file on disk is xxx_game.dat151.rel - Rockstar's own content.xml does the same);
  every data_file target exists (a missing one can crash clients on join); AUDIO_WAVEPACK folder exists and
  holds .awc; every .rel/.awc is listed in files{} (otherwise it is never sent to clients); .rel files with no
  data_file (e.g. an _amp.dat10.rel that is not mounted).
- .awc: 'ADAT' magic (plain AWC; vanilla files copied from the game may be encrypted); .awc file names unique across all scanned resources; wave-pack folders whose first 8
  characters collide (FiveM indexes wave packs by the first eight characters - cfx issue #2515, unverified in game);
  total add-on wave packs near the ~190 silent limit (issue #2515).
- vehicles.meta <audioNameHash>: each value should be a scanned pack name or a vanilla car (info only - vanilla
  names cannot be listed here); packs that no scanned car uses (a pack made for a car that still plays vanilla).
- CREDITS / readme present (packs usually contain audio the author cannot license; keep the credits).
"""
import argparse
import fnmatch
import json
import os
import re
import sys

AUDIO_TYPES = {'AUDIO_GAMEDATA': '151', 'AUDIO_SOUNDDATA': '54', 'AUDIO_SYNTHDATA': '10',
               'AUDIO_DYNAMIXDATA': '15', 'AUDIO_CURVEDATA': '12', 'AUDIO_SPEECHDATA': '4'}
SILENT_LIMIT = 190


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def files_patterns(text):
    pats = []
    for block in re.findall(r'\bfiles\s*\{(.*?)\}', text, flags=re.S):
        pats += re.findall(r"['\"]([^'\"]+)['\"]", block)
    pats += re.findall(r"\bfile\s*\(?\s*['\"]([^'\"]+)['\"]", text)
    return [p.replace('\\', '/').lower() for p in pats]


def matches(path, pats):
    for p in pats:
        if path == p or fnmatch.fnmatch(path, p) or fnmatch.fnmatch(path, p.replace('**/', '')):
            return True
    return False


def check(paths):
    findings = []

    def add(level, code, where, msg):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg})

    manifests, metas = [], []
    for base in paths:
        for root, dirs, fs in os.walk(base):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in fs:
                if f.lower() == 'fxmanifest.lua':
                    manifests.append(os.path.join(root, f))
                elif f.lower().endswith('vehicles.meta'):
                    metas.append(os.path.join(root, f))

    pack_names, awc_owner, wavepacks = {}, {}, []
    for man in manifests:
        res = os.path.dirname(man)
        rname = os.path.basename(res)
        with open(man, encoding='utf-8', errors='replace') as fh:
            text = strip_lua_comments(fh.read())
        all_files = []
        for root, _, fs in os.walk(res):
            all_files += [os.path.relpath(os.path.join(root, f), res).replace(os.sep, '/') for f in fs]
        low = [f.lower() for f in all_files]
        rels = [f for f in low if f.endswith('.rel')]
        awcs = [f for f in low if f.endswith('.awc')]
        dfs = re.findall(r"data_file\s*\(?\s*['\"]([A-Z0-9_]+)['\"]\s*\)?\s*\(?\s*['\"]([^'\"]+)['\"]", text)
        audio_dfs = [(t, p.replace('\\', '/')) for t, p in dfs if t in AUDIO_TYPES or t == 'AUDIO_WAVEPACK']
        if not audio_dfs and not rels and not awcs:
            continue
        where = f'{rname}/fxmanifest.lua'
        pats = files_patterns(text)
        mounted = set()
        for t, p in audio_dfs:
            pl = p.lower()
            if any(c in pl for c in '*?['):
                add('error', 'AUDIO_DATAFILE_GLOB', where, f"data_file '{t}' '{p}' 用了通配符。音频的 data_file 要一个文件一行写清楚，否则车会没声音（files{{}} 里可以用通配符）")
                continue
            if t == 'AUDIO_WAVEPACK':
                inside = [a for a in awcs if a.startswith(pl.rstrip('/') + '/')]
                if not any(f.lower() == pl or f.lower().startswith(pl.rstrip('/') + '/') for f in all_files):
                    add('error', 'WAVEPACK_MISSING', where, f"AUDIO_WAVEPACK '{p}' 这个资料夹不存在")
                elif not inside:
                    add('error', 'WAVEPACK_EMPTY', where, f"AUDIO_WAVEPACK '{p}' 里没有 .awc")
                folder = os.path.basename(pl.rstrip('/'))
                wavepacks.append((folder, where))
                continue
            num = AUDIO_TYPES[t]
            if pl.endswith('.rel'):
                add('warn', 'DATAFILE_REL_SUFFIX', where, f"data_file '{t}' '{p}' 直接写到 .rel。惯例（Rockstar 的 content.xml 和社群包都是）是写到 .dat 为止，例如 xxx_game.dat，游戏自己补上 {num}.rel")
                target = pl
            elif pl.endswith('.dat'):
                target = pl + num + '.rel'
            else:
                target = pl
            if target not in low:
                add('error', 'DATAFILE_TARGET_MISSING', where, f"data_file '{t}' '{p}' 对应的 {os.path.basename(target)} 不在资源里。缺文件可能让玩家进服时闪退")
            else:
                mounted.add(target)
                if t == 'AUDIO_GAMEDATA':
                    pname = re.sub(r'_game\.dat151\.rel$', '', os.path.basename(target))
                    # an engine pack has a granular NPC bank <name>_npc.awc; MLO occlusion / script SFX packs don't
                    if any(os.path.basename(a) == pname + '_npc.awc' for a in awcs):
                        pack_names[pname] = rname
        for r in rels:
            listed = bool(pats) and matches(r, pats)
            if r in mounted and pats and not listed:
                add('error', 'NOT_IN_FILES', where, f"{r} 有 data_file 但没写进 files{{}}，不会传给玩家")
            elif r not in mounted and listed:
                add('warn', 'REL_NOT_MOUNTED', where, f"{r} 写进了 files{{}} 但没有对应的 data_file。没挂上去的 dat10（_amp）会让引用它的引擎没声音或用错音色")
            elif r not in mounted:
                add('info', 'REL_UNUSED', where, f"{r} 既没有 data_file 也没写进 files{{}}，是用不到的多余档案（可以清掉，不影响游戏）")
        for f in awcs:
            if pats and not matches(f, pats):
                add('error', 'NOT_IN_FILES', where, f"{f} 没写进 files{{}}，不会传给玩家")
        if not pats and (rels or awcs):
            add('error', 'NO_FILES_BLOCK', where, "没有 files{} 区块，.rel 和 .awc 都不会传给玩家")
        for a in awcs:
            full = os.path.join(res, a)
            try:
                with open(full, 'rb') as fh:
                    magic = fh.read(4)
            except OSError:
                magic = b''
            if magic != b'ADAT':
                add('warn', 'AWC_NOT_PLAIN', f'{rname}/{a}', "开头不是 'ADAT'：要嘛是从游戏档案直接复制的加密 .awc（原版 DLC 音频，通常能用），要嘛是损坏。自己做或改过的包一定要是 'ADAT' 开头；用 CodeWalker 打开确认")
            awc_owner.setdefault(os.path.basename(a), []).append(f'{rname}/{a}')
        if not any(re.search(r'(credit|readme|licen)', f) for f in low):
            add('info', 'NO_CREDITS', where, '没有 CREDITS / readme。保留原作者、来源和授权说明（大部分声浪包含有作者无权授权的游戏音频，只能自己伺服器用）')

    for name, where in awc_owner.items():
        if len(where) > 1:
            add('error', 'AWC_NAME_DUPLICATE', where[0], f"{name} 出现在 {len(where)} 个地方（{', '.join(where)}）。wave pack 会被合并到同一个虚拟资料夹，撞名的会互相盖掉")
    by8 = {}
    for folder, where in wavepacks:
        by8.setdefault(folder[:8], set()).add(folder)
    for k, v in by8.items():
        if len(v) > 1:
            add('info', 'WAVEPACK_PREFIX8', ', '.join(sorted(v)), f"这些 wave pack 名字的前 8 个字都是 '{k}'。FiveM 依前 8 个字索引 wave pack（issue #2515，未在游戏里验证）；里面的 .awc 名字要全部不同，进游戏逐台测一次")
    if len(wavepacks) > SILENT_LIMIT - 20:
        add('warn', 'NEAR_AUDIO_LIMIT', f'{len(wavepacks)} wave packs', f"扫描到 {len(wavepacks)} 个 add-on wave pack。超过约 {SILENT_LIMIT} 个之后，后面载入的会没声音而且不报错（cfx issue #2515）")

    used = set()
    for meta in metas:
        with open(meta, encoding='utf-8', errors='replace') as fh:
            text = fh.read()
        for model, hashname in re.findall(r'<modelName>\s*([^<\s]+)\s*</modelName>.*?<audioNameHash>\s*([^<\s]*)\s*</audioNameHash>', text, flags=re.S):
            hn = hashname.lower()
            used.add(hn)
            rel = os.path.relpath(meta, paths[0]).replace(os.sep, '/')
            if not hn:
                add('info', 'AUDIO_HASH_EMPTY', rel, f"{model}: audioNameHash 是空的，会用 handling/模型默认声音")
            elif hn in pack_names:
                add('info', 'AUDIO_HASH_OK', rel, f"{model} → {hn}（{pack_names[hn]}）。声音资源要在车之前 ensure")
            else:
                add('info', 'AUDIO_HASH_OTHER', rel, f"{model} → {hn}：不在扫描到的声浪包里。是原版车的声音就没问题；是 add-on 包的话检查名字（要等于包里 dat151 车辆项目的 Name）")
    if metas:
        for name, rname in sorted(pack_names.items()):
            if name not in used:
                add('warn', 'PACK_UNUSED', f'{rname}', f"声浪包 '{name}' 装了，但扫描到的 vehicles.meta 没有一台车的 audioNameHash 用它（做给哪台车的？那台车可能还在用原版声音）。只在扫描范围包含所有车辆资源时才准")
    return findings


def main():
    ap = argparse.ArgumentParser(description='Check FiveM vehicle sound resources (read-only)')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--quiet-info', action='store_true', help='hide info lines')
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    findings = check([os.path.abspath(p) for p in args.paths])
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            if level == 'info' and args.quiet_info:
                continue
            for f in [x for x in findings if x['level'] == level]:
                print(f"{icons[level]} {f['code']}: [{f['file']}] {f['message']}")
        if not any(f['level'] != 'info' for f in findings):
            print('✓ 没发现错误或警告')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
