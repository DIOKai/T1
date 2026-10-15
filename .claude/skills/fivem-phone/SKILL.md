---
name: fivem-phone
description: Build, extend and design FiveM phones — write custom apps for npwd (free, GPL), lb-phone (paid, open app API) and qb-phone / z-phone, build a phone frame from scratch in NUI (open/close, phone prop and cellphone@ animations, walking with KeepInput, pause/death handling, scaling 720p–4K), make a foldable phone (cover screen vs inner screen, hinge animation, two-pane list-detail when open, state kept across fold/unfold, tabletop/book postures), and make it look like a real iOS/Android phone without costing FPS. Includes a checker for phone apps and phone resources. Use whenever the user mentions a FiveM/QBCore/Qbox phone or phone app — even if they only say "手机", "做手机 app", "npwd app", "lb-phone app", "qb-phone 加 app", "折叠手机", "摺疊手機", "手机界面", "手机拿出来动作", "手机打不开/关不掉".
---

# FiveM phone

A FiveM phone is a NUI page shaped like a phone, plus a prop in the player's hand, plus server-backed data (contacts, messages, bank). Most of the work is **writing apps for a phone that already exists**; building a whole phone is a big project and only worth it when no existing phone fits. This skill covers both, plus foldable phones and phone-style design.

Read what you need:
- `references/choose-a-phone.md` — npwd vs lb-phone vs qb-phone vs z-phone vs your own: licence, price, framework, how apps plug in. Read first when the user hasn't said which phone they use.
- `references/apps-npwd.md` — external apps for npwd 1.x (config `apps` + module federation) and the npwd v4 template (`RegisterExternalApp`).
- `references/apps-lb-phone.md` — `AddCustomApp`, `SendCustomAppMessage`, the functions lb-phone injects into the app page.
- `references/apps-qb-phone.md` — adding an app to qb-phone or a fork (z-phone): config, html container, js, NUI callbacks.
- `references/phone-frame.md` — building or fixing the phone itself: open/close, focus, KeepInput while walking, prop and animations, pause menu, death, vehicles, scaling.
- `references/foldable.md` — foldable phone UI: postures, cover/inner screens, hinge animation, layouts, state continuity, performance.
- `references/phone-design.md` — making it feel like a real phone (iOS/Android conventions adapted to FiveM), and which design skills to pair.

Related skills (ask before using, per the project rules): `mobile-ios-design`, `mobile-android-design`, `apple-design` (real-phone conventions), `fivem-menu-design` (NUI rules and checker this skill builds on), `fivem-react-nui`, `fivem-script`, `game-ui-ux`, `impeccable`, `make-interfaces-feel-better`, `fivem-security-audit`, `oxlib`, `oxmysql`, `fivem-animation` (custom phone animations).

## Workflow

### 1. Find out which phone
Ask, or look in the server's resources: `npwd`, `lb-phone`, `qb-phone`, `z-phone`, `qs-smartphone`, `gksphone`, … The app API is completely different per phone, so nothing else can start before this. If the server has no phone yet, use `references/choose-a-phone.md` — the free choice is npwd (any framework) or qb-phone/z-phone (QBCore/Qbox). Don't recommend paid phones; if the user already owns one, help them with its public app API.

### 2. App or whole phone?
| Want | Do |
|---|---|
| a new app (job app, shop, bank, gang, racing, dark web …) | write it against the phone's app API — `apps-npwd.md` / `apps-lb-phone.md` / `apps-qb-phone.md` |
| restyle the existing phone | theme options first (npwd and lb-phone have settings/themes); fork only if needed, keeping the licence (npwd GPL-3.0, qb-phone GPL-3.0, z-phone AGPL-3.0) |
| a foldable phone | a new frame or a fork of a free phone; `foldable.md` + `phone-frame.md` |
| a phone from scratch | `phone-frame.md` for the shell; plan the apps as separate modules from day one |

### 3. Design the app like a phone app
Follow `phone-design.md`: one task per screen, a header with back, a bottom tab bar for 3–5 sections, lists with clear rows, the host phone's theme (light/dark) and fonts. Use `mobile-ios-design` or `mobile-android-design` for platform details and `apple-design` for the motion/feel.

### 4. Build
- Data comes from the server (oxmysql), keyed by the player's citizenid; the page only displays it and sends intent. Prices, rewards, money moves and permission checks happen on the server — run `fivem-security-audit` thinking on every callback.
- Inside a host phone, don't fight the host: the phone owns focus, ESC, the prop and the animation. Your app only renders inside its frame and talks through its API.
- Keep the bundle small: one app shouldn't ship its own copy of React when the host provides it (npwd v4), and images should be small WebP.

### 5. Check
Run `python .claude/skills/fivem-phone/scripts/check_phone_app.py <resource>` (local, read-only, Python only). It detects the phone/app type and checks:
- lb-phone apps: re-adding on lb-phone restart, waiting for lb-phone to start, `ui`/icon paths that exist and are in `files`, identifier mismatches, components used before `componentsLoaded`.
- npwd v4: app id vs `__npwd_ext_<id>`, bundle in `files`, React marked external, `dependency 'npwd'`.
- npwd 1.x: federation exposes `./config`, `web/dist` shipped.
- qb-phone/forks: every app in `Config.PhoneApplications` has an `<app>-app` container, no duplicate slots.
- phone frames: prop deleted, model released, phone animation stopped, pause menu and death closing the phone, fixed-px phone frames, foldable hinge without `perspective`.
- plus all NUI menu checks from `fivem-menu-design` (focus release, `cb` always called, UI-trusted prices, CDNs, blur, infinite animations, …), adjusted so apps inside a host phone aren't blamed for the host's job.

Then test in game: open/close 10 times quickly, restart your app resource and the phone resource while open, die with the phone open, open it in a vehicle, pause menu with phone open, 1280×720 and 2560×1440, and for foldables fold/unfold in the middle of a task.

## Ground rules
- Server decides; the phone displays. Never trust amounts, prices, targets or job checks coming from the page.
- Free and open resources only; keep the original licence and credits when forking. Don't copy paid, escrowed or leaked phone code — write apps against the public API instead.
- Things not checked against a source are marked "unverified" in the references; verify those in game before relying on them.
- Ask before using the related skills, per CLAUDE.md. The checker script may run once this skill is approved.
