# C — archviz-cinematic 研究笔记（Blender 5.x，免费工具）

研究日期：2026-10-22。当前 Blender 手册 `docs.blender.org/manual/en/latest/` = **Blender 5.2 LTS**（2026-07-14 发布，支持到 2028-07；5.3 已进 beta）。
来源：https://developer.blender.org/docs/release_notes/5.2/

标记规则：每条事实后附来源 URL。**未验证** = 只有社区/二手来源、经验值，或我没有在官方文档里读到原文。bpy 代码片段均**未在 Blender 里实际跑过**（未验证），写技能时要先在 5.2 里跑一次。

---

## 0. 和现有技能的分工（避免重复）

已读：
- `archviz/SKILL.md`（71 行）+ `references/archviz-camera.md`、`archviz-lighting.md`（各 5 行）：只有提纲 —— "24–35mm 室内"、"外景用 shift 校正竖线"、"眼高 ~1.5–1.7m"、"HDRI + 窗户 portal + 实用灯"、"玻璃 IOR 合理"、"保留分层 EXR"。没有具体参数、没有运镜、没有渲染/编码流程、没有 bpy。
- `lighting-design/SKILL.md`：游戏引擎实时/烘焙光照（lightmap、probe、Lumen、阴影级联）—— 不是 Cycles 离线渲染，基本不重叠。
- `camera-systems/SKILL.md`：游戏玩家相机（跟随、deadzone、轨道碰撞、Cinemachine）—— 不涉及电影运镜和建筑透视。

**建议 archviz-cinematic 只放现有技能没有的东西**：具体运镜配方和时长/速度、两点透视的 shift 计算、Blender 5.x 的天空/曝光/AgX 参数、渲染预算、动画去噪闪烁、图片序列 → ffmpeg 编码、玻璃/窗帘/植物的具体做法。基础规则（真实比例、竖线、24–35mm）引用 `archviz` 即可，不再重写。

---

## 1. 相机（静帧 + 运镜）

### 1.1 Blender 相机属性（官方）
来源：https://docs.blender.org/manual/en/latest/render/cameras.html
- **Shift X/Y**：调整消失点。手册对比图：用 lens shift 时水平线保持水平，旋转相机则会歪斜。"Using lens shift is equivalent to rendering an image with a larger FOV and cropping it off-center." → 这就是建筑摄影的移轴（两点透视）做法。
- **Focal Length / Lens Unit**（mm 或 FOV）；提示："While the camera is moving towards an object the Focal Length property can be decreased to produce a Dolly Zoom"。
- **Depth of Field**：Focus Object（链接后 Distance 失效）、Focus Distance、**F-Stop**（越小虚化越强）、Blades（≥3 才出多边形光斑）、Rotation、Ratio（<1 横向、>1 纵向，模拟变形宽银幕光斑）。
- **Sensor Fit** Auto/Horizontal/Vertical；`sensor_width` 默认 36 mm（全画幅）。API：https://docs.blender.org/api/current/bpy.types.Camera.html
- **Composition Guides**：Thirds、Center、Diagonal、Golden Ratio、Golden Triangle A/B、Harmony Triangle A/B —— 可在相机视图里打开辅助构图。
- **Safe Areas**：默认 EBU 标准，有 4:3 center-cut。
- Passepartout 完全不透明时 Blender 会优化相机外区域的渲染。

### 1.2 建筑相机规则（行业经验）
- **两点透视**：相机保持水平（Rotation X = 90°、Y = 0），用 **Shift Y** 上下取景，不要倾斜相机，否则竖线汇聚（三点透视，楼像往后倒）。来源：Maxwell Render 文档 Shift Lens https://nextlimitsupport.atlassian.net/wiki/spaces/maxwell4/pages/5679360/Shift+Lens ；Blender 手册同上。
- 几乎所有外景都用两点透视；室内只有明显仰视/俯视时才需要。偏轴太多时画面边角会被拉伸，所以配"中等广角 + 合适相机高度"。来源（二手教学站，**未验证**权威性）：https://www.studiomatrx.org/students/architectural-visualization-rendering/camera-fundamentals-focal-length
- **焦距**（全画幅等效，同上来源，经验值）：广角 16–28 mm、标准 35–50 mm、长焦 ≥85 mm；**室内 24–35 mm**，更广只用于刻意的英雄镜头；外景四周开阔时可以更广。细节特写用 50–85 mm 压缩空间（经验值，**未验证**）。
- **眼高**：约 1.5–1.6 m（同上来源）。现有 archviz 技能写 1.5–1.7 m，一致。室内低机位 1.0–1.2 m 让天花板显高、家具显大是常见做法（**未验证**，经验值）。
- **Shift 的近似计算**（**未验证**，由几何推导）：shift 单位是"传感器较长边的比例"。想让画面中心看向相机上方高度差 Δh、距离 d 的点：`shift_y ≈ (Δh / d) × (focal_length / sensor_width)`（横构图、Sensor Fit=Auto/Horizontal 时）。写技能时用 bpy 实测确认。
- 构图：三分法、引导线、对称、框中框、黄金比例（Digital Architect，定性）：https://thedigitalarchitect.beehiiv.com/p/6-key-techniques-creating-cinematic-architectural-animations

### 1.3 经典运镜与时长/速度
来源汇总（多为经验值）：
- 越慢越电影化；最常见错误是相机太快；修法通常是"更少、缓动更好的关键帧"。10 秒的移动用 3–4 个关键帧；30 秒的揭示用 4–5 个姿态；"Four great keyframes beat forty scribbled ones"。如果觉得快，速度减半、片段拉长。镜头先做 10 s，再拉到 12–15 s，揭示结尾加一个短停留。滚转锁 0。转向要慢，最好边前进边转。来源：https://www.studiomatrx.org/students/architectural-visualization-rendering/camera-paths-and-walkthroughs （**二手**）
- 步行速度参考：散步约 3 ft/s（≈0.9 m/s）到快走约 6 ft/s（≈1.8 m/s）；按平面图距离反推秒数。来源：2001 年 AEC 论文（较旧）https://www.graphicon.ru/html/2001/pdf/AEC-Russia-Ross2.pdf （通过搜索摘要获得，PDF 未全文阅读，**未验证**）。建议做室内推进时 ≤0.5 m/s 更"电影"（**未验证**，经验值）。
- 漫游结构：外景建立镜头 → 绕楼（全圈或半圈）→ 走向入口制造"要进去"的预期 → 用转场进入室内，不要硬切；不要做真实摄影机做不到的运动；在相机视图里判断，不要在顶视图里判断。来源：SIGGRAPH HyperGraph https://education.siggraph.org/static/HyperGraph/animation/cameras/camera_suggestions.htm
- 一般避免手持晃动，除非故事需要；起点用轻微摇镜（pan）。来源：Digital Architect（同上）。
- **常用运镜配方**（名称与做法为行业通用术语；数值是建议起点，**未验证**）：
  | 运镜 | 做法 | 建议起点 |
  |---|---|---|
  | Dolly / push-in 推进 | 相机沿视线直线前进，看向固定目标 | 6–10 s，移动 1–3 m，ease in-out |
  | Slider 横移 | 相机平行于立面横移，朝向不变，前景物（植物、柱子）制造视差 | 6–8 s，1–2 m |
  | Crane / pedestal 升降 | 竖直升起越过前景（围墙、灌木）揭示建筑 | 8–12 s，升 2–6 m |
  | Orbit 环绕 | 相机挂在中心空物体上，旋转空物体 Z，Track To 目标 | 10–20 s 转 20–45°；外景用较长焦距 35–50 mm |
  | Reveal through door 穿门揭示 | 从门框/墙后起步，门框作为前景遮挡后推进 | 6–10 s，门框占画面边缘 |
  | Drone / aerial 航拍 | 高处缓慢前推或环绕，Saint-Tropez 类别墅加海景 | 10–15 s；高度 20–60 m |
  | Pan / tilt 摇 | 相机不动只转向 | 每秒转角小；24 fps 下慢摇，避免抖（judder） |
- 24 fps 下摇镜要更慢以免顿挫；论坛有"一点横穿画面约 7 秒"的说法，**仅单人经验，未验证**：https://www.dvxuser.com/goto/post?id=5700121

### 1.4 景深（DoF）用法
- 室内推进用 f/2.8–f/5.6 做轻微虚化，外景大全景通常关 DoF 或 f/8+（**未验证**，经验值；真实相机 f 值换算由 Blender 物理处理）。
- Focus Object 指向一个空物体，动画对焦（rack focus）只需动画空物体位置。手册：Focus Object 会让 Distance 失效（上面 cameras.html）。
- Depth 通道在有 DoF/运动模糊时会有噪点，合成假景深用 **Mist pass** 更干净。来源：https://docs.blender.org/manual/en/latest/render/layers/passes.html

### 1.5 bpy 动画方法
- **关键帧插值与缓动**（官方）：Interpolation = Constant / Linear / Bézier（默认，"smooth in both values and speed"）；Easing 类（Sine/Quad/Cubic/Quart/Quint/Expo/Circ）+ Ease In / Ease Out / Ease In Out；Dynamic Effects（Back/Bounce/Elastic，建筑镜头不要用）。Handle 类型：Automatic、**Auto Clamped**（防止过冲，推荐默认）、Vector、Aligned、Free。Handle Smoothing "Continuous Acceleration" 让少量关键帧的曲线更顺，适合"少量关键帧的 limited animation"。来源：https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/properties.html
- API：`Keyframe.interpolation`、`Keyframe.easing`（'AUTO'/'EASE_IN'/'EASE_OUT'/'EASE_IN_OUT'）。https://docs.blender.org/api/current/bpy.types.Keyframe.html
- **F-Curve 修改器**可加噪声（模拟轻微手持感）等：https://docs.blender.org/manual/en/latest/editors/graph_editor/fcurves/modifiers.html
- **Follow Path 约束**："cameras on rails"；Fixed Position 打开后用 **Offset Factor（0–1）** 定位，动画这个值就能用 F-Curve 控制缓动（比 Evaluation Time 更好控制）；可配合 Track To 让移动相机始终看向目标；Forward/Up 轴不能相同；要完美贴合路径先 Alt-G/Alt-R 清零。来源：https://docs.blender.org/manual/en/latest/animation/constraints/relationship/follow_path.html
- **Blender 5.0 Python API 变化（重要）**：旧的 `action.fcurves` / `action.groups` / `action.id_root` **已移除**；F-Curve 在 channelbag 里，用 `bpy_extras.anim_utils.action_get_channelbag_for_slot(action, slot)` 读、`action_ensure_channelbag_for_slot()` 建；EEVEE 引擎 ID 改回 `BLENDER_EEVEE`（不是 `BLENDER_EEVEE_NEXT`）；`scene.node_tree` 移除，用 `scene.compositing_node_group`；`ImageFormatSettings.media_type` 必须先设再设 `file_format`。来源：https://developer.blender.org/docs/release_notes/5.0/python_api/

```python
# 未验证：Blender 5.2 推进镜头示例（关键帧 + 缓动）
import bpy
from bpy_extras import anim_utils
cam = bpy.data.objects["Camera"]
scn = bpy.context.scene
scn.render.fps = 24
cam.location = (0, -8, 1.55); cam.keyframe_insert("location", frame=1)
cam.location = (0, -5, 1.55); cam.keyframe_insert("location", frame=240)  # 10 s
act = cam.animation_data.action
cb = anim_utils.action_get_channelbag_for_slot(act, cam.animation_data.action_slot)
for fc in cb.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'SINE'      # 或 'BEZIER' + Auto Clamped handles
        kp.easing = 'EASE_IN_OUT'
cam.data.lens = 28
cam.data.shift_y = 0.05              # 两点透视：相机保持水平，用 shift 取景
cam.data.dof.use_dof = True
cam.data.dof.aperture_fstop = 4.0
```

---

## 2. 光照

### 2.1 天空（Blender 5.x 已改名）
来源：https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/sky.html ；API https://docs.blender.org/api/current/bpy.types.ShaderNodeTexSky.html
- 5.0 起 Sky Type：
  - **Single Scattering** = 原 Nishita（4.5 手册还叫 "Nishita"），"legacy and may be removed"。
  - **Multiple Scattering**（新，基于 Fernando García Liñán）—— "most accurate model"。**archviz 用这个。**
  - Preetham、Hosek/Wilkie：legacy，将移除。
  - 对比：4.5 手册 https://docs.blender.org/manual/en/4.5/render/shader_nodes/textures/sky.html 只有 Nishita；5.0 手册 https://docs.blender.org/manual/en/5.0/render/shader_nodes/textures/sky.html 出现 Multiple Scattering → 5.0 新增（版本归属由手册对比得出）。
- bpy enum：`'SINGLE_SCATTERING' | 'MULTIPLE_SCATTERING' | 'PREETHAM' | 'HOSEK_WILKIE'`。旧脚本里的 `'NISHITA'` 在 5.x 不能用。
- 参数：Sun Disc（**Cycles only**）、Sun Size、Sun Intensity、**Sun Elevation**（离地平线角度）、**Sun Rotation**（绕天顶）、**Altitude**（海滩 = 0）、**Air**（1≈城市空气）、**Aerosols**（原 Dust；1≈城市气溶胶）、**Ozone**（让天更蓝）。
- 手册注："Single and Multiple Scattering skies are very bright by default (hence accurate)" → 降 Color Management 的 **Exposure**。
- **真实地点和时间**：官方扩展 **Sun Position**（GPL，免费，Blender 4.2+，v4.4.0）根据经纬度/日期/时间驱动太阳灯 + 天空纹理，可同步 HDRI 旋转。Saint-Tropez 别墅可直接输入当地坐标。来源：https://extensions.blender.org/add-ons/sun-position/

### 2.2 黄金时刻 / 蓝调时刻
- 黄金时刻 ≈ 太阳高度 −4° 到 +6°；蓝调时刻 ≈ −6° 到 −4°（无官方天文定义，摄影惯例）。来源：https://sunrisesunset.io/golden-hour-blue-hour/ ；https://www.home-assistant.io/conditions/sun.is_golden_hour/
- 在 Sky 节点里：Sun Elevation 2°–6° 做黄金时刻暖光，长阴影；蓝调时刻太阳在地平线下，天光为主 + 室内灯/发光窗户（**未验证**：Multiple Scattering 在负高度时的表现需实测）。
- 白平衡：Color Management 有 **White Balance**（Temperature/Tint，默认 D65），可整体调暖/冷。来源：https://docs.blender.org/manual/en/latest/render/color_management/displays_views.html

### 2.3 灯光强度（官方参考表）
来源：https://docs.blender.org/manual/en/latest/render/lights/light_object.html
- 太阳灯 Strength（W/m²）：晴天 1000、多云 500、阴天 200、月光 0.001。
- 点/聚/面光（W，辐射功率，不是电功率）：蜡烛 0.05 W；800 lm LED 灯泡 2.1 W；1000 lm 灯泡 2.9 W；1500 lm PAR38 泛光 4 W（Area Disk）；2500 lm 荧光灯管 4.5 W（Area Rectangle）；5000 lm 车灯 22 W（Spot 125°）。
- 这些值会比肉眼感觉的亮/暗，因为渲染器不会自动适应 → 用 Exposure 补偿。灯的 **Temperature**（黑体 K）、**Exposure**（×2^exposure）、**Normalize**（改尺寸时总功率不变）、Point/Spot **Radius** 与 **Soft Falloff**。
- 面光 **Spread**（模拟格栅柔光箱）；**Multiple Importance Sample**；**Cast Shadow**。来源：https://docs.blender.org/manual/en/latest/render/cycles/light_settings.html

### 2.4 Light Portals（Cycles，5.2 仍存在）
来源：https://docs.blender.org/manual/en/latest/render/cycles/light_settings.html ；https://docs.blender.org/manual/en/latest/render/cycles/optimizations/reducing_noise.html
- 面光勾选 **Portal**，放在窗户、门洞等光进入室内的位置，形状匹配开口；"significantly reduce noise in interior scenes"；"rendering with portals is usually slower, but as it converges more quickly, less samples are required"；**外景无用**。
- 5.0 新增 **Portal Depth** 光通道：https://developer.blender.org/docs/release_notes/5.0/cycles/
- 替代/补充：**Path Guiding**（**仅 CPU**），"when a room is lit through a small door opening"，Training Samples 128–256 通常足够。来源：https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html
- **Light Tree**：更有效采样多盏灯（室内很多筒灯时有用），但不考虑自定义衰减、纹理灯等（同上）。

### 2.5 HDRI
- World ▸ Settings ▸ Sampling = Auto/Manual 开启 MIS，HDRI 里有小而亮的太阳时必须开；Map Resolution 越高越准。技巧：Mix 节点 + Light Path "Is Camera Ray"，背景看高清 HDRI、照明用低清（或反之）。来源：https://docs.blender.org/manual/en/latest/render/cycles/world_settings.html
- 5.2：World 新增 **Cast Shadows** 选项。来源：https://developer.blender.org/docs/release_notes/5.2/cycles/
- 免费 HDRI：**Poly Haven**（CC0，可商用，不需署名）https://polyhaven.com/license

### 2.6 室内外曝光平衡
- 把亮度控制在 **Color Management ▸ Exposure**（作用在视图变换前，单位 stop）或 **Film ▸ Exposure**（作用在数据上，Cycles）。来源：https://docs.blender.org/manual/en/latest/render/color_management/displays_views.html ；https://docs.blender.org/manual/en/latest/render/cycles/render_settings/film.html
- 用 **False Color** 视图检查曝光（蓝=暗、灰 16–22% 为中灰、红/白=过曝），同上 displays_views 页。
- 合成里用 Exposure 节点 + 遮罩单独提亮窗户区（手册示例正是"increase the brightness of the window area using a mask"）：https://docs.blender.org/manual/en/latest/compositing/types/color/adjust/exposure.html
- **Light Groups**（Cycles only）：每组灯一个 pass，合成里调颜色/强度不用重渲；太阳、天空(World)、室内灯分组，便于事后平衡室内外。来源：https://docs.blender.org/manual/en/latest/render/layers/passes.html

### 2.7 IES 和人工照明
- IES Texture 节点（Internal/External），输出 Factor 接 Emission Strength。来源：https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/ies.html
- **只在 Cycles 有效**：灯的节点树（含 IES）"Shader-based light definitions are only supported in Cycles. EEVEE ... ignores light shader node trees"。来源：https://docs.blender.org/manual/en/latest/render/cycles/light_settings.html ；EEVEE 限制页 "Lights ... do not support light node trees" https://docs.blender.org/manual/en/latest/render/eevee/limitations/limitations.html
- 免费 IES：ieslibrary.com（2020 年报道 9 万+ 免费文件，可商用 —— 现状**未验证**）https://www.cgchannel.com/2020/06/download-over-90000-free-ies-lighting-files-from-ies-library/
- 噪点：Light Falloff 节点 Smooth 减少近距离热点；只钳制间接光（Clamp Indirect）保留直接高光。来源：reducing_noise.html（同上）

### 2.8 夜景发光窗户
- 简单做法：窗户后面放发光面（Emission）或真实室内 + 灯。发光网格在材质设置里控制 MIS：很亮、作为光源 → 开；只是微微发光 → 关能减噪。来源：reducing_noise.html
- 现有 LESSONS 规定"玻璃后面要有真实室内"（用户之前对 MLO 的要求）—— archviz-cinematic 写夜景时应沿用：真室内 + 部分房间开灯，不要用印上去的假室内贴图。

---

## 3. 渲染设置

### 3.1 Cycles vs EEVEE
- EEVEE "is based on rasterization and is not a path tracer ... Cycles will always provide more physically accurate renders"。来源：https://docs.blender.org/manual/en/latest/render/eevee/index.html
- EEVEE 限制：灯没有节点树（无 IES）、面光 Spread 不支持；薄墙会漏光；光探针捕捉不支持镜面；屏幕空间效果到屏幕边缘消失（可用 overscan）；只正确模拟一次折射；体积不出现在反射/折射里。来源：https://docs.blender.org/manual/en/latest/render/eevee/limitations/limitations.html
- EEVEE 光追：`use_raytracing` **默认关**，要手动开；Method = Light Probe / Screen-Trace；有 Fast GI（AO 或 GI）。来源：https://docs.blender.org/manual/en/latest/render/eevee/render_settings/raytracing.html ；API https://docs.blender.org/api/current/bpy.types.SceneEEVEE.html （taa_render_samples 默认 64）
- 5.2 EEVEE：屏幕空间光追重做，能量守恒修正后"some scenes might render darker than in 5.1"；新 Backface 选项减少漏光；Far Thickness 移除；灯可对相机隐藏；阴影池 1.5/2 GB。来源：https://developer.blender.org/docs/release_notes/5.2/eevee/
- **建议**（**未验证**，经验）：EEVEE 用于预演（animatic）、运镜/节奏确认；最终片用 Cycles。室内（反弹光多、玻璃多）尤其用 Cycles。

### 3.2 Cycles 采样与去噪（官方）
来源：https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html
- **Noise Threshold**（自适应采样）：典型 0.1–0.001，越低越好越慢；0 = 根据样本数自动；Min Samples 0 = 自动。Time Limit 可限每帧时间（不含预处理）。
- **Denoiser**：Automatic（优先 OIDN）/ **OpenImageDenoise**（"Typically provides the highest quality"）/ OptiX（仅 NVIDIA）。Passes：至少 **Albedo**，推荐 **Albedo + Normal**。Prefilter：None / Fast / **Accurate**。Quality：High / Balanced / Fast。Use GPU。
- **Use Animated Seed**："a good idea to enable this when rendering animations because a varying noise pattern is less noticeable"。
- Scrambling Distance 在视口会造成闪烁；与 Blue-Noise 不兼容。
- **Sample Subset** + `bpy.ops.cycles.merge_images` 可多台机器分样本渲同一帧。
- 5.2：AMD RDNA2 上 OIDN 不再 GPU 加速。来源：https://developer.blender.org/docs/release_notes/5.2/cycles/

### 3.3 动画去噪闪烁（重点）
- OIDN 是逐帧去噪，没有时间稳定性；低样本时帧间闪（"boiling"）。社区：提高样本能减轻，室内可能要上千样本；关 Animated Seed 能提高稳定性但会产生帧间固定纹样。来源（社区）：https://blenderartists.org/t/flickering-noise-on-cycles-animation/1383040 ；https://devtalk.blender.org/t/taking-a-look-at-optix-7-3-temporal-denoising-for-cycles/18656?page=6 （**未验证**）
- **官方时间稳定去噪只有 OptiX**：`bpy.ops.cycles.denoise_animation(input_filepath='', output_filepath='')` 仍在 5.x API；要求 Denoising Data pass、输出 OpenEXR MultiLayer、整段渲完；不在 UI 里，只能 Python 调用。源码里 temporal 模式只在 `denoiser_optix.cpp` 出现（`OPTIX_DENOISER_MODEL_KIND_TEMPORAL`，需要 motion pass），`denoiser_oidn.cpp` 没有 → **非 NVIDIA 卡没有官方时间去噪**。来源：https://docs.blender.org/api/current/bpy.ops.cycles.html ；https://projects.blender.org/blender/blender/src/branch/main/intern/cycles/blender/addon/operators.py ；https://projects.blender.org/blender/blender/src/branch/main/intern/cycles/integrator/denoiser_optix.cpp ；BlenderNation（3.1 时加入，需 Vector + Denoising Data pass）https://www.blendernation.com/2022/01/10/optix-temporal-denoising-support-added-to-blender-3-1-alpha/
- 第三方合成节点组（Temporal Denoising Toolkit）作者称 5.0.x 合成器 bug 会让它失效、5.1 正常，且动画焦距时 motion vector 不正确 —— **未验证**，不推荐依赖。https://markstead.gumroad.com/l/TemporalDenoisingToolkit
- **实用防闪清单**（官方依据 + 经验）：
  1. 提高样本 / 降低 Noise Threshold（0.01 → 0.005）。
  2. 室内加 Light Portals 或 Path Guiding（CPU）让收敛更快。
  3. 去噪 Passes = Albedo + Normal，Prefilter = Accurate，Quality = High。
  4. Clamp Indirect（如 4–10）、Filter Glossy ≈ 1.0、关反射/折射焦散 → 减少萤火虫（萤火虫是动画闪烁的主要来源）。来源：https://docs.blender.org/manual/en/latest/render/cycles/render_settings/light_paths.html
  5. 输出 EXR（含 Denoising Data），保留事后用合成 Denoise 节点或 OptiX 时间去噪重做的余地。
  6. 先渲 3–5 秒测试片段看闪烁，再渲全片。

### 3.4 Light Paths（官方）
来源：https://docs.blender.org/manual/en/latest/render/cycles/render_settings/light_paths.html
- Max Bounces：Total / Diffuse / Glossy / Transmission / Volume / Transparent。玻璃需要最多 transmission 反弹；漫反射可以少。手册建议"Limited Global Illumination"预设加速。
- Clamping：Direct / Indirect（建议主要钳制间接光）。Filter Glossy 1.0 起步。Caustics Reflective/Refractive 可关。
- Fast GI Approximation（Replace/Add，AO Factor/Distance）：减少室内噪点但降质，可用于预演。
- 材质颜色避免接近 1.0 的值，最大 ~0.8，靠灯更亮来补 —— 减少噪点。来源：reducing_noise.html

### 3.5 色彩管理：AgX 与 Looks
来源：https://docs.blender.org/manual/en/latest/render/color_management/displays_views.html ；OCIO 配置 https://projects.blender.org/blender/blender/src/branch/main/release/datafiles/colormanagement/config.ocio
- Views（5.2）：Standard、ACES 1.3、**ACES 2.0**、Khronos PBR Neutral、**AgX**、Filmic（"deprecated and is superseded by AgX"）、Filmic Log、False Color、Raw；另有 AgX/ACES 的 HDR nits 版本。
- AgX：16.5 stops 动态范围，高曝光颜色向白去饱和，像胶片。4.0 起为新文件默认。来源：https://developer.blender.org/docs/release_notes/4.0/color_management/
- **AgX Looks 准确名称**（从官方 config.ocio 读出）：`AgX - Punchy`（"A darkening punchy look"）、`AgX - Greyscale`、`AgX - Very High Contrast`、`AgX - High Contrast`、`AgX - Medium High Contrast`、`AgX - Base Contrast`、`AgX - Medium Low Contrast`、`AgX - Low Contrast`、`AgX - Very Low Contrast`。bpy：`scene.view_settings.view_transform = 'AgX'`; `scene.view_settings.look = 'AgX - Medium High Contrast'`（字符串是否需要前缀在 5.2 里**未实测**）。
- 建议（**未验证**，经验）：archviz 用 AgX + Base 或 Medium High Contrast；产品/材质色准要求高用 Khronos PBR Neutral（手册说它面向"product photography"、曝光良好的场景）。
- Exposure（stop）在视图变换前；Gamma 在后；Curves；White Balance。
- HDR 视频：显示设 Rec.2100 PQ/HLG + H.265/AV1 + 10/12 bit；"Bit depth 10 with PQ encoding is a good default"。

### 3.6 运动模糊
来源：https://docs.blender.org/manual/en/latest/render/cycles/render_settings/motion_blur.html ；API https://docs.blender.org/api/current/bpy.types.RenderSettings.html
- `use_motion_blur` 默认关；`motion_blur_shutter` 默认 **0.5 帧** = 180° 快门（24 fps 时等效 1/48 s）。180° 快门规则来源：https://www.studiobinder.com/blog/what-is-the-180-degree-shutter-rule/
- 限制：不考虑灯光的世界坐标运动（相机和灯一起动会错误模糊）；正交相机没有相机运动模糊。慢速建筑运镜开 0.5 能去掉"CG 太锐"的感觉（**未验证**，经验）。

### 3.7 合成（Blender 5.0 起大改）
来源：https://developer.blender.org/docs/release_notes/5.0/compositor/
- 合成树是独立 data-block（可跨文件复用）；**Composite 节点移除**，用 Group Output；Use Nodes 移除；File Output 节点重做（Directory + File Name）；Glare 新增 Sun Beams 模式/Kernel，Low/Medium 质量帧间稳定，Fog Glow 更真实；Lens Distortion 保留 alpha。
- Glare 类型：Bloom、Ghosts、Streaks、Fog Glow、Simple Star、Sun Beams、Kernel；参数 Threshold、Smoothness、Clamp Maximum、Strength、Saturation、Tint、Size。Sun Beams 示例建议只用最亮区域做光源再用 Add 混回。来源：https://docs.blender.org/manual/en/latest/compositing/types/filter/glare.html
- Lens Distortion：Radial（桶形/枕形）、Horizontal；Dispersion（色差）；Fit。来源：https://docs.blender.org/manual/en/latest/compositing/types/transform/lens_distortion.html
- 暗角：合成里无专用节点 —— 用 Ellipse Mask + Blur + Mix(Multiply)（常见做法，**未验证**于 5.2 节点名）。
- 合成去噪：Denoise 节点（OIDN），输入 Noisy Image + Denoising Albedo + Denoising Normal（开 Denoising Data pass）。来源：https://docs.blender.org/manual/en/latest/compositing/types/filter/denoise.html
- 其他有用 pass：Mist（0–1 深度，做大气透视/雾）、Vector（Vector Blur 做后期运动模糊）、Cryptomatte（Object/Material/Asset 遮罩）、Shadow Catcher、Light Groups。来源：passes.html
- 5.0 新 pass：**Render Time pass**（逐像素渲染时间，用于找慢区域）。来源：https://developer.blender.org/docs/release_notes/5.0/cycles/
- bpy：`tree = bpy.data.node_groups.new("Comp", "CompositorNodeTree"); scene.compositing_node_group = tree`（5.0 Python API 页）。

### 3.8 输出：先图片序列，再 ffmpeg
- 手册明确："It's not recommended to render directly to a video format in the first instance" —— 中途出错视频可能不可播、要从头重渲；先渲 PNG 或 OpenEXR 序列，再编码，编码只要几秒到几分钟。也不要对有损文件做后期。来源：https://docs.blender.org/manual/en/latest/render/output/properties/output.html
- 帧号自动补 4 位（image0001.png），`#` 自定义位数；**Overwrite 关 + Placeholders 开** = 简易多机渲染农场 / 断点续渲。（同上）
- 5.0：`media_type`（'IMAGE' / 'MULTI_LAYER_IMAGE' / 'VIDEO'）要先设。多层 EXR 默认 multi-part。来源：https://docs.blender.org/api/current/bpy.types.ImageFormatSettings.html ；https://developer.blender.org/docs/release_notes/5.0/pipeline_io/
- 5.2：EXR 半精度（FP16）写入更快；可以关闭渲染输出保存。来源：https://developer.blender.org/docs/release_notes/5.2/pipeline_io/ ；/5.2/rendering/
- Blender 内置编码（FFmpegSettings）：容器默认 MKV；`constant_rate_factor` 预设 LOSSLESS/PERC_LOSSLESS/HIGH/MEDIUM(默认)/LOW/…/CUSTOM；`ffmpeg_preset` BEST/GOOD/REALTIME；ProRes 422 Proxy/LT/422/HQ/4444/4444 XQ；色深 10 bit 支持 H.264/H.265/AV1，12 bit 支持 H.265/AV1；CRF 范围 H.264/H.265/AV1 0–51。来源：https://docs.blender.org/api/current/bpy.types.FFmpegSettings.html ；output.html
- **外部 ffmpeg（官方 wiki）**：
  - x264 CRF 0–51，默认 23，合理 17–28，**17–18 ≈ 视觉无损**；+6 ≈ 码率减半；用你能忍受的最慢 preset；`-tune animation`/`film`/`grain` 可选。来源：https://trac.ffmpeg.org/wiki/Encode/H.264
  - x265 默认 CRF 28 ≈ x264 CRF 23 画质、约一半大小；Apple 兼容加 `-tag:v hvc1`。来源：https://trac.ffmpeg.org/wiki/Encode/H.265
  - 示例（**未验证**参数组合，按 wiki 规则拼）：
    ```
    ffmpeg -framerate 24 -i frames/img_%04d.png -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart out_h264.mp4
    ffmpeg -framerate 24 -i frames/img_%04d.png -c:v libx265 -preset slow -crf 22 -pix_fmt yuv420p10le -tag:v hvc1 out_h265.mp4
    ffmpeg -framerate 24 -i frames/img_%04d.png -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le out_prores_hq.mov
    ```
    `-pix_fmt yuv420p` 为了播放器兼容、`+faststart` 便于网页播放 —— 这两点是 ffmpeg 社区通用做法，本次未从 wiki 原文读到（**未验证**）。ProRes `profile:v 3` = HQ（**未验证**）。
  - Windows 上 ffmpeg 是免费开源工具；用户要自己安装（装之前先问）。

### 3.9 渲染时间预算
- 总帧数 = 秒 × fps。例：30 s × 24 fps = 720 帧；每帧 2 min → 24 h；每帧 6 min → 72 h。（算术）
- 估算法（建议流程，**未验证**为行业标准）：在最终分辨率下渲 3 个代表帧（最亮、最暗/最复杂、玻璃最多）→ 取最大值 × 帧数 × 1.2 余量；超预算就：降分辨率 → 提高 Noise Threshold → 限制 Time Limit → 加 Portals → 减反弹 → 改 EEVEE 预演。
- 提速选项：**Persistent Data**（动画时保留渲染数据，默认关，耗内存）来源：https://docs.blender.org/manual/en/latest/render/cycles/render_settings/performance.html ；5.2 **Texture Cache**（大幅降内存和启动时间，渲染略慢）来源：https://developer.blender.org/docs/release_notes/5.2/cycles/ ；Simplify（Texture Limit/Resolution）。
- 先用 Format ▸ Percentage 50% 做测试渲染（同比例）。来源：https://docs.blender.org/manual/en/latest/render/output/properties/format.html

---

## 4. 材质真实感

### 4.1 PBR / Principled BSDF
来源：https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html
- 层：金属/漫反射/次表面/透射基础层 → 可选薄膜 → 镜面层 → 可选 coat → sheen；发光在 coat/sheen 之下。
- **5.2 新增 Thin Wall**（布尔输入）："the surface is considered a thin sheet"；手册列举用途 "papers, leaves, and window sheets"；薄墙模式下 SSS 半径等无效；EEVEE 中用 Thin Wall 时 Thickness 要设 0、Thickness Mode = Slab。来源：https://developer.blender.org/docs/release_notes/5.2/rendering/ （PR#157469）
- 5.0：Principled/Metallic 新增 thin-film 虹彩（镀膜玻璃可用）。来源：https://developer.blender.org/docs/release_notes/5.0/cycles/
- 颜色值别超过 ~0.8（减噪，见 3.4）。

### 4.2 建筑玻璃
- Glass BSDF 会因焦散产生噪点；建议直接看时用 Glass，间接（阴影）用 Transparent，用 Light Path 节点混合 → 正确颜色阴影、没有焦散。来源：https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/glass.html ；reducing_noise.html "Glass and Transparent Shadows"
- 窗玻璃两种做法：
  1. **薄（单面）**：5.2 用 Principled + Transmission 1 + **Thin Wall**（官方点名 "window sheets"）；旧版本用 Transparent + Glossy 混合近似（论坛做法，**未验证**）。
  2. **厚（实体）**：Solidify 给厚度（如 6–10 mm），IOR ≈1.5（常见浮法玻璃值，**未验证**来源），需要更多 Transmission 反弹。论坛对单面玻璃是否需要 Solidify 有分歧。来源：https://blenderartists.org/t/how-to-model-a-proper-window-glass/597072 ；https://blenderartists.org/t/window-glass-material-which-is-the-better/1468224 （**未验证**）
- Film ▸ Transparent Glass：把透射面渲成透明，用于合成。来源：film.html
- 绿色边缘调色（真实浮法玻璃边缘偏绿）—— **未找到可靠来源，未验证**。

### 4.3 倒角 / 边缘
- **Bevel 修改器**优先（快）；Bevel 着色节点（Cycles only，"may slow down renders by 20%"，建议用于烘焙或静帧）。来源：https://docs.blender.org/manual/en/latest/render/shader_nodes/input/bevel.html ；修改器 https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/bevel.html
- 边缘磨损：AO/Pointiness 驱动的遮罩（常见做法，**未验证**于 5.2 节点名）。

### 4.4 窗帘
- 半透明薄纱：Principled 加 Transmission/Subsurface + **Thin Wall**（5.2 示例有 "Thin Wall with transmission / subsurface"）；或 Translucent BSDF 混合（**未验证**）。布料形状可用 `cloth-sim` 技能（已存在）。

### 4.5 植物、家具、杂物（免费来源）
- **Poly Haven**：HDRI/纹理/模型 CC0，可商用，不需署名；禁止爬取（要用官方 API 条款）。https://polyhaven.com/license
- **ambientCG**：材质 CC0 1.0，可商用，不需署名。https://docs.ambientcg.com/license/
- 用户已有 `free-3d-assets` 技能（Poly Haven / Poly Pizza / Sketchfab，`blender` MCP 的 `search_assets`）和 `set-dressing` 技能 → archviz-cinematic 应引用它们，不要重写。Sketchfab 每个模型授权不同（要逐个看）。
- 植物动画：风吹叶子可让外景"活"起来（**未验证**，经验）；多实例用 Geometry Nodes / 集合实例降低内存。5.2 EEVEE 实例化 CPU 绑定场景最多快 2 倍。来源：https://developer.blender.org/docs/release_notes/5.2/eevee/

### 4.6 比例
- 现有 archviz 已有"真实比例"规则；补充：Unit Scale = 1、Length = Meters；门高 ~2.1 m、台面 ~0.9 m、椅座 ~0.45 m 这类尺寸检查（常见建筑尺寸，**未验证**，各国规范不同）。SketchUp 导入后先检查单位（SketchUp 常用英寸）——**未验证**，需看导入器。

---

## 5. 渲染后 AI 增强（只提一句）
- 可选：渲染后的帧做 AI 放大/插帧/风格化，由另一个技能负责（如 `image-enhancer`）。注意：对每帧单独 AI 处理容易产生帧间不一致（闪烁）（**未验证**，经验）；付费 AI 视频工具按用户规则不推荐。

---

## 6. 写技能时的建议结构（给主代理参考）
1. SKILL.md：适用场景（"SketchUp 粗模 → 电影感短片"、"别墅动画"）、和 `archviz`/`free-3d-assets`/`set-dressing`/`cloth-sim`/`lighting-design`/`camera-systems` 的分工、整体流程（导入检查 → 镜头脚本 → EEVEE 预演 → 灯光 → 材质 → Cycles 测试帧 → 预算 → 序列帧渲染 → 合成 → ffmpeg）。
2. references/camera-moves.md：运镜配方表 + bpy（5.x channelbag API）。
3. references/lighting-5x.md：Multiple Scattering 天空、Sun Position、曝光、portal、IES、黄金时刻。
4. references/render-delivery.md：采样/去噪/防闪、AgX looks、运动模糊、合成、输出与 ffmpeg、预算公式。
5. references/materials.md：Thin Wall 玻璃、窗帘、倒角、免费资产。
6. 可选脚本（本地只读或只写到指定文件夹）：渲染预算计算器；shot list → 关键帧生成器（要先问用户再在 Blender 里执行）。
