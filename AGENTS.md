# AGENTS.md（给 OpenAI Codex 等代理看）

这个仓库的规则写在 `CLAUDE.md` 和 `LESSONS.md`，Claude Code 和 Codex 共用同一套，不要另写一份。

开始任何任务前：

1. 先读 `CLAUDE.md`：用任何技能前都要先问用户、不用付费的东西、FiveM/3D/土木工程的规则。用户用中文交流，回复也用中文。
2. 再读 `LESSONS.md`：用户纠正过的做法，照着做，不要让用户再说一次。
3. 用户纠正你，或说"下次/以后/记住……"时，照 `.agents/skills/correction-memory/SKILL.md` 做：先改好，再把规则写进 `LESSONS.md` 并提交。

技能在 `.agents/skills/`（是 `.claude/skills/` 的链接，两边是同一份文件）。

`CLAUDE.md` 里提到的插件（superpowers、muto-atlas、document-skills 等）是 Claude Code 专用的，Codex 里没有就跳过，不要假装用了。MCP（blender、fivem、freecad、ifc）在 Codex 里装了才能用，用法看 `mcp-for-blender`、`fivem-mcp`、`freecad-mcp`、`ifc-mcp` 技能，一样要先问用户；`fivem` 只连本机测试服。

每批新技能的来源、授权和检查记录放在 `docs/skill-batches/`。新加技能后，要在 `CLAUDE.md` 写清楚什么情况建议用哪个、和旧技能重叠时以哪个为主，Claude Code 和 Codex 才都知道怎么选。
