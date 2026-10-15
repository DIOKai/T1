# Sequence contract

## Scope

The offline helper scripts/evaluate_phases.py accepts a JSON mapping and a date. It does not open IFC or install Ifc4D. Dates are inclusive calendar-day intervals: a task is active on both its start and finish day and completed on the following day.

Input:
~~~json
{
  "elements": ["column-01", "existing-wall"],
  "initially_present": ["existing-wall"],
  "activities": [
    {"id": "A1", "start": "2026-01-01", "finish": "2026-01-03"},
    {"id": "A2", "start": "2026-01-05", "finish": "2026-01-06"}
  ],
  "links": [
    {"element": "column-01", "task": "A1", "action": "install"},
    {"element": "existing-wall", "task": "A2", "action": "remove"}
  ]
}
~~~
~~~text
python scripts/evaluate_phases.py mapping.json --date 2026-01-07
~~~

Visible includes installing elements during their activity, completed installed elements afterwards, initially present elements until removal finishes, and temporary elements only during their activity. Active element IDs are returned separately for highlight/styling. The helper rejects repeated action links, unknown IDs and contradictory lifecycle arrangements rather than guessing.

The supported lifecycle is at most one install plus one later removal per element, initially-present plus removal, or one temporary interval. Multiple installation/removal cycles, sub-day milestones, calendars, resource leveling and critical path require a richer scheduler. Unlinked elements/tasks are reported rather than silently assumed complete.

## Handoff and acceptance

- Check model and schedule revisions and preserve stable GlobalIds; do not identify elements by names alone.
- Confirm permanent elements remain visible after their finish date.
- Confirm removal/temporary-work behavior at both date boundaries.
- Verify rejected/missing mappings cannot become a green completion percentage.
- Reopen any edited IFC and inspect actual process/product associations.
- Compare external mapping snapshots to the viewer; record discrepancies and unrendered states.

## Sources

Reviewed 2026-10-15:
- [Ifc4D](https://docs.ifcopenshell.org/ifc4d.html): programme exchange foundation.
- [IfcOpenShell sequence API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/sequence/index.html): inspect installed-version task/relationship operations.
- [Bonsai](https://docs.bonsaibim.org/): installed sequencing and visualization workflow.

Third-party schedule Skill examples were reviewed as background but not copied. Date-only filtering of currently active tasks cannot represent permanent completed construction correctly.
