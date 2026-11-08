# 车辆建模补完：引擎舱、底盘、内装、配件

日期：2026-11-08。用户问「做车辆模型的全部都有吗，引擎、车内饰品那些」。

检查后发现：`blender-vehicle-modeling` 的车身外观和进游戏两段很完整，但引擎舱、底盘、内装、警用和改装配件只有检查规则，没有做法。原本的来源课程明说不做引擎。用户同意补完，并要求「查资料多些」。

## 资料

三个子代理分头调研，再由一个子代理补缺口：
- **影片**：约 110 部有字幕的教学影片。
  - 只抓字幕，不下载影片。
  - 几部没字幕的低模内装和引擎舱影片，照这次对话一开始用户同意的做法，下载 360p 截图来读，影片读完就删掉。
  - 中途被 YouTube 限流。原因是抓「自动翻译成英文」的字幕轨，改成只抓原语言字幕后解决。
- **第一手数据**：用 CodeWalker.Core 只读导出原版车核对，没有改游戏文件。
  - 一般车：buffalo、bison、sadler、granger、vigero2。
  - 警车：police、police3、police4、sheriff2、fbi2。
  - 核对了各 LOD 的三角面、骨骼、shader、贴图来源。
- **文字资料**：Sollumz 文档、modding-forum 指南、citizenfx 说明、muto-atlas 骨骼表。
- **用户自己的东西**（只读整合）：
  - 引擎舱规则（LESSONS）；
  - `H:\FiveM\vanilla_ref\tools` 里的检查工具；
  - Silverado 引擎舱零件包的记录。

## 新增和修改

`blender-vehicle-modeling` 新增三份参考：
- `references/engine-bay-and-underbody.md`
  - 引擎、整个引擎舱、连续的车身钣金内衬、底盘和悬吊、排气、刹车；
  - 车和卡车的零件清单；
  - 原版各 LOD 的面数；
  - 整个引擎舱共用一张贴图；
  - 用户的引擎舱规则和检查工具顺序。
- `references/interior.md`
  - 仪表板、仪表、方向盘、座椅、门板、警用内装；
  - shader 和共用贴图；
  - 各 LOD 的面数和检查清单。
- `references/accessories-and-parts.md`
  - 警灯灯条的骨骼层级，防撞杆和探照灯用 extra；
  - 改装件：单独 yft、轴心在骨骼上、mod_col 碰撞；
  - 自制轮毂；
  - 小零件和装配流程。

其他修改：
- `blender-vehicle-modeling/SKILL.md`：
  - 建车顺序加入第 7 步引擎舱和底盘、第 8 步内装、第 11 步配件；
  - 常见错误表加 5 行；
  - 补了触发词。
- `fivem-vehicle-mod/references/police-emergency.md`：
  - 补 extra 生成规则：`requiredExtras`、`extraIncludes`、`FLAG_EXTRAS_*`；
  - 警灯 scale、scaleFactor、delta、start；
  - 旋转灯速度表；
  - `SetVehicleExtra` 会修车（社群说法）。
- `fivem-vehicle-mod` 补上 Codex 用的 `agents/openai.yaml`。

## 量原版车得到的关键事实

这几条都是推断或实测，技能里有标明：
- 刹车卡钳挂在 `hub_lf/rf/lr/rr`，跟着转向、不跟轮子转；刹车盘在会转的轮子网格里（推断）。
- `engine` 骨骼没有任何面，引擎舱蒙皮到 `chassis`；原版引擎舱九成五以上只用一张共享贴图 `vehicle_generic_detail2`。
- 仪表是 `dials` 骨骼上的一片平面，贴 render target 贴图 `script_rt_dials_*`，由 vehicles.meta 的 `dashboardType` 决定样式；没有指针骨骼。
- 座椅骨骼只标出人坐的位置，座椅模型挂在 `chassis`。
- 原版灯条：外壳挂 `misc_a`（有碰撞），灯罩挂 `siren_glassN`，发光片挂 `sirenN`。

## 对照测试

题目是「警用 SUV 的引擎舱、底盘、内装、能用 extra 开关的警灯」。新版技能对比改之前的旧版；旧版那次也读了用户的记忆资料，所以对照组不弱。

| | 新版 | 旧版 |
|---|---|---|
| 通过 | 8/8 | 5/8 |

旧版的错误：
- 仪表做成指针网格；
- 警灯骨骼层级混乱，还说关掉 extra 后灯可能悬空发光；
- 座椅挂错骨骼；
- 刹车盘要四个角分开做；
- L1–L3 的面数比原版实测高好几倍。

评分代理指出部分标准分不出新旧版（因为用户规则也在记忆里），已加三条（刹车盘在轮子网格里、engine 骨骼没有面且共用一张贴图、LOD 面数在原版范围内），并把警灯那条拆成三条，留给下一轮用。

## 研究中顺便发现的用户车辆问题

已回报给用户，没有动：
- `16chargerpd`、`ram2500pd` 没有 siren 骨骼；
- um21yukonpd 的 `brakelight_m.001`、ram2500pd 的 `misc_f.001/.002` 带了复制后缀；
- Shelby 尾翼的轴心可能没放在骨骼上；
- Silverado 引擎舱零件包的独立 `.blend` 已不在，零件还合在 Silverado 和 Yukon 的车身里。

## 还没验证的

技能里都有标记：
- Sollumz 会不会导出 Weighted Normal 的自定义法线；
- 用 `vehicle_track2` 做会动的皮带；
- 驾驶员手臂的 IK；
- 发光片的模型缩放怎么配 `scaleFactor`（各教程说法矛盾）；
- 发电机、冷气压缩机、启动马达、转向机、油箱、挡泥板、拖车钩这几样没有有字幕的教学，只写了一般做法。
