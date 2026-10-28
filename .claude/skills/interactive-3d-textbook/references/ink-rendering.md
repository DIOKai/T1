# Ink rendering: line-art 3D on white paper with selective glow (three.js r170, WebGLRenderer)

Read this before writing shaders or the postprocessing stack. Contents: 0 Recommended pipeline · 1 Outlines (decision table at the end of §1) · 2 Hatching · 3 Paper · 4 Glow and white paper · 5 Material injection and colour management · 6 Other repos and licences · Sources

**Desktop vs phone.** The full pipeline below (normal prepass + ink effect + bloom) is the desktop target. On touch devices or when frame time stays above ~25 ms: keep the normal prepass at `resolutionScale` 0.5–0.75, merge ink + bloom into the single `EffectPass`, skip MSAA (the pmndrs README recommends `antialias:false` on the renderer when using its composer; let the ink effect's smoothstep do the anti-aliasing), and render on demand (SKILL.md "Phone budget"). The book-and-popup note's "prefer `antialias:true` over FXAA" applies only when no postprocessing is used at all.

Research notes, 2026-10-28. Target: black-ink textbook illustration on off-white paper, with silhouette and crease lines, hatched shadows, paper grain, and a few vivid glowing "energy" elements. Stack: three r170 `WebGLRenderer` with optional pmndrs `postprocessing` v6.x. Every claim cites a source in [brackets]; the list is at the end. **UNVERIFIED** marks anything I did not confirm in source or by running it.

---

## 0. Recommended pipeline (summary)

1. **Base render** (pmndrs `RenderPass`): scene with plain lit materials. Use near-white albedo, because tone drives the hatching. Emissive "energy" meshes get `emissiveIntensity` > 1 so they exceed 1.0 in HDR.
2. **Normal + depth prepass**: render once more with `scene.overrideMaterial = MeshNormalMaterial`, into a half-float target that has a `DepthTexture` [S3][S4].
3. **One custom `Effect`** (merged by `EffectPass`) that:
   - runs Sobel on depth and normals to get the outlines;
   - turns luminance into hatch strokes;
   - darken-blends the ink over a paper texture [S9][S10].
   Energy pixels are masked out of the ink step.
4. **Bloom** with `luminanceThreshold ≈ 1.0` and `frameBufferType: HalfFloatType`, so only emissive pixels glow [S12][S13].
5. **Vignette and grain** last. Either use no tone mapping, or apply tone mapping before compositing the paper, so the paper stays white (§4).

Cost: roughly 2 scene renders plus 1–2 fullscreen passes plus bloom mips. The OutlineEffect route instead adds a full second scene draw (§1).

---

## 1. Outlines

### 1a. Screen-space edges on depth + normals (the default choice)

**Normal pass in r170.** `MeshNormalMaterial` writes `packNormalToRGB(normal)`, which is the view-space normal mapped to 0–1 [S4]. The official `RenderPixelatedPass` shows the r170 pattern [S3]:
- swap `scene.overrideMaterial` to a `MeshNormalMaterial`;
- render into a `WebGLRenderTarget` with `HalfFloatType` and `NearestFilter`;
- read depth from a `DepthTexture` attached to the beauty target.

Its edge shader uses 4 neighbours (not a full Sobel). The depth term is `clamp(neighbourDepth - depth)`. The normal term is `(1 - dot(n, nNeighbour))`, gated so that only the shallower pixel draws the line. Defaults are `normalEdgeStrength 0.3` and `depthEdgeStrength 0.4` [S3]. pmndrs also ships a `NormalPass` (MeshNormalMaterial, `resolutionScale`) [S14].

```js
// r170, my own sketch
const rt = new THREE.WebGLRenderTarget(w*dpr, h*dpr, { type: THREE.HalfFloatType,
  minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
rt.depthTexture = new THREE.DepthTexture(w*dpr, h*dpr);
const nMat = new THREE.MeshNormalMaterial();
function normalPass() {
  const o = scene.overrideMaterial, bg = scene.background;
  scene.overrideMaterial = nMat; scene.background = null;
  renderer.setRenderTarget(rt);
  renderer.setClearColor(new THREE.Color().setRGB(0.5, 0.5, 1)); // NOT new Color(0x8080ff)
  renderer.clear(); renderer.render(scene, camera);
  renderer.setRenderTarget(null); scene.overrideMaterial = o; scene.background = bg;
}
```

Gotcha (verified in r170 source): `Color.setHex` defaults to `SRGBColorSpace` [S5], and the clear colour is converted to the linear working space [S6]. So `0x8080ff` clears to about 0.216, not 0.5. Use `setRGB`, which takes working-space values.

**Sobel kernel.** Use 9 taps offset by `thickness * texel`, with `gx` from `[-1 0 1; -2 0 2; -1 0 1]` and `gy` as its transpose; the edge is `length(vec2(gx, gy))` [S9][S11]. Maxime Heckel's Moebius pass combines the two buffers as `outline = gradDepth*25.0 + gradNormal`, with `outlineThickness = 3.0` and no explicit threshold [S11]. spite's version Sobels only the normal buffer, then `aastep(.5, 1.-length(sobel))` [S9]. Use linear depth (`perspectiveDepthToViewZ` → `viewZToOrthographicDepth`) so the depth weight does not change with distance [S11].

The official `webgl_postprocessing_sobel` example only Sobels the *luminance* of the colour image (LuminosityShader → SobelOperatorShader) [S2]. It finds texture and lighting edges, not geometric creases, so it is wrong for this look.

**Animation and DPR.** Lines are recomputed every frame, so they work with skinned, morphed and instanced meshes for free. Skinning comes from the object, not the material; the risk is low, but I did not test the override with skinned meshes in r170 (UNVERIFIED). Vertex displacement added with `onBeforeCompile` is **not** in the normal pass, and those surfaces lose their creases. Heckel works around this by assigning a matching custom normal material per mesh [S11].

`thickness` is in render-target pixels. At DPR 2 the lines become half as wide in CSS pixels unless you multiply by `renderer.getPixelRatio()`. The official sobel example sets `resolution = innerWidth * devicePixelRatio` [S2]. Lines alias, so add SMAA/FXAA after them, or keep the smoothstep soft [S15 notes FXAA after outlines].

**Line wobble.** Offset every Sobel tap by a small noise vector: `hash(gl_FragCoord.xy) * sin(gl_FragCoord.y*0.08)` in x and `cos` in y, times `amplitude / resolution` [S11]. Because this hash is fixed per pixel, it does not boil, but the wobble stays fixed on screen while objects slide under it (see §3).

### 1b. Inverted hull — three's `OutlineEffect` (examples/jsm/effects)

After the normal render, it renders the scene a second time. Each material gets a BackSide `ShaderMaterial` that pushes vertices out along the projected normal: `pos + normalize(pos - pos2) * thickness * pos.w` [S1].
- Multiplying by `pos.w` makes thickness a constant fraction of the viewport, so it is independent of distance and DPR.
- It includes the skinning, morph and displacement chunks, so animated meshes work.
- Defaults: `defaultThickness 0.003`, `defaultColor [0,0,0]`, `defaultAlpha 1`. Per-material overrides go in `material.userData.outlineParameters` [S1].
- It skips materials with `wireframe` or `depthTest === false` [S1].

Downsides:
- It doubles draw calls.
- It only gives silhouettes plus some back-facing creases; sharp interior creases on flat-shaded parts are missed.
- Hard-edged (non-smoothed) normals split the hull at corners and leave gaps (general knowledge, UNVERIFIED here).
- It calls `renderer.render` itself, so with pmndrs you need a custom pass or `LambdaPass` around `effect.render`. I have not verified that this composes cleanly with pmndrs (UNVERIFIED).

### 1c. `EdgesGeometry` + `LineSegments2` / `LineMaterial` (exact crease lines)

`new EdgesGeometry(geo, thresholdAngle)` keeps edges whose face angle is above `thresholdAngle`, in degrees, default 1 [S7]. Convert with `new LineSegmentsGeometry().fromEdgesGeometry(edges)` [S8].

`LineMaterial.linewidth` is in pixels unless `worldUnits` is set; the example comment reads "in world units with size attenuation, pixels otherwise" [S8]. In r170, `LineSegments2.onBeforeRender` sets `resolution` automatically from `renderer.getViewport()` [S8]. `getViewport` returns the *logical* (CSS-pixel) viewport [S6], so line width is in CSS pixels and holds across DPR.

Use `alphaToCoverage: true` for smooth edges. It needs MSAA, so give the pmndrs composer `multisampling: 4` [S13]. UNVERIFIED that A2C works inside a pmndrs MSAA target.

Pitfalls:
- These are only *crease* lines. Silhouettes of smooth surfaces (sphere, torus) never appear, so pair this with 1a or 1b for silhouettes.
- Lines can z-fight with their own faces. Use `polygonOffset` on the mesh material (general practice, UNVERIFIED tuning).
- Under skinning or morphs, the lines do not deform with the mesh. Rigid animation (transform only) is fine.

### Decision table — which outline method when

| Need | Pick | Why / cost |
|---|---|---|
| Silhouettes + creases on everything, objects animate/deform | **1a depth+normal Sobel** | Recomputed per frame; 1 extra scene render + fullscreen pass. Scale thickness × DPR. |
| Crisp, exactly-placed technical crease lines on rigid CAD-like parts | **1c EdgesGeometry + LineSegments2** | Real pixel width (CSS px), DPR-stable; no silhouettes; doesn't follow skinning. |
| Bold silhouette only, skinned characters, no post stack | **1b OutlineEffect** | DPR/distance-stable; second full scene draw; misses interior creases. |
| Textbook look (recommended) | **1a for silhouettes + 1c for key mechanical creases** | 1c lines are drawn in the base render, so 1a ignores them unless they are in the normal pass. |
| Luminance Sobel (`webgl_postprocessing_sobel`) | Avoid for ink | Detects shading/texture, not geometry [S2]. |

---

## 2. Hatching / cross-hatching

### Tonal Art Maps (Praun, Hoppe, Webb, Finkelstein, SIGGRAPH 2001) [S16]

- A TAM is a grid of hatch images: columns are tones, rows are mip levels.
- **Nesting rule**: every stroke in image (ℓ,t) also appears in all darker and all finer images. As tone darkens or the camera approaches, existing strokes persist while new ones fade in, which avoids "swimming strokes".
- Mip levels are custom-built so that strokes keep the same *pixel* width at every level.
- The paper used 6 tones packed into the RGB channels of 2 textures, plus an implicit white (the paper colour).
- Blending is 6-way: 2 tones bracket each vertex's tone, and those are blended barycentrically across the 3 vertices.
- Finest images are 256×256 and toroidal.
- Cross-hatching schedule: horizontal strokes only for the first ~3 columns, vertical from about the 4th, both from about the 6th.
- An optional `clamp(8t-3.5)` transfer gives inkier strokes (they lengthen instead of greying), but it adds jaggies.
- Performance: 20–40 fps on a GeForce2.
- In a modern shader: compute `tone` per fragment and sample 2 RGB TAM textures with mipmaps. Lerp the 2 bracketing channels, `clamp(8t-3.5)` for the ink look. UVs need a sensible parametrization; the paper used lapped textures aligned to curvature.

### Screen-space vs object-space

Praun et al. explain the trade-off [S16]:
- **Screen-space**: easy constant stroke width, but a "shower-door effect": strokes look painted on glass while objects move behind them.
- **Object-space**: strokes stick to the surface, but density has to be managed with distance (which TAM mips handle).

The temporal-coherence trade-off in general is surveyed by Bénard, Bousseau and Thollot (CGF 2011) [S17]. For a mostly static textbook camera with slow orbit, screen-space post hatching is acceptable and much simpler. For objects moving across the frame, prefer object/world-space (triplanar) hatching.

### spite/sketch (MIT, Jaume Sanchez, #inktober 2020) [S9]

Built on three r120 with `#version 300 es` shaders. Two families:
1. **Material-based (`cross-hatch-*`)**: subclasses `MeshStandardMaterial` and uses `onBeforeCompile`.
   - The vertex shader adds world position and UV varyings.
   - After `#include <dithering_fragment>` it takes `l = 1 - luma(gl_FragColor)`, remapped with `smoothstep(range.x, range.y, l)`.
   - It generates **world-space triplanar** hatching with `texcube(worldPos, normal, l*10)`: `texh` iterates up to 10 noise-texture-driven stroke layers, and the count grows with darkness, so darker means more layers.
   - Strokes are thresholded with `smoothstep(.5-e, .5+e)`. The result is `mix(inkColor, paper, .25+.75*line)`, with the paper sampled in screen space via `gl_FragCoord / textureSize`.
   - Strokes are attached to the object (no shower door); paper is attached to the screen.
2. **Post-process (`post-*`)**:
   - Renders colour into one FBO and `MeshNormalMaterial` (DoubleSide) as `overrideMaterial` into another.
   - Edges: `normalEdge = aastep(.5, 1 - length(sobel(normalTex, uv, size, thickness)))`.
   - Hatching (`post-cross-hatch-i`): screen-space diagonal line families, `abs(mod(p.x ± p.y [- offset], 10.)) < e`, added at luma thresholds 1.0 / 0.8 / 0.6 / 0.4 / 0.2. The line width `e` is scaled by `length(dFdx, dFdy)` so it stays anti-aliased. Then `blendDarken(paper, ink, 1-r)`.
   - `post-technical` uses rotated sine-line hatching per tone band (`angleDark`, plus a second layer at +90°), plus a screen-blended light hatch.
   - Paper textures (Craft, Watercolor, Parchment) come from maxpacks paperpack. Check that licence separately (UNVERIFIED).
   - Pitfall I noticed: `aastep` is wrapped in `#ifdef GL_OES_standard_derivatives`. In GLSL ES 3.00 that macro is probably undefined, so it silently falls back to aliased `step` (UNVERIFIED).

### Heckel "Moebius-style post-processing" (2024-03-26) [S11]

- A custom `Pass` (pmndrs `Pass` + `FullScreenQuad`); the article notes R3F's `<EffectComposer>` did not accept custom passes.
- The normal material computes Blinn-Phong itself (`shininess 600`, `diffuseness 0.5`) and stores **diffuse light in the normal buffer's alpha**. Specular ≥ 0.25 is written white, so the Sobel outlines the highlights.
- Tone bands: luma ≤ 0.35 black, ≤ 0.45 ×0.25, ≤ 0.60 ×0.5, ≤ 0.75 ×0.7.
- Hatching is pixel stripes `mod(coord, 8.0) <= 1.0`: horizontal, vertical and diagonal layers at successive luma thresholds. The article's prose and code disagree on the order; the code uses 0.35, 0.55 and 0.80. Background is excluded with `depth <= 0.99`.

### Stippling

A grid of dots whose radius grows with darkness, mentioned by Heckel as a "raster" alternative [S11]. pmndrs/inkwell also has halftone effects [S18]. For an organic stipple, threshold a blue-noise texture against tone (general technique, UNVERIFIED source).

---

## 3. Paper look

- **Grain**: sample a tileable paper texture in screen space: `texture(paper, uv * resolution / paperSize)` [S9]. Ink with `min(paper, ink)` (darken) so the grain shows through the ink [S9]. pmndrs `TextureEffect` can overlay a texture with any `BlendFunction` [S14].
- **Off-white background**: use something like `#F4EFE4`. Set the paper's `texture.colorSpace = SRGBColorSpace`, since it is a colour texture [S5].
- **Vignette**: pmndrs `VignetteEffect` (`offset 0.5`, `darkness 0.5` defaults) [S14]. Keep it subtle (darkness ~0.2–0.3, my suggestion).
- **Wobble without distracting boil**:
  - Noise fixed in screen space does not flicker, but it gives a shower-door look [S16][S11].
  - Noise reseeded every frame boils like hand-drawn animation; this is very distracting in a textbook.
  - Middle ground: reseed at a stepped rate. inkwell provides `steppedTime` / `steppedJitter` for "on twos" (~12 fps) [S18].
  - Or drive the noise in object/world space (triplanar, like spite's material hatching) so the wobble moves with the surface [S9].
  - For a technical illustration, use small amplitude (≤1 px) and no time variation (my recommendation).

---

## 4. Ink + selective glow, and keeping the paper white

- **Threshold bloom** (pmndrs `BloomEffect`): defaults are `luminanceThreshold 1.0`, `luminanceSmoothing 0.03`, `mipmapBlur true`, `intensity 1.0`, `radius 0.85`, `levels 8`, blend `SCREEN` [S12].
  - Keep paper and ink at or below 1.0, and give energy meshes emissive above 1 (for example `emissiveIntensity 3–6`, my estimate).
  - This **requires** `new EffectComposer(renderer, { frameBufferType: HalfFloatType })`. The default `UnsignedByteType` clamps to [0,1], so nothing exceeds the threshold [S13].
  - This is the cheapest option: no extra scene renders.
- **`SelectiveBloomEffect`**: `new SelectiveBloomEffect(scene, camera, opts)` then `effect.selection.add(mesh)`, with options `inverted` and `ignoreBackground` [S12b]. Internally it adds a `DepthPass` and a depth-mask pass, so it costs an extra scene render. Use it only if glowing objects can't be pushed above 1.0 (for example in LDR buffers).
- **three's own approach** (`webgl_postprocessing_unreal_bloom_selective`):
  - Put glowing objects on layer `BLOOM_SCENE = 1`.
  - Swap every other mesh to a black `MeshBasicMaterial`, render the bloom composer, restore materials.
  - Mix the result into the final composer, with an `OutputPass` at the end [S19].
  - That is 2 scene renders plus a material swap per frame.
- **Make the ink skip the glow**: write an "energy" mask. Either use the normal-pass alpha, the way Heckel stores light there [S11], or test `luma > 1.0` in the HDR input. Then skip hatching and outlines on those pixels so the colour stays vivid. My design, UNVERIFIED in practice.
- **Glow on white paper**: SCREEN or ADD blending onto ~0.95 paper has almost no headroom, so halos disappear except over ink. Options (my suggestions, UNVERIFIED):
  - darken the paper slightly (~0.9);
  - use saturated emissive colours so the hue shift is visible;
  - or composite the bloom with an alpha/normal-style blend (`mix(paper, glowColor, bloomAlpha)`) via the effect's `blendFunction` [S14].
- **Tone mapping vs white paper** (computed from the r170 tone-mapping GLSL [S20], my port):
  - ACES Filmic maps linear 1.0 to **#E2E2E2**, and paper `#F4EFE4` to **#DFDDDA** (grey).
  - Khronos Neutral maps 1.0 to **#F0F0F0**, and paper to **#EBE6DB**.
  - So either use **no tone mapping** (`NoToneMapping`), with the paper composited in LDR and only emissives in HDR; or put `ToneMappingEffect` *before* the paper/ink composite.
  - pmndrs says to keep `renderer.toneMapping = NoToneMapping` and use `ToneMappingEffect` (modes include `AGX`, `NEUTRAL`, `ACES_FILMIC`) at the end of the pipeline [S13][S14].

---

## 5. Injecting into materials in r170, and colour management

- **`onBeforeCompile(shader, renderer)`**: modify `shader.vertexShader` / `fragmentShader` with `.replace('#include <chunk>', ...)` and add uniforms on `shader.uniforms`. spite inserts after `#include <dithering_fragment>` to post-process the lit colour [S9].
  - The program cache key defaults to `onBeforeCompile.toString()`. Override `customProgramCacheKey()` if materials share code but differ in defines [S21].
  - WebGLRenderer only. It breaks silently when a chunk name changes between releases, so pin three.
  - Lighting, shadows, skinning and fog keep working, which is the main reason to prefer it over `ShaderMaterial` for "lit, then inked" materials.
- **`ShaderMaterial`**: full control but no built-in lighting. You must add `#include <colorspace_fragment>` (and `tonemapping_fragment` if wanted) yourself; the manual says: "Custom materials based on ShaderMaterial and RawShaderMaterial have to implement their own output color space conversion" [S5].
- **Colour management (r170)**:
  - `ColorManagement.enabled` is true by default.
  - `renderer.outputColorSpace` defaults to `SRGBColorSpace` [S5][S6].
  - Colour textures (map, emissiveMap, paper) need `colorSpace = SRGBColorSpace`; data textures (normal, noise, TAM hatch masks) stay `NoColorSpace` [S5]. Treat TAM/noise textures as data, or their tone curve shifts.
  - Hex colours are sRGB and converted to linear [S5].
  - When rendering to a render target, r170 writes linear and skips tone mapping; output encoding happens only on the canvas [S6].
  - With pmndrs, setting `outputColorSpace = SRGBColorSpace` is enough; it encodes at the end [S13].
  - With three's own `EffectComposer` (HalfFloat targets by default [S22]), end with `OutputPass` [S19].
- **pmndrs custom `Effect`**: write `mainImage(const in vec4 inputColor, const in vec2 uv, out vec4 outputColor)`. Declaring `EffectAttribute.DEPTH` gives `depthBuffer`, `readDepth(vec2 uv)`, `getViewZ(depth)`, `cameraNear/Far`, `resolution` and `texelSize` [S14]. All effects in one `EffectPass` merge into a single shader [S13].
- **pmndrs version**: v6.39.5 (2026-09-09) has peer dependency `three >= 0.168.0 < 0.187.0`, which includes r170 [S13]. The pmndrs README recommends `antialias:false, stencil:false, depth:false` on the renderer [S13].

---

## 6. Other repos (licence checked with `gh api repos/X --jq .license.spdx_id`)

| Repo | Licence | What's useful | Notes |
|---|---|---|---|
| mrdoob/three.js @ r170 | MIT | OutlineEffect, RenderPixelatedPass (depth+normal edges), LineSegments2, sobel / toon / selective-bloom examples | Primary reference |
| pmndrs/postprocessing | **Zlib** | BloomEffect, SelectiveBloomEffect, NormalPass, ToneMappingEffect, TextureEffect, VignetteEffect, custom Effect API | v6.39.5 |
| spite/sketch | MIT | Triplanar material hatching via onBeforeCompile; post Sobel(normals) + screen hatching + paper | three r120; paper JPGs from maxpacks, licence UNVERIFIED |
| VelkinaStudio/inkwell | MIT | pmndrs Effects: InkOutline (Sobel depth+luma, jitter), Halftone, Posterize, on-twos timing | v0.1.0. **Likely bug**: `readDepthAt` calls `readDepth(texture2D(depthBuffer, uv).r)`, but pmndrs only defines `readDepth(vec2)`, so this would not compile as written (read from source, not run: UNVERIFIED). Its outline uses depth+luma, not normals, so it misses creases on smooth surfaces. |
| plasmo310/three-toon-outline-material | MIT | Toon + outline material (Japanese README) | Not inspected in depth |
| OmarShehata/webgl-outlines | MIT | Depth + normal post outlines with FXAA, plus a "surface ID" variant for cleaner creases, and a selective-outline PR | Last pushed 2022 |

---

## Sources

- [S1] three.js r170 `examples/jsm/effects/OutlineEffect.js` — https://github.com/mrdoob/three.js/blob/r170/examples/jsm/effects/OutlineEffect.js (MIT)
- [S2] three.js r170 `examples/webgl_postprocessing_sobel.html` — https://github.com/mrdoob/three.js/blob/r170/examples/webgl_postprocessing_sobel.html (MIT)
- [S3] three.js r170 `examples/jsm/postprocessing/RenderPixelatedPass.js` — https://github.com/mrdoob/three.js/blob/r170/examples/jsm/postprocessing/RenderPixelatedPass.js (MIT)
- [S4] three.js r170 `src/renderers/shaders/ShaderLib/meshnormal.glsl.js` — https://github.com/mrdoob/three.js/blob/r170/src/renderers/shaders/ShaderLib/meshnormal.glsl.js
- [S5] three.js r170 Color management manual — https://github.com/mrdoob/three.js/blob/r170/docs/manual/en/introduction/Color-management.html and https://threejs.org/docs/#manual/en/introduction/Color-management; `src/math/Color.js` (`setHex(hex, colorSpace = SRGBColorSpace)`)
- [S6] three.js r170 `src/renderers/WebGLRenderer.js` (getViewport, outputColorSpace, render-target linear/no tone mapping) and `src/renderers/webgl/WebGLBackground.js` — https://github.com/mrdoob/three.js/tree/r170/src/renderers
- [S7] three.js r170 `src/geometries/EdgesGeometry.js` and docs — https://threejs.org/docs/#api/en/geometries/EdgesGeometry
- [S8] three.js r170 `examples/jsm/lines/{LineMaterial,LineSegments2,LineSegmentsGeometry}.js`, `examples/webgl_lines_fat.html` — https://github.com/mrdoob/three.js/tree/r170/examples/jsm/lines
- [S9] spite/sketch (MIT): `cross-hatch-i/crossHatchMaterial.js`, `post-cross-hatch-i/post.js`, `post-technical/post.js`, `shaders/{sobel,aastep,blend-darken}.js`, `js/paper.js` — https://github.com/spite/sketch, demo https://spite.github.io/sketch/
- [S10] (folded into S9 and S11)
- [S11] Maxime Heckel, "Moebius-style post-processing and other stylized shaders", 2024-03-26 — https://blog.maximeheckel.com/posts/moebius-style-post-processing/
- [S12] pmndrs/postprocessing v6.39.5 `src/effects/BloomEffect.js` — https://github.com/pmndrs/postprocessing/blob/v6.39.5/src/effects/BloomEffect.js (Zlib)
- [S12b] `src/effects/SelectiveBloomEffect.js` — https://github.com/pmndrs/postprocessing/blob/v6.39.5/src/effects/SelectiveBloomEffect.js
- [S13] pmndrs/postprocessing README (Output Color Space, Tone Mapping, Performance) and `package.json` — https://github.com/pmndrs/postprocessing ; docs https://pmndrs.github.io/postprocessing/public/docs/
- [S14] pmndrs/postprocessing v6.39.5 sources: `src/passes/NormalPass.js`, `src/effects/{TextureEffect,VignetteEffect,ToneMappingEffect}.js`, `src/enums/{ToneMappingMode,EffectAttribute}.js`, `src/materials/glsl/effect.frag` — https://github.com/pmndrs/postprocessing/tree/v6.39.5/src
- [S15] OmarShehata/webgl-outlines (MIT) — https://github.com/OmarShehata/webgl-outlines ; article https://omar-shehata.medium.com/how-to-render-outlines-in-webgl-8253c14724f9
- [S16] Praun, Hoppe, Webb, Finkelstein, "Real-Time Hatching", SIGGRAPH 2001, pp. 581–586 — https://hhoppe.com/proj/hatching/ , PDF https://hhoppe.com/hatching.pdf
- [S17] Bénard, Bousseau, Thollot, "State-of-the-Art Report on Temporal Coherence for Stylized Animations", CGF 30(8), 2011 — https://diglib.eg.org/handle/10.1111/v30i8pp2367-2386 (abstract only read)
- [S18] VelkinaStudio/inkwell (MIT) — https://github.com/VelkinaStudio/inkwell (README, `src/effects/InkOutlineEffect.js`)
- [S19] three.js r170 `examples/webgl_postprocessing_unreal_bloom_selective.html` — https://github.com/mrdoob/three.js/blob/r170/examples/webgl_postprocessing_unreal_bloom_selective.html
- [S20] three.js r170 `src/renderers/shaders/ShaderChunk/tonemapping_pars_fragment.glsl.js` — https://github.com/mrdoob/three.js/blob/r170/src/renderers/shaders/ShaderChunk/tonemapping_pars_fragment.glsl.js (hex results computed by my Python port of ACESFilmic/Neutral; AgX not computed)
- [S21] three.js r170 `src/materials/Material.js` (`onBeforeCompile`, `customProgramCacheKey`)
- [S22] three.js r170 `examples/jsm/postprocessing/EffectComposer.js` (default `HalfFloatType` targets)
- Also: Codrops, Maya Nedeljković, "Sketchy Pencil Effect with Three.js Post-Processing", 2022-11-29 — https://tympanus.net/codrops/2022/11/29/sketchy-pencil-effect-with-three-js-post-processing/ (not read in full; cited by Heckel for noise-texture line displacement); plasmo310/three-toon-outline-material (MIT) — https://github.com/plasmo310/three-toon-outline-material
