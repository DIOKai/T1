# Drawing take-off and revision control

Use this procedure for actual drawing-based measurement. For a simple dimension-only question, keep the traceable calculation and omit unnecessary registers. This is a verification workflow, not a substitute for the selected measurement standard.

## Establish coverage

Record each supplied drawing's identifier, revision, issue date/purpose, PDF page, relevant viewport/detail and whether it was visually reviewed. Identify superseded, missing and duplicate sheets. Inspect plans, elevations, sections, schedules, specifications and relevant details together. List the scope measured, excluded and unresolved; a sheet listed in a register is not a sheet reviewed.

Prefer explicit written dimensions and schedules. Reconcile dimension chains, overall dimensions, room repetition and detail references. Do not decide a drawing/specification conflict solely because one document is later: use the project's stated precedence and issue purpose, or identify the query and affected quantity. Continue unaffected measurement.

## Calibrate each measured viewport

Read the drawing visually. A printed scale or PDF page size alone does not establish the scale of a resized image or a detail pasted into another sheet. For scaled measurement:

1. Identify a known dimension in the same viewport. Record its drawing distance, real distance, units and resulting conversion. Use tool-coordinate or pixel distances only with a recorded rendering/resolution basis.
2. Check a second independent known dimension, preferably in the other direction. Record the measured-versus-dimensioned difference. Establish a tolerance appropriate to the decision and drawing quality before accepting the check; do not choose it after seeing the error.
3. Calibrate separately for each scale/view and each revised or resized rendering. Where horizontal/vertical checks disagree, investigate distortion, perspective or incorrect dimensions. Do not use a single factor for nonuniform distortion.
4. If no reliable calibration is available, preserve supported dimensioned quantities and mark the remaining measurement unresolved. Do not infer dimensions from apparent object sizes or AI confidence.

Vector geometry can improve measurement but still needs scale, viewport, units and scope checks. Raster/vision extraction proposes observations; verify them against dimensions and counted/marked regions. It does not establish unseen thicknesses, heights or specifications.

## Retain measurement evidence

Give every take-off line a stable ID independent of its description. Record drawing/detail/revision, location or room, marked region or coordinate locator, dimension string and multiplicity, calculation, unit, measurement convention/source and quantity status. Use a marked-up copy when available; retain the original unchanged. Label bounds, exclusions and openings so another reviewer can reconstruct the measurement.

Keep net measured work, procurement quantities/waste and installation quantities separate. Confirm deductions and inclusions from the relevant work-section table; do not apply a generic opening threshold. Keep provisional/unmeasured scope visible with a query ID. A blank/TBD quantity is not zero; an unmatched rate is not a default price. Count items exactly and prevent double counting across plans, details, schedules and repeated rooms.

## Compare revisions

Freeze the prior issued baseline. Match by stable scope/location IDs, not descriptions alone. Show added, removed and changed quantities, prior/new units, drawing revisions and the cause. Convert units explicitly before comparison. Separate quantity, specification, rate, scope, coding and currency effects; disclose unresolved effects rather than forcing the bridge to balance.

For quantity and rate changes, one auditable bridge is: quantity effect = (new quantity − old quantity) × old rate; rate effect = new quantity × (new rate − old rate). This places the interaction in the rate effect. State this convention and treat new/removed scope separately. Reconcile the sum of changes to prior/new totals, while preserving unpriced scope outside the priced subtotal.

Before issue, independently check material dimensions/counts, calibration, sheet coverage, unit conversions, deductions, repeated scope, rate compatibility and summary reconciliation. State what was checked and what remains unresolved; a successful arithmetic check does not prove drawing completeness.
