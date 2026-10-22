# Optimizing the tour GLB with glTF-Transform

Tool: `@gltf-transform/cli` 4.5.1 (MIT, Node ≥ 20). Free. Online viewer/inspector: https://gltf.report/ (a website — ask before putting a client's private model into it).

Install (ask the user first): `npm install --global @gltf-transform/cli`, or without a global install `npx @gltf-transform/cli <command> ...` (downloads on first run). KTX2 commands (`uastc`, `etc1s`) also need **KTX-Software ≥ 4.4.0** (`ktx` on PATH, Apache-2.0).

## Why not `optimize`
`gltf-transform optimize` defaults (from the CLI source): `--instance true --palette true --simplify true --prune true --prune-attributes true --prune-solid-textures true --flatten true --join true --compress meshopt --texture-compress auto --texture-size 2048`. For a tour:

| Default | What it breaks |
|---|---|
| `--prune-attributes true` | deletes TEXCOORD_1 if no glTF texture references it — your code-loaded lightmaps don't, so the lightmap UVs vanish |
| prune `keepLeaves/keepExtras` false | deletes empty nodes that only carry extras (spawn, hotspots, furniture slots) |
| `--join`, `--flatten` | merges rooms, furniture and clickable objects; room/slot nodes disappear |
| `--simplify` | moves vertices: bent wall corners, broken lightmap UVs (rule of thumb — test before using) |
| `--palette` | merges materials; name-based swaps stop working |

If you must use `optimize`, switch these off explicitly: `--prune-attributes false --join false --flatten false --simplify false --palette false` (and note `optimize`'s prune still drops extras-only leaves — check the result).

## Step-by-step (recommended)
Work on copies; keep the Blender export untouched.

```bash
# 0. Inspect and validate the raw export
gltf-transform inspect model.glb
gltf-transform validate model.glb
python scripts/check_walkthrough_build.py model.glb

# 1. Merge duplicate meshes/materials/textures (keeps nodes)
gltf-transform dedup model.glb step1.glb

# 2. Remove unused data but keep lightmap UVs, extras and marker nodes
gltf-transform prune step1.glb step2.glb --keep-attributes true --keep-extras true --keep-leaves true

# 3. Texture size (phones: 2048 max is a common starting point, rule of thumb)
gltf-transform resize step2.glb step3.glb --width 2048 --height 2048

# 4. KTX2: UASTC for normal/ORM data, ETC1S for colour (pattern from the README)
gltf-transform uastc step3.glb step4.glb \
    --slots "{normalTexture,occlusionTexture,metallicRoughnessTexture}" \
    --level 4 --rdo --rdo-lambda 4 --zstd 18 --verbose
gltf-transform etc1s step4.glb step5.glb --quality 255 --verbose
#    No ktx installed? Use WebP instead of 4a/4b (smaller download, but full-size in GPU memory):
#    gltf-transform webp step3.glb step5.glb --slots "baseColor"

# 5. Geometry compression (decoder: three/addons/libs/meshopt_decoder.module.js)
gltf-transform meshopt step5.glb dist/model.glb --level medium

# 6. Check again — TEXCOORD_1, spawn, hotspots, rooms must still be listed
python scripts/check_walkthrough_build.py dist/model.glb
```

Alternative for step 5: `gltf-transform draco step5.glb dist/model.glb --method edgebreaker` (needs the Draco decoder files hosted). Meshopt output compresses further with gzip/brotli on the host; Draco output barely does.

## Lightmap files
Lightmaps live outside the GLB (glTF has no lightmap slot, and the GLTFLoader has no lightmap extension), so glTF-Transform doesn't touch them. Optimize them yourself:
- PNG/JPG at 1024–2048 per room atlas is a common start (rule of thumb). JPG artefacts show in dark gradients — compare.
- KTX2 lightmaps: `ktx create` (KTX-Software) — then load with `KTX2Loader` instead of `TextureLoader` in `main.js` (`loadLightmap`). 未验证 which ETC1S/UASTC settings keep smooth gradients; compare screenshots.
- EXR/HDR keeps dynamic range; needs `EXRLoader`/`HDRLoader` and is much larger.

## Splitting large tours
Over 25 MiB (Cloudflare Pages per-file limit), or first room should appear fast:
- Export one GLB per floor (best: each one is self-contained and loads independently).
- `gltf-transform partition` splits buffers into several `.bin` files (still one scene JSON; all parts load together). Output must be `.gltf`; check `gltf-transform partition --help` for the flags (未验证 here).

## GPU memory, quick arithmetic
2048² RGBA8 = 16 MiB, ≈ 21 MiB with mipmaps; 4096² ≈ 85 MiB. KTX2 transcoded to BC7/ASTC 4×4 ≈ 1/4 of that; ETC1S → ETC2 RGB ≈ 1/8 (Basis general knowledge, not checked item by item). WebP/JPG/PNG save download only — on the GPU they are full RGBA8.

## Sources
- glTF-Transform: https://github.com/donmccurdy/glTF-Transform (CLI source `packages/cli/src/cli.ts`, prune options `packages/functions/src/prune.ts`), docs https://gltf-transform.dev/cli
- npm: https://registry.npmjs.org/@gltf-transform/cli/latest
- KTX-Software: https://github.com/KhronosGroup/KTX-Software (minimum version from glTF-Transform `packages/cli/src/transforms/toktx.ts`)
- meshoptimizer / gltfpack (alternative tool, MIT): https://github.com/zeux/meshoptimizer/blob/master/gltf/README.md
