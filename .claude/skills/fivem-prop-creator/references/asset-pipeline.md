# Build pipeline (Blender + Sollumz 2.9 + CodeWalker)

Checked 2026-11-08 against Sollumz docs 2.9 / source `main` 2026-11-06 and Cfx assets-manual beginner series (fivem-docs 467b2f3). Menu names move between Sollumz versions; match the installed one.

## Container

| Container | What it holds (Sollumz docs) | Use |
|---|---|---|
| `.ydr` Drawable | shader group (+ optional embedded textures), optional skeleton, High/Medium/Low/Very Low models, lights, embedded bounds | static or pushable props, doors, hand-held props |
| `.yft` Fragment | drawable + physics (composite bounds, physics groups per bone, mass/inertia), optional damaged drawable, lights | breakable, separating or swinging parts; animated parts that must collide (see doors-fragments-animated.md) |
| `.ydd` Drawable Dictionary | several drawables, no archetype of its own; archetype fills `drawableDictionary` | LOD sets, instanced props. Embedded collision does **not** work inside a YDD |

Measured vanilla: prop_chair_01a / prop_table_06 / prop_roadcone01a / v_ilev_ph_door01 are YDR; prop_bench_01a, prop_fire_hydrant_1, prop_bin_01a, prop_container_05a, prop_streetlight_01, prop_gas_pump_1a are YFT. No measured prop uses YDD.

## Model rules

- Real scale; compare with a vanilla prop of known size placed next to it. Apply rotation/scale before converting.
- Origin: bottom centre for placed props (CodeWalker snap-to-ground uses the origin — Bumpy86 -24PBSYT74w [19:37]); grip point for hand props (attachment offsets stay near 0); hinge / bottom corner / bottom centre for doors (Cfx part 8).
- UV map name `UVMap 0` (wrong names make the model invisible in CodeWalker — Sollumz FAQ, Cfx part 3).
- Vertex colour attribute `Color 1`, Face Corner, Byte Color. Red channel = exterior/night lighting, green = interior artificial light; without it props glow pinkish red at night or turn black in an MLO (Sollumz FAQ; mnsb223 j8kZWnYZ_e4 [15:00]–[16:34]).
- Convert to Drawable (Sollumz object tools), name the drawable and models after the file name, put each mesh in its LOD slot (High first).

## Shaders (pick by maps used)

| Need | Shader |
|---|---|
| diffuse only / + spec / + normal / normal + spec | `default`, `spec`, `normal`, `normal_spec` (normal map colour space Non-Color in Blender) |
| cut-out alpha (leaves, fences) | `cutout`, `normal_cutout`, `normal_spec_cutout`, `cutout_fence(_normal)` |
| blended alpha | `alpha`, `normal_alpha`, `spec_alpha` |
| overlay layer | `decal`, `decal_glue`, `normal_spec_decal` |
| glowing | `emissive`, `emissivenight` (night only: wall lights, gas pump), `emissivestrong`, `normal_spec_emissive` (TV) |
| glass | `glass`, `glass_pv`, `glass_env` (bottle), `glass_spec`, `glass_emissive` |
| tintable (bins, crates) | `*_tnt` + a 256×4 palette texture; entity Tint Value picks the row |

Shader parameter values from one tutor (ook_3D R_az2tpBhRw: specular falloff ~5, intensity ~0.2, fresnel ~0.94) are taste, not Rockstar data — test in game.

## Textures: embedded or YTD

- Embedded (`Set all Materials Embedded`) = no separate `.ytd`; a YTD shares textures between props. Both are valid; vanilla often mixes a few embedded textures with a shared archetype `txd` (burger: 2 embedded + `prop_cs_ld_snack`).
- When everything is embedded Sollumz sets the archetype texture dictionary to the model name — that is not a missing file.
- DDS, power of two, full mip chain. DXT1 opaque, DXT5 alpha, ATI2/BC5 normals; A8R8G8B8 only for tiny palettes or screens. Sizes in lods-textures-budgets.md.
- HD textures: mark HD → `+hi.ytd` (`+hidr` for embedded) at full size, base at half, bound in `_manifest.ymf` `HDTxdBindingArray`; archetype `hdTextureDist` decides when they load.

## Export

- Sollumz 2.9 exports native binaries or CodeWalker XML (Legacy Gen8 or Enhanced Gen9). XML must be imported in CodeWalker before it can stream; renaming `.xml` to `.ydr` is not conversion.
- Keep the `.blend`, the XML export and a `SOURCE.txt`/`CREDITS.md` (author, URL, licence, date) next to — not inside — `stream/`.
- Conversion-only jobs: keep `.ydr/.yft/.ytd` 1:1, report size warnings, never re-compress or decimate unless asked (LESSONS).
- To measure a similar vanilla prop: open it in CodeWalker (RPF Explorer → export XML) or point `scripts/rsc_probe.py` at an extracted file (`py -3 -I rsc_probe.py prop_x.ydr prop_x.ytd prop_x.ytyp` prints LOD triangles, lodDist, textures, archetype fields).
