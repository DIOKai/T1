---
name: civil-material-test-tracker
description: Build and review construction material-test registers linking concrete or earthwork samples to locations, batches, test ages, laboratory reports, and project criteria. Use for test traceability and missing-record checks, not automatic material acceptance.
---

# Civil Material Test Tracker

Build a traceable register from actual sampling and laboratory evidence. Separate a recorded result, a calculation, a review flag and formal acceptance.

Use [test-register.csv](assets/test-register.csv) as an optional blank schema and read [register-review.md](references/register-review.md) for field meanings and review rules. Use the user's existing register when supplied.

## Workflow

1. Establish project, location/lot, specification revision, test types, required frequencies/ages and responsible reviewer. Do not import ACI/ASTM thresholds as universal Malaysian criteria.
2. Link sample ID, material batch/delivery, exact location, sampling date/time, specimen IDs, curing/handling evidence and laboratory report/revision.
3. Preserve individual results and units. Any grouping/average must follow the selected project method; distinguish cube versus cylinder and informational versus acceptance ages.
4. For earthwork compaction, identify the applicable laboratory density/moisture curve, method and material before comparing field results. A percent without its reference curve is incomplete.
5. Flag duplicate sample/specimen IDs, missing locations/reports, unperformed due tests, conflicting revisions, unsupported units and criteria without a source. Do not turn a missing result into zero or an automatic fail.
6. Report missing records and review candidates by location and batch, retaining raw results and the reviewer's actual disposition.

This skill does not book a laboratory, submit reports, accept/reject a load, or notify others without the relevant task authorization. It does not supply test-method editions, national criteria or material acceptance decisions.
