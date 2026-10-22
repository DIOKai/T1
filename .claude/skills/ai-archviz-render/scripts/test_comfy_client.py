"""Tests comfy_client.py against a tiny stub of the ComfyUI routes (no real ComfyUI needed).

  python test_comfy_client.py
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import comfy_client as cc  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\nstub-image"


class Stub(BaseHTTPRequestHandler):
    state = {}

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        s = self.state
        if self.path == "/object_info":
            return self._json({k: {} for k in ("LoadImage", "KSampler", "CLIPTextEncode", "SaveImage",
                                               "CheckpointLoaderSimple", "ControlNetLoader",
                                               "ControlNetApplyAdvanced", "VAEEncode", "VAEDecode", "Note")})
        if self.path.startswith("/history/"):
            pid = self.path.split("/")[-1]
            s["polls"] = s.get("polls", 0) + 1
            if s["polls"] < 2:
                return self._json({})  # not finished yet
            return self._json({pid: {"status": {"status_str": "success", "completed": True},
                                     "outputs": {"11": {"images": [
                                         {"filename": "air_render_00001_.png", "subfolder": "", "type": "output"},
                                         {"filename": "preview.png", "subfolder": "", "type": "temp"}]}}}})
        if self.path.startswith("/view?"):
            s["view"] = self.path
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(PNG)))
            self.end_headers()
            return self.wfile.write(PNG)
        self._json({"error": "not found"}, 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        s = self.state
        if self.path == "/upload/image":
            assert self.headers["Content-Type"].startswith("multipart/form-data; boundary=")
            name = body.split(b'filename="')[1].split(b'"')[0].decode()
            s.setdefault("uploads", []).append((name, PNG in body))
            return self._json({"name": "up_" + name, "subfolder": "", "type": "input"})
        if self.path == "/prompt":
            s["prompt"] = json.loads(body)
            return self._json({"prompt_id": "abc12345-stub", "number": 1, "node_errors": {}})
        self._json({"error": "not found"}, 404)


class ComfyClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
        cls.host = "http://127.0.0.1:%d" % cls.srv.server_address[1]
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.tmp = tempfile.mkdtemp(prefix="comfy_test_")
        for n in ("beauty.png", "depth.png"):
            with open(os.path.join(cls.tmp, n), "wb") as f:
                f.write(PNG)
        cls.wf = os.path.join(HERE, "..", "assets", "example_workflow_api.json")

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        Stub.state.clear()

    def test_refuses_remote_hosts(self):
        for h in ("http://192.168.1.5:8188", "https://comfy.example.com", "http://10.0.0.1",
                  "http://127.0.0.1.evil.com:8188", "ftp://127.0.0.1"):
            with self.assertRaises(cc.ComfyError, msg=h):
                cc.check_local(h)
        for h in ("http://127.0.0.1:8188", "localhost:8188", "http://[::1]:8188", "http://127.0.0.2:8188"):
            cc.check_local(h)

    def test_health(self):
        with open(self.wf, encoding="utf-8") as f:
            wf = json.load(f)
        res = cc.Client(self.host).health(wf)
        self.assertGreater(res["node_types"], 5)
        self.assertEqual(res["missing_node_types"], [])

    def test_fill_types_and_leftovers(self):
        wf = {"9": {"inputs": {"seed": "{{SEED}}", "text": "a {{PROMPT}} b"}}}
        out = cc.fill(wf, {"SEED": "42", "PROMPT": "villa"})
        self.assertEqual(out["9"]["inputs"]["seed"], 42)
        self.assertEqual(out["9"]["inputs"]["text"], "a villa b")
        self.assertEqual(cc.leftovers(cc.fill(wf, {"SEED": "1"})), {"PROMPT"})

    def test_missing_placeholder_blocks_queue(self):
        out = os.path.join(self.tmp, "o1")
        rc = cc.main(["run", "--host", self.host, "--workflow", self.wf,
                      "--upload", "IMAGE=" + os.path.join(self.tmp, "beauty.png"), "--out", out])
        self.assertEqual(rc, 2)
        self.assertNotIn("prompt", Stub.state)
        self.assertNotIn("uploads", Stub.state)  # nothing uploaded when the workflow is incomplete

    def test_full_run(self):
        out = os.path.join(self.tmp, "o2")
        rc = cc.main(["run", "--host", self.host, "--workflow", self.wf,
                      "--upload", "IMAGE=" + os.path.join(self.tmp, "beauty.png"),
                      "--upload", "DEPTH=" + os.path.join(self.tmp, "depth.png"),
                      "--set", "SEED=421337", "--set", "PROMPT=tropical villa",
                      "--set", "NEGATIVE=blurry", "--out", out])
        self.assertEqual(rc, 0)
        s = Stub.state
        self.assertEqual([u[0] for u in s["uploads"]], ["beauty.png", "depth.png"])
        self.assertTrue(all(u[1] for u in s["uploads"]))
        p = s["prompt"]["prompt"]
        self.assertEqual(p["9"]["inputs"]["seed"], 421337)
        self.assertEqual(p["4"]["inputs"]["image"], "up_beauty.png")
        self.assertEqual(p["5"]["inputs"]["image"], "up_depth.png")
        self.assertTrue(p["2"]["inputs"]["text"].startswith("tropical villa"))
        self.assertGreaterEqual(s["polls"], 2)
        files = os.listdir(out)
        self.assertIn("air_render_00001_.png", files)
        self.assertNotIn("preview.png", files)  # temp previews are skipped
        with open(os.path.join(out, "air_render_00001_.png"), "rb") as f:
            self.assertEqual(f.read(), PNG)
        self.assertTrue(any(f.startswith("run_") for f in files))

    def test_dry_run_does_not_contact_prompt(self):
        rc = cc.main(["run", "--host", self.host, "--workflow", self.wf, "--dry-run",
                      "--upload", "IMAGE=" + os.path.join(self.tmp, "beauty.png"),
                      "--upload", "DEPTH=" + os.path.join(self.tmp, "depth.png"),
                      "--set", "SEED=1", "--set", "PROMPT=x", "--set", "NEGATIVE=y"])
        self.assertEqual(rc, 0)
        self.assertNotIn("prompt", Stub.state)
        self.assertNotIn("uploads", Stub.state)

    def test_unreachable(self):
        with self.assertRaises(cc.ComfyError):
            cc.Client("http://127.0.0.1:9", timeout=2).object_info()


if __name__ == "__main__":
    unittest.main(verbosity=2)
