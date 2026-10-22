# Verifying the model

Check in four layers; each catches what the one before can't.

## 1. Layout (before Blender)
`python scripts/validate_layout.py layout.json` — scale via median door width (0.6–1.2 m), openings within their segment and not overlapping, openings at least half a wall thickness + 5 cm from corners, sill + height ≤ wall height, wall ends that touch nothing, self-crossing polygons, room area vs label (> 5 % warns), room total vs listing (> 15 % warns), rooms with no door, rooms unreachable from an exterior door.

`python scripts/fp_geometry.py layout.json --svg top.svg --px-per-m <plan px/m>`: footprints at the plan's own scale; open both images in any viewer with the SVG at 50 % opacity over the plan.

## 2. Geometry (in Blender)
`verify()` from `build_in_blender.py` returns:
- `floating`: objects whose underside has no other object within 2 cm below (the bottom slab is exempt). Anything here is a bug in the layout (wrong `base_offset`, level elevation) — fix the JSON, rebuild.
- `windows_with_glass`: every window should appear here.

Common failures and what they look like:

| Symptom | Likely cause |
|---|---|
| everything 2.54× or 3.28× too big/small | inches/feet/metres mixed — check the median door width |
| gap or overlap at a corner | path points not shared between segments, or a T-wall ending on the axis instead of the face |
| interior wall poking through the outside | its end goes past the exterior wall's inner face |
| a room with no way in | missed door on the plan (AI readers often drop bathroom doors) |
| window over a stair or cut by a floor | opening `sill`/`height` taken from the wrong level |

## 3. Visual
- Top camera (`add_top_camera()`) with the reference plan under the slab (`add_reference_plan()`): walls should sit on the plan's lines.
- Six views: front, right, back, left, top, perspective (same set the Bonsai audit uses).
- From the street into every window: a floor, walls and ceiling must be behind the glass — never the sky or the void. Turn on backface culling in the material settings when the model is going to a game engine; faces that only show from one side look like holes there.
- Viewport screenshots through the MCP are more reliable than renders for checks; renders through the MCP sometimes come back black.

## 4. Report to the user
List: overall size, each room's area vs label, which numbers are measured vs guessed, the validator's warnings you kept and why, what `verify()` found, and what you could not check.
