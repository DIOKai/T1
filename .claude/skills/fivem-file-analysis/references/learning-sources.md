# 四个视频与官方核对笔记

整理日期：2026-10-17。以下四条全部收录。搜索取得标题、作者、日期及简介；访问视频和检索字幕未取得完整正文。观看、逐字转录与视频步骤复现状态均为未完成，不能把下面独立整理的官方资料要点归因于视频全文。

| 视频 | 元资料 | 本批用途与限制 |
|---|---|---|
| [CTFGuide: Lua Bytecode](https://www.youtube.com/watch?v=NzP12hWKgok) | Almond Force；2024-09-19 | 简介为 Lua 字节码逆向题解；仅作练习入口，未取得题目原文件/完整讲解，不编造解题步骤 |
| [unluac.jar Tutorial](https://www.youtube.com/watch?v=ul1BLoJ5N-E) | TopGEO；2019-02-27 | 简介涉及 Java/unluac 编译块反编译；标题“Decrypt”不作为加密能力证据，旧下载链接没有执行 |
| [Sollumz: Import and Export a model from CodeWalker](https://www.youtube.com/watch?v=mSjdd_nI3Q0) | Quan's Maps；2024-06-29 | 简介为 Blender/CodeWalker 双向交换；未逐步复现，菜单/API 与当前版本重新核对 |
| [How ESCROW LOCK Assets For FiveM](https://www.youtube.com/watch?v=Xc5m9_sGrOY) | Eishabeesha；2025-06-30 | 学习入口描述资产保护流程，不能当成解锁教程；附带付费课程/服务不启用 |

独立从官方资料整理的学习顺序：
1. 先根据原档、哈希和报错区分读取失败、文本与二进制，不把乱码等同加密。
2. 学标准 Lua 块与工具适用范围，再区分反编译、混淆 VM 和密码解密；细节见 [lua-bytecode.md](lua-bytecode.md)。
3. 学原生资产与 XML/二进制交换的差别，确认实际工具版本；见 [asset-formats.md](asset-formats.md)。
4. 学 Escrow 运行授权和可编辑文件范围；见 [escrow-and-access.md](escrow-and-access.md)。

这些是官方资料交叉核对后的原创流程，不是视频字幕摘要。后续若取得字幕或完整观看，应按段落/时间戳补证据，区分作者说法、工具官方限制和实际复现结果；不覆盖本批来源历史。仅保存链接和必要元资料，不镜像视频、整段字幕或附带资产。
