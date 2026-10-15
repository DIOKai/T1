# Catalog contract

scripts/catalog_assets.py uses Python 3 standard library. Run from this skill directory:
~~~text
python scripts/catalog_assets.py "PATH_TO_LIBRARY" --hash
~~~
Capture stdout to a new catalog file outside the scanned root. No parser, game native or executable asset is run. The helper skips links/reparse points, reports unreadable or changing files and keeps relative paths.

The JSON records path, resource directory when an enclosing fxmanifest.lua or __resource.lua exists, extension, size, modified time and optional SHA-256. Same filename ignoring case is a potential naming collision; the script does not assert that different resources actually conflict. Equal SHA-256 values indicate equal scanned bytes, not equal licensing or interchangeable packaging.

For an enriched catalog use:
- catalog_id: stable local key independent of display name.
- resource/path/source_hash and revision/build: the file identity.
- asset_kind, model_name, collection/component/variation IDs: observed values plus evidence.
- preview_path and preview_status: existing, generated, missing or failed.
- source/license_notes and user_tags: user's provenance and organization.
- validation_status: scanned, viewer-checked, game-tested or unresolved.

Do not store credentials, server connection strings or unrelated personal files in a catalog intended for GitHub. Do not rename sources to fit catalog labels.

## Sources and boundary

Reviewed 2026-10-15:
- [Cfx resource manifest](https://docs.fivem.net/docs/scripting-reference/resource-manifest/).
- [CodeWalker](https://github.com/dexyfex/CodeWalker): game-aware inspection.
- [DurtyFree GTA data](https://github.com/DurtyFree/gta-v-data-dumps): optional stock-identifier lookup; data/preview redistribution terms must be checked separately.

This helper catalogs files, not rendered geometry, texture validity, DLC availability or all runtime asset identifiers. It does not bundle third-party game dumps or previews.
