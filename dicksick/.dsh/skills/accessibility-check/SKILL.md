---
name: accessibility-check
description: Review web accessibility using scoped axe/Playwright checks plus keyboard, focus, forms, and dynamic-content evidence. Use for accessibility audits and regression tests; automated findings alone do not establish WCAG conformance.
---

# Accessibility Check

先确定页面、状态、用户流程、浏览器/设备和目标规范版本/等级。未给目标时可提出项目适用的审查基线，但不能擅自宣称法定合规。保留现有测试框架和权限边界。

## 证据流程

1. 检查现有Playwright、axe、浏览器和测试账号；只对授权的本地/测试环境执行。缺工具时输出静态发现与未完成项，不冒充实际浏览器审计。
2. 建立状态清单：初始页、菜单/对话框、表单错误、加载/空/失败、流式内容与成功状态。按可观察的页面条件等待；不要统一使用networkidle等待持续连接页面。
3. 运行项目版本适用的自动扫描并保留规则ID、受影响节点、页面状态和截图。对规则适用性人工核对；超时、扫描错误或缺失结果不是零违规。
4. 按 [manual-checks.md](references/manual-checks.md) 检查键盘、焦点、名称、标签、结构与动态播报；必要时安排实际读屏。静态代码检查无法确认真实焦点与读屏结果。
5. 先报告具体触发方式、影响和证据，再在已授权范围修复；不自动启用来源Skill的更新、全站写操作或代码批量修改。复验改变的状态，并保存未验证清单。

工具用法与证据结构见 [automation-and-evidence.md](references/automation-and-evidence.md)。默认不启动NVDA/VoiceOver或其他用户级辅助工具；需要真实读屏验收时明确设备和可用环境。

交付按用户影响排序的发现、定位、复现步骤、修复建议与复验结果；不编造“自动工具能覆盖固定百分比”的保证。
