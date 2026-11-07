# 车辆声浪、跳舞、服装技能

日期：2026-11-08。用户在上一批（`yt-modeling-2026-11-08.md`）之后要求：找做车辆声音的技能（没有完整的就做一个）、学习做跳舞的影片做成单独的技能（「找多点资料」）、补完整服装技能。三份资料都由子代理调研（YouTube 只抓字幕，加上官方文档和源码），没有下载影片、声浪包或安装任何东西。所有技能都是本仓库自己写的。

## 新增

| 技能 | 用途 | 资料 |
|---|---|---|
| [fivem-vehicle-sound](../../.claude/skills/fivem-vehicle-sound/SKILL.md) | 引擎声浪的整条链（audioNameHash → dat151 → dat54 → granular awc）；装声浪包、复制改名做变化版、改音色、调参数、车没声音 | CodeWalker 源码（RelFile.cs、AwcFile.cs）、Cfx 文档和 issue #2515、Rockstar GDC 2014 演讲、社群包页面、用 CodeWalker.Core 导出用户已装的 7 个包核对 |
| [fivem-dance](../../.claude/skills/fivem-dance/SKILL.md) | 自定义舞蹈：免费动作来源和授权陷阱、BPM 换算循环帧数、律动、导出前烘焙循环、rpemotes 单人/双人/群舞/道具舞 | 40 部有字幕的教学影片、rpemotes-reborn 源码、Sollumz 导出器源码、Blender 5.2 手册、各动捕工具的 README 和授权 |

工具：
- `fivem-vehicle-sound/scripts/sound_pack.ps1`：dump 和 clone，用户自己的 CodeWalker.Core。
- `revoice_wav.py`：只用标准库。
- `check_sound_resource.py`：只读检查。
- `fivem-dance/scripts/dance_timing.py`：分数精确计算节拍和循环帧数。
- `bake_loop.py`：bpy，把循环烘焙成单一 action。

## 修改

- `fivem-clothing-creator`：
  - 重写 SKILL.md。最前面写明：串流自制衣服是 Cfx Element Club Argentum 以上的付费权益，只说明、不推荐购买。
  - 新增 4 份参考：add-on 包命名和 manifest；组件、道具和 flags；布料物理等；接 illenium-appearance。
  - 新增 `check_clothing_resource.py` 和 29 个测试。手动命名的档（`jacket_000_u.ydd`、`hat_000.ydd`）会提示该放进哪个栏位。
- `blender-shoe-modeling` 的 `gta-feet-component.md`：高跟鞋改成照 grzyClothTool 源码的免费做法。
- `fivem-animation`：加上指向 `fivem-dance` 的段落；修正 CodeWalker Ped Viewer 预览 .ycd 的条件。

## 验证

**声浪工具：用你伺服器上的真实声浪包测，只读，输出都放在暂存区。**
- `sound_pack.ps1 clone` 测了三个包：Mustang 5.0、Hellcat（含 amp.dat10）、LT1（30k 和 48k 混用）。复制版和原包逐项比对都是 0 处差异：Mustang 1077 个数值、Hellcat 8125 个、LT1 1006 个，只有名字不同；AWC 逐字节相同。
- 10 月 24 日手工复制、已经过试听的 dominatorgrt，拿同样方法比对也是 0 处差异。
- 测试中找到并修好两个会让复制版去播原包声音的 bug：
  - 容器名称是用 hash 储存的，没改到；
  - RandomizedSound 写在属性里的引用没改到。
- 改音色流程：导出 WAV → `revoice_wav.py` → 重建 AWC → 再导出。改过的串流逐字节等于编辑结果；颗粒表、循环表、采样数和采样率都不变；长度不对的 WAV 会被拒绝。
- 另修掉 `revoice_wav.py` 里一个 n² 的效能 bug。

**检查脚本：跑了伺服器的 resources，只读。** 找到两个真问题，回报给用户，没有自己改：
- `lg81hcredeye` 声明了不存在的 `_amp.dat`。
- `yukon62` 声浪包装了，但 um21yukonpd 还用原版 `BISON`。

**单元测试**：声浪 8 个、跳舞 27 个、`bake_loop.py` 在 Blender 5.2 无界面模式测过、服装 29 个，全部通过。

## 对照测试结果

同一道题派子代理「有技能」和「对照」作答，对照组是没有技能，或改之前的旧版服装技能；再由评分代理逐条打分。

| 测试 | 有技能 | 对照 | 对照的主要错误 |
|---|---|---|---|
| Mustang 三个变化版 + 通配符没声音 | 7/7 | 3/7 | 只复制车辆和引擎记录，变化版仍共用原包声音库；叫用户中途更新 CodeWalker；说作者通常允许修改转用 |
| 128 BPM K-pop 循环 + 双人版 | 8/8 | 3/8 | 用已废弃的 EmoteLoop；推荐付费额度的 Rokoko/DeepMotion；说反了双人舞时谁被移动；没讲 Sollumz 不导出 Cycles/NLA |
| 外套和帽子看不到、帽子穿发 | 8/8 | 旧版 5/8 | 回答「正式服可以用」却没提付费串流权益；帽子压发不知道怎么做；没有检查脚本 |

合计：有技能 100%，没技能 40.5%，旧版服装技能 62.5%。

评分代理指出部分标准太松或偏向技能，已改：
- 跳舞第 2 条改成不管用不用技能的写法；
- 拆开绑在一起的条件；
- 新增「谁被移动」「双人片段要原地」「不能无条件保证正式服能用」。

还没进游戏验证的（技能里都标了）：
- 声浪的 8 字前缀规则；
- Cycles/NLA 不会被导出（从源码推断）；
- 循环首尾重复那一帧会不会让动作顿一下；
- 测试服人数多少以下不需要串流权益。
