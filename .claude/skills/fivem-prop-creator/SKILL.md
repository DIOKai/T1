---
name: fivem-prop-creator
description: Create, adapt, diagnose, and package GTA V/FiveM props using Blender, Sollumz, and CodeWalker. Use for YDR/YTD/YTYP assets, prop collision, LODs, and resource acceptance; route room-and-portal interiors to an MLO workflow.
---

# FiveM Prop Creator

Deliver a prop with a reproducible source-to-resource chain and evidence appropriate to its intended behavior.

## Choose the asset path

Inspect the source first. Establish game edition/build, Blender/Sollumz/CodeWalker versions, dimensions, pivot, intended placement, and replacement versus add-on delivery. Preserve original assets and work within the user's modification rights. Use free tools.

- Static decoration normally follows the Drawable/YDR path.
- Movable or breakable props need a compatible physics/Fragment path. A static export does not prove rigid-body or breakage behavior.
- Animated props and functional doors need separate animation, archetype, physics, and gameplay checks.
- Ped attachments need a bone/local transform; attachment does not turn a prop into a ped component.

Read [asset-pipeline.md](references/asset-pipeline.md) for integration decisions and [acceptance.md](references/acceptance.md) for observable tests.

## Build and integrate

1. Compare scale, orientation, and origin with a known-good game asset. Apply transforms deliberately, preserving hierarchy and placements.
2. Build visual geometry and reduced LODs. Choose budgets from the brief and measurements; do not invent universal triangle or texture limits.
3. Use supported Sollumz shaders. Verify texture names, UVs, normal/specular usage, alpha, vertex colors, and backface behavior against that shader.
4. Author GTA bounds/collision for the object purpose, including intended openings and walkable surfaces. UCX naming is not GTA collision validation.
5. Connect archetype name, asset type/name, dictionaries, bounds, and placement references.
6. Export through the installed toolchain's supported route. XML is an intermediate when used; renaming XML to a binary extension is not conversion.
7. Fresh-load the exported result in a game-aware viewer, then perform the relevant local-game tests when authorized.

For conversion-only requests, preserve model and texture binaries 1:1 unless the user requests optimization. Report size concerns without silently reducing textures, mipmaps, or geometry.

## Completion and tools

Report paths, versions, asset identifiers, dependencies, and pass/fail/not-run results. A viewport render does not prove game compatibility.

This skill supplies instructions, not an MCP connection. Inspect available tools before calling them. Permission to create a Skill does not authorize changing a live scene, server configuration, or deployment.
