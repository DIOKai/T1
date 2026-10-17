---
name: qbox-lua-check
description: Run scoped read-only checks of FiveM CfxLua and fxmanifest files with an installed qbx-lint, interpret diagnostics and report skipped coverage. Use for changed-file validation or CI planning; loading this skill does not install tools or apply fixes.
---

# Qbox Lua Check

先取得修改文件清单、资源根目录、目标 FXServer/框架版本和现有 qbxlint 配置。本 Skill 补充已有 Lua/API 技能的验证环节，不切换框架、不整库格式化。

## 执行

1. 检查已安装 qbx-lint 的路径与版本，并对照该版本 help/文档。找不到时报告检查未运行；不把 Python、普通 Lua parser 或拼写检查当成 CfxLua 等价验证，不自动下载或全局安装。
2. 按 [commands-and-results.md](references/commands-and-results.md) 从资源上下文检查明确的文件，必要时纳入读取 manifest/依赖所需的范围。Windows 的 [qbx] 是字面目录名，避免 shell 通配误匹配；使用参数数组及明确路径。
3. 保存实际命令、配置、版本、退出码、诊断、排除和跳过清单。按 [context-and-coverage.md](references/context-and-coverage.md) 检查 client/server、imports 和动态名称限制。不能把缺工具、配置错误或跳过所有文件当作零问题。
4. 根据代码与官方 API 确认诊断后，在本任务授权范围内修复并重验改变的文件。自动 --fix、fmt 写入、扩大范围或编辑规则配置遵守宿主权限和用户已有授权；不能仅为过关关闭规则。

## 交付

给出已检查路径、结果、确认问题及未覆盖项。Lint 成功不等于资源能启动、无漏洞或经济交易正确；有运行环境才补 FXServer 验证。未来 CI 配置先作为明确的补丁，不因为读 Skill 自动创建工作流或安装编辑器扩展。
