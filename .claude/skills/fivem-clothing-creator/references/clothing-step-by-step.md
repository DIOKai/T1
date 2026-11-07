# FiveM freemode clothing: concrete step-by-step

Click-level workflow distilled 2026-11-08 from the videos and docs below (transcripts via yt-dlp; silent parts from frames). Numbers marked as someone's habit (e.g. D's blue-channel fill) are habits, not rules — compare with a vanilla texture first. Durty Cloth Tool is paid; the free route is YMTEditor + a hand-written meta (§11).

## Sources

- **[D] Druu, "Making custom clothes/ytd/ydd for FiveM"** (Pl703WrlCnE, 1:19:19, Blender 4.0.2 + Sollumz + CodeWalker + Photoshop CS3 + Materialize). Full transcript plus about 25 frames at key timestamps. Cited as `D mm:ss`.
- **[T] twobidona, "Creating Clothes in Blender"** (OGSo28XLkHM, 8:02). The audio is only song lyrics, so everything here comes from 48 frames. It is general Blender garment modeling on a stylized body, not GTA, so use it for modeling technique only. Cited as `T mm:ss (from frames)`.
- **[S] Sollumz, Basic Clothes Editing:** https://docs.sollumz.org/tutorials/basic-clothes-editing
- **[DCT] Durty Cloth Tool docs:** https://docs.gta.clothing/ (index at /llms.txt). Pages used: game-mechanics/game-limits-and-crashes, drawable-types-and-textures, skin-tone-data; cloth-modding/levels-of-detail, rigging-and-weight-painting, textures-power-of-two; basics/essential-knowledge/high-heels.
- **[CFX] Cfx forum, "[How-To] Stream clothes and props as addons, for MP Freemode models":** https://forum.cfx.re/t/how-to-stream-clothes-and-props-as-addons-for-mp-freemode-models/3345474

## 0. Tools

- Blender 4.x with Sollumz. D installs Sollumz by copying the add-on folder into `%APPDATA%\Blender Foundation\Blender\<ver>\scripts\addons` when Preferences > Install fails (D 2:44–3:09).
- CodeWalker latest release, from the CodeWalker Discord #releases. Start GTA V once before CodeWalker's first load (D 4:48).
- An image editor that writes DDS (DXT1/DXT5) and edits alpha. D uses the free Photoshop CS3 with the NVIDIA DDS plugin. Free alternatives such as GIMP or paint.net with DDS support are my suggestion, not tested by D.
- Materialize (free) for height to normal maps (D 1:53, 55:50).
- Durty Cloth Tool (DCT) for building packs. **The licensed version costs about €10/month.** The free version allows one 3D preview per launch and no animation preview (D 72:40–73:27). The free manual route is YMTEditor plus a hand-written meta (see §11), and [CFX] also mentions the author's grzyClothTool (licence unverified). Following T1 rules, do not recommend the paid licence.

## 1. Export the base assets from CodeWalker (D 3:33–6:47, S steps 1–3)

1. Use https://tobii.space (opens in Chrome) as a visual gallery to pick a vanilla component and note its file name (D 3:59). [S]: it is missing some newer DLCs.
2. In CodeWalker RPF Explorer, search `mp_f_freemode` or `mp_m_freemode` and sort by Name/Type. Turn on **Edit mode**, right-click the `.ydd`, choose **Export XML…** and pick a folder (D 5:34–5:58). Exporting the YDD also writes a subfolder with its **embedded normal and specular** textures (D 8:52; S).
3. Export the matching **`.ytd` diffuse** the same way (for example `jbib_diff_007_a_uni.ytd`; it unpacks to a folder containing the `.dds`) (D 6:20; S).
4. Export a nude **lower body, bare arms (uppr), bare feet and a head**. The head lets you check the neck seam (D 6:20–6:47).
5. Export the **skeleton**: `mp_f_freemode_01.yft` or `mp_m_freemode_01.yft`, found in `x64v.rpf\models\cdimages\streamedpeds_mp.rpf`. Place its `.yft.xml` in the **same folder** as every `.ydd.xml` you will import (D 8:00–10:07; S).
6. [S]: each DLC has an original folder plus patchday folders. For real work, take the newest patchday version.

Folder per piece: `xxx.ydd.xml` + `xxx\` (embedded normal/spec) + `xxx_diff_..._a_uni.ytd.xml` + `xxx_diff_..._a_uni\` (diffuse) + `mp_?_freemode_01.yft.xml`.

## 2. Build the test body in Blender (D 10:07–16:07)

- Use **File > Import > Codewalker XML** (or the Sollumz tab: Drawables > Import XML). In the side panel, under **Drawable Dictionary**, tick **Import External Skeleton** (frame D 10:25). [DCT] calls this option "Auto" in newer Sollumz versions. Without it, the mesh imports with no weights.
- Check that the vertex groups have bone names (for example `SKEL_L_Hand`). Names like `UNK.001` mean the YFT was not next to the XML [S].
- Sollumz hierarchy: Drawable Dictionary armature (`jbib_003_u`) > Drawable (`jbib_003_u.001`) > mesh `SKEL_ROOT` (LOD meshes `SKEL_ROOT_high`, `.001`, `.002`). **Keep the Sollumz material.** D found that deleting it and re-adding a Sollumz shader breaks things (D 12:05). **Keep both UV maps and their names** (`UVMap 0`, `UVMap 1`) and the vertex groups (D 12:30).
- For a posable test body, move every body mesh under one armature and point each Armature modifier at it (D 13:45). If the head misbehaves, import the head with its own skeleton (D 14:33).
- Load the diffuse with **File > External Data > Find Missing Files** and point it at the diffuse folders. If a mesh still lacks its diffuse, set it in Sollumz **Texture Parameters > DiffuseSampler** (D 15:20–16:07; S). A pink mesh means the diffuse is missing.
- Viewport: Texture color with MatCap or Studio lighting [S]. **Turn on Backface Culling.** GTA draws front faces only, so holes show up only with culling on [S].

## 3. Get a garment mesh

**3a. Converting another game's mesh (D 16:26–27:22).** This only applies with written permission: check the creator's terms of use and credit them (D 16:31–19:15). For Sims 4, Sims 4 Studio exports the mesh at **LOD 0**. Open the `.blend` in its old Blender, delete the camera, lights and the Sims body, and export FBX. Then:
- Import the FBX into the GTA body file and delete leftover body faces (L to select linked). If you cannot tell body from garment, plug the diffuse into Color and Alpha (D 24:26–25:41).
- **Remove all vertex groups** (the old weights).
- **Rename the UV map to the GTA name** (`UVMap 0`) and delete any extra map (D 26:31–27:22).
- **Arm pose fix (D 38:03–40:11):** do not drag sleeves with proportional editing. Pose the *source* armature's bones until the arms match the GTA A-pose. Apply the Armature modifier, then use **Parent > Clear and Keep Transformation** and delete the rig. You can scale the whole source armature to resize the garment, which D finds more accurate than scaling in Edit Mode.

**3b. Modeling from scratch (T, from frames).**
- Duplicate a region of body faces (Shift+D, P > Selection), or start from a plane. Modifier stack: **Mirror** (Axis X, Clipping on, Merge 0.001 m) > **Subdivision** (Catmull-Clark, Viewport 2 / Render 2; 1/2 on the shoe) > **Shrinkwrap** (Wrap Method Nearest Surface Point, Snap Mode **Above Surface**, Target = body, **Offset 0.001 m**) (T 0:20, 5:10–5:30).
- Extrude edge loops down the body (E repeated) and cut with the Knife (K). Model collars, waistbands, cuffs, straps, buttons and bows as **separate objects**, and mark seams red on panel borders (T 1:30–4:40).
- For ruffles and folds, use **Multires** (Viewport/Sculpt/Render 3) with the **Inflate/Deflate** brush (radius about 28 px, strength 0.5) and the **Cloth** brush (Deformation Grab, Force Falloff Radial, Cloth Mass 1.0, Damping 0.01, Simulation Area Local) (T 6:17–6:40).
- Bake the detail onto the low mesh: New Image **2048×2048** (Alpha on), Cycles **Bake Type Normal, Space Tangent, Selected to Active, Cage** on with a cage object, Target Image Textures, Clear Image (T 6:56–7:20). For GTA, that baked normal becomes the **embedded bump** texture.
- Straighten UV strips (ruffles, bands) with the **UV Squares** add-on (To Grid by Shape / To Square Grid) (T 5:00).

## 4. Fit to the freemode body (D 27:48–37:23)

- Edit Mode: select all, move and scale roughly. For straps and other local parts, use X-ray plus **Proportional Editing** (O) with G/S.
- **Sculpt Mode: use only Grab, Snake Hook, Elastic Deform and Blob.** Inflate/Draw can tear the mesh apart, especially if Merge by Distance was not run. Use **X symmetry**, a **small radius** and **single clicks rather than long drags** (D 30:36–34:55). Switch symmetry off for asymmetric areas, and fall back to vertex editing for tight spots.
- **Fit to the vanilla base body**, not a custom body, for maximum compatibility (D 77:53).
- Leave some **"breathing room"** so the garment works with other bust/body sizes (D 29:49–30:13).
- **Minimize "hand cuts"** (the extra uppr arm variants a top needs). Shape tops so they work over a **full uppr or the ~15 base uppr** that ship with FiveM, which means fewer extra files for server owners (D 32:34–33:49).
- Shoes: fit to the base legs so they work with **tights, underwear and shorts** (D 35:45–36:33).
- Check in **solid and textured view with all textures loaded**. That is where skin poking through shows (D 36:58).

## 5. Weights (D 41:05–51:16; DCT)

1. Import a **vanilla component of the same type and similar shape** with its skeleton (D uses `jbib_003_u` for a dress). Tip: study an existing well-weighted mod of the same garment type as a reference, but do not copy it (D 41:22).
2. Select the new mesh, then Shift-select the vanilla mesh (it becomes active). In **Weight Paint mode, run Weights > Transfer Weights**. Operator panel (frame D 44:15): Data Type **Vertex Group(s)**, **Create Data** on, Vertex Mapping **Nearest Vertex**, **Object Transform** on, Destination Layers **By Name**. D says "layers by name"; Source = All Layers is my inference.
3. Run **Weights > Smooth** with Subset **All Groups**, Factor 0.5, Iterations 1 (frame D 44:30). Raise the factor if the result is blotchy.
4. A **hard seam line** usually means split vertices. Run **Mesh > Clean Up > Merge by Distance** (frame D 46:05; [S] also ticks **Sharp Edges** on every LOD), then **repeat the transfer and smooth** (D 45:41–46:27).
5. Remove stray paint, such as a random blob on the chest, by hand (D 46:51).
6. **Max 4 meaningful influences per vertex.** Sollumz exports the strongest four and normalizes. Unweighted vertices fall back to the root and look detached in game [DCT].
7. **D's merge trick (47:59–48:48):** select the vanilla mesh, invert-select its geometry and keep it, then Ctrl+J the new garment *into* the vanilla object and delete the vanilla faces. The garment inherits the correct Sollumz material, UV map names and vertex-group set. Remove the old diffuse afterwards.
8. **Test:** parent the garment to the body armature, go to Pose Mode and rotate arms, knees and spine. Look for parts that move on their own (bad weights). D mentions the familiar FiveM bug where "part of the shirt runs with you" (D 49:39–51:16).

## 6. UVs and textures (D 51:26–60:49; S; DCT)

- Diffuse: crop the source texture, paste it on a black canvas, and save as DDS **DXT1, no alpha, with mipmaps** (NVIDIA plugin: "Generate MIP maps", 11 levels; frame D 53:55). Fit the UVs by selecting all and moving/scaling the UV island onto the texture (D 54:30–55:21).
- Size: use the smallest power-of-two size that looks right. 512×256 is valid, but 500×256 or 768×512 are not [DCT]. D: do not make 4K. **Diffuse for meshes that contain skin (`_r`) must be ≤512×512** (D 78:42 correction; DCT skin-tone page).
- Normal (Bump Sampler): Materialize, height map first, then normal, saved as PNG. D then **fills the blue channel with white** before saving DDS without alpha (D 57:30). That is D's empirical habit, so check it against a vanilla `_normal_` texture before you copy it.
- Specular (Spec Sampler): D uses a desaturated diffuse with an **Overlay** fill in a material colour from the **"Specular Color Texture Guide" by Alex189** (skin, leather, metal, glowing and so on). D's spec file is `feet_spec_014.dds` (D 59:11–60:22).
- Assign the textures in the Sollumz material **Texture Parameters**: DiffuseSampler, BumpSampler, SpecSampler (D 58:22). Missing normal or spec gives a **checkerboard** in game [S].
- Embedded names keep the component prefix: `uppr_normal_000`, `uppr_spec_000`, `feet_spec_014` [DCT; S; frame D 76:40].

## 7. Vertex colours (D 60:54–63:55; S)

Delete the imported colour attributes, then add two, both **Face Corner + Byte Color**:
- `colour0` (D uses the British spelling; [S] says "Color 1"): **#FF8000, alpha max**. A wrong value gives black shading on one side.
- `colour1`: **#000000, alpha 0**. Any other value causes wind shaking or an oily, sweaty shine.
- Emissive or glowing parts: colour0 **#FFBAFF**, colour1 #000 with alpha 0 [S; the Alex189 guide lists 255,186,255].
- Shortcut: in Vertex Paint, Ctrl+X fills the whole mesh [S].

## 8. LODs (D 64:04–66:34; DCT; S)

- In the Sollumz **LODs panel** (Object Data), the slots are Very High / High / Med / Low / Very Low. Clothing uses **High, Med and Low** (frame D 65:10). Press **Shift+V** to switch the visible LOD.
- D: delete the old Med/Low, **Copy LOD** from High, then in Edit Mode select all and run **Mesh > Clean Up > Decimate Geometry**. Build Low from **a copy of Med**, not High. One frame shows Low at **Ratio 0.050** (D 66:00). D's rule: lower it "until just before gaps appear".
- [DCT]: protect the silhouette, openings, neck/hand/foot borders and weighted joints. Restore vertex colours, UVs and weights after decimation, and pose-test each LOD. Blender's vertex count is lower than the exported count because UV seams and sharp edges split vertices.
- [S]: filling holes on Med/Low is optional, but match the High silhouette (for example, delete the sleeves on every LOD).

## 9. Export (D 66:59–69:23)

- Delete the test body and keep the armature. Select the hierarchy (Outliner > Select Hierarchy [S]), then **File > Export > Codewalker XML** into a **new folder** so the originals are not overwritten.
- Export panel (frame D 68:59): Include **Limit To Selected Objects** on, Fragment Toggle LODs **Very High + High–Very Low**, **Drawable Dictionary: Exclude Skeleton** on, everything else off.
- If export fails, click the error bubble. D's usual causes are a skeleton or file-structure problem or a missing element (D 69:00).

## 10. CodeWalker conversion and preview (D 69:23–72:17)

- Drag the `.ydd.xml` and the texture into a mods folder in **CodeWalker RPF Explorer (Edit mode)**. It converts to `.ydd`/`.ytd`.
- Texture variants: right-click > **New YTD**, name it `jbib_diff_003_b_uni`, add the texture and Update. Repeat for c, d and so on, up to **26 variants (a–z)** [S; DCT].
- The CodeWalker preview is the **first troubleshooting gate**. If parts are invisible there, they usually are in game too, most often because of a Sollumz shader or material problem (D 71:31–71:53).

## 11. Component IDs, naming and packaging

**Components [DCT]:** 0 head, 1 berd (masks), 2 hair, 3 uppr (torso/arms/gloves), 4 lowr (pants), 5 hand (bags), 6 feet (shoes), 7 teef, 8 accs (undershirts), 9 task (vests), 10 decl (decals), 11 jbib (tops/jackets).

**Props [DCT]:** 0 head, 1 eyes, 2 ears, 6 lwrist, 7 rwrist. Only those five appear in the picker.

**Naming:**
- `_u.ydd` pairs with `_uni.ytd` (no skin). `_r.ydd` pairs with `_whi.ytd` (contains skin). Example: `feet_014_r` / `feet_diff_014_a_whi` (frame D 75:40).
- Skin data applies only to Body/Legs/Shoes (uppr, lowr, feet) [DCT].
- In YMTEditor, give `_r` drawables **propMask 17/19/21** [CFX].

**Category trick (D 66:59–67:26):** any category works for a top, but **footwear and leg garments must ship the matching body part** (feet or legs). That is why many downloaded skirts and pants live in the jbib/shirt slot.

**Manual pack, no DCT [CFX]:**
- Resource: `stream\` (ydd/ytd/ymt) + `mp_f_freemode_01_<dlc>.meta` + `fxmanifest.lua` with `data_file 'SHOP_PED_APPAREL_META_FILE' '<meta>'` and the meta listed in `files`.
- Meta: `<ShopPedApparel><pedName>mp_f_freemode_01</pedName><dlcName>x</dlcName><fullDlcName>mp_f_freemode_01_x</fullDlcName><eCharacter>SCR_CHAR_MULTIPLAYER_F</eCharacter>…`. Male uses `SCR_CHAR_MULTIPLAYER`.
- All names lowercase and identical across YMT, meta and files. Props use the `^` form: `mp_f_freemode_01_p_x^p_head_000.ydd`.

**Limits [DCT]:**
- 26 textures per drawable.
- 128 items per drawable type/gender as legacy guidance (FiveM sync supports 0–255). 255 usable per collection, and 256 reports zero.
- One YMT per gender per collection, and the free YMT slots per game build are few (about 3–5 on b3717–b3889).
- Shop-meta entries are global (65,520, one per item and texture).
- Asset size warnings start above 16 MiB.

## 12. Skin-containing meshes, shoes and pants (D 73:51–78:42)

- Shoes include the lower foot/ankle skin. Pants include the leg/foot joint area. Otherwise there is a hole with nothing for the shoe to join. **Check the seam against the default nude parts with no gap** (D 74:15–75:08).
- Diffuse: skin area painted with a skin texture, **no alpha** (D 75:31).
- Spec: the skin area uses the guide's skin colour, and the **spec alpha is black on skin and white everywhere else** (D 76:45–77:08).
- DCT has a "has skin tone data" checkbox. High heels need the DCT **Is High Heels** flag with Heel Height tuned in **0.1 steps** until the feet stop clipping the floor [DCT].

## 13. Testing

Test on your own local test server, not only in the DCT preview (D 73:51). Then run the existing acceptance list in SKILL.md.

## Common mistakes seen in the sources

- Forgot Import External Skeleton, so no weights or `UNK` groups, and the YDD is invisible in game.
- Deleted or replaced the Sollumz material, or renamed UV maps or vertex groups.
- Skipped Merge by Distance, causing seams and sculpt tearing.
- Forgot vertex colours (wind shake or sweat shine) or used wrong values. D admits "oops, I forgot to color the vertices" is the classic miss (D 68:37).
- Diffuse not power of two, `_r` diffuse over 512, missing spec alpha on `_r`, or skin UVs moved.
- LOD decimated until holes appear. Low built from High instead of Med.
- Shoes or pants shipped without the body part, leaving a hole at the ankle.
- Converted meshes without the creator's permission.
