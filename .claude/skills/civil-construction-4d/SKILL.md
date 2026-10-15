---
name: civil-construction-4d
description: Link IFC elements to construction schedules and review install, removal, temporary-work, and phase visibility states. Use for construction sequencing and 4D handoff; this skill does not invent durations, productivity or an approved programme.
---

# Civil Construction 4D

Use supplied schedule revisions and stable element identities to produce a repeatable sequence. Preserve source IFC and programme files.

## Establish the model

Confirm schedule/model revisions, element GlobalIds, task IDs, planned versus actual dates, time zone/calendar, units, activity types and requested snapshots. Distinguish permanent installation, removal and temporary work before linking.

Read [sequence-contract.md](references/sequence-contract.md) for timeline semantics, an offline evaluator and acceptance scenarios.

## Link and verify

1. Audit duplicate/missing task or element IDs, reversed dates, link coverage and activity dependencies.
2. Map elements deliberately by trade, zone or level, then review the mapping. A floor-wide auto-link can assign finishes to the structural task.
3. Keep completed permanent construction visible. Remove temporary works or demolished elements only according to explicit tasks.
4. Inspect schedule calendars and dependencies with the installed programme tool; a visibility helper does not calculate critical path or validate working-day durations.
5. If editing IFC, inspect current IfcOpenShell/Bonsai sequence APIs first and save a new model. An external JSON mapping is not proof of persisted IFC task assignments.
6. Review snapshots before, during and after each representative activity, including a completed element, removal and temporary work.

Deliver the mapping, model/schedule revisions, uncovered elements, date semantics and observed snapshot evidence. Do not call a date-filtered list an actual rendered simulation without viewer evidence.
