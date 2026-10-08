# Real foldables to copy (2025–2026)

Copy real devices: players know them, and "almost like a Fold" reads as cheap. Specs below come from manufacturer pages, carriers and press coverage, found through search on 2026-10-08. The official Apple and Samsung pages were blocked from this environment, so figures come from secondary sources that quote them. Where sources disagreed, that is noted. Use in-universe or generic names in game ("书本折叠", "翻盖", "三折叠"), not trademarks.

## Devices

| Device | Fold | Closed (cover) screen | Open (inner) screen | Body | Notes |
|---|---|---|---|---|---|
| **Apple iPhone Duo** (announced 2026-09-09) | book, inward | 5.4" portrait, 1398 × 2034 | 7.6", 1878 × 2670, used **landscape** when open | open 117.8 × 164.6 × 5.2 mm, closed 117.8 × 84.1 × 11.3 mm, 254 g | both screens share one aspect ratio, so content scales when opening. Short and wide when closed ("passport"). Touch ID in the side button. Matte nano-texture reduces (doesn't remove) the crease |
| **Samsung Galaxy Z Fold8** (2026) | book, inward | 5.5", **10:16** (wide) | 7.6", **4:3** | closed 81.9 × 123.9 × 9.7 mm, open 161.4 × 123.9 × 4.5 mm, 201 g | new wide shape, closer to a normal phone when closed |
| **Samsung Galaxy Z Fold8 Ultra** (2026) | book, inward | 6.5", 2520 × 1080, **21:9** (tall, narrow) | 8.0", ≈ 2504 × 2256 (near square; some sources list Fold7's 2184 × 1968) | open 158.4 × 143.2 × 4.1 mm, closed 158.4 × 72.8 × 8.9 mm, 215 g | the classic tall Fold shape. Same as Fold7 |
| **Samsung Galaxy Z Flip8** (2026) | clamshell (top folds onto bottom) | 4.1" FlexWindow, 948 × 1048 (almost square) | 6.9", 2520 × 1080, 21:9 | closed 75.4 × 85.7 × 13.1 mm, open 75.4 × 166.9 × 6.1 mm, 180 g | cover runs widgets and up to 5 pinned apps, about 16 apps can run fully on the cover. Flex mode: half-folded with content on top and controls below |
| **Samsung Galaxy Z TriFold** (2025-12) | two hinges, both **inward** ("G" fold), different sizes | 6.5", 2520 × 1080, 21:9 | 10.0", 2160 × 1584, 4:3 | open 159.2 × 214.1 × 3.9–4.2 mm, closed 159.2 × 75 × 12.9 mm, 309 g | unfold **right side first, then left**. Only fully folded or fully open. Warns (screen + haptic) on a wrong fold order. "Three 6.5-inch phones side by side": 3 portrait apps, standalone DeX |
| **Huawei Mate XTs** (2025-09) | two hinges, **outward** "Z" fold | 6.4" single | 7.9" dual (2048 × 2232), 10.2" triple (2232 × 3184, 16:11) | 3.8 mm open, 12.8 mm closed, 298 g | three usable states. The screen is on the outside (no cover screen). The later Mate XT 2 switched to inward folding |

## What their software does (copy this behaviour)

**iPhone Duo / iOS 27** (press coverage of Apple's announcement):
- Opening shows **two Home Screen pages side by side**, not one enlarged page.
- **Split View**: two apps side by side, or two windows of one app, with saved app pairs and drag and drop between them.
- When partly folded, content moves away from the crease (tabletop: video on top, hands-free calls).
- Same aspect ratio on both screens, so the UI resizes proportionally between them.
- Reported: Dock, Lock Screen controls and app navigation move to the sides of the inner screen, and the Dynamic Island runs vertically along the side. That is unverified; check Apple's page before copying it.

**Samsung One UI 9** (Fold8 / Fold8 Ultra / Flip8):
- **App Continuity**: the app continues from cover to main screen and back.
- **Multi-window**: two-way and three-way splits (Fold8 adds a 90:10 three-app layout and three apps stacked side by side), pop-up windows, swipe gestures for split/pop-up (off by default), and a **taskbar** with favourite and recent apps on the open screen.
- **Flip8 FlexWindow**: a consistent cover layout, a widget page, 5 pinned apps, editing the apps/widgets/Quick Panel without opening the phone, the wallpaper stretched with the clock repositioning, Now Bar/Now Brief, and Mirror View (cover as mirror).
- **Flex mode** (half-folded): preview on one half and controls on the other (camera, video, calls).
- **TriFold**: smartphone mode on the cover, tablet mode on the main screen, three portrait apps, DeX.

## How the template turns this into frames

`assets/phone-template/web/app.js` → `DEVICES` stores, per state, `body` (the measured outline in mm) and `screen` (resolution ÷ ppi, or diagonal + aspect ratio), both converted at 152 pt per inch. The frame is whatever is left between them, so each device keeps its real bezel widths and the devices keep their real sizes relative to each other. Notes:
- Fold8 Ultra: Samsung's inner screen is portrait (taller than wide, about 2184 × 1968 on Fold7), so the open canvas is 813 × 902 pt.
- Not replicated: side buttons, camera bumps and the Flip's cover-screen lens cut-outs, hinge hardware, colours and materials. Screen corner radii are estimates from photos, not published values. iPhone Duo's camera position and vertical Dynamic Island are unverified, so the template uses a normal pill.
- Real industrial design is protected (trade dress): keep generic names and don't copy logos or exact styling into a public resource.

## What this means for a FiveM phone

1. **Pick one device family per server** and copy its proportions (the canvases in `assets/phone-template/web/app.js` → `DEVICES` are derived from the specs above at ≈ 152 pt per inch).
2. **Closed = a complete phone.** Every app must work on the cover (Fold, TriFold, Duo). For a Flip cover, design a separate small UI: clock, widgets, 5 pinned apps, notifications, quick reply.
3. **Open = more panes, not bigger UI.** Book fold → 2 panes, TriFold → 3 panes, with the pane borders on the hinges. Home → two or three pages of icons/widgets. Messages → list | chat (| contact info). Wallet → balance | history (| transfer form).
4. **Continuity**: folding never loses the open item, scroll or draft (Samsung App Continuity, Apple's proportional resize).
5. **Respect the hinge(s)**: no controls or text on a crease. TriFold has two hinges, at ⅓ and ⅔.
6. **Copy the physical ritual**: TriFold opens right side first, then left, so animate it in two steps. A Flip opens upward from its bottom edge. A book fold opens leftwards when the phone sits at the right edge of the screen.
7. **Immersive**: every control lives inside the phone (lock screen, control centre, settings, an edge grip to unfold). Nothing floats outside the phone.
