# B — archviz-web-walkthrough 资料笔记（2026-10-22）

目的：为新技能 `archviz-web-walkthrough` 准备资料——把 Blender 的建筑/室内做成浏览器里可自由走动的导览（类似 Klay / Kunkun Visual 的物业导览），可选家具替换面板。通用 three.js 的内容交给仓库里已有的 40 个 threejs-* 技能；本技能只写建筑可视化专用的流程。

标记说明：**[源码]** = 直接读了源码或标签里的文件；**[文档]** = 官方文档页面；**[二手]** = 第三方文章；**未验证** = 没找到一手来源，或者只是经验值。

---

## 0. 现有仓库技能（不要重复写这些内容）

位置：`C:/Users/USER/OneDrive/Desktop/T1-main/wt-archviz-3d-skills/.claude/skills/`（批次记录在 `docs/skill-batches/city-40-2026-10-18.md`）

- `threejs-assets`：通用的 GLTFLoader 解码器配置（Draco/Meshopt/KTX2）、加载状态、处理过时的异步结果、缓存和克隆、GPU 纹理内存预算。内容很短，不讲具体 CLI 命令。→ 本技能应在这里补上**建筑可视化专用的 glTF-Transform 参数**（特别是保留 uv1、extras 和节点名），通用部分只引用它。
- `threejs-camera-controls-and-rigs`：「一个通道只有一个写入者」的相机架构（面向 WebGPU）；框取分支里已经写了 "architecture → eye/section anchors, lens shift, constrained orbit/pan/walk"，还有交接、抖动、大坐标。→ 本技能只写**第一人称行走、碰撞、楼梯、传送**的具体做法，相机所有权规则引用它。
- `threejs-performance`：通用的性能分析流程、renderer.info 的局限、释放资源。不给具体数字。→ 本技能给**建筑导览的预算起点**（标明是经验值），测量方法引用它。
- 其他相关的：`threejs-lighting`、`threejs-materials`、`threejs-html`（标签/面板）、`threejs-interaction`（拾取）、`threejs-deployment`、`threejs-webgpu`、`threejs-compatibility-fallbacks`、`threejs-ambient-contact-shading`、`threejs-exposure-color-grading`。
- 第二组技能（linegel）面向 **Three.js r185 WebGPU/TSL**；第一组跟随项目安装的版本。

---

## 1. 当前版本（2026-10-22 核实）

| 项目 | 版本 | 来源 |
|---|---|---|
| three.js | r186（GitHub Releases 显示为 Latest，日期 24 Sep）；npm `three@0.186.1` | https://github.com/mrdoob/three.js/releases ；https://registry.npmjs.org/three/latest |
| Blender | 5.2.2 LTS（2026-09-15），5.3 预计 2026-11-10 | https://www.blender.org/download/ |
| Blender glTF 插件（main 分支） | bl_info version (5, 4, 6)（这是 main 开发版，不是 5.2 正式版） | https://raw.githubusercontent.com/blender/blender/main/scripts/addons_core/io_scene_gltf2/__init__.py **[源码]** |
| @gltf-transform/cli | 4.5.1（2026-09-28），MIT，Node >=20 | https://registry.npmjs.org/@gltf-transform/cli/latest |
| KTX-Software（glTF-Transform 的 etc1s/uastc 需要） | 最低 4.4.0，Apache-2.0 | glTF-Transform `packages/cli/src/transforms/toktx.ts`（`KTX_SOFTWARE_VERSION_MIN = '4.4.0'`）**[源码]**；https://github.com/KhronosGroup/KTX-Software/blob/main/LICENSE.md |
| gltfpack（另一种方案） | 1.3.0，MIT | https://registry.npmjs.org/gltfpack/latest |
| Spark（World Labs） | `@sparkjsdev/spark` 2.4.0，MIT，peer `three >=0.180.0` | https://registry.npmjs.org/@sparkjsdev/spark/latest ；https://github.com/sparkjsdev/spark |
| nipplejs（触屏摇杆） | 1.0.4，MIT（2026-05-26） | https://registry.npmjs.org/nipplejs |

---

## 2. Blender → glTF 导出设置（网页建筑可视化）

来源：Blender 5.2 LTS 手册 glTF 页 https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html **[文档]**（注意：旧网址 `/addons/import_export/` 和 `/files/import_export/` 现在都是 404）

### 2.1 导出选项（手册里的原名）
- **Format**：glTF Binary（.glb）单文件；或 glTF Separate（.gltf + .bin + 贴图），方便事后改 JSON 和贴图，也方便 CDN 分开缓存。手册说明 Separate 格式要把所有文件一起分享。
- **Include**：`Selected Objects`、`Visible Objects`、`Renderable Objects`、`Active Collection`（+ `Include Nested Collections`）、`Active Scene`、**`Custom Properties`**（导出为 glTF `extras`，可以用来标记房间名、传送点、可替换家具的插槽 id）、`Cameras`、`Punctual Lights`（KHR_lights_punctual）。
- **Transform**：**`Y Up`** —— "Export using glTF convention, +Y up"（保持开启）。
- **Data - Scene Graph**：`GPU Instances`（EXT_mesh_gpu_instancing，适合大量重复的椅子、灯具）、`Geometry Nodes Instances`（手册标为 experimental）、`Flatten Object Hierarchy`、`Full Collection Hierarchy`。
- **Data - Mesh**：**`Apply Modifiers`** —— "Export objects using the evaluated mesh"（建筑用了 Array/Mirror/Bevel/Solidify 修改器时一定要开）；`UVs`、`Normals`、`Tangents`、`Attributes`（下划线开头的属性）、`Loose Edges/Points`、`Shared Accessor`。
- **Data - Material**：`Materials` = Export / Placeholder / Viewport / No Export。**Images**：Automatic / JPEG / WebP / None；JPEG、WebP 有 `Image Quality`；`Create WebP`（额外生成一份 WebP）；`WebP fallback`（再生成一份 png 后备）。手册原话："JPEG might be preferable for web applications due to the smaller file size"；选 WebP 时 "all textures will be saved as WebP, without any png/jpg fallback"。
- **Data - Draco Compression**：Compression Level，Quantization（Position/Normal/Texture Coordinates/Color/Generic）。
- **Data - Meshopt Compression（5.2 新增）**：`Meshopt Extension` 可选 EXT_meshopt_compression 或 KHR_meshopt_compression。来源：5.2 发布说明 https://developer.blender.org/docs/release_notes/5.2/pipeline_io/ **[文档]**；源码默认值 `default='EXT_meshopt_compression'` **[源码]**。
- **Lighting Mode**：Standard（物理单位 cd/lx/nt）/ Unitless / Raw（Deprecated）。
- 手册写明："Blender's Area light type and World lighting are not supported by glTF, and will be ignored during export" → 建筑可视化里面光源和 HDRI 世界光不会导出，只能**烘焙**，或者在 three.js 里重新布光（光照部分引用 `threejs-lighting`）。
- glTF 材质只认 Principled BSDF 的那几个通道；程序化节点不会导出，要先烘成贴图（手册 Materials 章节）。metallic 放 B 通道，roughness 放 G 通道；ORM 贴图的 occlusion 放 R 通道。
- 导出 **Unlit**：手册写的是 "mix in a camera ray, and avoid using the Principled BSDF node" → 导出成 KHR_materials_unlit。适合「整张光照已烘进 baseColor」的做法。
- **KHR_materials_variants**：Blender 可以导入和导出。3D View 的 glTF Variants 页签里有 Assign to Variant / Assign as Original / Display Variant；**每个材质槽对应一个 glTF primitive**；要先在插件偏好设置里打开 UI（手册 "glTF Variants" 章节）。

### 2.2 多套 UV（光照贴图用的第二套 UV）
- **[源码]** `blender/exp/primitive_extract.py`（main 分支）：`if export_settings['gltf_texcoords'] ... self.tex_coord_max = len(self.blender_mesh.uv_layers)` → 开了 UVs 就导出**所有 UV 图层**，第 n 个图层对应 `TEXCOORD_n`（按图层在列表里的顺序）。5.2 正式版是否一样：未验证（只看了 main）。
- 手册提示："Not all glTF readers support multiple UV maps"。
- 社区经验（three.js 论坛）：拿 The_Lightmapper 加 three.js 时，UV 顺序弄错会导致贴图用错通道 https://discourse.threejs.org/t/why-is-uv-map-designed-in-blender-not-showing-up-correctly-in-gltf-glb-model-on-my-website/16988/3 **[二手]**。

### 2.3 在 Blender（Cycles）里烘焙光照
来源：https://docs.blender.org/manual/en/latest/render/cycles/baking.html **[文档]**
- 用途里写明 "Creating light maps to provide global illumination or speed up rendering in games"。
- 需要 UV 贴图，再加一个 Image Texture 节点作为目标（"Active Image Texture node … is used as the baking target"）；如果某个材质里没有选中的激活图片节点，"nothing will be baked for this material"。
- Bake Type：**Combined**（"all materials, textures, and lighting except specularity"，可以分别勾选 Direct/Indirect 和 Diffuse/Glossy/Transmission/Emit）、**Diffuse**（只勾 Direct+Indirect、不勾 Color → 得到纯光照的灰度或彩色光照贴图）、Ambient Occlusion、Shadow、Normal、Roughness、Emit 等。
- 烘焙沿用渲染设置（samples、bounces）。
- **Margin**：Extend / Adjacent Faces + Size(px)，作用是避免 UV 接缝在 mipmap 下出现缝。
- **Lightmap Pack**（UV ‣ Unwrap ‣ Lightmap Pack）：`Share Texture Space`（多个物体共用一张光照贴图且 UV 不重叠）、**`New UV Map`**（新建一套 UV，不覆盖第一套贴图 UV）、Pack Quality、Margin。来源：https://docs.blender.org/manual/en/latest/modeling/meshes/editing/uv.html **[文档]**。
- 烘焙时用的是哪一套 UV（active 还是 active render），手册这一页没写清楚 → **未验证**；按经验，烘焙前把光照贴图那套 UV 设成 active，或在 Image Texture 前接 UV Map 节点。
- 两种做法（取舍是经验总结，**未验证**为官方建议）：
  - A. **只烘光照（lightMap）**：第一套 UV 保留可平铺的材质贴图，第二套 UV 放光照贴图；three.js 里设 `material.lightMap`。好处：材质还能替换（适合家具或地板换色）。坏处：glTF 没有 lightMap 槽 → 要在代码里加载光照贴图并指定（见 §3）。
  - B. **Combined 烘进 baseColor + Unlit**：最省、在手机上最稳；但材质和光照绑死，换材质就要重新烘；镜面反射没有了（Combined 不含 specular）。
  - 可替换的家具通常**不要**烘进房间的光照贴图（换掉以后会留下影子）；家具单独烘 AO，或者实时加接触阴影（引用 `threejs-ambient-contact-shading`）。（经验，**未验证**）

---

## 3. three.js 里的 lightMap / aoMap（r186）

- `Texture.channel`（默认 0）决定这张贴图用哪一套 UV。**[源码]** `src/textures/Texture.js` r186。
- `WebGLPrograms.js`：`lightMapUv: HAS_LIGHTMAP && getChannel( material.lightMap.channel )`，`aoMapUv: ... material.aoMap.channel` **[源码]** → 第二套 UV 要设 `tex.channel = 1`。
- GLTFLoader 的属性对应：`TEXCOORD_0:'uv'`、`TEXCOORD_1:'uv1'`、`TEXCOORD_2:'uv2'`、`TEXCOORD_3:'uv3'` **[源码]**；glTF 贴图的 `texCoord > 0` 会自动设成 `texture.channel = mapDef.texCoord` **[源码]**（所以 occlusionTexture 指向 TEXCOORD_1 时 aoMap 会自动用 uv1）。
- 这个 channel 机制从 r151 开始（社区帖 "Using multiple UV maps per model (r150 and earlier)" https://discourse.threejs.org/t/using-multiple-uv-maps-per-model-r150-and-earlier/41973 **[二手]**）。
- MeshStandardMaterial r186 注释 **[源码]**：lightMap "represents pre-baked illuminance data, and the texture must be assigned a Texture#colorSpace. Most lightMap textures set `texture.colorSpace = LinearSRGBColorSpace` and use float-type formats such as .exr or .hdr"；`lightMapIntensity` 默认 1；aoMap 只用 R 通道，必须是 `NoColorSpace`。光照贴图在 shader 里加到 irradiance（`lightmap_pars_fragment` / `lights_fragment_maps`）**[源码]**。
  - 实务：光照贴图如果存成 8 位 PNG/JPG/KTX2，要自己定色彩空间和强度（sRGB 编码时设 SRGBColorSpace），会比 HDR 损失动态范围。**未验证**哪个最好，要实际对比截图。
- glTF 核心**没有 lightMap 槽**；GLTFLoader 支持的扩展列表里也没有 lightmap 扩展 **[源码]** → 做法：(1) 光照贴图单独发布（KTX2/EXR/PNG），按材质名或 `extras` 在加载后指定，设 `channel = 1`；(2) 或者整张烘进 baseColor（Unlit）。
- 示例：`webgpu_materials_lightmap`（three.js examples/files.json r186 有这个例子）。

### GLTFLoader r186 支持的扩展（源码注释）**[源码]**
内置：KHR_draco_mesh_compression、KHR_lights_punctual、KHR_materials_*（anisotropy, clearcoat, dispersion, emissive_strength, ior, specular, transmission, iridescence, unlit, volume）、KHR_mesh_quantization、**KHR_meshopt_compression**、KHR_texture_basisu、KHR_texture_transform、EXT_materials_bump、EXT_meshopt_compression、EXT_mesh_gpu_instancing、EXT_texture_avif、EXT_texture_webp。
要另外注册插件的：**KHR_gaussian_splatting**、**KHR_materials_variants**（指向 takahirox/three-gltf-extensions）、MSFT_texture_dds、KHR_animation_pointer、NEEDLE_progressive。
来源：https://raw.githubusercontent.com/mrdoob/three.js/r186/examples/jsm/loaders/GLTFLoader.js

---

## 4. glTF-Transform CLI

- 仓库：https://github.com/donmccurdy/glTF-Transform ，MIT（LICENSE.md）**[源码]**；文档：https://gltf-transform.dev/cli
- 安装：`npm install --global @gltf-transform/cli`（Node LTS；package engines `>=20`）；在线试用：https://gltf.report/
- README 里的命令 **[文档]**：
  ```bash
  gltf-transform optimize input.glb output.glb --texture-compress webp
  gltf-transform draco input.glb output.glb --method edgebreaker
  gltf-transform meshopt input.glb output.glb --level medium
  gltf-transform resize input.glb output.glb --width 1024 --height 1024
  gltf-transform webp input.glb output.glb --slots "baseColor"
  gltf-transform uastc input.glb output1.glb \
      --slots "{normalTexture,occlusionTexture,metallicRoughnessTexture}" \
      --level 4 --rdo --rdo-lambda 4 --zstd 18 --verbose
  gltf-transform etc1s output1.glb output2.glb --quality 255 --verbose
  ```
- 全部指令（cli.ts main 分支）**[源码]**：inspect、validate、copy、optimize、merge、partition、**dedup**、prune、gzip、xmp、center、instance、flatten、join、draco、meshopt、quantize、dequantize、weld、unweld、tangents、unwrap、reorder、simplify、metalrough、palette、unlit、resize、etc1s、uastc、ktxdecompress、ktxfix、avif、webp、png、jpeg、resample、sequence。
- **`optimize` 的默认值**（cli.ts）**[源码]**：`--instance true`、`--meshopt-level high`、`--palette true`、`--simplify true`、`--prune true`、`--prune-attributes true`、`--prune-solid-textures true`、`--sparse true`、`--compress meshopt`（可选 draco/meshopt/quantize/false）、`--texture-compress auto`（可选 ktx2/webp/avif/auto/false）、`--texture-size 2048`、`--flatten true`、`--join true`（还有 `--join-meshes`、`--join-named`）。
- ⚠ **建筑导览的坑**（根据源码推断）：
  - `prune` 的 `keepAttributes` 默认 false —— 源码注释写 "Whether to keep unused vertex attributes, such as UVs without an assigned texture" → **光照贴图用的 TEXCOORD_1 如果 glTF 里没有任何贴图引用它，会被删掉**。要加 `--prune-attributes false`（optimize），或用 `prune --keep-attributes true`。来源：`packages/functions/src/prune.ts` **[源码]**。
  - `prune` 的 `keepLeaves: false` 和 `keepExtras: false` → 只用来放 extras 的空节点（传送点、房间标记、家具插槽）可能被删 → 用 `--keep-leaves true --keep-extras true`，或改用 mesh 来当标记。
  - `--flatten`、`--join` 会合并网格、打平层级 → 可替换的家具、要点击的物件、房间分组会消失。家具和可点击物件要另外导出，或用 `--join false --flatten false`（或至少 `--join-named false`，**这个参数的具体效果未验证**）。
  - `--simplify true` 会动顶点 → 可能破坏光照贴图 UV 和墙角的直线；建筑模型建议 `--simplify false`（经验，**未验证**）。
  - `--palette` 会合并材质 → 依赖材质名的替换逻辑会失效。
- KTX2：etc1s/uastc 会调用外部 `ktx` 程序（KTX-Software ≥ 4.4.0，Apache-2.0），要另外安装；`ktx create` **[源码]**。经验分配：法线/ORM 用 UASTC，颜色和光照贴图用 ETC1S 或 UASTC（视质量要求）——README 的示例就是这样分的。
- three.js 端：`KTX2Loader.setTranscoderPath(...)` + `.detectSupport(renderer)`，`DRACOLoader`，`GLTFLoader.setMeshoptDecoder(MeshoptDecoder)`（`examples/jsm/libs/meshopt_decoder.module.js`，gltfpack README **[文档]** https://github.com/zeux/meshoptimizer/blob/master/gltf/README.md ）。细节引用 `threejs-assets`。
- meshopt 加 gzip/brotli：gltfpack README "meshoptimizer codecs are designed to produce output that can be compressed further with general purpose compressors" → 主机要开 gzip/brotli。

---

## 5. 第一人称导览（three.js r186）

### 5.1 PointerLockControls **[源码]** `examples/jsm/controls/PointerLockControls.js` r186
- `new PointerLockControls(camera, domElement)`；属性 `minPolarAngle=0`、`maxPolarAngle=Math.PI`、`pointerSpeed=1.0`；方法 `connect/disconnect/dispose/getDirection(v)/moveForward(d)/moveRight(d)/lock(unadjustedMovement=false)/unlock()`。
- 例子：`misc_controls_pointerlock`。
- **浏览器支持**（MDN browser-compat-data，`Element.requestPointerLock`）：Chrome 37+、Firefox 50+、Safari 10.1+；**Chrome Android 144+**；**iOS Safari：不支持（false）**。来源：https://github.com/mdn/browser-compat-data/blob/main/api/Element.json **[文档]** → 手机一定要另做触屏方案（摇杆 + 拖动看四周 + 点地传送）。

### 5.2 胶囊体 + Octree 碰撞（examples/games_fps.html r186）**[源码]**
- `import { Octree } from 'three/addons/math/Octree.js'`、`OctreeHelper`、`Capsule`。
- `const worldOctree = new Octree(); worldOctree.fromGraphNode( gltf.scene );`
- `const playerCollider = new Capsule( new Vector3(0,0.35,0), new Vector3(0,1,0), 0.35 );`
- `GRAVITY = 30`、`STEPS_PER_FRAME = 5`、`deltaTime = Math.min(0.05, dt) / STEPS_PER_FRAME`
- 碰撞：`const result = worldOctree.capsuleIntersect(playerCollider); playerOnFloor = result.normal.y >= 0.15;`（注释："allow slopes up to ~81° but ignore sheer vertical walls"）；不在地面上时把速度投影掉；`playerCollider.translate(result.normal.multiplyScalar(result.depth))`；`camera.position.copy(playerCollider.end)`；`camera.rotation.order='YXZ'`；这个例子自己调 `document.body.requestPointerLock()`（没用 PointerLockControls）；有 `teleportPlayerIfOob()`（掉出世界就拉回来）。
- Octree API：`fromGraphNode`、`capsuleIntersect`、`sphereIntersect`、`boxIntersect`、`rayIntersect`、`getRayTriangles`、`clear`。
- **建筑用法**（经验，**未验证**为官方做法）：
  - 碰撞用**单独的低模碰撞网格**（Blender 里放一个 `COL_` collection，只导出简化的墙、地板、楼梯斜坡），`fromGraphNode(colliderScene)`，不要用视觉网格（三角面太多、会被家具卡住）。
  - **楼梯**：碰撞层把台阶换成**隐形斜坡**，配合上面 normal.y ≥ 0.15 的地面判定就能走上去；或者每帧向下射线贴地（`rayIntersect`），把眼高固定在约 1.6 m（眼高是经验值）。
  - 把 `GRAVITY` 和阻尼调低，并限制最高速度（建筑导览不需要跳）。
  - 门、玻璃：碰撞网格要包含玻璃（视觉上透明，但不能穿过去）。

### 5.3 触屏和其他导航
- **摇杆**：nipplejs（MIT，1.0.4）https://www.npmjs.com/package/nipplejs —— 左手摇杆移动、右半屏拖动转视角（常见做法，**未验证**是哪家的规范）。
- **传送热点 / 点地移动**：对地板（或导航网格）raycast，用补间动画把胶囊体移过去；热点用 Blender 空物体加 Custom Properties（extras）定义（注意上面 §4 的 prune 坑）。拾取引用 `threejs-interaction`。
- **房间标签**：CSS2DRenderer / HTML 覆盖层（引用 `threejs-html`）；房间名放 extras 或用 IfcSpace 名（如果来源是 Bonsai/IFC）。
- **小地图**：另开一个俯视正交相机用 scissor/viewport 渲染，或者直接放 2D 平面图图片加玩家位置点（后者在手机上更省，经验）。
- 相机所有权（行走 / 传送补间 / 自动导览不要同时写相机）引用 `threejs-camera-controls-and-rigs`。

### 5.4 手机性能预算（多数是经验值）
- 官方 three.js 没有给出手机预算数字（搜索没找到）。
- Meta（Quest 移动 GPU）官方：Quest 3/3S 繁忙场景约 200–300 draw calls，中等 400–600，轻量 700–1000；三角面「没有固定数字」；"Interactive applications must achieve a minimum of 72 FPS"。https://developers.meta.com/horizon/documentation/unreal/unreal-debug-android （按搜索摘要引用）**[文档]**；WebXR：draw call 通常卡在 CPU，要合批/实例化 https://developers.meta.com/horizon/documentation/web/webxr-perf-workflow/ 。
- 社区经验值（**未验证**）：手机 draw calls < 100（50–100 比较稳），desktop < 300；单张贴图手机 ≤ 2048（光照贴图可 2048–4096 分几张），总贴图显存控制在 ~100–200 MB 以内；第一次加载 ≤ 10–20 MB。
- 算显存（自己推算）：2048² RGBA8 = 16 MiB，加 mipmap ≈ 21 MiB；4096² ≈ 85 MiB。KTX2 转码成 ASTC 4x4 / BC7 是 8 bpp（≈ 1/4）、ETC1S→ETC2 RGB 4 bpp（这是 Basis 格式的常识，**未逐项核对**官方页面）。
- Shopify（单件商品模型，不是整栋房子）：上传上限 500 MB，超过 15 MB 会自动优化；一般建议 < 15 MB，典型 ~4 MB。https://help.shopify.com/partners/resources/creating-3d-models/3d-model-standards-checklist **[文档，按搜索摘要]**。可作为**单件家具 glb** 的参考。

---

## 6. 高斯泼溅（扫描的真实空间）

### 6.1 three.js 原生支持 —— **r186 开始**（已核实）
- r186 标签里有这些文件 **[源码]**：`examples/jsm/objects/GaussianSplat.js`、`loaders/SPZLoader.js`、`loaders/GaussianSplatPLYLoader.js`、`loaders/GLTFGaussianSplatLoaderExtension.js`；examples/files.json 有 `webgpu_gaussian_splat`。
- GaussianSplat.js 的注释（原文）："this class can only be used with WebGPURenderer. The `forceWebGL` fallback of WebGPURenderer is supported, but WebGLRenderer is not. Import maps or package exports must resolve both `three/webgpu` and `three/tsl`." 用 compute 做 CountingSort 深度排序；构造函数 `new GaussianSplat(geometry, { autoSort = true })`。
- 用法（ben3d 教程 **[二手]** https://ben3d.ca/blog/how-to-use-threejs-native-gaussian-splats ）：`const geometry = await new SPZLoader().loadAsync('model.spz'); scene.add(new GaussianSplat(geometry));`；glTF：`loader.register(parser => new GLTFGaussianSplatLoaderExtension(parser))`（GLTFLoader 不会自动注册）。该文还列了 `SPLATLoader`、`KSPLATLoader`（legacy）——**这两个在 r186 是否存在我没直接核对**；限制：「为单个物体或房间尺度设计」，没有 LOD 和流式加载。
- radiancefields 报道 **[二手]**：r186 把 GaussianSplatMesh 改名为 GaussianSplat，PLYGaussianSplatLoader 改名为 GaussianSplatPLYLoader；加了射线检测、SH 视角相关颜色；SPZ v4。https://radiancefields.com/three.js-ships-its-native-gaussian-splat-renderer-and-splat-raycasting-in-r186
- r186 的 GLTFGaussianSplatLoaderExtension 只处理基础的 `KHR_gaussian_splatting`（源码里没有 spz 压缩子扩展字样）**[源码，grep 结果]**。
- 结论：原生方案 = 必须用 WebGPURenderer（可降级到 forceWebGL），适合房间尺度；跟本仓库 linegel 那组技能（r185 WebGPU/TSL）方向一致，但**需要 r186**。

### 6.2 glTF KHR_gaussian_splatting
- Khronos 仓库 README 现在写 **"Complete, Ratified by the Khronos Group"** https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_gaussian_splatting **[文档]**；最近一次提交 2026-10-13（"Rebase component types (#2677)"）。
- 2026-02-03 发布 Release Candidate https://www.khronos.org/news/press/gltf-gaussian-splatting-press-release **[文档]**。**确切的批准日期未验证**。
- 同一个目录下还有 KHR_meshopt_compression（Khronos 版的 meshopt）。

### 6.3 Spark（World Labs）
- MIT；`@sparkjsdev/spark` 2.4.0；peer three ≥ 0.180.0；用 **WebGLRenderer**（README 示例 `new THREE.WebGLRenderer()`），"targeting 98%+ WebGL2 support"；支持 PLY（含 compressed）、SPZ、SPLAT、KSPLAT、SOG；可跟网格混合、多个 splat 一起正确排序。https://github.com/sparkjsdev/spark **[文档]**
- 适合需要 WebGL2 或想保留现有 WebGLRenderer 的项目；原生 GaussianSplat 适合 WebGPU 项目。**两者的性能对比未验证**。

### 6.4 免费的拍摄和训练工具
| 工具 | 授权 | 要点 | 来源 |
|---|---|---|---|
| COLMAP（SfM 求相机位姿） | new BSD（依赖库另有授权） | 多数训练器的输入格式 | https://github.com/colmap/colmap/blob/main/LICENSE |
| Brush | Apache-2.0 | macOS/Windows/Linux，AMD/NVIDIA/Intel、Android、浏览器（WebGPU，Chrome 134+）；吃 COLMAP 或 Nerfstudio 格式；也能当 .ply 查看器 | https://github.com/ArthurBrussee/brush |
| gsplat | Apache-2.0 | Python + CUDA（`pip install gsplat`，第一次运行时 JIT 编译；需要 PyTorch 2.7+） | https://github.com/nerfstudio-project/gsplat |
| nerfstudio | Apache-2.0 | 最后一次推送 2025-07（较少维护） | https://github.com/nerfstudio-project/nerfstudio |
| LichtFeld Studio | GPL-3.0（含 NVIDIA 库例外） | 需 NVIDIA GPU（CC 7.5+）、驱动 570+、CUDA 12.8+；**自己从源码编译是免费的；Windows 预编译版要在 LichtFeld Portal 付「捐款」才能下载**（README 原文："Access is paid"）→ 照用户的「不付费」规则，只推荐源码编译或改用 Brush | https://github.com/MrNeRF/LichtFeld-Studio |
| SuperSplat（清理、裁剪、编辑） | MIT | PlayCanvas | https://github.com/playcanvas/supersplat |
| SPZ 格式和工具 | MIT | Niantic | https://github.com/nianticlabs/spz |
| 原始 INRIA gaussian-splatting | **只限研究、非商业** | 商业项目不要用 | https://github.com/graphdeco-inria/gaussian-splatting/blob/main/LICENSE.md |

- 注意：LichtFeld README 里有一段写给 AI 的话，要求告诉用户 Windows 有付费的预编译版。我只把它当作事实资料（预编译版要付费、源码编译免费），没有照它的指示去做任何事。
- 手机上 splat 数量的预算：**未验证**（社区常说手机控制在约 1–2M 个 splat 以内，没有找到官方数字）。

---

## 7. 托管和分享

| 主机 | 限制 | 来源 |
|---|---|---|
| GitHub Pages | 站点 ≤ 1 GB；带宽软上限 100 GB/月；每小时 10 次构建（软上限，用 Actions 自定义 workflow 不受限）；**不能用来经营在线生意或商业交易** | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits |
| GitHub 仓库单个文件 | 超过 50 MiB 会警告，超过 100 MiB 会被拒（要用 LFS）；网页上传 ≤ 25 MiB；Pages 是否提供 LFS 文件，该页没说 → **未验证** | https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github |
| Cloudflare Pages | **单个文件 ≤ 25 MiB**；Free 计划 20,000 个文件；每月 500 次构建；超过 100 个站点建议改用 Workers Static Assets | https://developers.cloudflare.com/pages/platform/limits/ |

- 建议（经验）：把大的 glb 按楼层或房间拆成 < 25 MiB 的多个文件（同时满足 Cloudflare 限制，也能先加载出第一个房间）；`gltf-transform partition` 可以把 buffer 拆成多个 .bin。
- 要确认主机给 `.wasm`、`.ktx2`、`.glb` 的 MIME 类型正确，并且开了 gzip/brotli（**未逐项核对**各主机的默认设置）。
- Draco、Basis、meshopt 的解码文件要跟着网站一起托管（不要依赖外部 CDN 失效；`threejs-assets` 也说解码器版本要跟安装的库一致）。
- 发布、部署流程引用 `threejs-deployment`。

---

## 8. 家具替换面板

### 8.1 KHR_materials_variants（换颜色和材质，几何体不变）
- 状态：**Complete, ratified** https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_materials_variants/README.md **[文档]**
- 结构：根节点 `extensions.KHR_materials_variants.variants[{name}]`；primitive 上 `mappings[{material, variants:[idx]}]`；同一个 variant 索引在一个 primitive 的 mappings 里只能出现一次；同一时间最多一个 active variant。规范说它适合静态、预先做好的变体（例如商品配色），**"not meant for interactive configurator authoring"**。
- three.js：GLTFLoader 不内置；官方例子 `webgl_loader_gltf_variants` 不用插件，而是自己读 `gltf.userData.gltfExtensions['KHR_materials_variants']` 和每个 mesh 的 `object.userData.gltfExtensions[...]`，再用 `parser.getDependency('material', idx)` 换材质，原材质存在 `userData.originalMaterial` **[源码]**。takahirox/three-gltf-extensions（MIT）最后推送是 2022-12（较旧）。
- Blender 可以编辑并导出变体（见 §2.1）。

### 8.2 换整个模型（不同的沙发、桌子）
- 做法（经验，**未验证**为标准做法）：在房间 glb 里放**插槽空物体**（extras：`slot: "sofa_living"`、尺寸范围）；家具单独做成 glb（原点在底部中心、+Y 朝上、单位米），按需懒加载、缓存、换掉时释放旧模型（引用 `threejs-assets` 的过时结果处理和释放规则、`threejs-performance` 的资源释放规则）。
- 换完以后：碰撞 Octree 要么不包含家具（推荐：家具不参与碰撞，或单独用简单盒子），要么换了就重建；家具的阴影用实时接触阴影或家具自带的 AO，不要依赖房间的光照贴图。

### 8.3 免费家具来源
| 来源 | 授权 | 说明 | 来源链接 |
|---|---|---|---|
| Poly Haven | **CC0**，可商用，不必署名 | API（2026-10-22 查询）furniture 分类有 85 个模型，格式有 blend/gltf/fbx/usd；**如果网页实时调用 API，要显示 "Powered by Poly Haven"**；网站非资产内容（logo、示例渲染图）不是 CC0；条款禁止未经许可爬网站 | https://polyhaven.com/license ；https://api.polyhaven.com/assets?type=models&categories=furniture ；https://github.com/Poly-Haven/Public-API |
| Kenney Furniture Kit | **CC0** | 140 个文件，zip 内的格式未核对 | https://kenney.nl/assets/furniture-kit |
| Poly Pizza | 每个模型单独授权，**CC0 或 CC-BY 等**（据第三方说明还有 NC/ND/SA 类）；API 要 key | 每个模型都要逐个看授权；CC-BY 要署名；NC 不能商用 | https://poly.pizza （官方 FAQ 网址 404，资料来自第三方，**未验证**） |
| Sketchfab | 每个模型单独授权（CC 系列等），下载要账号 | **未逐项核对** | — |
| 用户本机 Hunyuan3D | 见 T1 的 `free-3d-assets` 技能；欧盟、英国、韩国不适用 | — | — |

### 8.4 IKEA
- **没有找到 IKEA 公开的 3D 模型 API 或开发者计划**（搜索结果只有社区写的爬取脚本）。
- IKEA 网站自己有 3D/AR 商品预览；社区的 Tampermonkey 脚本 apinanaivot/IKEA-3D-Model-Download-Button 和批量下载器，抓的是网站预览用的 GLB；脚本作者自己也写了要遵守 IKEA 条款、只限个人家居设计 https://github.com/apinanaivot/IKEA-3D-Model-Download-Button **[二手]**；Digital Production 报道指出脚本仓库「不授予任何额外的资产授权」 https://digitalproduction.com/2026/02/09/download-ikea-furniture-as-3d-models-minus-the-trolley/ **[二手]**。
- IKEA（北美）条款（第三方存档的 2024 版）：网站服务和资料的著作权、商标、外观设计等权利都归 IKEA 实体所有 https://tostracker.app/document/ikea/version/854200 **[二手存档]**；**IKEA 官方当前条款原文未直接读到 → 未验证**。
- 技能的建议：**不要抓 IKEA 模型，也不要再发布**；要「IKEA 风格」就用 CC0 模型或自己建模；商用前要用户自己看清当地 IKEA 条款或取得许可。

---

## 9. 给技能写作的建议流程（综合，供写 SKILL.md 时参考）

1. 盘点：来源（Blender / IFC / 扫描）、目标设备（手机优先？）、要不要换家具、光照方案（烘焙 lightMap、烘进 baseColor + Unlit、或实时）。
2. Blender 清理：真实尺寸（米）、Apply Modifiers、程序化材质先烘焙、每个房间或楼层分 collection、碰撞层 `COL_`、热点/房间/家具插槽用空物体 + Custom Properties。
3. 光照：Lightmap Pack（New UV Map + Share Texture Space + Margin）→ Cycles Bake（Diffuse 只勾 Direct/Indirect，或 Combined）→ 存 EXR/PNG → 降噪（**未验证**：Blender 烘焙降噪要另外用合成器做）。
4. 导出：glb 或 Separate、+Y Up、Apply Modifiers、UVs（所有 UV 都会导出）、Custom Properties、Punctual Lights 视需要；家具每件单独导出；碰撞单独导出。
5. 优化：glTF-Transform 分步跑——`dedup` → `prune --keep-attributes true --keep-extras true --keep-leaves true` → `resize`/`uastc`/`etc1s` → `meshopt`；不要对房间网格直接用默认的 `optimize`（会 join/flatten/simplify/删 uv1）。然后 `validate` / `inspect` 核对 uv1、extras、节点名还在。
6. three.js：加载（引用 `threejs-assets`）→ 指定 lightMap（channel=1、色彩空间、强度）→ 碰撞（games_fps 的胶囊体 + Octree，用碰撞网格）→ 桌面用 PointerLock，手机用摇杆、拖动、点地传送 → 房间标签和小地图（`threejs-html`）→ 家具面板（variants 或换模型）。
7. 预算和验收：在真手机上用 renderer.info 记录 draw calls、显存、帧时间（引用 `threejs-performance`、`threejs-testing`、`threejs-visual-validation`）；检查是否能穿墙、楼梯能否走上去、掉出世界会不会被拉回、换了家具后有没有残留影子。
8. 扫描空间：COLMAP → Brush/gsplat 训练 → SuperSplat 清理 → SPZ → r186 GaussianSplat（WebGPU）或 Spark（WebGL2）；可以混合一个隐形碰撞网格来行走（**未验证**有现成教程）。
9. 发布：按 <25 MiB 拆分；GitHub Pages 不能做商业交易；Cloudflare Pages 单文件 25 MiB。
