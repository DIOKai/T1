---
name: fivem-asset-acceptance
description: Use when checking a FiveM asset resource before it goes on the server, after a conversion, or after buying or downloading it - props, vehicles, liveries, clothing, MLO and maps, weapons, animations, sounds, graphics packs or peds - to run the release gate (packaging, name conflicts, 16/48 MiB sizes, LODs, collision, textures, escrow, licence and source) and plan the in-game test. Triggers include 上服前检查, 验收, 素材检查, 资源能不能用, 买来的素材.
---

# FiveM 素材上服验收

这个技能只做**验收**：判断一包素材能不能上服、哪里有问题、还有什么没验证。不重做模型，不自动压缩、减面、删 mipmap 或改原档（LESSONS：转换 1:1，尺寸问题只报告）。修东西交给对应类别的技能。

先确认：素材类别、Legacy 还是 Enhanced、game build、资源名、来源（自制 / 免费下载 / 买的 / 转换的）、交付目录。只检查交付副本；原档目录（如 `ori\`）保持不动。

## 第 1 步：清单和来源

1. 列文件清单和哈希（`fivem-asset-catalog` 的 `catalog_assets.py --hash`，只读）。1:1 转换用源和成品的哈希对比证明没动过。
2. 根目录要有 `CREDITS.md` / `LICENSE` / `SOURCE.txt`：作者、来源网址、授权、日期，转换的写原档哈希。“免费下载”不等于可以转发；Hunyuan3D 授权不适用欧盟/英国/韩国，SMPL 类动捕只能非商用（CLAUDE.md）。模板见 [package-and-provenance.md](references/package-and-provenance.md)。
3. 加密：Cfx Asset Escrow 支持 Lua、YFT、YDD、YDR。加密的资源根目录有 `.fxap`，被加密的 stream 文件开头是 `FXAP` 而不是 `RSC7`。只能在有授权的伺服器 key 上跑（否则控制台 “You lack the required entitlement”），内容、大小、LOD 都看不到——列为“需人工/未验证”，**绝对不要尝试解密**。买来的素材走 `fivem-authorized-asset-workflow`。

## 第 2 步：跑静态闸门

```
py -3 -I .claude/skills/fivem-asset-acceptance/scripts/asset_gate.py <资源或资源文件夹> [更多] [--json] [--only prop,vehicle] [--list] [--verbose] [--ui]
```

只读、标准库。它会：

- 认出每个资源的类型（可以多种）：道具、车辆、服装、地图/MLO、武器、动画、音效、画质包；`--ui` 时再加手机 App 和 NUI；纯脚本跳过（脚本安全用 `fivem-security-audit`）。
- 对每种类型调用兄弟技能的检查器（`--json`），每个资源跑一次（问题归属准确），同类型有多个资源时再合并跑一次抓跨资源冲突（重名、id 撞号）。检查器列表和各自看不到的东西见 [checkers.md](references/checkers.md)。
- **人物 ped 没有检查器**：一律标“⧗ 需人工”，照 `fivem-ped-character` 人工看骨骼、权重、组件。
- 通用检查（所有类型）：没 manifest、stream 里的 XML / 源文件、文件名空格、16/48 MiB（和 FXServer 同一个公式，按 RSC 头算，不是磁盘大小）、escrow、没有来源/授权文件、两个资源串流同名文件、`stream_enhanced` 缺 `stream` 里的文件（Enhanced 有 `stream_enhanced` 时只载入它）。
- 最后印一张中文汇总：✓ 通过 / ⚠ 警告 / ✘ 失败 / ⧗ 需人工 / ⧗ 未完成，再附上找到的类型的游戏内检查清单。

退出码：0 没错误，1 有错误，2 有检查器出错或超时（结果不完整，要说出来）。

怎么读结果：✘ 错误 = 上服会坏（不加载、闪退、隐形、串流问题），先修；⚠ 警告 = 很可能有问题或和原版差很多，逐条判断；ℹ 提示 = 参考（原版的数值、未验证的说法）。汇总里 “通过” 只代表静态检查没发现问题。

## 第 3 步：工具里目视检查

照 [visual-and-runtime.md](references/visual-and-runtime.md)：在 CodeWalker / Blender 打开背面剔除，从玩家位置多方向看缺面破洞；看 LOD 切换、碰撞（CodeWalker 显示 collision）、比例和原点。车辆要照 LESSONS 查引擎舱、车底、各画质等级、破洞扫描。Blender 预览和游戏验收分开记录；动 Blender、导出、转换都要先问。

## 第 4 步：游戏内测试（只在本机测试服）

照闸门最后印的清单逐项做（每种类型的完整表在 visual-and-runtime.md）：冷启动进服、restart 资源一次、F8 和伺服器控制台找 16/48 MiB、“Could not add data_file”、entitlement 警告；两个客户端；Legacy 和 Enhanced 都要用就两边都进。脚本资源才看 `resmon` / profiler（`fivem-performance-profile`）。不要连正式服；`fivem` MCP 只连本机测试服，用前先问。

## 第 5 步：交报告

分三栏：**已通过**、**失败**（带文件路径和修法交给哪个技能）、**未验证**（escrow 内容、yft 内部结构、二进制碰撞旗标、ped、没进游戏测的项目）。写上工具和版本、game build、检查器输出位置。静态通过但没进游戏测的，明确写“游戏内未验证”。看过教学影片、找到模型来源或扫描过文件，都不能单独算验收完成。

## 用到的技能

`fivem-prop-creator`、`fivem-vehicle-mod`、`fivem-vehicle-livery`、`fivem-clothing-creator`、`fivem-mlo-housing`、`fivem-weapon`、`fivem-animation`、`fivem-vehicle-sound`、`fivem-graphics-pack`、`fivem-phone`、`fivem-menu-design`（各自的检查器），`fivem-ped-character`（人工），`fivem-asset-catalog`、`fivem-file-analysis`（打不开的文件）、`fivem-authorized-asset-workflow`（买来的素材）。照 CLAUDE.md，用这些技能前先问用户。
