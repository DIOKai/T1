#!/usr/bin/env python3
"""Release gate for FiveM asset resources: find each resource's asset type(s), run the matching
per-type checker of the sibling skills, add cross-cutting checks, print one Chinese summary.

Usage:
    py -3 -I asset_gate.py <resource | folder of resources> [more] [--json] [--only prop,vehicle,...]
                           [--list] [--verbose] [--timeout 300]

Standard library only, read-only: the checkers are run as subprocesses with --json and never
write either. Exit code 2 when a checker crashed or timed out (result incomplete), 1 when any
error was found, 0 otherwise. "Static pass" is not "works in game": the summary ends with the
in-game checklist for the asset types it found.

Per-type checkers (looked up next to this skill, ../../<skill>/scripts/<file>):
  prop      fivem-prop-creator/check_prop_resource.py
  vehicle   fivem-vehicle-mod/check_vehicle_resource.py (+ fivem-vehicle-livery/check_livery.py)
  clothing  fivem-clothing-creator/check_clothing_resource.py
  map       fivem-mlo-housing/check_mlo_resource.py
  weapon    fivem-weapon/check_weapon_resource.py
  anim      fivem-animation/check_anim_resource.py
  sound     fivem-vehicle-sound/check_sound_resource.py
  graphics  fivem-graphics-pack/check_graphics_pack.py
  phone     fivem-phone/check_phone_app.py
  nui       fivem-menu-design/check_nui_menu.py
  ped       no checker - always reported as manual (需人工)

Each checker runs once per resource (exact attribution) and once over all resources of its type
when there are several (its cross-resource findings - duplicate names, id clashes - are kept as a
separate group). JSON shapes differ ([...] or {"findings": [...]}, key "file" or "resource"); both
are normalised to {level, code, file, message, checker}.

Gate checks (all types): NO_MANIFEST, XML_IN_STREAM, SOURCE_IN_STREAM, NAME_CASE, ASSET_OVER_16MIB /
48MIB (FXServer ResourceStreamComponent formula), ESCROWED (FXAP files / .fxap; other checkers'
NOT_RSC7 on FXAP files is dropped), NO_PROVENANCE (no CREDITS / LICENSE / README / SOURCE file),
CROSS_RESOURCE_DUPLICATE (same stream file name in two resources that no checker compared),
STREAM_ENHANCED_PARTIAL (stream_enhanced replaces stream on Enhanced - Cfx legacy-vs-enhanced).
A gate finding is dropped when a checker already reported the same code for that resource.
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(SKILLS, 'fivem-prop-creator', 'scripts'))
try:
    import rsc_probe  # noqa: E402  (shared stdlib RSC7 reader; optional)
except ImportError:   # pragma: no cover
    rsc_probe = None

MIB = 1024 * 1024
RSC_EXT = ('.ydr', '.yft', '.ydd', '.ytd', '.ytyp', '.ybn', '.ycd', '.ymap', '.ymt', '.yld', '.awc', '.ynv', '.ywr')
SOURCE_EXT = ('.blend', '.blend1', '.fbx', '.obj', '.dds', '.png', '.tga', '.psd', '.spp', '.max', '.mb', '.ma', '.jpg')
TYPE_LABEL = {'prop': '道具', 'vehicle': '车辆', 'clothing': '服装', 'map': '地图/MLO', 'weapon': '武器',
              'anim': '动画', 'sound': '音效', 'graphics': '画质包', 'phone': '手机/App', 'nui': 'NUI 界面',
              'ped': '人物 ped', 'script': '脚本（非素材）'}
CHECKERS = {   # type -> [(skill folder, script, optional)]
    'prop': [('fivem-prop-creator', 'check_prop_resource.py', False)],
    'vehicle': [('fivem-vehicle-mod', 'check_vehicle_resource.py', False),
                ('fivem-vehicle-livery', 'check_livery.py', True)],
    'clothing': [('fivem-clothing-creator', 'check_clothing_resource.py', False)],
    'map': [('fivem-mlo-housing', 'check_mlo_resource.py', False)],
    'weapon': [('fivem-weapon', 'check_weapon_resource.py', False)],
    'anim': [('fivem-animation', 'check_anim_resource.py', False)],
    'sound': [('fivem-vehicle-sound', 'check_sound_resource.py', False)],
    'graphics': [('fivem-graphics-pack', 'check_graphics_pack.py', False)],
    'phone': [('fivem-phone', 'check_phone_app.py', False)],
    'nui': [('fivem-menu-design', 'check_nui_menu.py', False)],
    'ped': [],
}
SHARED_CODES = {'DUPLICATE_ASSET', 'XML_IN_STREAM', 'SOURCE_IN_STREAM', 'NAME_CASE', 'NOT_RSC7', 'ASSET_OVER_16MIB',
                'ASSET_OVER_48MIB', 'NO_THIS_IS_A_MAP', 'ESCROWED', 'PROP_HEAVY'}
PATH_IN_MESSAGE = re.compile(r"([^\s'\"（(,，]+\.(?:xml|ydr|yft|ydd|ytd|ytyp|ybn|ycd|ymap|ymt|awc|blend|fbx|obj|dds|png|tga))", re.I)
GATE_CODES = {'NO_MANIFEST', 'XML_IN_STREAM', 'SOURCE_IN_STREAM', 'NAME_CASE', 'ASSET_OVER_16MIB',
              'ASSET_OVER_48MIB', 'ESCROWED'}
CHECKLIST = {
    'common': ['在本机测试服（不要连正式服）冷启动进服一次，再 restart 这个资源一次',
               'F8 和伺服器控制台找警告：16/48 MiB 超大资源、Could not add data_file、You lack the required entitlement（escrow）',
               '两个客户端一起看（同步、别人看得到）；Enhanced 和 Legacy 都要用的话两边都进'],
    'prop': ['用测试指令 CreateObject 生成，或 ymap 放置；从 0 m 走到 lodDist 再走远，从三个方向看 LOD 切换、不会太早消失',
             '走上去、绕一圈、从下面看、推它、开枪（弹孔和声音对应材质）、开车撞：碰撞对不对',
             '白天/晚上/下雨各看一次：晚上不发粉红光（顶点色）、emissive 晚上会亮',
             'Dynamic 道具推得动/会断、断了会重生；门：开、关、锁，两个客户端看到同一状态'],
    'vehicle': ['/car 生成；每个画质等级（Very High/High/Medium/Low）看 LOD',
                '开、撞、看变形和轮子；车灯、警灯警笛、夜间',
                '引擎舱/车底/破洞扫描（LESSONS）、改装菜单、引擎声'],
    'clothing': ['外观菜单逐件逐贴图看，男女都看', '极端姿势（蹲、举手、坐）看穿模', '两个客户端看同步'],
    'map': ['传送过去，从远处走近，经过每个 portal', '每层楼、楼梯、车道都走一遍，车开上坡道',
            '白天/晚上/下雨：室内灯、室内不下雨；第一人称；两个玩家；声音遮挡'],
    'weapon': ['给自己武器，看手上位置、瞄准、开火、换弹', '配件逐个装上看', 'ox_inventory 图片和名称'],
    'anim': ['逐个播放表情，看循环接缝、道具位置', '男女角色都试', '两个客户端看同步'],
    'sound': ['播放/触发，和原版比较音量', '远近衰减', '循环有没有爆音（audio-quality-check）'],
    'graphics': ['白天、黄昏、夜晚、雨天、室内各看一次', '对比帧数（开关画质包）'],
    'phone': ['打开手机和 App，每个画面走一遍', '重启手机资源后 App 还在'],
    'nui': ['打开/关闭界面、焦点和鼠标正常', '不同分辨率看排版', 'resmon 看空闲时 CPU'],
    'ped': ['当玩家和 NPC 各生成一次，看 LOD', '布娃娃、动画、脸部表情', '没有检查器：骨骼、权重、组件全靠人工（fivem-ped-character）'],
}


def find_resources(paths):
    found, loose = [], []
    for p in paths:
        p = os.path.abspath(p)
        hit = False
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            if 'fxmanifest.lua' in files or '__resource.lua' in files:
                found.append(root)
                hit = True
                dirs[:] = []
        if not hit and os.path.isdir(p):
            loose.append(p)
    return sorted(set(found)), loose


def list_files(root):
    out = []
    for r, dirs, fs in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        out += [os.path.join(r, f) for f in fs]
    return out


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def read_manifest(root):
    for name in ('fxmanifest.lua', '__resource.lua'):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            with open(p, encoding='utf-8', errors='replace') as fh:
                return strip_lua_comments(fh.read())
    return ''


def header(path):
    try:
        with open(path, 'rb') as fh:
            return fh.read(16)
    except OSError:
        return b''


def page_size(flags):
    s = (((flags >> 27) & 0x1) + (((flags >> 26) & 0x1) << 1) + (((flags >> 25) & 0x1) << 2)
         + (((flags >> 24) & 0x1) << 3) + (((flags >> 17) & 0x7F) << 4) + (((flags >> 11) & 0x3F) << 5)
         + (((flags >> 7) & 0xF) << 6) + (((flags >> 5) & 0x3) << 7) + (((flags >> 4) & 0x1) << 8))
    return (0x200 << (flags & 0xF)) * s


class Res:
    def __init__(self, root, loose=False):
        self.root = root
        self.name = os.path.basename(root)
        self.loose = loose
        self.files = list_files(root)
        self.rels = [os.path.relpath(f, root).replace(os.sep, '/') for f in self.files]
        self.manifest = '' if loose else read_manifest(root)
        self.types = set()
        self.findings = []     # normalised findings attributed to this resource
        self.checkers = []     # (name, exit code or 'crash')

    def streamed(self):
        out = []
        for f, r in zip(self.files, self.rels):
            parts = r.lower().split('/')[:-1]
            if any(x.startswith('stream') for x in parts):
                out.append((f, r))
        return out


def classify(res, ui=False):
    man = res.manifest
    names = [os.path.basename(r).lower() for r in res.rels]
    streamed = [(f, r.lower()) for f, r in res.streamed()]
    sexts = {os.path.splitext(r)[1] for _, r in streamed}
    snames = [os.path.basename(r) for _, r in streamed]
    t = set()
    if re.search(r'VEHICLE_METADATA_FILE|HANDLING_FILE|CARCOLS_FILE|VEHICLE_VARIATION_FILE', man) \
            or any(n in ('vehicles.meta', 'handling.meta', 'carcols.meta', 'carvariations.meta') for n in names) \
            or any(n.endswith('_hi.yft') for n in snames):
        t.add('vehicle')
    if re.search(r'WEAPONINFO_FILE|WEAPON_METADATA_FILE|WEAPONCOMPONENTSINFO_FILE', man) \
            or any(n.startswith(('weapons', 'weaponarchetypes', 'weaponcomponents')) and n.endswith('.meta') for n in names):
        t.add('weapon')
    if 'SHOP_PED_APPAREL_META_FILE' in man or any('^' in n and n.endswith(('.ydd', '.ytd', '.yld')) for n in snames):
        t.add('clothing')
    if 'PED_METADATA_FILE' in man or 'peds.meta' in names:
        t.add('ped')
    mlo = False
    if rsc_probe is not None:
        mlo = any(rsc_probe.ytyp_has_mlo(f) for f, r in streamed if r.endswith('.ytyp') and header(f)[:4] == b'RSC7')
    if sexts & {'.ymap', '.ymf'} or mlo or (re.search(r'\bthis_is_a_map\b', man) and '.ybn' in sexts and '.ytyp' not in sexts):
        t.add('map')
    models = sexts & {'.ydr', '.yft', '.ydd'}
    if models and not t & {'vehicle', 'weapon', 'clothing', 'ped'}:
        if '.ytyp' in sexts or 'DLC_ITYP_REQUEST' in man or 'map' not in t:
            t.add('prop')
    emotes = any(n.startswith('animationlist') and n.endswith('.lua') for n in names)
    if emotes or ('.ycd' in sexts and not t & {'vehicle', 'weapon'}):
        t.add('anim')   # vehicles and weapons ship their own .ycd; those are checked with them
    rel_audio = any(re.search(r'\.dat\d+\.rel$', n) for n in names)
    if any(n.endswith('.awc') for n in names) or 'AUDIO_WAVEPACK' in man or (rel_audio and 'map' not in t):
        t.add('sound')  # a .dat151.rel alone in a map resource is audio occlusion (map checker)
    if 'TIMECYCLEMOD_FILE' in man or 'visualsettings.dat' in names \
            or any(n.startswith('timecycle') and n.endswith('.xml') for n in names) or (sexts and sexts <= {'.ytd'}):
        t.add('graphics')   # texture-only resources (HD road / texture packs) belong to fivem-graphics-pack
    if ui:
        phone_text = man + ' ' + res.name.lower()
        if re.search(r'npwd|lb-phone|qb-phone|z-phone|RegisterExternalApp|AddCustomApp', phone_text, re.I):
            t.add('phone')
        elif re.search(r"\bui_page\b", man):
            t.add('nui')
    if not t:
        t.add('script')
    return t


def dedupe_shared(findings):
    """Two checkers on one resource (e.g. map + prop) both report packaging problems; keep the first
    of each (code, file name) for the codes every checker shares."""
    out, seen = [], set()
    for f in findings:
        if f['code'] in SHARED_CODES:
            name = os.path.basename(str(f['file'] or '')).lower()
            if name in ('', 'fxmanifest.lua', '__resource.lua') or '.' not in name:
                m = PATH_IN_MESSAGE.search(f['message'])   # some checkers point at the manifest, name the file in the text
                name = os.path.basename(m.group(1)).lower() if m else name
            key = (f['code'],) if f['code'] in ('NO_THIS_IS_A_MAP', 'ESCROWED') else (f['code'], name, f['level'])
            if key in seen:
                continue
            seen.add(key)
        out.append(f)
    return out


def checker_path(skill, script):
    return os.path.join(SKILLS, skill, 'scripts', script)


def run_checker(path, targets, timeout):
    """Returns (exit_code | 'crash' | 'timeout', findings, stderr tail)."""
    cmd = [sys.executable, '-I', '-X', 'utf8', path, *targets, '--json']   # utf8: some checkers print Chinese without reconfiguring stdout
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, cwd=os.path.dirname(path),
                           encoding='utf-8', errors='replace')
    except subprocess.TimeoutExpired:
        return 'timeout', [], ''
    try:
        data = json.loads(p.stdout or 'null')
    except json.JSONDecodeError:
        return 'crash', [], (p.stderr or p.stdout or '')[-400:]
    if isinstance(data, dict):
        data = data.get('findings', [])
    if not isinstance(data, list) or p.returncode not in (0, 1):
        return 'crash', [], (p.stderr or '')[-400:]
    out = []
    for f in data:
        if isinstance(f, dict):
            out.append({'level': f.get('level', 'info'), 'code': f.get('code', '?'),
                        'file': f.get('file') if f.get('file') is not None else f.get('resource'),
                        'message': f.get('message', '')})
    return p.returncode, out, ''


def resolve(res, where):
    """Absolute path of a checker's 'file' field inside res, or None."""
    if not where:
        return None
    w = str(where).replace('\\', '/')
    cands = [w]
    if w.startswith(res.name + '/'):
        cands.append(w[len(res.name) + 1:])
    for c in cands:
        p = os.path.join(res.root, c)
        if os.path.isfile(p):
            return p
    return None


def gate_checks(res, add):
    streamed = res.streamed()
    if res.loose:
        game = [r for _, r in streamed if r.lower().endswith(RSC_EXT)]
        if game:
            add('error', 'NO_MANIFEST', res.name, f'有 stream 文件夹和游戏文件（{game[0]} 等），但没有 fxmanifest.lua，伺服器不会载入')
    escrowed = 0
    for f, r in streamed:
        low = os.path.basename(r).lower()
        where = f'{res.name}/{r}'
        if low.endswith('.xml'):
            add('error', 'XML_IN_STREAM', where, 'XML 放在 stream 里不会被加载（改扩展名不是转换，要用 Sollumz/CodeWalker 导出成二进制）')
            continue
        if low.endswith(SOURCE_EXT):
            add('warn', 'SOURCE_IN_STREAM', where, '源文件/散装贴图放在 stream 里不会被游戏用，只会被玩家下载')
            continue
        if not low.endswith(RSC_EXT):
            continue
        base = os.path.basename(r)
        if ' ' in base:
            add('warn', 'NAME_CASE', where, f"文件名 '{base}' 有空格。FiveM 按文件名串流，统一小写、不要空格")
        elif base != base.lower():
            add('info', 'NAME_CASE', where, f"文件名 '{base}' 有大写（哈希不分大小写，一般能用；统一小写比较不会搞混）")
        head = header(f)
        if head[:4] == b'FXAP':
            escrowed += 1
            continue
        if head[:4] in (b'RSC7', b'RSC8') and len(head) >= 16:
            v, p = int.from_bytes(head[8:12], 'little'), int.from_bytes(head[12:16], 'little')
            size, what = max((page_size(v), '虚拟'), (page_size(p), '物理（显存）'))
            if size > 48 * MIB:
                add('error', 'ASSET_OVER_48MIB', where, f'{what}内存 {size / MIB:.1f} MiB > 48 MiB，FXServer 说一定会出串流问题')
            elif size > 16 * MIB:
                add('warn', 'ASSET_OVER_16MIB', where, f'{what}内存 {size / MIB:.1f} MiB > 16 MiB（FXServer 警告线）')
    fxap_files = [r for r in res.rels if r.lower().endswith('.fxap')]
    if escrowed or fxap_files:
        add('warn', 'ESCROWED', res.name, f'Cfx Asset Escrow 加密：{escrowed} 个 stream 文件开头是 FXAP' + ('，根目录有 .fxap' if fxap_files else '')
            + '。加密部分的内容、大小、LOD 都没检查，要靠游戏内测试；只能在买它的 Cfx 帐号拥有的伺服器 key 上用，不要尝试解密')
    if not res.types <= {'script', 'nui', 'phone'}:
        top = [r for r in res.rels if '/' not in r]
        if not any(re.search(r'(credit|licen[cs]e|readme|source|attribution|notice|copying)', r, re.I) for r in top):
            add('warn', 'NO_PROVENANCE', res.name, '根目录没有 CREDITS / LICENSE / README / SOURCE 文件。记下作者、来源网址、授权、日期（转换的要记原档哈希）；“免费下载”不等于可以转发')
    dirs = {r.lower().split('/')[0] for r in res.rels if '/' in r}
    if 'stream' in dirs and 'stream_enhanced' in dirs:
        legacy = {os.path.basename(r).lower() for _, r in streamed if r.lower().startswith('stream/') and r.lower().endswith(RSC_EXT)}
        enhanced = {os.path.basename(r).lower() for _, r in streamed if r.lower().startswith('stream_enhanced/')}
        missing = sorted(legacy - enhanced)
        if missing:
            add('warn', 'STREAM_ENHANCED_PARTIAL', res.name, f"有 stream_enhanced，但 {len(missing)} 个 stream 文件（{', '.join(missing[:4])}…）不在里面。"
                'Cfx 文档：有 stream_enhanced 时 Enhanced 版只载入它、不载入 stream；Enhanced 不需要这些文件的话可以忽略')


def main():
    ap = argparse.ArgumentParser(description='FiveM asset release gate (read-only)')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--only', help='comma list of types: ' + ','.join(t for t in TYPE_LABEL if t != 'script'))
    ap.add_argument('--list', action='store_true', help='only list resources and detected types')
    ap.add_argument('--verbose', action='store_true', help='print every finding, info included')
    ap.add_argument('--ui', action='store_true', help='also run the phone / NUI checkers on UI resources')
    ap.add_argument('--timeout', type=int, default=300)
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    only = set(args.only.split(',')) if args.only else None
    report = gate(args.paths, only=only, run=not args.list, timeout=args.timeout,
                  ui=args.ui or bool(only and only & {'phone', 'nui'}))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report, verbose=args.verbose, listing=args.list)
    if args.list:
        sys.exit(0)
    if report['summary']['crashed']:
        sys.exit(2)
    sys.exit(1 if report['summary']['failed'] or any(f['level'] == 'error' for f in report['cross']) else 0)


def gate(paths, only=None, run=True, timeout=300, ui=False):
    roots, loose = find_resources(paths)
    resources = [Res(r) for r in roots] + [Res(p, loose=True) for p in loose]
    for r in resources:
        r.types = classify(r, ui=ui)
        if only:
            r.types &= only
    resources = [r for r in resources if r.types]
    cross, crashed, missing = [], [], set()
    if run:
        by_checker = {}
        for r in resources:
            for t in sorted(r.types):
                for skill, script, optional in CHECKERS.get(t, []):
                    path = checker_path(skill, script)
                    if not os.path.isfile(path):
                        if not optional and (skill, script) not in missing:
                            missing.add((skill, script))
                            cross.append({'level': 'warn', 'code': 'CHECKER_MISSING', 'file': f'{skill}/scripts/{script}',
                                          'message': f'找不到 {TYPE_LABEL[t]} 的检查器 {skill}/scripts/{script}，这类资源只做了通用检查', 'checker': 'gate'})
                        continue
                    by_checker.setdefault(path, []).append(r)
        for path, group in by_checker.items():
            cname = os.path.basename(path)
            seen = set()
            for r in group:
                code, found, err = run_checker(path, [r.root], timeout)
                r.checkers.append((cname, code))
                if code in ('crash', 'timeout'):
                    crashed.append((cname, r.name, err))
                    r.findings.append({'level': 'error', 'code': 'CHECKER_CRASHED', 'file': r.name, 'checker': 'gate',
                                       'message': f'{cname} {"超时" if code == "timeout" else "出错"}，这个资源的结果不完整：{err.strip()[-200:]}'})
                    continue
                for f in found:
                    f['checker'] = cname
                    seen.add((f['code'], f['message']))
                    if f['code'] == 'NOT_RSC7':
                        p = resolve(r, f['file'])
                        if p and header(p)[:4] == b'FXAP':
                            continue
                    r.findings.append(f)
            if len(group) > 1:
                targets = [r.root for r in group]
                batches, cur, length = [], [], 0
                for t in targets:   # keep the Windows command line under ~30k characters
                    if cur and length + len(t) > 24000:
                        batches.append(cur)
                        cur, length = [], 0
                    cur.append(t)
                    length += len(t) + 3
                batches.append(cur)
                for b in batches:
                    code, found, err = run_checker(path, b, timeout)
                    if code in ('crash', 'timeout'):
                        crashed.append((cname, f'{len(b)} 个资源合并检查', err))
                        continue
                    for f in found:
                        if (f['code'], f['message']) not in seen and f['level'] in ('error', 'warn'):
                            f['checker'] = cname
                            cross.append(f)
                            seen.add((f['code'], f['message']))
    # gate checks
    for r in resources if run else []:
        mine = []
        gate_checks(r, lambda lv, c, w, m: mine.append({'level': lv, 'code': c, 'file': w, 'message': m, 'checker': 'gate'}))
        reported = {f['code'] for f in r.findings}
        r.findings += [f for f in mine if not (f['code'] in GATE_CODES and f['code'] in reported)]
        r.findings = dedupe_shared(r.findings)
    # cross-resource duplicates no checker compared
    owners = {}
    for r in resources if run else []:
        for f, rel in r.streamed():
            low = os.path.basename(rel).lower()
            if low.endswith(RSC_EXT) and not rel.lower().startswith('stream_enhanced/') and '/stream_enhanced/' not in rel.lower():
                owners.setdefault(low, []).append(r)
    cross_text = ' '.join(f['message'] for f in cross)
    for low, rs in sorted(owners.items()):
        uniq = list(dict.fromkeys(rs))
        if len(uniq) > 1 and low not in cross_text:
            names = ', '.join(f"{x.name}（{'/'.join(TYPE_LABEL.get(t, t) for t in sorted(x.types))}）" for x in uniq[:4])
            cross.append({'level': 'error', 'code': 'CROSS_RESOURCE_DUPLICATE', 'file': ', '.join(x.name for x in uniq[:4]),
                          'message': f"'{low}' 同时在 {len(uniq)} 个资源里串流：{names}。只有一个会生效（载入顺序决定），要改名或删掉一份",
                          'checker': 'gate'})
    # summary
    out = {'resources': [], 'cross': cross, 'summary': {}}
    counts = {'passed': 0, 'warned': 0, 'failed': 0, 'manual': 0, 'skipped': 0}
    for r in resources:
        lv = [f['level'] for f in r.findings]
        if any(f['code'] == 'CHECKER_CRASHED' for f in r.findings):
            status = 'incomplete'
        elif 'error' in lv:
            status = 'failed'
        elif r.types == {'script'}:
            status = 'skipped'
        elif 'warn' in lv:
            status = 'warned'
        elif 'ped' in r.types or any(f['code'] == 'ESCROWED' for f in r.findings) or not r.checkers:
            status = 'manual'
        else:
            status = 'passed'
        if status in counts:
            counts[status] += 1
        out['resources'].append({'name': r.name, 'path': r.root, 'types': sorted(r.types), 'status': status,
                                 'checkers': [{'name': n, 'exit': c} for n, c in r.checkers],
                                 'findings': r.findings})
    counts['crashed'] = len(crashed)
    counts['incomplete'] = sum(1 for x in out['resources'] if x['status'] == 'incomplete')
    counts['total'] = len(resources)
    types = sorted({t for r in resources for t in r.types} - {'script'})
    counts['types'] = types
    out['summary'] = counts
    out['checklist'] = {t: CHECKLIST.get(t, []) for t in ['common'] + types if t in CHECKLIST}
    return out


ICON = {'failed': '✘ 失败', 'warned': '⚠ 警告', 'passed': '✓ 通过', 'manual': '⧗ 需人工', 'incomplete': '⧗ 未完成',
        'skipped': '· 跳过'}
LEVEL = {'error': '✘', 'warn': '⚠', 'info': 'ℹ'}


def print_report(rep, verbose=False, listing=False):
    order = {'failed': 0, 'incomplete': 1, 'warned': 2, 'manual': 3, 'passed': 4, 'skipped': 5}
    res = sorted(rep['resources'], key=lambda x: (order[x['status']], x['name'].lower()))
    print(f"素材上服检查：{rep['summary']['total']} 个资源\n")
    for r in res:
        types = '/'.join(TYPE_LABEL.get(t, t) for t in r['types'])
        if listing:
            print(f"  {r['name']}  [{types}]")
            continue
        if r['status'] == 'skipped' and not verbose:
            continue
        c = {lv: sum(1 for f in r['findings'] if f['level'] == lv) for lv in ('error', 'warn', 'info')}
        chk = ', '.join(f"{x['name']}" for x in r['checkers']) or '无检查器'
        print(f"{ICON[r['status']]}  {r['name']}  [{types}]  错误 {c['error']} / 警告 {c['warn']} / 提示 {c['info']}  （{chk}）")
        shown = 0
        for lv, cap in (('error', 8), ('warn', 5), ('info', 0)):
            items = [f for f in r['findings'] if f['level'] == lv]
            limit = len(items) if verbose else cap
            for f in items[:limit]:
                print(f"    {LEVEL[lv]} {f['code']}: [{f['file']}] {f['message'][:220]}")
                shown += 1
        hidden = len(r['findings']) - shown
        if hidden > 0 and not verbose:
            print(f'    …另有 {hidden} 条（--verbose 或 --json 看全部，也可以单独跑那个检查器）')
    if listing:
        return
    if rep['cross']:
        print('\n跨资源问题：')
        for f in rep['cross'][: None if verbose else 15]:
            print(f"  {LEVEL[f['level']]} {f['code']}: [{f['file']}] {f['message'][:240]}")
        if not verbose and len(rep['cross']) > 15:
            print(f"  …另有 {len(rep['cross']) - 15} 条")
    s = rep['summary']
    print(f"\n汇总：✓ 通过 {s['passed']}  ⚠ 警告 {s['warned']}  ✘ 失败 {s['failed']}  ⧗ 需人工 {s['manual']}"
          f"  ⧗ 未完成 {s['incomplete']}  · 跳过（纯脚本）{s['skipped']}")
    if s['crashed']:
        print(f"注意：{s['crashed']} 次检查器出错/超时，结果不完整")
    print('\n静态检查通过 ≠ 游戏里能用。上服前在本机测试服照下面做：')
    for t, items in rep['checklist'].items():
        print(f"  【{'通用' if t == 'common' else TYPE_LABEL.get(t, t)}】")
        for it in items:
            print(f'    □ {it}')


if __name__ == '__main__':
    main()
