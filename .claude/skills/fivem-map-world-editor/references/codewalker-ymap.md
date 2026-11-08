# CodeWalker and the ymap format

Contents: 1 setup · 2 projects and placing · 3 CEntityDef fields and flags · 4 CMapData and content flags · 5 LOD hierarchy and parentIndex · 6 custom HD/LOD chain · 7 car generators, timecycle boxes, grass, occluders, LOD lights · 8 Sollumz 2.9 ymaps · 9 saving, manifests, binary vs XML · 10 placements and dependencies

Citation keys are listed in [sources.md](sources.md). `[U]` = the user's own server incident or tool.

## 1. Setup

- Options → **Enable DLC**, DLC level = the newest entry (bottom; at least mpheist for any `hei_` file), **Save Settings** [D:cfx2]. The level must match the server's `sv_enforceGameBuild` (user: 3258) [V:tNRd5EZj0Oc 01:00]. Wrong level = you edit a copy that a newer DLC copy replaces in game [D:forum-cwfivem; V:vDYllxY7ReY 01:40].
- Keys: T toolbar, right-click select, E edit mode (W move, E rotate, R scale), Shift+drag on the gizmo duplicates, Ctrl+Z/Y [D:cw-readme, D:cfx4]. "Some options may cause CodeWalker to crash" [D:cw-readme].
- **Max LOD** dropdown (ORPHANHD / HD / LOD / SLOD1-4) shows one level at a time - the main tool for seeing what a building is made of [V:vDYllxY7ReY 04:20; V:tNRd5EZj0Oc 05:20].
- Selection modes: Entity, **Collision** (world `.ybn`), Car Generator, **Occluders** (blue = box, red = model) and more [D:cfx5; V:8r6KS9n2f7k 00:20]. Options → show collision meshes [V:vDYllxY7ReY 03:00].
- CodeWalker sometimes shows stale state: close and reopen the project to verify [V:vDYllxY7ReY 09:40]. One tutor says saving while another Max LOD level is shown "will corrupt its parent ymap file" - close and reopen CodeWalker between LOD levels (single claim, treat as caution) [V:D0bj_m5iEGA 00:40].
- Version: the user has v30_dev46 (`H:\Fivem modss\ZM3\1cfcd8-CodeWalker30_dev46`). The Sollumz Enhanced tutorial asks for dev48+ (unverified; Discord) [D:cw-g5m].

## 2. Projects and placing

1. File → New Project. With the project window open, editing a world entity adds its ymap to the project [D:cw-readme]; or right-click → Add to Project [V:vDYllxY7ReY 02:00].
2. New things go in a **new ymap** with your prefix (Project → New Ymap → New Entity), never appended to a vanilla ymap [V:vDYllxY7ReY 08:40].
3. Archetype field = any vanilla name or a custom one whose `.ytyp` CodeWalker has loaded (project or mods folder). If CodeWalker cannot load it, the entity draws nothing and **Calculate Extents falls back to a sphere of the entity radius** - near-zero extents, prop invisible in game [SRC:cw-extents].
4. Select the ymap → **Calculate Extents** + **Calculate All Flags** (or tick Project → Auto Calculate Ymap Extents / Flags) → Save [D:cfx4; SRC:cw-project]. Forgetting extents is the classic "not in game" [V:vDYllxY7ReY 16:00].
5. New custom archetypes: Tools → **Manifest Generator** with only the new ymaps open → save `<prefix>_manifest.ymf` into `stream/` [D:cfx4; V:vDYllxY7ReY 12:40]. Several resources each shipping a file literally called `_manifest.ymf` is common on this server; whether FiveM keeps all of them is undocumented - use a unique name (unverified risk).
6. Finding vanilla names: the selection panel, RPF Explorer search, `muto-atlas`, or the user's `find_archetypes.ps1` / `find_names.ps1`.

## 3. CEntityDef fields and flags

Fields: archetypeName, flags, guid, position, rotation (quaternion; Sollumz writes the inverse of the world rotation for CEntityDef but not for MLO instances [U:make_ymaps.py]), scaleXY, scaleZ, parentIndex, lodDist (≤ 0 → archetype lodDist), childLodDist, lodLevel, numChildren, priorityLevel (non-required levels may be skipped [D:sz-maps]), extensions, ambientOcclusionMultiplier, artificialAmbientOcclusion, tintValue.

Entity flags (CodeWalker EditYmapEntityPanel) [SRC:cw-flags]:

| Bit | Meaning | Bit | Meaning |
|---|---|---|---|
| 1 | Allow full rotation | 65536 | Underwater |
| 2 | Stream low priority | 131072 | Doesn't touch water |
| 4 | Disable embedded collisions | 262144 | Doesn't spawn peds |
| 8 | **LOD in parent map** | 524288 | Cast static shadows |
| 16 | LOD adopt me | 1048576 | Cast dynamic shadows |
| 32 | Static entity | 2097152 | Ignore time settings |
| 64 | Interior LOD | 4194304 / 8388608 | Don't render / only render shadows |
| 32768 | LOD use alt fade | 16777216 … 536870912 | reflection / water / mirror render switches |

Vanilla buildings: 1572864 (both shadow bits). HD with its LOD in another ymap: 1572888 (+8 +16) [spike on kt1_13]. Stumpy Mason's custom HD: 1572872 (+8) [V:m6H6tBL3CQ8 15:20].

lodLevel enum (binary values, checked against XML): 0 HD, 1 LOD, 2 SLOD1, 3 SLOD2, 4 SLOD3, 5 ORPHANHD, 6 SLOD4.

## 4. CMapData and content flags

Fields: name, parent (LOD ymap name), flags, contentFlags, streamingExtentsMin/Max, entitiesExtentsMin/Max, entities, containerLods, boxOccluders, occludeModels, physicsDictionaries, instancedData (grass), timeCycleModifiers, carGenerators, LODLightsSOA, DistantLODLightsSOA, block.

`flags`: 1 scripted (not loaded until `RequestIpl` [D:sz-maps]), 2 has LOD-level entities. `contentFlags` as CodeWalker CalcFlags computes them [SRC:cw-ymapflags]:

| Bit | Set when | Bit | Set when |
|---|---|---|---|
| 1 | HD / ORPHANHD entities | 64 | physics dictionaries (grass adds v_proc1/2) |
| 2 | LOD entities (+ flags 2) | 128 | LOD lights |
| 4 | SLOD2+ | 256 | distant LOD lights (+ flags 2) |
| 8 | MLO instance | 512 | critical (CalcFlags never sets it) |
| 16 | SLOD1+ | 1024 | grass batches |
| 32 | box or model occluders | | |

CalcFlags starts from 0, so **Calculate All Flags also clears `flags` 1 (scripted) and contentFlags 512** - re-set them on a scripted or critical ymap (Kiiya's MLO ymaps are scripted, flags 1). Checked: vanilla kt1_13 = flags 2 / contentFlags 18, kt1_lod = 20, occluder ymaps = 32, the user's MLO ymaps = 9. Extents: entitiesExtents = rotated archetype boxes × scale; streamingExtents = that ± lodDist [SRC:cw-extents] - a 1500 m lodDist makes a ~3 km streaming box that contains the map origin (the user's `lpt_t3.ymap`, flagged by the checker).

`name`: CodeWalker.Core leaves it 0 when you build a ymap by code without setting `Name` (all of the user's compiled La Puerta ymaps); those worked in game, but set it [U:occluders.ps1].

## 5. LOD hierarchy and parentIndex

HD → LOD → SLOD1 → SLOD2 → SLOD3 (→ SLOD4); ORPHANHD = HD with no parent. Vanilla files per block: `<area>_<block>_strm_N` (HD props), `_long_N` (HD with big lodDist), `<area>_<block>.ymap` (LOD + SLOD1, parent of strm/long), `<area>_lod.ymap` (SLOD2/3, parent of the block ymaps), `_critical_N`, `_milo_`, `*_grass_*`, `<area>_occl_NN`, `lodlights_*` / `distlodlights_*` [D:sz-maps; U:kt1 files].

**Where parentIndex points** (CodeWalker `YmapFile.cs` load loop ~line 312 + `ConnectToParent`, read 2026-11-08; the checker uses the same rule): the parent is in the **parent ymap** (CMapData `parent`) when flag 8 is set, when the index is past this ymap's own entity list, or when the entity at that index here is not a higher LOD level; otherwise in the same ymap. With this rule all 18 vanilla kt1 ymaps resolve with no bad index; vanilla `kt1_rd` holds 514 LOD + 63 SLOD1 that parent each other internally; the `bkr_id1_rd_long_0` copy in pio_cht has entities without flag 8 whose index (578) is past their own list (349) - they resolve into the parent ymap. The rule is CodeWalker's reading; the engine's exact rule is not documented (unverified).

- `numChildren` cannot be verified from a subset (children live in neighbouring ymaps) - only compare before/after.
- Deleting or reordering entities in a LOD/SLOD ymap shifts every later index; children in strm/long then show the wrong LOD. Kiiya's `kiiya_kt1_rd_veg.ymap` (on the user's server) has every tree's parentIndex one too high - the checker's `LOD_INDEX_SHIFTED`.

## 6. Custom HD → LOD → SLOD chain

Cfx part 6 [D:cfx6] and Stumpy Mason's numbers [V:m6H6tBL3CQ8 15:00-24:40]:

| ymap | entity | lodLevel | flags | parentIndex | lodDist / childLodDist | numChildren |
|---|---|---|---|---|---|---|
| `x.ymap` (parent = `x_lod`) | HD | HD | 1572872 (+8) | index in `x_lod`, 0-based | 50 / 0 | 0 |
| `x_lod.ymap` (parent = `x_slod`) | SLOD1 first (flag 16 adopt me), then LOD | LOD | | into `x_slod` | 100 / 50 (= HD lodDist) | 1 |
| `x_slod.ymap` | SLOD2 / SLOD3 | | | -1 at the top | 250-500 / 200 | |

Then `_manifest.ymf`. Drawable LOD switch distances (High/Med/Low/VLow on the drawable) are separate from entity lodDist, which ends visibility [V:m6H6tBL3CQ8 07:00-11:00]. Copy Rockstar's distances for similar objects [V:m6H6tBL3CQ8 24:40].

**Default for one building on this server: ORPHANHD, moderate lodDist, drawable LODs inside the model.** The user's La Puerta crash bisection ended with a standalone tower (no LOD parent) [U:ledger]; an HD+LOD pair without `.ymf` was the first suspect (Cfx says LOD setups need one).

## 7. Car generators, timecycle boxes, grass, occluders, LOD lights

- **Car generators**: position, orientX/Y, perpendicularLength, carModel (spawn name) or popGroup (model set), flags (1 force spawn, 2 ignore density, 4 police, 8 firetruck, 16 ambulance, 32 day, 64 night, 128/256 align, …), livery, body colour remaps [SRC:cw-cargen]. CarModel 0 + empty popGroup = random fitting vehicle; police-station gens keep spawning police cars on a server → delete them; copy flags from a reliable vanilla gen; move gens so trucks do not clip into new builds [V:FqZ1OuHfNoM]. `qbx_density` on the user's server overrides 23 vanilla strm ymaps only to disable car gens - another map editing those files collides with it.
- **Timecycle modifiers**: box + modifier name (vanilla or from `data_file 'TIMECYCLEMOD_FILE'`), percentage, range, hours [D:sz-maps; D:datafiles]. Remove vanilla ones over a cleared site [U:strip_vanilla_site].
- **Grass**: instanced batches (contentFlags 1024); CodeWalker Tools → Delete Grass (bulk since v30_dev44) [D:cw-g5m]. FurGrass and `ma@` procedural grass are invisible in CodeWalker [D:sz-faq] - grass through a new floor = batch and/or the `ma@` collision material.
- **Occluders**: boxes and triangle models in `*_occl_*` ymaps (contentFlags 32). Removing a building does not remove them [U:vanilla-occluders; V:ADe_gczZUQw 05:40]. New ones: Sollumz map data, Box Occluder or Model Occluder Group/Model, ymap name with `_occl` (tutor says required; unverified, vanilla always uses it) [V:8r6KS9n2f7k 05:00]. Never make an occluder larger than the solid wall it stands for.
- **LOD lights**: `lodlights_*` (child) + `distlodlights_*` (parent) ymaps; Sollumz "Bake LOD Lights" builds both [D:sz-maps]. Removing a lit vanilla building leaves its distant lights (video, from chapter titles, unverified) [V:ecpZsF8aJWc]. On the user's server `molo_lspdhq` and `kiiya_lapuerta` both ship `vw_lodlights_medium015.ymap` / `vw_distlodlights_medium015.ymap` - one silently wins.

## 8. Sollumz 2.9 ymaps

Sollumz imports/exports ymaps: map groups → containers (container hierarchy = ymap LOD hierarchy, one ymap per container) → entities, car generators, timecycle modifiers, grass batches, occluders, LOD lights [D:sz-maps]. Items outside a container are skipped on export. **Containers with missing LOD parents or children are locked** (entities cannot be deleted) - import the whole chain (strm + block + `_lod`) before deleting. Auto-partitioning splits like vanilla (strm, long, critical, milo, grass). Grass generation nodes need Blender 5.0+. Sollumz does not edit ynd, ynv or water [D:sz-features].

## 9. Saving, manifests, binary vs XML

- CodeWalker saves binary. XML round trip: RPF Explorer Export/Import XML, or CodeWalker.Core in PowerShell (user's `compile_ymaps.ps1`: XmlMeta → YmapFile → optional CalcFlags → Save → reload and compare counts) [U].
- `stream/` holds binaries only; an `.xml` in `stream/` is never loaded.
- `_manifest.ymf` is binary (starts `PSIN`). It carries ytyp dependencies, `HDTxdBindingArray` for custom `+hi` texture dictionaries [D:sz-tex] and MLO interior data (`fivem-mlo-housing`).
- `this_is_a_map 'yes'` reloads the map store when the resource loads [D:manifest]. Resources that only override vanilla files often work without it (qbx_density, bob74_ipl on this server); new ymaps should have it.
- After editing: restart the resource / server and reconnect; live map changes do not hot-reload; clear the cache if needed [D:forum-removed]. `save_gta_cache <resource>` can pre-build map + collision cache [D:console].

## 10. Placements and dependencies

Resolve ymap entity → ytyp archetype → drawable + texture dictionary → collision. Include base-game/DLC and minimum-build dependencies. Duplicate names across resources load last-wins, which is not compatibility. Do not create archetypes for stock props. A visible ramp is not driveable until its collision exists; a road mesh does not create traffic (paths: [terrain-roads-water-paths.md](terrain-roads-water-paths.md)). Distinguish streamed static placements from scripted networked objects: overlapping spawns can look like z-fighting.
