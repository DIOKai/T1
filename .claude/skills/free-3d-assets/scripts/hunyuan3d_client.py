#!/usr/bin/env python3
"""Talk to a local Hunyuan3D 2.1 API server (api_server.py) from the command line.

Standard library only. Runs on the user's PC next to the server; sends nothing anywhere else.

  python hunyuan3d_client.py health [--url http://127.0.0.1:8081]
  python hunyuan3d_client.py generate photo.png --out model.glb [--texture] [--seed 1234]
         [--octree 256] [--steps 20] [--guidance 5.0] [--faces 40000] [--no-remove-bg]
         [--url ...] [--timeout 900]

Request fields and ranges match Hunyuan3D-2.1 api_models.GenerationRequest
(octree 64-512, steps 1-20, guidance 0.1-20, faces 1000-100000). The server answers
/generate with the model file (GLB), or with JSON {"text", "error_code"} and HTTP 404 on failure.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = os.environ.get("HUNYUAN3D_URL", "http://127.0.0.1:8081")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_IMAGE_BYTES = 20 * 1024 * 1024
RANGES = {
    "octree": (64, 512),
    "steps": (1, 20),
    "guidance": (0.1, 20.0),
    "faces": (1000, 100000),
    "seed": (0, 2**32 - 1),
}


def fail(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def check_range(name, value):
    lo, hi = RANGES[name]
    if not lo <= value <= hi:
        fail(f"--{name} must be between {lo} and {hi} (Hunyuan3D 2.1 limit), got {value}")


def request(url, data=None, timeout=30):
    headers = {"Accept": "*/*"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    # A local server: don't send it through a system proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return opener.open(req, timeout=timeout)


def explain_http_error(e):
    body = e.read()[:2000]
    try:
        info = json.loads(body)
    except ValueError:
        info = None
    if e.code == 422:
        detail = info.get("detail") if isinstance(info, dict) else body.decode("utf-8", "replace")
        return f"the server rejected the request (422 validation error): {detail}"
    if e.code == 404 and isinstance(info, dict) and "error_code" in info:
        return ("generation failed on the server (it answers 404 for any generation error). "
                "Look at the server window: out of GPU memory is the usual cause. Try without --texture, "
                "a lower --octree, or start the server with --low_vram_mode.")
    if e.code == 404:
        return "404 Not Found: is this a Hunyuan3D 2.1 api_server? Check --url (the web UI on :8080 is not the API)."
    return f"HTTP {e.code}: {body.decode('utf-8', 'replace')}"


def cmd_health(args):
    url = args.url.rstrip("/") + "/health"
    try:
        with request(url, timeout=10) as r:
            info = json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        fail(explain_http_error(e))
    except (urllib.error.URLError, OSError) as e:
        fail(f"can't reach {url}: {getattr(e, 'reason', e)}. Is the Hunyuan3D API server running?")
    except ValueError:
        fail(f"{url} did not return JSON: is this the Hunyuan3D API server?")
    print(json.dumps(info))
    return 0 if info.get("status") == "healthy" else 1


def cmd_generate(args):
    path = args.image
    ext = os.path.splitext(path)[1].lower()
    if ext not in IMAGE_EXTS:
        fail(f"{path}: use a PNG, JPG or WEBP image (Hunyuan3D 2.1 takes images only, no text prompt)")
    if not os.path.isfile(path):
        fail(f"{path}: file not found")
    size = os.path.getsize(path)
    if size == 0 or size > MAX_IMAGE_BYTES:
        fail(f"{path}: image is {size} bytes; use a non-empty image under 20 MB")
    for name in ("octree", "steps", "guidance", "faces", "seed"):
        check_range(name, getattr(args, name))

    out = args.out or os.path.splitext(os.path.basename(path))[0] + ".glb"
    if os.path.exists(out) and not args.force:
        fail(f"{out} already exists (use --force to overwrite)")

    with open(path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("ascii")
    payload = {
        "image": image_b64,
        "remove_background": not args.no_remove_bg,
        "texture": args.texture,
        "seed": args.seed,
        "octree_resolution": args.octree,
        "num_inference_steps": args.steps,
        "guidance_scale": args.guidance,
        "face_count": args.faces,
    }
    url = args.url.rstrip("/") + "/generate"
    print(f"sending {os.path.basename(path)} to {url} (texture={'on' if args.texture else 'off'}); "
          f"this takes minutes...", file=sys.stderr)
    start = time.time()
    try:
        with request(url, data=json.dumps(payload).encode("utf-8"), timeout=args.timeout) as r:
            data = r.read()
            ctype = r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        fail(explain_http_error(e))
    except (urllib.error.URLError, OSError) as e:
        reason = getattr(e, "reason", e)
        if "timed out" in str(reason):
            fail(f"no answer after {args.timeout} s. The server may still be working; raise --timeout.")
        fail(f"can't reach {url}: {reason}. Is the Hunyuan3D API server running?")

    if data[:4] == b"glTF":
        kind = "GLB"
    elif "json" in ctype or data[:1] == b"{":
        fail(f"expected a model file, got JSON: {data[:300].decode('utf-8', 'replace')}")
    else:
        kind = "model (not GLB; maybe OBJ)"
    tmp = out + ".part"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, out)
    print(json.dumps({"out": out, "bytes": len(data), "format": kind, "seconds": round(time.time() - start, 1),
                      "seed": args.seed}))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="Client for a local Hunyuan3D 2.1 API server")
    p.add_argument("--url", default=DEFAULT_URL, help=f"server address (default {DEFAULT_URL}, or $HUNYUAN3D_URL)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("health", help="check the server is up")

    g = sub.add_parser("generate", help="image -> 3D model")
    g.add_argument("image")
    g.add_argument("--out", help="output file (default: <image name>.glb)")
    g.add_argument("--force", action="store_true", help="overwrite --out")
    g.add_argument("--texture", action="store_true", help="also paint textures (needs much more VRAM)")
    g.add_argument("--seed", type=int, default=1234)
    g.add_argument("--octree", type=int, default=256, help="mesh detail 64-512 (default 256)")
    g.add_argument("--steps", type=int, default=20, help="inference steps 1-20 (default 20; the server alone defaults to 5)")
    g.add_argument("--guidance", type=float, default=5.0)
    g.add_argument("--faces", type=int, default=40000, help="max faces for texturing 1000-100000")
    g.add_argument("--no-remove-bg", action="store_true", help="image already has a clean/transparent background")
    g.add_argument("--timeout", type=int, default=900, help="seconds to wait (default 900)")

    # Allow --url after the subcommand too.
    for sp in sub.choices.values():
        sp.add_argument("--url", default=argparse.SUPPRESS)

    args = p.parse_args(argv)
    return cmd_health(args) if args.cmd == "health" else cmd_generate(args)


if __name__ == "__main__":
    sys.exit(main())
