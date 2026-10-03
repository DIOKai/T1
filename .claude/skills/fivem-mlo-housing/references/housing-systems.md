# Housing systems

All free. Facts below come from each project's repository (README, config, source) at the time of research.

| Script | Framework | Interiors | Licence | Status |
|---|---|---|---|---|
| **qbx_properties** | Qbox | shells + IPL apartments; MLO support listed as a todo | GPL-3.0 | maintained (Qbox project) |
| qb-houses + qb-apartments + qb-interior | QBCore | shells (qb-interior streams K4MB1 starter shells) + apartments | GPL-3.0 | maintained (QBCore) |
| ps-housing | QBCore / Qbox | shells, IPL, MLO ("IPL & MLO Support") with furniture | **CC BY-NC-SA 4.0** — no commercial use | archived by Project Sloth |
| bob74_ipl | any | vanilla interiors and entity sets (not a housing system) | MIT | maintained |

Paid systems (bcs_housing, qs-housing, nolag_properties, …) are out.

## qbx_properties (recommended on Qbox)

- Install: remove `qbx_apartments` and `qbx_houses`; use `qbx_spawn` or no spawn selector; import `property.sql`, `property_garages.sql`, `decorations.sql`; needs ox_lib, ox_inventory (stashes) and the shell resource for any shell you use.
- `config/shared.lua`:
  - `shellUndergroundOffset = 50.0` — shells spawn this far **below the property's own entrance**, so every house has its own space without routing buckets.
  - `apartmentOptions` — starter apartments (`interior`, `label`, `description`, `enter`).
  - `interiors` — keyed either by a **shell model hash** (`` [`furnitured_midapart`] ``) with coordinates **relative to the shell** (`firstspawn`, `exit`, `clothing`, `stash`, `logout`), or by an **IPL apartment name** (`'4IntegrityWayApt28'`) with absolute coordinates.
- Built-in decorating (gizmo), stashes via `exports.ox_inventory:RegisterStash`, realtor tooling.
- Adding a shell: stream the shell model (with its `.ytyp` / `_manifest.ymf`), add an `interiors` entry with offsets measured inside the shell.

## QBCore: qb-houses / qb-apartments / qb-interior

- qb-interior streams shell `.ydr`s (container, furnished mid apartment, Franklin's aunt, Lester, Michael, garage, modern hotel…) and exports `CreateShell(spawn, exitXYZH, model)` plus helpers such as `CreateFurniMid`, `CreateLesterShell`; it spawns the shell, freezes it and teleports the player to `spawn + exit offset`.
- qb-houses uses those exports for owned houses; qb-apartments for starter apartments.
- Add shells by streaming the model in a resource and calling `CreateShell` with your offsets.

## ps-housing

Full-featured (realtor job, furniture catalogue with limits, raids with `police_stormram`, keys, garages, migration commands from qb-houses/qb-apartments), but archived and **non-commercial**. Only suggest it if the user's server earns nothing (no Tebex, no paid priority) and accepts no updates. Its `Config.Shells` maps a label to `hash` and `doorOffset`; the special `"mlo"` entry handles MLO/IPL properties.

## Shell vs IPL vs MLO for houses

| Need | Use |
|---|---|
| many player houses, cheap | shells (K4MB1 free starter shells come with qb-interior; other free shells exist — check licences) |
| nice starter apartments | IPL apartments (qbx_properties `apartmentOptions`, bob74_ipl) |
| a specific house players walk into from the street | MLO + a housing script that supports MLO/IPL properties (ps-housing's `mlo`, or custom logic: doors via door-lock, stash/wardrobe zones via ox_target) |

## Design notes (for NoPixel-style housing)

- Server-authoritative everything: ownership, prices, keys, furniture counts and positions are validated server-side; the client only renders.
- Furniture: store model, position, rotation per property in the database; spawn locally when the player enters; cap count per property (performance and abuse).
- Keys: owner + shared key list; police raid needs a job/grade check and an item, logged.
- Stashes per property (`ox_inventory` stash id with the property id), wardrobe via the clothing resource.
- Test with several players entering different and the same properties at once.
