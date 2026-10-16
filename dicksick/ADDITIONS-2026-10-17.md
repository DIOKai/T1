# Dicksick 补充包 — 2026-10-17

本批仅新增文件，保留原17个Skill、20个模型记录以及所有既有配置。当前本目录合计23个Skill；新增模型资料为3个权重候选与2个API后端索引。

## 新增Skill

| Skill | 用途 | 来源 |
|---|---|---|
| [deepseek-api](.dsh/skills/deepseek-api/SKILL.md) | 协议、缓存、SDK/网关差异和架构资料 | 本任务独立编写，补充已有app-integration |
| [promptfoo-evals](.dsh/skills/promptfoo-evals/SKILL.md) | 固定题目、断言和回归评测 | Promptfoo上游导入，加宿主说明 |
| [promptfoo-provider-setup](.dsh/skills/promptfoo-provider-setup/SKILL.md) | 评测连接、响应解析与本地OpenAPI辅助 | evals的配套依赖，保留内置YAML解析器及许可证 |
| [webapp-testing](.dsh/skills/webapp-testing/SKILL.md) | 本地网页测试、截图、日志 | Anthropic上游导入，加Windows/宿主说明 |
| [rag-document-pipeline](.dsh/skills/rag-document-pipeline/SKILL.md) | 文档、分块、检索、重排、引用与更新 | T1新编写 |
| [harness-skill-compatibility](.dsh/skills/harness-skill-compatibility/SKILL.md) | DSH发现路径、工具/依赖和迁移检查 | T1新编写 |

新建的UI元数据供Codex使用，不代表DSH读取它；DSH以本版本支持的SKILL.md和配置为准。原 [.dsh目录使用说明](README.md) 仍适用：T1 Git根下的dicksick不是自动独立项目根，需要正确的provider路径。此批不改全局设置或启动Harness。

## 运行边界

导入的Skill默认遵守本仓库权限和费用规则。先读新增的host-integration说明；示例中的付费模型、远程验证及redteam内容不代表已配置或获准运行。Redteam专用Skill未收录。

webapp-testing上游脚本和示例保留，Windows服务器子进程树清理和真实浏览器流程未验证；不要直接套用Unix输出路径，持续连接页面也不应统一等待networkidle。

只在本任务暂存/输出目录取包、写文件和跑离线检查，没有全局安装Skill、安装Promptfoo/Playwright、下载模型、配置API Key、启动浏览器/应用或调用付费API。

## 模型与来源

- [新增模型/API候选](models/ADDITIONS-2026-10-17.md)
- [本批来源、提交和文件记录](SOURCES-additions-2026-10-17.json)

验证结果见来源记录。静态/离线辅助程序检查不等于真实DSH发现、浏览器端到端验收或模型效果评测。
