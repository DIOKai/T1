# OCR quality and evidence

For every requested page record source-file hash, source page number, extraction method/version, output locator, processing status and any uncertainty. Distinguish a physically blank page, a successfully extracted empty page, an OCR error and a page never processed.

A useful pilot contains dense text, a table, rotated content and a low-quality page when available. Compare line order, negatives/decimal separators, units, dates and table headers against the image. Do not use model-generated confidence as a calibrated accuracy score.

Check expected versus returned pages, truncation, repeated headers and missing regions. Preserve source wording in transcription; explanations and corrected spelling belong in a separate section. Mark unreadable spans without guessing. A screenshot can support review but is not equivalent to a machine-verifiable text diff.

Use only an explicit output directory; keep originals and superseded outputs intact unless replacement is authorized. Report which pages or fields were reviewed and which remain uncertain.

Supplementary video: [DeepSeek-OCR 2 Guide](https://www.youtube.com/watch?v=4H0Ozgq75Gc), Byte Goose AI., 2026-01-27. Only search metadata/description were checked, not a complete transcript; performance and fine-tuning claims are not adopted as verified facts.
