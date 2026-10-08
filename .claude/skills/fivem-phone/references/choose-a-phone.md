# Choosing a phone

Checked against each project's repository (commit dates in brackets). Prices and features of paid phones change. Treat anything not taken from a repository as unverified.

| Phone | Licence / price | Framework | Stack | How apps plug in |
|---|---|---|---|---|
| **npwd** (project-error/npwd, master = v3.16.0 [2025-03]) | GPL-3.0, free | framework-agnostic (bridges for QBCore/ESX/standalone; Qbox through its QB bridge, unverified) | React + TypeScript (Vite), TS game scripts | external app **resources** loaded at runtime: 3.x uses module federation listed in npwd's `config.json` → `"apps"`; a newer **v4 template** uses `exports.npwd:RegisterExternalApp` → see `apps-npwd.md` |
| **qb-phone** (qbcore-framework/qb-phone [2026-08]) | GPL-3.0, free | QBCore (Qbox via qb bridge, unverified) | jQuery + plain HTML/CSS/JS, Lua | no plug-in API: you **edit the phone** (config + html + js + Lua) → `apps-qb-phone.md` |
| **z-phone** (Z3MO/z-phone [2026-04]) | AGPL-3.0, free | QBCore, Qbox (`Config.Framework = 'auto'`), ox_inventory/ox_target/ox_lib optional | qb-phone fork, redesigned dark/glass UI | same as qb-phone (edit the fork) |
| **lb-phone** | **paid**, escrowed | QBCore, Qbox, ESX, … | closed | public custom-app API: `exports["lb-phone"]:AddCustomApp` with your own UI page; MIT app templates (lb-phone-app-template: vanilla JS, React JS/TS, Vue) → `apps-lb-phone.md` |
| own phone | yours | any | any | you design the app system → `phone-frame.md` |

Dependencies seen in the manifests/READMEs:
- npwd: `screenshot-basic`, `pma-voice` (fxmanifest `dependency`), a database (oxmysql/mysql-async per its install docs, unverified), and an image host for photos (`config.json` → `images`, default fivemanage; pick a free tier or self-hosted option and tell the user if a host needs payment).
- qb-phone: `qb-core`, `screenshot-basic`, optional qb-policejob, qb-crypto, qb-lapraces, qb-houses, qb-garages, qb-banking; its shared scripts load `@qb-apartments/config.lua`; its page loads jQuery, Bootstrap, moment, DOMPurify and more from CDNs.
- z-phone: `screenshot-basic`, `@ox_lib/init.lua`, and `@z-garages/config.lua` in shared scripts (comment it out without z-garages, per its manifest).

## Recommendation logic

- The user already runs one → write apps for that one. Don't suggest switching phones just to add an app.
- New server, any framework, wants modern React apps → **npwd**.
- QBCore/Qbox server that wants a simple phone it can edit freely in plain JS → **qb-phone**, or **z-phone** for a more modern look plus Qbox/ox support (AGPL: if you modify it and players use it, share your modified source).
- The user already bought lb-phone → its app API is good and documented. Don't recommend buying it, since the project rules say no paid tools.
- Foldable phone → none of the free phones fold out of the box. Fork npwd or qb-phone/z-phone and add a fold state to the frame (`foldable.md`), or build a new frame.

## Licences in practice

- GPL-3.0 (npwd, qb-phone): a modified version you distribute must stay GPL-3.0 with source available. Sending the resource to players' clients is generally treated as distribution in the FiveM community. That is not legal advice: tell the user to read the licence.
- AGPL-3.0 (z-phone): also covers network use. Share modified source.
- An app you write as a **separate resource** that talks to npwd or lb-phone through exports/events is your own code, and you choose its licence. Copying code out of the phone into the app brings the phone's licence along.
- lb-phone's templates are MIT. lb-phone itself is escrowed: never decompile it or use leaked copies.
