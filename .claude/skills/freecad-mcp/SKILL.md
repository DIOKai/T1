---
name: freecad-mcp
description: Inspect, create, edit, validate, and export models in a live FreeCAD session through neka-nat/freecad-mcp. Use for parametric CAD, screenshots, and exploratory FEM; not for certified engineering conclusions.
---

# FreeCAD MCP

Use the connected FreeCAD MCP for work on the user's local documents. Preserve editable parametric structure and make dimensions, units, constraints, and output paths explicit.

## Connection and authorization

- Before live access, explain whether the planned calls are read-only or mutating and obtain approval.
- If the MCP or FreeCAD add-on is unavailable, report the missing connection. Do not install or reconfigure it automatically.
- Keep the RPC service on localhost. Remote access requires separate approval, an authentication token, a narrow allowlist, and preferably an SSH tunnel.
- Prefer typed MCP tools. Code-execution tools run arbitrary Python with the user's permissions and are a last resort.
- Do not enable blanket `alwaysAllow` permissions.

## Modeling workflow

1. Inspect open documents, object hierarchy, units, active body/sketch, constraints, and current view before changing anything.
2. Confirm ambiguous dimensions, tolerances, reference planes, materials, loads, and output location.
3. Build with native editable features and constrained sketches where practical. Use transactions, recompute after changes, and keep names meaningful.
4. Validate the result with shape checks, object properties, dimensions or bounding boxes, constraint status, and screenshots from useful views.
5. Save to a new file or export path by default. Overwrite an existing FCStd, STEP, STL, DXF, or other file only with explicit permission.

## FEM and engineering limits

- Treat FEM as exploratory assistance, not professional certification.
- Verify unit systems, material properties, load magnitude/direction, supports, mesh quality, solver status, and reaction balance independently.
- Do not invent Malaysian National Annex values, SMM2 rules, material data, safety factors, or code requirements. Ask the user for project-specific inputs.
- Clearly separate modeled facts, assumptions, solver output, and engineering judgment.

## Acceptance

Report the document and objects changed, requested dimensions, validation results, and saved/exported paths. If FreeCAD or a solver reports an error or verification is incomplete, do not claim success.

Source: https://github.com/neka-nat/freecad-mcp
