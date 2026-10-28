---
type: llm
focus: trace
weight: 1
---

The render loop does no rendering work when nothing is changing (a dirty/invalidate flag or equivalent) and stops on visibilitychange when the tab is hidden.
