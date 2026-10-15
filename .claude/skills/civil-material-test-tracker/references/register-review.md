# Test-register review

## Data model

The blank CSV is one row per specimen/test event; a sample can have several specimens and ages. Keep stable IDs separate from location descriptions.

- project_id/location/lot_id/batch_id: trace a record back to construction.
- sample_id/specimen_id/test_type/method: distinguish a sample from a specimen and an actual test.
- sampled_at/test_due_at/tested_at: preserve original date/time convention and project time zone; age calculations need an explicit reference rule.
- result_value/result_unit: raw result, not a guessed normalized value.
- report_id/report_revision/report_path: supporting lab evidence.
- criterion_ref/review_status/reviewer: identify the exact rule and who decided.

Store the full criterion in a supplied project rule table (ID, method, version, applicability, unit, limit/logic and source). Do not encode a single 'strength >= specified strength' rule as universal concrete acceptance.

## Useful checks

1. Repeated specimen ID with conflicting batch, age or result: review conflict; do not overwrite.
2. Planned/due tests without results: outstanding, not zero strength.
3. Result with missing report or wrong unit/type: incomplete evidence.
4. A report superseded by a revision: retain both and identify the applicable version.
5. Concrete results: verify specimen type, grouping, age, curing and specified method before any mean/threshold calculation.
6. Soil results: verify wet/dry density, moisture basis, laboratory curve, method and material correspondence.
7. Sampling coverage: compare against provided lot sizes and frequency criteria; do not invent a frequency.
8. Signed approval: record actual reviewer evidence; the assistant must not fill an approval field as if it were the reviewer.

For calculations/report files, independently check dates, units and reconciliations. An amber review status is more accurate than invented compliance when criteria are absent.

## Sources and limitations

Reviewed 2026-10-15:
- [Domain Experts civil technician draft](https://github.com/wonsukchoi/domain-experts/blob/main/roles/civil-engineering-technician/SKILL.md) was inspected as background on traceability; its US assumptions and heuristics are not adopted here.
- Obtain the actual project specification and applicable test-method editions from the user or an authorized source before interpreting results.

The template and instructions are newly authored; no third-party code, normative standards text or numeric acceptance thresholds are bundled.
