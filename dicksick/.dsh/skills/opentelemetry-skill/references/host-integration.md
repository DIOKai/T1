# T1 host integration

This file is a T1 addition. The fixed upstream SKILL.md adds only a link to this note; upstream reference documents, example and license are preserved.

Treat upstream configuration as task-specific guidance, not permission to enable telemetry on the user's coding agent or machine. This repository adds instructions only: no Collector, exporter, SDK, cloud backend or agent setting is installed or activated.

Honor the repository's free-only and data-scope rules. Start with local/synthetic telemetry and an explicitly scoped service. Do not set CLAUDE_CODE_ENABLE_TELEMETRY, edit global Codex/Claude config, export private data, or enable cloud services merely because the upstream reference shows a command. Keep prompt/answer/tool-content capture off unless that specific capture is requested and its destination is approved.

Upstream examples span multiple platforms and host products. Verify distribution, component stability, SDK/semantic-convention version and actual emitted signals before applying them. Rule-of-100/cardinality advice is a heuristic, not a universal validated threshold; compare against the project's volume and backend constraints. A parsed YAML document is not a tested Collector pipeline.

Only SKILL.md, its complete references, the referenced Python example and LICENSE are imported. Upstream plugin manifests, auto-monitoring workflows, repository automation and evaluation harnesses are not installed. Host references do not make their commands or paid features available in DSH.

Syntax/source checks were performed during packaging; live OTel delivery and agent-native telemetry were not tested. If no actual runtime is available, report that boundary instead of claiming a successful trace.
