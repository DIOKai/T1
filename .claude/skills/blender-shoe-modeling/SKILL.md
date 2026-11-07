---
name: blender-shoe-modeling
description: Use when modeling footwear in Blender — sneakers, boots, heels, sandals, Jordan/Air-Force-style trainers — including soles and tread, upper panels, eyelets, laces, tongue, stitching, logos, creases and leather materials, or when a shoe must become a GTA V / FiveM freemode `feet` drawable. Also use for 做鞋子模型/建模球鞋/靴子建模/FiveM 鞋子, or when shoe panels intersect, laces look fake, stitches stretch along a curve, or a game shoe is far too heavy.
---

# Blender shoe modeling

A believable shoe is layers of material sitting on one form: sole unit, stacked leather panels that never intersect, laces that pull the upper inward, seams and creases where it bends. Model the form once, then hang everything on it.

## Order of work

1. **References.** Side, top, back and **sole (bottom)** photos as reference images. Shoes are asymmetric (inner side straighter) — mirror only to start.
2. **The last (base form).** Low-poly cube blockout → Subdivision preview → support loops at heel/sole/toe → Grab-sculpt to the side view → apply Subdivision 1. This dense form is what every panel snaps to. `references/shoe-techniques.md` §1–2.
3. **Sole unit.** Outsole outline, tread circles inset and knifed into the flow, **all tread faces extruded together** (same depth), midsole extruded up, groove by pushed-in loops. Boots: integrated or separate heel. §3.
4. **Upper panels.** One object per leather panel: outline, face-snap onto the last, Solidify, Subdivision. Panels stack and tuck under each other; never intersect. Mirror a panel *before* adding support loops, snap the copy back piece by piece, join, recalc normals. §4.
5. **Collar, tongue, heel tab, logos.** Quilted tongue ribs = beveled rows scaled inward; logos as quad panels (snapping off to tuck under). §5–6.
6. **Eyelets and perforations.** Vertex bevel + inset ring, or snapped thin torus; toe perforations by boolean on a dense copy with an inner lining behind. §7.
7. **Laces.** Strip from hole to hole (or a beveled curve), pushed through eyelets; push the upper inward under tight laces; knot from duplicated segments. §8.
8. **Stitching and wear.** Sculpted Crease lines, or geometry stitches with `scripts/stitches.py` (Array Fit Curve + Curve, no stretching); Multires creases at the toe break. §9–10.
9. **Materials.** UV each panel separately, leather/fabric/rubber PBR (free ambientCG), bump noise. §11.
10. **Game shoe?** Follow `references/gta-feet-component.md`: retopo over the freemode foot, bake stitches/laces/eyelets to textures, ankle skin part when skin shows, foot-bone weights, then the `fivem-clothing-creator` gates.

## Quick reference

| Detail | Fast reliable method |
|---|---|
| Even tread depth | select all groove faces, one extrude |
| Panel on the shoe | face snapping + Solidify, Proportional Edit to separate layers |
| Clean eyelet hole | Ctrl+Shift+B vertex bevel → I inset → delete |
| Lace through hole | plane strip extruded hole-to-hole, Solidify, Grab-sculpt |
| Stitches (render) | `stitches_along(make_stitch(), seam_curve)` |
| Stitches (game) | normal-map bake, never geometry |
| Creases | Multires + Draw (Ctrl = groove) at toe break and ankle |

## Common mistakes

| Mistake | Fix |
|---|---|
| Blobby shoe under Subdivision | support loops near heel, sole edge, toe |
| Panels poke through each other | stack with offset, tuck edges under, check every angle |
| Mirrored side after support loops = mess | mirror first, loops after |
| Uneven tread grooves | extrude all tread faces at once |
| Holes look into an empty shoe | duplicate inner lining layer |
| Stitches stretch on the curve | apply rotation/scale on both, stitch starts at its origin (script does this) |
| Shipping a 200k-tri sneaker to FiveM | retopo near a vanilla shoe's triangle count, bake details |
| Real brand on a game shoe | swap for an in-game brand |

## References

- `references/shoe-techniques.md` — step-by-step techniques with source timestamps.
- `references/gta-feet-component.md` — converting to a freemode `feet` drawable (fit, budget, bake, skin, weights, heels).
- `references/sources.md` — videos and docs studied.
- `scripts/stitches.py` — geometry stitch helper (bpy; run through the `blender` MCP after asking).
