# Interior: dashboard, dials, wheel, seats, trim, police gear

Players see the cabin in first person, through the glass and when doors open. Vanilla GTA V spends about a quarter of L0 on it, then drops it fast. This file covers modelling each part, the GTA mechanisms behind dials, wheel and seats, and the game-ready budgets.

Citations: `(videoId mm:ss)` = YouTube captions (±30 s); `(from frames)` = read from contact sheets of an uncaptioned video (burned-in text or none), no spoken method; `[measured]` = counted read-only from vanilla buffalo, granger, sadler, police, police3, sheriff2 (and vigero2 bones) exported from the user's game (CodeWalker XML, per LOD/bone/shader); `[user meta]` = read from the user's server vehicle resources. Maya / ZModeler tutorials are (paid) tools; their methods transfer to Blender. Sources at the end.

Contents: 1. Plan, blockout, low-poly game route · 2. Dashboard, vents, screen, buttons, console · 3. Gauges and the `dials` render target · 4. Steering wheel (incl. low-poly/game wheel), column, pedals · 5. Seats and belts · 6. Door cards, headliner, pillars, carpet, cargo, cage · 7. Shaders, textures, tint · 8. Bones, layouts, seat-bone fix, first-person camera · 9. Budgets and LOD plan · 10. Police interiors · 11. Checks and checklist · Sources

---

## 1. Plan and blockout

- **References:** interior photos are perspective, so blueprints don't help. Match the camera with **fSpy** + the fSpy-Blender importer (free) and trace through it (iDzdESU1axk 01:01–07:38). Look up real sizes: gauges, wheel diameter, seat depth (ePFcO6mpZTk 04:06).
- **Scale figure first:** put a real-scale human mesh in the driver seat before modelling the cockpit; it shows wheel reach and dash height (ePFcO6mpZTk 31:18; gKkY8QF96oQ 10:23).
- **Grow the interior from the body shell:** duplicate the shell loop at the windshield base, separate (P), extrude; the dash then follows the body exactly (mQqNDRkQZ3o 02:03; gKkY8QF96oQ 01:02). Seen from above, dash + console form "a curved T"; bridge front to back so it is solid (ePFcO6mpZTk 38:05).
- **Pro blockout order** (ePFcO6mpZTk 06:08–52:26): inner shell (delete fake panel thickness, extrude inward) → inner door skins → sills and floor → wheel wells and cargo → figure → seats → steering wheel → dash top, centre stack, gauges → console → door pivots, then open the doors and look for holes.
- **Mirror** (Empty, Clipping) while symmetric; apply it before the driver cluster, screen and asymmetric buttons (gKkY8QF96oQ 03:05, 41:19).
- Block big shapes, then split each tier or trim piece into its own object (Shift+D, P): easier materials, UVs and baking (Tc2wqzVEc_g 01:02; PkrddBKKR1E 21:30).
- **Build for the LOD later:** 16-sided cylinders for vents and knobs, so every other edge can be dissolved for an 8-sided game version (1fuT43yHJiE 27:52).

**Low-poly game route (Seven gray Cubes, from frames)** — interior line-art blueprints (top/front/side) as reference; the video calls itself principles, "Not for line and exact guide" (Mv_233YX6ws 00:20–02:40).
1. **Dash + console from one cube:** extrude it into the dash body, then down into the centre-console "bridge" (a T from the front), "flaten the bridge with the rest of the dashboard" (Mv_233YX6ws 02:00–04:40). Centre-stack surround = inset frame; console extruded back to the lever; loops only where the silhouette bends (07:40–15:40).
2. **Binnacle** extruded up and forward from the same mesh's top faces; the opening under it by deleting and bridging faces (16:00–21:40).
3. **Separate objects:** instrument cluster (two low-segment rings bridged by a middle panel, extruded back, rings inset for a bezel lip, dial faces deleted) (22:20–28:40), steering wheel (§4), gear lever as stacked low cylinders (47:00). In GTA the wheel must be its own `steeringwheel` part anyway.
4. **Vents** cut as a hole in the stack face and filled/inset back; **slats not modelled** (32:00–35:40; slats in the texture is inferred). Screens and button panels = rectangle insets (36:00–37:40).
5. Place the dash relative to the seat H-point and the wheel in side view (AMT5MzZowwk 14:00–17:45); tunnel and floor as simple dark blocks (20:00–23:00).
- For GTA (inferred): 8–16 segments for round parts; vents, buttons, dial faces and numerals in the texture, not geometry.

## 2. Dashboard, vents, screen, buttons, console

**Surface**
- Even edge spacing; slide with G G so loops stay on the surface (mQqNDRkQZ3o 07:14).
- Sharpen with a loop slid tight (Ctrl+R, then E/F), a 1-segment bevel, inset + outset around cut-outs, or Mean Crease (Tc2wqzVEc_g 00:30; bijFDd6yKLA 08:37). Set corner radius by sliding the two holding edges (_VJSQVUP6U4 23:39).
- No bare single-sided edges, "a big tell that it's fake": Solidify only where the thickness shows (_VJSQVUP6U4 22:06). Delete faces the shell already hides (gKkY8QF96oQ 16:03).

**Vents**
- Rectangular: inset, delete the face, extrude the rim for depth; angle the face outward; mirror left/right (gKkY8QF96oQ 17:10, 27:53).
- Slats A: three loops, Ctrl+B into strips, Select > Invert, extrude the rest inward (gKkY8QF96oQ 34:37). Slats B: one slat plane, Shift+D, then Shift+R to repeat, Solidify (mQqNDRkQZ3o 33:50–37:36).
- Round: low-poly tube + ball housing; blades from a flattened cube rotated 72° for five; Edge Split on marked sharps (FV66bVT1Tog 02:02–04:35).
- In a curved panel: knife the outline, mark seam, L select, extrude, step-scale the fins (bijFDd6yKLA 02:32).
- Put a black back plate behind the slats so the duct isn't empty (inferred; same idea as the grille backsplash, car-workflow §6).

**Screen, buttons, knobs**
- Screen = a simple inset panel, "it's a screen, it's not having any buttons" (uah_Odm3ygY 28:36); one extra loop so the UV doesn't stretch (8orRQAmLbm0 19:09).
- Round buttons on a grid: vertex bevel (Ctrl+Shift+B, 1 segment), LoopTools Circle, knife away n-gons; caps by inset (Individual Origins) + extrude (gKkY8QF96oQ 42:20–48:00). Knurled knobs: extrude individual faces, scale on two axes (FV66bVT1Tog 16:16).
- Icons: one black/white icon atlas (paint.net, free) and UV each button face onto its icon (FV66bVT1Tog 41:36), or floating alpha decal faces (8orRQAmLbm0 15:33). Airbag lettering = normal map (MZRD7tpdFIo 27:51).

**Console, shifter, cup holders**
- Console: a cube between the seats, end face extruded up and tapered, about half seat height; raise its bottom edges so the floor can't be seen through (ePFcO6mpZTk 46:45–49:18).
- Shifter boot: cloth sim on a subdivided base + a sculpt pass (1fuT43yHJiE 71:51, Maya; Blender Cloth + Sculpt, inferred). Bake it for game use.
- Cup holders: inset, LoopTools Circle, extrude down, close the bottom (general method, unverified).

## 3. Gauges and the `dials` render target

- **Model the pods**, not the faces: 16-vertex cylinders built as extrude/scale/inset rings (uah_Odm3ygY 26:03). Dial faces are textures (1fuT43yHJiE 31:35). A low-poly video insets low-segment circles into the dash, makes tick marks small inset faces in an orange material and the needle a thin quad, numerals not modelled (AMT5MzZowwk 18:00–19:45, from frames); in GTA skip the needle and ticks, the `dials` plane below draws them.
- **GTA does not use modelled needles** [measured]:
  - A flat mesh skinned to the **`dials`** bone, shader **`vehicle_dash_emissive`** ("dedicated for emissive dials being lit up at night", Sollumz shaders doc), texture **`script_rt_dials_<type>`** (seen: `gen_taxi`, `cavalcade`, `race`, `dukes`, `digital`).
  - L0: 100–114 tris, bbox ~0.66 × 0.10 × 0.22 m, covering the cluster and centre-stack screens. L1: usually one quad (2 tris); granger keeps 114.
  - The game draws needles, RPM bars and warning lights into that texture. No vanilla skeleton has needle or speedo bones.
- **Recipe** (I5r3Z1bXZkU, ZModeler; Blender steps inferred):
  1. Detach the cluster-screen faces into their own object, skinned to `dials`; lay a grid of quads over it.
  2. Shader `vehicle_dash_emissive`, diffuse = the `script_rt_dials_*` texture (vanilla, not shipped), diffuse colour white, spec colour black, black spec map (07:37–09:38).
  3. UV each quad onto one cell of the render-target layout (RPM bars, indicators, digits); a quad must sit fully inside its lit cell (10:08–14:40).
  4. Sit the plane "paper thickness" in front of the cluster; too close or behind and it draws behind the dash (16:14).
  5. Set `<dashboardType>VDT_...</dashboardType>` in vehicles.meta to the matching style (20:18). Types in the user's cars [user meta]: VDT_RACE, VDT_GENTAXI, VDT_CAVALCADE, VDT_FEROCI, VDT_ZTYPE, VDT_TRUCKDIGI, VDT_DUKES.
- `dashboardType` and the `script_rt_dials_*` texture must belong together, or the dials show nothing or the wrong layout (gta5-mods "Missing Speedometer Fix"; community, partly verified). The texture must be reachable in the car's dictionary chain (modding-forum "weird dials" thread).
- Some mods layer their own dial-face texture over the render target (e.g. `charger21_dials` in the user's Charger) (unverified how).
- `dashglow` bone: no mesh, in front of the driver above the dash (buffalo (-0.43, 0.64, 0.32)); probably the dash-light point (unverified).
- Meta-side details (vehicles.meta fields): `fivem-vehicle-mod` → `references/resource-and-meta.md`.

## 4. Steering wheel, column, pedals

**Model**
1. Model upright at the world origin, origin at the hub centre, then rotate and snap onto the column (every source; PkrddBKKR1E 43:33; MZRD7tpdFIo 01:32).
2. Rim: torus or Spin; 64 major × 8 minor to match spoke joins (Xvq26oxrRP8 03:32), counts divisible by 4 (MZRD7tpdFIo 10:39); set segments in Adjust Last Operation before moving it.
3. Spoke joins: delete rim faces at the joint, match edge counts, Bridge Edge Loops, support loops (Xvq26oxrRP8 05:03–07:05).
4. Hub: 24-vertex circle a bit larger than the photo (SubD shrinks circles); badge dome from half a UV sphere; logo as low-poly letters Shrinkwrapped onto the pad, then applied (MZRD7tpdFIo 17:43–22:48).
5. Grip ridges from photo shadows (1oeP1dPhCOE 37:36); rough is fine.
6. Separate rotating parts (rim, spokes, pad, paddles, wheel buttons) from fixed parts (column shroud, stalks, ignition) (1oeP1dPhCOE 70:38).

**Low-poly / game wheel (from frames)**
- Rim = Add > Torus with low major/minor segments scaled to a dimensioned wheel drawing; hub = low-segment cylinder; spokes bridged from the rim's inner faces to the hub, "fill the arms and recalculate normals if needed"; button pads = insets, logo a small separate part (Mv_233YX6ws 38:00–45:20; segment counts ~16–20 × 4–6, unverified). Same build with 4 flat spokes (AMT5MzZowwk 09:45–12:30).
- **Real size from a calipered photo:** the Assetto Corsa build measures rim thickness 28.9 mm (2w7B_--Sboo 00:25–01:15); spoke plate traced flat from a front product photo with lightening and bolt holes, dish from a side photo (02:30–12:30).
- **Rim UV = one long straight strip** so a stitch or stripe texture tiles along it; logo on its own UV island (24:10–25:50, 33:20–44:35). Texture painted in Photoshop (paid): use GIMP or Krita (free).
- **Reaching a budget:** Subdivision (applied) → Weld (All, ~0.001 m) → Decimate (Collapse, Face Count ≈ 3.2k) (48:20; numbers read at 360p, unverified). Decimate leaves messy triangles: fine for a small part, but aim at the vanilla ~2k tris (below) and keep body-visible parts hand-built (user LOD rule).
- Align the new wheel to the old wheel's position and pivot (old one as a wireframe overlay) (49:10–49:35).

**GTA placement** [measured]
- Rotating parts on the **`steeringwheel`** bone (alt:V docs call it `steering`; every vanilla yft uses `steeringwheel`). Shroud, stalks and cluster stay on `chassis`.
- Vanilla wheel: ~0.35 m across, L0 1,932–2,420 tris, L1 160–310, gone at L2; shader `vehicle_detail2` (+ `vehicle_badges`/`vehicle_decal` for the logo).

| Car | `steeringwheel` | `seat_dside_f` | tilt (quat x) |
|---|---|---|---|
| buffalo | (-0.420, 0.469, 0.189) | (-0.423, 0.123, -0.133) | -0.153 (~17.6°) |
| police3 | (-0.424, 0.552, 0.166) | (-0.428, 0.206, -0.157) | -0.153 |
| granger / sheriff2 | (-0.438, 0.807, 0.484) | (-0.443, 0.481, 0.212) | -0.130 (~14.9°) |

- Rule of thumb: same X as the driver seat bone, +0.33–0.35 m forward, +0.27–0.32 m up, tilted 15–18°. Driver hands come from the layout's clipsets, so keep the wheel near the vanilla offset for the chosen `layout` (inferred; IK onto the rim is unverified). Which local axis the wheel spins about: unverified; import a vanilla car in Sollumz and copy its bone frame.
- `steerWheelMult` in vehicles.meta scales the turn (meaning unverified).

**Column and pedals**
- Column = narrowing extruded cylinder (uah_Odm3ygY 00:32); stalks and keyhole are simple parts (1fuT43yHJiE 50:58).
- Pedals: flat at the origin, ridges, taper, bend, place (1fuT43yHJiE 45:25); hole grid from one hole + two Arrays, curvature with a Curve modifier (FV66bVT1Tog 36:31). In GTA they are static on `chassis` (no car pedal bones; inferred).

## 5. Seats and belts

- **Blockout:** seat depth ~510–540 mm; half cube + Mirror; extrude the side profile cushion → back, then bolsters from the top view (ePFcO6mpZTk 32:55; PIFZLzcKgRw 00:31–07:10).
- **Low-poly bucket seat (AMT5MzZowwk, from frames):** reference = the seat maker's dimension drawing (that seat only: cushion depth 465 mm, back width 520 mm, back height 770–830 mm, H-point marked) (00:30–04:30). Trace the cushion in side view, extrude the backrest up along the back curve in ~5–6 segments (01:00–01:45); bolsters extruded and scaled out in front view, half seat + Mirror (02:00–06:15); loops round the insert, insert separated from the bolsters (06:45–08:15); **pleats = horizontal loop-cut bands with a second material** (tan insert, black bolsters), no stitch geometry (08:15–09:30); passenger seat = Shift+D (13:15).
- **Panels:** loops on the real seams and bolster ridges; separate insert/bolsters/back with Mean Crease, gap bevels, or tucked separate objects (AojSGzM6NWo 12:38–15:44). Rip alone is re-welded by Merge by Distance.
- **Seams** at real scale: bevels 0.5 / 0.3 cm, 2 segments, trench 0.025–0.05 cm (uqb9lh6gE6U 19:45–24:53). Push the mesh out ~0.2 along normals first, smoothing shrinks it (10:49).
- **Stitches:** seam loop → curve (origin at the start) → one stitch with Array above Curve, axes matching (AojSGzM6NWo 30:26; L5UFIkBXye8 01:00). For games: "texture stitching ... this is for very very high-end CG" (uqb9lh6gE6U 45:27). Model them on a high-poly copy and bake, or use a tiling stitch texture on a straight UV strip, as for the wheel rim (2w7B_--Sboo 24:10).
- **GTA:** seat bones carry no geometry; seats are skinned to `chassis` [measured]. Vanilla leather grain comes from the shared `vehicle_generic_leather2_n` detail normal. Police rear bench: `vehicle_detail2` with `police_rearseat_HD`.
- **Belts:** curve swept with a ~6 × 0.4–0.5 cm rounded profile; hardware from simple primitives; strap holes as collapsed insets (uqb9lh6gE6U 57:10–62:21). Material bands from normals, not colour (-wcbmQV8BIg). No belt bone in vanilla; static on `chassis` (inferred). Layout seen in a scale-model build: B-pillar trim with the guide loop, webbing as a thin strip down the pillar to the retractor cover, buckle on the seat side (lPpTbWvTe6Q 15:00–17:15, from frames); for GTA a textured flat strip of ~2–4 quads per run (inferred).

## 6. Door cards, headliner, pillars, carpet, cargo, cage

- **Inner door skin:** select the door's inside faces (deselect outer by ~10° angle), push inward; or extrude the door line inward, S X 0 (ePFcO6mpZTk 09:16; A5ek-AnfeEM 08:34–22:52). Armrest, pocket and handle extrude from it.
- **Door cards are skinned to each `door_*side_*` bone** so they swing with the door [measured]: 120–375 interior tris per door at L0, 45–77 at L1. A scale-model build makes the card a separate shell inside the door, with the armrest/pull pocket and speaker or map-pocket recesses knifed in and pushed in (lPpTbWvTe6Q 00:00–04:00, from frames).
- **Headliner, visors, mirror, pillar trims, carpet** (no captioned tutorial even after a second search on 2026-11-08; the only evidence is frames of lPpTbWvTe6Q, a 1/18 scale-model build):
  - Seen (from frames): the whole inner shell (pillars, roof lining, inner sills) is its own object; the headliner is a separate panel following the roof curve and stopping short of the windscreen and door frames; the rear-view mirror hangs from the headliner at the top of the windscreen; visors are flat padded rectangles with a vanity-mirror inset and a hinge rod (identification unverified) (04:45–06:15, 10:15). Its vent slats are real thin walls, scale-model detail; in GTA use texture/alpha (07:00).
  - Method (general, unverified): headliner = roof faces duplicated, normals flipped, offset inward ~2–3 cm, one material; A/B/C trims = inner shell faces split on real seams (_VJSQVUP6U4 17:29); visors and mirror = bevelled boxes on the headliner; carpet = floor-pan faces duplicated with a carpet normal + detail texture. Rear bench and seat wrinkles: no source at all.
  - GTA split (inferred): shell and headliner on `chassis` (`vehicle_interior2`), door cards on the door bones, belts and small hardware last. Flat textures read badly on carpet and headliner; give them normal + spec (qjvfpj28gm4 01:02). Dome light sits near the `interiorlight` bone.
- **Cargo:** duplicate the inner wheel-well piece, add strut towers and a spare-tyre tray (ePFcO6mpZTk 22:33–27:40).
- **Seal it:** extend the floor up behind the seats past the rear glass (FTx9ruiAicY 03:36–06:24); fill gaps and inner arches; open the doors and look (ePFcO6mpZTk 50:20). Back-face culling ON (T1 rule).
- **Roll cage / partition frame:** tubes about A-pillar width, joined by snap + Boolean + merge + bevel; more segments = fewer Boolean artefacts (_VJSQVUP6U4 29:19–33:24). If it crosses the first-person view, see `PovCameraVerticalAdjustmentForRollCage` (§8).

## 7. Shaders, textures, tint

| Look | Shader (Sollumz) | Notes |
|---|---|---|
| Dash, plastics, leather seats, wheel | `vehicle_detail2` | diffuse/normal/spec on UV0 + tileable detail on UV1; "leather detail effect to seats and dashboards" |
| Plain trim, door cards, shell, small objects | `vehicle_interior2` (no normal) / `vehicle_interior` (normal) | vanilla pairs interior2 with `vehicle_generic_smallspecmap` |
| Dials | `vehicle_dash_emissive` | §3 |
| Lit buttons and screens | `vehicle_dash_emissive_opaque` | vanilla: 84–106 tris on chassis at L0 [measured]; symbols need a texture whose alpha holds only the symbols (qjvfpj28gm4 09:40–11:10) |
| Metal, chrome | `vehicle_mesh` | chrome trick: true-black detail texture (qjvfpj28gm4 17:16) |
| Logos, small decals | `vehicle_badges` / `vehicle_decal` | |

- SCRAT uses `vehicle_lightsemissive` (light ID 0, always on) for lit buttons instead; which is better is unverified. Vanilla uses dash_emissive_opaque.
- **Spec maps:** `vehicle_generic_smallspecmap` = glossy; darker = matte; pure black = dead matte; auto-generated spec maps give white speckles (qjvfpj28gm4 07:38–09:10).
- **Shared textures:** interior atlases mostly do **not** sit in the car's own ytd (buffalo.ytd holds only lights and badges). They come from shared parent dictionaries via `txdRelationships` in vehicles.meta, e.g. um21yukonpd → `vehicles_bob_brown_interior` [measured, user meta]. Reuse `vehicle_generic_smallspecmap`, `vehicle_generic_leather2_n`, `vehicle_generic_int_objects` and a vanilla interior parent to save memory. Meta syntax: `fivem-vehicle-mod` → `resource-and-meta.md`.
- **Custom textures:** bake seams, stitches, grain and embossed icons into the low-poly normal map; one texel density for all leather/metal/carbon (1fuT43yHJiE 77:52); atlas small parts. With detail2's tiling detail, even 64×64 seat textures can look good (qjvfpj28gm4 02:34). Check Face Orientation before baking (uah_Odm3ygY 17:43).
- Cycles leather/carbon node trees (8orRQAmLbm0) are previews only; they don't export.
- **Paintable interior:** Sollumz paint layers include *Interior Trim* and *Dashboard*; which interior shaders accept them (needs `matDiffuseColor`) is unverified.
- **Window tint = glass vertex-colour alpha:** black = no tint, white = darkest; set it on **every LOD** (R5T7stYU3A0 04:07–05:38). It decides how much interior shows from outside.

## 8. Bones, layouts, first-person camera

| Bone | Geometry? | Use |
|---|---|---|
| `steeringwheel` | yes | rotating wheel parts (§4) |
| `dials` | yes | render-target mesh (§3) |
| `dashglow` | no | dash-light point (unverified) |
| `interiorlight` | no | cabin light, roof centre (buffalo (0, 0.148, 0.664)) |
| `seat_dside_f`, `seat_pside_f`, `seat_dside_r`, `seat_pside_r` (+ `_r1`, `_r2`… for more rows) | no | where peds sit; vehiclelayouts `SeatBoneName` |
| `door_*side_*` | yes | door cards |
| `extra_ten`, `extra_11`, `extra_12` | yes | interior extras (`FLAG_HAS_INTERIOR_EXTRAS` spawns one or none); vanilla = small dash-centre items 0.07–0.24 m |
| `chassis` | yes | dash, seats, floor, console, headliner, shroud, pedals |

- **Seat position = seat bone position**; how the ped sits (low, standard, van) comes from the layout clipsets. Model the cushion and wheel to suit a vanilla `layout` (e.g. `LAYOUT_BISON`) rather than inventing one; custom layouts are poorly documented and crash-prone (cfx forum).
- **Ped sits wrong (floats, clips) — two causes, two fixes (qiD_6MZu0zY, Andrometall, from frames; CodeWalker + Blender/Sollumz, free):**
  1. Wrong `<layout>` in vehicles.meta (example `LAYOUT_LOW`): switch to another vanilla layout, names from vanilla `vehiclelayouts.meta` (00:18–00:30).
  2. Misplaced seat bone: CodeWalker RPF Explorer > Open Folder (the resource) > right-click the `.yft` and `_hi.yft` > Export XML (00:36–01:06) → import the XML with Sollumz (01:12) → hide what blocks the view, armature **Edit Mode** ("Don't forget to use Edit Mode") (01:42–02:12) → the wrong bone sits low near the floor; G it up onto the cushion surface at the rear centre of the seat pan (02:18–02:37) → export XML, import back to yft in CodeWalker, replace the old files after a backup (02:42–03:42) → hard-restart the server "to avoid desync issue" (03:48).
  - Unverified: whether the seat mesh or the `seat_dside_f` origin must move too, and whether both `.yft` and `_hi.yft` need the change (the video edits both). Driver arm IK on the wheel is not documented anywhere.
- **First person:** vehicles.meta `povCameraName`, `PovCameraOffset` (um21yukonpd: 0, -0.17, 0.60), `PovPassengerCameraOffset`, `PovRearPassengerCameraOffset`, `PovCameraVerticalAdjustmentForRollCage`, `FirstPerson*IKOffset` [user meta]. Hand these to `fivem-vehicle-mod`.
- Neon bones moved into the cabin give interior LED glow (rBfjLaVy-Yc 01:08, ZModeler; in Blender just move the bones, inferred).

## 9. Budgets and LOD plan

Vanilla, triangles [measured]. Interior = `vehicle_interior2`, `vehicle_detail2`, `vehicle_dash_emissive*`, plus `steeringwheel`, `dials`, interior extras.

| Car | L0 total | L0 interior | wheel L0 | L1 total / interior | L2 total / interior | L3 / L4 interior |
|---|---:|---:|---:|---|---|---|
| buffalo | 46,138 | ~13,160 | 1,936 | 15,168 / 1,887 | 5,393 / 636 | 0 |
| granger | 58,435 | ~14,860 | 2,420 | 19,317 / 2,315 | 7,931 / 1,058 | 0 |
| sadler | 55,727 | ~13,250 | 2,420 | 17,838 / 1,741 | 8,220 / 773 | 0 |
| police | 49,952 | ~14,000 | 1,932 | 17,123 / 2,018 | 8,981 / 1,367 | 0 |
| police3 | 54,354 | ~14,700 | 1,932 | 15,174 / 1,587 | 9,792 / 1,044 | 0 |
| sheriff2 | 59,519 | ~14,300 | 2,420 | 20,496 / 1,933 | 10,333 / 1,010 | 0 |

LOD plan (inferred from the table):
- **L0 ~12–15k** (≈ 25–30 % of a 50k car): full cabin; wheel ~2k; seats with real bolsters, seams baked; vents 8–16 sides; cluster pods; `dials` mesh; lit button faces; door cards on door bones; headliner, pillars, console, pedals, simple belts. Spend detail in the driver's view cone; rear seats and cargo lighter.
- **L1 ~1.5–2.5k:** same silhouettes; wheel ~200 (torus 16 × 4 + flat spokes); dials one quad; seats as boxes with bolsters; dash one shell; no stitches, belts, pedals.
- **L2 ~0.5–1.5k:** dark shell (floor, dash block, seat blocks) so windows don't show daylight through the car; no wheel, no dials.
- **L3/L4:** none; glass or body must hide the empty cabin.

## 10. Police interiors

- **Vanilla** [measured]: police (Stanier) has no interior extras, hard rear bench on detail2. police3 and sheriff2 each have one interior extra, `extra_12`, a small dash-centre unit (police3: 764 tris L0, 146 L1, interior2 + mesh); what it is visually was not confirmed (likely radio/console, unverified). police3's partition glass is `vehicle_vehglass` on `chassis` (from the accessories research).
- **Three ways FiveM builders add gear:**
  1. **Extras in the main yft** (`extra_1`…`extra_12`, `extra_ten`): partition, cage, laptop, radio. The extra number is per car (Tebex pack: partition = extra 10; a Crown Vic: partition + shotgun = extra 7). Give an extra with child parts a collision so children hide with it (modding-forum extras guide).
  2. **Modkit parts** (own yft on a bone, carcols `VMT_*`): trunk drawers, MDT variants, consoles; one user car puts dash bobbleheads on `VMT_INTERIOR2` / bone `bobble_head` [user meta].
  3. **Script-attached props** (e.g. a laptop-stand prop attached at runtime): nothing in the model.
- **Modelling** (no dedicated video; general method, unverified):
  - Partition/cage: tube frame (roll-cage method); mesh panel as alpha cutout or baked hole pattern; polycarbonate window as `vehicle_vehglass` (unverified on an extra). Visible in first person: L0 detail, L1 simple frame.
  - Laptop/MDT mount: cylinder pole + swivel; screen as an emissive face with a static image; on an interior extra or modkit slot.
  - Radio, siren controller, radar head: small boxes with lit-icon faces (§2, §7).
  - Shotgun rack: two clamps and a bar on the partition or roof; the gun as a prop if wanted.
  - K9 cage, trunk drawers: trunk modkit parts.
- Lightbars, push bars and exterior extras: `accessories-and-parts.md`. Extras/modkit meta: `fivem-vehicle-mod` (`police-emergency.md`, `modkits-liveries-sirens.md`).

## 11. Checks and checklist

**Checks before export**
1. Back-face culling ON; look through every window and an open door from eye height.
2. Red-ground render (engine-bay §9): no holes into sills, behind the dash, under the seats.
3. Seat bone vs cushion: the hip lands on the cushion; test first and third person in game (fix: layout or bone, §8).
4. Wheel on `steeringwheel`, origin on the column axis; it turns, the shroud doesn't, hands are on the rim.
5. Dials show: `dashboardType` matches the `script_rt_dials_*` texture; plane just in front of the cluster.
6. Interior extras toggle; children hide with their extra.
7. Tint alpha set on every LOD.
8. Every interior part has an L1 version or is deliberately absent; L2 dark shell present.

**Parts checklist (L0)**
- [ ] Inner shell: door skins, sills, floor/tunnel, firewall, inner arches, rear deck/cargo, sealed
- [ ] Dash: top pad, lower dash, glovebox, centre stack, vents (driver, centre, passenger, demisters), trim
- [ ] Cluster binnacle + pods; `dials` mesh + matching `dashboardType`
- [ ] Screen, climate panel, hazard/buttons with lit icons
- [ ] Console: shifter + boot, handbrake, cup holders, armrest
- [ ] Wheel on `steeringwheel` (rim, spokes, pad, logo, buttons, paddles); shroud, stalks, ignition on chassis
- [ ] Pedals + dead pedal
- [ ] Front seats (cushion, back, bolsters, headrests + posts, rails, levers); rear seats; armrest
- [ ] Belts: strap, buckle, B-pillar loop
- [ ] Door cards on door bones: armrest, pull handle, inner handle, window switches, speaker, pocket
- [ ] Headliner, visors, rear-view mirror, dome light, grab handles; A/B/C trims; parcel shelf; carpet/mats
- [ ] Police: partition/cage, MDT + mount, radio, siren controller, radar, gun rack, hard rear bench, window bars, K9 cage, trunk gear, each on an extra or modkit slot
- [ ] L1 simplified cabin, L2 dark shell, L3/L4 none; bones `seat_*`, `steeringwheel`, `dials`, `interiorlight` match the model

---

## Sources (videos: https://www.youtube.com/watch?v=<id>, captions read 2026-11-08)

On Mars 3D (Maya, paid tool): ePFcO6mpZTk (interior blockout), 1fuT43yHJiE (final part: IP, vents, dials, pedals, door panels), uqb9lh6gE6U (race seats, seams, belts), _VJSQVUP6U4 (rear hatch, roll cage), PkrddBKKR1E (steering wheel) · Infect3dmodelz: gKkY8QF96oQ, uah_Odm3ygY (dashboard 1–2), 8orRQAmLbm0 (interior materials), 5eciNLeADdE (seat) · Praize3d: mQqNDRkQZ3o, Tc2wqzVEc_g (dashboard), QK1ZUJlqmdU (wheel) · Aryan: AojSGzM6NWo (seats), MZRD7tpdFIo (steering wheel), FV66bVT1Tog (interior timelapse), iDzdESU1axk (fSpy), bijFDd6yKLA (vents) · Xvq26oxrRP8 (Casper 3D, wheel) · 1oeP1dPhCOE (Monarco, wheel) · A5ek-AnfeEM (Seven gray Cubes, interior) · FTx9ruiAicY (BlenderForNoobs) · PIFZLzcKgRw (Enpix, low-poly seat) · LxRl6K-S5T4, L5UFIkBXye8 (stitches) · -wcbmQV8BIg (belt shader) · SCRAT (ZModeler, French): qjvfpj28gm4 (GTA interior shaders), I5r3Z1bXZkU (GTA digital dials) · R5T7stYU3A0 (Onslaught, tint in Sollumz) · rBfjLaVy-Yc (interior LEDs) · T9x11bZMGmQ (McGinlay, extras) · xX08GYid-zI (police pack showcase, paid pack) · added 2026-11-08, all read from frames: Mv_233YX6ws, AMT5MzZowwk (Seven gray Cubes, low-poly interior: dash from a cube, gauges, wheel, bucket seat) · 2w7B_--Sboo (VB Assetto, steering wheel for Assetto Corsa: measurements, rim UV strip, decimate) · qiD_6MZu0zY (Andrometall, fix misplaced seat bone in FiveM) · lPpTbWvTe6Q (irasnarob, 1/18 Peugeot 106 interior: door cards, headliner, mirror, visors, belts; scale model, not game-ready).

Written: Sollumz vehicle shaders https://docs.sollumz.org/documentation/fragments.yft/vehicle-shaders · Sollumz positioning bones / LOD assignment · modding-forum extras https://www.modding-forum.com/guide/25-extra-components/ and LOD models https://www.modding-forum.com/guide/1-lod-models/ · alt:V bone list https://docs.altv.mp/gta/articles/vehicle/bones.html · gta5-mods Missing Speedometer Fix https://www.gta5-mods.com/misc/missing-speedometer-solution-in-replace-car-modes · modding-forum "weird dials" https://www.modding-forum.com/forums/thread/538-weird-dials · cfx forum "Configure seat layout" https://forum.cfx.re/t/help-configure-seat-layout/1399840 · vehiclelayouts example (PLOKMJNB/FiveM-Civ-Car-Pack) · police pack listings (Tebex partition = extra 10; modding-forum Crown Vic; gta5-mods 2016 FPIU), cited only for how they are built.
