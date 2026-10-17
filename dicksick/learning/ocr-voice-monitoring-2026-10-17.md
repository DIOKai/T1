# Dicksick 下一批 Skill 学习资料索引

检索与内容核对日期：2026-10-17。使用 Skill Installer 查找候选，按 Skill Creator 的范围、依赖和可验证性标准筛选。此索引记录前一轮研究结果；本批据此导入或新建 6 个 Skill。候选内容审阅与实际运行验证分开，详见本批来源记录。

## 1. 文档 OCR

- [DeepSeek-OCR-2 官方源码](https://github.com/deepseek-ai/DeepSeek-OCR-2)：优先看安装环境、推理示例、PDF处理与输出形式。补充 Skill 应要求页面追溯、表格单位保留、缺失识别与OCR结果核验。
- [官方模型卡](https://huggingface.co/deepseek-ai/DeepSeek-OCR-2)：按所选版本核对依赖、授权及设备。
- [现成 OCR Skill 候选](https://github.com/hec-ovi/ocr-skill/blob/main/SKILL.md)：当前入口为ocr，MIT，自带CLI与后端合同，但包含.noob路径和必须使用其CLI的强约束；README描述musl二进制。不能直接假定Windows可运行。其未提供路径就扫描全部图片/PDF的规则不适合直接继承，应缩小到用户授权范围。仅作为结构/接口参考，未安装或执行。

## 2. 语音输入与朗读

- [Qwen3-ASR 官方源码](https://github.com/QwenLM/Qwen3-ASR)：学习离线/流式识别、长音频和时间戳；不同后端能力分别核查。
- [Qwen3-TTS 官方源码](https://github.com/QwenLM/Qwen3-TTS)：区分CustomVoice、VoiceDesign和Base，按具体检查点选择接口，不把整个家族能力套到每个尺寸。
- [ASR Transformers原生检查点](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf)。
- 未来 Skill 重点是格式/采样率、分段、取消、音频权限与错误、文字/时间戳对齐和实际播放验收。未找到已完整审查、可直接替代这个流程的通用Skill；本轮不声称不存在其他候选。官方仓库也有云API示例，免费路线只参考本地实现，不自动启用云服务。

## 3. AI运行监控

- [OpenTelemetry Python入门](https://opentelemetry.io/docs/languages/python/getting-started/)：先学习trace/span、metrics、logs与本地输出。
- [OpenTelemetry Collector文档](https://opentelemetry.io/docs/collector/)：之后再学接收、处理、导出与配置验证。
- [OpenTelemetry Skill候选](https://github.com/o11y-dev/opentelemetry-skill)：入口及参考结构已核对，metadata标Apache-2.0。覆盖Collector、SDK、脱敏、采样与AI代理。优先候选；导入时固定提交并保留完整参考/许可证，按实际部署版本核对。包含云和多宿主配置例子，并不代表要启用收费后端或用户遥测。
- 目标能力：识别延迟、错误、重试和用量来源，默认不采集原始Prompt/回答/密钥；内容采集须单独匹配数据范围。

## 4. 无障碍检查

- [Playwright官方无障碍测试](https://playwright.dev/docs/accessibility-testing)：学习axe集成与自动检查的边界，配合键盘和实际页面状态验证。
- [a11y-audit候选](https://github.com/kylane/a11y-audit)：入口已读取，覆盖静态、axe、键盘和读屏等模式。入口很长，依赖Playwright MCP及部分Claude工具，并包含更新检查。更适合作为参考或经过精简的改编候选，不宣称可直接在DSH运行。
- 自动扫描通过不能等同完整WCAG合规；不要复制候选中未经项目确认的通过阈值或全自动修复流程。

## 5. 离线数据与同步

- [Expo SQLite官方文档](https://docs.expo.dev/versions/latest/sdk/sqlite/)：学习持久化、事务、参数绑定和迁移。
- [已收录的离线/取消参考](https://github.com/DIOKai/T1/blob/main/dicksick/.dsh/skills/expo-data-fetching/references/offline-and-cancellation.md)：已有网络状态与请求暂停/取消示例，不需要重新复制同一基础能力。
- 后续真正需要补充：持久化outbox、幂等提交、同步冲突、账号切换隔离、删除与版本迁移、重启/断网/恢复场景。SQLite存储本身不自动提供完整同步。
- [TanStack Query取消说明](https://tanstack.com/query/latest/docs/framework/react/guides/query-cancellation)：对照安装版本及是否消费AbortSignal核验；现有参考中“自动取消”的注释不能作为所有请求自动被中断的保证。本次未改原文件。

## 6. 发布包与依赖检查

- [Changesets官方入门](https://github.com/changesets/changesets/blob/main/docs/intro-to-using-changesets.md)：学习版本与变更说明；更适合包/monorepo场景，不是所有项目的强制依赖。
- [npm pack文档](https://docs.npmjs.com/cli/v11/commands/npm-pack/)：学习实际打包清单、dry-run与脚本开关，核对本地CLI版本。发布前检查不等于执行publish。
- 后续独立Skill应覆盖构建资源、依赖/锁文件、许可证、密钥遗漏、版本与校验和，并区分检查、打包与发布权限。优先写适合T1用途的轻量检查流程，避免导入绑定特定语言或产品的自动发布Skill。

## YouTube辅助学习

只核对到搜索元数据、作者、发布日期、简介/章节，未取得完整字幕或逐帧观看。下面仅供选看，技术规则仍以上述官方资料为准。

| 视频 | 日期/作者 | 适合学习 | 边界 |
|---|---|---|---|
| [DeepSeek-OCR 2 Guide](https://www.youtube.com/watch?v=4H0Ozgq75Gc) | 2026-01-27，Byte Goose AI. | 实现与架构概览 | 简介含微调与对比宣传，不作为性能结论依据 |
| [Qwen3 ASR ComfyUI](https://www.youtube.com/watch?v=aW2VmmSkWcM) | 2026-02-11，AxiomGraph | 音频转写与字幕流程 | ComfyUI流程，与直接API/SDK接入不同 |
| [React Native Expo: Offline Data Storage with SQLite](https://www.youtube.com/watch?v=vgPdAARd6Gw) | 2024-12-10，Aaron Saunders | SQLite CRUD入门，10:00起进入SQLite | 教程较旧，接口按当前Expo SDK核对；CRUD不等于同步冲突处理 |

## 下一步适合采用的方式

优先完整审查OpenTelemetry Skill；OCR与无障碍候选经过宿主/权限适配再考虑导入。语音、持久化同步和发布检查依据官方源码编写独立流程。所有来源固定版本并保留授权；静态阅读不等于安装、兼容性或运行验收。
