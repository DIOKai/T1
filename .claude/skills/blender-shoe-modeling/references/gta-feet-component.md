# Turning a shoe into a GTA/FiveM `feet` component (component 6)

**Source data:**
1. In CodeWalker, export the **bare-feet `feet_xxx_r`** (or `_u`) you will replace, the matching **lowr** nude base, and `mp_?_freemode_01.yft`.
2. Import with **Import External Skeleton** (see `fivem-clothing-creator` → `references/clothing-step-by-step.md` §1–2).
3. Use a vanilla **shoe** of similar shape as the weight and material donor.

**Fit:**
- Model or **retopologize** the high-poly sneaker over the **freemode foot in its rest pose**. A Shrinkwrap to the foot with **Above Surface, offset 0.001 m** works for inner layers (T 5:10, from frames).
- Fit it so it works with the **default nude legs, tights, underwear and shorts** (D 35:45–36:33).
- The `feet` drawable holds **both shoes**. Keep the left/right asymmetry.
- **Keep the sole height close to the vanilla shoe you replace.** GTA does not lift the ped for a thicker sole, so a chunky sole sinks into the ground (or floats if thinner). Measure the vanilla sole bottom and match it.

**Low-poly budget:** there is **no official number**. [DCT] says to compare against a working item of the same type. A practical rule (my inference): **measure a vanilla sneaker `feet_*` High LOD triangle count** in Blender and stay near it. Then:
- Laces become a simplified strip or a block with texture and normal. Use alpha only if needed, since opaque is cheaper.
- Eyelets, perforations and stitches go into the texture.
- Remove inner faces nobody sees, but **keep an inner lining** so you can't see through the collar. GTA culls backfaces, so check with Backface Culling on.

**Bake:** high to low, normal map 1024² or smaller, power of two [DCT].
- The embedded textures are `feet_normal_XXX` and `feet_spec_XXX`. The external diffuse is `feet_diff_XXX_a_uni` (no skin) or `_a_whi` (with skin).

**Skin:**
- Low-top or sockless designs that show ankle skin must ship the **foot/ankle body part** and seam it to the default lowr with no gap (D 73:51–75:08). Name it `_r` + `_whi`.
- Keep the diffuse ≤512×512, with no alpha in the diffuse. Set the **spec alpha black on skin and white elsewhere**.
- Only enable skin data when skin is actually modeled [D 75:31–77:08; DCT skin-tone].
- Fully enclosed sneakers can be `_u` + `_uni`.

**Weights:** transfer from the vanilla shoe (Transfer Weights, Nearest Vertex, By Name, then Smooth). Keep at most 4 influences.
- The sole and toe box should be essentially **rigid on the foot bone, with only the toe-break area weighted to the toe bone**.
- The collar blends into the calf.
- Check the actual bone names in the imported skeleton (expected `SKEL_L_Foot`, `SKEL_L_Toe0`, `SKEL_L_Calf` and the R equivalents; unverified here).
- Pose-test walking, crouching and toe bend.

**Remaining gates:** run `fivem-clothing-creator` → `references/clothing-step-by-step.md` §6–10 (vertex colours #FF8000 / #000 a0, LOD High/Med/Low with the silhouette kept, Sollumz export, CodeWalker preview).

**Heeled shoes:** (DCT is paid — the free route is YMTEditor; the matching high-heel setting there is unverified, test in game) enable DCT **Is High Heels** and tune Heel Height in **0.1** steps until the feet stop sinking into the floor. Fix missing rig weights in Blender; the flag does not replace them [DCT high-heels].

**Then:** run the `fivem-asset-acceptance` checks. Test on the local test server only.
