# Road setting-out schedules

Use for chainage/station, offset, design elevation and crossfall exports. A point export tool does not automatically provide a complete alignment-based setting-out system.

## Confirm the coordinate contract

Record alignment/profile/surface revisions; horizontal CRS, vertical datum and epoch; units at each API boundary; start station; station equations; increasing-station direction; left/right offset sign; profile grade and crossfall convention; rounding and required precision. Do not infer API units from a GUI unit label.

Inspect the installed FreeCAD Road objects and methods. Preserve straight, circular and transition-curve geometry; stationing by sampled chord length is an approximation, not exact curve stationing. Do not invent an alignment method name or claim every Road workbench feature is complete.

## Generate and review

1. Establish station ranges, regular interval and special stations: tangent/curve boundaries, intersections, changes of grade/crossfall and supplied control points.
2. Evaluate the alignment's position and unit tangent at the intended station through a verified API or documented analytic method.
3. Apply the declared offset convention. For EN coordinates and positive-left offset o, the left normal of tangent (tE,tN) is (-tN,tE); thus Eoffset=E-o*tN and Noffset=N+o*tE. This geometric convention still needs agreement with the user's project.
4. Derive Z from the chosen profile/crossfall or design surface. Keep percent versus ratio and positive-left/right signs explicit. Do not apply one planar crossfall across a crowned/region-changing section.
5. Produce point ID, alignment/revision, station, signed offset, E/N/Z, feature code, datum/units and calculation method. Keep full precision internally, round only the delivery copy.
6. Compare exports against independent control/check stations and inspect the plotted points.

## Road Workbench limits observed in source

The reviewed README marks Tables, Superelevation, Volume and LandXML export incomplete. The point-group exporter is real code, but formats E/N/Z to three decimals and opens the destination for writing. Its five column mappings must be unique valid positions.

Export to a fresh destination, check column mapping and precision against the task, then read the result back. It does not prove a full road setting-out table, station-equation handling or sufficient project precision. Recheck the installed revision before relying on these observations.

## Acceptance examples

- Straight northward tangent (0,1), positive-left offset 2: Easting decreases by 2 and Northing is unchanged.
- Circular curve: compare a known analytic point/tangent; chord stationing must not silently replace arc stationing.
- Station equation: display station versus continuous alignment parameter stays traceable.
- Crown/region transition: left/right elevations follow the specified section.
- Export round-trip: IDs, order, units, signs and elevations agree within the supplied tolerance; unmatched controls are visible.

## Sources

Reviewed 2026-10-15:
- [FreeCAD Road README](https://github.com/HakanSeven12/Road).
- [Point export source](https://github.com/HakanSeven12/Road/blob/main/freecad/road/tasks/task_geopoints_export.py).
- [Alignment source](https://github.com/HakanSeven12/Road/blob/main/freecad/road/geometry/alignment/alignment.py).

These references guide inspection; no live FreeCAD command or verified end-to-end road export is claimed by this document.
