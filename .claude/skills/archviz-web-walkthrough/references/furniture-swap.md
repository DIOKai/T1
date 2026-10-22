# Furniture and material swap panel

Two different problems — pick per item:

| Want | Use | Cost |
|---|---|---|
| same sofa, other fabric/colour; other floor wood | **KHR_materials_variants** in the room or furniture GLB | tiny; only materials/textures change |
| a different sofa or table | separate furniture GLBs placed at `slot` empties | one download per option; needs disposal |

## KHR_materials_variants
- Status: complete, ratified (Khronos). Root `extensions.KHR_materials_variants.variants: [{name}]`; each primitive `extensions.KHR_materials_variants.mappings: [{material, variants: [i...]}]`; one variant index appears at most once per primitive; one active variant at a time. The spec says it's for static, pre-made variants, "not meant for interactive configurator authoring".
- Author in Blender: add-on preferences → enable glTF Variants UI; 3D View ‣ glTF Variants: Assign to Variant / Assign as Original / Display Variant. Each material slot = one primitive.
- three.js: GLTFLoader doesn't apply it. The official example `webgl_loader_gltf_variants` reads the extension data itself:
```js
const variants = gltf.userData.gltfExtensions?.KHR_materials_variants?.variants ?? [];
async function selectVariant(name) {
  const index = variants.findIndex(v => v.name === name);
  const jobs = [];
  gltf.scene.traverse(o => {
    const ext = o.isMesh && o.userData.gltfExtensions?.KHR_materials_variants;
    if (!ext) return;
    o.userData.originalMaterial ??= o.material;
    const m = ext.mappings.find(m => m.variants.includes(index));
    jobs.push(m ? gltf.parser.getDependency('material', m.material).then(mat => {
      o.material = mat; gltf.parser.assignFinalMaterial(o);
    }) : Promise.resolve(o.material = o.userData.originalMaterial));
  });
  await Promise.all(jobs);
}
```
  (Same calls as the r186 example `selectVariant`: `parser.getDependency('material', i)` then `parser.assignFinalMaterial(mesh)`; re-check if the project uses another three version.) takahirox/three-gltf-extensions (MIT) also has a plugin, last pushed 2022-12.
- If the room uses lightmaps: a variant material is a new material object — copy `lightMap`/`lightMapIntensity` from the original onto it (the template's lightmaps are assigned after load, not stored in glTF).
- `check_walkthrough_build.py` lists the variants it finds.

## Whole-model swap
1. Room GLB: an Empty per position with `slot` = "sofa_living" (+ optional `maxWidth`, `maxDepth` in metres for the panel to filter options). Keep it through optimization (`--keep-leaves true --keep-extras true`).
2. Each option: its own GLB, origin bottom-centre, +Y up, metres, ideally < ~2–5 MB (rule of thumb; Shopify's single-product guidance says < 15 MB, typical ~4 MB).
3. On select: load (guard with a generation counter so a slow earlier load can't overwrite a newer pick — `threejs-assets`), add under the slot, remove the old model and dispose its geometries/materials/textures if nothing else uses them (`threejs-performance`). Cache recently used options.
4. Collision: keep furniture out of the Octree (`nocollide`), or add one simple box per item to a separate small Octree. Rebuilding the room Octree on every swap is slow.
5. Shadows: don't rely on the room lightmap (it has no shadow for the new item, and keeps the old one if furniture was baked in). Use the item's own baked AO or real-time contact shading (`threejs-ambient-contact-shading`).

UI: a bottom sheet with thumbnails works on phones; HTML panels → `threejs-html`; interface polish skills (`impeccable` etc.) only if the user wants them (ask).

## Free furniture sources
| Source | Licence | Notes |
|---|---|---|
| Poly Haven | CC0, commercial OK, no attribution | furniture category had 85 models (API, 2026-10-22); blend/gltf/fbx/usd. If the page calls their API live, show "Powered by Poly Haven". Site logos/renders aren't CC0; no scraping without permission |
| Kenney Furniture Kit | CC0 | low-poly, stylised |
| Poly Pizza | per model (CC0, CC-BY, possibly NC/ND/SA) | check every model; CC-BY needs credit; NC can't be used commercially; API needs a key (free tier details 未验证) |
| Sketchfab | per model | account needed to download; check each licence |
| user's own Hunyuan3D | see `free-3d-assets` | not for EU/UK/South Korea users |

### IKEA
No public IKEA 3D model API or developer programme was found. Community scripts that grab the GLBs used by IKEA's own web previews exist, but they grant no licence to the assets, and IKEA's terms reserve rights to site content. **Don't scrape IKEA models and don't redistribute them.** For an "IKEA look" use CC0 models or model it; for a real commercial IKEA tie-in the user must get permission.

## Sources
- KHR_materials_variants: https://github.com/KhronosGroup/glTF/blob/main/extensions/2.0/Khronos/KHR_materials_variants/README.md
- three.js example: https://github.com/mrdoob/three.js/blob/r186/examples/webgl_loader_gltf_variants.html
- Blender manual (glTF Variants): https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html
- Poly Haven licence/API: https://polyhaven.com/license , https://github.com/Poly-Haven/Public-API
- Kenney: https://kenney.nl/assets/furniture-kit
- Shopify 3D checklist: https://help.shopify.com/partners/resources/creating-3d-models/3d-model-standards-checklist
- IKEA download script (secondary): https://github.com/apinanaivot/IKEA-3D-Model-Download-Button
