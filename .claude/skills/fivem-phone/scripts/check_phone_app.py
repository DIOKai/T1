#!/usr/bin/env python3
"""Check a FiveM phone app or phone resource (npwd, lb-phone, qb-phone/z-phone, custom phones).

Usage:
    python check_phone_app.py <resource or folder> [more] [--json]

Detects what each resource is (lb-phone app, npwd v4 app, npwd 3.x federation app, qb-phone or a fork,
custom phone frame) and runs phone-specific checks, plus the NUI checks from
fivem-menu-design/scripts/check_nui_menu.py when that skill is installed next to this one. Apps that
live inside a host phone are not blamed for things the host does (ESC, focus).

Standard library only, read-only. Exit code 1 when errors are found.

Sources (see ../references):
- lb-phone-app-template (MIT): AddCustomApp / SendCustomAppMessage, onResourceStart re-add,
  GetResourceState wait, componentsLoaded, ui/icon paths
- npwd-app-template (v4): RegisterExternalApp id == vite IIFE name __npwd_ext_<id>, dist/web/app.js,
  runtime-provided externals
- npwd master 3.16: useExternalApps.tsx loads https://cfx-nui-<res>/web/dist/remoteEntry.js and the
  federated './config'; cl_exports.ts sendNPWDMessage
- qb-phone: Config.PhoneApplications, `<app>-app` container required by the click handler, data-appslot divs
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MENU_CHECKER = os.path.normpath(os.path.join(HERE, '..', '..', 'fivem-menu-design', 'scripts'))

SKIP_DIRS = {'node_modules', '.git', '.vite', '.cache'}
UI_EXT = ('.html', '.htm', '.css', '.scss', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte')
CODE_EXT = ('.lua', '.js', '.ts', '.mjs', '.cjs', '.tsx', '.jsx')

# NUI findings that are the host phone's job when the resource is an app inside npwd / lb-phone
HOST_HANDLES = {'NO_ESCAPE_CLOSE', 'NO_UI_PAGE', 'FOCUS_NO_RELEASE', 'KEEP_INPUT_NO_DISABLE'}

try:
    sys.path.insert(0, MENU_CHECKER)
    import check_nui_menu as menu  # noqa: E402
except ImportError:  # fivem-menu-design not installed: phone checks only
    menu = None
finally:
    if sys.path and sys.path[0] == MENU_CHECKER:
        sys.path.pop(0)


def strip_lua_comments(text):
    text = re.sub(r'--\[(=*)\[.*?\]\1\]', '', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def strip_js_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'(?<![:\'"\w])//[^\n]*', '', text)


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


def glob_to_re(pattern):
    """fxmanifest file glob → regex over resource-relative paths ('**' any depth, '*' one segment)."""
    out, i = '', 0
    while i < len(pattern):
        if pattern.startswith('**/', i):
            out += '(?:.*/)?'
            i += 3
        elif pattern.startswith('**', i):
            out += '.*'
            i += 2
        elif pattern[i] == '*':
            out += '[^/]*'
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(out + '$')


def manifest_files(manifest):
    blocks = re.findall(r'\bfiles\s*\(?\s*\{(.*?)\}', manifest, flags=re.S)
    pats = re.findall(r"['\"]([^'\"]+)['\"]", ' '.join(blocks))
    pats += re.findall(r"\bfile\s*\(?\s*['\"]([^'\"]+)['\"]", manifest)
    return pats


def shipped(rel, pats):
    rel = rel.replace('\\', '/').lstrip('./')
    return any(glob_to_re(p.replace('\\', '/').lstrip('./')).match(rel) for p in pats)


def lua_blocks(lua, start_pat):
    """Text from each match of start_pat to the next 'end)' at line start or 1500 chars, whichever first."""
    for m in re.finditer(start_pat, lua):
        yield lua[m.end():m.end() + 1500]


def check_phone(res):
    findings = []
    name = os.path.basename(res)

    def add(level, code, msg):
        findings.append({'level': level, 'code': code, 'resource': name, 'message': msg})

    manifest = strip_lua_comments(read(os.path.join(res, 'fxmanifest.lua')) or read(os.path.join(res, '__resource.lua')))
    pats = manifest_files(manifest)
    ui_page_m = re.search(r"ui_page\s*\(?\s*['\"]([^'\"]+)['\"]", manifest)
    ui_page = ui_page_m.group(1) if ui_page_m else None

    files = [f for f in walk(res)]
    rel = {f: os.path.relpath(f, res).replace(os.sep, '/') for f in files}
    lua = '\n'.join(strip_lua_comments(read(f)) for f in files
                    if f.endswith('.lua') and os.path.basename(f) not in ('fxmanifest.lua', '__resource.lua'))
    # game scripts in JS/TS (npwd apps) — exclude the web UI folder and built output
    game_js = '\n'.join(strip_js_comments(read(f)) for f in files
                        if f.endswith(('.ts', '.js', '.mjs')) and not re.search(r'(^|/)(web|ui|html|dist|build|public)/', rel[f])
                        and os.path.getsize(f) < 400 * 1024)
    code = lua + '\n' + game_js
    ui_files = [f for f in files if f.lower().endswith(UI_EXT) and re.search(r'(^|/)(web|ui|html|nui|src|public)/', rel[f])
                and os.path.getsize(f) < 400 * 1024]
    ui = '\n'.join(read(f) for f in ui_files)
    css = '\n'.join(read(f) for f in ui_files if f.lower().endswith(('.css', '.scss')))
    vite_cfg = '\n'.join(read(f) for f in files if re.search(r'vite\.config\.(t|j|mj)s$', f))

    kinds = []

    # ---------- lb-phone app ----------
    if re.search(r'exports\s*\[\s*["\']lb-phone["\']\s*\]\s*:\s*AddCustomApp|exports\.?\[?["\']?lb-phone', code) and 'AddCustomApp' in code:
        kinds.append('lb-phone app')
        if not re.search(r'onResourceStart[\s\S]{0,300}["\']lb-phone["\']', code):
            add('warn', 'LB_NO_READD', '没有在 onResourceStart 里对 "lb-phone" 重新 AddCustomApp：lb-phone 一重启，你的 app 就从手机上消失，直到你的资源也重启（官方模板有这段）')
        if not re.search(r'GetResourceState\s*\(\s*["\']lb-phone["\']\s*\)', code):
            add('warn', 'LB_NO_WAIT', '没有等 GetResourceState("lb-phone") == "started" 就调用 AddCustomApp：资源比 lb-phone 先启动时会报 No such export')
        ids = set(re.findall(r'identifier\s*=\s*["\']([^"\']+)["\']', code))
        sent = set(re.findall(r'SendCustomAppMessage\s*\(\s*["\']([^"\']+)["\']', code))
        for s in sorted(sent - ids):
            if ids:
                add('warn', 'LB_IDENTIFIER_MISMATCH', f"SendCustomAppMessage 用的 identifier '{s}' 和 AddCustomApp 的 {sorted(ids)} 不一样：消息送不到你的 app")
        for m in re.finditer(r'\bui\s*=\s*([^\n,]+)', code):
            expr = m.group(1)
            if re.search(r'localhost|127\.0\.0\.1', expr) and not re.search(r'url\s*:\s*find|:find\(', expr):
                add('error', 'LB_UI_DEV_SERVER', f'AddCustomApp 的 ui 指向本机开发服务器（{expr.strip()[:80]}）：只有开发者自己的电脑打得开，上线前改回 GetCurrentResourceName() .. "/ui/…"')
            path_m = re.search(r'\.\.\s*["\']/([^"\']+)["\']', expr)
            if path_m:
                target = path_m.group(1)
                if not os.path.exists(os.path.join(res, target)):
                    add('error', 'LB_UI_MISSING', f"AddCustomApp 的 ui 指向 '{target}'，但资源里没有这个文件（React/Vue 要先 build）：app 打开会是空白")
                elif pats and not shipped(target, pats):
                    add('error', 'LB_UI_NOT_SHIPPED', f"'{target}' 没写进 fxmanifest 的 file/files：玩家下载不到，app 打开空白")
            elif re.search(r'^["\'][\w-]+/', expr.strip()):
                add('warn', 'LB_UI_HARDCODED', f'ui 把资源名写死了（{expr.strip()[:60]}）：资源改名就打不开，用 GetCurrentResourceName() .. "/…"')
        for m in re.finditer(r'cfx-nui-["\']\s*\.\.\s*GetCurrentResourceName\(\)\s*\.\.\s*["\']/([^"\']+)["\']', code):
            target = m.group(1)
            if not os.path.exists(os.path.join(res, target)):
                hint = '（在 dist/build 里：先 build 再检查）' if re.search(r'(^|/)(dist|build)/', target) else ''
                add('warn', 'LB_ASSET_MISSING', f"icon/images 指向 '{target}'，但资源里没有这个文件{hint}：手机里会显示破图")
        if re.search(r'\b(setPopUp|setContextMenu|sendNotification|selectGallery|selectGIF|selectEmoji|colorPicker|useCamera)\s*\(', ui) and 'componentsLoaded' not in ui:
            add('warn', 'LB_NO_COMPONENTS_LOADED', '界面用了 lb-phone 注入的函数（setPopUp 等），但没等 componentsLoaded 消息：页面比手机组件先加载时会报 undefined（官方模板等到 componentsLoaded 才加载脚本/渲染）')
        if ui_page and re.search(r'localhost|127\.0\.0\.1', ui_page):
            add('error', 'PHONE_DEV_UI_PAGE', f"ui_page 还是开发服务器 {ui_page}（React 模板默认这样）：上线前改成 build 出来的 ui/dist/index.html")

    # ---------- npwd v4 app ----------
    if 'RegisterExternalApp' in code:
        kinds.append('npwd v4 app')
        ids = re.findall(r'RegisterExternalApp\s*\(\s*\{[\s\S]{0,400}?\bid\s*:\s*["\']([^"\']+)["\']', code)
        iife = re.findall(r'__npwd_ext_([\w-]+)', vite_cfg)
        if ids and iife and ids[0] not in iife:
            add('error', 'NPWD4_ID_MISMATCH', f"RegisterExternalApp 的 id '{ids[0]}' 和 vite.config 的 name '__npwd_ext_{iife[0]}' 不一样：npwd 找不到你的 app 代码（模板要求两边一致）")
        if ids and not iife and vite_cfg:
            add('warn', 'NPWD4_NO_IIFE_NAME', "vite.config 里没有 name: '__npwd_ext_<id>' 的 IIFE 设定：npwd v4 靠这个名字加载 app")
        out = re.search(r"outDir\s*:\s*['\"]([^'\"]+)['\"]", vite_cfg)
        bundle = 'dist/web/app.js'
        if out:
            out_rel = os.path.normpath(os.path.join('web', out.group(1))).replace(os.sep, '/')
            bundle = out_rel.rstrip('/') + '/app.js'
        if not shipped(bundle, pats):
            add('error', 'NPWD4_BUNDLE_NOT_SHIPPED', f"fxmanifest 的 files 没有 {bundle}：玩家下载不到 app 的网页代码")
        if vite_cfg and not re.search(r"external\s*:\s*\[[^\]]*['\"]react['\"]", vite_cfg):
            add('warn', 'NPWD4_BUNDLES_REACT', 'vite.config 没把 react 设为 external：会打包第二份 React，npwd 里会出现 Invalid hook call，体积也变大（模板把 react、react-dom、lucide-react、@npwd/sdk、@npwd/keyos、motion/react 都设为 external）')
        if not re.search(r"dependenc(y|ies)\s*\(?\s*\{?[^\n]*['\"]npwd['\"]", manifest):
            add('info', 'NPWD4_NO_DEPENDENCY', "fxmanifest 没写 dependency 'npwd'：npwd 没开时你的资源也会启动然后报错")

    # ---------- npwd 3.x federation app ----------
    exposes_config = re.search(r"exposes\s*:\s*\{[^}]*['\"]\./config['\"]", vite_cfg)
    if re.search(r'vite-plugin-federation', vite_cfg) and re.search(r'\bremotes\s*:', vite_cfg) and not exposes_config:
        kinds.append('npwd (phone itself)')  # the host loads remotes; it is not an app
    elif re.search(r'vite-plugin-federation', vite_cfg) and 'RegisterExternalApp' not in code:
        kinds.append('npwd 3.x app')
        if not exposes_config:
            add('error', 'NPWD3_NO_CONFIG_EXPOSE', "federation 没有 exposes './config'：npwd 3.x 会去拿 remote 的 './config'，拿不到 app 就不显示")
        if not shipped('web/dist/remoteEntry.js', pats):
            add('error', 'NPWD3_REMOTE_NOT_SHIPPED', 'fxmanifest 的 files 没包含 web/dist/remoteEntry.js：npwd 会从 https://cfx-nui-<资源名>/web/dist/remoteEntry.js 加载，build 输出也要在 web/dist')
        if not re.search(r"shared\s*:\s*\[[^\]]*['\"]react['\"]", vite_cfg):
            add('warn', 'NPWD3_REACT_NOT_SHARED', "federation 的 shared 没有 react：app 会带自己的 React，npwd 里 hooks 会坏（npwd 自己 shared 的是 react、react-dom、@emotion/react、react-router-dom、fivem-nui-react-lib）")
        add('info', 'NPWD3_APPS_CONFIG', f"记得把 '{name}' 加进 npwd 的 config.json → \"apps\"，并在 server.cfg 里先 ensure {name} 再 ensure npwd（资源名要和 apps 里写的一样）")

    is_npwd_app = any(k.startswith('npwd') for k in kinds)
    if is_npwd_app and re.search(r'\bSendNUIMessage\s*\(', lua) and not ui_page:
        add('warn', 'NPWD_SENDNUIMESSAGE', "app 的 Lua 用了 SendNUIMessage：你的页面是在 npwd 的 NUI 里面，自己资源的 SendNUIMessage 送不到。改用 exports.npwd:sendNPWDMessage(app, method, data)")

    # ---------- qb-phone or fork ----------
    if 'Config.PhoneApplications' in code and re.search(r'class=["\'][^"\']*phone-application', ui):
        kinds.append('qb-phone (or fork)')
        cfg = '\n'.join(strip_lua_comments(read(f)) for f in files if f.endswith('.lua'))
        block_m = re.search(r'Config\.PhoneApplications\s*=\s*\{', cfg)
        apps, slots = [], {}
        if block_m:
            depth, i = 1, block_m.end()
            while i < len(cfg) and depth:
                depth += {'{': 1, '}': -1}.get(cfg[i], 0)
                i += 1
            body = cfg[block_m.end():i]
            for am in re.finditer(r"\[\s*['\"]([\w-]+)['\"]\s*\]\s*=\s*\{([^{}]*)\}", body):
                key, inner = am.group(1), am.group(2)
                app_m = re.search(r"\bapp\s*=\s*['\"]([\w-]+)['\"]", inner)
                slot_m = re.search(r'\bslot\s*=\s*(\d+)', inner)
                app = app_m.group(1) if app_m else key
                apps.append(app)
                if slot_m:
                    slots.setdefault(int(slot_m.group(1)), []).append(app)
        html = '\n'.join(read(f) for f in ui_files if f.lower().endswith(('.html', '.htm')))
        for app in apps:
            if not re.search(r'class=["\'][^"\']*\b' + re.escape(app) + r'-app\b', html):
                add('warn', 'QB_APP_NO_CONTAINER', f"Config.PhoneApplications 有 '{app}'，但 html 里没有 class=\"{app}-app\" 的画面：点图标没反应（app.js 找不到这个元素就不打开）")
        for slot, owners in sorted(slots.items()):
            if len(owners) > 1:
                add('warn', 'QB_SLOT_DUPLICATE', f"slot {slot} 被 {owners} 同时使用：后面的会盖掉前面的图标")
        divs = {int(s) for s in re.findall(r'data-appslot=["\'](\d+)["\']', html)}
        for slot, owners in sorted(slots.items()):
            if divs and slot not in divs:
                add('warn', 'QB_SLOT_NO_DIV', f"{owners} 用 slot {slot}，但 html 只有 data-appslot {min(divs)}–{max(divs)}：图标不会出现，要在 index.html 加对应的格子")

    # ---------- phone prop / animation (any phone frame) ----------
    phone_prop = re.search(r'CreateObject\s*\([^)]*(phone|prop)', lua, flags=re.I) or \
        re.search(r'CreateObject\s*\([^)]*phone', game_js, flags=re.I)
    phone_model = re.search(r'["\'`]prop_\w*phone\w*["\'`]|phoneModel|phoneProp', code)
    if phone_prop and phone_model:
        kinds.append('phone frame')
        if not re.search(r'\bDelete(Object|Entity)\s*\(', code):
            add('error', 'PROP_NO_DELETE', '有生成手机道具（CreateObject）但找不到 DeleteObject/DeleteEntity：关手机后道具留在手里/地上，联网道具会越积越多，所有人都看得到')
        if re.search(r'\bRequestModel\s*\(', code) and not re.search(r'SetModelAsNoLongerNeeded', code):
            add('info', 'MODEL_NOT_RELEASED', '生成道具后没有 SetModelAsNoLongerNeeded：模型一直占着内存（小问题，顺手加上）')
        if not re.search(r'onResourceStop', code):
            add('warn', 'NO_RESOURCE_STOP_CLEANUP', '没有 onResourceStop 清理：资源重启时手机道具留在玩家手上、动作停不下来（focus 会自动释放，但道具和动作不会）')
    if re.search(r'cellphone@', code):
        if not re.search(r'StopAnimTask|ClearPedTasks|ClearPedSecondaryTask', code):
            add('warn', 'ANIM_NO_STOP', '播放了 cellphone@ 动作但找不到 StopAnimTask/ClearPedTasks：关手机后角色还举着手')
    if 'phone frame' in kinds and re.search(r'SetNuiFocus\s*\(\s*true', code):
        if not re.search(r'IsPauseMenuActive', code):
            add('info', 'NO_PAUSE_CLOSE', '没检查 IsPauseMenuActive：手机开着时按暂停菜单，回来手机还在、鼠标可能卡住（npwd 每 500ms 检查一次并关掉手机）')
        if not re.search(r'isdead|inlaststand|IsEntityDead|IsPedDeadOrDying|onPlayerDeath|baseevents:onPlayerDied|hospital:client|ambulancejob', code, flags=re.I):
            add('info', 'NO_DEATH_CLOSE', '没看到死亡/倒地时关手机的处理：玩家倒地时手机还开着、还能操作（qb-phone 开手机前检查 isdead / inlaststand / ishandcuffed）')

    # ---------- frame CSS ----------
    if 'phone frame' in kinds or re.search(r'\.(phone|phone-frame|phone-container|device)\b[^{]*\{[^}]*\b(width|height)\s*:\s*\d{3,}px', css):
        if re.search(r'\.(phone|phone-frame|phone-container|device)\b[^{]*\{[^}]*\b(width|height)\s*:\s*\d{3,}px', css) and \
                not re.search(r'\d+(\.\d+)?vh|aspect-ratio|clamp\(|scale\(', css):
            add('info', 'PHONE_FIXED_PX', '手机外框用固定 px 宽高，也没有 vh/aspect-ratio/scale：720p 会太大、2K/4K 会很小。用 height: min(78vh, 52rem) + aspect-ratio，里面全用 rem')
    if re.search(r'rotate[YX]\s*\(', css) and re.search(r'fold|hinge|\.half\b', css + ui, flags=re.I) and 'perspective' not in css + ui:
        add('info', 'FOLD_NO_PERSPECTIVE', '折叠动画用了 rotateY/rotateX 但父元素没有 perspective：翻折看起来是扁的。父元素加 perspective: 1200–1600px，翻面元素加 backface-visibility: hidden')

    return kinds, findings


def check(paths):
    resources = find_resources(paths)
    findings, kinds_by_res = [], {}
    menu_findings = []
    if menu is not None:
        menu_findings, _ = menu.check(paths)
    for res in resources:
        kinds, f = check_phone(res)
        kinds_by_res[os.path.basename(res)] = kinds
        findings.extend(f)
    for f in menu_findings:
        kinds = kinds_by_res.get(f['resource'], [])
        inside_host = any(k.startswith(('npwd', 'lb-phone')) for k in kinds)
        if inside_host and f['code'] in HOST_HANDLES:
            continue
        if f['code'] == 'UI_PAGE_REMOTE' and any(x['code'] == 'PHONE_DEV_UI_PAGE' and x['resource'] == f['resource'] for x in findings):
            continue
        findings.append(f)
    return findings, resources, kinds_by_res


def main():
    ap = argparse.ArgumentParser(description='Check a FiveM phone app or phone resource')
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args()
    findings, resources, kinds = check(args.paths)
    if args.json:
        print(json.dumps({'resources': {os.path.basename(r): kinds.get(os.path.basename(r), []) for r in resources},
                          'findings': findings}, ensure_ascii=False, indent=2))
    else:
        print(f'扫描了 {len(resources)} 个资源')
        for r in resources:
            k = kinds.get(os.path.basename(r)) or ['普通 NUI / 不是手机相关']
            print(f'  · {os.path.basename(r)}: {", ".join(k)}')
        if menu is None:
            print('（没找到 fivem-menu-design 的 check_nui_menu.py，只做了手机专用检查）')
        icons = {'error': '✘ 错误', 'warn': '⚠ 警告', 'info': 'ℹ 提示'}
        for level in ('error', 'warn', 'info'):
            for x in [f for f in findings if f['level'] == level]:
                print(f"{icons[level]} {x['code']}: [{x['resource']}] {x['message']}")
        if not findings:
            print('✓ 没发现问题')
    sys.exit(1 if any(f['level'] == 'error' for f in findings) else 0)


if __name__ == '__main__':
    main()
