---
name: free-3d-assets
description: Use when the user wants 3D models for GTA V / FiveM (props, furniture, food, weapons-as-props, decorations, characters/peds) without paying — generating them from a picture with Hunyuan3D running locally on their own NVIDIA GPU, or getting them from free libraries (Poly Haven, Poly Pizza, Sketchfab CC models) — and then making them game-ready (scale, polycount, LODs, Sollumz .ydr/.ytyp, or a rigged add-on ped through muto-ped-rig). Also use when they mention Tripo, Meshy, Rodin, "AI 生成 3D", "图片转 3D", "image to 3D", "Hunyuan3D", "混元3D", "找免费模型", "做道具", or ask for a free alternative to a paid 3D generator.
---

# Free 3D assets for FiveM

Paid generators (Tripo, Meshy, Rodin, Blender MCP Premium) are off the table: the project rules forbid paid tools, and Tripo's free-plan output is non-commercial anyway. Two free routes cover almost everything:

1. **Generate locally with Hunyuan3D** (Tencent, free weights, runs on the user's NVIDIA GPU). It is **image → 3D**: give it a clear picture of one object.
2. **Download from free libraries** (Poly Haven CC0, Poly Pizza, Sketchfab models with a free licence). The `blender` MCP already searches and imports these.

Either way, the model is not game-ready when it arrives. `references/to-gta.md` turns it into a FiveM prop or ped.

Read what you need:
- `references/hunyuan3d-local.md` — install (Windows one-click pack or official repo), VRAM per step, the API server, connecting the `blender` MCP's local mode, the `steps = 20` gotcha, licence (territory, MAU, no training other models).
- `references/free-libraries.md` — Poly Haven, Poly Pizza, Sketchfab: licences, what to check, attribution file.
- `references/to-gta.md` — scale, cleanup, polycount and texture budgets, LODs, collision, Sollumz `.ydr` + `.ytyp`, streaming and spawning. Characters → muto-ped-rig → add-on ped.

Related skills (ask before using, per the project rules): `retopology`, `uv-workflow`, `texture-workflow`, `lod-pipeline`, `asset-optimization`, `collision-proxy` (use Sollumz bounds names for GTA, not UCX), `prop-artist`, `fivem-mlo-housing` (furniture inside interiors), `fivem-animation` (animate the ped), `pixabay-assets` (reference photos for image-to-3D), muto-atlas `/prop` `/asset` (vanilla prop names and sizes to match).

## Workflow

### 1. Decide: find or generate
- Common real-world object (chair, crate, plant, food) → search the libraries first (`blender` MCP `search_assets` / `import_asset`). Ready topology and textures, zero GPU time.
- Unique object, from a photo or concept art → Hunyuan3D.
- Character → Hunyuan3D or a library model, then **muto-ped-rig** (ask first; it installs a Blender extension). Never ship a ped without the GTA skeleton.

### 2. Generate with Hunyuan3D (the user's PC)
- One object, centred, plain background, three-quarter view, good light. Hunyuan3D removes the background itself (`remove_background`).
- **No text prompts in 2.1.** For "make me a burger", find or make an image first: a photo, a Pixabay image (`pixabay-assets`), or the user's sketch.
- Shape only needs ~10 GB VRAM (official). Texture needs ~21 GB on the official code, so a 12–16 GB card should generate the **shape** and texture it in Blender, or use the Windows pack's low-VRAM mode (see the reference).
- Drive it from Blender (`blender` MCP `generate_3d` with Hunyuan3D in **Local API** mode, steps = 20) or with `scripts/hunyuan3d_client.py` (Python standard library, talks to the local API server):
  ```bash
  python .claude/skills/free-3d-assets/scripts/hunyuan3d_client.py health --url http://localhost:8081
  python .claude/skills/free-3d-assets/scripts/hunyuan3d_client.py generate burger.png --out burger.glb
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
