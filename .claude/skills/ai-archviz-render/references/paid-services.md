# Paid route (付费) — documented only

**Rule:** don't use these and don't recommend buying them. If the user asks for one: say it is paid, quote the price below with its reliability, name the free alternative, and wait for a clear yes before doing anything that costs money or needs their API key. Keys go in environment variables, never in files or commits.

Prices checked 2026-10. "未验证" = official page could not be read; numbers come from third parties.

| Service | Price | Reliability | Free alternative |
|---|---|---|---|
| **OpenAI GPT Image** (API, per 1M tokens) | gpt-image-2: image input $8, **image output $30**; gpt-image-1.5 $8/$32; gpt-image-1 $10/$40; gpt-image-1-mini $2.50/$8; Batch half price (gpt-image-2 output $15). Per-image cost: use OpenAI's calculator. | official page | local Qwen-Image or SDXL (also for "reference images" in reels) |
| **Runway** | Free $0 (125 one-time credits); **Standard $15/mo** ($12 yearly) 625 credits; Pro $35 ($28) 2,250; Max $95 ($76) 9,500 | official page | Wan2.2 in ComfyUI |
| **Krea** | Free (100 compute units/day, **no commercial use**, Seedance needs a paid plan); Basic $9/mo ($5 yearly); **Pro $35** ($21); Max $105 ($63); Business $200 ($160). Realtime generation, Enhancer; video via Kling/Runway/Veo/Wan/Seedance | official page, but the page contradicts itself (one spot says Max $70/40k) | ComfyUI + Wan2.2 |
| **Higgsfield** (aggregator: Seedance, Kling, …) | Starter ≈ $19/mo yearly, 270 credits; Plus $47 yearly / $59 monthly, 1,200; Ultra $99 / $129, 3,000; Free not for commercial use; credits don't roll over. Credits per Seedance run unknown. | **未验证** (official page unreadable) | ComfyUI + Wan2.2 |
| **Kling** | Standard $10/mo 660 credits; Pro $37 3,000; Premier $92 8,000; Ultra $180 26,000; free daily credits reported inconsistently | **未验证** | Wan2.2 |
| **ByteDance Seedance** (BytePlus ModelArk API) | per token; Seedance 2.5 ≈ $10.70/M tokens (480p/720p), ≈ $2.84 per 5 s 1080p; Dreamina is web UI only, no API | **未验证** | Wan2.2 |

Notes for when the user does choose one:
- They give less geometry control than Blender passes + ControlNet. Still upload the clay render as reference and still do the overlay check.
- Check each service's terms on commercial use of outputs and on uploading client designs (confidentiality).
- The agent never signs up, enters payment details or API keys for the user — the user does that themselves.

## Sources
- OpenAI: https://developers.openai.com/api/docs/pricing
- Runway: https://runway.com/pricing
- Krea: https://www.krea.ai/pricing
- Higgsfield: https://higgsfield.ai/pricing (unreadable), https://creatify.ai/blog/higgsfield-pricing-(2026)-plans-and-what-you-ll-actually-pay , https://lumalabs.ai/news/higgsfield-pricing
- Kling: https://www.eesel.ai/en/blog/kling-ai-pricing , https://www.aiarty.com/ai-video-generator/kling-ai-pricing.htm
- Seedance: https://www.developersdigest.tech/models/video-generation/byteplus , https://www.byteplus.com/en/topic/578667
