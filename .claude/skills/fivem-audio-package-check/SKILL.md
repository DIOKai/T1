---
name: fivem-audio-package-check
description: Inspect staged FiveM audio resources for manifest mounts, AWC and REL references, sound identifiers, name conflicts and playback lifecycle evidence. Use for engine or scripted SFX packaging and silence troubleshooting; source WAV presence is not a compiled audio-bank test.
---

# FiveM Audio Package Check

确认资源类别（原生引擎声、脚本 SFX、NUI 音频或语音）、目标 Legacy/Enhanced、构建、依赖和已有播放路径。Qbox 负责玩法/权限接入，不取代 GTA 音频银行。只读检查交付副本，不改 ori、车辆原档或现有银行。

1. 按 [mounts-and-references.md](references/mounts-and-references.md) 核对 manifest 与实际文件、内部声名/容器名、扩展名解析规则、大小写和跨包冲突；不能只靠文件名齐全判银行有效。
2. WAV/MP3 素材、AWC 波形容器与 REL 元数据是不同对象。记录转换工具、版本、来源映射和错误。只有受支持的工具实际解析内部结构后才能报告内部引用；未解析的二进制、escrow 或缺工具部分标未验证。
3. 按 [playback-and-acceptance.md](references/playback-and-acceptance.md) 区分客户端播放、网络传播与服务端业务授权，核对银行加载、sound ID、停止/释放与实体生命周期。原生播放与 NUI 的音量/空间/清理方式按实际实现，不互相套用。
4. 目标测试服验证启动、F8/控制台、实际声源/驾驶视角、近远距离、负载/RPM（引擎声）、两客户端及 resource stop/restart。仅获文件审查授权时交付步骤和待测项，不执行服务器命令。

输出文件/引用清单、确认错误、潜在冲突与未验证项。没有真实银行解析、播放与多人验证，不称引擎声音制作完成或可正式上服。源音频处理另由循环编辑/质量检查承担。
