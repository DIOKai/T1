# Revit API essentials for agent scripts

Written for pyRevit's `run_query` / `run_modify` (Python against the Revit API). The same API sits under the C# bridges (`send_code_to_revit`). **Signatures below are the common ones from memory and forum/docs checks — confirm each with `lookup_revit_api` in the user's Revit before relying on it**; overloads change between Revit years.

## Things that bite first

1. **Units.** Internal length is **feet**, area ft², angles radians. Convert every number you compute: `ft = m / 0.3048`; report back `m = ft * 0.3048`, `m² = ft² * 0.09290304`. Revit 2021+ also has `DB.UnitUtils.ConvertToInternalUnits(3.0, DB.UnitTypeId.Meters)` (ForgeTypeId API; the old `DisplayUnitType` enum is gone in newer versions).
2. **Transactions.** Any model change needs an open `DB.Transaction` (or the runner's own). Read pyRevit's `revit-scripting` skill for whether `run_modify` wraps one for you — its host fails a run that leaves a transaction open, so if you open one, close it (`Commit` / `RollBack`) in `try/finally`.
3. **Element vs type.** `FilteredElementCollector(doc).OfClass(DB.Wall)` returns instances *and* nothing else, but `OfCategory(...)` returns types too unless you add `.WhereElementIsNotElementType()`.
4. **Names are data.** Pick wall/floor/roof types, families and levels from a query result. A made-up type name just fails; a fuzzy match may pick the wrong one — show the user what you matched.
5. **Python engine.** `get_context.scripting` says IronPython 2.7, IronPython 3.4 or CPython. IronPython 3.4 lacks walrus, `match`, `async`, `1_000`. Write plain Python 3 that also avoids f-string tricks if the engine is 2.7.
6. **Families must be loaded and activated.** `symbol.IsActive` false → `symbol.Activate()` (then `doc.Regenerate()`) before placing instances. Loading a family from disk (`doc.LoadFamily(path)`) is a model change.

## Read-only patterns (run_query)

```python
levels = sorted(DB.FilteredElementCollector(doc).OfClass(DB.Level), key=lambda l: l.Elevation)
wall_types = DB.FilteredElementCollector(doc).OfClass(DB.WallType)
floor_types = DB.FilteredElementCollector(doc).OfClass(DB.FloorType)
doors = (DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Doors)
         .OfClass(DB.FamilySymbol))
mats = DB.FilteredElementCollector(doc).OfClass(DB.Material)
result = {
    "levels": [{"id": l.Id, "name": l.Name, "elev_m": round(l.Elevation * 0.3048, 3)} for l in levels],
    "wall_types": [DB.Element.Name.GetValue(t) for t in wall_types],   # .Name works on most; this form is IronPython-safe
    "floor_types": [DB.Element.Name.GetValue(t) for t in floor_types],
    "door_types": ["%s : %s" % (s.FamilyName, DB.Element.Name.GetValue(s)) for s in doors],
    "materials": [{"name": m.Name, "shading_rgb": [m.Color.Red, m.Color.Green, m.Color.Blue]} for m in mats if m.Color.IsValid],
}
```
`Material.Color` is the material's **shading colour** (Graphics tab) — the colour the glTF exporter in `revit-to-web.md` writes.

Parameters: `el.LookupParameter("Comments")` (by name, language-dependent) or `el.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)` (stable). Read with `.AsString()`, `.AsDouble()` (internal units), `.AsInteger()`, `.AsElementId()`, `.AsValueString()` (formatted).

## Creating things (run_modify) — check each with lookup_revit_api

| Thing | Usual call | Notes |
|---|---|---|
| Level | `DB.Level.Create(doc, elevation_ft)` then `.Name = "Level 2"` | Plan views aren't created automatically → `DB.ViewPlan.Create(doc, floor_plan_view_family_type_id, level.Id)` |
| Wall | `DB.Wall.Create(doc, DB.Line.CreateBound(p0, p1), wall_type_id, level_id, height_ft, offset_ft, flip, structural)` | Several overloads; the simplest is `(doc, line, level_id, structural)`. Set top constraint via `WALL_HEIGHT_TYPE` / `WALL_USER_HEIGHT_PARAM`. Draw walls on their location line (default wall centerline — check `WALL_KEY_REF_PARAM`). |
| Floor | `DB.Floor.Create(doc, [curve_loop], floor_type_id, level_id)` | Revit 2022+; `doc.Create.NewFloor` is obsolete since 2022. Build a `DB.CurveLoop` of closed lines, counter-clockwise. |
| Roof | `doc.Create.NewFootPrintRoof(curve_array, level, roof_type, out model_curve_array)` | The `out` argument is awkward from Python — look it up and test with `dry_run`; or use an extrusion roof. |
| Door / window | `doc.Create.NewFamilyInstance(location_xyz, symbol, host_wall, level, DB.Structure.StructuralType.NonStructural)` | Host must be a wall; location on the wall's location line; sill height via `INSTANCE_SILL_HEIGHT_PARAM`. |
| Furniture / point family | `doc.Create.NewFamilyInstance(xyz, symbol, level, NonStructural)` | Activate the symbol first. |
| Free-form / sculpture | `DB.DirectShape.CreateElement(doc, DB.ElementId(DB.BuiltInCategory.OST_GenericModel))` + `.SetShape(list_of_GeometryObject)` | Geometry from `TessellatedShapeBuilder` (meshes) or solids. Not schedulable as walls/floors — it's a look-alike. |
| 3D view | `DB.View3D.CreateIsometric(doc, three_d_view_family_type_id)` | Section box: `view.SetSectionBox(bbox)`. |
| Material | `DB.Material.Create(doc, "Name")` → `doc.GetElement(id)`; `.Color = DB.Color(r, g, b)` | Sets the shading colour (what a colour map uses). Changing materials is a model change → approval. |

Coordinates: `DB.XYZ(x_ft, y_ft, z_ft)`. Project base point / survey point: don't move them; build relative to an origin agreed with the user.

## Staged, re-runnable builds

- Each stage sets Comments = `ai:<stage>` on everything it creates. Re-running a stage = delete elements with that tag (in the same `run_modify`), then create again. Never delete untagged elements unless the user named them.
- Keep coordinates and dimensions in a workspace module (`workspace=` folder on `run_query`/`run_modify`) so every stage reads the same data — e.g. the `layout.json` written by `floorplan-to-blender` (metres; convert to feet when creating).
- After a stage: `capture_view` (3d) and, for plans, the level's plan view; compare against the brief/plan; report counts and key dimensions in metres.
- Warnings Revit raises (joins, overlaps) come back in the run envelope (`dialogs` / failures). Read them; don't suppress them blindly.

## Sources
- pyRevit 7.0.0 release notes (script contract, guards): https://github.com/pyrevitlabs/pyRevit/releases/tag/v7.0.0.26278%2B2233
- pyRevit agent runtime docs: https://docs.pyrevitlabs.io/agent-runtime/
- `NewFloor` obsolete since 2022 → `Floor.Create`: https://www.rvtdocs.com/2022/a026924c-ed96-761a-8d0d-2114086fe656 , https://forums.autodesk.com/t5/revit-api-forum/create-floor-revit-api-2023/m-p/11265961
- FamilyInstance class (2024): https://www.revitapidocs.com/2024/0d2231f8-91e6-794f-92ae-16aad8014b27.htm
- BIMBridge working method (units, staged tags): https://github.com/kenpro0/bimbridge-mcp/blob/main/skills/bimbridge/SKILL.md
- Other signatures in the table: general Revit API knowledge, **not individually re-checked** — that's why every one says "lookup_revit_api first".
