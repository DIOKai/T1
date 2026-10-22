# Facade recipes (Geometry Nodes)

Seven patterns, each written as a node chain. Recipes 4 and 5 are prebuilt in `scripts/facade_nodes.py` (`FP_Fins`, `FP_FloorStack`) and recipe 2 is `FP_PlanarCheck`. The others are short enough to build on the spot with the same helpers (`_G`, `_io`, `_sock` in the script) or by hand. These are method suggestions put together from the node set, not copied from one source. Node names below are the UI names; identifiers are in the table at the end.

Each recipe ends with **Attach**: how the result stays on the structure. That comes from the user's rule that nothing in a building may float.

## 1. Panelize a flat or curved surface
Surface mesh (a Grid bent with Set Position, or a converted NURBS surface) → **Split Edges** (each panel becomes separate) → **Scale Elements** (domain Face, scale < 1 leaves joints; drive the scale with Geometry Proximity / an attractor for openings that open and close) → **Extrude Mesh** (Faces, Individual on, Offset Scale = panel thickness).
- Panel size comes from the surface's subdivision: pick the grid so panels come out around the target module.
- **Attach:** panels stay on the surface (scaling is about each face's own centre). Keep the joint (1 − scale) small, about 10–20 mm at real scale, so they read as one skin.

## 2. Check, and rationalise, flat panels
**Is Face Planar** (Threshold in metres) → **Store Named Attribute** (`fp_planar`, Boolean, Face) → **Set Material** red for all, grey where planar. That is `FP_PlanarCheck`. `planarity_report()` gives the numbers.
Fixes, cheapest first:
- **Triangulate** only the non-planar faces (Selection = not planar). Triangles are always flat, but there are twice as many panels.
- Change the base surface: cylinders, cones and translational surfaces can be tiled with flat quads; doubly curved ones need varying edge lengths or angles (McNeel forum discussion, see sources).
- Split into strips (recipe 7) or plan for cold-bent glass, and say that this is a cost decision for the facade engineer.
- **Attach:** unchanged; this only re-cuts faces.

## 3. Mullions and transoms
**Mesh to Curve** on the panel edges (all edges, or only vertical ones: use Edge Vertices, then normalize(Position 2 − Position 1) and |z| > 0.95) → **Curve to Mesh** with a **Quadrilateral** profile (e.g. 50 × 150 mm) → Set Material.
- Without a set curve normal the profile may roll on curved edges. Check from close up; for flat walls it's fine.
- **Attach:** profiles run along existing edges, so they sit on the panel joints. Make the bottom transom line the slab edge.

## 4. Sun fins / louvres (`FP_Fins`)
Horizontal edges below the roof line (Edge Vertices + Bounding Box) → **Mesh to Curve** → **Resample Curve** (Length = Spacing) → points; **Sample Nearest Surface** of the wall's Normal (flattened to horizontal) → **Align Rotation to Vector** (X axis, pivot Z) → **Instance on Points** (unit Cube, Scale = depth × thickness × height) → **Realize Instances**. Depth comes from **Map Range** of the distance to the Attractor object (near = Max Depth).
- Rotated fins (angle by attractor or random) rotate about their own back edge, not the centre. Otherwise they leave the wall: offset by half the depth *after* rotating.
- **Attach:** each fin's back face lies on the wall line, its bottom on a floor line, and its height equals floor-to-floor so it reaches the next slab line. The roof line is excluded so fins don't stick up past the parapet.

## 5. Stacked floor plates (`FP_FloorStack`)
**Fill Curve** (footprint) → **Extrude Mesh** down by slab thickness + flipped cap = one slab; **Mesh Line** (Count = Floors + 1, Offset = (0, 0, floor height)) → **Instance on Points** of the slab, rotation = Index × Twist (Align Rotation to Vector of (cos a, sin a, 0)) → **Realize Instances**; core = footprint × Core Scale extruded from 0 to the roof level. A **Repeat Zone** does the same if each floor needs to depend on the one below (setbacks, tapering).
- Taper: scale each instance by `1 − Index × k`.
- **Attach:** the ground slab sits on the ground (its top at z = 0) and the core runs through every slab. With heavy twist or taper, check that the core stays inside every slab (`find_floating`). Add perimeter columns (instances on the footprint's points of the *smallest* floor) when the slabs cantilever a long way.

## 6. Modular block distribution
**Distribute Points on Faces** (Poisson, Distance Min = module size, so blocks don't collide) or a grid of points → **Instance on Points** with **Collection Info** (Separate Children + Reset Children on, Pick Instance on, Instance Index from Random Value (integer) or from an attribute) → **Rotate Instances** in 90° steps for variety → Realize Instances.
- For stacked "block" massing, distribute on the *top faces* of the blocks below (select faces with Normal z > 0.9). Each new block then stands on an existing one.
- **Attach:** points lie on faces that point up (slabs, roofs, the ground), and each module's origin must be at its *bottom* centre. Check the collection's origins first: a module with a centred origin sinks halfway into the slab.

## 7. Strips on a curved surface (developable approximation)
Cut the surface into strips along one direction: Resample the strip-edge curves to the same count, then build ruled quads between neighbouring curves (one quad row per strip) → recipe 2 to check planarity per quad.
- Blender can't prove a strip is developable. Use a narrow strip and a planar check per quad as a proxy. For production, do this in Rhino (`Brep.CreateDevelopableLoft`, see `rhino-mcp`) if the user has it.
- **Attach:** strips share their long edges, so the skin stays closed. Fix the strips to slab edges with transoms (recipe 3).

## Links to other skills
- **Building shell first:** `floorplan-to-blender` builds walls, slabs and openings from a plan. Run the facade on its exterior walls (and keep its rule: real glass with real rooms behind it).
- **Paid alternative:** `rhino-mcp` does the same with Grasshopper, LunchBox and PanelingTools in Rhino 8 (paid, $995; 90-day trial). Ask before using it, and only when the user already has Rhino.
- **Rendering:** `archviz` (+ `archviz-cinematic` if installed). **Free models for modules:** `free-3d-assets`.

## Node identifiers
Verified to exist in the Blender 5.2 API docs (research notes, 2026-10-22): `GeometryNodeSplitEdges`, `GeometryNodeScaleElements`, `GeometryNodeExtrudeMesh`, `GeometryNodeInputMeshFaceIsPlanar`, `GeometryNodeStoreNamedAttribute`, `GeometryNodeSetMaterial`, `GeometryNodeTriangulate`, `GeometryNodeMeshToCurve`, `GeometryNodeCurveToMesh`, `GeometryNodeCurvePrimitiveQuadrilateral`, `GeometryNodeResampleCurve`, `GeometryNodeSampleNearestSurface`, `FunctionNodeAlignRotationToVector` (not `GeometryNode…`), `GeometryNodeInstanceOnPoints`, `GeometryNodeRealizeInstances`, `GeometryNodeProximity`, `GeometryNodeFillCurve`, `GeometryNodeMeshLine`, `GeometryNodeRepeatInput`, `GeometryNodeDistributePointsOnFaces`, `GeometryNodeCollectionInfo`, `GeometryNodeRotateInstances`, `FunctionNodeRandomValue`, `GeometryNodeMeshGrid`, `GeometryNodeSetPosition`, `GeometryNodeBoundBox`.
Not real: `GeometryNodeAlignRotationToVector`, `GeometryNodeGrid`.
Not checked: `GeometryNodeInputMeshEdgeVertices`, `GeometryNodeMeshCube`, and the `ShaderNode*` math nodes; socket names in general. Print `node.inputs.keys()` once in Blender before relying on a name.
Version note: in 5.1/5.2 Realize Instances gained `realize_to_point_domain` ("for compatibility with 5.0 and earlier"), so its output may differ slightly between versions.

## Sources
- Blender 5.2 API node pages, e.g. https://docs.blender.org/api/current/bpy.types.GeometryNodeRealizeInstances.html
- Geometry Nodes manual: https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/index.html ; Distribute Points on Faces: https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/point/distribute_points_on_faces.html
- Flat quads on curved surfaces: https://discourse.mcneel.com/t/planarizing-quad-panels-on-double-curved-surface/116811
- Attractor facades (method): https://www.studiomatrx.org/students/computational-parametric-design/responsive-facades
- Free GN building generator to study: https://80.lv/articles/free-post-soviet-building-generator-for-blender/
