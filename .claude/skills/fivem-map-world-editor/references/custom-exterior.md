# Custom exterior builds (Blender + Sollumz → CodeWalker)

Contents: 1 plan · 2 model · 3 textures · 4 LODs · 5 collision · 6 ytyp · 7 lights · 8 place and package · 9 budgets

For single props the authority is `fivem-prop-creator`; for anything players walk into, `fivem-mlo-housing`. This file covers outdoor structures placed with a ymap: plazas, building shells, walls, bridges, landmarks. Citation keys: [sources.md](sources.md). Driving the user's Blender through the `blender` MCP needs asking first; before modelling, study a YouTube tutorial for that kind of object and trace real references (LESSONS); nothing may float, buildings stand on real foundations, windows are real glass with real interiors behind (LESSONS).

## 1. Plan

- Survey the site from game data (coordinates, street heights from path nodes, neighbouring vanilla entities) - the user's `survey_*.ps1` CSVs did this for La Puerta.
- Decide what vanilla must go first ([removing-vanilla.md](removing-vanilla.md)) and which resource will own each overridden file.
- One unique prefix for every file and archetype (`lore_lsq_…`), never generic names.

## 2. Model

- World coordinates (or record the placement transform). Convert to Drawable, Sollumz shaders [D:sz-mesh].
- **Vertex colours**: Sollumz FAQ "VERTEX PAINTING is required" - red for outdoors, green inside MLOs, otherwise pink glow at night [D:sz-faq]. UV map / colour attribute names must follow Sollumz convention or the model is invisible in CodeWalker [D:sz-faq].
- **|UV| < ~50** (half floats; see [terrain-roads-water-paths.md](terrain-roads-water-paths.md) §1).
- Several pieces may be joined (Ctrl+J) per material area to keep draw calls down [V:ADe_gczZUQw 22:20].

## 3. Textures

- DDS, power of two, recommended max 2048 [D:sz-faq]. Embedded ("Set all Materials Embedded", no ytd needed) for one-offs [D:sz-mesh]; a shared `.ytd` named in the archetype's texture dictionary for many pieces.
- Custom HD dictionaries (`+hi.ytd`, `+hidr`, `+hifr`, `+hidd`) must be listed in the `_manifest.ymf` HDTxdBindingArray [D:sz-tex].
- A ytd built by code with CodeWalker `BuildFromTextureList` needs `NameHash = JenkHash.GenHash(name)` per texture or textures show wrong [U:gta-half-float-uvs].
- FXServer warns above 16 MiB and expects streaming trouble above 48 MiB per file (RSC header formula); real RSC size reached 1.31× the texture-sum estimate on the user's packs [U:graphics-pack].

## 4. LODs

- **One building**: drawable LODs High/Medium/Low/Very Low inside the model (Sollumz Auto LOD under Tools → Drawable → LOD Tools [D:sz-lod]); entity ORPHANHD with a moderate lodDist. This is what the user's La Puerta tower ended with after the crash bisection [U:ledger].
- **Big landmark seen from far**: entity LOD chain HD → LOD → SLOD in separate ymaps + `_manifest.ymf` ([codewalker-ymap.md](codewalker-ymap.md) §6) [D:cfx6; V:m6H6tBL3CQ8].
- Drawable switch distances end at the entity/archetype lodDist; beyond it the object disappears [V:m6H6tBL3CQ8 10:20].

## 5. Collision

Separate world `.ybn` (Convert to Composite, empties at 0,0,0, composite named like the file, world coordinates) or embedded in the drawable (RoyalT converts with embedded collision and applies the flag preset [V:ADe_gczZUQw 22:20]). Primitives first; Flag Preset on every BVH; ≤ 32 767 polygons per BVH (user-observed export failure) [D:sz-col; D:sz-ybn]. Cut the vanilla ybn where the build stands.

## 6. ytyp

Archetype name = drawable name; lodDist, texture dictionary, physics dictionary, flags (Static for fixed structures, shadow flags), asset type [D:sz-ytyp; D:sz-flags]. Sollumz "Export with ytyp". Load it via the `.ymf` or `data_file 'DLC_ITYP_REQUEST' 'stream/x.ytyp'` (prop ytyps only - MLO ytyps never, see `fivem-mlo-housing`). CodeWalker must have the ytyp loaded before Calculate Extents (else a tiny sphere → invisible) [SRC:cw-extents].

## 7. Lights

Lights live in the drawable (Sollumz light objects and flags); distant glow needs LOD lights - Sollumz "Bake LOD Lights" creates `lodlights` + `distlodlights` ymaps; lights with a non-zero Light Fade Distance are skipped, Large lights need the "Far LOD Light" flag [D:sz-maps]. Night-only emissive windows (`emissivenight`) - check by night in game.

## 8. Place and package

1. Convert XML in CodeWalker (RPF Explorer) or export ymaps from Sollumz 2.9.
2. New ymap with your prefix; entities at world position; Calculate Extents + All Flags; Manifest Generator → `<prefix>_manifest.ymf`.
3. Resource layout:

```
[assets]/[border-maps]/lore_plaza/      <- category name unique server-wide
  fxmanifest.lua
  CREDITS.md                            <- author, source, licence, date
  stream/lore_plaza.ymap  lore_plaza.ytyp  lore_plaza_*.ydr  lore_plaza.ytd  lore_plaza_col.ybn  lore_plaza_manifest.ymf
```

```lua
fx_version 'cerulean'
game 'gta5'
lua54 'yes'
this_is_a_map 'yes'
```

4. Run `check_map_resource.py`, then `fivem-asset-acceptance`.

## 9. Budgets and performance

- Entity count and lodDist: streaming extents grow by lodDist (the checker warns above 1 500 for HD) ([codewalker-ymap.md](codewalker-ymap.md) §4); lodDist 1500 on the user's tower made a ~3 km box containing the map origin.
- Texture memory (`strmem`), streaming (`strdbg`, `strlist`) [D:console]; `resmon` measures scripts, not streaming.
- Occluders for big solid buildings help performance, but never larger than the real wall.
- Compare with Rockstar's distances (measured 2026-11-08 on 18 vanilla kt1 ymaps, `vanilla_ref/la_puerta/ymap_xml`): ORPHANHD 3 066 entities, median lodDist 30, max 250; HD 1 094, median 174, max 350; LOD median 400 (190-425); SLOD1 600-750; SLOD2 1 500; SLOD3 15 000. An HD entity above ~350-500 has no vanilla precedent there.
