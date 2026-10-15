# Menu patterns and FiveM-safe style recipes

These are starting points to adapt, not rules from a source. Values are rules of thumb; check them in game.

## Layouts

| Menu | Layout | Keyboard | Notes |
|---|---|---|---|
| Action list (job actions, vehicle menu) | narrow column in a corner, title + 5–9 visible rows, scroll | ↑/↓, Enter, Backspace back, ESC close | ox_lib `registerMenu` fits; keep labels ≤ 30 chars |
| Context menu (third-eye result, player options) | small card near the target or centre-right | mouse, ESC | ox_lib `registerContext`; show metadata (price, time) on the row |
| Shop / store | left: categories; centre: grid of items with image, name, price; right or bottom: cart + total + buy | Tab between areas, arrows in grid, Enter add, Delete remove | price shown is the **server's**; confirm before buying; show money left |
| Garage / impound | list of vehicles with plate, fuel, engine/body health bars, state badge (out/in/impounded) | ↑/↓, Enter take out | badge colours with text, not colour alone |
| Boss / management | tabs: employees, finances, settings; tables with actions | Tab, arrows | confirm destructive actions (fire, withdraw); log server-side |
| Inventory | two grids (player / other), slot size from `vh`, weight bar, hover/selected detail panel | arrows to move selection, Enter use, Shift+drag split | virtualise large grids; images small WebP |
| Radial menu | 6–8 segments max, icon + short label, centre shows the hovered label | mouse direction, number keys | submenus as a second ring, not more segments |
| Pause / ESC replacement | full screen, dimmed game behind, large main buttons | arrows, Enter, ESC back | leave a way to the real GTA settings |
| HUD | corners and bottom edge, not centre; hide when cinematic/menus open | — | update on events, not every frame |

Common to all: a visible **selected** state (not only hover), focus ring for keyboard users, disabled state with reason ("not enough money"), loading state for server calls, success/error feedback in the menu, and a sound for move/select/back if the server uses them (e.g. `PlaySoundFrontend(-1, 'NAV_UP_DOWN', 'HUD_FRONTEND_DEFAULT_SOUNDSET', true)`, `'SELECT'`, `'BACK'`).

## Style recipes (performance-safe)

Use these as tokens; replace the accent with the server's brand colour.

**Clean dark (default, cheapest)**
```css
:root { font-size: clamp(12px, 1.6vh, 22px); --bg: rgba(12,14,18,.92); --panel: rgba(22,25,31,.95);
  --line: rgba(255,255,255,.08); --text: #E8EAED; --muted: #9AA0A6; --accent: #7C5CFF; --radius: .5rem; }
.menu { background: var(--bg); border: 1px solid var(--line); border-radius: var(--radius); color: var(--text); }
.row.selected { background: color-mix(in srgb, var(--accent) 22%, transparent); box-shadow: inset 3px 0 0 var(--accent); }
.menu { transition: transform .15s ease-out, opacity .15s ease-out; }
```

**Light glass (one panel only)**
```css
.menu { background: rgba(18,20,26,.70); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,.10); }
/* only the outer panel blurs; rows are solid; no blur on hover/animation */
```

**GTA-style (sharp, bold)** — square corners, uppercase condensed headings (an open-licence condensed font bundled locally), a solid colour title bar, white rows with dark selected row, minimal animation.

**Neon / street** — dark base, one saturated accent with a *static* glow (`text-shadow` or a 1–2 px coloured border); no pulsing glows.

**Minimal / premium** — generous spacing, one typeface in two weights, thin dividers, muted palette, accent used only for the primary action and selection.

## Fonts and icons (free, bundle locally)

Open-licence fonts (SIL OFL / Apache) such as Inter, Roboto, Rajdhani, Oswald, Barlow Condensed; `ui-ux-pro-max` lists more pairings with licences (`--domain typography`). Icons: Font Awesome Free (what ox_lib uses), Lucide, Phosphor. Download the files into the resource and add them to `files {}`.

## Quick self-review

- Readable at 720p and 4K? Contrast ≥ 4.5:1 over a bright daytime scene and at night?
- Usable with keyboard only? ESC/Backspace everywhere? Focus released?
- Nothing animating when idle? At most one small blur? FPS unchanged with the menu open?
- Consistent with the server's other menus (accent, font, radius, sounds)?
