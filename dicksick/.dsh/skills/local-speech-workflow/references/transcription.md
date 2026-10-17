# ASR and alignment

Primary sources: [Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR) and [native Transformers checkpoint](https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf). Recheck the installed package and exact checkpoint before selecting a loader. The legacy qwen-asr and native Transformers interfaces are different integration choices.

Check offline, streaming, batch and timestamp support separately for the chosen backend. In the publisher qwen-asr workflow, streaming and alignment have distinct constraints; adding an aligner is not speaker diarization. Do not claim speakers were identified from timestamps alone.

For long recordings keep chunk start times, overlap, output order and completeness. Deduplicate overlap conservatively with evidence, preserve original transcripts and apply each chunk offset exactly once. Silence, music, code-switching, clipped speech and out-of-vocabulary words need explicit review cases. Supplied contextual words should aid recognition, not invent missing speech.

A timestamp must identify its time base, unit and whether it is model-estimated or forced-aligned. Verify monotonicity, duration bounds, pauses and boundary words against the original audio. If only text was returned, report timestamps unavailable rather than distributing words evenly.

Video discovery: [Qwen3 ASR ComfyUI](https://www.youtube.com/watch?v=aW2VmmSkWcM), AxiomGraph, 2026-02-11. Metadata and description only; a ComfyUI demonstration does not validate an SDK or mobile integration.
