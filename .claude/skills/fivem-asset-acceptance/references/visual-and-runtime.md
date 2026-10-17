# 视觉与游戏验证

先选适合的类别，勿要求每个道具具有车辆骨骼或每个模型都有独立 YBN。

| 类别 | 关键证据 |
|---|---|
| 道具 | 尺寸/原点、材质/透明、碰撞方式与预期静态/动态行为 |
| 车辆 | 固定骨骼/层级、meta 关联、轮子/门/灯、引擎舱/底盘和各 LOD 可见性 |
| 人物/服装 | GTA 骨骼和权重、组件/贴图关联、极端姿势穿模、实际动画 |
| 地图/MLO | 放置、bounds、碰撞、室内 portal/room（如适用）、加载距离/LOD 与地形接合 |

打开背面剔除，以玩家位置、多方向与目标 LOD 检查缺面/破洞；正中和俯视图有助判断对称，不能只用斜角遮住问题。碰撞是独立证据：玩家可走、车辆可撞、材质/脚步正确不由可见网格保证。GTA 使用 Sollumz bounds/flags，不用其他引擎的 UCX 命名替代。

LOD 在工具内切换和游戏距离变化都要看；预览成功不证明远距离无消失或游戏质量等级正确。纹理分辨率/尺寸警告先报告，不自动重压缩。对比原始文件与交付文件，保留测试场景、截图、日志与未测项。

主要资料：[静态碰撞](https://docs.sollumz.org/tutorials/creating-static-collisions.md)、[LOD 编辑](https://docs.sollumz.org/documentation/drawables.ydr/level-of-detail-lods-editing.md)。以实际 Sollumz/Blender 版本确认位置和导出流程。

补充视频：
- [ook_3D：Creating Custom Models / Sollumz Essentials](https://www.youtube.com/watch?v=IMv9UIHpLsM)，2023-10-26。
- [Bumpy86_x：Basic prop tutorial for simple collisions](https://www.youtube.com/watch?v=-24PBSYT74w)，2025-08-17。

本批只核对元资料和简介，未完整观看/复现；旧菜单位置需对照当前版本。只保存学习链接和原创要点，不复制整段字幕、视频或其资产。
