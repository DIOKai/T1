# Collision, archetype flags, special attributes

## Bounds

Hierarchy (Sollumz collisions.ybn doc): `Bound Composite → Bound GeometryBVH → Bound Poly Mesh / Poly Box / Poly Sphere / Poly Capsule / Poly Cylinder`, or primitive children (`Bound Box`, `Bound Sphere`, `Bound Capsule`, `Bound Cylinder`) directly under the composite.

- **Apply a Flag Preset to every Bound GeometryBVH** (sidebar Object > Flag Presets > `General (Default)`). Sollumz: "A very common mistake users make is not applying a Flag Preset to the Bound GeometryBVH, resulting in the collision not working in game." Presets in 2.9: General (Default), General 2 (no map_weapon), Water surface, Leaves - Bush, Stair plane, Stair mesh, Deep surface.
- Primitives for most of a prop, poly mesh only where they cannot fit (Sollumz static-collisions tip; Bumpy86 -24PBSYT74w [00:46]–[01:10]: "auto embed collision" poly meshes are for shells/terrain, not props). Inside a BVH use **Bound Poly Box** + "create box from selection" ([02:46]).
- Object scale stays 1: change radius/length/extents in the Sollumz panel ([04:35], [07:49]). Extents never 0 — tutor uses ≥ 0.01 ([10:04], unverified beyond the tutor). Boxes may overlap ([05:25]). Popping/misaligned boxes after export = transforms not applied ([17:47]).
- Embedded: build the composite (or duplicate → Convert to Composite → decimate to ~0.15 for a mesh collision, Cfx part 5 UN7iaK5ADpk [06:40]), parent it under the Drawable. External `.ybn` is map collision at world coordinates (empties at 0,0,0, transforms applied); `hi@` ybn = weapons/bullets only; `ma@` = procedural grass/trash.
- Not Unreal `UCX_` names. Hand-held props attached to a ped need no collision (vanilla hand props still carry one Bound Box).

Measured vanilla (CodeWalker.Core): prop_chair_01a = composite of 17 Bound Box, prop_table_06 = 15 boxes, prop_bench_01a = 18, prop_patio_heater_01 = 1 box + 4 cylinders, prop_facgate_07b = 52 boxes, prop_gas_pump_1a = 19 boxes + one 56-polygon geometry. Small props: a single Bound Box. Poly geometry only where needed and tiny: cone 14, ATM 54, vending machine 126 + 20.

### Collision materials (Sollumz table, density kg/m³ → mass)

METAL_SOLID_SMALL 24500 / MEDIUM 28000 / LARGE 31500; METAL_HOLLOW_SMALL 1750 / MEDIUM 2100 / LARGE 2450; WOOD_SOLID_SMALL 1400 / MEDIUM 2100 / LARGE 2852.5; WOOD_HOLLOW_* 350–1050; PLASTIC 3500; PLASTIC_HOLLOW 875; GLASS_SHOOT_THROUGH / GLASS_BULLETPROOF / GLASS_OPAQUE 8750; CERAMIC 9695; RUBBER 4200; CARDBOARD_BOX 200; FOAM 175; LEATHER 3307.5 (~180 in total). Material decides footsteps, bullet decals/VFX and fragment mass. Material flags for clutter: not climbable, not cover (Bumpy86 [13:56]); BVH flags: untick map_weapon = bullets pass, untick map_cover = no cover (mnsb223 j8kZWnYZ_e4 [06:56]–[07:20]).

## Archetype flags (Sollumz `ArchetypeFlags`, flagN = 1 << (N-1))

1 Wet Road Reflection, 2 Dont Fade, 3 Draw Last, 4 Climbable By AI, 5 Suppress HD TXDs, **6 Static**, 7 Disable alpha sorting, 8 Tough For Bullets, 9 Is Generic, **10 Has Anim**, **11 UV Anims**, 12 Shadow Only, 13 Damage Model, 14 Dont Cast Shadows, 15 Cast Texture Shadows, 16 Dont Collide With Flyer, **17 Double-sided rendering**, **18 Dynamic**, 19 Override Physics Bounds, **20 Auto Start Anim**, 21/22 water reflection proxies, **23 Does Not Provide AI Cover**, **24 Does Not Provide Player Cover**, 25 Is Ladder (deprecated), 26 Has Cloth, **27 Enable Door Physics**, 28 Is Fixed For Navigation, 29 Dont Avoid By Peds, 30 Use Ambient Scale, 31 Is Debug, 32 Has Alpha Shadow. (CreateObject native doc: door archetype = 0-based bit 26 = flag 27.)

Measured patterns (vanilla Legacy):

| Prop kind | Flags |
|---|---|
| street props (cone, chair, table, bin, hydrant, streetlight) | 18 + 23 + 24 + 30 = 549584896 |
| simple dynamic (bottle, phone, cup, dumpster, bench, container) | 18 + 30 = 537001984 |
| ATM, vending machine, car wreck | 18 + 28 + 30 |
| apartment (MLO) furniture | **6 Static** + 30 (lamp also 14) |
| tree | 17 + 30, no Dynamic |
| doors, gates | 18 + 27 + 30 (some + 23/24) |
| windmill (animated fragment) | 10 + 18 + 20 + 30, clip dictionary `v_industrial` |

Tutorials that say "set Static + Cast Texture Shadows" (FivemMloGuy r4b13tw4IVg [03:07], Bumpy86 [16:23]) are right only for decor that must never move. Pushable world props use Dynamic, like Rockstar. Fragments need Dynamic (Sollumz prop-setup page).

## Special attributes (Sollumz `SpecialAttribute`)

0 none, 3 traffic light, 5 garage door, 6 MLO water level, 7 normal door, 8 sliding door, 9 barrier door, 10 sliding vertical door, 11 bush, 12 rail crossing barrier door, 13 deformable bush, 14 single axis rotation, 15 dynamic cover bound, 16 rumble on vehicle collision, 17 rail crossing light, 30 clock, 32 street light (1/2/31 deprecated).

Measured: roadcone/bin/crate 16, dumpster/gas pump 15, traffic light 3, doors see doors-fragments-animated.md.

## Physics dictionary

Sollumz: "blank or same as archetype name if embedded". Vanilla ydr props point at names with no file at all (`v_minigame`, `prop_ld_tools` — searched x64*.rpf / update.rpf), so a physics dictionary without a `.ybn` is normal and the checker never errors on it.
