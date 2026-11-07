# Blender → FiveM MLO, step by step (video study, 2026-11-08)

Use this when actually clicking through an MLO build: it lists every button and the mistakes the tutors made on camera. `mlo-authoring.md` stays the short, source-checked overview; where the two differ, **§0 below and `mlo-authoring.md` win over the videos**.

Contents: §0 hard rules vs tutor advice · §1 extract the building · §2 import · §3 open the exterior · §4 interior shell · §5 materials/UVs · §6 drawable, collision, vertex colour · §7 ytyp · §8 binaries, placement, manifest · §9 occlusion · §10 resource and testing · §11 clothing store · mistakes checklist · web sources.

Sources: the qDESAUCE "BLENDER TO FIVEM" course (series 1 #1-#12, series 2 #1-#5, clothing store #1-#2, teaser), read from the full auto-captions. Also Bady Design PART 01-03 and the 51-minute live stream, which have no captions; they were read from frames (contact sheets every 10-25 s plus zoomed crops). Anything marked "(from frames)" is a reading of the screen, not something the tutor said. Citations are `video-id [mm:ss]`.

Short ids used below. Series 1: a99U, 5iio, R3bo, SCHd, 1b5Y, SKqp, Iesr, NW_g, 1vZR, ttQD, oSJE, nTYh. Series 2: uUWc, uQjk, qPPr, 7ofI, CAj2. Clothing store: gtZZ, g6xc. Bady Design: CgE8, EjQf, j8g, cSYL (live).

Coverage gaps (say these honestly when the user asks about them):
- None of the videos teaches lights, room timecycle modifiers, entity sets, LOD distances for interior entities, or audio occlusion. qDESAUCE says those are in a paid course.
- Series 1 #2-#5 (5iio, R3bo, SCHd, 1b5Y) are generic Blender basics.
- The clothing-store pair stops after "open doors and windows → collision → occlusion". Racks, mirrors, counters and changing rooms are never shown.

## 0. Hard rules vs tutor advice (read first)

These rules come from real crashes and vanishing interiors on this server (bisected on La Puerta, 2026-10-14 to 10-18) and from how every working MLO on it is packaged. `check_mlo_resource.py` checks the ones it can see in XML.

| Hard rule (user's server) | What the tutors do | Verdict |
|---|---|---|
| One MLO instance per `*_milo_.ymap` + `.ymf` | They name the ymap freely (`hacker_lounge_interior`, `..._car_interior`, `testmlo`). It does hold one MLO entity, and they generate a ymf (oSJE [35:56–45:53], 7ofI [41:02–47:25], cSYL 41:40–43:45 from frames). | Keep their steps but **rename the ymap to `<name>_milo_.ymap`**. Put doors, props and occluder edits somewhere other than that ymap. |
| Never `DLC_ITYP_REQUEST` an MLO ytyp | qDESAUCE's fxmanifest is only `fx_version 'cerulean'`, `games {'gta5'}`, `this_is_a_map 'yes'` (SKqp [24:39]), so it agrees with the rule. **Many web install guides tell you to add `DLC_ITYP_REQUEST`** (e.g. xgamingserver, fivemx). | Ignore those guides. A Cfx forum thread ties a "DLC_ITYP_REQUEST of a ytyp that contains a MLO definition" to crashes (Rockstar Editor) — https://forum.cfx.re/t/rockstar-editor-while-trying-to-open-clip-build-3258/5374685 |
| Portal normal `(c1−c0)×(c2−c0)` points away from room_from, toward room_to. Decide the side by testing points ~0.3 m either side of the portal, never by the room-box centre. | Every tutor builds portals as From = room → To = limbo with the arrow pointing outward (oSJE [20:03–23:49], 7ofI [28:32]). Sollumz docs say the same ("go out from inside when limbo is one of the parts"). | Consistent. |
| Few rooms | Each tutor uses limbo + 1 room (oSJE [17:43]; 7ofI [27:10]; cSYL 31:40 from frames). | Consistent. |
| \|UV\| < ~50 (half-float) | They tell you to scale UVs **up** in the UV Editor to tile bricks smaller (1vZR [21:37–22:53], uQjk [32:37]). | **Conflict risk.** Tile with a smaller texel scale, cap the scale, then check max \|UV\| before export (snippet below). Never scale UVs ×10+ on a large wall. |
| Doors attached to a portal are not also in a room's attachedObjects | Not covered | Sollumz writes both if both ids are set; clear the room one. |

UV check before export (run through the `blender` MCP after asking; read-only):

```python
import bpy
for ob in bpy.context.selected_objects:
    if ob.type != 'MESH' or not ob.data.uv_layers:
        continue
    for uvl in ob.data.uv_layers:
        m = max((max(abs(d.uv.x), abs(d.uv.y)) for d in uvl.data), default=0.0)
        print(f"{ob.name} / {uvl.name}: max |UV| = {m:.1f}" + ("  <-- over 50, recenter or lower the tiling" if m > 50 else ""))
```

Other places where the advice conflicts or looks dubious:
- **Where the shell entity goes.** Both tutors and the official Sollumz tutorial put the interior shell entity in the **limbo** room (oSJE [24:18–25:55]; 7ofI [32:58]; Sollumz docs "add the room limbo to the entity"). The tutor's stated reason: without it the MLO shows in CodeWalker but not in game. Our skill says to attach entities to their rooms. Treat this as unresolved. Test both ways, and look for doorway flicker and rain on the floor. A forum answer also says to check the shell is in limbo when rain falls inside: https://forum.cfx.re/t/rain-falling-through-mlo/5331985
- **The MLO archetype comes from the collision object**, so its name ends in `_col`, and the ymap entity uses the `_col` name. qDESAUCE (oSJE [14:07]) and Sollumz docs (`tutorial_interior_col`) both do this. It is fine; just be consistent.
- **Vertex colour advice disagrees.** qDESAUCE fills `Color 1` with RGB **255/0/255** (oSJE [6:57–7:19]; "seemed to have done the best for me"). Sollumz docs use **G = 0.2, others 0**. Bady Design fills the shell green (cSYL 24:10, from frames). R = night darkness, so 255 red makes it dark at night. Prefer the Sollumz value as the starting point, then judge it in game at night.
- **Roughness wired straight into SpecSampler** (1vZR [13:44–18:25]; uQjk [30:31]). Specular is roughly the inverse of roughness and the tutors never invert it. Invert it, or use a proper spec map.
- **PNG→DDS on aconvert.com** (1vZR [14:38]) is an online upload. Prefer a local converter. Bady Design uses the free Folder2YTD tool (cSYL 39:10, from frames); downloading it needs the user's OK.
- **Doors in a separate ymap failed** (nTYh [14:53–21:29]: the door would not open). The later series adds doors as MLO entities on the portal (CAj2 [44:21]). Use that method.
- **Hiding vanilla props by moving them underground** inside an overridden vanilla ymap (nTYh [17:53]; CAj2 [54:04]). This streams a whole vanilla ymap, which other map resources may also override. Prefer the server's existing occluder/ymap tooling, and keep one owner per vanilla ymap.

## 1. Pick and extract the building (CodeWalker)

1. Pick a building that already has a floor inside and few openings (a99U [4:03–6:34]). Noclip through it first. **If the world or your ped vanishes inside, occluders are the cause** (a99U [6:58–7:22]).
2. CodeWalker: open the side panel → **Options**, enable **DLC** (and Mods), and pick the latest DLC level → **Save Settings**. Otherwise you get outdated files and miss collisions (SKqp [2:04–2:51]; g6xc [9:35]; oSJE [33:56]).
3. Press **T** for the toolbar. Click the **select** tool *before* the Move tool, or Move cancels (SKqp [4:30]). Open the **Selection** tab, set mode to Entity, select the building and copy its name (SKqp [6:07]).
4. **Tools → RPF Explorer**: search the name → right-click the `.ydr` → **Export XML**. Double-click it → expand → **Materials → Save All Textures** into the same folder (SKqp [7:43–10:57]; uUWc [6:38]). Bady Design keeps `xml ydr/`, `xml ybn/`, `xml ymap/` and `textures/` folders (CgE8 1:00–2:40, from frames).
5. **Collisions:** set Selection mode to **Collision** and export *every* `.ybn` that touches the building, including `hi@<name>.ybn` (Iesr [2:10–5:49]; uUWc [7:29]). One building can have 2+ ybns. **If you still can't walk in, you edited only one of them** (Iesr [12:38]). When search returns several versions, take the newest/patch one; gtZZ says "the biggest file" (g6xc [9:35]). The live search returned 14 hits across update/dlc packs (cSYL 3:20, from frames).
6. Export the building's `.ymap` too (e.g. `hei_id2_18_strm_0.ymap`) so Blender places everything at world coordinates (CgE8 1:30; EjQf 1:40, from frames). qDESAUCE skips this (uUWc [17:05]). He places by hand in CodeWalker, which costs accuracy.
7. **Don't move the exported texture files afterwards.** Blender loses them (gtZZ [17:36]).

## 2. Import into Blender

- **File → Import → CodeWalker XML**, or press **V** for the Sollumz pie menu (it only appears in Object Mode, gtZZ [29:41]). Pie items: Import/Export CodeWalker XML, Find Missing Textures, Convert Material, Convert to Drawable, Convert to Composite, Apply Flag Preset (EjQf 0:30, from frames).
- Pink model means missing textures → **V → Find Missing Textures** → point at the texture folder (SKqp [13:24–14:41]).
- The **ymap import options** include Skip Missing Entities, Exclude Entities, Instance Entities, Exclude Box Occluders, Exclude Model Occluders and Exclude Car Generators (EjQf 1:50, from frames). After import, delete the car-generator helpers.
- **Shift-click the eye icon** to hide or show a whole hierarchy. Turn off Overlays → Relationship Lines (Iesr [9:51–10:40]). Numpad `.` frames the selection (CAj2 [8:05]).

## 3. Open the exterior

1. Edit the exterior `.ydr`: Edit Mode → Face select → select the door/window faces → **X → Delete Faces** (SKqp [15:50–17:52]; uUWc [14:05]). Keep signs and decals (uQjk [3:16]). **Keep the light objects (small circles) in the building hierarchy.** Delete them and the facade goes black at night (gtZZ [19:09]). Delete geometry you don't need, because fewer faces means less load (gtZZ [27:16]).
2. Add the cut lines first with **Ctrl+R** loop cuts snapped to the old frame, then delete (NW_g [23:47–27:51]).
3. **Exterior collision (.ybn):** delete whole boxes that block the doorway with X in Object Mode. On the poly-mesh wall, use X-ray + Edge snap (icon blue) → Ctrl+R → delete the doorway face (Iesr [11:51–17:12]; CAj2 [9:26]). In the live stream a `METAL_GARAGE_DOOR` Bound Poly Box gets deleted (cSYL 35:50–37:05, from frames).
   - **After editing (not deleting) a bound object, always set N → Sollumz Tools → General → Set Sollumz Type = Bound Poly Mesh. Skip it and the collision breaks** (Iesr [17:12–19:10]; CAj2 [23:00]).
   - Keep the floor collision. Keep window boxes and vent boxes too; bullets use them (g6xc [2:52]).
4. Export the edited exterior ydr and both ybns under the **vanilla names**. **Don't forget the edited exterior**: series 2 forgot it once (7ofI [39:51]).
5. Iterate on collision between Blender and CodeWalker until you can walk through (CAj2 [27:16]).

## 4. Model the interior shell

1. Do all vanilla edits and exports **before** moving anything. If the building is skewed, rotate the whole set to X/Y, model, then rotate back (NW_g [6:51–10:31]; qPPr [19:24]).
2. Start from **one Plane** (Shift+A → Mesh → Plane), not a cube (NW_g [11:20]; uUWc [18:42]). Snap it (Vertex/Edge snap, Bady also ticks *Align Rotation to Target*, j8g 1:00 from frames) to the doorway's floor edge so the threshold is flush. Use G X / G Y to keep it level. Keep it slightly inside the outer wall (NW_g [18:06]).
3. Loop-cut where doors and windows will go *before* extruding (uUWc [23:02]). Select the boundary edges → **E Z** up to the ceiling (NW_g [20:32]; uUWc [29:25]). Bady types exact extrude values on the numpad (cSYL 11:15, from frames). Bridge the edge loop over a door to make the lintel (j8g 10:15, from frames). Close the roof with Alt-select the top loop → **F** (uQjk [21:53]), and do the roof last (uUWc [35:59]).
4. **Door/window frames:** Cube → I (inset) the front and back → X Delete Faces → select two opposite edges → F, repeat around the loop (NW_g [31:32–42:48]; qPPr [5:27]). Make frames **slightly oversized** so they hide seams and tolerate placement error (NW_g [42:00]; qPPr [48:03]). Use **Delete → Faces**, not "Delete Only Faces", or loose edges remain (qPPr [5:54–11:30]).
5. **Face Orientation** (Viewport Overlays → Geometry): blue faces render, red are invisible in game. Flip with **Alt+N → Flip** (oSJE [2:30–4:56]; uQjk [44:00]; cSYL 17:30–20:00, from frames).
6. Join with Ctrl+J, **selecting the interior last (active)** (NW_g [43:14]; qPPr [48:51]). Names use underscores (SCHd [5:40]).
7. **Origin + transforms:**
   - Bady duplicates the shell as a `location` object left at the world position, then moves the shell to 0,0,0 (cSYL 23:20–23:45, from frames). This matches the Sollumz docs' "mirror" + `General → Object Location & Rotation Tools` copy button.
   - Series 2 instead uses **Shift+S → Selection to Cursor** (cursor at origin) → **Object → Apply → All Transforms** before converting (7ofI [22:04]).
   - **Skipping Apply All Transforms caused the collision and shell to sit apart, a tilted building, a "ghost" and invisible walls** (oSJE [50:29–55:23]). The fix: apply, re-export ydr/ybn/ytyp, delete the old ymap and ymf, redo placement.

## 5. Materials, UVs, textures

- **N → Sollumz Tools → Drawables → Shader Tools**: filter "norm" → **normal_spec** → Create Shader Material. Flat pictures use `default`; glass uses **glass_env** (1vZR [11:19]; uQjk [25:37]; ttQD [8:03]). Sollumz docs use `normal`.
- Map Base color → **DiffuseSampler**, roughness → **SpecSampler** (invert, see §0), normal → **BumpSampler** with Color Space **Non-Color** (uQjk [30:31]). **Texture names must be unique**, or the game picks one at random (1vZR [15:51]).
- **Rename the UV map to "UVMap 0"** in Object Data → UV Maps. Without it the material shows a flat colour (1vZR [20:48]; uQjk [27:13]).
- Unwrap with **Cube Projection** for walls, Smart UV Project for odd shapes (1vZR [21:37]). Then check \|UV\| (§0). Assign each face set its own material slot and press **Assign** (1vZR [28:03]; uQjk [35:24]).
- Shine: specular intensity **0.2**, falloff **5** (caption unclear), fresnel **0.94** — an "experiment" value the tutor got from another video (1vZR [44:10–45:26]).
- Textures must be **DDS and power-of-two** (NW_g [45:13]; Sollumz docs). Download 2K from ambientcg.com, but **downsize early, not at the end** (1vZR [4:35]; uQjk [28:26]).
- **Embed or YTD:**
  - qDESAUCE ticks **Embed** per texture (Material → Sollumz → Texture Parameters). Forgetting it gave untextured walls in game (oSJE [30:18–31:10]; 7ofI [36:04]). Sollumz panel buttons: *Set all Textures Embedded / Remove all Embedded Textures / Set all Materials Embedded / Unembedded* (cSYL 29:10, from frames).
  - Bady instead **reuses the vanilla building's own materials** (e.g. `IM_Wall01`, `cmk_wall_brick_x1`) on the interior (cSYL 26:15–28:20, from frames). He then packs the texture folder into `test_mlo_shell.ytd` with Folder2YTD: Quality *Balanced*, Detect Transparency *By pixels*, Output *GTA V (.YTD)*, power-of-two threshold, **Generate MipMaps** on (cSYL 39:10, from frames).
- Vanilla glass and door textures can be found via forge.plebmasters.de → RPF Explorer → Save All Textures (ttQD [5:05]).

## 6. Drawable, collision, vertex colour

1. **Convert to Drawable**: V pie or Sollumz → Drawables → Create Drawable Objects, tick **Center to Selection**, leave **Auto-embed collision unticked** (oSJE [5:21]; 7ofI [23:20]).
2. **Vertex colours**: Data → Color Attributes → `+` → name `Color 1`, Domain **Face Corner**, Type **Byte Color** (oSJE [6:57]). For values see §0. Without them the ped's skin tone shifts at the portal and night colours are wrong (ttQD [18:29]).
3. **Interior collision**: Shift+D → right-click (stay in place) → **Alt+P → Clear and Keep Transformation**, rename `<name>_col`, remove its materials. Then Sollumz → Collisions → Create Bounds: type **Bound BVH** (7ofI), tick **Apply Default Flag** + **Center to Selection** → **Convert to Composite**. The hierarchy is `_col` → BVH → poly mesh (oSJE [8:30–11:18]; 7ofI [23:46]).
4. Select the poly mesh → Collision material **concrete** (also wood, glass, carpet; it drives footsteps and bullet FX) → **Create Collision Material** (oSJE [11:18–14:07]).
   - Set that material's **Sollumz → Room ID = 1**, matching the room (oSJE [17:43]; 7ofI [28:05]).
   - Bady names it `CONCRETE.room1` with Room ID 1, Procedural ID 0, Ped Density 0 (cSYL 31:15, from frames).
   - Sollumz docs: a different floor material per room so each gets its Room ID.
5. If a wall's collision sits too far inside, peds can't touch the wall. Move that collision face (CAj2 [55:22]).

## 7. YTYP: archetypes, rooms, portals, entities

1. Sollumz Tools → **Archetype Definition** → YTYPS `+`.
2. Select the **collision** root → type **MLO** → **Auto-Create From Selected**. Then select the drawable root → type **Base** → Auto-Create (oSJE [14:07–16:29]; 7ofI [25:51]). Bady's MLO archetype reads Asset Type *Assetless*, Name/Asset Name `test_mlo_coll` (cSYL 32:05, from frames).
3. MLO sub-tabs: Rooms, Portals, Entities, Timecycle Modifiers, MLO Flags, Entity Sets (oSJE [17:17]).
4. **Rooms**: **Create Limbo Room** first, then the room. Floor ID: limbo **0**, room **1** (oSJE [17:43–19:55]; 7ofI [27:10]). Set bounds with **Set Bounds From Selection** on the collision's corner vertices (cSYL 32:05, from frames; Sollumz docs).
5. **Portals**:
   - Enable **Show Portal Gizmo**. Edit the collision poly mesh in vertex mode and select the 4 **innermost** vertices of the opening while viewing **from outside**. Set From = room1, To = limbo → **Create From Vertices**. **The arrow must point outward**; use **Flip Direction** if not, and **Update From Vertices** after edits (oSJE [20:03–23:49]; 7ofI [28:32]; cSYL 33:20–33:45, from frames).
   - Windows: pick the inner 4 vertices because the glass blocks the view.
   - **One portal per door (a door plus the transom window above it counts as one) and one per window.** The car-shop had 8. **Forgetting a back window's portal = a wall you can't see through** (7ofI [28:32]).
6. **Entities**: Rooms → select room → Entities → **Add Object(s) as Entity** → set the entity's Room (tutor: limbo, see §0) (oSJE [24:18]).
   - Furniture and props **must be MLO entities in the ytyp, not ymap entities**, or they flicker or vanish inside (nTYh [2:04–3:16]).
   - Props without collision (some chairs) need your own collision or a substitute (nTYh [11:57]).
   - Static, non-door props get a static flag so they don't fall over (nTYh [9:57], caption unclear).
   - Some vanilla props break after game updates; swap in a lookalike (nTYh [4:05]).
7. **Doors**:
   - Get vanilla doors from plebmasters forge (category Objects, check it is an openable door) → Export XML → import only to size the frame. **Scale the frame, never the door** (7ofI [3:35–13:18]; ttQD [12:39–17:12]).
   - In CodeWalker: ytyp → MLO archetype → **Portal → Add Entity** = door name. Place it on the inner side of the portal. **Do not mark doors static** (CAj2 [44:21–53:14]).
   - **Portal numbering: Blender starts at 1, CodeWalker at 0** (Blender portal 6 = CW 5) (CAj2 [44:21]).
8. Export: **Export ytyp.xml**. For the drawable and the collision, **Select Hierarchy** (Outliner right-click) → Export CodeWalker XML (oSJE [27:29]; SKqp [18:38]). Bady's export dialog shows *Limit To Selected Objects*, *Export with ytyp*, *Apply Parent Transforms*, Mesh Domain *Face Corner*, LOD toggles (cSYL 34:35, from frames). Hidden objects don't export (Sollumz docs).

## 8. Binaries, CodeWalker placement, manifest

1. **XML in `stream/` does nothing.** In RPF Explorer enable **Edit mode** → New → RPF Archive ("converter") → drag the XMLs in to get binaries (SKqp [20:38–21:50]; CAj2 [39:50]). Bady drops them into `mods\mapping.rpf` (cSYL 40:00, from frames).
2. Project window: Folder → **Open Folder** → the `stream` folder (oSJE [33:56]; 7ofI [41:02]).
3. **New Ymap** → save. **Close and reopen the project before editing**, or CodeWalker glitches or crashes (oSJE [39:08]).
4. Ymap → **New Entity**: replace `prop_alien_egg_01` with the MLO (`_col`) archetype name (oSJE [35:56]; Sollumz docs). Paste the position from Blender, or move it with snapping **off** until portals line up with the openings (7ofI [41:02]).
   - Bady's entity: LodDist 200, lodLevel `LODTYPES_DEPTH_ORPHANHD`, priority `PRI_REQUIRED` (cSYL 43:20, from frames).
   - Then Calculate all flags and extents on the ymap (cSYL 41:40 from frames; Sollumz docs).
5. **Save the ytyp too, or the ymap won't save** (oSJE [44:40]; CAj2 says to save the ytyp "a thousand times").
6. **Tools → Manifest Generator → Generate → Save** into `stream` (oSJE [44:40–45:53]). The generated ymf lists imap→ityp dependencies **and an `Interiors` / `CInteriorBoundsFiles` entry naming the MLO's collision** (cSYL 43:45, from frames). That is why the ymf matters. Regenerate after every ytyp or ymap change (CAj2 [53:40]).

## 9. Occlusion

- CodeWalker Selection mode **Occlusion** (DLC on). Box occluders → right-click → **Delete Box**. Model occluders show as red triangles → select, drag slightly to confirm the selection, → **Delete Triangle**. Include roof occluders; delete only those blocking the interior view (oSJE [46:20–48:00]; 7ofI [46:13]; g6xc [10:28]).
- CodeWalker auto-adds the overridden `*_occl` ymap. **Don't rename it**; save it into stream.
- Leftover floor occluders cause slight flicker (g6xc [10:28]).
- Sollumz 2.9 can also import and export occluders (Occluders tab; Automatic / Boxes Only / Models Only), which is an alternative to deleting them in CodeWalker: https://docs.sollumz.org/documentation/maps/occluders
- On this server, use the existing `tools/occluders.ps1` workflow so you don't fight other resources over the same `_occl` ymap.

## 10. Resource and testing

- `stream/` holds: the edited vanilla `.ydr` and **both** ybns, the interior `.ydr` (+ `.ytd`), the `_col.ybn`, the `.ytyp`, the ymap(s) and the `.ymf`.
  - The live stream's final set: `hi@id2_13_0.ybn`, `id2_13_0.ybn`, `id2_13_build19.ydr`, `test_mlo.ytyp`, `test_mlo_coll.ybn`, `test_mlo_shell.ydr`, `test_mlo_shell.ytd` (cSYL 44:10, from frames).
  - **Forgetting the `_col.ybn` was a real mistake** (oSJE [37:05]).
- `fxmanifest.lua` sits **outside** `stream/` (SKqp [22:14]). `ensure` it, then restart.
- Leave the area before restarting the resource. Make sure the new files are actually copied to the server (nTYh [19:53]).
- Test list from the videos: walk in through every portal (cSYL 50:25). Check textures (z-fighting flicker, 7ofI [47:25]), garage-door sound (CAj2 [55:22]: none), night halo around windows and peds (nTYh [13:16]: "add lights"), and wall contact.
- Add our own checks too: rain, night, two players, and `check_mlo_resource.py`.

## 11. Clothing store (gtZZ, g6xc + what is NOT covered)

What the videos show:
- The location is **Leopolds** (near Vangelico and the city hall). Only the front part is converted. Vanilla mannequins stay, because they live in the vanilla ymap. They have no night LOD (gtZZ [34:47]).
- For collision, two `hei_bh1_09…` ybns are edited (caption unclear). Delete only the doorway boxes. Keep window boxes, vent boxes and the floor (g6xc [2:52]).
- Occlusion: delete triangles and boxes, including those on the roof. One occl ymap is produced and saved unrenamed (g6xc [10:28]).
- The tutor mentions possible storage and fitting areas (gtZZ [4:53]) but never builds them.

Not covered by any video. This is guidance from our skill and the Sollumz flags list, not from the tutors:
- **Racks, shelves, counters:** reuse vanilla clothing-store props (no streaming cost) as ytyp MLO entities in room1. Choose props by name in CodeWalker or plebmasters (category Objects). Give heavy fixtures collision.
- **Mirrors:** a GTA mirror is a **portal with the Mirror flag** (portal flag 4; with Mirror Using Expensive Shaders 16, Mirror Can See Directional 128, Mirror Can See Exterior View 1024, Mirror Floor 512). Its 4 corners sit on the mirror quad. Rooms that can see it need **Mirror Potentially Visible** (room flag 512). Mirrors are expensive, so use at most one or two. This is unverified in video; test in game.
- **Changing rooms:** small partitions inside room1. Don't add rooms for them.
- **Lighting:** retail needs bright, even light. The videos give no light settings. Use Sollumz lights in the drawable plus a bright `int_*` room timecycle, and test at night.
- **Clothing script:** the store menu is coordinates in the clothing script's config (illenium-appearance or qb-clothing style), not part of the MLO. Add the zone after the MLO is placed.

## Common mistakes the tutors call out (checklist)

These come from SKqp, Iesr, oSJE, nTYh, uQjk, qPPr, 7ofI, CAj2, gtZZ and g6xc:
- Forgot Origin to Geometry / Apply All Transforms.
- Forgot Select Hierarchy before export.
- XML put in stream.
- fxmanifest put inside stream.
- Edited only one of several ybns; forgot the `hi@` ybn or the edited exterior.
- Didn't set Bound Poly Mesh after editing collision.
- RPF Explorer not in Edit mode.
- UV map not renamed; texture not Embedded / not DDS; material not Assigned; normal map not Non-Color.
- Textures moved after export.
- Interior not selected last when joining.
- Snapping left on while placing.
- Missing window portal; portal index off by one.
- Ytyp or ymf not re-saved; vanilla ymap edit not saved.
- DLC off in CodeWalker.
- Occluders left in place.
- Building lights deleted.

## Web sources

- Sollumz "Creating Interiors" tutorial: https://docs.sollumz.org/tutorials/creating-interiors and sub-pages `/importing-from-codewalker`, `/texturing`, `/collisions`, `/create-ytyp`, `/export-blender`, `/create-ymap`.
  - Notable points: export both `hi@` and plain ybn; DDS power-of-two; vertex colour example G 0.2; a different floor material per room for Room ID; Create Limbo Room first; portal Room → Limbo with Flip Direction; shell entity in limbo; copy location via `General > Object Location & Rotation Tools`; Calculate flags/extents; Tools → generate manifest.
- Sollumz occluders: https://docs.sollumz.org/documentation/maps/occluders
- Doc index (archetype flags, lights, ymap entities, timecycle modifiers): https://docs.sollumz.org/llms.txt
- Cfx forum, rain through an MLO (suggestions: No Exterior Lights on rooms, portal normals outward, shell in limbo, seal gaps; no confirmed fix): https://forum.cfx.re/t/rain-falling-through-mlo/5331985
- Cfx forum, a ytyp with an MLO definition loaded via `DLC_ITYP_REQUEST` crashes the Rockstar Editor: https://forum.cfx.re/t/rockstar-editor-while-trying-to-open-clip-build-3258/5374685
