# 技能使用规则

用户用中文交流，**每一条回复都用中文**，包括做完一大段工作后的总结、进度汇报和建议下一步；代码、日志、文件是英文也不要跟着切成英文（代码和指令本身可以保持英文）。用 AskUserQuestion 问用户时，问题、选项和选项说明也全部用中文。（2026-10-10 用户又提醒一次「说中文」）

## 用技能前一律先问

每次收到请求，先看已安装的技能、插件和 MCP 里有没有和这件事相关的。有的话，**先问用户要不要用，等用户同意再用**，即使明显对得上也一样。问的时候说清楚：
- 用哪个技能
- 它会做什么、为什么适合这件事
- 会不会改文件、装东西、跑脚本、开浏览器、连外部服务、要登录、派出子代理或跑很久

几个相关的技能可以一次列出来问，不要一个一个问。用户说"直接做"、或这次对话里已经同意过同一个技能，就不用再问。用户明确说不要用的，就不用。

这条规则适用于所有技能和插件，包括用户以后新加的。

## 记住用户的纠正

用户说我哪里做错了，或说"下次/以后/记住…"时，用 `correction-memory` 技能：先改好，再把规则写进 `LESSONS.md` 并提交。这是用户自己要求的固定流程，不用再问。下面导入的就是之前记下的经验，照着做：

@LESSONS.md

## 不用付费的东西

用户不要付费的工具和服务。需要付费 API key、订阅或额度的技能和功能都不用，也不推荐；只有免费的替代方案时才提，并说明它是免费的。比如 Blender MCP 的 Premium AI 生成 3D 模型、Gemini/Nano Banana 生图 API，都不要用。

## 写 FiveM / QBCore / Qbox 相关代码时

优先建议用户自己的 `fivem-script` 技能，再按需要搭配（都照上面的规则先问）：
- `fivem-pro`：FiveM 开发规范、resmon 性能优化、Sollumz + CodeWalker 做地图/MLO
- `fivem-security-audit`：审查 script 的后门、漏洞、性能问题，也能判断来路不明的 script 安不安全
- superpowers（规划、调试、审查）和安全检查技能（insecure-defaults、sharp-edges）
- `oxlib`、`oxmysql`、`ox-inventory`、`ox-target`：ox 系列的 API 速查
- `fivem-react-nui`：用 React + TypeScript + Vite + Tailwind 做 NUI
- `fivem-vehicle-mod`：做、修、上架 addon 车辆资源（meta 文件、改装套件、涂装、警笛、贴图大小、Enhanced 转换），包括模组警车和用 Sollumz 做车的流程。车辆资源上服前跑它自带的 `check_vehicle_resource.py`（本地、只读；用户同意用这个技能后就可以直接跑）；npx 工具第一次跑会下载套件，先说一声
- `fivem-graphics-pack`：画质包、调色（暖色/电影感）、visualsettings、2K/4K 贴图、ReShade 和 LUT。它的三个脚本都是本地运行、只写到指定的输出文件夹或只读，用户同意用这个技能后就可以直接跑。ReShade 是玩家自己装的，只在 Legacy 版、伺服器允许插件时有效
- `fivem-mlo-housing`：做或修 MLO、原版室内（IPL、entity set）、房屋系统（qbx_properties 等）、家具摆放。它的 `check_mlo_resource.py` 是本地只读检查，用户同意用这个技能后就可以直接跑；要在 Blender 里动手时照下面 3D 的规则先问
- `fivem-phone`：做 FiveM 手机或手机 app（npwd、lb-phone、qb-phone/z-phone）、自己做手机外框、折叠手机、手机界面设计。新手机从它的 `assets/phone-template`（沉浸式，6 种真机比例）开始。它的 `check_phone_app.py` 是本地只读检查，用户同意用这个技能后就可以直接跑；手机界面设计可以再问要不要搭配 `mobile-ios-design`、`mobile-android-design`、`apple-design`。lb-phone 本身是付费的，只在用户已经有它时帮写 app，不推荐购买

- `qbcore-framework`、`qbox-framework`：QBCore / Qbox 的 API。先看用户用的是哪个框架（`qb-core` 还是 `qbx_core`），不要混用；Qbox 以 docs.qbox.re 为准
- `fivem-security`：写伺服器代码时就防漏洞（事件验证、权限、限频）；写完再用 `fivem-security-audit` 审查
- `fivem-basics`、`lua-basics`、`fivem-deployment`：FiveM 资源结构、Lua 基础、FXServer 版本和 server.cfg

改完 FiveM 的 Lua 后，如果用户电脑上有 `qbx-lint`，就对改过的文件跑一次检查（只读，直接跑）；要用 `qbx-lint --fix` 或 `qbx-lint fmt` 改文件前先问。

`fivem` MCP 能在用户的伺服器上下指令、调用 native，权限很大：用之前先问，只连本机测试服，不要连正式服。

## 3D 模型和动作

Blender 技能（retopology、lod-pipeline、asset-optimization、uv-workflow、rigging、animation、export-pipeline、vehicle-artist、hard-surface、collision-proxy、texture-workflow，以及做室内用的 set-dressing、archviz、prop-artist、environment-artist）要通过 `blender` MCP 在用户自己的 Blender 里执行代码，用之前先问。做 GTA 模型时，在 Blender 里完成后提醒用户用 Sollumz 导出成 .ydr/.yft/.ycd。

要 3D 模型（道具、家具、食物、角色）时先建议 `free-3d-assets`：常见的东西先从 Poly Haven / Poly Pizza / Sketchfab 找免费模型（`blender` MCP 的 `search_assets`），独特的东西用用户自己电脑上的 Hunyuan3D 从图片生成（不用 Tripo、Meshy、Rodin 和 Blender MCP Premium，都要付费）。它的 `hunyuan3d_client.py` 只连用户本机的 Hunyuan3D 服务器，用户同意用这个技能后就可以直接跑；帮用户装 Hunyuan3D、启动服务器、在 Blender 里执行代码前要先问。`blender` MCP 本地模式的 Inference Steps 要设 20（Hunyuan3D 2.1 最多 20）。Hunyuan3D 授权不适用于欧盟、英国、韩国，用户在那些地方要提醒。

要免费图片、视频（NUI 背景、手机壁纸、商店图片、loading screen、贴图、生成 3D 用的参考图）或音乐、音效时，先建议 `pixabay-assets`。它的 `pixabay.py` 要用户自己的免费 API key（放在环境变量 `PIXABAY_API_KEY`，不要写进文件或提交），会连 pixabay.com，用户同意用这个技能后就可以直接跑。Pixabay 的音乐和音效没有 API，要手动下载。

做 GTA/FiveM 角色动画或自定义表情时用 `fivem-animation`（流程：Blender → Sollumz → CodeWalker → rpemotes/TaskPlayAnim；Mixamo 动作用它的 `references/mixamo-to-gta.md`，经 muto-ped-rig 转到 GTA 骨骼，装 muto-ped-rig 前先问），它自带的 `check_anim_resource.py` 是本地只读检查，用户同意用这个技能后就可以直接跑。

学或做动画时：先用 `motion-design` 讲原则（时间、间距、缓动、预备动作、跟随），再用 `blender-animation-rigging` 和 `animation` 在 Blender 里操作；用户想学的时候配合 `anthropic-skills:learn` 一步步教，每一步让用户自己动手。`blender-animation-rigging` 写的是 Blender Lab 官方 MCP，这里装的是 `blender` MCP（mcp-for-blender），用它的 `execute_blender_code` 执行同样的 bpy 代码。`motion-design` 提到的 blender-motion、aftereffects-motion 没有装（前者会接付费的 Higgsfield），不要去找。

这些 Blender 技能是通用游戏美术流程，用于 GTA 时以 GTA 的规则为准：
- 车辆骨骼名必须用 GTA 的固定名字（如 `door_dside_f`、`wheel_lf`），用 muto-atlas 查（`/vehicle`），不要用技能里的 `SM_Vehicle_*` 命名
- 碰撞用 Sollumz 的 bounds 和碰撞 flag（muto-atlas `trunk/flags.md`），不用 collision-proxy 里的 UCX/UHX 命名
- 参考数字：车辆 LOD0 最好在 5 万个三角面以下

## 界面美化和设计

做网页、FiveM NUI、HUD、菜单这类界面时，可以先问要不要用：`example-skills:frontend-design`（基础）、`impeccable`（最完整：audit 找问题、critique 点评、polish 润色、animate 加动效、bolder/quieter 等）、`taste-skill:design-taste-frontend`（避免 AI 模板感，旧站改造用 `redesign`）。FiveM NUI 跑在游戏内浏览器里，动效和特效要克制，以不影响帧数为准。做 FiveM 菜单、NUI 时先建议 `fivem-menu-design`（它会再搭配 `game-ui-ux`、`game-feel`、`ui-ux-pro-max`、`impeccable`），它的 `check_nui_menu.py` 是本地只读检查，用户同意用这个技能后可以直接跑。要加细节、打磨动效时可以建议 `make-interfaces-feel-better`、`emil-design-eng`、`review-animations`、`find-animation-opportunities`；界面做完用 `break-ui` 拿极端数据测一遍；风格还没定时可以建议 `prototype` 做几个版本给用户挑。审查做好的界面可以建议 `visual-critique` 插件（`/critique-screen`）、`ui-design-review`、`web-design-guidelines`（要联网下载规则）；要统一整个服务器的界面风格可以建议 `design-brief` → `design-tokens` → `design-review`。这些都要先问。海报、静态图用 `canvas-design`。做游戏 HUD、菜单时可以再问要不要搭配 `game-ui-design`；定配色用 `color-theory`，定字体用 `typography`，做完 NUI 用 `typography-audit` 检查字体；设计动效的节奏和性格可以用 `lottie-motion-design`；做伺服器整套品牌用 `branding`；规划设计系统、做原型和测试可以用 `design-systems`、`prototyping-testing` 插件。`vehicle-design`、`character-design`、`lighting-design` 讲外形和灯光的设计原理，做 GTA 车、ped、MLO 灯光时可以搭配，但骨骼、碰撞、灯光设置照 GTA 的规则。做 icon 时可以先问要不要用：自己画一整套风格统一的 SVG icon（FiveM 菜单、HUD、手机 app）用 `icon-set-generator`；伺服器 logo、手机 app 图标用 `app-icon-expert`；找现成的免费 icon 用 `better-icons`（要 `npm install -g better-icons` 或 npx，第一次装之前先问；它的 `better-icons setup` 会改 MCP 设置，不要自己跑；每个 icon 库授权不同，Tabler、Heroicons 是 MIT，Lucide 是 ISC，Material Symbols 和 mdi 是 Apache 2.0，这些都能免费商用；CC BY 的要署名）；网站 favicon 用 `favicon-gen`（在 Windows 上 ImageMagick 的指令是 `magick`，不要用 `convert`，那是 Windows 自带的磁盘转换指令）。FiveM 里的 icon 要打包进资源，不要从 CDN 加载。`brandkit`、`imagegen-frontend-*` 要配外部生图工具，Claude Code 自己不能生图；免费的选项不确定时先说明，不推荐付费生图服务。做视频用 Remotion 技能（只在本机装了 `--remotion` 才有），用户的公司超过 3 人就要付费授权，要先提醒。

## 游戏设计

设计工作收入、抢劫奖励、声望/等级曲线、商店价格这类数值时，用 `game-balance-economy`（可以用它的 `expected_value.py` 算期望收益）；设计小游戏、HUD、通知这类玩家看到的反馈时，用 `game-interface-feedback`。经济相关的奖励一定要由伺服器判定（配合 `fivem-security-audit`）。设计任务、抢劫、小游戏时可以问要不要用 `puzzle-design`、`level-design`；写剧情、城市背景、帮派设定用 `narrative-design`、`worldbuilding`、`lore-building`；想让主播容易出精彩片段用 `streamer-bait-design`，彩蛋用 `easter-egg-design`；核心玩法、打斗、社群用 `game-design-core`、`combat-design`、`community-building`。系统方面：NPC 对话和行为用 `dialogue-systems`、`game-ai`，音效用 `audio-design`，制作和等级系统用 `survival-crafting`、`rpg`，镜头用 `camera-systems`，玩家数据存储用 `save-systems`。这些都是通用游戏设计，例子多是 Godot/Unity，用在 FiveM 时换成 Lua、oxmysql、ox_lib 的做法；FiveM 的存档就是数据库，玩家进度和奖励一样要伺服器判定。

## muto-atlas

GTA V / FiveM 资料库插件。回答游戏资料相关的问题（原版车规格、骨骼名、archetype、native）时先查它，不要猜。它的指令会跑本地脚本，第一次建资料库（`/asset-setup`）前先问用户。不要用 `build_atlas_db.py --tagger claude`（要付费 API key），用 `--tagger rules`。

## 土木工程

- `quantity-surveyor`：算工程量、BOQ、单价分析，相关时先问要不要用。它没有马来西亚 SMM2 的资料，单价和计量规则要用户提供，不要自己编。
- `freecad` MCP（FreeCAD 建模、FEM 分析）和 `ifc` MCP（BIM/IFC 模型）会在用户电脑上执行操作，用之前先问。
- 马来西亚标准：MS EN 1992 就是 Eurocode 2 加马来西亚国家附件。用 Eurocode 的方法算，国家附件的数值请用户提供，不要猜。
- AutoCAD、Revit、Civil 3D、ETABS 是付费软件，不推荐基于它们的工具。
