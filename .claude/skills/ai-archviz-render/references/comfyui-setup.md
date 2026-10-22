# ComfyUI setup (free, local)

Everything here installs or downloads things — **ask the user before each step** and say how big it is.

## Install choices (Windows)
- **Desktop app** (Windows/macOS): the officially recommended route for new users.
- **Portable build**: download, unzip with 7-Zip, double-click `run_nvidia_gpu.bat`. The console shows `http://127.0.0.1:8188` when it is ready; closing that window stops ComfyUI. The README itself says portable is "not recommended for regular users".
  - RTX 20-series and newer: `ComfyUI_windows_portable_nvidia.7z`
  - GTX 10-series and older: `ComfyUI_windows_portable_nvidia_cu126.7z`
  - AMD, Intel and ARM64 builds also exist.
  - Python packages for the portable build: `.\python_embeded\python.exe -m pip install <pkg>` (ask first).
- `pip install comfy-cli` then `comfy install`, or manual `git clone` (manual installs on RTX 20+ need PyTorch for CUDA 13.0 / cu130 or newer).

Licence: GPL-3.0. Using it to make images doesn't put the images under GPL; it matters only if you redistribute modified ComfyUI code.

Minimum hardware per README: "as low as 4GB vram + 8GB ram", depending on the model. Real archviz models want much more (SDXL ≈ 8 GB is comfortable; Qwen-Image 20B much more — its model card gives no VRAM figure; use fp8/GGUF builds if the user's card is small, 未验证 per build).

## Keeping models outside the install
Copy `extra_model_paths.yaml.example` to `extra_model_paths.yaml`, set `base_path` and the `checkpoints`/`loras`/`vae`/`controlnet` subfolders. Handy when models live on another drive.

## The local API (what `comfy_client.py` uses)
Default `http://127.0.0.1:8188`.
| Route | Use |
|---|---|
| `GET /object_info` | all node classes and their inputs (health check; also shows whether a custom node is missing) |
| `POST /upload/image` | upload a pass (multipart field `image`; optional `subfolder`, `type`, `overwrite`) → `{name, subfolder, type}` |
| `POST /prompt` | `{"prompt": <API-format workflow>, "client_id": "..."}` → `prompt_id` + `number`, or `error` / `node_errors` |
| `GET /history/<prompt_id>` | outputs and status once finished (path form is common usage, 未验证 against the route table) |
| `GET /view?filename=&subfolder=&type=output` | download a result |
| `/ws` | WebSocket progress events (`status`, `executing`, `progress`, `executed`); the client polls instead to stay stdlib-only |

The workflow **must** be the API format (UI: File → Export (API)); the normal "Save" format has a different structure and `/prompt` rejects it.

Don't expose ComfyUI to the network (`--listen 0.0.0.0`) to "make it easier": anyone on the network could then queue jobs and read files through custom nodes.

## Sources
- README: https://github.com/comfyanonymous/ComfyUI
- Portable install: https://docs.comfy.org/installation/comfyui_portable_windows
- Server routes: https://docs.comfy.org/development/comfyui-server/comms_routes
- API example: https://github.com/comfyanonymous/ComfyUI/blob/master/script_examples/basic_api_example.py
