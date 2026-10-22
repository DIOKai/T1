# Blender → Unreal Engine 5

## Prepare in Blender (before exporting)
- One object per wall run / floor / ceiling per room, one per furniture piece. Lumen can't handle a whole room + furniture as one mesh.
- Walls at least **10 cm** thick (software Lumen leaks light through thinner walls). Close every gap at corners and where walls meet floor/ceiling.
- Apply scale (Ctrl+A > Scale) on everything; rotations applied or consistent.
- Furniture pivot at **bottom centre** (experience value) so web-panel moves/scales keep it on the floor.
- Materials: Principled BSDF only. Bake procedural textures, AO-mixed colours, emission and anything node-heavy to image textures. Normal maps through a Normal Map node.
- Glass is its own object (it won't be Nanite and needs a translucent material in UE).
- Naming: `SM_<Room>_<Thing>` for meshes, `M_`/`MI_` for materials (experience value — makes MCP asset searches easy).
- Save the .blend; export to a folder outside the UE project's `Content/`.

## FBX (most reliable for static meshes)
| Setting | Value |
|---|---|
| Apply Scalings | **FBX Units Scale** (not FBX All) |
| Apply Unit | on |
| Forward / Up | −Z Forward, Y Up (defaults) |
| Apply Transform | optional for static meshes; experimental, has known Blender issues (T99075) |
| Apply Modifiers | on |
| Smoothing | Face |
| Tangent Space | on |
| Add Leaf Bones | off |
| Path Mode | Copy, embed textures |

Blender Unit Scale 1.0 usually works for static meshes; skeletal meshes often use 0.01. **Check**: after import the actor's Scale must read (1, 1, 1). (100, 100, 100) means the export was wrong — re-export, don't patch in UE. UE 5.4/5.5 Interchange may recompute normals; look for shading seams.

## glTF / GLB
Imported through Interchange (UE 5.2+). Supports KHR_materials clearcoat, transmission, sheen, IOR, unlit, specular-glossiness and mesh quantization. Whether metres → centimetres is converted automatically is **unverified** (Epic's glTF import page returned empty). Measure a door after import: it should be ~200–210 cm tall.

## USD
Blender File > Export > Universal Scene Description (UVs, normals, materials). UE: enable USD Importer (restart), preview in USD Stage Editor, then import. Good for large scenes with many instances.

## Datasmith / Send to Unreal / .blend import
- No official Epic Datasmith exporter for Blender; a community add-on exists (0xafbf); UE 5.7/5.8 compatibility unverified.
- Epic's "Send to Unreal" (Blender Tools, 2020) now lives on as a community fork (poly-hammer/BlenderTools, not Epic). Whether Epic archived the original: unverified.
- Fab "Blender Interchange Content Importer" imports .blend (Blender 3.0–4.3); price unverified — check before suggesting (free only).

## In Unreal
- Import into `/Game/Archviz/<Project>/Meshes`, `/Materials`, `/Textures`.
- Lumen projects: no lightmap UVs needed. For Nanite meshes turn **off** Generate Lightmap UVs (otherwise import time and data balloon).
- Nanite: Build Nanite at import, or right-click > Nanite > Enable. Opaque and Masked only — **no translucent materials (glass)**, no MSAA, VR stereo, Forward shading, lighting channels, morph targets. High-poly furniture benefits (faster Lumen surface cache).
- Materials: rebuild as one master material (base colour/ORM/normal textures + tint/roughness parameters) and a material instance per finish. The web panel swaps instances.
- Collision: walls/floors use simple collision or complex-as-simple for the walkthrough; furniture gets box collision.

## Verify after import
1. Every actor scale (1, 1, 1); a door ~2 m; ceiling height matches the layout JSON.
2. Side view: nothing floats, nothing sinks into the floor.
3. Lit view with Lumen: look for light leaks at wall/ceiling joints (thicken or overlap the meshes).
4. From the street into every window: a real room behind the glass (user's earlier rule).
5. Material slots: no default grey checker materials left.

## Sources
- Blender → UE5 export guide (Feb 2026, unofficial): https://sarahhyperdense.substack.com/p/blender-to-ue5-the-complete-export
- Blender FBX Apply Transform issue: https://developer.blender.org/T99075
- glTF extensions in UE: https://dev.epicgames.com/documentation/unreal-engine/API/Plugins/GLTFCore/GLTF__EExtension
- glTF import page (empty when fetched): https://dev.epicgames.com/documentation/en-us/unreal-engine/importing-gltf-files-into-unreal-engine
- USD workflow (unofficial): https://jsabbott.artstation.com/blog/PQeVO/tutorial-blender-to-ue5-workflow-using-usd
- Nanite: https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine
- Lumen technical details: https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine
- Send to Unreal: https://www.cgchannel.com/?p=117307 , https://github.com/poly-hammer/BlenderTools
- Fab .blend importer: https://www.fab.com/listings/c719cc60-e69d-4567-be89-8744c52744a4
- unreal-engine-mcp (glTF via Interchange needs 5.2+): https://pypi.org/project/unreal-engine-mcp/
