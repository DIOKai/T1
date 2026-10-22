# 研究笔记：ai-short-drama（2026-10-22）

来源：一条 Threads 帖子推荐 火宝短剧 / Toonflow / Pixelle-Video。以下全部来自 2026-10-22 读到的仓库页面、README、LICENSE、GitHub API 和官方帮助页。未能核实的标「未验证」。不是法律意见。

## 1. 火宝短剧 huobao-drama

- 仓库：https://github.com/chatfire-AI/huobao-drama （GitHub API：16.5k star，创建 2026-01-05，最后 push 2026-10-05，open issues 37，未归档）
- 最新 release：v4.0.8（2026-10-05），Windows 安装包 `HuobaoDrama.Setup.4.0.8.exe` 约 148 MB。https://github.com/chatfire-AI/huobao-drama/releases
- **许可：CC BY-NC-SA 4.0**（LICENSE 文件正文为 CC BY-NC-SA 4.0；GitHub 显示 "Other"）。README：「Commercial use is prohibited … without prior written permission from the author」。→ 拿它做付费服务、商业部署、接单都不行；自己学习、非商业作品可以。生成出来的视频本身是否受此限制，许可没有明说（未验证），保守起见商用前问作者。
- 技术栈：Node.js 20+，Hono + Drizzle + better-sqlite3 + Mastra agents；Nuxt 3 前端；Electron 桌面版；FFmpeg 由 `ffmpeg-static` 内置。
- Windows 安装：下载 Setup.exe（未签名，SmartScreen 要「更多信息 → 仍要运行」）；或 `git clone` 后 backend/frontend 各 `npm install`、`npm run dev`（前端 3013，后端 5679）；或 Docker 镜像 `huobao/huobao-drama:4.0.6`。
- 流程：小说/一句话 → AI 改写剧本（分集）→ 提取角色/场景/道具 → 生成参考图 → 分镜拆解 + 视频提示词 → 批量生视频 → FFmpeg 合成导出。支持 9:16 竖屏。
- 外部服务（README 原表）：文字 OpenAI（兼容 API）、Gemini；图片 OpenAI、Gemini、火山引擎；视频 火山 Seedance 2.0、MiniMax H3、阿里百炼 Wan 3.0。**全部是云端付费 API**。README 首屏推广自家中转 API key（api.firemux.com，付费）。
- 免费/本地替换：文字走「OpenAI 兼容」→ 理论上可接 Ollama 的 `http://localhost:11434/v1`（**未验证**，README 没写）。图片、视频 README 没有 ComfyUI/本地选项 → **不能完全免费跑**。
- GPU：本身不需要（全部云端）。
- 隐私：API key 存在本地 SQLite（`ai_service_configs` 表）；剧本、参考图会发到所选云端供应商。Seedance 引用本地素材需要 `PUBLIC_BASE_URL` 公网地址（会把素材暴露到公网）。
- 给 AI 代理的文字：仓库根有 `CLAUDE.md`（https://github.com/chatfire-AI/huobao-drama/blob/master/CLAUDE.md），内容是给贡献者的代码结构和命令说明（如 `npm run dev`、`configs/config.yaml 是死配置`），**没有**要求代理执行操作或越权的内容；只当资料，不照做。另有 `backend/workspace/skills/` 是它自己 Mastra agent 的 SKILL.md。

## 2. Toonflow（Toonflow-app）

- 仓库：https://github.com/HBAI-Ltd/Toonflow-app （18.9k star，创建 2026-01-29，最后 push 2026-10-20，open issues 3）。镜像：Gitee、AtomGit。
- 最新 release：v2.0.7（2026-10-20），`toonflow-2.0.7-Setup.exe` 约 48 MB。https://github.com/HBAI-Ltd/Toonflow-app/releases
- **许可：MIT**（LICENSE 正文 "MIT License, Copyright (c) 2026 HBAI-Ltd"）。README「不追溯条款」：v1.0.8 前按 AGPL-3.0，v1.0.8~v1.1.8 按 Apache-2.0 + 附加协议；当前版本 MIT、去掉商业附加条款 → 可商用（老版本不行，要用新版）。
- 技术栈：Bun 1.3.14 + Vue 3 + TypeScript，桌面壳 Electrobun；Windows/macOS/Android ARM64 客户端；Docker（`docker compose up -d --build`，端口 3000）。
- Windows 安装：下载 Setup.exe（会自动装 WebView2）。
- 功能：无限画布写剧本与分镜、角色/场景/道具资产、角色三视图、3D 导演台预演、多参考素材视频生成、Agent、MCP、插件市场、21 种界面语言。
- 外部服务：README「自由接入模型 — 配置第三方 API，也可接入本地 ComfyUI 和 LLM」；FAQ：「第三方模型服务的 API 调用可能收费；使用本地模型或 ComfyUI 时，需要自行准备…算力」。接入 ComfyUI 是「通过自定义供应商适配」，具体步骤在飞书文档（未读，**未验证**难度）。
- README 示例成本：2 分钟成片约 ¥130（Seedance 2.0 视频约 ¥120 + GPT Image 2 + Claude Opus 4.6）——这就是用付费模型的真实花费量级。
- 推广：赞助商（秘塔 MiniMax H3、APIMart、优云智算）和自营中转 TF-Router（api.toonflow.net，付费；其源码开源 https://github.com/HBAI-Ltd/TF-Router）。插件市场也在 api.toonflow.net。
- GPU：本身不需要；接本地 ComfyUI 时看模型。
- 安全/隐私：README 4.4「业务页面与 API **没有独立登录鉴权**」，服务器部署必须用防火墙或 SSH 隧道，不要把 3000 端口开到公网。README 里 macOS 的 `sudo spctl --master-disable` 是放宽整机安全的「最后手段」——不要建议用户照做（也是修改系统安全设置）。
- 给 AI 代理的文字：根目录 `AGENTS.md`（https://github.com/HBAI-Ltd/Toonflow-app/blob/master/AGENTS.md），是给贡献者的代码规范（小驼峰命名、禁止新增测试文件、文件操作统一入口等），**没有**针对用户代理的指令；只当资料。

## 3. Pixelle-Video

- 仓库：https://github.com/ATH-MaaS/Pixelle-Video （29.3k star，创建 2025-11-07，最后 push 2026-06-14，open issues 169）。README 里的链接仍指向旧组织 AIDC-AI（NOTICE：Copyright (C) 2025 AIDC-AI）。**4 个月没有 push，issue 多**，维护活跃度比另外两个低。
- 最新 release：v0.1.15（2026-01-27），`Pixelle-Video-v0.1.15-win64.zip` 约 399 MB（Windows 一键整合包，内含 Python/ffmpeg，解压后 `start.bat`，打开 http://localhost:8501）。
- **许可：Apache-2.0**（LICENSE + NOTICE 列出第三方依赖许可）→ 可商用，保留版权和 NOTICE。
- 定位：「输入一个主题」→ 文案 → 每句配图/视频 → TTS 配音 → BGM → 模板合成。偏解说/知识类短视频，**不是**多角色剧情短剧（没有角色资产管理/分镜编辑）。另有数字人口播、图生视频、动作迁移模块。
- 外部服务：LLM 支持 GPT、通义千问、DeepSeek、**Ollama**；图像/视频/TTS 走 ComfyUI 工作流（本地 selfhost 或 RunningHub 云端，付费）或直连 API（OpenAI、DashScope Wan、火山 Seedream/Seedance、可灵，都付费）。
- 免费方案（README FAQ 原话）：「完全免费方案: LLM 使用 Ollama（本地运行）+ ComfyUI 本地部署 = 0 元」。
- 本地工作流（workflows/selfhost）：image_flux、image_qwen、image_nano_banana（Nano Banana 是 Google 付费 API）、tts_edge、tts_index2、video_wan2.1_fusionx、analyse_image/video。注意 image_flux 默认用 FLUX —— FLUX.1 dev 是非商用许可（见 ai-archviz-render models-and-licenses.md），商用换 Qwen-Image。
- TTS：Edge-TTS 免费但调用微软在线朗读服务（要联网，非官方用途，商用合规**未验证**）；Index-TTS 本地、可声音克隆 —— 克隆他人声音要本人同意。
- GPU（docs/zh/getting-started/installation.md）：「如需本地运行 ComfyUI，建议配备 NVIDIA 显卡（6GB+ 显存）」。视频模型（Wan）实际要更多显存，见 ai-archviz-render。
- 隐私：「打印模型请求参数」会把 prompt 和文件路径打到终端；用云端服务时内容会上传。
- 给 AI 代理的文字：README 和 docs 没有发现针对 AI 代理的指令。

## 4. 本地免费组件（交给 ai-archviz-render）

- ComfyUI：GPL-3.0，生成的图片不受 GPL 约束。安装与模型下载交给 `ai-archviz-render`（references/comfyui-setup.md）。
- Wan2.2 TI2V-5B：Apache-2.0，ComfyUI 文档称约 8 GB 显存可跑；Wan2.2 14B（I2V/FLF2V）显存需求高（见 ai-archviz-render references/consistency-and-video.md）。
- 商用安全的图像模型：Qwen-Image（Apache-2.0）、SDXL（Open RAIL++-M）；FLUX.1 dev 非商用。
- HunyuanVideo 许可排除欧盟、英国、韩国。

## 5. 短剧制作要点

- 竖屏 9:16（1080×1920）是主流；集长说法不一：1–2 分钟、1–3 分钟、2–3 分钟；中国监管口径「几十秒到约 15 分钟」。https://en.wikipedia.org/wiki/Microdrama ， https://filmthreat.com/features/what-are-the-characteristics-of-vertical-micro-dramas-key-insights-on-length-and-format/ ， https://www.finaldraft.com/blog/what-are-verticals-and-micro-dramas
- 开头钩子：写作指南强调「前五秒最重要」，每集要有自己的起承转合和结尾悬念（https://www.inktip.com/article_single.php?a_id=259）；「3 秒钩子」多来自工具厂商营销文，当经验值。
- 付费模式：前几集免费，之后付费/看广告解锁；卡点设在最想看下去的悬念处（https://ppc.land/microdrama/ ，二手资料）。
- 镜头表：剧本和生成之间加一张 shot list（构图、动作、台词、时长）；为静音播放写字幕（厂商资料，经验值）。
- 角色一致性：每个角色一张参考设定图（正/侧/背三视图 + 表情），每个镜头都带参考图；本地可用 IP-Adapter / 角色 LoRA（训练 LoRA 用的图要有权利）。Toonflow「角色三视图」、火宝「参考图注入视频生成」都是这个思路。
- 中国国内：2024 年起微短剧分类分层审核，未经审核备案的不得上网传播（https://www.thepaper.cn/newsDetail_forward_26517473 、https://www.peopleapp.com/column/30047779058-500006006362 ，新闻报道，具体条文未逐字核对）。

## 6. 平台 AI 标识规则

- 中国：《人工智能生成合成内容标识办法》2025-09-01 施行（网信办等四部门），显式标识（文字/声音/图形，用户能看到）+ 隐式标识（元数据）；禁止删除、篡改、伪造、隐匿标识。https://www.xinhuanet.com/tech/20250909/fb164c6d092146aa8e13ddc283fe416a/c.html ， https://www.cls.cn/detail/2133981
- 抖音：发布时可在设置里主动声明 AI 生成；未声明的疑似 AI 内容平台会加「疑似使用AI生成技术」标识；第三方 AIGC 工具生成的内容需主动声明；不得删除平台标识。（财联社/IT之家报道，抖音原文未读到，**部分未验证**）https://www.cls.cn/detail/1344887 ， https://www.ithome.com/0/879/586.htm ， https://www.chinalawtranslate.com/抖音关于人工智能生成内容标识的水印与元数据规/
- TikTok：社区准则「Integrity and Authenticity」（页面显示 2026-09-24 生效）——描绘真实场景或真人的 AI 生成或大幅修改内容必须打标签；未标的可能被删除、限流或由平台加标签；有标签也不允许误导公共事务或伤害个人的内容；无新意的搬运内容不进 For You。https://www.tiktok.com/community-guidelines/en/integrity-authenticity
- YouTube（含 Shorts）：上传时 Studio「AI use」选是；必须披露：看起来真实的、让真人说没说过的话、改动真实事件/地点、生成没发生过的真实场景、AI 音乐为主。不用披露：明显不真实/动画、美颜调色、字幕、AI 帮写剧本/标题/缩略图。动画/非写实内容的标签在描述里。重复不披露可能被强制加标签、删除或移出 YPP；披露本身不影响推荐和变现。https://support.google.com/youtube/answer/14328491 。帮助页没有单独讲 Shorts。
- YouTube 变现：2025-07-15 起 YPP「inauthentic content」（原 repetitious content）——大量生产、重复的内容不能变现（报道，https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/ ）。→「一句话批量出片赚钱」正好撞这条。

## 7. 生成内容的版权

- 美国版权局 AI 报告第 2 部分（2025-01-29）：只靠提示词不足以构成作者身份；人类对输出做出足够的表达性选择、编排、修改的部分可以受保护，个案判断。https://copyright.gov/newsnet/2025/1060.html
- 中国：北京互联网法院 2023 年「AI 文生图」案（李某诉刘某）认定原告对经过大量提示词和参数调整的 AI 图片享有著作权（据公开报道，判决原文未在本次核对，**未验证**细节）。
- 结论：剧本、分镜、剪辑、配音这些人做的部分是版权的主要来源；改编别人的小说要有授权（「小说转短剧」最大的版权风险是原著，不是 AI）。

## 给 AI 代理的 README 文字汇总

- huobao-drama `CLAUDE.md`：贡献者开发指南，无越权指令。
- Toonflow-app `AGENTS.md`：贡献者代码规范，无越权指令。
- Pixelle-Video：未发现。
- 三个 README 都有推广付费中转/赞助商 API 的内容（firemux、TF-Router、秘塔、APIMart、优云智算、RunningHub）——视为广告，不照做、不推荐。
