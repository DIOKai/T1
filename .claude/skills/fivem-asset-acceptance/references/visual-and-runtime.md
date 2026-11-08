# 视觉与游戏验证

先选适合的类别，不要求每个道具有车辆骨骼或每个模型都有独立 YBN。

## 工具里目视（CodeWalker / Blender）

| 类别 | 关键证据 |
|---|---|
| 道具 | 尺寸/原点、材质/透明、嵌入碰撞（CodeWalker 显示 collision）、LOD 切换、Dynamic/Static 旗标合不合用途 |
| 车辆 | 固定骨骼/层级、meta 关联、轮子/门/灯、引擎舱/底盘和各 LOD 可见性、破洞扫描（LESSONS） |
| 服装 | GTA 骨骼和权重、组件/贴图关联、极端姿势穿模 |
| 人物 ped | 骨骼、权重、头/身体/头发组件、LOD（没有检查器，全靠这一步） |
| 地图/MLO | 放置、bounds、碰撞、portal/room、加载距离/LOD、和地形接合、有没有悬空（LESSONS） |
| 武器 | 骨骼 Gun_Root/Gun_GripR/Gun_Main_Bone、配件挂点、碰撞 |

打开背面剔除，从玩家位置多方向、在目标 LOD 检查缺面/破洞；正中和俯视图判断对称，不要用斜角遮问题。碰撞是独立证据：可走、可撞、脚步声/弹孔对材质，不由可见网格保证。GTA 用 Sollumz bounds/flags，不用别的引擎的 UCX 命名。贴图尺寸警告先报告，不自动重压缩。保留测试场景、截图、日志和未测项。

## 游戏内（只在本机测试服）

通用：冷启动进服一次，再 `restart <资源>` 一次；F8 和伺服器控制台找 16/48 MiB、“Could not add data_file”、“You lack the required entitlement”；两个客户端看同步（开第二个客户端的方法以当前 Cfx 文档为准）；Legacy、Enhanced 都要用就两边都进。脚本资源才用 `resmon 1` / `profiler`（fivem-performance-profile）。查串流内存的控制台指令名字还没在 Cfx 文档确认，不写进流程。

| 类型 | 生成/载入 | 距离 | 碰撞 | 光线 | 其他 |
|---|---|---|---|---|---|
| 道具 | 测试指令 CreateObject（如 `/haiprop <model>`）或 ymap | 0 m → lodDist → 更远，三个方向：LOD 切换、不提早消失 | 绕、踩上去、钻下面、推、开枪（弹孔和声音=材质）、开车撞 | 白天/晚上/下雨：晚上不发粉红光、emissive 晚上亮 | Dynamic 推得动/会断/会重生；门开关锁，两个客户端同一状态 |
| 车辆 | `/car <名字>` | 每个画质等级（Very High/High/Medium/Low）看 LOD | 开、撞、变形、轮子 | 车灯、警灯警笛、夜间 | 引擎舱/车底/破洞（LESSONS）、改装菜单、涂装、引擎声 |
| 服装 | 外观菜单 | — | 极端姿势穿模 | — | 每个贴图变体、男女、两个客户端 |
| 人物 ped | 当玩家 + 当 NPC | LOD | 布娃娃 | — | 动画、脸部表情 |
| 地图/MLO | 传送 | 远处走近、经过每个 portal | 每层楼、楼梯、车开上坡道 | 白天/晚上、室内灯、室内不下雨 | 声音遮挡、第一人称、两个玩家 |
| 武器 | 给武器 | — | — | — | 手上位置、瞄准、开火、换弹、每个配件、背包图片 |
| 动画 | 播放每个表情 | — | — | — | 循环接缝、道具位置、男女、两个客户端 |
| 音效 | 播放/触发 | 远近衰减 | — | — | 音量和原版比、循环爆音（audio-quality-check） |
| 画质包 | 开/关 | — | — | 白天、黄昏、夜、雨、室内 | 帧数对比 |

LOD 在工具里切换和游戏距离变化都要看；预览成功不证明远距离不会消失。

主要资料：[静态碰撞](https://docs.sollumz.org/tutorials/creating-static-collisions.md)、[LOD 编辑](https://docs.sollumz.org/documentation/drawables.ydr/level-of-detail-lods-editing.md)、Cfx beginner series part 4–8。以实际 Sollumz/Blender 版本确认菜单位置。

补充视频（只记学习链接和原创要点，不复制字幕或资产）：
- [ook_3D：Creating Custom Models / Sollumz Essentials](https://www.youtube.com/watch?v=IMv9UIHpLsM)，2023-10-26。
- [Bumpy86_x：Basic prop tutorial for simple collisions](https://www.youtube.com/watch?v=-24PBSYT74w)，2025-08-17（游戏内测：跳不上去、不能当掩体、子弹有反应 [21:18]）。
- 更多道具影片和时间点见 `fivem-prop-creator/references/sources.md`。
