# Engine bay, underbody and brakes

KG's course hides the bay and the underside with a plane (car-workflow §6). That is not enough for a car the user ships: every car needs a complete 3D bay and a real underbody in every LOD (user rules, §9). This file covers modelling them, making them game-ready for GTA V / FiveM, and checking them for holes.

Citations: `(videoId mm:ss)` = YouTube captions (±30 s); `(from frames)` = read from contact sheets of an uncaptioned video, no spoken method; `[measured]` = triangle/bone counts taken from the user's own vanilla exports in `H:\FiveM\vanilla_ref\{buffalo,bison,sadler,granger,vigero2}` (CodeWalker XML, counted per bone and region); `(user rule)` = T1 LESSONS / memory notes. Sources at the end.

Contents: 1. Plan · 2. Engine recipes (block, intake, headers, belt) · 3. Hard-surface toolkit · 4. Hoses and wires · 5. Rest of the bay, bay sheet-metal shell, checklists · 6. Underbody, suspension corner, differential, exhaust · 7. Brakes and wheels in GTA · 8. Game-ready: bones, shaders, atlas + baking, budgets · 9. User rules and tools · 10. Mistakes · Sources

---

## 1. Plan

- **Reuse first.** For GM trucks/SUVs use the user's Silverado bay kit (§9.3). For other cars a vanilla GTA engine of the same layout from the user's own game files is a fine base; the GTA SA tutorial simply reuses a vanilla engine of the same layout (c5RLkjnmTFs 22:00). Never ripped or paid models.
- **References:** engines have no blueprints. Build a PureRef photo board (free / pay-what-you-want) and use spare-parts exploded diagrams for sizes (YRBGpyMQf2c 02:00).
- **Dimensions chain:** start from bore and stroke and derive piston → rod → crank circle → caps → block; "each part contains the information to model the next one" (YRBGpyMQf2c 03:30–06:30).
- **Layout decides the blockout** (general knowledge, unverified):
  - **V8** (US trucks, muscle): two banks at 90°, intake plenum in the valley, two valve covers, exhaust manifolds on the outer sides, accessories on front brackets driven by one serpentine belt.
  - **Inline-4/6** (often transverse FWD): one bank; intake one side, exhaust the other; belt and accessories toward one front wheel, gearbox on the other side.
  - **Boxer:** two flat low banks; the top of the bay is mostly intake, air box and hoses.
- **Block order for any layout:** block → heads/valve covers → intake (plenum, runners, throttle body) → exhaust manifolds → front accessories + belt → radiator and tanks → hoses and wires last.
- **Construction type decides the underbody:** body-on-frame (two rails + crossmembers; pickups, most trucks) vs unibody (floor pan + tunnel + subframes; most cars) (Wikipedia "Vehicle frame").

## 2. Engine recipes

**Block and heads (YRBGpyMQf2c 06:30–12:00)**
1. Start from the easiest flat face with the bore circles placed, extrude outward. Sides first for proportion, then the front/rear details.
2. Use one part as the negative of the next (bearing cap shape → block pocket).
3. Repeated parts (pistons, coils, runners) as linked duplicates (Alt+D) while modelling (05:00). Apply and join them before export: instances do not reach the yft (inferred; the user's kit is joined meshes).
4. Only the **outside** of the block shows with the bonnet open (valve covers, intake, accessory drive, manifolds). Crankcase internals are wasted triangles: BlMMGFiW1do (an hour of bearing bulkheads inside the crankcase) is **not useful for GTA**. The one habit worth keeping from it: bolt bosses as 6-sided prisms with an inset bore (BlMMGFiW1do 03:00–09:30, from frames).

**Intake manifold / plenum (iGLu588hB58)**
1. Isolate the profile where two parts meet (Shift+D, P), extrude to the far border, snap, Merge by Distance (00:30).
2. Domed ends: UV sphere added in Edit Mode with a matching ring count; delete the unneeded half (01:30).
3. Inlet tube from a circle with a **matching vertex count**; if a joint bulges, delete and refill with the free F2 add-on (02:30–05:30).
4. Custom transform orientation from a face normal for angled parts (06:00).
5. Relax with Smooth Vertices + LoopTools Space, then keep a hidden duplicate as a Shrinkwrap/Data Transfer target (07:00).
6. Bosses on curved surfaces: inset → LoopTools Circle → extrude → Shrinkwrap (vertex group) back to the target (07:30–10:30).
7. Bevel modifier Limit Method = Weight, 2 segments, 0.5–1 mm, Subdivision 2 (09:30).
8. Cast lettering and ribs: for a game model, bake them to the normal map (§8.3), not geometry.

**Exhaust manifold / headers (exUIOwAH-cw 00:30–10:00)**
- Bézier curve, Bevel Depth ~0.03–0.04, Resolution ~10; primaries bent with E + R per segment; flange = half circle + Mirror traced to the port shape; duplicate primaries per cylinder; convert to mesh.

**Belt and pulleys (nH5hTrOKiuM 0:16–3:04)**
1. Pulleys: cylinders (12–16 sides) with a ribbed groove ring (Spin / Screw).
2. Path: Shift+A > Curve > Circle; in Edit Mode move groups of points (G X) until the loop wraps the pulleys; rotate the curve 90° on Y (0:16–1:19). Keep straight runs tangent to each pulley and the belt sitting in the grooves, no gap (user no-floating rule).
3. Belt: a cube scaled thin on Z ("on a car they're up to like a centimeter thick"), long on Y, belt width on X (1:19).
4. Loop cuts along the length so it bends; the video used 185 (2:01). For GTA use ~4–6 per pulley wrap plus 1 per straight run (a few hundred tris); ribs go in the normal map (inferred).
5. Curve modifier, target = the circle, **Deform Axis −Y**; scale Y until the ends just meet without overlap (2:23–3:04). Apply the modifier.
- The video's animation (keyed Y offset) is irrelevant to GTA.
- Moving belt in GTA: shader `vehicle_track2` (UV-animated; Sollumz docs say "in modded vehicles works only on the left side"). ZModeler videos put the belt under a `misc_*` bone, offset and mirrored (W0UdnIzpEfE 01:00–03:30; GBJmKSZVuq0 03:30). The Sollumz version of that trick is unverified; a static belt on `vehicle_mesh` is the safe default.

**Alternator, AC compressor, power-steering pump, starter** (still no captioned tutorial after a second search on 2026-11-08; general method, unverified): cylinder body + pulley on the belt plane (belt method above) + bracket to the block. The starter sits low at the engine/gearbox joint and is rarely seen.

## 3. Hard-surface toolkit (free)

- **Segment counts:** match counts where parts join; T-joints are easiest with two 6-vertex cylinders + LoopTools Circle + Bridge Edge Loops (QCe4Ms7jmvM 06:30). Game values (experience values, unverified): pulleys 16–24, hoses 6–8, bolts 6, wires 4–6 in L0; halve for L1. The user's hose tool defaults to 8 sides.
- **Bevel + Weighted Normal (Face Area, Keep Sharp):** flat faces shade flat, only bevels blend (Blender manual, Weighted Normal; sqGFhiP-2mc; fixes n-gon artefacts B1bco_ONbTU 01:00). Whether Sollumz exports custom split normals unchanged: unverified, check in game.
- **Creases first, bevel everything last** so bevels meet without n-gons (FSbgOOz-pN8 01:00–03:00).
- **Booleans** for holes, apply, then bevel the new loops (xyxR9F0TDpY 02:00). Hard Ops / BoxCutter are (paid); native Boolean is enough. Free stand-ins for what cWUsciTzT_U does with them: radial bolt holes = Array with an Object Offset Empty rotated 360°/n + Boolean, or Spin with Duplicate (BoxCutter radial array, 11:22); HardOps spring button = native Screw modifier (28:48).
- **No fake connections:** a pin or joint goes into a real hole Boolean-cut slightly bigger, a sleeve is extruded until it touches its neighbour, "So it's no longer floating" (cWUsciTzT_U 16:45–17:11, 33:22). Same idea as the user's no-floating and hoses-end-on-a-fitting rules.
- **Arrays:** radiator sections, Array + Curve for disc slots (STQpq8_4DjY 18:00), Array + Curve for cable profiles (oADKArjs85M 00:30–05:30).
- **Bolt Factory** (bundled: Add > Mesh > Bolt) for studs (RjXv3o9zyfw 04:00). In GTA most bolts are normal-map detail.
- **Screw modifier** / **Extra Curve Objects → Spirals** (bundled) for springs and threads (k1tl9jyG7n4 04:30; RjXv3o9zyfw 07:00).
- Paid add-ons seen in the videos (Random Flow, Curve Basher, Hard Ops, BoxCutter, gumroad curve kits): don't recommend.

## 4. Hoses and wires

1. **Vertex path:** one vertex, extrude exact segments, Ctrl+Shift+B to round corners, Object > Convert > Curve, Bevel Depth (= radius) + Resolution (= sides) + Fill Caps, convert back to mesh when final (QCe4Ms7jmvM 00:30–02:30; U-x-nlWR6Lk 00:00). Path curves bend smoother than Bézier (QCe4Ms7jmvM 05:00).
   - Bézier variant: Shift+A > Curve > Bezier, E to extrude points or Subdivide between two selected points; Object Data > Geometry > Bevel Depth/Resolution and **tick Fill Caps**, or the hose ends stay open (wgIs1rZxyrw 0:24–1:38). Open ends are see-through holes under GTA back-face culling (inferred).
   - **Corrugated hose:** model one ring, Snap Selection to Active onto the curve; **ring and curve origins must match** or you get "really strange results" (1:59–2:21); Ctrl+P > Keep Transform; Array (relative offset 0/0/1 on Z) then Curve modifier, Fit/Fixed Count raised to fill the length; loop cuts so it bends (2:43–3:52). Triangles multiply fast: only on short visible hoses (intake boot, booster line); otherwise a plain tube with ribs in the normal map (inferred). Paid hose add-ons are not needed (4:16).
2. **Hooks keep ends glued:** empty parented to each fitting, select empty then curve, Edit Mode, pick the end point, Ctrl+H > Hook to Selected Object (RFWWzV6QPWc 03:00–08:30). Ends follow when the kit moves to another car.
3. **Braided lines:** Array + Curve + Simple Deform twist (oADKArjs85M 05:30), then bake to a normal map for game use.
4. **Routing rules (user rules):** both ends on a real fitting (a gap > ~2 cm = floating); route low along the firewall and over parts, never as a straight bridge in mid-air above the engine ("线漏空了" = a hanging hose, not just a loose end).

## 5. Rest of the bay

- **Radiator + shroud + fan:** a box radiator angled to show through the grille, connected by the upper hose; check nothing pokes through the closed hood (c5RLkjnmTFs 29:30–32:00). Core fins = texture, not geometry.
- **Inner fenders / aprons:** extrude the bay opening down, scale in, fill; corners sharp (c5RLkjnmTFs 16:30–21:30). Make them **continuous walls**: one box per side (wall between engine and tyre, shelf over the tyre, front cap) (user rule).
- **Firewall + cowl panel** behind the engine so the cabin is not visible (user's fix).
- Hood underside goes on `bonnet`; hinges are optional detail on chassis (unverified).

**Bay sheet-metal shell (YjlIHIE1TYg, Aristo, from frames)** — the body-in-white of the bay built around an engine already in place; the best source for the user's continuous-shell rule. References: photos of a stripped empty bay, real bay photos of the same car, a white unibody stock image for rails and aprons (00:00, 15:00, 2:20:00).
1. **Wheel tub:** half a UV sphere (8–12 segments for GTA, inferred) sized to tyre + suspension travel; flat plates extruded from the body's inner edge down to meet it = the inner fender wall between engine and wheel (17:30–26:15).
2. **Strut tower:** a cylinder (8–12 sides) pushed down through the top of the dome, capped with a mount plate (30:00–35:00, 1:18:45–1:23:45).
3. **Firewall and cowl:** large flat panels along the body's inner edge at the back of the bay; a stepped cowl shelf under the windscreen (37:30–58:45, 1:40:00–1:45:00). Booster/master-cylinder area as cylinders and boxes on the firewall (41:15–1:08:45; parts identified by shape, unverified).
4. **Frame rails / aprons:** long box sections extruded along the bottom edge of each inner fender toward the front, joined by a front crossmember (1:25:00–1:53:45, 2:21:15–2:43:45).
5. **Radiator support:** a frame across the front between the headlight buckets, traced in wireframe against the body (1:47:30–1:58:45, 2:45:00–2:58:45).
6. **Headlight backs:** the lamp housings are closed off from the bay side (2:00:00–2:17:30); the clear lenses stay untouched (user rule 7, §9.1).
7. **Shut strips:** body-coloured strips along the top of the inner fenders, hood latch and hinge pads (2:01:15–2:17:30, 3:00:00); in GTA `vehicle_shuts` / paint on the bonnet-shut area (§8.2).
8. One flat colour per part group while modelling (body, shell, new sheet metal, painted strips) (1:20:00–3:02:30), like the user's red-ground check colours.
- Result: one continuous closed shell (towers, inner fenders, firewall, cowl, rails, radiator support), engine kept as a separate group (3:05:00). Faces are big, flat-shaded, not subD (1:40:00–1:58:45), so it suits a game bay (polycount not readable at 360p, unverified). This is the `side_boxes` idea (§9.2) done as real car-shaped panels; finish with the red-ground render.
- **Front suspension link** visible through the open bay: "you can see through ... to the road" (c5RLkjnmTFs 09:30–12:30).
- **Cover behind removable bumpers** so a lost bumper shows no hole (c5RLkjnmTFs 01:00–05:30); `bumper_f/_r` detach in GTA.
- **Opening under the engine** is fine; a full undertray is not (user rule, §9.1).

**Car checklist (unibody FWD/RWD):** block + heads/valve covers + intake/plenum + throttle body · exhaust manifold(s) · belt + pulleys · alternator · AC compressor · power-steering pump (or electric rack) · radiator + shroud + fan(s) + upper/lower hoses · coolant reservoir · washer tank · battery + tray + cables · fuse box · ECU · air box + intake tube · brake booster + master cylinder + reservoir · ABS unit + brake lines · strut towers · continuous inner fenders · firewall + cowl · radiator support · hood underside · wiring harness along the inner fender/firewall.

**Truck checklist (body-on-frame):** all of the above, usually a longitudinal V8 (valley intake, two valve covers, two manifolds), bigger radiator + fan, often a second battery.

## 6. Underbody, suspension, exhaust

**Wheel wells and floor (PPz2_PCxQi4)**
1. Duplicate the arch panels, match vertex counts, extrude inward leaving room for suspension, Bridge Edge Loops inner to outer, grid-fill the top, Shift+N (04:30–14:30).
2. Split the underside into front, centre and rear (diffuser/exhaust tunnel) zones; match counts, Space, merge, fill (15:00–45:30).
3. A photo-derived underside texture (free GIMP + InsaneBump, 9nv9yimKeVY) is allowed only as a texture **on** real 3D floor/frame geometry, never instead of it (user rule: no photo planes).

**Unibody underbody:** floor pan + tunnel, front subframe + control arms + steering rack + tie rods, CV shafts (FWD) or driveshaft + differential (RWD), rear subframe/axle + springs/shocks, sway bars, fuel tank + filler neck, heat shields, brake lines.

**Body-on-frame underbody:** two C-channel/boxed rails + crossmembers visible from the side and below, body mounts, IFS or solid front axle, transfer case (4x4), front/rear driveshafts, solid rear axle + diff, leaf springs + shackles + U-bolts (TElU85phpy0 00:30, parts list only), shocks, long exhaust along a rail, tank between the rails, spare tyre under the bed, hitch.

**Suspension parts:** coilover = stacked cylinders + Bolt Factory studs + spiral spring with flattened ends (RjXv3o9zyfw 00:00–09:30). Skip the video's rig and any rigid-body suspension (UIRyGTXjvOE): GTA moves `suspension_*`, `hub_*` and `wheel_*` bones itself, so put parts on the right bones instead of rigging.

**Front corner: hub, tie rod, knuckle, upper arm, shock, spring (cWUsciTzT_U; uses paid Boxcutter/HardOps, free stand-ins in §3)**
1. **Hub:** cylinder, extrude the back face, inset/extrude rings; radial bolt holes (11:22–13:17).
2. **Tie rod:** cylinder in a hole in the hub, rubber boot = loop cut + bevel 4–6 segments + proportional scale (13:17–15:14); then duplicate a face, P, extrude the long rod with rings at the ends (15:34–16:22).
3. **Bearing + knuckle:** duplicate the hub's cylinder faces back into a sleeve and extrude it until it touches, "no longer floating" (16:45–17:11); grow the knuckle up and back from the sleeve, Limited Dissolve, holding loops; extrude a lower boss for the bottom joint (17:32–20:45).
4. **Upper A-arm:** ball-joint cylinder in the knuckle top; the two legs as a vertex path → curve → Geometry Depth tube, mirrored; a cross cylinder at the back = chassis bushing; convert, Ctrl+J, inset/extrude the bushing eyes (21:08–23:42).
5. **Shock tower:** plane extruded and mirrored, Subdivision + Solidify; mounting hole from 4 faces inset + LoopTools Circle (24:08–26:12).
6. **Shock:** a cylinder tilted inward, "a small tilt can make a huge difference" (26:12–28:26). **Spring:** Screw modifier, first value = coil spacing, second = wire thickness (~0.03, very sensitive), Iterations = coils (28:48–29:30).
7. **Lower link:** faces extruded down from the shock base and rotated to the bearing end (29:53–32:15).
- **For GTA (inferred, unverified):** vanilla suspension pieces are only 38–65 tris (§8.1), so rebuild this subD corner at 8–12-sided cylinders without holding loops and bake the detail (§8.3). Parts that steer (knuckle, outer tie rod) → `hub_*`; arms, inner tie rod, shock body → `suspension_*` or `chassis`. Which bone each vanilla piece uses is unverified: import vanilla buffalo/bison and check. The video's knuckle split and wheel rig (46:44–49:26) are animation only.

**Differential (XcO8ovnr_Z0, low value):** the video models internal bevel gears with the Extra Objects Math Surface and rigid-body tests; none of it shows on a car. Model only the **outer housing**: pumpkin-shaped Screw/lathe profile with a ribbed cover, pinion snout toward the driveshaft, axle tubes as cylinders to the hubs; `chassis`, or `transmission_r` on 4x4s (recipe inferred, unverified). The driveshaft video found (N5Miyqi2OXI, Portuguese bus build) could not be read.

**Exhaust:** downpipe → cat → mid pipe → muffler → tailpipe as curves (exUIOwAH-cw); hangers = small blocks/rods to the floor (unverified). Tips need the `exhaust`, `exhaust_2`… bones at the outlets for smoke/backfire.

**Still no captioned tutorial** for sway bars, steering rack, fuel tank, heat shields: simple primitives + bevel (general method, unverified). Leaf springs, solid axles and header detail have candidate videos without captions that were not frame-read (TtIyp7GFvNw, HLR66MxfShI, sKb3yc5iow0, QQDArOv3htM); TElU85phpy0 gives a parts list only.

## 7. Brakes and wheels in GTA

- **Caliper:** model from a photo with Mirror on Y and Z through an empty (Clipping on), piston bores, pads separate, one subdivision level (STQpq8_4DjY 01:00–16:00).
- **Disc:** cylinder, inset the hat, cooling slots by Array + Curve (STQpq8_4DjY 16:00–19:00).
- **Drilled, vented disc in order (TdDf_X_ayFE, from frames):** flat ring of quads in front view with an "X" of topology around each hole position and a small vertex circle per hole (00:00–01:12) → extrude to thickness, punch the holes through (00:45–01:39) → vented = two friction plates with radial vanes between (01:48–02:15) → hat extruded forward with 5 lug holes, centre bore and concentric grooves (02:24–03:27) → caliper: plane outline over the disc at ~3 o'clock, extruded to wrap the disc edge, rounded under subdivision (03:36–05:24) → pads separate inside (05:33) → logo as a text/curve pressed into the caliper face (05:51). Real brand logos on calipers get swapped or removed (user brand rule).
- **For GTA (inferred):** holes and vanes are far over budget. Disc = flat ring of 12–24 segments on the **wheel mesh**, holes/slots in the texture and normal map; caliper = simple shell on `hub_*` with the logo in the texture; skip the pads (hidden).
- **Caliper goes on `hub_lf/rf/lr/rr`, never on `wheel_*`** [measured]. Each vanilla hub bone sits exactly at the wheel position, is parented to `chassis`, and carries a ~1,100-tri caliper in L0 (buffalo/bison/sadler/granger 1,132; vigero2 1,046), ~20 in L1, 7–16 in L2. The hub follows steer and suspension but not wheel spin (inferred from the data; GTA IV also used `hub_lf` for the brake disc, LCPDFR tutorial). On `wheel_*` the caliper spins with the tyre.
- **Disc lives in the wheel mesh:** the vanilla `wheel_lf` drawable contains a flat ring at radius ~0.1–0.2 m on the centre plane, so it spins with the wheel [measured]; a wheel-swap tutorial treats the disc as part of the wheel too, "looks like the brake disc scale is good" (2re9Hv-n6CY 4:19). Wheel swaps, `wheelScale` and the rim–tyre gap: `accessories-and-parts.md` §7.
- **Only `wheel_lf` has geometry**; the game instances it for the other wheels (Sollumz wheels doc). Calipers, by contrast, exist on all four hub bones.
- GTA cars have no other brake bone (bikes have `bikedisc_f/_r`).

## 8. Game-ready

### 8.1 Bones (muto-atlas bone tags; checked against the vanilla exports)

| Bone | What goes on it |
|---|---|
| `chassis` | engine, all accessories, hoses, bay walls, firewall, floor/frame, fixed exhaust, fuel tank |
| `engine` | **0 triangles** in all five vanilla cars [measured]: a position marker. Skin the engine to `chassis`. (`engineblock` on vigero2: 2 tris) |
| `overheat`, `overheat_2` | smoke points, no mesh |
| `bonnet` | hood skin + underside + moving hinge half |
| `bumper_f/_r`, `wing_lf/rf` | detachable/deforming panels (cover behind them) |
| `hub_*` | calipers (§7) |
| `suspension_lf/rf/lr/rr` | small arm/strut pieces, 38–65 tris, kept to L3 [measured]; which piece goes on `suspension_*` vs `hub_*` vs `chassis` per vanilla car: unverified (§6) |
| `transmission_f/_r` (`_m`) | moving axle/diff on 4x4s; granger 78 / 156 tris, kept to L2 [measured] |
| `exhaust`, `exhaust_2..9` (+ `exhaust_10..16`, separate tag block) | exhaust outlet points |
| `petroltank`, `petroltank_l/_r` | fuel-tank position (fire point) |
| `misc_a..misc_z` | free misc parts |
| `chassis_lowlod`, `chassis_dummy` | leave as in the donor |

Check names with muto-atlas `/vehicle`; remove Blender `.001` suffixes before export.

### 8.2 Shaders (Sollumz vehicle shaders doc)
- `vehicle_mesh`: "metallic vehicle parts, like exhausts, engines, chassis parts" (UV0 diffuse/normal/spec, UV1 dirt).
- `vehicle_shuts`: "inner sides of engine bay, doors, bonnet and boot".
- `vehicle_track2`: UV-animated belts, left side only in modded cars (§2).
- Vertex colours: R = AO, G = deformation, B = burn. Baked AO can also go in R.

### 8.3 One shared atlas, then bake
- Rockstar textures ≥ 95 % of every bay with **one shared atlas** [measured]: `vehicle_generic_detail2` (1024² DXT1) + `vehicle_generic_detail2_normal` (512²) + `vehicle_generic_detail_spec` (512²), dirt `vehicle_genericmud_car`, bay edges `vehicle_generic_doorshut` (1024×512). They live in `vehshare.ytd`, which all vehicles share through `txdRelationships` (modding-forum shared textures guide). Reusing them from an add-on without shipping them is unverified in FiveM; test.
- Otherwise make **one 512–1024 atlas** for bay + underbody (the user's kit uses a 512 atlas). Polycount: atlases save texture fetches; keep padding.
- Bake high-poly detail (bolts, ribs, lettering, fins, braids) to the low-poly normal map: Cycles, select high-poly then low-poly, Selected to Active, Extrusion ~0.02 or a Cage (inflated duplicate), active Image Texture node = target, Tangent space; save the image (b9LYJDxKEmU 00:00–06:00; G6Yc3b-3GfA; Blender manual "Render Baking"). Flipped normals give a yellow mess: check Face Orientation first. 90° edges need a tiny bevel.
- **Before any bake (W4fsal2VgUQ):** low poly on plain Shade Smooth, **no Auto Smooth modifier while baking** ("it create a weird sharp detail") (0:00); UV-unwrap it first (1:49); **explode touching parts** in a separate bake file, moving each low+high pair apart, or overlaps give normal/AO artifacts (2:34–3:46, 6:09) — a bay full of pulleys on the block and hoses on the radiator needs this (inferred). The video bakes in Substance Painter (paid); its Max Frontal Distance fix (0.005 → 0.003, 4:35–8:40) maps to Blender's Extrusion / Max Ray Distance or a Cage (inferred). Seam touch-ups in GIMP/Krita (free) instead of Photoshop (9:05).
- **Sculpted castings without a separate high poly (LvFilHJfinU, free Blender route):** for engine block, diff housing, knuckle.
  1. Even out face sizes with loop cuts (Multires splits each face in 4) and **apply scale** (1:52–3:30).
  2. Multiresolution in Object Mode, **Linear** subdivide so the shape doesn't round off (3:30–5:42).
  3. Sculpt: Scrape/Fill worn edges, Crease Sharp for dents, Draw with a free height-map texture and Stroke Method Anchor at 0.1–0.2 (6:13–15:57).
  4. UV unwrap (16:35); Image Texture node, new image, **no alpha, no 32-bit float** (films, not games), Non-Color (changeable only after saving) (18:01–18:48, 22:08).
  5. Viewport level 0 → **Shape > Conform Base** (not Apply Base, which distorts) (19:19–20:24); Shade Smooth (21:37).
  6. Cycles > Bake > **Bake from Multires**, Normals, target image selected — much faster than Selected to Active (20:38–21:56); plug in through a Normal Map node.
  7. Bake Displacement too: through a Color Ramp over the base colour as fake cavity/AO, inverted as roughness (23:08–26:24).
  - For GTA (inferred): the normal map goes in the `vehicle_mesh` bump slot; AO/cavity is **baked into the diffuse** of the shared bay atlas (no separate AO input); 512–1024 px, not the video's 2K.
- **Normal-map convention** (OpenGL vs DirectX green channel) is chosen per engine (W4fsal2VgUQ 4:12). Which one Sollumz/GTA expects is unverified: compare with a vanilla `_n` texture before shipping.

### 8.4 Budgets per LOD

Vanilla, whole car / engine bay / underbody, triangles [measured]. Bay = chassis tris in front of the cowl, inside the front wheels; under = chassis tris below axle height (crude boxes).

| car | L0 | L1 | L2 | L3 | L4 | bay L0/L1/L2/L3 | under L0/L1/L2/L3 |
|---|---:|---:|---:|---:|---:|---|---|
| buffalo | 46,138 | 15,168 | 5,393 | 1,471 | 393 | 2,599 / 826 / 479 / 157 | 1,446 / 628 / 307 / 64 |
| bison | 57,926 | 17,618 | 5,786 | 1,939 | 610 | 4,471 / 773 / 413 / 166 | 1,049 / 523 / 246 / 70 |
| sadler | 55,727 | 17,838 | 8,220 | 3,131 | 947 | 3,835 / 742 / 515 / 140 | 124 / 101 / 38 / 20 |
| granger | 58,435 | 19,317 | 7,931 | 1,995 | 590 | 4,542 / 1,201 / 479 / 126 | 883 / 452 / 256 / 104 |
| vigero2 | 90,092 | 24,277 | 12,688 | 6,628 | 1,033 | 2,371 / 1,378 / 961 / 708 | 568 / 392 / 293 / 161 |

Working targets (experience values derived from the table):

| LOD | bay (engine + accessories) | underbody (frame, exhaust, suspension) | each caliper |
|---|---|---|---|
| L0 (Very High) | 3k–8k | 1k–3k | ~1k |
| L1 (High) | 0.8k–1.4k | 0.4k–0.6k | ~20 (a box) |
| L2 (Medium) | 0.4k–1k | ~250 | ~10 |
| L3 (Low) | ~150 (blocks + black liner) | < 100 | — |
| L4 | a few dozen | — | — |

Keep the user's rules: body panels ≥ ~40 % in Medium/Low, bay parts may drop more; non-_hi yft under 16 MiB. The user's kit (~7,600 faces) is fine for L0 but must be reduced for L1+.

## 9. User rules and tools

### 9.1 Rules (T1 LESSONS "FiveM" + memory notes; apply without being asked)
1. **Complete 3D bay on every car:** radiator + fan, hoses, coolant tank, alternator, AC compressor, air box + intake, battery, fuse box, ECU, brake booster + master cylinder. "只有引擎罢了其他东西添加下" = an engine alone is not enough.
2. **Real 3D in every LOD** (Very High / High / Medium / Low). A photo on a plane or an empty bay counts as missing; report which LOD lacks what and fix it.
3. **Hoses connected at both ends** (> ~2 cm = floating) and **routed low**, along the firewall and over parts.
4. **No see-through holes.** Check with back-face culling ON and a **red-ground render** from player eye points (front, both front corners, both sides, above, low front, rear-left). Ray numbers alone are not trusted. Look hard at headlight backs, fender top edges, radiator sides and the grille-surround "eyebrow" corners.
5. **Close holes with continuous inner-fender walls**, not patchy cells.
6. **Never a full underbody plate** that shows under the bumper. Ground seen straight under the engine is fine; a hidden black underfill ~5 mm above the lowest part is allowed.
7. **Nothing inside clear lamp lenses:** no back faces or black patches behind headlight/taillight glass; check from outside through the lens.
8. **Medium/Low:** body panels ≥ ~40 %; render every LOD.
9. GTA draws only front faces, Blender draws both: preview with `material.use_backface_culling = True`; seal curved panels with a shared-vertex flipped shell (per-face copies leave hairline cracks).

### 9.2 Tools (in the user's `H:\FiveM\vanilla_ref\tools\` folder, not in this skill)
They run inside Blender through the `blender` MCP: ask first, run one LOD per call (big loops time out).

| Tool | What it does |
|---|---|
| `scan_installed.py` | `reset()`, then `scan_one(stream_dir, name)`: imports an installed yft, hides collision, sets Very High, writes `holes\<name>.json`. Reset between cars. |
| `hole_scan.py` | `scan(arm)`: rays down over the bay, oblique, and up along the wheelbase; tyre/hub/nothing hit = hole. `bay_view(arm)`: 8 player eye points aimed under the closed hood. Numeric pass. |
| `bay_cam.py` | `backdrop(ground_z)`: red emissive ground + magenta sky seen only by the camera; `views(...)`: the 8 standard eyes; `render(...)`; `red_score(...)`; `pixel_leaks(...)` GTA-style per-pixel rays; `seal_views`/`seal_region` flip back faces a leak passes. **The trusted visual check.** |
| `bay_cull_fix.py` | `fix(arm, hood_name='bonnet')`: every face hit from behind by player/under-car rays gets a flipped copy (0.8 mm), all LODs; `count_back(arm)`; `_add_flipped_shell` crack-free back shell. |
| `bay_liner.py` | `side_boxes(...)`: the preferred continuous double-sided inner-fender box per side (+ corner quads); `holes_per_lod`; `find_leaks`/`seal_leaks`; `drape` (black cover under the closed hood only); `backing` (black sheet 6 mm behind thin trim like the grille surround); `underfill` (hidden floor 5 mm above the lowest part). Rejected: `line_bay` (5 cm cells), `add_floor`/`add_front_floor` (showed under the bumper). Double-sided pairs must be offset or rays pass through. |
| `wire_check.py` | `loose(lod, gap=0.02)` hose ends off a part; `fix_all`, `fix_rear(y_max)`, `connect_short`, `dedupe`; `drop_hose` lowers a hanging hose onto the parts below; `add_path_hose(lod, pts, r, uv_like, sides=8)` new hose along a curve; `kit_offset`. |
| `hole_patch.py` | `patch(arm, holes, mat, size=0.10)`: small double-sided black patches. Last resort for small holes inside the body. |
| `corner_flip.py` | makes single-sided faces in a region double-sided (skips glass, kit, existing twins): front-corner triangle shards. |
| `ram_bayfix.py` | worked example chaining corner_flip + seal_region + pixel-leak flips. |

**Order:** model or fit the bay → join into `chassis` per LOD → `wire_check.loose` + fixes → `bay_cull_fix.fix` → `bay_liner.side_boxes` (+ corner quads, firewall/cowl) → `bay_cam.backdrop` + `render` from `views`, look for red → `seal_leaks` / `seal_region` / `corner_flip` where red shows → `underfill` / `backing` for ground specks → repeat for each LOD → `hole_scan.bay_view` as numeric confirmation → remove render helpers → export.

### 9.3 Silverado engine-bay kit (memory note `engine-bay-kit`)
- ~30 parts, ~7,600 faces (radiator support/radiator/fan, coolant tank, hoses, alternator, AC, airbox, battery, fuse box, ECU, brake booster/master cylinder, ABS, cowl panel), mesh `_bay2`, material `um23_bay`, 512 atlas `um23_bay_atlas` — the standalone `silvpd_fullbay.blend` was in a temporary folder and is **gone (checked 2026-11-08)**. The parts still exist merged into the `chassis` of the user's Silverado (silvpd / um23) and `um21yukonpd`: to reuse them, import that car with Sollumz (ask first), select the bay islands (everything inside the bay box under the bonnet, e.g. by a bounding-box selection), separate them into a new `_bay2` object with its material/atlas, and save it as a kit `.blend` somewhere permanent the user chooses (not a temp folder).
- **Fit to another car:** append `_bay2` → align by `wheel_lf` (Silverado wheel_lf y 1.845, z -0.538) → ray-cast up to the bonnet and lower anything that pokes through → join into `chassis` on all 4 LODs (Low: drop islands < 5 cm) → remove any stray `chassis.001` vertex group → `wire_check` (kit hoses were routed for the Silverado; ends hang on other cars) → hole scan. Known offset vs the Yukon fit for the Ram: (0.005, 0.355, 0.258).
- Hoses added during fitting were kept on VH + High only on um21yukonpd to stay under 16 MiB.

## 10. Mistakes

| Symptom | Cause → fix |
|---|---|
| Caliper spins with the tyre | Skinned to `wheel_*` → skin to `hub_*` (all four) |
| See-through holes only in game | GTA culls back faces → culling preview, red-ground renders, flipped shells |
| Black slab visible under the bumper | Full undertray → remove; use hidden `underfill` |
| Patchy black squares in the bay | Hole-by-hole cells → one continuous inner-fender box per side |
| Hoses floating over the engine | Kit routed for another car → `wire_check.loose`, `drop_hose`, reroute low |
| Kit pokes through the closed hood | Not ray-checked against `bonnet` → lower parts |
| Bay vanishes at distance | Joined only into Very High → join into every LOD |
| Yellow, broken normal bake | Flipped normals → Face Orientation, Shift+N, rebake |
| Black shards through the headlight | Patches/back faces inside the lens → remove them |
| Hose ends see-through | Curve Bevel without Fill Caps → tick Fill Caps before converting |
| Corrugated hose rings scattered | Ring and curve origins differ → match origins, then Array + Curve |
| Bake artifacts where parts touch | Overlapping parts baked together → explode pairs in a bake file |

---

## Sources (videos: https://www.youtube.com/watch?v=<id>, captions read 2026-11-08)

YRBGpyMQf2c (Alessiuccio, real V8 without blueprints) · iGLu588hB58 (Alessiuccio, intake manifold) · c5RLkjnmTFs (TheMadeMan GTA, GTA SA undercarriage & engine) · PPz2_PCxQi4 (Versus 53, underbody) · STQpq8_4DjY (Infect3dmodelz, brake caliper) · RFWWzV6QPWc (Infect3dmodelz, cables with hooks) · QCe4Ms7jmvM (ItsPaulTodd, pipes/wires) · U-x-nlWR6Lk (Render Kunstler, pipes in 5.0) · oADKArjs85M (Art of Akrosh, cables) · exUIOwAH-cw (Big Man Ting, exhaust) · W0UdnIzpEfE, GBJmKSZVuq0 (ZModeler moving belts) · xyxR9F0TDpY (zerobio, radiator) · sqGFhiP-2mc (Gleb Alexandrov, Weighted Normal) · B1bco_ONbTU, FSbgOOz-pN8 (Aryan) · XKPlUMuvLcI (PzThree, weighted bevels) · b9LYJDxKEmU (Markom3D, baking) · G6Yc3b-3GfA (Blender Secrets, cage) · Komry1kruHs (Grant Abbitt, colour atlas) · RjXv3o9zyfw (Plockis, coilover) · k1tl9jyG7n4 (CG Essentials, Screw modifier) · TElU85phpy0 (leaf springs) · 9nv9yimKeVY (Steven Brooks, underside texture) · UIRyGTXjvOE (rigid-body suspension, not for GTA).

Added 2026-11-08 (gap pass): YjlIHIE1TYg (graphics_dh, Aristo engine-bay shell; from frames) · nH5hTrOKiuM (M. Novoselskiy, belt on a Curve modifier) · wgIs1rZxyrw (iPaintSmallThings, hoses and corrugated hoses) · cWUsciTzT_U (EidosEdge, suspension corner; uses paid Boxcutter/HardOps) · TdDf_X_ayFE (Alessiuccio, drilled vented disc + caliper; from frames) · LvFilHJfinU (Grant Abbitt, Multires bake) · W4fsal2VgUQ (CG VOICE, high-to-low bake; Substance Painter is paid) · 2re9Hv-n6CY (13Stewartc, wheel swap; disc on the wheel) · XcO8ovnr_Z0 (O.T. Vinta, differential internals; low value) · BlMMGFiW1do (Alessiuccio, V8 crankcase internals; from frames; **not useful for GTA**). Not readable: N5Miyqi2OXI (driveshaft, Portuguese), 86MKO1x9-8Y (caliper, no English captions); uncaptioned and not frame-read: TtIyp7GFvNw, HLR66MxfShI (leaf spring / independent suspension), sKb3yc5iow0 (S13 suspension), QQDArOv3htM (headers).

Written: Blender manual (Weighted Normal, Curve Geometry, Render Baking, Screw modifier) · Sollumz docs: vehicle shaders https://docs.sollumz.org/documentation/fragments.yft/vehicle-shaders, wheels https://docs.sollumz.org/documentation/fragments.yft/vehicle-setup/wheels, LOD assignment · muto-atlas `trunk/bone-tags.md` · modding-forum LOD models https://www.modding-forum.com/guide/1-lod-models/ and shared textures https://modding-forum.com/guide/21-shared-textures · Polycount wiki (face weighted normals, texture atlas) · Wikipedia "Vehicle frame" · LCPDFR GTA IV conversion tutorial (hub_lf) · Unreal forum on non-spinning caliper bones.
