# 样本与环绕接缝

记录采样率 Fs 和整数样本边界；秒到样本的取整策略明确，左右声道用同一边界。实际重采样会改变样本；仅改采样率元资料会改变播放速度/音高，不是透明转换。

同一循环的尾端与头端要同时比较幅值、斜率、相位、频谱/能量和背景变化。单点接近零不能证明接缝无感。正相关信号做等功率淡化可能叠加偏响，反相又可能抵消；曲线和交叠长度由素材、试听及测量决定，不固定套用几十毫秒。

制作环绕淡化时明确剪去/重叠哪一段、输出周期及再次重复的接点；不要把带起始淡入/末尾淡出的文件当成无缝循环，它可能每周期“呼吸”。用于播放器 loop markers 时记录 marker 是否真的被目标格式和游戏工具保留；普通 WAV 可播放不表示下游采用 loop 元数据。

转速层需要在相近声学条件下校准，兼顾 on-load/off-load、引擎/排气和驾驶舱/车外视角（按资源实际结构）。跨层过渡与单文件首尾是两种不同验收，不能互相替代。

依据：[FFmpeg acrossfade](https://ffmpeg.org/ffmpeg-filters.html#acrossfade)、[atrim](https://ffmpeg.org/ffmpeg-filters.html#atrim)、[aresample](https://ffmpeg.org/ffmpeg-filters.html#aresample)，核对日期 2026-10-17；这些是工具机制，不是 FiveM 固定参数标准。
