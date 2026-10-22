# Colour-map and 3D-animation-driven AI (stills and video)

The reels: (1) a Revit → three.js model rendered as a **"color map" video** (one flat colour per material along a camera path) that a paid AI turned into a photoreal video following the colour regions; (2) a villa rebuilt roughly in Blender from photos, its **3D animation used as motion input** and **real photos as style references** (Magnific + Seedance, paid). Both work because the 3D animation fixes *where things are and how the camera moves*; the AI only paints. The free route below does the same locally; the paid route is documented and needs a clear yes first.

Make the inputs with `archviz-cinematic` (`references/build-up-and-colormap.md`, `scripts/colormap_pass_bpy.py`) and this skill's `export_passes_bpy.py` (depth/mist/normal/line). Render **every pass for the same frames** of the same camera.

## Inputs to render from Blender (same camera, same frame range)
| Pass | Use | Notes |
|---|---|---|
| Colour map (flat colour per material, AA off) | segmentation ControlNet for stills; region guide for paid video models; mask source | ADE20K colours if you want the seg ControlNet to know "wall/floor/window" |
| Depth or **Mist** | the main structure control for stills **and** free video models | Mist when motion blur/DoF is on (`blender-passes.md`) |
| Line art (Freestyle) / Canny of the clay | straight edges (MLSD/canny control) | strong for window mullions, railings |
| Clay / beauty first frame | img2img start and the checking reference | |
| Cryptomatte / Index masks | protect signage, repaint only glass/plants | |

## Free route — stills
SDXL + **xinsir ControlNet Union SDXL** (Apache-2.0; its card lists **Segment**, Depth, Canny, Lineart, MLSD, Normal…), two ControlNet applies stacked:
1. **Depth/Mist** at high strength (≈0.8–1.0, rule of thumb) — locks geometry.
2. **Segment** from the colour map at medium strength (≈0.4–0.7, rule of thumb) — tells the model which region is wall, floor, glass, plant. The union card doesn't document the palette; ADE20K colours are the safe bet (SD1.5's `control_v11p_sd15_seg` was trained on ADE20K-style maps) — 未验证 for the SDXL union model: test once with an obvious room.
3. Prompt names materials per region ("oak floor, white plaster walls, linen sofa, floor-to-ceiling glass"), plus an IP-Adapter style image (a real photo the user owns or a CC0 one) for mood.
Then the usual checks (`consistency-and-video.md`): overlay on clay, signage composited back from Blender.

Without a seg-capable ControlNet: use the colour map only to **make masks** (one colour → one mask, exact because AA is off) and inpaint region by region with depth ControlNet on.

## Free route — video (local ComfyUI)
Both models below are **Apache-2.0** (commercial use allowed per ComfyUI docs / model card), run in ComfyUI with official templates, and take a **control video** (your Blender depth/edges sequence) plus a **reference / start image**. Neither lists "segmentation colour map" as a native control type — the colour map's job in the free route is to make the **first frame** (stills route above) and masks; the **depth or edge video** carries the motion.

| Model | What it takes | Size / VRAM (as documented) | Fit |
|---|---|---|---|
| **Wan2.2 Fun Control 14B** (Alibaba PAI, high-noise + low-noise fp8 pair; template "Wan 2.2 14B Fun Control") | start image + control video (Canny, **Depth**, OpenPose, **MLSD**, trajectory) + prompt; node `Wan22FunControlToVideo` | ComfyUI tested on an **RTX 4090D 24 GB**, 640×640, 81 frames: ~83 % VRAM, ~520 s; with the optional LightX2V 4-step LoRAs ~89 % VRAM, ~79–138 s (less motion detail). No minimum VRAM stated; GGUF community quantizations exist (未验证 quality) | **Best default**: Blender depth/MLSD video as control + an AI-made photoreal first frame from the stills route |
| **Wan2.1 VACE** 14B (720P/480P) or 1.3B (480P only) | reference image(s) + control video (depth/pose/edges from preprocessing) + masks; node `WanVaceToVideo` | ComfyUI docs, RTX 4090: 640×640×49 frames ≈ 7 min; 720×1280×81 ≈ 40 min; 14B fp16 file ≈ 32 GB (fp8 text encoder to save VRAM); 1.3B ≈ 7 GB | When you want **real photos as reference** (VACE's reference-to-video) or masked edits (repaint only the windows) |
| Wan2.2 VACE Fun A14B | VACE-style control on Wan2.2 (Canny/Depth/Pose/MLSD, subject reference) | listed Apache-2.0 on mirrors; official card not read (**未验证**) | newer option; check ComfyUI templates in the user's version |

Recipe (rule of thumb, results 未验证 on architecture):
1. Blender: camera move ≤ 0.5 m/s, render in 81-frame chunks (the documented test length; Wan 14B clips are usually played at 16 fps — check the template's save node — so 81 frames ≈ 5 s; frame count `4n+1`, i.e. length−1 divisible by 4 per ComfyUI VACE docs), render **Mist/Depth** and **line art** sequences, and the colour map.
2. First frame: stills route (depth + segment ControlNet + photo reference) → check against clay.
3. Wan2.2 Fun Control: start image = that frame, control video = depth (or MLSD for crisp edges), prompt = materials + light, not the motion ("the camera" is already in the control). Resolution: start 640×640 or 832×480, divisible by 16.
4. Longer films: chain 81-frame chunks using the **last frame of chunk N as the start image of chunk N+1**; expect colour drift — re-anchor with a fresh stills-route frame every few chunks.
5. Check every chunk: windows/mullions stable, no breathing walls, signage re-composited from Blender per frame.

Hardware honesty: on 8–12 GB cards these 14B models need heavy offloading or GGUF and become very slow; the 1.3B VACE (480P) or Wan2.2 TI2V-5B (`consistency-and-video.md`) are the realistic options there. A clean Blender render of the same camera is still the most stable "video" — offer it.

Licences: ComfyUI is GPL-3.0 (the app); Wan weights Apache-2.0; the T5/umt5 encoder and VAE files come with the templates (licences per their cards — have the user read them for client work). Not legal advice.

## Camera paths "proposed by AI"
The reel's AI path proposal is replaceable by the agent working from plan data — rooms, doors, eye-level paths through door axes, speeds: `archviz-cinematic` `references/build-up-and-colormap.md` section (c). No paid tool needed.

## Paid route (付费) — ask first, never by default
Same inputs, less control. Only if the user explicitly asks; say it is paid, give the price with its reliability, name the free route above, and wait for a clear yes. The agent never signs up, pays or enters keys; keys stay in env vars.

| Service | What the reels used it for | Price notes (checked 2026-10) | Reliability |
|---|---|---|---|
| **Higgsfield** (aggregator; Seedance 2.0 etc.) | colour-map video → photoreal; camera-reference feature reads a clip's camera motion | its blog: ~$0.22 for a 10 s Fast clip, no monthly plan; a CapCut comparison: ~$0.135–0.14 per second; plan table in `paid-services.md` | **未验证**, sources contradict each other |
| **Seedance 2.0** (ByteDance; via Dreamina, Higgsfield, BytePlus/Segmind APIs) | takes text + images + video clips (+ audio) together, i.e. 3D animation as motion reference + photos as style | Segmind: 720p 5 s ≈ $0.76 from text/image, ≈ $0.46 with a reference video (input video duration is billed too) | third-party, **未验证** |
| **Magnific** (Freepik rebranded as Magnific in 2026) | upscaling / "re-imagining" stills and frames, access to video models | third-party: Premium ~$16, Premium+ ~$37, Pro ~$90 per month (others list different numbers; one shared credit pool) | **未验证**, sources disagree |

Rules that still apply on the paid route: upload the clay/colour-map first frame as reference, do the overlay check, composite signage from Blender, and check each service's terms on commercial use and on uploading a client's unreleased design (confidentiality).

## Sources
- Wan2.2 Fun Control in ComfyUI (models, Apache-2.0, 4090D test, control types, node): https://docs.comfy.org/tutorials/video/wan/wan2-2-fun-control , https://blog.comfy.org/p/comfyui-wan22-fun-inp-support
- Wan VACE in ComfyUI (files, Apache-2.0, 4090 timings, length−1 divisible by 4): https://docs.comfy.org/tutorials/video/wan/vace
- Wan2.1 VACE model card (Apache-2.0, 1.3B 480P only, 14B 480P/720P): https://huggingface.co/Wan-AI/Wan2.1-VACE-14B
- Wan2.2 VACE Fun (mirror cards, 未验证): https://huggingface.co/QuantStack/Wan2.2-VACE-Fun-A14B-GGUF , https://huggingface.co/Pyros13/Wan2.2-VACE-Fun-A14B-Diffusers/blob/main/README.md
- xinsir ControlNet Union SDXL (Segment supported, Apache-2.0): https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
- ADE20K palette: https://github.com/open-mmlab/mmsegmentation/blob/main/mmseg/datasets/ade.py
- Seedance / Higgsfield (third-party and vendor blog): https://higgsfield.ai/blog/generating-with-seedance-2-0 , https://higgsfield.ai/blog/best-platforms-to-access-seedance-2-0 , https://dreamina.capcut.com/seedance/seedance-price , https://segmind.com/models/seedance-2.0/pricing
- Magnific pricing (third-party, conflicting): https://www.renderahouse.com/blog/magnific-ai-pricing , https://www.myarchitectai.com/blog/magnific-ai-pricing , https://oakgen.ai/blog/magnific-ai-freepik-rebrand-pricing
