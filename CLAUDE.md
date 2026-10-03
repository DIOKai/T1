# 技能使用规则

用户用中文交流，回复也用中文。

## 什么时候直接用、什么时候先问

每次收到请求，先看已安装的技能里有没有和这件事相关的。

这条规则适用于所有技能和插件，包括用户以后新加的。新加的技能不用等用户再交代，同样按下面的方式判断：直接用，或者先问。

**直接用，用的时候告诉用户用了哪个**（一句话，例如"我用 systematic-debugging 来查这个问题"）：
- 请求和技能明显对得上，比如要 PDF 就用 `document-skills:pdf`，要查 bug 就用 `superpowers:systematic-debugging`
- 技能只是给出做事的方法或步骤，不会额外改文件、装东西或连外部服务

**先问用户要不要用，说明这个技能会做什么、为什么适合**：
- 只是可能相关，不确定是不是用户要的
- 技能会大幅改变做法，比如 superpowers 的 brainstorming 会先问一轮需求，TDD 会先写测试
- 会安装依赖、跑脚本、开浏览器、连外部服务或需要登录，比如 playwright-skill、video-downloader、knowledge-work 插件里的连接器
- 会派出多个子代理或跑很久，比如 trailofbits 的 c-review、zeroize-audit
- 用户没要求、但用了明显有帮助的技能（主动建议）

**不用**：没有相关技能，或者用户明确说不要用。

## 不用付费的东西

用户不要付费的工具和服务。需要付费 API key、订阅或额度的技能和功能都不用，也不推荐；只有免费的替代方案时才提，并说明它是免费的。比如 Blender MCP 的 Premium AI 生成 3D 模型、Gemini/Nano Banana 生图 API，都不要用。

## 写 FiveM / QBCore / Qbox 相关代码时

优先用用户自己的 `fivem-script` 技能，再按需要搭配：
- `fivem-pro`：FiveM 开发规范、resmon 性能优化、Sollumz + CodeWalker 做地图/MLO
- `fivem-security-audit`：审查 script 的后门、漏洞、性能问题，也能判断来路不明的 script 安不安全
- superpowers（规划、调试、审查）和安全检查技能（insecure-defaults、sharp-edges）
- `oxlib`、`oxmysql`、`ox-inventory`、`ox-target`：ox 系列的 API 速查
- `fivem-react-nui`：用 React + TypeScript + Vite + Tailwind 做 NUI
- `fivem-vehicle-mod`：做、修、上架 addon 车辆资源（meta 文件、改装套件、涂装、警笛、贴图大小、Enhanced 转换）。车辆资源上服前先跑它自带的 `check_vehicle_resource.py`（本地、只读，直接跑）；npx 工具第一次跑会下载套件，先说一声

改完 FiveM 的 Lua 后，如果用户电脑上有 `qbx-lint`，就对改过的文件跑一次检查（只读，直接跑）；要用 `qbx-lint --fix` 或 `qbx-lint fmt` 改文件前先问。

`fivem` MCP 能在用户的伺服器上下指令、调用 native，权限很大：用之前先问，只连本机测试服，不要连正式服。

## 3D 模型和动作

Blender 技能（retopology、lod-pipeline、asset-optimization、uv-workflow、rigging、animation、export-pipeline、vehicle-artist、hard-surface、collision-proxy、texture-workflow，以及做室内用的 set-dressing、archviz、prop-artist、environment-artist）要通过 `blender` MCP 在用户自己的 Blender 里执行代码，用之前先问。做 GTA 模型时，在 Blender 里完成后提醒用户用 Sollumz 导出成 .ydr/.yft/.ycd。

做 GTA/FiveM 角色动画或自定义表情时用 `fivem-animation`（流程：Blender → Sollumz → CodeWalker → rpemotes/TaskPlayAnim），它自带的 `check_anim_resource.py` 是本地只读检查，直接跑。

学或做动画时：先用 `motion-design` 讲原则（时间、间距、缓动、预备动作、跟随），再用 `blender-animation-rigging` 和 `animation` 在 Blender 里操作；用户想学的时候配合 `anthropic-skills:learn` 一步步教，每一步让用户自己动手。`blender-animation-rigging` 写的是 Blender Lab 官方 MCP，这里装的是 `blender` MCP（mcp-for-blender），用它的 `execute_blender_code` 执行同样的 bpy 代码。`motion-design` 提到的 blender-motion、aftereffects-motion 没有装（前者会接付费的 Higgsfield），不要去找。

这些 Blender 技能是通用游戏美术流程，用于 GTA 时以 GTA 的规则为准：
- 车辆骨骼名必须用 GTA 的固定名字（如 `door_dside_f`、`wheel_lf`），用 muto-atlas 查（`/vehicle`），不要用技能里的 `SM_Vehicle_*` 命名
- 碰撞用 Sollumz 的 bounds 和碰撞 flag（muto-atlas `trunk/flags.md`），不用 collision-proxy 里的 UCX/UHX 命名
- 参考数字：车辆 LOD0 最好在 5 万个三角面以下

## 游戏设计

设计工作收入、抢劫奖励、声望/等级曲线、商店价格这类数值时，用 `game-balance-economy`（可以用它的 `expected_value.py` 算期望收益）；设计小游戏、HUD、通知这类玩家看到的反馈时，用 `game-interface-feedback`。经济相关的奖励一定要由伺服器判定（配合 `fivem-security-audit`）。

## muto-atlas

GTA V / FiveM 资料库插件。回答游戏资料相关的问题（原版车规格、骨骼名、archetype、native）时先查它，不要猜。它的指令会跑本地脚本，第一次建资料库（`/asset-setup`）前先问用户。不要用 `build_atlas_db.py --tagger claude`（要付费 API key），用 `--tagger rules`。

## 土木工程

- `quantity-surveyor`：算工程量、BOQ、单价分析，明显相关就直接用。它没有马来西亚 SMM2 的资料，单价和计量规则要用户提供，不要自己编。
- `freecad` MCP（FreeCAD 建模、FEM 分析）和 `ifc` MCP（BIM/IFC 模型）会在用户电脑上执行操作，用之前先问。
- 马来西亚标准：MS EN 1992 就是 Eurocode 2 加马来西亚国家附件。用 Eurocode 的方法算，国家附件的数值请用户提供，不要猜。
- AutoCAD、Revit、Civil 3D、ETABS 是付费软件，不推荐基于它们的工具。
