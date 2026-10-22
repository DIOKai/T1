#!/usr/bin/env python3
"""Drive a LOCAL ComfyUI from the command line (Python standard library only).

Refuses any host that isn't localhost / 127.0.0.1 / ::1, so project images never leave the machine.

  python comfy_client.py health [--host http://127.0.0.1:8188] [--workflow wf_api.json]
  python comfy_client.py run --workflow wf_api.json \
      --upload IMAGE=passes/beauty.png --upload DEPTH=passes/depth.png \
      --set SEED=421337 --set PROMPT="modern villa, golden hour" --out renders/cam01 [--dry-run]

The workflow must be ComfyUI's API format (File -> Export (API)). Put placeholders such as
"{{IMAGE}}", "{{DEPTH}}", "{{SEED}}", "{{PROMPT}}" where values should go:
  - a string that is exactly "{{KEY}}" is replaced by the value; whole integers/floats become numbers
    (so "seed": "{{SEED}}" becomes "seed": 421337);
  - "{{KEY}}" inside a longer string is replaced as text.
--upload KEY=path uploads the file first and substitutes the name ComfyUI gives it.
Any {{...}} left over is an error; nothing is queued.
"""
import argparse
import ipaddress
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

DEFAULT_HOST = "http://127.0.0.1:8188"
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
NUMBER = re.compile(r"^-?\d+(\.\d+)?$")


class ComfyError(RuntimeError):
    pass


def check_local(host):
    """Return a normalised base URL, or raise if the host is not this machine."""
    u = urllib.parse.urlparse(host if "://" in host else "http://" + host)
    name = (u.hostname or "").lower()
    ok = name == "localhost"
    if not ok:
        try:
            ok = ipaddress.ip_address(name).is_loopback
        except ValueError:
            ok = False
    if u.scheme not in ("http", "https") or not ok:
        raise ComfyError("refusing non-local ComfyUI host %r: this client only talks to "
                         "localhost / 127.0.0.1 / ::1" % host)
    return "%s://%s" % (u.scheme, u.netloc)


class Client:
    def __init__(self, host=DEFAULT_HOST, timeout=30):
        self.base = check_local(host)
        self.timeout = timeout
        self.client_id = uuid.uuid4().hex

    def _req(self, method, path, body=None, headers=None, raw=False):
        req = urllib.request.Request(self.base + path, data=body, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                data = r.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:2000]
            raise ComfyError("%s %s -> HTTP %s: %s" % (method, path, e.code, detail))
        except urllib.error.URLError as e:
            raise ComfyError("cannot reach ComfyUI at %s (%s). Is it running?" % (self.base, e.reason))
        return data if raw else json.loads(data.decode("utf-8") or "null")

    def object_info(self):
        return self._req("GET", "/object_info")

    def health(self, workflow=None):
        info = self.object_info()
        missing = []
        if workflow:
            missing = sorted({n.get("class_type") for n in workflow.values()
                              if isinstance(n, dict) and n.get("class_type") not in info})
        return {"host": self.base, "node_types": len(info), "missing_node_types": missing}

    def upload_image(self, path, overwrite=True):
        boundary = "----air" + uuid.uuid4().hex
        fname = os.path.basename(path)
        ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            content = f.read()
        parts = [
            b"--%s\r\nContent-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\n"
            b"Content-Type: %s\r\n\r\n" % (boundary.encode(), fname.encode("utf-8"), ctype.encode()),
            content, b"\r\n",
            b"--%s\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\n%s\r\n"
            % (boundary.encode(), b"true" if overwrite else b"false"),
            b"--%s--\r\n" % boundary.encode(),
        ]
        res = self._req("POST", "/upload/image", b"".join(parts),
                        {"Content-Type": "multipart/form-data; boundary=" + boundary})
        name = res.get("name")
        if res.get("subfolder"):
            name = res["subfolder"] + "/" + name
        return name

    def queue(self, workflow):
        body = json.dumps({"prompt": workflow, "client_id": self.client_id}).encode("utf-8")
        res = self._req("POST", "/prompt", body, {"Content-Type": "application/json"})
        if res.get("error") or res.get("node_errors"):
            raise ComfyError("ComfyUI rejected the workflow: %s" %
                             json.dumps({"error": res.get("error"), "node_errors": res.get("node_errors")})[:3000])
        return res["prompt_id"]

    def wait(self, prompt_id, timeout=1800, interval=1.0):
        end = time.time() + timeout
        while time.time() < end:
            hist = self._req("GET", "/history/" + urllib.parse.quote(prompt_id))
            entry = (hist or {}).get(prompt_id)
            if entry:
                status = entry.get("status") or {}
                if status.get("status_str") == "error":
                    raise ComfyError("generation failed: %s" % json.dumps(status.get("messages"))[:3000])
                if status.get("completed", True) and entry.get("outputs") is not None:
                    return entry
            time.sleep(interval)
        raise ComfyError("timed out after %ss waiting for %s" % (timeout, prompt_id))

    def download_outputs(self, entry, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        saved = []
        for node_id, out in (entry.get("outputs") or {}).items():
            for kind in ("images", "gifs", "videos"):
                for item in out.get(kind, []) or []:
                    if item.get("type", "output") != "output":
                        continue  # skip previews/temp
                    q = urllib.parse.urlencode({"filename": item["filename"],
                                                "subfolder": item.get("subfolder", ""), "type": "output"})
                    data = self._req("GET", "/view?" + q, raw=True)
                    dest = os.path.join(out_dir, os.path.basename(item["filename"]))  # no path traversal
                    with open(dest, "wb") as f:
                        f.write(data)
                    saved.append(dest)
        return saved


def _convert(value):
    if isinstance(value, str) and NUMBER.match(value):
        return float(value) if "." in value else int(value)
    return value


def fill(obj, values):
    """Replace {{KEY}} placeholders recursively. Returns a new object."""
    if isinstance(obj, dict):
        return {k: fill(v, values) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fill(v, values) for v in obj]
    if isinstance(obj, str):
        m = PLACEHOLDER.fullmatch(obj)
        if m and m.group(1) in values:
            return _convert(values[m.group(1)])
        return PLACEHOLDER.sub(lambda mm: str(values.get(mm.group(1), mm.group(0))), obj)
    return obj


def leftovers(obj):
    found = set()
    if isinstance(obj, dict):
        for v in obj.values():
            found |= leftovers(v)
    elif isinstance(obj, list):
        for v in obj:
            found |= leftovers(v)
    elif isinstance(obj, str):
        found |= set(PLACEHOLDER.findall(obj))
    return found


def _pairs(items, what):
    out = {}
    for it in items or []:
        if "=" not in it:
            raise ComfyError("%s needs KEY=value, got %r" % (what, it))
        k, v = it.split("=", 1)
        out[k.strip().upper()] = v
    return out


def run(args):
    client = Client(args.host, timeout=args.http_timeout)
    with open(args.workflow, encoding="utf-8") as f:
        wf = json.load(f)
    if "nodes" in wf and "links" in wf:
        raise ComfyError("this is the UI save format; export with File -> Export (API) instead")
    values = _pairs(args.set, "--set")
    uploads = _pairs(args.upload, "--upload")
    for k, p in uploads.items():
        if not os.path.isfile(p):
            raise ComfyError("upload file not found: %s" % p)
    # check every placeholder has a value BEFORE uploading anything
    preview = dict(values, **{k: os.path.basename(p) for k, p in uploads.items()})
    left = leftovers(fill(wf, preview))
    if left:
        raise ComfyError("placeholders without a value: %s (use --set/--upload)" % ", ".join(sorted(left)))
    if args.dry_run:
        return {"dry_run": True, "workflow": fill(wf, preview)}
    for k, p in uploads.items():
        values[k] = client.upload_image(p)
    filled = fill(wf, values)
    pid = client.queue(filled)
    entry = client.wait(pid, timeout=args.timeout)
    saved = client.download_outputs(entry, args.out)
    meta = {"prompt_id": pid, "values": values, "files": saved, "workflow": os.path.abspath(args.workflow)}
    with open(os.path.join(args.out, "run_%s.json" % pid[:8]), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(description="Local-only ComfyUI client")
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("health")
    h.add_argument("--host", default=DEFAULT_HOST)
    h.add_argument("--workflow")
    r = sub.add_parser("run")
    r.add_argument("--host", default=DEFAULT_HOST)
    r.add_argument("--workflow", required=True)
    r.add_argument("--upload", action="append", help="KEY=path (uploaded, name substituted)")
    r.add_argument("--set", action="append", help="KEY=value")
    r.add_argument("--out", default="comfy_out")
    r.add_argument("--timeout", type=float, default=1800)
    r.add_argument("--dry-run", action="store_true")
    for p in (h, r):
        p.add_argument("--http-timeout", type=float, default=60)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "health":
            wf = None
            if args.workflow:
                with open(args.workflow, encoding="utf-8") as f:
                    wf = json.load(f)
            result = Client(args.host, timeout=args.http_timeout).health(wf)
        else:
            result = run(args)
    except ComfyError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
