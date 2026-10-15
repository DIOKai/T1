---
name: civil-structural-fem
description: Set up, run, diagnose, and review preliminary structural finite-element analyses in FreeCAD FEM with CalculiX using traceable geometry, materials, loads, constraints, meshes, units, convergence checks, and engineering review boundaries.
---

# Civil Structural FEM

Use FreeCAD FEM and CalculiX for transparent preliminary analysis and investigation, not automatic design certification.

## Define the analysis contract

Confirm the engineering question, governing code, material model, geometry idealization, units, supports, releases, contacts, load cases/combinations, serviceability/ultimate criteria, required outputs, and validation benchmark. Request missing national-annex or project values instead of guessing.

Read [references/freecad-calculix.md](references/freecad-calculix.md) before creating solver objects or interpreting units and results.

## Analysis workflow

1. Inspect and simplify geometry deliberately. Record omitted features and whether members are represented as solids, shells, beams, or trusses.
2. Assign materials and sections from verified project data. Keep characteristic/design values and partial factors traceable.
3. Apply supports, connections, contacts, loads, temperatures, and combinations so the model represents a defensible load path. Avoid artificial restraints added only to make the solver run.
4. Generate an appropriate mesh and check element quality, local refinement, connectivity, and load/constraint transfer.
5. Run the smallest useful analysis first. Review solver warnings, rigid-body motion, singularities, excessive distortion, contact status, and convergence before trusting contours.
6. Perform mesh-sensitivity checks at critical results. Compare reactions with applied loads and compare simple regions against hand calculations or a known benchmark.
7. Report displacements, reactions, stresses/forces, utilization inputs, buckling/frequency results where applicable, governing combinations, limitations, and items requiring engineer review.

## Acceptance criteria

- Units are explicit and consistent from geometry through solver output.
- Reactions and applied loads balance within a stated tolerance appropriate to the model.
- The deformed shape and force flow are physically plausible.
- Critical results are not dominated by an unreviewed singularity or one coarse element.
- At least one independent benchmark and one mesh-sensitivity comparison are recorded.
- No code-compliance claim is made without the applicable standard, national annex, load combinations, material factors, and qualified review.

For Malaysian reinforced-concrete work, treat MS EN 1992 as Eurocode 2 with the applicable Malaysian National Annex and request the project-specific annex values. Ask before controlling FreeCAD through MCP or running a solver that writes analysis files.
