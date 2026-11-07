# 照 YouTube 教学学来的建模技能

日期：2026-11-08。用户给了 12 个 YouTube 影片和播放清单，问「能不能学成 skill」，范围选「全部」，并要求另外找更多资料。用 yt-dlp 抓字幕（60 部影片里 54 部有字幕）；没字幕的影片下载 360p，用 ffmpeg 每 10–25 秒截一张拼成对照图，再放大看细节。所有技能都是本仓库自己写的，没有复制影片的文字、图片或模型。写法照 `example-skills:skill-creator` 和 `superpowers:writing-skills`（先测有技能和没有技能的差别）。

## 新增

| 技能 | 用途 | 学自 |
|---|---|---|
| [blender-vehicle-modeling](../../.claude/skills/blender-vehicle-modeling/SKILL.md) | 从蓝图建车和直升机：蓝图摆法、最少四边形笼子、拓扑、反射检查、缝线、格栅、车灯、轮毂、轮胎、进 GTA 的预算和检查 | Kevin Gallant 20 集车辆细分建模课、JOYCE 整车拆解、Kim Sergei 直升机缩时 |
| [blender-product-modeling](../../.claude/skills/blender-product-modeling/SKILL.md) | 有真实尺寸的产品（手机、手表）：毫米精确的机身、圆角加圆边、按钮和镜头、游戏低面数版本；只有照片时用本机 Hunyuan3D | iPhone 建模、智能手表建模、Bady Design 的 AI 道具影片（付费的 Meshy 换成免费的本机 Hunyuan3D） |
| [blender-shoe-modeling](../../.claude/skills/blender-shoe-modeling/SKILL.md) | 球鞋和靴子：鞋楦、鞋底纹路、分片鞋面、鞋眼、鞋带、缝线、皱褶；做成 freemode feet 组件 | PixelicaCG、J Derinor（Jordan 1）、Blacknest 三部鞋子影片 |

每个技能附一个 bpy 脚本（`vehicle_setup.py`、`product_body.py`、`stitches.py`），都在 Blender 5 无界面模式实际跑过、量过尺寸。影片里提到的付费工具（DCT、Stitch Maker、Meshy）标明「付费」，不是必需。

## 修改

- `fivem-mlo-housing`：新增 `references/blender-to-fivem-steps.md`（qDESAUCE 19 集有字幕的课程、Bady Design 3 集加直播，从 CodeWalker 导出到游戏测试的每一步和教学者自己犯过的错）。SKILL.md 加上这个伺服器的 MLO 打包规则：每个 MLO 单独一个 `*_milo_.ymap`、MLO 的 ytyp 只靠 `.ymf` 载入（不要 `DLC_ITYP_REQUEST`）、portal 法线指离 roomFrom、房间少、|UV| < 50。旧版检查脚本还会建议用 `DLC_ITYP_REQUEST`，跟这些规则冲突，已改掉。
- `check_mlo_resource.py` 新增检查：`ITYP_REQUEST_MLO`、`ITYP_REQUEST_CHECK`、`PORTAL_FACING`、`PORTAL_AND_ROOM`、`YMAP_MULTI_MLO`、`YMAP_MLO_MIXED`、`YMAP_MLO_NAME`；修好 Windows 上输出中文会崩溃的问题，以及 portal 角点写成 `6.0,-25.0,0.0` 文字时读不到的问题。附 `scripts/test_check_mlo_resource.py`（4 个测试）。
- `fivem-clothing-creator`：新增 `references/clothing-step-by-step.md`（Druu 79 分钟的衣服教学），SKILL.md 补上权重转移设定、顶点色和 `_r` / `_whi` 贴图规则。
- `fivem-prop-creator`：加上模型来源的指引（产品 → `blender-product-modeling`，只有照片 → 本机 Hunyuan3D 路线）。
- `fivem-mlo-housing` 加上 Codex 用的 `agents/openai.yaml`。

## 验证

- 三个 bpy 脚本：Blender 5 无界面模式实际跑过。手机机身 78 × 8.25 × 163.4 mm 完全一致，封闭网格，渲染版 700 面、游戏版 332 面；蓝图四张的位置和大小跟 4.69 × 1.92 × 1.45 m 的量尺盒对齐；7 根辐条 56 个顶点；40 mm 弧线上 14 针缝线，离弧心 39.65–40.3 mm，没有拉长。
- `check_mlo_resource.py`：4 个测试通过。在伺服器真实的 La Puerta 导出上，修好后的 26 个 portal 全部判为方向正确，1 个判断不了（车库出入口，房间框越过开口，跟当初要另外指定方向的记录一致）；把角点顺序反过来，26 个全部被抓到。La Puerta 旧的测试版（当初闪退的打包方式）被 `YMAP_MLO_MIXED`、`YMAP_MLO_NAME` 抓到。
- 子代理对照测试：见下方「对照测试结果」。

没有改用户的伺服器、Blender 场景或全局设定；没有安装新工具（yt-dlp 是这次经用户同意装的）。

## 对照测试结果

每个技能出一道真实题目，同时派子代理「有技能」和「对照」作答（新技能的对照是不给技能；`fivem-mlo-housing` 的对照是改之前的旧版），再派评分代理逐条打分。测试案例放在各技能的 `evals/` 里。

| 测试 | 有技能 | 对照 | 主要差别 |
|---|---|---|---|
| 手机道具（精确尺寸） | 第 1 轮 4/5；改进后第 2 轮 7/7 | 4/5 | 第 1 轮有技能的版本没有 UV、没做碰撞物件 → 脚本加了 `game_ready()`（方块投影 UV、碰撞盒），第 2 轮在 Blender 实跑全部达标；对照的脚本在 Blender 里跑到一半报错，三角面 1900（多 5.7 倍） |
| 跑车（四张蓝图） | 7/7 | 4/7 | 对照的轮圈 48 段不是 7 的倍数、没有反光检查、缝线没讲支撑线；但对照讲了碰撞、UV、车窗 shader、内装 → 已补进 `gta-game-ready.md`。有技能的代理还找出 `radial_array()` 预设绕错轴（应该绕 X），已修好并实测 |
| Jordan 风格 feet 组件 | 6/6 | 4/6 | 对照没有鞋楦和分片叠层，还把付费的 Durty Cloth Tool 说成免费；对照提到鞋底太厚会陷进地里 → 已补进技能 |
| 服装店 MLO（教程建议对不对） | 8/8 | 旧版 5/8 | 旧版的 `_milo` 命名少了下划线、没讲 portal 方向、没提删 occluder；新版少了「档名加独特前缀」→ 已补 |

合计：有技能 95%，对照 68%，旧版 MLO 62.5%（第 1 轮）。评分代理指出几条评分标准太松（UV、品牌、付费工具），已改严，留给下一轮用。
