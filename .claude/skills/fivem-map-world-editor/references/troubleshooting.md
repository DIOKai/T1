# Troubleshooting and acceptance

Contents: 1 symptom → cause → fix · 2 crash bisection · 3 in-game acceptance tests · 4 checker usage · 5 checker codes · 6 findings on the user's server (2026-11-08)

Citation keys: [sources.md](sources.md).

## 1. Symptom → cause → fix

| Symptom | Likely causes (most common first) | Fix |
|---|---|---|
| Prop/building fine in CodeWalker, missing in game | extents not calculated (all 0) [V:vDYllxY7ReY 16:00]; ytyp not loaded (no `.ymf` / DLC_ITYP_REQUEST) [D:cfx4]; archetype typo; Calculate Extents run while CodeWalker could not load the archetype (tiny sphere) [SRC:cw-extents]; lodDist tiny; resource not ensured / not restarted | recalc with the ytyp loaded; manifest; restart + reconnect |
| Model invisible even in CodeWalker | UV / colour attribute names not Sollumz convention [D:sz-faq]; missing txd | fix names, embed or ship the ytd |
| Removed thing still there | another resource ships the same ymap (later wins); edited base not `hei_`/newer DLC copy; old cache; object lives in a road/neighbour ymap [D:forum-cwfivem; D:forum-removed; U:strip_vanilla_roadprops] | search all resources; edit `hei_`; clear cache; check `<area>_rd_*` |
| Removed thing comes back at distance | LOD / SLOD1 entity left [D:forum-removeprops]; beyond ~750 m SLOD2/3 merged mesh [V:D0bj_m5iEGA 04:20; U:ledger] | bury LOD too; SLOD needs mesh edit |
| From some spots the world behind is missing (sky, black dots) | occluder of the removed building still in `*_occl_*` [U:vanilla-occluders; V:ADe_gczZUQw 05:40]; camera inside an MLO room through glass [U:ledger]; duplicate occl ymaps [D:forum-collfinder] | cut occluders (base + hei_); MLO portals |
| Flicker, z-fighting, floating props, MLO holes | two resources ship the same ymap/occl ("ymaps are almost always the cause of flickering") [D:forum-collfinder; V:gWvvGdzO8Ak; V:WMek-S1QU_I]; duplicate entities (`DUPLICATE_ENTITY`); coplanar faces; scripted object over a static one | merge into one file in one resource |
| Invisible wall / bullets stop in empty air | world ybn of the removed building (plain or `hi@`) [V:vDYllxY7ReY 02:40; V:tNRd5EZj0Oc 17:00] | cut the ybn copies |
| Fall through new ground / no collision | BVH without flag preset; collision in local coordinates; no ybn shipped [D:sz-faq; D:sz-ybn] | flag preset, world coords |
| Wrong tree/LOD pops at the wrong place | parentIndex shifted after deleting in a LOD ymap (`LOD_INDEX_SHIFTED`, Kiiya veg) | remap indices or restore |
| Cars spawn inside the new build | vanilla car generators left [V:FqZ1OuHfNoM 02:00] | delete/move car gens |
| Grass through the floor | grass batch or `ma@` procedural material [D:sz-faq] | Delete Grass tool; edit `ma@` |
| Props glow pink at night | no vertex colours [D:sz-faq] | paint (red outdoors) |
| Striped / stepped textures on big meshes | |UV| too large (half floats) [U] | recentre UVs |
| Whole map stutters on join | huge streaming extents (lodDist 1500+), oversized textures (16/48 MiB) [U:ledger; D:console] | smaller lodDist; split ytd |
| Demo spawn maps start | `[maps]` category name clash with `[cfx-default]\[maps]` [U:server-layout] | rename category |
| Crash near the map | MLO packaging (see `fivem-mlo-housing`), oversized assets, bad LOD indices (suspected) | bisect (section 2) |

Tools: `strdbg` (what streams now), `strlist`, `strmem`, `resmon`, `cl_drawperf` (dev mode), `save_gta_cache <resource>` [D:console]. Live edits don't hot-reload: restart, reconnect, clear cache [D:forum-removed].

## 2. Crash bisection

Move half of the suspect resources to `txData\…\disabled_resources` (comment their ensure lines), restart, test, halve again [U:2026-10-14]. On the user's server the crash was MLO packaging, not the vanilla overrides; an HD+LOD pair without `.ymf` was the first suspect and the tower ended standalone (ORPHANHD, no LOD parent). Note the crash address from the client log.

## 3. In-game acceptance tests

Choose exact coordinates and routes; log the resource set (each map alone, then all together) and the build.

| Check | Test | Pass |
|---|---|---|
| References | fresh-join with only this resource | everything visible, no F8 warnings |
| Placement | visit boundaries, road ties, entrances | nothing floats, no gaps, nothing intersects (LESSONS: no floating parts) |
| Collision | walk, drive both ways, shoot walls and ground | no falls, invisible walls, wheel sink; bullets hit real geometry |
| Streaming | approach from four directions at walking and driving speed | nothing pops in late or missing |
| LOD | look from 100 m, 300 m, 750 m, 1.5 km, by air | no old building, no double silhouette, smooth switches |
| Occlusion | stand on the site, turn 360°; orbit the new build | city always drawn |
| Lights | same views at night | no orphan lights, emissives on |
| Traffic / peds | wait 10 min near new roads and builds | no cars inside builds, peds path sensibly |
| Lifecycle | `restart <res>`, cold join | same result, no duplicates |
| Compatibility | this resource alone vs full server | differences traced to file names |
| Multiplayer | two clients | same world for both |

Viewer-only checks (CodeWalker) never prove gameplay, navigation or multiplayer. Mark unrun checks.

## 4. Checker usage

```
py -3 -I .claude/skills/fivem-map-world-editor/scripts/check_map_resource.py <paths...> [--xml DIR] [--orig DIR] [--vanilla-list FILE] [--names FILE] [--json]
```

- A whole server resources folder in one run (~1.5 s on the user's server) gives the cross-resource checks. Resources without map files (vehicles, clothing, texture packs) only take part in duplicate-name checks.
- Compiled ymaps are decoded directly; XML adds ybn/ydr/ynd checks and is required for `--orig` (the original side).
- `--vanilla-list`: names of real game files (one per line) → exact `VANILLA_OVERRIDE` / `HEI_PAIR_MISSING`; without it, names are guessed from patterns (`kt1_13_strm_0`, `hei_`, `v_`, `prop_`, …).
- `fivem-asset-acceptance`'s `asset_gate.py` runs it (and the MLO checker) for every resource it classifies as map/MLO.
- Not checked: binary ybn content, occluder geometry (only ymap extents), ytyp `CTimeArchetypeDef` (night-only archetypes - archetype checks are skipped for that resource), anything in escrowed (FXAP) files, behaviour in game.

## 5. Checker codes

| Code | Level | Meaning → fix |
|---|---|---|
| NO_THIS_IS_A_MAP | warn | map files in stream, no `this_is_a_map 'yes'` |
| XML_IN_STREAM | error | XML is never loaded from stream → convert |
| NOT_RSC7 / YMF_IS_XML | warn | not a compiled file / text `.ymf` |
| ASSET_OVER_16MIB / 48MIB | warn / error | FXServer limits from the RSC header |
| YTYP_NOT_LOADED | warn | custom ytyp with no `.ymf` and no DLC_ITYP_REQUEST |
| WATER_XML_NOT_LOADED / TIMECYCLE_NOT_DECLARED | warn | not in `files{}` + `LoadWaterFromPath` / no TIMECYCLEMOD_FILE |
| HD_TXD_PRESENT | info | custom `+hi` dictionaries need HDTxdBindingArray |
| YND_NAME / YNV_NAME / YND_AREA_MISMATCH | warn / info / warn | path file names, node areas |
| YBN_SIBLINGS | info | vanilla collision overridden without its `hi@` / `ma@` |
| MLO_HERE | info | run `check_mlo_resource.py` too |
| ZERO_EXTENTS | error | Calculate Extents not run |
| EXTENTS_DONT_COVER | warn | HD entity > 50 m outside entitiesExtents, or entities outside streaming box |
| HUGE_STREAMING_EXTENTS | warn | custom HD-only ymap wider than 4 km, or > 1 km and covering the map origin |
| FLAGS_MISMATCH | warn / info | differs from CodeWalker CalcFlags (warn when bits are missing) |
| YMAP_NAME_EMPTY / YMAP_NAME_MISMATCH | info / warn | CMapData name 0 / not the file name |
| LOD_INDEX_OUT_OF_RANGE | error | parentIndex past the target ymap's list |
| LOD_RANK | error | parent not a higher LOD level |
| LOD_NO_PARENT_MAP | warn | index points at a same-level entity and no parent ymap is set |
| LOD_INDEX_SHIFTED | error | most children point ±1/2 away from a parent sitting on them |
| LOD_FLAG_WITHOUT_PARENT | warn / info | ORPHANHD with a parent; flag 8 with parentIndex −1 |
| LOD_PARENT_MISSING | info | parent ymap not in the run (normal for vanilla parents) |
| LOD_DIST_SUSPICIOUS | warn | HD lodDist > 1500; childLodDist > lodDist |
| DUPLICATE_ENTITY | warn | same archetype at the same spot twice (X vs `hei_X` excluded) |
| CUSTOM_LOD_NO_MANIFEST | warn | custom HD/LOD pair without `.ymf` |
| CUSTOM_MODEL_NO_ARCHETYPE | warn | resource's own model placed but no local archetype |
| ARCHETYPE_NOT_LOCAL | info | archetypes not in local ytyps (vanilla is fine) |
| DUPLICATE_STREAM_FILE | error / warn | same file in two resources (ymap/ybn/ytyp/ynd/ynv/minimap = error; `.ymf`, models, textures = warn) |
| VANILLA_OVERRIDE | info | which vanilla files each resource owns |
| HEI_PAIR_MISSING | warn / info | base without `hei_` (warn with --vanilla-list) / `hei_` only (fine for FiveM) |
| OCCLUDER_CHECK | info | area ymaps overridden but no `*_occl_*` override anywhere |
| CATEGORY_NAME_CLASH | warn | two `[category]` folders with one name |
| BVH_TOO_MANY_POLYS / BVH_NO_FLAGS / YBN_EMPTY | warn / error / warn | ybn XML |
| UV_TOO_LARGE / NO_VERTEX_COLOUR / TEXTURE_SIZE | warn / info / warn | ydr XML |
| DIFF_SUMMARY | info | removed / buried / moved / added per ymap (`--orig`) |
| REMOVED_HAS_LOD_CHILDREN | error | deleted parent, children still there |
| INDEX_SHIFT | error | child now points to a different parent than in vanilla |
| NUMCHILDREN_STALE | warn | parent lost children, numChildren unchanged |
| LOD_LEFT_BEHIND | warn | all children gone, LOD still in place |
| OCCLUDER_NOT_EDITED | warn | no occluder ymap override covers the cleared area |
| COLLISION_NOT_EDITED | info | no ybn override for the block |
| CARGEN_IN_REMOVED_AREA / TCMOD_IN_REMOVED_AREA | warn / info | car gens / timecycle boxes left in the cleared area |
| HEI_EDIT_DIFFERS | warn | base and `hei_` edited differently, or `hei_` not edited |
| SLOD_REMINDER | info | far SLOD meshes still show the building |
| XML_INVALID / YMAP_UNREADABLE / ORIG_EMPTY / ORIG_NO_MATCH | error / info / warn / warn | input problems |

## 6. Findings on the user's server (2026-11-08, read-only run)

Whole `resources` folder (~1.5 s): 8 errors, 32 warnings, 210 notes. Map-relevant:
- **kiiya_lapuerta** `kiiya_kt1_rd_veg.ymap`: 44 of 52 trees have parentIndex +1 (HD #0 sits exactly on LOD #0 but points to LOD #1, 130 m away; the last tree points past the list) → LODs swap at the wrong trees. Paid resource: report to the author or fix a local copy. Also `kiiya_kt1_rd_apt_ext.ymap`: 12 HD entities point at other HD entities with no parent ymap (`LOD_NO_PARENT_MAP`); two `.xml` texture files left in `stream/`.
- **molo_lspdhq ↔ kiiya_lapuerta** both ship `vw_lodlights_medium015.ymap` and `vw_distlodlights_medium015.ymap` (one wins).
- `_manifest.ymf` shipped under that same name by blockz_borderv2, blockz_borderv2_tunnel, kiiya_lapuerta, cylex_animmenuv2 (effect undocumented).
- pio_cht ships two different copies of `id1_rd_2.ybn`, `hi@id1_rd_2.ybn`, `id1_17_2.ybn`, `pio_h3_rd_1.ydr` in different sub-folders (only one loads).
- Huge streaming boxes: molo_lspdhq building (lodDist 9 999, 20 km box), molo_davispd exterior (2 000), blockz wall (7.5 km).
- `this_is_a_map` missing in sa_euro_junctions, pillbox, qbx_density, bob74_ipl (they work as overrides; add it to new map resources).
- La Puerta self-built build folder (`H:\FiveM\mods\mlo\la_puerta_towers\build`) with `--orig`: 0 errors; `lpt_t3.ymap` streaming box 3.2 km over the origin (lodDist 1500); all compiled ymaps have CMapData name 0; empty `ma@kt1_13_0` composite.
