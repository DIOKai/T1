# T1 — Claude Code / Cowork Skills 合集

用 Claude Code 打开这个仓库时，`.claude/settings.json` 会自动登记 8 个插件市场，并提示你安装下面已启用的插件；`.claude/skills/` 里的技能直接可用，不用安装。

## 已启用的插件（16 个，`.claude/settings.json`）

| 来源 | 插件 |
|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | `document-skills`、`example-skills`、`claude-api`、`academy-guide` |
| [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace) | `superpowers` |
| [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) | `playwright-skill`（首次使用需在插件目录跑 `npm run setup`） |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 8 个和 FiveM（Lua/JS/Python）、GitHub 有关的：`sharp-edges`、`insecure-defaults`、`differential-review`、`static-analysis`、`supply-chain-risk-auditor`、`variant-analysis`、`git-cleanup`、`code-improver` |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `taste-skill`（MIT）：让网页、界面不像 AI 套模板。主技能 `design-taste-frontend`，另有 redesign（旧站改造）、minimalist、soft、brutalist 等风格，以及 `brandkit`、`imagegen-frontend-*` 这类出参考图的技能（要配 ChatGPT Images 之类的生图工具，Claude Code 自己不能生图） |
| [B7Kompirine/muto-atlas](https://github.com/B7Kompirine/muto-atlas) | `muto-atlas`：GTA V / FiveM 资料库（车辆骨骼名、碰撞 flag、Sollumz/CodeWalker 常见坑、原版车规格），19 个指令，要先建资料库（见下） |

`anthropics/knowledge-work-plugins` 和 `phuryn/pm-skills` 只登记了市场，没有默认启用，原因见下。要用时 `claude plugin install <插件>@<市场>`。

## 直接放进仓库的技能（65 个，`.claude/skills/`）

- **FiveM**：`fivem-pro`（[leminhhuy113/fivem-pro](https://github.com/leminhhuy113/fivem-pro)，MIT）讲开发、性能优化，以及用 Sollumz + CodeWalker 做地图/MLO；`fivem-security-audit`（[matiaspalmac/fivem-audit-skill](https://github.com/matiaspalmac/fivem-audit-skill)，MIT）查后门、漏洞、性能问题
- **FiveM ox 系列和 NUI**：oxlib、oxmysql、ox-inventory、ox-target（[germanfndez/fiveai-skills](https://github.com/germanfndez/fiveai-skills)，MIT）；fivem-react-nui（[proelias7/fivem-skill](https://github.com/proelias7/fivem-skill)，MIT），用 React + TypeScript + Vite + Tailwind 做 NUI
- **车辆模组**：`fivem-vehicle-mod`（本仓库自己写的）——addon 车资源的结构、meta 文件、改装套件、涂装、警笛、贴图/大小限制、GTA V Enhanced 转换、故障排查；模组车在 Blender + Sollumz 里怎么做（用原版车当底、骨骼、车漆层、灯光 ID、车窗、LOD）；模组警车/救护车/消防车（siren 骨骼和 carcols 警灯设置、extras、涂装、qbx_police/qb-policejob 配置、Renewed-Sirensync 等警笛控制和自定义警笛声），附 `check_vehicle_resource.py` 交叉检查脚本（检查名字对不对得上、改装套件/警笛 id 撞号、无效的 data_file 类型）。资料来自 FiveM 源码和官方文档源码。配合免费工具：[fivem-vehicle-validator](https://github.com/PrestigeRoleplay/fivem-vehicle-validator)、[fivem-handling-presets](https://github.com/PrestigeRoleplay/fivem-handling-presets)、[fivem-joaat-hash](https://github.com/PrestigeRoleplay/fivem-joaat-hash)（都用 npx 跑）和游戏内调 handling 的 [vehicleDebug](https://github.com/kerminal/vehicleDebug)（放进测试服 resources）
- **FiveM 动画**：`fivem-animation`（本仓库自己写的）——Blender → Sollumz（.ycd.xml）→ CodeWalker（.ycd）→ FiveM，用 rpemotes-reborn 自定义表情或 TaskPlayAnim 播放；GTA 骨骼 tag、30 fps、四元数、烘焙、mover、clip Hash/Duration、道具挂载、故障排查，附 `check_anim_resource.py` 检查脚本。资料来自 Sollumz、CodeWalker、FiveM 源码、citizenfx/natives 和 rpemotes 源码
- **画质包**：`fivem-graphics-pack`（本仓库自己写的）——三种画质包：伺服器端的色调（timecycle modifier 做暖色/冷色/电影感/写实，玩家自动拿到、可用 `/graphics` 切换或关掉）、visualsettings（车灯、夜间灯光）、2K/4K 贴图替换（内存计算、16/48 MiB 限制、`+hi` 只在"非常高"贴图画质下加载、车辆贴图默认被限到 1024），以及玩家自己装的 ReShade（FiveM 的 plugins 文件夹、ReShade 5 要在 CitizenFX.ini 加确认行、LUT 调色）。附三个脚本：`make_timecycle_pack.py`（一键生成画质包资源）、`make_lut.py`（生成 ReShade LUT，预设 warm/cool/cinematic/realistic/vivid/noir）、`check_graphics_pack.py`（检查 numMods、拼错的变量、没注册的 XML、按 RSC 头算的贴图内存）。资料来自 FiveM 源码（TimecycleEditor、VisualSettingsNatives、ReShadeFixups、TextureStreamingLimits、ResourceStreamComponent）、citizenfx/natives 和 ReShade 的 LUT.fx。只推荐免费工具（NVE、QuantV、iMMERSE Pro 要付费，不用）
- **室内和房屋**：`fivem-mlo-housing`（本仓库自己写的）——三种室内怎么选（MLO、原版 IPL、shell），用 Blender + Sollumz + CodeWalker 做 MLO（limbo、房间、portal、实体、entity set、房间 timecycle、门、碰撞、顶点色灯光、`_manifest.ymf`、ht_mlotool 声音遮挡），在脚本里切换 entity set 和 IPL，以及 qbx_properties / qb-houses / ps-housing 怎么用 shell 和公寓、家具摆放和授权。附 `check_mlo_resource.py`，检查 this_is_a_map、manifest、portal 连错房间、房间没 portal、实体没放进房间（进屋看不到）、门的 flag、ymap extents、撞名。资料来自 Sollumz wiki 和源码、FiveM 官方资产教程和源码、citizenfx/natives 以及各房屋脚本自己的代码
- **记住纠正**：`correction-memory`（本仓库自己写的）——你说我哪里做错、或说"下次/记住…"时，先改好，再把规则写进仓库根目录的 `LESSONS.md`。CLAUDE.md 用 `@LESSONS.md` 导入它，所以以后每次对话都会自动读到。新对话从 main 开始，所以经验要合并进 main 才生效
- **界面美化**：`impeccable`（[pbakaus/impeccable](https://github.com/pbakaus/impeccable)，Apache 2.0）——在 Anthropic 的 frontend-design 基础上加强，1 个技能 24 个指令：`/impeccable audit`（找问题）、`critique`（设计点评）、`polish`（最后润色）、`animate`（加动效）、`bolder`/`quieter`（更大胆/更低调）、`colorize`、`typeset`、`layout` 等。它的 4 个子代理放在 `.claude/agents/`。**只装了技能本体，没装它插件里的 hook**：那些 hook 会在每次开对话、每次改文件、每次回答结束时自动跑它的程序，违反"用技能前一律先问"，改 FiveM Lua 时也会跑。第一次用到它的检查程序时，会从 impeccable 的 GitHub 下载对应平台的程序并校验 sha256。搭配已装的 `frontend-design`（网页界面）和 `canvas-design`（海报、静态图），做 FiveM NUI 时最有用
- **做视频（Remotion）**：`remotion-best-practices` 等 12 个技能（[remotion-dev/skills](https://github.com/remotion-dev/skills)），用 React 写代码做视频。那个仓库没有授权文件，所以没有复制进 T1；在自己电脑上用 `python scripts/install_local.py --remotion` 安装（会执行 Remotion 官方的 `npx skills add remotion-dev/skills`，并关掉它的追踪），云端对话里没有。Remotion 本身个人和 3 人以下公司免费，4 人以上要付费授权
- **土木工程**：quantity-surveyor（[MuscleOtter/quantity-surveyor](https://github.com/MuscleOtter/quantity-surveyor)，MIT），算工程量、BOQ、单价分析、投标、变更、现金流
- **室内设计（Blender）**：set-dressing、archviz、prop-artist、environment-artist（[arjun988/blender-skills](https://github.com/arjun988/blender-skills)，MIT）——室内布置、真实尺寸和灯光、家具道具、模块化房间
- **动画**：motion-design（[LobzyJay/motion-design-with-claude](https://github.com/LobzyJay/motion-design-with-claude)，MIT）——12 条动画原则、时间和间距、缓动；blender-animation-rigging（[ra100/blender-claude-plugin](https://github.com/ra100/blender-claude-plugin)，MIT）——Blender 5.x 关键帧、曲线编辑器、NLA、驱动器、约束、IK/FK、形态键
- **游戏设计**：game-balance-economy、game-interface-feedback（[LVTD-LLC/skills](https://github.com/LVTD-LLC/skills)，MIT）——经济与数值平衡（工作收入、抢劫奖励、声望曲线）、界面反馈和小游戏手感
- **Blender 建模 / 模型优化 / 动作**：从 [arjun988/blender-skills](https://github.com/arjun988/blender-skills)（MIT）挑了 11 个：retopology、lod-pipeline、asset-optimization、uv-workflow、rigging、animation、export-pipeline，以及做车用的 vehicle-artist、hard-surface、collision-proxy、texture-workflow。需要下面的 Blender MCP

- 20 个 Cowork 技能，来自 [EAIconsulting/cowork-skills-library](https://github.com/EAIconsulting/cowork-skills-library)（MIT）
- 12 个通用技能，来自 [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)（Apache-2.0）：changelog-generator、competitive-ads-extractor、content-research-writer、domain-name-brainstormer、file-organizer、image-enhancer、invoice-organizer、lead-research-assistant、meeting-insights-analyzer、raffle-winner-picker、tailored-resume-generator、video-downloader

来源与许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## Blender MCP（`.mcp.json`）

Blender 技能要在你自己的电脑上跑，Claude 通过 [MCP for Blender](https://github.com/ahujasid/blender-mcp)（MIT，免费）操作 Blender。已在 `.mcp.json` 里设置好，并关闭了匿名统计（`DISABLE_TELEMETRY`）。

1. 装 [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. 运行 `uvx mcp-for-blender install-addon`，然后在 Blender 的 Edit → Preferences → Add-ons 里启用 "MCP for Blender"
3. 在 Blender 3D 视图按 N，在侧边栏里点启动服务
4. 在 T1 里打开 Claude Code，同意启用 `blender` 这个 MCP 服务

不要开它的付费功能（Premium 的 AI 生成 3D 模型）；Sketchfab、Poly Haven 这些免费素材可以用。做 GTA 模型时，在 Blender 里完成后再用 [Sollumz](https://github.com/Sollumz/Sollumz) 导出成 .ydr/.yft/.ycd。

## 其他 MCP 服务（`.mcp.json`，都免费）

| 服务 | 作用 | 你要准备的 |
|---|---|---|
| `fivem` | [fivem-mcp](https://github.com/ziyacivan/fivem-mcp)：让 Claude 看你测试服的后台、F8 日志、截图、调用 native | Node 22+；`server.cfg` 设 `rcon_password`，再把同一个密码设成环境变量 `FIVEM_RCON_PASSWORD`。**只连本机测试服**，它权限很大 |
| `freecad` | [freecad-mcp](https://github.com/neka-nat/freecad-mcp)：操作 FreeCAD 建模、跑 FEM 结构分析 | [FreeCAD](https://www.freecad.org/)（免费）；把 `addon/FreeCADMCP` 复制到 FreeCAD 的 Mod 文件夹，选 **MCP Addon** 工作台，点 **Start RPC Server** |
| `ifc` | [IfcOpenShell ifcmcp](https://docs.ifcopenshell.org/ifcmcp.html)：不用 Revit 也能查、改 BIM/IFC 模型，算工程量 | 只要 uv |

用不到的服务，Claude Code 第一次问要不要启用时选不启用就行。

## qbx-lint（Qbox 官方 Lua 检查工具）

[Qbox-project/qbx-lua](https://github.com/Qbox-project/qbx-lua)（GPL-3.0，免费）会按 fxmanifest 分清 client/server/shared，检查 FiveM Lua 的错误。

1. 到 [Releases](https://github.com/Qbox-project/qbx-lua/releases) 下载 `qbx-lint-<你的系统>`，解压后把 `qbx-lint.exe` 放进 PATH 里的文件夹
2. 在资源文件夹里跑 `qbx-lint` 检查，`qbx-lint fmt` 排版
3. 用 VS Code 的话装 [Qbox Lua](https://marketplace.visualstudio.com/items?itemName=Qbox.qbx-lua) 扩展

装好后，Claude 改完 Lua 会自动跑 `qbx-lint` 检查。

NUI 起手模板（免费）：[fivem-react-boilerplate-lua](https://github.com/project-error/fivem-react-boilerplate-lua)

## 房屋相关的 FiveM 资源（放进你的伺服器，不是装进 T1，都免费）

| 资源 | 作用 | 许可证 |
|---|---|---|
| [bob74_ipl](https://github.com/Bob74/bob74_ipl) | 加载原版室内（公寓、办公室、夜店等）和切换 entity set | MIT |
| [qbx_properties](https://github.com/Qbox-project/qbx_properties) | Qbox 官方房屋系统，可以买房、装修 | GPL-3.0 |
| [object_gizmo](https://github.com/Demigod916/object_gizmo) | 通用的游戏内 3D 移动、旋转物件工具，给自己写的家具或道具摆放用。qbx_properties 自带装修工具，不需要它 | GPL-3.0 |

安装步骤：
1. **qbx_properties 先清掉旧系统**（照它 README）：从伺服器移除 `qbx_apartments` 和 `qbx_houses`；出生点不要用别的公寓选择系统（用 [qbx_spawn](https://github.com/Qbox-project/qbx_spawn) 或不用出生系统）。
2. 下载（在伺服器的 `resources` 文件夹里）：
   ```
   git clone https://github.com/Bob74/bob74_ipl
   git clone https://github.com/Qbox-project/qbx_properties
   git clone https://github.com/Demigod916/object_gizmo   # 需要时才装
   ```
   不用 git 的话，到 GitHub 页面点 **Code → Download ZIP**，解压后把文件夹名后面的 `-main` 去掉。
3. 把 qbx_properties 里的 3 个 SQL 文件导入数据库：`property.sql`、`property_garages.sql`、`decorations.sql`（用 HeidiSQL 之类的工具执行）。
4. 在 `server.cfg` 里加（放在 `oxmysql`、`ox_lib`、`qbx_core` 之后）：
   ```
   ensure bob74_ipl
   ensure qbx_properties
   ensure object_gizmo   # 需要时才加
   ```
5. 重启伺服器，看控制台有没有报错。设定在各资源的 `config` 文件夹里。

不要用付费的 bcs_housing、qs-housing、nolag_properties；ps-housing 是 CC BY-NC-SA（禁止商用）而且已经停止维护。

## muto-atlas 资料库（在你自己的电脑上建一次）

插件本身不带游戏资料，要用你电脑上的 GTA V 和 CodeWalker 建资料库：

1. 在 T1 里打开 Claude Code，同意安装 muto-atlas 插件
2. 输入 `/asset-setup`，按提示填 GTA V 路径、`CodeWalker.Core.dll` 路径、你的服务器 `resources` 路径

会跑本地 Python/PowerShell 脚本，并从 GitHub 和 runtime.fivem.net 下载公开的 GTA/FiveM 资料（免费）。不要用 `build_atlas_db.py --tagger claude`，那要付费的 Anthropic API key；用 `--tagger rules`。

做车辆可以参考：[awesome-fivem-vehicles](https://github.com/PrestigeRoleplay/awesome-fivem-vehicles)、[Sollumz 车辆制作教程](https://sollumz.com/2026/06/16/sollumz-vehicle-creation-guide-for-gta-v-fivem/)。

## 在 Cowork 里安装

Cowork 的插件只能在 Cowork 界面里装：打开 [claude.com/plugins](https://claude.com/plugins/)，安装 Productivity、Sales、Marketing、Data 等职能插件。
EAIconsulting 的 20 个技能也可以打包上传到 Cowork（Settings → Capabilities → Skills），每个技能文件夹就是一个 skill。

## 按需再装（已登记市场，一条命令即可）

```bash
# knowledge-work-plugins 里的职能插件（每个都带很多 MCP 连接器）
claude plugin install productivity@knowledge-work-plugins
claude plugin install engineering@knowledge-work-plugins
claude plugin install data@knowledge-work-plugins

# superpowers 的扩展
claude plugin install elements-of-style@superpowers-marketplace
claude plugin install episodic-memory@superpowers-marketplace
```

## 在自己电脑上用（local 模式）

### 每台电脑一行命令（推荐）

**Windows**（开 PowerShell，贴这一行）：
```
irm https://raw.githubusercontent.com/DIOKai/T1/main/scripts/setup.ps1 | iex
```
**Mac / Linux**：
```
curl -fsSL https://raw.githubusercontent.com/DIOKai/T1/main/scripts/setup.sh | sh
```

它会把 T1 下载到 `你的用户文件夹\T1`（已经有了就更新），然后执行 `install_local.py --all --auto-update`，也就是装好下面所有东西，再加一个**自动更新**：之后每次打开 Claude Code，它会在后台 `git pull` T1 并重新链接技能。所以你在一台电脑（或云端）加的技能、记下的经验，合并进 main 以后，其他电脑下次打开 Claude Code 就会有，不用每台再装一次。
- 没网络、或那台电脑的 T1 有没提交的改动时，它什么也不做，不会影响打开 Claude Code
- T1 里新启用的**插件**不会自动装（要用 `claude` 命令装，比较慢）：自动更新发现有新插件时，会提醒你跑 `install_local.py --plugins`
- 要先装 Git 和 Python 3；缺了会告诉你用 `winget install` 装哪个。Remotion 和 fivem MCP 还要 Node.js
- 第一次在某个文件夹打开 Claude Code 时会问你要不要信任这个文件夹，选"是"，自动更新才会跑（Claude Code 的安全规则）
- 不想自动更新：`python scripts/install_local.py --uninstall` 会连同自动更新一起移除，之后再跑一次不加 `--auto-update` 的安装即可

### 手动安装

在 T1 文件夹里开 local 会话，会直接读到这里的技能、规则和插件设置（第一次会问你要不要信任这个文件夹）。在**别的文件夹**开 local 会话，比如 FiveM 伺服器、Blender 项目，就只会读你电脑上的 `~/.claude`（Windows 是 `C:\Users\你的名字\.claude`）。所以要跑一次安装脚本：

```
git clone https://github.com/DIOKai/T1
cd T1
python scripts/install_local.py --dry-run --all   # 先看会做什么
python scripts/install_local.py --all             # 技能 + 规则 + 插件 + MCP + Remotion
```

它会做这些事：
- 把 65 个技能链接到 `~/.claude/skills/`。用的是链接不是复制，以后在 T1 里 `git pull`，技能就跟着更新；你自己建的同名技能不会被覆盖
- 在 `~/.claude/CLAUDE.md` 加一段，导入 T1 的 `CLAUDE.md`（它再导入 `LESSONS.md`），所以在哪个文件夹都用同一套规则，包括"用技能前一律先问"。原来的 CLAUDE.md 会先备份成 `CLAUDE.md.bak`
- `--plugins`：用 `claude` 命令把 16 个插件装到用户范围
- `--mcp`：把 blender、fivem、freecad、ifc 四个 MCP 加到用户范围（要先装 uv 和 Node.js）
- `--remotion`：装 Remotion 的 12 个做视频技能（要先装 Node.js）
- `.claude/agents/` 里的子代理（impeccable 的 4 个）也会一起链接到 `~/.claude/agents/`

只加 `--plugins` 或 `--mcp` 就只装那一部分，不加就只装技能和规则。`git pull` 之后再跑一次就会加上新技能、移除已删掉的技能。`--uninstall` 会移除链接和那段规则。Windows 不用管理员权限，链接做不了时会自动改用 junction。需要 Python 3（技能自带的检查脚本本来也要用）。

## OpenAI Codex 也能用

Codex 不读 `CLAUDE.md` 和 `.claude/skills/`，它读 `AGENTS.md` 和 `.agents/skills/`。所以：

- `AGENTS.md` 让 Codex 先读 `CLAUDE.md` 和 `LESSONS.md`，两边用同一套规则和同一份纠正记录。
- `.agents/skills` 是指向 `.claude/skills` 的链接（symlink），64 个技能两边共用，不会有两份内容不同步。
- 插件（superpowers、muto-atlas 等）和 MCP 是 Claude Code 专用的，Codex 里没有。
- Windows 上 clone 时，git 默认可能把链接变成普通文本文件：用 `git clone -c core.symlinks=true …` 并开启 Windows 开发者模式。Codex 云端（Linux）不受影响。

## 刻意没启用的

| 插件 | 原因 |
|---|---|
| knowledge-work-plugins 的全部插件 | 主要为 Cowork 设计；16 个职能插件合计约 170 个 MCP 连接器、180 多个技能，全部在 Claude Code 里启用会拖慢启动并挤占技能列表 |
| `phuryn/pm-skills` 的 9 个插件 | 产品经理用的（PRD、OKR、市场分析），和 FiveM 无关；每次对话开头的技能说明约占 5,800 token |
| trailofbits 其余 30 个插件 | 智能合约、C/C++、Rust、Android、Lean、二进制分析、塔罗牌等，和 FiveM 无关；关掉后每次对话开头少读约 6,800 token |
| `discernment-nudge@anthropic-agent-skills` | 会在每个回答后面追加追问 |
| `gh-cli@trailofbits` | hook 会拦截所有 GitHub 网页抓取改走 `gh` |
| `modern-python@trailofbits` | 会在 PATH 里放 shim，拦截 `pip`/`python` 命令 |
| `fp-check@trailofbits` | 每次回答结束都会多跑一次 LLM 检查 |
| Composio 的 836 个 `*-automation` 技能 | 都需要 Composio 账号和 API key |
| `skill-share`、`twitter-algorithm-optimizer`（Composio） | 许可证缺失或为 AGPL |
| hesreallyhim/awesome-claude-code、travisvn/awesome-claude-skills | 只是链接清单，没有可安装的技能 |
| ErinSpringmeyer/skills | 仓库目前是空的 |
| Nano Banana 等生图技能 | 要付费的 API key |
| `burpsuite-project-parser@trailofbits` | 要 Burp Suite Professional（付费） |
| `second-opinion@trailofbits` | 要 OpenAI Codex 或 Gemini CLI 账号 |
| `culture-index@trailofbits` | 要付费的 Culture Index 测验结果 |
| `dispatch-starter`（EAIconsulting） | 要 Cowork Max 方案 |
| `developer-growth-analysis`（Composio） | 要 Composio Rube 账号和 Slack |
| `langsmith-fetch`（Composio） | 要 LangSmith 账号，只对 LangChain 开发有用 |
| arjun988/blender-skills 其余 87 个技能 | 只挑了建模优化和动作相关的，避免技能列表过长 |
| wojzj57/fiveai-skills | 没有许可证 |
| CodeCrafter98/fivem-agent-skills | 43 个技能太多，内容和 fivem-pro 重叠 |
| germanfndez/fiveai-skills 其余技能 | `fivemanage` 是付费服务；其他和 fivem-pro 重叠 |
| proelias7/fivem-skill 其余技能 | 和 fivem-pro 重叠，ESX/vRP 用不到 |
| AutoCAD、Revit、Civil 3D、ETABS 相关的 MCP | 软件本身要付费 |
