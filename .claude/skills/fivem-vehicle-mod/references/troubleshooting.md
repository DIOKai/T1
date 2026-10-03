# Troubleshooting: symptom → cause → fix

Always start with: the **server console** after `ensure <resource>` (size warnings, errors), the **client F8 console / CitizenFX log** (data_file and handling messages), and `check_vehicle_resource.py`.

| Symptom | Likely cause | Check / fix |
|---|---|---|
| Car won't spawn / "model doesn't exist" | vehicles.meta not mounted (missing from `files {}` or no `VEHICLE_METADATA_FILE`); `modelName` ≠ .yft name; .yft not under `stream/`; same model in two resources | cross-check script (`META_NOT_IN_FILES`, `META_NO_DATA_FILE`, `YFT_MISSING`, `MODEL_DUPLICATE`) |
| Drives like an Adder / handling.meta ignored | `handlingId` ≠ `handlingName` → client log `Couldn't find handling for hash … returning ADDER instead!`; `HANDLING_FILE` missing; another resource loads the same handlingName later (last loaded wins) | `HANDLING_ID_MISMATCH`, `HANDLING_NAME_DUPLICATE`; restart resource and respawn |
| A meta file seems ignored | wrong data_file type (`DLCTEXT_FILE`, `CARCONTENTUNLOCKS_FILE`, typo) → log `Could not add data_file … invalid type`; `TEXTFILE_METAFILE` is refused by design | `DATA_FILE_INVALID_TYPE`, `DATA_FILE_REFUSED`, `DATA_FILE_NO_MATCH` |
| Invisible car / white or missing textures | .ytd missing or `txdName` mismatch; bad txdRelationships parent; oversized assets | `YTD_MISSING`; server console size warnings; compress textures |
| Textures vanish when many cars around ("texture loss") | streaming memory exhausted by heavy add-ons | `references/performance-and-enhanced.md` — compress, split `+hi.ytd`, fewer heavy cars |
| Car disappears or pops at distance | missing LOD levels; odd `lodDistances` | export L0–L3; copy vanilla lodDistances |
| Wheels missing, wrong or not turning | wheel meshes not on the fixed bones `wheel_lf/rf/lr/rr` (the game copies the LF wheel to the others) | bone names via muto-atlas `/vehicle`; `wheelScale` doesn't resize the tyre |
| Doors / bonnet / boot won't open | bones not named exactly `door_dside_f`, `door_pside_f`, `door_dside_r`, `door_pside_r`, `bonnet`, `boot`; bone has no physics group with collision (Sollumz warns "Bone … has physics enabled, but no associated collision!") | fix names and physics/collision in Sollumz |
| Glass doesn't shatter | window mesh not using `VEHICLE VEHGLASS` shader, or no physics child / bone link | Sollumz window setup (shattermap mode AUTO needs PyMateria) |
| Lights don't work (head/tail/indicators) | light ids not set in vertex colour alpha (Sollumz: 1–2 head, 3–4 tail, 5–8 indicators, 9–11 brake, 12–13 reverse, 14–17 extras, 0 = always on) | set light ids in Sollumz |
| No engine sound / wrong sound | `audioNameHash` doesn't match a loaded bank; audio data_file paths wrong (drop the number suffix and `.rel`); `.rel`/`.awc` missing from `files {}` | `references/resource-and-meta.md` §9; quick fix: a vanilla car name |
| Tuning menu empty / shows another car's parts / floating parts | modkit id collision; carvariations `<kits>` ≠ carcols `kitName`; script didn't call `SetVehicleModKit(veh, 0)` | `MODKIT_ID_DUPLICATE`, `KIT_NOT_DEFINED`; use ids ≥ 1024 |
| Wrong siren pattern / wrong light colours | siren or light settings id shared with another resource, or > 255 | `SIREN_ID_DUPLICATE`, `LIGHT_ID_DUPLICATE`, `*_RANGE` |
| Siren lights don't flash at all | carvariations `sirenSettings` 0 or pointing at a missing id; no `siren1…` bones on the model | `SIREN_ID_UNDEFINED`; check bones with muto-atlas `/vehicle`; `references/police-emergency.md` |
| Some siren lights dead | more `<sirens>` items than siren bones, or > 20 lights | match bone count; `SIREN_LIGHTS_OVER_20` |
| Siren sound wrong, unsynced or goes silent | vanilla siren not muted by the controller; tone names not configured for the model; another script leaking `GetSoundId()` without `ReleaseSoundId()` | configure the model in the siren controller (Renewed-Sirensync `config.lua`); find the leaking script |
| Extra 10 never appears | bone named `extra_10` instead of `extra_ten` | rename the bone |
| Extras on/off reversed in a script | `SetVehicleExtra`'s third argument means **disable** | pass `false` to turn on, or use `qbx.setVehicleExtra(veh, id, enable)` |
| Livery button does nothing | `FLAG_HAS_LIVERY` missing (texture method) or livery parts not in a `VMT_LIVERY_MOD` kit (modkit method) | `references/modkits-liveries-sirens.md` |
| Name shows as NULL / label key | no `AddTextEntry` for `gameName` / `vehicleMakeName` / `modShopLabel` | `vehicle_names.lua` |
| Enhanced client: car broken, Legacy fine | assets not converted, or both `stream/` and `stream_enhanced/` exist (Enhanced uses only `stream_enhanced`) | convert with Alchemist or Sollumz Gen9 export |
| Enhanced client freezes at 100% loading | open issue with FXServer b157 data_file mounts (report #567, 2026-10-01) | try the previous server build; check rfc discussions |
