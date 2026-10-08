# From a downloaded or generated model to a FiveM asset

Sources: muto-ped-rig v0.3.2 README (character steps, measured limits), this repo's `fivem-mlo-housing/references/mlo-authoring.md` and `fivem-pro/references/maps-sollumz.md` (Sollumz drawables, collision, ytyp, LODs, all sourced there), `fivem-animation/references/playing-and-rpemotes.md` (streaming custom props). Budget numbers marked "rule of thumb" come from common practice, not from Rockstar. Measure them against vanilla props of the same kind (muto-atlas `/prop`, or open the vanilla `.ydr` in CodeWalker).

## Props (static objects)

### 1. Clean up in Blender
1. Import (`.glb`: File ▸ Import ▸ glTF; the importer converts glTF's Y-up to Blender's Z-up). Hunyuan3D and library models arrive at **arbitrary scale**. The `blender` MCP reports `world_bounding_box`.
2. **Scale to real size**: 1 Blender unit = 1 metre = 1 GTA unit. A burger ≈ 0.1 m, a chair seat ≈ 0.45 m high, a door ≈ 2.0–2.1 m. Apply scale (Ctrl+A ▸ Scale).
3. **Origin at the bottom centre** (where it touches the ground), so `PlaceObjectOnGroundProperly` and `ox_target` offsets behave. Front faces **-Y**, matching vanilla props (rule of thumb).
4. Delete junk: generated models often have a ground plate, floating bits and internal faces. Merge by distance, recalculate normals (Shift+N), check for non-manifold edges.
5. Rename: `prop_<server>_<thing>` (e.g. `prop_dio_burger`), lowercase, no spaces. The name becomes the model hash, so it must be unique. Vanilla uses `prop_`, `v_`, `p_` prefixes: don't reuse a vanilla name unless you mean to replace it.

### 2. Reduce to a budget
Generated meshes are dense and uneven (Hunyuan3D's default `face_count` is 40,000), library models vary.

| Object | Triangles, LOD0 (rule of thumb) |
|---|---|
| hand-held (food, phone, bottle) | 300 – 2,000 |
| small furniture (chair, lamp, crate) | 1,000 – 5,000 |
| big furniture / machines (sofa, ATM, vending machine) | 3,000 – 15,000 |
| hero props seen up close (car lift, display piece) | up to ~30,000 |

- Quick: Decimate modifier (Collapse), then fix the UVs if they break. Better: retopology (`retopology` skill, ask first).
- Hunyuan3D shape-only output has **no UVs**. Unwrap before texturing (`uv-workflow`); a mesh without UVs also bloats the file.
- AI meshes are often **triangle soup** with uneven density. Remesh (Voxel) then Decimate gives cleaner results than Decimate alone.

### 3. Textures
- Sollumz needs **power-of-two** sizes (256, 512, 1024, 2048) and converts to **DDS**. Hand-held props: 256–512 px; furniture: 512–1024; big props: 1024–2048. Avoid 4K on props: it costs VRAM for every player.
- One material per prop where possible (Sollumz shader `default.sps`, or `normal.sps` with a normal map, `spec.sps`/`normal_spec.sps` for shine). Generated PBR maps: base colour → diffuse, normal → normal map; roughness/metallic need converting to GTA's specular map (rule of thumb: invert roughness for the spec map's intensity).
- Bake the generated texture onto your clean UVs if you remeshed (`texture-workflow`).
- Put textures in a `.ytd` named like the drawable, or embed them. Several props sharing one `.ytd` saves memory.

### 4. LODs and distance
- Sollumz Drawable has High / Medium / Low / Very Low slots. Small props usually need High plus one lower level. Halve the triangles and textures per step (512 → 256 → 128, as in `maps-sollumz.md`).
- `lodDist` in the `.ytyp` archetype sets the draw distance. Small props ~30–60 m, furniture ~60–100 m, big props more (rule of thumb). A huge draw distance on many props hurts FPS.
- `lod-pipeline` / `asset-optimization` can automate this (ask first).

### 5. Collision
- Make a **separate simple mesh** (a few boxes or a low-poly hull), not the render mesh.
- Sollumz: convert it to a **Bound Composite** with child Bound Box / Bound Poly, tick "Apply flag preset", and set a **collision material** (wood, metal, concrete…) so bullets and footsteps sound right. Without a flag preset, collision silently doesn't work.
- Don't use `UCX_` names (that's Unreal); Sollumz bounds only. muto-atlas `trunk/flags.md` lists the flags.
- Hand-held props attached to a ped (food, phone) need no collision.

### 6. Export
1. Select the mesh → **Sollumz Tools ▸ Drawable ▸ Convert to Drawable** (mesh goes to the High LOD); convert materials to Sollumz shaders; parent the Bound Composite under the Drawable.
2. **Archetype Definition** panel → new YTYP (e.g. `dio_props`) → select the drawable → type **Base** → *Auto-Create From Selected*. Check name, `lodDist`, texture dictionary.
3. Sollumz ▸ Export (objects visible) → `.ydr.xml`, `.ytyp.xml` (and `.ytd` folder). Drag them into CodeWalker's RPF Explorer to get binaries.

### 7. Ship
```
dio_props/
  fxmanifest.lua
  stream/
    prop_dio_burger.ydr
    prop_dio_burger.ytd
    dio_props.ytyp
  CREDITS.md
```
```lua
fx_version 'cerulean'
game 'gta5'
data_file 'DLC_ITYP_REQUEST' 'stream/dio_props.ytyp'
```
Spawn test (client):
```lua
local model = `prop_dio_burger`
lib.requestModel(model)            -- ox_lib; or RequestModel + wait for HasModelLoaded
local c = GetEntityCoords(cache.ped)
local obj = CreateObject(model, c.x, c.y + 1.0, c.z, false, false, false)
PlaceObjectOnGroundProperly(obj)
SetModelAsNoLongerNeeded(model)
```
If it's invisible: check the ytyp is loaded (`data_file`), names match exactly, the binaries (not XML) are in `stream/`, and the textures are found (pink/white = missing `.ytd`). Hand-held: `AttachEntityToEntity(obj, ped, GetPedBoneIndex(ped, 28422), …)`. `GetPedBoneIndex` takes the bone **tag**: 28422 = `PH_R_Hand` (right prop holder), 60309 = `PH_L_Hand`, 57005 = `SKEL_R_Hand` (`fivem-animation/references/skeleton-and-authoring.md`). Use `fivem-animation` for the holding animation.

For **placing props in the world permanently** (ymap) or inside an interior, continue with `fivem-mlo-housing`.

## Characters (add-on peds)

Generated or downloaded people have the wrong skeleton. **muto-ped-rig** (GPL-3, Blender 4.2+, Sollumz 2.9; ask first, it installs a Blender extension) fits them to the real 128-bone GTA skeleton:

0. **Remove Existing Rig** (Mixamo/Sketchfab rigs) → **Fix Orientation/Scale** (faces -Y, metres; heights outside 0.8–3 m become 1.8 m).
1. **Auto Markers**, drag spheres if needed. Select only the body (a held weapon confuses the height).
2. **Fit Skeleton** → 3. **Compute Weights** → 4. **Convert to GTA Rest Pose** → **Validate**.
5. **Export to Sollumz + Test Resource**: head/uppr/lowr drawables, `<ped>.ytd`, `.ymt`, `.yft` + `.ydd`, and a test resource with a spawn command.

Before rigging an AI-generated character:
- **Decimate first.** muto measured ~25 KB of RAM per vertex in the weight step (233k vertices → 2.8 min, 5.8 GB). Aim for 20k–60k vertices.
- **Unwrap UVs.** Without them the `.ydd` grows ~4× (muto's measurement).
- A-pose works best, T-pose is supported. Hunyuan3D usually copies the pose of the input picture, so use an A-pose or T-pose image of the character, arms away from the body.
- Hands and faces from image-to-3D are rough. muto's Hand/Face Templates fit vanilla bones; expect to fix fingers.

Then animate it with `fivem-animation` (Mixamo clips go through muto's retarget, `fivem-animation/references/mixamo-to-gta.md`).

## Checklist before it goes on the server
- [ ] Real-world scale, origin at the base, faces -Y
- [ ] Triangles within budget for its size; LOD present for anything bigger than a hand-held prop
- [ ] Power-of-two textures, ≤ 2048, in a `.ytd`
- [ ] Simple collision with a flag preset and material (static props)
- [ ] Unique lowercase name; `.ytyp` with sensible `lodDist`; `DLC_ITYP_REQUEST` in the manifest
- [ ] Binaries in `stream/`, XML and source files kept outside
- [ ] `CREDITS.md` with source, author, licence
- [ ] Spawned and checked in game (and resmon after spawning many)
