# Blender 5.x passes for ControlNet

## Why passes instead of letting ComfyUI guess
ComfyUI preprocessors (Depth-Anything, Canny, MLSD) can estimate depth or edges from a clay render, and that is a fine fallback. But they *estimate*; Blender *knows*. Native passes have exact edges at window frames and columns, which is what keeps the AI from moving them (rule of thumb from practice, not a benchmark).

## What each pass is
| Pass | ViewLayer property | Notes |
|---|---|---|
| Beauty | always | img2img base and the clay reference |
| Depth (was `Z`) | `use_pass_z` | distance from the camera in scene units, **not 0–1**; **not anti-aliased**; noisy with DOF/motion blur |
| Mist | `use_pass_mist` | already 0–1; Start/Depth/Falloff in World → Mist Pass (`world.mist_settings`); anti-aliased → use it when DOF or motion blur is on |
| Normal | `use_pass_normal` | **world-space** normals |
| Object Index | `use_pass_object_index` | per-object `pass_index`; not anti-aliased |
| Cryptomatte | `use_pass_cryptomatte_object` / `_material` / `_asset` | better than Index: handles several objects per pixel, transparency, motion blur; saved in multilayer EXR |
| Line art | `scene.render.use_freestyle` + `view_layer.use_freestyle` | Freestyle lines; the "as render pass" option puts them in their own pass (`freestyle_settings.as_render_pass`, 未验证 in 5.x) |

## Blender 5.0 compositor changes (old scripts break)
- `scene.node_tree` is **removed**. Create a tree with `bpy.data.node_groups.new(name, "CompositorNodeTree")` and assign it to `scene.compositing_node_group`.
- `scene.use_nodes` is deprecated (always True).
- File Output node: `base_path`, `file_slots`, `layer_slots` are gone → `directory`, `file_name`, `file_output_items` (`file_slots[0].path` → `file_output_items[0].name`).
- The Composite node is replaced by Group Output.
- Socket names: `Z` → `Depth`, `IndexMA` → `Material Index`, `DiffCol` → `Diffuse Color`.
- File Output only adds frame numbers to file names when rendering an animation.

`scripts/export_passes_bpy.py` follows these. It makes its own tree (`AIR_Passes`) and remembers the user's previous one so `restore()` can put it back — never overwrite a user's compositor setup silently.

## Turning passes into ControlNet inputs (rules of thumb)
- **Depth:** normalize, then invert to **near = white, far = black** (MiDaS/Depth-Anything convention most depth ControlNets were trained on — 未验证 for every model). Save 16-bit PNG. The script does normalize + invert. If the result looks inside-out in ComfyUI, flip it with an Invert Image node.
- **Mist:** already 0–1 with far = white; the script inverts it too, so it matches the depth convention. Set mist Start/Depth to cover the building (e.g. start at the camera, depth to just past the back wall); otherwise everything is one flat grey.
- **Normal:** ControlNet normal models usually expect camera/OpenGL-space normals mapped to 0–1 (未验证). Blender gives world space. The script saves the world normal as EXR only; easiest is to run ComfyUI's normal preprocessor on the beauty/clay pass, or convert in the compositor by hand.
- **Line art:** white lines on black for xinsir lineart (未验证); invert if your workflow expects black on white.
- **Masks:** Cryptomatte in the multilayer EXR, or ID Mask PNGs from Object Index (the script makes one PNG per index you list). Give glass, plants, sky, signage their own `pass_index` before export.

## Index/AA gotcha
Depth, Position and Index passes have no anti-aliasing, so their edges are stair-stepped. For ControlNet that is fine (it is downscaled anyway); for a mask you composite back, grow/blur it 1–2 px.

## Sources
- ViewLayer properties (5.2 docs): https://docs.blender.org/api/current/bpy.types.ViewLayer.html
- Passes manual: https://docs.blender.org/manual/en/latest/render/layers/passes.html
- 5.0 Python API changes: https://developer.blender.org/docs/release_notes/5.0/python_api/
- 5.0 compositor changes: https://developer.blender.org/docs/release_notes/5.0/compositor/
- xinsir ControlNet Union (control types): https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
