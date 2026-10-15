# Sollumz and FiveM clothing reference

Primary references:

- Sollumz basic clothes editing: https://docs.sollumz.org/tutorials/basic-clothes-editing
- Cfx.re resource manifest: https://docs.fivem.net/docs/scripting-reference/resource-manifest/
- Cfx.re data-file types: https://docs.fivem.net/docs/game-references/data-files/
- Sollumz repository: https://github.com/Sollumz/Sollumz

Verified component concepts:

- Freemode components are streamed parts in YDD containers and use a separate YFT skeleton.
- Common component codes include `head`, `berd`, `hair`, `uppr`, `lowr`, `hand`, `feet`, `teef`, `accs`, `task`, `decl`, and `jbib`. Confirm the actual target and current tool output instead of guessing from the garment name.
- `SHOP_PED_APPAREL_META_FILE` is a recognized FiveM data-file type for shop apparel metadata.
- Sollumz documentation warns that missing rigging/vertex groups can make an exported YDD fail to appear, and that streamed ped materials may require normal and specular textures.
- The official tutorial documents common vertex-color and freemode skin-texture behavior. Copy values only after confirming the target base asset and installed Sollumz version.

Diagnostic order:

1. Confirm target ped, generation, component, resource start, and manifest entries.
2. Confirm filenames and internal/embedded texture names.
3. Confirm skeleton import, bone names, vertex groups, and weights.
4. Confirm material/shader, diffuse/normal/specular/alpha, dimensions, and mipmaps.
5. Confirm LODs, geometry normals, back-face visibility, UVs, and vertex colors.
6. Compare against a known-good, legally obtained base component.

