# Underground utility coordination

Use for water/drainage/power/communications routes and their relationships to foundations, roads and terrain. General model validation remains in model-quality.md.

## Establish a usable basis

Identify model revisions, common horizontal/vertical reference, units, placement/georeferencing, ground/design surface, utility class, existing/proposed status, source confidence and actual geometry availability. State any survey uncertainty and missing depth information.

Classify representations before measuring: centerline-only, nominal diameter, outer physical surface, insulation/protection, excavation envelope and maintenance envelope are different geometries. A line intersection is not a proven pipe collision; center-to-center distance is not surface clearance.

## Select rules and tools

Obtain the applicable project/jurisdiction rules for cover, crossing/separation, access and permitted exceptions. Do not invent a universal clearance or burial depth.

Use the connected IfcMCP or installed IfcClash/IfcOpenShell geometry tools after inspecting current arguments. Separate:
- physical intersection;
- minimum surface-to-surface clearance;
- operational/maintenance or excavation envelope conflicts.

Bounding boxes may shortlist pairs but cannot prove exact contact or clearance, particularly for oblique/curved assets. Do not label element-center distances as penetration depth.

## Review

1. Check utility-to-utility and utility-to-structure pairs with explicit selections and exclusions.
2. For cover, compare the relevant pipe/protection top with the governing surface at the corresponding horizontal location; do not compare an arbitrary ground vertex or pipe invert as if it were top cover.
3. Inspect crossings, changes of grade, chambers, entries, foundation toes and access/removal space.
4. Confirm results in section/viewpoint with stable GlobalIds, model revisions, coordinates, units and rule IDs.
5. Distinguish intentional connections from unintended overlaps; record a reviewed exception instead of silently deleting all same-system clashes.
6. Recheck after a revision, retaining issue identity and disposition. Do not move utilities or edit design solely because a clash report was requested.

## Acceptance

Issue rows include the two objects, measurement definition, actual distance/overlap, criterion/source, tolerance, location/viewpoint and review status. Missing surfaces, centerline-only data or unknown rules remain incomplete. A clean geometric model is not evidence of surveyed underground conditions.

## Sources

Reviewed 2026-10-15: [IfcClash](https://docs.ifcopenshell.org/ifcclash.html), [IfcOpenShell geometry tree](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_tree.html), and [IfcMCP](https://docs.ifcopenshell.org/ifcmcp.html). Third-party bounding-box Skill examples were inspected as background, not copied as a precise clearance engine.
