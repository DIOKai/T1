---
name: civil-as-built-check
description: Compare supplied as-built survey points or scans with design coordinates or model surfaces and report traceable deviations. Use for measured-versus-design QA; survey file validation and model revision comparison are separate workflows.
---

# Civil As-Built Check

Choose the comparison that matches the project criterion before calculating a deviation.

## Establish the comparison

Record design revision, observation date, coordinate systems/datums/epoch, units, control, element/point correspondence, measurement uncertainty and supplied tolerances. Do not align observations to the design merely to minimize the deviations being inspected.

Read [comparison-contract.md](references/comparison-contract.md) for matched-point input, cloud-to-mesh limits and report requirements.

## Work

1. Preserve and hash raw design and survey inputs. Inspect field schema and missing/duplicate IDs before computing.
2. For known point correspondence, use scripts/compare_points.py to calculate signed E/N/Z deltas and horizontal/3D magnitudes from explicitly declared linear units and a shared frame.
3. For scans versus surfaces, use an available tool such as CloudCompare with documented registration, normal orientation, sampling and search limits.
4. Distinguish nearest-surface distance from displacement along a design axis or elevation difference. A nearest point on another nearby surface may be the wrong design target.
5. Compare only against supplied criteria; retain 'not assessed' when tolerance, correspondence or metadata is unresolved. Missing/unmatched points are not passes.
6. Deliver point/element locators, observed/design values, criterion, deviations, exclusions and the checks still required.

No automatic geometry correction, source overwrite or construction certification follows from this skill. It supports measurement review and an evidence trail.
