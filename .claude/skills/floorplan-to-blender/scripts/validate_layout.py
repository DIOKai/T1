#!/usr/bin/env python3
"""Check a floorplan-to-blender layout JSON before building it in Blender.

Read-only. Catches the mistakes that make AI-built houses look wrong: wrong scale,
openings off the wall or overlapping, walls that end in mid-air, rooms nobody can
walk into, room areas that disagree with the plan labels or the listing.

Usage:
    python validate_layout.py layout.json [--json]
Exit code 1 if there are errors, 0 if only warnings or nothing.
Standard library only.
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fp_geometry import opening_span, polygon_area, wall_segments  # noqa: E402

M2_PER_FT2 = 0.09290304
# Plausible ranges (rules of thumb, not code requirements; see references/reading-plans.md).
DOOR_W = (0.6, 1.2)
DOOR_H = (1.95, 2.45)
LEVEL_H = (2.2, 4.5)
WALL_T = (0.05, 0.6)
SILL = (0.0, 1.8)


def _seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def _segments_intersect(p1, p2, p3, p4):
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return (d1 * d2 < -1e-12) and (d3 * d4 < -1e-12)


def _self_intersects(poly):
    n = len(poly)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(i - j) <= 1 or (i == 0 and j == n - 1):
                continue
            if _segments_intersect(poly[i], poly[(i + 1) % n], poly[j], poly[(j + 1) % n]):
                return True
    return False


def _area_m2(v):
    if not v:
        return None
    unit = v.get("unit", "m2")
    return float(v["value"]) * (M2_PER_FT2 if unit in ("ft2", "sqft", "sf") else 1.0)


def validate(layout):
    errors, warnings, info = [], [], []
    E, W, I = errors.append, warnings.append, info.append

    if layout.get("schema") != "floorplan-to-blender/1":
        W(f"schema is {layout.get('schema')!r}, expected 'floorplan-to-blender/1'")
    if layout.get("units", "m") != "m":
        E("units must be 'm' (convert feet/inches/mm to metres before building)")

    levels = {lv["id"]: lv for lv in layout.get("levels", [])}
    if not levels:
        E("no levels")
    for lv in levels.values():
        h = float(lv.get("height", 0))
        if not LEVEL_H[0] <= h <= LEVEL_H[1]:
            W(f"level {lv['id']}: floor-to-ceiling height {h} m is unusual (expected {LEVEL_H[0]}-{LEVEL_H[1]})")

    walls = {}
    segs_by_wall = {}
    for w in layout.get("walls", []):
        wid = w.get("id")
        if wid in walls:
            E(f"duplicate wall id {wid}")
        walls[wid] = w
        if w.get("level") not in levels:
            E(f"wall {wid}: unknown level {w.get('level')}")
            continue
        t = float(w.get("thickness", 0))
        if not WALL_T[0] <= t <= WALL_T[1]:
            E(f"wall {wid}: thickness {t} m out of range {WALL_T}")
        if len(w.get("path", [])) < 2:
            E(f"wall {wid}: path needs at least 2 points")
            continue
        segs = wall_segments(w)
        segs_by_wall[wid] = segs
        for s in segs:
            if s["length"] < 0.05:
                E(f"wall {wid} segment {s['index']}: length {s['length']:.3f} m (duplicate point?)")
        if w.get("closed") and len(w["path"]) >= 3:
            poly = [tuple(p) for p in w["path"]]
            if _self_intersects(poly):
                E(f"wall {wid}: closed path crosses itself")

    # Openings: inside their segment, clear of the corners, not overlapping each other.
    door_widths = []
    spans = {}
    for op in layout.get("openings", []):
        oid = op.get("id")
        wid = op.get("wall")
        if wid not in segs_by_wall:
            E(f"opening {oid}: unknown wall {wid}")
            continue
        segs = segs_by_wall[wid]
        si = int(op.get("segment", 0))
        if not 0 <= si < len(segs):
            E(f"opening {oid}: wall {wid} has no segment {si}")
            continue
        seg = segs[si]
        a, b = opening_span(op, seg)
        t = float(walls[wid]["thickness"])
        margin = 0.05
        if a < -1e-6 or b > seg["length"] + 1e-6:
            E(f"opening {oid}: spans {a:.2f}-{b:.2f} m but wall {wid} segment {si} is {seg['length']:.2f} m long")
        elif a < t / 2 + margin or b > seg["length"] - t / 2 - margin:
            W(f"opening {oid}: closer than {t / 2 + margin:.2f} m to a corner of wall {wid} segment {si}")
        h = float(op.get("height", 0))
        sill = float(op.get("sill", 0))
        level_h = float(walls[wid].get("height") or levels[walls[wid]["level"]]["height"])
        if sill + h > level_h + 1e-6:
            E(f"opening {oid}: sill+height {sill + h:.2f} m is taller than the wall ({level_h:.2f} m)")
        typ = op.get("type", "door")
        if typ in ("door", "sliding_door"):
            if typ == "door":
                door_widths.append(float(op["width"]))
            if not DOOR_H[0] <= h <= DOOR_H[1]:
                W(f"door {oid}: height {h:.2f} m unusual (expected {DOOR_H[0]}-{DOOR_H[1]})")
            if sill > 0.05:
                W(f"door {oid}: sill {sill:.2f} m above the floor")
        if typ == "window" and not SILL[0] <= sill <= SILL[1]:
            W(f"window {oid}: sill {sill:.2f} m unusual")
        key = (wid, si)
        for other_id, (oa, ob) in spans.get(key, []):
            if a < ob - 1e-6 and oa < b - 1e-6:
                E(f"openings {other_id} and {oid} overlap on wall {wid} segment {si}")
        spans.setdefault(key, []).append((oid, (a, b)))

    # Scale sanity from door widths (the classic inch/foot or px mix-up shows up here).
    if door_widths:
        door_widths.sort()
        med = door_widths[len(door_widths) // 2]
        I(f"median door width {med:.2f} m over {len(door_widths)} doors")
        if not DOOR_W[0] <= med <= DOOR_W[1]:
            E(f"median door width {med:.2f} m is outside {DOOR_W} m - the scale is probably wrong")

    # Wall ends that touch nothing (free ends are fine only when marked).
    for wid, w in walls.items():
        if wid not in segs_by_wall or w.get("closed"):
            continue
        for end in (tuple(w["path"][0]), tuple(w["path"][-1])):
            touching = False
            for oid, ow in walls.items():
                if oid == wid or oid not in segs_by_wall or ow.get("level") != w.get("level"):
                    continue
                tol = float(ow["thickness"]) / 2 + float(w["thickness"]) / 2 + 0.02
                for s in segs_by_wall[oid]:
                    if _seg_dist(end, s["start"], s["end"]) <= tol:
                        touching = True
                        break
                if touching:
                    break
            if not touching and not w.get("free_ends"):
                W(f"wall {wid}: end {list(end)} does not meet another wall (set \"free_ends\": true if intended)")

    # Rooms: valid polygons, area vs label, reachable through doors/openings.
    rooms = layout.get("rooms", [])
    total = 0.0
    room_area = {}
    for r in rooms:
        poly = [tuple(p) for p in r.get("polygon", [])]
        if len(poly) < 3:
            E(f"room {r.get('id')}: polygon needs 3+ points")
            continue
        if _self_intersects(poly):
            E(f"room {r.get('id')}: polygon crosses itself")
        area = abs(polygon_area(poly))
        room_area[r["id"]] = area
        total += area
        lab = _area_m2(r.get("label_area"))
        if lab:
            diff = (area - lab) / lab * 100
            msg = f"room {r['id']} ({r.get('name', '')}): {area:.2f} m2 vs label {lab:.2f} m2 ({diff:+.1f}%)"
            (W if abs(diff) > 5 else I)(msg)
    if rooms:
        I(f"sum of room floors {total:.1f} m2 ({total / M2_PER_FT2:.0f} ft2)")
    listing = _area_m2((layout.get("source") or {}).get("listing_area"))
    if listing and rooms:
        diff = (total - listing) / listing * 100
        msg = (f"room floors {total:.1f} m2 vs listing {listing:.1f} m2 ({diff:+.1f}%); listings usually measure "
               f"to the outside of exterior walls, so floors are expected to be a few % smaller")
        (W if abs(diff) > 15 else I)(msg)

    # Which rooms each door/opening touches (midpoint near a room edge), then reachability.
    def rooms_touching(pt, reach):
        hit = []
        for r in rooms:
            poly = [tuple(p) for p in r.get("polygon", [])]
            if len(poly) < 3:
                continue
            if any(_seg_dist(pt, poly[i], poly[(i + 1) % len(poly)]) <= reach for i in range(len(poly))):
                hit.append(r["id"])
        return hit

    graph = {r["id"]: set() for r in rooms}
    # Open-plan spaces (living + kitchen with no wall between) are declared, not guessed.
    for r in rooms:
        for other in r.get("open_to", []):
            if other not in graph:
                E(f"room {r['id']}: open_to names unknown room {other}")
                continue
            graph[r["id"]].add(other)
            graph[other].add(r["id"])
    entrances = set()
    for op in layout.get("openings", []):
        if op.get("type", "door") == "window" or op.get("wall") not in segs_by_wall:
            continue
        segs = segs_by_wall[op["wall"]]
        si = int(op.get("segment", 0))
        if not 0 <= si < len(segs):
            continue
        seg = segs[si]
        a, b = opening_span(op, seg)
        u = (a + b) / 2
        mid = (seg["start"][0] + seg["d"][0] * u, seg["start"][1] + seg["d"][1] * u)
        reach = float(walls[op["wall"]]["thickness"]) / 2 + float(walls[op["wall"]]["thickness"]) + 0.15
        touched = rooms_touching(mid, reach)
        for x in touched:
            for y in touched:
                if x != y:
                    graph[x].add(y)
        if walls[op["wall"]].get("kind") == "exterior":
            entrances.update(touched)
    if rooms:
        no_door = [rid for rid, nb in graph.items() if not nb and rid not in entrances]
        for rid in no_door:
            W(f"room {rid}: no door or opening found on its edges - check the plan for a missed door")
        if entrances:
            seen, stack = set(entrances), list(entrances)
            while stack:
                for nb in graph[stack.pop()]:
                    if nb not in seen:
                        seen.add(nb)
                        stack.append(nb)
            unreachable = [rid for rid in graph if rid not in seen and rid not in no_door]
            for rid in unreachable:
                W(f"room {rid}: cannot be reached from an exterior door")
        else:
            W("no exterior door found (an opening on an exterior wall that touches a room)")

    # How much is measured vs guessed.
    guessed = [w["id"] for w in layout.get("walls", []) if w.get("thickness_source") == "default"]
    if guessed:
        I(f"{len(guessed)} wall thicknesses are defaults, not measured: {', '.join(guessed[:8])}")
    scale = (layout.get("source") or {}).get("scale") or {}
    if scale:
        I(f"scale method {scale.get('method')}, {len(scale.get('samples', []))} samples, "
          f"error {scale.get('error_pct', '?')}%")
        if scale.get("method") == "door_width":
            W("scale was estimated from door widths only (+-5-10%); ask the user for one real dimension")
    return errors, warnings, info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("layout")
    ap.add_argument("--json", action="store_true", help="print machine-readable results")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # Chinese room names on a cp1252/gbk Windows console
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    with open(a.layout, encoding="utf-8") as f:
        layout = json.load(f)
    errors, warnings, info = validate(layout)
    if a.json:
        print(json.dumps({"errors": errors, "warnings": warnings, "info": info}, ensure_ascii=False, indent=2))
    else:
        for tag, items in (("ERROR", errors), ("WARN", warnings), ("INFO", info)):
            for m in items:
                print(f"[{tag}] {m}")
        print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
