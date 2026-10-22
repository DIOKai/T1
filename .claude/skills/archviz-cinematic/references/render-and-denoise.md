# Render settings, denoising and flicker

## Cycles or EEVEE
- EEVEE "is based on rasterization and is not a path tracer … Cycles will always provide more physically accurate renders."
- EEVEE limits that matter for architecture: no light node trees (no IES), no Area Spread, thin walls leak light, only one refraction is simulated, screen-space effects vanish at frame edges (use overscan), volumes missing in reflections/refractions. Ray tracing (`use_raytracing`) is **off by default**. 5.2 reworked screen-space ray tracing: some scenes render darker than in 5.1; a new Backface option reduces leaks.
- Use EEVEE for the animatic and timing approval; Cycles for the final film, especially glass-heavy interiors (experience, unverified).

## Cycles starting point (experience values; tune per scene)
| Setting | Exterior | Interior |
|---|---|---|
| Noise Threshold | 0.01 | 0.005–0.01 |
| Max Samples | 512–1024 | 1024–4096 |
| Denoiser | OpenImageDenoise ("typically provides the highest quality") | same |
| Denoise passes / prefilter / quality | Albedo + Normal / Accurate / High | same |
| Animated Seed | on (manual: "a good idea … when rendering animations") | on |
| Clamp Indirect | 10 | 4–10 |
| Filter Glossy | 1.0 | 1.0 |
| Caustics reflective / refractive | off | off |
| Light Portals | — | yes, in every window |
| Motion blur | on, shutter 0.5 (180°) | on, 0.5 |

Manual facts behind the table: Noise Threshold typical 0.1–0.001 (0 = automatic); Time Limit caps time per frame; Scrambling Distance flickers in the viewport and doesn't work with Blue-Noise; glass needs more Transmission bounces, diffuse can use fewer; keep material colours ≤ ~0.8. Motion blur: off by default, `motion_blur_shutter` default 0.5 frame = 180° (1/48 s at 24 fps); it ignores lamp world-space motion and orthographic cameras have no camera blur. Speed: **Persistent Data** (keeps render data between frames, more RAM); 5.2 **Texture Cache** (much lower memory and start-up, slightly slower render); Simplify texture limits; Format ▸ Percentage 50 % for tests.

## Why animations flicker
OIDN denoises each frame on its own; low samples leave different noise each frame and the denoiser "boils" (community reports, unverified). Turning Animated Seed off stabilises noise but leaves a fixed pattern glued to the screen.

### Anti-flicker checklist
1. Raise samples / lower Noise Threshold (0.01 → 0.005).
2. Interiors: Light Portals, or Path Guiding on CPU, so light converges faster.
3. Denoise with Albedo + Normal, Prefilter Accurate, Quality High.
4. Kill fireflies (main cause of flicker): Clamp Indirect 4–10, Filter Glossy 1.0, caustics off.
5. Save **OpenEXR MultiLayer** with **Denoising Data** so you can re-denoise later (compositor Denoise node or OptiX temporal).
6. Render a 3–5 s test clip, encode it, watch it looping full screen; only then render everything.
7. The 5.0 **Render Time pass** shows per-pixel cost — find the slow, noisy area.

### Temporal denoising (NVIDIA only)
`bpy.ops.cycles.denoise_animation(input_filepath='', output_filepath='')` is still in the 5.x API. Requirements: Denoising Data pass, OpenEXR MultiLayer output, the whole sequence rendered first; the temporal model needs motion (Vector) data. There is **no UI button** — run it from Python. In the Cycles source the temporal mode exists only in the OptiX denoiser (`OPTIX_DENOISER_MODEL_KIND_TEMPORAL`), not in OIDN, so **AMD/Intel/CPU users have no official temporal denoiser**. A third-party compositor node-group toolkit claims temporal denoising but reportedly broke in 5.0.x — don't depend on it (unverified). 5.2 note: OIDN on AMD RDNA2 is no longer GPU-accelerated.

```python
# NOT RUN in Blender. Output setup for a later denoise pass (5.x: media_type BEFORE file_format).
import bpy
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
vl = scene.view_layers[0]
vl.cycles.denoising_store_passes = True       # Denoising Data
vl.use_pass_vector = True                      # motion vectors (temporal model, vector blur)
s = scene.cycles
s.use_adaptive_sampling = True; s.adaptive_threshold = 0.01; s.samples = 1024
s.use_denoising = True; s.denoiser = 'OPENIMAGEDENOISE'
s.denoising_input_passes = 'RGB_ALBEDO_NORMAL'; s.denoising_prefilter = 'ACCURATE'
s.sample_clamp_indirect = 6.0; s.blur_glossy = 1.0
s.caustics_reflective = False; s.caustics_refractive = False
s.use_animated_seed = True
img = scene.render.image_settings
img.media_type = 'MULTI_LAYER_IMAGE'          # 5.0+: set first
img.file_format = 'OPEN_EXR_MULTILAYER'
img.color_depth = '16'
scene.render.filepath = "//renders/shot01/shot01_"
scene.render.use_overwrite = False; scene.render.use_placeholder = True
# After the whole sequence is rendered (NVIDIA + OptiX only):
# bpy.ops.cycles.denoise_animation(input_filepath="//renders/shot01/shot01_####.exr",
#                                  output_filepath="//renders/shot01_dn/shot01_####.exr")
```
Property names above follow the Cycles RNA as documented; `denoise_animation`'s exact path pattern handling was not tested.

## Colour: AgX looks
Views (5.2): Standard, ACES 1.3, ACES 2.0, Khronos PBR Neutral, **AgX**, Filmic ("deprecated and is superseded by AgX"), Filmic Log, False Color, Raw (+ HDR variants). AgX: 16.5 stops, bright colours desaturate toward white like film; default for new files since 4.0.

Exact look names (from Blender's `config.ocio`): `AgX - Punchy`, `AgX - Greyscale`, `AgX - Very High Contrast`, `AgX - High Contrast`, `AgX - Medium High Contrast`, `AgX - Base Contrast`, `AgX - Medium Low Contrast`, `AgX - Low Contrast`, `AgX - Very Low Contrast`.

```python
vs = bpy.context.scene.view_settings
vs.view_transform = 'AgX'
vs.look = 'AgX - Medium High Contrast'   # whether 5.2 wants the prefix in bpy: unverified, read vs.look back
```
Start with Base or Medium High Contrast (experience). Khronos PBR Neutral targets product photography / well-exposed scenes — good for colour-accurate material shots. HDR delivery: Rec.2100 PQ/HLG display + H.265/AV1 10-bit ("Bit depth 10 with PQ encoding is a good default").

## Compositor in 5.x
- The compositing tree is its own data-block: `tree = bpy.data.node_groups.new("Comp", "CompositorNodeTree"); scene.compositing_node_group = tree`. `scene.node_tree` and Use Nodes are gone; the **Composite node is removed — the result goes to Group Output**. File Output node reworked (Directory + File Name).
- Glare: Bloom, Ghosts, Streaks, Fog Glow, Simple Star, **Sun Beams**, Kernel; Low/Medium quality is temporally stable in 5.0. Lens Distortion: Radial, Horizontal, Dispersion.
- Denoise node (OIDN): Noisy Image + Denoising Albedo + Denoising Normal.
- Useful passes: Mist (aerial perspective/fog, cleaner than Depth with DoF/blur), Vector, Cryptomatte, Light Groups, Shadow Catcher.
- Vignette: Ellipse Mask + Blur + Mix Multiply (common practice; node names unverified in 5.2).

## Sources
- EEVEE: https://docs.blender.org/manual/en/latest/render/eevee/index.html ; limits: https://docs.blender.org/manual/en/latest/render/eevee/limitations/limitations.html ; ray tracing: https://docs.blender.org/manual/en/latest/render/eevee/render_settings/raytracing.html ; 5.2 EEVEE notes: https://developer.blender.org/docs/release_notes/5.2/eevee/
- Sampling / denoise: https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html
- Light paths: https://docs.blender.org/manual/en/latest/render/cycles/render_settings/light_paths.html ; reducing noise: https://docs.blender.org/manual/en/latest/render/cycles/optimizations/reducing_noise.html
- Motion blur: https://docs.blender.org/manual/en/latest/render/cycles/render_settings/motion_blur.html ; RenderSettings API: https://docs.blender.org/api/current/bpy.types.RenderSettings.html
- Performance (Persistent Data): https://docs.blender.org/manual/en/latest/render/cycles/render_settings/performance.html
- Cycles operators (denoise_animation): https://docs.blender.org/api/current/bpy.ops.cycles.html ; source: https://projects.blender.org/blender/blender/src/branch/main/intern/cycles/blender/addon/operators.py , https://projects.blender.org/blender/blender/src/branch/main/intern/cycles/integrator/denoiser_optix.cpp
- OptiX temporal denoise (3.1): https://www.blendernation.com/2022/01/10/optix-temporal-denoising-support-added-to-blender-3-1-alpha/
- Flicker discussions (community, unverified): https://blenderartists.org/t/flickering-noise-on-cycles-animation/1383040 , https://devtalk.blender.org/t/taking-a-look-at-optix-7-3-temporal-denoising-for-cycles/18656?page=6
- Color management: https://docs.blender.org/manual/en/latest/render/color_management/displays_views.html ; OCIO config: https://projects.blender.org/blender/blender/src/branch/main/release/datafiles/colormanagement/config.ocio ; AgX in 4.0: https://developer.blender.org/docs/release_notes/4.0/color_management/
- Compositor 5.0: https://developer.blender.org/docs/release_notes/5.0/compositor/ ; Glare: https://docs.blender.org/manual/en/latest/compositing/types/filter/glare.html ; Denoise node: https://docs.blender.org/manual/en/latest/compositing/types/filter/denoise.html ; Passes: https://docs.blender.org/manual/en/latest/render/layers/passes.html
- Python API 5.0: https://developer.blender.org/docs/release_notes/5.0/python_api/ ; 5.0 Cycles (Render Time pass): https://developer.blender.org/docs/release_notes/5.0/cycles/ ; 5.2 Cycles: https://developer.blender.org/docs/release_notes/5.2/cycles/
