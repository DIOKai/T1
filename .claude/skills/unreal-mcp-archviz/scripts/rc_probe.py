#!/usr/bin/env python3
"""Read-only probe for Unreal Engine's Remote Control HTTP server.

    python rc_probe.py                      # GET /remote/info and /remote/presets
    python rc_probe.py --describe "/Game/Maps/House.House:PersistentLevel.Sofa_2"
    python rc_probe.py --port 30010 --json  # machine-readable output

Never sends write calls: the only PUT it makes is /remote/object/describe,
which reads an object's properties and functions. Only localhost targets are
allowed (127.0.0.1, localhost, ::1). Standard library only.

Exit codes: 0 = server answered, 2 = nothing listening / unreachable,
3 = server answered with an error on a requested route, 4 = bad arguments.
"""
import argparse
import json
import socket
import sys
import urllib.error
import urllib.request

LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
# The probe may only ever use these (method, route) pairs.
ALLOWED = {("GET", "/remote/info"), ("GET", "/remote/presets"), ("PUT", "/remote/object/describe")}


def build_request(host, port, method, route, body=None):
    """Return a urllib Request; raises ValueError for anything not read-only or not local."""
    if (method, route) not in ALLOWED:
        raise ValueError(f"refusing {method} {route}: rc_probe is read-only")
    if host not in LOCAL_HOSTS:
        raise ValueError(f"refusing host {host!r}: rc_probe only talks to localhost")
    netloc = f"[{host}]" if ":" in host else host
    url = f"http://{netloc}:{int(port)}{route}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    return req


def send(req, timeout):
    """Return (status, parsed_or_text, error_string)."""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read().decode("utf-8", "replace")
            status = res.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        status = e.code
    except (urllib.error.URLError, ConnectionError, socket.timeout, OSError) as e:
        reason = getattr(e, "reason", e)
        return None, None, str(reason)
    try:
        return status, json.loads(raw), None
    except ValueError:
        return status, raw, None


def summarize_info(data):
    if isinstance(data, dict):
        routes = data.get("HttpRoutes") or data.get("Routes") or []
        if isinstance(routes, list) and routes:
            names = []
            for r in routes:
                if isinstance(r, dict):
                    names.append(f"{r.get('Verb', '?')} {r.get('Path', '?')}")
            return f"{len(routes)} routes" + (": " + ", ".join(names[:8]) + (" ..." if len(names) > 8 else "") if names else "")
    return "answered (unrecognised format)"


def summarize_presets(data):
    if isinstance(data, dict):
        presets = data.get("Presets", data.get("presets"))
        if isinstance(presets, list):
            labels = [p.get("Name", p.get("name", "?")) if isinstance(p, dict) else str(p) for p in presets]
            return f"{len(presets)} preset(s)" + (": " + ", ".join(labels) if labels else "")
    return "answered (unrecognised format)"


def summarize_describe(data):
    if isinstance(data, dict):
        props = data.get("Properties") or []
        funcs = data.get("Functions") or []
        fnames = [f.get("Name", "?") for f in funcs if isinstance(f, dict)]
        return (f"class {data.get('Class', '?')}, {len(props)} properties, {len(funcs)} functions"
                + (": " + ", ".join(fnames[:15]) + (" ..." if len(fnames) > 15 else "") if fnames else ""))
    return "answered (unrecognised format)"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Read-only probe for Unreal Remote Control (HTTP).")
    ap.add_argument("--host", default="127.0.0.1", help="localhost only (default 127.0.0.1)")
    ap.add_argument("--port", type=int, default=30010, help="Remote Control HTTP port (default 30010)")
    ap.add_argument("--describe", metavar="OBJECT_PATH", help="also PUT /remote/object/describe for this object")
    ap.add_argument("--timeout", type=float, default=3.0)
    ap.add_argument("--json", action="store_true", help="print raw results as JSON")
    a = ap.parse_args(argv)

    steps = [("GET", "/remote/info", None, summarize_info),
             ("GET", "/remote/presets", None, summarize_presets)]
    if a.describe:
        steps.append(("PUT", "/remote/object/describe", {"objectPath": a.describe}, summarize_describe))

    results, exit_code = [], 0
    for method, route, body, summ in steps:
        try:
            req = build_request(a.host, a.port, method, route, body)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 4
        status, data, err = send(req, a.timeout)
        results.append({"method": method, "route": route, "status": status, "error": err, "data": data})
        if err is not None:
            if not a.json:
                print(f"NOT LISTENING: nothing answered at http://{a.host}:{a.port} ({err}).")
                print("  In Unreal: enable the Remote Control API plugin, then run `WebControl.StartServer` "
                      "in the console (packaged build: launch with -RCWebControlEnable -RCWebInterfaceEnable).")
            exit_code = 2
            break
        ok = 200 <= status < 300
        if not a.json:
            print(f"{'OK ' if ok else 'ERR'} {method} {route} -> HTTP {status}: "
                  f"{summ(data) if ok else str(data)[:300]}")
        if not ok:
            exit_code = max(exit_code, 3)

    if a.json:
        print(json.dumps({"host": a.host, "port": a.port, "results": results}, indent=2, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
