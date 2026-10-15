---
name: civil-site-earthworks
description: Plan, model, check, and report civil site terrain, survey surfaces, grading, platforms, slopes, and cut/fill quantities with free tools such as FreeCAD, QGIS, and IFC. Use for preliminary earthworks and audit-ready quantity workflows, not final engineer certification.
---

# Civil Site and Earthworks

Create a traceable existing-ground to proposed-ground workflow without inventing survey control, design criteria, or geotechnical factors.

## Establish the survey contract

Before modeling, confirm coordinate reference system, horizontal and vertical datums, units, survey date, point/breakline source, site boundary, exclusions, design surfaces, required output, and governing standard. Never assume that local coordinates are georeferenced.

Read [references/open-earthworks-stack.md](references/open-earthworks-stack.md) when choosing tools or exchange formats.
Read [references/video-study.md](references/video-study.md) for the verified FreeCAD Road Workbench survey-point-to-terrain demonstration scope and its acceptance checks.

## Workflow

1. Preserve the original survey data. Check duplicates, spikes, voids, swapped axes, unit scale, impossible elevations, and missing breaklines.
2. Build the existing-ground surface with boundary and breakline control. Record interpolation method and triangle-edit decisions.
3. Define proposed platforms, roads, batters, retaining interfaces, drainage constraints, and tie-ins from user-supplied criteria.
4. Compare existing and proposed surfaces over one explicit calculation boundary. Separate cut, fill, unsuitable material, topsoil strip, and imported/exported material where data supports it.
5. Apply shrink, swell, compaction, bulking, and wastage only when the user supplies project values or an authoritative source. Report raw geometric volume separately from adjusted quantities.
6. Produce check views: contours, spot levels, slopes, sections, cut/fill map, balance summary, and exception list.

## Acceptance criteria

- CRS, datum, units, boundaries, surfaces, and assumptions are recorded.
- Surface extents and sample spot levels match the source within stated tolerance.
- No unexplained spikes, holes, inverted triangles, or boundary leakage remain.
- Cut and fill recompute consistently from the saved surfaces and boundary.
- Quantity output separates measured geometry from project factors and clearly marks unverified inputs.

Ask before operating FreeCAD/IFC MCP. Treat results as preliminary until reviewed against the survey, geotechnical information, drainage design, and local authority requirements by a qualified civil engineer or surveyor.
