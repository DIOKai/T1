# revit-mcp 研究笔记

日期：2026-10-22。用途：给新技能 `revit-mcp` 打底（Claude Code / Codex 通过 MCP 连接用户自己的 Revit；Revit 模型转 three.js 网页、做「每种材质一个颜色」的 colour map 影片）。
标记：每条事实后面附来源；没有一手来源支撑的标 **未验证**；我自己推出来的做法标 **（推论）**。
背景：用户有 Autodesk 会员（Revit 可用）；Autodesk 云端额度 / APS Design Automation 这类另外收费的仍不用。

---

## 1. BIMBridge（reel 里那个）

- **仓库**：https://github.com/kenpro0/bimbridge-mcp 。`gh search repos BIMBridge` 只找到这一个同名 MCP 项目（另一个 bradlittlefield/bimbridge-pages 是无关的看板页）。建于 2026-10-15，最后 push 2026-10-17，5 star，0 fork，1 个 open issue（"Translate the docs to English"）。README 主要是法文，末尾有英文段。来源：GitHub API `repos/kenpro0/bimbridge-mcp`、README。
  - reel 里的「Statue of Liberty 一个 prompt」是否就是这个仓库：README 的示例 prompt 和流程（Claude Desktop/Code 装、经 pyRevit、Revit 里每次改动要批准、读 levels/views）都对得上，但 reel 本身我看不到 → **未验证是同一个**。
- **它是什么**：BIMBridge 自己**不是** MCP 服务器。它是一个安装脚本 + 两个技能 + 法文文档，把 **pyRevit 7 内建的 MCP 服务器**（`pyrevit.exe mcp`）装好、打开、注册到 Claude Desktop / Claude Code / Codex。README 原话（译）：「AI 和 Revit 之间的桥是 pyRevit 官方的 MCP 服务器，BIMBridge 提供一键安装、AI 应用配置、技能和法文文档」。
- **授权**：BIMBridge = MIT（LICENSE 文件 + GitHub API）；底层 pyRevit = GPL-3.0。
- **要求**：Windows 10/11、Revit 2022 或更新、pyRevit 7+（缺了会自动装）。来源：README「Prérequis」。注意 pyRevit 官方文档说 agent runtime 只在 Revit 2024、2025 上验证过，2026 待测（见 §2）→ BIMBridge 写的 2022+ 比 pyRevit 官方验证范围宽，**2022/2023/2026/2027 未验证**。
- **安装方式**（README + INSTALL.md + install.ps1，我读了全文）：
  - A：在 Claude Code 里说「照 INSTALL.md 装 BIMBridge」；B：PowerShell `irm https://raw.githubusercontent.com/kenpro0/bimbridge-mcp/main/install.ps1 | iex`。
  - install.ps1 做的事：找 Revit 2019–2032 安装；找 / 检查 pyRevit 7（`pyrevit configs agent` 输出含 "Agent host"）；没有就从 GitHub releases 下载 `pyRevit_<ver>_signed.exe` 静默安装（`/VERYSILENT`），失败再用 `winget install pyRevit.pyRevit`；Revit 开着时拒绝装；`pyrevit configs agent enable`、`pyrevit configs agent skills enable`；把 `bimbridge`、`mep-review` 两个技能复制到 `%APPDATA%\pyRevit\agent\skills`；Claude Code 有就跑 `pyrevit mcp install claude`；改 `%APPDATA%\Claude\claude_desktop_config.json`（先备份成 `.bimbridge-backup`，只加 `mcpServers.pyrevit = {command: <pyrevit.exe>, args: ["mcp"]}`）；Codex 有 CLI 就 `pyrevit mcp install codex`，没有 CLI 但有 `~/.codex` 就在 `config.toml` 追加 `[mcp_servers.pyrevit] command = '<pyrevit.exe>' args = ["mcp"]`；最后 `pyrevit attached`、`pyrevit agent status`。日志 `%TEMP%\bimbridge-install.log`。
  - INSTALL.md 规则：不要用管理员跑；不要改 agent policy（默认 ask）；不要动其他 MCP。
  - 卸载：同仓库 `uninstall.ps1`（移除技能和 MCP 注册、关 agent host，pyRevit 留着）。
- **安全观察（推论）**：`irm … | iex` 直接执行网络上的脚本，而且会静默装 pyRevit；仓库很新（7 天）、只有一个作者。技能里应建议：**先读 install.ps1、或者干脆不用 BIMBridge，直接装 pyRevit 7 官方安装包再用 pyRevit 自己的 `pyrevit mcp install` 命令**——功能一样（MCP 服务器本来就是 pyRevit 的），少一层第三方脚本。BIMBridge 额外给的只有两个技能（工作方法、MEP 只读审查）和法文文档。
- **BIMBridge 技能的做法**（skills/bimbridge/SKILL.md，可借鉴）：先 `run_query` 看已有 levels / 墙、楼板、屋顶类型和族，不要编类型名；每个阶段一次 `run_modify`，`title` 写清楚（它会显示在 Revit 的批准框和撤销名里）；超过几个元素先 `dry_run=true`；新建的元素 Comments 参数打 `bimbridge:<stage>` 标签，重跑某阶段只删这个标签的元素；每阶段后 `capture_view` 看图；顺序 levels → walls → floors → openings → roofs → materials → views；大工程每批几百个元素；Revit 内部长度单位是英尺（`ft = m / 0.3048`，`m2 = ft2 * 0.09290304`）；拍片时把阶段切小、用 `show_elements` 选中新东西；不要在真项目建议改 `auto`。

## 2. pyRevit 7 Agent Runtime（真正的 MCP 服务器）

- pyRevit v7.0.0（tag `v7.0.0.26278+2233`，2026-10-06 发布，非 prerelease）。仓库 https://github.com/pyrevitlabs/pyRevit ，GPL-3.0，~1965 star，2026-10-21 仍有 push。来源：GitHub releases API、release notes。
- Release notes 原文要点：「agent runtime：任何支持 MCP 的 coding agent（Claude Code、Codex、Cursor、VS Code、OpenCode）都能读写一个开着的 Revit 模型，方式是送 **Python 程序**，不是调用几百个按 API 切分的工具」；**Status: experimental**，host **默认关闭**（`[agent] enabled = false`）。
- **工具**（release notes 表格）：`get_skill`、`list_revit_instances`、`get_context`、`inspect_elements`（最多 50 个元素）、`lookup_revit_api`（从正在跑的 Revit 反射出 API 签名，含 `creation` 工厂方法列表）、`show_elements`（选取 / 缩放 / 临时隔离，不算改模型）、`capture_view`（`export` / `viewport` / `screen` / `3d`）、`run_query`（只读；改了模型会失败并回滚；`workspace` 可放自己的模块；`timeout_s` 默认 300）、`run_modify`（批准后才改；`dry_run=true` 预览后回滚）、`get_run`。另有 `list_skills`（报每个技能来源和 SHA-256）。
- **执行约定**：脚本里有 `doc`、`uidoc`、`app`、`uiapp`、`DB`、`UI`、`inputs`；把结果赋给 `result`（ElementId→int，Element→{id, category, name, class}，XYZ→[x,y,z]）。
- **主机强制的保护**：query 改了模型 → `query_modified_model`；run 期间存档 / 另存 / 同步中心 / 导出文件 / 导出视图会被取消并报 `blocked`；改到另一个打开的文件 → `other_document_modified` 回滚；脚本出错整体回滚；Revit error 级失败报 `revit_failure`；transaction 没关 → `transaction_left_open`；超时在 Python 行之间停（`timeout`，最多 3600 s）；每次批准的改动 = **一个** undo（名字 `Agent: <title>`）。
- **批准模式**：`ask`（默认，Revit 里弹框，改动元素被选中并临时隔离，Keep / Discard）、`readonly`（只能 query 和 dry run，**不是 Python 沙箱**）、`auto`（不弹框，但仍是一个 undo、仍有保护、仍记录）。命令 `pyrevit configs agent policy (readonly | ask | auto)`；也在 Revit **pyRevit → Settings → Agent Runtime (MCP)**。来源：https://docs.pyrevitlabs.io/agent-runtime/ 、release notes。
- **注册到客户端**：`pyrevit mcp install claude`（user scope；`--project` 写当前目录 `.mcp.json`）、`pyrevit mcp install codex`（Codex 只支持用户级）；移除 `pyrevit mcp uninstall <client>` / `--all`。含注释的配置文件不会被改写，只打印条目让你贴。文档没写写入的具体条目；BIMBridge install.ps1 写给 Claude Desktop / Codex 的是 `command = <pyrevit.exe>`，`args = ["mcp"]`。多个 Revit：`pyrevit mcp --revit=<year>`。CLI 必须是同一个 build 的 `pyrevit`（旧版 PATH 上的不认识 agent/mcp 命令）。
- **安全**（docs 页）：传输是命名管道 `\\.\pipe\pyrevit-agent-<pid>`，没有 TCP 端口、不上网；只允许当前 Windows 用户，拒绝网络登录 → 同一用户下任何进程都能送脚本；CLI 核对管道进程是不是登记的 Revit；RDP 可以，SSH 故意拒绝；AI 读到的东西（元素名、参数值、结果）会送到模型供应商；脚本、请求、响应、截图明文存在 `%APPDATA%\pyRevit\agent`，保留 14 天；「回滚保护的是模型，不是文件系统或网络，没有沙箱，只连可信 agent，不要喂不可信内容」。Routes server 不需要（Routes 没有认证，也不会被拿来执行代码）。
- **验证范围**：docs 写 Phase 0 在 Revit 2024 和 2025 上验证（2024 build 24.1.11.26，IronPython 3.4.2）；Revit 2026 的 CPython 和 2026 检查「pending」。release notes 的 CI 集成测试（加载 add-in）默认跑 2022–2027，但那只证明 add-in 能载入 → agent runtime 在 2026/2027 **未验证**。
- **Python 版本**：`get_context.scripting` 报默认引擎；IronPython 2.7.12 或 3.4.2，或 CPython（pythonnet）。IronPython 3.4.2 不支持海象运算符、async、`1_000`、`/` 位置参数、`match`。
- **pyRevit 自带的 agent 技能**：`revit-scripting`（每次 run 前读）、`pyrevit-library`、`modeling`、`views`、`scheduling`、`drawings`、`family-editing`、`revit-files`、`extension-authoring`（仓库 `pyrevitlib/pyrevit/agent/skills/` 目录列表核对过）。用户技能（`%APPDATA%\pyRevit\agent\skills`）不能覆盖同名内置技能或主机强制规则。

## 3. 其他开源 Revit MCP（2026-10-22 GitHub API 数据）

| 仓库 | 授权 | star | 最后 push | 架构 / 要点 |
|---|---|---|---|---|
| mcp-servers-for-revit/mcp-servers-for-revit | MIT | 389 | 2026-10-20 | revit-mcp 的 fork；TS MCP 服务器（npm `mcp-server-for-revit`，stdio）⇄ WebSocket ⇄ C# Revit add-in ⇄ command set；Revit 2020–2026；~26 个工具（create_level、create_line_based_element、color_elements、`send_code_to_revit` 执行 C# 等）；Claude Code：`claude mcp add mcp-server-for-revit -- cmd /c npx -y mcp-server-for-revit`；Revit 里 Settings 勾选启用哪些命令。**没有逐次批准框**（README 没提）→ 推论：改动直接落地 |
| mcp-servers-for-revit/revit-mcp（+ revit-mcp-plugin、revit-mcp-commandset） | MIT | 475 | 2026-10-21 | 原版，同架构 |
| mcp-servers-for-revit/mcp-server-for-revit-python | MIT | 216 | 2026-10-14 | FastMCP → HTTP → pyRevit Routes（localhost:48884）→ Revit API |
| bimwright/rvt-mcp | Apache-2.0 | 94 | 2026-10-21 | 全 C#；.NET 8 服务器 stdio；Revit 2022–2027；≤2024 走 localhost TCP、≥2025 走命名管道；README 称 237 个工具 + C# 逃生口；有 Claude Desktop MCPB 安装包 |
| oakplank/RevitMCP | MIT | 64 | 2026-10-18 | pyRevit 扩展 + Python 服务器；46 个工具，含 `export_active_view_image`、`delete_elements`（dry-run + 确认 + 上限）；也有 Web UI 127.0.0.1:8000 |
| Demolinator/revit-mcp-server | MIT | 37 | 2026-10-21 | FastMCP → pyRevit Routes :48884；Revit 2024–2027；48 个工具；要 uv |

- 走 pyRevit **Routes**（HTTP :48884）的方案：pyRevit 文档说 Routes server 没有认证 → 本机任何程序都能打这个端口（推论：比命名管道 + 批准框风险高）。
- 来源：各仓库 README（gh api）、`gh search repos "revit mcp" --sort stars`。star 数和日期是当天快照。

## 4. Autodesk 官方 Revit MCP

- Autodesk 博客 2026-06-17「Introducing the Revit Public MCP Server」：Tech Preview，Revit 2027 的独立附加组件，从 Autodesk 账户（Revit 2027 权益下）下载，装好会自动配置 Claude Desktop / Cursor，走 stdio。来源：https://www.autodesk.com/blogs/aec/2026/06/17/revit-public-mcp-server/ （WebFetch 403，内容来自搜索摘要 → **细节未直接核对**）。
- Autodesk 开发者博客（日文，2026-09-29，Toshiaki Isezaki）「Revit MCP サーバー更新」：需要 **Revit 2027 + 2027.2 Update 以上**；分 **Read / Write / Experimental** 三个安装包（Write 含 Read，Experimental 含全部），都是 Technical Preview；从 Autodesk Account → Products & Services → Product Updates → Extensions 下载；本机 STDIO；有 Claude Desktop 时安装包写 `claude_desktop_config.json`；建议先备份项目。文章没写 Claude Code / Codex 的配置、没写费用、没列具体工具名（链到 "Tools and Language Support" 页）。来源：https://blog.autodesk.io/revit-mcp-server-update/ 、https://blog.autodesk.io/revit-2027-mcp-server-release/
- 推论：用户有 Revit 会员，若用的是 Revit 2027.2+，官方 MCP 是在会员权益内下载的；**是否另外计费、是否要 Autodesk 云端额度：未验证**，用之前要问。Claude Code / Codex 怎么接：文章没写 → 可参考装好后 `claude_desktop_config.json` 里的条目手动搬，**未验证**。
- Revit 2027 还有 Autodesk Assistant（产品内 AI，Tech Preview，据 Architosh 说也用 MCP）：https://architosh.com/2026/04/autodesk-revit-2027-big-new-ai-and-graphics-changes/ （未细读）。

## 5. Revit API 要点（agent 写脚本时用）

- 内部长度单位是**英尺**；BIMBridge 技能写 `feet = meters / 0.3048`。Revit 2021+ 可用 `UnitUtils.ConvertToInternalUnits(value, UnitTypeId.Meters)`（ForgeTypeId）**（常识，未逐条核对 docs 页）**。
- 改模型必须在 `Transaction` 里（Start/Commit/RollBack）；pyRevit agent 的 `run_modify` 是否自动包 transaction：release notes 说「transaction left open → 失败」，意思是脚本自己开的要自己关；具体由 pyRevit `revit-scripting` 技能说明 → 让 agent 先 `get_skill("revit-scripting")`，不要猜。
- `Document.NewFloor` 在 Revit 2022 标为 obsolete，改用 `Floor.Create(doc, IList<CurveLoop>, floorTypeId, levelId)`。来源：https://www.rvtdocs.com/2022/a026924c-ed96-761a-8d0d-2114086fe656 、Autodesk 论坛 https://forums.autodesk.com/t5/revit-api-forum/create-floor-revit-api-2023/m-p/11265961
- 其他常用（签名以 `lookup_revit_api` 在用户自己的 Revit 里反射为准）：`Level.Create(doc, elevation)`、`Wall.Create(doc, Line, levelId, structural)`（多个重载）、`doc.Create.NewFamilyInstance(...)`（放门窗家具前 `FamilySymbol.Activate()`）、`ViewPlan.Create`、`View3D.CreateIsometric`、`FilteredElementCollector(doc).OfClass(...)/OfCategory(...).WhereElementIsNotElementType()`、`Element.LookupParameter` / `get_Parameter(BuiltInParameter…)` → `.Set()`。**（常识，未逐条核对；技能里要求先 lookup）**
- FamilyInstance 类页（revitapidocs 2024）：https://www.revitapidocs.com/2024/0d2231f8-91e6-794f-92ae-16aad8014b27.htm
- 自定义 3D 导出走 `CustomExporter` + `IExportContext`（Leia glTF 导出器就是这么做的，见 §6）**（推论，从 Leia 源码结构看）**。

## 6. Revit → glTF / three.js（免费）

### 6.1 Leia：e-verse 的 revit-glTF-exporter
- https://github.com/EverseDevelopment/revit-glTF-exporter ，MIT，81 star，release v4.5.242（2026-06-03）。README 说「free add-in」，从 Autodesk App Store 装：https://apps.autodesk.com/RVT/es/Detail/Index?id=492952120634946986&appLang=en&os=Win64 。README 写支持 2019–2024，但仓库根目录有 `Revit_glTF_Exporter_2025/2026/2027` 项目 → 2025–2027 有代码，**App Store 版本是否已发布 2027：未验证**。
- 用法（README）：进 3D 视图 → 隐藏不要的 → 选导出属性 → Export。
- **材质**：`Common_glTF_Exporter/Utils/MaterialUtils.cs` 读每个 mesh 的 `MaterialElementId` → `gl_mat.name = material.Name`，`baseColorFactor = material.Color`（RGB/255）+ `1 - Transparency`，metallic 0、roughness 1；没有材质时用默认材质。有 `materials` / `textures` 两种模式；目录里有 DracoWrapper、MeshOpt（压缩）。→ **glTF 材质名 = Revit 材质名，颜色 = Revit 材质的着色颜色（Graphics → Shading color）**。这就是做 colour map 的最短路（推论）。

### 6.2 Revit 原生导出
- **FBX**：Revit 自带「Export to FBX」（3D 视图），带材质指定、灯光、render appearance 给 3ds Max。来源：https://help.autodesk.com/cloudhelp/2023/ENU/Revit-DocumentPresent/files/GUID-C8038EFE-FB14-4591-85A1-8407B2BDDD0A.htm 。之后可用 Blender 导入 FBX 再导 glTF（交给 `archviz-web-walkthrough`）。
- **glTF / OBJ**：没找到 Autodesk 官方说明 Revit 原生导出 glTF；搜到的都是第三方插件（不少付费，如 SimLab、ProtoTech 试用）→ **原生 glTF 未验证（推论：没有）**。
- **IFC**：Revit 原生，代码开源 https://github.com/Autodesk/revit-ifc （GitHub API 未检出 LICENSE 文件；README：Revit 2019+ 用的 IFC 代码，开源版覆盖自带版本，Autodesk Desktop App 也可更新）。

### 6.3 IFC → glTF / three.js
- **IfcOpenShell IfcConvert**（LGPL-3.0）：输出 `.obj`（含 `.mtl`）、`.dae`、`.glb`（glTF 2.0 二进制）、`.xml`、`.svg`、`.ttl`、`.ifc`、`.stp`。`--use-material-names`「用材质名代替唯一 ID 命名材质，**适用于 OBJ 和 DAE**」；`--use-element-guids` / `--use-element-names` 也只列 OBJ、DAE、STP、SVG；`--y-up` 只列 OBJ；`--include entities IfcWall IfcSlab`、`--center-model`、`--enable-layerset-slicing`（按 IfcMaterialLayerSet 切片 → 墙的各层材质分开）。来源：仓库 `docs/ifcconvert/usage.rst`。→ **GLB 输出里材质 / 元素是否保留名字：未验证**；要保名字时用 OBJ + `--use-material-names --use-element-guids`（推论）。
- **web-ifc**（That Open，MPL-2.0，npm 0.0.78 当天）：浏览器 / Node 读写 IFC。`StreamAllMeshes(modelID, cb)` 给每个元素一个 `FlatMesh{expressID, geometries[]}`，每个 `PlacedGeometry` 有 `color{x,y,z,w}`、`geometryExpressID`、`flatTransformation`。`expressID` 就是 IFC 文件里的 `#id`（`GetLine(modelID, expressID)` 用同一个 ID）。来源：`src/ts/web-ifc-api.ts`、`examples/usage/src/geometrystream.ts`。
- **That Open Engine components**（@thatopen/components，MIT）：基于 three.js 的 BIM 组件，有 IfcLoader 示例。https://github.com/ThatOpen/engine_components
- three.js 当天 npm 版本 0.186.1。

### 6.4 colour map（每种材质一个平涂颜色）（推论为主）
- 路线 A（最短）：Revit 里给每种材质设不同的 **Shading color** → Leia 用 materials 模式导出 glb → three.js 里把每个材质换成 `MeshBasicMaterial({color})`（不受光照）→ 每种材质一个纯色。或者不改 Revit，直接在 three.js 里按材质名哈希出颜色。
- 路线 B（IFC）：Revit 导 IFC → 本技能 `ifc_material_colormap.py` 读出「元素 #id / GlobalId → 材质名」和「材质名 → 颜色」→ web-ifc 按 `expressID` 上色。多层墙只拿到层集名或第一层（脚本说明）。
- 路线 C：在 Revit 里直接做：材质 Shading color + 视图 Visual Style = Shaded（不勾 Use Render Appearance）→ 视图本身就是 colour map，可 `capture_view` 截图或 Revit 自带漫游导出 → 只能出 Revit 自己的相机，不如 three.js 灵活。**未验证**。
- 关闭色调映射 / 抗锯齿注意：colour map 要「色块精确」时 `renderer.toneMapping = NoToneMapping`、`outputColorSpace` 要和取色一致；MSAA 会在边缘混色 → 做 ID/分割图时关抗锯齿（推论，常见做法）。
- 相机路径和影片输出交给 `archviz-web-walkthrough`（网页、相机）和 `archviz-cinematic`（运镜、ffmpeg 编码）；AI 把 colour map 变照片交给 `ai-archviz-render`（ControlNet 用 segmentation 图）（推论）。

## 7. 本技能的决策

- 首推 **pyRevit 7 官方 agent runtime**（GPL-3.0、免费、命名管道、Revit 内批准、单步 undo、免费）；BIMBridge 只当「一键安装 + 两个技能」的可选包，先读它的 install.ps1。
- Revit 2027.2+ 可选 Autodesk 官方 MCP（会员内，Tech Preview，费用未验证 → 先问）。
- 需要固定工具集（不想让 AI 写 Python）时才考虑 mcp-servers-for-revit / rvt-mcp / RevitMCP；注意它们没有逐次批准框（mcp-servers-for-revit 的 `send_code_to_revit` 能执行任意 C#）。
- 脚本：`ifc_material_colormap.py` 纯标准库，读 IFC 文本（STEP），只读，输出 JSON 调色板。
