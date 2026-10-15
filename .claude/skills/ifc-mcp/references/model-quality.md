# IFC quality review

Use for an IFC audit or post-edit regression check. Establish schema, purpose, exchange requirements/IDS, units, coordinate reference, model scope and revision first. Preserve the raw hash and state which checks are actually available.

## Separate validation layers

| Layer | Inspect | Evidence / limit |
| --- | --- | --- |
| Parse | File can be opened and references read | Parser failures are structural blockers; opening alone is not schema validation |
| Schema | Entity/attribute compatibility, cardinality and constraints | Log tool/version and whether EXPRESS rules were enabled |
| Model structure | Spatial decomposition, containment, identity, type relations, units, placements | Stable GlobalId is not a display name; regenerated IDs can break issue tracking |
| Project information | Required classes, properties, classifications, values and applicability | Run the supplied IDS; absent IDS means project compliance is not established |
| Geometry | Missing/invalid shapes, placements, duplicate candidates, clashes/clearance | Log selections, excluded classes, units and tolerances |
| Quantities | Quantity type/unit, inclusion scope, gross/net rules and plausibility | Stored values and calculated values are distinct; no measurement standard is assumed |

Some projects legitimately use nested elements, assemblies or non-building spatial entities. Check the schema/project requirements before treating every non-storey relation as an error. IFC4X3 infrastructure cannot be evaluated with a building-only assumption.

## Tool routing and mutation

Discover connected tools first. If available, baseline with summary/tree, then targeted info/relations and validation. Record the express_rules setting for ifc_validate. No connected server means no claimed MCP execution.

Do not reset or replace another in-memory session without considering unsaved state. Treat ifc_quantify as a model mutation; query stored quantities for read-only review. Save edits to an explicit new path. Never use an empty save path as a routine audit step.

When IfcTester is already available, use the supplied IDS and check the installed CLI:
~~~text
python -m ifctester project.ids model.ifc -r Html -o report.html
~~~
This writes a report, not an IFC correction. Inspect the report and specification applicability; an empty applicable set is not evidence that expected elements exist. Missing tools or specifications remain 'not checked', not 'passed'.

## Findings and acceptance

Each issue should include model revision, stable GlobalId (or STEP ID plus revision if GlobalId is absent/duplicated), class, observed value/location, rule, severity, evidence and suggested disposition. STEP IDs may change after re-export.

For clashes, record pair selections, units, clearance versus intersection mode, exclusions and tolerance. Intended connections can overlap; geometric intersection is not automatically a design defect.

Repeat only relevant checks after edits, reopen the saved output, and compare identity/relations/quantity changes with the baseline. Report unsupported checks separately. Schema success is not structural design approval.

## Sources

Checked 2026-10-15:
- [IfcMCP](https://docs.ifcopenshell.org/ifcmcp.html): query/edit distinction, validate options, quantify mutation and save behavior.
- [IfcTester](https://docs.ifcopenshell.org/ifctester.html): IDS evaluation and report generation.
- [IfcOpenShell validation API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/validate/index.html): consult installed-version validation capabilities.

Review scenarios: a schema-valid model lacking required fire data needs IDS review; a read-only quantity request must not call a mutating quantity generator; a clean clash result without recorded selections/tolerance is incomplete evidence.
