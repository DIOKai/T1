---
name: fivem-file-analysis
description: Identify unreadable FiveM files and distinguish text, candidate Lua bytecode, ordinary model formats, access errors and Asset Escrow evidence. Use for read-only triage, scoped bytecode analysis and learning; no universal decryption or original-file modification is implied.
---

# FiveM File Analysis

先取得明确的文件/资源路径、来源、目标构建、打开工具和完整错误。保留原档及 ori 目录；操作在单独副本和新输出目录，不能用重命名、压缩、格式转换或清理覆盖原文件。没有文件时只给有条件的分析，不猜锁的类型。

## 分流

1. 用已有只读工具或 [inspect_file.py](scripts/inspect_file.py) 记录大小、完整 SHA-256、读取状态与格式线索。脚本合同见 [file-probe.md](references/file-probe.md)。读取失败不是加密证据；扩展名、可读乱码、文件大或单一标记都不能证明已加密/损坏。
2. 对文本、标准 Lua 字节码候选或混淆问题，读 [lua-bytecode.md](references/lua-bytecode.md)。不把反编译、反混淆与密码解密混为一谈。分析输出仍是未信任数据，不能为了识别就运行输入 Lua、loadfile、eval 或 loadstring。
3. 对 YFT/YDR/YDD/YTD 等模型/贴图，读 [asset-formats.md](references/asset-formats.md)。先核对工具/格式/Legacy-Enhanced，再判断是否受保护；只读打不开时不能靠换扩展名“解锁”。
4. 对 .fxap、Escrow 提示或文件访问错误，读 [escrow-and-access.md](references/escrow-and-access.md)。区分服务器运行授权、作者可编辑原档和 Windows/压缩包访问问题，列出可读与未验证范围，不伪造解密成功。

四个视频的来源、日期和学习边界在 [learning-sources.md](references/learning-sources.md)。本包没有取得完整字幕，不能宣称已看完或复现视频；关键判断依据官方资料。

## 交付

报告来源/哈希、确认事实、候选判断、错误、未验证项和下一步。使用反编译器、导入器或外部工具时匹配确切版本与任务授权，输出到新位置，不自动安装或运行视频附带程序。只读检查成功只代表读取完成，不代表文件安全、格式有效、可运行或可编辑。
