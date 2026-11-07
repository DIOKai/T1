# Image → FiveM prop (6DQTDMM-6CQ, from frames; generator mapped to free Hunyuan3D)

1. **Generate (free):** run Hunyuan3D 2.x on the user's PC through the `free-3d-assets` skill (its `hunyuan3d_client.py`), with **Inference Steps ≤ 20**. Ask before starting the server. Hunyuan3D's license does not cover the EU, UK or South Korea. Feed it a clean single-object image on a plain background. *(The video used Meshy: Upload image > Model Type Standard > Generate, 0:18–0:48. Its output was **Topology Triangle, 592,099 faces / 324,725 verts**, from frames 0:48. Expect Hunyuan output to be similarly dense and all triangles.)*
2. **Save the generated textures:** in the Shading tab, save each image (diffuse, normal, roughness) with Image > Save As to a `textures` folder (1:30–1:54). Packed GLB textures are otherwise lost on XML export.
3. **Match scale to a vanilla prop:** import a similar vanilla GTA prop through Sollumz. He kept project folders `textures / 3d model / GTA5 Prop / image / ready stream file / exports` (2:06) and imported **`ch_prop_box_ammo01b`**. Scale the AI mesh to the same size, put it on the ground at the origin, and apply scale (2:18–2:42). This also gives a triangle-count benchmark.
4. **Clean up / reduce (the video skips this; it shipped about 590k faces, which is a big mistake for a prop):**
   - Merge by Distance, delete loose and internal parts, Recalculate Normals.
   - Flat manufactured objects: Limited Dissolve, or better, **rebuild a clean low poly** from primitives using the AI mesh only as a guide (section 2 methods).
   - Organic or irregular objects: Decimate (Collapse), then check the silhouette. Forum experience is that decimate alone breaks down past about 50 %.
   - Smart UV Project or seams on the low poly, then Cycles **Bake Selected to Active** (diffuse, normal, AO) from the AI high to the low.
   - Pick the triangle budget by comparison with the vanilla prop of the same size. Don't invent a universal limit.
5. **Sollumz conversion** (3:06–3:24):
   - Sollumz Tools > Drawable > Create Drawable Objects > **Convert to Drawable**, with **Auto-Embed Collision** and **Center to Selection** ticked (from frames).
   - Resulting hierarchy: `prop_x` (Drawable) > `prop_x.col` (Bound Composite) > `prop_x.model.bvh` > `prop_x.model.poly_mesh`, plus `prop_x.model` (the visual model).
   - Use a low-poly mesh or Bound Poly Box/Capsule primitives for collision, never the 590k mesh. Sollumz docs recommend primitives.
6. **Collision material and flags** (3:30): Collisions > Create Collision Material. He picked a wood material (WOOD_SOLID_MEDIUM-style list, from frames) > Convert to Selected. Also apply a **Flag Preset** to the BVH. The Sollumz docs call a missing flag preset "a very common mistake" that leaves the collision dead in game.
7. **Vertex colour and shader** (3:48–4:24): the Vertex Painter filled white, and a Color Attribute was added (GTA shaders read vertex colour, so black vertex colour darkens the prop). Convert the material to a Sollumz shader (NORMAL/normal_spec: DiffuseSampler, BumpSampler) and load the saved PNGs.
8. **Archetype** (4:36–4:48): Archetype Definition > create YTYP > Archetype **Auto Create From Selected**, flags set (Static ticked, from frames). Then Export ytyp.xml, or use Export CodeWalker XML with "Export with ytyp" ticked (Sollumz docs).
9. **Export and convert** (4:48–5:30): output is `prop_x.ydr.xml`, `prop_x.ytyp.xml` and a texture folder.
   - He built the YTD with the third-party **Folders2YTD (MrVicho13) v0.4.0.2**: PNG → DDS → `prop_x.ytd`.
   - Free alternative inside Sollumz: Shader Tools > "Set all Materials Embedded", so the textures live in the YDR.
   - Use power-of-two texture sizes.
   - He then used CodeWalker RPF Explorer in Edit mode to import the XMLs into a mod RPF and previewed the ydr. In his preview it rendered dark/untextured, a sign of a missing YTD link.
10. **Test** (5:42–7:00): CodeWalker world view with Enable Mods/DLC on, the prop seen next to vanilla props for scale.
    - For FiveM: put the `.ydr`, `.ytd` and `.ytyp` in `stream/`, and add `data_file 'DLC_ITYP_REQUEST' 'stream/prop_x.ytyp'` (fxmanifest pattern already in `fivem-prop-creator`). Place it with a YMAP + `_manifest.ymf` (Sollumz static-mesh tutorial) or spawn it with CreateObject.
    - Walk into it to test collision. The fxmanifest step is not shown in the video; it is in the author's paid ebook.

After step 10, package and accept the prop with the `fivem-prop-creator` skill (fxmanifest, YMAP placement, collision walk test).
