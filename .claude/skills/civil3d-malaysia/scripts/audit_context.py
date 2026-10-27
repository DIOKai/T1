#!/usr/bin/env python3
"""Read-only project metadata checks; never a JKR/MSMA compliance assessment."""

import argparse
import json
import math
from pathlib import Path


SCOPES = {"survey", "earthworks", "road", "drainage", "automation"}
PLACEHOLDERS = {"tbd", "todo", "unknown", "unverified", "待确认", "未核验", "待填写", "?"}


def filled(value):
    return isinstance(value, str) and bool(value.strip()) and value.strip().casefold() not in PLACEHOLDERS


def report(errors, status=None):
    return {
        "status": status or ("incomplete" if errors else "metadata-complete"),
        "engineering_compliance_checked": False,
        "limitations": "Only metadata presence/types checked. Evidence and engineering adequacy require review.",
        "issues": errors,
    }


def audit(data):
    errors = []
    if not isinstance(data, dict):
        return report(["root: expected an object"])

    def object_at(key):
        value = data.get(key)
        if not isinstance(value, dict):
            errors.append(f"{key}: expected an object")
            return {}
        return value

    def require_text(obj, fields, prefix):
        for key in fields:
            if not filled(obj.get(key)):
                errors.append(f"{prefix}.{key}: non-placeholder text required")

    project = object_at("project")
    require_text(project, ("name", "state", "authority"), "project")
    if project.get("country") != "MY":
        errors.append("project.country: must be MY")
    drawing = object_at("drawing")
    require_text(drawing, ("release", "build", "template"), "drawing")
    if drawing.get("linear_unit") != "m":
        errors.append("drawing.linear_unit: expected m; review source units before modelling")
    survey = object_at("survey")
    require_text(survey, ("horizontal_reference", "vertical_reference", "control_evidence"), "survey")

    scope = data.get("scope")
    selected = set()
    if not isinstance(scope, list) or not scope:
        errors.append("scope: expected a non-empty list")
    else:
        for index, item in enumerate(scope):
            if not isinstance(item, str) or item not in SCOPES:
                errors.append(f"scope[{index}]: unsupported scope")
            elif item in selected:
                errors.append(f"scope[{index}]: duplicate scope")
            else:
                selected.add(item)

    criteria = data.get("criteria")
    if not isinstance(criteria, list):
        errors.append("criteria: expected a list")
        criteria = []
    seen_ids, covered = set(), set()
    for index, item in enumerate(criteria):
        prefix = f"criteria[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: expected an object")
            continue
        require_text(item, ("id", "unit", "applicability", "source", "edition", "clause"), prefix)
        item_id = item.get("id")
        if filled(item_id):
            if item_id in seen_ids:
                errors.append(f"{prefix}.id: duplicate criterion")
            seen_ids.add(item_id)
        item_scope = item.get("scope")
        if not isinstance(item_scope, str) or item_scope not in selected:
            errors.append(f"{prefix}.scope: must be a selected scope")
        else:
            covered.add(item_scope)
        value = item.get("value")
        if type(value) not in (int, float) or (isinstance(value, float) and not math.isfinite(value)):
            errors.append(f"{prefix}.value: finite number required (not boolean)")
        if item.get("evidence_status") != "reviewed":
            errors.append(f"{prefix}.evidence_status: reviewed evidence required")
        if item.get("basis_jurisdiction") != "MY":
            errors.append(f"{prefix}.basis_jurisdiction: Malaysian adoption basis required")
        external = item.get("external_reference")
        if external is not None:
            if not filled(external):
                errors.append(f"{prefix}.external_reference: use text or null")
            if not filled(item.get("malaysian_adoption_evidence")):
                errors.append(f"{prefix}.malaysian_adoption_evidence: required for an external reference")
    for task_scope in sorted((selected & {"road", "earthworks", "drainage"}) - covered):
        errors.append(f"criteria: no criterion recorded for selected {task_scope} scope")
    return report(errors)


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-finite JSON number: {value}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("context", type=Path)
    args = parser.parse_args(argv)
    try:
        with args.context.open(encoding="utf-8-sig") as source:
            data = json.load(source, object_pairs_hook=unique_keys, parse_constant=reject_constant)
        result = audit(data)
        exit_code = 1 if result["issues"] else 0
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        result = report([str(error)], "invalid-input")
        exit_code = 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
