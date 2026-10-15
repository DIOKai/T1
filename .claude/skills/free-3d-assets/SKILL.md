---
name: free-3d-assets
description: Use when the user wants 3D models for GTA V / FiveM (props, furniture, food, weapons-as-props, decorations, characters/peds) without paying — generating them from a picture with Hunyuan3D running locally on their own NVIDIA GPU, or getting them from free libraries (Poly Haven, Poly Pizza, Sketchfab CC models) — and then making them game-ready (scale, polycount, LODs, Sollumz .ydr/.ytyp, or a rigged add-on ped through muto-ped-rig). Also use when they mention Tripo, Meshy, Rodin, "AI 生成 3D", "图片转 3D", "image to 3D", "Hunyuan3D", "混元3D", "找免费模型", "做道具", or ask for a free alternative to a paid 3D generator.
---

# Free 3D assets for FiveM

Paid generators (Tripo, Meshy, Rodin, Blender MCP Premium) are off the table: the project rules forbid paid tools, and Tripo's free-plan output is non-commercial anyway. Two free routes cover almost everything:

1. **Generate locally with Hunyuan3D** (Tencent, free weights, runs on the user's NVIDIA GPU). It is **image → 3D**: give it a clear picture of one object.
2. **Download from free libraries** (Poly Haven CC0, Poly Pizza, Sketchfab models with a free licence). The `blender` MCP can search and import these (`search_assets` / `import_asset`; ask before using it, per the project rules).

Either way, the model is not game-ready when it arrives. `references/to-gta.md` turns it into a FiveM prop or ped.

Read what you need:
- `references/hunyuan3d-local.md` — install (Windows one-click pack or official repo), VRAM per step, the API server, connecting the `blender` MCP's local mode, the `steps = 20` gotcha, licence (territory, MAU, no training other models).
- `references/free-libraries.md` — Poly Haven, Poly Pizza, Sketchfab: licences, what to check, attribution file.
- `references/to-gta.md` — scale, cleanup, polycount and texture budgets, LODs, collision, Sollumz `.ydr` + `.ytyp`, streaming and spawning. Characters → muto-ped-rig → add-on ped.

Related skills (ask before using, per the project rules): `retopology`, `uv-workflow`, `texture-workflow`, `lod-pipeline`, `asset-optimization`, `collision-proxy` (use Sollumz bounds names for GTA, not UCX), `prop-artist`, `fivem-mlo-housing` (furniture inside interiors), `fivem-animation` (animate the ped), `pixabay-assets` (reference photos for image-to-3D), muto-atlas `/prop` `/asset` (vanilla prop names and sizes to match).

## Workflow

### 1. Decide: vanilla, find or generate
- **Vanilla first.** GTA already has thousands of props (food, drinks, phones, tools, furniture). Check muto-atlas `/prop` or CodeWalker for one that fits (UNVERIFIED example: a burger prop like `prop_cs_burger_01`; look the name up, don't guess). A vanilla prop costs no download for players.
- Common real-world object with no good vanilla match (chair, crate, plant, food) → search the libraries (`search_assets` / `import_asset`). Ready topology and textures, zero GPU time.
- Unique object, or the user wants **their own photo** turned into 3D → Hunyuan3D. When the user explicitly asks for their photo, mention the vanilla/library options in one line and then do what they asked.
- Character → Hunyuan3D or a library model, then **muto-ped-rig** (ask first; it installs a Blender extension). Never ship a ped without the GTA skeleton.

### 2. Generate with Hunyuan3D (the user's PC)
- One object, centred, plain background, three-quarter view, good light. Hunyuan3D removes the background itself (`remove_background`).
- **No text prompts in 2.1.** For "make me a burger", find or make an image first: a photo, a Pixabay image (`pixabay-assets`), or the user's sketch.
- VRAM: shape ~10 GB, texture ~21 GB on the official code. On a **12–16 GB** card: the Windows pack's **2.1 web UI** (memory-optimised, needs ≥ 24 GB system RAM) makes textured models; the **API 2.1** program fits shape only, so paint the texture in Blender or use API 2.0. Table and Blender texturing steps in the reference. Close FiveM and browsers while generating.
- Drive it from the web UI, from Blender (`blender` MCP: `get_addon_status` → Premium must be off → `generate_3d(image=<full path>, provider="hunyuan3d")`, sidebar mode **local api**, Inference Steps **20**), or with `scripts/hunyuan3d_client.py` (Python standard library; runs on the PC with the server, so copy the file there or run it from a local T1 clone):
  ```powershell
  py hunyuan3d_client.py health --url http://localhost:8081
  py hunyuan3d_client.py generate burger.png --out burger.glb --steps 20
  ```
- Running code in the user's Blender, and starting servers on their PC, are ask-first actions.

### 3. Make it game-ready
Follow `references/to-gta.md`: real-world scale, pivot at the base, decimate to budget, check UVs and textures (≤ 1024–2048 px), LODs, collision, Sollumz export, `.ytyp`, test in game. Run the polycount/texture checks before export (`asset-optimization`).

### 4. Credit and licence
Write `CREDITS.md` next to the asset: source URL, author, licence, date, and for Hunyuan3D outputs the model version. Library licences vary per model; see `references/free-libraries.md`.

## Ground rules
- Free only. Don't sign up for Blender MCP Premium, Tripo, Meshy or Rodin, or a Tencent Cloud (official Hunyuan API) account, on the user's behalf. Local Hunyuan3D needs no account.
- Hunyuan3D 2.1's licence doesn't apply in the EU, UK and South Korea, and you can't use its outputs to train or improve other AI models. Fine for a Malaysian FiveM server; mention it if the user is elsewhere.
- Don't recreate trademarked products 1:1 (logos, branded packaging) from photos for a public resource.
- Things not verified from a primary source are marked UNVERIFIED in the references. Test in game before relying on them.
