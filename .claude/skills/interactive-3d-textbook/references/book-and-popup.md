# Book and pop-up: the open book, page turn, pop-up rise, camera, text, phone budget, sound (three.js r170, WebGLRenderer)

Read this before building the book scene. Contents: 1 Modelling and lighting the book · 2 Page turn · 3 Pop-up effect (shear rise, pen-drawn lines) · 4 Camera · 5 Text on pages · 6 Phone budget · 7 Audio cues and Freesound licensing · Sources

Two layers, two treatments (as in the reference genre): the **book and desk** are the "real world" — softly lit paper, cloth cover, desk mat, window light and a contact shadow; the **diagram** that rises off the page is ink line-art on white card (ink-rendering.md). Keep that split clean: every part of the diagram is inked, nothing on the book is.

Scope: an open book on a desk. Each lesson's diagram rises off the page like a pop-up, pages turn between lessons, and the scene stays light enough for phones. Claims cite sources (list at the end). **UNVERIFIED** marks anything not confirmed in a primary source. Snippets are written for this note; none are copied from unlicensed code.

Reference build studied: **kouki-takezawa/popup-art-book** (MIT, confirmed with `gh api ... --jq .license.spdx_id` → `MIT`). It is a build-free Three.js **r128** pop-up book with 10 spreads, procedural canvas textures, and no image files [S1]. Its techniques port to r170 unchanged.

---

## 1. Modelling and lighting the book

**Structure, following popup-art-book [S1 README "本の作り", js/book.js]:**
- Covers are cloth-covered boards: 0.3 thick and 0.4 larger than the pages on each side. The pages are 0.15-thick card. The page edges show paper layers. The left and right stacks swap thickness as pages turn, so the visible stack depth changes with the page number.
- A **rounded spine** strip joins both covers. Page roots sit on that arc. Each page's root (width ~1 unit) is a **flexible hinge ribbon**: a cubic Bezier from the spine point to the rigid page board, rebuilt each frame (`makeRibbon`/`setRibbon`), so it sinks into the gutter.
- Gutter darkening is **painted into the page CanvasTexture** (`gutter()`), not lit. That costs nothing at runtime.

**Slight page curvature (own suggestion):** use one subdivided `PlaneGeometry` per visible top page, with about 24 segments across the page and 1–2 along the spine. Sag the vertices near the gutter: `y = stackTop - sag * (1 - smoothstep(0, gutterW, s))`, where `s` is the distance from the spine. Reuse the page-bend function in §2 with a small fixed curl and you get the classic lifted-page profile.

**Lighting:**
- **Soft window light:** one `DirectionalLight` (or `SpotLight`) casting shadows, plus a `HemisphereLight` for fill. With `PCFSoftShadowMap`, `shadow.radius` **has no effect**. The docs say to get softness by *decreasing* `mapSize` instead [S3 LightShadow]. popup-art-book uses `PCFSoftShadowMap`, a 2048 map (1024 on small touch screens), and `bias = -0.0004` [S1 js/book.js L15, js/common.js].
- **Window gobo/cookie:** `SpotLight.map` modulates the light colour by a texture, and the docs describe a "cookie-like masking effect". **Warning from the docs: `.map` is disabled if `.castShadow` is false** [S3 SpotLight]. Example settings in r170: `angle = π/6`, `penumbra = 1`, `decay = 2`, `shadow.mapSize = 1024`, `shadow.focus = 1` [S4 webgl_lights_spotlight]. On phones, a cheaper option with the same look is to **bake the window-pane light pattern into the desk texture**, or to lay a transparent multiply decal plane on the desk. That costs zero extra passes (own suggestion).
- **Contact shadow under the book:** the r170 example `webgl_shadow_contact` renders the object from below with an `OrthographicCamera` into a 512×512 `WebGLRenderTarget`, using a `MeshDepthMaterial` patched in `onBeforeCompile` to output `(1 - fragCoordZ) * darkness`. It then blurs with `HorizontalBlurShader`/`VerticalBlurShader` onto a transparent plane [S4 webgl_shadow_contact]. **The book never moves on the desk, so render this once**, or ship a pre-blurred PNG blob shadow.
- **Shadow updates on demand:** set `renderer.shadowMap.autoUpdate = false` and `shadowMap.needsUpdate = true` only on frames where the page or pop-ups move. The r170 `WebGLShadowMap.render` returns early when both flags are false [S5 WebGLShadowMap.js L66–75]. popup-art-book does exactly this [S1 js/common.js, js/book.js L798].

## 2. Page turn

| Approach | Cost | Notes |
|---|---|---|
| **CPU per-frame vertex bend** of a subdivided plane | ~30×2 segments → <100 verts; trivial | Easy to raycast. Shadows stay correct automatically. Recommended. |
| **Vertex-shader bend** (`onBeforeCompile` on `begin_vertex`) | Free on CPU | Must also patch `customDepthMaterial` or shadows stay flat. Bounding sphere goes stale, so set `frustumCulled = false` or enlarge it. |
| **SkinnedMesh + bone chain** | Bone matrices per frame | Works [S6 SkinnedMesh/Bone docs], but a single chain gives limited bend detail (three.js forum thread [S7]). Overkill unless pages are authored in Blender. |
| **Cone deformation** (Hong, Card, Chen 2006, "Turning Pages of 3D Electronic Books") | Per-vertex trig | Realistic corner curl. Open implementation: prideout/pageturn (Apache-2.0) [S8]. |

**Inextensible arc bend (own code).** The page is a strip whose bend angle grows linearly from spine to edge, φ(s) = φ₀ + k·s. Integrating gives exact positions that preserve arc length, so the paper never stretches:

```js
// Page mesh lives in a Group at the spine; spine runs along local Z, Y is up.
const geo = new THREE.PlaneGeometry(W, H, 32, 2);
const P = geo.attributes.position, N = geo.attributes.normal;
const s0 = new Float32Array(P.count), w0 = new Float32Array(P.count);
for (let i = 0; i < P.count; i++) { s0[i] = P.getX(i) + W / 2; w0[i] = P.getY(i); }

function bendPage(t, curl = 1.2) {            // t: 0 = lying right, 1 = lying left
  const phi0 = Math.PI * t;
  const k = -curl * Math.sin(Math.PI * t) / W; // free edge lags; flip sign after t>.5 for follow-through
  for (let i = 0; i < P.count; i++) {
    const s = s0[i], phi = phi0 + k * s, flat = Math.abs(k) < 1e-5;
    const x = flat ? s * Math.cos(phi0) : (Math.sin(phi) - Math.sin(phi0)) / k;
    const y = flat ? s * Math.sin(phi0) : (Math.cos(phi0) - Math.cos(phi)) / k;
    P.setXYZ(i, x, y, w0[i]);
    N.setXYZ(i, -Math.sin(phi), Math.cos(phi), 0);   // analytic normal, no computeVertexNormals
  }
  P.needsUpdate = N.needsUpdate = true;
  geo.computeBoundingSphere();
}
```

**Cone curl (summary of prideout/pageturn `pageDeformer.ts`, Apache-2.0 [S8]).** For texcoord (u,v), cone apex `A` (on the spine line) and angle θ: `r = √(u² + (v−A)²)`, `d = r·sinθ`, `α = asin(u/r)`, `β = α/sinθ`. Then `x = d·sinβ`, `y = r + A − d(1−cosβ)sinθ`, `z = d(1−cosβ)cosθ`. θ and A are animated over time, and the whole page also rotates about the spine. The US patent 7,898,541 by the same authors describes a cone angle that starts at 90° and reaches its minimum at mid-animation [S9].

**Timing feel:** popup-art-book drives each page with a spring rather than a fixed tween. It uses `K = 260` (covers `K = 170`), damping `C = 2·0.5·√K` (damping ratio 0.5), 120 Hz sub-steps, and a bounce of 0.3 against the page stack. The root flexes first and the page lands with a small rebound. Under `prefers-reduced-motion` it switches to critical damping with no bounce [S1 js/book.js `stepSprings`].

**Front/back textures:** use two meshes sharing the same geometry, one `side: FrontSide` with page N and one `side: BackSide` with page N+1. Mirror the back texture (`wrapS = RepeatWrapping; repeat.x = -1`) or flip its UVs. Alternatively, use one material with `gl_FrontFacing` in `onBeforeCompile`. popup-art-book swaps materials per side of a hinge mesh (`setPageMat`) [S1].

**Page content as texture:**
- **CanvasTexture:** draw the page with Canvas 2D and set `texture.needsUpdate = true` after redrawing [S10 manual canvas-textures]. For crisp text, size the canvas at roughly the *on-screen* page size × `min(devicePixelRatio, 2)`, capped at 2048 px. Set `texture.anisotropy = renderer.capabilities.getMaxAnisotropy()`, because the page is seen at a grazing angle. Both APIs exist in r170 [S5 Texture.js, WebGLCapabilities.js], and popup-art-book does this with a 2048 cap [S1 common.js `tex()`]. Keep `colorSpace = SRGBColorSpace` for colour canvases.
- **Memory:** after upload, popup-art-book shrinks the source canvas to 1×1. It builds only the open spread plus one on each side and disposes the rest [S1 README "処理を軽くするしくみ", book.js `dispose`/`trim`].

## 3. Pop-up effect

**How popup-art-book folds parts up [S1 js/common.js header, js/book.js `setPop`/`applyOpen`/`popReach`]:**
1. Each pop-up group is a **parallelogram (parallel) fold made with a shear matrix, not a rotation**. The group's local Y axis tilts from lying flat toward the gutter (angle a = 0) to upright (a = π/2), while its footprint stays put. Horizontal planes stay horizontal, which matches a real parallel fold, where faces stay parallel to one page or the other.
2. Each group has a fold direction `[dx, dz]` (into the page interior), a `delay`, a `dur` (default 1.1 s) and a `layer` (stacking order when flat).
3. **Layer lift:** while folded, each layer is raised 0.03 × layer, and the lift fades to 0 by a = π/2. The README notes that a folded part's tilt must stay smaller than the layer step, or parts poke through and z-fight.
4. **Collision cap:** at build time it measures each group's max *height ÷ distance from the gutter* (`r`). It then limits the angle to `asin(min(1, 0.9·tan(open)/r))`, so parts never pass through the facing page as the book closes.
5. **Easing:** `easeOutBack` with overshoot c1 = 1.4. Parts rise top layer first, and fold back in about 1.5 s before any page turn. Under reduced motion it uses ease-in-out at 2× speed.
6. Parts that never animate are **merged per material** after building. Animated parts are flagged `userData.live`.

Own minimal version of the shear rise:

```js
function setRise(g, a, dir, base, layer) {   // dir = unit [dx,dz] toward the gutter
  const c = Math.cos(a), s = Math.max(1e-3, Math.sin(a)); // det = s; never 0 (normalMatrix inverse)
  const lift = layer * 0.002 * (1 - a / (Math.PI / 2));
  g.matrixAutoUpdate = false;
  g.matrix.set(1, c * dir[0], 0, base.x,
               0, s,          0, base.y + lift,
               0, c * dir[1], 1, base.z,
               0, 0,          0, 1);
  g.matrixWorldNeedsUpdate = true;
}
const easeOutBack = (k, c1 = 1.4) => 1 + (c1 + 1) * (k - 1) ** 3 + c1 * (k - 1) ** 2;
// per frame: a_i = easeOutBack(clamp((t - delay_i) / dur_i, 0, 1)) * Math.PI / 2
```

**True hinged flaps (V-folds, angled pieces):** put each flap in a `Group` whose origin sits on the fold line and rotate it about that axis. In a real V-fold the flap angles are coupled to the page-opening angle. Glassner's "Interactive Pop-up Card Design" (IEEE CG&A Jan 2002; MSR-TR-98-03) gives the closed-form geometry for single-slit, asymmetric single-slit and V-fold mechanisms [S11], and Okamura & Igarashi build on it [S12]. **UNVERIFIED:** the exact formulas, because the PDFs could not be text-extracted here. In this app the book stays open at 180°, so you can animate flap angles directly ("rising from a flat page") without solving the full linkage.

Li et al., "Popup: Automatic Paper Architectures from 3D Models" (SIGGRAPH 2010) generates architectures from **two sets of parallel patches** that are guaranteed physically realizable and stable [S13]. That is a good mental model for diagram pieces: vertical cards parallel to the back page, horizontal shelves parallel to the base page.

**Staggering:** 80–150 ms between parts, top-down or along the reading order, total ≤ 1.5 s (popup-art-book's whole rise runs about 4.6 s with a camera tour; shorter suits lessons). These are rules of thumb. **UNVERIFIED** as a standard.

**Pen "drawing-on" effect with fat lines (r170 `LineMaterial`):** `LineMaterial` has `dashed`, `dashSize`, `gapSize`, `dashScale` and `dashOffset`. The fragment shader discards when `mod(vLineDistance + dashOffset, dashSize + gapSize) > dashSize` [S5 LineMaterial.js L14–16, L320]. `computeLineDistances()` returns `this` and stores `instanceDistanceStart/End` [S5 LineSegments2.js L241–262]. `resolution` is set automatically in `onBeforeRender` from the viewport [S5 LineSegments2.js L361]. `linewidth` is in pixels unless `worldUnits = true` [S4 webgl_lines_fat L108].

```js
import { Line2 } from 'three/addons/lines/Line2.js';
import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
const geo = new LineGeometry().setPositions(flatXYZ);
const mat = new LineMaterial({ color: 0x23201c, linewidth: 2.5, dashed: true });
const line = new Line2(geo, mat).computeLineDistances();
const end = geo.attributes.instanceDistanceEnd;
const L = end.getX(end.count - 1);           // total length
mat.dashSize = mat.gapSize = L;              // one dash, period 2L
function drawOn(p) {                          // p: 0..1
  line.visible = p > 0;                       // at p=0 the round cap still shows a dot
  mat.dashOffset = L * (1 - p);              // visible where distance <= p*L
}
```

Alternatives:
- For filled shapes, a reveal shader (`onBeforeCompile`, `if (vUv.x > uProgress) discard;`).
- Redrawing strokes progressively into a small CanvasTexture. Each redraw re-uploads the texture, so keep that canvas small.

## 4. Camera

`PerspectiveCamera.fov` is the **vertical** FOV in degrees [S6 PerspectiveCamera]. Fit the open book's bounding circle (radius r) in both directions:

```js
function fitDistance(camera, r, margin = 1.08) {
  const v = THREE.MathUtils.degToRad(camera.fov);
  const h = 2 * Math.atan(Math.tan(v / 2) * camera.aspect);
  return (r * margin) / Math.sin(Math.min(v, h) / 2);   // portrait → h is the limiting angle
}
```

- **Portrait phones (aspect < 1):** the whole spread becomes tiny. Prefer framing **only the current page** (diagram page), or raise the pitch toward top-down, and put the lesson text in HTML below the canvas. Optionally widen the FOV to 55–60° (rule of thumb, **UNVERIFIED**). popup-art-book uses FOV 50 and refits on `resize` [S1 common.js, book.js].
- **OrbitControls limits (r170 property names [S5 OrbitControls.js L61–97]):** `minPolarAngle`/`maxPolarAngle` (0 = straight down; keep `maxPolarAngle` around 1.1 rad so the camera never dips below the desk), `minAzimuthAngle`/`maxAzimuthAngle` (for example ±0.6 rad), `minDistance`/`maxDistance`, `enablePan = false`. `enableDamping` (default `false`, `dampingFactor` 0.05) requires calling `controls.update()` every frame, which conflicts with render-on-demand (manual note [S10 rendering-on-demand]).
- **Focus move on page turn:** tween `controls.target` and `camera.position` together over about 0.8–1.2 s with ease-in-out, and disable the controls while tweening. popup-art-book keeps the user's orbit and distance across page turns and blends tour poses with a cubic `easeIO` [S1 book.js].

## 5. Text on pages

| Method | Crispness | Accessibility / selection | Cost |
|---|---|---|---|
| **troika-three-text** (MIT, v0.53.0, peer `three >= 0.125.0`) | SDF glyphs; `sdfGlyphSize` (default 64, power of 2) trades sharpness for memory | Not in the DOM, so not read by screen readers or selectable | Font parsing and SDF generation run in a web worker. `preloadFont({font, characters})`. WOFF2 not supported. Call `dispose()` [S14] |
| **CanvasTexture** | Good if sized to screen px × DPR and anisotropic | Same as above | One texture upload per page |
| **HTML overlay** (projected `Vector3.project(camera)` → CSS transform, or `CSS3DRenderer`) | Native crisp text | Selectable, translatable, screen-reader friendly | DOM layout. Not occluded by WebGL objects; sorting needs care (manual `align-html-elements-to-3d` uses `z-index: 0` stacking contexts [S10]). `CSS3DRenderer`/`CSS2DRenderer` ship in r170 `examples/jsm/renderers` [S5] |

**Recommendation:** keep the **real lesson text in semantic HTML** (headings, lists, `<figure>` captions), always present in the document flow or in a side panel on desktop and a sheet below on mobile. Render a *decorative* copy on the page texture and mark the canvas `aria-hidden="true"` (or give it a short `aria-label`). This keeps text selectable, translatable, zoomable and searchable. troika's CJK coverage depends on its Noto fallback fonts, which load from jsDelivr by default (self-hosting the full set is about 300 MB) [S14]. For Chinese text, a CanvasTexture using the page's own web font is simpler.

## 6. Phone performance budget

- **Pixel ratio:** `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))` (manual "Handling HD-DPI" explains the trade-off [S10 responsive]). popup-art-book also adapts it at runtime: starting at min(2, dpr), it drops by 0.25 (floor 0.75) when average frame time exceeds 1/40 s, and raises it again after three good windows under 1/55 s, measured only on frames it actually drew [S1 book.js `adaptPR`].
- **Render on demand:** render only when something changed: controls `change`, resize, animation in progress [S10 rendering-on-demand]. popup-art-book uses an `invalidate()` flag [S1]. Stop the loop with `renderer.setAnimationLoop(null)` (documented in r170 [S3 WebGLRenderer]) on `visibilitychange` when `document.hidden` [S15].
- **Draw calls:** read `renderer.info.render.calls`. Target ≤ ~100 on phones (rule of thumb, **UNVERIFIED**). Merge static pop-up parts by material, as popup-art-book does (`mergeStatic`).
- **Textures:** ≤ 2048² per page (1024² on phones). Dispose spreads more than ±1 away. Use KTX2/Basis for any photographic textures (own suggestion).
- **Shadows:** one shadow-casting light, `autoUpdate = false`, 1024 map on touch devices [S1]. Contact shadow rendered once or baked.
- **Postprocessing:** every full-screen pass costs fill rate at DPR². Avoid it on phones, or use at most one combined pass. Prefer `antialias: true` on the context over FXAA/SMAA passes (rule of thumb, **UNVERIFIED**).
- **Reduced motion:** honour `matchMedia('(prefers-reduced-motion: reduce)')`: shorter turns, no overshoot, no camera tour [S1].

## 7. Audio cues (page turn, flap, pen, stamp)

- **Unlocking:** create or resume the `AudioContext` inside a user gesture. A context created outside a gesture starts `suspended`, so call `audioCtx.resume()` in a click/pointer handler when `state === "suspended"` [S16 MDN Best practices]. Firefox blocks Web Audio until sticky activation (`media.autoplay.block-webaudio`), and `navigator.getAutoplayPolicy("audiocontext")` can query the policy where supported [S17 MDN Autoplay guide].
- **Sprite playback:** decode one MP3 once (`decodeAudioData`), then for each cue create a **new** `AudioBufferSourceNode` (a node can be started only once; calling it again throws `InvalidStateError`) and call `start(when, offset, duration)`. Offset and duration are in seconds and are independent of `playbackRate` [S18].

```js
// sprite.json: { "turn":[0,0.62], "flap":[0.8,0.25], "pen":[1.2,0.9], "stamp":[2.3,0.3] }
let ctx, buf, map;
async function initAudio() {                       // call from first pointerdown
  ctx ??= new AudioContext();
  if (ctx.state === 'suspended') await ctx.resume();
  if (!buf) {
    map = await (await fetch('sfx/sprite.json')).json();
    buf = await ctx.decodeAudioData(await (await fetch('sfx/sprite.mp3')).arrayBuffer());
  }
}
function play(name, gain = 1, rate = 1) {
  if (!buf || muted) return;
  const [off, dur] = map[name], src = ctx.createBufferSource(), g = ctx.createGain();
  src.buffer = buf; src.playbackRate.value = rate; g.gain.value = gain;
  src.connect(g).connect(ctx.destination);
  src.start(0, off, dur);
}
```

Tips:
- Vary `rate` by ±5% for repeated flaps.
- Leave ≥ 50 ms of silence between sprite clips, and measure offsets on the *decoded* buffer, because MP3 encoders add leading padding (**UNVERIFIED** amount). howler.js (MIT) uses a similar `{name: [offsetMs, durationMs]}` sprite format if you want a library instead [S19].
- Always provide a mute toggle.
- **UNVERIFIED:** iOS hardware silent switch muting Web Audio; test on a device.

**Freesound licensing:** sounds are offered under **CC0, CC BY, or CC BY-NC**. Sampling+ is legacy and being removed. CC0 needs no credit (you just can't claim authorship), BY requires credit, and BY-NC bars commercial use [S20 FAQ]. The search page has a license filter [S20]. Licenses are per sound, so check each sound's page; forum guidance says the license appears below the download button (**UNVERIFIED** official wording) [S21]. Your downloads are listed at `/home/attribution/` [S20]. For each sound, record the URL, author, license and download date in a `CREDITS.md`, and keep a screenshot of the license (forum suggestion [S21]). Downloading requires a Freesound account, which **the user must do themselves** (**UNVERIFIED** that a login is required).

---

## Sources (licence of code where relevant)

- [S1] kouki-takezawa/popup-art-book — README, `js/book.js`, `js/common.js` — https://github.com/kouki-takezawa/popup-art-book — **MIT** (verified via gh API). Live: https://popup-art-book.vercel.app
- [S3] three.js r170 docs: SpotLight, LightShadow, WebGLRenderer — https://github.com/mrdoob/three.js/tree/r170/docs/api/en — **MIT**
- [S4] three.js r170 examples: `webgl_shadow_contact.html`, `webgl_lights_spotlight.html`, `webgl_lines_fat.html` — https://github.com/mrdoob/three.js/tree/r170/examples — **MIT**
- [S5] three.js r170 source: `src/renderers/webgl/WebGLShadowMap.js`, `src/textures/Texture.js`, `src/renderers/webgl/WebGLCapabilities.js`, `examples/jsm/lines/LineMaterial.js`, `examples/jsm/lines/LineSegments2.js`, `examples/jsm/controls/OrbitControls.js`, `examples/jsm/renderers/` — https://github.com/mrdoob/three.js/tree/r170 — **MIT**
- [S6] three.js docs: SkinnedMesh, Bone, PerspectiveCamera — https://threejs.org/docs/pages/SkinnedMesh.html , https://threejs.org/docs/pages/Bone.html , https://threejs.org/docs/#api/en/cameras/PerspectiveCamera
- [S7] three.js forum, "Animating a flexible object" — https://discourse.threejs.org/t/animating-a-flexible-object/6906
- [S8] prideout/pageturn (`src/pageDeformer.ts`) — https://github.com/prideout/pageturn — **Apache-2.0**. Write-up: https://prideout.net/pageturn/ . Paper: L. Hong, S.K. Card, J. Chen, "Turning Pages of 3D Electronic Books", IEEE 3DUI 2006, pp. 159–165 (cited via https://devblogs.microsoft.com/cppblog/?p=2173)
- [S9] US 7,898,541 B2 — https://patents.google.com/patent/US7898541
- [S10] three.js manual (r170 repo): rendering-on-demand, responsive, canvas-textures, align-html-elements-to-3d — https://github.com/mrdoob/three.js/tree/r170/manual/en — **MIT**
- [S11] A. Glassner, "Interactive Pop-up Card Design, Part 1", IEEE CG&A Jan/Feb 2002 — https://www.glassner.com/wp-content/uploads/2014/04/CG-CGA-PDF-02-01-Pop-Up-Cards-1-Jan02.pdf ; MSR-TR-98-03 — https://www.glassner.com/wp-content/uploads/2014/04/MSR-TR-98-03-Interactive-Pop-Up-Card-Design.pdf (contents not text-extracted here)
- [S12] Okamura & Igarashi, Smart Graphics 2009 — https://www-ui.is.s.u-tokyo.ac.jp/~takeo/papers/okamura_smartgraphics2009_popup.pdf
- [S13] Li, Shen, Huang, Ju, Hu, "Popup: Automatic Paper Architectures from 3D Models", ACM TOG 29(4) 2010 — https://cg.cs.tsinghua.edu.cn/people/~xianying/Papers/Popup/index.html
- [S14] troika-three-text README + package.json (v0.53.0, peer three >= 0.125.0) — https://github.com/protectwise/troika/tree/main/packages/troika-three-text — **MIT**
- [S15] MDN Page Visibility API — https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API
- [S16] MDN Web Audio API best practices — https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices
- [S17] MDN Autoplay guide — https://developer.mozilla.org/en-US/docs/Web/Media/Guides/Autoplay
- [S18] MDN AudioBufferSourceNode.start() — https://developer.mozilla.org/en-US/docs/Web/API/AudioBufferSourceNode/start
- [S19] howler.js — https://github.com/goldfire/howler.js — **MIT**
- [S20] Freesound FAQ — https://freesound.org/help/faq/
- [S21] Freesound forum, legal help and attribution — https://freesound.org/forum/legal-help-and-attribution-questions/
- Not used for code: wass08/r3f-animated-book-slider-final (no licence declared on GitHub — do not copy).
