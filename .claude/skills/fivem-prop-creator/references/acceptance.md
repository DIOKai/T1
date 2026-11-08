# Prop acceptance: checker codes and in-game tests

## Run the checker

```
py -3 -I .claude/skills/fivem-prop-creator/scripts/check_prop_resource.py <resource | folder | export folder> [more] [--json]
```

Read-only, standard library, exit 1 on errors. It reads compiled RSC7 files through `rsc_probe.py` (only the small "virtual" block is inflated, so big texture dictionaries are cheap) and Sollumz/CodeWalker XML exports. Archetype names in a compiled ytyp are hashes; they are matched to file names with joaat, so records whose model is not in the scanned folders stay anonymous (`ARCHETYPE_UNNAMED`). Scan several resources together when one resource requests a ytyp streamed by another.

| Code | Level | Meaning → fix |
|---|---|---|
| `NO_MANIFEST` | error | stream folder without fxmanifest.lua |
| `ITYP_REQUEST_MISSING` | error | DLC_ITYP_REQUEST names a ytyp stem that exists nowhere → fix the name or ship the ytyp |
| `ITYP_REQUEST_MLO` | error | requested ytyp holds an MLO archetype (binary or XML) → remove the line, let the .ymf load it |
| `ITYP_REQUEST_PATH` / `_OTHER` / `_EXTERNAL` | info | found by file name at another path / in another scanned resource / no path given — works |
| `ITYP_REQUEST_GLOB` | warn | glob matches no file (`*ytyp.`) |
| `ITYP_NOT_REQUESTED` | warn | ytyp with custom models, no request, no .ymf → invisible / spawn fails |
| `ITYP_ONLY_YMF` | info | only a .ymf loads it; ymap placement works, script spawning unverified |
| `XML_IN_STREAM` | error | XML is never loaded from stream |
| `SOURCE_IN_STREAM` | warn | .blend/.fbx/.dds/.png in stream: downloaded, never used |
| `NAME_CASE` | warn / info | space in a streamed name / uppercase only |
| `NOT_RSC7`, `ESCROWED` | warn, info | not a compiled file / Cfx escrow (FXAP) — content unverifiable |
| `ASSET_OVER_16MIB` / `_48MIB` | warn / error | FXServer streaming warning (RSC header formula) |
| `PROP_HEAVY` | info | > 2 MiB physical (ydr/yft) or > 4 MiB (ytd); vanilla street props < 1 MiB |
| `DUPLICATE_ASSET` | error | same stream file name twice |
| `ARCHETYPE_DUPLICATE` | warn | same archetype in two ytyps (identical or different settings) |
| `ARCHETYPE_NO_MODEL` / `ASSET_TYPE_MISMATCH` / `YDD_MISSING` | error / warn | archetype without model file, ydr↔yft type wrong, missing ydd |
| `NAME_MISMATCH` | error | archetype name ≠ assetName |
| `ARCHETYPE_UNNAMED` | warn / info | archetypes whose hash matches no scanned file |
| `MODEL_NO_ARCHETYPE` / `MODEL_REPLACES_VANILLA` / `NO_YTYP` | warn / info | streamed model nobody defines (custom name / Rockstar-style name = replacement) |
| `LODDIST_ZERO` / `LODDIST_HIGH` | error / warn | lodDist ≤ 0 / > 500 m on a small prop |
| `LODDIST_DEFAULT` / `LODDIST_VS_SIZE` / `LODDIST_SHORT` | info | Sollumz 200/100 untouched / far above the vanilla band / under 10 m |
| `FLAGS_ZERO`, `STATIC_AND_DYNAMIC`, `FRAGMENT_NOT_DYNAMIC` | info, warn, warn | flag choice (collisions-and-flags.md) |
| `DOOR_FLAGS` / `DOOR_ATTR_ZERO` | warn / info | door attribute 5/7/8/9/10/12 without Dynamic + Door Physics / flag 27 with attribute 0 (vanilla does it, unverified) |
| `ANIM_NO_CLIP`, `CLIP_NO_FLAG`, `CLIP_NOT_LOCAL` | error, warn, info | animation flags vs clip dictionary |
| `TXD_NOT_LOCAL` | info | texture dictionary not in the scan (vanilla shared dictionary?) |
| `TEX_NOT_POW2` / `TEX_TOO_BIG` / `TEX_LARGE` / `TEX_UNCOMPRESSED` / `TEX_NO_MIPS` | warn / warn / info / warn / warn | texture rules (lods-textures-budgets.md) — report, do not re-compress unasked |
| `NO_HIGH_LOD`, `NO_LOD`, `LOD_NOT_REDUCED`, `TRIS_HIGH`, `LOD_SWITCH_BEYOND_UNLOAD` | warn, info, warn, info, info | LOD set-up vs vanilla |
| `NO_COLLISION` | warn / info | no embedded bounds and no same-name ybn (info for hand-sized props and map/MLO resources) |
| `EXTERNAL_YBN` | info | only a separate ybn — map collision; spawned-prop behaviour unverified, embed it |
| `BVH_NO_FLAGS` | error | XML: GeometryBVH without Composite Flags → collision does nothing |
| `POLY_COLLISION_HEAVY` | warn | XML: > 300 collision polygons (vanilla max 126) |
| `PARSE_FAILED` | info | binary layout not understood; open in CodeWalker |

Not checked: `.yft` internals (header and size only), collision flags inside compiled bounds, which vanilla dictionaries exist, appearance and behaviour in game.

## Real result on the user's server (read-only, 2026-11-08)

- `wood_table`: 2048² A8R8G8B8 texture → 32 MiB (warn), Sollumz default lodDist, flags 0, collision only in a separate ybn.
- `wood_table_v2`: two 2048² A8R8G8B8 → 64 MiB (error, over 48 MiB), defaults, flags 0, no Medium LOD; embedded composite collision OK.
- `lp_elevator`: seven 512² A8R8G8B8 textures (14 MiB ytd), flags 0 on doors/car.
- `cylex_animmenuv2`: two DLC_ITYP_REQUEST globs `*ytyp.` that match nothing, `badge1.ytyp` requested but absent, 16 duplicate-archetype groups between bzzz ytyps, 1000×1000 textures, a watertank lodDist of 2,000,000.

## In-game tests (local test server only, never the live server)

Log game build, archetype names, coordinates, tool versions.

| Check | Test | Pass |
|---|---|---|
| Load | cold join, then `restart <res>`; F8 + server console | no 16/48 MiB, "Could not add data_file" or entitlement messages |
| Identity | spawn by name (`/haiprop <model>` or ymap) | appears with textures, right size and origin |
| Distance | walk 0 → lodDist → beyond from three sides | LOD swaps where expected, no early vanish or pop |
| Collision | walk around/onto/under, push, shoot, drive into it | blocks, footstep and bullet sounds match the material |
| Lighting | day, night, rain | no pink night glow (vertex colour), emissive lit at night |
| Dynamics | push, hit, break | Dynamic props move; broken parts behave; respawn |
| Doors | open, close, lock with two clients | both clients see the same state |
| Conflicts | start with neighbouring resources | no name collision with other packs |

Record observations or "not run". A clean checker run and a CodeWalker view are not an in-game pass.
