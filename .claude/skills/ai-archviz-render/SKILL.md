---
name: ai-archviz-render
description: Turn locked Blender architecture (clay or draft renders) into photoreal AI stills and short clips WITHOUT the AI changing the building — export depth/mist/normal/line/mask passes from Blender 5.x, drive a local ComfyUI (free) with ControlNet so walls, windows and columns stay where they are, keep several angles consistent with a fixed seed and reference image, animate with Wan2.2 first/last-frame or drive Wan2.2 Fun Control / VACE with a Blender depth or colour-map video, and check every result against the clay render. Paid services (OpenAI GPT Image, Runway, Krea, Higgsfield, Kling, Seedance, Magnific) are documented only and need the user's OK first. Use whenever the user wants AI rendering of a building, interior or apartment, "AI 渲染", "AI 出图", "把白模变成真实照片", "建筑效果图 AI", "ComfyUI 建筑", "ControlNet 室内", "让 Blender 渲染更真实", "AI 做建筑动画/短片", "图生视频", "色块图转视频", "color map 视频", "3D 动画转真实视频", "像 reels 里 30 分钟做出房子效果图" — even if they don't name ComfyUI.
---

# AI archviz render (geometry stays locked)

The reels that "render a villa with AI in 5 minutes" skip the part that matters to a real client: **the AI quietly redesigns the building** — an extra window, a balcony rail that melts, six columns become five, the shop sign turns into gibberish. A pretty image of the wrong building is worse than a clay render. So this skill treats Blender as the source of truth and AI only as a "skin": Blender passes lock the geometry, ControlNet follows them, and every output is overlaid on the clay render before it goes to anyone.

**Claude/Codex cannot generate images or video themselves.** Pixels come from the user's own ComfyUI (free, local) or a paid service the user chooses. The agent writes scripts, sets up passes, fills workflow JSON and talks to the local ComfyUI API.

Comes after `floorplan-to-blender` (geometry) and `archviz` / `archviz-cinematic` (materials, lights, cameras) when those are available. Ask before using any of them, and before using the `blender` MCP (T1 rule). Remind the user to save the .blend first.

## Workflow

### 1. Lock the geometry first
AI cannot fix a wrong model; it makes it look plausible. Check with the user that the building is final (dimensions, openings, signage positions) and that each camera is framed. Render one clay/draft still per camera — it is the reference every AI output is checked against.

### 2. Export passes from Blender (5.x API)
Read `references/blender-passes.md`. Through the `blender` MCP:
```python
import runpy
ep = runpy.run_path(r"<skill>/scripts/export_passes_bpy.py")
print(ep["setup"](r"<project>/passes", passes=("beauty", "depth", "mist", "normal", "index", "crypto")))
print(ep["render_still"]())      # writes the files through the compositor File Output nodes
ep["restore"]()                  # put the user's own compositor back
```
Blender 5.0 broke old scripts: `scene.node_tree` is gone (use `scene.compositing_node_group`), File Output uses `directory`/`file_name`/`file_output_items`, the pass is `Depth` (was `Z`). The script follows the 5.x API, but **it has not been run in Blender** (no Blender on the authoring machine) — if a call fails, read the error, fix the script, tell the user.

Which pass for what: **Depth/Mist** → depth ControlNet (Mist when depth of field or motion blur is on, because Depth is not anti-aliased and gets noisy); **line art** (Freestyle) → lineart/MLSD ControlNet for straight edges; **Normal** → normal ControlNet; **Cryptomatte / Object Index** → masks to repaint only glass, plants or sky, and to *protect* signage and logos.

### 3. Set up ComfyUI (free, local) — ask first
ComfyUI is GPL-3.0 and runs on the user's GPU. Installing it, downloading models, or starting it needs the user's OK each time (large downloads, many GB). Read `references/comfyui-setup.md` for the install choices (Desktop app, or the Windows portable `ComfyUI_windows_portable_nvidia.7z` / `_cu126` for GTX 10-series and older, started with `run_nvidia_gpu.bat`), where models go, and VRAM notes.

Pick models by **what the user is allowed to do with the output** — read `references/models-and-licenses.md`. Short version: for paid client work prefer Qwen-Image (Apache-2.0), FLUX.1 schnell (Apache-2.0) or SDXL (OpenRAIL++-M) with xinsir ControlNet Union SDXL (Apache-2.0). FLUX.1 dev's licence lets you use *outputs* commercially but running the *model* for revenue counts as commercial use — say this plainly and let the user decide; don't call it "free for commercial use".

### 4. Build the workflow, then drive it from a script
The user builds/loads a workflow in ComfyUI's UI (official templates are a good start), checks it works by hand once, then exports it with **File → Export (API)**. In that JSON, replace the values you want to vary with placeholders: `"{{IMAGE}}"`, `"{{DEPTH}}"`, `"{{LINES}}"`, `"{{MASK}}"`, `"{{SEED}}"`, `"{{PROMPT}}"`, `"{{NEGATIVE}}"`. Then:
```bash
python scripts/comfy_client.py health
python scripts/comfy_client.py run --workflow wf_api.json \
  --upload IMAGE=passes/beauty.png --upload DEPTH=passes/depth.png \
  --set SEED=421337 --set PROMPT="modern tropical villa, late afternoon, ..." --out renders/cam01
```
`comfy_client.py` (Python standard library only) talks **only** to a ComfyUI on localhost / 127.0.0.1 / ::1 and refuses any other host, so nothing about the user's project leaves the machine. It checks `/object_info`, uploads passes, fills placeholders (and refuses to queue if any `{{…}}` is left), posts `/prompt`, polls `/history/<id>`, and downloads results with `/view`. `--dry-run` prints the filled workflow without uploading or queueing. Whole-number values become numbers (`"{{SEED}}"` → `421337`). `assets/example_workflow_api.json` shows the placeholder shape (SDXL img2img + depth ControlNet); it is an illustration, not a tested workflow. `scripts/test_comfy_client.py` tests the client against a stub server (passes; no real ComfyUI was available). Running it against the user's ComfyUI is fine once they agreed to use this skill and ComfyUI is running; starting ComfyUI is their call.

### 5. Keep it consistent, keep it honest
Read `references/consistency-and-video.md`. The essentials: same seed + same prompt + same style reference (IP-Adapter) across cameras; ControlNet strength high (≈0.8–1.0, rule of thumb); for img2img over the beauty pass keep denoise low so the AI re-skins instead of redesigns; repaint by mask, not the whole frame.

**Text and logos are never left to the AI.** It garbles signs and swaps brands. Mask them out and composite the Blender original back on top (Qwen-Image is better at text, but still check).

Then check every output: overlay it at 50 % on the clay render (or toggle between them) and look for changed window counts, rails, columns, roof lines, perspective drift. Report what you checked; if something changed, regenerate with stronger ControlNet / lower denoise / a tighter mask instead of "it's close enough".

### 6. Short clips
Image-to-video models make buildings "breathe" and flicker. Most stable free route: render the first and last frame of a Blender camera move as stills (same seed/ControlNet), then let **Wan2.2 FLF2V (first/last frame, Apache-2.0)** fill the middle. On an 8 GB card use Wan2.2 TI2V-5B with ComfyUI's offloading. Details, VRAM and the models to avoid (HunyuanVideo-I2V: not licensed in EU/UK/South Korea, ~60 GB VRAM) are in `references/consistency-and-video.md`. For a truly stable walkthrough, a real Blender animation render still beats AI video — say so.

### 6b. Colour-map video and 3D animation as motion input
When the user has (or wants) a flat colour-per-material render of a camera move, or wants a Blender animation plus real photos turned into a photoreal clip like the reels: read `references/colormap-video-to-video.md` — segmentation + depth ControlNet for stills, Wan2.2 Fun Control / Wan VACE (Apache-2.0) with the Blender depth video as control for video, and the paid Higgsfield / Seedance / Magnific route (付费, ask first). The colour map itself comes from `archviz-cinematic`'s `scripts/colormap_pass_bpy.py`.

### 7. Paid route (付费) — only if the user asks
`references/paid-services.md` lists OpenAI GPT Image, Runway, Krea, Higgsfield, Kling and Seedance with prices and how reliable each price is. **Never use or recommend buying them on your own.** If the user wants one, tell them it is paid, what it costs according to the notes, which free route does the same job, and wait for a clear yes. The same "geometry locked + check against clay" rules apply; most of these give less control than ControlNet.

## Hand-off and related skills (ask first)
- Geometry → `floorplan-to-blender`; lighting/materials/cameras → `archviz`, `materials`, `lighting-design`.
- Edits and cuts of the final clips → `ffmpeg-skill`.
- Free stock skies/textures/reference photos → `pixabay-assets`.
- 3D props that are missing → `free-3d-assets`.

## Limits (say them, don't hide them)
- The agent can't see the user's GPU, models or ComfyUI nodes; workflow node names vary between versions and custom nodes. The user's exported API JSON is the truth.
- `export_passes_bpy.py` was written from the Blender 5.0 release notes and 5.2 API docs but **never run in Blender**. Exact names for some 5.x pieces (`file_output_items.new` arguments, `media_type`, some socket names) are marked 未验证 in the script and handled with fallbacks.
- Depth/normal polarity conventions differ between ControlNet models (未验证 per model) — test once with an obvious scene and flip if near/far is reversed.
- Licences in the notes were read on 2026-10-22; they change. This is not legal advice — for client work, have the user read the licence of every model in the workflow.
- AI output is not a measured drawing. Never present it as construction-accurate.
