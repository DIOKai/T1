# 武器、涂装、警笛、道具和上服验收

日期：2026-11-08。用户问「还有什么要添加的吗」，从列出的缺口里选了全部五项。地图编辑另开 PR 合并。

## 资料

四个子代理分头调研武器、涂装、地图编辑、道具和验收：
- **影片**：只抓原语言字幕（不抓自动翻译，避免被 YouTube 限流），请求之间停顿。武器 22 部、涂装 13 部、道具 15 部。中途仍被限流，没达到每项 20 部的目标；缺的内容都记在各技能的 sources 里。
- **第一手资料**：用 CodeWalker.Core 只读导出原版档案核对。
  - 武器 26 把；
  - 涂装：police、polgauntlet、tornado5、ambulance、firetruk 等；
  - 道具约 50 个；
  - 声音：游戏 `audio_rel.rpf` 里的 dat54。
- **源码和文档**：FiveM 源码（LoadStreamingFile.cpp 等）、Sollumz 2.9 文档和源码、docs.fivem.net、ox_inventory 2.48 源码。都只读。

警笛由主会话自己做，拿用户 10 月做的 `lore_sirens` 包对照验证。

## 新增

- `fivem-weapon`：
  - Blender 建枪；
  - 原版骨骼和挂点：Gun_Root、WAPClip/WAPScop…、配件根骨骼 AAP*；
  - 武器没有 ytyp（archetype 写在 weaponarchetypes.meta），外置 ytd，普通 ydr 加 `_hi.ydr`；
  - 各个 meta 和 data_file 顺序，接 ox_inventory（AttachPoints 和 Components 两边都要写），伺服器判定；
  - 附 `check_weapon_resource.py` 和 27 个测试。
- `fivem-vehicle-livery`：
  - 三种做法：`_sign_N` 加 FLAG_HAS_LIVERY；VMT_LIVERY_MOD（2023–25 原版警车的做法）；画死在车身；
  - 涂装层是 `DiffuseSampler2` 读 UV1；
  - 左右侧可能被转了 180°/90°，不一定只是镜像；
  - 在 4096 上画、导出 2048 DXT5 带 mipmap；
  - 附 `livery_template.py`（不用 Blender，从 yft XML 画 UV1 模板）、`check_livery.py`，共 12 个测试。

## 修改

- **`fivem-vehicle-sound`**：新增 `references/siren-sounds.md` 和 `scripts/siren_pack.ps1`（建立或导出警笛声包）。
  - **发现**：CodeWalker 照写的大小写算名字 hash，游戏却用小写名字的 hash。原版 dat54 里只有小写 hash，已核对。
  - 所以用户 10 月做的警笛包（名字是大写）装上去会完全没声音。新工具一律小写，建完还会自我检查。
  - 用新工具重建的 `federal.awc` 跟 10 月那份逐字节相同；设定档里除了名字 hash，其余都一样。
  - 测试时也更正了一个说法：CodeWalker 导入 XML 时会自动把 SoundSet 条目照 hash 排序（已实测）。
- **`fivem-prop-creator`**：
  - 重写技能，加上原版实测预算（手持 64–440 面，街道家具 600–2,300 面并有 Medium LOD）；
  - flag：要能推动就开 Dynamic，Static 只给 MLO 家具；
  - DLC_ITYP_REQUEST 只认档名；
  - 门的 special attribute（Cfx 网页把 Benny's 门写成 5，实际是 10）；
  - 附 `rsc_probe.py`（只用 Python 自带模块读编好的 ydr、ytd、ytyp）和 `check_prop_resource.py`，21 个测试。
- **`fivem-asset-acceptance`**：
  - 重写成五步上服闸门；
  - 附 `asset_gate.py`：自动判断素材类型，跑对应的检查脚本（MLO、服装、车辆、声音、动画、手机、NUI、画质包、道具、武器、涂装），再加上跨资源检查（加密档、来源说明、重名、16/48 MiB），10 个测试；
  - 加密档案改成警告，默认就显示。
- **`fivem-mlo-housing/check_mlo_resource.py`** 修两个 bug：
  - DLC_ITYP_REQUEST 改成只按档名比对，rpemotes 那种档放子资料夹的写法不再误报；
  - 门的类型补上 9、10、12。
- **`fivem-vehicle-mod`**：加上指向涂装技能和警笛参考资料的连结。

## 对照测试

| 测试 | 新版 | 对照 | 对照的主要错误 |
|---|---|---|---|
| 三八式 add-on，背包有、手上看不见 | 9/9 | 无技能 6/9 | 说 `_hi.ydr` 可有可无、贴图嵌进去就不用 ytd（会隐形）；骨骼名漏写；meta 格式错 |
| 四套警笛装上去没声音 | 6/6 | 旧版 5/6 | 要求样本数一定要偶数（补静音会让每圈循环多一个空隙）；对照组自己读源码，也找到了大小写的原因 |
| LSCSO 两套涂装（糊、只有一边） | 9/9 | 无技能 6/9 | 说 vehicles.meta 不用改（其实要 FLAG_HAS_LIVERY）；+hi.ytd 放 4096 来修模糊；没讲 UV1 |
| 木桌看不到、推不动 | 8/8 | 旧版 5/8 | 说 flags 0 是对的（其实要 Dynamic）；只算到 16 MiB 警告线；lodDist 200 照留 |
| 买来的包上服验收 | 8/8 | 旧版 3/8 | 建议在正式服先关玩家来测；没查贴图格式和碰撞；没讲授权不能转发 |

评分代理指出部分标准太松或分不出高下，已改严或加条，留给下一轮用：武器 4 条，涂装 3 条，警笛 3 条，道具 2 条，验收 3 条。

## 检查时在用户伺服器上发现的问题

都只读、没有修改，已回报用户，也记进记忆：
- 10 月的 `lore_sirens` 警笛包名字是大写 hash，要重建才会响。
- 涂装：
  - 3 台车的涂装贴图在贴图档里找不到（18CDemonTT、CChallengerBLF、camaro18bb），gonzo_sierra24 同样；
  - 6 台车开了 FLAG_HAS_LIVERY，车身却没有涂装层；
  - 4 台车有 `_sign_1` 却没开 FLAG_HAS_LIVERY；
  - 有几台留着没删的草稿贴图。
- 道具：wood_table_v2 贴图没压缩，64 MiB，超过 48 MiB；wood_table 32 MiB。
- cylex_animmenuv2：
  - DLC_ITYP_REQUEST 的通配符写错，什么都匹配不到；
  - 请求的 badge1.ytyp 不存在；
  - 有 16 组重复的 archetype。
- pillbox：用 DLC_ITYP_REQUEST 载入 MLO 的 ytyp（v_int_40），照这个伺服器的规则可能闪退。
- 25 台警车的 ytd 超过 48 MiB。照 1:1 规则只报告。
