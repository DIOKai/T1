# Tools compared (read 2026-10-22)

Sources: each repo's README, LICENSE, release page and the GitHub API on 2026-10-22. Full notes with URLs: `docs/skill-batches/archviz-batch2-2026-10-22-research/ai-short-drama.md`. Not legal advice; re-check the release page before installing.

| | 火宝短剧 huobao-drama | Toonflow | Pixelle-Video |
|---|---|---|---|
| Repo | github.com/chatfire-AI/huobao-drama | github.com/HBAI-Ltd/Toonflow-app | github.com/ATH-MaaS/Pixelle-Video (README links still say AIDC-AI) |
| What it makes | Novel / one sentence → script → characters/scenes/props → storyboard → clips → stitched episode | Infinite canvas: script, storyboard, character/scene/prop assets, 3-view character sheets, 3D director preview, multi-reference video | Topic → narration script → one image/clip per sentence → TTS → BGM → HTML template → video (narration style, not multi-character drama) |
| Licence | **CC BY-NC-SA 4.0 — no commercial use** without written permission | **MIT** (current; v1.0.8–1.1.8 Apache-2.0 + extra terms, earlier AGPL-3.0) | **Apache-2.0** (+ NOTICE) |
| Commercial use | No | Yes | Yes |
| Needs paid API? | **Yes** for images and video (OpenAI, Gemini, Volcano Seedance 2.0, MiniMax H3, Bailian Wan 3.0 — 付费). Text via OpenAI-compatible API | No if you run local LLM + ComfyUI; third-party APIs optional (付费) | No — README "完全免费方案: Ollama + 本地 ComfyUI = 0 元". Optional RunningHub, DashScope, OpenAI, Seedance, Kling (付费) |
| Local / free option | Text only: OpenAI-compatible endpoint → Ollama `http://localhost:11434/v1` (**未验证**). No ComfyUI per README | "可接入本地 ComfyUI 和 LLM" via custom provider (steps in a Feishu doc, **未验证**) | Ollama for LLM; ComfyUI selfhost workflows: image_flux, image_qwen, tts_edge, tts_index2, video_wan2.1_fusionx (image_nano_banana is Google paid) |
| GPU | None (cloud) | None for the app; ComfyUI needs one | Docs: NVIDIA 6 GB+ for local ComfyUI; video models need more |
| Windows install | `HuobaoDrama.Setup.4.0.8.exe` (~148 MB, unsigned → SmartScreen), or Node 20 + `npm install` ×2, or Docker | `toonflow-2.0.7-Setup.exe` (~48 MB, installs WebView2), or Docker (`docker compose up -d --build`, port 3000) | `Pixelle-Video-v0.1.15-win64.zip` (~399 MB, unzip → `start.bat` → localhost:8501), or `uv run streamlit run web/app.py` + ffmpeg |
| Activity (2026-10-22) | v4.0.8 on 2026-10-05; 16.5k★; 37 open issues | v2.0.7 on 2026-10-20; 18.9k★; 3 open issues | v0.1.15 on 2026-01-27, last push 2026-06-14; 29.3k★; 169 open issues |
| Privacy / safety | Keys in local SQLite; scripts and images sent to the cloud provider; Seedance needs a public `PUBLIC_BASE_URL` to read local assets (exposes them) | **No login on the web/API** — keep port 3000 local or use an SSH tunnel; plugin market at api.toonflow.net | Uploads only when a cloud service is chosen; "打印模型请求参数" prints prompts and paths to the console |
| Ads in README | Own relay key api.firemux.com (付费) | TF-Router relay (付费, source open), sponsors 秘塔 / APIMart / 优云智算 (付费) | RunningHub cloud (付费) |
| Files aimed at AI agents | `CLAUDE.md` — contributor dev guide, no instructions to the user's agent | `AGENTS.md` — contributor code style (camelCase, no test files), no instructions to the user's agent | none found |

## Cost reality
Toonflow's own showcase: a ~2-minute episode in ~2 hours cost about **¥130** in API calls (Seedance 2.0 video ~¥120, language ~¥10, GPT Image 2 < ¥1). That is the order of magnitude for paid video models; local Wan2.x costs electricity and time instead.

## Local model licences (from ai-archviz-render)
- ComfyUI GPL-3.0 (outputs not affected).
- Wan2.2 TI2V-5B / 14B — Apache-2.0, commercial OK. Wan2.1 FusionX (Pixelle's local video workflow) is a community merge — check its own model card before commercial use (未验证).
- Qwen-Image — Apache-2.0. SDXL — Open RAIL++-M. **FLUX.1 dev — non-commercial model licence** (Pixelle's default `image_flux`).
- HunyuanVideo licence excludes EU, UK, South Korea.
- The strictest licence among checkpoint, LoRA, VAE and text encoder wins.

## How to choose (short)
1. Commercial? → drop 火宝短剧.
2. Has an NVIDIA GPU and wants 0 cost? → Pixelle-Video (narration) or Toonflow + local ComfyUI (drama).
3. Wants recurring characters and editing control? → Toonflow.
4. Personal fun, accepts 付费 API, wants the most automatic path? → 火宝短剧.
