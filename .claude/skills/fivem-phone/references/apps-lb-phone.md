# lb-phone custom apps

lb-phone is a **paid, escrowed** phone. Don't recommend buying it. If the user already owns it, its custom-app API is the right way to add apps. Never edit or decompile lb-phone itself.

Source: lb-phone-app-template (MIT, © 2023 LB): `lb-vanillajs/client.lua`, `lb-reactts/client/client.lua`, `lb-reactts/ui/src/components.d.ts` (the type declarations of everything lb-phone injects), and README. The full docs are at docs.lbscripts.com/phone/custom-apps; not read here.

## Resource layout

```
my_app/
  fxmanifest.lua    -- client_script, file "ui/**/*" (or "ui/dist/**/*"), ui_page "ui/index.html"
  client.lua        -- AddCustomApp, NUI callbacks, SendCustomAppMessage
  server.lua        -- data, validation (your own)
  ui/index.html …   -- your app page (vanilla, React, Vue)
```
lb-phone shows your page inside the phone frame (an iframe of your resource; `window.name` is non-empty there, and the React template only renders when `window.name === ''` in dev or after `componentsLoaded` in game).

## Registering the app (client)

```lua
local identifier = "my-app"

while GetResourceState("lb-phone") ~= "started" do Wait(500) end
-- the React template also waits Wait(1000) for the export to exist

local function addApp()
    local added, err = exports["lb-phone"]:AddCustomApp({
        identifier  = identifier,           -- unique
        name        = "My App",
        description = "…",
        developer   = "…",
        defaultApp  = false,                -- true = installed on every phone automatically
        size        = 59812,                -- shown size in kB
        -- price    = 0,                    -- optional in-game price to download
        images      = { "https://cfx-nui-" .. GetCurrentResourceName() .. "/ui/assets/screenshot.png" },
        ui          = GetCurrentResourceName() .. "/ui/index.html",
        icon        = "https://cfx-nui-" .. GetCurrentResourceName() .. "/ui/assets/icon.svg",
        fixBlur     = true,                 -- set when your CSS uses em/rem instead of px
    })
    if not added then print("Could not add app:", err) end
end

addApp()
AddEventHandler("onResourceStart", function(res)
    if res == "lb-phone" then addApp() end  -- lb-phone restarted → register again
end)
```
- `ui` is `<resource>/<path>` (no scheme). In dev the template points it at a Vite server (`http://localhost:3000/` or `:5500`). **Switch back before going live.** The React template ships with `ui_page "http://localhost:3000/"` uncommented.
- The React template reads the path from the manifest: `GetResourceMetadata(GetCurrentResourceName(), "ui_page", 0)`.
- Paths must exist and be in `file`/`files`, or the app opens blank.

## Talking between Lua and the page

- Lua → page: `exports["lb-phone"]:SendCustomAppMessage(identifier, { type = "update", … })`. The page gets it as a `message` event (`e.data.type`). In React, use the injected `useNuiEvent(type, cb)`.
- Page → Lua: injected `fetchNui(event, data, mockData?)` → `RegisterNUICallback(event, function(data, cb) … cb(result) end)` in your resource. Always call `cb`.
- Camera: `exports["lb-phone"]:EnableWalkableCam()` / `DisableWalkableCam()` (used by the React template's camera toggle).

## What lb-phone injects into the page

Wait for `window.postMessage('componentsLoaded')` (the page receives `e.data === 'componentsLoaded'`) before calling any of these. The vanilla template loads its main script only then. In React or TypeScript, use the `window.` prefix (README).

- variables: `resourceName` (use it when fetching), `appName` (the identifier), `settings`
- data: `fetchNui`, `useNuiEvent`, `getSettings()`, `onSettingsChange(cb)` (theme in `settings.display.theme`: set it on your root, e.g. `data-theme`)
- phone UI: `setPopUp({ title, description, attachment, buttons })`, `setContextMenu({ title, buttons })`, `sendNotification({ title, content, thumbnail, avatar, showAvatar })`, `formatPhoneNumber(n)`, `setApp(name | { name, data })` (open another app), `createCall({ number, videoCall, company, hideNumber })`
- pickers: `selectGallery`, `selectGIF`, `selectEmoji`, `colorPicker`, `useCamera(cb, options)`
- `components.*`: `uploadMedia`, `saveToGallery`, `fetchPhone`, `setColorPicker`, `setMusicSelector`, `setContactSelector`, `setEmojiPickerVisible`, `setShareComponent`, `setGifPickerVisible`, `setGallery`, `setFullscreenImage`, `setHomeIndicatorVisible`, `createGameRender(canvas)`

Use the phone's own pop-ups, context menus and pickers instead of drawing your own. They match the phone's theme and the player already knows them.

## Design notes

- Follow the phone theme (light/dark) from `getSettings`/`onSettingsChange`. The templates ship `colors.css` with both palettes.
- Size with `rem`/`em` and set `fixBlur = true`. The template's dev page scales the frame with `window.innerWidth / 1920`.
- The template loads Poppins from Google Fonts. For production, bundle the font locally (CDN fonts fail when blocked, and every player downloads them).

## Common mistakes

- No `onResourceStart` re-add → restarting lb-phone makes the app disappear until your resource restarts.
- Calling `AddCustomApp` before lb-phone has started → "No such export". Wait for `GetResourceState`.
- Left `ui_page`/`ui` on `localhost` → works on the developer's PC only.
- Different identifier in `AddCustomApp` and `SendCustomAppMessage` → messages never arrive.
- Prices and rewards taken from `fetchNui` data on the server → exploitable. Validate server-side.
