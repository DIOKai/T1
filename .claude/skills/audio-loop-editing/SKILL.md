---
name: audio-loop-editing
description: Prepare and verify local engine, mechanical or ambience audio loops using sample-aware cuts, phase and level checks, wrap transitions and repeated playback. Use for cyclic seam repair; simple repetition or a video loop command is not seamless audio design.
---

# Audio Loop Editing

确认输入范围、来源授权、用途、目标周期、RPM/负载（若适用）、声道、实际采样率和游戏/播放器。保留原档和 ori；派生文件只写明确的新路径。先 probe 和试听代表性片段，再选切点，不批量覆盖素材。

## 制作与核验

1. 挑相对稳定的音色/转速区域，区分稳态循环与点火、熄火、换挡、放炮等一次性事件。不同 RPM、发动机/排气及负载层分别记录，不能把任意录音拉长就称真实引擎模型。
2. 按 [sample-and-wrap.md](references/sample-and-wrap.md) 确定切点、周期和处理方式。声道一起剪切；零交叉只是一条线索，相位、斜率、能量和音色变化仍会产生可闻接缝。
3. 用实际可用的 Audacity 或本地 FFmpeg 做任务所需的裁切/环绕交叉淡化。查安装版帮助和 [tools-and-evidence.md](references/tools-and-evidence.md)；缺依赖时说明未执行，不自动安装。ffmpeg-skill 的 loop.py 是视频重复工具，且不修接缝，不能拿来处理纯音频循环。
4. 对最终循环单元的尾到头边界验证；跨两段淡化成功并不证明新文件首尾可重复。报告交叠消耗的样本与实际输出长度，不假定输入输出时长不变。
5. 重复播放多个周期，在切点前后、耳机/扬声器及目标游戏负载下核对点击、能量凹陷、周期脉冲、相位抵消和转速过渡。数值、波形和试听各自列证据；没有实际听过就标“试听未完成”。

输出切点/循环点的时间与样本坐标、处理参数、格式、前后对比及未验证项。音频合成输出可用于试验，不能代替真实车声来源或游戏内引擎映射验证。
