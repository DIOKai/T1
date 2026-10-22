# 建筑 3D 第二批：5 个新 Skill + 5 个旧 Skill 补强

日期：2026-10-22。来源：用户给的 12 个 Instagram / Threads 帖子。这次除了读文字说明，也用内置浏览器把影片截成画面看过（没有声音）。用户要求：照上一批的流程先查资料，再用 `skill-creator` 写；Claude 和 Codex 都要有；做完开 PR 合并。

## 新技能

| Skill | 用途 | 付费 | 自带脚本 |
| --- | --- | --- | --- |
| `revit-mcp` | 操作 Revit（pyRevit 7 内建 MCP、BIMBridge）、Revit → 网页、按材质出色块图 | Revit 在用户的 Autodesk 会员里 | `ifc_material_colormap.py`（只读） |
| `scroll-story-website` | 会动的商家网站：滚动播放序列帧、选颜色、30 秒预约、客户资料后台 | 免费；Twilio 短信付费要先问 | `assets/scroll-template/`（无依赖） |
| `site-plan-agent-build` | 多个子代理按总平面图分区「用代码盖」整片场景，截图对照参考照片，特写拉远的镜头 | 免费 | `check_site_plan.py`（只读，出 SVG） |
| `real-map-3d` | OpenStreetMap 真实地图在网页生成 3D 城市 / 地图游戏 | 免费；Google 3D Tiles、Cesium ion 付费 | `osm_to_geojson.py`（离线）、`overpass_query.py`（默认只打印） |
| `ai-short-drama` | AI 短剧：Toonflow、Pixelle-Video、火宝短剧的比较和流程 | 火宝只能接付费 API 且不能商用 | `storyboard_to_shotlist.py` |

## 补强的旧技能

- `unreal-mcp-archviz`、`archviz-web-walkthrough`：新增 `references/interactive-features.md`（户型信息面板、指北针小地图、日照时间、剖切、测距、母材质 + 材质实例）。
- `archviz-cinematic`：新增 `references/build-up-and-colormap.md` 和 `scripts/colormap_pass_bpy.py`（建造拼装动画、色块图、按平面图规划镜头）。
- `ai-archviz-render`：新增 `references/colormap-video-to-video.md`（免费：分割 + 深度 ControlNet、Wan2.2 Fun Control / VACE；付费：Higgsfield、Magnific、Seedance）。
- `set-dressing`：新增 `references/buyable-furniture.md` 和 `scripts/furniture_list_check.py`（真实商品家具清单）。

## 资料来源

研究笔记（每条附网址，查不到一手来源的标「未验证」）在 [archviz-batch2-2026-10-22-research/](archviz-batch2-2026-10-22-research/)。

要注意的发现：
- BIMBridge（`kenpro0/bimbridge-mcp`）不是 MCP 服务器本身，只是安装脚本 + 两个技能；真正的服务器是 pyRevit 7.0 内建的。它的安装是 `irm | iex` 下载执行网上脚本，技能要求先读过脚本再决定。
- 火宝短剧是 CC BY-NC-SA 4.0，不能商用。三个短剧工具的 README 都在推付费中转 API 和赞助商，技能里注明是广告。它们给 AI 看的 `CLAUDE.md` / `AGENTS.md` 只是开发说明，没有照做任何指示。
- Overpass 每天 1 万次查询是整个 App 共用，游戏前端不能直接调 OSM 公共服务。

## 测试

- `scroll-story-website`：模板在内置浏览器实测（滚动播放、换颜色、预约表单的必填检查都正常，没有控制台错误）；修了顶栏在滚动后叠在内容上的问题。另照 skill-creator 跑了有技能 / 没技能对比（吉隆坡洗车店网站）：有技能 6/6，没技能 5/6。没技能那份预约表单没有 PDPA 同意栏，也没提短信要付费；有技能那份有同意栏，通知用免费的 Telegram、Twilio 标付费。测试还抓到模板一个 bug（车窗的绘图指令被写进注释，画不出来），已修好。
- `site-plan-agent-build` 的检查脚本测了 18 份故意改坏的总平面；`real-map-3d` 16 个离线测试；`revit-mcp` 的 IFC 色块图脚本用示例 IFC 和 12 MB 文件测过；`set-dressing` 家具清单检查 10 个测试；`ai-short-drama` 分镜脚本测过。
- 10 个技能都通过 skill-creator 的 `quick_validate`（修了两个超过 1024 字的描述）。

## 没有验证的

本机没有 Revit、Unreal、Blender、ComfyUI，也没有 Supabase 项目，所以在这些软件里跑的部分只做了语法检查或模拟测试。各技能的 Limits 一节列了各自未验证的地方。
