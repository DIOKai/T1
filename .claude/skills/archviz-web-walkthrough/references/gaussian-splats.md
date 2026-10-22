# Gaussian-splat tours (scanned real spaces)

Use when the user has a real room/shop/house to scan instead of a Blender model. Splats look photoreal but have no clean surfaces: you can't swap materials, lighting is baked into the capture, and collision needs a separate invisible shell.

## Capture and train (free tools)
| Step | Tool | Licence | Notes |
|---|---|---|---|
| Photos/video | phone or camera | — | even, overlapping coverage; lock exposure; avoid moving people and mirrors |
| Camera poses (SfM) | COLMAP | new BSD (dependencies have their own licences) | input format most trainers accept |
| Train | **Brush** | Apache-2.0 | Windows/macOS/Linux, AMD/NVIDIA/Intel, Android, even the browser (WebGPU, Chrome 134+); reads COLMAP or Nerfstudio data; also a .ply viewer |
| Train (alt) | gsplat | Apache-2.0 | Python + CUDA, `pip install gsplat` (JIT compile on first run, PyTorch 2.7+) — ask before installing |
| Train (alt) | nerfstudio | Apache-2.0 | last push 2025-07, less maintained |
| Clean, crop | SuperSplat (PlayCanvas) | MIT | remove floaters, crop to the room, export |
| Compress | SPZ (Niantic) | MIT | small files for the web |

**Don't recommend:**
- LichtFeld Studio's Windows prebuilt — the README says access is paid (LichtFeld Portal "donation"). The source is GPL-3.0 and free to build yourself (needs NVIDIA GPU CC 7.5+, driver 570+, CUDA 12.8+). Per the user's no-paid rule: Brush or a source build.
- The original INRIA `gaussian-splatting` code for commercial work: its licence is research / non-commercial only.

Phone budget: no official number found. The community often says ~1–2 million splats on phones (未验证) — measure.

## Displaying in three.js
### Option 1: three.js r186 native `GaussianSplat` (WebGPU)
Files in r186: `examples/jsm/objects/GaussianSplat.js`, `loaders/SPZLoader.js`, `loaders/GaussianSplatPLYLoader.js`, `loaders/GLTFGaussianSplatLoaderExtension.js`; example `webgpu_gaussian_splat`.
- Source comment: **only works with `WebGPURenderer`** (its `forceWebGL` fallback is supported; plain `WebGLRenderer` is not). Import maps must resolve `three/webgpu` and `three/tsl`.
- Depth sorting by compute (counting sort); `new GaussianSplat(geometry, { autoSort: true })`.
```js
import * as THREE from 'three/webgpu';
import { SPZLoader } from 'three/addons/loaders/SPZLoader.js';
import { GaussianSplat } from 'three/addons/objects/GaussianSplat.js';
const geometry = await new SPZLoader().loadAsync('room.spz');
scene.add(new GaussianSplat(geometry));
```
- glTF `KHR_gaussian_splatting` (Khronos README: complete, ratified): register `loader.register(p => new GLTFGaussianSplatLoaderExtension(p))` — GLTFLoader doesn't register it automatically. r186's extension handles the base extension only (no SPZ-compression sub-extension seen in the source).
- Designed for single objects / room scale; no LOD or streaming. `SPLATLoader`/`KSPLATLoader` mentioned in a tutorial were not checked in r186 (未验证).
- This means the template's `WebGLRenderer` must be swapped for `WebGPURenderer` — see `threejs-webgpu`. Octree/Capsule are renderer-independent math and still work.

### Option 2: Spark 2.4 (World Labs, MIT) — WebGL2
`@sparkjsdev/spark` 2.4.0, peer `three >= 0.180.0`, uses the normal `WebGLRenderer` ("targeting 98%+ WebGL2 support"). Loads PLY (incl. compressed), SPZ, SPLAT, KSPLAT, SOG; mixes with meshes and sorts multiple splats together. Best fit for the template (keeps WebGLRenderer). Import it through the importmap at a pinned version and self-host for production. Performance vs native: 未验证.

## Walking inside a splat
1. In Blender (or by hand) make a few boxes for floor and walls at the scanned room's scale, named `COL_*`, export as `collision.glb`.
2. Align: scans have arbitrary scale/orientation. Measure one known distance (a door width) in SuperSplat or the viewer and scale the splat to metres; level the floor before export.
3. Load `collision.glb` for the Octree only (layer 1), the splat for display. The template's collision code works unchanged.
No ready-made tutorial for this combination was found (未验证 as an established workflow) — test walls and floor carefully.

## Sources
- three.js r186 files: https://github.com/mrdoob/three.js/tree/r186/examples/jsm/objects , https://github.com/mrdoob/three.js/tree/r186/examples/jsm/loaders
- Tutorial (secondary): https://ben3d.ca/blog/how-to-use-threejs-native-gaussian-splats
- r186 news (secondary): https://radiancefields.com/three.js-ships-its-native-gaussian-splat-renderer-and-splat-raycasting-in-r186
- KHR_gaussian_splatting: https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_gaussian_splatting
- Spark: https://github.com/sparkjsdev/spark , https://registry.npmjs.org/@sparkjsdev/spark/latest
- COLMAP: https://github.com/colmap/colmap/blob/main/LICENSE
- Brush: https://github.com/ArthurBrussee/brush
- gsplat: https://github.com/nerfstudio-project/gsplat
- nerfstudio: https://github.com/nerfstudio-project/nerfstudio
- LichtFeld Studio: https://github.com/MrNeRF/LichtFeld-Studio
- SuperSplat: https://github.com/playcanvas/supersplat
- SPZ: https://github.com/nianticlabs/spz
- INRIA licence: https://github.com/graphdeco-inria/gaussian-splatting/blob/main/LICENSE.md
