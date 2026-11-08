# 包装、加密与来源

## 包装

对照 [Cfx Resource Manifest](https://docs.fivem.net/docs/scripting-reference/resource-manifest/) 检查实际资源类别所需的 data_file、files、依赖与加载入口；不是所有 stream 文件都要写进 files，不套用万能 manifest。

- 一个资源一个文件夹，`fxmanifest.lua` 有 `fx_version` 和 `game 'gta5'`（`__resource.lua` 是旧格式）。
- 游戏二进制放 `stream/`（任意深度）；同时支持 Enhanced 时放 `stream_enhanced/`——Cfx legacy-vs-enhanced 文档：有 `stream_enhanced` 时 Enhanced 版**只载入它、不载入 stream**，所以 Enhanced 需要的文件都要在里面。
- `.meta`、`.dat*.rel` 这类数据文件放 stream 外面，用 `data_file` + `files {}`；写错类型会被忽略（控制台 “Could not add data_file … invalid type”）。
- stream 里不该有：`.xml` 导出（不会被加载）、`.blend/.fbx/.obj/.psd/.dds/.png/.tga` 源文件和散装贴图、`Thumbs.db`、`desktop.ini`。XML 和游戏二进制不同；改扩展名不是转换。
- 地图 / 道具：`this_is_a_map` 只负责重载 ymap（FiveM ResourcesTest.cpp）；`DLC_ITYP_REQUEST` 只按文件名找 ytyp（LoadStreamingFile.cpp），可以给道具用，**不能给 MLO 的 ytyp 用**（这个伺服器上会闪退，交给 .ymf）。
- 名字：小写、不要空格；同一个 stream 文件名只能有一份（两个资源都串流同名文件时只有一个生效）。archetype / 模型名加项目前缀；改装套件、警笛、灯光 id（车辆检查器）、服装 collection（服装检查器）、声浪包 8 字前缀（声浪检查器）不能撞。
- 大小：FXServer 按 RSC 头算每个文件的虚拟和物理内存（`ConvertRSC7Size`）：> 16 MiB 警告，> 48 MiB “Oversized assets can and WILL lead to streaming issues”（ResourceStreamComponent.cpp）。磁盘上的大小是压缩过的，会低估。只报告；要不要压缩由用户决定。

先列清单再操作；不要为了“清理”删掉不认识的文件。

## 加密（Cfx Asset Escrow）

- 支持 Lua、YFT、YDD、YDR（[asset-escrow 文档](https://docs.fivem.net/docs/server-manual/asset-escrow/)；YTD、YCD、YTYP 不加密）。`escrow_ignore {}` 里的文件保持明文。
- 认法：资源根目录有 `.fxap`；被加密的 stream 文件开头 4 个字节是 `FXAP`，不是 `RSC7`（在用户电脑上只读看过：`cfx_onx_mp_faces` 的 .ydd；`busmods-stream` 有 .fxap 但 .ycd 是明文）。
- 只能在拥有授权的 Cfx 帐号的伺服器 key 上跑，否则 “You lack the required entitlement”。加密素材只能经 Tebex 包发放，不能转给别的帐号。
- 验收时：加密部分的内容、大小、LOD、碰撞都列“未验证”，靠游戏内测试。不解密、不找破解工具。其他检查器把 FXAP 文件报成 NOT_RSC7 时，闸门会把它改算成 ESCROWED。

## 来源与授权

每个资源根目录放一个 `CREDITS.md`（或 `SOURCE.txt` / `LICENSE`），闸门找不到就报 NO_PROVENANCE：

```
素材：<名字>
作者：<作者 / 店铺>
来源：<网址>（下载日期 2026-xx-xx）
授权：<CC0 / CC BY 4.0（需署名）/ 购买授权，只限本伺服器 / 不明>
转换：<工具和版本>，原档 SHA-256 <哈希>，1:1 未压缩
备注：<Hunyuan3D 生成（欧盟/英国/韩国不适用）/ 含游戏音频，只能自用>
```

- 工具开源不代表用它导入的模型也开源。只有下载链接或写“免费”而没有明确授权的，不能说可以再发布。只审查，不代为下载、重新打包或上传。
- 1:1 复制的模型/贴图要比对源和成品的哈希；合法的格式转换则记录来源 → 成品的对应关系和改动原因，不能宣称转换后哈希仍一样。

## 检查器的范围

二进制内部只能用适当工具、导入导出和游戏验证确认。沿用各类别检查器时先看它的说明（参数、只读），结果只代表它覆盖的范围，不升级成整包认证。见 checkers.md。

来源：[Sollumz 官方文档](https://docs.sollumz.org/)、[CodeWalker 源码](https://github.com/dexyfex/CodeWalker)、[Enhanced 资产转换](https://docs.sollumz.org/tutorials/asset-conversion-for-gtav-enhanced.md)、citizenfx/fivem `ResourceStreamComponent.cpp` / `LoadStreamingFile.cpp` / `ResourcesTest.cpp`、fivem-docs `developers/legacy-vs-enhanced`、`server-manual/asset-escrow`。核对日期 2026-11-08；执行时对照实际安装版本。Enhanced 教程里的单机 OpenRPF/ASI 步骤不等于 FiveM 资源部署，不据此替玩家装插件。
