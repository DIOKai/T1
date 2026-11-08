# Sources and video study

Contents: 1 documentation · 2 source code read · 3 the user's own incidents and tools · 4 videos with transcripts · 5 videos with chapter titles only · 6 gaps

Checked 2026-11-08 unless noted. Keys are used in the other references. "(unverified)" = single tutor, chapter title only, or not tested in game.

## 1. Documentation

- [D:cfx2] Cfx assets manual part 2 - CodeWalker Enable DLC + DLC level newest + Save Settings. https://docs.fivem.net/docs/assets-manual/beginner-series/part-2/
- [D:cfx4] part 4 "Placing Assets & Creating Simple Map Mods" - project, new ymap/entity, Shift+drag duplicate, Calculate Extents + Calculate All Flags, Manifest Generator → `_manifest.ymf` ("necessary to load the models correctly"), fxmanifest with `this_is_a_map 'yes'`. https://docs.fivem.net/docs/assets-manual/beginner-series/part-4/
- [D:cfx5] part 5 Collision - Collision selection mode, export ybn XML, Bound Poly Box under a GeometryBVH "which must have the proper flags", world coordinates. https://docs.fivem.net/docs/assets-manual/beginner-series/part-5/
- [D:cfx6] part 6 LODs - HD flag "LOD in Parent Map", LOD at the same coordinates, ChildLodDist = HD LodDist, HD ymap Parent = LOD ymap, ParentIndex 0, NumChildren 1, manifest. No distances given. https://docs.fivem.net/docs/assets-manual/beginner-series/part-6/
- [D:manifest] resource manifest - `this_is_a_map` "reloads the map storage when the resource gets loaded". https://docs.fivem.net/docs/scripting-reference/resource-manifest/
- [D:datafiles] data files - DLC_ITYP_REQUEST, TIMECYCLEMOD_FILE, SCENARIO_*, TRAINTRACK_FILE, GTXD_PARENTING_DATA …; no water / navmesh / occlusion key. https://docs.fivem.net/docs/game-references/data-files/
- [D:natives] CFX natives `LOAD_WATER_FROM_PATH`, `RESET_WATER`, water-quad getters/setters (runtime.fivem.net/doc/natives_cfx.json).
- [D:console] client console commands `strdbg`, `strlist`, `strmem`, `resmon`, `cl_drawperf`, `save_gta_cache`. https://docs.fivem.net/docs/client-manual/console-commands/
- [D:builds] `sv_enforceGameBuild` table (3258 Bottom Dollar Bounties; Enhanced only 3889). https://docs.fivem.net/docs/server-manual/server-commands/
- [D:sz-maps] Sollumz 2.9 "Maps (.ymap)" - containers = LOD hierarchy, six item types, locked containers with missing LOD parents/children, partitioning, LOD lights bake. https://docs.sollumz.org/documentation/maps
- [D:sz-ybn] Sollumz collisions - plain / `hi@` / `ma@`, Composite → GeometryBVH → poly/primitives, "a very common mistake … not applying a Flag Preset". https://docs.sollumz.org/documentation/collisions.ybn
- [D:sz-col] Sollumz "Creating static collisions". https://docs.sollumz.org/tutorials/creating-static-collisions
- [D:sz-mesh] Sollumz "Creating static meshes" (embedded materials, ytyp, manifest). https://docs.sollumz.org/tutorials/creating-static-meshes
- [D:sz-ytyp] / [D:sz-flags] Sollumz archetype definition and flags. https://docs.sollumz.org/documentation/archetype-definition.ytyp
- [D:sz-tex] Sollumz texture dictionaries (`+hi` HDTxdBindingArray in the `.ymf`).
- [D:sz-lod] Sollumz drawable LODs and Auto LOD tool.
- [D:sz-faq] Sollumz FAQ - DDS power of two ≤ 2048, vertex painting required (red outdoors), invisible in CodeWalker = attribute names, BVH flag preset, two grass types invisible in CodeWalker.
- [D:sz-features] Sollumz features - ydr/ydd/ybn/ymap/ytyp full, yft/ycd partial, no ynd/ynv/water.
- [D:cw-readme] CodeWalker README (projects, keys, "Some options may cause CodeWalker to crash"). https://github.com/dexyfex/CodeWalker
- [D:cw-g5m] CodeWalker on gta5-mods (v30_dev46 2024-01-29; v.29 YNV editing WIP; v.26 manifest generator; v30_dev44 bulk delete grass).
- [D:forum-cwfivem] https://forum.cfx.re/t/codewalker-and-fivem/4482005 - edits not showing: another map streams the same ymap / newer DLC copy; move below the map instead of deleting.
- [D:forum-removed] https://forum.cfx.re/t/codewalker-issue-please-help-props-removed-in-cw-still-showing-in-game/5132772 - no live reload, clear cache, ybn and LODs too.
- [D:forum-removeprops] https://forum.cfx.re/t/remove-default-props-with-codewalker/826267 - props return at distance = LOD.
- [D:forum-two] https://forum.cfx.re/t/making-two-codewalker-projects-compatible-with-eachother-when-streamed/5136214 - merge duplicate files.
- [D:forum-collfinder] https://forum.cfx.re/t/fivem-map-file-collision-finder-dev-resource/5306267 - duplicate-name scanner; "ymaps are almost always the cause of flickering".
- [D:forum-ynd] https://forum.cfx.re/t/ynd-aka-support-of-traffic-paths-for-custom-maps/135190 (2018) - streamed ynd work (not official docs).

## 2. Source code read (2026-11-08)

- [SRC:cw-project] CodeWalker ProjectForm menus (New Ymap/Ytyp/Ybn/Ynd/Ynv/Trains/Scenario; Auto Calculate Extents/Flags; Manifest / Nav Mesh / LOD Lights generators, Delete Grass, Import Menyoo XML; no water editor).
- [SRC:cw-flags] CodeWalker EditYmapEntityPanel entity flag names.
- [SRC:cw-ymapflags] CodeWalker `YmapFile.CalcFlags` (starts from 0; bits as in codewalker-ymap.md §4).
- [SRC:cw-extents] `YmapFile.CalcExtents` - archetype boxes ± lodDist; sphere fallback when the archetype is not loaded.
- [SRC:cw-lod] `YmapFile` load loop (`isroot` when index out of range, flag 8, or parent not a higher level) and `ConnectToParent` (roots index into the parent ymap).
- [SRC:cw-ynd] / [SRC:cw-ynv] / [SRC:cw-cargen] path grid, navmesh cells, car generator flags.
- [SRC:sz-terrain] Sollumz `editor_tools/vertex_paint/terrain.py` - terrain layer colours.
- Binary ymap layout used by the checker: meta root `CMapData` 0xD3593FA6, `CEntityDef` 0xCE501483, `CMloInstanceDef` 0x09CC28BE, array offsets (entities +96, box occluders +128, occlude models +144, physics dictionaries +160, grass +208, timecycle +224, car gens +240, LOD lights +264, distant LOD lights +400), lodLevel enum 0 HD … 5 ORPHANHD, 6 SLOD4; verified against CodeWalker XML of the same files (kt1_lod, lpt_t3, kt1_occl_00, qbx_density car gens, vw_lodlights, cs6 grass).

## 3. The user's own incidents and tools [U]

Memory notes `C:\Users\Owner\.claude\projects\H--FiveM\memory\` (vanilla-occluders, mlo-packaging-rules, gta-half-float-uvs, la-puerta-towers-project, graphics-pack-project, postal-map-project, fivem-server-layout) and `H:\FiveM\mods\mlo\la_puerta_towers\.ledger\progress.md`:
- occluders left after removing kt1_13 (2026-10-18) and `tools/occluders.ps1`; camera inside an MLO room as a second cause;
- `strip_vanilla_site.py`, `strip_vanilla_roadprops.py`, `compile_ymaps.ps1`, `edit_vanilla_ybn.py` (index remap, numChildren 17 → 16, bury at z −500, `hei_` copies, three ybn);
- SLOD2/3 visible beyond ~750 m (open limitation);
- BVH with 37 292 polygons failed the Sollumz export;
- crash bisection 2026-10-14 (MLO packaging, standalone tower);
- half-float UVs, ytd NameHash;
- `[maps]` category clash; `minimap_sea_*` second owner;
- `H:\FiveM\vanilla_ref\tools` survey scripts (CodeWalker.Core, read-only on the game).

## 4. Videos with transcripts (English captions, 20-s buckets)

- **vDYllxY7ReY** Tobii, "[GTA 5 Tutorial - Part 18] Deleting world details the right way (YMAP)", 2020, 19:46 - 00:40 children make deletion risky; 01:40 DLC latest; 02:40 world collision ybn; 04:20 Max LOD HD = deletable details; 05:40 move LODs under the world; 07:20 SLOD = merged model; 08:40 new details in a separate ymap; 09:40 stale view → reopen; 12:40 manifest only for the new ymap; 16:00 forgot Calculate Extents; 18:20 moved LOD faintly visible far away.
- **D0bj_m5iEGA** Ottoerich, "How to remove LOD's", 2022, 5:07 - 00:20 move under the map; 00:40 reopen CodeWalker per LOD level ("will corrupt its parent ymap", single claim); 01:40 SLOD mesh edit; 04:20 delete occluders.
- **tNRd5EZj0Oc** gta5 modder, "Removing trees - FiveM and CodeWalker - Tutorial 1 of 3", 2023, 17:53 - 01:00 game build = DLC level; 02:40 just below the surface; 05:20 every LOD level; 11:00 auto extents/flags, manifest; 17:00 trunk collision remains.
- **ADe_gczZUQw** RoyalT Customz, "Custom Hood | Removing Occlusions and Adding Buildings Part 1", 2026, 25:19 - 00:40 cover left-over collision; 05:40 glitching without removing occlusions; 06:40 delete occluders of the building; 22:20 embedded collision + flag preset.
- **8r6KS9n2f7k** gta5 modder, "Create occluders with Blender and Sollumz", 2026, 11:13 - 00:20 blue box / red model; 02:20 CodeWalker position → Sollumz; 05:00 `_occl` name ("not going to work" without, single claim); 10:40 manifest.
- **FqZ1OuHfNoM** Tobii, "[Part 3] Car generators", 2019, 8:55 - 01:00 car gen boxes; 02:00 police gens; 03:20 edit the copy another map ships; 05:40 CarModel spawn name; 06:20 copy flags from vanilla.
- **m6H6tBL3CQ8** Stumpy Mason, "LOD Tutorial Part 1", 2025, 25:50 - 01:20 drawable LODs; 09:00 ORPHANHD; 15:00 parented HD (1572872), parentIndex in the parent ymap; 16:40 LOD/SLOD ymaps with distances; 24:40 copy Rockstar's distances.
- **gWvvGdzO8Ak** Bodhix, "How to fix Occlusion conflicts in FiveM | Flickering MLO's", 2026, 4:52 - duplicate occl files; merge into one.
- **WMek-S1QU_I** The Kong On Top, "How to merge maps using codewalker", 2024, 20:50 - test alone/together, merge shared vanilla ymaps, keep in one resource.

## 5. Videos with chapter titles or description only (captions blocked, HTTP 429) - content unverified

FlV5YeolMTY (RoyalT, terrain + building + collision removal, 1:00:27, no chapters) · 9GddiFy6nhQ (Ottoerich, remove props, "enable dlc to match server level") · J_OpnSDDiQI (ook_3D, replace terrain, no English captions) · pqdp_sHfgxs, 7Jm74L3FfLk (ook_3D, terrain blending) · toR0HegiteU (EnderMods, French, "Éditer une zone complète", chapters 00:42 export … 30:12 road transitions, 37:18 collisions, 55:03 LODs; description: remove OCCLUDERS when placing new buildings/MLOs) · mfFe7rZn3NM, 2knoRkP09sE (dexyfex, paths) · U0nrVL44Fb4 (dexyfex, scenarios) · BGquctFhXPc (Luman3D, navmesh; advertises a paid tool) · 2jAb5ux-ZzI (Desertos, stream water.xml) · zjwdHu30CyY (Stumpy Mason, custom pool) · cP1f8h5RHtA (Stumpy Mason, basic collision) · PmvzT8AQ4bs (gta5 modder, altering a SLOD YDD) · ecpZsF8aJWc (gta5 modder, deleting vanilla LOD lights) · 4ErOxj6QNzA (ook_3D, editing collisions) · z3QwE87YtDk (Twisle, custom ymaps).

## 6. Gaps

- Highest-value unread: FlV5YeolMTY (terrain + collision removal), PmvzT8AQ4bs (SLOD ydd edit), ecpZsF8aJWc (LOD lights), water/pool videos.
- Not documented anywhere found: the engine's exact parentIndex rule (CodeWalker's reading is used), whether same-named `.ymf` files in two resources conflict, whether CMapData name 0 matters (worked on the user's server), the BVH polygon limit.
