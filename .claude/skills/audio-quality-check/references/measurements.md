# 测量方法

先用 ffprobe 读取实际流：

```text
ffprobe -v error -show_streams -show_format -of json input.wav
ffmpeg -hide_banner -nostdin -i input.wav -map 0:a:0 -af astats=metadata=0:reset=0 -f null -
ffmpeg -hide_banner -nostdin -i input.wav -map 0:a:0 -af loudnorm=I=-23:TP=-2:LRA=7:print_format=json -f null -
```

以上 null 输出只解码/测量，不写归一化后的音频；loudnorm 参数用于本次分析调用，-23 不是 FiveM 标准。测量日志通常在 stderr，不按 stdout 空白认定失败或零值。选流、采样窗口与退出码要保留；未知音频/多音轨不能默认只有 0:a:0。

也可使用已导入 ffmpeg-skill 的 probe.py 或 loudness.py --measure-only；先查该版本 help。--dry-run 的测量工具仍可能实际运行 FFmpeg/ffprobe，不能承诺没有计算或文件读取。

astats 的峰值/Peak_count 与 true peak、LUFS 不同。silencedetect 的阈值/持续时间是显式检查参数，不是删音频指令。原始有意静音、长间隔和低声环境不能据此判坏文件。响度分析对静音可能返回 -inf；保留“无有效测量”而不是强行归一化。

来源：[ffprobe](https://ffmpeg.org/ffprobe.html)、[astats](https://ffmpeg.org/ffmpeg-filters.html#astats-1)、[loudnorm](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)、[silencedetect](https://ffmpeg.org/ffmpeg-filters.html#silencedetect)，核对日期 2026-10-17。
