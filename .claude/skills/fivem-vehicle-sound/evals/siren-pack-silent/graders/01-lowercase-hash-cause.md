---
type: llm
focus: trace
weight: 1
---

The answer identifies the cause: CodeWalker hashes names exactly as written (case-sensitive) while the game hashes audio names in lowercase, so uppercase names written into the REL are never found; names must be written in lowercase.
