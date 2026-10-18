# 本机 SVG Creator 接入

上游脚本为 Linux 容器编写，写死 /home/claude 与 /mnt/user-data/outputs，并会在缺 CairoSVG 时调用带 --break-system-packages 的 pip。Windows 上不直接运行这条路径，也不为满足原命令创建这些目录或改全局 Python。

在本机执行时，以本说明替代容器专用 helper 命令：保留输入，在用户指定的新输出目录写 SVG；选择已可用的浏览器或 SVG 渲染器生成预览，实际查看后修改，再确认最终 SVG 与预览来自同一版本。若只有源码检查能力，交付候选并明确“视觉验收未完成”，不能把脚本计数当作已经看过图片。依赖缺失则说明缺口，安装需纳入用户当前任务范围，不自动改系统环境。

本批只安装并检查格式/语法，没有运行原 svg_loop.py、安装 CairoSVG 或验证任何设计成品。原辅助脚本保留供合适的宿主使用。
