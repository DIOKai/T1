"""Synthetic fixtures only; no values here are Malaysian design requirements."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audit_context", ROOT / "scripts" / "audit_context.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def fixture():
    return {
        "project": {"name": "Synthetic test", "country": "MY", "state": "Test state", "authority": "Test authority"},
        "scope": ["road"],
        "drawing": {"release": "Test release", "build": "Test build", "template": "Synthetic.dwt", "linear_unit": "m"},
        "survey": {"horizontal_reference": "Synthetic local grid", "vertical_reference": "Synthetic datum", "control_evidence": "Test control file"},
        "criteria": [{"id": "test-only", "scope": "road", "value": 1.0, "unit": "m", "applicability": "Synthetic fixture only", "source": "Test source, not a standard", "edition": "test", "clause": "test clause", "evidence_status": "reviewed", "basis_jurisdiction": "MY"}],
    }


class AuditTests(unittest.TestCase):
    def test_complete_is_never_engineering_approval(self):
        result = MOD.audit(fixture())
        self.assertEqual(result["status"], "metadata-complete")
        self.assertFalse(result["engineering_compliance_checked"])

    def test_missing_reference_evidence(self):
        data = fixture()
        data["survey"]["vertical_reference"] = None
        data["criteria"][0]["clause"] = "TBD"
        result = MOD.audit(data)
        self.assertEqual(len(result["issues"]), 2)

    def test_european_default_rejected(self):
        data = fixture()
        data["criteria"][0]["basis_jurisdiction"] = "EU"
        self.assertTrue(MOD.audit(data)["issues"])

    def test_external_reference_requires_local_adoption(self):
        data = fixture()
        data["criteria"][0]["external_reference"] = "Foreign document"
        self.assertTrue(MOD.audit(data)["issues"])
        data["criteria"][0]["malaysian_adoption_evidence"] = "Synthetic project adoption record"
        self.assertEqual(MOD.audit(data)["issues"], [])

    def test_non_numeric_boolean_and_nonfinite_values(self):
        for value in (True, False, "1", None, float("inf"), float("nan")):
            with self.subTest(value=value):
                data = fixture()
                data["criteria"][0]["value"] = value
                self.assertTrue(MOD.audit(data)["issues"])

    def test_scope_coverage_and_duplicates(self):
        data = fixture()
        data["scope"] += ["drainage", "road"]
        data["criteria"].append(copy.deepcopy(data["criteria"][0]))
        self.assertEqual(len(MOD.audit(data)["issues"]), 3)

    def test_bad_types_return_issues_not_traceback(self):
        for data in ([], None, {"scope": [{}, []], "criteria": [[], {"scope": {}, "id": []}]}):
            with self.subTest(data=data):
                self.assertTrue(MOD.audit(data)["issues"])

    def test_wrong_country_units_or_unreviewed_evidence(self):
        data = fixture()
        data["project"]["country"] = "GB"
        data["drawing"]["linear_unit"] = "mm"
        data["criteria"][0]["evidence_status"] = "unreviewed"
        self.assertEqual(len(MOD.audit(data)["issues"]), 3)

    def test_example_is_deliberately_incomplete(self):
        data = json.loads((ROOT / "assets" / "project-context.example.json").read_text(encoding="utf-8"))
        self.assertEqual(MOD.audit(data)["status"], "incomplete")

    def test_survey_only_does_not_require_road_criteria(self):
        data = fixture()
        data["scope"] = ["survey"]
        data["criteria"] = []
        self.assertEqual(MOD.audit(data)["issues"], [])

    def run_file(self, contents):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "context.json"
            path.write_bytes(contents)
            before = path.read_bytes()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = MOD.main([str(path)])
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(directory).iterdir()), [path])
            return code, json.loads(output.getvalue())

    def test_cli_bom_and_read_only(self):
        code, result = self.run_file(json.dumps(fixture()).encode("utf-8-sig"))
        self.assertEqual(code, 0)
        self.assertFalse(result["engineering_compliance_checked"])

    def test_cli_rejects_duplicate_keys_bad_json_nonfinite(self):
        for content in (b'{"project":1,"project":2}', b'{broken', b'{"value":NaN}', b'{"value":Infinity}'):
            with self.subTest(content=content):
                code, result = self.run_file(content)
                self.assertEqual(code, 2)
                self.assertEqual(result["status"], "invalid-input")

    def test_cli_incomplete_exit_code(self):
        code, result = self.run_file(b'{}')
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "incomplete")

    def test_cli_missing_file_is_json_error(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = MOD.main([str(Path(directory) / "missing.json")])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.getvalue())["status"], "invalid-input")


if __name__ == "__main__":
    unittest.main()
