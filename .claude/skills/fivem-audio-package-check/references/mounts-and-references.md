# 挂载与名称

以 [Cfx data_file 类型](https://docs.fivem.net/docs/game-references/data-files/) 和 [manifest](https://docs.fivem.net/docs/scripting-reference/resource-manifest/) 核对挂载。常见 AUDIO_WAVEPACK 指波形包目录，AUDIO_SOUNDDATA / AUDIO_GAMEDATA 对应不同音频元数据；仅按当前格式/工具输出需要声明，不能给所有 SFX 强加引擎用的整套文件。

Cfx 示例中 game.dat151.rel 与 sounds.dat54.rel 表示不同数据类型。不要颠倒它们，也不能凭数字后缀证明二进制内容正确。某些 mounter 的声明使用逻辑路径/省略后缀，先查实际解析约定，不把声明字符串与磁盘文件名直接一比就判缺失。

核对从播放的 sound/soundset 或车辆音频标识，到 REL 内部条目、容器/波形引用、AWC 和挂载目录的链路；外部文件名一致不意味着内部哈希/引用一致。复制新包应按工具支持的结构改名并重建，不能仅改文件名或全局文本替换。

跨资源同名银行/标识、错误启动依赖、旧缓存或依赖没有加载可能造成静音；分别列证据，不默认清空玩家缓存。不要改名、替换已有公共声音或压缩原素材来“修复”。

实现参考：[CodeWalker](https://github.com/dexyfex/CodeWalker)、[AWC 数据结构](https://github.com/dexyfex/CodeWalker/blob/master/CodeWalker.Core/GameFiles/FileTypes/AwcFile.cs)。源代码可帮助理解格式，不能取代选定工具版本的实测或授权来源。核对日期 2026-10-17。
