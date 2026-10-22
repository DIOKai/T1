# Build-up animation, colour-map pass, and camera paths from a plan

Three tricks behind the "villa assembles itself, then AI turns it into a real video" reels:
- **(a) Build-up** — colour-coded blocks fly/drop in piece by piece along a camera move.
- **(b) Colour-map pass** — the same camera move rendered with one flat colour per material, so an AI model can follow the regions (the "color map video" in the Revit → Three.js reel). The AI step itself lives in `ai-archviz-render` (`references/colormap-video-to-video.md`).
- **(c) Camera paths planned from the floor plan** — eye-level routes through doors, close-up-then-pull-out shots. The reels use paid AI to "propose" paths; with the plan data the agent can do it directly.

All bpy below targets the **Blender 5.x API** (no `action.fcurves` — F-curves live in the slot's channelbag, see `camera-moves.md`). **Not run in Blender** — syntax-checked only. Through the `blender` MCP (ask first; user saves the .blend first).

## (a) Build-up assembly animation

### Plan
- **Order**: bottom to top reads as "construction" (foundation → slab → walls → roof → glazing → furniture). Sort by each object's lowest world Z, then by X/Y so a storey builds in a sweep. Alternative orders: by collection (structure, envelope, interiors), or by distance from the camera's path so pieces land just before the camera sees them.
- **Timing** (experience values): 6–12 frames per piece at 24 fps, next piece starts when the previous is 40–60 % done (overlap), whole build 6–10 s for a house. Hundreds of pieces → group them (one wall run = one piece) or the build drags.
- **Motion**: drop from 2–4 m above with ease-out (Cubic/Expo), or scale up from the base. Overshoot (`BACK`) only for a playful look; architecture usually wants a clean settle.
- **Look**: render the build in the **colour-map look** (section b, flat colour per material — Keanu's reel) or clay, then cross-dissolve to the beauty pass on the finished building.
- Animate **delta transforms** (`delta_location`, `delta_scale`) so each object's real location/scale stays untouched and can be cleared in one go.
- Keep the camera moving slowly during the build (orbit or slider, `camera-moves.md`); a static camera makes it look like a progress bar.

### bpy (Blender 5.x)
```python
# NOT RUN in Blender — written from the 5.x API docs (Object.delta_location, keyframe_insert, channelbag).
import bpy
from mathutils import Vector
from bpy_extras import anim_utils

def world_min_z(ob):
    return min((ob.matrix_world @ Vector(c)).z for c in ob.bound_box)

def build_up(objects, start=1, per_piece=8, overlap=0.5, drop=3.0, scale_in=False,
             interp='CUBIC', easing='EASE_OUT'):
    objs = sorted(objects, key=lambda o: (round(world_min_z(o), 1),
                                          round(o.matrix_world.translation.x, 1),
                                          round(o.matrix_world.translation.y, 1)))
    step = max(1, round(per_piece * (1 - overlap)))
    for i, ob in enumerate(objs):
        f0 = start + i * step
        f1 = f0 + per_piece
        # hidden until its turn (CONSTANT interpolation, set below)
        ob.hide_render = True;  ob.keyframe_insert("hide_render", frame=f0 - 1)
        ob.hide_render = False; ob.keyframe_insert("hide_render", frame=f0)
        ob.hide_viewport = False
        ob.delta_location = (0, 0, drop); ob.keyframe_insert("delta_location", frame=f0)
        ob.delta_location = (0, 0, 0);    ob.keyframe_insert("delta_location", frame=f1)
        if scale_in:
            ob.delta_scale = (1, 1, 0.001); ob.keyframe_insert("delta_scale", frame=f0)
            ob.delta_scale = (1, 1, 1);     ob.keyframe_insert("delta_scale", frame=f1)
        ad = ob.animation_data
        cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
        for fc in cb.fcurves:
            for kp in fc.keyframe_points:
                if fc.data_path == "hide_render":
                    kp.interpolation = 'CONSTANT'
                else:
                    kp.interpolation = interp
                    kp.easing = easing
            fc.update()
    return f"{len(objs)} pieces, frames {start}–{start + (len(objs) - 1) * step + per_piece}"

# Example: everything in the 'Building' collection except glass, then glass last
col = bpy.data.collections["Building"]
solid = [o for o in col.all_objects if o.type == 'MESH' and 'glass' not in o.name.lower()]
glass = [o for o in col.all_objects if o.type == 'MESH' and 'glass' in o.name.lower()]
print(build_up(solid, start=1))
print(build_up(glass, start=1 + len(solid) * 4 + 8, drop=0.0, scale_in=True))
```
Notes:
- Objects that **already have an action** (animated doors) get the build keys added to the same action — fine, but check them afterwards. Objects that share mesh data still animate separately (delta transforms are per object).
- Scale-in uses the **object origin**: set origins to the bottom (Object ▸ Set Origin) first, or the piece grows from its centre.
- `hide_render` keys are what Cycles/EEVEE respect; viewport visibility is left on so you can see the animation in the timeline.
- To remove: clear the delta keys (`ob.animation_data.action` channelbag → remove the `delta_location`/`delta_scale`/`hide_render` F-curves) and reset `delta_location = (0,0,0)`.

### Alternatives
- **One joined mesh** (SketchUp/Revit import as one object): separate by material or loose parts first (Edit Mode ▸ Separate), or use **Geometry Nodes**: Mesh Island → per-island delay from island index or Z, compare with Scene Time, `Set Position` offset/`Scale Elements` — no per-object keys, but harder to edit by hand (no tested node tree here, 未验证).
- **Driver on one "progress" property** (an Empty's custom property 0–1 driving every piece's delta Z with a per-piece delay) gives one slider for the whole build. Whether such expressions stay on Blender's fast "simple expression" path or need Auto Run Python Scripts is 未验证 — keyframes avoid that question.
- Cell-fracture "un-explode" effects are physics-sim work → `blender-animation-rigging` / rigid body; not covered.

## (b) Colour-map pass (flat colour per material, for AI guidance)

What the AI needs: the **same camera** and **same frames** as the beauty film, each region a single flat colour, **no anti-aliasing, no lighting, no tone mapping** — otherwise edges blend into colours that mean nothing and the model guesses.

Fastest route: **Workbench**, Lighting **Flat**, Color **Material** (uses each material's Viewport Display colour = `Material.diffuse_color`), specular/shadow/cavity/outline off, Render AA **Off**, view transform **Standard**. No node edits, seconds per frame. The skill's script does exactly this and restores everything:

```python
import runpy
cm = runpy.run_path(r"<skill>/scripts/colormap_pass_bpy.py")
print(cm["setup"](mode="semantic"))    # ADE20K colours for named classes (wall, floor, glass, sofa…), hashed colours for the rest
print(cm["legend"]())                  # name → hex → class; keep it with the frames
cm["render_animation"](r"//colormap/frame_")
cm["restore"]()
```
- **mode="semantic"**: material names containing `wall`, `floor`, `glass`/`window`, `door`, `sofa`, `plant`… get the **ADE20K palette** colour of that class (wall 120,120,120; floor 80,50,50; windowpane 230,230,230; sky 6,230,230 …) — the palette segmentation ControlNets were trained on (ADE20K for the SD1.5 seg model; for SDXL union models the palette is undocumented, 未验证). Rename materials meaningfully first (`Wall_Plaster`, `Floor_Oak`) — the legend shows what got classified.
- **mode="material"**: one stable hashed colour per material — good for paid video models that just "follow the colour regions" and for Keanu-style colour-coded build-ups.
- **mode="object"**: per object (`Object.color`) — when one material is used on many parts you want separated.
- Colours are set in linear so that the **Standard** transform outputs the exact sRGB values (check one pixel of a frame in an image editor; exact match 未验证 in 5.x).
- Glass renders as an opaque flat colour (Workbench ignores transmission) — usually right for segmentation (the window is a region). For "see the interior through glass" use mode="object" with the glass objects hidden instead.

**Alternatives**:
- **Cryptomatte** (View Layer ▸ Passes ▸ Cryptomatte Object/Material, Cycles or EEVEE): exact per-object/material mattes for *masks* in compositing and ComfyUI; not a colour map by itself (the preview colours aren't stable classes).
- **Object/Material Index** passes (`pass_index`) → ID masks; used by `ai-archviz-render`'s `export_passes_bpy.py`.
- Render the matching **depth/mist** sequence too (`ai-archviz-render` passes): free video models use depth/edges as their control, the colour map as the first-frame guide.

## (c) Camera paths from the floor plan

The agent can propose paths without paid AI when it has the plan as data: room polygons/centres, door positions and widths, floor heights (from `floorplan-to-blender`, IFC/Bonsai, or measured in the .blend).

### Method
1. **Room graph**: rooms = nodes, doors/openings = edges (door centre, wall normal, clear width). Start at the entrance; order rooms by a walk the viewer would take (entrance → living → kitchen/dining → terrace → bedrooms; skip service rooms unless asked). A depth-first walk that returns through the corridor is usually fine.
2. **Waypoints per door**: approach point 0.8–1.0 m before the door centre (along the wall normal), the door centre, exit point 0.8–1.0 m after — the camera crosses the door **straight**, never diagonally through the frame (rule of thumb). Doors < 0.8 m clear: cut instead of passing through (the lens will clip the frame).
3. **Inside rooms**: one point near the room's "best view" corner rather than its centre (rooms read best from a corner toward the window, rule of thumb), then on to the next door.
4. **Height** 1.5–1.6 m eye level (`camera-moves.md`); keep it constant through doors.
5. **Speed** ≤ 0.4–0.5 m/s inside (experience value): frames = path length / speed × fps. Long tours → several shots (one or two rooms each) joined by cuts at doorways, not one 3-minute take.
6. **Look direction**: a target Empty that rides the same path a little ahead (≈ 1–1.5 m), so the camera turns *before* corners; keep the target at eye height so verticals stay straight.

```python
# NOT RUN in Blender. waypoints in metres (x, y); z = floor + eye height.
import bpy

def path_camera(waypoints, z=1.55, fps=24, speed=0.45, lens=24, name="CAM_tour"):
    cu = bpy.data.curves.new(name + "_path", 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('NURBS'); sp.points.add(len(waypoints) - 1)
    for p, (x, y) in zip(sp.points, waypoints):
        p.co = (x, y, z, 1.0)
    sp.use_endpoint_u = True; sp.order_u = 3                 # smooth, passes through the ends
    path = bpy.data.objects.new(name + "_path", cu); bpy.context.scene.collection.objects.link(path)
    length = sum(((waypoints[i+1][0]-waypoints[i][0])**2 + (waypoints[i+1][1]-waypoints[i][1])**2) ** 0.5
                 for i in range(len(waypoints) - 1))
    frames = max(2, round(length / speed * fps))
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name)); cam.data.lens = lens
    tgt = bpy.data.objects.new(name + "_target", None)
    for ob in (cam, tgt):
        bpy.context.scene.collection.objects.link(ob)
        c = ob.constraints.new('FOLLOW_PATH'); c.target = path; c.use_fixed_location = True
    lead = min(0.1, 1.2 / max(length, 0.1))                  # target ≈1.2 m ahead
    for ob, a, b in ((cam, 0.0, 1.0 - lead), (tgt, lead, 1.0)):
        c = ob.constraints["Follow Path"]
        c.offset_factor = a; c.keyframe_insert("offset_factor", frame=1)
        c.offset_factor = b; c.keyframe_insert("offset_factor", frame=frames)
    tt = cam.constraints.new('TRACK_TO'); tt.target = tgt
    tt.track_axis = 'TRACK_NEGATIVE_Z'; tt.up_axis = 'UP_Y'
    return cam, frames, round(length, 2)
```
Easing: the `offset_factor` keys get the default Bézier ease in/out — set them to `SINE`/`EASE_IN_OUT` through the channelbag as in `camera-moves.md`. Check the whole path in the camera view (nothing clips through a wall or door leaf; the camera never gets closer than ~0.3 m to a wall, rule of thumb). Also check with `archviz-web-walkthrough`'s collision shell if one exists.

### Shot types that read well (experience values)
| Shot | How |
|---|---|
| Close-up then pull-out | start at 50–85 mm on a material/detail 0.6–1 m away, **dolly back** 1.5–3 m (don't zoom) while the room is revealed; 6–8 s |
| Doorway reveal | start behind the door frame edge, push through on the door axis (above, steps 2) |
| Corner sweep | slider 1–2 m along the window wall, looking diagonally across the room |
| Build-up orbit | slow 20–30° orbit while section (a) assembles the house |
| Plan-to-3D | top orthographic view of the colour-map plan, crane down into perspective (lens shift keeps verticals) |

Tell the user which paths you derived from which plan data, and that door/room data you inferred (not measured) is a guess.

## Sources
- Blender 5.0 Python API changes (channelbags, removed `action.fcurves`): https://developer.blender.org/docs/release_notes/5.0/python_api/
- Object (delta_location, delta_scale, color, pass_index): https://docs.blender.org/api/current/bpy.types.Object.html
- View3DShading (light FLAT, color_type MATERIAL/OBJECT/RANDOM): https://docs.blender.org/api/current/bpy.types.View3DShading.html
- SceneDisplay (render_aa OFF): https://docs.blender.org/api/current/bpy.types.SceneDisplay.html
- Material.diffuse_color (viewport display colour): https://docs.blender.org/api/current/bpy.types.Material.html
- Follow Path constraint: https://docs.blender.org/manual/en/latest/animation/constraints/relationship/follow_path.html
- Cryptomatte: https://docs.blender.org/manual/en/latest/render/layers/passes.html
- ADE20K palette (mmsegmentation): https://github.com/open-mmlab/mmsegmentation/blob/main/mmseg/datasets/ade.py
- xinsir ControlNet Union SDXL (supports "Segment"; palette not documented): https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
