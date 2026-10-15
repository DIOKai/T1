---
name: fivem-asset-catalog
description: Inventory and organize existing GTA V/FiveM asset libraries with resource paths, hashes, optional previews, component identifiers, and provenance. Use for finding and cataloging assets; this skill does not generate or convert the asset itself.
---

# FiveM Asset Catalog

Keep a searchable inventory tied to real files, resource revisions and explicitly observed identifiers. Preserve the user's folders and binaries.

## Inventory

1. Confirm the scoped library root and whether the catalog is local or intended for sharing. Do not sweep unrelated folders.
2. Run scripts/catalog_assets.py ROOT for a read-only file inventory; add --hash when content hashing is useful. The script emits JSON to stdout and does not generate previews.
3. Resolve likely asset type and resource ownership from manifests/game-aware viewers. A filename stem is only a candidate model name; a hash or extension alone is not proof of a spawnable model.
4. Add component/variation/collection identifiers for ped assets only after inspecting the actual packaging. Do not infer globally stable clothing indices from a filename.
5. Generate previews only with available authorized tools. Mark missing previews explicitly. Reference existing preview paths instead of copying a whole library.
6. Maintain source, rights/usage notes and original hashes separately from derived previews. A database of stock GTA identifiers does not grant redistribution rights to images or purchased mods.

Read [catalog-contract.md](references/catalog-contract.md) for the schema, duplicate interpretation and helper limits.

## Acceptance

The index must resolve back to the exact resource/file, identify stale entries, distinguish exact duplicates from same-name candidates, and retain source evidence. A successful scan does not prove file-format validity or in-game loading. Changes to source folders, renaming or deduplication require a separate scoped request.
