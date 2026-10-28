---
name: interactive-3d-textbook
description: Build interactive 3D textbook / explorable lesson pages in the browser in the style of "Every Joule" — an open book on a desk, each diagram rising off the page as black-ink line-art 3D, the key quantity shown as glowing colour, and a predict → test → prove loop with a lift-the-flap explanation, a stamp, live sliders and readouts, plus quiz and teacher notes. Three.js (WebGLRenderer) with pmndrs postprocessing. Use whenever the user wants a 3D textbook, interactive lesson, explorable explanation, pop-up book diagram, "能动手玩的课本", "互动课本", "3D 课本", "互动教材", "立体书", "翻开书页图会立起来", "像 Every Joule 那样", physics/engineering/biology lessons students can experiment with (energy, seepage, soil mechanics, circuits, cells), ball experiments (bouncing ball, projectile / throwing / basketball shot, two balls colliding, pendulum, "弹跳球", "抛物线", "投篮", "碰撞", "单摆", "可以弄球的互动网页"), a 2D or 3D version of such a page, or asks to make an existing lesson page look and teach like that — even if they never say "skill".
---

# Interactive 3D textbook lessons

A lesson page here is two things at once: a **teaching loop** that only works if the student commits to a prediction before seeing the result, and a **rendering style** (white paper, black ink, a few glowing quantities) that is easy to get subtly wrong in three.js. Most failures are not crashes — they are a stamp that punishes wrong guesses, paper that renders grey, a glow that disagrees with the numbers, or a phone that stays hot because the page never stops redrawing. The rules below exist to prevent exactly those.

Read the reference for the part you are building; don't load all three up front:

- `references/lesson-design.md` — predict → test → prove, prediction options from real misconceptions, the flap, the stamp, synchronised representations, quiz, teacher notes, accessibility. Read before writing any lesson text or UI.
- `references/ink-rendering.md` — outlines (depth+normal edges, crease lines, inverted hull), hatching, paper, selective glow, tone mapping, r170 colour-management traps. Read before writing shaders or the postprocessing stack.
- `references/book-and-popup.md` — modelling the book, page turn, pop-up rise, pen-drawn lines, camera framing, page text, phone budget, audio sprite. Read before building the book scene.
- `references/ball-physics.md` — anything with a moving ball (bounce, projectile, collision, pendulum): exact formulas, fixed-step numerics, sourced misconceptions, what PhET shows, 2D vs 3D. Read before writing any physics.

**Ball experiments: start from `assets/ball-lab/`.** It is a tested lesson page with four experiments (bounce, thrown vs dropped, collision, pendulum) in zh + en, one shared physics module, and a 2D (SVG) and 3D (book, ink, glow) view of the same lesson behind a toggle, with automatic 2D fallback. Copy the folder, then change or add lessons in `lessons.js`; keep `physics.js` and its tests. Never hand-write the motion with per-frame `y += v` updates: unchecked integrators and penetrate-then-correct bounces give numbers that disagree with the textbook formula the student will check them against.

Related T1 skills (ask before using, per CLAUDE.md): `threejs-web` routes to the base three.js skills — use `threejs-postprocessing`, `threejs-shaders`, `threejs-materials`, `threejs-lighting`, `threejs-animation`, `threejs-interaction`, `threejs-html`, `threejs-performance`, `threejs-audio`. The `threejs-bloom`, `threejs-procedural-*`, `threejs-scalable-real-time-shadows`, `threejs-ambient-contact-shading`, `threejs-exposure-color-grading` and `threejs-camera-controls-and-rigs` skills target r185 WebGPU/TSL; read them for ideas only, their code does not run on WebGLRenderer. Interface polish: `impeccable`, `typography`, `game-feel`, `animate`. Sound: `audio-design`, `pixabay-assets`, `ffmpeg-skill`.

## Before you build: pin down four things

1. **The one idea** this page teaches (one page = one idea; a second idea is a second page).
2. **The misconception** the prediction will surface, with a source (see `references/lesson-design.md` §6 for energy; for any other subject follow the source ladder in §6a, and only label an option "teacher's judgement" after the ladder came up empty).
3. **The model**: what you compute, which equations, and every simplification (no rolling inertia, 2D flow, homogeneous soil…). These go on the page, not just in your report.
4. **Stack and versions**: three r170 (or the project's version) with `WebGLRenderer`, pmndrs `postprocessing` 6.x whose peer range covers that three version. Pin both in the import map or package.json.

## The lesson loop — what a page IS

Each experiment is this sequence, in this order, driven by one state object:

| Step | What exists on screen | Rules |
|---|---|---|
| Hook | One-sentence question tied to something the student cares about | Max ~25 words. |
| Predict | 3 options (4 at most), each a position a real student holds | Wrong options come from documented misconceptions. Native radio inputs in a `fieldset`. Choice **locks** before the experiment can run. Optional "sure / not sure". |
| Test | The 3D experiment, ≤3 controls on the first step | Representations (bars, graph, equation) start collapsed or minimal; the student opens them. Slider extremes must show something meaningful. Confounds off by default (friction off when the point is mass). |
| Prove | A flap the student lifts | The explanation **reuses the student's own run** (their height, their joules, their FS). For a wrong prediction, name the misconception behind *that* option without blame ("Surprised? Here's why…"). |
| Stamp | A stamp on the page | Awarded for **completing the loop** (predict + test + lift the flap), right or wrong. A correct prediction may add a second small mark. No points, streaks, leaderboards or red-only ✗. Stamp text is about the physics ("Mass cancels out"), not praise. |

Why the stamp rule matters: the research behind predict-first (Crouch et al. 2004) only works if students *commit* to a guess. Gate the reward on being right and students learn to stop guessing or to game the answer — the exact behaviour the page is meant to fix. Both unguided test builds of this skill withheld the stamp for wrong answers; don't.

**One state, every view, same frame.** The 3D glow, energy bars, equation with substituted numbers, numeric readouts and the canvas `aria-label` all read from the same state and update in the same animation frame. A glow that is lit while the readout says 0 J teaches the wrong thing. Drive emissive intensity from the quantity it represents (0 → no glow).

**Readouts:** SI units with a space (`4.9 J`, `2.0 m/s`), 2–3 significant figures, fixed decimals while a value changes, totals computed from unrounded values.

**Say what the model leaves out.** Put a short "What this model ignores" note behind the flap or in the teacher notes (e.g. "the ball slides, rolling energy is ignored", "time runs at 0.5×", "grid solution reads ~5 % low at the pile"). Slow motion must be labelled on screen.

## Rendering recipe — paper stays white, only energy glows

```js
import * as THREE from 'three';
import { EffectComposer, RenderPass, EffectPass, BloomEffect,
         ToneMappingEffect, ToneMappingMode } from 'postprocessing';

const renderer = new THREE.WebGLRenderer({ antialias: false, stencil: false, depth: false });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.NoToneMapping;          // tone mapping happens in the composer, or not at all
renderer.outputColorSpace = THREE.SRGBColorSpace;

const composer = new EffectComposer(renderer, { frameBufferType: THREE.HalfFloatType }); // 8-bit clamps → no glow
composer.addPass(new RenderPass(scene, camera));
const bloom = new BloomEffect({ mipmapBlur: true, luminanceThreshold: 1.0, luminanceSmoothing: 0.03, intensity: 1.2 });
const tone = new ToneMappingEffect({ mode: ToneMappingMode.AGX }); // optional — see the paper check below
composer.addPass(new EffectPass(camera, bloom, tone)); // one pass; paper (≤ 1.0) never blooms, energy emissive is > 1.0
// Ink/paper compositing (references/ink-rendering.md) is one more Effect in the same EffectPass.
```

- Paper, ink and desk stay at or below 1.0 linear before bloom. Energy meshes use `emissiveIntensity` > 1 **scaled by the quantity** (`emissiveIntensity = 1.5 + 4 * share`, and `0` when the store is empty). Gate the glow on what the readout *shows*: if the label rounds to `0.0 J`, the store must not glow.
- **Bloom is invisible on white paper.** `BloomEffect`'s default blend (SCREEN/ADD) brightens towards white, so on a near-white page the halo disappears. Composite the bloom texture as a *tint over the paper* instead: pass `bloom.texture` into your paper/ink Effect as a uniform, mix it in there (`col = mix(col, bloomRGB / max(bloomLuma, 1e-4), clamp(bloomLuma, 0., 1.))`, or multiply towards the glow hue), and silence the bloom's own blend with `bloom.blendMode.opacity.value = 0`. Both test runs had to rediscover this; do it from the start.
- **Paper check (the rule is the result, not the setting):** screenshot the page and read a blank-paper pixel. It must land within ~3 % of the paper colour you chose. Tone mapping on the final frame pulls white down (computed from r170's GLSL: ACES maps 1.0 → #E2E2E2, Neutral → #F0F0F0). If your pixel is grey, either raise the page light/exposure until the tone-mapped paper hits the target, tone-map before compositing the paper, or drop tone mapping. The reference genre does use a final tone-mapping pass with a bright, warm paper — what matters is that the reader sees white paper.
- Colour textures (paper, page canvas) `colorSpace = SRGBColorSpace`; data textures (noise, hatch masks, normal buffers) stay `NoColorSpace`. Hex colours are sRGB; clear a normal buffer with `setRGB(0.5, 0.5, 1)`, not `0x8080ff`.
- Two layers: the **book and desk** are softly lit (paper, cloth cover, desk mat, window light); the **diagram** is ink line-art on white card. Every part of the diagram is inked — no plain-lit object inside it. The diagram must be **3D objects** (track, ball, pile, soil block, flow tube) that rise off the page and read from a slight angle, not a flat 2D figure printed on a tilted card.

Outline choice (details and shader in `references/ink-rendering.md`): depth+normal Sobel in post for silhouettes + creases on everything that moves; add `EdgesGeometry` → `LineSegments2` for exact technical crease lines on rigid parts; `OutlineEffect` only for skinned characters without a post stack. Never use the luminance Sobel example — it finds shading edges, not geometry.

## Phone budget — the page must go quiet when nothing moves

```js
let dirty = true, running = 0;               // running > 0 while a sim/animation is active
const invalidate = () => { dirty = true; };
controls?.addEventListener('change', invalidate);
addEventListener('resize', () => { resize(); invalidate(); });
function loop(time) {
  if (!dirty && running === 0) return;      // idle: no GPU work at all
  dirty = false; update(time); composer.render();
}
renderer.setAnimationLoop(loop);
document.addEventListener('visibilitychange', () => {
  renderer.setAnimationLoop(document.hidden ? null : loop);
  if (!document.hidden) invalidate();       // repaint once on return
});
```

- Shadows: `renderer.shadowMap.autoUpdate = false`; set `shadowMap.needsUpdate = true` only on frames where something that casts moves. The book never moves — bake or render its contact shadow once.
- Pixel ratio ≤ 2, and drop it (to ~1.25) on touch devices or when frame time stays above ~25 ms; raise it back after a few good seconds.
- One `EffectPass` holding all effects (they merge into one shader). Skip MSAA on phones; prefer the ink effect's own anti-aliasing.
- Measure: `renderer.info.render.calls` (rule of thumb ≤ ~100 on phones — a heuristic, verify on a device), and say in the report what you measured and what you didn't.

## Accessibility (non-negotiable for a lesson)

All of it works from the keyboard: predictions (radios), lock, run/release, reset, flap (`button` with `aria-expanded`), sliders (native `range` with `aria-valuetext="2.0 metres"`). Every drag has a non-drag alternative (slider or buttons). Results and stamps are announced through a polite `aria-live` region; the canvas has a text alternative updated with the current state. `prefers-reduced-motion`: no camera fly-ins, no stamp bounce, pop-ups appear instead of rising. Energy stores are never colour-only — add labels or patterns. Real lesson text lives in semantic HTML; text drawn on page textures is decorative (`aria-hidden`).

## Sound (optional, adds a lot)

Page turn, flap, pen, stamp as one audio sprite (one mp3 + JSON offsets), `AudioContext` created/resumed on the first user gesture, a fresh `AudioBufferSourceNode` per play, a visible mute toggle. Only use sounds whose licence you checked one by one (Freesound CC0 is the easy case), and list them in `CREDITS.md`. See `references/book-and-popup.md` §7.

## Deliver

1. Run the checker and fix every error it reports (local, read-only, Python standard library):
   `python .claude/skills/interactive-3d-textbook/scripts/check_lesson.py <lesson-folder>`
   For ball lessons also run `node tests/physics.test.mjs` (exact-formula checks) and, if you changed lessons or views, `node tests/ball-lab.e2e.cjs <dir with three + postprocessing installed> <screenshot dir>` — it routes the CDN import map to local packages, so it works offline.
2. Open it in a browser over a local server (ES modules don't load from `file://`): desktop and a 375×812 viewport. Walk the loop twice — once predicting right, once wrong — and confirm the stamp appears both times. A hidden or background browser tab runs no `requestAnimationFrame` and freezes CSS transitions, so build a `?debug`-only `advance(ms)` hook that steps the simulation and renders one frame; use it to test, and say in the report which animations you never saw at live frame rate.
3. Screenshot blank paper and confirm it is white, not grey; screenshot the glow at 0 % and 100 % of the quantity.
4. Remove test hooks (`window.__lesson`, `advance()` helpers) or put them behind `?debug`.
5. Report: what was built, the model and its simplifications, what you tested and on what, what you didn't (real phone, Safari, frame rate), and the licences of anything third-party.

## Common mistakes

| Mistake | Fix |
|---|---|
| Stamp only for a correct prediction | Stamp for completing the loop; optional extra mark for correct. |
| Blank paper reads grey in the final frame (often a final `ToneMappingEffect` with default exposure) | Measure the paper pixel; raise page light/exposure, tone-map before the paper composite, or drop tone mapping. |
| `luminanceThreshold` below 1.0, or 8-bit composer | Paper blooms or nothing blooms. Threshold 1.0 + `HalfFloatType`. |
| Glow on while the quantity is zero | Emissive intensity from state; 0 when empty. |
| `requestAnimationFrame` drawing every frame forever | Render on demand + pause on `visibilitychange`. |
| A flat 2D figure on a tilted card, or a diagram mixing inked and plain-lit parts | The diagram is 3D objects, all inked; the book around it is softly lit. |
| Simplifications only in the chat report | On the page (flap / teacher notes); label slow motion. |
| Distractors invented ("trick" options) | From documented misconceptions (`references/lesson-design.md` §6a source ladder); no trick answers. |
| Glow uses the default SCREEN bloom on white paper, so no halo is visible | Composite bloom as a tint over the paper (see the rendering recipe). |
| Debug globals shipped | Remove or gate behind `?debug`. |
| Ball motion with `y += v*dt` and "if below floor, flip v" | Exact motion between impacts + solved impact time (`physics.js`); test against h₀e²ⁿ, √(2h/g), momentum, the exact pendulum period. |
| "Period doesn't depend on amplitude" taught as exact | Almost independent below ~20°; say so, and show the +7 % at 60° in "explore more". |
| Only a 3D view | Offer the 2D view too (phones, print, no WebGL); same lesson, same numbers. |
