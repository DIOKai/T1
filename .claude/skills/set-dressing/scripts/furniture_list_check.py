#!/usr/bin/env python3
"""Check a buyable-furniture list (CSV or JSON) and optionally export a shopping list CSV.

Read-only on the input; standard library only. Checks:
  - required fields present (name, store, url, price, w_cm, d_cm, h_cm)
  - dimensions numeric and > 0, price numeric and >= 0, qty integer >= 1
  - url is http(s)
  - totals per currency
  - fit: footprint vs room size, height vs ceiling, and whether the piece can be
    carried through the door (smallest side <= door width and middle side <=
    door height - a rule of thumb that ignores turning in corridors)
  - 3D model licence missing / non-free, substitutions without a reason

Usage:
  python furniture_list_check.py furniture.csv
  python furniture_list_check.py furniture.json --door-width 80 --door-height 200 \
      --room 420x360 --ceiling 260
  python furniture_list_check.py furniture.csv --rooms rooms.json --export shopping.csv

rooms.json: {"Living": {"w_cm": 420, "d_cm": 360, "h_cm": 260, "door_w_cm": 80, "door_h_cm": 200}}
Item columns: id, room, name, store, url, price, currency, qty, w_cm, d_cm, h_cm,
              model_source, model_url, model_licence, substitute, substitute_reason, notes
Exit code: 0 = no errors, 1 = errors found, 2 = bad input/usage.
"""

import argparse
import csv
import json
import sys
from urllib.parse import urlparse

REQUIRED = ("name", "store", "url", "price", "w_cm", "d_cm", "h_cm")
FREE_LICENCES = ("cc0", "cc-by", "cc by", "public domain", "mit", "own", "self-made",
                 "hunyuan3d-own", "manufacturer-free", "royalty-free")
EXPORT_FIELDS = ("room", "name", "store", "url", "qty", "price", "currency", "line_total",
                 "w_cm", "d_cm", "h_cm", "substitute", "notes")


def load_items(path):
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", data) if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise ValueError("JSON must be a list of items or {\"items\": [...]}")
        return [dict(i) for i in items]
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def num(value):
    """Parse '1.299,90', '1,299.90', '799', 799 -> float, or None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace(" ", "")
    for sym in ("R$", "US$", "$", "€", "£", "RM", "¥"):
        s = s.replace(sym, "")
    if not s:
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):     # 1.299,90 (pt-BR / EU)
            s = s.replace(".", "").replace(",", ".")
        else:                                 # 1,299.90
            s = s.replace(",", "")
    elif "," in s:
        head, _, tail = s.rpartition(",")
        s = head.replace(",", "") + ("." + tail if len(tail) != 3 else tail)
    try:
        return float(s)
    except ValueError:
        return None


def parse_room(text):
    try:
        w, d = text.lower().split("x")
        return {"w_cm": float(w), "d_cm": float(d)}
    except ValueError:
        raise argparse.ArgumentTypeError("--room must look like 420x360 (cm)")


def truthy(v):
    return str(v or "").strip().lower() in ("1", "true", "yes", "y", "sim", "是")


def check(items, rooms=None, default_room=None):
    rooms = rooms or {}
    errors, warns, totals, rows = [], [], {}, []
    for idx, it in enumerate(items, 1):
        label = f"#{it.get('id') or idx} {it.get('name') or '(no name)'}"
        for k in REQUIRED:
            if str(it.get(k, "")).strip() == "":
                errors.append(f"{label}: missing {k}")
        dims = {}
        for k in ("w_cm", "d_cm", "h_cm"):
            v = num(it.get(k))
            if it.get(k) not in (None, "") and (v is None or v <= 0):
                errors.append(f"{label}: {k} must be a number > 0 (got {it.get(k)!r})")
            dims[k] = v if v and v > 0 else None
        price = num(it.get("price"))
        if it.get("price") not in (None, "") and (price is None or price < 0):
            errors.append(f"{label}: price must be a number >= 0 (got {it.get('price')!r})")
            price = None
        q_raw = it.get("qty", 1)
        q = num(q_raw if q_raw not in (None, "") else 1)
        if q is None or q < 1 or q != int(q):
            errors.append(f"{label}: qty must be a whole number >= 1 (got {q_raw!r})")
            q = 1
        q = int(q)
        url = str(it.get("url", "")).strip()
        if url and urlparse(url).scheme not in ("http", "https"):
            errors.append(f"{label}: url must start with http(s):// (got {url[:40]!r})")
        cur = (str(it.get("currency", "")).strip() or "?").upper()
        line_total = price * q if price is not None else None
        if line_total is not None:
            totals[cur] = totals.get(cur, 0.0) + line_total
        if cur == "?" and price is not None:
            warns.append(f"{label}: no currency given")

        lic = str(it.get("model_licence", "")).strip().lower()
        if not lic:
            warns.append(f"{label}: no 3D model licence recorded")
        elif any(t in lic for t in ("-nc", " nc", "noncommercial", "non-commercial", "editorial", "-nd", " nd")):
            warns.append(f"{label}: model licence '{it.get('model_licence')}' restricts commercial use or edits")
        elif not any(f in lic for f in FREE_LICENCES):
            warns.append(f"{label}: model licence '{it.get('model_licence')}' - check it allows this use")
        if lic.startswith("cc-by") or lic.startswith("cc by"):
            warns.append(f"{label}: CC BY model - credit the author")
        if truthy(it.get("substitute")) and not str(it.get("substitute_reason", "")).strip():
            warns.append(f"{label}: marked as substitute but no substitute_reason")

        room = rooms.get(str(it.get("room", "")).strip()) or default_room or {}
        if all(dims.values()):
            w, d, h = dims["w_cm"], dims["d_cm"], dims["h_cm"]
            rw, rd = room.get("w_cm"), room.get("d_cm")
            if rw and rd:
                fits = (w <= rw and d <= rd) or (w <= rd and d <= rw)
                if not fits:
                    errors.append(f"{label}: footprint {w:g}x{d:g} cm larger than room {rw:g}x{rd:g} cm")
            ceil = room.get("h_cm")
            if ceil and h > ceil:
                errors.append(f"{label}: height {h:g} cm above ceiling {ceil:g} cm")
            dw, dh = room.get("door_w_cm"), room.get("door_h_cm")
            if dw:
                s = sorted((w, d, h))
                ok = s[0] <= dw and (dh is None or s[1] <= dh)
                if not ok:
                    need = f"smallest side {s[0]:g} cm" + (f", middle side {s[1]:g} cm" if dh else "")
                    warns.append(f"{label}: may not pass a {dw:g} cm door ({need}) - check assembled vs flat-pack")
        rows.append({
            "room": it.get("room", ""), "name": it.get("name", ""), "store": it.get("store", ""),
            "url": url, "qty": q, "price": "" if price is None else f"{price:.2f}", "currency": cur,
            "line_total": "" if line_total is None else f"{line_total:.2f}",
            "w_cm": it.get("w_cm", ""), "d_cm": it.get("d_cm", ""), "h_cm": it.get("h_cm", ""),
            "substitute": "yes" if truthy(it.get("substitute")) else "",
            "notes": it.get("notes", ""),
        })
    return errors, warns, totals, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--rooms", help="JSON with per-room sizes (see docstring)")
    ap.add_argument("--room", type=parse_room, help="default room footprint WxD in cm, e.g. 420x360")
    ap.add_argument("--ceiling", type=float, help="default ceiling height cm")
    ap.add_argument("--door-width", type=float, help="default door clear width cm")
    ap.add_argument("--door-height", type=float, help="default door clear height cm")
    ap.add_argument("--export", help="write a shopping-list CSV here (refuses to overwrite without --force)")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    try:
        items = load_items(a.file)
        rooms = {}
        if a.rooms:
            with open(a.rooms, encoding="utf-8") as f:
                rooms = json.load(f)
    except (OSError, ValueError) as e:
        print(f"ERROR: cannot read input: {e}", file=sys.stderr)
        return 2
    default = dict(a.room or {})
    if a.ceiling:
        default["h_cm"] = a.ceiling
    if a.door_width:
        default["door_w_cm"] = a.door_width
    if a.door_height:
        default["door_h_cm"] = a.door_height
    errors, warns, totals, rows = check(items, rooms, default or None)
    print(f"{len(items)} items checked")
    for e in errors:
        print("ERROR", e)
    for w in warns:
        print("WARN ", w)
    for cur, t in sorted(totals.items()):
        print(f"TOTAL {cur} {t:,.2f}")
    subs = sum(1 for r in rows if r["substitute"])
    if subs:
        print(f"INFO  {subs} item(s) are substitutes (3D model differs from the product)")
    if a.export:
        import os
        if os.path.exists(a.export) and not a.force:
            print(f"ERROR: {a.export} exists - use --force to overwrite", file=sys.stderr)
            return 2
        with open(a.export, "w", encoding="utf-8-sig", newline="") as f:
            wr = csv.DictWriter(f, fieldnames=EXPORT_FIELDS)
            wr.writeheader()
            wr.writerows(rows)
        print(f"wrote {a.export}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
