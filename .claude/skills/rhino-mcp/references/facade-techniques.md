# Rhino facade techniques

Code for `run_python` (CPython 3 in Rhino 8). The official server gives you `__rhino_doc__`; use it instead of `scriptcontext.doc`. Signatures come from McNeel's Python stubs (last updated 2024-08, so a new Rhino 8 overload may be missing). Print results and keep scripts short: one step per call, so a failure is easy to see.

## Key RhinoCommon calls
| Need | Call |
|---|---|
| parameter range | `Surface.Domain(direction) -> Interval` |
| point / normal / frame | `Surface.PointAt(u, v)`, `Surface.NormalAt(u, v)`, `Surface.FrameAt(u, v) -> (bool, Plane)` |
| curvature | `Surface.CurvatureAt(u, v) -> SurfaceCurvature` → `.Gaussian`, `.Mean`, `.Kappa(i)`, `.Direction(i)` |
| iso-curves | `Surface.IsoCurve(direction, constantParameter)` |
| shape tests | `Surface.IsPlanar(tol)`, `IsCylinder(tol)`, `IsSphere(tol)` |
| closest point | `Surface.ClosestPoint(pt) -> (bool, u, v)` |
| quad panel | `Brep.CreateFromCornerPoints(a, b, c, d, tol)` (non-coplanar corners give a twisted face) |
| flat panel from outline | `Brep.CreatePlanarBreps(curves, tol)` |
| developable strip | `Brep.CreateDevelopableLoft(crv0, crv1, reverse0, reverse1, density)` or `(rail0: NurbsCurve, rail1: NurbsCurve, fixedRulings)` |
| loft | `Brep.CreateFromLoft(curves, start, end, loftType, closed)` |
| floor slices | `Brep.CreateContourCurves(brep, plane)` / `(brep, start, end, interval)` |
| split | `Brep.Split(cutters, tol)` |
| divide | `Curve.DivideByCount(n, includeEnds)`, `Curve.DivideByLength(len, includeEnds)`, `Curve.PerpendicularFrameAt(t)`, `Curve.Offset(plane, dist, tol, cornerStyle)` |
| flatness | `Plane.FitPlaneToPoints(points) -> (PlaneFitResult, Plane, maxDeviation)`; `Point3d.ArePointsCoplanar(points, tol)` (owning class 未验证) |
| cut sheets | `Unroller(brep).PerformUnroll()` |

## 1. Context read
```python
import Rhino
doc = __rhino_doc__
print(doc.ModelUnitSystem, doc.ModelAbsoluteTolerance)
for layer in doc.Layers:
    objs = doc.Objects.FindByLayer(layer)
    if objs:
        bb = Rhino.Geometry.BoundingBox.Empty
        for o in objs:
            bb.Union(o.Geometry.GetBoundingBox(True))
        print(layer.FullPath, len(objs), bb.Min, bb.Max)
```
Report what each layer seems to be (site, neighbours, massing) and ask the user to confirm before modelling.

## 2. Curvature map
```python
import Rhino
doc = __rhino_doc__
obj = doc.Objects.FindId(SELECTED_ID)          # get the id from get_selection
srf = obj.Geometry.Faces[0].UnderlyingSurface() if isinstance(obj.Geometry, Rhino.Geometry.Brep) else obj.Geometry
du, dv = srf.Domain(0), srf.Domain(1)
n = 20
ks = []
for i in range(n + 1):
    for j in range(n + 1):
        u = du.ParameterAt(i / n); v = dv.ParameterAt(j / n)
        c = srf.CurvatureAt(u, v)
        if c: ks.append(c.Gaussian)
flat = sum(1 for k in ks if abs(k) < 1e-4)
print("samples", len(ks), "near-zero K", flat, "min", min(ks), "max", max(ks))
```
Near-zero K (single-curved or flat) → quads or developable strips. Large |K| → triangles, smaller panels or cold-bent glass. The 1e-4 threshold is a placeholder: it depends on units and panel size, so tell the user it's a design-study value.

## 3. Quad panels + flatness report
```python
import Rhino, System
doc = __rhino_doc__; tol = doc.ModelAbsoluteTolerance
# srf: from step 2
nu, nv = 24, 12
du, dv = srf.Domain(0), srf.Domain(1)
P = [[srf.PointAt(du.ParameterAt(i / nu), dv.ParameterAt(j / nv)) for j in range(nv + 1)] for i in range(nu + 1)]
layer = doc.Layers.FindName("FCD_Panels") or doc.Layers[doc.Layers.Add("FCD_Panels", System.Drawing.Color.Gray)]
worst, twisted = 0.0, 0
for i in range(nu):
    for j in range(nv):
        q = [P[i][j], P[i + 1][j], P[i + 1][j + 1], P[i][j + 1]]
        res, plane, dev = Rhino.Geometry.Plane.FitPlaneToPoints(q)
        worst = max(worst, dev); twisted += dev > 0.002
        b = Rhino.Geometry.Brep.CreateFromCornerPoints(q[0], q[1], q[2], q[3], tol)
        if b:
            attr = Rhino.DocObjects.ObjectAttributes(); attr.LayerIndex = layer.Index
            doc.Objects.AddBrep(b, attr)
doc.Views.Redraw()
print("panels", nu * nv, "twisted >2 mm", twisted, "worst", worst)
```
(The 2 mm limit is a placeholder for the facade engineer's value.) Put new geometry on its own layer so it's easy to delete or hide, and don't touch the user's layers.

## 4. Developable strips and cutting sheets
Divide the surface into iso-curves in one direction (`IsoCurve`), then loft neighbours with `CreateDevelopableLoft(c0, c1, False, False, density)`. If it returns nothing for a pair, that strip can't be developable at that width: use narrower strips or a different direction. Unroll each strip with `Unroller(strip).PerformUnroll()` and lay the flats out on a separate layer for cutting.

## 5. Facade detail
- **PanelingTools** (McNeel): build an ordered grid (`ptGridSurfaceDomainNumber`), then `ptPanelGrid` or `ptPanelGridQuads` (flat quads with a max deviation). Plain points have no u,v order and can't be panelled. On Rhino 8 for Mac the menu may be missing, but the commands still work from the command line. Run them with `run_command`.
- **LunchBox** (Proving Ground, free, LGPL): Grasshopper components for quad, diamond, triangle, hexagon and skewed panels. Install through `PackageManager`. Build with `g1_apply_graph` (sliders + components + wires in one call), then `g1_solve_graph`.
- **Attractor**: panel area centre → distance to attractor point or curve → Remap / Graph Mapper → opening size, rotation or scale.
- Other plug-ins people combine: Kangaroo (form-finding, planarising), Ladybug (sun and environment), Weaverbird (meshes).
- **Attach:** mullions offset from panel edges, fins standing on slab edges, nothing hanging in space (user rule). Check by sectioning (`CreateContourCurves`) at each floor and looking for loose pieces.

## 6. Modular block distribution
Slice the massing per floor (`CreateContourCurves(brep, start, end, floor_height)`), turn each slice into a planar region, and place block modules only on upward faces with their base point on the slab. Check overlaps with `Brep.CreateBooleanIntersection` on a copy, or bounding boxes for speed.

## 7. Hand over to Blender (free rendering)
Export the result (OBJ or FBX, on a copy, with `run_command` `-Export`; ask first because it writes a file), then go to `archviz` in Blender. If the user has no Rhino licence at all, do the whole job in Blender with `parametric-facade`.

## Sources
- RhinoCommon stubs: https://github.com/mcneel/pythonstubs (`stubs/Rhino/Rhino-stubs/Geometry/__init__.pyi`)
- Rhino Python guides: https://developer.rhino3d.com/guides/rhinopython/
- PanelingTools: https://wiki.mcneel.com/labs/panelingcommands , manual https://wiki.mcneel.com/_media/labs/panelingtoolsmanual.pdf , Mac menu https://discourse.mcneel.com/t/panelingtools-ui-missing-in-rhino-8-for-mac/216240 , point ordering https://discourse.mcneel.com/t/how-to-convert-regular-points-to-paneling-points/74634
- LunchBox: https://apps.provingground.io/install-lunchbox-for-grasshopper/ , https://howtorhino.com/rhino-grasshopper-tutorials/lunchbox-plugin/
- Flat quads on double curvature: https://discourse.mcneel.com/t/planarizing-quad-panels-on-double-curved-surface/116811
- Attractor facades: https://www.studiomatrx.org/students/computational-parametric-design/responsive-facades , https://grasshopper3d.com/video/grasshopper-tutorial-parametric-facade , https://www.studiomatrx.org/students/parametric-architecture/parametric-tools-and-techniques
- RhinoAI `run_python` / `__rhino_doc__`: https://github.com/mcneel/RhinoAI/tree/main/rhino/plugin/Tools
