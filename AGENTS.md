# AGENTS.md（给 OpenAI Codex 等代理看）

这个仓库的规则写在 `CLAUDE.md` 和 `LESSONS.md`，Claude Code 和 Codex 共用同一套，不要另写一份。

开始任何任务前：

1. 先读 `CLAUDE.md`：用任何技能前都要先问用户、不用付费的东西、FiveM/3D/土木工程的规则。用户用中文交流，回复也用中文。
2. 再读 `LESSONS.md`：用户纠正过的做法，照着做，不要让用户再说一次。
3. 用户纠正你，或说"下次/以后/记住……"时，照 `.agents/skills/correction-memory/SKILL.md` 做：先改好，再把规则写进 `LESSONS.md` 并提交。

技能在 `.agents/skills/`（是 `.claude/skills/` 的链接，两边是同一份文件）。

`CLAUDE.md` 里提到的插件（superpowers、muto-atlas、document-skills 等）和 MCP（blender、fivem、freecad、ifc）是 Claude Code 专用的，Codex 里没有就跳过，不要假装用了。
