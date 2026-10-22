---
name: archviz-web-walkthrough
description: Turn a Blender building, apartment or interior into an interactive browser walkthrough like Klay / Kunkun Visual property tours — walk freely in first person (desktop pointer lock + WASD, mobile joystick, drag-to-look and tap-to-teleport), wall and stair collision, room labels and hotspots, an optional furniture / material swap panel, unit info panel, compass minimap, time-of-day sun, section cut and measuring tool, an optional Gaussian-splat mode for scanned real rooms, then free static hosting. Covers lightmap baking, glTF export and glTF-Transform optimization that keeps lightmap UVs, collision and mobile budgets. Use whenever the user wants a 3D web tour, virtual showroom, online open house, walk-through of a floor plan or Blender scene in the browser, "put my house model on a website", or a scanned room on the web — even if they only say "网页看房", "3D看房", "在线漫游", "网页漫游", "做成网页可以走", "VR看房", "虚拟样板间", "换家具", "第一人称走进房子", "高斯泼溅放网页", "剖切", "测量距离", "日照", "户型信息".
---

# Archviz web walkthrough

A property tour that feels good is mostly **not** a three.js problem: it's baked light that looks real on a phone, a collision mesh that lets you through every door but not through glass, and files small enough to open on 4G. Most failed tours skip one of these: real-time lights that look flat, walking through walls, a 180 MB GLB. So this skill goes Blender → optimized glTF → a small static page, and checks the file between every step.

General three.js work is already covered by the repo's `threejs-*` skills; this skill only adds the archviz-specific parts and links to them. Ask the user before using any of them, before touching Blender through the `blender` MCP, and before installing anything (T1 rules). Everything recommended here is free unless marked 付费.

## Inputs to settle first (ask in one go)

- Source: Blender scene (often from `floorplan-to-blender`), IFC/Bonsai model, or a phone/drone **scan** of a real space (→ Gaussian-splat branch, step 9).
- Target devices: phone-first? (Usually yes for property tours — iOS Safari has no pointer lock, so touch controls are mandatory, not optional.)
- Lighting approach: (A) baked lightmap on a second UV + normal materials (materials stay swappable), (B) everything baked into baseColor + Unlit (cheapest, most stable on phones, but no swaps and no specular), or (C) real-time lights only (fastest to make, looks flat indoors).
- Furniture swap? Colour/material variants only, or whole different models?
- Where it will be hosted, and whether it's commercial (GitHub Pages forbids running an online business; see step 10).

## Pipeline

### 1. Prepare the scene in Blender
Read `references/blender-export.md`. Real scale in metres, Apply Modifiers on export, procedural materials baked to images (glTF only exports Principled BSDF inputs). Split meshes **per room/floor** so the browser can cull and so files can later be partitioned. Put a simplified collision shell in a `COL_` collection (walls, floors, glass, a ramp instead of every stair). Mark tour data with Object Custom Properties — they export as glTF `extras` and the template reads them:

| Property | On | Meaning |
|---|---|---|
| `spawn` = 1 | Empty | start position (feet), optional `yaw` in degrees |
| `hotspot` = "Living room" | Empty | teleport button with that label |
| `room` = "Kitchen" | floor mesh | room name shown while standing on it |
| `lightmap` = "lightmaps/kitchen.png" | mesh | lightmap file applied on UV1 |
| `collider` = 1 / name `COL_*` | mesh | collision only, never rendered |
| `nocollide` = 1 | mesh | visible but walk-through (rugs, plants) |
| `slot` = "sofa_living" | Empty | furniture swap anchor |

### 2. Bake lighting (approach A or B)
UV ‣ Unwrap ‣ **Lightmap Pack** with **New UV Map** (keeps UV0 for tiling materials), **Share Texture Space** and a margin. Cycles bake **Diffuse** with only Direct + Indirect (pure light, approach A) or **Combined** (approach B; no specular). Set a Margin so mipmaps don't show seams. Details, the UV-order trap and the parts marked 未验证 are in `references/blender-export.md`. Don't bake swappable furniture into the room lightmap — swapping leaves a shadow of the old sofa behind.

### 3. Export glTF
Binary `.glb` (or glTF Separate when you want to edit textures afterwards), **+Y Up**, Apply Modifiers, UVs on (all UV layers export, layer n → `TEXCOORD_n`), **Custom Properties** on, Punctual Lights only if you use approach C. Area lights and World/HDRI lighting **don't export** — bake them or relight in three.js (`threejs-lighting`). Blender 5.2 adds Meshopt compression in the exporter; for this pipeline leave compression off at export and compress once in step 4, so the extras/UV checks run on clean data. Export swappable furniture as separate small GLBs (origin bottom-centre, metres).

### 4. Optimize step by step — never bare `optimize`
Read `references/optimize-gltf.md` and run the commands there. glTF-Transform's `optimize` defaults (`--join`, `--flatten`, `--simplify`, `--palette`, `--prune-attributes`) silently destroy a tour: they delete TEXCOORD_1 when no glTF texture uses it (your lightmaps are loaded from code, so nothing does), drop empty nodes that only carry extras (hotspots, spawn), merge rooms and furniture into one mesh, and bend straight wall corners. Run `dedup` → `prune --keep-attributes true --keep-extras true --keep-leaves true` → texture resize/KTX2 → `meshopt`, then **check**:

```bash
python scripts/check_walkthrough_build.py dist/model.glb
```
It is read-only (Python stdlib) and reports file size vs the 25 MiB Cloudflare limit, node/mesh/material/texture counts, texture formats and sizes (KTX2 or not, estimated GPU memory), whether TEXCOORD_1 survived, tour extras (spawn, hotspots, rooms, lightmaps — and whether the lightmap files exist), `COL_` colliders, KHR_materials_variants, and a draw-call estimate. Fix every ERROR; read every WARN. Run it on the export **and** after each optimize step when something disappears.

### 5. Build the page from the template
Copy `assets/walkthrough-template/` (index.html + main.js, no build step, three r186 pinned via importmap) next to `model.glb` and serve it over HTTP (`python -m http.server` — opening the file directly fails because ES modules and fetch need http). The template already does: GLTFLoader with Draco/KTX2/Meshopt decoders, lightmaps from `lightmap` extras (`texture.channel = 1`, `flipY = false`), collider layer for the Octree, capsule physics, pointer-lock WASD, touch joystick + drag-to-look, hotspot buttons that teleport, a room label, and out-of-bounds respawn. Before shipping, self-host the decoders and three (the CDN is for prototyping; `threejs-assets` says decoder versions must match the library). For loader/decoder detail use `threejs-assets`; for lights/tone mapping `threejs-lighting` and `threejs-exposure-color-grading`.

Lightmap brightness: three.js divides diffuse light by π, so the template defaults `lightMapIntensity` to π — measured in r186 (no tone mapping, 8-bit sRGB lightmap): the result then equals albedo × lightmap. The template treats PNG/JPG lightmaps as sRGB; three.js docs suggest linear float (EXR/HDR). That a Blender Diffuse bake follows the same albedo × lightmap convention is 未验证 — compare a screenshot against the Blender render and set `lightmapIntensity` per mesh if needed. The template exposes `window.tour` (`ready`, `scene`, `camera`, `renderer`, `player`, `teleport`, `frame`) as a readiness signal and for stepping frames in browser tests.

### 6. Walking, collision, stairs
Read `references/controls-and-collision.md`. It's the three.js `games_fps` capsule + Octree approach adapted for architecture: build the Octree from the `COL_` shell, not the visual mesh; eye height ~1.6 m and capsule radius ~0.25 m (rules of thumb, so 80 cm doors pass); slopes count as floor when `normal.y >= 0.15`, so a hidden ramp over the stairs just works; low walking speed, no jump. Desktop: pointer lock. Mobile: left joystick + right-side drag + tap hotspots, because iOS Safari doesn't support `requestPointerLock`. Only one system writes the camera at a time — walk, teleport tween or auto-tour (ownership rules: `threejs-camera-controls-and-rigs`).

### 7. Hotspots, labels, minimap
Hotspot buttons come from `hotspot` extras; room names from `room` extras on floors (a downward ray every ~0.2 s). For richer labels/panels use `threejs-html`; for clicking 3D objects `threejs-interaction`. Minimap: on phones a 2D floor-plan image with a dot for the player is cheaper than a second rendered view (rule of thumb); `floorplan-to-blender`'s top SVG or a top-camera render works as the image.

### 7b. Interactive extras (optional)
Unit/lot info panel, compass + minimap, time-of-day sun and sky, section (cut) view with stencil caps, two-tap measuring and a material changer bar: read `references/interactive-features.md`. A moving sun conflicts with baked lightmaps — it lists the options (baked presets is the phone default).

### 8. Furniture / material swap (optional)
Read `references/furniture-swap.md`. Colour or fabric options on the same geometry → **KHR_materials_variants** (ratified; authored in Blender's glTF Variants panel; three.js doesn't load it automatically — use the pattern from the official `webgl_loader_gltf_variants` example). Different models → `slot` empties + lazily loaded furniture GLBs, disposing the old one. Furniture sources: Poly Haven and Kenney (CC0), Poly Pizza/Sketchfab (check each model's licence), or the user's own Hunyuan3D via `free-3d-assets`. **IKEA has no public 3D model API** — don't scrape their site or redistribute their models; make "IKEA-style" from CC0 models instead.

### 9. Gaussian-splat branch (scanned real spaces)
Read `references/gaussian-splats.md`. Free pipeline: capture → COLMAP → train with Brush (Apache-2.0, runs on Windows/AMD/NVIDIA) or gsplat (Apache-2.0, CUDA) → clean in SuperSplat (MIT) → SPZ/PLY. Display either with three.js r186's native `GaussianSplat` (**WebGPURenderer only**, room scale, no LOD/streaming) or Spark 2.4 (MIT, WebGL2, works with the template's WebGLRenderer). Add an invisible collision shell (a few boxes) to walk inside a splat. Don't recommend LichtFeld Studio's Windows prebuilt (paid download — build from source or use Brush), and never use the original INRIA code for a commercial job (research/non-commercial licence).

### 10. Test and host
Test with `threejs-testing` (browser fixture, console/network errors, touch interaction) and on a **real phone** — headless Chrome is not a mobile GPU. Checklist: can't walk through any wall or glass; every door passable; stairs climbable; falling out of the world respawns; every hotspot reachable; after a furniture swap no ghost shadow; draw calls and frame time measured with `threejs-performance`. Starting budgets (rules of thumb, not official): phone < ~100 draw calls, desktop < ~300; textures ≤ 2048 on phones; first load ≤ ~10–20 MB.

Then read `references/hosting.md`: Cloudflare Pages (free, **25 MiB per file**), GitHub Pages (1 GB site, 100 GB/month soft bandwidth, not for running an online business). Split big tours per floor below 25 MiB. Deployment mechanics: `threejs-deployment`. Publishing is the user's call — don't deploy anything without asking.

## Tools and MCP

- `blender` MCP (steps 1–3, runs bpy in the user's Blender; ask first, save the .blend first). Operation details: `mcp-for-blender`. If it isn't connected, say so; don't install or reconfigure it without approval. Typical setup for the open-source blender-mcp server (未验证 that it's the same package the user has installed):
  - Claude Code: `claude mcp add blender -- uvx blender-mcp`
  - Codex: in `~/.codex/config.toml` add `[mcp_servers.blender]` with `command = "uvx"` and `args = ["blender-mcp"]`
- Node CLIs (`@gltf-transform/cli`, KTX-Software `ktx`) for step 4: ask before installing; `npx @gltf-transform/cli ...` avoids a global install but downloads the package on first run — say so.

## Limits (say them, don't hide them)
- Tested on a small generated GLB (two rooms, door gap, `COL_` shell, hotspots, lightmap, variants) in desktop Chromium and its mobile emulation: walls/door collision, hotspot teleport, keys 1–9, room label, joystick and drag-to-look all worked, no console errors. Not tested on a real iPhone/Android, with KTX2/Draco/meshopt files, on stairs, or with a production-size scene. Variants are only detected by the checker; the template has no swap UI.
- Several Blender details are 未验证 for 5.2 release builds (UV layer → TEXCOORD order was read from the main branch; which UV the baker uses). Check the exported file with the script instead of trusting settings.
- Octree collision is static: moving doors need their own handling (leave doorways open in the collision shell, or rebuild).
- Gaussian splats: no official phone budget exists (community says ~1–2 M splats, 未验证); native three.js splats need WebGPU.
- Budgets above are rules of thumb; measure on the user's devices.
