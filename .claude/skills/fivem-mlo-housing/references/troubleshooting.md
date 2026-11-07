# Troubleshooting: symptom → cause → fix

Start with `check_mlo_resource.py <resource> <export-folder>`, then the server console after `ensure`, then walk through the interior in game.

| Symptom | Likely cause | Fix |
|---|---|---|
| Interior doesn't appear at all | MLO ymap not loaded (no `_manifest.ymf`, extents not calculated, XML instead of binaries in `stream/`); `CMloInstanceDef` archetype name ≠ MLO archetype name; resource not ensured | run the checker; regenerate the manifest; Calculate Extents/Flags; compile XML with CodeWalker |
| Visible from outside, disappears when entering (or the reverse) | entities not attached to the room; room bounds don't cover the space; portal faces the wrong way or is missing | attach entities to rooms; set bounds from the collision; portals inside → outside, flip if needed |
| Interior vanishes from some angles (grey floor + sky), fine from others | portals facing mixed directions | every portal's normal away from roomFrom; the checker's `PORTAL_FACING` lists them; Flip Direction in Sollumz |
| Every client crashes near the MLO, or right after loading | several MLO instances in one ymap; an MLO mixed into a ymap with other entities; `DLC_ITYP_REQUEST` of the MLO ytyp | one MLO per `*_milo_.ymap`, MLO ytyp loaded only by the `.ymf` (checker: `YMAP_MULTI_MLO`, `YMAP_MLO_MIXED`, `ITYP_REQUEST_MLO`) |
| Textures stretched or swimming on big walls | UVs far outside 0–1 (half-float precision) | recenter UVs, lower the tiling, keep \|UV\| under ~50 |
| Can't see out of windows / doorway looks like a wall | no portal on that opening (or not to limbo) | add a portal per window/door to limbo |
| Flicker at doorways | overlapping room bounds; portal not exactly in the opening | tighten bounds; snap portal corners to the opening |
| Fall through the floor / walk through walls | missing or wrong interior `.ybn`; exterior collision not cut or still blocking | rebuild the Bound Composite; edit both `name.ybn` and `hi@name.ybn` |
| Pitch black at night | no lights in the `.ydr`; vertex colour R high everywhere; room timecycle too dark | add lights; tune vertex colours (G for artificial light); pick a brighter room `timecycleName` |
| Too bright / looks like outdoors | no room timecycle; "Force Directional Light On" set | set an `int_*` style timecycle; remove the flag |
| Rain or weather inside | it's a shell (exterior) or the area isn't inside an MLO room | for shells, disable rain/freeze weather while inside; for MLOs, check room bounds |
| Outside sound through walls | no audio occlusion | generate with ht_mlotool; `AUDIO_GAMEDATA` + `.ymt` in a `this_is_a_map` resource |
| Two MLOs fight / vanilla building flickers through | same location or same archetype/file names; vanilla building not replaced | one MLO per location; unique names; stream the edited exterior under the vanilla name |
| Door doesn't move | special attribute not set, missing Dynamic + Enable Door Physics, origin not at hinge | fix the ytyp flags and the model origin |
| Entity set toggles don't show | no `RefreshInterior`; wrong interior id (coords outside); name typo; another resource resets it | refresh after changes; get the id at coords inside; one owner per interior |
| Shell: players see each other in different houses | all shells at the same coords | spawn per-property locations (qbx_properties `shellUndergroundOffset`) or routing buckets |
| Furniture missing for other players or after relog | props spawned networked/unsaved, or only for the placer | save server-side; spawn locally for everyone inside on enter |
| Long load / textures pop in | oversized `.ytd` (16/48 MiB warnings) | split dictionaries, 2K textures, reuse vanilla props |
