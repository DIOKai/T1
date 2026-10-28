#!/usr/bin/env python3
"""Check an interactive 3D textbook lesson (three.js + pmndrs postprocessing) for
the mistakes that unguided builds of this kind of page keep making.

Usage:
    python check_lesson.py <lesson-folder-or-file> [more paths] [--json]

Reads .html / .js / .mjs / .css files (skips node_modules, vendor, dist, build and
*.min.js). Standard library only, read-only. Exit code 1 when errors are found.

These are static heuristics: a hit means "go and look", not proof. Each finding
names the file and line so you can confirm it in the code and in the browser.

Checks
- Rendering: bloom without a HalfFloat composer (nothing can exceed 1.0), bloom
  threshold below 1.0 (white paper blooms), uncapped devicePixelRatio, the
  normal-buffer clear colour written as hex, WebGPU/TSL imports mixed into a
  WebGLRenderer page.
- Idle cost: an animation loop with no render-on-demand flag, no pause on
  visibilitychange, shadow maps re-rendered every frame.
- Lesson loop: a stamp awarded only inside a "prediction was correct" branch,
  no reduced-motion handling, no aria-live status region, range sliders without
  aria-valuetext, a canvas without a text alternative, no note of what the
  model ignores.
- Delivery: debug globals (window.__x) left in the page.
"""
import argparse
import json
import os
import re
import sys

EXTS = ('.html', '.htm', '.js', '.mjs', '.css')
SKIP_DIRS = {'node_modules', 'dist', 'build', '.git', '.vite', 'vendor'}   # vendor/: third-party builds, not lesson code


def walk(paths):
    files = []
    for p in paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            files.append(p)
            continue
        for root, dirs, fs in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
            for f in fs:
                if f.lower().endswith(EXTS) and not f.lower().endswith('.min.js'):
                    files.append(os.path.join(root, f))
    return files


def rel(path, bases):
    for b in bases:
        b = os.path.abspath(b)
        if os.path.isdir(b) and path.startswith(b + os.sep):
            return os.path.relpath(path, b).replace(os.sep, '/')
    return os.path.basename(path)


def line_of(text, idx):
    return text.count('\n', 0, idx) + 1


def strip_js_comments(text):
    # keep line numbers stable: replace comment bodies with spaces/newlines
    def blank(m):
        return re.sub(r'[^\n]', ' ', m.group(0))
    text = re.sub(r'/\*.*?\*/', blank, text, flags=re.S)
    text = re.sub(r'(?<![:\'"\\])//[^\n]*', blank, text)
    return text


def check(paths):
    findings = []

    def add(level, code, where, msg):
        findings.append({'level': level, 'code': code, 'file': where, 'message': msg})

    files = walk(paths)
    if not files:
        add('error', 'NO_FILES', '', '找不到 .html / .js 文件，路径要指向课程文件夹或文件')
        return findings

    srcs = {}
    for f in files:
        try:
            raw = open(f, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        srcs[f] = strip_js_comments(raw) if not f.lower().endswith('.css') else raw
    allcode = '\n'.join(srcs.values())

    def first(pattern, flags=0):
        for f, t in srcs.items():
            m = re.search(pattern, t, flags)
            if m:
                return f, t, m
        return None

    def where(hit):
        f, t, m = hit
        return f'{rel(f, paths)}:{line_of(t, m.start())}'

    uses_three = re.search(r"from\s+['\"]three['\"]|three@|three\.module\.js|THREE\.", allcode)
    if not uses_three:
        add('info', 'NO_THREE', '', '没看到 three.js，这个检查是给 three.js 课程页用的，结果可能不准')

    # ---------- rendering ----------
    bloom = first(r'\bnew\s+(Selective)?BloomEffect\s*\(')
    if bloom:
        if not re.search(r'frameBufferType\s*:\s*(THREE\.)?HalfFloatType|frameBufferType\s*:\s*(THREE\.)?FloatType', allcode):
            add('error', 'BLOOM_8BIT', where(bloom),
                '用了 BloomEffect，但 EffectComposer 没设 frameBufferType: HalfFloatType。8 位缓冲把颜色截到 0–1，自发光超不过 1.0，阈值发光会失效（要么全不亮，要么只能把阈值调低，让白纸也发光）')
        for f, t in srcs.items():
            for m in re.finditer(r'luminanceThreshold\s*[:=]\s*([0-9.]+)', t):
                try:
                    v = float(m.group(1))
                except ValueError:
                    continue
                if v < 1.0:
                    add('warn', 'BLOOM_THRESHOLD_LOW', f'{rel(f, paths)}:{line_of(t, m.start())}',
                        f'bloom 阈值 {v} 低于 1.0：白纸（接近 1.0）也可能发光。阈值设 1.0，让能量物体的自发光 > 1（并随能量大小变化）')

    tone = first(r'\bnew\s+ToneMappingEffect\s*\(|toneMapping\s*=\s*THREE\.(ACESFilmic|AgX|Neutral|Reinhard|Cineon)ToneMapping')
    if tone:
        add('info', 'TONE_MAPPING', where(tone),
            '有色调映射：截图量一下空白纸面的像素，要在你选的纸色 ±3% 以内。ACES 会把 1.0 压成 #E2E2E2，Neutral 压成 #F0F0F0；变灰就提高页面光照或曝光、或在合成纸面之前做色调映射')

    for f, t in srcs.items():
        for m in re.finditer(r'setPixelRatio\s*\(([^)]*)\)', t):
            arg = m.group(1)
            if 'devicePixelRatio' in arg and 'Math.min' not in arg and 'min(' not in arg:
                add('warn', 'DPR_UNCAPPED', f'{rel(f, paths)}:{line_of(t, m.start())}',
                    'setPixelRatio(devicePixelRatio) 没有上限：3 倍屏手机要画 9 倍像素，后处理会很慢。用 Math.min(devicePixelRatio, 2)，触控设备再降低')

    hexclear = first(r'setClearColor\s*\(\s*(new\s+THREE\.Color\s*\(\s*)?0x8080ff', re.I)
    if hexclear:
        add('warn', 'NORMAL_CLEAR_HEX', where(hexclear),
            '法线缓冲用 0x8080ff 清屏：hex 是 sRGB，会转成线性约 0.216 而不是 0.5。改用 new THREE.Color().setRGB(0.5, 0.5, 1)')

    webgpu = first(r"from\s+['\"]three/(webgpu|tsl)['\"]|WebGPURenderer")
    webgl = first(r'\bnew\s+(THREE\.)?WebGLRenderer\s*\(')
    if webgpu and webgl:
        add('warn', 'WEBGPU_MIXED', where(webgpu),
            '同一页面同时有 WebGLRenderer 和 WebGPU/TSL：TSL 节点材质不能在 WebGLRenderer 上用，pmndrs postprocessing 也只支持 WebGL。选一种')

    # ---------- idle cost ----------
    loop = first(r'setAnimationLoop\s*\(|requestAnimationFrame\s*\(')
    if loop:
        if not re.search(r'\b(dirty|needsRender|needsRedraw|invalidate|renderRequested|frameloop\s*=\s*[\'"]demand)\b', allcode):
            add('warn', 'NO_RENDER_ON_DEMAND', where(loop),
                '动画循环每一帧都在画，没有「需要时才画」的标记（dirty / invalidate）。画面不动时手机也一直跑 bloom 和后处理，会发热耗电。见 SKILL.md「Phone budget」')
        if not re.search(r'visibilitychange|document\.hidden|visibilityState', allcode):
            add('warn', 'NO_VISIBILITY_PAUSE', where(loop),
                '没有处理 visibilitychange：切到别的分页时停下动画循环（setAnimationLoop(null)），回来再重画一次')
    if re.search(r'shadowMap\.enabled\s*=\s*true', allcode) and not re.search(r'shadowMap\.autoUpdate\s*=\s*false', allcode):
        sm = first(r'shadowMap\.enabled\s*=\s*true')
        add('info', 'SHADOWS_EVERY_FRAME', where(sm),
            '阴影贴图每帧都重画。书不会动：设 shadowMap.autoUpdate = false，只在有东西移动的帧设 needsUpdate = true')

    # ---------- lesson loop ----------
    stamp_gate = None
    for f, t in srcs.items():
        if f.lower().endswith('.css'):
            continue
        for m in re.finditer(r'if\s*\(\s*!?\s*(ok|correct|isCorrect|wasCorrect|right|isRight|gotIt|success)\b[^)]*\)\s*\{?([^\n]{0,200})', t):
            body = m.group(2)
            nxt = t[m.end():m.end() + 300]
            if m.group(0).lstrip().startswith('if') and '!' not in m.group(0)[:6] and re.search(r'stamp', body + nxt[:160], re.I):
                stamp_gate = (f, t, m)
                break
        if not stamp_gate:
            m = re.search(r'\b(ok|correct|isCorrect|right)\s*\?\s*[^:;\n]{0,80}[Ss]tamp[^:;\n]{0,80}:\s*[^;\n]{0,80}(no stamp|not quite|No stamp)', t)
            if m:
                stamp_gate = (f, t, m)
        if stamp_gate:
            break
    if stamp_gate:
        add('error', 'STAMP_ONLY_IF_CORRECT', where(stamp_gate),
            '印章看起来只在「预测正确」的分支里发。印章要奖励「做完整个流程」（预测 + 测试 + 掀开解释），猜错也要给；答对可以再加一个小记号。只奖励答对，学生会不敢猜或去猜答案，预测就失去作用')
    elif re.search(r'stamp', allcode, re.I) and re.search(r'no stamp|not quite', allcode, re.I):
        hit = first(r'(?i)no stamp')
        if hit:
            add('warn', 'STAMP_MAYBE_GATED', where(hit),
                '有「No stamp」之类的文字：确认答错时也会盖章（奖励完成流程，不是奖励答对）')

    if not re.search(r'prefers-reduced-motion', allcode):
        add('error', 'NO_REDUCED_MOTION', '',
            '没有处理 prefers-reduced-motion：开了「减少动态效果」时，要去掉镜头飞入、印章弹跳，立体图直接出现')
    if not re.search(r'aria-live', allcode):
        add('warn', 'NO_LIVE_REGION', '',
            '没有 aria-live 区域：实验结果、印章、判定要用 polite 的朗读区宣布，不要移动焦点')
    for f, t in srcs.items():
        for m in re.finditer(r'<input\b[^>]*type\s*=\s*["\']range["\'][^>]*>', t, re.I):
            tag = m.group(0)
            ident = re.search(r'id\s*=\s*["\']([^"\']+)', tag)
            ok = 'aria-valuetext' in tag
            if not ok and ident:
                ok = re.search(r'aria-valuetext', allcode) is not None and ident.group(1) in allcode
            if not ok:
                add('warn', 'SLIDER_NO_VALUETEXT', f'{rel(f, paths)}:{line_of(t, m.start())}',
                    '滑杆没有 aria-valuetext：读屏只会念数字。实时设成带单位的文字，例如 "2.0 metres"')
        for m in re.finditer(r'<canvas\b[^>]*>', t, re.I):
            tag = m.group(0)
            if not re.search(r'aria-label|aria-labelledby|aria-describedby|role\s*=\s*["\']img', tag):
                cid = re.search(r'id\s*=\s*["\']([^"\']+)', tag)
                if not (cid and re.search(r"setAttribute\(\s*['\"]aria-(label|describedby)", allcode)):
                    add('warn', 'CANVAS_NO_TEXT_ALT', f'{rel(f, paths)}:{line_of(t, m.start())}',
                        '3D canvas 没有文字说明：加 aria-label（或 role="img" + aria-describedby），并随实验状态更新')
    if not re.search(r'(?i)ignor|simplif|assum|approximat|idealis|idealiz|neglect|model leaves|not modell?ed|not covered'
                     r'|\bmodel\s*:|what (this|the) model|isotropic|homogeneous|frictionless|reads [^.<]{0,20}(low|high)'
                     r'|per ?cent (low|high)|忽略|简化|假设|近似|理想化', allcode):
        add('warn', 'NO_MODEL_NOTE', '',
            '页面上没写模型忽略了什么（例如不算滚动动能、慢动作 0.5×、网格解偏低几 %）。写在翻页解释或教师说明里，慢动作要在画面上标出')

    # ---------- delivery ----------
    for f, t in srcs.items():
        for m in re.finditer(r'\bwindow\.__\w+\s*=', t):
            if re.search(r'debug', t[max(0, m.start() - 160):m.start()], re.I):
                continue
            add('warn', 'DEBUG_GLOBAL', f'{rel(f, paths)}:{line_of(t, m.start())}',
                f'留下了测试用的全局变量 {m.group(0).rstrip("= ").strip()}：交付前删掉，或放在 ?debug 参数后面')

    return findings


def main():
    ap = argparse.ArgumentParser(description='Check an interactive 3D textbook lesson page')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    try:  # Windows consoles default to a legacy code page that can't print Chinese or ✘ ⚠
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass
    findings = check(args.paths)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                loc = f"[{x['file']}] " if x['file'] else ''
                print(f"{icons[level]} {x['code']}: {loc}{x['message']}")
        if not findings:
            print('✓ 没发现问题')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
