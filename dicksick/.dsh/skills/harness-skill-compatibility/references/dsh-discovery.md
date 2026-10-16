# DSH discovery contract

Reviewed 2026-10-17 against the upstream filesystem provider documentation. Recheck the installed version before proposing configuration.

The documented default roots include project .dsh/skills, project .agents/skills, configured customSkillDirs, user DSH skills and user agents skills. The project root uses the nearest .git ancestor; in T1 that can be above dicksick. Discovery is one level deep: a bundle name/SKILL.md or a flat name.md directly inside a scanned root.

The current provider documents includeDefaultRoots=false for isolating custom roots. Confirm plugin mounting, version, actual absolute paths and precedence before editing any config. Never turn this documentation into an automatic global configuration change.

DSH's disable-model-invocation and user-invocable fields have their own semantics. Codex agents/openai.yaml is host metadata and does not automatically configure DSH; Claude slash commands and placeholders likewise need explicit host support. Preserve source metadata in the source bundle; do not rename a boolean merely because a different host has a similarly named field.

Inspect logs/catalog output when a file is skipped; an absent entry may indicate malformed frontmatter, a wrong root, disabled surface or missing provider. Do not infer a successful load from the presence of SKILL.md.

- [Filesystem provider](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)
- [Skill subsystem](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md)
