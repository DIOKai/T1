# Civil 3D Malaysia 技能批次 — 2026-10-27

用户要求：网上学习 Civil 3D，按马来西亚要求整理，上传 T1 供 Codex 与 Claude 使用；不改无关内容。

## 新增内容

新增 `.claude/skills/civil3d-malaysia/`：主技能、马来西亚依据、测量/土方、道路/排水、自动化、来源与学习路线、JSON 元数据模板、只读检查器及离线测试。`agents/openai.yaml` 提供 Codex 显示名称和默认提示词。

沿用仓库现有 `.agents/skills -> ../.claude/skills`（Git mode 120000，原 blob 不变），因此 Codex 与 Claude 共用相同技能正文。`CLAUDE.md` 的土木工程部分仅补一条相关路由/重叠优先级。没有修改已有技能、安装器、其他代理配置或 README 统计。

## 研究与来源

[来源与学习记录](../../.claude/skills/civil3d-malaysia/references/sources-and-learning.md) 列出具体官方 URL、检索日期和读取限制。已读 Autodesk 设计条件、走廊面、管网规则、2027 Dynamo / 2027.1 更新、官方课程目录，以及 JPS 的 MSMA 介绍页。

JKR/JUPEM/MSMA 全文 PDF 本次未能完整取得；视频仅确认官方入口，没有声称观看完整视频。没有写入未经核验的 JKR 半径/超高表、MSMA ARI/IDF/雨强或坐标转换常数。使用时需核对项目采用版本和条款，区分马来西亚采用标准与直接套 EU/UK/US 默认值。

说明、Python 标准库检查器和测试为本次原创；未复制第三方代码、手册、付费课件或视频。外部标准/文档只作引用，不重新许可或重新分发。没有为原仓库添加或改变许可证。

## 验证记录

- Python unittest：14 项通过。覆盖资料缺项、EU 管辖依据、国外参考缺少马来西亚采用证明、错误单位/国家、非数值与 NaN/Infinity、重复 scope/criterion、错误字段类型、只测量范围、模板有意未填，以及 CLI 的 BOM、重复 JSON 键、无效 JSON、缺文件和不改输入文件。
- 模板明确为 incomplete；metadata-complete 只指字段存在/类型通过，所有报告固定 engineering_compliance_checked: false。测试数值为合成值，不是工程设计标准。
- 已检查受限格式的 frontmatter/Codex 元数据字段、相对链接与上传文件清单。官方 quick_validate.py 尝试运行，但本地 PyYAML 目录访问异常，未能完成；不将其列为通过。
- 未打开/修改 DWG，未运行 Civil 3D、Dynamo 图或 .NET 插件；未声称软件集成或工程合规验证通过。

## 文档场景审阅

以下是对技能指令的离线审阅，不是独立模型对比实验或 Civil 3D 运行测试。

| 场景 | 指令处理 | 结果 |
|---|---|---|
| 公制模板是否等于马来西亚标准 | 区分单位与标准，核对 JKR criteria file/check set | 已覆盖 |
| 无地点就要求统一 ARI/管径 | 查 JPS/PBT/项目依据，不编数值 | 已覆盖 |
| GDM2000 直接重贴 GDM2020 | 核实 realization/投影/epoch/竖向控制，设置 CRS 不等于转换 | 已覆盖 |
| 点文件 E/N 交换 | 用控制点测试映射，保留原始资料 | 已覆盖 |
| Top 面直接当所有土方 BOQ | 明确 formation、剥土、材料分项与计量界面 | 已覆盖 |
| 管网无规则警告就符合 MSMA | 分开几何规则、水文/水力与工程审核 | 已覆盖 |
| 声称已有 Civil 3D MCP | 检查实际工具，无连接器则指导/生成待测试代码 | 已覆盖 |
| 旧版 Dynamo/.NET 教程直接用于 2027 | 核实构建、engine/SDK/API，副本小范围验证 | 已覆盖 |

## 两端使用

- Claude Code：从 `.claude/skills/civil3d-malaysia/SKILL.md` 加载。
- Codex：支持仓库 symlink 的检出从 `.agents/skills/civil3d-malaysia/SKILL.md` 加载，可用 `$civil3d-malaysia` 指定。
- Windows 若没有还原 symlink，可分别将同一 canonical 技能目录安装到 `~/.claude/skills/civil3d-malaysia` 和 `~/.codex/skills/civil3d-malaysia`，不改全局 Git 设置或复制整套旧技能。

本批为仓库上传，没有将新技能安装到本机全局目录；此前通用技能安装与本批发布分开。
