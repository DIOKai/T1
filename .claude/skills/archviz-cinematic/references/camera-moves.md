# Camera moves for architecture

Slow beats fast. The most common mistake in archviz animation is a camera that moves too fast; the fix is usually fewer, better-eased keyframes, not more. A 10 s move needs 3–4 keyframes; a 30 s reveal 4–5 poses. If it feels fast, halve the speed and lengthen the clip; build the shot at ~10 s, then try 12–15 s; end a reveal on a short hold. Roll stays 0. Turn slowly, and turn while moving forward rather than on the spot (studiomatrx, second-hand teaching source).

## Recipes (starting points — experience values, unverified)

| Move | How | Start with | Lens |
|---|---|---|---|
| Dolly / push-in | straight line along the view direction toward a fixed target | 6–10 s, 1–3 m | 24–35 mm |
| Slider | parallel to the facade, rotation fixed; plants/columns in front give parallax | 6–8 s, 1–2 m | 24–35 mm |
| Crane / pedestal | straight up past a wall or hedge, camera stays level, frame with shift | 8–12 s, 2–6 m | 28–35 mm |
| Orbit | camera parented to an Empty at the centre; rotate the Empty Z | 10–20 s for 20–45° | 35–50 mm |
| Reveal through door | start behind a door frame or wall edge, frame at the image edge, push in | 6–10 s | 24–28 mm |
| Drone / aerial | high, slow push or orbit; villa + landscape/sea | 10–15 s, 20–60 m high | 28–50 mm |
| Pan / tilt | camera fixed, only rotates; very slow at 24 fps to avoid judder | small degrees per second | any |

Speed references: walking is about 0.9 m/s (stroll) to 1.8 m/s (brisk) (old AEC paper, unverified). Interior push-ins look more "cinematic" at ≤ 0.5 m/s (experience, unverified). At 24 fps, pans must be slower than feels natural or they judder; one forum rule of thumb says an object should take ~7 s to cross the frame (single opinion, unverified).

Walkthrough structure (SIGGRAPH HyperGraph): establishing exterior → around the building → toward the entrance to build anticipation → into the interior with a transition, not a cut through a wall. Avoid moves a real camera couldn't make. Judge in the camera view, never the top view. No handheld shake unless the story asks for it.

## Two-point perspective
Keep the camera level (rotation X = 90°, Y = 0) and use **Shift Y**; tilting converges the verticals. Blender manual: lens shift "is equivalent to rendering an image with a larger FOV and cropping it off-center". Shift is a fraction of the larger frame side, so to centre a point Δh above the lens at horizontal distance d:

`shift_y ≈ (Δh / d) × (lens / sensor_width)` (landscape, Sensor Fit Auto; derived, verify in camera view)

Example: 28 mm lens, 36 mm sensor, roof ridge 4 m above the camera at 20 m → 0.2 × 0.78 ≈ 0.16. Above ~0.3 the corners stretch: raise the camera or step back instead. A crane move that should keep the building centred can animate `data.shift_y` downward as the camera rises.

## Easing (manual: F-Curve properties)
- Interpolation Constant / Linear / Bézier (default, "smooth in both values and speed"); easing types Sine…Expo with Ease In / Ease Out / Ease In Out. Don't use the dynamic ones (Back, Bounce, Elastic) on architecture.
- Handles: **Auto Clamped** prevents overshoot — use it with Bézier.
- Handle Smoothing "Continuous Acceleration" smooths curves with few keys.
- An F-curve **Noise** modifier with tiny strength can fake a subtle handheld feel — only if wanted.
- DoF rack focus: point Focus Object at an Empty, animate the Empty.
- Rails: **Follow Path** with Fixed Position and an animated **Offset Factor** (0–1) gives a curved path whose speed you ease on one F-curve; add **Track To** so the camera keeps looking at the target (Track To tilts the camera → verticals converge unless the target is at lens height).

## bpy in Blender 5.x
Blender 5.0 removed `action.fcurves`, `action.groups` and `action.id_root`. F-curves live in the channelbag of the action's slot. `keyframe_insert()` still works as before.

```python
# NOT RUN in Blender: written from the 5.0 release notes and the Keyframe API page.
import bpy
from bpy_extras import anim_utils

scene = bpy.context.scene
scene.render.fps = 24
cam = scene.camera
start, end = 1, 1 + 8 * 24                     # 8 s push-in

cam.location = (0.0, -12.0, 1.6)
cam.keyframe_insert(data_path="location", frame=start)
cam.location = (0.0, -10.0, 1.6)                 # 2 m in 8 s = 0.25 m/s
cam.keyframe_insert(data_path="location", frame=end)

ad = cam.animation_data
cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
for fc in cb.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'SINE'                # or 'BEZIER' + AUTO_CLAMPED handles
        kp.easing = 'EASE_IN_OUT'
    fc.update()
```

Interpolation set on a key controls the segment from that key to the next. The skill's `scripts/camera_moves_bpy.py` wraps this (`create_camera`, `keyframe_move` for dolly / push_in / slider / crane / orbit, `ease_keys`, `describe`) and falls back to `action.layers[].strips[].channelbag(slot)` if `anim_utils` is unavailable. It does **not** change user preferences (the new-keyframe interpolation default is a preference and would persist for the user). Not run in Blender — syntax-checked only.

Deeper F-curve / NLA / constraint work → `blender-animation-rigging`.

## Sources
- Blender manual, Cameras: https://docs.blender.org/manual/en/latest/render/cameras.html
- Camera API: https://docs.blender.org/api/current/bpy.types.Camera.html
- F-Curve properties (interpolation, easing, handles): https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/properties.html
- F-Curve modifiers: https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/modifiers.html
- Keyframe API: https://docs.blender.org/api/current/bpy.types.Keyframe.html
- Follow Path constraint: https://docs.blender.org/manual/en/latest/animation/constraints/relationship/follow_path.html
- Blender 5.0 Python API changes: https://developer.blender.org/docs/release_notes/5.0/python_api/
- Shift lens (Maxwell docs): https://nextlimitsupport.atlassian.net/wiki/spaces/maxwell4/pages/5679360/Shift+Lens
- Camera paths and walkthroughs (second-hand, unverified): https://www.studiomatrx.org/students/architectural-visualization-rendering/camera-paths-and-walkthroughs
- Focal lengths / eye height (second-hand, unverified): https://www.studiomatrx.org/students/architectural-visualization-rendering/camera-fundamentals-focal-length
- SIGGRAPH HyperGraph camera suggestions: https://education.siggraph.org/static/HyperGraph/animation/cameras/camera_suggestions.htm
- Cinematic archviz techniques: https://thedigitalarchitect.beehiiv.com/p/6-key-techniques-creating-cinematic-architectural-animations
- Walking speeds (AEC 2001, not read in full, unverified): https://www.graphicon.ru/html/2001/pdf/AEC-Russia-Ross2.pdf
