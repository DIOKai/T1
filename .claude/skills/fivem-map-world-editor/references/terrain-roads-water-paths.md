# Terrain, roads, collision, water, paths

Contents: 1 terrain tiles · 2 terrain blending · 3 world collision (ybn) · 4 roads and decals · 5 traffic paths (ynd) · 6 navmesh (ynv) · 7 trains and scenarios · 8 water and pools · 9 checks

Citation keys: [sources.md](sources.md). Several videos here could only be read from chapter titles (captions blocked) - those steps are marked.

## 1. Terrain tiles

Terrain is ordinary drawables (`.ydr`, often in a `.ydd`) placed by the block ymaps, plus world collision `.ybn`. Replacing terrain = overriding those files under the same names (one owner rule).

1. Find the tile in CodeWalker (select ground → archetype/ymap; Collision mode → ybn name).
2. Export ydr/ydd + ybn to XML with RPF Explorer; import into Blender with Sollumz. Record the tile's location before editing and restore it before export (ook_3D's description mentions `bpy.context.object.location`; video J_OpnSDDiQI, no captions, unverified).
3. Model the new ground; make transitions to the untouched vanilla road and pavement edges exactly coincide (EnderMods chapter "transitions with the vanilla road/sidewalk", toR0HegiteU 30:12, from chapter titles, unverified).
4. Rebuild collision to match (section 3), then the tile's LODs (the block LOD/SLOD drawables show the old ground from afar - toR0HegiteU 55:03 "LOD management", from chapter titles).
5. Export, convert with RPF Explorer, clean up the CodeWalker map (occluders: EnderMods' description says remove the OCCLUDERS when placing new buildings/MLOs), test on a local server.

Keep **|UV| < ~50**: GTA stores TexCoord0 as half floats; world-metre box-projected UVs (e.g. −240, 428) step in visible stripes. Half-float spacing is 2^(floor(log2|u|)−10): |u| 32-64 → 1/32, 256-512 → 1/4, ≥ 1024 → 1. Recentre UVs per polygon (user's `center_uvs()` in `la_puerta_towers/blender/scripts/mlo_export_common.py`) [U:gta-half-float-uvs].

## 2. Terrain blending (Sollumz)

Terrain shaders blend four texture layers using the **second colour attribute** (index 1): layer 1 = (0,0,0), layer 2 = (0,0,1), layer 3 = (0,1,0), layer 4 = (0,1,1) - green and blue select. The **first colour attribute's alpha** blends with the lookup sampler. Tools: Sollumz vertex-paint "Paint Terrain Texture" / "Paint Terrain Alpha" [SRC:sz-terrain]. Videos pqdp_sHfgxs / 7Jm74L3FfLk (ook_3D) not transcribed.

## 3. World collision (ybn)

- Three kinds per area: plain, `hi@` ("for weapon bullets") and `ma@` (procedural grass, garbage) [D:sz-ybn]. Edit all that exist.
- Hierarchy: Bound Composite → Bound GeometryBVH → Bound Poly Mesh / Poly Box / primitives. **Apply a Flag Preset to every GeometryBVH** ("a very common mistake" - nothing collides) [D:sz-ybn; D:sz-faq].
- Separate world collision: apply location (Ctrl+A), Convert to Composite, composite + BVH empties at 0,0,0, origin to geometry, rename the composite to the ybn file name; world coordinates [D:sz-col; D:cfx5]. Prefer primitives (boxes) over meshes (Stumpy Mason "Optimizing with boxes", cP1f8h5RHtA 5:51, chapter titles).
- Collision materials per surface (footsteps, bullets, tyre grip); `ma@` uses Procedural ID [D:sz-ybn].
- **More than 32 767 polygons in one BVH failed Sollumz export** on the user's server (37 292; observed, not documented) → split into several BVHs or simplify.
- Grass invisible in CodeWalker can still spawn from `ma@` procedural materials [D:sz-faq].

## 4. Roads and decals

Roads are terrain/road drawables plus decal meshes (`*_decal`, `*_detail`, `*_ov` names in the user's `sa_hd_roads`). Texture-only road packs belong to `fivem-graphics-pack` (16/48 MiB limits apply - the user's `globalroads+hi.ytd` is 92 MiB). A drawn road gives no traffic (section 5) and no collision change unless the ybn is edited.

## 5. Traffic paths (ynd)

- Path nodes live in `nodes<N>.ynd`, N = y·32 + x on a 32×32 grid of 512-unit cells starting at (−8192, −8192). Links carry AreaID + NodeID and cross into neighbour files: edit neighbours together; junctions and height maps are rebuilt on save [SRC:cw-ynd].
- CodeWalker: Project → New Ynd / edit existing; dexyfex's path tutorials (mfFe7rZn3NM, 2knoRkP09sE; chapter data only).
- FiveM streams `.ynd` from `stream/` like any other override; a 2018 forum thread confirms it works with no extra steps (not official docs - test) [D:forum-ynd]. One owner rule applies: the user's `blockz_borderv2` ships `nodes650/656-659…`.
- Street names for the pause map / postal scripts come from the nodes + `global.gxt2` (user's `survey_streets.ps1`).

## 6. Navmesh (ynv)

`navmesh[X][Y].ynv`, 150 m cells [SRC:cw-ynv]. CodeWalker v.29 added "YNV Nav mesh editing (WIP!)" and a Nav Mesh Generator [D:cw-g5m; SRC:cw-project]. Luman3D's navmesh video (BGquctFhXPc) advertises a third-party paid conflict tool - check price/licence before recommending. The user's `pio_cht` ships navmesh overrides. Ped behaviour around a new build: test in game; the generator is WIP.

## 7. Trains and scenarios

Trains: `data_file 'TRAINTRACK_FILE'` / `'TRAINCONFIGS_FILE'` + CodeWalker's train track editor [D:datafiles; SRC:cw-project]. Scenarios: CodeWalker scenario editor (dexyfex U0nrVL44Fb4, chapter data only) and `SCENARIO_POINTS_(OVERRIDE_)(PSO_)FILE` / `SCENARIO_INFO_FILE` data files [D:datafiles].

## 8. Water and pools

- `water.xml` quads are not editable in CodeWalker (render only) or Sollumz [D:cw-g5m; D:sz-features].
- FiveM loads a custom water file at runtime: put it in `files {}` and call `LoadWaterFromPath('my-resource', 'water.xml')` from a client script; `ResetWater()` restores the default; per-quad natives (`GetWaterQuadAtCoords`, `SetWaterQuadLevel`, `…Bounds`, `…Type` 0 square / 1-4 triangles, `…Alpha`, `…IsInvisible`, `…HasLimitedDepth`, `…NoStencil`) adjust quads [D:natives]. No `data_file` key exists for water [D:datafiles]. Video 2jAb5ux-ZzI shows a streaming method (not captured).
- Pools: custom water quads, or a Sollumz water drawable plus collision - Stumpy Mason's pool tutorial (zjwdHu30CyY: model prep 2:58, collision 3:55, server 11:03, water texture 12:38, CodeWalker 15:32; from chapter titles, unverified).

## 9. Checks

`check_map_resource.py` on XML exports: `BVH_TOO_MANY_POLYS`, `BVH_NO_FLAGS`, `YBN_EMPTY`, `UV_TOO_LARGE`, `NO_VERTEX_COLOUR`, `TEXTURE_SIZE`, `YND_AREA_MISMATCH` (XML format from CodeWalker source, unverified on a real export); on resources: `YND_NAME`, `YNV_NAME`, `YBN_SIBLINGS`, `WATER_XML_NOT_LOADED`. In game: drive the new road both ways at speed (wheel sink, bumps at seams), walk the edges, shoot the ground (`hi@`), watch traffic and peds for 10 minutes, look at the area from 500 m and 1 km (terrain LOD).
