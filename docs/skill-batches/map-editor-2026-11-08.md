# 地图编辑补完

日期：2026-11-08。和武器、涂装那一批（`weapons-livery-props-sirens-2026-11-08.md`）同时调研。资料查得最慢，所以另开 PR。

## 资料

- **影片**：只读到 9 部有英文原声字幕的影片，另外 17 部只有章节和简介，引用时标「from chapter titles, unverified」。YouTube 一直限流，几部重要的影片没拿到字幕，例如 RoyalT 那部一小时讲修地形、删建筑。
- **文档**：FiveM 官方素材手册第 2、4、5、6 篇，fxmanifest 和 data_file 文档，Sollumz 2.9 的 ymap 文档。
- **源码**：
  - CodeWalker：实体 flag 和 ymap 内容 flag 的对照表、Calculate Extents 和 CalcFlags 的算法、parentIndex 的判断逻辑（YmapFile.cs）；
  - Sollumz：地形 4 层材质。
- **用户本机**（只读）：18 个原版 kt1 ymap 导出、La Puerta 的 build 和工具、用户记下的踩坑经验。

## 修改

`fivem-map-world-editor` 从约 300 字补成完整技能：
- `SKILL.md`：
  - 分流表、8 步流程；
  - 这个伺服器踩过的规则：遮挡体、hei_ 版本、索引和 numChildren、父实体只能埋到地下、SLOD2/3 要改模型、三份 ybn、BVH 超过 32767 面导出失败、|UV|<50、一个原版档只能由一个资源覆盖、分类资料夹名不能重复。
- 参考资料：
  - 新增 `codewalker-ymap`、`removing-vanilla`、`terrain-roads-water-paths`、`custom-exterior`、`troubleshooting`、`sources`；
  - 删掉旧的 `world-integration`、`acceptance`，内容已经并进新档。它们是 Sollumz 还不能直接处理 ymap 之前写的。
- `scripts/check_map_resource.py`（只读，只用标准库），共 23 个测试：
  - 检查 manifest 和跨资源覆盖；
  - ymap 范围和 flags（照 CodeWalker 源码移植）；
  - LOD 索引：照 CodeWalker 的 isroot 逻辑，并新增「索引错一格」侦测；
  - 用 `--orig` 和原版对比；
  - 检查 ybn、ydr、ynd 的 XML；
  - 也能直接读编好的二进制 ymap（共用 `fivem-prop-creator/scripts/rsc_probe.py`）。
- `fivem-asset-acceptance` 的 `asset_gate.py` 和 `checkers.md` 登记了地图检查脚本。

## 对照测试

题目是「在 Legion Square 删原版大楼后，后面的城市不见、远处还看得到旧楼，朋友的警局地图也改过同一块」。

| | 新版 | 旧版 |
|---|---|---|
| 通过 | 8/8 | 5/8 |

旧版的错误：
- 只写了笼统的 `.ybn`，漏了 `hi@` 和 `ma@` 碰撞，照做子弹还会打到旧楼；
- 没讲 CodeWalker 要先读到自己的 ytyp 才能算 extents，否则算出来是个很小的球；
- 把 LOD 的位置说错；
- 只拿两个资源互相比对重名，没扫整个伺服器。

评分代理建议加的三条（numChildren 要修、LOD 和 SLOD1 在哪个文件、CodeWalker 要开 DLC）已经补上。

## 在用户伺服器上发现的问题

只读，已记进记忆，没有修改：
- **kiiya_lapuerta（付费资源）**：
  - `kiiya_kt1_rd_veg.ymap` 的 52 棵树里有 44 棵 parentIndex 错一格，最后一棵超出列表；
  - `kiiya_kt1_rd_apt_ext.ymap` 有 12 个 HD 实体指向同级的 HD；
  - stream 里留着 2 个 .xml。
- molo_lspdhq 和 kiiya_lapuerta 都串流同名的 lodlights ymap，只有一个会生效。
- 4 个资源都有 `_manifest.ymf` 这个同名档，会不会冲突没有文档，标为未验证。
- streaming 范围过大：molo_lspdhq_building（lodDist 9999）、molo_davispd_exterior、La Puerta 的 `lpt_t3.ymap`。
- La Puerta 的 build 加 `--orig` 和原版对比：0 个错误。

## 未验证

- 引擎实际采用的 parentIndex 规则（目前用 CodeWalker 的解读）；
- `_manifest.ymf` 同名会不会冲突；
- BVH 面数上限（只有用户自己导出失败的经验）；
- ynd 格式没拿真文件测过；
- 只看过章节标题的影片内容；
- `RemoveIpl` 对常驻 ymap 无效。
