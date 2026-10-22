# Interactive features in three.js (info panel, compass/minimap, sun, section, measure, variants)

The three.js versions of what the Unreal archviz reels show. Snippets target **three r186** (the template's pinned version) and plug into the template's `window.tour` (`scene`, `camera`, `renderer`, `player`, `teleport`). They are **not added to the template** — each feature changes rendering or input in ways that need testing on the user's scene and phone; copy the parts you need into `main.js`. Snippets were checked against the three.js source/examples named in Sources, not run in a browser as a whole (未验证 together).

Phone first: every feature below needs a tap-sized button (≥ 44 px, rule of thumb) and must not fight the joystick/drag-to-look; while a tool (measure, section drag) is active, pause look-drag on that pointer.

## 1. Unit / lot info panel
Data lives in glTF `extras` (set as Blender Custom Properties, exported with **Custom Properties** on — see `blender-export.md`) or in a small `units.json` keyed by an id extra. Keep numbers numeric and in metres / m².

| Extra (on the unit's floor mesh or an Empty) | Example |
|---|---|
| `unit` | `"A-0702"` |
| `area_m2` | `86.4` |
| `bedrooms` / `bathrooms` | `3` / `2` |
| `facing` | `"NW"` |
| `status` | `"available"` |

```js
// tap/click → which unit? (reuse one Raycaster; only test unit meshes, not the whole scene)
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
const unitMeshes = []; scene.traverse(o => { if (o.isMesh && o.userData.unit) unitMeshes.push(o); });
function pick(ev) {
  const r = renderer.domElement.getBoundingClientRect();
  ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  const hit = ray.intersectObjects(unitMeshes, false)[0];
  if (hit) showUnit(hit.object.userData);         // fill an HTML <aside>, not a 3D text mesh
}
```
In pointer-lock mode the "cursor" is the screen centre: use `ndc.set(0, 0)`. A plain HTML panel is cheaper and sharper than 3D text; for labels pinned to 3D points use `CSS2DRenderer` (`threejs-html` skill). Escape HTML when filling text from extras.

## 2. Compass and minimap
```js
const NORTH_YAW = THREE.MathUtils.degToRad(0); // world yaw that faces north; measure once from the site plan
const e = new THREE.Euler();
function updateCompass() {
  e.setFromQuaternion(camera.quaternion, 'YXZ');            // yaw = e.y (three.js: +y up, -z forward)
  compassEl.style.transform = `rotate(${THREE.MathUtils.radToDeg(e.y - NORTH_YAW)}deg)`;
}
```
Minimap: a 2D floor-plan image (top render or `floorplan-to-blender` SVG) with a dot. Map world XZ → image pixels with two reference points measured once (`u = (x - x0) * sx`, `v = (z - z0) * sz`). Rotate the dot arrow by the same yaw. Tap on the minimap → `tour.teleport()` to the nearest hotspot. A second WebGL render of the scene (orthographic camera into a scissor viewport) works but doubles draw calls — desktop only (rule of thumb).

## 3. Time of day (sun + sky) — and the lightmap conflict
```js
import { Sky } from 'three/addons/objects/Sky.js';
const sky = new Sky(); sky.scale.setScalar(450000); scene.add(sky);
const u = sky.material.uniforms;            // turbidity, rayleigh, mieCoefficient, mieDirectionalG, sunPosition
const sun = new THREE.DirectionalLight(0xffffff, 3); scene.add(sun, sun.target);
function setSun(elevDeg, azimDeg) {         // azimuth clockwise from north, rotated by NORTH_YAW
  const phi = THREE.MathUtils.degToRad(90 - elevDeg), theta = THREE.MathUtils.degToRad(azimDeg) + NORTH_YAW;
  const dir = new THREE.Vector3().setFromSphericalCoords(1, phi, theta);
  u.sunPosition.value.copy(dir);
  sun.position.copy(dir).multiplyScalar(50); sun.intensity = Math.max(0, Math.sin(THREE.MathUtils.degToRad(elevDeg))) * 3;
}
```
Check the direction once: at a morning time the sun must rise on the site's east side; if it rises west, negate `theta`. Real place and date → **SunCalc** (BSD-2-Clause, `getPosition(date, lat, lng)`). Check its README for your version's units: the current README says degrees with azimuth clockwise from north; older 1.x releases returned **radians with azimuth measured from south** (未验证 which version you get from the CDN — log one value at noon).

**Conflict: baked lightmaps can't move.** The template's approach A/B bakes the sun into textures, so a time slider then moves the sky but not the light on the floor. Options, cheapest first:
1. **Bake 2–4 snapshots** (morning / noon / golden hour / night) in Blender and switch or cross-fade `material.lightMap` per preset. Stays cheap on phones; slider becomes buttons. Multiplies lightmap download size (load presets lazily).
2. **Bake only indirect (bounce) light + real-time sun**: bake Diffuse with Indirect only, add a `DirectionalLight` with shadows for the sun. Moving sun works; shadow maps on phones are costly and indirect light no longer matches the sun angle (rule of thumb: acceptable within a few hours of the baked time).
3. **No bake, real-time only** (approach C) + `Sky` + `PMREMGenerator.fromScene(sky)` for the environment, refreshed only when the slider stops. Flat indoors, but fully dynamic.
4. Exterior only: keep interior baked, animate only sky + exterior sun (common in property tours).
Tell the user which one and why; option 1 is the default for phone-first tours.

## 4. Section (cut) mode
```js
const renderer = new THREE.WebGLRenderer({ antialias: true, stencil: true }); // stencil defaults to false since r163
renderer.localClippingEnabled = true;                    // needed for material.clippingPlanes
const cut = new THREE.Plane(new THREE.Vector3(0, -1, 0), 1.2);   // distance = -y + 1.2 → clips y > 1.2 m, keeps everything below
```
- **Global and simple**: `renderer.clippingPlanes = [cut]` cuts everything, including UI-like 3D helpers. **Per material**: `mat.clippingPlanes = [cut]` on building materials only (keep furniture whole if wanted). Points where `plane.distanceToPoint(p) < 0` are clipped (three.js `Plane` convention); flip with `cut.negate()` if the wrong half disappears.
- Move it live: `cut.constant = h`. Cheap — no recompile, only uniforms.
- **Caps** (otherwise walls look hollow): the official `webgl_clipping_stencil` example — per plane, render the solid's **back faces incrementing** and **front faces decrementing** the stencil (`colorWrite:false, depthWrite:false`, `IncrementWrapStencilOp` / `DecrementWrapStencilOp`), then draw a large plane mesh with `stencilFunc: NotEqualStencilFunc, stencilRef: 0` (`ReplaceStencilOp`), `renderOrder` just after the stencil pass, `onAfterRender = r => r.clearStencil()`, positioned each frame with `plane.coplanarPoint(cap.position)` + `cap.lookAt(cap.position.clone().sub(plane.normal))`.
- Caveats from the three.js forum: stencil caps need **closed (watertight) meshes** — Blender walls with missing faces or single-sided planes give stray caps; capping with several planes and `clipIntersection = true` doesn't work with this method; post-processing composers can break the stencil. Cheap fallback: `side: THREE.DoubleSide` on wall materials plus a dark flat colour for back faces via `onBeforeCompile` (`gl_FrontFacing`) — reads as poché without stencil.
- Collision: the Octree still has the ceiling; that's fine (section is visual). Turn walking off and use orbit controls while sectioning from outside ("dollhouse" view).

## 5. Measurement (two taps → metres)
```js
const pts = [];
function measureTap(ev) {
  const hit = raycastAt(ev, measurable)[0]; if (!hit) return;        // measurable = visual meshes, not COL_
  pts.push(hit.point.clone()); if (pts.length < 2) return;
  const [a, b] = pts.splice(0, 2), d = a.distanceTo(b);              // glTF from Blender = metres
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([a, b]),
                              new THREE.LineBasicMaterial({ color: 0xffcc00, depthTest: false }));
  line.renderOrder = 999; scene.add(line);
  label(a.clone().lerp(b, 0.5), `${d.toFixed(2)} m  (Δh ${Math.abs(b.y - a.y).toFixed(2)} m)`); // CSS2DObject
}
```
`linewidth` is ignored by WebGL (always 1 px) — use `Line2`/`LineMaterial` from addons for a thick line. Units are only right if the Blender scene was real scale and exported +Y up without extra scale; measure a door once (~2.0–2.1 m) as a sanity check. Add a "snap to axis" toggle: if |Δx| or |Δz| dominates, zero the others — wall-to-wall reads perpendicular.

## 6. Material variants (changer bar)
- Same geometry, different finish → **KHR_materials_variants** (see `furniture-swap.md`; three.js needs the pattern from the `webgl_loader_gltf_variants` example). This is the web equivalent of Unreal's "master material + instances": author one material per finish in Blender, the variants extension switches them.
- Colour/roughness tweak only → keep one material and change `material.color` / `roughness` / swap `map` — no new shader compile, instant (like a UE Material Instance parameter).
- Whole different model → `slot` empties + lazy GLB (`furniture-swap.md`).
- Bar UI: one row per slot (Floor, Sofa, Kitchen), thumbnails rendered once in Blender, active one highlighted, ≤ 6 visible per row on phones (rule of thumb). Changing a floor finish in a **baked** room keeps the baked light (lightmap is separate on uv1, approach A) — that's why approach A exists; approach B (light baked into baseColor) can't swap materials.

## Test checklist (real phone too)
- Panel: every unit tap shows the right data; numbers formatted with units; no HTML injection from extras.
- Compass: walk north on the site plan → compass points up.
- Sun: noon shadow direction matches the site orientation; lightmap preset switch doesn't flash black (preload).
- Section: no hollow walls with caps on; no stray caps (non-watertight meshes); frame time measured before/after.
- Measure a known door and a room width against the plan.

## Sources
- three.js Plane / clipping: https://threejs.org/docs/#api/en/math/Plane , https://threejs.org/docs/#api/en/materials/Material.clippingPlanes
- Stencil cap example (source read): https://github.com/mrdoob/three.js/blob/dev/examples/webgl_clipping_stencil.html
- Stencil default false since r163 and cap pitfalls (forum): https://discourse.threejs.org/t/webgl-clipping-stencil-plane/73867 , https://discourse.threejs.org/t/clipping-with-3-planes-stencils-and-clipintersection-true/62329 , https://discourse.threejs.org/t/stencil-clipping-gltf-weird-backfaces/41936
- Sky addon uniforms (source read): https://github.com/mrdoob/three.js/blob/dev/examples/jsm/objects/Sky.js
- SunCalc (BSD-2-Clause): https://github.com/mourner/suncalc
- Variants example: https://threejs.org/examples/webgl_loader_gltf_variants.html
- Raycaster: https://threejs.org/docs/#api/en/core/Raycaster ; Line2 (fat lines): https://threejs.org/examples/webgl_lines_fat.html
