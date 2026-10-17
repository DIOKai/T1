# Engine selection

Reviewed 2026-10-17.

Use existing text extraction when a PDF's text layer accurately represents the needed pages. OCR becomes relevant for scanned, image-only, corrupted or partially missing text. A hybrid PDF may need per-page handling rather than wholesale rasterization.

[DeepSeek-OCR-2 official repository](https://github.com/deepseek-ai/DeepSeek-OCR-2) and [model card](https://huggingface.co/deepseek-ai/DeepSeek-OCR-2) are the primary implementation references. The publisher examples use NVIDIA/CUDA and custom model code; do not infer Windows, CPU, VRAM fit or a particular inference-server route from a generic model-loader snippet. Pin a revision and inspect the loading code before permitting custom code. A mock backend is only a plumbing test.

The [hec-ovi OCR skill](https://github.com/hec-ovi/ocr-skill) informed candidate review, not this implementation. Its bundled binary, .noob paths, broad routing and whole-directory fallback are not copied. No third-party OCR runtime or model weights ship in this skill.

Choose based on local availability, languages, page layout, device, reproducibility and evidence requirements. If no suitable engine is installed, report that boundary and provide the chosen implementation plan; do not pretend OCR happened or automatically install a new environment.
