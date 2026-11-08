# Packaging, loading and placing props

## Two manifest patterns

**Spawn-only prop library** (props created by scripts, emote props):

```lua
fx_version 'cerulean'
game 'gta5'
data_file 'DLC_ITYP_REQUEST' 'stream/ha_props.ytyp'
```

**Map that places props** (ymap in `stream/`):

```lua
fx_version 'cerulean'
game 'gta5'
this_is_a_map 'yes'
data_file 'DLC_ITYP_REQUEST' 'stream/ha_props.ytyp'   -- only if scripts also spawn them
```

plus `stream/_manifest.ymf` from CodeWalker Tools > Manifest Generator (Cfx part 4: ymaps that place custom props need it; it also carries HD texture bindings).

- Game binaries go in `stream/` (any depth). Legacy + Enhanced: when `stream_enhanced/` exists, Enhanced loads it **instead of** `stream/` (Cfx legacy-vs-enhanced); put every file the Enhanced build needs there.
- `files {}` is not needed for streamed files. `lua54 'yes'` in the Cfx part 4 example is deprecated (resource-manifest page) and harmless.
- Lowercase names, no spaces; one name per model across the whole server — two resources streaming the same file name means only one wins.

## DLC_ITYP_REQUEST (verified in FiveM source)

`code/components/gta-streaming-five/src/LoadStreamingFile.cpp`, `CfxProxyItypMounter::LoadDataFile` → `ParseBaseName` (text after the last `/`, cut at the last `.`) → `FindSlot` in the ytyp streaming module. So:
- Only the file stem counts. Upstream rpemotes-reborn declares `stream/brummie_props.ytyp` while the file is at `stream/[Props]/Brummiee/brummie_props.ytyp` — works. `stream/prideprops_ytyp` (no extension) finds `prideprops_ytyp.ytyp`.
- The ytyp must be streamed by some running resource; the path you write is ignored.
- Globs are allowed in `data_file` (resource-manifest doc), but a glob that matches no file loads nothing. The user's cylex_animmenuv2 has `stream/[Props]/*ytyp.` (should be `*.ytyp`) — every ytyp it was meant to cover is unrequested. How DLC_ITYP_REQUEST treats glob results is **unverified**; listing files explicitly is safest.
- Equivalent of `PERMANENT_ITYP_FILE` (data-files doc). Fine for prop ytyps. **Never** request an MLO ytyp on this server — it crashed clients; the `.ymf` loads MLO ytyps (fivem-mlo-housing). The user's `pillbox` resource requests `v_int_40.ytyp`, which holds an MLO archetype — flagged by the checker (not changed).

## this_is_a_map

FiveM `code/components/citizen-resources-gta/src/ResourcesTest.cpp`: `this_is_a_map` only adds the pseudo entry `RELOAD_MAP_STORE` (the map store = ymaps). A resource with ymaps needs it; a spawn-only library does not (harmless if present — the user's wood_table resources have it).

## Placing

- **Script**: `lib.requestModel(model)` / `RequestModel` → `CreateObject(model, x, y, z, isNetwork, netMissionEntity, doorFlag)` (offsets by model radius on Z) or `CreateObjectNoOffset` (centred) → `PlaceObjectOnGroundProperly` → `SetModelAsNoLongerNeeded`. `isNetwork = false` = only this client sees it. `FreezeEntityPosition` for script props that must not move. The user's `hai_proptest` resource (`/haiprop <model>`) spawns a local copy for testing.
- **ox_target**: `exports.ox_target:addModel({ 'name' }, options)` for every instance; `addLocalEntity` for spawned ones (ox-target skill).
- **ymap** (Cfx part 4): CodeWalker project → New Ymap → New Entity → Archetype = name → place → **Calculate Extents** + **Calculate All Flags** → Manifest Generator. Entity flags worth knowing (Sollumz EntityFlags): Allow full rotation, Static entity, Disable embedded collisions, LOD in Parented YMAP, Cast Static/Dynamic Shadows, Ignore Day Night Settings; LOD level ORPHANHD for single props.

## Escrow and bought props

Cfx Asset Escrow protects Lua, YFT, YDD and YDR (not YTD/YCD/YTYP). Escrowed resources have a `.fxap` file and their protected stream files start with `FXAP` instead of `RSC7` (seen on the user's disk, read-only). They run only on a server key with the entitlement ("You lack the required entitlement" otherwise). Contents, size and LODs cannot be checked; never try to decrypt. `escrow_ignore {}` lists files left plain. Bought props: follow `fivem-authorized-asset-workflow` (back up originals, convert 1:1).
