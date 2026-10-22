---
name: archviz-cinematic
description: Make cinematic architectural stills and camera-move films of a building or interior in Blender 5.x for free — plan the shots, set up architectural cameras (two-point perspective with lens shift, real eye height, sane focal lengths), keyframe slow dolly / slider / crane / orbit / push-in / reveal moves, light with the Blender 5 Multiple Scattering sky, HDRI and portals, render a flicker-free Cycles image sequence, and encode it with ffmpeg. Use whenever the user wants a villa / house / apartment / SketchUp model turned into a cinematic film or real-estate video, a walkthrough or flythrough, a "Seedance / Kling / Runway / Veo style" architecture clip without paying for AI video, golden-hour or night exterior renders, or asks why their archviz animation flickers or looks fake — even if they only say "建筑动画", "电影感", "别墅动画", "做成影片", "漫游动画", "效果图", "运镜", "SketchUp 模型变电影", "楼盘宣传片", "渲染闪烁".
---

# Archviz cinematic (Blender 5.x)

The viral "basic SketchUp model → cinematic film" and "villa animated with Seedance" clips look expensive for three reasons that cost nothing in Blender: **slow, eased camera moves with few keyframes**, **level cameras (straight verticals)**, and **a believable sky + exposure**. Paid AI video adds motion that a real camera could never do and changes the building between frames; a Blender film keeps the architecture exact. This skill is the "how" for that; basic archviz rules (real scale, glass IOR, layered EXR) live in `archviz` — read it, don't repeat it here.

Everything in Blender goes through the `blender` MCP's `execute_blender_code` (runs bpy in the user's own Blender). T1 rules: **ask before using the MCP and any other skill named here**; tell the user to save the .blend first (MCP code can't be undone in one step); free tools only — no paid AI video, no paid render farms unless the user asks.

## Workflow

```
model check → shot list → cameras + moves (EEVEE animatic) → sky/lights → materials
  → Cycles test frames → render budget → image sequence → (comp) → ffmpeg encode
```

### 1. Check the model before any camera work
- Units metres, Unit Scale 1. SketchUp imports often arrive in inches/odd scale — measure a door (≈2.0–2.1 m high) before anything else (rule of thumb, not a code requirement).
- **The user's own rules (LESSONS)**: the building sits on a real ground / foundation, nothing floats (canopies, balconies, pool edges rest on slabs), windows are real transparent glass with a **real interior behind them** (floor, ceiling, walls, curtains, a few furnished rooms, some lit at night) — never a printed fake-interior texture. A cinematic camera sees through every window; check from the street before rendering.
- Missing furniture / plants / props → `set-dressing` + `free-3d-assets`; curtains → `cloth-sim`; materials → `materials`. Plan → model first → `floorplan-to-blender`.

### 2. Write a shot list (before touching keyframes)
Agree on it with the user. A 30–45 s villa film is usually 5–8 shots:

| # | Purpose | Lens (mm) | Move | Duration | Time of day |
|---|---|---|---|---|---|
| 1 | Establish: building in landscape | 35–50 | slow drone push or orbit 20–30° | 10–12 s | golden hour |
| 2 | Hero facade, straight verticals | 24–35 | slider 1–2 m past foreground plants | 6–8 s | golden hour |
| 3 | Reveal over wall / hedge | 28–35 | crane up 2–4 m, camera stays level | 8–10 s | golden hour |
| 4 | Entrance → interior | 24–28 | push-in through door frame (reveal) | 6–10 s | dusk |
| 5 | Living space | 24–28 | slider or slow push-in, ≤0.5 m/s | 6–8 s | dusk, interior lights on |
| 6 | Detail (material, light, view) | 50–85 | very slow push-in, shallow DoF | 4–6 s | — |
| 7 | Close: night exterior, lit windows | 35 | static or tiny orbit, hold 2 s at end | 6–8 s | blue hour |

Numbers are starting points from archviz practice, not standards (unverified). Story order: outside → approach the entrance → inside, with a transition rather than a hard cut through a wall; only moves a real camera/dolly/drone could make.

### 3. Camera craft
- **Eye height 1.5–1.6 m**; interiors may drop to 1.0–1.2 m to make ceilings feel higher (experience, unverified).
- **Focal length** (36 mm full-frame sensor): interiors 24–35 mm; wider only for a deliberate hero shot; details 50–85 mm; exterior orbits 35–50 mm.
- **Two-point perspective**: keep the camera level (rotation X = 90°, Y = 0) and frame up/down with **Shift Y**, never by tilting — tilting makes verticals converge and the building lean back. Lens shift = rendering a wider FOV and cropping off-centre (Blender manual). Approximate shift to centre a point Δh above the camera at distance d: `shift_y ≈ (Δh/d) × (lens/sensor_width)` (landscape frame, sensor fit Auto; derived from geometry, verify in Blender). Too much shift stretches corners — raise the camera instead.
- Composition guides (Thirds, Golden, Diagonal…) are in Camera ▸ Viewport Display. Judge moves through the camera view, never the top view.
- DoF: interiors f/2.8–5.6 for a soft background, exteriors off or f/8+ (experience). Point **Focus Object** at an Empty and animate the Empty for a rack focus.

### 4. Moves: few keyframes, eased, slow
Read `references/camera-moves.md` for the recipe table, speeds and 5.x-safe bpy. Rules: 2–4 keyframes per shot; ease in/out (Sine or Bézier with Auto Clamped handles); roll locked at 0; if it feels fast, halve the speed and lengthen the shot; end a reveal on a short hold; turn while moving, never swing the camera on the spot. The helper builds cameras and moves for you:

```python
import runpy
cm = runpy.run_path(r"<skill>/scripts/camera_moves_bpy.py")
cam = cm["create_camera"]("CAM_02_facade", location=(-6, -14, 1.6), look_at=(0, 0, 3.5), lens=28, level=True)
cm["keyframe_move"](cam, "slider", start_frame=1, seconds=7, distance=1.5, fps=24)
print(cm["describe"](cam))
```

Do the timing pass in **EEVEE** (or Workbench) as an animatic before lighting — cheap to change, and the user approves the rhythm.

### 5. Light (details in `references/lighting-and-sky.md`)
- **Sky Texture, Blender 5.x**: use **Multiple Scattering** (most accurate). **Single Scattering is the old Nishita** (legacy); scripts that set `sky_type = 'NISHITA'` **fail in 5.x** — the enum is `'MULTIPLE_SCATTERING' | 'SINGLE_SCATTERING' | 'PREETHAM' | 'HOSEK_WILKIE'`.
- Golden hour ≈ sun elevation 2–6°; blue hour ≈ sun below the horizon (−4 to −6°) with interior lights carrying the image (photography convention; check Multiple Scattering at negative elevations in a test render).
- These skies are physically bright: bring them down with **Color Management ▸ Exposure** (stops), check with the **False Color** view.
- Real place and date: the free official **Sun Position** extension drives sun + sky from latitude/longitude/time.
- HDRI (Poly Haven, CC0): turn on World MIS sampling when the HDRI has a small bright sun.
- **Light Portals only for interiors** lit through windows (area light, Portal on, matching the opening); useless outdoors. CPU-only alternative: Path Guiding.
- **IES profiles and light node trees are Cycles-only**; EEVEE ignores them.
- Light Groups (Cycles) let you rebalance sun / sky / interior lights in the compositor without re-rendering.

### 6. Materials that read as real
- Window glass, Blender 5.2: Principled BSDF, Transmission 1, **Thin Wall** on (the manual names "window sheets") for single-plane panes; solid panes with thickness (Solidify) need more Transmission bounces. Older versions: mix Glass (camera rays) with Transparent (shadow rays) via Light Path to avoid caustic noise.
- Sheer curtains: Thin Wall + transmission/subsurface. Visible edges: Bevel **modifier** (the Bevel shader node is Cycles-only and ~20 % slower).
- Keep base colours below ~0.8 (less noise); Poly Haven / ambientCG textures are CC0.
- Deeper shading work → `materials`.

### 7. Render settings (details in `references/render-and-denoise.md`)
- **Cycles for the final film** (physically correct bounces and glass); EEVEE for the animatic or stylised work. EEVEE: ray tracing is **off by default**, thin walls leak light, one refraction only.
- Cycles start point: Noise Threshold 0.01 (0.005 for interiors), Max samples 512–2048, Denoise **OpenImageDenoise**, passes **Albedo + Normal**, Prefilter **Accurate**, **Animated Seed on**, Clamp Indirect 4–10, Filter Glossy 1.0, caustics off. Motion blur on, shutter 0.5 (= 180°).
- **Flicker (boiling) is the #1 animation problem**: OIDN denoises each frame alone. Anti-flicker checklist: more samples / lower threshold → portals or path guiding for interiors → clamp + filter glossy to kill fireflies → render a 3–5 s test clip and watch it looping before the full render.
- **Temporal denoise exists only for NVIDIA (OptiX)**: render **OpenEXR MultiLayer** with the **Denoising Data** pass (plus Vector), then run `bpy.ops.cycles.denoise_animation(input_filepath=..., output_filepath=...)` — Python only, no UI button. AMD/Intel/CPU: no official temporal denoiser; use more samples.
- **AgX** view (Filmic is deprecated). Looks are named exactly `AgX - Punchy`, `AgX - Greyscale`, `AgX - Very High Contrast`, `AgX - High Contrast`, `AgX - Medium High Contrast`, `AgX - Base Contrast`, `AgX - Medium Low Contrast`, `AgX - Low Contrast`, `AgX - Very Low Contrast`. Start with Base or Medium High Contrast; Khronos PBR Neutral for colour-critical product/material shots.

### 8. Budget the render before starting it
Render 3 representative frames at final resolution (brightest, most complex, most glass), take the slowest, then:
```bash
python scripts/render_budget.py --seconds 40 --fps 24 --spf 95 120 140 --machines 1 --width 1920 --height 1080 --format exr-multilayer --passes 6 --deadline-hours 24
```
It reports total time, disk for the sequence (estimate) and which trade-offs (resolution %, noise threshold, samples, EEVEE) fit the deadline. Over budget → in this order: resolution → noise threshold → time limit → portals → fewer bounces → EEVEE.

### 9. Image sequence, then encode (details in `references/encode-and-deliver.md`)
- **Never render straight to video** (the manual says so: a crash leaves an unplayable file). Render PNG (16-bit for grading) or EXR sequences; **Overwrite off + Placeholders on** lets you resume, or split frames across several PCs.
- Encode with free ffmpeg (ask before installing it; if the user has it, use it):
```bash
python scripts/encode_sequence.py renders/shot01/ --fps 24 --codec h264 --out shot01.mp4          # prints the command
python scripts/encode_sequence.py renders/shot01/ --fps 24 --codec h265 --out shot01_hevc.mp4 --run
```
H.264 CRF 18 (≈ visually lossless), H.265 CRF 22 with `-tag:v hvc1` (plays on Apple), ProRes 422 HQ for editing. The script refuses to overwrite without `--force` and warns about missing frames. Cutting, music, titles → `ffmpeg-skill`.

### 10. Optional AI enhancement
For upscaling, style passes or an "AI look" on finished frames → `ai-archviz-render` (ask first). Per-frame AI processing tends to flicker between frames (unverified); keep the clean Blender sequence as the master.

## Blender 5.0 API breaks (old tutorials and scripts fail)
- `action.fcurves` / `action.groups` are **removed** → F-curves live in a channelbag: `bpy_extras.anim_utils.action_get_channelbag_for_slot(action, obj.animation_data.action_slot)`.
- `scene.node_tree` removed → `scene.compositing_node_group` (assign a `CompositorNodeTree` from `bpy.data.node_groups.new(...)`); **Composite node removed → Group Output**; Use Nodes removed.
- `ImageFormatSettings.media_type` (`'IMAGE'`, `'MULTI_LAYER_IMAGE'`, `'VIDEO'`) must be set **before** `file_format`.
- EEVEE engine id is `BLENDER_EEVEE` again (not `BLENDER_EEVEE_NEXT`); Sky `'NISHITA'` → `'SINGLE_SCATTERING'`.

## Hand-offs (ask before using each)
- Basics of archviz composition and delivery → `archviz`. Model from a plan → `floorplan-to-blender`.
- Furniture, plants, props → `set-dressing`, `free-3d-assets`; shaders → `materials`; curtains → `cloth-sim`.
- Deeper keyframe / constraint / NLA work → `blender-animation-rigging`; timing and easing principles → `motion-design`.
- Editing, music, captions, social formats → `ffmpeg-skill`. AI enhancement → `ai-archviz-render`.
- `lighting-design` and `camera-systems` are about **game engines** (lightmaps, follow cameras) — only borrow principles from them.

## Limits (say them, don't hide them)
- `camera_moves_bpy.py` was written against the Blender 5.x Python API docs but **was not run in Blender** (no Blender on the authoring machine); it was only syntax-checked. If a call fails, fix the script and tell the user. `render_budget.py` and `encode_sequence.py` were tested in plain Python (encode with ffmpeg 9.0.1 on generated test frames: H.264, H.265 Main 10 `hvc1`, ProRes HQ, missing-frame warning, overwrite refusal).
- Shot durations, speeds, lens and f-stop ranges, CRF choices and render-budget size estimates are experience values, not standards.
- The shift formula is derived from geometry, not quoted from the manual — check the framing in the camera view.
- No temporal denoising on non-NVIDIA GPUs; heavy interiors may need very high samples to stop flicker.
- The "AI video look" (people walking, water, swaying trees) needs real animation work in Blender (cloth, particles, rigged characters) — this skill covers cameras, light and delivery, not character animation.
