# Tools: usage and known quirks

Everything here was verified by reading each tool's source and running it on test resources (October 2026). All tools are free and MIT licensed.

## Contents
1. check_vehicle_resource.py (bundled)
2. fivem-vehicle-validator
3. fivem-handling-presets
4. fivem-joaat-hash
5. vehicleDebug (in-game)
6. muto-atlas /vehicle

---

## 1. check_vehicle_resource.py (bundled with this skill)

```
python .claude/skills/fivem-vehicle-mod/scripts/check_vehicle_resource.py <path> [more paths] [--json]
```

- `<path>` can be one resource or a folder of resources (e.g. `resources/[cars]`). Scanning the folder is what finds id collisions between resources.
- Python standard library only, read-only. Exit code 1 if any error.
- Messages are in Chinese with an English code, e.g. `HANDLING_ID_MISMATCH`.

| Code | Level | Meaning |
|---|---|---|
| DATA_FILE_NO_MATCH | error | a `data_file` path matches no file (typo or wrong case) |
| META_NOT_IN_FILES | error | a meta file exists but is not covered by `files {}` |
| META_NO_DATA_FILE | error | a meta file has no matching `data_file` type |
| XML_INVALID | error | meta file is not well-formed XML |
| YFT_MISSING | error | `modelName` has no `<model>.yft` |
| HANDLING_ID_MISMATCH | error | `handlingId` not found among `handlingName`s in the resource |
| NO_HANDLING_ID | error | vehicle has no `handlingId` |
| MODEL_DUPLICATE | error | same `modelName` in two resources |
| VARIATION_MODEL_UNKNOWN | error | carvariations entry for a model not in vehicles.meta |
| MODKIT_ID_DUPLICATE | error | two kits share a modkit id |
| SIREN_ID_DUPLICATE / LIGHT_ID_DUPLICATE | error | shared siren/light settings id |
| ASSET_OVER_48MIB | error | a .yft/.ytd/.ydr/.ydd using over 48 MiB of virtual or physical memory (RSC7 header) — FXServer says it WILL cause streaming issues |
| ASSET_OVER_16MIB | warn | virtual or physical memory over 16 MiB, decoded from the RSC7 header like FXServer does (falls back to file size for non-RSC files) — FXServer will print a size warning |
| DATA_FILE_INVALID_TYPE | warn | data_file type not in the Cfx list (e.g. `DLCTEXT_FILE`, `CARCONTENTUNLOCKS_FILE`) — ignored by FiveM |
| DATA_FILE_REFUSED | warn | `TEXTFILE_METAFILE` (dlctext.meta) — refused by FiveM |
| HANDLING_NAME_DUPLICATE | warn | same handlingName in two resources — last loaded wins |
| MODKIT_ID_RANGE | error | modkit id above 65535 |
| MODKIT_ID_LOW | info | modkit id below 1024 — may collide with vanilla; prefer ≥1024 |
| SIREN_ID_RANGE / LIGHT_ID_RANGE | error | siren/light settings id above 255 (one-byte field) |
| SIREN_LIGHTS_OVER_20 | warn | a siren setting with more than 20 lights (vanilla limit siren1–siren20; more needs the client-side SSLA, impossible on Enhanced) |
| SIREN_ID_UNDEFINED | info | carvariations `sirenSettings` points at an id no scanned carcols.meta defines — fine for vanilla ids, otherwise a typo or a missing resource |
| EMERGENCY_FLAGS | info | `VC_EMERGENCY` vehicle without `FLAG_LAW_ENFORCEMENT` / `FLAG_EMERGENCY_SERVICE` |
| NOT_RSC7 | warn | a .yft/.ytd/.ydr/.ydd under `stream/` doesn't start with the `RSC7` magic of Legacy resources — corrupt, placeholder, CodeWalker XML, or a misplaced Gen9 file |
| YFT_HI_MISSING | info | no `<model>_hi.yft` (only exported when the model has a Very High LOD) |
| YTD_MISSING | warn | `txdName` has no matching `.ytd` |
| KIT_NOT_DEFINED | warn | carvariations uses a kit not defined in this resource's carcols (fine if it's a vanilla kit) |
| LAYOUT_UNKNOWN | warn | layout not defined locally and not a vanilla `LAYOUT_*` name |
| NO_AUDIO | warn | empty `audioNameHash` |
| VEHICLES_META_SPARSE | warn | vehicles.meta entry lacks `layout`, `lodDistances`, `vehicleClass` or `type` |
| HANDLING_SPARSE | warn | a handling entry has fewer than 20 fields — copy a full vanilla entry instead |
| HANDLING_VANILLA | info | no handling.meta in the resource; only works if `handlingId` is a vanilla name |
| LEGACY_MANIFEST | warn | `__resource.lua` instead of `fxmanifest.lua` |

Limits: it does not open .yft/.ytd binaries (no poly counts, no texture formats), and it cannot know vanilla names, so a reference to a vanilla kit/layout/handling is reported as a warning or info, not an error.

## 2. fivem-vehicle-validator

```
npx -y fivem-vehicle-validator <resource>          # bin name: fivem-validate
npx -y fivem-vehicle-validator <resource> --json
```

Exit codes: 0 pass, 1 errors, 2 warnings only.

Checks (its 16 MB YTD "limit" is really FiveM's warning level, see performance-and-enhanced.md): fxmanifest exists, `fx_version` (cerulean/bodacious/adamant), `game 'gta5'`; vehicles.meta/handling.meta/carcols.meta/carvariations.meta listed in `files {}` and declared with the right `data_file` type; vehicles.meta has `modelName`, `txdName`, `handlingId`, `gameName` (warns on missing `vehicleMakeName`, `vehicleClass`, `type`, `audioNameHash`); duplicate modelNames within the file; handling.meta looks like handling XML and the first `fMass` (100–50000), `fInitialDragCoeff` (0.1–100), `fBrakeForce` (0.1–10), `nInitialDriveGears` (1–12) are in range; stream files exist; YTD >16 MB error, >12 MB warning; YFT without YTD; `_hi.yft` without base `.yft`; YFT >25 MB; total stream >50 MB; stream files in root, junk files (.bak, Thumbs.db…), nested fxmanifest, folder depth >5.

Known gaps and false results (verified):
- **Does not check `handlingId` against `handlingName`.** A resource with `handlingId MYCAR` and `handlingName MYCARX` passes, although the handling will not apply in game. The bundled script catches this.
- **False error with globs**: `files { 'data/**/*.meta' }` is valid FiveM, but the validator reports `MANIFEST_NO_VEHICLES_META` / `MANIFEST_META_NOT_IN_FILES`.
- Only reads the first `files {}` block, and only the first value of each handling field, so in a multi-car pack only the first car's handling is range-checked.
- No vehiclelayouts.meta, modkit id, siren id or cross-resource checks.

## 3. fivem-handling-presets

```
npx -y -p fivem-handling-presets fivem-handling list
npx -y -p fivem-handling-presets fivem-handling show <preset>
npx -y -p fivem-handling-presets fivem-handling apply <preset> <handling.meta> -o <output.meta>
```

Presets: street, drift, racing, offroad, realistic, muscle, lowrider, supercar, truck, motorcycle. Each is ~33 values (mass, drag, centre of mass, inertia, drive bias, gears, drive force, clutch, max flat vel, brakes, steering lock, traction, suspension, anti-roll, roll centre).

Quirks (verified):
- **Rewrites every car in the file.** The `handlingName` option in the docs is not implemented; the replacement is global. Apply it to a file containing only the one car, or copy values by hand.
- **Overwrites the input file unless `-o` is given.** Always use `-o`.
- Only replaces fields that already exist; missing fields are not added.
- "Fields not found in file" also lists fields whose value was already identical, so it doesn't necessarily mean the field is missing.

Treat presets as a starting point; they are generic and not tuned to the model's size or wheelbase.

## 4. fivem-joaat-hash

```
npx -y -p fivem-joaat-hash joaat <name> [name2 ...]     # e.g. adder -> 0xB779A091
npx -y -p fivem-joaat-hash joaat --reverse <name>       # is it a known vanilla vehicle?
npx -y -p fivem-joaat-hash joaat --decimal <name>
```

Same JOAAT hash as `GetHashKey()`. Use `--reverse` before choosing a spawn name to avoid replacing a vanilla car, and the plain form when a hash is needed (e.g. comparing against a log line or a script).

## 5. vehicleDebug (FiveM resource, github.com/kerminal/vehicleDebug)

- Install: put the folder in `resources/`, `ensure vehicleDebug`. Client-only resource with an NUI.
- Use: sit in the vehicle, press **Right Alt** (change `Config.Keybind` in `cl_config.lua`), edit any field; the change applies immediately (it calls `SetVehicleHandlingFloat/Int/Vector` and `ModifyVehicleTopSpeed(veh, 1.0)`). Top-centre shows top speed (mph) and arbitrary acceleration/deceleration peaks; "Reset Stats" clears them.
- Save: "Copy Handling" copies `<field value="..." />` lines for all editable fields (mass through monetary value). It does **not** include `<handlingName>` or SubHandlingData. Paste the lines over the matching fields inside the car's `<Item type="CHandlingData">`.
- Changes are client-side and per-vehicle-instance: other players don't see them and they are lost on respawn until pasted into handling.meta and the resource is restarted.
- `vehdebug` toggles the tool and is unrestricted by default. For anything but a private dev server, set `EnabledByDefault = false` and restrict the command (README: change the `false` in its `RegisterCommand` to `true` for ACE-only).
- Its tooltip for fInitialDriveMaxFlatVel says "multiply by 0-82 for mph"; that is a typo for 0.82.

## 6. muto-atlas `/vehicle`

- `/vehicle <name>` (or `python scripts/assetdb.py vehicle <name>`) — handlingId, modkit, extras, class, seats for 921 vanilla vehicles; `assetdb.py bones <model>` — the real skeleton.
- Vehicle bone names are fixed and 100% tag-stable (193 names: doors, windows, hood, wheels, lights, engine, exhaust, seats, mods, extras, sirens) — copy the name exactly.
- Requires the data layers built once with `/asset-setup` (GTA V + CodeWalker paths). Ask before running it the first time.
