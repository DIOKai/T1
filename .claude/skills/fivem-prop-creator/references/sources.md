# Sources (checked 2026-11-08)

Tags: **measured** = read from the user's own GTA V Legacy install (G:) with CodeWalker.Core 30 dev46, read-only; **unverified** = not confirmed by source code, docs and measurement together.

## Documentation
- Sollumz docs 2.9 (docs.sollumz.org): collisions.ybn (Flag Preset "very common mistake"), fragments.yft + bone-physics + collision-physics + prop-setup (Dynamic for physics), drawables.ydr + LOD editing, drawable-dictionary.ydd (no embedded collision), texture-dictionaries (HD `+hi`), archetype-definition.ytyp + archetype-flags, maps/entities + lod-hierarchy, lighting, FAQ (UVMap 0, vertex colour, power-of-two DDS, max 2048), tutorials creating-props / static-collisions / static-meshes. The ycd page is a TODO.
- Sollumz source `main` @ 2026-11-06 (release v2.9.0, 2026-08-04): `ytyp/properties/ytyp.py` (SpecialAttribute enum and labels, default lod_dist 200 / hd_texture_dist 100), `ytyp/properties/flags.py` (ArchetypeFlags), `ybn/gta5/presets/flag_presets.json`, `ybn/collision_materials.py` (densities).
- Cfx fivem-docs master @ 467b2f3 (2026-11-04): assets-manual beginner series part 1–9 (part 3 shaders/vertex colour, part 4 ymap + manifest generator, part 5 collision, part 6 LOD, part 7 animation, part 8 doors — page says Garage Door (5) for the vertical door, see doors-fragments-animated.md), scripting-reference resource-manifest (globbing, data_file, this_is_a_map, lua54 deprecated), game-references data-files (DLC_ITYP_REQUEST = PERMANENT_ITYP_FILE), developers legacy-vs-enhanced (stream_enhanced loaded instead of stream), server-manual asset-escrow (Lua/YFT/YDD/YDR, escrow_ignore).
- citizenfx/natives: CreateObject (doorFlag), CreateObjectNoOffset, AttachEntityToEntity, GetPedBoneIndex, PlayEntityAnim, AddDoorToSystem.

## FiveM source (citizenfx/fivem master)
- `code/components/gta-streaming-five/src/LoadStreamingFile.cpp` — `ParseBaseName` + `CfxProxyItypMounter::LoadDataFile`: DLC_ITYP_REQUEST finds the ytyp by file stem only.
- `code/components/citizen-server-impl/src/ResourceStreamComponent.cpp` — `ConvertRSC7Size`, 16 MiB warning, 48 MiB "Oversized assets can and WILL lead to streaming issues".
- `code/components/citizen-resources-gta/src/ResourcesTest.cpp` — `this_is_a_map` adds `RELOAD_MAP_STORE` only.

## File layouts (for `rsc_probe.py`)
- CodeWalker (dexyfex/CodeWalker) `Texture.cs`, `Drawable.cs`, `Meta.cs`, `MetaNames` (CMapTypes 3649811809, CBaseArchetypeDef 2195127427, CMloArchetypeDef 273704021). Offsets checked against CodeWalker.Core output on prop_table_06 (620/136 tris), apa sofa (4047), prop_tree_birch_02 (5298/1630), prop_pots.ytd (15 textures), and the user's wood_table ytyp/ydr (drawable bounding radius equals archetype bsRadius).

## Measurements
- 28 vanilla props (table in lods-textures-budgets.md): archetype lodDist/flags/special attribute/bsRadius, drawable triangles per LOD and LOD distances, textures, embedded bounds. Script `prop_budget.ps1` (research scratchpad, needs CodeWalker.Core + game keys).
- Searched x64*.rpf/update.rpf for the physics dictionaries vanilla ydr props name (`v_minigame`, `prop_ld_tools`): no such files.
- User's resources (read-only): wood_table, wood_table_v2 (built 2026-10-31 by "Ha.i prop_build.py", Poly Haven CC0), lp_elevator, cylex_animmenuv2, pillbox; FXAP magic on `mods\Clother\...\cfx_onx_mp_faces\stream\*.ydd`.
- Upstream rpemotes-reborn master fxmanifest (`stream/brummie_props.ytyp` vs file in `stream/[Props]/Brummiee/`).

## Videos (original English captions read; timestamps cited in the references)
| id | title / channel / date | used for |
|---|---|---|
| -24PBSYT74w | Basic prop tutorial for simple collisions — Bumpy86_x, 2025-08-18 | primitives, Poly Box, scale 1, extents ≥ 0.01, materials/flags, transforms, snap origin |
| ApaaGSSziUw | Basic YFT Fragment Prop Tutorial — ook_3D, 2024-11-12 | fragment steps, Copy Transforms, Dynamic |
| LI_eCB2JVgo | yft fragment / breakable props — FivemMloGuy, 2025-02-07 | bone hierarchy, Child Of, Set Mass |
| r4b13tw4IVg | Embedded collision — FivemMloGuy, 2025-02-05 | (Static flag advice, contradicted by vanilla) |
| 9e9e9S3hMMU | Embedded Collisions — ook_3D part 7, 2023-10-27 | Flag Preset on BVH, physics dictionary |
| c8gAgKEFDtw | Embedded LODs — ook_3D part 10, 2023-10-27 | LOD slots, tutor distances |
| R_az2tpBhRw | Shaders And Parameters — ook_3D part 11, 2023-10-27 | normal_spec, tutor parameter values |
| hDjwchaRGfM | Custom Swinging Doors — ook_3D, 2023-10-27 | door template, collision, attribute 7 |
| ajqNHqB8mYw | Cfx beginner part 8 (doors) — ook_3D, 2026-06-10 | Copy Transforms, Sliding Vertical Door for Benny's |
| j8kZWnYZ_e4 | YDR with embedded collisions and lights — mnsb223, 2023-10-02 | vertex colour, BVH flags, light editor, entity flags |
| dfO1eQf8WE0 | Animated Prop With Collisions — ook_3D, 2024-06-19 | colliding animated fragment |
| k1uU8x0vR4Q | Breakable YFT Glass — mnsb223, 2023-09-16 | glass (unverified on Sollumz 2.9) |
| 11EXhLYfJLs | Cfx beginner part 7 (animation) — ook_3D, 2026-03-28 | UV / bone animation flags |
| m6H6tBL3CQ8 | LOD Tutorial Part 1 — Stumpy Mason, 2025-08-23 | ORPHANHD, parented LOD chains |
| UN7iaK5ADpk | Cfx beginner part 5 (collision) — ook_3D, 2026-02-04 | collision study in CodeWalker, decimate 0.15 |

Not transcribed (rate limit): lights/emissive/tint/vertex-AO videos (ook_3D eR8ij5UCjeU, jjh3foliTVQ, L8hC-Cp1tJ0; Quixotic FWd4LxlHMtI) — their topics rely on docs only. Paid or closed tools seen in search results (PROJECT X conversion tool, RAINMAD map editor, "no Blender" animated-prop generators) are not recommended.

## Open questions (unverified)
1. Door attribute 0 + Enable Door Physics (vanilla) vs Sollumz "does nothing".
2. Breakable glass on non-vehicle fragments in Sollumz 2.9.
3. Whether a spawned prop uses a same-name external `.ybn`.
4. How DLC_ITYP_REQUEST expands globs; whether `[ ]` in a glob is literal.
5. Streaming-memory console commands (names not confirmed in Cfx docs — not written into the skill).
