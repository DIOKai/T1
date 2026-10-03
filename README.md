# T1 — Claude Code / Cowork Skills 合集

用 Claude Code 打开这个仓库时，`.claude/settings.json` 会自动登记 6 个插件市场，并提示你安装下面已启用的插件；`.claude/skills/` 里的技能直接可用，不用安装。

## 已启用的插件（54 个，`.claude/settings.json`）

| 来源 | 插件 |
|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | `document-skills`、`example-skills`、`claude-api`、`academy-guide` |
| [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace) | `superpowers` |
| [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) | `playwright-skill`（首次使用需在插件目录跑 `npm run setup`） |
| [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | 全部 9 个 `pm-*` 插件 |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 44 个中的 38 个（见下方"刻意没启用"） |
| [B7Kompirine/muto-atlas](https://github.com/B7Kompirine/muto-atlas) | `muto-atlas`：GTA V / FiveM 资料库（车辆骨骼名、碰撞 flag、Sollumz/CodeWalker 常见坑、原版车规格），19 个指令，要先建资料库（见下） |

`anthropics/knowledge-work-plugins` 只登记了市场，没有默认启用，原因见下。

## 直接放进仓库的技能（51 个，`.claude/skills/`）

- **FiveM**：`fivem-pro`（[leminhhuy113/fivem-pro](https://github.com/leminhhuy113/fivem-pro)，MIT）讲开发、性能优化，以及用 Sollumz + CodeWalker 做地图/MLO；`fivem-security-audit`（[matiaspalmac/fivem-audit-skill](https://github.com/matiaspalmac/fivem-audit-skill)，MIT）查后门、漏洞、性能问题
- **FiveM ox 系列和 NUI**：oxlib、oxmysql、ox-inventory、ox-target（[germanfndez/fiveai-skills](https://github.com/germanfndez/fiveai-skills)，MIT）；fivem-react-nui（[proelias7/fivem-skill](https://github.com/proelias7/fivem-skill)，MIT），用 React + TypeScript + Vite + Tailwind 做 NUI
- **土木工程**：quantity-surveyor（[MuscleOtter/quantity-surveyor](https://github.com/MuscleOtter/quantity-surveyor)，MIT），算工程量、BOQ、单价分析、投标、变更、现金流
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

## 刻意没启用的

| 插件 | 原因 |
|---|---|
| knowledge-work-plugins 的全部插件 | 主要为 Cowork 设计；16 个职能插件合计约 170 个 MCP 连接器、180 多个技能，全部在 Claude Code 里启用会拖慢启动并挤占技能列表 |
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
