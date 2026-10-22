# Consistency, checking, and short clips

Items marked "rule of thumb" come from common practice, not from a spec or a test we ran.

## Same building, same look, every camera
- **Fixed seed + fixed prompt + same style reference** (IP-Adapter, or the first approved render as reference) across all cameras (rule of thumb).
- **ControlNet strength high**, ≈0.8–1.0 (InstantX suggests 0.8–1.0 for its model). Lower only for soft areas like sky and planting.
- **img2img over the beauty pass:** keep denoise low (start ≈0.3–0.45, rule of thumb) so the AI re-skins materials and light instead of redrawing the building. Raise it only inside a mask.
- **Repaint by region:** Cryptomatte / ID masks for glass, plants, sky; one pass per region instead of the whole frame.
- **Protect** signage, logos, house numbers, brand colours: mask them out of generation and composite the Blender original back on top. AI garbles text and replaces logos (Qwen-Image renders text much better, but still check).
- Edits like "same building, rainy evening" suit Qwen-Image editing or FLUX Kontext (Kontext is non-commercial — see the licence file; consistency claims are BFL's own, not independently checked).

## Check every output against the clay render
Overlay at 50 % or flip between the two and look for:
- window/door count and position, mullion pattern
- railings, columns, beams, roof line, parapet height
- perspective / vertical lines drifting (verticals should stay vertical)
- signage and numbers (should be the composited original)
- materials the client didn't ask for (wood turned into stone)
If anything changed: raise ControlNet strength, lower denoise, tighten the mask, or add a lineart/MLSD ControlNet on top of depth. Report the check to the user; don't hand over an image you didn't compare.

## Short clips (image-to-video)
| Model | Licence | VRAM | Notes |
|---|---|---|---|
| **Wan2.2 TI2V-5B** | Apache-2.0 | official script targets 24 GB (e.g. 4090) with `--offload_model True --convert_model_dtype --t5_cpu`; ComfyUI docs say native offloading makes it "fit well on 8GB vram" | 720P, 24 fps, 1280×704 |
| **Wan2.2 I2V-A14B / FLF2V** | Apache-2.0 (ComfyUI docs: "support commercial use") | official ≈80 GB class; ComfyUI fp8 + offload runs on less, no number given (a third party reports OOM at decode on a 4090) | needs high-noise + low-noise models; **FLF2V = first + last frame**, best fit for architecture shots |
| LTX-Video 0.9.8 (13B/2B) | LTXV Open Weights License ("other"); the 2025-04 version requires a paid licence for companies with ≥ $10M revenue | not stated; 2B distilled for small cards | image-to-video supported |
| LTX-2 / 2.3 | LTX-2 Community License; a $10M threshold appears only in third-party sources (**未验证**); building a competing product needs a separate licence | not stated; fp8/fp4 builds | video + audio; built-in ComfyUI LTXVideo nodes |
| HunyuanVideo-I2V | Tencent Hunyuan Community License: **Territory excludes EU, UK, South Korea** (outputs not licensed there either); > 100M MAU needs a separate licence; outputs may not improve other models | 720p min 60 GB, 80 GB recommended | up to 129 frames (~5 s). **Don't suggest it** to users in those regions or on consumer GPUs. |

Free + commercial-friendly default: **Wan2.2 TI2V-5B** on consumer cards; Wan2.2 14B fp8 FLF2V when VRAM allows.

### Steadier architecture clips (rule of thumb, results 未验证)
1. Animate the camera in Blender (slow dolly/orbit; architecture hates fast moves).
2. Export passes for the first and last frame; make both stills with the same seed/ControlNet/reference and check both against clay.
3. Feed them to Wan2.2 FLF2V; prompt the motion ("slow dolly forward"), not the building.
4. Longer shots: AI keyframes every N frames from the Blender animation and FLF2V between pairs.
5. Watch for "breathing" walls, flickering windows, drifting text; re-composite signage per frame or cut around it.

If the user needs a reliable long walkthrough, a Blender animation render (or `archviz-web-walkthrough`) is more honest than AI video — say so.

## Sources
- InstantX strength: https://huggingface.co/InstantX/Qwen-Image-ControlNet-Union
- Qwen-Image text: https://huggingface.co/Qwen/Qwen-Image
- Wan2.2: https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B , https://docs.comfy.org/tutorials/video/wan/wan2_2 , https://computingforgeeks.com/run-wan-video-generation-locally/ (third party)
- LTX: https://huggingface.co/Lightricks/LTX-Video , https://open.windriver.com/info/uni-license-list/licenses/ltxv-owl-2025-04-17.html , https://huggingface.co/Lightricks/LTX-2 , https://static.lightricks.com/legal/ltx-2-open-weights-license-0.X.pdf
- HunyuanVideo-I2V: https://huggingface.co/tencent/HunyuanVideo-I2V , https://huggingface.co/tencent/HunyuanVideo-I2V/blob/main/LICENSE
