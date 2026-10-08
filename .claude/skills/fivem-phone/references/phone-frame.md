# Building or fixing the phone itself

For a new phone, or for changing how an existing free phone opens, holds and closes. The general NUI rules (focus votes, `cb`, assets, performance) are in `fivem-menu-design/references/fivem-nui-rules.md`. This file covers what is specific to phones.

Sources: npwd `apps/game/client/functions.ts` (prop), `animations/animation.service.ts`, `cl_controls.lua` (disabled controls, pause menu), `cl_main.ts` (TOGGLE_KEYS); qb-phone `client.lua` (prop, animation, open checks, Close callback). Control names are from those files' comments.

## Open / close state machine

```
closed ──open key──► opening (anim in + prop) ──► open (focus on) ──close──► closing (anim out) ──► closed
                                                     │  call ►  in-call (call anim, phone may be hidden but call continues)
```
Guard **every** transition. Opening twice quickly must not spawn two props, and closing must work from any state.

**Open checks** (qb-phone checks these before opening): not `isdead`, not `inlaststand`, not `ishandcuffed` (QBCore metadata), `not IsPauseMenuActive()`. Add a phone item check if the server uses "phone as item" (npwd: `config.json` → `PhoneAsItem` with an export; ox_inventory: `exports.ox_inventory:Search('count', 'phone')`). The inventory check is a convenience. The server must still refuse phone actions from players without the item if it matters.

**Key:** `RegisterCommand('phone', …)` + `RegisterKeyMapping('phone', 'Open Phone', 'keyboard', 'F1')` so players can rebind it in GTA settings (qb-phone does this; npwd uses `toggleKey`/`toggleCommand` in config).

**On open:** `SetNuiFocus(true, true)`, optional `SetNuiFocusKeepInput(true)` (walk while using the phone), start the animation and prop, then `SendNUIMessage({ action = 'open' })`.
**On close:** `SendNUIMessage({ action = 'close' })`, `SetNuiFocus(false, false)`, `SetNuiFocusKeepInput(false)`, play `cellphone_text_out`, then `StopAnimTask` and delete the prop after ~400 ms (qb-phone uses `SetTimeout(400, …)`). If a call is active, switch to the call animation instead of removing the prop.

**Auto-close:**
- pause menu: npwd checks `IsPauseMenuActive()` every 500 ms and hides the phone;
- death / last stand / cuffs (framework events or metadata);
- `onResourceStop` for your own resource: delete the prop, release focus, stop animations;
- the item being removed (phone as item).

## Walking while the phone is open (KeepInput)

`SetNuiFocusKeepInput(true)` lets movement keys reach the game. While it's on, disable the keys that would fight the phone every frame (`Wait(0)` loop only while open, `Wait(100+)` when closed). npwd disables these (control id → meaning):
`0` next camera, `1`/`2` look, `16`/`17` weapon next/prev, `22` jump, `24` attack, `25` aim, `26` look behind, `36` duck, `37` weapon wheel, `44` cover, `47` detonate, `55` dive, `75` exit vehicle, `76` handbrake, `81`/`82` radio, `91`/`92` passenger aim/attack, `99` vehicle weapon, `106` vehicle mouse control override, `114`/`115`/`121`/`122` flying, `135` sub, `140` melee light, `200` pause menu, `245` chat.
qb-phone (without KeepInput) disables look `1`–`6` and melee `140`, `257`, `263`, `264`.

**Typing:** with KeepInput on, typing "w" in a text field also walks forward. npwd fixes this with a NUI callback (`TOGGLE_KEYS` → `SetNuiFocusKeepInput(keepGameFocus)`) called when an input gains/loses focus. Do the same: `focusin` on inputs → keepInput false, `focusout` → true.

## Prop and animation

| | npwd | qb-phone |
|---|---|---|
| model | `prop_amb_phone` (or `dolu_npwd_phone` when convar `NPWD_PROPS` is set) | `prop_npc_phone_02` (`prop_cs_phone_01` supported with rotation `50.0, 320.0, 50.0`) |
| attach | bone index of `28422` (right hand), offsets 0, `AttachEntityToEntity(…, true, true, false, false, 2, true)` | same bone, `1, 1, 0, 0, 2, 1` |
| create | `CreateObject(hash, x, y, z + 0.2, true, true, true)` (networked, others see it) | `CreateObject(model, 1.0, 1.0, 1.0, 1, 1, 0)` |

Animations (both phones):
- on foot: dict `cellphone@`; in a vehicle: `anim@cellphone@in_car@ps` (`IsPedInAnyVehicle`).
- open `cellphone_text_in`, close `cellphone_text_out`, call `cellphone_call_listen_base`, switching `cellphone_text_to_call` / `cellphone_call_to_text`.
- flags: `50` for texting (upper body + loop + player control); npwd uses `49` for the call loop.
- Other tasks interrupt the animation (entering a car, ragdoll). npwd re-checks every 250 ms and replays it while the phone is open. Do this on a slow timer, not every frame.

Housekeeping: `RequestModel` → wait for `HasModelLoaded` with a timeout → create → `SetModelAsNoLongerNeeded`. `RemoveAnimDict` after use. Always `DeleteObject`/`DeleteEntity` the prop on close, on death and on resource stop. Leaked networked props pile up for everyone.

A custom phone model (e.g. a foldable) is a new prop: model it in Blender, export with Sollumz (.ydr), stream it, and add a `.ytyp` if needed. Ask before using the Blender skills. Custom open/fold animations → `fivem-animation`.

## The frame on screen

- Anchor bottom-right (the minimap is bottom-left), slide up with `transform: translateY()` 200–300 ms, ease-out. Remove from the page when closed (`display: none`).
- Size from the viewport, not px: one `--pt` unit derived from the frame height (`phone-design.md` §1), `aspect-ratio: 390 / 844`, everything inside in `calc(N * var(--pt))`. Check at 1280×720, 1920×1080 and 2560×1440.
- Status bar time: send the in-game clock (`GetClockHours()`, `GetClockMinutes()`) on open and once per in-game minute, not every frame.
- Notifications while closed: show a small "peek" banner without taking focus (no `SetNuiFocus`), then let the open key jump into that app.
- One page, many apps: keep the phone shell (status bar, home, notifications, router) separate from apps, so apps can be added without touching the shell.

## Data

- Phone number, contacts, messages, photos: in the database, keyed by the character (citizenid). Load them on open (or on character load) through a server callback (ox_lib `lib.callback`, QBCore `CreateCallback`).
- Messages to another player: the server checks that the target number exists and routes the message. Never let the page name a server ID to send to.
- Photos: `screenshot-basic` to an image host. Free/self-hosted options only. npwd's default config points at fivemanage, so check whether a free tier fits before recommending it.
