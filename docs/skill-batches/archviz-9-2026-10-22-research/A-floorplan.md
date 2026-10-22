# A — floorplan-to-blender 研究笔记

日期：2026-10-22。用途：给新技能 `floorplan-to-blender` 打底（平面图 / 房源照片 / AI 参考图 → Blender 里的准确 3D 房子，通过 `blender` MCP 的 `execute_blender_code` 跑 bpy）。
标记：每条事实后面附来源；没有一手来源支撑的标 **未验证**；我自己推出来的做法标 **（推论）**。

---

## 0. 环境事实（已核对）

- docs.blender.org/api/current 目前是 **Blender 5.2 Python API**（首页标题 "Blender 5.2 Python API Documentation"）。来源：https://docs.blender.org/api/current/index.html
- ahujasid/blender-mcp（现名 MCP for Blender）README 列出 9 个工具：`execute_blender_code`、`look`（viewport / camera / angles 多视角拼图 / frames，显示模式 solid、material、rendered、wireframe、xray，也能显示渲染或图片文件）、`get_scene_info`、`generate_3d`、`search_assets` / `import_asset`（Poly Haven、Sketchfab、Poly Pizza）、`get_addon_status`、`disable_telemetry`、`record_trajectory_feedback`。README 警告 `execute_blender_code` 可跑任意 Python，"ALWAYS save your work before using it"。授权 MIT。默认会收集匿名使用记录（安装 ID、工具名、成功与否等），内容收集默认关。来源：https://github.com/ahujasid/blender-mcp （README、LICENSE）
  - 注意 `generate_3d` "Premium generators are preferred automatically" —— 用户规则不用付费，技能里不要调用它去生成（或只在本地 Hunyuan3D 模式下，交给 `free-3d-assets`）。
  - 用户 CLAUDE.md 写的是 `get_viewport_screenshot`/`execute_blender_code`；新版 README 的看图工具叫 `look`。技能里两种都提一句，先用 `get_addon_status` 看实际有哪些工具 **（推论）**。

---

## 1. 从平面图读出尺寸

### 1.1 找比例（优先级从高到低）
1. **图上写的尺寸串**（如 `12'-6" x 10'-0"` 或 `3600`）：在图上量两条尺寸线端点之间的像素，除以标的长度 → 像素/米。至少取两个方向（X、Y）各一条、最好三条以上，比较一致性；X、Y 比例差 >2% 说明图被拉伸过（房源图常见）**（推论）**。
2. **比例尺 / 图例**（scale bar）：同上量像素。注意 PDF 打印比例（1:100）只在矢量 PDF 或原尺寸打印下有效，截图后就失效 **（推论）**。
3. **房间尺寸标签**（房源图常见 "Bedroom 11'2" x 10'6""）：这类数字通常是**室内净尺寸**（墙面到墙面），不是轴线尺寸 **未验证**（行业惯例，没找到统一标准）。
4. **标准构件推比例**（没有任何数字时的兜底，精度差，要告诉用户）：
   - 美国 IRC R311.2：每户至少一个出入门，净宽 ≥ 32 in（门开 90° 时门面到门挡量）、净高 ≥ 78 in；要达到 32 in 净宽实际要用 36 in 门；户内其他门没有最小尺寸规定。来源（二手，转述 IRC）：https://buildingcodetrainer.com/front-door-size-residential-egress/ 。ICC 原文页 codes.iccsafe.org 返回 403，**未直接核对条文**。
   - 美国常见室内门 28/30/32 in，卧室门常 30–32 in **未验证**（论坛：https://forum.nachi.org/t/interior-door-width/179624 ）。
   - 英国：英格兰和威尔士最常见室内门 1981 × 762 mm（2'6"），838 mm 与 Part M 轮椅通行相关，公制系列 2040 × 526/626/726/826/926 mm；苏格兰常见 2040 × 726 mm。来源（零售商，非标准）：https://www.howarth-timber.co.uk/help-advice/uk-door-sizes 、https://www.doorsuperstore.co.uk/help-and-advice/product-guides/internal-doors/uk-door-sizes-and-conversion-chart/
   - 马来西亚：没查到门宽标准；天花板高度 UBBL by-law 44 的数值**没查到一手条文，未验证**（不要写 2.6 m 当事实）。UBBL 第 42 条：其他居室最小 6.5 m²、宽 ≥ 2 m（PAM 文件转述）。来源：https://pam.org.my/images/resources/bureau/Category_C_-_Building_Control-2025.pdf
   - 门在平面图上的弧线半径 = 门扇宽，可以直接量弧线半径 **（推论）**。
   - 用标准构件推比例：量 3–5 扇门取中位数，不要只量一扇；结果标"估计 ±5–10%" **（推论，经验值）**。
5. **层高**：平面图通常不标。来源顺序：剖面/立面图 → 房源文字（"9 ft ceilings"）→ 照片里门高（门 ≈ 2.03 m / 80 in 或 1.98–2.04 m）对照天花 → 默认值（美国常见 8 ft = 2.44 m，新房 9 ft；默认值要告诉用户）**未验证（经验值）**。

### 1.2 英制 / 公制
- 全部内部存 **米**（Blender 默认单位 1 BU = 1 m）。解析 `12'-6"`、`12' 6"`、`12.5'`、`3600`（mm）、`3.6`（m）。小数英尺和英寸混写要分清 **（推论）**。
- JSON 里保留原始字符串（`"source_label": "12'-6\""`）方便核对 **（推论）**。

### 1.3 墙厚惯例
- 美式木结构：外墙尺寸一般标到**外墙立柱外皮**（face of stud），室内隔墙多标到**墙中线**；实砌体墙标到墙外皮；砖饰面+立柱标到立柱线。这是惯例不是统一标准，图纸应在说明里注明。来源（教材幻灯片 + 论坛）：https://www.slideshare.net/jayneross/reading-floor-plans 、https://forums.augi.com/archive/index.php/t-59740.html 、https://community.graphisoft.com/t5/Documentation/Dimension-to-CENTER-of-walls/td-p/113255
- 典型厚度：2x4 立柱实际 3.5 in，加两面 1/2 in 石膏板 ≈ 4.5 in（≈ 0.115 m）；外墙 2x6 + 外饰面常见 6.5–8 in **未验证（常识值，未找到一手标准）**。
- 马来西亚/亚洲常见砖墙：外墙 ~230 mm（9 in 砖）、内墙 ~115 mm（4.5 in 砖）**未验证**。仓库里 Bonsai 技能默认外墙 WAL200（200 mm）、内墙 WAL100（100 mm）。
- 做法：墙厚按图上墙的像素粗细量（粗线 = 外墙），再四舍五入到最近的常见值，并在 JSON 里标 `thickness_source: "measured" | "default"` **（推论）**。

### 1.4 缺尺寸时
- 只有总面积：用比例估出整体外包尺寸，再按面积反推比例因子：`k = sqrt(listing_area / measured_area_in_px²)` **（推论）**。
- 只有部分房间尺寸：用有尺寸的房间定比例，其他房间按像素换算，并在报告里列"哪些是量出来的、哪些是推出来的" **（推论）**。
- 照片-only（没有平面图）：用照片里的门、标准瓷砖（300/600 mm、12/24 in）、橱柜（台面高 ~0.9 m、深 ~0.6 m）推尺寸 **未验证（经验值）**；精度差，先跟用户确认关键尺寸。
- AI 参考图：本身就没有可信尺寸，只当风格参考；尺寸要用户给或用常见值 **（推论）**。

### 1.5 用房源面积交叉核对
- ANSI Z765-2021（美国独栋/联排住宅测量标准，Fannie Mae / Freddie Mac 采用）：从外墙**外饰面**量起；只算地上已完成面积；楼梯算在它下行出发的那一层；车库、未完成地下室、有顶门廊不算；已完成地下室单列；四舍五入到整平方英尺；不适用于公寓式 condo/co-op。来源（二手）：https://www.mckissock.com/blog/appraisal/appraisal-career/freddie-mac-announces-adoption-of-ansi-measurement-standard/ 、https://www.opendoor.com/articles/how-to-measure-square-footage 。层高 ≥ 7 ft 才算（Opendoor 转述）——**未直接核对标准原文**。
- iGUIDE 等扫描服务的面积**包含室内墙占地**，跟 ANSI 不能直接比。来源：https://help.youriguide.com/support-center/floorplans-and-measurements/information/iguide-method-of-measurement
- Zillow 面积来源：没有找到 Zillow 官方说明；评论文章说多半来自公共记录，也可能被经纪人输入覆盖，改建过的老房常对不上。来源（二手）：https://inman.com/2007/06/25/how-reliable-are-square-footage-figures 、https://bulletins.ncrec.gov/a-regulatory-affairs-division-case-study-square-footage-dont-include-unfinished-or-unheated-areas/ ——所以房源面积只当**粗核对**（容差建议 ±5–10%，经验值，**未验证**）。
- 核对方法 **（推论）**：
  - 外包面积 = 外墙外轮廓多边形面积（shoelace 公式）×（层数），减掉车库、阳台、门廊。
  - 室内净面积 = 各房间地板多边形之和。外包面积 ≥ 净面积 + 墙占地。
  - 1 m² = 10.7639 ft²。
- **Zillow 使用条款**：zillow.com/z/corp/terms 返回 403，**未核对**。技能里不要自动爬 Zillow，请用户自己把平面图/照片存成文件给我；复刻真实房子只做个人用途，公开发布前提醒版权（房源照片、平面图属拍摄者/经纪公司）**（推论）**。

---

## 2. 中间表示（JSON layout）

### 2.1 现有开放格式 / 项目
| 项目 | 内容 | 授权 | 状态 |
|---|---|---|---|
| CubiCasa5k | 5000 张平面图，SVG 多边形标注，80+ 类别；Zenodo 下载 | **CC BY-NC 4.0（非商业）** | 最后推送 2026-02-10 |
| grebtsew/FloorplanToBlender3d | OpenCV 图像处理把平面图图片转 Blender 房间；有 Config ini、Stacking 多层语言、Docker、server；需 Blender ≥ 2.93、Python ≥ 3.8；图片要小 | GPL-3.0 | 最后推送 2024-10-09 |
| art-programmer/FloorplanTransformation（Raster-to-Vector，ICCV 2017） | 平面图栅格 → 向量（墙角点、墙、门窗、房间） | MIT | 最后推送 2022-06-21 |
| bertjiazheng/Structured3D | 结构化 3D 数据集（junctions / lines / planes + 语义）| 代码 MIT（数据另有条款，**未核对**） | 2025-02-24 |
| furnishup/blueprint3d | three.js 室内编辑器，墙由 corners + walls 组成的 JSON | MIT | 2021-01-20（停更） |
| Archipack（s-leger） | Blender 建筑参数化：墙、门窗、楼板、楼梯、屋顶；免费版 + 付费版 | GPLv3 | GitHub 最后推送 2020-03-29；**Blender 5 兼容未验证**（大概率不能用） |
| Archimesh | Blender 建筑元件（房间、门、窗、柱、楼梯）；4.1 前内置，现在是 Extensions 平台上的扩展 "as it is, with limited support"，v1.2.5（2024-05-14），最低 4.2 | GPL-2.0-or-later | 页面提到 Blender 5 的说明，**Blender 5 是否正常未实测** |
| IFC（buildingSMART）+ Bonsai | 真正的开放 BIM 标准；仓库已有 bonsai-* 技能 | IfcOpenShell/Bonsai LGPL/GPL **（未逐个核对）** | 活跃 |

来源：
- https://github.com/CubiCasa/CubiCasa5k ，LICENSE 原文："CubiCasa5K is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License."（raw.githubusercontent.com/CubiCasa/CubiCasa5k/master/LICENSE），GitHub API pushed_at
- https://github.com/grebtsew/FloorplanToBlender3d （README，GitHub API: spdx GPL-3.0, pushed_at 2024-10-09）
- https://github.com/art-programmer/FloorplanTransformation （LICENSE MIT）
- https://github.com/bertjiazheng/Structured3D 、https://github.com/furnishup/blueprint3d （GitHub API）
- https://wiki.osarch.org/index.php/Archipack ；https://api.github.com/repos/s-leger/archipack
- https://extensions.blender.org/add-ons/archimesh/

结论：**不要依赖这些代码或数据**（GPL 会传染、CubiCasa 非商业、Archipack 停更）。技能自己定义一个小 JSON，由 Claude 看图填写（多模态读图），再由一个本地 Python 脚本（只用标准库 + bpy）建模。参考它们的**概念**：CubiCasa 的 Wall/Door/Window/Room 多边形分类，Raster-to-Vector 的"墙角点 + 墙段"图结构，blueprint3d 的 corners/walls 拓扑 **（推论）**。

### 2.2 建议的 JSON schema（草案，**（推论）**）
```json
{
  "schema": "floorplan-to-blender/1",
  "units": "m",
  "source": {"type": "plan_image|pdf|photos|ai_ref", "files": ["plan.png"],
             "scale": {"method": "dimension_string|scale_bar|door_width|area", "px_per_m": 84.2,
                       "samples": [{"label": "12'-6\"", "px": 320.5, "m": 3.81}], "error_pct": 1.2},
             "listing_area": {"value": 1450, "unit": "ft2", "standard": "ANSI Z765?|unknown"}},
  "levels": [{"id": "L1", "elevation": 0.0, "height": 2.74, "slab_thickness": 0.2}],
  "walls": [
    {"id": "W1", "level": "L1", "kind": "exterior|interior",
     "path": [[0,0],[10.2,0],[10.2,8.4]], "closed": false,
     "thickness": 0.2, "thickness_source": "measured|default",
     "justify": "center|left|right", "height": null, "base_offset": 0.0}
  ],
  "openings": [
    {"id": "D1", "wall": "W1", "segment": 0, "type": "door|window|opening|sliding_door|garage_door",
     "offset": 3.2, "offset_ref": "start|center", "width": 0.91, "height": 2.03, "sill": 0.0,
     "swing": "in_left|in_right|out_left|out_right|none"}
  ],
  "rooms": [
    {"id": "R1", "name": "Living", "level": "L1", "polygon": [[0.1,0.1],[5,0.1],[5,4],[0.1,4]],
     "floor_finish": "wood|tile|carpet", "ceiling_height": null, "label_area": {"value": 210, "unit": "ft2"}}
  ],
  "stairs": [
    {"id": "S1", "from": "L1", "to": "L2", "type": "straight|L|U", "start": [6,1], "direction": [0,1],
     "width": 0.9, "risers": 15, "riser": 0.18, "tread": 0.28}
  ],
  "fixtures": [{"type": "kitchen_counter|island|tub|shower|toilet|fireplace", "polygon": [], "height": 0.9}],
  "notes": ["Hall closet depth guessed 0.6 m"]
}
```
设计要点：
- 墙用**轴线 polyline + 厚度 + justify**（跟 IFC/Bonsai 的"轴线 + 材料层"一致，可直接映射到 `create_room_with_mitered_corners(corners=...)` 和 `add_interior_wall(start_xy, end_xy)`）。
- 门窗挂在**墙 id + 段号 + 沿墙偏移**上，不存世界坐标——墙移动时门窗跟着走，也能检查"门窗是否超出墙段 / 是否压在墙角"。
- 每个数字可带 `*_source`，最后报告"量出来 vs 猜的"。
- 房间多边形用于：地板、天花、面积核对、命名。

---

## 3. bpy 建模技巧（Blender 5.2 API 已核对的部分）

### 3.1 参考图（把平面图放进场景并定比例）
- **图片转平面**：Blender 4.2 起"Import Images as Planes"变成内置：`bpy.ops.image.import_as_mesh_planes(filepath=..., directory=..., files=[{"name": "plan.png"}], size_mode='ABSOLUTE', height=<平面图真实高度 m>, align_axis=..., shader='SHADELESS'|'EMISSION'|'PRINCIPLED', use_transparency=..., ...)`。`size_mode` 可选 `ABSOLUTE`（绝对尺寸）、`CAMERA`、`DPI`（像素/英寸）、`DPBU`（像素/Blender 单位，参数 `factor`）。**用 `size_mode='DPBU', factor=px_per_m` 就能让 1 m = 1 BU 直接对上比例。** 来源：https://docs.blender.org/api/current/bpy.ops.image.html （定义在 `startup/bl_operators/image_as_planes.py`）
  - `align_axis` 的取值本次没逐一核对（默认 `'CAM_AX'`）；要平放在地面用 `'+Z'` 或建好后旋转 **未验证具体枚举名**。
  - 这是 operator，经 MCP 跑在 timer 里可能缺 context；稳妥做法是自己建平面 + 材质（`bpy.data.images.load` + 一个 Image Texture 节点）**（推论）**。
- **相机背景图**（只在视口里显示，不进渲染）：`cam.data.background_images.new()`，`CameraBackgroundImage` 属性 `image`、`alpha`、`display_depth ('BACK'|'FRONT')`、`frame_method ('STRETCH'|'FIT'|'CROP')`、`offset`、`rotation`（仅正交）、`scale`、`use_flip_x/y`；相机要开 `cam.data.show_background_images = True`。来源：https://docs.blender.org/api/current/bpy.types.CameraBackgroundImage.html 、https://docs.blender.org/api/current/bpy.types.Camera.html
- 对齐流程 **（推论）**：选平面图上一个明确角点（外墙左下外角）放到世界原点；Y 轴朝图片上方；导入后用两个已知点检查距离误差 < 1%。

### 3.2 墙：斜接角（miter）
三种做法：
1. **自己算偏移多边形 + bmesh 挤出（推荐，无依赖）（推论）**：对每段 polyline 算左右法线偏移线，拐角处两条偏移线求交点（miter 点，= 角平分线方向 × t/2 / sin(θ/2)，或直接解两条直线交点），得到左、右两条偏移折线 → 组成墙脚多边形 → `bmesh.ops.extrude_face_region` 向上 `height`，或拉成 2D 面后加 Solidify。极锐角（<~15°）时 miter 会很长，要改成 bevel/截平 **（推论）**。闭合环要首尾也做 miter。
   - **T 型接头**（内墙碰外墙）：内墙轴线端点停在外墙**内皮**，不要穿进外墙（仓库 bonsai-walls 已经记过这个坑："knife-through-wall"）。
   - 每条墙一个对象或整层一个对象都可以；整层合成一个网格后可用 `bmesh.ops.remove_doubles` 焊接。多段相交时最简单是每段单独一块 + 对整层做一次 Boolean UNION（EXACT）**（推论）**。
2. **Solidify 修改器**：在墙轴线的竖直"纸片"网格上加 `SolidifyModifier`，`thickness`、`offset`（-1..1，0 为居中）、`use_even_offset=True`（保持拐角厚度均匀）、`solidify_mode='EXTRUDE'|'NON_MANIFOLD'`、`nonmanifold_thickness_mode='FIXED'|'EVEN'|'CONSTRAINTS'`。来源：https://docs.blender.org/api/current/bpy.types.SolidifyModifier.html 。对 L 角效果好；T/十字交叉要用 NON_MANIFOLD（Complex）模式，结果要检查 **（推论）**。
3. **Bonsai（要 BIM 时）**：`DumbWallGenerator.create_wall_from_2_points` + `DumbWallJoiner.connect` → IFC 斜接，见第 4 节。
- bmesh：`bmesh.ops.solidify(bm, geom, thickness)` 存在（把网格变成有厚度的壳）。来源：https://docs.blender.org/api/current/bmesh.ops.html

### 3.3 门窗洞（Boolean）
- `BooleanModifier`（5.2）：`operation` = `INTERSECT|UNION|DIFFERENCE`（默认 DIFFERENCE）；`operand_type` = `OBJECT|COLLECTION`；`solver` = `FLOAT`（快，不支持重叠几何）、`EXACT`（默认，共面面最好）、**`MANIFOLD`（最快，只对流形网格有效但结果更好）**；另有 `use_self`、`use_hole_tolerant`、`double_threshold`、`material_mode ('INDEX'|'TRANSFER')`、`collection`。来源：https://docs.blender.org/api/current/bpy.types.BooleanModifier.html
- 做法 **（推论）**：
  - 每个洞一个"切割盒"：宽 = 洞宽、高 = 洞高、深 = 墙厚 + 2×0.05 m（两边各伸出，避免共面），放在墙段局部坐标 `offset`、底在 `sill`；隐藏渲染（`hide_render=True`、显示为 `WIRE`/`BOUNDS`）。
  - 所有切割盒放进一个集合 `Cutters`，每面墙一个 Boolean，`operand_type='COLLECTION'`，比每洞一个修改器快。
  - 墙是闭合流形时用 `MANIFOLD`，否则 `EXACT`。
  - 不想保留修改器（导出 GTA/游戏）就 apply；要可编辑就保留。
  - 洞口要做**窗台/门框/玻璃**，玻璃后要有室内（见 LESSONS：门窗要真玻璃、后面要有真实室内）。
- 也可以不用 Boolean：直接在墙段上按洞口把墙拆成"洞左段 + 洞右段 + 洞上过梁 + 洞下窗下墙"四块盒子，几何最干净，没有 Boolean 失败的风险 **（推论）**。门窗多时这个更稳。

### 3.4 楼板、天花
- 楼板：外墙外轮廓多边形（或每个房间多边形）→ bmesh 面 → 向下挤出 `slab_thickness`，顶面在楼层标高 0；墙**坐在**楼板上（墙底 z=0）。Bonsai 技能也是同一个规则（`align_top_to_storey=True`：楼板顶在 Z=0，墙在上面）。
- 天花：每个房间多边形在 `z = ceiling_height` 放一块（法线朝下），或整层做一块板；上层楼板底 = 下层天花 **（推论）**。
- 房间地板分开做（不同材质：木地板/瓷砖），比一整块好上材质 **（推论）**。

### 3.5 检查用的俯视正交渲染叠图
- 相机：`cam.data.type = 'ORTHO'`、`ortho_scale` = 视野较大边长度（sensor_fit AUTO 时）；相机放在平面图中心正上方，旋转 (0,0,0) 朝下。`ortho_scale` 属性已核对：https://docs.blender.org/api/current/bpy.types.Camera.html ；"等于较大边长度"是 Blender 一般行为，**本次未在文档逐字核对**。
- 分辨率比例 = 平面图外包尺寸比例，`render.resolution_x/y` 设成跟原图同像素，叠图时可以直接逐像素比 **（推论）**。
- 渲染引擎：5.2 RenderSettings.engine 默认 `'BLENDER_EEVEE'`（5.x 不再叫 `BLENDER_EEVEE_NEXT`）。来源：https://docs.blender.org/api/current/bpy.types.RenderSettings.html 。（文档只列出 BLENDER_EEVEE，Cycles/Workbench 由插件注册——**推论**）
- 相机背景图**不进渲染**；要叠图就：(a) 把平面图平面放在 z=-0.01 用 Emission/Shadeless 材质，墙用半透明颜色，渲染一张；或 (b) 渲染墙的 silhouette（Workbench 平涂色）后用 Python（PIL 或 numpy）跟原图做差/叠加 **（推论）**。
- 更省事：blender-mcp 的 `look` 工具（viewport / camera / angles）直接看；仓库 `bonsai-project-setup` 也说视口截图比 MCP 里的渲染更可靠（渲染有时全黑）。

---

## 4. 仓库已有技能（可以委派，不要重复）

路径：`C:/Users/USER/OneDrive/Desktop/T1-main/wt-archviz-3d-skills/.claude/skills/`（共用 `bonsai_bim_helpers.py`，~5700 行）

| 技能 | 已经有的 | floorplan-to-blender 怎么用 |
|---|---|---|
| `bonsai-project-setup` | `setup_project()`：IfcProject→Site→Building→Storey；`WAL200`（200 mm 外墙）/`WAL100`（100 mm 内墙）两种 IfcWallType，`FLR200` 楼板，Frame/Glass/Panel 样式；`add_storey(name, elevation)`；**强制多角度截图审查**（FRONT/RIGHT/BACK/LEFT/TOP/PERSP_SE + 检查清单）；IDS 编写+验证、BCF；`add_wall_quantities()`、`fill_opening_overall_attrs()`；用 `bpy.ops.bim.save_project` 存档 | 用户要 BIM/IFC 时第一步。可以按 JSON 里的墙厚改 `exterior_wall_thickness`/`interior_wall_thickness`（如 0.23/0.115） |
| `bonsai-walls` | `create_room_with_mitered_corners(corners, wall_type_name, height, closed)`（真 IFC 斜接，`IfcRelConnectsPathElements`）；`add_floor_slab_from_walls(..., align_top_to_storey=True)`；`add_interior_wall(start_xy, end_xy, ...)` 自动把端点截到外墙内皮、同厚度内墙 L 角自动连接；`cleanup_orphan_walls()`；明确说不要用 Blender Boolean/Solidify（导出 IFC 会丢） | JSON `walls[kind=exterior].path` → `corners`；`walls[kind=interior]` 每段 → `add_interior_wall` |
| `bonsai-openings` | `add_parametric_door_to_wall(wall, target, width, height, operation_type)`、`add_parametric_window_to_wall(...)`、`add_equally_spaced_windows_to_wall(...)`（默认规则：窗等距居中）；真 `IfcOpeningElement`+`IfcRelVoidsElement`+`IfcRelFillsElement`；`target` 是**角点不是中心**（要减半宽）；`style_all_openings()`；门类型枚举 SINGLE_SWING_LEFT/RIGHT、DOUBLE_*、SLIDING_* | JSON `openings` 转成 `target = 墙起点 + 方向 × (offset - width/2)`。**注意**：floorplan 场景要按图上的位置放，不要套"等距居中"默认规则 |
| `archviz` | 很薄（71 行）：真实比例、相机 24–35 mm、HDRI+实际灯具、玻璃 IOR 合理；参考 `archviz-camera.md`、`archviz-lighting.md` | 建完后的材质、相机、灯光、出图交给它 |
| `set-dressing` | 布景：先锁布局再放道具、故事组团 3–7 件、不要堵门窗、留通道；`density-map.md`、`story-clusters.md` | 摆家具阶段 |
| `free-3d-assets` | 免费家具来源：Poly Haven（CC0）/ Poly Pizza / Sketchfab（看每个授权）经 `search_assets`/`import_asset`；独特物件用本机 Hunyuan3D（`hunyuan3d_client.py`，steps=20）；不用 Tripo/Meshy/Rodin/Premium；写 CREDITS.md；主要面向 GTA | 家具模型来源；GTA 相关的部分（Sollumz）只在用户要进 FiveM 时用 |

另外同一目录还有 `bonsai-roofs`、`bonsai-stairs`（`add_parametric_stair` + 楼梯洞 + 栏杆）、`bonsai-spaces-grid`（`add_space` = IfcSpace 房间）、`bonsai-drawings`（出平面/剖面 SVG——可以拿生成的平面图 SVG 回头跟原图比）。`bonsai_bim_helpers.py` 里还有 `audit_geometry()`：检查不同厚度墙互相穿插、楼梯穿楼板没开洞、楼梯洞没对齐。

**分工建议（推论）**：
- 默认（看图、渲染、游戏）：floorplan-to-blender 自己用纯 bpy 建网格（3.2–3.4）。
- 用户说要 BIM/IFC/施工图/算量：同一份 JSON 交给 bonsai-project-setup → bonsai-walls → bonsai-openings → bonsai-stairs → bonsai-spaces-grid，不用 Blender Boolean。
- 都做完：archviz（光和相机）→ set-dressing + free-3d-assets（家具）。
- 要进 FiveM：交给 `fivem-mlo-housing`。

---

## 5. 常见失败模式 + 验证方法

| 问题 | 怎么发现 | 来源 |
|---|---|---|
| 比例错（整栋大/小 2.54 倍或 0.3048 倍——英寸/英尺混淆） | 量门宽：落在 0.6–1.0 m 外就是比例错；外包面积 vs 房源面积 | （推论） |
| 墙角没接上 / 有缝 / 重叠 | 俯视正交叠图；BVHTree `overlap()` 找相交；墙端点到相邻墙的距离 | `mathutils.bvhtree.BVHTree.FromObject(object, depsgraph, *, deform, cage, epsilon)`、`overlap(other_tree)` 返回重叠面索引对：https://docs.blender.org/api/current/mathutils.bvhtree.html |
| 内墙穿过外墙（knife-through-wall） | bonsai `audit_geometry()`；或 BVH overlap 只看不同厚度的墙对 | 仓库 bonsai-walls / helpers |
| 悬空（楼板/家具/天花不贴） | 每个对象底部向下 `scene.ray_cast(depsgraph, origin, (0,0,-1))`，命中距离 > 1 cm 就是悬空 | `Scene.ray_cast(depsgraph, origin, direction, *, distance)` 返回 (result, location, normal, index, object, matrix)：https://docs.blender.org/api/current/bpy.types.Scene.html |
| 门窗洞没切穿 / 切到隔壁墙 | 从洞口中心沿墙法线双向 ray_cast：洞里应该打不到这面墙；切割盒深度 = 墙厚 + 余量 | （推论） |
| Boolean 失败（共面、非流形） | 切割盒伸出墙面；非流形用 EXACT；检查结果面数/是否非流形 | BooleanModifier 文档（solver 说明） |
| 窗户后面没室内 / 看穿到天空 | 从街上往窗里射线，必须先打到室内面（地板、墙、窗帘），不能打空 | 用户 LESSONS.md（2026-10-13 两条） |
| 楼放在空白方块上 / 构件浮空 | 从街景和仰视检查；ray_cast 向下 | 用户 LESSONS.md（2026-10-13） |
| 背面剔除导致游戏里"隐形" | 打开材质背面剔除再看 | 用户 LESSONS.md（GTA 车经验，墙同理） |
| 门窗压在墙角、窗在门的范围里 | JSON 校验：`offset - w/2 ≥ 墙厚/2 + 0.05` 且同墙洞口不重叠 | bonsai-project-setup 审查清单 + （推论） |
| 房间名/面积对不上 | 每个房间多边形面积 vs 图上标签（ft²/m²），差 > 5% 列出来 | （推论，阈值经验值） |
| 层高/门高不合理 | 门高 1.98–2.13 m、窗台 0.8–1.1 m、层高 2.4–3.0 m 外就提示 | **未验证（经验值）** |
| AI 自己"编"了图上没有的门 / 漏门（如卧室到浴室没门） | 建完后列出每个房间的门数，跟平面图逐一对；房间连通图（每个房间至少 1 个门/开口通到走道） | 厂商博客提到 AI 平面图出现"卧室到浴室没有门"：https://www.mindstudio.ai/blog/claude-3-creative-app-mcp-connectors-blender-adobe-sketchup （一家之言） |

### 5.1 推荐验证流程（推论）
1. **JSON 层（建模前）**：脚本检查——墙段长度 > 0、闭合外墙环面积为正、门窗在墙段范围内且不重叠、房间多边形不自交、面积合计 vs 房源面积。
2. **几何层（建模后）**：比例检查（门宽）、BVH 穿插、向下射线找悬空、洞口射线、法线方向（墙面法线朝外）。
3. **视觉层**：俯视正交渲染/视口截图与原平面图叠图（差异肉眼可见）；再按 bonsai-project-setup 的 6 个角度看一遍；从窗外往里看室内。
4. **报告**：列出"量出来的 / 猜的"尺寸和误差，交给用户确认。

---

## 6. 给技能的其他提醒（推论）
- 工作流：读图 → 定比例（报告误差）→ 填 JSON（让用户确认关键尺寸）→ 校验 JSON → 建模（bpy 或 Bonsai）→ 验证 → 材质/灯光（archviz）→ 家具（set-dressing + free-3d-assets）。"30 分钟做出公寓"的视频本质是这个流程，难点在第 2–3 步的尺寸准确。
- 每次 `execute_blender_code` 前提醒存档（blender-mcp README 的警告）。
- 代码按 "幂等" 写：先删掉同名集合 `FP_*` 再重建，避免重复对象盖住门窗（bonsai-walls 记过 orphan wall 的坑）。
- 所有对象放进集合：`FP_Reference`、`FP_Walls`、`FP_Cutters`、`FP_Floors`、`FP_Ceilings`、`FP_Openings`、`FP_Furniture`。
- 多层楼：每层一个 level，楼梯开洞（Bonsai 有现成 `add_stairwell_opening_for_stair`）。

## 7. 未能核对 / 待查
- IRC 条文原文（ICC 网站 403）。
- ANSI Z765-2021 原文（付费标准，只有二手摘要）。
- 马来西亚 UBBL 层高、门宽数值。
- Zillow 使用条款（403）。
- `import_as_mesh_planes` 的 `align_axis` 枚举名、在 MCP timer 上下文能否直接调用。
- Archimesh / Archipack 在 Blender 5.2 能否运行。
- Structured3D 数据集本身的授权（代码 MIT）。
