"""Tests for osm_to_geojson.py and overpass_query.py (stdlib unittest, offline).

Run:  python -m unittest discover -s scripts/tests -v   (from the skill folder)
"""
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
FIX = os.path.join(HERE, "fixtures")
sys.path.insert(0, SCRIPTS)

import osm_to_geojson as og  # noqa: E402
import overpass_query as oq  # noqa: E402


def load(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return json.load(fh)


class ParseTests(unittest.TestCase):
    def test_lengths(self):
        self.assertEqual(og.parse_length_m("12"), 12.0)
        self.assertEqual(og.parse_length_m("12 m"), 12.0)
        self.assertEqual(og.parse_length_m("7,5"), 7.5)
        self.assertAlmostEqual(og.parse_length_m("40 ft"), 12.192, places=3)
        self.assertAlmostEqual(og.parse_length_m("30'"), 9.144, places=3)
        self.assertAlmostEqual(og.parse_length_m("10'6\""), 3.2, places=2)
        for bad in (None, "", "tall", "-3", "12;14"):
            self.assertIsNone(og.parse_length_m(bad), bad)

    def test_height_rules(self):
        h = og.building_height({"height": "20", "building:levels": "3"}, 3.0, 3.0)
        self.assertEqual((h["height"], h["height_source"], h["levels"]), (20.0, "height", 3.0))
        h = og.building_height({"building:levels": "4", "roof:levels": "1"}, 3.0, 3.0)
        self.assertEqual((h["height"], h["height_source"]), (15.0, "levels"))
        h = og.building_height({"building:levels": "4", "roof:height": "2"}, 3.0, 3.0)
        self.assertEqual(h["height"], 14.0)
        h = og.building_height({}, 3.0, 3.0)
        self.assertEqual((h["height"], h["height_source"], h["levels"]), (9.0, "default", 3.0))
        h = og.building_height({}, 3.5, 2.0)
        self.assertEqual(h["height"], 7.0)
        h = og.building_height({"building:levels": "6", "building:min_level": "2"}, 3.0, 3.0)
        self.assertEqual((h["min_height"], h["levels"]), (6.0, 4.0))
        h = og.building_height({"height": "5", "min_height": "8"}, 3.0, 3.0)
        self.assertEqual(h["min_height"], 0.0)  # inverted solid rejected


class ConvertGeomStyle(unittest.TestCase):
    def setUp(self):
        self.fc, self.stats = og.convert(load("overpass_geom.json"))
        self.by = {f["id"]: f for f in self.fc["features"]}

    def test_counts(self):
        # ways 1,2,3,4,6,7 + relation 10; way 5 unclosed; 8 building=no; 9 highway
        self.assertEqual(sorted(self.by), sorted(
            ["way/1", "way/2", "way/3", "way/4", "way/6", "way/7", "relation/10"]))
        self.assertEqual(self.stats["skipped_unclosed"], 1)
        self.assertEqual(self.stats["default"], 1)

    def test_heights(self):
        p = lambda i: self.by[i]["properties"]  # noqa: E731
        self.assertEqual(p("way/1")["height"], 12.0)
        self.assertEqual(p("way/2")["height"], 15.0)
        self.assertEqual(p("way/3")["height_source"], "default")
        self.assertAlmostEqual(p("way/4")["height"], 9.14, places=2)
        self.assertEqual((p("way/7")["height"], p("way/7")["min_height"]), (40.0, 10.0))
        self.assertTrue(p("way/7")["is_part"])

    def test_orientation_ccw_outer(self):
        for f in self.fc["features"]:
            g = f["geometry"]
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for poly in polys:
                self.assertGreater(og.signed_area(poly[0]), 0, f["id"])
                self.assertEqual(poly[0][0], poly[0][-1])
                for hole in poly[1:]:
                    self.assertLess(og.signed_area(hole), 0, f["id"])

    def test_multipolygon_joined_with_hole(self):
        g = self.by["relation/10"]["geometry"]
        self.assertEqual(g["type"], "Polygon")
        self.assertEqual(len(g["coordinates"]), 2)
        self.assertEqual(len(g["coordinates"][0]), 5)  # 4 corners + closing point

    def test_parts_rule(self):
        self.assertTrue(self.by["way/6"]["properties"]["has_parts"])
        self.assertFalse(self.by["way/1"]["properties"]["has_parts"])
        fc2, st = og.convert(load("overpass_geom.json"), hide_outlines_with_parts=True)
        ids = {f["id"] for f in fc2["features"]}
        self.assertNotIn("way/6", ids)
        self.assertIn("way/7", ids)
        self.assertEqual(st["hidden_outlines"], 1)


class ConvertNodesStyle(unittest.TestCase):
    def test_node_refs_and_missing_node(self):
        fc, st = og.convert(load("overpass_nodes.json"))
        self.assertEqual([f["id"] for f in fc["features"]], ["way/21"])
        self.assertEqual(fc["features"][0]["properties"]["height"], 7.5)
        self.assertEqual(st["skipped_missing_geometry"], 1)


class LocalMetres(unittest.TestCase):
    def test_enu_against_meridian_arc(self):
        lat0 = 52.5
        f = og.EnuFrame(lat0, 13.0)
        e, n, u = f.to_enu(lat0 + 0.001, 13.0)
        # meridional radius of curvature M = a(1-e2)/(1-e2 sin^2)^1.5
        s = math.sin(math.radians(lat0))
        M = og.WGS84_A * (1 - og.WGS84_E2) / (1 - og.WGS84_E2 * s * s) ** 1.5
        self.assertAlmostEqual(n, math.radians(0.001) * M, delta=0.01)
        self.assertAlmostEqual(e, 0.0, delta=1e-6)
        e, n, u = f.to_enu(lat0, 13.001)
        N = og.WGS84_A / math.sqrt(1 - og.WGS84_E2 * s * s)
        self.assertAlmostEqual(e, math.radians(0.001) * N * math.cos(math.radians(lat0)), delta=0.01)

    def test_areas_and_origin(self):
        fc, _ = og.convert(load("overpass_geom.json"))
        local = og.to_local(fc, 52.5160, 13.3770)
        by = {f["id"]: f["properties"] for f in local["features"]}
        # fixture used approximate degree-per-metre factors; allow 1 %
        self.assertAlmostEqual(by["way/1"]["footprint_m2"], 400, delta=4)
        self.assertAlmostEqual(by["relation/10"]["footprint_m2"], 2500 - 400, delta=25)
        self.assertAlmostEqual(by["way/2"]["floor_area_m2"], by["way/2"]["footprint_m2"] * 4, delta=0.5)
        w1 = [f for f in local["features"] if f["id"] == "way/1"][0]
        first = w1["geometry"]["coordinates"][0][0]
        self.assertLess(abs(first[0]) + abs(first[1]), 1.0)  # way/1 starts at the origin


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(SCRIPTS, "osm_to_geojson.py"), *args],
                              capture_output=True, text=True)

    def test_cli_writes_files(self):
        with tempfile.TemporaryDirectory() as d:
            out, loc = os.path.join(d, "b.geojson"), os.path.join(d, "l.json")
            r = self.run_cli(os.path.join(FIX, "overpass_geom.json"), "--out", out, "--local", loc)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("buildings: 7", r.stderr)
            with open(out, encoding="utf-8") as fh:
                fc = json.load(fh)
            self.assertIn("OpenStreetMap", fc["attribution"])
            self.assertIn("footprint_m2", fc["features"][0]["properties"])
            with open(loc, encoding="utf-8") as fh:
                self.assertIn("origin", json.load(fh))

    def test_cli_rejects_non_overpass(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.json")
            with open(p, "w") as fh:
                json.dump({"remark": "runtime error: Query timed out"}, fh)
            r = self.run_cli(p)
            self.assertEqual(r.returncode, 2)
            self.assertIn("timed out", r.stderr)


class OverpassQuery(unittest.TestCase):
    def call(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = oq.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_prints_query_without_network(self):
        code, out, _ = self.call("--center", "52.5163,13.3777", "--radius", "300")
        self.assertEqual(code, 0)
        self.assertIn("[out:json][timeout:90];", out)
        self.assertIn('way["building"](', out)
        self.assertIn("out geom;", out)
        self.assertIn("curl -sS -A", out)
        self.assertIn("OpenStreetMap", out)

    def test_bbox_order_and_area(self):
        s, w, n, e = oq.bbox_from_center(52.5, 13.4, 500)
        self.assertLess(s, n)
        self.assertLess(w, e)
        self.assertAlmostEqual(oq.bbox_area_km2(s, w, n, e), 1.0, delta=0.01)

    def test_large_area_refused(self):
        code, _, err = self.call("--bbox", "52.0,13.0,52.5,13.8")
        self.assertEqual(code, 2)
        self.assertIn("pbf", err)

    def test_fetch_needs_real_user_agent(self):
        code, _, err = self.call("--center", "52.5,13.4", "--fetch")
        self.assertEqual(code, 2)
        self.assertIn("user-agent", err)


if __name__ == "__main__":
    unittest.main()
