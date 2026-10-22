#!/usr/bin/env python3
"""Check a site-plan JSON before handing zones to parallel agents.

Read-only on the plan. Catches the mistakes that make multi-agent scenes fall
apart: zones that overlap (two agents building the same ground), elements
outside their zone, buildings overlapping each other or standing in the pond,
zero/negative heights, things that float (or sink), stacked parts that don't
sit on their support, paths running into walls or water, zone interface points
that are not on the shared boundary, two zones writing the same file, and
camera moves that fly through buildings.

Coordinates: metres. Plan points are [x, z] (three.js convention: x east,
z south, y up). North is -z, drawn at the top of the SVG.

Usage:
    python check_site_plan.py site-plan.json [--svg plan.svg] [--json]
                              [--min-overlap 0.05] [--tol 0.02]
Exit code 1 if there are errors, 0 if only warnings or nothing.
Standard library only.
"""
import argparse
import json
import math
import os
import sys
from xml.sax.saxutils import escape

ANCHORS_FIXED = {"ground", "water_bed", "terrain"}


# ---------------------------------------------------------------- geometry
def rect_poly(center, size, rot_deg=0.0):
    cx, cz = center
    w, d = size
    hw, hd = w / 2.0, d / 2.0
    c, s = math.cos(math.radians(rot_deg)), math.sin(math.radians(rot_deg))
    pts = []
    for px, pz in ((-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)):
        pts.append((cx + px * c - pz * s, cz + px * s + pz * c))
    return pts


def circle_poly(center, r, n=24):
    return [(center[0] + r * math.cos(2 * math.pi * i / n),
             center[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def poly_area(p):
    a = 0.0
    for i in range(len(p)):
        x1, z1 = p[i]
        x2, z2 = p[(i + 1) % len(p)]
        a += x1 * z2 - x2 * z1
    return abs(a) / 2.0


def bbox_of(p):
    xs = [q[0] for q in p]
    zs = [q[1] for q in p]
    return (min(xs), min(zs), max(xs), max(zs))


def point_in_poly(pt, poly):
    x, z = pt
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z):
            xc = (xj - xi) * (z - zi) / (zj - zi) + xi
            if x < xc:
                inside = not inside
        j = i
    return inside


def seg_dist(p, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dz * dz
    if L2 == 0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dz) / L2))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dz))


def poly_dist(p, q):
    """Smallest edge-to-vertex distance between two non-overlapping polygons."""
    best = float("inf")
    for a, b in ((p, q), (q, p)):
        for v in a:
            for i in range(len(b)):
                best = min(best, seg_dist(v, b[i], b[(i + 1) % len(b)]))
    return best


def overlap_area(p, q, max_cells=140):
    """Approximate intersection area by sampling the shared bounding box.

    Works for convex and concave polygons; touching edges give ~0.
    """
    a, b = bbox_of(p), bbox_of(q)
    x0, z0 = max(a[0], b[0]), max(a[1], b[1])
    x1, z1 = min(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or z1 <= z0:
        return 0.0
    w, d = x1 - x0, z1 - z0
    step = max(w, d) / max_cells
    step = max(step, 0.02)
    nx, nz = max(1, int(math.ceil(w / step))), max(1, int(math.ceil(d / step)))
    sx, sz = w / nx, d / nz
    hits = 0
    for i in range(nx):
        x = x0 + (i + 0.5) * sx
        for j in range(nz):
            z = z0 + (j + 0.5) * sz
            if point_in_poly((x, z), p) and point_in_poly((x, z), q):
                hits += 1
    return hits * sx * sz


def inside_bbox(pt, bb, tol):
    return (bb[0] - tol <= pt[0] <= bb[2] + tol) and (bb[1] - tol <= pt[1] <= bb[3] + tol)


def bbox_overlap_area(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    d = min(a[3], b[3]) - max(a[1], b[1])
    return w * d if (w > 0 and d > 0) else 0.0


def on_bbox_edge(pt, bb, tol):
    if not inside_bbox(pt, bb, tol):
        return False
    return (abs(pt[0] - bb[0]) <= tol or abs(pt[0] - bb[2]) <= tol
            or abs(pt[1] - bb[1]) <= tol or abs(pt[1] - bb[3]) <= tol)


def sample_polyline(pts, step=0.5):
    out = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(L / step))
        for k in range(n):
            t = k / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    if pts:
        out.append(tuple(pts[-1]))
    return out


# ---------------------------------------------------------------- parsing
def footprint_poly(fp):
    if not isinstance(fp, dict):
        raise ValueError("footprint must be an object with rect, polygon or circle")
    if "rect" in fp:
        r = fp["rect"]
        size = r["size"]
        if size[0] <= 0 or size[1] <= 0:
            raise ValueError("rect size must be > 0")
        return rect_poly(r["center"], size, r.get("rotation_deg", 0.0))
    if "circle" in fp:
        c = fp["circle"]
        if c["radius"] <= 0:
            raise ValueError("circle radius must be > 0")
        return circle_poly(c["center"], c["radius"])
    if "polygon" in fp:
        p = [tuple(v) for v in fp["polygon"]]
        if len(p) < 3:
            raise ValueError("polygon needs at least 3 points")
        if poly_area(p) <= 0:
            raise ValueError("polygon has zero area")
        return p
    raise ValueError("footprint must have rect, polygon or circle")


def check(plan, min_overlap=0.05, tol=0.02):
    errors, warnings, info = [], [], []
    E, W = errors.append, warnings.append

    site = plan.get("site")
    if not isinstance(site, dict) or "bounds" not in site:
        E("site.bounds missing: [xmin, zmin, xmax, zmax] in metres")
        return errors, warnings, info, {}
    sb = tuple(site["bounds"])
    if len(sb) != 4 or sb[2] <= sb[0] or sb[3] <= sb[1]:
        E(f"site.bounds {list(sb)} must be [xmin, zmin, xmax, zmax] with max > min")
        return errors, warnings, info, {}
    ground = float(site.get("ground_y", 0.0))
    grid = site.get("grid")
    if plan.get("units", "m") != "m":
        E(f"units is {plan.get('units')!r}; this checker and the agents expect metres ('m')")
    if grid is not None and grid <= 0:
        E("site.grid must be > 0")
        grid = None

    # zones -------------------------------------------------------------
    zones = {}
    file_owner = {}
    for z in plan.get("zones", []):
        zid = z.get("id")
        if not zid:
            E("a zone has no id")
            continue
        if zid in zones:
            E(f"zone id '{zid}' used twice")
            continue
        bb = tuple(z.get("bbox", ()))
        if len(bb) != 4 or bb[2] <= bb[0] or bb[3] <= bb[1]:
            E(f"zone '{zid}': bbox must be [xmin, zmin, xmax, zmax] with max > min")
            continue
        if not z.get("owner"):
            E(f"zone '{zid}': no owner agent")
        if not (inside_bbox(bb[:2], sb, tol) and inside_bbox(bb[2:], sb, tol)):
            E(f"zone '{zid}': bbox {list(bb)} goes outside site bounds {list(sb)}")
        files = z.get("files", [])
        if not files:
            W(f"zone '{zid}': no files listed; agents need to know which files they own")
        for f in files:
            if f in file_owner and file_owner[f] != z.get("owner"):
                E(f"file '{f}' is owned by two agents ('{file_owner[f]}' and '{z.get('owner')}'); they will overwrite each other")
            file_owner.setdefault(f, z.get("owner"))
        zones[zid] = dict(z, bbox=bb)
    for f in plan.get("shared_files", []):
        path = f.get("path") if isinstance(f, dict) else f
        if path in file_owner:
            E(f"file '{path}' is both shared (read-only for zone agents) and owned by '{file_owner[path]}'")
    if not zones:
        E("no zones defined")
    zl = list(zones.values())
    for i in range(len(zl)):
        for j in range(i + 1, len(zl)):
            a = bbox_overlap_area(zl[i]["bbox"], zl[j]["bbox"])
            if a > min_overlap:
                E(f"zones '{zl[i]['id']}' and '{zl[j]['id']}' overlap by {a:.2f} m^2; each square metre must belong to one agent")
    covered = sum((z["bbox"][2] - z["bbox"][0]) * (z["bbox"][3] - z["bbox"][1]) for z in zl)
    site_area = (sb[2] - sb[0]) * (sb[3] - sb[1])
    if zl and covered < site_area - 0.5:
        W(f"zones cover {covered:.0f} of {site_area:.0f} m^2; nobody owns the rest (fine if it stays empty ground)")

    # water -------------------------------------------------------------
    waters = {}
    for w in plan.get("water", []):
        wid = w.get("id", "?")
        try:
            poly = [tuple(v) for v in w["polygon"]]
            if len(poly) < 3 or poly_area(poly) <= 0:
                raise ValueError
        except Exception:
            E(f"water '{wid}': polygon needs at least 3 points and an area")
            continue
        zid = w.get("zone")
        if zid not in zones:
            E(f"water '{wid}': zone '{zid}' does not exist")
        elif not all(inside_bbox(p, zones[zid]["bbox"], tol) for p in poly):
            E(f"water '{wid}': polygon leaves zone '{zid}'")
        depth = w.get("depth", 0)
        if depth <= 0:
            E(f"water '{wid}': depth must be > 0 (a pond needs a bed for things to stand on)")
        surf = w.get("surface_y", ground)
        if surf > ground + tol:
            E(f"water '{wid}': surface_y {surf} is above ground {ground}; the water would spill")
        waters[wid] = dict(w, poly=poly, bed=surf - depth, surface=surf)
    wl = list(waters.values())
    for i in range(len(wl)):
        for j in range(i + 1, len(wl)):
            a = overlap_area(wl[i]["poly"], wl[j]["poly"])
            if a > min_overlap:
                E(f"water '{wl[i]['id']}' and '{wl[j]['id']}' overlap ({a:.2f} m^2); merge them")

    # elements ----------------------------------------------------------
    els = {}
    for e in plan.get("elements", []):
        eid = e.get("id")
        if not eid:
            E("an element has no id")
            continue
        if eid in els:
            E(f"element id '{eid}' used twice")
            continue
        try:
            poly = footprint_poly(e.get("footprint"))
        except (KeyError, TypeError, ValueError, IndexError) as ex:
            E(f"element '{eid}': bad footprint ({ex})")
            continue
        h = e.get("height")
        if not isinstance(h, (int, float)) or h <= 0:
            E(f"element '{eid}': height must be a number > 0 (got {h!r})")
            h = 0.0
        els[eid] = dict(e, poly=poly, h=float(h))

    for eid, e in els.items():
        zid = e.get("zone")
        if zid not in zones:
            E(f"element '{eid}': zone '{zid}' does not exist")
        else:
            bb = zones[zid]["bbox"]
            out = [p for p in e["poly"] if not inside_bbox(p, bb, tol)]
            if out:
                E(f"element '{eid}': footprint leaves zone '{zid}' {list(bb)} "
                  f"(e.g. at [{out[0][0]:.2f}, {out[0][1]:.2f}]); move it or give it to the neighbouring zone")
        if not all(inside_bbox(p, sb, tol) for p in e["poly"]):
            E(f"element '{eid}': footprint leaves the site")
        if grid:
            c = e["footprint"].get("rect", e["footprint"].get("circle", {})).get("center")
            if c and any(abs(v / grid - round(v / grid)) > 1e-6 for v in c):
                W(f"element '{eid}': centre {c} is off the {grid} m grid (fine if intended)")

    # grounding / support
    def base_of(e):
        return float(e.get("base_y", ground))

    for eid, e in els.items():
        anchor = e.get("anchor", "ground")
        b = base_of(e)
        if anchor == "ground":
            if abs(b - ground) > tol:
                kind = "floats" if b > ground else "is sunk"
                E(f"element '{eid}' {kind}: anchor 'ground' but base_y={b} (ground_y={ground})")
            wet = [w for w in wl if overlap_area(e["poly"], w["poly"]) > min_overlap]
            if wet and not e.get("over_water"):
                for w in wet:
                    E(f"element '{eid}' stands in water '{w['id']}' "
                      f"({overlap_area(e['poly'], w['poly']):.2f} m^2) - the pagoda-in-the-pond mistake. "
                      "Move it, or mark over_water (bridges) / anchor water_bed (stepping stones)")
            if e.get("over_water"):
                if not wet:
                    W(f"element '{eid}': over_water is set but it crosses no water")
                land = [p for p in e["poly"] if not any(point_in_poly(p, w["poly"]) for w in wl)]
                if len(land) < 2:
                    E(f"element '{eid}': over_water but fewer than two footprint corners on land; "
                      "a bridge needs abutments on both banks")
        elif anchor == "water_bed":
            hosts = [w for w in wl if all(point_in_poly(p, w["poly"]) for p in e["poly"])]
            if not hosts:
                E(f"element '{eid}': anchor water_bed but its footprint is not fully inside any water")
            else:
                w = hosts[0]
                if abs(b - w["bed"]) > tol:
                    E(f"element '{eid}': anchor water_bed, base_y={b} but bed of '{w['id']}' is {w['bed']:.2f}")
                if b + e["h"] < w["surface"] - tol:
                    W(f"element '{eid}': top ({b + e['h']:.2f}) is under the water surface ({w['surface']:.2f}); invisible?")
        elif anchor == "terrain":
            W(f"element '{eid}': anchor terrain; this checker can't see the terrain - the zone agent must sample the height field")
        elif isinstance(anchor, str) and anchor.startswith("on:"):
            sid = anchor[3:]
            s = els.get(sid)
            if s is None:
                E(f"element '{eid}': supported by '{sid}', which does not exist")
                continue
            if s.get("zone") != e.get("zone"):
                W(f"element '{eid}' (zone {e.get('zone')}) sits on '{sid}' (zone {s.get('zone')}); one agent should own both")
            top = base_of(s) + s["h"]
            if abs(b - top) > tol:
                kind = "floats above" if b > top else "sinks into"
                E(f"element '{eid}' {kind} its support '{sid}': base_y={b}, support top={top:.2f}")
            off = [p for p in e["poly"] if not point_in_poly(p, s["poly"])
                   and min(seg_dist(p, s["poly"][i], s["poly"][(i + 1) % len(s["poly"])])
                           for i in range(len(s["poly"]))) > tol]
            if off:
                E(f"element '{eid}': footprint hangs over the edge of its support '{sid}' "
                  f"(e.g. at [{off[0][0]:.2f}, {off[0][1]:.2f}]); nothing may overhang without a support")
        else:
            E(f"element '{eid}': unknown anchor {anchor!r} (use ground, water_bed, terrain or on:<id>)")

    # cycles in on: chains
    for eid in els:
        seen, cur = [], eid
        while cur in els and str(els[cur].get("anchor", "")).startswith("on:"):
            if cur in seen:
                E(f"element '{eid}': support chain loops ({' -> '.join(seen + [cur])})")
                break
            seen.append(cur)
            cur = els[cur]["anchor"][3:]

    # element-element overlap / clearance
    def stacked(a, b):
        return a.get("anchor") == "on:" + b["id"] or b.get("anchor") == "on:" + a["id"]

    def allowed(a, b):
        return b["id"] in a.get("allow_overlap", []) or a["id"] in b.get("allow_overlap", [])

    el = list(els.values())
    for i in range(len(el)):
        a = el[i]
        ab = bbox_of(a["poly"])
        for j in range(i + 1, len(el)):
            b = el[j]
            if stacked(a, b) or allowed(a, b):
                continue
            bb = bbox_of(b["poly"])
            a0, a1 = base_of(a), base_of(a) + a["h"]
            b0, b1 = base_of(b), base_of(b) + b["h"]
            vert = min(a1, b1) - max(a0, b0)
            clear = max(a.get("clearance", 0), b.get("clearance", 0))
            near = (ab[0] - clear < bb[2] and bb[0] - clear < ab[2]
                    and ab[1] - clear < bb[3] and bb[1] - clear < ab[3])
            if not near:
                continue
            area = overlap_area(a["poly"], b["poly"])
            if area > min_overlap and vert > tol:
                E(f"elements '{a['id']}' and '{b['id']}' overlap ({area:.2f} m^2, {vert:.2f} m vertically). "
                  "Move one, stack it with anchor on:<id>, or list it in allow_overlap if intended")
            elif clear > 0 and area <= min_overlap:
                d = poly_dist(a["poly"], b["poly"])
                if d < clear - tol:
                    W(f"elements '{a['id']}' and '{b['id']}' are {d:.2f} m apart (clearance {clear} m wanted)")

    # paths -------------------------------------------------------------
    paths = {}
    for p in plan.get("paths", []):
        pid = p.get("id", "?")
        pts = [tuple(v) for v in p.get("polyline", [])]
        if len(pts) < 2:
            E(f"path '{pid}': polyline needs at least 2 points")
            continue
        if p.get("width", 0) <= 0:
            E(f"path '{pid}': width must be > 0")
        zid = p.get("zone")
        if zid not in zones:
            E(f"path '{pid}': zone '{zid}' does not exist")
        elif not all(inside_bbox(q, zones[zid]["bbox"], tol) for q in pts):
            E(f"path '{pid}': leaves zone '{zid}'; split it at the zone edge and add an interface point")
        reported = set()
        for q in sample_polyline(pts):
            for w in wl:
                if w["id"] in reported or not point_in_poly(q, w["poly"]):
                    continue
                if any(x.get("over_water") and point_in_poly(q, x["poly"]) for x in el):
                    continue
                reported.add(w["id"])
                E(f"path '{pid}' runs into water '{w['id']}' near [{q[0]:.1f}, {q[1]:.1f}] with no bridge")
            for x in el:
                if x["id"] in reported or x.get("passable") or x.get("over_water"):
                    continue
                if x.get("type") in ("ground_cover",):
                    continue
                if point_in_poly(q, x["poly"]):
                    reported.add(x["id"])
                    W(f"path '{pid}' runs into '{x['id']}' near [{q[0]:.1f}, {q[1]:.1f}] "
                      "(mark it passable if it is a gate the path goes through)")
        paths[pid] = dict(p, pts=pts)

    # interfaces --------------------------------------------------------
    for itf in plan.get("interfaces", []):
        iid = itf.get("id", "?")
        between = itf.get("between", [])
        pt = itf.get("point")
        if len(between) != 2 or any(z not in zones for z in between):
            E(f"interface '{iid}': 'between' must name two existing zones")
            continue
        if not pt or len(pt) != 2:
            E(f"interface '{iid}': point [x, z] missing")
            continue
        for z in between:
            if not on_bbox_edge(pt, zones[z]["bbox"], tol):
                E(f"interface '{iid}': point {pt} is not on the edge of zone '{z}'")
        if not itf.get("note"):
            W(f"interface '{iid}': add a note saying what meets here (path width, level, material)")

    # shots -------------------------------------------------------------
    for s in plan.get("shots", []):
        sid = s.get("id", "?")
        tgt = s.get("start_target")
        if tgt not in els:
            E(f"shot '{sid}': start_target '{tgt}' is not an element")
        for t in s.get("end_includes", []):
            if t not in els:
                E(f"shot '{sid}': end_includes '{t}' is not an element")
        cam = s.get("camera", {})
        a, b = cam.get("start"), cam.get("end")
        if not (a and b and len(a) == 3 and len(b) == 3):
            W(f"shot '{sid}': camera start/end [x, y, z] missing; can't check the move")
            continue
        if tgt in els:
            t = els[tgt]
            cx = sum(p[0] for p in t["poly"]) / len(t["poly"])
            cz = sum(p[1] for p in t["poly"]) / len(t["poly"])
            d0 = math.dist((a[0], a[2]), (cx, cz))
            d1 = math.dist((b[0], b[2]), (cx, cz))
            if d1 <= d0:
                W(f"shot '{sid}': camera ends no farther from '{tgt}' than it starts; this is not a pull-out")
            if d0 > 6:
                W(f"shot '{sid}': starts {d0:.1f} m from '{tgt}'; a close-up usually starts within ~0.3-3 m")
        hit = set()
        for k in range(41):
            t = k / 40
            p = [a[i] + (b[i] - a[i]) * t for i in range(3)]
            if p[1] < ground - tol and not any(point_in_poly((p[0], p[2]), w["poly"]) for w in wl):
                hit.add("(underground)")
            for x in el:
                if x["id"] in hit or x.get("type") == "tree":
                    continue
                y0 = base_of(x)
                if y0 <= p[1] <= y0 + x["h"] and point_in_poly((p[0], p[2]), x["poly"]):
                    hit.add(x["id"])
        for x in sorted(hit):
            W(f"shot '{sid}': camera path passes through {x}; bend the path or cut")

    info.append(f"site {sb[2]-sb[0]:.0f} x {sb[3]-sb[1]:.0f} m, {len(zones)} zones, "
                f"{len(els)} elements, {len(waters)} water bodies, {len(paths)} paths, "
                f"{len(plan.get('interfaces', []))} interfaces, {len(plan.get('shots', []))} shots")
    owners = {}
    for z in zl:
        owners.setdefault(z.get("owner"), []).append(z["id"])
    for o, zs in owners.items():
        n = sum(1 for e in el if e.get("zone") in zs)
        info.append(f"agent '{o}': zones {', '.join(zs)}; {n} elements; files {', '.join(f for z in zl if z['id'] in zs for f in z.get('files', []))}")
    return errors, warnings, info, {"site": sb, "zones": zones, "waters": waters, "els": els, "paths": paths}


# ---------------------------------------------------------------- SVG
PALETTE = ["#e4572e", "#4c6ef5", "#2b8a3e", "#ae3ec9", "#f08c00", "#0b7285", "#c2255c", "#5c940d"]


def write_svg(plan, g, path, px_per_m=10, problems=()):
    sb = g["site"]
    m = 40
    W_ = (sb[2] - sb[0]) * px_per_m + 2 * m
    H_ = (sb[3] - sb[1]) * px_per_m + 2 * m + 30

    def X(x):
        return (x - sb[0]) * px_per_m + m

    def Y(z):
        return (z - sb[1]) * px_per_m + m

    def pts(poly):
        return " ".join(f"{X(p[0]):.1f},{Y(p[1]):.1f}" for p in poly)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_:.0f}" height="{H_:.0f}" '
           f'viewBox="0 0 {W_:.0f} {H_:.0f}" font-family="sans-serif">',
           '<rect width="100%" height="100%" fill="#fbfaf6"/>']
    grid = plan.get("site", {}).get("grid") or 1.0
    step = grid
    while step * px_per_m < 8:
        step *= 2
    x = math.ceil(sb[0] / step) * step
    while x <= sb[2] + 1e-9:
        major = abs(x / 10 - round(x / 10)) < 1e-9
        out.append(f'<line x1="{X(x):.1f}" y1="{Y(sb[1]):.1f}" x2="{X(x):.1f}" y2="{Y(sb[3]):.1f}" '
                   f'stroke="{"#d0ccc0" if major else "#ebe8df"}" stroke-width="{1 if major else 0.5}"/>')
        x += step
    z = math.ceil(sb[1] / step) * step
    while z <= sb[3] + 1e-9:
        major = abs(z / 10 - round(z / 10)) < 1e-9
        out.append(f'<line x1="{X(sb[0]):.1f}" y1="{Y(z):.1f}" x2="{X(sb[2]):.1f}" y2="{Y(z):.1f}" '
                   f'stroke="{"#d0ccc0" if major else "#ebe8df"}" stroke-width="{1 if major else 0.5}"/>')
        z += step
    out.append(f'<rect x="{X(sb[0])}" y="{Y(sb[1])}" width="{(sb[2]-sb[0])*px_per_m}" '
               f'height="{(sb[3]-sb[1])*px_per_m}" fill="none" stroke="#333" stroke-width="2"/>')
    colors = {}
    for i, (zid, zz) in enumerate(g["zones"].items()):
        c = PALETTE[i % len(PALETTE)]
        colors[zid] = c
        bb = zz["bbox"]
        out.append(f'<rect x="{X(bb[0]):.1f}" y="{Y(bb[1]):.1f}" width="{(bb[2]-bb[0])*px_per_m:.1f}" '
                   f'height="{(bb[3]-bb[1])*px_per_m:.1f}" fill="{c}" fill-opacity="0.06" stroke="{c}" '
                   f'stroke-width="1.5" stroke-dasharray="6 4"/>')
        out.append(f'<text x="{X(bb[0])+4:.1f}" y="{Y(bb[1])+13:.1f}" font-size="11" fill="{c}" '
                   f'font-weight="bold">{escape(zid)} / {escape(str(zz.get("owner")))}</text>')
    for w in g["waters"].values():
        out.append(f'<polygon points="{pts(w["poly"])}" fill="#74c0fc" fill-opacity="0.7" stroke="#1971c2"/>')
    for p in g["paths"].values():
        d = " ".join(f"{X(q[0]):.1f},{Y(q[1]):.1f}" for q in p["pts"])
        out.append(f'<polyline points="{d}" fill="none" stroke="#c9b99a" stroke-opacity="0.9" '
                   f'stroke-width="{max(1, p.get("width", 1) * px_per_m):.1f}" stroke-linejoin="round"/>')
    order = sorted(g["els"].values(), key=lambda e: float(e.get("base_y", 0)))
    bad = set(problems)
    for e in order:
        c = colors.get(e.get("zone"), "#555")
        stroke = "#e03131" if e["id"] in bad else c
        sw = 2.5 if e["id"] in bad else 1
        fill_op = 0.15 if e.get("type") == "ground_cover" else 0.45
        out.append(f'<polygon points="{pts(e["poly"])}" fill="{c}" fill-opacity="{fill_op}" '
                   f'stroke="{stroke}" stroke-width="{sw}"><title>{escape(e["id"])} '
                   f'h={e["h"]} m base={e.get("base_y", 0)}</title></polygon>')
    for e in order:
        bb = bbox_of(e["poly"])
        if (bb[2] - bb[0]) * px_per_m < 30 and e.get("type") in ("tree", "lantern", "rock"):
            continue
        cx, cz = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
        out.append(f'<text x="{X(cx):.1f}" y="{Y(cz):.1f}" font-size="9" text-anchor="middle" '
                   f'fill="#222">{escape(e["id"])} {e["h"]:g}m</text>')
    for itf in plan.get("interfaces", []):
        p = itf.get("point")
        if p and len(p) == 2:
            out.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="4" fill="#fff" stroke="#000" stroke-width="1.5">'
                       f'<title>{escape(str(itf.get("id")))}</title></circle>')
    for s in plan.get("shots", []):
        cam = s.get("camera", {})
        a, b = cam.get("start"), cam.get("end")
        if a and b and len(a) == 3 and len(b) == 3:
            out.append(f'<line x1="{X(a[0]):.1f}" y1="{Y(a[2]):.1f}" x2="{X(b[0]):.1f}" y2="{Y(b[2]):.1f}" '
                       f'stroke="#862e9c" stroke-width="1.2" stroke-dasharray="3 3"/>')
            out.append(f'<circle cx="{X(a[0]):.1f}" cy="{Y(a[2]):.1f}" r="3" fill="#862e9c"/>')
            out.append(f'<text x="{X(a[0])+4:.1f}" y="{Y(a[2])-4:.1f}" font-size="9" fill="#862e9c">{escape(str(s.get("id")))}</text>')
    # north arrow + scale bar
    nx, ny = W_ - m + 18, m + 10
    out.append(f'<path d="M{nx},{ny-8} l5,14 l-5,-4 l-5,4 z" fill="#333"/>'
               f'<text x="{nx}" y="{ny+18}" font-size="10" text-anchor="middle">N (-z)</text>')
    sx, sy = m, H_ - 18
    out.append(f'<line x1="{sx}" y1="{sy}" x2="{sx + 10*px_per_m}" y2="{sy}" stroke="#333" stroke-width="3"/>'
               f'<text x="{sx + 10*px_per_m + 6}" y="{sy+4}" font-size="10">10 m</text>')
    out.append(f'<text x="{sx + 10*px_per_m + 50}" y="{sy+4}" font-size="10" fill="#555">'
               f'{escape(str(plan.get("name", "")))}  - red outline = problem</text>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--svg", help="write a top-view SVG site plan here")
    ap.add_argument("--px-per-m", type=float, default=10)
    ap.add_argument("--min-overlap", type=float, default=0.05, help="m^2 of overlap that counts (default 0.05)")
    ap.add_argument("--tol", type=float, default=0.02, help="length tolerance in m (default 0.02)")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    a = ap.parse_args()
    try:
        with open(a.plan, encoding="utf-8") as f:
            plan = json.load(f)
    except (OSError, json.JSONDecodeError) as ex:
        print(f"[ERROR] can't read {a.plan}: {ex}")
        return 1
    errors, warnings, info, g = check(plan, a.min_overlap, a.tol)
    if a.svg and g:
        names = set()
        for msg in errors + warnings:
            for eid in g["els"]:
                if f"'{eid}'" in msg:
                    names.add(eid)
        write_svg(plan, g, a.svg, a.px_per_m, names)
        info.append(f"SVG written: {os.path.abspath(a.svg)}")
    if a.json:
        print(json.dumps({"errors": errors, "warnings": warnings, "info": info}, ensure_ascii=False, indent=2))
    else:
        for tag, msgs in (("INFO", info), ("ERROR", errors), ("WARN", warnings)):
            for msg in msgs:
                print(f"[{tag}] {msg}")
        print(f"\n{len(errors)} errors, {len(warnings)} warnings"
              + ("  -> fix the errors before sending any zone agent out" if errors else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
