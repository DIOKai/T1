# Clothing video study

Videos reviewed at the page/chapters level:

- [Custom freemode clothing using Sollumz Blender 2025](https://www.youtube.com/watch?v=uBBHJ4vG4fM): chapters cover model import, weight transfer, textures/shaders, LOD creation, vertex painting, YMT creation, file import, meta preparation, and in-game testing.
- [GTA V/FiveM clothing tutorial — physics included](https://www.youtube.com/watch?v=YVk_rkkKS6o): a long-form Blender/Sollumz clothing demonstration with cloth-physics coverage.
- The full transcript of [NcProductions' custom-ped workflow](https://www.youtube.com/watch?v=uhsCTlLtcJs) was also studied because it demonstrates the same component, weighting, UV, vertex-color, metadata, and LOD constraints used by clothing.

The first two videos had no exportable transcript during review. Use them to locate visual demonstrations, not as the sole authority for numeric settings. Cross-check current behavior with `sollumz-clothing.md` and a known-good base asset.

## Reusable checks supported by the study

- Treat import, weighting, materials, LODs, YMT/meta, conversion, and in-game testing as separate gates. A clean Blender mesh passes only the modeling gate.
- Weight transfer needs manual cleanup, normalization, and pose testing. For the demonstrated GTA ped path, keep at most four effective influences per vertex unless the current target documentation proves otherwise.
- Component choice is functional, not cosmetic. Separating `lowr`, `feet`, `uppr`, `jbib`, or accessory roles changes metadata behavior and can affect offsets and alternates.
- Preserve the game's UV and texture contract. When a component combines several source materials, bake them into the target arrangement and verify diffuse, normal, specular, alpha, and internal names after conversion.
- Match normals at body/garment or garment/component boundaries where a visible seam would appear.
- Vertex color/alpha can drive lighting, wind, or sweat behavior depending on shader and component. Copy a known-good target asset and verify in game; do not infer the channel meaning from viewport color alone.
- Cloth physics is an additional deliverable, not a substitute for skin weights. Test pinned regions, stretch, penetration, wind response, animation response, and behavior when physics data is absent or fails to load.

## Merge-ready acceptance

- Every drawable and texture variation loads after a cold restart.
- Walk, run, crouch, sit, raise arms, and extreme joint poses show no severe deformation or exposed-body failure.
- Wind/physics cannot detach the garment, explode the mesh, or penetrate unacceptably.
- LOD changes are coherent, metadata selects the intended component, and a fresh conversion/reimport matches the saved source.
