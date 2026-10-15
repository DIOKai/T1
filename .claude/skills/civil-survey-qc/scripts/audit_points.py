#!/usr/bin/env python3
"""Limited, non-mutating audit of explicitly described linear survey CSV data."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import sys

FACTORS = {"m": 1.0, "mm": 0.001, "ft": 0.3048, "us-ft": 1200 / 3937}


def audit(path, *, order, header, units, delimiter=",", encoding="utf-8-sig",
          crs=None, vertical_datum=None, bounds=None, max_z_deviation=None):
    raw = Path(path).read_bytes()
    findings = []

    def flag(severity, code, line=None, **detail):
        findings.append({"severity": severity, "code": code, "line": line, **detail})

    if not crs or not crs.strip():
        flag("review", "unknown_horizontal_crs")
    if not vertical_datum or not vertical_datum.strip():
        flag("review", "unknown_vertical_datum")
    order = order.upper()
    if len(order) not in (4, 5) or set(order) not in (set("PENZ"), set("PENZD")):
        raise ValueError("order must contain P,E,N,Z once, with optional D")
    if len(set(order)) != len(order):
        raise ValueError("order fields cannot repeat")
    if units not in FACTORS:
        raise ValueError("unsupported units")
    if len(delimiter) != 1:
        raise ValueError("delimiter must be one character")
    if bounds is not None:
        if len(bounds) != 6 or not all(math.isfinite(v) for v in bounds):
            raise ValueError("bounds require six finite metre values")
        if any(bounds[i] > bounds[i + 1] for i in (0, 2, 4)):
            raise ValueError("bounds minima must not exceed maxima")
    if max_z_deviation is not None:
        if not math.isfinite(max_z_deviation) or max_z_deviation < 0:
            raise ValueError("max-z-deviation must be finite and nonnegative")

    reader = csv.reader(io.StringIO(raw.decode(encoding), newline=""),
                        delimiter=delimiter, strict=True)
    labels = None
    if header:
        labels = next(reader, None)
        if labels is None or len(labels) != len(order):
            flag("error", "invalid_header_width", 1, expected=len(order),
                 actual=0 if labels is None else len(labels))
    ids, xyz_seen, xy_seen = {}, {}, {}
    points = []
    data_rows = 0
    try:
        while True:
            start_line = reader.line_num + 1
            row = next(reader, None)
            if row is None:
                break
            data_rows += 1
            if not row or all(not v.strip() for v in row):
                flag("review", "blank_row", start_line)
                continue
            if len(row) != len(order):
                flag("error", "row_width", start_line, expected=len(order), actual=len(row))
                continue
            fields = dict(zip(order, row))
            point_id = fields["P"].strip()
            if not point_id:
                flag("error", "missing_point_id", start_line)
            elif point_id in ids:
                flag("error", "duplicate_point_id", start_line,
                     point_id=point_id, first_line=ids[point_id])
            else:
                ids[point_id] = start_line
            try:
                coords = tuple(float(fields[k].strip()) * FACTORS[units] for k in "ENZ")
                if not all(math.isfinite(x) for x in coords):
                    raise ValueError("not finite")
            except (ValueError, OverflowError):
                flag("error", "invalid_coordinate", start_line, point_id=point_id)
                continue
            if not point_id:
                continue
            if coords in xyz_seen:
                flag("review", "duplicate_xyz", start_line, point_id=point_id,
                     first_line=xyz_seen[coords])
            else:
                xyz_seen[coords] = start_line
            xy = coords[:2]
            if xy in xy_seen and coords[2] != xy_seen[xy][0]:
                flag("review", "same_xy_different_z", start_line, point_id=point_id,
                     first_line=xy_seen[xy][1])
            else:
                xy_seen.setdefault(xy, (coords[2], start_line))
            if bounds is not None:
                for i, axis in enumerate("ENZ"):
                    if not bounds[2*i] <= coords[i] <= bounds[2*i + 1]:
                        flag("error", "outside_supplied_bounds", start_line,
                             point_id=point_id, axis=axis, value_m=coords[i])
            points.append((start_line, point_id, coords))
    except csv.Error as exc:
        flag("error", "csv_parse_error", reader.line_num, message=str(exc))
    if not points:
        flag("error", "no_valid_points")
    if points and max_z_deviation is not None:
        median_z = statistics.median(p[2][2] for p in points)
        for line, point_id, coords in points:
            # Rearranged comparison avoids overflow in subtraction for extreme inputs.
            if abs(coords[2] / 2 - median_z / 2) > max_z_deviation / 2:
                flag("review", "z_deviation_candidate", line, point_id=point_id,
                     elevation_m=coords[2], median_z_m=median_z)
    extents = None
    if points:
        extents = {
            axis: {"min": min(p[2][i] for p in points),
                   "max": max(p[2][i] for p in points)}
            for i, axis in enumerate("ENZ")
        }
    status = ("blocked" if any(f["severity"] == "error" for f in findings)
              else "review-required" if findings else "clear-limited")
    return {
        "status": status,
        "source": {"path": str(Path(path).resolve()), "sha256": hashlib.sha256(raw).hexdigest(),
                   "bytes": len(raw)},
        "declared": {"order": order, "header": header, "header_labels": labels,
                     "delimiter": delimiter, "encoding": encoding, "units": units,
                     "crs": crs, "vertical_datum": vertical_datum},
        "criteria": {"bounds_m": bounds, "max_z_deviation_m": max_z_deviation},
        "data_rows": data_rows, "valid_coordinate_rows": len(points),
        "extents_m": extents, "findings": findings,
        "not_checked": ["CRS correctness", "axis correctness", "field accuracy",
                        "control residuals", "closure", "coverage",
                        "breaklines", "project acceptance", "professional certification"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--order", required=True, help="e.g. PNEZD or PENZ")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--header", action="store_true")
    modes.add_argument("--no-header", action="store_true")
    parser.add_argument("--units", choices=FACTORS, required=True)
    parser.add_argument("--delimiter", default=",", help="single character or tab")
    parser.add_argument("--encoding", default="utf-8-sig")
    parser.add_argument("--crs")
    parser.add_argument("--vertical-datum")
    parser.add_argument("--bounds", nargs=6, type=float)
    parser.add_argument("--max-z-deviation", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output and args.output.resolve() == args.input.resolve():
            raise ValueError("output cannot be the input file")
        report = audit(
            args.input, order=args.order, header=args.header, units=args.units,
            delimiter="\t" if args.delimiter == "tab" else args.delimiter,
            encoding=args.encoding, crs=args.crs, vertical_datum=args.vertical_datum,
            bounds=args.bounds, max_z_deviation=args.max_z_deviation)
        content = json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        else:
            sys.stdout.write(content)
        return 0 if report["status"] == "clear-limited" else 1
    except (OSError, UnicodeError, ValueError, LookupError, csv.Error) as exc:
        print(f"audit_points: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
