# 工具与证据

独立本地 FFmpeg 流程可以先生成两个片段的衔接样例：

```text
ffmpeg -hide_banner -nostdin -n -i first.wav -i second.wav -filter_complex "[0:a:0][1:a:0]acrossfade=d=0.05:c1=tri:c2=tri[a]" -map "[a]" -c:a pcm_s16le new-transition.wav
```

0.05 秒只是演示值，不是默认验收标准。先确认两段长度足够、采样率/布局及目标要求；交叠模式下输出期望时长约 A+B-d，以解码后的样本数核对。这个命令只处理两段衔接，不会自动造出首尾平滑的循环单元。PCM 导出也不代表源录音没有有损压缩。

在输出副本生成重复试听片段，特别检查每次尾到头边界。数值记录可包括切点幅度差、局部 RMS 和峰值；它们不是统一的可闻性分数。最终格式改变、重采样或压缩之后再复验。

使用 [Audacity](https://www.audacityteam.org/) 时保存项目/导出路径与选择范围，不能覆盖原始录音。导出后用 [ffprobe](https://ffmpeg.org/ffprobe.html) 核对流、时长、声道和采样率。没有音频播放/听觉审查能力时明确缺口；不要仅凭 ffmpeg exit0 宣称“无接缝”。
