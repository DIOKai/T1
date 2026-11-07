# Cloth physics, UVs, vertex colours, textures and modeling extras

Researched 2026-11-08. Adds to `clothing-step-by-step.md` (Druu-based). Citations: YouTube id [mm:ss] or URL. "(unverified)" = one source or inference. "(paid)" = do not recommend.

## 1. Cloth physics (YLD)

Bumpy86, YVk_rkkKS6o, building with grzyClothTool (free):
- Make a **separate cloth mesh** covering only the part that should move (a coat tail, a skirt flap). The **top row is pinned**; do not put pinned-only rows in the cloth group ([13:48–14:58]).
- The exporter allows at most **254 cloth vertices** (255 limit, one spare) ([16:08]).
- Mass per vertex baseline 0.0225; pinned vertices get pin radius 0 ([16:42–17:15]).
- Use **no more than about 6 distinct pin-radius values** and no fill gradient ([17:52]; his empirical finding).
- Vertices outside the binding boxes export with red-cube errors; move them back inside ([21:28–22:41]).
- **An unpinned top makes the piece fall forever and sometimes crashes the game** ([27:56]).
- CodeWalker does not render the cloth part; test in game ([45:05]).
- In grzyClothTool assign the cloth file per drawable ([46:54]). It is streamed as `<same base name>.yld` next to the `.ydd`, and the YMT gets `clothData.ownsCloth = 1` (BuildResourceHelper.cs 874).
- DCT page (not read in detail): https://docs.gta.clothing/cloth-modding/cloth-physics-yld.md
- Physics is extra, not a substitute for skin weights. Test what happens when it fails to load.

## 2. UV maps

- Components: **UVMap 0 = textures, UVMap 1 = blood and tattoo overlays** (uBBHJ4vG4fM [14:28]). That is why both maps must be kept with their names.
- Props: one UV map only (UyXC-6PEbkg [8:16]).
- Re-texturing an existing item: export its YTD as PNG in OpenIV/CodeWalker and read the layout (front panel, back panel, sleeves; blank areas unused), paint, re-import, check (5UhBgr9TsrM [13:51–17:44]).

## 3. Vertex colours: what the values mean

Keep the DCT/Sollumz values (https://docs.gta.clothing/cloth-modding/vertex-colors.md): **Color 1 (`colour0`) `#FF8000` alpha 1, Color 2 (`colour1`) `#000000` alpha 0.**

Why:
- Anurag: Color 2 **RGB white = moves with wind, black = no wind**; Color 2 **alpha white = sweat, black = none** (uBBHJ4vG4fM [15:34–16:42], using the Sollumz Vertex Painter). So any colour in Color 2 gives wind shake or an oily shine.
- Desertos: "illumination" (= colour1) 0,0,0 so the garment does not shake; colour0 255,128,0 (ey_YiqZoMOQ [36:06–37:13]).
- Bumpy86 says colour 1 alpha 0 (YVk_rkkKS6o [8:32]). That conflicts with Druu, Sollumz and DCT; treat it as a mis-speak.
- DCT: do not use Sollumz "Add Missing" for colour attributes, because it does not assign the clothing colour. Use `+` and set them manually.

## 4. Texture compression and size

ba86DBN396k [33:16–40:29] (DCT video; the facts are format facts, not tool-specific):

| Format | Use |
|---|---|
| BC1 / DXT1 | no alpha, widest support. On **mostly black fabric it shows green/purple blocks** |
| BC3 / DXT5 | with alpha |
| BC7 | high quality, DX11 only (his claim; BC7 is a DX11 format), slow to encode. Use for dark fabric |

- Always generate mipmaps.
- 1024 is what most servers use; 2048 only if quality really needs it; avoid 4096. Desertos: never 2K/4K, use 1024 or 512 (ey_YiqZoMOQ [32:05–32:40]). Skin (`_r`) diffuse ≤ 512 (Druu; DCT).
- Square preferred; rectangular power-of-two allowed (512×256 yes, 768×512 no).
- Embed normal and spec in the YDD; **never embed the diffuse** (uBBHJ4vG4fM [10:25]; ey_YiqZoMOQ [35:32]; Gu1vkyzbCy4 [9:58]). Variants are one diffuse YTD per letter sharing the embedded normal/spec.
- A missing embedded specular is flagged by DCT and can only be fixed in Blender (ba86DBN396k [45:57–46:31]).
- grzyClothTool shows a warning icon on textures above its size setting (AEy2Rr66l40 [2:10]).
- The checker cannot read texture formats inside a YTD (compressed resource). Check in CodeWalker's texture viewer.

## 5. Making the garment (free routes)

**Sewing from a 2D pattern** with Blender's built-in cloth sim:
1. Half pattern with a Mirror modifier (clipping on). Seam faces get a "seam" material; Knife (K), Bevel (Ctrl+B) (Uf03GRjvvHY [5:00–8:00]).
2. Body: **Collision** modifier. On a rigged body the **Armature modifier sits above Collision** (W9GDWKzf1mc [11:45]).
3. Cloth: Quality Steps 12, **Shape > Sewing** on, Self Collision on (Uf03GRjvvHY [9:40–11:34]; distance values garbled in captions).
4. Lower collision outer/inner thickness so it does not float; raise friction to about 10 if it slides (W9GDWKzf1mc [13:20–20:00]). Apply scale before simulating ([22:31]).
5. Solidify and Subsurf ([15:30–16:34]), then apply, retopologise, and continue with weights and LODs.

**Sculpt mask extract** (mojoGameDev FdD-wY_-s2w [0:00–3:18]): Lasso Mask (X symmetry) → Sharpen Mask → Extract Mask (solid off) → remesh with the free **QRemeshify** add-on → Smooth Vertices, Inflate against poke-through, Solidify about 0.02 → stitches extruded along normals → folds painted into the normal map with the free **Ucupaint** add-on. Check both add-ons' licences before recommending (unverified).

**Manual retopology** (Gamedev Fred Hz1_SndKKwU [0:00–7:38]): plane with face snapping + Mirror (clipping) + Displace to float off the high poly; **loops around the shoulder first, more than you think**; arms raised give a cleaner armpit; triangles are fine where nothing deforms; folds go in the normal map.

**Paid (do not recommend)**: Simply Cloth, Simply Stitch, Divine Cut, Cloth to Shape Keys, Retopo Planes, Laces Generator, Belt Maker, Procedural Torn (Blender Market; u82mSkQhhTI), Marvelous Designer.

Donor choice: pick a vanilla item of similar shape on tobii.space (open front, long sleeves…) (ey_YiqZoMOQ [5:00–6:05]). Apply all transforms (Ctrl+A) and reduce the material to plain image nodes before conversion (uBBHJ4vG4fM [0:31–1:05]).

## 6. Weights: alternatives and testing

- Transfer Weights panel: Druu says Destination "By Name" (the skill's Source = All Layers is an inference); Anurag says "source layer option to by name, destination all layers" (uBBHJ4vG4fM [5:16]). They conflict; read the operator labels in the installed Blender and pose-test. Then Smooth, Iterations 2 (uBBHJ4vG4fM [6:21]).
- Alternative: **Data Transfer modifier** → Vertex Data → Vertex Group, **Nearest Face Interpolated**, Mix Replace, factor 1; apply, then **Remove Unused Vertex Groups** (YVk_rkkKS6o [3:48–4:25]).
- Better deformation test than rotating bones: export the real clip `move_f@generic` from CodeWalker as XML, import it with a target skeleton, **Apply Clip to NLA**, untick the root-motion track to run in place, and weight-paint while it plays (UyXC-6PEbkg [15:56–17:35]). grzyClothTool's 3D preview can also play animations (ba86DBN396k [49:56–50:30]).
- Clipping fixes: a Lattice modifier (Blender equivalent of the 3ds Max FFD used in ey_YiqZoMOQ [51:28–52:41]).

## 7. Sollumz conversion, LODs, export (newer Sollumz)

- Shader **ped** (`ped_alpha` for transparent parts). With 3ds Max/GIMS a missing ped shader crashed (ey_YiqZoMOQ [34:57]); unverified for Sollumz.
- **Create Drawable > Convert to drawable model**, then **LOD Tools > Generate LODs** (reference mesh, Medium + Low, decimation step default 0.6), or put a manually decimated mesh in a LOD slot (uBBHJ4vG4fM [11:00–13:21]). Move the new drawable model under the imported drawable and delete the vanilla mesh ([13:21–13:54]).
- Polygon guidance (none official): DCT warns above 60,000 (ba86DBN396k [48:46]); Desertos thinks a jacket over 17k is a lot, LOD chain 10k / 5k / 1.5k (ey_YiqZoMOQ [24:35–29:09]). Compare with a vanilla item of the same type.
- Export: current Sollumz **File > Export > RAGE Asset** with **CW XML + Gen8 only** for the Legacy XML pair (https://docs.gta.clothing/cloth-modding/exporting-and-validation.md); older versions say Export > Codewalker XML.
