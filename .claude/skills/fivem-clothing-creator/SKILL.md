---
name: fivem-clothing-creator
description: Create, fit, rig, texture, package, troubleshoot, and accept-test GTA V/FiveM freemode clothing such as shirts, jackets, pants, shoes, and accessories using Blender, Sollumz, and local FiveM testing.
---

# FiveM Clothing Creator

Produce clothing that fits the intended freemode body, deforms with the original GTA skeleton, renders correctly at every LOD, and is packaged as a verifiable resource.

## Define the clothing contract

Confirm male/female target, component slot, add-on versus replacement, Legacy/Gen8 versus Enhanced/Gen9, texture variants, body coverage, expected wardrobe system, and delivery format. Preserve the original files and verify modification rights.

Read [references/sollumz-clothing.md](references/sollumz-clothing.md) before importing, naming textures, or diagnosing missing/invisible garments.

## Production workflow

1. Import the matching freemode YFT skeleton and a known-good component YDD with the external-skeleton option.
2. Build or fit the garment around the correct body components. Keep clothing separate from the body; resolve intersections at neutral and deformation poses.
3. Use even topology around shoulders, elbows, hips, knees, waist, and cuffs. Use cloth simulation only to establish useful drape, then clean and retopologize for the game.
4. Transfer weights from the appropriate base, normalize them, remove unintended influences, and test motion. An exported YDD with empty or wrong vertex groups is not acceptable.
5. Create and review high, medium, and low LODs. Preserve silhouette and coverage while reducing hidden detail.
6. Prepare GTA-compatible materials and YTD content. Check diffuse, normal, specular, alpha, texture dimensions, mipmaps, embedded names, UV placement, and vertex colors against the chosen base component.
7. Export through the installed Sollumz version's supported route. Package only the files required for the chosen add-on/replacement method; do not copy paths or assumptions from another server.

## Acceptance tests

- The resource starts without manifest or data-file errors.
- The garment appears in the intended slot and every texture variant resolves.
- No pink/checkerboard/transparent material, missing body region, severe clipping, or incorrect skin tint appears.
- Neutral, walk, run, crouch, seated, arm-raised, and extreme joint poses do not reveal unacceptable weight or intersection failures.
- High/medium/low LOD transitions are present and visually coherent.
- A restart and reconnect reproduce the same result on a local test server.

Report the exact ped, component code/index, drawable/texture identifiers, tested game generation, and anything not tested. Do not treat a higher slot count as proof that the garment renders correctly.

## Boundaries

Use only files the user may modify. Never decrypt escrowed assets or bypass entitlements. Ask before live Blender or FiveM MCP actions. Do not depend on author-specific absolute paths, private DLLs, or paid hosting features.
