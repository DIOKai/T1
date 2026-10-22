# E — Rhino MCP / SketchUp MCP / Blender Geometry Nodes 立面 调研笔记

调研日期：2026-10-22。每条事实后附来源；没能直接核实的标 **未验证**。GitHub 数据（星数、最后 push 时间、license）是 2026-10-22 用 `gh api repos/<repo>` 实时查的。

---

## 0. 灵感来源：Studio Tim Fu

- Studio Tim Fu：伦敦 Marylebone 约 10 人的 AI 建筑事务所，创办人 Tim Fu 曾在 Zaha Hadid Architects 做研究。来源：https://aecmag.com/features/studio-tim-fu-ai-driven-design/
- Cacao Greenhouse（瑞士 Maison Cailler 巧克力园）：2023 年从 Midjourney 概念开始，2024–2025 进入 Rhino + Grasshopper 做结构优化、立面合理化（facade rationalisation）、节点设计；双曲面形体被合理化成**全部平板**的金属和玻璃板。来源：同上（AEC Magazine）。
- 用户提到的「agent 做环境感知、曲线几何合理化、立面细部、模块体块分布」——搜索没找到 Studio Tim Fu 官方对该 agent 的公开说明。**未验证**（可能来自社交媒体视频）。

---

## 1. Rhino MCP 项目

### 1.1 总表（2026-10-22 `gh api` 实查）

| 项目 | License | ★ | 最后 push | Rhino 版本 | 执行代码方式 | Grasshopper |
|---|---|---|---|---|---|---|
| **mcneel/RhinoAI**（官方，旧名 mcneel/RhinoMCP） | MIT | 371 | 2026-10-20 | Rhino 8（以及 Rhino 9 WIP/BETA） | `run_python`（CPython 3，经 Rhino ScriptEditor）、`run_csharp`、`run_command` | GH1 + GH2 都有专用工具 |
| tanishqbhattad/rhino-mcp | MIT | 30 | 2026-10-12 | Rhino 8（`execute_python3` 要 8.11+） | IronPython 2 `execute_script`；CPython 3 `execute_python3`（需 developer 模式） | 页面无 GH 功能 |
| reer-ide/rhino_mcp | MIT | 29 | 2026-04-05 | Rhino 7+ | `execute_code`（任意 Python） | 「开发中，不完全可用」 |
| SerjoschDuering/rhino-mcp | README 写 MIT，但 GitHub 没检测到 LICENSE 文件 | 65 | 2025-04-08 | Rhino 7+（文档写 Rhino 7） | `execute_rhino_code`、`execute_code_in_gh` | 有（.gh 服务器组件，HTTP） |
| sholtomaud/rhino-mcp | 无 LICENSE 文件（GitHub API 404） | 0 | 2025-06-10 | 同 SerjoschDuering 系（fork） | 同上 | 同上 |
| mustafaisildakcom/rhino-mcp | 无 LICENSE 文件 | 1 | 2025-04-08（与 Serjosch 同一时间，基本是 fork 未更新） | 同上 | 同上 | 同上 |
| rhino-gh-mcp（PyPI 0.1.8，2026-01-28，作者 Archolic / liuxun1230） | MIT | – | – | Rhino 7/8 | 任意 Python（Rhino socket 9876；GH C# 组件 HTTP 9999） | 有 |

来源：
- https://github.com/mcneel/RhinoAI ；`gh api repos/mcneel/RhinoMCP` 描述 "old repo name for RhinoAI"
- https://github.com/tanishqbhattad/rhino-mcp
- https://github.com/reer-ide/rhino_mcp
- https://github.com/SerjoschDuering/rhino-mcp
- https://github.com/sholtomaud/rhino-mcp 、https://github.com/mustafaisildakcom/rhino-mcp（只查了 API 元数据，没细读 README）
- https://pypi.org/project/rhino-gh-mcp/

其他看到但没细查：always-tinkering/rhinoMcpServer（57★，2025-03 后没更新，无 license）、4kk11/RhinoMCPServer（MIT，13★）、EaseHee/rhino-mcp（MIT）、GOLEM-3DMCP（`pip install golem-3dmcp`，Rhino 8，**未验证**，GitHub 仓库地址没找到）。

### 1.2 推荐：McNeel 官方 RhinoAI（Rhino-MCP-Platform）

理由：Rhino 开发商自己出的、MIT、2026-10 仍在更新（plugin-v0.3.0 发布于 2026-09-30）、官方文档覆盖 Claude Code 和 Codex、有 GH1/GH2 专用工具、隐私说明清楚。

**安装（Rhino 端）** —— 来源：https://mcneel.github.io/RhinoAI/docs/getting-started/cc-plugin/ （仓库 `docs/content/docs/getting-started/cc-plugin.md`）
1. 只支持 Rhino 8（也可装进 Rhino 9 WIP/BETA）。
2. Rhino 里运行 `PackageManager`，搜索并安装 **Rhino-MCP-Platform**（或点链接 `rhino8://package/search?name=Rhino-MCP-Platform`）。
3. 运行 `MCPConnect`，把它生成的提示词贴进新的 Claude Code 会话，按提示重启 Claude Code。

**Claude Code 插件方式**（文档里这一段目前被 HTML 注释掉，但 `cc-plugin/README.md` 仍有）—— 来源：https://github.com/mcneel/RhinoAI/blob/main/cc-plugin/README.md
```
/plugin marketplace add mcneel/RhinoAI
/plugin install mcneel@rhino-mcp
```
- 插件 `.mcp.json`：`"rhino": {"type":"stdio","command":"node","args":["${CLAUDE_PLUGIN_ROOT}/router-launcher.mjs"]}`
- README 写：Rhino 里先跑 `MCPStart`，默认端口 **10500**（`http://localhost:10500`）。
- 插件附带：`/rhino-mcp:snapshot`、`/rhino-mcp:scene`、`/rhino-mcp:launch-rhino(s)`、`/rhino-mcp:install-mcp`；agents：rhino-modeler / drafter / inspector / organizer / teacher、grasshopper-scripter / reviewer / teacher（仓库 `cc-plugin/agents/`）。
- 注意：官方文档把 plugin 段注释掉了，当前推荐路径是 `MCPConnect` → 粘贴提示词。两种方式哪个对新版本最可靠 **未验证**（需实机测）。

**OpenAI Codex** —— 来源：https://mcneel.github.io/RhinoAI/docs/getting-started/codex/
```toml
# ~/.codex/config.toml
[mcp_servers.rhino]
command = "rhino-mcp-router"
args = ["--default-version", "8"]   # 9 = Rhino 9 WIP/BETA
```
（先在 Rhino 跑 `MCPConnect`，它会打印 Codex 需要的命令。）

Claude Desktop：安装 `.mcpb` connector（https://github.com/mcneel/RhinoAI/releases/download/connector-v0.1.6/connector.mcpb），它会自动帮你装 Rhino 插件。来源：仓库 README。

**工具清单**（从 `rhino/plugin/Tools/*.cs` 的 `[McpServerTool("…")]` 抓出来的，2026-10-22）：
- 文档/场景：`get_context`（只读一次拿选择、视口、文档摘要、GH 摘要）、`list_objects`、`get_selection`、`set_selection`、`get_viewport_image`、`set_camera`、`zoom_to_layer`、`zoom_to_object`、`set_layer_material`、`open_doc`、`save_doc`、`close_doc`、`get_commands`
- 执行代码：`run_python`（"Execute a Python 3 script…"，用注入的 `__rhino_doc__` 作文档句柄，**不要**信 `scriptcontext.doc` / `rhinoscriptsyntax`）、`run_csharp`（同样用 `__rhino_doc__`）、`run_command`（Rhino 命令行）
- `manage_plugin_commands`：把 C# 脚本注册成可重复使用的 Rhino 命令（**只 Rhino 9+**）
- Grasshopper 1：`g1_start`、`g1_search_components`、`g1_describe_component`、`g1_place_component`、`g1_place_slider`、`g1_connect`、`g1_connect_many`、`g1_apply_graph`（一次放滑块+组件+连线）、`g1_get_canvas_graph`、`g1_solve_graph`、`g1_delete_component`、`g1_clear_canvas`
- Grasshopper 2：同名 `g2_*`（`g2_solve_canvas`）
- `ask_user`
来源：https://github.com/mcneel/RhinoAI/tree/main/rhino/plugin/Tools ；`RunPythonTool.cs`、`RunCSharpTool.cs`、`GetContextTool.ai.cs`、`GH1/GH1_ApplyGraphTool.cs`

**安全**（来源：https://github.com/mcneel/RhinoAI/blob/main/PRIVACY.md ，2026-05-19 更新）：
- connector 本身不收集、不上报数据，全部在本机 Rhino 进程里处理。
- 但工具结果（几何、脚本输出、视口截图）会通过 Claude 客户端离开本机。
- `run_command`、`run_python`、`run_csharp` 能执行任意代码/命令，`open_doc`、`save_doc` 能读写用户账号可访问的任何文件——要像对待任何能跑脚本的工具一样小心。
- 技能里要写：用前先问；不要用来打开来路不明的 .3dm/.gh；改重要文件前先另存。

**备选：tanishqbhattad/rhino-mcp**（适合要更强安全闸门的人）：本机 only + 每用户 auth token；`RHINO_AIBRIDGE_MODE` = `safe`（默认，禁止代码和破坏性编辑）/ `standard` / `developer`；默认 `127.0.0.1:9544`；128 个工具分 lean(21)/standard(76)/full(128)；Codex 配置 `[mcp_servers.rhino_architect]` 用 `uv --directory <path>/server run --frozen rhino-architect`；安装用 `INSTALL.bat` + `PlugInManager` 装 `RhinoAIBridge.rhp`；README 没写 Claude Code 配置（只有 Claude Desktop）。来源：https://github.com/tanishqbhattad/rhino-mcp 。缺点：个人项目、30★、没有 GH 功能。

reer-ide 等旧项目：都是 blender-mcp 的衍生结构（Rhino 里跑 Python 脚本开 socket，`uvx reer-rhino-mcp`），任意代码执行无闸门、文档仍以 Rhino 7 为主，**不推荐**。来源：https://github.com/reer-ide/rhino_mcp 、https://github.com/SerjoschDuering/rhino-mcp （端口 9876；可选 Replicate 渲染要付费 API token——用户不用付费服务，技能里要排除）。

### 1.3 Rhino 8 价格与试用

- 价格（rhino3d.com/buy，2026-10-22 抓取，USD）：商业版单用户 **$995**；升级 $595；教育版 $195（升级 $95，需身份证明、不可转让）；Lab 30 用户 $975。来源：https://www.rhino3d.com/buy/
- 「Evaluation versions are NOT upgradable」。来源：同上。
- 评估版：**90 天**一次性试用；到期后**不能保存、插件不能加载**，需买授权。来源：https://www.rhino3d.com/downloadeval/ （搜索摘要）及 https://discourse.mcneel.com/t/rhino-8-evaluation-after-the-90-day-trial-expires/181869
- 到期后「锁定到单机当查看器」的说法是论坛用户经验，结果不一致 → **未验证**。
- 推论：评估期内插件可用，所以 Rhino-MCP-Platform 能试 90 天；到期后插件不加载 → MCP 也不能用（**推论，未实测**）。
- Rhino 是付费软件 → 技能必须写「用前先问；用户没有 Rhino 授权就推荐免费的 parametric-facade（Blender）路线」。

### 1.4 McNeel 官方论坛 AI 分类
- https://discourse.mcneel.com/c/rhino/artificial-intelligence-rhino/162 （HTTP 200 已确认）

---

## 2. Rhino / Grasshopper 立面技术

### 2.1 Panelization 工具
- **LunchBox**（Proving Ground）：免费、开源，LGPL；Rhino 7/8 用 `PackageManager` 搜 LunchBox 安装；面板类型有 quad grid、diamond、triangle、hexagon、skewed quad 等。Windows 为主，Rhino 8 Mac 仅「nominal testing」。来源：https://apps.provingground.io/install-lunchbox-for-grasshopper/ 、https://www.food4rhino.com/app/lunchbox （food4rhino 对脚本 403，摘要来自搜索）、https://howtorhino.com/rhino-grasshopper-tutorials/lunchbox-plugin/
- **PanelingTools**（McNeel）：两种做法——有序点网格（行列编号）或直接按曲面/多重曲面；面板可输出为 edges、face borders、face patches、flat faces、mesh。命令：`ptGridSurfaceDomainNumber`（按 UV 分割建网格）、`ptPanelGrid`（对网格做面板）、`ptPanelGridQuads`（可设最大偏差的平板四边形）、`ptGridArray`。普通点没有 u,v 编号不能面板化。Rhino 8 Mac 上菜单可能不显示但命令行能跑。来源：https://wiki.mcneel.com/labs/panelingcommands 、https://wiki.mcneel.com/_media/labs/panelingtoolsmanual.pdf 、https://discourse.mcneel.com/t/panelingtools-ui-missing-in-rhino-8-for-mac/216240 、https://discourse.mcneel.com/t/how-to-convert-regular-points-to-paneling-points/74634
- PanelingTools 在 Rhino 8 是否预装：**未验证**。

### 2.2 曲面合理化（rationalisation）
- 三点定一平面，四边形面板一般不平；要平就要选可平板化的基面（如环面的一部分、平移曲面）、或用松弛（Kangaroo）/ 专业工具（Evolute）、或退而用三角形（永远是平的，但板数多）。来源：https://discourse.mcneel.com/t/planarizing-quad-panels-on-double-curved-surface/116811
- 统一尺寸的平板四边形只能铺圆柱类曲面；双曲面必须改变边长或内角。来源：同上。
- **Kangaroo 2** 用固定锚点 + 平面化 goal 做松弛；Kangaroo2 随 Rhino 7+ 的 Grasshopper 自带、有 Planarize goal —— **未验证**（凭记忆，food4rhino 页面 403 没抓到）。
- 可展开条带（developable strips）：RhinoCommon `Brep.CreateDevelopableLoft`（见 2.4）；可用 `Unroller` 展开下料。
- 曲率分析：`Surface.CurvatureAt(u,v)` → `SurfaceCurvature`（`.Gaussian`、`.Mean`、`.Kappa(i)`、`.Direction(i)`）。高斯曲率 ≈ 0 的区域可做可展/单曲面板，|K| 大的区域用三角或冷弯玻璃（工程常识，具体阈值由幕墙顾问定）。

### 2.3 Attractor（吸引点）立面
- 做法：每块面板取面积中心 → 量到吸引点/吸引曲线的距离 → Remap / Graph Mapper 映射成开孔大小、旋转角或缩放。来源：https://www.studiomatrx.org/students/computational-parametric-design/responsive-facades 、Parametric House 教程 https://grasshopper3d.com/video/grasshopper-tutorial-parametric-facade （三角面板 + LunchBox + attractor 缩放）
- 常用插件组合：Kangaroo（找形）、LunchBox（面板）、Ladybug（环境/日照）、Weaverbird（网格）。来源：https://www.studiomatrx.org/students/parametric-architecture/parametric-tools-and-techniques

### 2.4 关键 RhinoCommon API（签名来自 McNeel 官方 Python stubs：https://github.com/mcneel/pythonstubs `stubs/Rhino/Rhino-stubs/Geometry/__init__.pyi`；developer.rhino3d.com API 页面是 JS 渲染、WebFetch 读不到）

注意：stubs 仓库最后 push 2024-08-12，签名应对 Rhino 8 成立，个别新重载可能缺。

- `Surface.Domain(direction) -> Interval`
- `Surface.PointAt(u, v)`、`Surface.NormalAt(u, v) -> Vector3d`
- `Surface.FrameAt(u, v) -> (bool, Plane)`
- `Surface.CurvatureAt(u, v) -> SurfaceCurvature`；`SurfaceCurvature.Gaussian` / `.Mean` / `.Kappa(direction)` / `.Direction(direction)`
- `Surface.IsoCurve(direction, constantParameter) -> Curve`
- `Surface.IsPlanar()` / `IsPlanar(tolerance)`；`Surface.IsCylinder(tolerance)`、`IsSphere`
- `Surface.ClosestPoint(testPoint) -> (bool, u, v)`
- `Brep.CreateFromCornerPoints(c1, c2, c3, c4, tolerance)`（四点面板；四点不共面时生成的是非平面面）
- `Brep.CreatePlanarBreps(curves, tolerance)`
- `Brep.CreateDevelopableLoft(crv0, crv1, reverse0, reverse1, density)` 及 `CreateDevelopableLoft(rail0: NurbsCurve, rail1: NurbsCurve, fixedRulings)`
- `Brep.CreateFromLoft(curves, start, end, loftType, closed)`
- `Brep.CreateContourCurves(brep, plane)` / `(brep, start, end, interval)` → 楼层切片
- `Brep.Split(cutters, tolerance)`
- `Curve.DivideByCount(n, includeEnds)`、`Curve.DivideByLength(len, includeEnds)`、`Curve.PerpendicularFrameAt(t)`、`Curve.Offset(plane, distance, tol, cornerStyle)`
- `Plane.FitPlaneToPoints(points) -> (PlaneFitResult, Plane, maxDeviation)`、`Point3d.ArePointsCoplanar(points, tol)`（stubs 中有，所属类按上下文推断 **未验证**）→ 检查四边形面板平面度
- `Unroller(...).PerformUnroll()` → 展开下料
- RhinoAI 的 `run_python` 用 `__rhino_doc__`，所以加对象写 `__rhino_doc__.Objects.AddBrep(...)`（**推论**，依据 RunPythonTool 描述）。

Python 指南：https://developer.rhino3d.com/guides/rhinopython/

---

## 3. SketchUp

### 3.1 Trimble 官方 SketchUp MCP（Claude connector）
- 发布：2026-04-28，Trimble 第一个 MCP connector；在 Claude 的 connector 设置里开启「Trimble SketchUp」（claude.ai/customize/connectors）；需 **Claude 账号 + Trimble ID**（OAuth）。来源：https://news.trimble.com/2026-04-28-Trimble-Links-SketchUp-with-Anthropics-Claude,-Bringing-New-Conversational-AI-powered-Capabilities-to-3D-Modeling
- 运作：Claude 在**云端 SketchUp 会话**里建模、边做边检查尺寸；同一个对话里有版本历史，可贴截图指出要改的地方；完成后给 2D 预览缩略图 + .skp 直接下载链接，可在 SketchUp Web / Desktop / iPad / iPhone 打开。来源：同上。
- Claude 连接器注册表（2026-10-22 实查 `search_mcp_registry`）：名称 "Trimble SketchUp"，描述 "Create and iterate 3D models for use in SketchUp"，工具 `build_model`、`get_docs`、`save_model`，URL `https://api.sketchup.com/mcp/v1/sketchup/mcp`。
- 有第三方评测说 Trimble 文档里中间那个工具是「Python 执行工具」而不是 build_model，两者不一致 → 以实际连上后的工具列表为准（**未验证**）。来源：https://hackceleration.com/resources/integrations/claude/sketchup （搜索摘要）
- 限制（第三方）：只能**新建** .skp，不能编辑/渲染已有模型；模型不跨会话保存，要自己下载。来源：同上（**未验证**，Trimble 新闻稿没说能否编辑旧模型）。
- 免费额度：Trimble 新闻稿说免费 entitlement「可保存最多 30 个模型，之后需付费 entitlement」；engineering.com 说「没有 SketchUp 订阅的用户每月可生成 30 个 .skp，有付费订阅（含 $19.99/月 的 SketchUp Go）不限」——**两者说法不同（总数 vs 每月）**，标未验证。来源：Trimble 新闻稿；https://www.engineering.com/now-sketchup-has-an-mcp-server-for-claude-based-3d-modeling/
- Trimble 表示第三方 AI 助手中只官方支持 Claude。来源：engineering.com 同上。
- 结论：**不需要装 SketchUp，也不需要付费就能先试**（免费 30 个），但它是连外部服务 + 要登录 Trimble ID → 技能里要先问；超出免费额度要付费 → 按用户规则不推荐付费。
- 官方帮助文档 URL：没找到 help.sketchup.com 上的专页 → **未验证**。

### 3.2 SketchUp 方案和价格
- 官网年付（每用户每月折算，USD）：**Go $10.75**、**Pro $33.25**、**Studio $71.58**；Go 只有 Web + iPad、**没有桌面版**；Pro/Studio 有桌面 + LayOut；Studio 含 V-Ray、Revit 导入。来源：https://sketchup.trimble.com/en/plans-and-pricing （sketchup.com 已 301 跳到这里）
- Go 月付 $19.99（engineering.com 提及），官网页面抓取未显示月付价 → 部分未验证。
- **SketchUp Free**（网页版）：仅限爱好者/非商业；商业用途需付费版。来源：https://forums.sketchup.com/t/export-formats/129818 （搜索摘要；官方页面原文 **未验证**）。

### 3.3 各方案导出格式（官方帮助表）
来源：https://help.sketchup.com/en/sketchup/using-sketchup-data-other-modeling-programs-or-tools

| 格式 | Free | Go | Pro | Studio |
|---|---|---|---|---|
| .dae (COLLADA) | ✗ | ✓ | ✓ | ✓ |
| .fbx | ✗ | ✓ | ✓ | ✓ |
| .obj | ✗ | ✓ | ✓ | ✓ |
| glTF（表里印成 ".gib"，应是笔误） | ✗ | ✗ | ✓ | ✓ |
| .stl | ✓ | ✓ | ✓ | ✓ |
| .3ds | ✗ | ✓ | ✓ | ✓ |
| .usdz | ✗ | ✗ | ✓ | ✓ |
| .ifc | ✗ | ✗ | ✓ | ✓ |

- 结论：SketchUp Free 只能导 STL（无材质/UV）→ 不适合「电影感」渲染；**免费路线是：拿 .skp 文件（Free 网页版可下载 .skp —— 未验证；或官方 MCP 生成的 .skp）→ Blender 用免费 .skp 导入插件**。

### 3.4 开源 SketchUp MCP
注意：都是在 SketchUp **桌面版**里装 Ruby 扩展（.rbz）开 TCP 服务器 → 需要 SketchUp Pro/Studio 桌面版（Go 没桌面版、Free 不能装扩展 —— 推论）。

| 项目 | License | ★ | 最后 push | 要点 |
|---|---|---|---|---|
| mhyrr/sketchup-mcp | README 写 MIT，但 GitHub 没检测到 LICENSE 文件 | 503 | 2026-04-25 | 照 blender-mcp 结构；`.rbz` 扩展 → Extensions > SketchupMCP > Start Server，端口 9876；客户端 `uvx sketchup-mcp`；工具 `get_scene_info`、`get_selected_components`、`create_component`、`delete_component`、`transform_component`、`set_material`、`export_scene`、`eval_ruby`（任意 Ruby） |
| **zinin/sketchup-mcp2** | MIT | 50 | 2026-10-20（v0.4.0） | 维护最积极；`uvx sketchup-mcp2`；`127.0.0.1:9876`；`.mcp.json` 示例直接给了 Claude Code 用法；工具含 create/delete/transform、boolean、chamfer/fillet、榫卯、`export_scene`（skp/obj/dae/stl/png/jpg）、`get_viewport_screenshot`（需 SketchUp 2026+）、`undo`、`eval_ruby`（**默认开启**，可在 Plugins → MCP Server → Settings 关掉）；每次修改包 `start_operation/commit_operation` 可一键撤销 |
| Shattenjagger/sketchup-mcp-bridge | MIT | 3 | 2026-05-31 | 声称修了 mhyrr 在 SketchUp 2026 的不同步/写入卡死 |
| andyluu98/vn-sketchup-mcp | MIT | 11 | 2026-09-01 | mhyrr 修复 fork，写了 Claude Code / Codex 一键安装 |
| SidhNor/sketchup-mcp-server | AGPL-3.0 | 8 | 2026-06-03 | 地形、语义建模 |

来源：https://github.com/mhyrr/sketchup-mcp 、https://github.com/zinin/sketchup-mcp2 、`gh search repos "sketchup mcp"`（2026-10-22）。

Claude Code 配置（zinin/sketchup-mcp2 README 原文结构）：
```json
{"mcpServers":{"sketchup":{"command":"uvx","args":["sketchup-mcp2"],
  "env":{"SKETCHUP_MCP_HOST":"127.0.0.1","SKETCHUP_MCP_PORT":"9876","SKETCHUP_MCP_TIMEOUT":"60"}}}}
```
Codex 配置：README 未写；按 Codex 通用格式 `[mcp_servers.sketchup] command="uvx" args=["sketchup-mcp2"]` —— **未验证**。

### 3.5 免费的 SketchUp → Blender
- **RedHaloStudio/Sketchup_Importer**（637★，最新 0.27.0 于 2026-01-26）：release notes 写「Support Blender 5.1 alpha」「Support SketchUp 2026.1.185」；基于官方 SketchUp C SDK 的 Python 绑定（pyslapi）。安装：Edit > Preferences > Add-ons > Install 选 zip → 启用 "Import-Export: Sketchup importer" → File > Import > Import Sketchup Scene (.skp)。**不支持 Linux**（SDK 没 Linux 库）；多重变换的组可能导入出错，可在 SketchUp 里先炸开再重新成组。License 字段 GitHub 没检测到 → 授权 **未验证**。来源：https://github.com/RedHaloStudio/Sketchup_Importer （README + releases）
- **martijnberger/sketchup_importer**（306★，0.24 "Blender 4.4" 发布于 2025-04-15，最后 push 2025-05）：README 写兼容 Blender 4.x、Python 3.11、SketchUp 文件到 2025.1。Blender 5.x **未验证**。来源：https://github.com/martijnberger/sketchup_importer
- 付费替代（不推荐）：SimLab SKP→Blender、SKP Editor、Easy Warehouse（Superhive）。来源：搜索结果 https://www.simlab-soft.com/3d-plugins/skp-to-blender-main.aspx 等。
- 次选：有 Go/Pro 时导出 FBX/DAE/OBJ（Go 起）或 glTF（Pro 起）进 Blender。
- 「基础 SketchUp 模型变电影」流程（建议，非来源事实）：导入 → 清理（合并重复材质、检查法线/背面）→ 换 PBR 材质（Poly Haven 免费）→ HDRI + 太阳光 → 相机路径动画 → Cycles/EEVEE 渲染；可衔接现有 `archviz`、`free-3d-assets` 技能。

---

## 4. Blender Geometry Nodes 立面（免费路线）

当前 API 文档版本：**Blender 5.2**（https://docs.blender.org/api/current/index.html 标题 "Blender 5.2 Python API Documentation"，2026-10-22）。

### 4.1 用 bpy 建节点组（4.0+ 接口，5.2 仍一致）
- 4.0 起节点组接口从 `tree.inputs/outputs` 移到 `tree.interface`。`socket_type` 只接受基础类型名，如 `NodeSocketFloat`（不接受 `NodeSocketFloatFactor`）。来源：https://developer.blender.org/docs/release_notes/4.0/python_api/
- 5.2 文档签名：`NodeTreeInterface.new_socket(name, *, description='', in_out='INPUT', socket_type='DEFAULT', parent=None)`；`new_panel(name, *, description='', default_closed=False)`；还有 `copy`、`remove(item, move_content_to_parent=True)`、`clear`、`move`、`move_to_parent`；遍历用 `items_tree`。来源：https://docs.blender.org/api/current/bpy.types.NodeTreeInterface.html
- `GeometryNodeTree` 属性：`is_modifier`、`is_tool`、`is_mode_object/edit/sculpt/paint`、`is_type_mesh/curve/pointcloud/grease_pencil`、`show_modifier_manage_panel` 等。来源：https://docs.blender.org/api/current/bpy.types.GeometryNodeTree.html
- `NodesModifier.node_group`、`bake_target`('PACKED'/'DISK')、`node_warnings` 等。来源：https://docs.blender.org/api/current/bpy.types.NodesModifier.html
- 5.0 API 变更里没有 Geometry Nodes 节点组/NodesModifier 的破坏性变更；相关改名是编辑器层面：`SpaceNodeEditor.geometry_nodes_type` → `node_tree_sub_type`，`geometry_nodes_tool_tree` → `selected_node_group`。来源：https://developer.blender.org/docs/release_notes/5.0/python_api/
- 5.0 新增：Bundle / Closure（Combine/Separate/Join Bundle、Closure Zone、Evaluate Closure）、大量 Grid/SDF 节点（SDF Grid Boolean、SDF Grid Fillet、Mesh to SDF Grid…）。可用于把立面参数打包成一个 Bundle（推论）。来源：https://developer.blender.org/docs/release_notes/5.0/geometry_nodes/
- 5.2 的 Realize Instances 有 `realize_to_point_domain`（「为兼容 5.0 及更早」）→ 5.1/5.2 行为有变，写技能时注意。来源：https://docs.blender.org/api/current/bpy.types.GeometryNodeRealizeInstances.html

最小骨架（API 已按上面核实；socket 名称按节点 UI 名称，执行前用 `node.inputs.keys()` 打印确认）：
```python
import bpy
ng = bpy.data.node_groups.new("Facade_Panels", "GeometryNodeTree")
ng.is_modifier = True
ng.interface.new_socket("Geometry", in_out='INPUT',  socket_type='NodeSocketGeometry')
ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
s = ng.interface.new_socket("Inset", in_out='INPUT', socket_type='NodeSocketFloat'); s.default_value = 0.1
n = ng.nodes
gin  = n.new("NodeGroupInput"); gout = n.new("NodeGroupOutput")
ext  = n.new("GeometryNodeExtrudeMesh"); ext.mode = 'FACES'
ng.links.new(gin.outputs["Geometry"], ext.inputs["Mesh"])
ng.links.new(ext.outputs["Mesh"], gout.inputs["Geometry"])
mod = bpy.context.object.modifiers.new("Facade", 'NODES'); mod.node_group = ng
```
（`ext.inputs["Mesh"]` 等 socket 名 **未逐个验证**。）

### 4.2 已核实存在的节点 bl_idname（5.2 文档页 HTTP 200）
- 面板/网格：`GeometryNodeMeshGrid`、`GeometryNodeSubdivideMesh`、`GeometryNodeDualMesh`、`GeometryNodeTriangulate`、`GeometryNodeSplitEdges`、`GeometryNodeExtrudeMesh`（mode: VERTICES/EDGES/FACES）、`GeometryNodeScaleElements`（domain FACE/EDGE → 面板缩小留缝 = inset 效果）、`GeometryNodeFlipFaces`、`GeometryNodeDeleteGeometry`、`GeometryNodeSeparateGeometry`、`GeometryNodeMeshBoolean`、`GeometryNodeEdgesToFaceGroups`、`GeometryNodeMeshFaceSetBoundaries`、`GeometryNodeSplitToInstances`
- 平面度：`GeometryNodeInputMeshFaceIsPlanar`（"Retrieve whether all triangles in a face are on the same plane"）、`GeometryNodeInputMeshFaceArea` → 可做「非平面板高亮 / 统计」
- 散布/实例：`GeometryNodeDistributePointsOnFaces`（distribute_method RANDOM/POISSON）、`GeometryNodeInstanceOnPoints`、`GeometryNodeMeshToPoints`、`GeometryNodeRotateInstances`、`GeometryNodeScaleInstances`、`GeometryNodeTranslateInstances`、`GeometryNodeRealizeInstances`、`GeometryNodeCollectionInfo`、`GeometryNodeObjectInfo`、`FunctionNodeAlignRotationToVector`（注意：不是 GeometryNode 前缀）
- 曲线（竖梃/鳍片）：`GeometryNodeMeshToCurve`（面边→曲线）、`GeometryNodeCurveToMesh`（扫掠剖面）、`GeometryNodeCurvePrimitiveQuadrilateral`（矩形剖面）、`GeometryNodeResampleCurve`、`GeometryNodeSampleCurve`、`GeometryNodeFillCurve`、`GeometryNodeCurveSpiral`、`GeometryNodeMeshLine`
- 属性驱动变化：`GeometryNodeInputPosition`、`GeometryNodeInputNormal`、`GeometryNodeInputIndex`、`FunctionNodeRandomValue`、`GeometryNodeProximity`（Geometry Proximity → 吸引点/吸引线距离）、`GeometryNodeSampleNearestSurface`、`GeometryNodeSampleIndex`、`GeometryNodeStoreNamedAttribute`、`GeometryNodeInputNamedAttribute`、`GeometryNodeSetPosition`
- 控制流：`GeometryNodeRepeatInput`（Repeat Zone → 楼板堆叠）、`GeometryNodeForeachGeometryElementInput`（For Each Element Zone）、`GeometryNodeMenuSwitch`、`GeometryNodeIndexSwitch`
- 其他：`GeometryNodeTransform`、`GeometryNodeJoinGeometry`、`GeometryNodeSetMaterial`、`GeometryNodeBoundBox`、`GeometryNodePointsToVertices`
- ✗ 不存在：`GeometryNodeAlignRotationToVector`、`GeometryNodeGrid`（404）。

### 4.3 立面配方（技术组合；是方法建议，非单一来源）
1. **曲面面板化**：曲面网格（或 Grid + Set Position 弯曲）→ Split Edges → Scale Elements（FACE，按 Proximity 映射缩放 = attractor 开孔）→ Extrude Mesh（individual，做板厚）。
2. **平板合理化检查**：Is Face Planar → 不平的板 Store Named Attribute 标红 / 或 Triangulate 只三角化不平的板。
3. **竖梃/横梃**：Mesh to Curve（全部边或只竖向边：用 Normal/边方向点积筛选）→ Curve to Mesh + Quadrilateral 剖面。
4. **遮阳鳍片**：Mesh to Points（面中心）→ Instance on Points（鳍片对象，旋转 = 法线对齐 Align Rotation to Vector + Random Value/Proximity 驱动角度）→ Realize Instances（导出前）。
5. **楼板堆叠**：Repeat Zone 或 Mesh Line（Count=层数、Offset=层高）→ Instance on Points 实例楼板轮廓 → Fill Curve + Extrude。
6. **模块体块分布**：Distribute Points on Faces（POISSON 控制最小间距）或 Grid 点 → Instance on Points（Collection Info 多个模块，Pick Instance + Random/Index 选模块）。
7. 曲面上做「等宽条带」可展开近似：沿一个方向 Resample 曲线 + 直纹 loft（推论；Blender 没有内建「可展开」验证，只能用 Is Face Planar 近似检查）。

### 4.4 免费学习资源
- Blender 官方手册 Geometry Nodes：https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html （200）
- Distribute Points on Faces 手册页：https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/point/distribute_points_on_faces.html （200）
- Blender Python API（5.2）：https://docs.blender.org/api/current/
- 免费 GN 建筑生成器（可拆开学习）：Alexey Yakovlev 的 Post-Soviet Building Generator（Blender 2.93+，免费）https://80.lv/articles/free-post-soviet-building-generator-for-blender/ ；makshiz Procedural Building Generator（Blender 4.3.x，价格 **未验证**）https://makshiz.itch.io/procedural-skyscraper
- 付费的（只列出、不推荐）：Nodee Buildings $59.99（非商用）、70S Office Curtain Wall Generator $4 等（Superhive）。
- 专门「GN 立面」免费系统教程：搜索没找到权威单一来源 → 技能里应自己写配方并实测。

---

## 5. 给三个技能的要点

**rhino-mcp**
- 推荐 McNeel 官方 RhinoAI（Rhino-MCP-Platform，MIT，Rhino 8/9 WIP）；备选 tanishqbhattad（有 safe/standard/developer 安全闸门）。
- 必须先问：Rhino 付费（$995 / 90 天试用到期后不能保存、插件不能加载）、会装 Rhino 插件、`run_python`/`run_csharp`/`run_command` 任意执行、`open_doc`/`save_doc` 能读写任何文件、视口截图会发给 Claude。
- 代码写法：`run_python` 用 `__rhino_doc__`；先 `get_context` 再动手；GH 用 `g1_apply_graph` 一次搭好。
- 不用 Replicate 等付费渲染 API。

**sketchup-mcp**
- 官方 connector：云端、Trimble ID 登录、免费额度 30 个（总数还是每月有矛盾）、只新建、产出 .skp 下载链接；工具名以连接后实际为准。
- 开源：zinin/sketchup-mcp2（MIT、最新）需 SketchUp 桌面版（Pro 起，付费）；`eval_ruby` 默认开，建议关。
- 免费路线：.skp → RedHaloStudio/Sketchup_Importer（Blender 5.1 alpha 支持，Windows/Mac）→ Blender 做电影感（衔接 `archviz`）。SketchUp Free 只能导 STL。

**parametric-facade**
- 全部用 Blender 5.x Geometry Nodes + bpy（通过 blender MCP 的 execute_blender_code，用前先问）。
- 4.0+ `tree.interface.new_socket(...)`；`ng.is_modifier = True`；`FunctionNodeAlignRotationToVector`；Realize Instances 5.1+ 行为有变。
- 必有检查：Is Face Planar 统计非平面板；面板/竖梃/鳍片都要坐在基面上（呼应 LESSONS「不能悬空」）。
