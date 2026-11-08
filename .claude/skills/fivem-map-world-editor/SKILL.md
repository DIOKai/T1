---
name: fivem-map-world-editor
description: Use when editing the GTA V or FiveM outdoor world with CodeWalker or Sollumz - placing props or buildings with a ymap, removing, moving or hiding vanilla buildings, trees or car generators, replacing terrain, roads or world collision, occluders, LOD and SLOD links, water, traffic paths, custom exterior builds, merging two map resources - or when map things vanish, flicker, float, still show from far away, the city behind goes missing or players fall through. Triggers include 地图编辑, 改地图, 删原版建筑, ymap, 地形, 碰撞, 遮挡, occluder, 道具放地图, 地图冲突, 东西不见了.
---

# FiveM map world editor

An outdoor map edit is never one file. A vanilla building is a set: HD entities in `<block>_strm_N` / `_long_N` ymaps, its LOD/SLOD1 in `<block>.ymap`, SLOD2/3 merged meshes in `<area>_lod.ymap`, world collision in `<block>_N.ybn` + `hi@` + `ma@`, occluders in `<area>_occl_NN.ymap`, plus car generators, timecycle boxes, LOD lights and a `hei_` copy of every ymap that multiplayer actually loads. Most "it came back / the city vanished / I fall through" reports are one member of that set left behind.

## Route

| Job | Read | Also |
|---|---|---|
| Place props or a building with a ymap | [codewalker-ymap.md](references/codewalker-ymap.md) | the prop itself → `fivem-prop-creator` |
| Remove, move or hide vanilla (buildings, trees, car gens) | [removing-vanilla.md](references/removing-vanilla.md) | |
| Terrain, roads, world collision, water, traffic paths, navmesh, scenarios | [terrain-roads-water-paths.md](references/terrain-roads-water-paths.md) | |
| Custom exterior build (plaza, tower shell, wall, landmark) in Blender + Sollumz | [custom-exterior.md](references/custom-exterior.md) | Blender MCP → ask first |
| Something is wrong in game; acceptance tests; checker codes | [troubleshooting.md](references/troubleshooting.md) | |
| Where a claim comes from; tutorial timestamps | [sources.md](references/sources.md) | |

Interiors with rooms and portals (`_milo_` ymaps, `.ymf` INTERIOR_DATA) → `fivem-mlo-housing`. Timecycle look / graphics packs → `fivem-graphics-pack`. Vanilla archetype and file names → `muto-atlas` (ask before `/asset-setup`). Release gate for any resource → `fivem-asset-acceptance` (its `asset_gate.py` runs this skill's checker on map resources). Per CLAUDE.md, ask before using any of them.

## Workflow

1. **Setup.** CodeWalker → Options: Enable DLC, DLC level = newest pack the server build loads (server.cfg `sv_enforceGameBuild 3258`), Save Settings - else you edit a copy a DLC replaces. User has CodeWalker v30_dev46; Sollumz 2.9+ also reads/writes ymaps.
2. **Find the owners.** Select the entity → the panel names its ymap; selection modes Collision / Occluders / Car Generator find the rest. Read-only tools in `H:\FiveM\vanilla_ref\tools` (`survey_ymaps.ps1`, `ymap_xml.ps1`, `find_archetypes.ps1`, `find_names.ps1`) do it from the game files.
3. **Search all resources for those file names.** One owner per vanilla file: if another map ships it, merge into that copy.
4. **Export untouched XML** (`vanilla_ref/<area>/ymap_xml`) and back up to `H:\FiveM\backup\<date>_<topic>`.
5. **Edit** the least risky way: new ymap → move under the map → scripted delete with index repair → SLOD mesh edit.
6. **Recalculate**: select each ymap → Calculate Extents + Calculate All Flags. New custom archetypes → Tools → Manifest Generator → `_manifest.ymf` (unique name).
7. **Package**: binaries only in `stream/`, `this_is_a_map 'yes'`, unique file prefix, resource in a uniquely named `[category]`.
8. **Check** with the script below, then test on the local test server (restart + reconnect; map edits do not hot-reload reliably).

## Rules that bite (from the user's server)

- **Removing a building leaves its occluder.** Standing on the cleared site, the city behind is not drawn (sky + black dots). Cut the box/model occluders over the site in `<area>_occl_*` and `hei_<area>_occl_*` (CodeWalker selection "Occluders", or the user's `la_puerta_towers\tools\occluders.ps1`). A camera inside an MLO room behind glass gives the same symptom.
- **Edit `hei_` copies too.** FiveM always runs the mpheist pack, so `hei_kt1_13.ymap` is what players see; base-only edits "do nothing".
- **parentIndex** points into the parent ymap (CMapData `parent`) when entity flag 8 "LOD in parent map" is set, when it is past the own list, or when the own entry is not a higher LOD level; otherwise into the same ymap (CodeWalker YmapFile). Deleting from a LOD ymap shifts every later index: remap children and lower the parent's `numChildren` (user: SLOD2 17 → 16).
- **Never delete a parent other files point at** - keep it in the list and move it to z −500.
- **Beyond ~750 m the old building still shows**: SLOD2/SLOD3 are merged meshes over many blocks; only editing that ydd/ydr removes it.
- **Vanilla collision comes in three**: `<block>_N.ybn`, `hi@` (bullets), `ma@` (procedural grass/trash). Cut all that exist.
- **One BVH with more than 32 767 polygons failed the Sollumz export** (user saw 37 292; not documented) - split it.
- **Keep |UV| < 50** on big terrain/road meshes (half-float UVs step into stripes).
- **Calculate Extents with an archetype CodeWalker cannot load** (custom ytyp not in the project/mods folder) gives a tiny sphere → props invisible in game.
- **One resource per overridden vanilla file; unique `[category]` names** (`[maps]` collided with `[cfx-default]\[maps]`).

## Check

```
py -3 -I .claude/skills/fivem-map-world-editor/scripts/check_map_resource.py <resource | resources folder | XML folder> [--xml DIR] [--orig vanilla_xml_dir] [--vanilla-list names.txt] [--json]
```

Read-only, stdlib. Decodes compiled ymaps directly: extents, CalcFlags, LOD links, shifted indices, lodDist, duplicates; across resources: duplicate stream files, vanilla overrides, `hei_` pairs, occluders, category clashes; XML: ybn polygons/flags, ydr UVs, ynd areas. `--orig` diffs against untouched vanilla XML (orphans, index shift, numChildren, LOD left behind, occluders/collision/car gens/`hei_` not edited). Codes: [troubleshooting.md](references/troubleshooting.md#checker-codes). Tests: `py -3 -I .claude/skills/fivem-map-world-editor/scripts/test_check_map_resource.py`. For MLOs also run `fivem-mlo-housing`'s `check_mlo_resource.py`.

## Common mistakes

| Mistake | Result | Do instead |
|---|---|---|
| New props appended to a vanilla ymap | conflicts with every other map editing that block | own ymap with your prefix |
| Delete an HD entity, leave its LOD | building pops back at distance | move the LOD under the map too |
| Delete from the LOD ymap without remapping | LODs swap at the wrong place | bury instead, or remap + numChildren |
| Forget Calculate Extents | ymap never streams | recalc + flags before every save |
| Edit only the base copy | no change in game | edit `hei_` too |
| Remove building, keep occluder / ybn | city vanishes / invisible walls | cut occluders and all ybn copies |
| Two resources ship the same ymap/occl | edits come back, flicker, floating props | merge into one copy in one resource |
| Huge lodDist (1500+) on a single building | streams from across the map | moderate lodDist + drawable LODs |

## Ground rules

- Free tools (CodeWalker, Sollumz GPL-3, Blender). Never redistribute paid or leaked maps (Kiiya, Molo…); edit them only for the user's own server.
- Work on exported copies; install on the server only after asking; test on the local test server.
- Mark single-tutorial or untested claims unverified; report files, coordinates, build, tested / not tested.
