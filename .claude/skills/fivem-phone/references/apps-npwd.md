# npwd external apps

npwd loads apps from **other resources** at runtime, so an app is its own resource and npwd stays untouched. Two generations exist. Check which one the server runs: look at the `version` in npwd's `fxmanifest.lua` and whether npwd's `config.json` has an `"apps"` array.

Sources: project-error/npwd master (fxmanifest `version 3.16.0`, 2025-03): `apps/phone/src/common/hooks/useExternalApps.tsx`, `apps/phone/src/os/apps/config/apps.tsx`, `apps/phone/src/os/apps/utils/createExternalAppProvider.tsx`, `apps/game/client/cl_exports.ts`, `apps/game/utils/messages.ts`, `packages/npwd-hooks`. project-error/npwd-app-template (2026-04, "v4 template").

## npwd 3.x (current public release)

**How npwd loads it** (useExternalApps.tsx):
1. npwd reads `"apps": ["my_app", …]` from **npwd's** `config.json`. Each entry is a resource name.
2. In game it loads `https://cfx-nui-<resource>/web/dist/remoteEntry.js`. In the browser dev mode it loads `http://localhost:4173/remoteEntry.js`.
3. Through Vite module federation (`@originjs/vite-plugin-federation`, format `esm`) it gets the remote module `./config`. It calls its default export as a function. The return value is the app config.
4. It renders `config.app` as the page, at route `config.path`, wrapped in npwd's theme (MUI theme merged with `config.theme`), an error boundary and a splash screen. `config.icon` and `config.notificationIcon` are React components.
5. On failure it logs `Failed to load external app "<name>". Make sure it is started before NPWD.` So **`ensure` the app before `ensure npwd`**.

**Config fields** (from `IAppConfig`/`IApp`): `id`, `nameLocale` (the label), `color`, `backgroundColor`, `path` (e.g. `/my_app`), `icon`, `app` (the root component), `notificationIcon`, optional `theme`, `disable`.

**What the app resource ships:**
- `web/dist/remoteEntry.js` and its chunks, built by Vite with the federation plugin. `exposes: { './config': './src/config.ts' }` and `shared: ['react', 'react-dom', …]` must match npwd's own shared list: `react`, `react-dom`, `@emotion/react`, `react-router-dom`, `fivem-nui-react-lib`. Otherwise the app gets a second React and hooks break.
- `fxmanifest.lua` with `files { 'web/dist/**/*' }` (or the explicit files) and your client/server scripts.
- The resource name must equal the name in npwd's `"apps"`. The URL is built from it.

**Talking to the game:**
- Lua → app page: the app's page lives inside **npwd's** NUI page. A `SendNUIMessage` from your own resource goes to your resource's page, not npwd's. Use npwd's export:
  `exports.npwd:sendNPWDMessage('my_app', 'setData', data)`. It sends `{ app, method, data }` to npwd's page, and your app listens with `window.addEventListener('message', …)` and filters on `event.data.app`.
- App page → Lua: `fetch('https://<your_resource>/<callback>', { method: 'POST', body: JSON.stringify(data) })` handled by `RegisterNUICallback` in your resource. Inside npwd's page `GetParentResourceName()` returns `npwd`, so write your own resource name, or read it from your config. Posting from one resource's page to another resource's callback is how external apps are expected to work. Unverified here: test it once.
- App ↔ npwd UI: `@npwd/hooks` (MIT) has `useNpwdEvent(event)` and `useSubscription(event, handler)`. They are thin wrappers over `window.dispatchEvent(new CustomEvent(event, { detail }))` and `addEventListener`.
- Useful npwd client exports (cl_exports.ts): `openApp(app)`, `setPhoneVisible(bool)`, `isPhoneVisible()`, `setPhoneDisabled(bool)`, `isPhoneDisabled()`, `startPhoneCall(number, anonymous)`, `fillNewContact`, `fillNewNote`, `getPhoneNumber()`, `isInCall()`, `endCall()`, `sendNPWDMessage(app, method, data)`, `createNotification(dto)`, `createSystemNotification(dto)`.
- Keyboard while typing: npwd toggles KeepInput itself (`PhoneEvents.TOGGLE_KEYS` NUI callback → `SetNuiFocusKeepInput(keepGameFocus)`). Text inputs from npwd's UI library already handle it. Custom inputs should use npwd's input component (exposed as `./Input` from npwd), or the player walks while typing.

## npwd v4 (new template)

The npwd-app-template README says it targets "NPWD v4". The public npwd repo branches don't contain `RegisterExternalApp` yet (checked master, develop, v2, reimagined), so **only use this when the server runs an npwd that has that export**. Otherwise use 3.x above.

Template layout:
```
client/client.ts      -- NUI callbacks, natives (esbuild → dist/client.js)
server/server.ts      -- registers the app
web/src/index.tsx     -- default export = app component, export const icon, optional widgets
web/vite.config.ts    -- IIFE bundle named __npwd_ext_<id> → dist/web/app.js
fxmanifest.lua        -- server_script dist/server.js, client_script dist/client.js,
                      -- files { 'dist/web/app.js' }, dependency 'npwd'
```

Registration (server, on your own `onResourceStart`):
```ts
on('onResourceStart', (res: string) => {
  if (res !== GetCurrentResourceName()) return;
  exports.npwd.RegisterExternalApp({ id: 'my_app', resourceName: GetCurrentResourceName(), name: 'My App' });
});
```
Rules from the template:
- `id` must match the Vite IIFE name `__npwd_ext_<id>`. That is how npwd finds the bundle.
- Do **not** bundle what npwd provides at runtime. Mark these as `external` with these globals: `react` → `__npwd_React`, `react/jsx-runtime` → `__npwd_jsxRuntime`, `react-dom` → `__npwd_ReactDOM`, `lucide-react` → `__npwd_lucideReact`, `@npwd/sdk` → `__npwd_sdk`, `@npwd/keyos` (npwd UI components) → `__npwd_keyos`, `motion/react` → `__npwd_motionReact`.
- Widgets: `export const widgets = [{ id, nameKey, sizes: ['small', 'medium'], component }]` for home-screen widgets.
- Styling classes in the template (`text-foreground`, `text-muted-foreground`, `bg-muted`) are theme tokens from npwd's UI. Use them so the app follows the phone's light/dark theme.
- Build: `npm install && cd web && npm install`, then `npm run build`. The template's GitHub Action zips a release on a `v*` tag. The README mentions an npwd registry/App Store for publishing.

## Common mistakes

- App resource started after npwd (3.x) → app silently missing. Fix the `ensure` order.
- Resource folder renamed → the 3.x URL or the v4 `resourceName`/id no longer match.
- Second copy of React bundled → "Invalid hook call". Use shared/external as above.
- `SendNUIMessage` from the app's Lua → nothing arrives. Use `sendNPWDMessage`.
- Trusting the page: amounts, targets and job checks must be validated in your **server** script.
