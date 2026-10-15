# FiveM NUI rules for menus

Sources: fivem-docs `scripting-manual/nui-development` (Fullscreen NUI, NUI callbacks); FiveM source `code/components/nui-resources/src/ResourceUIScripting.cpp` (focus natives), `nui-core/src/NUIWindow.cpp` and `NUIApp.cpp` (renderer settings); ox_lib `resource/interface/client/menu.lua`.

## How NUI is drawn

- NUI is Chromium (CEF) rendered off-screen and composited over the game. Each resource's `ui_page` is a **full-screen iframe** the size of the game window; there is **no click-through between resources** (fivem-docs).
- The off-screen renderer is set to `windowless_frame_rate = 240` (NUIWindow.cpp). Anything that changes on screen — a CSS animation, a spinner, a blur over moving game content — keeps it repainting. Idle, static UI is cheap; animated or blurred UI costs GPU time every frame.
- GPU rasterization is on and, by default, the GPU work runs in process (`nui_useInProcessGpu`, NUIApp.cpp).
- Dev tools: open `http://localhost:13172/` in a Chromium browser while the game runs, or `nui_devTools` in F8 with developer mode (fivem-docs). Use the Performance tab to see paint cost.

## Manifest and assets

```lua
ui_page 'web/build/index.html'          -- React/Vite: point at the BUILT file
files { 'web/build/index.html', 'web/build/**/*' }
```
- Every file the page loads must be in `files {}`.
- Reference resource files with relative paths or `https://cfx-nui-<resource>/path` (the old `nui://` is no longer a secure context).
- Bundle fonts and icon sets in the resource. CDN links (Google Fonts, cdnjs, jsDelivr) make every player download them on every open and break offline or where blocked.
- Keep images small (WebP, a few hundred KB); players download everything on join.

## Focus and input

- `SetNuiFocus(hasFocus, hasCursor)` gives keyboard and/or mouse to **this resource's** page. Internally each resource adds a "vote"; NUI stays focused while **any** resource has a vote (ResourceUIScripting.cpp). One resource that forgets `SetNuiFocus(false, false)` leaves the player stuck with a cursor. Always release on: close button, ESC, Backspace at the top level, death, and resource stop.
- A resource's votes are cleared when it stops, so restarting it frees the player — but only that resource's votes.
- `SetNuiFocusKeepInput(true)` lets the game keep receiving input while the page has focus (for menus you navigate while walking/driving). It only takes effect for a resource that also holds focus. Pair it with a loop that `DisableControlAction`s the keys the menu uses (arrows, Enter, Backspace, ESC/pause, weapon wheel, attack) while open, or the player will shoot, change weapon or open the pause menu while using the menu.
- `IsNuiFocused()` tells you whether any focus is active.
- ox_lib menus handle this for you: `lib.showMenu` calls `lib.setNuiFocus(not menu.disableInput, true)`; `canClose = false` blocks ESC/Backspace closing; `onClose(keyPressed)` receives `'Escape'` or `'Backspace'`.

### ESC and Backspace

```js
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') post('close');
  if (e.key === 'Backspace' && !isTypingInInput(e)) post('back');
});
```
```lua
RegisterNUICallback('close', function(_, cb)
  SetNuiFocus(false, false)
  SendNUIMessage({ action = 'hide' })
  cb({})
end)
```
Don't let Backspace navigate back while the player is typing in a text field.

## Messages and callbacks

- Lua → page: `SendNUIMessage({ action = 'open', data = ... })` (JSON-encodable data only); the page listens to `window.addEventListener('message', ...)`.
- Page → Lua: `fetch(\`https://${GetParentResourceName()}/name\`, { method: 'POST', body: JSON.stringify(data) })` handled by `RegisterNUICallback('name', function(data, cb) ... end)`.
- **Always call `cb(...)`**, even with `{}` — otherwise the page's `fetch` hangs until it times out (fivem-docs: "you **have to** return the callback at all times").
- Use `GetParentResourceName()` instead of a hard-coded resource name, so renaming the resource doesn't break every button.
- Send only what changed; don't push the whole state every frame from a Lua loop.

## Security

Everything coming from the page is player-controlled. The page sends **intent** (`{ item = 'water' }`); the server looks up price, stock, money, job/grade and distance, then responds. Never forward `data.price`, `data.amount`, `data.reward` to the server as truth. See `fivem-security-audit`.

## Scaling and readability

- The page is the size of the game window: 1280×720 up to 3440×1440 and 4K. Use `rem` with a root size tied to the viewport, e.g. `:root { font-size: clamp(12px, 1.6vh, 22px); }`, or `vh`/`clamp()` for panel sizes; anchor panels to edges/corners instead of absolute pixel positions.
- Test the longest strings (translations, long item names, big numbers) at 720p.
- The background is a moving, unpredictable game scene: use near-solid dark panels (`rgba(10,12,16,0.85)` or more), text contrast ≥ 4.5:1, a subtle text shadow for text placed directly over the game, and never pure white large areas at night.
- Don't cover the minimap, the centre of the screen or the player's character with persistent menus; side or corner placement is the norm (ox_lib positions: `top-left`, `top-right`, `bottom-left`, `bottom-right`).

## Performance checklist

- Hide = remove: when closed, `display: none` or unmount — an `opacity: 0` menu with running animations still repaints.
- Animate only `transform` and `opacity`; 120–200 ms for menu transitions; no `transition: all`; no width/height/top/left animations.
- No infinite animations (glows, pulses, spinners) except a loading indicator while actually loading.
- `backdrop-filter: blur()` re-blurs the game behind it every frame: at most one small panel, blur ≤ 8–12 px, or replace it with a semi-opaque dark background. Avoid stacking several blurred layers.
- Few, small shadows on list items; large blurred shadows on many elements slow repaints.
- Large lists: virtualise (render only visible rows) for inventories with hundreds of slots.
- Check with dev tools (Performance tab) and in-game FPS with the menu open vs closed.
