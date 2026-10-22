#!/usr/bin/env python3
"""Convert a saved Overpass API JSON response into GeoJSON building footprints.

Offline only: this script reads a file, it never fetches anything.
Python 3.8+ standard library only.

Accepts both Overpass output styles:
  * `out geom;`            ways/relations carry their own coordinates
  * `out body; >; out skel qt;`  ways reference node ids listed in the same file

Every footprint gets:
  height, min_height (metres), height_source ("height" | "levels" | "default"),
  levels, footprint_m2 (ground area), floor_area_m2 (area x levels, a rough
  gross floor area for gameplay), osm_id ("way/123" / "relation/9").

Outputs:
  --out FILE        GeoJSON in WGS84 lon/lat (RFC 7946, outer rings CCW)
  --local FILE      same features in local ENU metres [x=east, y=north]
                    around --origin (exact WGS84 -> ECEF -> ENU, ground at 0 m)

Example:
  python osm_to_geojson.py overpass.json --out buildings.geojson \
      --local buildings_local.json --origin auto

Heights are estimates whenever height_source != "height". Default values
(3.0 m per level, 3 levels when nothing is tagged) are rules of thumb, not data.
Data (c) OpenStreetMap contributors, ODbL. Keep that attribution with the output.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from typing import Dict, List, Optional, Sequence, Tuple

LonLat = Tuple[float, float]
Ring = List[LonLat]

# WGS84 ellipsoid
WGS84_A = 6378137.0
WGS84_F = 1 / 298.257223563
WGS84_E2 = WGS84_F * (2 - WGS84_F)

FEET_TO_M = 0.3048


# ---------------------------------------------------------------- heights
_NUM = r"[-+]?\d+(?:[.,]\d+)?"


def parse_length_m(value: Optional[str]) -> Optional[float]:
    """Parse an OSM length tag to metres. Bare numbers are metres.

    Handles "12", "12.5", "12,5", "12 m", "40 ft", "30'", "30'6\"".
    Returns None for anything unparseable or negative.
    """
    if value is None:
        return None
    v = str(value).strip().lower()
    if not v:
        return None
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*'\s*(?:(\d+(?:\.\d+)?)\s*\")?", v)
    if m:  # feet and inches
        feet = float(m.group(1))
        inches = float(m.group(2)) if m.group(2) else 0.0
        return round((feet + inches / 12.0) * FEET_TO_M, 3)
    m = re.fullmatch(r"(" + _NUM + r")\s*(m|metres?|meters?|ft|feet)?", v)
    if not m:
        return None
    num = float(m.group(1).replace(",", "."))
    if num < 0:
        return None
    unit = m.group(2) or "m"
    if unit in ("ft", "feet"):
        num *= FEET_TO_M
    return round(num, 3)


def parse_levels(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    v = str(value).strip().replace(",", ".")
    try:
        n = float(v)
    except ValueError:
        return None
    return n if n >= 0 else None


def building_height(tags: Dict[str, str], level_height: float,
                    default_levels: float) -> Dict[str, object]:
    """Return height info for one building or building:part tag dict."""
    height = parse_length_m(tags.get("height"))
    levels = parse_levels(tags.get("building:levels"))
    roof_levels = parse_levels(tags.get("roof:levels")) or 0.0
    roof_height = parse_length_m(tags.get("roof:height"))
    min_height = parse_length_m(tags.get("min_height"))
    min_level = parse_levels(tags.get("building:min_level"))

    if height is not None and height > 0:
        source = "height"
    elif levels is not None and levels > 0:
        source = "levels"
        roof = roof_height if roof_height is not None else roof_levels * level_height
        height = levels * level_height + roof
    else:
        source = "default"
        levels = None
        height = default_levels * level_height

    if min_height is None:
        min_height = (min_level * level_height) if min_level else 0.0
    if min_height >= height:  # broken tagging; do not produce inverted solids
        min_height = 0.0

    effective_levels = levels
    if effective_levels is None:
        effective_levels = max(1.0, round(height / level_height))
    if min_level:
        effective_levels = max(1.0, effective_levels - min_level)

    return {
        "height": round(float(height), 2),
        "min_height": round(float(min_height), 2),
        "height_source": source,
        "levels": effective_levels,
    }


# ---------------------------------------------------------------- geometry
def geodetic_to_ecef(lat: float, lon: float, h: float = 0.0) -> Tuple[float, float, float]:
    la, lo = math.radians(lat), math.radians(lon)
    n = WGS84_A / math.sqrt(1 - WGS84_E2 * math.sin(la) ** 2)
    x = (n + h) * math.cos(la) * math.cos(lo)
    y = (n + h) * math.cos(la) * math.sin(lo)
    z = (n * (1 - WGS84_E2) + h) * math.sin(la)
    return x, y, z


class EnuFrame:
    """Local East-North-Up frame (metres) tangent to WGS84 at an origin."""

    def __init__(self, lat0: float, lon0: float, h0: float = 0.0):
        self.lat0, self.lon0, self.h0 = lat0, lon0, h0
        self.ox, self.oy, self.oz = geodetic_to_ecef(lat0, lon0, h0)
        la, lo = math.radians(lat0), math.radians(lon0)
        self.sla, self.cla = math.sin(la), math.cos(la)
        self.slo, self.clo = math.sin(lo), math.cos(lo)

    def to_enu(self, lat: float, lon: float, h: float = 0.0) -> Tuple[float, float, float]:
        x, y, z = geodetic_to_ecef(lat, lon, h)
        dx, dy, dz = x - self.ox, y - self.oy, z - self.oz
        e = -self.slo * dx + self.clo * dy
        n = -self.sla * self.clo * dx - self.sla * self.slo * dy + self.cla * dz
        u = self.cla * self.clo * dx + self.cla * self.slo * dy + self.sla * dz
        return e, n, u


def signed_area(xy: Sequence[Tuple[float, float]]) -> float:
    """Shoelace area; positive = counter-clockwise. Ring may be closed."""
    a = 0.0
    for i in range(len(xy) - 1):
        a += xy[i][0] * xy[i + 1][1] - xy[i + 1][0] * xy[i][1]
    return a / 2.0


def clean_ring(ring: Ring) -> Optional[Ring]:
    """Drop consecutive duplicates, close the ring, reject < 3 distinct points."""
    out: Ring = []
    for p in ring:
        if not out or p != out[-1]:
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    if len(set(out)) < 3:
        return None
    out.append(out[0])
    return out


def orient(ring: Ring, ccw: bool) -> Ring:
    if (signed_area(ring) > 0) != ccw:
        return list(reversed(ring))
    return ring


def point_in_ring(pt: LonLat, ring: Ring) -> bool:
    x, y = pt
    inside = False
    for i in range(len(ring) - 1):
        x1, y1 = ring[i]
        x2, y2 = ring[i + 1]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin:
                inside = not inside
    return inside


def join_ways(segments: List[Ring]) -> Tuple[List[Ring], int]:
    """Join open way segments end-to-end into closed rings.

    Returns (closed_rings, number_of_segments_that_could_not_be_closed).
    """
    pending = [list(s) for s in segments if len(s) >= 2]
    rings: List[Ring] = []
    unclosed = 0
    while pending:
        cur = pending.pop(0)
        changed = True
        while cur[0] != cur[-1] and changed:
            changed = False
            for i, seg in enumerate(pending):
                if seg[0] == cur[-1]:
                    cur.extend(seg[1:])
                elif seg[-1] == cur[-1]:
                    cur.extend(list(reversed(seg))[1:])
                elif seg[-1] == cur[0]:
                    cur = seg[:-1] + cur
                elif seg[0] == cur[0]:
                    cur = list(reversed(seg))[:-1] + cur
                else:
                    continue
                pending.pop(i)
                changed = True
                break
        if cur[0] == cur[-1]:
            rings.append(cur)
        else:
            unclosed += 1
    return rings, unclosed


# ---------------------------------------------------------------- parsing
def is_building(tags: Dict[str, str]) -> bool:
    b = tags.get("building")
    p = tags.get("building:part")
    return (b is not None and b != "no") or (p is not None and p != "no")


def way_coords(el: dict, nodes: Dict[int, LonLat]) -> Optional[Ring]:
    if "geometry" in el and el["geometry"]:
        pts = [g for g in el["geometry"] if g]
        return [(float(g["lon"]), float(g["lat"])) for g in pts]
    refs = el.get("nodes")
    if not refs:
        return None
    coords = []
    for r in refs:
        if r not in nodes:
            return None
        coords.append(nodes[r])
    return coords


def convert(data: dict, level_height: float = 3.0, default_levels: float = 3.0,
            hide_outlines_with_parts: bool = False) -> Tuple[dict, Dict[str, int]]:
    """Return (FeatureCollection in lon/lat, stats)."""
    elements = data.get("elements", [])
    nodes: Dict[int, LonLat] = {}
    ways: Dict[int, dict] = {}
    for el in elements:
        if el.get("type") == "node" and "lat" in el:
            nodes[el["id"]] = (float(el["lon"]), float(el["lat"]))
        elif el.get("type") == "way":
            ways[el["id"]] = el

    stats = {"features": 0, "skipped_unclosed": 0, "skipped_missing_geometry": 0,
             "skipped_degenerate": 0, "height": 0, "levels": 0, "default": 0,
             "hidden_outlines": 0}
    features: List[dict] = []
    used_as_member = set()

    # relations first (multipolygon buildings)
    for el in elements:
        if el.get("type") != "relation":
            continue
        tags = el.get("tags", {})
        if tags.get("type") not in ("multipolygon", "building") or not is_building(tags):
            continue
        if tags.get("type") == "building":
            continue  # type=building relations group parts; parts are emitted on their own
        outers, inners = [], []
        missing = False
        for m in el.get("members", []):
            if m.get("type") != "way":
                continue
            role = m.get("role") or "outer"
            if "geometry" in m and m["geometry"]:
                coords = [(float(g["lon"]), float(g["lat"])) for g in m["geometry"] if g]
            elif m.get("ref") in ways:
                coords = way_coords(ways[m["ref"]], nodes)
                used_as_member.add(m["ref"])
            else:
                coords = None
            if not coords:
                missing = True
                continue
            (inners if role == "inner" else outers).append(coords)
        if missing and not outers:
            stats["skipped_missing_geometry"] += 1
            continue
        outer_rings, bad_o = join_ways(outers)
        inner_rings, bad_i = join_ways(inners)
        stats["skipped_unclosed"] += bad_o + bad_i
        polys = []
        cleaned_inners = [r for r in (clean_ring(x) for x in inner_rings) if r]
        for o in outer_rings:
            co = clean_ring(o)
            if not co:
                stats["skipped_degenerate"] += 1
                continue
            holes = [orient(h, ccw=False) for h in cleaned_inners if point_in_ring(h[0], co)]
            polys.append([orient(co, ccw=True)] + holes)
        if not polys:
            continue
        geom = ({"type": "Polygon", "coordinates": polys[0]} if len(polys) == 1
                else {"type": "MultiPolygon", "coordinates": polys})
        features.append(_feature("relation/%d" % el["id"], tags, geom,
                                 level_height, default_levels, stats))

    for wid, el in ways.items():
        tags = el.get("tags", {})
        if not is_building(tags):
            continue
        coords = way_coords(el, nodes)
        if not coords:
            stats["skipped_missing_geometry"] += 1
            continue
        if coords[0] != coords[-1]:
            stats["skipped_unclosed"] += 1
            continue
        ring = clean_ring(coords)
        if not ring:
            stats["skipped_degenerate"] += 1
            continue
        geom = {"type": "Polygon", "coordinates": [orient(ring, ccw=True)]}
        features.append(_feature("way/%d" % wid, tags, geom,
                                 level_height, default_levels, stats))

    # Simple 3D Buildings: an outline that contains building:part areas is not
    # drawn in 3D. Mark it, and drop it when asked.
    cell = 0.01  # degrees; grid index so big cities stay fast
    grid: Dict[Tuple[int, int], List[LonLat]] = {}
    for p in features:
        if p["properties"]["is_part"]:
            c = _ring_centroid(_outer_rings(p["geometry"])[0])
            grid.setdefault((int(math.floor(c[0] / cell)), int(math.floor(c[1] / cell))), []).append(c)
    for f in features:
        if f["properties"]["is_part"]:
            continue
        has = False
        for o in _outer_rings(f["geometry"]):
            xs = [q[0] for q in o]
            ys = [q[1] for q in o]
            for gx in range(int(math.floor(min(xs) / cell)), int(math.floor(max(xs) / cell)) + 1):
                for gy in range(int(math.floor(min(ys) / cell)), int(math.floor(max(ys) / cell)) + 1):
                    if any(point_in_ring(c, o) for c in grid.get((gx, gy), ())):
                        has = True
                        break
                if has:
                    break
            if has:
                break
        f["properties"]["has_parts"] = has
    if hide_outlines_with_parts:
        before = len(features)
        features = [f for f in features if not f["properties"].get("has_parts")]
        stats["hidden_outlines"] = before - len(features)

    for f in features:
        stats[f["properties"]["height_source"]] += 1
    stats["features"] = len(features)
    fc = {"type": "FeatureCollection",
          "attribution": "Data (c) OpenStreetMap contributors, ODbL 1.0, "
                         "https://www.openstreetmap.org/copyright",
          "features": features}
    return fc, stats


def _outer_rings(geom: dict) -> List[Ring]:
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    return [p[0] for p in geom["coordinates"]]


def _ring_centroid(ring: Ring) -> LonLat:
    pts = ring[:-1]
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def _feature(osm_id: str, tags: Dict[str, str], geom: dict, level_height: float,
             default_levels: float, stats: Dict[str, int]) -> dict:
    h = building_height(tags, level_height, default_levels)
    props = {"osm_id": osm_id,
             "building": tags.get("building") or tags.get("building:part"),
             "is_part": "building:part" in tags and tags.get("building:part") != "no",
             "has_parts": False,
             "name": tags.get("name")}
    props.update(h)
    return {"type": "Feature", "id": osm_id, "properties": props, "geometry": geom}


# ---------------------------------------------------------------- local metres
def bbox_center(fc: dict) -> Tuple[float, float]:
    lons, lats = [], []
    for f in fc["features"]:
        for ring in _outer_rings(f["geometry"]):
            for lon, lat in ring:
                lons.append(lon)
                lats.append(lat)
    if not lons:
        raise ValueError("no features: cannot pick an automatic origin")
    return (min(lats) + max(lats)) / 2.0, (min(lons) + max(lons)) / 2.0


def to_local(fc: dict, lat0: float, lon0: float) -> dict:
    """Copy of fc with coordinates in ENU metres; adds footprint/floor areas."""
    frame = EnuFrame(lat0, lon0)

    def conv_ring(ring: Ring) -> List[List[float]]:
        out = []
        for lon, lat in ring:
            e, n, _u = frame.to_enu(lat, lon)
            out.append([round(e, 3), round(n, 3)])
        return out

    feats = []
    for f in fc["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        lpolys = [[conv_ring(r) for r in poly] for poly in polys]
        area = 0.0
        for poly in lpolys:
            area += abs(signed_area(poly[0])) - sum(abs(signed_area(h)) for h in poly[1:])
        props = dict(f["properties"])
        props["footprint_m2"] = round(area, 1)
        props["floor_area_m2"] = round(area * float(props["levels"]), 1)
        lg = ({"type": "Polygon", "coordinates": lpolys[0]} if g["type"] == "Polygon"
              else {"type": "MultiPolygon", "coordinates": lpolys})
        feats.append({"type": "Feature", "id": f["id"], "properties": props, "geometry": lg})
    return {"type": "FeatureCollection",
            "crs_note": "local ENU metres, x=east y=north, tangent to WGS84 at origin",
            "origin": {"lat": lat0, "lon": lon0},
            "attribution": fc["attribution"],
            "features": feats}


def add_areas_to_lonlat(fc: dict, local: dict) -> None:
    for f, lf in zip(fc["features"], local["features"]):
        f["properties"]["footprint_m2"] = lf["properties"]["footprint_m2"]
        f["properties"]["floor_area_m2"] = lf["properties"]["floor_area_m2"]


# ---------------------------------------------------------------- CLI
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input", help="saved Overpass JSON response ([out:json])")
    ap.add_argument("--out", help="write lon/lat GeoJSON here")
    ap.add_argument("--local", help="write local-metre GeoJSON-like file here")
    ap.add_argument("--origin", default="auto",
                    help="'lat,lon' or 'auto' (bbox centre) for --local; default auto")
    ap.add_argument("--level-height", type=float, default=3.0,
                    help="metres per level when only building:levels is tagged (default 3.0, rule of thumb)")
    ap.add_argument("--default-levels", type=float, default=3.0,
                    help="levels assumed when no height info exists (default 3, rule of thumb)")
    ap.add_argument("--hide-outlines-with-parts", action="store_true",
                    help="drop building outlines that contain building:part areas (Simple 3D Buildings rule)")
    a = ap.parse_args(argv)

    if a.level_height <= 0 or a.default_levels <= 0:
        ap.error("--level-height and --default-levels must be > 0")
    try:
        with open(a.input, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print("ERROR: cannot read %s: %s" % (a.input, exc), file=sys.stderr)
        return 2
    if not isinstance(data, dict) or "elements" not in data:
        remark = data.get("remark") if isinstance(data, dict) else None
        print("ERROR: not an Overpass JSON response (no 'elements')%s"
              % (": " + remark if remark else ""), file=sys.stderr)
        return 2
    if data.get("remark"):
        print("WARN: Overpass remark (result may be incomplete): %s" % data["remark"],
              file=sys.stderr)

    fc, stats = convert(data, a.level_height, a.default_levels, a.hide_outlines_with_parts)

    local = None
    if fc["features"]:
        if a.origin == "auto":
            lat0, lon0 = bbox_center(fc)
        else:
            try:
                lat0, lon0 = (float(x) for x in a.origin.split(","))
            except ValueError:
                ap.error("--origin must be 'lat,lon' or 'auto'")
        local = to_local(fc, lat0, lon0)
        add_areas_to_lonlat(fc, local)

    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(fc, fh, ensure_ascii=False)
    if a.local:
        if local is None:
            print("WARN: no features, local file not written", file=sys.stderr)
        else:
            with open(a.local, "w", encoding="utf-8") as fh:
                json.dump(local, fh, ensure_ascii=False)
    if not a.out and not a.local:
        json.dump(fc, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")

    print("buildings: %(features)d  (height tag %(height)d, levels %(levels)d, "
          "default %(default)d)  skipped: unclosed %(skipped_unclosed)d, "
          "missing geometry %(skipped_missing_geometry)d, degenerate %(skipped_degenerate)d, "
          "hidden outlines %(hidden_outlines)d" % stats, file=sys.stderr)
    if local is not None:
        print("origin lat,lon = %.7f,%.7f" % (local["origin"]["lat"], local["origin"]["lon"]),
              file=sys.stderr)
    if fc["features"] and stats["default"] / max(1, stats["features"]) > 0.5:
        print("NOTE: more than half the heights are defaults (%g m); say so to the user."
              % (a.default_levels * a.level_height), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
