---
name: blender-vehicle-modeling
description: Use when building a car, truck, bike or helicopter model from scratch in Blender with subdivision/box modeling — blueprint setup, body blockout, edge flow, panel lines, vents, windows, lights, wheels, tires, logos, engine bay and underbody, interior (dashboard, dials, steering wheel, seats), police lightbars, extras and tuning parts — or when a vehicle mesh shows wobbly reflections, pinched holes, triangles that block loop cuts, or mushy panel gaps. Also use when such a model must become a GTA V / FiveM vehicle (yft) and needs game-ready LODs, and for 车辆建模/做车模型/从蓝图建车/直升机建模/引擎舱/底盘/内饰/仪表板/警灯/改装件. For converting an existing downloaded car mod use fivem-vehicle-mod instead.
---

# Blender vehicle modeling (cars, helicopters)

A car is judged by its reflections. Every technique here serves one goal: a minimal, evenly spaced quad cage whose highlights flow across panels without wobbles, then sharp panel gaps that do not disturb that surface. Principles live in `vehicle-artist`; this skill is the hands-on method from video courses, checked against vanilla GTA V files.

## Order of work

1. **References.** Four cropped blueprint views plus real photos of tricky parts (blueprints never agree between views — photos win). `scripts/vehicle_setup.py` `setup_blueprints(...)` places the sheets at the real car size (GTA axes: front = +Y).
2. **Blockout cage.** Either grow from the roof outward panel by panel with a Mirror (Clipping on), or trace the character lines with single-vertex extrusions and fill between them. Target a minimal base: ~1,000 verts for a whole car body before subdivision. `references/car-workflow.md` §1–2.
3. **Topology pass before any detail.** Even "grid-square" quads, matched vertex counts where surfaces meet, no triangles on curved panels (two-triangle → F, or knife + Alt+M), one ring of edges around every hole and wheel arch. §3.
4. **Reflection check.** Shiny/car-paint MatCap, orbit. Fix wobbles in the cage, not with more loops. Repeat after every big change. §5.
5. **Panel lines last.** Only after the big surface is final: close loop → two reinforcement loops → middle loop pushed in → bevel → delete strip; then extrude the borders inward for sheet thickness. §4.
6. **Components as separate objects.** Grille (array + lattice), lights (housing / clear lens / shrunken emitter), mirrors, handles, antennas (vertex group + Shrinkwrap), exhaust (curve), wheels (one spoke + radial array — `radial_array()`), tires (one tread block + Array + Curve), logos (shrinkwrapped trace). §6.
7. **Engine bay, underbody, brakes.** Complete 3D bay, continuous inner fenders, real frame/floor, exhaust, suspension; caliper on `hub_*`; hole checks with back-face culling and red-ground renders. `references/engine-bay-and-underbody.md`.
8. **Interior.** Grown from the shell: dash, `dials` render-target plane, wheel on `steeringwheel`, seats, door cards on door bones; sealed. `references/interior.md`.
9. **Materials/render** for previews only — procedural Cycles nodes do not reach GTA. car-workflow §7.
10. **Game-ready pass** if the target is GTA/FiveM: `references/gta-game-ready.md` (triangle budgets, apply modifiers, bake detail, GTA bone names, back-face culling, Sollumz shaders), then hand off to `fivem-vehicle-mod` for meta files and checks.
11. **Accessories** (police gear, tuning parts): pick the role (integrated / extra / siren / modkit part) first. `references/accessories-and-parts.md`.

Helicopters: model the mechanical core (mast, rotor head, tail rotor) as separately pivoted objects, then the skin; see `references/helicopter-workflow.md`.

## Quick reference

| Task | Setting / move |
|---|---|
| Subdivision while modeling | Viewport 2, render 3 (4 close-up) |
| Straighten a row of verts | S X/Y/Z 0 |
| Even out spacing without changing shape | Edge slide G G, LoopTools Space/Relax |
| Grille | Array ~39 + Array rows, Lattice U5 V1 W2 |
| Round lights / tips | 12-vertex cylinder; LoopTools Circle; Individual Origins scale |
| Spokes | circle verts = multiple of spokes (42 for 7); Array with Object Offset empty, or Spin 360° dupli |
| Tread | Array relative offset ~0.492 → Curve on Bézier circle; Edge Split, not SubD |
| Attach small parts to the body | vertex group of contact verts + Shrinkwrap (vertex group) |
| Bevel-weight workflow | Bevel modifier Limit Method Weight, Mirror first in stack |
| Hoses / wires | vertex path → Curve, Bevel Depth + Fill Caps, hook ends to fittings, convert to mesh |

## Common mistakes

| Symptom | Cause → fix |
|---|---|
| Wobbly highlight on a big panel | Uneven or too many loops → even out the cage, remove loops |
| Pinch around a vent/arch | No edge ring around the hole → inset/extrude a ring before deleting the face |
| Loop cut stops halfway | A triangle in the path → convert to quads first |
| Mushy panel gaps | No reinforcement loops on both sides of the gap |
| Seam at the centre line | Mirror Clipping off / Mirror not first in stack |
| Dark patches after extrude | Flipped normals → Shift+N |
| Mirrored text reads backwards | Mirror text manually (Ctrl+M), not with the modifier |
| Model looks right in Blender, holes in game | GTA culls back faces → check with back-face culling on (see `gta-game-ready.md`) |
| Brake caliper spins with the wheel | Skinned to `wheel_*` → skin it to `hub_lf/rf/lr/rr` |
| Speedo needles modelled, dash dead in game | GTA draws dials → flat `dials` plane, `vehicle_dash_emissive` + `script_rt_dials_*`, matching `dashboardType` |
| Siren lights stay on when the lightbar extra is off | Siren bones not children of the extra → parent `sirenN`/`siren_glassN` under it, give the extra a collision |
| Tuning part floats off the car | Pivot not on the attach bone → origin to bone head, Alt+G to the world origin |
| Light, extra or part does nothing in game | Bone named `misc_f.001` etc. → rename to the exact GTA name before export |

## References

- `references/car-workflow.md` — full step-by-step car method with video timestamps (blueprints, blockout, topology, panel lines, every component, materials).
- `references/engine-bay-and-underbody.md` — engine, bay parts, hoses, underbody, brakes, bay atlas, LOD budgets, the user's bay rules, hole-check tools, Silverado bay kit.
- `references/interior.md` — dash, dials, steering wheel position, seats, door cards, shaders, tint, budgets, police interiors.
- `references/accessories-and-parts.md` — lightbars, sirens, extras, tuning parts (pivot, `mod_col_N`, `turnOffBones`), custom wheels (carcols `<Wheels>` slots, `wheelScale`), small parts, checklists.
- `references/helicopter-workflow.md` — AH-6 workflow from a time-lapse, plus what to keep for a game helicopter.
- `references/gta-game-ready.md` — budgets, LOD distances, what must be applied/baked, naming, shaders, hand-off checks.
- `references/sources.md` — videos and web sources (the three part references keep their own source lists).
- `scripts/vehicle_setup.py` — `setup_blueprints()` and `radial_array()` (bpy; run through the `blender` MCP after asking).
