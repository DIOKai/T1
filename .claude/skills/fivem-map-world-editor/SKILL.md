---
name: fivem-map-world-editor
description: Create or diagnose GTA V/FiveM outdoor maps, YMAP placements, terrain replacements, exterior collision, world LOD relationships, and map resource conflicts using CodeWalker and Sollumz. Route room/portal interiors to an MLO workflow.
---

# FiveM Map World Editor

Treat an outdoor map as connected placement, archetype, visual, collision and streaming data.

## Establish scope

Inspect the area and existing files. Record game edition/build, tool versions, coordinates/affected area, add-on versus replacement intent, neighboring resources and source rights. Preserve originals.

Use an MLO workflow for interior rooms, portals and room associations. Mixed projects may need both; do not introduce room data for ordinary exterior geometry.

Read [world-integration.md](references/world-integration.md) for dependency and advanced-layer decisions and [acceptance.md](references/acceptance.md) before claiming completion.

## Edit and integrate

1. Identify owning YMAP/YTYP/YDR/YBN data and required references. Avoid replacing an entire archive to move one object.
2. Edit explicit placements. Preserve scale and quaternion conventions when transferring transforms between tools.
3. Connect new archetypes to the intended assets/dictionaries. YMAP references archetypes; it is not the visible mesh.
4. Recalculate extents and flags after changes. Inspect LOD parent/child references after deletions or entity reordering.
5. Align terrain visuals and collision along roads, curbs, entrances, coasts and boundaries. A visible ramp alone is not driveable terrain.
6. Review/regenerate dependency manifests where appropriate, package the resource and fresh-load it before testing.
7. Compare isolated-resource behavior with the target resource set to locate replacement/name conflicts.

Do not use arbitrary huge draw distances or blanket removal scripts as a substitute for identifying the responsible data.

## Completion

Report files, affected coordinates, dependencies, versions, resource set and repeatable test observations. Distinguish viewer evidence, local-game tests and multi-client tests.

Discover available tools instead of assuming a CodeWalker or FiveM MCP exists. Loading this skill does not authorize tool installation, live application changes, server edits or deployment beyond the user's task.
