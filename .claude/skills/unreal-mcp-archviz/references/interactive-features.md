# Interactive archviz features (UE 5.x)

What the Unreal-style "interactive apartment" reels show, and how to build each piece so it works in the editor **and** a packaged build, and can be driven both from in-game UI (UMG) and from the local web panel (Remote Control). Written from Epic docs and community tutorials; **not built in a live UE 5.8 editor** — Blueprint graphs below are descriptions, not exported assets.

One rule for all of them: put the logic in **one `BP_ArchvizController` actor** with BlueprintCallable functions (`SelectUnit`, `SetTimeOfDay`, `SetSectionHeight`, `SetSectionEnabled`, `SetSlotMaterial`, `StartMeasure`…). UMG buttons call those functions; the web panel calls the same functions through `PUT /remote/object/call` (see `remote-control-panel.md`). One implementation, two front ends, and the packaged build has no editor Python to fall back on.

| Feature | Core UE pieces | Remote-Control-callable |
|---|---|---|
| Unit / lot info panel | DataTable + struct, UMG widget, click via line trace | `SelectUnit(LotId)` |
| Compass + minimap | UMG image rotated by camera yaw; floor-plan image or Scene Capture 2D (orthographic) | read-only |
| Time of day | **SunSky** actor (Sun Position Calculator plugin) or Directional Light + Sky Atmosphere + Sky Light (Real Time Capture) | `SetTimeOfDay(Hours)` |
| Section (cut) mode | Material Parameter Collection + plane test in the master material (Masked) | `SetSectionHeight(cm)` / `SetSectionEnabled(bool)` |
| Measure tool | two clicks → line traces → distance / 100 = metres | `StartMeasure()` / `ClearMeasure()` |
| Material & furniture changer | **one master material + Material Instances**; Variant Manager optional | `SetSlotMaterial(Slot, MI)` / `SwapSlotMesh(Slot, Mesh)` |

## 1. Unit / lot info panel
- Data: a struct `FUnitInfo` (LotId, Area_m2, Bedrooms, Bathrooms, Orientation, Floor, Status, Price, PlanImage) and a **DataTable** imported from CSV, so the sales team edits a spreadsheet, not Blueprints. Units in the table are m² and metres — UE works in cm; convert only for display.
- Picking: each unit's floor or a simple invisible box volume carries a tag or a component with `LotId`. On click: `GetHitResultUnderCursorByChannel(Visibility)` (PlayerController; enable `bShowMouseCursor` and click events in the controller) → read the tag → `SelectUnit(LotId)` → DataTable `GetDataTableRow` → fill the widget.
- Highlight the selected unit with a Material Instance parameter (emissive tint) or Custom Depth + a post-process outline; don't swap whole materials for a highlight.
- Orientation text ("North-west facing living room") should come from the same North Offset the sun uses (section 3), so the panel and the shadows agree.

## 2. Compass and minimap
- **Compass**: a UMG image whose render angle = `−(CameraYaw − NorthYaw)`; `NorthYaw` is the world yaw that points north (keep it equal to SunSky **North Offset**). A strip compass instead scrolls a texture's U by yaw / 360.
- **Minimap, cheap and sharp (recommended)**: a top-down floor-plan image (from `floorplan-to-blender`'s SVG or one orthographic render) plus a dot/arrow. Map world XY → image UV with two reference points measured once. No extra rendering cost (rule of thumb).
- **Minimap, live**: Scene Capture Component 2D, **Orthographic**, Ortho Width = building width, pointing down, into a Texture Render Target 2D (512×512 is plenty, per a 2026 community guide), shown in a UMG Image via a material. Turn **Capture Every Frame off** and call `CaptureScene` only when something changed — continuous capture renders the scene again every frame. Hide roofs/ceilings from the capture with `HiddenActors` / show-only lists.

## 3. Time of day and lighting control
- **SunSky actor** (plugin **Sun Position Calculator**, Edit ▸ Plugins ▸ Misc): one Blueprint actor bundling Directional Light, Sky Light and SkyAtmosphere, positioned from **Latitude, Longitude, Time Zone, North Offset, Month, Day, Daylight Saving settings and Solar Time** (Solar Time is a float in 24-h time: 12:30 = 12.5 — Epic docs). Use it when the client cares about *real* sun angles for a real site.
- The Sky Light has **Real Time Capture** on by default (Movable/Stationary only), so the sky lighting follows the sun; keep it on for a time-of-day slider.
- `SetTimeOfDay(Hours)` on the controller: set SunSky `SolarTime` and call its refresh/update function (the SunSky Blueprint recomputes the sun on property change in the editor; which function to call at runtime is **未验证** — open the SunSky Blueprint and look for the update/refresh function it uses in its Construction Script). Fallback without the plugin: rotate the Directional Light's pitch (−90° = noon overhead, 0° = horizon) and yaw; with **Atmosphere Sun Light** ticked on the Directional Light, Sky Atmosphere colours the sky from that rotation.
- Night: interior lights on via a light group in the controller (`SetInteriorLights(bool)`), exposure in an unbound Post Process Volume — **fix the exposure range** per mode (day/night) or auto-exposure pumps while the sun moves.
- From the web panel: call `SetTimeOfDay` with `{"Hours": 17.5}`. Writing `SolarTime` directly with `PUT /remote/object/property` may not trigger the recompute (未验证) — the function route is safer.
- Lumen handles a moving sun in real time; expect a short GI lag while it converges (Lumen temporal accumulation), so animate time smoothly rather than jumping.

## 4. Section (cut) mode
Current practical approach (no official "section plane" feature for runtime found; Epic forum consensus):
1. A **Material Parameter Collection** `MPC_Section` with vector `PlanePoint`, vector `PlaneNormal`, scalar `Enabled`.
2. In the **master material** (section 6): `d = dot(AbsoluteWorldPosition − PlanePoint, PlaneNormal)`; `OpacityMask = lerp(1, step(d, 0), Enabled)` (keep pixels below the plane). Blend Mode **Masked**. Every material that should be cut must be (an instance of) this master — another reason for the master-material rule.
3. `SetSectionHeight(cm)` sets `PlanePoint.Z` with `SetVectorParameterValue` on the MPC; the cut moves live at full frame rate.
4. **Cap**: the masked method leaves walls hollow. Cheap fix: with **Two Sided** on, colour back faces flat dark (`TwoSidedSign` node → emissive/base colour), which reads as a poché section from most angles. A true solid cap needs mesh slicing (Procedural Mesh `SliceProceduralMesh`) once the plane stops — heavy; usually not worth it for archviz.
5. Caveats: Masked costs more than Opaque, also for Nanite (programmable raster path, 未验证 how much in 5.8); **Lumen/shadows may still see the cut-away geometry** (distance fields and the surface cache don't know your mask; behaviour 未验证 — test: section a room and check whether the removed ceiling still shades it). Often that's what you want (the room keeps its interior light). If not, hide whole actors instead.
6. Simplest robust alternative for a "dollhouse" view: tag roof / ceiling / upper-floor actors and `SetActorHiddenInGame(true)` per storey. No material work, clean edges, Lumen updates. Use the plane cut only for an arbitrary moving cut.
7. Third-party Fab plugins exist that clip per pixel and fill the cut (one is UE 5.8 / Win64 only and needs its materials patched) — paid; mention only if the user asks.

## 5. Measurement tool
- Mode on → first click: `GetHitResultUnderCursorByChannel(Visibility)` → store `ImpactPoint` A; second click → B. Distance `= Vector_Distance(A, B) / 100` → metres; show 2 decimals (`"3.47 m"`). Also show ΔZ for heights.
- Draw: a thin cylinder static mesh or spline mesh between A and B (DrawDebugLine is **not** in shipping builds), and a UMG label at the midpoint via `ProjectWorldToScreen` each tick.
- Snapping: optional — snap to the nearest of A/B on surfaces facing ±X/±Y (so wall-to-wall reads perpendicular) by projecting B onto the plane through A with the hit normal; real vertex snapping needs mesh data and isn't worth it here.
- Trace against the **collision**, not the visual mesh: furniture with only simple box collision will measure to the box. For accurate measures enable **Use Complex Collision as Simple** on the shell meshes (walls, floors), keep boxes on furniture.

## 6. Master material + material instances (the reel's quote)
"Create a main material and use instances for variations" is Epic's standard pattern: one parent material exposes **parameters** (BaseColor tint, texture slots, roughness, normal strength, UV scale, plus the section-plane block), and every finish (oak, walnut, linen, marble) is a **Material Instance Constant** that only sets values. Benefits: one shader compile, cheap switching, and section mode works everywhere.
- Runtime changes: `CreateDynamicMaterialInstance` once per mesh slot, then `SetScalarParameterValue` / `SetVectorParameterValue` / `SetTextureParameterValue` — no recompile. Swapping a whole finish = `SetMaterial(SlotIndex, MI_Walnut)`.
- Keep a few masters, not one per object: `M_Archviz_Opaque`, `M_Archviz_Glass` (translucent; can't be Nanite; section via a Masked-equivalent is not possible on translucency — fade opacity instead), `M_Archviz_Foliage`.
- **Variant Manager** (plugin): Level Variant Sets group property changes (materials, visibility, transforms, function calls) into named variants switchable **at runtime** via its Blueprint API (Epic docs). Good for "Package A / Package B" finish bundles; the controller's `SetSlotMaterial` stays the low-level call the web panel uses.
- Changer bar UI: one UMG button per variant with a thumbnail (render once in-engine), grouped by slot (Floor, Sofa, Kitchen fronts). Highlight the active one; don't show more than ~6 per slot on screen (UI rule of thumb).

## 7. Exposing it to Remote Control and MCP
- Web panel: add `SelectUnit`, `SetTimeOfDay`, `SetSectionHeight`, `SetSectionEnabled` to the panel's CONFIG as extra function calls on the controller's object path (`/Game/Maps/House.House:PersistentLevel.BP_ArchvizController_C_0` — get the real path with `scripts/rc_probe.py --describe`). Remote Control can call only functions marked **BlueprintCallable** (and "Call In Editor" is not needed).
- MCP: the agent can create the MPC, master material parameters and DataTable through the MCP's asset tools/Python, but Blueprint graphs (the controller's logic) are built by hand or with an MCP that edits Blueprint nodes (EngineWire). Ask before each destructive step; commit first.

## Test checklist
- Section at 120 cm in every room: no wall left uncut that should be cut (= a material not using the master); back faces read dark.
- Time slider 6:00 → 20:00: no exposure pumping, interior stays readable, shadows' direction matches the compass.
- Measure a door: ~0.80–0.90 m wide, ~2.0–2.1 m high (measures the model, not reality — compare with the plan).
- Packaged build launched with `-RCWebControlEnable -RCWebInterfaceEnable`: every panel button still works.

## Sources
- Sun and Sky actor (plugin, properties, Solar Time, Real Time Capture): https://dev.epicgames.com/documentation/en-us/unreal-engine/sun-and-sky-actor-in-unreal-engine
- Variant Manager (runtime Blueprint API, LevelVariantSetDirector): https://dev.epicgames.com/documentation/unreal-engine/working-with-scene-variants-in-unreal-engine , https://dev.epicgames.com/documentation/unreal-engine/scripting-the-variant-manager-setup , https://dev.epicgames.com/documentation/unreal-engine/calling-functions-on-variant-activation
- Section planes via MPC (community, older): https://forums.unrealengine.com/t/section-planes/128771
- Minimap with orthographic Scene Capture (community): https://forums.unrealengine.com/t/2719592 , https://uhiyama-lab.com/en/notes/ue/render-target-minimap-camera/
- Opacity mask basics: https://docs.unrealengine.com/4.27/en-US/Resources/ContentExamples/MaterialNodes/1_8
- Lumen + masked shadow bug report (5.5, target 5.8): https://issues.unrealengine.com/issue/UE-347428
- Paid clipping plugin example (Fab, 5.8/Win64 only): https://www.fab.com/listings/fae8e4c3-ce91-48a7-9b9b-832a70ab6b8e
- UE 5.8 release coverage: https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes , https://gamefromscratch.com/unreal-engine-5-8-released/
