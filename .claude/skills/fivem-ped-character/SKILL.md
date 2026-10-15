---
name: fivem-ped-character
description: Create, adapt, diagnose, and validate GTA V/FiveM ped heads, bodies, skin surfaces, hair, beards, and character meshes in Blender/Sollumz. Use for freemode or custom-ped character art; use fivem-clothing-creator when the task is mainly garments.
---

# FiveM Ped Character

Build character assets that remain compatible with the target GTA V ped, skeleton, materials, LODs, and FiveM packaging.

## Establish the target

Confirm the target ped, streamed freemode versus custom ped, male/female base where relevant, Legacy/Gen8 versus Enhanced/Gen9, replacement versus add-on delivery, available source files, and the user's right to modify them. Inspect first and preserve an untouched copy.

Read [references/official-pipeline.md](references/official-pipeline.md) before choosing the import/export route or asserting a file-format limitation.

## Build the character

1. Assemble the correct base components and the matching external YFT skeleton. Freemode bodies are split across component YDDs rather than being one ordinary mesh.
2. Establish silhouette and proportions before detail. For focused work, combine the installed `character-artist`, `sculpting`, `hair-groom`, `retopology`, `rigging`, `uv-workflow`, and `texture-workflow` skills only after the user approves their use.
3. Keep the target GTA bone names, hierarchy, vertex groups, bind pose, scale, and component boundaries unless the chosen ped pipeline explicitly supports a change. Do not invent a new player skeleton.
4. Treat game hair as a real-time asset: build readable masses, scalp coverage, alpha-tested cards or suitable mesh hair, compatible materials, and descending LODs. Do not export Blender strand curves as if GTA will render them directly.
5. Preserve freemode skin UV regions when tint or shared skin textures depend on them. Check head/body seams, normals, tangents, diffuse, normal, specular/roughness behavior, and alpha usage under representative lighting.
6. Transfer and normalize weights deliberately. Test jaw/neck, shoulders, elbows, hips, knees, hands, and extreme poses before export.

## Validate before delivery

- Inspect front, side, back, close-up, and gameplay-distance views.
- Verify all required LOD meshes, materials, texture names, vertex colors, skeleton links, and non-empty vertex groups.
- Fresh-import the exported asset when the toolchain supports it, then compare scale, hierarchy, weights, UVs, materials, and bounds.
- Test on a local FiveM development server only after separate permission. Record the game generation, ped name, component, export method, and unresolved limitations.

Do not claim success from a Blender viewport alone. A visually correct mesh can still fail because of skeleton, material, texture, LOD, or resource-packaging errors.

## Boundaries

Do not bypass Asset Escrow, encryption, entitlement checks, or license restrictions. Do not use paid generators or services. Ask before controlling Blender or FiveM through MCP because those actions execute on the user's live applications.
