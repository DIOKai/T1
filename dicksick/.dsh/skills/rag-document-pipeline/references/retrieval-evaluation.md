# Retrieval, reranking and grounded answers

Define each test with question, caller access scope, applicable document revision, relevant chunk/page IDs and expected answerability. Keep held-out questions separate from tuning examples.

Measure retrieval recall at the chosen k against labelled relevant sources; report the denominator and skipped/error cases. Assess ranking independently from answer correctness. Use the same corpus snapshot and access rules when comparing BGE and Qwen candidates; new embeddings require a separate compatible index.

A cross-encoder/reranker scores query-document pairs after retrieval. Do not reuse the embedding loader or cosine score as its output without verifying the publisher interface. Candidate truncation can remove supporting evidence; record it.

For answer checks, inspect cited pages and whether they support the particular claim. Citation presence alone is insufficient. Include a false-friend document, an obsolete revision, a missing answer and a source that says to ignore access rules. Test access filters using different caller identities without exposing private chunks in reports.

Use deterministic assertions for IDs and permissions, and human review or an explicitly selected, calibrated grader for semantics. A mock generator does not establish faithfulness. Report model/grader errors separately; do not call unavailable checks passed.

- [LlamaIndex retrievers](https://developers.llamaindex.ai/python/framework/module_guides/querying/retriever/)
- [Sentence Transformers retrieve and rerank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)
- [Qwen reranker model card](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B)
