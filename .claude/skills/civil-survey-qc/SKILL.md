---
name: civil-survey-qc
description: Inspect civil survey point files, coordinate metadata, control checks, breaklines, and terrain-readiness before modeling or earthwork quantities. Use for CSV/TXT survey QA; this skill does not certify survey accuracy or design infrastructure.
---

# Civil Survey QC

Separate structural file checks from spatial accuracy and project acceptance. Preserve raw observations and report issues without silently correcting them.

## Establish the data contract

Confirm the field order (for example PNEZD versus PENZD), delimiter, encoding, header presence, units for each axis, horizontal CRS/epoch, height type/vertical datum and source date. Keep point IDs as strings, including leading zeros. Do not infer a Malaysian CRS or datum from the user's location.

Read [survey-review.md](references/survey-review.md) for spatial/control checks. Read [script-use.md](references/script-use.md) when using the included point-file auditor.

## Inspect

1. Hash the raw source; record provenance, file size, point count and schema.
2. Inspect malformed rows, duplicate IDs/coordinates, missing values and nonfinite numbers. Zero Easting/Northing/elevation can be legitimate local coordinates; do not delete zeros.
3. Check declared axis order, units and metadata against supplied control and project extent. A plausible extent cannot prove the CRS or detect every swapped axis.
4. Compare controls using documented point correspondence and units. Separate horizontal/vertical residuals; do not invent a tolerance or automatically apply a shift.
5. Inspect spatial coverage, anomalous levels, breaklines, boundary and code completeness against project requirements. Avoid connecting surfaces across rivers/walls or bridging survey gaps without evidence.
6. Produce a red/amber/green report with source row/point IDs, actual value, criterion, severity, suggested investigation and disposition.

Red: unusable structural data or a failed supplied criterion. Amber: unknown metadata, suspected anomaly or unavailable check. Green applies only to checks actually completed; never call the survey accurate merely because the file parses.

## Local helper

scripts/audit_points.py uses only Python's standard library and reads one explicitly scoped CSV/TXT. It outputs JSON to stdout or a new report file; it does not edit points, transform CRS, calculate volume or perform field certification. It requires declared field order, header mode and units. Geographic degrees and mixed-axis units are outside this helper's scope.

Use supplied bounds/outlier thresholds only as review criteria; the helper will not invent them. For large point clouds use an appropriate spatial pipeline rather than assuming this in-memory CSV helper scales indefinitely.

## Handoff

Give the raw hash, declared schema/units/datums, summary of performed checks, missing criteria and a named list of unresolved rows/points. Keep proposed corrections separate from originals. Only pass to terrain/earthwork modeling after the project's relevant input requirements are met; otherwise state what remains unknown.
