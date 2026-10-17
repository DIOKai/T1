# FiveM 文件分析与四个视频学习来源

日期：2026-10-17。本批只新增文件，不动旧 Skill、配置、模型、原档或 ori。Claude 的 `.claude/skills/` 和 Codex 的 `.agents/skills` 已通过既有链接共享，本批不改链接。

新增 [fivem-file-analysis](../../.claude/skills/fivem-file-analysis/SKILL.md)：区分读取权限问题、文本/字节码、混淆、普通 GTA 资产格式与 Escrow 线索。按需要加载对应参考，保留未知状态和原始文件。附只读 Python 文件检查器，记录大小、SHA-256 和有限格式线索，不执行、上传、转换或解密输入。

## 学习材料

[四个视频完整来源列表与学习笔记](../../.claude/skills/fivem-file-analysis/references/learning-sources.md) 均已收录：CTFGuide Lua Bytecode、TopGEO unluac、Quan's Maps CodeWalker/Sollumz 交换、Eishabeesha Escrow 保护流程。

没有取得四部视频的完整字幕/正文，完整观看和视频步骤复现均未完成。因此本批不称“视频全部学完”，也不提供伪造的时间戳或逐字摘要。可用元资料与 Lua、unluac、Cfx、Sollumz 官方资料交叉核对后，形成原创分析流程；不是解密器，也没有实测解锁效果。

## 验证与来源

Skill 格式、UI 元数据、Python 语法及本地引用经过检查；只读 helper 在合成文件上通过 18 项行为测试，读取错误/reparse/并发变化场景采用模拟。独立代理使用该 Skill 对一个含两个合成输入的请求作离线评估；不是无 Skill 对照试验。

没有下载反编译器、执行未知输入、读取真实用户资源、登录 Cfx、调用游戏服、导入真实资产或改全局配置。真实 Lua 反编译、Escrow、模型工具链与游戏运行均未验证。

详见 [来源与验证记录](file-analysis-2026-10-17.sources.json)。
