# Restyling the stock menus

## ox_lib (communityox/ox_lib, LGPL-3.0)

### Quick: convars, no code
ox_lib's web UI reads its accent colour from client convars (`resource/client.lua` → `getConfig`):

```cfg
# server.cfg — setr replicates the value to clients
setr ox:primaryColor violet   # a Mantine colour name, default 'blue'
setr ox:primaryShade 7        # 0–9, default 8
```
Mantine colour names: `dark`, `gray`, `red`, `pink`, `grape`, `violet`, `indigo`, `blue`, `cyan`, `teal`, `green`, `lime`, `yellow`, `orange`. This changes the accent across menus, context menus, progress bars, skill checks and dialogs at once — the cheapest way to make ox_lib match the server's brand.

### Per menu (`lib.registerMenu`)
Fields from `resource/interface/client/menu.lua`:
- menu: `id`, `title`, `options`, `position` (`'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'`), `disableInput` (default true: page takes focus), `canClose` (false blocks ESC/Backspace), `onClose(keyPressed)` (`'Escape'` / `'Backspace'`), `onSelected`, `onSideScroll`, `onCheck`.
- option: `label`, `description`, `icon` (Font Awesome name or `{prefix, name}`), `iconColor`, `progress` + `colorScheme`, `values` (side-scroll list, items can be `{label, description}`), `defaultIndex`, `checked` (checkbox), `args`, `close`.

Design use: icons with a consistent style, short labels, the description line for detail, `progress` for stats, `values` instead of nested submenus for small choices, `checked` for toggles.

Context menus (`lib.registerContext`) are better for mouse-driven option lists with metadata; list menus (`registerMenu`) for keyboard navigation while moving.

### Deep re-theme (fork)
The web UI is React + Mantine (v5 at the time of writing); the base theme is `web/src/theme/index.ts` (`colorScheme: 'dark'`, `fontFamily: 'Roboto'`, component overrides). Changing fonts, radii, panel colours or layouts means editing the web source and rebuilding (the repo uses bun: `bun install && bun run build` in `web/`; its build script is `tsc && vite build`), then shipping the built `web/build`. Costs: you maintain a fork and must merge upstream updates; ox_lib is **LGPL-3.0**, so a modified ox_lib you distribute (which includes sending it to players) must keep the licence and make your modified source available. Prefer convars + per-menu options unless the server needs a full rebrand.

## qb-menu (qbcore-framework/qb-menu, GPL-3.0)

Plain HTML/CSS/JS in `html/` (`index.html`, `script.js`, `style.css`), client in `client.lua`. Restyle by editing `html/style.css` (colours, radius, font, spacing) — no build step. Its stock page loads Font Awesome and fonts from CDNs; for reliability, download them into `html/` and reference them locally (add them to `files {}`). Keep your changes in a fork or a patch file so updates don't overwrite them; GPL-3.0 applies to distributed modifications.

## Third-party reskins

Many "ox_lib / qb UI packs" are paid; don't recommend them. Free reskins exist on the Cfx forum — check the licence and read the code (`fivem-security-audit`) before installing anything unknown.
