# Hair workflow and acceptance

Use when the character task involves scalp hair, beards, brows or hair-card integration. This extends the character workflow; clothing-dominant work remains in its garment workflow.

## Identify the target

Record the exact ped/base, head shape, freemode versus custom ped, component slot, variation/texture identifiers, add-on versus replacement delivery, game edition/build and exporter version. Do not assume a texture overlay, hair component and ped-attached prop are interchangeable.

Keep a known-good target head/hair/skeleton and texture setup for comparison. Replacing one variation should not silently remap the rest. Preserve the user's source and rights to modify it.

## Geometry and cards

Block silhouette/scalp coverage before strands. Build card flow to reduce obvious gaps from player camera angles; inspect crown, parting, temples, ears and nape. A curve groom is a construction source, not evidence of GTA-compatible exported geometry.

Inspect normals and backfaces on both sides. Do not solve invisibility by indiscriminately duplicating all faces: compare the intended shader and asset path. Make purposeful lower LODs; ensure coverage remains when small cards disappear.

## Shaders and textures

Use a target-compatible ped hair shader. Compare exported texture slots, alpha convention, tint behavior, normal/specular treatment and vertex-color usage with a compatible reference. Blender Principled/PBR appearance is insufficient.

Do not prescribe one alpha threshold, shader name, channel value or texture compression for every GTA generation. Validate tint and transparency in the target toolchain. Inspect mip levels and silhouette at distance; fringes can appear even when a close preview looks clean.

## Rigging, wind and headgear

Use the correct external ped skeleton when required. Verify named bones rather than accepting unknown groups. Transfer weights deliberately and inspect head/neck/jaw movements. Keep the source character workflow's influence constraints unless current target documentation demonstrates otherwise.

Wind can involve shader/vertex-color behavior, bones or a combination depending on the asset path. Do not promise cloth/hair simulation by adding arbitrary helper bones. Compare a compatible base, then test the actual target behavior.

Identify supported hats/helmets and variations. Test them explicitly; automatic compressed-hair or alternate-variation behavior requires the relevant metadata and cannot be claimed from collision-free manual posing.

## Acceptance matrix

| Test | Expected evidence |
| --- | --- |
| Fresh import/viewer reload | Correct component, skeleton, shaders and texture references |
| Scalp/camera orbit | No unintended bare gaps, backface holes or ear/face penetration |
| Head turn, aim, crouch, driving | No detached cards, severe stretching or neck penetration |
| Color variations | Requested tint behavior survives export |
| Day/night/rain | No unintended alpha halos or sorting defects |
| Wind | Requested response observed in game, or explicitly untested |
| Required hats/helmets | No unacceptable clipping; variant behavior actually confirmed |
| Distance/LOD | Coverage and silhouette preserved at specified gameplay distances |
| Cold join/resource reload | Correct variation selected without stale data |

Record build, component identifiers, head/hats used and pass/fail/not-run. Do not claim compatibility with every head/hat from a single sample.

## Evidence provenance

Current review 2026-10-15:
- [Sollumz basic ped/clothing editing](https://docs.sollumz.org/tutorials/basic-clothes-editing) supports component and external-skeleton integration; it is not a complete hair-production tutorial.
- [Sollumz feature support](https://docs.sollumz.org/features) must be checked for the installed exporter.
- Existing video-verified-ped-workflow.md was recovered unchanged from T1 at f218a8cb3a340036e78bd29a3d88f66d9852fdd1. Its transcript-study statements belong to that earlier author/session.

This continuation did not independently watch those videos or retrieve their full transcripts. Hair-specific choices above are a proposed production/acceptance workflow requiring target-asset validation; they are not presented as verified quotations from those videos.
