# Models and what the licence allows

Read on 2026-10-22. Licences change; not legal advice. For client work the user should read each licence in the workflow (checkpoint, ControlNet, IP-Adapter, VAE, text encoders, LoRAs) — **the strictest one wins**.

## Image models
| Model | Licence | Commercial? |
|---|---|---|
| **Qwen-Image** (20B) | Apache-2.0 | Yes. Strong text rendering (especially Chinese), also does editing. Model card gives no VRAM figure. |
| **FLUX.1 [schnell]** | Apache-2.0 | Yes. |
| **SDXL base 1.0** | CreativeML Open RAIL++-M | Yes, royalty-free, "Licensor claims no rights in the Output", but follow Attachment A use restrictions. The model card's "intended for research purposes only" line conflicts with the licence; the licence governs. |
| **HiDream-I1** | Transformer MIT; VAE from FLUX schnell (Apache-2.0); text encoders Llama-3.1-8B-Instruct (**Llama 3.1 Community License**) + T5 (Apache-2.0) | Card says "Commercial-Friendly"; check the Llama 3.1 terms before commercial use. |
| **FLUX.1 [dev]** | FLUX.1 [dev] Non-Commercial License | **The model is non-commercial**: Non-Commercial Purpose excludes "revenue-generating activity" and "impact on end users". Section 2(d) says you may use **Output** "for any purpose (including for commercial purposes)", and outputs may not be used to train a competing model. So: outputs are allowed, but running dev for paid work is commercial use of the model → risky without a BFL commercial licence. Prefer schnell or Qwen-Image for client work. |
| FLUX.1 Kontext [dev] (editing/consistency) | non-commercial (exact licence name differs between sources, 未验证); commercial licence via BFL portal | Not without a licence. |
| FLUX.1 Depth/Canny [dev] | 未验证 (probably same as dev) | 未验证 |

## ControlNet / conditioning
| Model | Licence | Notes |
|---|---|---|
| **xinsir `controlnet-union-sdxl-1.0`** | Apache-2.0 | One model: Openpose, Depth, Canny, Lineart, AnimeLineart, Mlsd, Scribble, Hed, Softedge, Teed, Segment, Normal; ProMax adds tile/inpaint/outpaint. For archviz use Depth, Lineart/Mlsd (straight lines), Normal, Segment. |
| **InstantX Qwen-Image ControlNet Union** | 未验证 (not confirmed on the page) | canny, soft edge, depth, pose; suggested conditioning scale 0.8–1.0; ComfyUI has an official template; weights `Qwen-Image-InstantX-ControlNet-Union.safetensors`. |
| DiffSynth Qwen-Image union LoRA | 未验证 (source is a personal wiki) | canny/depth/lineart/softedge/normal/openpose |
| ComfyUI_IPAdapter_plus (e.g. `ip-adapter-plus_sdxl_vit-h.safetensors`) | 未验证 | style vs composition separately, "precise" style transfer; if the reference is too strong lower CFG to 3–4 or use RescaleCFG. |
| FLUX Redux | 未验证 (not researched) | — |

## Recommended free stacks
- **Commercial-safe, mid GPU:** SDXL checkpoint (check the fine-tune's own licence) + xinsir Union (depth + lineart/mlsd) + IP-Adapter style reference.
- **Text/signage-heavy, big GPU:** Qwen-Image + InstantX Union. Still composite real signage back from Blender.
- **Personal study only:** FLUX.1 dev is fine for non-commercial use — tell the user the commercial caveat above.

## Sources
- FLUX.1 dev licence: https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/LICENSE.md
- FLUX.1 schnell: https://huggingface.co/black-forest-labs/FLUX.1-schnell
- Kontext: https://rits.shanghai.nyu.edu/ai/flux-1-kontext-dev-released-open-weights-model-for-advanced-image-editing/ , https://blog.comfy.org/p/flux1-kontext-dev-day-0-support
- SDXL licence: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/LICENSE.md
- Qwen-Image: https://huggingface.co/Qwen/Qwen-Image
- HiDream-I1: https://huggingface.co/HiDream-ai/HiDream-I1-Full
- xinsir Union: https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
- InstantX Union: https://huggingface.co/InstantX/Qwen-Image-ControlNet-Union , https://comfy.org/p/supported-models/qwen-image-instantx-controlnet-union
- IPAdapter_plus mirror: https://gitee.com/Anstarc/ComfyUI_IPAdapter_plus
