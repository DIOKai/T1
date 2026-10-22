# First-person controls and collision (three.js r186)

The template (`assets/walkthrough-template/main.js`) implements everything below. This file explains why, so you can change it safely. Camera ownership in general (who may write the camera, hand-offs between walk/tween/auto-tour): `threejs-camera-controls-and-rigs`.

## Collision: capsule + Octree (from `examples/games_fps.html`)
```js
import { Octree } from 'three/addons/math/Octree.js';
import { Capsule } from 'three/addons/math/Capsule.js';

const octree = new Octree();
octree.layers.set(1);                 // only meshes on layer 1 are collision
colliderMeshes.forEach(m => m.layers.set(1));   // COL_* → layer 1 only = never rendered
octree.fromGraphNode(gltf.scene);    // calls updateWorldMatrix itself

const player = new Capsule(new Vector3(0, R, 0), new Vector3(0, EYE, 0), R);
const hit = octree.capsuleIntersect(player);
if (hit) {
  onFloor = hit.normal.y >= 0.15;     // games_fps: slopes up to ~81° count as floor
  if (!onFloor) velocity.addScaledVector(hit.normal, -hit.normal.dot(velocity));
  if (hit.depth >= 1e-10) player.translate(hit.normal.multiplyScalar(hit.depth));
}
camera.position.copy(player.end);
```
- `Octree.layers` exists in r186 (source checked): putting colliders on layer 1 only both hides them from the camera (camera renders layer 0) and selects them for the Octree. When the model has no colliders, the template enables layer 1 on every visual mesh except `nocollide` ones — works, but slower to build and furniture snags the capsule.
- Sub-stepping: games_fps uses `STEPS_PER_FRAME = 5` and clamps the frame delta to 0.05 s, so a slow phone frame can't tunnel through a thin wall. Keep both.
- Walls in the collision shell should be at least ~10 cm thick and closed at the top/bottom (rule of thumb); single-sided planes can be crossed when the capsule centre passes them.

## Architecture-specific tuning (rules of thumb, 未验证 as any standard)
| Value | Template | Why |
|---|---|---|
| eye height | 1.6 m | adult standing eye level |
| capsule radius | 0.25 m | passes 0.8 m doors with margin; 0.35 (games_fps) feels wide indoors |
| walk speed | ~1.6 m/s, Shift ×2 | real walking pace; games_fps is ~6 m/s |
| gravity | 30 (games_fps) | keeps feet on ramps and stairs |
| jump | none | tours don't need it and it lets people climb furniture |
| out of bounds | feet below lowest floor − 10 m → back to spawn | games_fps `teleportPlayerIfOob` idea |

Terminal speed with exponential damping `v += v·(e^(−k·dt) − 1)` and acceleration `a` is `a/k`; the template uses k = 4 like games_fps, so `a = 4 × target speed`.

### Stairs
Replace each stair run in the collision shell with one invisible **ramp** from the bottom nosing to the top nosing. A 30–35° ramp has `normal.y ≈ 0.82–0.87`, well above 0.15, so it counts as floor. Real step-by-step collision makes the capsule stutter. Alternative: cast a ray down each frame (`octree.rayIntersect(ray)`) and snap the eye to floor + 1.6 m — smoother on stairs, but you must handle drops yourself.

### Doors and glass
Leave doorways open in the collision shell (Octree is static; animated doors need their own logic or an Octree rebuild). Glass must be in the shell — invisible to the eye, solid to the capsule.

## Desktop: pointer lock
`canvas.requestPointerLock()` on click, then use `movementX/Y` of `mousemove` while `document.pointerLockElement === canvas`. Rotation order `YXZ` (yaw, then pitch); clamp pitch to ±~85°. `PointerLockControls` (`three/addons/controls/PointerLockControls.js`, events `lock`/`unlock`, `pointerSpeed`, `min/maxPolarAngle`) does the same; the template does it by hand like games_fps so desktop and touch share one yaw/pitch.

Browser support (MDN browser-compat-data, `Element.requestPointerLock`): Chrome 37+, Firefox 50+, Safari 10.1+, Chrome Android 144+, **iOS Safari: not supported**. So touch controls are required for any phone audience.

## Mobile: joystick + drag + tap
- Left-bottom virtual joystick (pointer events, `setPointerCapture`) → move vector. Template: ~40 lines, no dependency. Want a library instead: nipplejs 1.0.4 (MIT).
- Any other touch on the canvas → drag to look (radians per pixel, slower than mouse).
- Tap a hotspot button → teleport tween. Optional: tap the floor → raycast (`threejs-interaction`) → tween to that point, only if the hit point is on a mesh with `room` (so people can't teleport onto a wardrobe).
- `touch-action: none` on the canvas and joystick, or the browser scrolls/zooms instead.
- Pixel ratio capped (template: 2, or 1.5 on coarse pointers) — the biggest single win on phones.

## Teleport tween
During the tween, physics is paused and the tween is the only writer of the player position; afterwards velocity is zeroed. Hotspot positions are the Empty's world position = feet; the template adds the capsule offsets. A tween crossing a wall is fine (it's a teleport); the destination must be inside the collision shell.

## Room label
Every ~0.2 s cast a ray straight down from the capsule's feet against meshes whose own or ancestor `userData.room` is set; show that name. Cheaper than per-frame raycasts and works across floors.

## Sources
- three.js r186 `examples/games_fps.html`: https://github.com/mrdoob/three.js/blob/r186/examples/games_fps.html
- Octree / Capsule: https://github.com/mrdoob/three.js/blob/r186/examples/jsm/math/Octree.js , https://github.com/mrdoob/three.js/blob/r186/examples/jsm/math/Capsule.js
- PointerLockControls: https://github.com/mrdoob/three.js/blob/r186/examples/jsm/controls/PointerLockControls.js
- MDN compat data: https://github.com/mdn/browser-compat-data/blob/main/api/Element.json
- nipplejs: https://www.npmjs.com/package/nipplejs
- Texture channel / uv1: three.js r186 `src/textures/Texture.js`, `src/renderers/webgl/WebGLPrograms.js`, `examples/jsm/loaders/GLTFLoader.js`
