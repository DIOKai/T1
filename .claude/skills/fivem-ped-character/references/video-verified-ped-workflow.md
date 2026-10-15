# Video-verified custom-ped workflow

Primary video studied: [NcProductions — GTA V: Ped Modding Tutorial, From Blender to GTA V with Sollumz](https://www.youtube.com/watch?v=uhsCTlLtcJs), 41:28. The authored/available English transcript was reviewed end to end. The tutorial used Blender 2.93 and Sollumz 1.3, so its interface locations and unexplained numeric fields are historical, not current defaults.

Supplementary videos discovered but not treated as technical authority because no transcript was available:

- [Adding props and alternative outfits with Sollumz](https://www.youtube.com/watch?v=UyXC-6PEbkg)
- [Custom-ped, prop, and texture animation with Sollumz 2.1](https://www.youtube.com/watch?v=gdlRMsOWBYA)

## Durable decisions extracted from the full tutorial

### Skeleton and proportions

- Start from a legally obtained, known-good GTA ped YFT/YDD that matches the intended use. Import the YFT XML as the rig and use the original component as a placement and weighting reference.
- Choose the compatibility goal before moving bones. Editing bone positions/roll can fit a custom body, but it can break contact with stock animation targets such as weapons, steering wheels, and handlebars. When stock contact accuracy matters, fit the mesh to the stock skeleton instead.
- Do not copy the video's old Sollumz `Unknown 1`, `Flags`, or export-checkbox values into a current project without comparing the current UI, current documentation, and a known-good imported asset.

### Weighting

- Automatic weights are only a starting attempt. A practical fallback is to conform a known-good Rockstar mesh to the custom form, transfer its weights, then repair the vertex groups manually.
- Remove unintended helper/control-group influences only after comparing them with the chosen base skeleton. The video removed `PH_` and `IK_` vertex-group influences; do not turn this into a universal deletion rule for every skeleton.
- Limit and normalize to four effective bone influences per vertex for this demonstrated GTA ped path. Inspect deformation rather than accepting a successful export as proof.

### Components, UVs, textures, and seams

- Split the character intentionally into GTA component roles such as `head`, `hair`, `uppr`, `lowr`, `hand`, `feet`, `teef`, and accessories. The component split affects wardrobe behavior, metadata, textures, and even fixes such as foot-height adjustment.
- For the demonstrated custom-ped path, UV0 carries the component's diffuse/normal/specular layout and UV1 carries damage overlays. Preserve any source UV temporarily for baking, but do not assume the game will use arbitrary extra UV sets.
- Bake multiple source materials into the GTA-compatible texture arrangement required by the component. Check current Sollumz shader requirements rather than copying the video's compression or naming choices blindly.
- At split borders such as neck/head and leg/feet, align both vertex positions and split normals. A watertight-looking viewport mesh can still show a lighting seam in game.

### Wind, sweat, and hair

- The tutorial demonstrates separate vertex-color/alpha roles for lighting, wind movement, and sweat darkening. Treat the exact channel names and values as version- and shader-specific: compare with current Sollumz documentation and a known-good base component.
- Hair must use an appropriate ped hair shader/material and be tested for alpha sorting, scalp coverage, wind response, helmet behavior, and all required LODs. A white viewport vertex mask is not proof that the in-game wind result is correct.

### Facial animation

- Build the ordinary body rig first, then treat facial animation as a separate integration. The video imports a compatible cutscene facial rig, keeps its facial root, parents that root into the head hierarchy, transfers facial weights from a known-good head, and replaces the exported component rigs with the combined rig.
- Expression dictionary and clipset metadata are part of the result. Never copy the example ped names or metadata values unchanged; compare against a compatible base and test idle face, speech, and cutscene/gameplay expressions.

### LOD and packaging

- Create explicit high/medium/low representations for the important components, preserving rig, material, component, and texture relationships. Decimation alone is not an acceptance test.
- Inspect the exported YDD/YFT/YTD/YMT/meta chain in CodeWalker, then test in a local game/server. Reload after conversion so stale previews do not conceal missing textures.

## Acceptance sequence

1. In Blender, pose-test hands, shoulders, spine, hips, knees, feet, jaw, eyes, and facial controls; inspect every component seam and verify the effective influence count.
2. In CodeWalker, reload the converted files and run representative animations. Confirm skeleton presence, component names, shaders, textures, and LODs.
3. In game, test idle, walk, run, crouch, weapon aim, vehicle driving, speech/expression, damage overlays, sweat, wind, and camera-distance LOD transitions.
4. Record the base ped, GTA edition/build, Blender/Sollumz versions, component list, metadata files, known deviations, and any untested behavior.

Do not describe the result as animation-compatible, face-compatible, or production-ready until the matching acceptance checks pass.
