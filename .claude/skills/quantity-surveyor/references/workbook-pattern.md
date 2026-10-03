# Auditable estimating workbook

Use [the optional workbook](../assets/templates/estimating-template.xlsx) as an optional starting point for substantive estimates, not as a mandatory format. Copy it to the project deliverable location, retain the supplied company template when required, and remove unused sheets/columns. A small question can use one concise schedule. Use the spreadsheet authoring capability for edits and verify recalculation.

The template deliberately starts without quantities, rates or percentage allowances. Its formulas cover 100 reserved lines per detail sheet. Extend every formula, validation, summary and check range together when adding capacity; an out-of-range line must not disappear from totals. Titles/instructions identify the reserved capacity.

| Sheet | Purpose |
|---|---|
| Summary | Project basis, quantity/rate gaps, measured/supported and provisional/scenario subtotals, included-cost total, allocation and revision checks; a partial total must remain labelled partial |
| Drawings | Sheet/revision/page/viewport, visual review, scale/calibration checks and coverage/queries |
| Takeoff | Stable line ID, package/location/scope, source, dimension calculation, quantity/unit/status, rate linkage and calculated amount |
| Rates | Stable rate ID, source, geography/date/currency/unit, inclusions/exclusions and selected numeric rate |
| Queries | Missing scope/price/design information, affected IDs, cost implication where supportable, owner and resolution |
| Codes | Optional line-to-company-code allocation with confirmed/provisional/unallocated states; multiple allocations require an evidenced split |
| Revision | Prior/new baselines, change basis and independently reconciled amounts |

Keep dimension calculations auditable and typed quantities/rates numeric. Store IDs as strings. Blank quantity/rate means unresolved, not zero. Match units and currency explicitly before extending a line. The template flags duplicate IDs and rate-ID/unit/currency mismatches; identical descriptions are allowed. Stable line IDs prevent a repeated description from overwriting another location.

Summarise confirmed measured/priced lines separately from provisional quantities, scenario prices and unpriced/unmeasured scope. Each allowance needs its cost base, evidence and inclusions; do not apply automatic overhead, waste, risk or tax percentages. Confirm additions are outside item-rate inclusions. The template's included-cost total is not an approved budget or a forecast-final-cost model.

For company reporting, preserve literal identifiers and source/version/definition evidence. Keep confirmed, provisional and unallocated amounts visible and reconciling to the same included-cost basis. Coding uncertainty does not remove a cost from the project subtotal. The Codes sheet is a crosswalk; it cannot approve codes or budget transfers.

For revisions, use stable scope IDs and record the prior/new drawing basis. Distinguish added/removed scope, quantity, rate, specification, currency and coding changes. Record an independently established prior/new total and reconcile against the bridge; do not populate both sides from the same already-summed result.

Before issue inspect representative input changes and copied formulas, duplicate IDs, missing/invalid inputs, units/currency, query counts, rate source/base, additions and detail-to-summary/code/revision reconciliation. Check the saved workbook, not only its appearance. Keep marked drawing evidence and source locators alongside the deliverable. Do not claim complete scope because a total calculates.

## Small example

User-supplied dimensions: 10 m × 6 m. User-supplied installation rate: 50 currency units/m², including ordinary bedding. Measured floor installation = 60 m²; extension = 3,000. If owner-supplied stone has no supplied purchase rate, report that purchase as unpriced scope and label 3,000 an installation-only subtotal. Do not add a default purchase rate, duplicate bedding as levelling, or imply the subtotal is the full project cost. Record the measurement convention and source for any deductions separately.
