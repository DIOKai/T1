# OCR、语音、可观测性与交付检查补充

整理日期：2026-10-17。本批仅新增文件，原有 Skill、模型清单、Claude/Codex 配置均不覆盖。dicksick 内 Skill 从 23 个增至 29 个。

| Skill | 来源 | 用途 |
|---|---|---|
| [document-ocr](.dsh/skills/document-ocr/SKILL.md) | 新编写 | 文档识别、页面追溯、表格及数字核对 |
| [local-speech-workflow](.dsh/skills/local-speech-workflow/SKILL.md) | 新编写 | 本地转写、时间戳、朗读及应用音频流程 |
| [opentelemetry-skill](.dsh/skills/opentelemetry-skill/SKILL.md) | 固定提交导入 | traces、metrics、logs、Collector 与 AI 代理观测 |
| [accessibility-check](.dsh/skills/accessibility-check/SKILL.md) | 新编写 | axe/Playwright、键盘、焦点、动态内容检查 |
| [offline-sync](.dsh/skills/offline-sync/SKILL.md) | 新编写 | 持久化 outbox、幂等、冲突及账号隔离 |
| [release-package-check](.dsh/skills/release-package-check/SKILL.md) | 新编写 | 交付清单、必需文件与只读哈希核对 |

## 来源与学习

- [学习资料索引](learning/ocr-voice-monitoring-2026-10-17.md)：官方文档、GitHub 与补充视频线索；视频仅核对元资料，不称已完整观看。
- [来源记录](SOURCES-ocr-voice-2026-10-17.json)：固定上游提交、文件来源和验证范围。
- [语音模型候选](models/voice-candidates-2026-10-17.json)：Qwen3-ASR-0.6B-hf 与 Qwen3-TTS-12Hz-0.6B-CustomVoice；仅登记，未下载、加载或启用。

OpenTelemetry 来源为 o11y-dev/opentelemetry-skill，提交 `6d46bedb3df706f26321fbd53fe73e0204611482`。保留 LICENSE、所有 references 和入口所需示例；入口仅追加 T1 宿主说明链接，其他上游字节保持一致。仓库说明、CI 与插件配置未纳入 Skill 包。

其余 5 个按 Skill Creator 原则独立编写并附任务相关参考。OCR 与 a11y 现成候选已评估，因平台/宿主约束与范围不合适，没有直接复制或冒称上游版本。

## 验证范围

发布清单脚本使用合成目录通过 22 项测试；链接/reparse、并发变化与部分读取错误采用模拟。6 个 Skill 另做格式、UI 元数据、引用闭合、Python 语法及导入来源校验。

没有执行真实 OCR、语音推理、遥测服务、浏览器无障碍、移动端同步、DSH 运行时或独立代理行为测试。Skill 文件可供宿主读取，不代表所有运行依赖已安装或宿主会自动发现。没有启用收费 API、云导出、麦克风或全局 Skill 安装。
