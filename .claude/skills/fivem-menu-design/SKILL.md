---
name: fivem-menu-design
description: Design, build and beautify FiveM menus and in-game UI — ox_lib menus and context menus, qb-menu, custom NUI shop/garage/job/boss menus, inventories, radial menus, pause menus, HUDs — so they look premium, read clearly over the game, navigate by keyboard, scale from 720p to 4K/ultrawide, close with ESC, release NUI focus, and don't cost FPS. Combines game-ui-ux, game-feel, ui-ux-pro-max, impeccable and taste-skill with FiveM's NUI rules (focus votes, KeepInput, NUI callbacks, CEF repaint cost, cfx-nui assets) and a checker script. Use whenever the user wants to make, restyle, redesign, polish or fix a FiveM menu or NUI — even if they only say "菜单", "美化菜单", "menu 好丑", "UI 设计", "商店界面", "ox_lib 换颜色", "玻璃风格", "菜单关不掉", "鼠标卡住".
---

# FiveM menu design

A good FiveM menu is three things at once: **pleasant to look at**, **fast to use with a keyboard in the middle of a fight**, and **cheap** — it runs in an embedded Chromium (CEF) drawn on top of the game, so every blur, shadow and animation competes with the game for frame time. Generic web design skills get the first right and often break the other two. This skill is the FiveM layer on top of them.

Read what you need:
- `references/fivem-nui-rules.md` — focus, input, callbacks, assets, scaling, performance, security: the hard rules, with sources.
- `references/ox-lib-and-qb-menu.md` — restyling the stock menus: ox_lib convars and options, deeper ox_lib re-theming, qb-menu, licences.
- `references/menu-patterns.md` — layouts for common menus (list, context, shop, garage, boss, inventory, radial, pause, HUD) and FiveM-safe style recipes.

Related skills (ask before using, per the project rules): `game-ui-ux` (screen stack, keyboard/gamepad focus, scaling), `game-feel` (feedback — use sparingly), `ui-ux-pro-max` (search styles, palettes, fonts locally), `impeccable` (`audit`, `critique`, `polish`, `animate`, `bolder`/`quieter`), `taste-skill:design-taste-frontend`, `frontend-design`, `fivem-react-nui` (React/Vite NUI structure), `oxlib`, `game-interface-feedback`, `fivem-security-audit` (server-side validation).

## Workflow

### 1. Decide what kind of menu
| Need | Use |
|---|---|
| quick list of actions, consistent with the rest of the server | ox_lib `lib.registerMenu` / `lib.registerContext` — restyle with convars, no web code |
| an existing QBCore server's menus | qb-menu (restyle its `html/style.css`) |
| a branded shop, garage, boss menu, phone-like app, inventory | custom NUI (React per `fivem-react-nui`, or plain HTML/CSS/JS for small menus) |

Prefer the stock menus when they're good enough: one consistent menu system across the server beats ten pretty but different ones.

### 2. Design the flow before the look
Use `game-ui-ux` thinking: what the player is trying to do, the screen stack (list → detail → confirm), and **full keyboard control** — arrow keys/W-S move, Enter selects, Backspace goes back one level, ESC closes everything. Keep the most common action first and the dangerous one last with a confirm step. Server-side state (prices, stock, money) is fetched from the server, never invented in the UI.

### 3. Choose a style that survives the game
Pick a direction with `ui-ux-pro-max` (search styles/palettes/fonts locally) or `impeccable`/`taste-skill`, then apply the FiveM constraints in `references/menu-patterns.md`: solid or near-solid dark panels over a busy game scene, contrast ≥ 4.5:1, one accent colour, readable at 720p and 4K, at most one small blurred panel. Match the server's existing menus (ox_lib colour, fonts) unless the user wants a redesign.

### 4. Build
Custom NUI: `fivem-react-nui` for structure. Follow `references/fivem-nui-rules.md` for focus, callbacks, ESC, scaling and assets. Animate only `transform` and `opacity`, 120–200 ms, and remove the menu from the page when closed.

### 5. Polish
`impeccable audit` / `critique` on the built UI, then `polish`; `animate` and `game-feel` only for meaningful feedback (selection, purchase confirmed, error) — never idle loops. Add front-end sounds for move/select/back if the server uses them (`PlaySoundFrontend`).

### 6. Check and test
Run `python .claude/skills/fivem-menu-design/scripts/check_nui_menu.py <resource>` (local, read-only, Python only). It catches: `ui_page` missing or not in `files{}`, remote `ui_page`, `SetNuiFocus(true)` without a matching release, `SetNuiFocusKeepInput` without `DisableControlAction`, no ESC/Backspace handling, NUI callbacks that never call `cb`, prices/amounts from the UI sent straight to the server, hard-coded resource names in `fetch`, fonts/icons loaded from CDNs, heavy or many backdrop blurs, `transition: all`, layout-property animations, infinite animations, huge shadows, px-only font sizes, and UI images over 1 MB.

Then test in game: 1280×720, 1920×1080, 2560×1440 and an ultrawide if possible; keyboard only; ESC and Backspace at every level; open the menu twice quickly; restart the resource while it's open (focus must come back); watch FPS with the menu open vs closed; open it on a low-end PC if the server has many such players.

## Ground rules
- The server decides prices, stock, money and permissions; the menu only displays and requests. Flag any callback that trusts UI values.
- Free assets only, bundled in the resource (fonts with an open licence, Font Awesome Free, Phosphor, Lucide). No paid UI packs; don't copy paid or leaked menus.
- Ask before using the related skills, per CLAUDE.md. The checker script may run once this skill is approved.
