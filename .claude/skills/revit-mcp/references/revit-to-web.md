# Revit → three.js scene and the material colour-map video

Goal from the reel: put the Revit model in an interactive three.js page, plan camera paths there, and render a flat "colour map" video (one colour per material) — typically as a control video for AI rendering. All routes below are free. Exporting from Revit while an agent run is active is blocked by pyRevit, so export between runs (or let the user click Export).

## 1. Choose the export route

| Route | Keeps material per element? | When |
|---|---|---|
| **A. Leia glTF exporter** (add-in) → `.glb` | Yes: glTF material name = Revit material name, `baseColorFactor` = Revit shading colour (+ transparency) | Fastest path to a web scene and a colour map |
| **B. Revit IFC export** → `ifc_material_colormap.py` → web-ifc in three.js | Yes, via IfcRelAssociatesMaterial (by `#id` / GlobalId); layered walls → one material per element unless sliced | You also want BIM data (GlobalIds, properties) in the browser, or no add-in may be installed |
| **C. Revit FBX export** → Blender → glTF | Material assignments survive into FBX | You want Blender lighting, lightmaps, or the `archviz-web-walkthrough` / `archviz-cinematic` pipelines |
| B′. IFC → IfcConvert → OBJ (`--use-material-names --use-element-guids`) | Yes for OBJ/MTL per IfcConvert docs; for `.glb` **not verified** | Offline conversion without a browser |

### A. Leia (e-verse revit-glTF-exporter)
- Free, MIT: https://github.com/EverseDevelopment/revit-glTF-exporter ; install from the Autodesk App Store: https://apps.autodesk.com/RVT/es/Detail/Index?id=492952120634946986&appLang=en&os=Win64 (installing an add-in = ask first).
- README lists Revit 2019–2024; the repo also has 2025, 2026 and 2027 projects (latest release v4.5.242, 2026-06-03). Whether the App Store build covers 2027: **not verified**.
- Use: open a 3D view → hide what you don't want (furniture, site, annotations) → choose properties → Export. In its source (`MaterialUtils.cs`) the "materials" mode writes each mesh's Revit material name and shading colour, metallic 0, roughness 1. It ships Draco / meshopt compression; if you use Draco, three.js needs `DRACOLoader` with the decoder files hosted locally.
- Want the colour map straight out of Revit? Give every material a distinct **Shading colour** (Material Browser → Graphics; or `Material.Color` in a `run_modify`, with approval). Simpler and non-destructive: leave Revit alone and colour by material name in three.js (below).

### B. IFC
- Revit's IFC exporter is Autodesk's open-source `revit-ifc` (https://github.com/Autodesk/revit-ifc), updated through the Autodesk Desktop App. Export with materials included; IFC4 Reference View or IFC2x3 Coordination View both work for this.
- Build the palette: `python scripts/ifc_material_colormap.py model.ifc -o colormap.json --summary`. Fix "no material" elements in Revit and re-export, or accept they share the `(no material)` colour.
- In the browser, web-ifc (MPL-2.0, `npm install web-ifc`) streams every element: `ifcApi.StreamAllMeshes(modelID, mesh => ...)` gives `mesh.expressID` (= the `#id` key in colormap.json) and `mesh.geometries[i]` with `geometryExpressID`, `flatTransformation` (4×4) and its own `color`. Vertex data is 6 floats per vertex (position xyz + normal xyz). Follow the official viewer example rather than retyping it: https://github.com/ThatOpen/engine_web-ifc/blob/main/examples/viewer/web-ifc-three.ts — just replace its `getMeshMaterial(placedGeometry.color)` with the colour from `colormap.json`.
- Higher-level option: That Open Engine `@thatopen/components` (MIT, three.js based, IfcLoader → Fragments): https://github.com/ThatOpen/engine_components
- IfcConvert (IfcOpenShell, LGPL-3.0) options from its docs: outputs `.obj` (+`.mtl`), `.dae`, `.glb`, `.svg`, `.xml`…; `--use-material-names` and `--use-element-guids` are documented for OBJ/DAE (not GLB); `--include entities IfcWall IfcSlab` filters; `--enable-layerset-slicing` splits layered walls by IfcMaterialLayerSet so each layer can get its own colour; `--center-model` re-centres huge georeferenced coordinates.

### C. FBX
Revit → Export → FBX from a 3D view (built in; carries material assignments and render appearances, aimed at 3ds Max: https://help.autodesk.com/cloudhelp/2023/ENU/Revit-DocumentPresent/files/GUID-C8038EFE-FB14-4591-85A1-8407B2BDDD0A.htm). Import into Blender, then follow `archviz-web-walkthrough` (glTF export, glTF-Transform, three.js) — ask before using it.

## 2. The colour-map pass in three.js

```js
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true }); // exact colour edges, frame capture
renderer.toneMapping = THREE.NoToneMapping;         // otherwise colours shift
renderer.outputColorSpace = THREE.SRGBColorSpace;   // '#e65050' in the palette = #e65050 in the PNG

// optional palette from ifc_material_colormap.py, or hash names when you only have a .glb
const palette = await fetch('colormap.json').then(r => r.ok ? r.json() : null).catch(() => null);
function colourFor(name) {
  const hit = palette?.materials?.[name]?.color;
  if (hit) return hit;
  let h = 0; for (const c of name || '') h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return new THREE.Color().setHSL((h % 360) / 360, 0.65, 0.55);
}

const flatCache = new Map();
function flat(m) {
  if (!flatCache.has(m.name)) flatCache.set(m.name, new THREE.MeshBasicMaterial({ color: colourFor(m.name), side: m.side }));
  return flatCache.get(m.name);
}

const gltf = await new GLTFLoader().loadAsync('model.glb');
gltf.scene.traverse(o => {
  if (!o.isMesh) return;
  o.userData.original = o.material;                    // keep for toggling back to the shaded look
  o.material = Array.isArray(o.material) ? o.material.map(flat) : flat(o.material);
});
scene.background = new THREE.Color('#000000');          // keep background out of the palette
```

Notes:
- `MeshBasicMaterial` ignores lights, so each material is one exact flat colour — that's the point. Turn shadows, fog and post-processing off for this pass.
- Glass: give it its own opaque colour in the colour map; transparent glass mixes colours and confuses segmentation-driven AI.
- Revit models are often far from the origin (survey coordinates). Re-centre (`Box3().setFromObject(scene).getCenter()` → subtract) or jitter appears.
- Revit and IFC are Z-up; glTF and three.js are Y-up. Check orientation once on every route (a model lying on its side means a missing -90° X rotation) — not verified per exporter.

## 3. Plan the camera path, export frames

- Interactive planning: OrbitControls or the walkthrough controls from `archviz-web-walkthrough`; record keyframes (position + target) to JSON with a key press, then play them back along a `THREE.CatmullRomCurve3` with eased time.
- Frame-exact capture: step the timeline per frame (don't rely on real time), `renderer.render()`, then `canvas.toBlob()` → download, or drive the page headless with Playwright and `page.screenshot()` per frame (ask before installing Playwright). Render the **same path twice** — once shaded, once colour map — so the AI step has a matching pair.
- Encode the PNG sequence with ffmpeg (`archviz-cinematic` has the settings, e.g. `ffmpeg -framerate 24 -i f_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 16 out.mp4`). For segmentation control videos keep it lossless or near-lossless (`-crf 0`/`-qp 0` or PNG sequence) so colours don't bleed.
- Then hand the colour-map video to `ai-archviz-render` (local ComfyUI, Wan2.2 Fun Control / VACE) — ask first.

## Sources
- Leia repo, README, `Common_glTF_Exporter/Utils/MaterialUtils.cs`: https://github.com/EverseDevelopment/revit-glTF-exporter
- revit-ifc: https://github.com/Autodesk/revit-ifc
- IfcConvert usage (repo docs `docs/ifcconvert/usage.rst`): https://github.com/IfcOpenShell/IfcOpenShell/blob/v0.9.0/docs/ifcconvert/usage.rst (default branch on 2026-10-22) and https://docs.ifcopenshell.org/ifcconvert/usage.html
- web-ifc API (`src/ts/web-ifc-api.ts`: FlatMesh, PlacedGeometry) and examples: https://github.com/ThatOpen/engine_web-ifc
- Revit FBX export help: link above.
- three.js colour-management / tone-mapping settings and the capture method are standard three.js usage (r15x+; current npm 0.186.1) — **not tested against a Revit export here**.
