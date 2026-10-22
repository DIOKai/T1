# Blender → glTF for a web walkthrough

Checked against the Blender 5.2 LTS manual and the glTF add-on source on 2026-10-22. Items marked 未验证 were not confirmed in a primary source.

## 1. Scene preparation
- Unit scale 1, metres. A door should measure ~0.8–0.9 m wide; if not, fix the scale before anything else.
- One mesh (or a few) **per room and per floor**. Lets the browser frustum-cull, lets you partition files per floor later, and keeps lightmap atlases per room.
- Procedural materials don't export (glTF keeps only Principled BSDF inputs); bake them to images first. Packed ORM: occlusion R, roughness G, metallic B.
- Collision shell in a collection whose objects are named `COL_*` (or have `collider` = 1): simplified walls, floors, door frames, **glass** (transparent but solid), and a single ramp over each stair run. Keep doorways open. A few hundred triangles for a flat is plenty (rule of thumb).
- Tour data as Object Custom Properties (export as `extras`): `spawn`, `yaw`, `hotspot`, `room`, `lightmap`, `lightmapIntensity`, `collider`, `nocollide`, `slot`. Empties work, but glTF-Transform's `prune` deletes empty leaf nodes unless you pass `--keep-leaves true` (see `optimize-gltf.md`).
- Custom property names: lowercase ASCII. The three.js loader puts node extras on `object.userData`; node names are sanitized (spaces → `_`).

## 2. Lightmap UVs
1. Select the room meshes, UV ‣ Unwrap ‣ **Lightmap Pack**: tick **New UV Map** (adds a second UV layer, UV0 keeps tiling material UVs), **Share Texture Space** (one atlas for several objects without overlap), set Pack Quality and Margin.
2. Check the UV layer **order** in Object Data ‣ UV Maps: the exporter writes every UV layer in list order, layer n → `TEXCOORD_n` (read from the add-on's `primitive_extract.py` on the main branch; same in 5.2 release is 未验证). The lightmap layer must be second → `TEXCOORD_1` → three.js `uv1`. A wrong order is the classic "lightmap looks scrambled" bug.
3. Not all glTF readers support multiple UV maps (manual note) — three.js does.

## 3. Bake in Cycles
- Each material needs an **Image Texture node selected as active**, pointing to the target image (one per room atlas). If a material has no active image node, nothing is baked for it.
- Which UV layer the baker uses (active vs active-render) isn't spelled out on the manual page — 未验证. Safe habit: make the lightmap UV layer active before baking, or feed a UV Map node (set to the lightmap layer) into that Image Texture node.
- Bake type:
  - **Diffuse** with only Direct + Indirect ticked (Color off) → pure lighting for approach A (`material.lightMap`).
  - **Combined** → light × albedo for approach B (baseColor + Unlit). Combined excludes specular.
  - Ambient Occlusion → optional `aoMap` (R channel, `NoColorSpace` in three.js).
- **Margin** (Extend or Adjacent Faces, several px) so seams don't appear when mipmapped.
- Bake samples/bounces follow the render settings. Denoising a bake usually needs a compositor pass (未验证 for 5.2).
- Brightness in three.js: start with `lightmapIntensity` = π (the template default; three.js divides diffuse light by π) and compare with the Blender render.
- Save 8-bit PNG for a first test; 16-bit/float EXR keeps more range but is larger and needs `EXRLoader`.
- Don't bake swappable furniture into room lightmaps. Bake furniture its own AO or use real-time contact shading (`threejs-ambient-contact-shading`).

### Unlit export (approach B)
The manual: to export KHR_materials_unlit, mix in a camera ray and avoid the Principled BSDF node. Plug the Combined bake into that setup. Cheapest on phones; swapping a material means re-baking.

## 4. Export settings (File ‣ Export ‣ glTF 2.0)
| Section | Setting | Why |
|---|---|---|
| Format | glTF Binary (.glb) — or glTF Separate to edit JSON/textures later | one file vs editable |
| Include | Visible/Selected as needed, **Custom Properties** on | extras carry tour data |
| Include | Punctual Lights only for approach C | Area lights and World lighting are **not exported** (manual) |
| Transform | **+Y Up** on | glTF convention |
| Data ‣ Mesh | **Apply Modifiers** on; UVs on; Normals on | Array/Mirror/Solidify/Bevel walls |
| Data ‣ Scene Graph | GPU Instances for repeated chairs/lamps (EXT_mesh_gpu_instancing) | fewer draw calls |
| Data ‣ Material | Images: Automatic or JPEG (manual: JPEG is smaller for web); WebP has no fallback | |
| Compression | Draco off / Meshopt off here | compress once in glTF-Transform after checks |
| Lighting Mode | Standard | physical units |

Blender 5.2 added **Meshopt Compression** to the exporter (`EXT_meshopt_compression` default, or `KHR_meshopt_compression`). Fine for simple exports; for this pipeline compress later so `check_walkthrough_build.py` and `inspect` read uncompressed data first.

Material variants: enable the glTF Variants UI in the add-on preferences; 3D View ‣ glTF Variants tab: Assign to Variant / Assign as Original / Display Variant. One material slot = one glTF primitive.

Export furniture separately: origin at the bottom centre, +Y up after export, metres, one GLB per item.

## 5. After export
```bash
python scripts/check_walkthrough_build.py model.glb
```
Expect: TEXCOORD_1 on the room primitives, your spawn/hotspots/rooms listed, `COL_` colliders found. If something is missing here it was lost in Blender, not in optimization.

## Sources
- Blender 5.2 manual, glTF 2.0 add-on: https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html
- Blender 5.2 release notes (Meshopt export): https://developer.blender.org/docs/release_notes/5.2/pipeline_io/
- Exporter source (UV layers → TEXCOORD_n): https://github.com/blender/blender/tree/main/scripts/addons_core/io_scene_gltf2
- Cycles baking: https://docs.blender.org/manual/en/latest/render/cycles/baking.html
- Lightmap Pack: https://docs.blender.org/manual/en/latest/modeling/meshes/editing/uv.html
- UV order pitfall (community): https://discourse.threejs.org/t/why-is-uv-map-designed-in-blender-not-showing-up-correctly-in-gltf-glb-model-on-my-website/16988/3
