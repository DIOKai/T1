---
type: llm
focus: trace
weight: 1
---

The answer explains the hat-hair fix: a negative hair scale on the p_head prop (expressionMods index 0, e.g. via grzyClothTool hair scale) plus a creaturemetadata YMT referenced by the meta, and warns that it only works on hair with the MH_Hair_Scale bone (base hair ids 36 and above, most custom hair lacks it).
