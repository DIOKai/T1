# 本地音频处理与 FiveM 音频检查

2026-10-17：只新增四个 Skill 与本批说明。既有 `.agents/skills -> ../.claude/skills` 继续供 Codex 与 Claude 共享，不改变链接、旧 Skill、原始素材或 ori。

| 新 Skill | 用途 | 来源 |
| --- | --- | --- |
| [ffmpeg-skill](../../.claude/skills/ffmpeg-skill/SKILL.md) | 本地探测、裁切、拼接、格式转换与测量 | MIT 上游固定版本 |
| [audio-loop-editing](../../.claude/skills/audio-loop-editing/SKILL.md) | 循环切点、环绕淡化、相位与重复边界 | 本批原创 |
| [audio-quality-check](../../.claude/skills/audio-quality-check/SKILL.md) | 格式、峰值、响度、静音和听音证据 | 本批原创 |
| [fivem-audio-package-check](../../.claude/skills/fivem-audio-package-check/SKILL.md) | AWC/REL、manifest、引用和播放生命周期 | 本批原创 |

导入 [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) 固定提交 `11a70aa680c0916581164dc49957a1b64ec57a79`：保留 MIT LICENSE、全部 Python runtime、模板、入口参考与可选 MCP transport，共复制 74 个文件。除新增副本的 SKILL.md 收窄描述并追加宿主说明链接，其余复制文件逐字匹配上游；原上游仓库不变。新增接入参考与 UI metadata。没有复制演示媒体、上游开发配置或 npm 安装器，没有注册 MCP、安装字体、ASR 或修改全局设置。FFmpeg/ffprobe 使用本机已存在的版本，不打包二进制。

上游 loop.py 要求视频且不平滑接缝，不是纯音频无缝循环工具。精确音频裁切显式使用 --accurate，纯拼接使用 --transition none。游戏音效的响度、声道与采样率按素材用途和目标合同决定，不套用社交平台标准。

## 验证

14 项真实本地 FFmpeg/ffprobe 与导入脚本测试通过：单/双声道探测、中文路径、损坏输入、响度测量、全静音、归一化后复测、已有输出保护、精确裁切、纯拼接、视频 loop 拒绝纯音频、交叉淡化样本数、样本裁切与满幅测量。只使用合成 WAV；每个场景核对输入 SHA-256 与修改时间保持不变。

四份 Skill 格式、UI metadata、全部导入 Python 语法、本地 Markdown 引用和上游内容/模式已核对。另有一次独立代理离线任务演练；不是对照基准测试。未进行真人试听、AWC/REL 编译解析、游戏服、真实车声、全部视频、字幕、MCP 或 ASR 验证，不能据此宣称音效已完成游戏验收。

参见 [来源及验证记录](audio-four-2026-10-17.sources.json)。
