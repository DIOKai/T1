---
type: llm
focus: trace
weight: 1
---

The answer gives a concrete check that rejects near-miss loop lengths at 128 BPM (e.g. shows that 224 or 226 frames, or 112/113 frames, drift off the beat), for example with scripts/dance_timing.py --check or an equivalent calculation.
