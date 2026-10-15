#!/usr/bin/env python3
"""Evaluate a limited install/remove/temporary mapping at inclusive calendar dates."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys


def iso(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("dates must use YYYY-MM-DD")
    return date.fromisoformat(value)


def identifiers(values, label):
    if not isinstance(values, list) or any(
            not isinstance(x, str) or not x.strip() for x in values):
        raise ValueError(f"{label} must be a list of nonempty string IDs")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} IDs must be unique")
    return set(values)


def evaluate(data, target):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    day = iso(target)
    elements = identifiers(data.get("elements"), "elements")
    if not elements:
        raise ValueError("elements must not be empty")
    initial = identifiers(data.get("initially_present", []), "initially_present")
    if not initial <= elements:
        raise ValueError("initial elements must exist")
    rows = data.get("activities")
    if not isinstance(rows, list):
        raise ValueError("activities must be a list")
    tasks = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("activity must be an object")
        key = row.get("id")
        if not isinstance(key, str) or not key.strip() or key in tasks:
            raise ValueError("activity IDs must be unique nonempty strings")
        start, finish = iso(row.get("start")), iso(row.get("finish"))
        if start > finish:
            raise ValueError("activity start exceeds finish")
        tasks[key] = (start, finish)
    if not tasks:
        raise ValueError("activities must not be empty")
    links = data.get("links")
    if not isinstance(links, list):
        raise ValueError("links must be a list")
    lifecycles, linked_tasks = {}, set()
    for link in links:
        if not isinstance(link, dict):
            raise ValueError("link must be an object")
        element, task, action = link.get("element"), link.get("task"), link.get("action")
        if not all(isinstance(x, str) for x in (element, task, action)):
            raise ValueError("link fields must be strings")
        if element not in elements or task not in tasks:
            raise ValueError("link references unknown element/task")
        if action not in ("install", "remove", "temporary"):
            raise ValueError("action must be install, remove or temporary")
        actions = lifecycles.setdefault(element, {})
        if action in actions:
            raise ValueError("repeated action for one element is unsupported")
        actions[action] = task
        linked_tasks.add(task)
    for element, actions in lifecycles.items():
        if "temporary" in actions and (len(actions) != 1 or element in initial):
            raise ValueError("temporary cannot combine with other lifecycle states")
        if "install" in actions and element in initial:
            raise ValueError("initially present element cannot also be installed")
        if "remove" in actions:
            if element not in initial and "install" not in actions:
                raise ValueError("removal needs an initial or installed element")
            if "install" in actions and tasks[actions["remove"]][0] <= tasks[actions["install"]][1]:
                raise ValueError("removal must start after inclusive installation finish")
    visible, active_elements = set(initial), set()
    for element, actions in lifecycles.items():
        if "temporary" in actions:
            start, finish = tasks[actions["temporary"]]
            if start <= day <= finish:
                visible.add(element)
                active_elements.add(element)
            continue
        if "install" in actions:
            start, finish = tasks[actions["install"]]
            if day >= start:
                visible.add(element)
            if start <= day <= finish:
                active_elements.add(element)
        if "remove" in actions:
            start, finish = tasks[actions["remove"]]
            if start <= day <= finish:
                active_elements.add(element)
            if day > finish:
                visible.discard(element)
    active_tasks = sorted(key for key, (start, finish) in tasks.items() if start <= day <= finish)
    completed_tasks = sorted(key for key, (_, finish) in tasks.items() if day > finish)
    unlinked_elements = sorted(elements - initial - lifecycles.keys())
    unlinked_tasks = sorted(tasks.keys() - linked_tasks)
    return {
        "date": target, "interval_semantics": "start/finish inclusive calendar days",
        "visible_elements": sorted(visible), "active_elements": sorted(active_elements),
        "active_tasks": active_tasks, "completed_tasks": completed_tasks,
        "unlinked_elements": unlinked_elements, "unlinked_tasks": unlinked_tasks,
        "mapping_status": "review-required" if unlinked_elements or unlinked_tasks else "covered",
        "not_checked": ["IFC persistence", "rendered appearance", "working calendars",
                        "critical path", "task dependencies", "resource leveling"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        result = evaluate(json.loads(raw.decode("utf-8-sig")), args.date)
        result["source_sha256"] = hashlib.sha256(raw).hexdigest()
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        return 0 if result["mapping_status"] == "covered" else 1
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"evaluate_phases: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
