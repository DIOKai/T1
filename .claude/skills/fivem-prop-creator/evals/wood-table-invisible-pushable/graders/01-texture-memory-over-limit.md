---
type: llm
focus: trace
weight: 1
---

The answer identifies the two uncompressed 2048x2048 A8R8G8B8 textures as a texture-memory problem that pushes the ytd past FiveM's 16 MiB / 48 MiB streaming warning thresholds, and recommends block-compressed formats (DXT1/BC1 for opaque, DXT5/BC3 for alpha) at a smaller power-of-two size with mipmaps.
