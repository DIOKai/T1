# 研究笔记 F：ai-archviz-render 和 canva-to-web

调查日期：2026-10-22。每条事实后面附来源网址。标「未验证」的没有在官方页面上确认。标「经验」的是业界常见做法，不是官方规定。
重要前提：Claude 自己不能生成图片或视频。所有出图都由用户电脑上的 ComfyUI（免费）或用户自己选的付费服务完成，Claude 只负责写脚本、准备 Blender 通道、组 workflow JSON、调用本机 API。

---

## A. ai-archviz-render

### A1. 免费本地路线：ComfyUI

**授权和安装**
- ComfyUI 是 GPL-3.0 授权。https://github.com/comfyanonymous/ComfyUI
- Windows 有三种装法：官方推荐新手用的 Desktop app（Windows/macOS）、Windows 便携版（portable，README 写它"not recommended for regular users"）、`pip install comfy-cli` 然后 `comfy install`、手动 git clone。来源同上。
- 便携版的文件：RTX（20 系以上）用 `ComfyUI_windows_portable_nvidia.7z`；10 系和更旧的用 `ComfyUI_windows_portable_nvidia_cu126.7z`；另有 AMD、Intel 和 ARM64 版本。用 7-Zip 解压，双击 `run_nvidia_gpu.bat`，控制台出现 `http://127.0.0.1:8188` 就是启动好了。关掉命令窗口 ComfyUI 就会停。https://docs.comfy.org/installation/comfyui_portable_windows
- 模型放在别处：把 `extra_model_paths.yaml.example` 复制一份改名成 `extra_model_paths.yaml`，在里面设 `base_path` 和 checkpoints/loras/vae/controlnet 子文件夹。便携版装 Python 包要用 `.\python_embeded\python.exe -m pip install <pkg>`。来源同上。
- README 说最低可以在"as low as 4GB vram + 8GB ram"上跑（要看模型大小）。手动安装时，NVIDIA 20 系以上要用 cu130 或更新版本的 PyTorch。https://github.com/comfyanonymous/ComfyUI

**本机 HTTP API（让脚本驱动 ComfyUI）**
- 默认地址是 `http://127.0.0.1:8188`。官方示例 `script_examples/basic_api_example.py` 用 `POST /prompt` 发送 `{"prompt": <API 格式 workflow>}`。workflow 要先在界面里用「File → Export (API)」导出成 API 格式。https://github.com/comfyanonymous/ComfyUI/blob/master/script_examples/basic_api_example.py
- 路由：`POST /prompt` 把 workflow 加入队列，成功时返回 `prompt_id` 和 `number`，失败时返回 `error`/`node_errors`；`GET /history`（可以用 `/history/{prompt_id}`）取结果；`GET /view` 下载输出图；`POST /upload/image` 上传 Blender 通道图；`/ws` WebSocket 推送 `status`/`executing`/`progress`/`executed` 事件；`GET/POST /queue`；`GET /object_info` 列出所有节点的输入格式。https://docs.comfy.org/development/comfyui-server/comms_routes
- 流程建议：先 `/upload/image` 上传 depth、lineart 和 mask，再改 workflow JSON 里 LoadImage 节点的文件名、seed 和 prompt，然后 `POST /prompt`，用 WS 或轮询 `/history/{id}` 等结果，最后用 `/view?filename=…&type=output` 下载。（根据上面两个官方来源整理；`/history/{id}` 的路径格式是常用写法，未验证）

### A2. 开源图像模型和授权（是否可以商用）

| 模型 | 授权 | 可以商用吗 | 来源 |
|---|---|---|---|
| FLUX.1 [dev] | FLUX.1 [dev] Non-Commercial License | **模型本身不能商用**。Non-Commercial Purpose 排除了"revenue-generating activity"和"impact on end users"。但第 2(d) 条写着 Output "may use … for any purpose (including for commercial purposes)"。另外禁止用输出去训练竞争模型。结论：在付费工作里跑模型属于商用，有风险，要买 BFL 商用授权，或改用 schnell/Qwen | https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/LICENSE.md |
| FLUX.1 [schnell] | Apache-2.0 | 可以 | https://huggingface.co/black-forest-labs/FLUX.1-schnell |
| FLUX.1 Kontext [dev]（编辑和一致性） | 非商用（几个来源写的授权名称不一致，未验证）；商用授权要通过 BFL portal 购买 | 不行（除非买授权） | https://rits.shanghai.nyu.edu/ai/flux-1-kontext-dev-released-open-weights-model-for-advanced-image-editing/ ；ComfyUI 原生支持：https://blog.comfy.org/p/flux1-kontext-dev-day-0-support |
| FLUX.1 Depth/Canny [dev] | 未验证（推测和 dev 一样是非商用） | 未验证 | — |
| SDXL base 1.0 | CreativeML Open RAIL++-M | 可以（免费、royalty-free；"Licensor claims no rights in the Output"），但要遵守附件 A 的使用限制。注意：model card 的 Direct Use 写着"intended for research purposes only"，和授权条款不一致，以授权为准 | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/LICENSE.md |
| Qwen-Image（20B） | Apache 2.0 | 可以。文字渲染强（特别是中文），也支持编辑。model card 没写 VRAM 需求 | https://huggingface.co/Qwen/Qwen-Image |
| HiDream-I1 | Transformer 是 MIT；VAE 来自 FLUX schnell；文字编码器 Llama-3.1-8B-Instruct 走 Llama 3.1 Community License，T5 是 Apache 2.0 | model card 自称"Commercial-Friendly"。商用前要另外看 Llama 3.1 的条款 | https://huggingface.co/HiDream-ai/HiDream-I1-Full |

**ControlNet 和条件控制**
- xinsir `controlnet-union-sdxl-1.0`：Apache-2.0，一个模型支持 Openpose、Depth、Canny、Lineart、AnimeLineart、Mlsd、Scribble、Hed、Softedge、Teed、Segment、Normal；ProMax 版另外加了 tile、inpaint、outpaint。archviz 最好用 Depth、Lineart/Mlsd（直线）、Normal、Segment。https://huggingface.co/xinsir/controlnet-union-sdxl-1.0
- InstantX Qwen-Image ControlNet Union：一个模型包含 canny、soft edge、depth、pose，建议 conditioning scale 0.8–1.0。ComfyUI 有官方 workflow 模板，权重文件是 `Qwen-Image-InstantX-ControlNet-Union.safetensors`。https://huggingface.co/InstantX/Qwen-Image-ControlNet-Union ；https://comfy.org/p/supported-models/qwen-image-instantx-controlnet-union （授权名称未在页面确认，未验证）
- 另外有 DiffSynth 的 Qwen-Image union LoRA（canny/depth/lineart/softedge/normal/openpose），来源是个人 wiki，未验证。

**IP-Adapter / 参考图**
- ComfyUI_IPAdapter_plus 有 SDXL 版（如 `ip-adapter-plus_sdxl_vit-h.safetensors`），可以分开控制 style 和 composition，也有"precise" style transfer。README 建议参考图太强时把 CFG 降到 3–4 或用 RescaleCFG。授权未验证。https://gitee.com/Anstarc/ComfyUI_IPAdapter_plus （GitHub 原仓库的镜像）
- FLUX Redux：这次没有查到资料，未验证。

### A3. 开源图生视频模型

| 模型 | 授权 | VRAM | 备注 | 来源 |
|---|---|---|---|---|
| Wan2.2 TI2V-5B | Apache 2.0 | 官方命令要 24 GB（如 4090），会用 `--offload_model True --convert_model_dtype --t5_cpu`；ComfyUI 文档说用原生 offloading 可以"fit well on 8GB vram" | 720P、24 fps，1280×704 | https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B ；https://docs.comfy.org/tutorials/video/wan/wan2_2 |
| Wan2.2 I2V-A14B | Apache 2.0（ComfyUI 文档写着"support commercial use"） | 官方是 80 GB 级；ComfyUI 用 fp8 版和 offload 可以跑，但页面没写具体数字 | 需要 high noise 和 low noise 两个模型；还有 FLF2V（首尾帧，很适合建筑镜头） | 同上；https://computingforgeeks.com/run-wan-video-generation-locally/ （第三方：4090 在 decode 阶段 OOM） |
| LTX-Video 0.9.8（13B/2B） | "other"，LTXV Open Weights License。旧版 2025-04 的 LTXV 授权写着年收入 ≥ $10M 的公司要买付费授权 | 没写具体 GB；2B distilled 适合低 VRAM | 支持图生视频 | https://huggingface.co/Lightricks/LTX-Video ；https://open.windriver.com/info/uni-license-list/licenses/ltxv-owl-2025-04-17.html |
| LTX-2 / LTX-2.3 | LTX-2 Community License（2026-01-05 的 0.X 版）；$10M 门槛只在第三方来源看到，**未验证**；拿来做和 Lightricks 竞争的产品要另外买授权 | 没写；有 fp8/fp4 版本 | 可以同时生成画面和声音；ComfyUI 内建 LTXVideo 节点 | https://huggingface.co/Lightricks/LTX-2 ；https://static.lightricks.com/legal/ltx-2-open-weights-license-0.X.pdf |
| HunyuanVideo-I2V | Tencent Hunyuan Community License。**Territory 不包括欧盟、英国、韩国**；在那些地区用输出也没有授权；月活超过 1 亿要另外申请；禁止用输出改进其他模型 | 720p 最少 60 GB，建议 80 GB | 最多 129 帧（约 5 秒） | https://huggingface.co/tencent/HunyuanVideo-I2V ；https://huggingface.co/tencent/HunyuanVideo-I2V/blob/main/LICENSE |

→ 消费级显卡、免费又可以商用的首选：**Wan2.2 TI2V-5B（ComfyUI）**；显存够的话用 Wan2.2 I2V/FLF2V 14B fp8。Hunyuan 不适合用户在授权排除地区的情况，而且显存需求太高。

### A4. 从 Blender 导出通道（Blender 5.x）

- ViewLayer 的属性：`use_pass_z`、`use_pass_mist`、`use_pass_normal`、`use_pass_object_index`、`use_pass_material_index`、`use_pass_cryptomatte_object`/`_material`/`_asset`/`_accurate`、`use_pass_position`、`use_pass_diffuse_color` 等，Freestyle 用 `view_layer.use_freestyle`（也要打开 `scene.render.use_freestyle`，后者未在这一页确认）。文档版本是 5.2。https://docs.blender.org/api/current/bpy.types.ViewLayer.html
- Depth（旧名 Z）是相机到最近表面的距离，**不是 0–1**；Depth、Position、Object/Material Index **都没有抗锯齿**。开了景深或运动模糊时 Depth 会有噪点，这时改用 Mist。Mist 已经映射到 0–1，Start/Depth/Falloff 在 World 设置里。Normal 是世界空间法线。Cryptomatte 比 Index 好用（可以处理一个像素里有多个物体、透明、运动模糊）。https://docs.blender.org/manual/en/latest/render/layers/passes.html
- **Blender 5.0 合成器 API 的重大变化**（旧脚本会坏掉）：`scene.node_tree` 已经删除，改用 `scene.compositing_node_group`。新建方法是 `bpy.data.node_groups.new("…","CompositorNodeTree")`，然后指定给 `scene.compositing_node_group`。`scene.use_nodes` 已经废弃（永远是 True）。File Output 节点删掉了 `base_path`/`file_slots`/`layer_slots`，改成 `directory`、`file_name`、`file_output_items`（旧的 `file_slots[0].path` 改成 `file_output_items[0].name`）。Composite 节点被 Group Output 取代。通道名称改了：`Z` 改成 `Depth`，`IndexMA` 改成 `Material Index`，`DiffCol` 改成 `Diffuse Color`。File Output 只有渲染动画时才会在文件名加帧号。https://developer.blender.org/docs/release_notes/5.0/python_api/ ；https://developer.blender.org/docs/release_notes/5.0/compositor/
- 给 ControlNet 用的转换（经验）：Depth 用 Normalize 节点，或者直接用 Mist，再**反相成近白远黑**（大部分 depth ControlNet 用的是 MiDaS/Depth-Anything 那种"近亮"的格式，未验证是不是每个模型都一样），存成 16-bit PNG；Normal 要从世界空间转成相机空间并映射到 0–1，ControlNet normal 一般要 OpenGL/相机空间（未验证）；Freestyle 线稿配白底黑线或反相成黑底白线（xinsir lineart 用的是黑底白线，未验证）；Cryptomatte 或 Object Index 拿来做 inpaint mask，分区域重绘（玻璃、植栽、天空）。
- 另一个做法：用 ComfyUI 的预处理器（Depth-Anything、Canny、MLSD）直接处理 clay render。缺点是精度比 Blender 原生通道差（经验）。

### A5. 一致性，以及 AI 做不好的地方

- 固定 seed、固定 prompt、同一张参考图（IP-Adapter style），ControlNet strength 拉高（0.8–1.0），可以让多个角度风格一致（经验 + InstantX card 的 strength 建议）。
- 视频：用 Wan2.2 **FLF2V（首帧 + 尾帧）**，两张都用同一套 seed 和 ControlNet 先出静帧，再让模型补中间，比单纯 I2V 稳定（经验，模型功能见 ComfyUI Wan2.2 文档）。也可以先在 Blender 做好相机动画，每隔 N 帧用 ControlNet 出关键帧再补中间（经验，未验证效果）。
- AI 做不好的：会改动几何（多开窗、栏杆变形、柱子数目改变）、招牌文字和门牌乱码（Qwen-Image 文字渲染比较强，是例外：https://huggingface.co/Qwen/Qwen-Image ）、品牌 logo 会被改掉、视频里建筑会"呼吸"或闪烁、比例和透视会漂移。对策（经验）：几何靠 ControlNet 锁定，文字和 logo 在后期用 Blender 原图或合成叠回去，不要让 AI 画；交付前拿 AI 图和 clay 图叠图对照检查。
- FLUX Kontext 和 Qwen-Image 编辑适合"只改材质或天气、不动结构"的局部修改（BFL 自己宣称的一致性，未经独立验证）。

### A6. 付费路线（只记录，用之前要先问用户）

| 服务 | 价格（2026-10 查） | 来源 / 可靠度 |
|---|---|---|
| OpenAI GPT Image（API，每 1M token） | gpt-image-2：图片输入 $8、图片输出 $30；gpt-image-1.5：$8/$32；gpt-image-1：$10/$40；gpt-image-1-mini：$2.50/$8；Batch 半价（gpt-image-2 输出 $15）。按张算的价格要用官方计算器 | https://developers.openai.com/api/docs/pricing （官方） |
| Higgsfield（Seedance、Kling 等聚合平台） | 第三方：Starter 约 $19/月（年付）、270 credits；Plus $47 年付或 $59 月付、1,200 credits；Ultra $99 年付或 $129 月付、3,000 credits；Free 不能商用；credits 不累积。官方定价页抓不到内容，**未验证** | https://creatify.ai/blog/higgsfield-pricing-(2026)-plans-and-what-you-ll-actually-pay ；https://lumalabs.ai/news/higgsfield-pricing ；官方 https://higgsfield.ai/pricing |
| ByteDance Seedance 官方 | BytePlus ModelArk 按 token 计费；第三方说 Seedance 2.5 约 $10.70/M token（480p/720p），5 秒 1080p 约 $2.84；Dreamina 是网页 UI、没有 API。**未验证** | https://www.developersdigest.tech/models/video-generation/byteplus ；https://www.byteplus.com/en/topic/578667 |
| Runway | Free $0（125 一次性 credits）；Standard $15/月（年付 $12）625 credits；Pro $35（年付 $28）2,250；Max $95（年付 $76）9,500 | https://runway.com/pricing （官方） |
| Kling | 第三方：Standard $10/月 660 credits、Pro $37/月 3,000、Premier $92/月 8,000、Ultra $180/月 26,000；免费的每日 credits 说法互相矛盾。**未验证** | https://www.eesel.ai/en/blog/kling-ai-pricing ；https://www.aiarty.com/ai-video-generator/kling-ai-pricing.htm |
| Krea | Free（每天 100 compute units、不能商用、Seedance 要付费方案）；Basic $9/月（年付 $5）；Pro $35（年付 $21）；Max $105（年付 $63）；Business $200（年付 $160）。有实时生成、Enhancer，影片可选 Kling/Runway/Veo/Wan/Seedance | https://www.krea.ai/pricing （官方，页面数据有矛盾：Max 有一处写 $70/40k） |

注：参考影片里的"GPT Images for reference images"＝用 OpenAI 付费 API 或 ChatGPT 生参考图；免费的替代方案是本机 Qwen-Image 或 SDXL。

---

## B. canva-to-web

### B1. Canva MCP（官方远端服务器）

- 官方说明：Canva MCP 是远端 MCP 服务器，功能有生成设计、编辑设计、搜索和读取设计/页面/文件夹、素材和品牌管理、导出（PDF、PNG、JPG、PPTX、MP4 等）、留言。适用 Canva Developer Terms、usage policy、prohibited use。https://www.canva.dev/docs/mcp/
- Claude Code 接法（第三方整理）：`claude mcp add --transport http canva https://mcp.canva.com/mcp`，第一次用时浏览器会跳出 OAuth 登录。https://glama.ai/mcp/servers/yfloby6xwt （本机已经装了 `plugin:canva:canva`，目前显示还没授权，要用户自己跑 `/mcp` 登录）
- 工具和方案限制（官方 tools 页）：所有方案都能用 `search-designs`、`get-design`、`get-design-pages`、`get-design-content`、`get-design-thumbnail`、`get-export-formats`、`export-design`（20 次/分钟，画质依方案而定）、`get-assets`、`generate-image`、`remove-background`、`separate-image-layers`、编辑 transaction 等。**只有 Pro 以上能用**：`get-design-dataset`、`autofill-design`、`get-brand-template-dataset`、`search-brand-templates`、`list-brand-kits`、`create-design-from-brand-template`、`create-brand-template-draft`、`publish-brand-template`、`resize-design`（Free 有限量试用）。全服务器默认上限 300 次/分钟/用户。https://www.canva.dev/docs/mcp/tools/
- 本机连接器实际看到的 schema（2026-10-22）：`read-design` 可以读文字、页数、metadata、**页面缩略图**、演讲者备注；开 editing transaction 后可以读结构化的 element 数据。`export-design` 的 `type` 只能是 `pdf|png|jpg|gif|pptx|mp4|csv`（**没有 SVG，也没有 HTML**），PNG/JPG 可以设宽高（40–25000 px）、`as_single_image`、`transparent_background`、`export_quality: regular|pro`，会返回下载网址。`get-design-dataset` 说明它是查设计"能不能 autofill"的栏位，**不是**拿来读菜单内容的。→ 读菜单内容用 `read-design`（文字）加 `export-design` PNG（视觉参考或切图）。
- Connect API 本身支持更多格式：`html_bundle`、`html_standalone`，而 SVG 导出"currently unavailable"。Free 方案的限制：不能导出 lossy PNG、透明背景、`export_quality: pro`（设计里有没买的付费元素也会失败）；固定尺寸设计放大不能超过 1.125 倍。https://www.canva.dev/docs/connect/api-reference/exports/create-design-export-job/ （MCP 的 export-design 有没有开放 HTML，以本机 schema 为准：没有）
- Free 账号可以用核心功能：官方 tools 页把大部分工具标成"All"，就是证据。Access/permissions 页面 404，所以企业管理员开关等细节未验证。
- Canva Code 2.0（2026-07）开放给免费用户，可以从 prompt 生成前端网站或互动体验，也能导入 HTML 变成可编辑的设计；**能不能导出 HTML 代码未验证**（只有讲 2025 旧版的二手部落格这样说）。https://www.khaleejtimes.com/business/tech/canva-code-20-explained-how-the-new-ai-tool-builds-websites-and-apps ；https://www.edtechinnovationhub.com/news/canva-opens-code-20-to-free-users-with-editable-ai-built-websites-and-apps

### B2. 导出的设计放到网站上：授权注意事项（Canva Content License Agreement）

- Pro Content 用在网页上，每个未编辑的文件最多 **480,000 像素**（例如 600×800）。用 Canva 自己的网站发布或嵌入 Canva 托管的设计就没有这个限制。Free Content 没有像素限制。（第 5A 条）
- 不能把 Content 单独抽出来，做成让别人能下载、导出或取得原档的形式（第 9.8、9.10、9.12 条）。→ 做网站时把菜单插图、照片整合进设计，不要把原素材做成可以下载的单图库（是否构成"standalone"，未验证，属于法律判断）。
- 字体只能在 Canva 里用，或作为导出设计的一部分；**不能转换或抽出字体文件**（第 9A 条）。→ 网站文字要用免费网络字体（Google Fonts 等）重新排版，不要从 Canva 拿字体。
- Content 不能用来当商标或店名标志（第 9.2 条）→ 咖啡店 logo 不能直接用 Canva 素材。
- 设计里混了不同类别的 Content 时，以最严格的类别为准（第 1.3–1.4 条）。https://www.canva.com/policies/content-license-agreement/ ；概要：https://www.canva.com/help/licenses-copyright-commercial-use/
- 这些不是法律意见，建议提醒用户自己读一次授权。

### B3. 手机点餐 demo 网站的做法

- 点击目标尺寸：WCAG 2.2 SC 2.5.8 最少 **24×24 CSS px**（有 spacing、inline 等例外）。https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html 。Apple HIG 建议 44×44 pt（HIG 页面抓不到内容，**未验证**，以记忆为准）。
- `prefers-reduced-motion: reduce`：先写默认动画，后面用同样权重的 selector 覆盖；把缩放、位移换成淡入淡出，而不是只放慢；2020 年起所有浏览器都支持。https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- 滑卡选饮料（经验）：用 pointer events 加 CSS `scroll-snap`，同时提供左右按钮和键盘方向键（滑动不能是唯一操作方式），卡片 `aria-roledescription="slide"`。甜度用 segmented control 或 radiogroup（0/30/50/70/100%），配料用 checkbox 加数量 stepper（`−`/`+` 按钮 ≥ 44px，中间数字 `aria-live="polite"`）。购物车用底部 sheet，数量改变时 badge 弹一下（reduced-motion 时改成颜色变化）。完成订单的动画用 CSS 或 Lottie，时间 < 1.5 s，并附文字确认，在 `role="status"` 区域读出。
- demo 不能接真的付款：GitHub Pages 明文禁止拿来"facilitating commercial transactions"、处理密码和信用卡。https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits

### B4. 免费静态托管

| 服务 | 免费额度 | 来源 |
|---|---|---|
| GitHub Pages | 站点 ≤ 1 GB，软上限每月 100 GB 流量；不能做网店或付款 | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits |
| Cloudflare Pages | 每月 500 次 build，每站 20,000 个文件，单个文件 ≤ 25 MiB，每个项目 100 个自订网域；流量这页没写 | https://developers.cloudflare.com/pages/platform/limits/ |
| Netlify | Free 有 300 credits 上限，流量每 GB 20 credits（大约 15 GB，和其他用量共用）；超出后会怎样页面没写 | https://www.netlify.com/pricing/ |
| Claude Artifact | 单个 HTML 页面可以直接发布分享（本环境的工具，私人连结，免费） | 本机工具说明 |

---

## 未验证 / 待补
- Seedance 在 Higgsfield 每次生成要多少 credits、Higgsfield 官方方案名称和价格（官方页面抓不到内容）。
- Kling 官方定价页（抓到空白）。
- FLUX.1 Depth/Canny [dev]、Kontext [dev] 的授权原文；FLUX Redux。
- LTX-2 授权的 $10M 门槛原文。
- Apple HIG 44pt 原文。
- Canva MCP 的 access/permissions 页面（404）；Canva Code 2.0 能不能导出 HTML。
- ControlNet depth 和 normal 的极性约定（每个模型可能不同，要实际测试）。
