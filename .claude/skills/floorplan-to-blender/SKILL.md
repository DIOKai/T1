---
name: floorplan-to-blender
description: Turn a floor plan (image, PDF, screenshot of a real-estate listing), listing photos, or AI reference images into an accurately scaled 3D house or apartment in Blender — read the dimensions, write them into a checked layout JSON, then build walls with mitered corners, real door and window openings with glass, floors, ceilings, slab and stairs through the blender MCP, and verify against the plan. Use whenever the user wants to model a building, apartment, villa, house or room layout from a drawing or photos, recreate a Zillow/real listing in 3D, "AI modeled this apartment in 30 minutes", make a 3D version of a floor plan, or block out architecture before archviz, a web walkthrough, Unreal or FiveM — even if they only say "平面图转3D", "照图建模", "把这间房子做出来", "户型图", "建公寓模型", "重建房源".
---

# Floor plan → Blender

The reels that "model an apartment in 30 minutes" all hide the same hard part: **getting the dimensions right**. Building walls is easy once the numbers are right; a house built from guessed numbers looks wrong forever (doors 1.3 m wide, a bedroom that doesn't fit a bed, a window floating in a stair). So this skill separates the work into reading → a checked JSON → building → verifying, and never skips the checks.

Everything goes through the `blender` MCP (`execute_blender_code` runs bpy in the user's Blender). Ask before using it (T1 rule) and remind the user to save the .blend first — code sent through the MCP can't be undone in one step. Use `get_addon_status`/the tool list to see what that MCP version offers (newer versions look at the scene with `look`, older ones with `get_viewport_screenshot`). Don't call its `generate_3d` tool: it prefers paid generators.

## Workflow

### 1. Collect inputs (ask for files, don't scrape)
Ask the user to save the plan/photos as files and give you the paths. Don't scrape listing sites — their terms forbid it and the images belong to the photographer/agent; a recreation is fine for personal study, but remind the user before publishing it. Ask, in one go, what you can't read: how many floors, ceiling height, metric or imperial, wall material (brick/concrete or timber), and what the model is for (renders, web walkthrough, Unreal, FiveM MLO, BIM drawings) because that decides step 5.

### 2. Find the scale and read dimensions
Read `references/reading-plans.md`. In order of trust: written dimension strings > scale bar > room-size labels > standard door widths (last resort; ±5–10 %). Measure at least two dimensions in each direction; if X and Y disagree by more than ~2 % the image was stretched — fix that first. Convert everything to metres. For photos or AI images there is no reliable scale: ask the user for one real measurement (a room width, the door height), or say clearly that you used typical values.

Room sizes from a listing or a client often don't add up to the outline (rooms 7 + 5 + 4 m in an 18.3 m deep house). Don't stretch rooms silently: decide whether the sizes are gross (to wall centres/outside, typical when a room width equals the building width) or net (wall face to face), keep the given rooms as given, mark the leftover as an unknown space, and ask the user what it is — offer two or three likely answers.

### 3. Write the layout JSON
Write `<project>/layout.json` in the schema of `references/layout-schema.md` (copy `assets/example-layout.json` as a start). Walls are axis polylines with thickness and justification; openings hang on a wall + segment + distance along it, so they move with the wall. Record where each number came from (`thickness_source`, `scale.samples`, `notes`) — the user needs to know which numbers are guesses.

Show the user the key dimensions (overall size, each room, ceiling height, door/window sizes) and the list of guessed values before building. This is the cheapest moment to fix a mistake.

### 4. Validate, then build
```bash
python scripts/validate_layout.py layout.json
python scripts/fp_geometry.py layout.json --svg top.svg --px-per-m <plan px_per_m>
```
`validate_layout.py` (read-only) catches scale errors via door widths, openings outside their wall or overlapping, wall ends touching nothing, rooms without a door or unreachable from the entrance, room areas off from their labels by more than 5 %, and the room total against the listing area. Fix every ERROR; read every WARN and either fix it or tell the user why it's right. `top.svg` at the plan's own px-per-metre can be laid over the plan image to compare by eye before Blender is even opened.

Copy `scripts/fp_geometry.py` and `scripts/build_in_blender.py` into the user's project folder next to `layout.json`, so the project still builds later even if this skill moves or a worktree is deleted. Then build in Blender (send through `execute_blender_code`):
```python
import runpy
fp = runpy.run_path(r"<project>/build_in_blender.py")
print(fp["build"](r"<project>/layout.json"))
fp["add_reference_plan"](r"<project>/plan.png", px_per_m=<px_per_m>, origin_px=(<x>, <y>))
fp["add_top_camera"]()
print(fp["verify"]())
```
`build()` deletes the old `FP_*` collections first, so edit the JSON and run it again rather than patching meshes by hand. Walls are split into piers, sills and lintels around each opening instead of boolean-cut, so there are no boolean failures and the geometry exports cleanly to glTF, FBX and Sollumz. Windows get a glass pane, doors a closed leaf; these are placeholders for real models later.

### 5. Verify like a reviewer
Read `references/verification.md`. In short: top camera view against the plan (walls on the plan's lines), `verify()` reports floating objects, then look from front/right/back/left/top/perspective, and from the street into every window — there must be a real room behind every pane (the user's own rule from earlier work: windows are real glass with real interiors, nothing floating, buildings sit on the ground). Report what you checked and anything you couldn't.

### 6. Hand off
- Renders and camera moves → `archviz` then `archviz-cinematic`; furniture → `set-dressing` + `free-3d-assets`.
- Interactive web tour → `archviz-web-walkthrough`; Unreal → `unreal-mcp-archviz`.
- BIM / IFC drawings, quantities → read `references/bim-handoff.md`: the same JSON maps onto `bonsai-project-setup` → `bonsai-walls` → `bonsai-openings` → `bonsai-stairs` → `bonsai-spaces-grid` → `bonsai-drawings` (use those instead of `build_in_blender.py`; they create real IFC walls and openings).
- FiveM interior → `fivem-mlo-housing` (MLO rules win over this skill's defaults).
- Facade patterns on the shell → `parametric-facade`.

All of these are separate skills: ask before using them.

## Limits (say them, don't hide them)
- Only straight stairs are built; L/U stairs → `bonsai-stairs` or model by hand.
- Roofs aren't built → `bonsai-roofs`, or model them; sloped ceilings need manual work.
- Curved walls must be approximated with short segments (about 0.3–0.5 m each).
- `build_in_blender.py` was written against the Blender 5.2 Python API docs, but it was not run in Blender when this skill was made (no Blender on the authoring machine); the geometry module and validator were tested in plain Python. If a bpy call fails, fix the script and mention it.
