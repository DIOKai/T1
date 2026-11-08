# 各类别检查器（asset_gate.py 会自动调用）

全部是标准库、只读、`--json` 输出、有 error 就退出码 1、中文讯息。闸门用 `py -3 -I -X utf8 <检查器> <资源> --json` 跑（`-X utf8`：有些检查器没把输出改成 UTF-8，Windows 管道会报编码错）。JSON 形状不一样（`[...]` 或 `{"findings": [...]}`，位置字段叫 `file` 或 `resource`），闸门统一成 `{level, code, file, message, checker}`。

| 类型 | 怎么认出来 | 检查器 | 主要查什么 | 看不到的 |
|---|---|---|---|---|
| 道具 | stream 有 .ydr/.yft/.ydd，且不是车辆/武器/服装/ped | `fivem-prop-creator/scripts/check_prop_resource.py` | DLC_ITYP_REQUEST（只认文件名）、archetype ↔ 模型、二进制 YTD/YDR/YTYP（贴图格式/mip、LOD 面数、嵌入碰撞、lodDist、旗标、门属性）、XML 的 BVH 旗标 | yft 内部、二进制碰撞旗标 |
| 车辆 | vehicles/handling/carcols/carvariations meta 或 `_hi.yft` | `fivem-vehicle-mod/scripts/check_vehicle_resource.py` | meta 互相引用、modkit/警笛/灯光 id、16/48 MiB | 引擎舱、破洞、外观（LESSONS 人工） |
| 车辆涂装 | 同上（有就跑） | `fivem-vehicle-livery/scripts/check_livery.py` | livery 贴图存在、FLAG_HAS_LIVERY、_sign_N、各 LOD 有涂装层、贴图格式 | 涂装好不好看、字是否反 |
| 服装 | stream 名字有 `^` 或 SHOP_PED_APPAREL_META_FILE | `fivem-clothing-creator/scripts/check_clothing_resource.py` | 命名、meta、贴图配对、编号、FXAP | YDD/YMT 内容 |
| 地图/MLO | .ymap/.ymf、MLO ytyp（二进制也认得）、this_is_a_map + .ybn | `fivem-mlo-housing/scripts/check_mlo_resource.py` | manifest、MLO 规则（portal 朝向、房间）、ymap、重名、16/48 MiB | 二进制 ymap 内容 |
| 武器 | WEAPONINFO_FILE 等或 weapons*.meta | `fivem-weapon/scripts/check_weapon_resource.py` | meta 引用、配件、骨骼（XML）、ox_inventory | 手感、动画 |
| 动画 | .ycd（不属于车辆/武器）或 AnimationList*.lua | `fivem-animation/scripts/check_anim_resource.py` | ycd 头、clip hash、rpemotes 清单 | 动作好不好看 |
| 音效 | .awc、AUDIO_WAVEPACK、.dat*.rel（地图里的 .dat151.rel 是声音遮挡，不算） | `fivem-vehicle-sound/scripts/check_sound_resource.py` | data_file ↔ .rel、awc 头、8 字前缀、CREDITS | 音色、音量 |
| 画质包 | TIMECYCLEMOD_FILE、visualsettings.dat、timecycle xml、只有 .ytd 的贴图包 | `fivem-graphics-pack/scripts/check_graphics_pack.py` | timecycle 变量、manifest、16/48 MiB、ReShade | 画面效果 |
| 手机 App（`--ui`） | npwd / lb-phone / qb-phone 字样 | `fivem-phone/scripts/check_phone_app.py` | app 注册、NUI | 实际操作 |
| NUI（`--ui`） | `ui_page` | `fivem-menu-design/scripts/check_nui_menu.py` | ui_page/files、焦点、外部网址 | 好不好用 |
| 人物 ped | PED_METADATA_FILE 或 peds.meta | **没有** | — | 全部人工（fivem-ped-character） |

闸门自己再查：NO_MANIFEST、XML_IN_STREAM、SOURCE_IN_STREAM、NAME_CASE（空格=警告，只有大写=提示）、ASSET_OVER_16MIB/48MIB、ESCROWED、NO_PROVENANCE、CROSS_RESOURCE_DUPLICATE、STREAM_ENHANCED_PARTIAL。检查器已经报过同一个代码的，闸门那条不重复；两个检查器在同一资源报同一个文件的包装问题（例如地图 + 道具都报 DUPLICATE_ASSET），只留第一条。

找不到检查器时报 CHECKER_MISSING（涂装检查器是可选的，没有就安静跳过）；检查器出错/超时报 CHECKER_CRASHED，那个资源标“⧗ 未完成”，闸门退出码 2。

2026-11-08 在用户伺服器 `resources` 上只读跑的结果（160 个资源，88 个纯脚本跳过）：通过 16、警告 24、失败 32。失败多数是车辆 `.ytd` 超过 48 MiB（25 台）、kiiya_lapuerta 等 MLO 的 stream 里有 XML/重名文件、pillbox 用 DLC_ITYP_REQUEST 载入 MLO ytyp、cylex_animmenuv2 的 ytyp 通配符写错、wood_table_v2 贴图 64 MiB、lg81hcredeye 缺 `_amp.dat10.rel`。
