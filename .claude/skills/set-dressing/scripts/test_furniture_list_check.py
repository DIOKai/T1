"""Tests for furniture_list_check.py (stdlib unittest). Run: python test_furniture_list_check.py"""

import csv
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import furniture_list_check as flc  # noqa: E402

GOOD = {"id": "1", "room": "Living", "name": "Sofa 3 lugares", "store": "Mercado Livre",
        "url": "https://example.com/sofa", "price": "1.299,90", "currency": "BRL", "qty": "1",
        "w_cm": "210", "d_cm": "90", "h_cm": "85", "model_source": "Poly Haven",
        "model_licence": "CC0", "substitute": "yes", "substitute_reason": "similar shape, no official model"}


class NumTests(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(flc.num("1.299,90"), 1299.90)
        self.assertEqual(flc.num("1,299.90"), 1299.90)
        self.assertEqual(flc.num("R$ 799"), 799.0)
        self.assertEqual(flc.num("12,5"), 12.5)
        self.assertEqual(flc.num(42), 42.0)
        self.assertIsNone(flc.num("abc"))
        self.assertIsNone(flc.num(""))


class CheckTests(unittest.TestCase):
    def test_good_item_no_errors(self):
        e, w, t, rows = flc.check([GOOD], {"Living": {"w_cm": 420, "d_cm": 360, "h_cm": 260,
                                                      "door_w_cm": 80, "door_h_cm": 200}})
        self.assertEqual(e, [])
        self.assertAlmostEqual(t["BRL"], 1299.90)
        self.assertEqual(rows[0]["substitute"], "yes")

    def test_missing_and_bad_values(self):
        bad = dict(GOOD, w_cm="", price="free", qty="0", url="ftp://x")
        e, w, t, _ = flc.check([bad])
        text = "\n".join(e)
        self.assertIn("missing w_cm", text)
        self.assertIn("price must be a number", text)
        self.assertIn("qty must be", text)
        self.assertIn("url must start", text)

    def test_room_ceiling_door(self):
        big = dict(GOOD, w_cm="500", d_cm="100", h_cm="270")
        e, w, _, _ = flc.check([big], None, {"w_cm": 420, "d_cm": 360, "h_cm": 260,
                                              "door_w_cm": 80, "door_h_cm": 200})
        self.assertTrue(any("larger than room" in x for x in e))
        self.assertTrue(any("above ceiling" in x for x in e))
        self.assertTrue(any("door" in x for x in w))

    def test_rotated_footprint_fits(self):
        it = dict(GOOD, w_cm="350", d_cm="200")
        e, _, _, _ = flc.check([it], None, {"w_cm": 250, "d_cm": 400})
        self.assertEqual(e, [])

    def test_licence_warnings(self):
        e, w, _, _ = flc.check([dict(GOOD, model_licence=""), dict(GOOD, model_licence="CC BY-NC 4.0"),
                                dict(GOOD, model_licence="CC-BY 4.0")])
        text = "\n".join(w)
        self.assertIn("no 3D model licence", text)
        self.assertIn("restricts commercial", text)
        self.assertIn("credit the author", text)

    def test_substitute_needs_reason(self):
        _, w, _, _ = flc.check([dict(GOOD, substitute_reason="")])
        self.assertTrue(any("no substitute_reason" in x for x in w))

    def test_totals_per_currency_and_qty(self):
        items = [dict(GOOD, price="100", qty="3", currency="BRL"), dict(GOOD, price="50", currency="usd")]
        _, _, t, _ = flc.check(items)
        self.assertEqual(t, {"BRL": 300.0, "USD": 50.0})


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = flc.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_csv_json_export(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "f.csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                wr = csv.DictWriter(f, fieldnames=list(GOOD))
                wr.writeheader(); wr.writerow(GOOD)
            exp = os.path.join(d, "shop.csv")
            code, out, _ = self.run_cli(p, "--room", "420x360", "--ceiling", "260",
                                        "--door-width", "80", "--door-height", "200", "--export", exp)
            self.assertEqual(code, 0, out)
            self.assertIn("TOTAL BRL 1,299.90", out)
            with open(exp, encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]["line_total"], "1299.90")
            code, _, err = self.run_cli(p, "--export", exp)          # no overwrite without --force
            self.assertEqual(code, 2)
            j = os.path.join(d, "f.json")
            with open(j, "w", encoding="utf-8") as f:
                json.dump({"items": [dict(GOOD, w_cm=0)]}, f)
            code, out, _ = self.run_cli(j)
            self.assertEqual(code, 1)
            self.assertIn("w_cm must be a number > 0", out)

    def test_bad_input(self):
        code, _, err = self.run_cli("does_not_exist.csv")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
