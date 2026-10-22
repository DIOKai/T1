# real-map-3d 资料笔记（2026-10-22）

目的：为新技能 `real-map-3d` 准备资料——在浏览器里用**真实地图数据**（OpenStreetMap 建筑、行政边界、地形）做 3D 城市，服务「Capital Rift」这类欧洲地图经营游戏（分区、放大到真实街区、盖工厂、出租建筑）。仓库里已有的 40 个 three.js 技能（见 `docs/skill-batches/city-40-2026-10-18.md`）只会生成虚构/程序化城市，本技能补上「真实数据从哪来、能不能用、怎么转成游戏坐标」。

标记：**[文档]** 官方页面；**[源码]** 读了源码或仓库文件；**[npm]** npm registry 当天的 latest；**未验证** = 没找到一手来源、是推论或经验值。所有页面都在 2026-10-22 读取。

---

## 1. OSM 数据授权（ODbL）

- 署名：要写出「OpenStreetMap」并说明数据是 ODbL，可以把文字链接到 openstreetmap.org/copyright；「© OpenStreetMap contributors」可用；改过样式可写 "Map data from OpenStreetMap"。互动地图放在地图角落；**游戏可以放在启动画面、游戏画面、游玩中、制作人员名单或菜单**，但详细授权信息要找得到。署名可以在互动或 5 秒后淡出，但要留「(i)」或关于菜单。页面没有专门讲 3D。**[文档]** https://osmfoundation.org/wiki/Licence/Attribution_Guidelines
- Produced Work（成品，如图片、游戏画面）vs Derivative Database（衍生数据库）：判断标准是结果是不是「用来提取原始数据」；不是的话就是 Produced Work。页面没有游戏的例子 → 「游戏画面算 Produced Work」是推论（**未验证**）。用衍生数据库做出 Produced Work 并公开使用时，**底层的衍生数据库也要按 ODbL 提供**。**[文档]** https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline
- FAQ：和「独立」数据库合在一起可能是 Collective Database，share-alike 不一定延伸到独立数据；但「修改、补充、更正、扩展」OSM 的数据是衍生数据库。Produced Work 可以用任何条款授权，但别人**要求时**要提供 OSM 数据和衍生数据库。FAQ 没说游戏代码要开源（ODbL 管数据不管代码，推论，**未验证**）。**不是法律意见。** **[文档]** https://osmfoundation.org/wiki/Licence/Licence_and_Legal_FAQ
- Horizontal Map Layers：按「Feature Type」（街道、餐厅、公园…）判断；某类要素**全部**来自非 OSM 来源 → 不触发 share-alike；同一类既有 OSM 又有非 OSM（哪怕分图层）→ 触发；「对照 OSM 补漏」也是衍生。**[文档]** https://osmfoundation.org/wiki/Licence/Community_Guidelines/Horizontal_Map_Layers_-_Guideline
  - 对游戏的推论（**未验证，需律师确认**）：玩家盖的工厂、租约、资源点是游戏自己的 Feature Type，和 OSM 建筑分开存 → 大概率不触发 share-alike；但如果「修正 OSM 建筑高度/轮廓」并存回游戏的建筑表，这张表就是衍生数据库，公开使用时要按 ODbL 提供。

## 2. Overpass API

- 公共实例列表与政策。主实例 `https://overpass-api.de/api/interpreter`（FOSSGIS，页面说经常超载）。轻度使用：**每天 < 10,000 次查询、< 1 GB 数据、总处理时间 < 10 分钟**；定期使用再除以 100（< 100 次、< 10 MB/天）。**App 和网站的所有用户共用这份额度**。要带能识别 App 的 User-Agent 或 Referer；不要并行跑多个脚本；**商业用途要自建或用付费服务器**；结果要缓存；遇到 HTTP 429/406 暂停 30 秒再试。默认超时 3 分钟，可 `[timeout:900]`。输出 `[out:json]`、`out geom`（way 直接带坐标）；osmtogeojson 可转 GeoJSON。页面还特别提醒不要从 lovable.app / netlify.app 这类快速部署平台直接调用。**[文档]** https://wiki.openstreetmap.org/wiki/Overpass_API
- 其他实例：VK Maps、private.coffee（大项目先通知）、overpass.ch（免费 1 万次/月、30 次/分钟）；Geofabrik/Tracestrack 等付费。**[文档]** 同上。
- 结论：**游戏客户端绝不能直接调 Overpass**；只在开发时离线抓小范围，或用 Geofabrik 等的 .osm.pbf 分区下载自己处理（下载站本技能没逐一核实条款，**未验证**）。

## 3. OSM 瓦片政策（tile.openstreetmap.org）

- 要 HTTPS、独特的 User-Agent（App）/ 有效 Referer（网页）、地图上清楚署名、遵守缓存头（读不到就至少缓存 7 天）。**禁止**：批量下载/预取/预生成、「下载离线」、后台抓用户没看的瓦片、无头机器人。**无 SLA**，重度使用会被封。替代：OSM 衍生的托管服务、商业服务、矢量瓦片或自建。**[文档]** https://operations.osmfoundation.org/policies/tiles/
- 结论：游戏不能拿 tile.openstreetmap.org 当底图。
- Nominatim（地理编码）：最多 **1 次/秒**、整个 App 共用、要缓存、**禁止自动补全**和系统性批量查询。**[文档]** https://operations.osmfoundation.org/policies/nominatim/

## 4. 免费/开放的矢量瓦片

| 方案 | 费用/限制 | 授权 | 来源 |
|---|---|---|---|
| **Protomaps PMTiles（自建）** | 每日 planet build（z0–15，约 120 GB），用 `pmtiles extract` 截区域，`--maxzoom` 缩小；**不要盗链 build URL**，复制到自己的存储 | 数据：ODbL Produced Work，要 OSM 署名；`pmtiles` 4.5.0、`@protomaps/basemaps` 5.7.2 都是 BSD-3-Clause **[npm]** | https://docs.protomaps.com/basemaps/downloads |
| Protomaps 图层 | `buildings` 图层有 `height`、`min_height`（低缩放可能量化），z15+ 是与 OSM 对应的单栋，z0–14 是合并的 | — | https://docs.protomaps.com/basemaps/layers |
| **OpenFreeMap** | 公共实例免费、**不限地图浏览量和请求**、无需注册/API key、**允许商用**；靠捐款；离线下载每次 ≤ 3000 瓦片或 50 MB、≤ 4 并发 | 代码 MIT；要署名 "OpenFreeMap © OpenMapTiles Data from OpenStreetMap" | https://openfreemap.org/ ；https://openfreemap.org/quick_start/ |
| OpenFreeMap 样式 | `https://tiles.openfreemap.org/styles/liberty`、`/bright`、`/positron`；矢量源 `https://tiles.openfreemap.org/planet`（来自 MapLibre 3D 建筑示例）；schema = OpenMapTiles | — | 同上 |
| MapTiler Cloud Free | 5,000 map sessions/月、100,000 API 请求/月、3D sessions 2,000/月；超出就**暂停到下个月**；地图上显示 MapTiler logo；页面写「测试、原型、个人或非商业」→ **商用不清楚，视作付费方案** | — | https://www.maptiler.com/cloud/pricing/ |

结论：原型用 OpenFreeMap；正式上线自建 Protomaps PMTiles（静态文件 + HTTP Range，放 CDN/对象存储）。注意 OpenFreeMap 无 SLA（推论，**未验证**），不要把游戏命脉绑在捐款运营的公共实例上。

## 5. MapLibre GL JS

- 版本：`maplibre-gl` **6.15.0**，**BSD-3-Clause**。**[npm]** https://registry.npmjs.org/maplibre-gl/latest ；**[源码]** https://github.com/maplibre/maplibre-gl-js/blob/main/LICENSE.txt
- 3D 建筑（官方示例，用 OpenFreeMap）：source `https://tiles.openfreemap.org/planet`，`source-layer: 'building'`，`type: 'fill-extrusion'`，`minzoom: 15`，`filter ['!=', ['get','hide_3d'], true]`，高度 `['interpolate',['linear'],['zoom'],15,0,16,['get','render_height']]`，底 `render_min_height`；插在第一个文字图层下；`canvasContextAttributes: {antialias: true}`。**[文档]** https://maplibre.org/maplibre-gl-js/docs/examples/display-buildings-in-3d/
- 地形：style 里 `terrain: {source, exaggeration}` + `raster-dem` 源 + `hillshade` 图层 + `TerrainControl`；示例用 Mapterhorn `https://tiles.mapterhorn.com/tilejson.json`。**[文档]** https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/
- CustomLayerInterface：`renderingMode: '3d'` 共享深度缓冲；`render` 时混合是预乘 alpha；要渲到纹理用 `prerender`；`onAdd(map, gl)` / `onRemove`。**[文档]** https://maplibre.org/maplibre-gl-js/docs/API/interfaces/CustomLayerInterface/
- three.js 自定义图层的手写写法（`args.defaultProjectionData.mainMatrix` × 模型矩阵；`MercatorCoordinate.fromLngLat` + `meterInMercatorCoordinateUnits()`；y 轴缩放取负；`renderer.autoClear=false`、`resetState()`、`triggerRepaint()`；注释里提到 `args.getMatrixForModel(origin, altitude)` 在任何投影下都对）。**[源码]** 2025-06 版本的 `test/examples/add-a-3d-model-using-threejs.html`（commit f9140dc）：https://github.com/maplibre/maplibre-gl-js/blob/f9140dc2c2ff2b77bdac4d882ce1f2452e2293e6/test/examples/add-a-3d-model-using-threejs.html
- **2026-10-06 起**官方示例改用 `maplibre-gl-three@3.0.0`（`ThreeDManager`、`createLayer()`、`getEcefMatrix({point, height})`、`load3dTiles`），搭配 three 0.186.1、3d-tiles-renderer 0.5.3。**[源码]** commit f98ef79；https://raw.githubusercontent.com/maplibre/maplibre-gl-js/main/test/examples/add-3d-tiles-3d-objects-and-models-using-threejs.html 。maplibre-gl-three 的授权本次没查，**未验证**。
- 手写写法在 6.x 上是否原样可用：没实测，**未验证**。

## 6. deck.gl

- `deck.gl` 9.4.0、`@deck.gl/mapbox` 9.4.0，MIT。**[npm]** MapLibre 有专门的 `@deck.gl/maplibre`（MapLibreOverlay）；交错模式下像素比由 MapLibre 的 `pixelRatio` 决定。**[文档]** https://deck.gl/docs/api-reference/mapbox/mapbox-overlay （MapLibreOverlay 页本次没读，**未验证**）

## 7. OSM 建筑高度

- `height` 优先（含屋顶，单位默认米，裸数字就是米）；没有时用 `building:levels`，常用约 **3 m/层**；`roof:levels` 不算进 `building:levels`；`building:levels:underground` 不算地上高度；`building:min_level` 与 `min_height` 决定悬空部分的底。`building:levels` 应是正整数。CoMaps / Organic Maps / F4 Map 只在没有 `height` 时才用层数。**[文档]** https://wiki.openstreetmap.org/wiki/Key:building:levels
- Simple 3D Buildings：`building:part` 存在时，3D 渲染**不用**外轮廓（2D 仍用）；`roof:height` 让立面高 = `height − roof:height`；页面没定义每层默认高度。**[文档]** https://wiki.openstreetmap.org/wiki/Simple_3D_Buildings
- 没有任何高度标签时的默认值：本技能脚本用 3 层 × 3 m = 9 m，是**经验值**，可改。

## 8. 行政区边界（游戏分区）

- `admin_level=2` = 国界；3–11 是下级，数字越大越小。德国 4 = 州、6 = 县（Landkreis）、8 = 市镇；法国 4 = 大区、6 = 省、8 = 市镇；意大利 4 = 大区、6 = 省、8 = 市镇。各国含义不同，要查国家表。**[文档]** https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative （页面太长，波兰/英国/西班牙在后半段，本次没读，**未验证**）
- **Natural Earth**：**公有领域**，无需许可、可商用、无需署名（可选写 "Made with Natural Earth"）；无精度担保。**[文档]** https://www.naturalearthdata.com/about/terms-of-use/ （页面没讲争议领土；游戏分区涉及争议边界时自行决定显示方式，**未验证**）

## 9. 高程数据（DEM）

- **Copernicus DEM GLO-30 / GLO-90**：全球免费授权，约 30 m / 90 m；公众可下载 GLO-30 和 GLO-90（要注册 Copernicus Data Space）；修改后要写 "produced using Copernicus WorldDEM-30" 加 DLR / Airbus 版权声明。详细条款在 ESA 用户许可和附件里（本次没读，**未验证**）。**[文档]** https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM
- **Terrarium** 编码：`高度 = (R×256 + G + B/256) − 32768`。**[源码]** https://github.com/tilezen/joerd/blob/master/docs/formats.md
- AWS Terrain Tiles（Mapzen/Tilezen）：S3 `elevation-tiles-prod`（us-east-1）、欧盟副本 `elevation-tiles-prod-eu`，无需账号。**[文档]** https://registry.opendata.aws/terrain-tiles/ 。署名要按来源列（EU-DEM："Europe terrain data produced using Copernicus data and information funded by the European Union - EU-DEM layers" 等）。**[源码]** https://github.com/tilezen/joerd/blob/master/docs/attribution.md 。具体 URL 模板这两页都没给，常见的 `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png` 是**未验证**。
- **Mapterhorn**：公共地形瓦片，全球 30 m + 部分国家更高分辨率；Terrarium 编码、512 px WebP；`https://tiles.mapterhorn.com/{z}/{x}/{y}.webp`、TileJSON；可从 `https://download.mapterhorn.com/` 下载 `planet.pmtiles`（z0–12）和分区 z13+ 自建；代码 BSD-3；Cloudflare 赞助；**页面没写用量限制和数据授权**，署名看 https://mapterhorn.com/attribution（本次没读，**未验证**）。**[文档]** https://mapterhorn.com/ ；https://mapterhorn.com/data-access/

## 10. 付费 / 有限额的 3D 服务（只记录，用前先问）

- **Google Photorealistic 3D Tiles**（**付费**）：Map Tiles API 3D Tiles（Enterprise SKU）每月免费 1,000 events，之后每 1,000 events 6.00 美元起；要 API key（计费账号是否必需页面没写，**未验证**）。政策：**禁止预取/存储/缓存**（有限例外）、禁止提取几何、禁止离线；署名单行放底部；自己的 3D 物件可以叠上去但不能从瓦片描出来。→ 不适合「把建筑当游戏资产」。**[文档]** https://developers.google.com/maps/billing-and-pricing/pricing ；https://developers.google.com/maps/documentation/tile/policies
- **Cesium ion Community**（**有限免费，商用要付费**）：10 GB 存储、15 GB/月流量；「个人与非商业」，公司年收入/融资超过 5 万美元或超量就要付费；含 Google 3D Tiles 1,000 root tiles/月。**[文档]** https://cesium.com/platform/cesium-ion/pricing/

## 11. 坐标与性能（本技能自己写的部分）

- Web Mercator：MapLibre 的 `MercatorCoordinate`（0–1 世界坐标）和 `meterInMercatorCoordinateUnits()`（随纬度变化，= 1/(地球周长×cos 纬度)）。**[源码]** 上面的示例。
- 游戏逻辑用**局部 ENU 米**（东、北、上）：WGS84 → ECEF → ENU 是标准公式（脚本里实现并用测试对照子午线弧长）。为什么不用墨卡托米：墨卡托在纬度 φ 处放大 1/cos φ（欧洲 50°N 约 1.56 倍），面积、租金、运输距离会算错。
- float32 精度：three.js 顶点是 float32，离原点几十公里后厘米级抖动——每个城市/区块用自己的原点（推论、通用图形学常识，**未验证**具体阈值）。
- 性能做法（合并几何、实例化、按瓦片加载/卸载、LOD）交给仓库的 `threejs-performance`、`threejs-geometry`；本技能只给地图游戏的分层建议，数字都是经验值。

## 12. npm 当天版本（2026-10-22）

maplibre-gl 6.15.0 (BSD-3-Clause)；pmtiles 4.5.0 (BSD-3-Clause)；@protomaps/basemaps 5.7.2 (BSD-3-Clause)；three 0.186.1 (MIT)；deck.gl 9.4.0 (MIT)；osmtogeojson 3.0.0-beta.5 (MIT)。来源 `https://registry.npmjs.org/<包名>/latest`。

## 13. 交给其他技能

- 经济数值（产出、租金、价格曲线）→ `game-balance-economy`；核心循环、多人互动 → `game-design-core`（照 T1 规则先问）。
- three.js 通用：`threejs-web`、`threejs-geometry`、`threejs-performance`、`threejs-interaction`、`threejs-camera-controls-and-rigs`、`threejs-procedural-buildings-and-cities`（给没有细节的 OSM 盒子加立面）。
