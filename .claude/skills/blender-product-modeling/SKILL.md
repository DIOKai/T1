---
name: blender-product-modeling
description: Use when modeling a real consumer product or gadget in Blender — phone, smartwatch, tablet, remote, earbuds case, controller, laptop, speaker — from spec sheets and product photos, or when such a model must become a game prop (FiveM/GTA phone prop, iFruit device, in-world gadget). Also use when the user says 建模手机/手表/产品建模, "model an iPhone", rounded-rectangle bodies, camera bump, lens rings, watch straps, or complains that a bevel looks fake, SubD looks blobby, or an AI-generated prop is far too heavy.
---

# Blender product modeling

Products are judged against the real object, so accuracy beats speed: real dimensions, crisp-but-rounded edges, correct material contrast. Two families of technique cover almost every gadget; pick by where the model goes.

## Choose the method first

| Target | Method | Why |
|---|---|---|
| Slab devices (phone, tablet, remote) for renders or quick props | **A – modifier stack**: quad plane → Bevel(Vertices) → Solidify → edge Bevel | Fast, dimensionally exact, few edges |
| Round/organic devices (watch case, earbuds, controller) or anything that will use SubD | **B – SubD topology**: primitive with enough segments → loops → bevel weights → Bevel(Weight) + Subdivision | Clean shading on curved surfaces |
| Game prop (FiveM/GTA) | Either, but finish with **low-segment bevel + Harden Normals / Weighted Normal**, never SubD | SubD watches reached 100–190k tris; props must stay near vanilla budgets |
| Only an image of the object exists | Generate with free local Hunyuan3D (`free-3d-assets`), then **rebuild or reduce** — never ship the raw mesh | AI meshes arrive ~600k triangles, all tris |

## Workflow

1. **Units and references.** Keep 1 Blender unit = 1 m (what GTA needs) and only display millimetres (`use_millimetre_display()` in the script); model at the spec size (e.g. phone 163.4 × 78.0 mm). Reference images (Shift+A > Image > Reference) are scaled to the spec outline — never scale the model to the picture. Apply rotation/scale before Mirror or Bevel.
2. **Body.** Method A or B (details and numbers: `references/techniques.md` §2). `scripts/product_body.py` builds a method-A slab body from real mm in one call.
3. **Cut-outs.** Buttons, ports, speaker holes: model the part, then a Boolean on the body using that part, so one object both cuts the slot and stays as the key. On SubD meshes keep cutters low (≈8 segments) and rebuild quads with J / vertex slide.
4. **Raised parts.** Camera plateau, lens rings (Bridge Edge Loops), screen inset (I → extrude inward), crown/buttons (Individual Origins scale for taper). §3–4.
5. **Repeated parts.** Straps, grilles, bands: build *one* module and Array it ("addition, not subtraction"); dissolve seams with Select Similar > Length; curl with Simple Deform > Bend. §5.
6. **Edge treatment.** Render: Bevel Weight 1 on sharp edges → Bevel (Limit Weight, Percent ≈10 %, 2 segments, Miter Outer Arc) → Subdivision 2. Game: Bevel 1–3 segments + Harden Normals or Weighted Normal (Keep Sharp). §6.
7. **Materials.** Name and link materials; the contrast between metal frame, black cavities, glass and screen sells it. Table in §7. Replace real logos with GTA brands (Apple → iFruit) for anything going into FiveM.
8. **Into FiveM?** Follow `references/image-to-fivem-prop.md`, then hand off to `fivem-prop-creator` for packaging and acceptance.

## Checks before calling it done

- Measure the bounding box against the spec (± 0.5 mm for products, real metres for props).
- Matcap/HDRI turntable: no pinching at boolean holes, no blobby SubD corners, normals consistent (Face Orientation overlay all blue).
- Game prop: triangle count compared with a vanilla prop of similar size; **UVs unwrapped** (a game mesh without UVs can't be textured or baked); orientation matches a similar vanilla prop (check in CodeWalker — hand-held props follow the hand bone); collision is primitives or a low-poly hull, never the visual mesh. `game_ready(body)` in the script does the UV unwrap and a box collision.

## Common mistakes

| Mistake | Fix |
|---|---|
| Modeled to image scale (0.72 m corner radius on a phone) | Millimetre units, spec dimensions, scale the image instead |
| Mirror/Bevel misbehaves | Ctrl+A rotation & scale first |
| Bevel looks fake/uniform | Width Type Percent, Miter Outer Arc, support loops closer together |
| Boolean holes pinch under SubD | Fewer cutter segments, hand-rebuilt quads, Auto Merge while sliding |
| Shading flips after extrudes | Shift+N; use Extrude Manifold |
| Raw AI mesh shipped / used as collision | Retopo or Decimate + bake, primitive collision with a Flag Preset |
| Real brand on an in-game prop | GTA equivalent brand |

## References

- `references/techniques.md` — step-by-step techniques with the source video timestamps (bodies, buttons, camera bump, straps, edge treatment, materials).
- `references/image-to-fivem-prop.md` — picture → free generator → cleanup → Sollumz ydr/ytyp → FiveM test.
- `references/sources.md` — videos and documentation this skill was built from.
- `scripts/product_body.py` — bpy helper for rounded-rectangle bodies (run through the `blender` MCP, ask first).
