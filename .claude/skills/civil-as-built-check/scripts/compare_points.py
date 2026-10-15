#!/usr/bin/env python3
"""Compare explicit point IDs in declared linear coordinate frames; no alignment."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

FACTORS = {"m": 1.0, "mm": 0.001, "ft": 0.3048, "us-ft": 1200 / 3937}


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite JSON number")
    try:
        result = float(value)
    except (ValueError, OverflowError):
        raise ValueError(f"{label} must be a finite JSON number") from None
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def points(dataset):
    unit = dataset.get("units")
    if unit not in FACTORS:
        raise ValueError("units must be m, mm, ft or us-ft")
    rows = dataset.get("points")
    if not isinstance(rows, list):
        raise ValueError("points must be a list")
    output = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("point must be an object")
        key = row.get("id")
        if not isinstance(key, str) or not key.strip() or key in output:
            raise ValueError("point IDs must be unique nonempty strings")
        coordinates = tuple(number(row.get(axis), f"{key}.{axis}") * FACTORS[unit]
                            for axis in ("e", "n", "z"))
        if not all(math.isfinite(x) for x in coordinates):
            raise ValueError("unit conversion overflow")
        output[key] = coordinates
    return output


def compare(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    design, observed = data.get("design"), data.get("observed")
    if not isinstance(design, dict) or not isinstance(observed, dict):
        raise ValueError("design and observed must be objects")
    frame = design.get("frame")
    if not isinstance(frame, str) or not frame.strip() or observed.get("frame") != frame:
        raise ValueError("nonempty coordinate frame labels must match exactly")
    d, o = points(design), points(observed)
    raw_tolerances = data.get("tolerances_m", {})
    if not isinstance(raw_tolerances, dict) or set(raw_tolerances) - {"horizontal", "vertical"}:
        raise ValueError("tolerances_m accepts horizontal and vertical only")
    tolerances = {}
    for key, value in raw_tolerances.items():
        tol = number(value, key)
        if tol < 0:
            raise ValueError("tolerances must be nonnegative")
        tolerances[key] = tol
    rows = []
    for key in sorted(d.keys() & o.keys()):
        delta = tuple(b - a for a, b in zip(d[key], o[key]))
        horizontal, spatial = math.hypot(*delta[:2]), math.hypot(*delta)
        if not all(math.isfinite(v) for v in (*delta, horizontal, spatial)):
            raise ValueError("deviation overflow")
        checks = {}
        if "horizontal" in tolerances:
            checks["horizontal"] = horizontal <= tolerances["horizontal"]
        if "vertical" in tolerances:
            checks["vertical"] = abs(delta[2]) <= tolerances["vertical"]
        status = ("outside-supplied-tolerance" if False in checks.values()
                  else "within-supplied-tolerance" if len(checks) == 2 else "not-assessed")
        rows.append({"id": key, "design_m": dict(zip("ENZ", d[key])),
                     "observed_m": dict(zip("ENZ", o[key])),
                     "delta_m": dict(zip("ENZ", delta)),
                     "horizontal_m": horizontal, "spatial_m": spatial,
                     "checks": checks, "status": status})
    missing, unexpected = sorted(d.keys() - o.keys()), sorted(o.keys() - d.keys())
    overall = ("blocked" if not rows else
               "outside-supplied-tolerance" if any(
                   row["status"] == "outside-supplied-tolerance" for row in rows) else
               "review-required" if missing or unexpected or len(tolerances) != 2 else
               "within-supplied-tolerance")
    return {"status": overall, "frame": frame, "units": "m",
            "tolerances_m": tolerances, "points": rows,
            "missing_observed_ids": missing, "unexpected_observed_ids": unexpected,
            "not_checked": ["geodetic correctness", "registration", "measurement uncertainty",
                            "surface distances", "contractual acceptance", "certification"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes()
        result = compare(json.loads(raw.decode("utf-8-sig")))
        result["source_sha256"] = hashlib.sha256(raw).hexdigest()
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        if not result["points"]:
            return 1
        return 0 if result["status"] == "within-supplied-tolerance" else 1
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"compare_points: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
