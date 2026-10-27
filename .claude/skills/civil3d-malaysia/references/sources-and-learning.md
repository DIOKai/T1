# 资料与学习记录

检索日期：2026-10-27。此技能依据公开文档整理操作流程；没有观看/转录完整 YouTube 视频，没有在 Civil 3D 现场跑工程模型。本表区分已经读到的正文、只见索引的文档及待学习视频，不把链接存在当成已验证内容。

## 已读官方网页正文

| 资料 | 用于本技能的内容 | 适用限制 |
|---|---|---|
| [Autodesk: Working with Design Criteria](https://help.autodesk.com/cloudhelp/2025/ENU/Civil3D-Tutorials/files/GUID-CAEC3077-D78A-4F42-8E47-41FABAB6915D.htm) | 默认设计条件与 AASHTO 有关；可创建本地 criteria file / design check set | 2025 教程，不是 JKR 数值表 |
| [JPS: About MSMA](https://storm.water.gov.my/about-msma) | MSMA 的水量/水质源头控制框架及第二版 2012 的发布/采用信息 | 未提供本次可核对的完整设计表；不是对项目适用版次的批准 |
| [Autodesk: Corridor Surfaces](https://help.autodesk.com/cloudhelp/2024/ENU/Civil3D-UserGuide/files/GUID-E6E60500-197F-41C3-B131-79C80E74D30E.htm) | 动态/分离曲面关系、更新与避免以走廊面作为走廊目标 | 2024 文档；操作位置在用户版本复核 |
| [Autodesk: Pipe Network Part Rules](https://help.autodesk.com/cloudhelp/2024/ENU/Civil3D-UserGuide/files/GUID-8600D35E-2B92-4377-88B4-C2FFED9950CC.htm) | cover/slope/length 等规则的作用与警告范围 | 规则检查不能代替完整水文/水力分析 |
| [Autodesk: New in Dynamo for Civil 3D 2027](https://help.autodesk.com/cloudhelp/2027/ENU/Civil3D-WhatsNew/files/GUID-FC66011C-0DED-4332-B345-AD299D7D0245.htm) | Dynamo Core、PythonNet3 与新旧节点变动 | 需进一步核对用户安装的是 2027 还是 2027.1 |
| [Autodesk: What's New in Civil 3D 2027.1](https://www.autodesk.com/blogs/aec/2026/10/20/whats-new-in-civil-3d-2027-1/) | 2026-10-20 发布说明：排水、引用、API/Dynamo 更新及官方视频入口 | 产品功能不等于马来西亚设计合规；云功能需另核授权和项目数据权限 |
| [Autodesk: Civil 3D Quick Start Guide](https://www.autodesk.com/learn/ondemand/curated/civil-3d-quick-start-guide) | 测量点、曲面、道路、管网的官方学习顺序 | 已读目录和下列课程简介，未观看课程视频 |

## 已定位但未取得可完整审阅原文的资料

不得以本节作为已核验的参数出处。没有下载/复制这些标准全文或表格进入仓库。

| 资料 | 本次取得的证据 | 后续使用前要求 |
|---|---|---|
| [JKR ATJ 8/86 (Pindaan 2015) PDF 入口](https://epsmg.jkr.gov.my/images/c/c9/BPIS_ATJ_8-86_19062020.pdf) | 官方域名搜索索引；浏览读取失败，本地下载 DNS 失败 | 取得项目允许使用的原文，核对版本、条款和适用道路类别；不称为全国最新标准 |
| [JUPEM PKPUP 2/2021](https://www.jupem.gov.my/jupem18a/assets/uploads/files/pekeliling/d95f4-pkpup-2-2021.pdf) | 官方搜索索引出现 GDM/realization 信息；完整读取失败 | 取得原文与项目测量报告，核对实际基准/epoch；本技能不提供转换常数 |
| [JUPEM PKPUP 3/2021](https://www.jupem.gov.my/storage/upload/pekeliling/d9d1d-pkpup-3-2021.pdf) | 官方转换资料入口，正文未成功读取 | 核对适用范围、方法及项目独立控制检核 |
| [JPS MSMA 2nd Edition PDF 入口](https://wplb.water.gov.my/assets/msma-2nd-edition.pdf) | 官方域名索引；全文读取失败 | 用可合法取得的项目副本确认表格/章节/补充要求，不能混用旧版目录 |
| [Autodesk: Civil 3D .NET 10 transition requirements](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Civil-3D-Requirements-for-products-affected-by-the-Microsoft-NET-10-transition.html) | 官方搜索结果含迁移说明；页面正文读取返回空 | 编译前重新取得当前兼容说明并核对安装环境，不只依据搜索摘要选择 TargetFramework |

## 学习路线与可复现练习

以下四个课程已核对标题/简介，不宣称已观看视频。练习是本技能提出的独立教学建议，必须使用临时图纸和合成数据，不能套用到真实项目作为批准标准。

1. [Importing survey points into a base drawing](https://www.autodesk.com/learn/ondemand/curated/civil-3d-quick-start-guide/46imh9y2RS8MSmadJVwboH)：创建小型点文件，先指定坐标字段；故意交换 E/N 检查能否通过控制点发现错误，再恢复正确映射。
2. [TIN surface / breaklines 课程](https://www.autodesk.com/learn/ondemand/curated/civil-3d-quick-start-guide/49UpvlZ8VgJp3F0j8OnrYx)：用非共线合成地面点建 TIN，添加一条沟线和边界，对照三角网及断面；不只看等高线。
3. [Corridor and surface for a road 课程](https://www.autodesk.com/learn/ondemand/curated/civil-3d-quick-start-guide/2UEiGE6OGe45PLgptTUJN3)：建立小段 alignment/profile/assembly/corridor，改一个经明确标注的教学参数并重建，检查上下游对象；教学值不是 JKR 条文。
4. [Gravity pipe network 课程](https://www.autodesk.com/learn/ondemand/curated/civil-3d-quick-start-guide/6QRggPyEHcGnw16R8lX1sv)：建少量节点，在 plan/profile 对照 flow、invert、rim、cover 与单位；即使规则无警告，也应能解释还缺哪些水力输入。

Autodesk 2027.1 官方文章还链接以下 YouTube 视频：

- [Autodesk Assistant — Civil 3D 2027.1](https://www.youtube.com/watch?v=vaU_e_eiSWA)
- [Connected References for Data Shortcuts — Civil 3D 2027.1](https://www.youtube.com/watch?v=CIZB2ujk9_w)

本次视频读取失败，仅核对了官方文章的标题/链接；不引用未观看内容。使用未来视频时记录频道、URL、发布日期、软件版本，以及实际观看或取得字幕的时间范围；不把教学中的外国标准设置写进马来西亚参数台账。

## 内容来源与复用

技能说明、检查器和测试为本次原创；引用以链接、短标题与流程摘要为主，不打包 Autodesk/JKR/JPS/JUPEM 的手册、视频、培训素材或许可受限代码。外部资料保留其原有版权/使用条款；本批原创内容的适用许可遵循 T1 仓库已有许可，不替外部标准重新授权。
