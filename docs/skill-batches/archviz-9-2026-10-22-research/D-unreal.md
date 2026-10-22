# D. Unreal Engine 5 + MCP 做互动 archviz：研究笔记

研究日期：2026-10-22。每条后面附来源 URL；标「未验证」的是没能在一手页面上确认的内容。
说明：unrealengine.com 的 license/FAQ/EULA 页面对抓取返回 403，授权部分只能用 Epic 博客的转述和第三方报道交叉核对，详见第 5 节。

---

## 1. 开源 Unreal MCP 服务器

### 1.0 Epic 官方：Unreal MCP（UE 5.8 内置，Experimental）
- 来源：https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-mcp-in-unreal-editor
- 状态：**Experimental**，API 和数据格式可能随时改，很多功能还不完整。
- 启用：Edit > Plugins 打开 **Unreal MCP**（内部名 `ModelContextProtocol`）和 **All Toolsets**（Toolset Registry 会自动启用），重启编辑器。Terminal 插件是可选的。
- 设置（Editor Preferences > General > Model Context Protocol）：Auto Start Server（预设关）、Server Port Number（预设 **8000**）、Server URL Path（预设 `/mcp`）、Enable Tool Search（预设开）。手动启动：控制台 `ModelContextProtocol.StartServer [port]`。
- 传输：只支持 HTTP / SSE，不支持 stdio 和 WebSocket。端点 `http://127.0.0.1:8000/mcp`。
- 接客户端：控制台执行 `ModelContextProtocol.GenerateClientConfig ClaudeCode`（也可 `Codex`、`All`），在项目根目录生成配置。
  - Claude Code：生成 `.mcp.json`，里面是 `unreal-mcp`，`"type": "http"`，指向上面的 URL；从项目根目录启动 `claude`。等效指令（按 Claude Code 通用语法推出，**未验证**是否与生成档完全一致）：`claude mcp add --transport http unreal-mcp http://127.0.0.1:8000/mcp`
  - Codex：生成的是 TOML，而且「只写一次」，已有文件不会覆盖，要手动删旧的。Epic 页面没给具体内容。按 Codex 文档的格式应为（**未验证**与生成档一致）：`codex mcp add unreal-mcp --url http://127.0.0.1:8000/mcp`，或 `~/.codex/config.toml` 里 `[mcp_servers.unreal-mcp]` `url = "http://127.0.0.1:8000/mcp"`。
- 工具：开启 Tool Search 时 `tools/list` 只返回三个元工具 `list_toolsets`、`describe_toolset`、`call_tool`；toolset 例子有 SceneTools、ActorTools、MaterialInstanceTools、ObjectTools；能生成 actor、设灯光、建材质实例、跑自动化测试。可用 Python（`unreal.ToolsetDefinition`）或 C++ 写自定义工具，改完跑 `ModelContextProtocol.RefreshTools`。
- 安全：预设只绑 localhost，拒绝非 loopback 的 Origin；**没有认证**，官方说不能暴露到本机以外。工具在 game thread 串行执行，客户端不要并发调用。
- 实测评价（Puget Systems，2026-07-09，https://www.pugetsystems.com/?p=48127）：灰盒房间、开关灯 Blueprint 做得好；改玩家控制把游戏弄坏、PCG 做不出来；单次回应 5～15+ 分钟。结论：适合加速你已懂的系统，不适合从零设计系统。
- 5.8 发布于 Unreal Fest 2026（Puget 文章）；第三方说 2026 年 6 月（https://www.elephorm.com/formation/maitriser-lintegration-du-mcp-unreal-engine-dans-chatgpt-et-claude-ai/comprendre-larchitecture-mcp-dans-unreal-engine-58 ，未验证）。

### 1.1 UEMCP（PyPI `uemcp`）
- PyPI：https://pypi.org/project/uemcp/ ；仓库：https://github.com/ATDev-Inc/uemcp
- 授权 MIT（© 2026 ATDev）。版本 0.1.0，2026-06-12 发布。GitHub：**0 star**、0 fork、22 commits、1 issue、5 PR（采用度很低，新项目）。
- 支持版本：PyPI 写「vanilla UE 5.0 through 5.6」，GitHub README 写「5.0 through 5.7」——两处不一致。
- 连接：**不用编译 C++ 插件**，走 Unreal 内置 **Python remote execution**：UDP 多播发现 239.0.0.1:6766 + TCP 命令通道。UE 端要开 Python Editor Script Plugin 和项目设置「Enable Remote Execution」。
- Claude Code：先装 uv，然后 `claude mcp add unreal -- uvx uemcp`
- Codex：页面没写。按 Codex 通用语法：`codex mcp add unreal -- uvx uemcp`（**未验证**）。
- 工具（页面一处写 29 个一处写 31 个）：编辑器状态、`ue_python`（执行任意 Python，可用整个 `unreal` 模块）、控制台指令、actor 列表/生成/删除/变换/属性、资产搜索/导入/复制/删除/`ue_save_all`、材质和材质实例、指派材质、Blueprint 和组件、开关关卡、镜头、截图、PIE 开始/停止。
- 安全：remote execution 协议**没有认证**；保持 localhost 预设、多播 TTL 0；等于把编辑器的 Python 控制台交给客户端；工具能改删项目内容，建议用版本控制；可以不开放 `ue_save_all` 作为手动检查点。

### 1.2 ChiR24/Unreal_mcp（现名 EngineWire）
- https://github.com/ChiR24/Unreal_mcp
- MIT；**967 star**、184 fork、dev 分支 2,793 commits；npm 稳定版 0.5.30，0.6 是 beta/pre-release。页面没显示最后提交日期；第三方列表说最后 push 2026-05-06（https://gittrend.io/repo/ChiR24/Unreal_mcp ，未验证）。
- 支持 UE 5.0～5.8；预编译二进制只能用在同一个引擎小版本和平台。
- 连接：**原生 C++ 编辑器插件**（不是 Python、也不是 Remote Control）。
  - Route A：插件内置 Streamable HTTP `http://127.0.0.1:3000/mcp`，不需要 Node。
  - Route B：Node 20.19+ 的 stdio 服务器，经 WebSocket 8090 连插件。
- 安装：把 `EngineWire` 文件夹复制到 `<项目>/Plugins/EngineWire/`，打开项目让 UE 编译（纯 Blueprint 项目可用预编译二进制）；Project Settings > Plugins > EngineWire 勾 Enable Native MCP Server，重启；token 在 `<Project>/Saved/MCP/capability-token`。
  - Claude Code：`claude mcp add --transport http unreal-engine http://127.0.0.1:3000/mcp --header "X-MCP-Capability-Token: <token>"`
  - Route B：`npx -y unreal-engine-mcp-server@beta`，env 设 `UE_PROJECT_PATH`（必须带 `@beta`，否则装到不匹配的 0.5.30）。
  - Codex：页面没写。按 Codex 文档推出（**未验证**）：`config.toml` 里 `[mcp_servers.unreal-engine]` `url = "http://127.0.0.1:3000/mcp"` `http_headers = { "X-MCP-Capability-Token" = "<token>" }`。
- 工具：只暴露一个 MCP 工具 `unreal`（search / describe / execute / configure），背后近 400 项能力、23 个内部工具（manage_asset、manage_blueprint、control_actor、control_editor、manage_level、manage_sequence 等），覆盖关卡、Blueprint/UMG、材质、Niagara、地形、Level Sequence、PIE 截图。
- 安全（最完整）：预设只听 127.0.0.1；每项目 capability token（常数时间比较，删档重启即轮换）；62 项破坏性操作每次调用要单独同意；资产路径限制在 `/Game`、`/Engine`；会串接或退出编辑器的控制台指令被挡。

### 1.3 chongdashu/unreal-mcp
- https://github.com/chongdashu/unreal-mcp
- MIT；2.1k star、350 fork、33 commits，无 release；第三方列表说最后 push 2025-04-22（https://gittrend.io/repo/chongdashu/unreal-mcp ，未验证）。
- UE 5.5+、Python 3.12+；Python FastMCP 服务器经 **TCP 55557** 连 C++ 插件 `UnrealMCP`，要自己用 Visual Studio 编译。
- 自称 **EXPERIMENTAL**，「Production use is not recommended」。README 只写 Claude Desktop / Cursor / Windsurf 的 JSON 配置。
- 工具：actor 增删/变换、Blueprint 类和组件、Blueprint 节点图（事件、函数调用、连线、变量）、视口镜头。
- 安全：页面没提 TCP 连接的认证/加密。看起来已停更，不推荐。

### 1.4 ziggymar/unreal-mcp
- GitHub 链接 https://github.com/ziggymar/unreal-mcp 返回 **404**；mcpservers.org 列表页 403。搜索摘要说它是 Node/TypeScript、专注 UE 5.6/5.8 Blueprint 读写、只需 Launcher 版（来源：搜索摘要引用 https://mcpservers.org/servers/ziggymar/unreal-mcp ，**未验证**）。仓库可能已删或改名，不推荐。

### 1.5 其他找到的
- **runreal/unreal-mcp**：https://github.com/runreal/unreal-mcp — MIT、116 star、24 commits；UE 5.4+ 验证过；走 Python remote execution，无 C++ 插件；`npx -y @runreal/unreal-mcp`（需 Node）；20 个工具（执行 Python、控制台、资产搜索/导出/验证、world outliner、建/改/删 actor、截图、移镜头）。非 Epic 官方；改绑 0.0.0.0 会暴露到局域网。
  - Claude Code（按通用语法，未验证）：`claude mcp add unreal -- npx -y @runreal/unreal-mcp`；Codex：`codex mcp add unreal -- npx -y @runreal/unreal-mcp`（未验证）。
- **unreal-engine-mcp**（PyPI）：https://pypi.org/project/unreal-engine-mcp/ ，仓库 https://github.com/FFZackFair92/unreal-engine-mcp — MIT；0.10.0（2026-07-31）；GitHub 只有 5 star。UE 5.0+（作者测 5.8）。预设走 Python remote execution，可切 `UE_MCP_TRANSPORT=remotecontrol` 用 Remote Control HTTP 30010。162 个工具：建项目、导入 .glb/.gltf/.fbx（glTF 走 Interchange 要 5.2+）、建关卡、摆 actor、材质图、Blueprint、C++ 类和 Live Coding、`RunUAT BuildCookRun` 打包、Poly Haven/ambientCG/Kenney 免费资产下载、截图。**唯一在页面上写明 Codex 配置的**：
  - Claude Code：`pip install unreal-engine-mcp` 后 `claude mcp add unreal-mcp -- python -m unreal_mcp.server`（或用 `uvx unreal-engine-mcp`）
  - Codex：`~/.codex/config.toml` → `[mcp_servers.unreal-mcp]` `command = "python"` `args = ["-m", "unreal_mcp.server"]`（python 要是装了包的那个，不确定就写绝对路径）
  - 安全：只听 127.0.0.1；保持 `bAllowConsoleCommandRemoteExecution`、`bAllowAnyRemoteFunctionCall` 关；`UE_MCP_MULTICAST_TTL` 预设 0，调高等于把任意代码执行暴露到网络；有 PyPI provenance 签名。限制：Blueprint 节点图不能用 Python 写，逻辑要放 C++ 父类。
- **db-lyon/ue-mcp**（npm `ue-mcp`）：README https://cdn.jsdelivr.net/gh/db-lyon/ue-mcp@main/README.md — MIT；Windows UE 5.4～5.8；TS 服务器 stdio + C++ bridge 插件（WebSocket JSON-RPC），需 Node 18+ 和 Visual Studio；`npx ue-mcp init` 会自动部署插件并检测 Claude Code / Codex；29 类工具 2,040+ 动作（5.8 上含 Epic 原生约 830 个）；有写入守卫、版本控制守卫、git 快照。star 数没查到。

### 1.6 Codex 通用配置语法（官方）
- 来源：https://learn.chatgpt.com/docs/extend/mcp?surface=cli （由 developers.openai.com/codex/mcp 308 转址）
- stdio：`codex mcp add <name> --env K=V -- <command>`；HTTP：`codex mcp add <name> --url <url>`
- `config.toml`（`~/.codex/config.toml` 或受信任项目的 `.codex/config.toml`）：stdio 用 `command`/`args`/`[mcp_servers.x.env]`；HTTP 用 `url`、可选 `bearer_token_env_var`、`http_headers`；`startup_timeout_sec`（预设 10）、`tool_timeout_sec`（预设 60）。UE 操作（导入、编译着色器）常超过 60 秒，建议调高（经验值）。

### 1.7 推荐
1. **UE 5.8：用 Epic 官方 Unreal MCP**。免费、不用装第三方代码、Claude Code 和 Codex 都能用 `GenerateClientConfig` 自动生成配置；缺点是 Experimental、没认证（只能本机）。
2. **要更完整的工具 + 更好的安全护栏**：ChiR24 EngineWire（token、破坏性操作逐次同意、路径白名单，星数最多且活跃）；代价是要放 C++ 插件（Blueprint 项目可用预编译二进制，版本要对上）。
3. **UE 5.0～5.7 Launcher 版、不想编译**：走 Python remote execution 的 runreal/unreal-mcp（采用度相对高）或 unreal-engine-mcp（工具最多、写明 Codex 配置，但 star 很少）。UEMCP 只有 0 star、版本说法前后矛盾，暂不首推。
4. 不推荐 chongdashu（自称实验、看似停更、需自己编译、无认证）和 ziggymar（仓库 404）。
- 所有方案都能在编辑器里执行任意 Python/操作：只绑 127.0.0.1、不要开隧道、项目要先进 git/版本控制、第一次用前备份。

---

## 2. Blender 内容进 UE5

- **单位/比例**：UE 用厘米、Blender 用米，差 100 倍。FBX：Blender Unit Scale 保持 1.0 对静态网格通常可行（FBX 元数据处理换算），骨骼网格常用 0.01；导入后 Details 显示 Scale (100,100,100) 而不是 (1,1,1) 就是错了。来源：https://sarahhyperdense.substack.com/p/blender-to-ue5-the-complete-export （2026-02-15，Blender 4.x / UE 5.6，非官方）
- **FBX 导出设置**（同上来源）：Apply Scalings = FBX Units Scale（不要 FBX All）、Apply Unit 开、Forward/Up 保持 -Z / Y、静态网格 Apply Transform 可选、Apply Modifiers 开、Tangent Space 开、Smoothing = Face、Add Leaf Bones 关、Path Mode = Copy + 嵌入贴图。UE 5.4/5.5 的 Interchange 可能重算法线，要看着色有没有问题。Apply Transform 是实验选项，Blender 有已知问题（https://developer.blender.org/T99075）。
- **glTF**：UE 的 Interchange glTF 导入支持多个 KHR_materials 扩展（clearcoat、transmission、sheen、IOR、unlit、specular-glossiness 等）及 KHR_mesh_quantization。来源：https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GLTFCore/GLTF__EExtension 。unreal-engine-mcp 说 glTF/.glb 经 Interchange 导入需要 UE 5.2+（https://pypi.org/project/unreal-engine-mcp/）。glTF 导入时米→厘米是否自动换算：**未验证**（Epic 官方 glTF 导入页 https://dev.epicgames.com/documentation/en-us/unreal-engine/importing-gltf-files-into-unreal-engine 抓到的内容是空的）。经验上 glTF 规范单位是米，导入后应先量一扇门（约 200～210 cm）核对（经验值）。
- **USD**：Blender File > Export > Universal Scene Description（勾 UV、法线、材质），UE 开 USD Importer 插件（要重启），用 USD Stage Editor 先预览再导入。来源：https://jsabbott.artstation.com/blog/PQeVO/tutorial-blender-to-ue5-workflow-using-usd （2025-12，非官方）
- **Datasmith**：Epic 没有官方 Blender Datasmith 导出器；有社区插件（0xafbf，2020 起，https://github.com/0xafbf），2026-01 还有教程在用（https://blog.gitcode.com/0d868825cca103d73499190a98123e25.html）；Epic 论坛「Datasmith for Blender!」需求帖（https://forums.unrealengine.com/tag/datasmith）。官方 3ds Max Datasmith 导出器已支持 UE 5.8（https://www.unrealengine.com/plugins/3ds-max?lang=es-ES）。社区插件对 UE 5.7/5.8 的兼容性：未验证。
- **Epic Send to Unreal（Blender Tools）**：2020 年由 Epic 发布（https://www.cgchannel.com/?p=117307），现有社区维护的 fork（https://github.com/poly-hammer/BlenderTools ，自称与 Epic 无关）。官方仓库是否已归档：未验证。
- **第三方 .blend 直接导入**：Fab 上有「Blender Interchange Content Importer」，自称支持 Blender 3.0～4.3，材质效果等同 glTF/USD/FBX，作者也建议在 UE 里重做材质（https://www.fab.com/listings/c719cc60-e69d-4567-be89-8744c52744a4）。是否付费：未验证。
- **Lightmap UV vs Lumen/Nanite**：用 Lumen 时可以不做 lightmap UV；Nanite 文档说不用 Lightmass 烘焙就关掉 Generate Lightmap UVs，否则导入时间和数据量大增（https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine）。Lumen 下 GI 不能用静态 lightmap（https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine）。
- **材质转换**：只有 Principled BSDF 能可靠带过去（底色、粗糙度、金属度、alpha、IOR、经 Normal Map 节点的法线）；程序纹理、数学/颜色节点、自发光、SSS、clearcoat 不会转，建议烘焙贴图后在 UE 里重建材质（Hyperdense 文章，非官方）。实际做法（经验值）：在 UE 建一个主材质 + 材质实例，换家具材质就是换材质实例，方便网页控制面板切换。
- **为 Lumen 拆网格**：墙、地板、天花板要分开成独立网格；Lumen 不支持把整间房连家具做成一个网格导入；软件光追墙要至少 10 cm 厚以防漏光（Lumen 技术细节页）。这对 Blender 建模直接有要求。

---

## 3. UE5 archviz：Lumen / Nanite / 渲染 / 打包 / Pixel Streaming

### Lumen（https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine）
- 硬件光追（HWRT）：品质较高，追真实三角形；需要 RTX 2000 / RX 6000 或更新。软件光追：SM6 硬件（GTX 1070 以上）可跑，用 Mesh Distance Fields（要在项目设置开 Generate Mesh Distance Fields）。
- 最高品质镜面反射：HWRT + Ray Lighting Mode = Hit Lighting for Reflections，可项目级或 Post Process Volume 单独设。
- 调整：Lumen Scene Detail（小物件在反射里发黑、漏光时调高）、Lumen Scene Quality（室内镜面多次反弹斑点）、Max Trace Distance（漏光）、Final Gather Lighting Update Speed（灯光变化后 GI 更新速度，改完要调回）。
- 限制：墙 ≥10 cm；小自发光网格会被剔除（开 Emissive Light Source）；不支持 Forward Shading、VR；页面没有 archviz 专门建议。
### Nanite（https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine）
- 导入时勾 Build Nanite；已有资产右键 Nanite > Enable。
- 只支持 Opaque、Masked；**不支持半透明**（玻璃窗、玻璃家具不能用 Nanite），也不支持 MSAA、VR 立体、Forward、Lighting Channels、morph target。
- Nanite 静态网格完整支持 Lumen GI/反射和 Virtual Shadow Maps；高面数家具用 Nanite 能加速 Lumen surface cache 捕捉。
- 光追用 Fallback Mesh，降低 Fallback Relative Error 可增加细节。
### 电影级输出
- Movie Render Graph（MRG）：节点式，比 MRQ 更灵活；Temporal Samples 在 Sampling Method 节点（全局），Spatial Samples 在 Renderer 节点（每层）；每层可选 Path Tracer 或 Deferred。MRG 仍缺 nDisplay、High Resolution Rendering、ProRes、FCP XML 等（以文档当前版本为准）。来源：https://dev.epicgames.com/documentation/unreal-engine/transitioning-to-the-movie-render-graph-from-movie-render-queue-in-unreal-engine
- Path Tracer：与 Sequencer、MRQ 整合；室内、高反照率材质渲染更久（https://dev.epicgames.com/documentation/unreal-engine/path-tracer-in-unreal-engine）。一位 archviz 用户报告 HD 一帧约 7 分钟（https://cgarchitect.com/projects/4f54a56d-path-tracing-unreal-engine-5 ，个人经验）。
- MRG 页面本身（movie-render-graph-in-unreal-engine）抓到空内容，「是否已 production ready」**未验证**。
### 打包互动漫游
- First Person 模板 + 打包（Platforms > Windows > Package Project）是常规流程（**未逐页核对 5.8 文档**，属一般知识）。unreal-engine-mcp 提供 `RunUAT BuildCookRun` 打包工具（https://pypi.org/project/unreal-engine-mcp/）。
- 打包版默认关闭 Remote Control，要加启动参数 `-RCWebControlEnable -RCWebInterfaceEnable`（见第 4 节）。
### Pixel Streaming（https://dev.epicgames.com/documentation/en-us/unreal-engine/getting-started-with-pixel-streaming-in-unreal-engine ；概览 https://dev.epicgames.com/documentation/en-us/unreal-engine/pixel-streaming-in-unreal-engine）
- 用 WebRTC 把 UE 画面和声音推到浏览器/手机，前端不用装东西；支持键鼠、触控、手柄、自定义 HTML5 UI。
- 插件：Pixel Streaming 或 **Pixel Streaming 2**（下一代）。
- 启动参数：`-PixelStreamingURL=ws://127.0.0.1:8888`，可加 `-RenderOffScreen`。
- 服务器：GitHub `EpicGamesExt/PixelStreamingInfrastructure`（`git clone --branch UEX.Y`），或执行 `Engine\Plugins\Media\PixelStreaming\Resources\WebServers` 下的 `get_ps_servers`（会联网下载）；在 `SignallingWebServer\platform_scripts\cmd` 跑 `setup.bat`（管理员 PowerShell）、`start_with_stun.bat`；预设端口 80 和 8888；浏览器开 `http://127.0.0.1`。
- 编码要「特定 GPU 硬件」，页面没写 NVENC/AMF 细节（未验证）。Pixel Streaming in Editor 是实验功能。
- 公网部署要自己的服务器/云 GPU（会花钱）；本机/局域网展示免费。

---

## 4. 网页控制面板 ↔ Unreal

### Remote Control API（Beta）
- 概览：https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-for-unreal-engine — 引擎内 Web 服务器处理 HTTP + WebSocket；网页可调用 Blueprint/Python 可调用的函数，读写 Blueprint/Python/Preset 暴露的属性；Remote Control Preset 可不写代码暴露内容，并接到配套网页 app 的控件。
- 快速上手：https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-quick-start-for-unreal-engine — Edit > Plugins > Messaging > **Remote Control API**；HTTP 预设 **30010**（Project Settings > Web Remote Control 可改）；`WebControl.StartServer` / `StopServer` / `EnableServerOnStartup`；预设只绑 127.0.0.1，要给其他设备用就改 DefaultEngine.ini `[HTTPServer.Listeners]` 的 `DefaultBindAddress`，官方警告不要暴露到公网，只用于局域网/VPN。
- WebSocket：https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-websocket-reference-for-unreal-engine — 预设 **30020**（`ws://127.0.0.1:30020`）；消息 `{"MessageName":"http","Parameters":{"Url":...,"Verb":"PUT","Body":{...}}}`；`preset.register` 订阅 Preset 事件（PresetFieldsChanged）。
- HTTP 路由：https://dev.epicgames.com/documentation/en-us/unreal-engine/remote-control-api-http-reference-for-unreal-engine
  - `GET /remote/info`、`PUT /remote/object/call`（objectPath、functionName、parameters、generateTransaction）、`PUT /remote/object/property`（READ_ACCESS / WRITE_ACCESS / WRITE_TRANSACTION_ACCESS）、`/remote/object/describe`、`/remote/search/assets`、`/remote/object/thumbnail`、`/remote/batch`；`/remote/object/event` 是实验（要 `WebControl.EnableExperimentalRoutes = 1`）。
  - 移动家具示例：`PUT /remote/object/call` + `functionName: "SetActorLocation"` + `parameters: {"NewLocation":{"X":100,"Y":0,"Z":30},"bSweep":true}`。缩放用 `SetActorScale3D`、旋转用 `SetActorRotation`（AActor 标准函数，属一般知识）。
- 打包版/-game：「Remote Control is disabled by default in packaged projects or in -game」，启动参数加 `-RCWebControlEnable -RCWebInterfaceEnable`（概览页）。
- 安全设置（URemoteControlSettings，https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/RemoteControlCommon/URemoteControlSettings）：`bRestrictServerAccess` + `AllowedOrigin`（限制来源）、`bEnforcePassphraseForRemoteClients`（非 localhost 要密码，`FRCPassphrase`）、`bEnableRemotePythonExecution`（官方注明可能有漏洞）、远程任意函数调用和控制台指令开关、`bAutoStartWebSocketServer`。预设值页面没列（未验证）。
- 网页 app 端口 30000：**未验证**（官方页没提）。

### 换家具 / 换材质的做法（设计建议，经验值）
- 推荐：在关卡里做一个「家具管理」Blueprint actor（或 Python 函数），暴露 `SwapMesh(slot, meshPath)`、`SetMaterial(slot, materialInstancePath)`、`Move/Scale/Rotate(slot, ...)` 这类 BlueprintCallable 函数；网页用 `PUT /remote/object/call` 调它，或用 Remote Control Preset 暴露。这样网页不用知道每个 actor 的内部路径，打包版也能用（打包版没有编辑器 Python）。
- 直接改：`/remote/object/property` 写 StaticMeshComponent 的 `StaticMesh`、材质用 `SetMaterial` 函数——可行，但 objectPath 很长、关卡变动就失效。
- 编辑器 Python 路线（MCP / `bEnableRemotePythonExecution`）只在编辑器里有效，适合 Claude 布置场景；给客户用的网页控制面板应走 Remote Control 函数调用。
- 网页从另一个 origin（如 `file://` 或 localhost:5173）发请求会遇到 CORS/Origin 限制，要设 `AllowedOrigin`（未实测）。

---

## 5. 授权（License）

- Epic 2024 年公布、至今沿用的规则（Epic 博客 https://www.unrealengine.com/blog/we-are-updating-unreal-engine-twinmotion-and-realitycapture-pricing-in-late-april ，抓取被 403，内容来自搜索摘要和 CGPress 转述 https://cgpress.org/archives/unreal-engine-updates-pricing-for-non-game-industries.html）：
  - 学生、教育者、爱好者，以及**年总营收低于 100 万美元的公司**：免费使用。
  - **年营收超过 100 万美元、不做游戏的公司**：Unreal Subscription，**每席每年 1,850 美元**，用于线性内容（电影、电视、**建筑可视化**、不直接卖给个人用户的沉浸体验）。
  - 游戏开发者：不变——终身总营收超过 100 万美元的部分付 **5% 权利金**；Epic Games Store 营收不计。
  - 截至 2026-09 第三方查证 1,850 美元/席/年没变（https://www.renderahouse.com/blog/twinmotion-pricing ，2026-09-07）。
  - 2026-05-27 起 Unreal Subscription 不再包含 Twinmotion 和 RealityScan（搜索摘要引用 Epic 博客更新，**未在一手页面核对**）。
- 互动应用（给客户的漫游 exe）：
  - 旧 EULA 的权利金例外包括「不可回收的顾问费或委托开发费」（例：建筑师做的漫游模拟）；Epic 员工在论坛说为单一客户做的委托作品，委托费免权利金；客户若之后靠它收费（如订阅、上架商店卖）则要付权利金。来源：https://answers.unrealengine.com/questions/184591/view.html 等（UE4 时代论坛，**需对照现行 EULA**：https://www.unrealengine.com/en-US/eula/unreal ，抓取 403，未验证）。
  - 新规则下「授权给第三方、运行时依赖 Unreal 代码的应用」是否落在席位制之外：搜索摘要说席位制对象须「不做授权给第三方并在运行时依赖 Unreal 代码的应用」，具体条款**未验证**。
- 实务建议：个人/小公司（年营收 < 100 万美元）做 archviz 渲图、视频、给客户的漫游都免费；只有把漫游当产品卖给大众或公司营收超过门槛时才要细看 EULA。正式商用前请用户自己读 unrealengine.com/license 和 EULA。
- 磁盘空间：Epic 没有给官方数字。用户报告：5.8.1 压缩包 39 GB、解压后约 70 GB；Launcher 安装有人报 115 GB；源码编译 160～400 GB。来源：https://forums.unrealengine.com/t/storage-required-to-install-unreal-engine-5-8-1/2740177 、https://forums.unrealengine.com/t/required-disk-space-to-install-ue5-from-source/2742506 。建议预留 **至少 150 GB**（引擎 + 项目 + DerivedDataCache + 打包输出），放 NVMe SSD（经验值）。

---

## 6. 硬件需求

- 官方（标为 5.8 文档，https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine）编辑器推荐：Windows 11、四核 2.5 GHz Intel/AMD、**32 GB RAM**、**8 GB+ VRAM**、DirectX 12 显卡最新驱动；参考工作站用 NVMe SSD（2 TB 系统盘 + 4 TB 数据盘，只是示例）。
- Lumen（GI、反射、MegaLights）：Windows 10 1909.1350+、DX12、项目开 SM6；GPU：**NVIDIA RTX 2000 系列以上 / AMD RX 6000 以上 / Intel Arc A 系列以上**（硬件光追）。软件光追 GTX 1070 起（Lumen 技术页）。
- Nanite / Virtual Shadow Maps：DX12 + SM 6.6 atomics（或 Vulkan VK_KHR_shader_atomic_int64）、SM6 开（新项目预设开）。
- Pixel Streaming 编码需特定 GPU（未细查）。
- MCP 实测单次回应 5～15+ 分钟、耗大量 token（Puget），复杂场景要预期慢。

---

## 7. 给技能作者的要点
- 技能要先判断用户 UE 版本：5.8 → 官方 Unreal MCP；≤5.7 → Python remote execution 类（runreal / unreal-engine-mcp）或 EngineWire。
- 所有 MCP 都等于在编辑器里执行任意代码：只绑 localhost、项目先 git、不开 TTL>0、不开隧道。
- Blender 端：墙/地/天花分开、墙 ≥10 cm、Principled BSDF only、导出前 Apply scale；家具单独导出、轴心放底部中心，便于网页移动/缩放（经验值）。
- 网页控制：给客户用走 Remote Control（HTTP 30010 / WS 30020），打包版加 `-RCWebControlEnable -RCWebInterfaceEnable`；Python 只在编辑器。
- 玻璃不能 Nanite；无 lightmap UV（Lumen）。
- 免费：UE、MCP 服务器、Remote Control、本机 Pixel Streaming 都免费；云端 Pixel Streaming / 云 GPU 要钱（用户不要付费服务，不推荐）。
