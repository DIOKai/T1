# Research notes — enhancements to 5 existing archviz skills (2026-10-22)

Trigger: reels the user saw — (A) Unreal official interactive archviz (lot info panel, compass minimap, daylight control, material/furniture changer bar, live section, 3D measure, "create a main material and use instances for variations"); (B) Revit → three.js "color map" video turned photoreal by Higgsfield, AI-proposed camera paths; (C) villa rebuilt in Blender from photos, colour-block build-up animation, Magnific + Seedance with the 3D animation as motion input and photos as references; (D) Airbnb apartment furnished from a real Mercado Livre cart.

Rule followed: new reference files, 1–2 pointer lines per SKILL.md, frontmatter descriptions kept free of ": " and " #". Nothing installed. "未验证" = not confirmed from an official source or not tested.

## 1. unreal-mcp-archviz → references/interactive-features.md
Confirmed (Epic docs):
- SunSky actor belongs to the **Sun Position Calculator** plugin (Edit ▸ Plugins ▸ Misc); bundles Directional Light, Sky Light, SkyAtmosphere; Details: Latitude, Longitude, Time Zone, North Offset, Month, Day, DST fields, **Solar Time** (float, 12:30 = 12.5). Sky Light **Real Time Capture** on by default (Movable/Stationary). Epic's ArchVis template has time-of-day Sequencers.
- **Variant Manager** works in editor and at runtime, has a Blueprint API to switch variants, LevelVariantSetDirector for function calls.
Community / 未验证:
- No official runtime "section plane" feature found; forum consensus = Material Parameter Collection plane + dot product + Masked opacity, back-face colour as cap; procedural mesh slicing for real caps. Lumen/shadow interaction with masked-out geometry 未验证 (Epic issue UE-347428 shows Lumen alpha-masking bugs in 5.5, target 5.8).
- Which SunSky function to call at runtime after setting SolarTime: 未验证.
- Minimap: orthographic Scene Capture 2D → Render Target 512², capture on demand (2026 community guide).
- UE 5.8 released mid-June 2026 (MegaLights production-ready, Lumen Lite, Unreal MCP plugin) — secondary coverage; official notes page only partly readable.
- Paid Fab clipping plugin exists (5.8/Win64 only) — mention only if asked.

## 2. archviz-web-walkthrough → references/interactive-features.md
Confirmed (three.js source read):
- `webgl_clipping_stencil`: `WebGLRenderer({ stencil: true })`, `localClippingEnabled = true`, back faces IncrementWrap / front faces DecrementWrap stencil ops, cap with `NotEqualStencilFunc` + Replace ops, `renderOrder = i + 1.1`, `onAfterRender → clearStencil()`, `plane.coplanarPoint` + `lookAt`.
- WebGLRenderer `stencil` defaults to false since r163 (forum, matches the example's explicit `stencil: true`).
- `Sky.js` uniforms: turbidity, rayleigh, mieCoefficient, mieDirectionalG, sunPosition.
- SunCalc licence BSD-2-Clause; current README says degrees, azimuth clockwise from north (older releases used radians from south — version check advised).
Design decision: features **not added to the template** (rendering/input changes need per-scene and phone testing); snippets `node --check`-ed only. Baked lightmap vs moving sun: four options documented, baked presets as phone default.

## 3. archviz-cinematic → references/build-up-and-colormap.md + scripts/colormap_pass_bpy.py
Confirmed (Blender API pages, current): `View3DShading.light` ∈ STUDIO/MATCAP/FLAT; `color_type` ∈ MATERIAL/OBJECT/RANDOM/VERTEX/TEXTURE/SINGLE; `SceneDisplay.render_aa` has OFF/FXAA/5/8/…; `Material.diffuse_color` (viewport colour, RGBA); `Object.color`; `Object.pass_index`.
ADE20K palette taken from mmsegmentation `ade.py` (e.g. wall 120,120,120; floor 80,50,50; windowpane 230,230,230; sky 6,230,230; door 8,255,51; sofa 11,102,255).
未验证: Workbench uses World viewport colour as the render background in 5.x; exact sRGB pixel match through the Standard view transform; GN build-up node tree; whether driver expressions stay on the simple-expression path. All bpy not run in Blender (no Blender here); pure helper functions tested in plain Python.

## 4. ai-archviz-render → references/colormap-video-to-video.md
Confirmed:
- **Wan2.2 Fun Control** (ComfyUI docs): Apache-2.0, commercial use; high/low-noise 14B fp8 pair + optional LightX2V 4-step LoRAs; control types Canny, Depth, OpenPose, MLSD, trajectory; node `Wan22FunControlToVideo`; tested RTX 4090D 24 GB, 640×640, 81 frames: ~83 % VRAM ~520 s; with LoRA ~89 % ~79–138 s. No minimum VRAM stated.
- **Wan2.1 VACE**: Apache-2.0 (model card + ComfyUI docs); 1.3B 480P only, 14B 480P/720P; 14B fp16 ≈ 32 GB, 1.3B ≈ 7 GB; 4090: 640×640×49 ≈ 7 min, 720×1280×81 ≈ 40 min; for first-last frame, length−1 divisible by 4.
- **xinsir ControlNet Union SDXL**: Apache-2.0, supports Segment (palette undocumented → ADE20K assumed, 未验证).
Not native: neither Wan model lists a segmentation colour map as control → colour map used for first frame + masks; depth/MLSD video carries motion.
Wan2.2 VACE Fun A14B: Apache-2.0 on mirror cards only (未验证).
Paid (付费, ask first; all 未验证, sources conflict): Higgsfield Seedance (~$0.22 per 10 s Fast clip per its blog; ~$0.135–0.14/s per a CapCut comparison; camera-reference feature), Seedance 2.0 multimodal (text+images+video+audio; Segmind 720p 5 s ≈ $0.76, ≈ $0.46 with reference video), Magnific (Freepik rebranded 2026; ~$16 / $37 / $90 per month per one source, others differ).

## 5. set-dressing → references/buyable-furniture.md + scripts/furniture_list_check.py (+ test)
Confirmed: Poly Haven = CC0, any use, no attribution required. IKEA: no official public 3D API or licence; community tools pull web-preview models without IKEA permission (reported) → don't scrape/redistribute. Manufacturer CAD/BIM downloads exist but terms vary; third-party catalogues re-host brand models with their own unclear rights (per-brand terms 未验证).
Script: stdlib, read-only on input, CSV/JSON, checks required fields, numeric dims/prices (handles 1.299,90 and 1,299.90), qty, http(s) URLs, per-currency totals, room footprint (either orientation), ceiling, door pass rule of thumb, licence warnings (missing / NC / ND / CC BY), substitutes without reason; `--export` shopping CSV, refuses overwrite without `--force`. 10 unittest cases pass.
Clearance numbers (60–90 cm paths, 45–60 cm around tables/beds) are rules of thumb.

## Tests run
- `python -B set-dressing/scripts/test_furniture_list_check.py` → 10 tests OK.
- `py_compile` on `colormap_pass_bpy.py`, `furniture_list_check.py`; every ```python block in the new references compiled; colormap pure functions exercised with a stub `bpy`.
- Every ```js block in the web reference `node --check`-ed as an ES module.
- Not run: Blender, Unreal, ComfyUI, browser.

## Sources (combined)
- https://dev.epicgames.com/documentation/en-us/unreal-engine/sun-and-sky-actor-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/working-with-scene-variants-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/scripting-the-variant-manager-setup
- https://forums.unrealengine.com/t/section-planes/128771
- https://forums.unrealengine.com/t/2719592 ; https://uhiyama-lab.com/en/notes/ue/render-target-minimap-camera/
- https://issues.unrealengine.com/issue/UE-347428
- https://gamefromscratch.com/unreal-engine-5-8-released/ ; https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes
- https://github.com/mrdoob/three.js/blob/dev/examples/webgl_clipping_stencil.html
- https://github.com/mrdoob/three.js/blob/dev/examples/jsm/objects/Sky.js
- https://discourse.threejs.org/t/webgl-clipping-stencil-plane/73867 ; https://discourse.threejs.org/t/clipping-with-3-planes-stencils-and-clipintersection-true/62329
- https://github.com/mourner/suncalc
- https://docs.blender.org/api/current/bpy.types.View3DShading.html ; https://docs.blender.org/api/current/bpy.types.SceneDisplay.html ; https://docs.blender.org/api/current/bpy.types.Material.html ; https://docs.blender.org/api/current/bpy.types.Object.html
- https://developer.blender.org/docs/release_notes/5.0/python_api/
- https://github.com/open-mmlab/mmsegmentation/blob/main/mmseg/datasets/ade.py
- https://docs.comfy.org/tutorials/video/wan/wan2-2-fun-control ; https://blog.comfy.org/p/comfyui-wan22-fun-inp-support
- https://docs.comfy.org/tutorials/video/wan/vace ; https://huggingface.co/Wan-AI/Wan2.1-VACE-14B
- https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
- https://higgsfield.ai/blog/generating-with-seedance-2-0 ; https://higgsfield.ai/blog/best-platforms-to-access-seedance-2-0 ; https://dreamina.capcut.com/seedance/seedance-price ; https://segmind.com/models/seedance-2.0/pricing
- https://www.renderahouse.com/blog/magnific-ai-pricing ; https://www.myarchitectai.com/blog/magnific-ai-pricing ; https://oakgen.ai/blog/magnific-ai-freepik-rebrand-pricing
- https://polyhaven.com/license
- https://digitalproduction.com/2026/02/09/download-ikea-furniture-as-3d-models-minus-the-trolley/ ; https://extensions.blender.org/add-ons/ikea-browser/reviews/?score=3
- https://www.cadforum.cz/catalog_en/?vyr=Vitra
