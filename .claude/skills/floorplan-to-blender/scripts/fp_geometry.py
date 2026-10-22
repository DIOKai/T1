#!/usr/bin/env python3
"""Pure-Python geometry for floorplan-to-blender (no bpy needed).

Turns a layout JSON (schema floorplan-to-blender/1, see references/layout-schema.md)
into closed solids: mitered wall pieces split around openings, glass panes,
door leaves, room floors and ceilings, a structural slab and straight stairs.
build_in_blender.py turns these solids into Blender meshes; this file can also
write an OBJ (to look at in any viewer) and a top-down SVG (to overlay on the plan).

Usage:
    python fp_geometry.py layout.json --obj out.obj --svg top.svg
Standard library only.
"""
import argparse
import json
import math
import sys

EPS = 1e-9


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _mul(a, k):
    return (a[0] * k, a[1] * k)


def _len(a):
    return math.hypot(a[0], a[1])


def _norm(a):
    n = _len(a)
    return (a[0] / n, a[1] / n)


def _left(d):
    return (-d[1], d[0])


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def polygon_area(poly):
    """Signed shoelace area (positive = counter-clockwise)."""
    s = 0.0
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        s += p[0] * q[1] - q[0] * p[1]
    return s / 2.0


def _line_intersect(p, d, q, e):
    """Intersection of p + s*d and q + u*e, or None if parallel."""
    den = _cross(d, e)
    if abs(den) < 1e-12:
        return None
    s = _cross(_sub(q, p), e) / den
    return _add(p, _mul(d, s))


def wall_offsets(wall):
    """(left, right) offsets from the axis, measured along the left normal."""
    t = float(wall["thickness"])
    j = wall.get("justify", "center")
    if j == "left":       # wall body lies on the left of the drawn path
        return t, 0.0
    if j == "right":
        return 0.0, -t
    return t / 2.0, -t / 2.0


def wall_segments(wall):
    """Segments of a wall path with mitered left/right end points.

    Returns a list of dicts: start, end, d (unit dir), n (left normal), length,
    and Ls, Le, Rs, Re = mitered corners of the footprint on the left/right faces.
    """
    pts = [tuple(map(float, p)) for p in wall["path"]]
    closed = bool(wall.get("closed", False))
    if closed and _len(_sub(pts[0], pts[-1])) < 1e-6:
        pts = pts[:-1]
    n_seg = len(pts) if closed else len(pts) - 1
    oL, oR = wall_offsets(wall)
    t = float(wall["thickness"])
    segs = []
    for i in range(n_seg):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        d = _norm(_sub(b, a))
        segs.append({"index": i, "start": a, "end": b, "d": d, "n": _left(d), "length": _len(_sub(b, a))})

    def offset_point(seg, which, off):
        base = seg["start"] if which == "start" else seg["end"]
        return _add(base, _mul(seg["n"], off))

    def miter(prev, nxt, off):
        p = offset_point(prev, "end", off)
        q = offset_point(nxt, "start", off)
        x = _line_intersect(p, prev["d"], q, nxt["d"])
        if x is None:  # collinear: no corner
            return q
        # Very sharp corners make huge spikes; clamp them to a bevel-ish point.
        if _len(_sub(x, prev["end"])) > 4.0 * max(t, 0.05):
            return q
        return x

    for i, s in enumerate(segs):
        has_prev = closed or i > 0
        has_next = closed or i < n_seg - 1
        prev = segs[i - 1] if has_prev else None
        nxt = segs[(i + 1) % n_seg] if has_next else None
        s["Ls"] = miter(prev, s, oL) if prev else offset_point(s, "start", oL)
        s["Rs"] = miter(prev, s, oR) if prev else offset_point(s, "start", oR)
        s["Le"] = miter(s, nxt, oL) if nxt else offset_point(s, "end", oL)
        s["Re"] = miter(s, nxt, oR) if nxt else offset_point(s, "end", oR)
        s["oL"], s["oR"] = oL, oR
    return segs


def opening_span(op, seg):
    """Axial start/end (metres from segment start) of an opening."""
    w = float(op["width"])
    off = float(op["offset"])
    if op.get("offset_ref", "start") == "center":
        return off - w / 2.0, off + w / 2.0
    return off, off + w


def _point_at(seg, u, side):
    """Point on the left/right face at axial coordinate u, honouring miters at the ends."""
    if u <= EPS:
        return seg["Ls"] if side == "L" else seg["Rs"]
    if u >= seg["length"] - EPS:
        return seg["Le"] if side == "L" else seg["Re"]
    off = seg["oL"] if side == "L" else seg["oR"]
    return _add(_add(seg["start"], _mul(seg["d"], u)), _mul(seg["n"], off))


def prism(footprint, z0, z1):
    """Closed prism from a CCW or CW footprint polygon. Returns (verts, faces)."""
    fp = list(footprint)
    if polygon_area(fp) < 0:
        fp.reverse()
    n = len(fp)
    verts = [(x, y, z0) for x, y in fp] + [(x, y, z1) for x, y in fp]
    faces = [list(reversed(range(n))), [n + i for i in range(n)]]
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n + j, n + i])
    return verts, faces


def _box_on_segment(seg, u0, u1, off0, off1, z0, z1):
    a = _add(_add(seg["start"], _mul(seg["d"], u0)), _mul(seg["n"], off0))
    b = _add(_add(seg["start"], _mul(seg["d"], u1)), _mul(seg["n"], off0))
    c = _add(_add(seg["start"], _mul(seg["d"], u1)), _mul(seg["n"], off1))
    e = _add(_add(seg["start"], _mul(seg["d"], u0)), _mul(seg["n"], off1))
    return prism([a, b, c, e], z0, z1)


def build_solids(layout):
    """All solids for the layout: list of dicts {name, kind, material, verts, faces, level}."""
    levels = {lv["id"]: lv for lv in layout.get("levels", [])}
    solids = []

    def add(name, kind, material, vf, level):
        solids.append({"name": name, "kind": kind, "material": material,
                       "verts": vf[0], "faces": vf[1], "level": level})

    openings_by_wall = {}
    for op in layout.get("openings", []):
        openings_by_wall.setdefault(op["wall"], []).append(op)

    for wall in layout.get("walls", []):
        lv = levels[wall["level"]]
        z0 = float(lv.get("elevation", 0.0)) + float(wall.get("base_offset", 0.0))
        h = float(wall.get("height") or lv["height"])
        z1 = z0 + h
        for seg in wall_segments(wall):
            ops = sorted(
                [o for o in openings_by_wall.get(wall["id"], []) if int(o.get("segment", 0)) == seg["index"]],
                key=lambda o: opening_span(o, seg)[0])
            cursor = 0.0
            piece = 0

            def solid_piece(u0, u1, za, zb, tag):
                nonlocal piece
                if u1 - u0 < 1e-4 or zb - za < 1e-4:
                    return
                fp = [_point_at(seg, u0, "R"), _point_at(seg, u1, "R"),
                      _point_at(seg, u1, "L"), _point_at(seg, u0, "L")]
                add(f"{wall['id']}_s{seg['index']}_{tag}{piece}", "wall", "FP_Wall",
                    prism(fp, za, zb), wall["level"])
                solids[-1]["part"] = tag  # "p" pier, "sill", "lintel" (spans between piers)
                piece += 1

            for op in ops:
                a, b = opening_span(op, seg)
                sill = float(op.get("sill", 0.0))
                top = sill + float(op["height"])
                solid_piece(cursor, a, z0, z1, "p")          # full-height pier before the hole
                solid_piece(a, b, z0, z0 + sill, "sill")      # below the hole
                solid_piece(a, b, z0 + top, z1, "lintel")     # above the hole
                otype = op.get("type", "door")
                mid = (seg["oL"] + seg["oR"]) / 2.0
                if otype == "window":
                    add(f"{op['id']}_glass", "glass", "FP_Glass",
                        _box_on_segment(seg, a, b, mid - 0.006, mid + 0.006, z0 + sill, z0 + top), wall["level"])
                elif otype in ("door", "sliding_door"):
                    add(f"{op['id']}_leaf", "door", "FP_Door",
                        _box_on_segment(seg, a + 0.01, b - 0.01, mid - 0.02, mid + 0.02, z0 + sill, z0 + top - 0.01),
                        wall["level"])
                elif otype == "garage_door":
                    add(f"{op['id']}_leaf", "door", "FP_Door",
                        _box_on_segment(seg, a, b, mid - 0.03, mid + 0.03, z0 + sill, z0 + top), wall["level"])
                cursor = b
            solid_piece(cursor, seg["length"], z0, z1, "p")

    # Structural slab under each level: outer outline of the closed exterior wall(s).
    for wall in layout.get("walls", []):
        if wall.get("kind") == "exterior" and wall.get("closed"):
            lv = levels[wall["level"]]
            e = float(lv.get("elevation", 0.0))
            st = float(lv.get("slab_thickness", 0.2))
            segs = wall_segments(wall)
            outer_side = "L" if polygon_area([s["Ls"] for s in segs]) > polygon_area([s["Rs"] for s in segs]) else "R"
            outline = [s["Ls"] if outer_side == "L" else s["Rs"] for s in segs]
            add(f"{wall['id']}_slab", "slab", "FP_Slab", prism(outline, e - st, e), wall["level"])

    # Room floors (thin finish on top of the slab, under the walls' base) and ceilings.
    for room in layout.get("rooms", []):
        lv = levels[room["level"]]
        e = float(lv.get("elevation", 0.0))
        ch = float(room.get("ceiling_height") or lv["height"])
        poly = [tuple(map(float, p)) for p in room["polygon"]]
        finish = room.get("floor_finish", "wood")
        add(f"{room['id']}_floor", "floor", f"FP_Floor_{finish}", prism(poly, e, e + 0.015), room["level"])
        add(f"{room['id']}_ceiling", "ceiling", "FP_Ceiling", prism(poly, e + ch - 0.015, e + ch), room["level"])

    # Straight stairs as solid steps (L/U stairs are left to bonsai-stairs or manual work).
    for st in layout.get("stairs", []):
        if st.get("type", "straight") != "straight":
            continue
        lv = levels[st["from"]]
        e = float(lv.get("elevation", 0.0))
        d = _norm(tuple(map(float, st["direction"])))
        n = _left(d)
        start = tuple(map(float, st["start"]))
        w = float(st["width"])
        risers = int(st["risers"])
        rise = float(st["riser"])
        tread = float(st["tread"])
        # n risers need n-1 treads: the last riser steps onto the upper floor itself.
        for k in range(risers - 1):
            a = _add(start, _mul(d, k * tread))
            b = _add(start, _mul(d, (k + 1) * tread))
            fp = [_add(a, _mul(n, -w / 2)), _add(b, _mul(n, -w / 2)), _add(b, _mul(n, w / 2)), _add(a, _mul(n, w / 2))]
            add(f"{st['id']}_step{k:02d}", "stair", "FP_Stair", prism(fp, e, e + (k + 1) * rise), st["from"])
    return solids


def write_obj(solids, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# floorplan-to-blender preview (Z up, metres)\n")
        base = 1
        for s in solids:
            f.write(f"o {s['name']}\nusemtl {s['material']}\n")
            for v in s["verts"]:
                f.write("v %.5f %.5f %.5f\n" % v)
            for face in s["faces"]:
                f.write("f " + " ".join(str(base + i) for i in face) + "\n")
            base += len(s["verts"])


SVG_COLOURS = {"wall": "#333", "glass": "#3a8fd9", "door": "#c27c2c", "slab": "#eee",
               "floor": "#f4e9d8", "stair": "#999"}


def write_svg(solids, path, level=None, px_per_m=50.0):
    """Top-down footprints (y up) so the result can be laid over the source plan."""
    keep = [s for s in solids if s["kind"] != "ceiling" and (level is None or s["level"] == level)]
    xs = [v[0] for s in keep for v in s["verts"]]
    ys = [v[1] for s in keep for v in s["verts"]]
    if not xs:
        raise SystemExit("nothing to draw")
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pad = 0.5
    W = (maxx - minx + 2 * pad) * px_per_m
    H = (maxy - miny + 2 * pad) * px_per_m
    order = ["slab", "floor", "stair", "wall", "door", "glass"]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.1f} {H:.1f}">',
           f'<rect width="100%" height="100%" fill="white"/>']
    for kind in order:
        for s in keep:
            if s["kind"] != kind:
                continue
            n = len(s["verts"]) // 2
            pts = " ".join("%.1f,%.1f" % ((x - minx + pad) * px_per_m, (maxy - y + pad) * px_per_m)
                           for x, y, _ in s["verts"][:n])
            op = "0.6" if kind in ("slab", "floor") else "0.9"
            out.append(f'<polygon points="{pts}" fill="{SVG_COLOURS.get(kind, "#888")}" fill-opacity="{op}" '
                       f'stroke="#000" stroke-width="0.5"><title>{s["name"]}</title></polygon>')
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("layout")
    ap.add_argument("--obj", help="write an OBJ preview")
    ap.add_argument("--svg", help="write a top-down SVG of the footprints")
    ap.add_argument("--level", help="SVG: only this level id")
    ap.add_argument("--px-per-m", type=float, default=50.0, help="SVG scale (match the plan's px_per_m to overlay)")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):  # Chinese names on a cp1252/gbk Windows console
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    with open(a.layout, encoding="utf-8") as f:
        layout = json.load(f)
    solids = build_solids(layout)
    kinds = {}
    for s in solids:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    print("solids:", ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    if a.obj:
        write_obj(solids, a.obj)
        print("wrote", a.obj)
    if a.svg:
        write_svg(solids, a.svg, a.level, a.px_per_m)
        print("wrote", a.svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
