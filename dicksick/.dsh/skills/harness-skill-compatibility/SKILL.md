---
name: harness-skill-compatibility
description: Audit and adapt agent skill bundles for DeepSeek Harness discovery, metadata, resource paths, tool availability, dependencies, and invocation behavior. Use when moving skills between Claude, Codex, and DSH or diagnosing missing skills.
---

# Harness Skill Compatibility

检查技能能否被目标Harness发现、读取和执行。保留来源目录；改编写入明确的新副本，记录差异。不要把文件存在当作已加载或运行成功。

## 检查顺序

1. 确定实际Harness版本、启动目录、项目根、skill provider配置和可用工具。只读相关配置；不遍历凭据或自动修改全局设置。
2. 依据该版本官方文档检查根目录与优先级。T1中的 dicksick/.dsh/skills 不会因进入dicksick子目录就必然成为项目根技能目录。
3. 检查直接子目录SKILL.md或受支持的平铺文件、YAML name/description、名称冲突与调用字段。路径存在和格式通过仍不证明provider已启用。
4. 跟踪正文实际用到的references/scripts/assets、同级Skill和工具；逐项标明已有、缺失、可替代或未验证。保留完整许可证、数据及依赖；不要只复制入口。
5. 对Claude专用工具名、hooks、commands、子代理和环境变量占位符建立显式映射。工具名称相似不保证权限/输入输出等价；没有等价实现就报告受阻流程。
6. 只在已授权副本中进行必要适配。测试发现、加载、按需资源与一个无副作用场景，再考虑实际执行。保持宿主已有权限和费用规则。

## 参考与输出

目录与字段合同见 [dsh-discovery.md](references/dsh-discovery.md)。
验收分层和迁移清单见 [migration-checks.md](references/migration-checks.md)。

输出来源/目标版本、目录与工具映射、缺失项、最小改编差异和实际运行证据。
区分文件核对、静态检查、provider发现、模型选用和真实任务验收；不把这些合并为单个“兼容”结论。
