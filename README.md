# T1 — Claude Code / Cowork Skills 合集

用 Claude Code 打开这个仓库时，`.claude/settings.json` 会自动登记 6 个插件市场，并提示你安装下面已启用的插件；`.claude/skills/` 里的技能直接可用，不用安装。

## 已启用的插件（56 个，`.claude/settings.json`）

| 来源 | 插件 |
|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | `document-skills`、`example-skills`、`claude-api`、`academy-guide` |
| [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace) | `superpowers` |
| [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) | `playwright-skill`（首次使用需在插件目录跑 `npm run setup`） |
| [phuryn/pm-skills](https://github.com/phuryn/pm-skills) | 全部 9 个 `pm-*` 插件 |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 44 个中的 41 个（见下方"刻意没启用"） |

`anthropics/knowledge-work-plugins` 只登记了市场，没有默认启用，原因见下。

## 直接放进仓库的技能（44 个，`.claude/skills/`）

- **FiveM**：`fivem-pro`（[leminhhuy113/fivem-pro](https://github.com/leminhhuy113/fivem-pro)，MIT）讲开发、性能优化，以及用 Sollumz + CodeWalker 做地图/MLO；`fivem-security-audit`（[matiaspalmac/fivem-audit-skill](https://github.com/matiaspalmac/fivem-audit-skill)，MIT）查后门、漏洞、性能问题
- **Blender 建模 / 模型优化 / 动作**：从 [arjun988/blender-skills](https://github.com/arjun988/blender-skills)（MIT）挑了 7 个：retopology、lod-pipeline、asset-optimization、uv-workflow、rigging、animation、export-pipeline。需要下面的 Blender MCP

- 21 个 Cowork 技能，来自 [EAIconsulting/cowork-skills-library](https://github.com/EAIconsulting/cowork-skills-library)（MIT）
- 14 个通用技能，来自 [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)（Apache-2.0）：changelog-generator、competitive-ads-extractor、content-research-writer、developer-growth-analysis、domain-name-brainstormer、file-organizer、image-enhancer、invoice-organizer、langsmith-fetch、lead-research-assistant、meeting-insights-analyzer、raffle-winner-picker、tailored-resume-generator、video-downloader

来源与许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## Blender MCP（`.mcp.json`）

Blender 技能要在你自己的电脑上跑，Claude 通过 [MCP for Blender](https://github.com/ahujasid/blender-mcp)（MIT，免费）操作 Blender。已在 `.mcp.json` 里设置好，并关闭了匿名统计（`DISABLE_TELEMETRY`）。

1. 装 [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. 运行 `uvx mcp-for-blender install-addon`，然后在 Blender 的 Edit → Preferences → Add-ons 里启用 "MCP for Blender"
3. 在 Blender 3D 视图按 N，在侧边栏里点启动服务
4. 在 T1 里打开 Claude Code，同意启用 `blender` 这个 MCP 服务

不要开它的付费功能（Premium 的 AI 生成 3D 模型）；Sketchfab、Poly Haven 这些免费素材可以用。做 GTA 模型时，在 Blender 里完成后再用 [Sollumz](https://github.com/Sollumz/Sollumz) 导出成 .ydr/.yft/.ycd。

## 在 Cowork 里安装

Cowork 的插件只能在 Cowork 界面里装：打开 [claude.com/plugins](https://claude.com/plugins/)，安装 Productivity、Sales、Marketing、Data 等职能插件。
EAIconsulting 的 21 个技能也可以打包上传到 Cowork（Settings → Capabilities → Skills），每个技能文件夹就是一个 skill。

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
| arjun988/blender-skills 其余 87 个技能 | 只挑了建模优化和动作相关的，避免技能列表过长 |
| wojzj57/fiveai-skills | 没有许可证 |
| CodeCrafter98/fivem-agent-skills | 43 个技能太多，内容和 fivem-pro 重叠 |
