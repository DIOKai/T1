# Removing, moving or hiding vanilla

Contents: 1 decision ladder · 2 find every owner · 3 the cut list · 4 base and hei_ copies · 5 one owner, merging two maps · 6 the user's scripted pipeline · 7 verify

Citation keys: [sources.md](sources.md).

## 1. Decision ladder (least risky first)

1. **Add, do not modify.** A new building or prop goes in a new ymap with your prefix [V:vDYllxY7ReY 08:40].
2. **Move under the map** anything that has LOD links. In CodeWalker switch Max LOD ORPHANHD → HD: what disappears had no LOD link and may be deleted; what remains at LOD/SLOD level must be moved, not deleted [V:vDYllxY7ReY 04:20-08:00; D:forum-removeprops; D:forum-cwfivem]. Do it at every level (HD, then Max LOD = LOD, …) - farther levels group many objects (trees) into one [V:D0bj_m5iEGA 01:20; V:tNRd5EZj0Oc 05:20-10:40]. "Just below the surface" is enough per one tutor [V:tNRd5EZj0Oc 02:40]; the user buries at z −500. A LOD whose box also covers fences moves them too - leave it [V:vDYllxY7ReY 06:40]. Moved LODs can stay faintly visible from very far [V:vDYllxY7ReY 18:20].
3. **Delete with index repair** (scripted, section 6): remap every child's parentIndex, lower `numChildren`, keep parents that other files index into (bury them at z −500, never delete → index shift).
4. **SLOD merged meshes**: SLOD2/SLOD3 drawables (ydd/ydr) cover whole blocks; the old building stays visible beyond ~750 m until that mesh is edited in Blender [V:D0bj_m5iEGA 01:40-03:00; V:vDYllxY7ReY 07:20; U:ledger]. Video on editing the YDD: PmvzT8AQ4bs (from chapter titles, unverified).
5. **RemoveIpl** only works for IPL-group / scripted ymaps (vanilla interiors, Cayo); do not rely on it for always-loaded city ymaps (no authoritative source; unverified).

## 2. Find every owner

- CodeWalker: select the entity (panel shows its ymap), then Collision / Occluders / Car Generator selection modes; Max LOD to see LOD and SLOD members.
- From the game files (read-only, `H:\FiveM\vanilla_ref\tools`, CodeWalker.Core): `survey_ymaps.ps1` (vanilla entities inside a world box, names resolved), `survey_bounds.ps1` (world boxes), `ymap_xml.ps1 -Out <dir> -Names a.ymap,b.ymap` (newest copy across all archives/DLC → XML), `find_archetypes.ps1` (which ytyp defines an archetype), `find_names.ps1`, `cw_export_all.ps1`. Call via `powershell -NoProfile -Command "& 'tool.ps1' -Names a,b"` so arrays parse.
- Props of a block often sit in the **road ymaps** (`<area>_rd_*`) too [U:strip_vanilla_roadprops].

## 3. The cut list

For every removed building check each row:

| Member | Where | Left behind gives |
|---|---|---|
| HD props | `<block>_strm_N`, `_long_N`, `<area>_rd_*` | the building / clutter itself |
| LOD, SLOD1 | `<block>.ymap` | building pops back at mid distance |
| SLOD2/3 | `<area>_lod.ymap` merged mesh | visible beyond ~750 m (mesh edit) |
| World collision | `<block>_N.ybn`, `hi@<block>_N.ybn` (bullets), `ma@<block>_N.ybn` (procedural grass/trash) [D:sz-ybn] | invisible walls, bullets stop, grass inside |
| Occluders | `<area>_occl_NN.ymap` (+ `hei_`), also `woccl_city_00`, `ch1_far_occl_00` style files | city behind not drawn from the site |
| Car generators | the block's strm ymaps | cars spawn inside the new build |
| Timecycle boxes | block ymap | odd light/colour near the build |
| LOD lights | `lodlights_*` / `distlodlights_*` | floating lights at night (video ecpZsF8aJWc, unverified) |
| Grass batches | `*_grass_*` / `ma@` material | grass through the floor |
| Scenario points / paths | scenario files, `nodes*.ynd` | peds/cars walking through the build |

Collision: buildings often have **no embedded collision** - moving the entity leaves the world `.ybn` behind [V:vDYllxY7ReY 02:40; V:tNRd5EZj0Oc 17:00]. Export the ybn (RPF Explorer → XML), cut the polygons inside the site in Blender/Sollumz, keep kerbs and streets, re-export; check that nothing outside the site changed (user's `edit_vanilla_ybn.py` ray check `band_lost` = 0) [D:cfx5; U]. A completely empty `ma@` composite was a crash suspect on the user's server (unverified). Pragmatic workaround seen in a tutorial: cover left-over collision with the new building or bushes [V:ADe_gczZUQw 00:40].

Occluders: cut only the boxes / model triangles over the site; never delete a whole occluder ymap (the rest of the area then over-draws). User's `occluders.ps1`: `-Extract` newest copies, drop boxes and triangles overlapping the site rectangle, set `Name` before `Save()`, reload and verify counts; stream base **and** `hei_` copies [U:vanilla-occluders]. CodeWalker GUI: selection Occluders, delete the ones on the building, Calculate flags + extents, save [V:ADe_gczZUQw 06:40; V:gWvvGdzO8Ak]. "The world vanishes from some spots" also happens when the gameplay camera sits inside an MLO room through glass [U:ledger round 7].

## 4. Base and hei_ copies

Many city ymaps exist twice: `kt1_13.ymap` and `hei_kt1_13.ymap` (mpheist DLC). FiveM always loads the MP packs, so the `hei_` copy is the one players see; edit both the same way [U:ledger; V:vDYllxY7ReY 01:40]. Kiiya's La Puerta on the user's server ships only the `hei_` copies (fine for FiveM). Check with `ymap_xml.ps1` or CodeWalker (DLC on) whether a `hei_` copy exists - not every ymap has one. Later DLCs can add their own copies (`lr_`, `bkr_` …): set CodeWalker's DLC level to the newest.

## 5. One owner, merging two maps

A vanilla file can be replaced by **one** resource. Two map resources shipping the same ymap / occl / ybn → the later one wins: removed things come back, props double or float, flicker [D:forum-cwfivem; D:forum-two; D:forum-collfinder; V:WMek-S1QU_I]. Before editing, search all resources for the file name (the checker's `DUPLICATE_STREAM_FILE`).

Merge: test each map alone, then together; copy both resources' versions of each shared file into a work folder; open in CodeWalker and apply both sets of edits (move floating props under the map, delete each other's occluders over each MLO); Calculate extents + flags; keep the merged file in ONE resource and delete it from the other [V:WMek-S1QU_I 05:20-18:40; V:gWvvGdzO8Ak]. Edit the copy another map already ships instead of adding a second (car gens near a police station map) [V:FqZ1OuHfNoM 03:20]. A free "collision finder" dev resource lists duplicates by name [D:forum-collfinder].

Found on the user's server (2026-11-08 checker run): `molo_lspdhq` and `kiiya_lapuerta` both ship `vw_lodlights_medium015.ymap` and `vw_distlodlights_medium015.ymap`; several resources ship a file called `_manifest.ymf`.

## 6. The user's scripted pipeline (La Puerta, kt1_13)

`H:\FiveM\mods\mlo\la_puerta_towers\tools`:
1. `ymap_xml.ps1` → untouched XML of `kt1_13`, `_strm_0/1`, `_long_0`, `kt1_lod`, `kt1_rd*` and all `hei_` copies (`vanilla_ref\la_puerta\ymap_xml`).
2. `strip_vanilla_site.py` / `strip_vanilla_roadprops.py`: remove CEntityDefs, car generators and timecycle boxes inside the site polygon; remap children's parentIndex when a LOD ymap's list changes; decrement the SLOD2's numChildren (17 → 16); a parent that lost all children but is indexed by other ymaps stays in the list at z −500.
3. `compile_ymaps.ps1 -CalcFlags`: XML → YmapFile → CalcFlags → Save → reload and compare entity/car-gen counts.
4. `occluders.ps1`, `edit_vanilla_ybn.py` for occluders and the three ybn.
5. Known limitation left open: SLOD2/3 beyond ~750 m.

## 7. Verify

```
py -3 -I check_map_resource.py <resource> --xml <edited xml dir> --orig <vanilla xml dir>
```

On the La Puerta build this reports 0 errors: removed counts per ymap, no index shift, `hei_` edits identical, occluders cut, plus the reminders `COLLISION_NOT_EDITED` (kt1_rd) and `SLOD_REMINDER`. Then in game: stand on the site and look in every direction (city drawn?), fly up and away to 1 km (old building gone at which distance?), walk and drive across (no invisible walls), shoot the former walls (hi@), night (no orphan lights), both single-file restart and full reconnect.
