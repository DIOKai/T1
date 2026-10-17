# 播放与验收

按目标 Cfx Native Reference 核对实际采用的 REQUEST_SCRIPT_AUDIO_BANK、PlaySoundFromEntity/Coord/Frontend、StopSound 和 ReleaseSoundId；银行/声名、加载参数与 networked 行为按所选 native 和资源版本查证，不从另一个封装猜签名。释放 ID 不等同停止播放，停止和释放的责任分别明确。

resource stop、玩家退出/切换、实体删除和超出范围都要有预期行为；并发声音数量有边界，银行加载失败要限时结束/报告，不无限等待。不要每帧重复请求同一声音或在两条网络路径重复触发。

服务端验证请求者权限、允许的声名/事件、位置/实体和频率；客户端仅提供意图，不能让任意客户端指定全服声音或无限大范围。原生 API 的 networked 参数不代表服务端业务权限已经通过。两客户端试听还要检查附近/远处、重入范围、所有权变化和延迟。

引擎声按怠速、升降转速、负载/收油、换挡、驾驶舱/车外及停熄测试；脚本 SFX 按触发、结束/停止、叠加和音量设置测试。源 WAV 的“无缝”不能证明打包后游戏混音无脉冲或失真。

来源：[Cfx Native Reference](https://docs.fivem.net/natives/)、[事件安全](https://docs.fivem.net/docs/developers/server-security/)。实际游戏测试仍必须记录目标构建与结果，不能把文档示例当作运行证据。

已核对的官方源定义：[RequestScriptAudioBank](https://github.com/citizenfx/natives/blob/master/AUDIO/RequestScriptAudioBank.md)、[StopSound](https://github.com/citizenfx/natives/blob/master/AUDIO/StopSound.md)、[ReleaseSoundId](https://github.com/citizenfx/natives/blob/master/AUDIO/ReleaseSoundId.md)。银行请求文档注明新版构建有额外 playerBits 参数，应核对目标绑定，不能把旧签名复制成所有版本通用封装。
