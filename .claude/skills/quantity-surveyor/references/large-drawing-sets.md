# Large drawing sets and coordinated take-off

Use this workflow for drawing-based quantities and scope review across sheets, disciplines or revisions. Scale it to the task: a small calculation does not need a document-control system. These are instructions for the host agent, not an installed PDF/OCR/CAD engine. Never claim pages were processed, rendered or checked without doing that work. Assessment covers quantity/cost evidence and coordination; it does not constitute engineering design approval or code certification.

## Establish the set

Record the requested trade, building/floor/zone, issue purpose/date, measurement rules and deliverable. Inventory actual files and pages before claiming set completeness. Use [drawing-register.csv](../templates/drawing-register.csv), or the user's equivalent. Record a stable file ID, content hash where tools permit, filename, PDF page number (one-based), printed sheet number/title, discipline, revision, issue date/status and review state. A printed sheet number is not a PDF page number. Record unknown metadata as unknown.

Compare the drawing index/transmittal against actual title blocks. Identify missing, duplicated, superseded, unreadable and out-of-scope sheets, including specifications, schedules, addenda and referenced external drawings. Establish the applicable issued set from the project instruction/transmittal; do not pick the greatest revision label, newest file timestamp or a familiar “IFC” label automatically. Where issues conflict, hold affected results provisional and request resolution while continuing unaffected work. Preserve original files and prior issue records.

Track review stage separately from disposition: a view can be inventoried, text-indexed, visually inspected for the stated scope or reconciled, while still having open queries. Preserve the completed review stage alongside an open/resolved/excluded disposition and reasons. Use separate view/scope rows when one sheet contains different stages; do not overwrite inspected coverage with a blanket unresolved label. A successful upload or text search does not establish visual inspection or trade completeness. Report supplied-file coverage separately from coverage against the expected drawing index; if the expected set is unknown, say so.

## Navigate before measuring

Use text extraction, bookmarks, OCR, legends and title blocks to build a lightweight index. Search that index to find relevant plans, elevations, sections, schedules, details and specifications. Repeated tags, OCR matches and schedule rows are candidates, not installed quantities. Confirm interpretation on the source view. OCR can lose decimal points, diameter signs, leaders, rotated notes and dimension associations.

Follow relevant dependencies in both directions: plan callouts to details/sections, details back to their locations, schedules to actual instances, matchlines to adjacent areas, risers to floor plans, and notes to applicable specifications. Record the source and destination of each material unresolved reference. A search with no hit is not proof of absence. Check the applicable index, legends, notes and relevant visual regions before making an absence finding; qualify the area and issue searched.

Work in manageable batches by trade/building/floor/zone, with high-impact or unclear interfaces first. Save a checkpoint containing the source-set IDs, included scope, inspected views, unresolved references, quantity record IDs, reconciled totals and the next batch. Resume from that record rather than conversational memory alone. One database is optional; ordinary tables/files are sufficient. Never upload project drawings to an external parsing service without authorization for that transfer.

## Inspect and calibrate each view

A sheet may contain several scales and rotations. Identify the specific viewport and its title, detail number, bounds and scale. Prefer explicit written dimensions and documented units. For graphical measurement, calibrate that view to a reliable known dimension and check another known dimension where available; note when independent calibration verification is unavailable. Account for non-uniform scaling, scans, rotation and resized crops. Do not transfer a sheet-wide scale to every detail. “NTS” and unresolved “as noted” do not authorize scaling. Stop affected measurement when calibration is unreliable; report the missing dimension or provisional method explicitly.

Record coordinate conventions for evidence: original page dimensions, units, origin, rotation and the crop/resize transform when used. Pixel coordinates, PDF points and normalized coordinates are not interchangeable. If precise coordinates are unavailable, use an honest sheet/detail/grid/room locator, not invented bounding boxes.

Inspect dense drawings through legible regional crops or overlapping tiles where tools support them. Retain the overview and source linkage. Deduplicate objects across overlapping tiles and matchlines by physical instance/location; do not discard edge objects merely because they touch a tile boundary. If the host cannot display drawings, produce an inventory/text-based preliminary review and specify the unperformed visual and measurement work.

## Measure physical scope once

Use [quantity-evidence.csv](../templates/quantity-evidence.csv), or an equivalent auditable ledger. Trace each item to issue, sheet, view and location, measurement method, dimensions/count, unit, deduction/waste basis and calculation. Repeated type labels can represent many instances; repeated depictions of one instance can appear on plans, details and elevations. Neither “one tag = one item” nor “every elevation is only a type” is a universal rule. Resolve actual instance/location identity and applicability before counting.

Reconcile plans against relevant schedules and legends. Determine whether a schedule lists types, individual instances, quantities or design options. Do not add schedule totals to plan counts for the same scope. Show disagreements and competing evidence rather than silently forcing totals to agree. A zero requires an adequate search of the stated scope; unread, missing and unresolved areas remain unknown.

For symbol detection, retain accepted, rejected and uncertain candidates with source locators. Review filtered candidates and sweep relevant regions for missed items independently of the detector's shortlist. A clean shortlist can still omit half the scope. Keep confirmed quantities separate from provisional alternatives and unresolved scope; do not convert an agent's confidence adjective into a probability or an invented accuracy percentage.

Check scope appropriate to the trade: openings and returns; wall/finish types and heights; slab thicknesses and penetrations; facade anchors, substrates and interfaces; MEP risers, fittings, insulation, controls and builders' work; demolition, temporary works, access, protection, testing and external utilities. These are prompts for evidence checks, not automatic additions. Include each obligation once under the adopted pricing boundary. Record unresolved performance or design questions for the responsible professional.

## Revisions and reconciliation

Compare applicable old/new sheets and their changed areas, plus linked schedules, notes and details. Revision clouds help navigation but do not prove that all changes are clouded. Check alignment and unchanged control points before trusting an overlay. A changed file/hash, revision, legend or source interpretation invalidates affected cached findings and dependent quantities, even if the page number is unchanged. Mark those records for re-review; retain the old evidence and show additions, removals and net change separately. Do not carry a prior review status forward silently.

Independently verify significant arithmetic, units, duplicate instance IDs, deductions and totals. Arithmetic agreement does not establish scope completeness. Reconcile confirmed and provisional subtotals without counting alternative interpretations twice. Keep unknown unmeasured scope visible rather than assigning it zero value.

## Deliver with a clear boundary

Provide the requested quantities/costs, the issued-set basis, sheet/view coverage for the requested scope, evidence ledger, unresolved dependencies and prioritized queries. State exactly which portions were unreviewed or excluded and why. “120 of 150 supplied sheets inspected for doors” is a coverage statement, not 80% quantity accuracy or proof that the project set is complete. Do not describe a complete estimate when material scoped areas remain unread.

For a very large set, propose a representative pilot with an independently prepared, adjudicated reference take-off before relying on scale-up. Include difficult and rare relevant cases as well as routine sheets; retain disputed reference items and reconcile them rather than treating one human pass as infallible. Measure detection precision/recall, missed scope, quantity error by unit/trade, reference correctness and time/review burden against that reference. Use the same issue and measurement rules. Keep absolute errors when the reference is zero; do not average incompatible units or let overcounts cancel omissions. Neither this workflow nor earlier synthetic QS scores supplies a measured full-set accuracy rate.
