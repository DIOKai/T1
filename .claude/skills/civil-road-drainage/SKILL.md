---
name: civil-road-drainage
description: Develop and review preliminary road alignments, profiles, corridors, cross-sections, earthworks interfaces, culverts, and storm-drainage layouts with FreeCAD/IFC and other free tools. Use when road or drainage geometry and engineering checks must remain traceable to supplied standards and inputs.
---

# Civil Road and Drainage

Coordinate road geometry and drainage while keeping geometric modeling separate from code compliance and hydraulic design approval.

## Required inputs

Confirm project coordinates and datum, terrain source, design standard and jurisdiction, design speed, vehicle/loading class, horizontal and vertical controls, lane/shoulder widths, crossfalls, superelevation rules, sight-distance criteria, pavement scope, rainfall data, return period, catchments, runoff method, allowable velocities, outfalls, tailwater, utilities, and environmental constraints.

For Malaysian work, request the applicable JKR/MSMA project criteria and edition. Do not invent coefficients, recurrence intervals, minimum radii, pipe sizes, or national-annex values.

Read [references/free-road-stack.md](references/free-road-stack.md) before selecting software or IFC entities.

## Road workflow

1. Audit terrain, survey control, and constraints.
2. Build horizontal alignment, stationing, vertical profile, crossfall/superelevation, assemblies, and regions from explicit design criteria.
3. Generate applied sections and corridor surfaces. Review tie-ins, transitions, intersections, clearances, earthworks, and constructability.
4. Produce plan/profile, cross-sections, setting-out data, and an exception register.

## Drainage workflow

1. Delineate catchments and flow paths from verified terrain and proposed grading.
2. Record the supplied rainfall source, loss/runoff assumptions, design event, time of concentration method, and boundary conditions.
3. Lay out inlets, channels, pipes, culverts, manholes, outlets, and erosion protection around the road geometry and utilities.
4. Check continuity, cover, grade, inlet/outlet levels, surcharge/flood path, velocity/erosion risk, maintenance access, and downstream constraints using the chosen authoritative method.
5. Mark any element that has geometry only and has not received a hydraulic capacity check.

## Acceptance criteria

- Every controlling value cites a supplied standard, project brief, survey, or calculation.
- Stationing, profile, cross-sections, structures, and drainage share one coordinate/unit contract.
- Road and drainage geometry contain no unexplained discontinuities or inverted grades.
- Reports distinguish modeled geometry, calculated capacity, and unverified assumptions.
- A qualified civil engineer reviews safety, standards compliance, hydrology/hydraulics, geotechnical inputs, and issued drawings.

Ask before using live FreeCAD or IFC MCP. Never represent preliminary model output as construction approval.
