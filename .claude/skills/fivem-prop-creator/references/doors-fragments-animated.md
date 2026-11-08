# Doors, fragments, animated props, lights, hand props

## Fragments (breakable / physical props)

Sollumz fragments docs + ook_3D ApaaGSSziUw (2024) + FivemMloGuy LI_eCB2JVgo (2025):
1. Apply transforms, Convert to Drawable, name drawable + models ([00:23]); origins to geometry.
2. Fragments > Create Fragment, rename fragment and skeleton ([01:11]); "Create physic bones at objects", parent the bones in a chain with one root ([01:35]) — several top-level bones cause problems (docs).
3. Pose mode → Bone Tools "apply bone flags rotation and translation" ([02:00]); rotation only on the main bone, rotation + translation on loose parts (LI_eCB2JVgo [06:19]); physics off on root/main bones that have no collision.
4. Bound Composite with one Bound Box per part ([02:46]), each linked to its bone with **Copy Transforms** (ook) or **Child Of** (FivemMloGuy [08:55]) + "set correct space for bone parenting".
5. Mass per collision, or `Sollumz Tools > Fragment > Set Mass > Calculate` (needs a collision material). Volume/inertia auto-calculated.
6. **Strength -1 = the part reacts but never separates** (container doors swing); other values break off.
7. YTYP: physics dictionary = object name (embedded), flag **Dynamic** ([05:23]); not Override Physics Bounds (LI_eCB2JVgo [11:45]).

"If you're not sure what physics properties to set, import a similar model from the game and copy them" (Sollumz bone-physics page). Destroyed variants are not editable in Sollumz. Vanilla: prop_bench_01a 1 group / 18 children with a damaged drawable, prop_fire_hydrant_1 3/9, prop_container_05a 4/8, prop_gas_pump_1a 9/22.

Breakable glass on a prop (mnsb223 k1uU8x0vR4Q, 2023, Sollumz ~2.1: bone "breakable glass = pane", `glass_breakable` shader, GLASS_SHOOT_THROUGH) conflicts with Sollumz 2.9 docs ("GlassWindows not supported" outside vehicles) — **unverified on 2.9**, test before promising it.

## Doors (Cfx part 8 + ook_3D hDjwchaRGfM)

Templates (import from the game, keep their bone and bound): swinging `v_ilev_bl_door_l.ydr`, sliding gate `prop_facgate_07b.ydr`, vertical roller `lr_prop_supermod_door_01.ydr`.

1. Origin: hinge edge (swinging), bottom corner (sliding), bottom centre (vertical). Align with the template, apply transforms, convert, parent to the template armature with **Copy Transforms** (Cfx) or **Child Of** (ook) to the door bone + bone-parenting space.
2. Collision: one Bound Box with inertia 1, or a duplicated mesh → Convert to Composite → General (Default) preset → WOOD_SOLID_LARGE, inertia 1 (tutor values, hDjwchaRGfM [04:04]–[04:50]). Resized template collision → apply scale or make a new composite (ajqNHqB8mYw [02:14]).
3. YTYP: **Dynamic + Enable Door Physics (27)** and:

| Door | Origin | Special attribute | Evidence |
|---|---|---|---|
| swinging | hinge | 7 Normal Door | Cfx part 8; vanilla v_ilev_ph_door01 = 7 |
| sliding / gate | bottom corner | 8 Sliding Door | Cfx part 8 |
| vertical roller (Benny's) | bottom centre | **10 Sliding Vertical Door** | Cfx part 8 video ajqNHqB8mYw [04:07]; vanilla lr_prop_supermod_door_01 = 10 |
| house garage (goes up and tilts) | — | 5 Garage Door | video [04:29]; vanilla prop_ld_garaged_01, prop_com_gar_door_01 = 5 |
| barrier / rail crossing | — | 9 / 12 | Sollumz enum (not tested) |

The Cfx part 8 **page** writes "Garage Door (5)" for the vertical/Benny's setup; its video and the game file say 10 — treat the page as wrong.

**Unverified conflict**: vanilla `v_ilev_bl_door_l` (the Cfx swinging template itself) and gates prop_facgate_07b, prop_gate_airport_01, prop_lrggate_01c_l have attribute **0** with flag 27, while the Sollumz flags page says Enable Door Physics does nothing without a door attribute. Use the attribute from the table and test on the local server.

4. Scripts: `CreateObject(model, x, y, z, isNetwork, netMissionEntity, doorFlag)` — natives doc: doorFlag must be true to create door models in network mode. Lock/unlock through the door system (`AddDoorToSystem`, `DoorSystemSetDoorState`) or ox_doorlock (the user's patched copy — memory `ox-doorlock-lockpick-patch`). In an MLO the door is an MLO entity on the portal (fivem-mlo-housing).

## Animated props (Cfx part 7, 11EXhLYfJLs)

- **UV scroll** (signs, screens): Clip Dictionary template → Animation (Target = Materials) + Clip named `<hash>.clip`, duration = frames / 30 → material Animation Tracks UV keys → export ycd + drawable → ytyp Clip Dictionary = ycd name, flags **UV Anims (11) + Auto Start Anim (20)**. Animation and clip must be named like the object "otherwise it won't automatically animate" ([00:21]).
- **Bone animation**: armature as Drawable, mesh constrained to a bone (Copy Transforms), keyframes in pose mode, flags **Has Anim (10) + Auto Start (20)**.
- **Moving part that must collide** (fan, turnstile): make it a fragment — split base and moving part, physics bones, strength -1, Bound Box (not Poly Box) per moving part linked with Child Of, physics off on the base bone, clip dictionary + Has Anim + Auto Start, Set Mass > Calculate (ook_3D dfO1eQf8WE0 [00:00]–[08:04]). CodeWalker does not animate collisions; the game does ([08:57]). Vanilla prop_windmill_01 is exactly this (yft, 27 physics children, clip dict `v_industrial`, flags 10 + 18 + 20).
- Script-driven: `PlayEntityAnim(entity, anim, dict, blendDelta, loop, holdLastFrame, driveToPose, startPhase, flags)` needs the prop to have its own skeleton.
- The Sollumz ycd page is still a TODO; Cfx part 7 is the authority.

## Lights on props

Lights live in the YDR/YFT (Sollumz lights panel: interior/exterior only, shadows, time flags, flashiness). Measured: lamp, street light, ATM, vending machine, gas pump, windmill 1 light; wall light / worklight 2. Pair with `emissive` / `emissivenight` shaders. CodeWalker light editor: time flags (e.g. on 21:00–07:00), electric hum (mnsb223 j8kZWnYZ_e4 [19:24]–[21:44]). Entity extension "Light Effect" overrides per placement.

## Hand-held props

- `AttachEntityToEntity(prop, ped, GetPedBoneIndex(ped, tag), x, y, z, rx, ry, rz, p9, useSoftPinning, collision, isPed, rotationOrder, syncRot)`. Tags: 28422 PH_R_Hand, 60309 PH_L_Hand, 57005 SKEL_R_Hand, 18905 SKEL_L_Hand; wrong index → prop at the ped's centre.
- rpemotes: `Prop`, `PropBone`, `PropPlacement = {x, y, z, rx, ry, rz}` (rotation order 1); ox_lib progressBar `prop = { model, bone, pos, rot }` (order 0). Animation side: `fivem-animation`.
- Budget: one LOD, ≤ ~440 tris, lodDist 10–30, one Bound Box, Dynamic. Community emote props often keep Sollumz 200/100 + Static — vanilla does not.
