# Hunyuan3D on the user's own PC

Sources: Tencent-Hunyuan/Hunyuan3D-2.1 (README, `api_server.py`, `api_models.py`, `API_DOCUMENTATION.md`, LICENSE), YanWenKun/Hunyuan3D-2-WinPortable (README), ahujasid/blender-mcp (`addon.py`: `create_hunyuan_job_local_site`, scene properties). All read 2026-10-08.

## Which version

| | Hunyuan3D 2.1 (2025-06) | Hunyuan3D 2.0 / 2mini / 2mv |
|---|---|---|
| input | **image only** (API has no text field) | image; 2.0's demo also had a text-to-image front end (UNVERIFIED in the API) |
| output | mesh + **PBR** textures | mesh + plain colour texture |
| VRAM (official numbers) | shape 10 GB, texture 21 GB, both 29 GB | lower; 2mini is the lightest |
| licence | Tencent Hunyuan 3D 2.1 Community License | Tencent Hunyuan 3D 2.0 Community License (same structure) |

The Windows pack below bundles both. On a 12–16 GB card: generate the **shape with 2.1**, then texture with the pack's low-VRAM options (its README says geometry can run in ≥ 3 GB and texture in ≥ 6 GB with its "mmgp" optimisations, at the cost of system RAM, ≥ 24 GB recommended), or texture in Blender yourself.

## Install

### Option A: Windows one-click pack (easiest)
YanWenKun/Hunyuan3D-2-WinPortable:
1. NVIDIA driver ≥ 576.57. Pick the pack by GPU: **CUDA 12.9** for RTX 20/30/40/50, **CUDA 12.6** for GTX 10-series and older (and RTX 20/30/40). Download the `.7z.001` and `.7z.002` from the releases page, put them in one folder, extract the `.001`.
2. Extract to a short path such as `C:\AI\HY3D2` (Windows 260-character path limit).
3. For textures, install the **CUDA Toolkit** (12.9.1 per the README) and the **Visual C++ Build Tools**. Without them it still makes meshes, but no textures.
4. Run `UPDATE.bat`, then `RUN.bat`. In the launcher pick the program: "Hunyuan3D 2.1" (web UI) or **"API 2.1"** (the server the `blender` MCP talks to). Ticking "Enable Texture Generation" compiles the texture parts on first launch, which takes a while.
5. Models download on first start. The web UI says `running on http://0.0.0.0:8080`; open http://localhost:8080. For the API mode, use the address the window prints (UNVERIFIED which port the pack uses for the API).

### Option B: official repo (Linux/Windows with Python)
Python 3.10, PyTorch 2.5.1 + CUDA 12.4 (as tested by Tencent):
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

`scripts/hunyuan3d_client.py` wraps `/health` and `/generate` (standard library only).

## Connecting the `blender` MCP (local mode)

The installed `blender` MCP (mcp-for-blender) has a Hunyuan3D panel: 3D Viewport ▸ N ▸ BlenderMCP ▸ Tencent Hunyuan 3D → mode **Local API** → **API URL** = `http://127.0.0.1:8081` (or the pack's address). Then `generate_3d` (or the panel) sends `POST {url}/generate` and imports the GLB.

- **Keep "Inference Steps" at 20.** The addon only allows 20–50 and Hunyuan3D 2.1 only accepts 1–20, so anything above 20 fails with a validation error (422). Octree 256 and guidance 5.5 are fine.
- Leave "Texture" off on 12–16 GB cards unless the server runs in low-VRAM mode.
- The MCP docs say `generate_3d` prefers **Premium** generators automatically. Premium is a paid service; don't sign up. With Premium off, the local generator is used.
- The tool takes an image path or URL. A text prompt only works if the server supports text, and 2.1 doesn't.

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
