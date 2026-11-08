# Accessories and add-on parts: police gear, extras, tuning parts, small parts

How to model and rig parts that go on or come off a car: lightbars and siren lights, push bars and spotlights, extras, modkit tuning parts, custom wheels, and small details. Blender + Sollumz (free) only; most GTA tutorials use ZModeler 3 (paid, subscription), whose "dummy" = a Sollumz **bone**, "[COL]" = a Sollumz **bound** on a bone, "L0–L3" = Sollumz **LOD levels** (nYeVr126qIk 5:26). Meta files (carcols, carvariations, vehicles.meta flags) belong to `fivem-vehicle-mod`.

Citations: `(videoId m:ss)` = YouTube captions; `[measured]` = dumped read-only from vanilla `police3`, `sheriff2`, `fbi2`, `police4` and from the user's cars under `H:\FiveM\mods\police\car`; `[W:n]` = written sources at the end. GTA axes: +Y front, +Z up, +X passenger side.

Contents: 1. Pick the role first · 2. How Rockstar built police gear · 3. Siren lights and lightbars · 4. Spotlight, push bar, antennas, partition · 5. Extras · 6. Tuning (modkit) parts · 7. Custom wheels (rims) · 8. Modelling recipes · 9. Small parts and shaders · 10. Fitting workflow · 11. Checks and checklists · Sources

---

## 1. Pick the role first

| Role | Lives in | Bone | Collision | Toggled by |
|---|---|---|---|---|
| Integrated (always there) | car yft | the bone it moves with (`chassis`, `boot`, `bumper_f`…) | the car's bound on that bone | — |
| Extra | car yft | `extra_1`…`extra_9`, `extra_ten`, `extra_11`, `extra_12` | own bound + Use Physics if it has children or must collide | spawn flags / `SetVehicleExtra` |
| Siren light | car yft | `siren1`…`siren20` (+ `siren_glassN` lens) | lens only | carcols siren setting |
| Tuning part | **own yft** | carcols `bone` (attach point) | car's `mod_col_N` bone | mod shop / `SetVehicleMod` |
| Script prop | separate prop | — | prop's own | script at runtime |

Decide this before modelling; it fixes pivot, bone, collision and LODs.

## 2. How Rockstar built police gear [measured]

| Car | Part | Shader | Bone |
|---|---|---|---|
| police3 | lightbar housing | `vehicle_mesh` | `misc_a` (child of chassis) |
| police3 | lightbar lenses, 3 segments | `vehicle_vehglass` + flipped `vehicle_vehglass_inner` | `siren_glass1/2/3` (children of `misc_a`) |
| police3 | LED emitters just under the lens top | `vehicle_lightsemissive` | `siren1–4` (children of `misc_a`) |
| police3 | rear-deck / grille emitters, no lens | `vehicle_lightsemissive` | `siren5–8` / `siren17–20` |
| police3 | `siren9–16` | — | bones only: light + corona, no mesh |
| police3 | A-pillar spotlight | paint + mesh; lamp face lightsemissive | `extra_1`; lamp on child `extralight_1` |
| police3 | console unit (inferred) | interior2 + mesh | `extra_12` (no physics) |
| police3 | partition glass | `vehicle_vehglass` | `chassis` |
| sheriff2 | mirror lights with own lenses | lightsemissive + vehglass | `siren9/10` + `siren_glass4/5` |
| fbi2 | visor bar inside the windscreen top, no lens | lightsemissive | `siren2,5,7,8,17,18` |
| fbi2 | spotlight | — | `extra_ten` (no physics) |
| police4 | push bar | `vehicle_mesh` | `extra_1` (no physics) |

- Physics children in police3: `misc_a`, `siren_glass1–3`, `extra_1`, `mod_col_*`; **not** siren bones, not `extra_12`.
- Size: all 12 lit emitters = 44 tris; lightbar glass ≈ 568 tris; housing ≈ 470 verts; emitters 4–36 verts each.
- Emissive geometry comes before glass in the drawable's geometry order. Whether Sollumz preserves or needs an order: unverified (ZModeler users must move emissive above glass or it doesn't show through, tDavDny_Nx0 18:17; 1lemt-N7drw 22:40).
- In the user's um21yukonpd, light groups are extras with their sirens as children: `extra_1` (child of `boot`) → `siren1–5`, `extra_2` → `siren6–9`, `extra_3` → `siren10–15, 20`, `extra_4` → `siren18–19`. `16chargerpd` and `ram2500pd` have **no** `siren*` bones, so their siren settings can only wig-wag head/tail lights.

## 3. Siren lights and lightbars

**How a siren light works**
- A light = bone `sirenN` (light + corona origin) + optional small `vehicle_lightsemissive` mesh skinned to it. A bone alone still gives light and corona. Max **20** (`siren1`…`siren20`); SSLA's 32 is a client mod, not for FiveM [W:1].
- **Flashing = scaling:** the game scales the emitter up and down; off = shrunk, usually hidden inside the bar [W:1] (tDavDny_Nx0 11:35). **Mesh scale × carcols `scaleFactor` = visible size.** Default: mesh scale 0.5 with scaleFactor 2; keep scaleFactor low, high multipliers drift out of place after collisions [W:1]. Tutorials disagree (Amply 0.01, FZfkuJj5yx0 0:24–1:35; ZModeler 0.1 mesh / 0.015 dummy, Q4Wfa0bgcU0 11:01), and vanilla police3 uses small visible ~6 cm quads: pick one convention and keep mesh scale and scaleFactor consistent. Stale scaleFactors give "super massive sirens" (FZfkuJj5yx0 4:03).
- **Direction:** model each emitter **pointing to the front of the car**; carcols `delta` (radians, 180° = 3.14159274) rotates it. A light angled 45° toward the driver front needs the model rotated −45° to match; angled sirens also need `start` adjusted or the corona falls out of sync [W:1]. Rear-facing lights: rotate the emitter 180° and set delta to π (1lemt-N7drw 19:47). For reflections all round, use separate front- and rear-facing sirens (Q4Wfa0bgcU0 34:50).
- **Bone placement:** head at the emitter (Shift+S cursor to selected → bone head to cursor) (FZfkuJj5yx0 1:58–2:46). The corona appears at the bone ("at the axis of the siren object" [W:1]); keep it at the visible light, not inside the dash (tDavDny_Nx0 27:59).
- Leave ~1 mm between emissive meshes so they don't clip [W:1].
- **Physics:** off on siren bones; on for siren glass and extras (nYeVr126qIk 7:33; matches vanilla).
- **Every LOD that shows the light** needs the siren meshes, or they vanish at distance (4fHDu6fUw74 18:46).
- Sollumz has no siren page in its docs [W:6]; these steps rest on community videos + vanilla data.

**Lightbar build (Blender + Sollumz)**
1. **Housing / base / feet:** box/cylinder blockout + bevel, no subdivision cage; `vehicle_mesh` (or a paint layer) on a `misc_*` bone (police3 `misc_a`), or on `extra_N` if the bar must toggle (nYeVr126qIk 1:41).
2. **Lenses:** outer `vehicle_vehglass` + inner `vehicle_vehglass_inner` (flipped copy facing in), split into segments on `siren_glass1`, `siren_glass2`…, each with a bound using **CAR_GLASS_WEAK** so it breaks when shot; shattermap mode **Simple**; lenses need L0 **and** L1 (broken glass uses L1) [W:5].
3. **Emitters:** flat quads facing out, `vehicle_lightsemissive`, one module per `sirenN`; reflectors/LED bodies behind as `vehicle_mesh`.
4. **Parenting:** `siren_glassN` and `sirenN` are children of the housing bone or of the extra, so they move and hide together. Not parented to the extra → sirens stay visible when the extra is off (FZfkuJj5yx0 3:16, 10:34).
5. **Collision:** a box/hull on the housing bone (car metal) + one per lens (car glass weak), each a Sollumz bound linked to its bone (nYeVr126qIk 8:17–9:52).
6. **Rotators (old beacons):** keep the rotor module a separate `misc` object inside the siren's hierarchy so it inherits rotation without being scaled [W:3].

**Hidden lights:** visor (inside the windscreen top), rear deck, grille: emitters only, the vehicle glass or grille is the lens (fbi2, police4). Mirror lights get their own small lens (sheriff2). Wig-wag headlights are carcols only: an unscaled siren bone + corona at the headlight [W:3].

**Moving a vanilla lightbar to another car** (4fHDu6fUw74 2:39–7:18; nYeVr126qIk): import both cars, select the `misc_a` hierarchy (housing, glass, sirens), unparent, separate the bones into a new armature, fit and scale, Ctrl+J into the target armature, parent `misc_a` to `chassis` (rename if the target already has `misc_a`), re-link the bounds to the target's collision, **apply all transforms** (4:26), unembed materials, export, add the light textures to the ytd (16:21). Rockstar meshes stay inside GTA/FiveM only.

**Meta side** (siren setting id, colours, sequencers, rotation/flashiness, `scale`/`scaleFactor`, `delta`, `start`, rotator speed): `fivem-vehicle-mod` → `references/police-emergency.md`.

## 4. Spotlight, push bar, antennas, partition

- **A-pillar spotlight:** an extra (police3 `extra_1`, fbi2 `extra_ten`): housing on the extra + child bone `extralight_1` for the lamp face, whose faces get light ID 14–17 (extralight 1–4). Which script switches extralights in FiveM: unverified; a moving beam is script work, not modelling.
- **Push bar / bull bar:** cylinder with end faces deleted, extrude loops and rotate in 30° steps for elbows, Mirror (clipping), plates from cubes with the hidden back face deleted, bevel only edges that catch light (wk9MX-mKpfs 2:21–11:31); winch from boxes (h7EM-CVXTpg). Two rigs:
  1. **Toggleable extra** (police4 `extra_1`): mesh on `extra_N`, collision boxes roughly following the bar (HnpvnOLblLA 2:58–7:35).
  2. **Always on, rams like a bumper:** add the bar faces to the `bumper_f` vertex group and stretch the `bumper_f` bound forward over it (V5xd2uq-KfY 0:56–2:37, ZModeler; Blender equivalent inferred).
- **Antennas:** 5–6-sided closed tubes on a base disc (single faces vanish under culling), on an extra or `misc_*` so they can be removed. KG's shrinkwrap attach trick is in car-workflow §6.
- **Partition / cage:** glass partition = `vehicle_vehglass` on `chassis` (police3); bars on an interior extra or as a tuning part. Interior gear: `interior.md` §10.

## 5. Extras

- **Names:** `extra_1`…`extra_9`, **`extra_ten`**, `extra_11`, `extra_12` [W:7]. `extra_13/14` may exist on some cars (natives page saw 14 on b944) but the names are unverified.
- **What fits:** anything toggled whole: lightbar or light groups, push bar, spotlight, antennas, laptop, cage, slicktop cover.
- **Children** (sirens, siren glass, nested extras) must be parented to the extra bone to hide with it.
- **Collision:** give an extra a bound + **Use Physics** when it has children or must collide; "without one, children can remain visible" [W:7]. Childless cosmetic extras can skip it (vanilla police4 `extra_1`, fbi2 `extra_ten`, `extra_12`). Bound named e.g. `extra_1.col`, material car metal (car glass weak for lenses) (nYeVr126qIk 8:17).
- **Parts on moving panels** go on an extra parented to that panel's bone (um21yukonpd `extra_1` under `boot` opens with the tailgate; police3 `siren13` under `door_dside_f`).
- Turning on an extra with collision needs a repair/respawn to take effect, and `SetVehicleExtra` reportedly repairs the car (community claim, HnpvnOLblLA 9:21; [W:9]).
- Spawn rules (`requiredExtras`, `extraIncludes`, `FLAG_EXTRAS_*`, `FLAG_HAS_INTERIOR_EXTRAS`) and the script native: `fivem-vehicle-mod` → `police-emergency.md`.

## 6. Tuning (modkit) parts

**The pivot rule.** The game attaches a part directly to the carcols `bone`. Its pivot must be at that bone's head and the part sit at the world origin; "if there is an offset … it will be floating" (8fodj9quXzQ 0:23–3:29). A part bound to the wrong bone floats, or fits but no longer opens with the bonnet [W:11].

**Blender + Sollumz steps (8fodj9quXzQ)**
1. Duplicate the car file; keep the drawable empty, the part and the armature; delete every bone but one, rename it (e.g. `root`).
2. Rename the hierarchy to the part's yft name: `<car>_<part>_<n>` (e.g. `mycar_spoil_01`, `_bumf_01`, `_skirt_01`).
3. 3D cursor to the attach bone's head → Object > Set Origin > Origin to 3D Cursor → **Alt+G** (clear location).
4. Rename the vertex group to the root bone and assign all faces.
5. LODs High / Medium / Low (L0–L2); "you don't need L3 on tuning parts" (pzWJuN9ZTQA 3:08). Very High optional.
6. Export as its own yft; carcols lists it in `visibleMods` (`fivem-vehicle-mod` → `modkits-liveries-sirens.md`).

**Collision: `mod_col_N` in the car, not in the part**
- Parts carry no collision. Add a bone `mod_col_1`, `mod_col_2`… to the **car** (duplicate a bone; centre at the origin, or inside the boot so a spoiler's collision opens with it), give it a bound, and turn on **Use Physics**, otherwise the collision does nothing (8fodj9quXzQ 14:17; pzWJuN9ZTQA 18:15). carcols `collisionBone` points to it; it only becomes solid when the part is fitted.
- `mod_col_10` breaks the naming pattern (muto-atlas). Tick *Auto Calculate Bonetags* when bones were added.
- Engine dress-up and parts that touch nothing: collisionBone `chassis` (8fodj9quXzQ 13:34). Collision material `phys car void` is shoot-through but still blocks peds (pzWJuN9ZTQA 15:50). Big mod collisions push the camera back (14:41).

**Stock parts on their own bones**
- `turnOffBones` hides the visual **and** collision of every listed bone while the part is fitted (8fodj9quXzQ 11:04). So every stock piece a part replaces must sit on its own bone: stock spoiler on `misc_h`/`misc_t`, skirts on `misc_d`, exhaust tips on `exhaust`/`misc_f`; bumpers and bonnets turn off `bumper_f` / `bonnet` themselves. Unique `misc_x` names, never duplicates.

| Part | `type` | `bone` | Notes |
|---|---|---|---|
| Boot spoiler | VMT_SPOILER | `boot` | mod_col under boot |
| Roof/fixed wing, roof rack, bed cover | VMT_SPOILER / VMT_ROOF | `chassis` | |
| Front bumper / splitter | VMT_BUMPER_F | `bumper_f` | off `bumper_f` |
| Rear bumper / diffuser | VMT_BUMPER_R | `bumper_r` | |
| Skirts / step bars | VMT_SKIRT | `chassis` | off `misc_d`/`misc_g` |
| Bonnet / scoop | VMT_BONNET | `bonnet` | off `bonnet` |
| Grille | VMT_GRILL | `chassis` or `bumper_f` | |
| Fender flares | VMT_WING_L/R | `chassis` | |
| Exhaust tips | VMT_EXHAUST | `chassis` | off `exhaust`/`misc_f` |
| Cage, ladder rack | VMT_CHASSIS / VMT_ROOF | `chassis` | |
| Seats / wheel | VMT_SEATS / VMT_STEERING | `chassis` / `steeringwheel` | |
| Engine dress-up | VMT_ENGINEBAY1–3 | `chassis` or `engine`/`engineblock` | shakes with the engine on the engine bone (tCeJpvb3Tu8 4:56) |
| Livery part | VMT_LIVERY_MOD | `chassis` | |

(From the user's 83 carcols files [measured] and the tutorials.) Two of the user's Shelby parts are in car space with no bone offset (one would float by this rule); check such downloaded parts in game.

## 7. Custom wheels (rims)

Both wheel tutorials use ZModeler 3 (paid); the rules carry over to Blender + Sollumz, the exact Sollumz clicks are unverified.

**A. Replace the car's own wheel** (`wheel_lf` in the car yft; only `wheel_lf` has geometry, the game copies it to the other wheels — engine-bay §7) (2re9Hv-n6CY)
1. Hide the old wheel; give the new wheel's LOD meshes the old wheel's local axes so the pivot is at the hub centre (1:13–2:00).
2. Left view: scale uniformly on X/Y until the tyre matches the old one, then the width on X separately (2:00–3:10).
3. L0–L3 under the wheel; L3 lighter than L2 (3:10–3:56, 7:56). A paintable rim material takes the in-game wheel colour (3:56). The brake disc is part of the wheel mesh (4:19); the caliper stays on `hub_*`.
4. **Burst-tyre scale:** when a tyre pops GTA "scales everything that is outside of a certain point to zero", so a properly built wheel keeps a **clear gap between rim lip and tyre bead**; tyre vertices too close to or behind the rim stretch and look melted (5:26–6:12). Duplicate the wheel collision, scale it down into that gap, read its scale (0.293686 in the video) into vehicles.meta `wheelScale` (and `wheelScaleRear` if the rear wheels differ), delete the helper (4:42–6:58). Test by shooting the tyres (9:10).

**B. Add-on rim in the mod-shop wheel list (carcols `<Wheels>`)** — from the user's own `H:\FiveM\mods\police\car\Mustang\lore\shelby20\data\carcols.meta` lines 805–821 [measured, read-only]:
```xml
<Wheels>
  <Item> <!-- VWT_SPORT -->
    <Item>
      <wheelName>wheel_shelby20_01</wheelName> <wheelVariation />
      <modShopLabel>shelby20_01</modShopLabel>
      <rimRadius value="0.348500"/> <rear value="false"/>
    </Item>
  </Item>
```
- Model streamed as `stream/wheel_shelby20_01.ydr`; manifest `data_file 'CARCOLS_FILE' 'data/carcols.meta'`.
- **The outer `<Item>` position is the wheel type.** Order (the full 11-slot list in the user's `Lore car\Sport\Coquette L8\ori\data\carcols.meta`, lines 560–575 [measured]): VWT_SPORT, VWT_MUSCLE, VWT_LOWRIDER, VWT_SUV, VWT_OFFROAD, VWT_TUNER, VWT_BIKE, VWT_HIEND, VWT_SUPERMOD1, VWT_SUPERMOD2, VWT_SUPERMOD3 (11 types).
- **Caution:** the shelby20 file has only 7 outer items and its comments skip LOWRIDER/SUV/OFFROAD/TUNER. It works only because its single real rim sits in the first slot (SPORT). A rim for a later type needs every earlier slot present as an empty `<Item/>` (inferred from the order, unverified in game). Don't copy that file as a template.
- **Rim model prep (SRmXFJETx_E):** textures **embedded in the ydr** (a texture group named after the wheel), otherwise "they're not gonna work" (1:08–1:22); name ends in two digits, `_01` (1:22, 2:25); **pivot centred on the wheel**, or "they rotate dumb" (1:42–2:06); L0/L1/L2 copies (2:25–3:26); wrong textures show green (4:22). Sollumz equivalent = embedded textures in the drawable (unverified).
- Replace mods that overwrite a vanilla rim (e.g. `wheel_hiend_03` in `wheels_mods.rpf`, sometimes plus `vehshare.ytd`) change it on every car; on FiveM prefer route B (names from gta5-mods listings, unverified).
- Community notes, low confidence: `wheelName` must match the model name exactly; many rim packs exceed 16 MiB; LS Customs menus can show add-on names as "null"; carcols load order matters on first connect [W:12].
- **Unverified:** what `wheelVariation` and `rear` do (bikes, rear-only rims), whether `modShopLabel` needs a text entry to show, the vanilla wheel ydr names, and whether a rim ydr may carry its own tyre (the `wheelScale` gap rule comes from one ZModeler source).

## 8. Modelling recipes (free Blender)

- **Start from the body:** duplicate the faces under the part, separate (P), extrude/solidify outward, so it sits flush (rS6oHfzudwU 1:33); or Shrinkwrap (Project) onto the body with Subdivision above Shrinkwrap (lA4q_yteoLc 3:29).
- **Spoiler:** cube + Mirror, airfoil by loop cuts, bevel outer loops 1–2 segments, keep quads (uaibNn-un1o 2:16–13:35). Low-poly: boot faces → Solidify → Weighted Normal (Keep Sharp) → Mirror (rS6oHfzudwU 2:43).
- **Bumper / body kit:** from the existing bumper, delete half, Mirror; Weighted Normal + mark sharp; 3-segment bevel instead of crease for flare lines (1JDiK78wHwQ 1:11–7:45).
- **Fender flares:** half circle on the arch → extrude along normals → shear to taper → delete clipped body faces (ETZBIp96oic).
- **Hood vents/scoops** without wrecking reflections: cut with support loops, then Shrinkwrap to a clean hood copy with a vertex group excluding the rim (7UgocT6IIWY 0:25–5:24).
- **Holes:** Bevel (limit width) + live Boolean; fine on flat or hidden areas (Krqgk036VE0).
- **Exhaust tips (low-poly):** 6-vertex cylinder, 30° bend steps, inset + extrude in, dark inside (PTQFRrNCPrM 2:27–6:24).
- **Roof / ladder rack:** rails from scaled cubes, 5–6-sided rungs with ends deleted, supports sunk into the roof with hidden faces deleted (ATniHgNarcI 1:45–17:22).
- **Mirrors:** from a vertex off the body, extrude the housing, inset + extrude concave glass, arm into the door (gOcb0VmIuII; DwlMDzLGZHU 4:12). Indicator in the mirror = lightsemissive faces with the indicator light ID.
- **Door handles:** cube with the inner face deleted, one face pulled for the grip, sunk into the body (DwlMDzLGZHU 0:40); recessed with a boolean (vgh9VLwqBBg).
- **Wipers:** static only (low-poly blade + arm) (EF8CJUx3HNY). Animated wipers need single-player ASI mods (VehFuncs/EVF, P1CX4_iLAmI, kiUuCGiMXu4), not usable on FiveM (inferred).
- **Mud flaps, tow hooks, hitch, fuel cap, roof rails, step bars, tool boxes** (no captioned tutorial, still none after a second search on 2026-11-08 — results were real-car fitting videos; general method, unverified): low-poly box/cylinder + bevel; step bars as VMT_SKIRT, tool box / bed cover as VMT_ROOF/CHASSIS on `chassis`, hitch on a `misc_*` at the rear, spare wheel on its own misc bone (`misc_stepney` seen in the user's Silverado).
- Apply Subdivision, Shrinkwrap and Weighted Normal before export; whether Sollumz keeps custom split normals is unverified.

## 9. Small parts and shaders

| Use | Shader |
|---|---|
| Badges, logos (alpha quads; vanilla police3 badges = 4 tris) | `vehicle_badges` |
| Extra decals, scratches | `vehicle_decal` / `vehicle_decal2` |
| Metal/plastic parts (bars, racks, exhaust) | `vehicle_mesh` |
| Body-colour parts | `vehicle_paint*` + paint layer |
| Plate (keep the vanilla plate mesh; the game draws the numbers) | `vehicle_licenseplate` |
| Whole wheel incl. hubcaps | `vehicle_tire` (wheels only) |
| Lights without light IDs (always lit, e.g. the user's cosmetic LED bars) | `vehicle_lightsemissive` |
| Interior gadgets, screens | `vehicle_interior2`, `vehicle_dash_emissive` |

- Existing 3D badges are matched in 3D (T1 lesson); new badges are usually decal quads.
- Delete faces nobody sees (backs of plates, bottoms sunk into the body); 5–6 sides for small rods; arrays for slats and rungs.
- Vertex colours: R = AO, G = deformation, B = burn; repaint AO where a part changed (pzWJuN9ZTQA 1:16).
- Budgets (measured, adds only when fitted): bed cover 242 tris, bull bar 1.75k, exhaust 2.4k, spoiler 2.8k, front bumper ≈ 10k; spotlight extra ≈ 130 verts. Use the same materials in every LOD [W:2].

## 10. Fitting workflow (Blender + Sollumz)

1. **Import** the car (Split By Group, Import with _hi) and any donor; find missing textures (nYeVr126qIk 1:03).
2. **Pick the role** (§1).
3. **Integrated / extra / siren (inside the car yft):**
   - Fit the mesh, **apply all transforms** (Ctrl+A).
   - New bone: duplicate an existing bone, rename exactly (`extra_1`, `siren6`, `misc_x`, `mod_col_2`), head at the pivot, parent (`chassis`, `boot`, the extra, `misc_a`). **Rename away any `.001` suffix**: the user's cars have `brakelight_m.001`, `misc_f.001` (whether Sollumz strips them: unverified; don't rely on it).
   - Vertex group named exactly as the bone; Drawable Model under the car's `.mesh`; Armature modifier to the car armature.
   - Use Physics: on for extras with children, siren glass, `mod_col_*`, doors/bonnet/boot; off for siren bones.
   - Bound on the bone, right material, one convex hull per collision mesh (JtAWRNCIT-k 42:24). Tick *Auto Calculate Inertia/Volume* if collisions changed, *Auto Calculate Bonetags* if bones were added.
4. **Tuning part:** §6.
5. **LODs:** every new mesh in High/Medium/Low (Data → Sollumz LOD); parts merged into chassis go into each LOD mesh; glass L0 + L1.
6. **Back-face culling preview**; emissive visible through lens/glass.
7. **Export:** unembed materials, export, add part textures to the ytd; re-import the exported XML to check bones and sirens (FZfkuJj5yx0 7:35).

## 11. Checks and checklists

**In game:** extras toggle and their children disappear; extras with collision work after repair/respawn; sirens flash with the right colour, size and direction (night test for reflections); siren glass breaks when shot; push bar collision actually hits; tuning parts sit on the car and move with their bone (spoiler opens with the boot), stock part hidden, mod collision works; LOD distances; lights dead → check for a siren id clash (`fivem-vehicle-mod`).

**Police car**
- [ ] Lightbar: housing on `misc_*` or an extra; lenses `siren_glassN` (outer + inner glass, CAR_GLASS_WEAK, Simple, L0 + L1); emitters per `sirenN`; front and rear-facing; model rotation matches delta
- [ ] Visor, rear deck, grille, mirror lights; wig-wag in carcols
- [ ] Spotlight as extra, lamp face on `extralight_N` with light ID
- [ ] Push bar as extra (collision boxes) or merged into `bumper_f`
- [ ] Antennas (closed tubes), partition glass on chassis, cage/laptop as interior extras
- [ ] Vanilla plate mesh; steel wheels/hubcaps with `vehicle_tire`
- [ ] Sirens ≤ 20, in every LOD that shows them, parented under their extra
- [ ] Bone names exact, no `.001`; meta (`requiredExtras`, `FLAG_EXTRAS_STRONG`, siren id) via `fivem-vehicle-mod`

**Civilian tuning**
- [ ] Each part its own yft, pivot at the attach bone, part at the origin, LOD L0–L2
- [ ] Replaced stock parts on their own bones for `turnOffBones`
- [ ] `mod_col_N` bones with Use Physics where collision is needed; spoiler's under `boot`
- [ ] Unique modkit id (`fivem-vehicle-mod`)
- [ ] Custom rim: pivot at the hub centre, textures embedded, `_01` name = `wheelName`, right outer `<Wheels>` slot with all earlier slots present; rim–tyre gap + `wheelScale`/`wheelScaleRear`, shoot-the-tyre test

**Truck / work vehicle**
- [ ] Bull bar + winch; LED bar (always-lit emissive or siren-driven)
- [ ] Roof/ladder rack, bed cover, tool box (VMT_ROOF/CHASSIS + mod_col), step bars (VMT_SKIRT), flares (VMT_WING_*), mud flaps, hitch (`misc_*`), spare wheel
- [ ] Parts on the tailgate skinned to `boot`

---

## Sources

Videos (https://www.youtube.com/watch?v=<id>, captions read 2026-11-08): 8fodj9quXzQ, JtAWRNCIT-k (Lola Car Dev, Blender + Sollumz tuning parts / full car) · nYeVr126qIk, FZfkuJj5yx0 (Amply, lightbars and sirens in Blender + Sollumz) · 4fHDu6fUw74 (Fadilj, siren tutorial in Blender) · Q4Wfa0bgcU0 (Cesta, ZModeler) · 1lemt-N7drw, HnpvnOLblLA, V5xd2uq-KfY (McGinlay, ZModeler: rear lights/deltas, rambar extra, rambar collision) · tDavDny_Nx0 (Paul Modications, ZModeler) · H4Ze4Mc2HX8 (Lil DizNick, extras always on) · fTAIm4OyzzE (northbayjoe, ZModeler tuning parts) · tCeJpvb3Tu8 (autochan) · pzWJuN9ZTQA, TYQHfPLaEQw (13Stewartc, mod parts, livery yft) · wrac7MJR0Uk (Radit, UV template) · wk9MX-mKpfs, h7EM-CVXTpg, ATniHgNarcI, PTQFRrNCPrM, DwlMDzLGZHU (BillyMcDev low-poly truck parts) · _PX9OsQBIq0, vgh9VLwqBBg (Versus 53) · uaibNn-un1o (Steven Brooks, spoilers) · rS6oHfzudwU, 1JDiK78wHwQ, ETZBIp96oic (kev__) · lA4q_yteoLc, FSbgOOz-pN8, Krqgk036VE0 (Aryan) · 7UgocT6IIWY (hood vents) · gOcb0VmIuII (Enpix, mirror) · EF8CJUx3HNY (static wipers) · P1CX4_iLAmI, kiUuCGiMXu4 (animated wipers, single-player ASI only) · added 2026-11-08: SRmXFJETx_E (Zeakor Designs, add-on wheel ydr, ZModeler) · 2re9Hv-n6CY (13Stewartc, replace vehicle wheels + `wheelScale`, ZModeler) · 2zTuDKVTVOc (custom wheels to FiveM; captions music-only, not read).

- [W:1] modding-forum, Setting Up Emergency Lights https://modding-forum.com/guide/18-setting-up-emergency-lights
- [W:2] modding-forum, Common Issues https://www.modding-forum.com/guide/11-common-issues-with-vehicle-mods-and-their-solutions/ ; Materials and Shaders https://www.modding-forum.com/guide/14-materials-and-shaders/
- [W:3] modding-forum, Rotator Lightbars and Wig-Wags https://www.modding-forum.com/guide/20-emergency-lights-rotator-lightbars-and-wig-wags/
- [W:4] Sollumz docs, Vehicle Shaders https://docs.sollumz.org/documentation/fragments.yft/vehicle-shaders
- [W:5] modding-forum, Glass Collisions https://www.modding-forum.com/guide/9-glass-collisions/
- [W:6] Sollumz docs: Bone Physics, Collision Physics, Vehicle Light IDs, Vertex Groups/Hierarchy/Armature, LOD Assignment (https://docs.sollumz.org/llms.txt index; no siren or extras page)
- [W:7] modding-forum, Extra Components https://www.modding-forum.com/guide/25-extra-components/
- [W:8] citizenfx/natives SetVehicleExtra https://github.com/citizenfx/natives/blob/master/VEHICLE/SetVehicleExtra.md
- [W:9] Cfx forum, SetVehicleAutoRepairDisabled with SetVehicleExtra https://forum.cfx.re/t/unexpected-behaviour-of-setvehicleautorepairdisabled-with-setvehicleextra/841872 ; Luxart docs, Extra Integrations https://docs.luxartengineering.com/shared-plugins/extra-integrations
- [W:11] modding-forum thread 665, dummy positioning on tuning doors (search snippet)
- [W:12] Cfx forum (search-result summaries only): https://forum.cfx.re/t/custom-wheel-pack-add-on/55906 , https://forum.fivem.net/t/add-on-vehicles-no-modifications/119634 , https://forum.cfx.re/t/how-to-add-rims/112288 ; replace-rim listings https://www.gta5-mods.com/vi/vehicles/vw-clubsport-gti-rim , https://uk.gta5-mods.com/vehicles/dws-rim-replace-paintable
