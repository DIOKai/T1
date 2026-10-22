#!/usr/bin/env python3
"""Print a polite Overpass QL query (and a curl command) for a small area.

Default: NO network. It only prints. Run the printed curl yourself, or pass
--fetch (only after the user agreed) to download once with a real User-Agent.
Python 3.8+ standard library only.

Overpass usage policy (overpass-api.de, read 2026-10-22):
  light use < 10,000 queries/day and < 1 GB/day, shared by ALL users of an app;
  identify yourself (User-Agent), no parallel scripts, cache results,
  on HTTP 429/406 wait before retrying, commercial use -> own/paid server.
  https://wiki.openstreetmap.org/wiki/Overpass_API
Never call Overpass from a game client. Fetch at build time, save, convert.

Examples:
  python overpass_query.py --center 52.5163,13.3777 --radius 400
  python overpass_query.py --bbox 48.853,2.345,48.858,2.352 --what landuse
  python overpass_query.py --center 52.5163,13.3777 --radius 400 --fetch \
      --user-agent "CapitalRift-dev/0.1 (you@example.com)" --save berlin.json
"""
from __future__ import annotations

import argparse
import math
import shlex
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_ENDPOINT = "https://overpass-api.de/api/interpreter"
MAX_AREA_KM2 = 4.0  # rule of thumb for a polite single request of buildings
EARTH_R = 6371008.8

QUERIES = {
    # building outlines + parts, with geometry inline (osm_to_geojson.py reads this)
    "buildings": """(
  way["building"]({b});
  relation["building"]["type"="multipolygon"]({b});
  way["building:part"]({b});
  relation["building:part"]["type"="multipolygon"]({b});
);
out geom;""",
    # land use hints for gameplay zoning (industrial, quarry, farmland ...)
    "landuse": """(
  way["landuse"]({b});
  relation["landuse"]["type"="multipolygon"]({b});
);
out geom;""",
    # roads for logistics / trucks
    "roads": """(
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|unclassified|service)$"]({b});
);
out geom;""",
}


def bbox_from_center(lat: float, lon: float, radius_m: float):
    dlat = math.degrees(radius_m / EARTH_R)
    dlon = math.degrees(radius_m / (EARTH_R * math.cos(math.radians(lat))))
    return lat - dlat, lon - dlon, lat + dlat, lon + dlon


def bbox_area_km2(s: float, w: float, n: float, e: float) -> float:
    h = math.radians(n - s) * EARTH_R
    wdt = math.radians(e - w) * EARTH_R * math.cos(math.radians((s + n) / 2))
    return abs(h * wdt) / 1e6


def build_query(what: str, bbox, timeout: int) -> str:
    s, w, n, e = bbox
    b = "%.6f,%.6f,%.6f,%.6f" % (s, w, n, e)  # Overpass order: south,west,north,east
    return "[out:json][timeout:%d];\n%s\n" % (timeout, QUERIES[what].format(b=b))


def parse_floats(text: str, count: int, name: str):
    try:
        vals = [float(x) for x in text.split(",")]
    except ValueError:
        raise SystemExit("ERROR: %s must be %d comma-separated numbers" % (name, count))
    if len(vals) != count:
        raise SystemExit("ERROR: %s must be %d comma-separated numbers" % (name, count))
    return vals


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--bbox", help="south,west,north,east in degrees")
    g.add_argument("--center", help="lat,lon (use with --radius)")
    ap.add_argument("--radius", type=float, default=300.0, help="metres around --center (default 300)")
    ap.add_argument("--what", choices=sorted(QUERIES), default="buildings")
    ap.add_argument("--timeout", type=int, default=90, help="Overpass [timeout:] seconds (default 90)")
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--save", default="overpass.json", help="file name used in the curl command / --fetch")
    ap.add_argument("--allow-large", action="store_true",
                    help="allow areas above %.0f km2 (split into tiles instead when you can)" % MAX_AREA_KM2)
    ap.add_argument("--fetch", action="store_true",
                    help="actually download once (needs --user-agent; only after the user agreed)")
    ap.add_argument("--user-agent", help="identify your app + contact, e.g. 'MyGame-dev/0.1 (me@example.com)'")
    a = ap.parse_args(argv)

    if a.bbox:
        s, w, n, e = parse_floats(a.bbox, 4, "--bbox")
    else:
        lat, lon = parse_floats(a.center, 2, "--center")
        if a.radius <= 0:
            ap.error("--radius must be > 0")
        s, w, n, e = bbox_from_center(lat, lon, a.radius)
    if not (-90 <= s < n <= 90 and -180 <= w < e <= 180):
        ap.error("bbox must be south<north and west<east (south,west,north,east); "
                 "boxes crossing the antimeridian are not supported")
    area = bbox_area_km2(s, w, n, e)
    if area > MAX_AREA_KM2 and not a.allow_large:
        print("ERROR: area %.2f km2 is above %.0f km2. Split it into tiles, or for whole "
              "cities/countries use a .osm.pbf extract instead of Overpass. "
              "--allow-large overrides." % (area, MAX_AREA_KM2), file=sys.stderr)
        return 2

    q = build_query(a.what, (s, w, n, e), a.timeout)
    ua = a.user_agent or "YourGame-dev/0.1 (your-email@example.com)"
    curl = ("curl -sS -A %s --data-urlencode %s -o %s %s"
            % (shlex.quote(ua), shlex.quote("data=" + q), shlex.quote(a.save), a.endpoint))

    print("# area: %.3f km2  bbox(s,w,n,e): %.6f,%.6f,%.6f,%.6f" % (area, s, w, n, e))
    print("# Overpass QL (paste into https://overpass-turbo.eu to preview first):")
    print(q)
    print("# One polite download (POSIX shell / Git Bash quoting; run once, keep the file, do not loop):")
    print(curl)
    print("# Then: python osm_to_geojson.py %s --out buildings.geojson --local buildings_local.json"
          % a.save)
    print("# Data (c) OpenStreetMap contributors, ODbL. Show this attribution in the game.")

    if not a.fetch:
        return 0
    if (not a.user_agent or "example.com" in a.user_agent
            or ("@" not in a.user_agent and "http" not in a.user_agent)):
        print("ERROR: --fetch needs --user-agent with your app name and a real contact "
              "(email or URL).", file=sys.stderr)
        return 2
    body = urllib.parse.urlencode({"data": q}).encode("utf-8")
    req = urllib.request.Request(a.endpoint, data=body, headers={
        "User-Agent": a.user_agent,
        "Content-Type": "application/x-www-form-urlencoded",
    })
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=a.timeout + 30) as resp:
            payload = resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (429, 406, 504):
            print("ERROR: HTTP %d from Overpass (busy or rate limited). Wait at least "
                  "30 s (better: minutes) before ONE retry; do not loop." % exc.code, file=sys.stderr)
        else:
            print("ERROR: HTTP %d: %s" % (exc.code, exc.reason), file=sys.stderr)
        return 3
    except urllib.error.URLError as exc:
        print("ERROR: network: %s" % exc.reason, file=sys.stderr)
        return 3
    with open(a.save, "wb") as fh:
        fh.write(payload)
    print("# saved %s (%d bytes, %.1f s)" % (a.save, len(payload), time.time() - t0), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
