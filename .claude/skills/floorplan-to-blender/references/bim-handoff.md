# Handing the layout to the Bonsai (IFC) skills

Use this when the user wants BIM: IFC files, plans/sections from the model, quantities, or a model an engineer will open. The Bonsai skills make real IFC walls and openings; `build_in_blender.py` makes plain meshes that only look right. Ask before using them (each is its own skill).

| layout.json | Bonsai skill / function |
|---|---|
| project, levels | `bonsai-project-setup`: `setup_project()`, `add_storey(name, elevation)`. Set exterior/interior wall type thickness to the JSON values (e.g. 0.23 / 0.115) instead of the 0.2 / 0.1 defaults. |
| closed exterior wall | `bonsai-walls`: `create_room_with_mitered_corners(corners=path, wall_type_name=..., height=level height, closed=True)` |
| floor slab | `bonsai-walls`: `add_floor_slab_from_walls(..., align_top_to_storey=True)` |
| each interior wall | `bonsai-walls`: `add_interior_wall(start_xy, end_xy, ...)` — it trims ends to the exterior inner face itself, so you can pass the axis end points |
| openings | `bonsai-openings`: `add_parametric_door_to_wall` / `add_parametric_window_to_wall`. Their `target` is the opening's **corner**, not its centre: `target = segment_start + d × (start_offset)`. Don't use its "equally spaced, centred" default — place each opening where the plan has it. |
| stairs | `bonsai-stairs`: `add_parametric_stair` plus the stairwell opening and railings |
| rooms | `bonsai-spaces-grid`: `add_space` per room polygon (IfcSpace with boundaries and quantities) |
| drawings | `bonsai-drawings`: plans/sections/elevations; the plan SVG can be compared with the source plan |

Don't use Blender booleans or modifiers on IFC walls — they don't survive IFC export (the Bonsai skills say the same). Run `audit_geometry()` from `bonsai_bim_helpers.py` afterwards for walls crossing each other and stairs through slabs.
