#!/usr/bin/env python3
"""Check a FiveM menu / NUI resource for focus bugs, stalled callbacks, performance traps and design issues.

Usage:
    python check_nui_menu.py <resource> [more resources] [--json]

Reads fxmanifest.lua, client Lua, and the UI source (html/css/js/ts/tsx/jsx/vue/svelte, including
Tailwind classes). Skips node_modules and .git. Standard library only, read-only.
Exit code 1 when errors are found.

Sources for the rules (see references/fivem-nui-rules.md):
- fivem-docs scripting-manual/nui-development (ui_page + files, cfx-nui protocol, focus stack,
  "you have to return the callback at all times")
- FiveM source nui-resources/ResourceUIScripting.cpp (focus is a per-resource vote: any resource that
  never calls SetNuiFocus(false, false) keeps the player's cursor/keyboard captured; KeepInput only
  applies to a resource that also holds focus) and nui-core/NUIWindow.cpp (windowless_frame_rate 240:
  anything animating keeps the UI repainting)
"""
import argparse
import json
import os
import re
import sys

UI_EXT = ('.html', '.htm', '.css', '.scss', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte')
ASSET_EXT = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.webm', '.ogg', '.mp3', '.wav', '.ttf', '.otf', '.woff', '.woff2', '.svg')
SKIP_DIRS = {'node_modules', '.git', '.vite', '.cache'}
MB = 1024 * 1024


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def find_resources(paths):
    out = []
    for p in paths:
        p = os.path.abspath(p)
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
            if 'fxmanifest.lua' in files or '__resource.lua' in files:
                out.append(root)
    return sorted(set(out))


def walk(res):
    for root, dirs, files in os.walk(res):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        for f in files:
            yield os.path.join(root, f)


def read(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            return fh.read()
    except OSError:
        return ''


def nui_callback_blocks(lua):
    """Yield (name, cb_param, body) for each RegisterNUICallback / RegisterNuiCallback."""
    pat = re.compile(r"RegisterN[Uu][Ii][Cc]allback\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*function\s*\(\s*([\w_]*)\s*,?\s*([\w_]*)\s*\)")
    matches = list(pat.finditer(lua))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(lua)
        yield m.group(1), (m.group(3) or 'cb'), m.group(2) or 'data', lua[m.end():end]


def check(paths):
    findings = []
    resources = find_resources(paths)

    for res in resources:
        name = os.path.basename(res)

        def add(level, code, msg):
            findings.append({'level': level, 'code': code, 'resource': name, 'message': msg})

        manifest_path = os.path.join(res, 'fxmanifest.lua')
        manifest = strip_lua_comments(read(manifest_path) or read(os.path.join(res, '__resource.lua')))
        ui_page = re.search(r"ui_page\s*\(?\s*['\"]([^'\"]+)['\"]", manifest)
        files_decl = ' '.join(re.findall(r'files\s*\{(.*?)\}', manifest, flags=re.S)) + ' ' + \
            ' '.join(re.findall(r"\bfile\s*['\"]([^'\"]+)['\"]", manifest))

        lua_files = [f for f in walk(res) if f.endswith('.lua') and os.path.basename(f) not in ('fxmanifest.lua', '__resource.lua')]
        lua = '\n'.join(strip_lua_comments(read(f)) for f in lua_files)
        ui_files = [f for f in walk(res) if f.lower().endswith(UI_EXT)]
        # built bundles are huge and minified; prefer source when both exist
        src_files = [f for f in ui_files if os.path.getsize(f) < 400 * 1024]
        ui_text = '\n'.join(read(f) for f in src_files)

        uses_focus = re.search(r'SetNuiFocus\s*\(\s*true|lib\.setNuiFocus\s*\(\s*true', lua)
        if not ui_page and not ui_files:
            continue  # not a NUI resource

        if ui_page:
            page = ui_page.group(1)
            if not page.startswith(('http://', 'https://')):
                if not os.path.exists(os.path.join(res, page)):
                    add('error', 'UI_PAGE_MISSING', f"ui_page '{page}' 不存在（React/Vite 项目要先 build，再指向 build 出来的 index.html）")
                base = page.split('/')[-1]
                if base not in files_decl and page not in files_decl and '*' not in files_decl:
                    add('error', 'UI_PAGE_NOT_IN_FILES', f"ui_page '{page}' 没写进 files {{}}，客户端下载不到")
            else:
                add('warn', 'UI_PAGE_REMOTE', f"ui_page 指向外部网址 {page}：玩家每次都要从那个网站加载，网站挂了菜单就打不开")
        elif ui_files:
            add('info', 'NO_UI_PAGE', '有网页文件但 fxmanifest 没有 ui_page（如果它只是被别的资源引用就没问题）')

        # focus
        if uses_focus and not re.search(r'SetNuiFocus\s*\(\s*false|lib\.setNuiFocus\s*\(\s*false|lib\.resetNuiFocus', lua):
            add('error', 'FOCUS_NO_RELEASE', '有 SetNuiFocus(true, …) 但找不到 SetNuiFocus(false, false)：关菜单后玩家的鼠标/键盘会一直被卡住（只要有一个资源没放开焦点就会卡）')
        if re.search(r'SetNuiFocusKeepInput\s*\(\s*true', lua) and not re.search(r'DisableControlAction|DisableAllControlActions', lua):
            add('warn', 'KEEP_INPUT_NO_DISABLE', 'SetNuiFocusKeepInput(true) 会让游戏继续收到按键，但没看到 DisableControlAction：玩家在菜单里打字或按方向键时，角色也会跟着动/开枪')
        if uses_focus and ui_files and not re.search(r"""['"]Escape['"]|['"]Esc['"]|keyCode\s*===?\s*27|which\s*===?\s*27|['"]Backspace['"]""", ui_text) \
                and not re.search(r'lib\.(registerMenu|showMenu|registerContext|showContext)', lua):
            add('warn', 'NO_ESCAPE_CLOSE', '界面里找不到 Escape/Backspace 的处理：玩家按 ESC 关不掉菜单（GTA 的暂停菜单还会被打开）')

        # callbacks
        for cb_name, cb_param, data_param, body in nui_callback_blocks(lua):
            if not re.search(r'\b' + re.escape(cb_param) + r'\s*\(', body):
                add('error', 'NUI_CB_NOT_CALLED', f"NUI 回调 '{cb_name}' 里没有调用 {cb_param}(…)：网页那边的 fetch 会一直卡住直到超时（FiveM 文档：一定要回 cb，空的 {{}} 也行）")
            if re.search(r'TriggerServerEvent|lib\.callback', body) and re.search(
                    re.escape(data_param) + r'\.(price|cost|money|amount|reward|payout|total|count)\b', body):
                add('warn', 'CLIENT_TRUSTED_VALUE', f"NUI 回调 '{cb_name}' 把网页传来的价格/数量（{data_param}.price 之类）直接送去伺服器：伺服器一定要自己查价格和数量，网页数据可以被玩家改")

        if re.search(r"fetch\(\s*[`'\"]https://(?!cfx-nui-)[a-z0-9_\-]+/", ui_text) and 'GetParentResourceName' not in ui_text:
            add('warn', 'HARDCODED_RESOURCE_NAME', "fetch 的网址把资源名写死了：资源改名后所有按钮都会失效，改用 `https://${GetParentResourceName()}/…`")

        # remote assets
        remote = sorted(set(re.findall(r"""(?:src|href|url\(|@import)\s*=?\s*['"(]?\s*(https?://(?!cfx-nui-|localhost|127\.0\.0\.1)[^'")\s]+)""", ui_text)))
        if remote:
            add('warn', 'REMOTE_ASSETS', f"从外部网站加载 {len(remote)} 个文件（例如 {remote[0][:80]}）：玩家每次开菜单都要联网下载，慢或被墙就缺字体/图标。把字体、图标打包进资源")

        # performance
        blurs = [int(x) for x in re.findall(r'backdrop-filter\s*:\s*[^;]*blur\(\s*(\d+)', ui_text)]
        tw_blur = re.findall(r'\bbackdrop-blur(?:-(sm|md|lg|xl|2xl|3xl))?\b', ui_text)
        if blurs or tw_blur:
            big = [b for b in blurs if b > 12] + [t for t in tw_blur if t in ('lg', 'xl', '2xl', '3xl')]
            level = 'warn' if big or (len(blurs) + len(tw_blur)) > 3 else 'info'
            add(level, 'BACKDROP_BLUR', f"用了 {len(blurs) + len(tw_blur)} 处毛玻璃（backdrop-filter / backdrop-blur），其中 {len(big)} 处模糊很大：游戏内浏览器每帧都要重新模糊后面的游戏画面，低配电脑会掉帧。最多一个面板、模糊 ≤ 8–12px，或改用半透明深色底")
        if re.search(r'transition\s*:\s*all\b|transition-property\s*:\s*all\b|\btransition-all\b', ui_text):
            add('warn', 'TRANSITION_ALL', '用了 transition: all（或 Tailwind transition-all）：任何属性一变都会触发动画和重绘，只给 transform / opacity / color 加过渡')
        if re.search(r'transition[^;{}]*\b(width|height|top|left|right|bottom|margin|padding)\b', ui_text):
            add('info', 'LAYOUT_ANIMATION', '有对 width/height/top/left/margin 做动画：会让浏览器重新排版，改用 transform（translate/scale）')
        infinite = len(re.findall(r'animation[^;{}]*\binfinite\b', ui_text)) + len(re.findall(r'\banimate-(spin|ping|pulse|bounce)\b', ui_text))
        if infinite:
            add('warn', 'INFINITE_ANIMATION', f"有 {infinite} 个无限循环动画：NUI 最高按 240 帧重绘，菜单关着时如果元素还在页面上（只是透明）也会一直吃显卡。关菜单时用 display:none / 卸载组件")
        if re.search(r'box-shadow\s*:[^;]*\b(\d{2,})px\s+(\d{2,})px', ui_text):
            add('info', 'BIG_SHADOW', '有很大的 box-shadow（模糊半径两位数）：大量元素用大阴影会拖慢重绘，菜单列表项尽量用边框或小阴影')
        px_fonts = len(re.findall(r'font-size\s*:\s*\d+px', ui_text))
        if px_fonts >= 5 and not re.search(r'\b\d+(\.\d+)?(vh|vw|vmin|rem)\b|clamp\(', ui_text):
            add('info', 'FIXED_PX_SIZES', f"字体大小全用 px（{px_fonts} 处），没有 rem/vh/clamp：NUI 画面就是游戏视窗大小，720p 会显得很大、1440p/4K 会很小。用 rem + 根字号随 vh 变化，或 clamp()")

        # assets
        for f in walk(res):
            if f.lower().endswith(ASSET_EXT) and os.path.getsize(f) > MB and 'stream' not in f.replace(res, '').split(os.sep):
                add('warn', 'BIG_UI_ASSET', f"{os.path.relpath(f, res)} 有 {os.path.getsize(f) / MB:.1f} MB：玩家进服都要下载，菜单打开也要解码。图片压成 WebP、控制在几百 KB")
    return findings, resources


def main():
    ap = argparse.ArgumentParser(description='Check a FiveM menu / NUI resource')
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
            for x in [f for f in findings if f['level'] == level]:
                print(f"{icons[level]} {x['code']}: [{x['resource']}] {x['message']}")
        if not findings:
            print('✓ 没发现问题')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
