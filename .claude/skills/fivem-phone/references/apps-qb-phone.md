# Adding an app to qb-phone (and forks such as z-phone)

qb-phone has **no plug-in API**. An app is added by editing the phone resource in four places. Keep your changes in a fork or a patch so qb-phone updates don't wipe them. GPL-3.0 applies (z-phone: AGPL-3.0).

Source: qbcore-framework/qb-phone (2026-08): `config.lua`, `client.lua`, `html/index.html`, `html/js/app.js`, README. z-phone (Z3MO/z-phone) keeps the same structure with `client/`, `server/`, `shared/bridge.lua` folders and Qbox/ox support.

## How the home screen works

- `Config.PhoneApplications` (config.lua) lists the built-in apps. Each entry has: `app` (route/id, unique), `color` (icon background), `icon` (Font Awesome class), `tooltipText` (name), `tooltipPos`, `job` (`false` or a job name), `blockedjobs` (list), `slot` (home-screen position), `Alerts`.
- `Config.StoreApps` are downloadable apps with the same fields plus `style`, `password`, `creator`, `title`… On load, the client copies installed store apps into `Config.PhoneApplications`.
- The client sends the table to the page (`SendNUIMessage` with `applications = Config.PhoneApplications`). `QB.Phone.Functions.SetupApplications` fills `.phone-application[data-appslot="<slot>"]`. The stock html has **20** slot divs, while `QB.Phone.Data.MaxSlots = 16` is only used to clear slots. Keep slots unique and within the divs that exist.
- A job app shows only when `job` matches the player's job name. `blockedjobs` hides the app from those jobs, but only while the player is **on duty** (`IsAppJobBlocked` checks `job.onduty`). This hiding is cosmetic: the server callback must still check the job.
- Clicking an icon (`$(document).on('click', '.phone-application', …)` in app.js) looks for an element with class `<app>-app`. **If it doesn't exist, nothing happens.** If it exists, `ToggleApp(app, "block")` shows it. Then an `if (PressedApplication == "…")` chain loads that app's data, e.g. `$.post('https://qb-phone/SetupGarageVehicles', …)`.

## Steps

1. **config.lua:** add an entry
   ```lua
   ['myapp'] = { app = 'myapp', color = '#6c5ce7', icon = 'fas fa-store', tooltipText = 'My App',
                 tooltipPos = 'top', job = false, blockedjobs = {}, slot = 17, Alerts = 0 },
   ```
2. **html/index.html:** add the screen next to the others (`<div class="myapp-app"> … </div>`, inside the same container as `garage-app` etc.) and `<script src="./js/myapp.js"></script>` with the other scripts. Add a slot div if you use a slot that doesn't exist.
3. **html/js/app.js:** in the click chain add
   ```js
   } else if (PressedApplication == "myapp") {
       $.post('https://qb-phone/myapp:getData', JSON.stringify({}), function (data) { MyApp.render(data); });
   ```
   Put the app's own logic in `html/js/myapp.js` and styles in `html/css/myapp.css` (link it in index.html). The manifest's `files` globs (`html/js/*.js`, `html/css/*.css`) already include new files there.
4. **client.lua:** add the NUI callbacks and always call `cb`:
   ```lua
   RegisterNUICallback('myapp:getData', function(_, cb)
       QBCore.Functions.TriggerCallback('qb-phone:server:myapp:getData', function(result) cb(result) end)
   end)
   ```
   and on the server `QBCore.Functions.CreateCallback(...)` that reads from the database for **this** player and validates everything.

Lua → page pushes use `SendNUIMessage({ action = 'myapp:update', … })` plus a branch in the page's message listener (`window.addEventListener('message', …)` in app.js).

## Things to fix while you're in there (optional, ask first)

- The stock page loads jQuery, Bootstrap, moment, DOMPurify, emojionearea, clipboard.js and Font Awesome from CDNs. Bundle them locally for reliability (the checker reports this).
- `$.post('https://qb-phone/…')` hard-codes the resource name. Renaming the folder breaks every button. Prefer `https://${GetParentResourceName()}/…` in new code.
- Animations: qb-phone uses `cellphone@` and `anim@cellphone@in_car@ps` with flag 50 and attaches `prop_npc_phone_02` to bone 28422. See `phone-frame.md` before changing them.

## z-phone specifics

- `Config.Framework = 'auto' | 'qb' | 'qbox'`, `Config.Inventory = 'auto' | 'qb' | 'ox'`, `Config.Target = 'auto' | 'qb' | 'ox'`. Use the bridge in `shared/bridge.lua` instead of calling QBCore directly, so the app works on both QBCore and Qbox.
- Its manifest loads `@z-garages/config.lua`. Comment it out without z-garages, as the manifest says.
- Same app steps as above. The file names differ (client/server folders), so search for the click handler and `PhoneApplications` in the fork.
