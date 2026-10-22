---
name: parametric-facade
description: Free parametric facades in Blender Geometry Nodes, built by bpy through the blender MCP — panelize flat or curved building skins, check which panels are flat enough to fabricate, add mullions and vertical fins that vary with an attractor, stack twisted floor plates around a core, and distribute modular blocks — with checks that nothing floats. Use whenever the user wants a parametric / computational / Zaha- or Studio-Tim-Fu-style facade, curtain wall, louvres, brise-soleil, fins, panel pattern, twisted tower, stacked floor slabs, facade rationalisation, or wants Rhino/Grasshopper-style results without paying for Rhino — even if they only say "参数化立面", "做立面", "幕墙", "遮阳鳍片", "百叶", "扭转大楼", "楼板堆叠", "曲面分板", "立面合理化", "像 Grasshopper 那样".
---

# Parametric facades in Blender (free)

This is the free route to what Rhino + Grasshopper studios show off: a curved skin cut into panels, fins that thicken toward the sun side, a twisted tower of slabs. Blender's Geometry Nodes do the same things procedurally, and Blender costs nothing. The paid route lives in `rhino-mcp`; offer it only when the user already owns Rhino or asks for it.

Everything runs through the `blender` MCP (`execute_blender_code`). Ask before using it (T1 rule) and have the user save the .blend first: code sent through the MCP can't be undone in one step. See `mcp-for-blender` for how that MCP is driven.

## Two rules that shape every step

1. **Nothing floats.** The user's standing rule for buildings: every fin, plate, panel and block must sit on a slab, beam, wall or the ground, like a real building. Floor plates stack around a core; fins stand on floor lines and touch the wall; panels lie on the surface. `find_floating()` checks this, so run it before showing anything.
2. **Flat panels are what get built.** A quad on a doubly curved surface is usually twisted, and twisted glass or metal costs a lot more or needs triangulating. Studio Tim Fu's Cacao Greenhouse is a good example: its double-curved form was rationalised into all-flat metal and glass panels. Report how many panels aren't flat (`planarity_report()`) whenever the skin is curved.

## Workflow

### 1. Get the base shape
- Building shell from a plan → `floorplan-to-blender` (ask first). Its walls and slabs are the structure the facade attaches to.
- Massing only → a mesh drawn by hand, or `FP_FloorStack` from a footprint curve (below).
- Curved skin → a NURBS/subdivided surface converted to mesh. Keep its horizontal edges on the floor lines if fins will go on it.

Ask the user, in one go: floor-to-floor height, number of floors, target panel size (typical curtain-wall modules are about 1.2–1.5 m wide, a rule of thumb), what the facade is for (stills, animation, game export), and where the sun or main view is (that becomes the attractor).

### 2. Build the node groups
```python
import runpy, bpy
fn = runpy.run_path(r"<skill>/scripts/facade_nodes.py")
print(fn["build_all"]())          # FP_Fins, FP_FloorStack, FP_PlanarCheck (rebuilt each time)
```
| Group | Input | What it makes |
|---|---|---|
| `FP_FloorStack` | closed footprint curve centred on its origin | `Floors`+1 slabs (ground to roof), `Floor Height`, `Slab Thickness`, `Twist`°/floor, plus a core (footprint × `Core Scale`) from ground slab to roof so every slab is carried |
| `FP_Fins` | envelope mesh with horizontal edges on floor lines | fins every `Spacing` m along each floor line (not the roof line), back face on the wall, `Fin Height` tall, depth from `Min Depth` to `Max Depth` by distance to `Attractor` within `Radius` |
| `FP_PlanarCheck` | any mesh | non-flat faces red, flat grey, face attribute `fp_planar` |

Apply with keyword names (spaces → underscores):
```python
tower = bpy.data.objects["Footprint"]
fn["apply"](tower, "FP_FloorStack", Floors=24, Floor_Height=3.6, Twist=2.5, Core_Scale=0.35)
skin = bpy.data.objects["Envelope"]
fn["apply"](skin, "FP_Fins", Spacing=1.2, Fin_Height=3.6, Max_Depth=0.8, Attractor=bpy.data.objects["SunTarget"])
```
Set `Fin Height` equal to the floor-to-floor height so each fin runs from one slab line to the next. If the envelope has extra horizontal edges between floors (panel rows), fins appear on those too; give `FP_Fins` a mesh cut only at floor lines, or set `Fin Height` to the row height. Delete triangulated roof/bottom caps first, because every horizontal edge below the roof gets fins.

For panels, mullions, blocks and the other patterns, follow `references/recipes.md`. It has seven recipes with the node chain for each, including the ones the script doesn't prebuild.

### 3. Check before showing
```python
print(fn["planarity_report"](skin, tol=0.001))   # faces, non_planar, worst_deviation_m
print(fn["find_floating"](tower))                # must return "floating": []
print(fn["find_floating"](skin))
```
- `find_floating` splits the evaluated mesh into separate pieces. A piece counts as supported when it touches the ground or touches/intersects a supported piece within 2 cm. Anything it lists is a bug: fix the inputs (heights, spacing, footprint centring) and don't hide the piece.
- Look at the result yourself, from the street (eye height ~1.6 m), from below at a steep angle (that's where floating fins and gaps show), and from the top. Fins must meet the wall and slab edges with no gap.
- With `FP_PlanarCheck` on a copy, red faces show where panels would be twisted. Fixes are in recipe 2.

### 4. Hand off
- Materials, lighting, cameras → `archviz` (ask first); add `archviz-cinematic` if it is installed.
- Real IFC elements (curtain wall, slabs) → the `bonsai-*` skills; Geometry Nodes output is only a mesh to them.
- Game export: run `Realize Instances` (the script already realizes fins and slabs), apply the modifier on a copy, then follow `export-pipeline` / `lod-pipeline`.

## Limits (say them, don't hide them)
- **Not run in Blender.** No Blender was available when this skill was written. `facade_nodes.py` passed `python -m py_compile`, its pure-Python helpers (`islands`, `unsupported`, `boxes_touch`, `face_flatness`) were tested in plain Python, and all three groups were built against a mock `bpy` that checks every link uses a socket name the script expects. Node **identifiers** used and verified in the research notes against the Blender 5.2 API docs: `GeometryNodeBoundBox`, `GeometryNodeMeshToCurve`, `GeometryNodeResampleCurve`, `GeometryNodeInputNormal`, `GeometryNodeSampleNearestSurface`, `GeometryNodeObjectInfo`, `GeometryNodeInputPosition`, `GeometryNodeSetPosition`, `FunctionNodeAlignRotationToVector`, `GeometryNodeInstanceOnPoints`, `GeometryNodeRealizeInstances`, `GeometryNodeSetMaterial`, `GeometryNodeJoinGeometry`, `GeometryNodeFillCurve`, `GeometryNodeExtrudeMesh`, `GeometryNodeFlipFaces`, `GeometryNodeMeshLine`, `GeometryNodeInputIndex`, `GeometryNodeTransform`, `GeometryNodeInputMeshFaceIsPlanar`, `GeometryNodeStoreNamedAttribute`. **Unchecked** (not in the notes, from general Blender knowledge): `GeometryNodeInputMeshEdgeVertices`, `GeometryNodeMeshCube`, `ShaderNodeMath`, `ShaderNodeVectorMath`, `ShaderNodeMapRange`, `ShaderNodeSeparateXYZ`, `ShaderNodeCombineXYZ`; **all socket names** (e.g. `Position 1`, `Planar`, `Threshold`, `Sample Position`, `Offset`, `Individual`, `Result`); whether Resample Curve's mode and Align Rotation to Vector's axes are node properties or menu sockets in 5.x (the script tries both); and whether Extrude Mesh keeps the original face (the slabs add a flipped cap; if a slab looks doubled or dark, use `Flip Normals`). If a socket name differs, `_sock()` raises an error that lists the real names: fix the script and tell the user.
- Planarity in Blender is a check, not a solver. There is no built-in planarize/relax like Kangaroo or Evolute; the fixes are triangulating, choosing a translational or cylindrical surface, or splitting into strips (recipe 7).
- Blender has no "developable surface" verification; strips are only approximated.
- `FP_FloorStack` assumes the footprint is centred on the object origin and roughly convex. With large twists or an off-centre footprint the core can leave a slab. `find_floating` catches that.
- This is visualisation geometry. Panel sizes, fin loads, glass thickness and fixings need a facade engineer.

## Sources
- Blender 5.2 Python API (NodeTreeInterface.new_socket, GeometryNodeTree.is_modifier, NodesModifier): https://docs.blender.org/api/current/
- 4.0 interface change (`tree.interface`): https://developer.blender.org/docs/release_notes/4.0/python_api/
- 5.0 Python API and Geometry Nodes changes: https://developer.blender.org/docs/release_notes/5.0/python_api/ , https://developer.blender.org/docs/release_notes/5.0/geometry_nodes/
- Geometry Nodes manual: https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html
- Studio Tim Fu / Cacao Greenhouse rationalised to flat panels: https://aecmag.com/features/studio-tim-fu-ai-driven-design/
