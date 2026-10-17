---
name: audio-quality-check
description: Measure local audio streams, duration, sample rate, channels, levels and silence, then review clipping, loop and mix evidence against an explicit delivery contract. Use for audio QA without automatically normalizing or changing recordings.
---

# Audio Quality Check

先确定用途、目标格式/声道、响度合同、听音场景与输入范围。UI、车声、环境、对话和音乐不能统一套用社交平台 loudness 目标。原档和 ori 只读；本 Skill 默认测量与报告，修复另按用户任务范围执行。

1. 检查本地 ffmpeg/ffprobe 路径和版本；按 [measurements.md](references/measurements.md) 记录真实流、时长、采样率、布局、编码、大小、测量窗口与过滤链。缺流、解码失败或缺工具单独报告，不能写零问题。
2. 分清 sample peak、true peak、RMS、integrated LUFS、LRA 和静音；单位与时间范围一起报告。短促 SFX、全静音或极短录音可能没有稳定 LUFS/LRA，-inf/缺字段不是可随意填零的数值。
3. 按 [review-and-fixes.md](references/review-and-fixes.md) 结合波形/试听判断爆音、失真、底噪、DC、相位和循环脉冲。峰值碰到满刻度仅是削波线索，降低音量不能恢复已经削掉的细节。
4. 对比输入/输出的目标格式、时长、声道与测量结果；采样率改标记不算真正重采样。真峰或 LUFS 达标也不能证明素材来源、游戏兼容或听感通过。

交付测量表、工具/参数、定位、可确认问题及未完成试听/目标运行项。不要为了“过检”改门槛、删静音、强制单声道、降噪或统一加大音量。
