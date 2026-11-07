---
type: llm
focus: trace
weight: 1
---

The answer rejects scaling the UVs 20x and gives a concrete limit or fix: keep |UV| under about 50 (half-float precision) or recentre the UVs near 0, with a lower tiling instead.
