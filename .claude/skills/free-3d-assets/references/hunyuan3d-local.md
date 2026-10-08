# Hunyuan3D on the user's own PC

Sources: Tencent-Hunyuan/Hunyuan3D-2.1 (README, `api_server.py`, `api_models.py`, `API_DOCUMENTATION.md`, LICENSE), YanWenKun/Hunyuan3D-2-WinPortable (README), ahujasid/blender-mcp v2.1.9 (`addon.py`, `src/blender_mcp/server.py`, `generation.py`). All read 2026-10-08. The installed `blender` MCP is this package: its PyPI name is `mcp-for-blender` and its tools (`get_addon_status`, `search_assets`, `import_asset`, `generate_3d`, `look`) are the ones in that source.

## Which version

| | Hunyuan3D 2.1 (2025-06) | Hunyuan3D 2.0 / 2mini / 2mv |
|---|---|---|
| input | **image only** (API has no text field) | image; the Windows pack's 2.0 web UI also has **text → 3D** (it makes an image first with HunyuanDiT) |
| output | mesh + **PBR** textures | mesh + plain colour texture |
| VRAM (official numbers) | shape 10 GB, texture 21 GB, both 29 GB | lower (no official table read); 2mini is the lightest |
| licence | Tencent Hunyuan 3D 2.1 Community License | Tencent Hunyuan 3D 2.0 Community License (same structure) |

The Windows pack below bundles both, with "mmgp" memory optimisations that move model parts to system RAM. Its README: geometry in ≥ 3 GB VRAM (2.1, maximum optimisation), texture in ≥ 6 GB (2.0, maximum optimisation), **≥ 24 GB system RAM** (less VRAM → more RAM). Which program has mmgp matters:

| Pack program | mmgp | Use on a 12–16 GB card |
|---|---|---|
| **Hunyuan3D 2.1** (web UI, :8080) | yes | shape + PBR texture in one go, slower. Best quality route |
| Hunyuan3D 2.0 (web UI) | yes | lighter; also text → 3D |
| **API 2.0** | partial | what Blender / the client script can use with **texture on** |
| **API 2.1** | **no** | official VRAM numbers apply: shape (~10 GB) fits on 12 GB, texture (~21 GB) won't |

So on 12 GB: the web UI 2.1 for textured models, or API 2.1 shape-only and paint the texture yourself (below), or API 2.0 with texture. The API takes an image and returns a finished model; there's no "texture this existing mesh" call. Close FiveM, browsers and other GPU programs while generating, and ask the user how much system RAM they have before suggesting the mmgp modes.

**Texturing a shape-only mesh in Blender** (free): unwrap (Smart UV Project), then project the original photo onto it. Texture Paint mode → Texture Slots → paint with the photo as a *stencil* brush texture from the matching view, or use the camera-projection method (UV Project modifier from a camera aligned to the photo), then bake to the UVs. Back and hidden sides need hand painting or a second photo. `texture-workflow` covers baking (ask first).

## Install

### Option A: Windows one-click pack (easiest)
YanWenKun/Hunyuan3D-2-WinPortable:
1. NVIDIA driver ≥ 576.57. Pick the pack by GPU: **CUDA 12.9** for RTX 20/30/40/50, **CUDA 12.6** for GTX 10-series and older (and RTX 20/30/40). Download the `.7z.001` and `.7z.002` from the releases page, put them in one folder, extract the `.001`.
2. Extract to a short path such as `C:\AI\HY3D2` (Windows 260-character path limit).
3. For textures, install the **CUDA Toolkit** (12.9.1 per the README) and the **Visual C++ Build Tools**. Without them it still makes meshes, but no textures.
4. Run `UPDATE.bat`, then `RUN.bat`. In the launcher pick the program: "Hunyuan3D 2.1" (web UI) or **"API 2.1"** (the server the `blender` MCP talks to). Ticking "Enable Texture Generation" compiles the texture parts on first launch, which takes a while.
5. Models download on first start. The web UI says `running on http://0.0.0.0:8080`; open http://localhost:8080. For the API programs, use the address the window prints (UNVERIFIED which port the pack uses; the official `api_server.py` defaults to 8081, and the Blender addon's default URL is `http://localhost:8081`).

### Option B: official repo (Linux, or WSL2 on Windows)
Python 3.10, PyTorch 2.5.1 + CUDA 12.4 (as tested by Tencent). The build steps use `bash` and `wget`; on plain Windows use Option A.
```bash
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
cd hy3dpaint/custom_rasterizer && pip install -e . && cd ../..
cd hy3dpaint/DifferentiableRenderer && bash compile_mesh_painter.sh && cd ../..
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P hy3dpaint/ckpt
# web UI
python3 gradio_app.py --model_path tencent/Hunyuan3D-2.1 --subfolder hunyuan3d-dit-v2-1 --texgen_model_path tencent/Hunyuan3D-2.1 --low_vram_mode
# API server (default port 8081)
python3 api_server.py --host 127.0.0.1 --port 8081 --low_vram_mode
```
Bind to `127.0.0.1`. The default `--host 0.0.0.0` exposes the server to the whole network.

## The API (2.1, `api_server.py`)

- `POST /generate` with JSON returns the model file (GLB) directly. It is synchronous and takes minutes.
- `POST /send` returns `{uid}`; `GET /status/{uid}` returns `status` and `model_base64` when done.
- `GET /health`.

Request fields (`api_models.GenerationRequest`, with ranges):

| field | default | range |
|---|---|---|
| `image` | — (required) | base64 PNG/JPG |
| `remove_background` | true | |
| `texture` | false | true needs the texture pipeline (VRAM!) |
| `seed` | 1234 | 0 – 2³²−1 |
| `octree_resolution` | 256 | 64 – 512 (higher = finer mesh, more VRAM) |
| `num_inference_steps` | 5 | **1 – 20** |
| `guidance_scale` | 5.0 | 0.1 – 20 |
| `num_chunks` | 8000 | 1000 – 20000 |
| `face_count` | 40000 | 1000 – 100000 (max faces for texturing) |

`scripts/hunyuan3d_client.py` wraps `/health` and `/generate` (standard library only). Its `--steps` default is 20 (quality); the server's own default is 5 (fast drafts). It must run on the PC with the server: copy the single file there, or run it from the T1 checkout if T1 is cloned on that PC (`python C:\path\to\T1\.claude\skills\free-3d-assets\scripts\hunyuan3d_client.py ...`, or `py` if `python` opens the Microsoft Store).

## Connecting the `blender` MCP (local mode)

Settings in Blender: 3D Viewport ▸ N ▸ MCP for Blender sidebar ▸ tick **Tencent Hunyuan 3D** → Mode **local api** (the other mode, "official api", is Tencent Cloud with SecretId/SecretKey: an account and paid quota, don't use) → **API URL** (default `http://localhost:8081`; change it to the pack's address) → Octree Resolution, **Inference Steps**, Guidance Scale, Generate Texture.

How `generate_3d` picks a generator (`generation.choose_provider`): if **Premium** is active, everything goes through Premium (paid), even `provider="hunyuan3d"`. Without Premium, `auto` takes the first enabled own generator in the order Hunyuan3D, then Hyper3D Rodin. So:
1. `get_addon_status` first: `premium_generators` must be empty, and Hunyuan3D should show as on. Never paste a Premium licence key.
2. Call `generate_3d(image="C:/full/path/burger.png", provider="hunyuan3d")`. Being explicit avoids falling through to Rodin (which needs a paid key).
3. The addon sends `POST {url}/generate` (image as base64, timeout 600 s) and imports the GLB. The local call is synchronous; if the MCP call times out on a slow card, use the panel or `hunyuan3d_client.py` and import the GLB.

- **Inference Steps: keep 20.** The addon only allows 20–50 (default 20) and Hunyuan3D 2.1 only accepts 1–20, so anything above 20 fails with a validation error (422). Octree 256 and guidance 5.5 (addon defaults) are fine.
- "Generate Texture" on API 2.1 needs ~21 GB more VRAM. Leave it off on 12–16 GB, or point the URL at API 2.0.
- The tool takes an image path or URL. Images pasted in chat can't be passed; ask for a file path. A text prompt only works on a server that supports text (2.1 doesn't).

## Getting good results

- One object per image, centred, filling ~70 % of the frame, plain or removable background, soft even light, no motion blur, slight top-down three-quarter view.
- Thin parts (straps, antennas, chair legs) come out thick or merged. Model those by hand afterwards.
- Symmetric objects: a front or three-quarter shot works best. The back is guessed.
- Raise `octree_resolution` (e.g. 384) only for detailed objects. It's slower and uses more VRAM.
- Try 2–3 seeds and keep the best.

## Licence essentials (2.1 LICENSE, read in full before public use)

- Royalty-free, but **only in the "Territory"**: worldwide **excluding the EU, the UK and South Korea**. Outputs may not be used outside the Territory either.
- Services above **1 million monthly active users** need a separate licence from Tencent.
- Outputs must not be used to **improve any other AI model**.
- Follow Tencent's Acceptable Use Policy.
- Not legal advice. For a small FiveM server in Malaysia these terms are generally fine.
