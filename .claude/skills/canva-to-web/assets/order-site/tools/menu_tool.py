#!/usr/bin/env python3
"""Check a menu.json and turn it into SQL for the Supabase schema. Standard library only.

  python tools/menu_tool.py check menu.json        # problems and warnings, exit 1 on errors
  python tools/menu_tool.py sql menu.json > seed.sql   # settings + menu rows (re-runnable upsert)

The check catches what usually goes wrong when a menu is read from a Canva design: prices with
more than 2 decimals, duplicate ids, missing translations, items pointing at unknown categories or
option groups, a "halal" claim without a certificate number, and opening hours that don't parse.
"""
import json
import re
import sys

LANGS_DEFAULT = ["en", "zh", "ms"]
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
ID_RE = re.compile(r"^[a-z0-9_-]{1,40}$")
TIME_RE = re.compile(r"^([01][0-9]|2[0-3]):[0-5][0-9]$")
ALLERGENS = {"milk", "egg", "peanut", "tree_nut", "soy", "wheat", "gluten", "fish", "shellfish", "sesame"}
DIETARY = {"vegetarian", "vegan"}
HALAL_WORDS = re.compile(r"halal|حلال|清真|pork[- ]?free|no pork|tanpa babi|bebas babi|无猪肉", re.I)


def sen(value, where, errors):
    """Price in RM -> integer sen; error if it has more than 2 decimals or is negative."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"{where}: price must be a number, got {value!r}")
        return 0
    cents = round(value * 100)
    if abs(value * 100 - cents) > 1e-6:
        errors.append(f"{where}: price {value} has more than 2 decimals")
    if cents < 0:
        errors.append(f"{where}: price is negative")
    return int(cents)


def check(menu):
    errors, warnings = [], []
    shop = menu.get("shop") or {}
    langs = shop.get("languages") or LANGS_DEFAULT

    def texts(obj, where, required=True):
        if not isinstance(obj, dict) or not obj:
            if required:
                errors.append(f"{where}: needs a text object like {{\"en\": \"...\"}}")
            return
        for lang in langs:
            if not str(obj.get(lang, "")).strip():
                warnings.append(f"{where}: no '{lang}' text (falls back to English)")
        for v in obj.values():
            if HALAL_WORDS.search(str(v)) and not shop.get("halal_cert"):
                errors.append(f"{where}: says '{v}' but shop.halal_cert is not set. Only a JAKIM-certified premises may claim "
                              "halal (and 'pork-free' style wording can also mislead). Remove the wording or add the certificate.")

    texts(shop.get("name"), "shop.name")
    for key, lo, hi in (("sst_rate", 0, 0.2), ("service_charge_rate", 0, 0.2)):
        v = shop.get(key, 0)
        if not isinstance(v, (int, float)) or not lo <= v <= hi:
            errors.append(f"shop.{key}: must be a fraction between {lo} and {hi} (e.g. 0.06 for 6%), got {v!r}")
    if shop.get("sst_rate"):
        if not str(shop.get("sst_reg_no") or "").strip():
            errors.append("shop.sst_rate is set but shop.sst_reg_no is empty: only a business registered with Customs (MySST) may charge SST")
        warnings.append("shop.sst_rate is set: confirm the current F&B rate (6% in 2025-26) with the owner or accountant")
    for day in shop.get("closed_dates") or []:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(day)):
            errors.append(f"shop.closed_dates: {day!r} must be YYYY-MM-DD")
    cert = shop.get("halal_cert")
    if cert is not None and not (isinstance(cert, dict) and cert.get("number") and cert.get("expires")):
        errors.append("shop.halal_cert: must be null or {\"number\": ..., \"expires\": \"YYYY-MM-DD\"}")
    hours = shop.get("hours") or {}
    for d in DAYS:
        for win in hours.get(d, []):
            if not (isinstance(win, list) and len(win) == 2 and all(isinstance(t, str) and TIME_RE.match(t) for t in win)):
                errors.append(f"shop.hours.{d}: window {win!r} must be [\"HH:MM\", \"HH:MM\"]")
    if not any(hours.get(d) for d in DAYS):
        errors.append("shop.hours: no opening hours at all, the shop could never take an order")
    pay = shop.get("payment") or {}
    if not any(pay.get(k) for k in ("counter", "duitnow_qr", "online")):
        errors.append("shop.payment: enable at least one of counter, duitnow_qr, online")
    if pay.get("online"):
        warnings.append("shop.payment.online is on: online payment gateways charge per transaction (paid); ask the owner first")

    group_ids, cat_ids, item_ids = set(), set(), set()
    for g in menu.get("option_groups", []):
        gid = g.get("id", "")
        if not ID_RE.match(gid) or gid in group_ids:
            errors.append(f"option group id {gid!r} is invalid or duplicated")
        group_ids.add(gid)
        if g.get("type") not in ("single", "multi"):
            errors.append(f"option group {gid}: type must be single or multi")
        texts(g.get("label"), f"option_groups.{gid}.label")
        opt_ids = set()
        for o in g.get("options", []):
            oid = o.get("id", "")
            if not ID_RE.match(oid) or oid in opt_ids:
                errors.append(f"option {gid}.{oid!r} is invalid or duplicated")
            opt_ids.add(oid)
            sen(o.get("price", 0), f"option {gid}.{oid}", errors)
            texts(o.get("label"), f"option {gid}.{oid}.label")
        if not opt_ids:
            errors.append(f"option group {gid}: has no options")
        if g.get("default") and g["default"] not in opt_ids:
            errors.append(f"option group {gid}: default {g['default']!r} is not one of its options")
        if g.get("type") == "single" and g.get("required") and not g.get("default"):
            warnings.append(f"option group {gid}: required with no default, customers must pick one every time")
    for c in menu.get("categories", []):
        cid = c.get("id", "")
        if not ID_RE.match(cid) or cid in cat_ids:
            errors.append(f"category id {cid!r} is invalid or duplicated")
        cat_ids.add(cid)
        texts(c.get("label"), f"categories.{cid}.label")
    for it in menu.get("items", []):
        iid = it.get("id", "")
        if not ID_RE.match(iid) or iid in item_ids:
            errors.append(f"item id {iid!r} is invalid or duplicated")
        item_ids.add(iid)
        if it.get("category") not in cat_ids:
            errors.append(f"item {iid}: unknown category {it.get('category')!r}")
        sen(it.get("price"), f"item {iid}", errors)
        texts(it.get("name"), f"items.{iid}.name")
        texts(it.get("desc"), f"items.{iid}.desc", required=False)
        for gid in it.get("groups", []):
            if gid not in group_ids:
                errors.append(f"item {iid}: unknown option group {gid!r}")
        for a in it.get("allergens", []):
            if a not in ALLERGENS:
                warnings.append(f"item {iid}: allergen {a!r} is not in the standard list {sorted(ALLERGENS)}")
        for dty in it.get("dietary", []):
            if dty not in DIETARY:
                warnings.append(f"item {iid}: dietary tag {dty!r} is not one of {sorted(DIETARY)}")
        if it.get("color") and not re.match(r"^#[0-9a-fA-F]{6}$", it["color"]):
            errors.append(f"item {iid}: color must look like #a1b2c3")
    if not item_ids:
        errors.append("menu has no items")
    return errors, warnings


def q(value):
    """SQL literal."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, (dict, list)):
        return "'" + json.dumps(value, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(value).replace("'", "''") + "'"


def arr(values):
    return "'{" + ",".join('"' + str(v).replace('"', '') + '"' for v in values) + "}'"


def to_sql(menu):
    shop = menu["shop"]
    errors = []
    out = ["-- generated by tools/menu_tool.py; safe to re-run (upserts)", "begin;"]
    out.append(
        "insert into public.settings (id, name, tagline, currency, timezone, languages, halal_cert, sst_rate, sst_reg_no, "
        "service_charge_rate, sst_on_service_charge, service_charge_takeaway, round_cash_to_5sen, prep_minutes, slot_minutes, max_tables, "
        "dine_in, takeaway, payment, hours, closed_dates) values (1, "
        + ", ".join([q(shop["name"]), q(shop.get("tagline", {})), q(shop.get("currency", "RM")),
                     q(shop.get("timezone", "Asia/Kuala_Lumpur")), arr(shop.get("languages", LANGS_DEFAULT)),
                     q(shop.get("halal_cert")), q(shop.get("sst_rate", 0)), q(shop.get("sst_reg_no")),
                     q(shop.get("service_charge_rate", 0)),
                     q(shop.get("sst_on_service_charge", True)), q(shop.get("service_charge_takeaway", False)),
                     q(shop.get("round_cash_to_5sen", True)),
                     q(shop.get("prep_minutes", 10)), q(shop.get("slot_minutes", 15)), q(shop.get("max_tables", 20)),
                     q(shop.get("dine_in", True)), q(shop.get("takeaway", True)),
                     q(shop.get("payment", {"counter": True})), q(shop["hours"]),
                     arr(shop.get("closed_dates") or [])])
        + ") on conflict (id) do update set name = excluded.name, tagline = excluded.tagline, currency = excluded.currency, "
        "timezone = excluded.timezone, languages = excluded.languages, halal_cert = excluded.halal_cert, "
        "sst_rate = excluded.sst_rate, sst_reg_no = excluded.sst_reg_no, service_charge_rate = excluded.service_charge_rate, "
        "sst_on_service_charge = excluded.sst_on_service_charge, service_charge_takeaway = excluded.service_charge_takeaway, "
        "round_cash_to_5sen = excluded.round_cash_to_5sen, "
        "prep_minutes = excluded.prep_minutes, slot_minutes = excluded.slot_minutes, max_tables = excluded.max_tables, "
        "dine_in = excluded.dine_in, takeaway = excluded.takeaway, payment = excluded.payment, hours = excluded.hours, "
        "closed_dates = excluded.closed_dates;")
    for i, c in enumerate(menu["categories"]):
        out.append(f"insert into public.categories (id, label, sort) values ({q(c['id'])}, {q(c['label'])}, {i}) "
                   "on conflict (id) do update set label = excluded.label, sort = excluded.sort;")
    for i, g in enumerate(menu["option_groups"]):
        out.append(f"insert into public.option_groups (id, label, type, required, default_option, max_total, sort) values "
                   f"({q(g['id'])}, {q(g['label'])}, {q(g['type'])}, {q(g.get('required', False))}, {q(g.get('default'))}, "
                   f"{q(g.get('max_total'))}, {i}) on conflict (id) do update set label = excluded.label, type = excluded.type, "
                   "required = excluded.required, default_option = excluded.default_option, max_total = excluded.max_total, sort = excluded.sort;")
        for j, o in enumerate(g["options"]):
            out.append(f"insert into public.options (group_id, id, label, price_sen, max_qty, sort) values ({q(g['id'])}, {q(o['id'])}, "
                       f"{q(o['label'])}, {sen(o.get('price', 0), o['id'], errors)}, {q(o.get('max', 1))}, {j}) "
                       "on conflict (group_id, id) do update set label = excluded.label, price_sen = excluded.price_sen, "
                       "max_qty = excluded.max_qty, sort = excluded.sort;")
    for i, it in enumerate(menu["items"]):
        out.append(f"insert into public.items (id, category_id, name, description, price_sen, color, image_url, allergens, dietary, "
                   f"featured, sold_out, sort) values ({q(it['id'])}, {q(it['category'])}, {q(it['name'])}, {q(it.get('desc', {}))}, "
                   f"{sen(it['price'], it['id'], errors)}, {q(it.get('color'))}, {q(it.get('image'))}, {arr(it.get('allergens', []))}, "
                   f"{arr(it.get('dietary', []))}, {q(it.get('featured', False))}, {q(it.get('sold_out', False))}, {i}) "
                   "on conflict (id) do update set category_id = excluded.category_id, name = excluded.name, "
                   "description = excluded.description, price_sen = excluded.price_sen, color = excluded.color, "
                   "image_url = excluded.image_url, allergens = excluded.allergens, dietary = excluded.dietary, "
                   "featured = excluded.featured, sold_out = excluded.sold_out, sort = excluded.sort;")
        out.append(f"delete from public.item_groups where item_id = {q(it['id'])};")
        for j, gid in enumerate(it.get("groups", [])):
            out.append(f"insert into public.item_groups (item_id, group_id, sort) values ({q(it['id'])}, {q(gid)}, {j});")
    out.append("commit;")
    if errors:
        raise SystemExit("menu has errors, run `check` first:\n  " + "\n  ".join(errors))
    return "\n".join(out) + "\n"


def main(argv):
    if len(argv) != 3 or argv[1] not in ("check", "sql"):
        print(__doc__)
        return 2
    try:
        with open(argv[2], encoding="utf-8") as fh:
            menu = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"error: cannot read {argv[2]}: {e}", file=sys.stderr)
        return 2
    errors, warnings = check(menu)
    if argv[1] == "check":
        for w in warnings:
            print("WARN ", w)
        for e in errors:
            print("ERROR", e)
        n_items = len(menu.get("items", []))
        print(f"{n_items} items, {len(errors)} errors, {len(warnings)} warnings")
        return 1 if errors else 0
    if errors:
        print("menu has errors, run `check` first", file=sys.stderr)
        return 1
    sys.stdout.write(to_sql(menu))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
