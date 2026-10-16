# Ingestion and index lifecycle

Reviewed 2026-10-17.

## Preserve evidence

Keep a source hash and revision, document ID, page/section locator, extraction method/version, chunk ID, language, and access scope. OCR needs a link to the image/page; unreadable cells remain unknown. Do not guess missing numbers, units, or table headings.

Extract one representative document before bulk work. Check reading order, tables, repeated headers, Unicode, scanned pages and page labels. Chunk along meaningful structure; record overlap and truncation. Separate content hashes from identity: identical text can belong to different documents or access scopes.

## Index compatibility

Store an index fingerprint including embedding publisher/model/revision, dimensions, normalization, parser and chunk configuration. A reranker can score candidates but cannot repair a missing source. Rebuild into a new namespace on incompatible changes, compare retrieval and only then switch the application reference.

Use source IDs and revisions for update/delete reconciliation. Verify old chunks cannot appear after replacement or permission revocation; include caches and exported citations. A vector store entry alone is not a backup of original documents.

## Sources

- [LlamaIndex documents and nodes](https://developers.llamaindex.ai/python/framework/module_guides/loading/documents_and_nodes/)
- [LlamaIndex document management](https://developers.llamaindex.ai/python/framework/module_guides/indexing/document_management/)
- [Qwen embedding model card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B)

These references inform the workflow, not a claim that LlamaIndex, OCR or any vector database has been installed.
