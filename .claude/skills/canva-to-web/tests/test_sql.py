#!/usr/bin/env python3
"""Run the ordering schema against a local Postgres with Supabase-like roles and check security + pricing."""
import json
import subprocess
import sys
import uuid

PG = ["psql", "-h", sys.argv[1], "-p", "55432", "-U", "postgres", "-d", "shop", "-At", "-v", "ON_ERROR_STOP=1"]
FAIL = []


def sql(stmt, role=None, sub=None):
    pre = ""
    if sub:
        pre += f"set request.jwt.claim.sub = '{sub}'; "
    if role:
        pre += f"set role {role}; "
    r = subprocess.run(PG + ["-c", pre + stmt], capture_output=True, text=True)
    out = "\n".join(l for l in r.stdout.splitlines() if l != "SET").strip()
    return r.returncode, out, r.stderr.strip()


def ok(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -> {detail}"))
    if not cond:
        FAIL.append(name)


def order(payload, role="anon"):
    code, out, err = sql(f"select public.place_order($J${json.dumps(payload)}$J$::jsonb)", role)
    return (json.loads(out) if code == 0 and out else None), err


def expect_error(name, payload, msg):
    res, err = order(payload)
    ok(name, res is None and msg in err, err or res)


admin = lambda s: sql(s)  # noqa: E731
admin("update settings set sst_reg_no = 'W10-1234-56789012'")
admin("update settings set hours = '{\"mon\":[[\"00:00\",\"00:00\"]],\"tue\":[[\"00:00\",\"00:00\"]],\"wed\":[[\"00:00\",\"00:00\"]],"
      "\"thu\":[[\"00:00\",\"00:00\"]],\"fri\":[[\"00:00\",\"00:00\"]],\"sat\":[[\"00:00\",\"00:00\"]],\"sun\":[[\"00:00\",\"00:00\"]]}', "
      "service_charge_rate = 0.10, sst_rate = 0.06, sst_on_service_charge = true, accepting_orders = true")
admin("delete from orders; delete from order_counters;")

base = {"mode": "dine_in", "table": 7, "name": "Ali", "phone": "+60 12-345 6789", "payment": "counter", "consent": True, "lang": "zh"}

# --- anon can read the menu, nothing else
code, out, err = sql("select count(*) from items", "anon")
ok("anon reads menu", code == 0 and out == "5", err)
code, out, err = sql("select count(*) from orders", "anon")
ok("anon cannot read orders", code != 0 and "permission denied" in err, out)
code, out, err = sql("insert into orders (order_no) values ('X')", "anon")
ok("anon cannot insert orders directly", code != 0 and "permission denied" in err, out)
code, out, err = sql("update items set price_sen = 1 where id = 'latte'", "anon")
ok("anon cannot change prices", code != 0 and "permission denied" in err, out)
code, out, err = sql("select count(*) from staff", "anon")
ok("anon cannot read staff", code != 0, out)

# --- pricing is server-side; client prices are ignored
p = dict(base, lines=[
    {"item": "latte", "qty": 2, "price": 0.01, "options": {"size": "large", "milk": "oat"}},
    {"item": "matcha", "qty": 1, "options": {"toppings": {"pearl": 2, "foam": 1}}},
], total_sen=1)
res, err = order(p)
ok("valid dine-in order", res is not None, err)
if res:
    # latte large oat = 990+200+150 = 1340 x2 = 2680 ; matcha 1290 + 2*150 + 250 = 1840 ; subtotal 4520
    # service 10% = 452 ; SST 6% of (4520+452) = 298.32 -> 298 ; total 5270
    ok("subtotal from server prices", res["subtotal_sen"] == 4520, res)
    ok("service charge 10%", res["service_sen"] == 452, res)
    ok("SST 6% on subtotal+service", res["sst_sen"] == 298, res)
    ok("total", res["total_sen"] == 5270, res)
    ok("cash rounding keeps 5270", res["cash_total_sen"] == 5270, res)
    ok("first order number A001", res["order_no"] == "A001", res)
    ok("defaults filled (sweetness s50)", any(o["option"] == "s50" for o in res["lines"][0]["options"]), res["lines"][0])
    token = res["token"]
    code, out, err = sql(f"select public.order_status('{token}')", "anon")
    st = json.loads(out) if out else {}
    ok("order_status by token", st.get("order_no") == "A001" and st.get("status") == "new" and "phone" not in st, out or err)
    code, out, err = sql(f"select public.order_status('{uuid.uuid4()}')", "anon")
    ok("unknown token returns nothing", code == 0 and out == "", out)

res2, err = order(dict(base, lines=[{"item": "lemon", "qty": 1}]))
ok("order numbers increase", res2 and res2["order_no"] == "A002", err or res2)

# --- validation
expect_error("sold-out item rejected", dict(base, lines=[{"item": "lemon", "qty": 1}]) if not admin("update items set sold_out = true where id = 'lemon'")[0] else {}, "sold_out:lemon")
admin("update items set sold_out = false where id = 'lemon'")
expect_error("option from another group rejected", dict(base, lines=[{"item": "latte", "qty": 1, "options": {"toppings": {"pearl": 1}}}]), "bad_option")
expect_error("over per-topping max", dict(base, lines=[{"item": "matcha", "qty": 1, "options": {"toppings": {"pearl": 4}}}]), "bad_option")
expect_error("over total toppings", dict(base, lines=[{"item": "matcha", "qty": 1, "options": {"toppings": {"pearl": 3, "jelly": 2}}}]), "too_many_toppings")
expect_error("negative topping", dict(base, lines=[{"item": "matcha", "qty": 1, "options": {"toppings": {"pearl": -1}}}]), "bad_option")
expect_error("unknown option value", dict(base, lines=[{"item": "latte", "qty": 1, "options": {"size": "venti"}}]), "bad_option")
expect_error("qty 0 rejected", dict(base, lines=[{"item": "latte", "qty": 0}]), "bad_qty")
expect_error("qty 50 rejected", dict(base, lines=[{"item": "latte", "qty": 50}]), "bad_qty")
expect_error("unknown item", dict(base, lines=[{"item": "beer", "qty": 1}]), "unknown_item")
expect_error("no lines", dict(base, lines=[]), "bad_lines")
expect_error("table out of range", dict(base, table=999, lines=[{"item": "latte", "qty": 1}]), "bad_table")
expect_error("consent required", dict(base, consent=False, lines=[{"item": "latte", "qty": 1}]), "consent_required")
expect_error("disabled payment method", dict(base, payment="online", lines=[{"item": "latte", "qty": 1}]), "payment_not_allowed")
expect_error("takeaway needs phone", dict(base, mode="takeaway", phone="", lines=[{"item": "latte", "qty": 1}]), "phone_required")
code, now_iso, _ = sql("select to_char(now() + interval '1 minute', 'YYYY-MM-DD\"T\"HH24:MI:SSOF')")
expect_error("pickup sooner than prep time", dict(base, mode="takeaway", pickup_at=now_iso, lines=[{"item": "latte", "qty": 1}]), "bad_pickup_time")
code, later_iso, _ = sql("select to_char(now() + interval '30 minutes', 'YYYY-MM-DD\"T\"HH24:MI:SSOF')")
res, err = order(dict(base, mode="takeaway", table=None, pickup_at=later_iso, lines=[{"item": "latte", "qty": 1}]))
ok("takeaway with valid pickup", res is not None and res["mode"] == "takeaway", err)
expect_error("html in name is just text but too long name rejected", dict(base, name="x" * 61, lines=[{"item": "latte", "qty": 1}]), "bad_name")

admin("update settings set accepting_orders = false")
expect_error("paused shop rejects", dict(base, lines=[{"item": "latte", "qty": 1}]), "paused")
admin("update settings set accepting_orders = true")

# closed: open only in a window 12 hours away from now (local time)
code, h, _ = sql("select to_char((now() at time zone 'Asia/Kuala_Lumpur') + interval '12 hours', 'HH24')")
win = f'[["{h}:00","{h}:30"]]'
admin("update settings set sst_reg_no = 'W10-1234-56789012'")
admin("update settings set hours = '{" + ",".join(f'"{d}":{win}' for d in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]) + "}'")
expect_error("closed shop rejects dine-in", dict(base, lines=[{"item": "latte", "qty": 1}]), "closed")
admin("update settings set sst_reg_no = 'W10-1234-56789012'")
admin("update settings set hours = '{\"mon\":[[\"00:00\",\"00:00\"]],\"tue\":[[\"00:00\",\"00:00\"]],\"wed\":[[\"00:00\",\"00:00\"]],"
      "\"thu\":[[\"00:00\",\"00:00\"]],\"fri\":[[\"00:00\",\"00:00\"]],\"sat\":[[\"00:00\",\"00:00\"]],\"sun\":[[\"00:00\",\"00:00\"]]}'")

# overnight window: Friday 18:00-02:00 -> open Sat 01:00, closed Sat 03:00 and Fri 17:00
admin("update settings set sst_reg_no = 'W10-1234-56789012'")
admin("update settings set hours = '{\"fri\":[[\"18:00\",\"02:00\"]]}'")
for ts, want in (("2026-10-30 23:00+08", "t"), ("2026-10-31 01:00+08", "t"), ("2026-10-31 03:00+08", "f"), ("2026-10-30 17:00+08", "f")):
    code, out, _ = sql(f"select public.shop_is_open('{ts}')", "anon")
    ok(f"overnight hours {ts} -> {want}", out == want, out)
admin("update settings set sst_reg_no = 'W10-1234-56789012'")
admin("update settings set hours = '{\"mon\":[[\"00:00\",\"00:00\"]],\"tue\":[[\"00:00\",\"00:00\"]],\"wed\":[[\"00:00\",\"00:00\"]],"
      "\"thu\":[[\"00:00\",\"00:00\"]],\"fri\":[[\"00:00\",\"00:00\"]],\"sat\":[[\"00:00\",\"00:00\"]],\"sun\":[[\"00:00\",\"00:00\"]]}'")

# 5-sen rounding (Bank Negara: 1,2,6,7 down; 3,4,8,9 up)
code, out, _ = sql("select string_agg(public.round_5sen(x)::text, ',' order by x) from generate_series(100, 110) x")
ok("5-sen rounding table", out == "100,100,100,105,105,105,105,105,110,110,110", out)

# flood protection: 5 orders per phone in 10 minutes
admin("delete from orders")
flood = dict(base, phone="0111111111", lines=[{"item": "latte", "qty": 1}])
for _ in range(5):
    order(flood)
expect_error("6th order from same phone in 10 min rejected", flood, "too_many_orders")

# idempotency: the same client_ref returns the same order, not a second one
admin("delete from orders")
ref = str(uuid.uuid4())
r1, e1 = order(dict(base, client_ref=ref, lines=[{"item": "latte", "qty": 1}]))
r2, e2 = order(dict(base, client_ref=ref, lines=[{"item": "latte", "qty": 1}]))
code, cnt, _ = sql("select count(*) from orders")
ok("retry with same client_ref returns same order", r1 and r2 and r1["token"] == r2["token"] and cnt == "1", (e1, e2, cnt))
r3, e3 = order(dict(base, client_ref="not-a-uuid", lines=[{"item": "latte", "qty": 1}]))
ok("bad client_ref ignored, order still placed", r3 is not None, e3)

# PDPA purge
admin("update orders set created_at = now() - interval '100 days' where token = '" + r1["token"] + "'")
code, n, err = sql("select public.purge_personal_data(90)")
code2, row, _ = sql("select customer_name || '|' || coalesce(phone,'null') from orders where token = '" + r1["token"] + "'")
ok("purge blanks old name/phone only", n == "1" and row == "-|null", (n, row, err))
code, out, err = sql("select public.purge_personal_data(0)", "anon")
ok("anon cannot run purge", code != 0 and "permission denied" in err, out)
code, out, err = sql("select public.order_result(o) from orders o limit 1", "anon")
ok("anon cannot call order_result directly", code != 0, out)

# SST needs a registration number
code, out, err = sql("update settings set sst_reg_no = null where id = 1")
ok("SST on without registration number is refused", code != 0 and "sst_needs_registration" in err, out or err)
admin("update settings set sst_reg_no = 'W10-1234-56789012'")

# closed dates: Friday 2026-10-30 open 18:00-02:00 but listed as a day off -> closed, including after midnight
admin("update settings set hours = '{\"fri\":[[\"18:00\",\"02:00\"]]}', closed_dates = '{2026-10-30}'")
for ts, want in (("2026-10-30 20:00+08", "f"), ("2026-10-31 01:00+08", "f")):
    code, out, _ = sql(f"select public.shop_is_open('{ts}')", "anon")
    ok(f"closed date {ts} -> {want}", out == want, out)
admin("update settings set closed_dates = '{}', hours = '{\"mon\":[[\"00:00\",\"00:00\"]],\"tue\":[[\"00:00\",\"00:00\"]],\"wed\":[[\"00:00\",\"00:00\"]],"
      "\"thu\":[[\"00:00\",\"00:00\"]],\"fri\":[[\"00:00\",\"00:00\"]],\"sat\":[[\"00:00\",\"00:00\"]],\"sun\":[[\"00:00\",\"00:00\"]]}'")

# takeaway while closed: refused unless takeaway_preorder; pickup more than 12 h ahead refused
code, h, _ = sql("select to_char((now() at time zone 'Asia/Kuala_Lumpur') + interval '3 hours', 'HH24')")
admin("update settings set hours = '{" + ",".join(f'"{d}":[["{h}:00","{h}:59"]]' for d in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]) + "}'")
code, pick, _ = sql(f"select to_char(date_trunc('hour', now() + interval '3 hours') + interval '15 minutes', 'YYYY-MM-DD\"T\"HH24:MI:SSOF')")
expect_error("takeaway refused while closed", dict(base, mode="takeaway", pickup_at=pick, phone="0122222222", lines=[{"item": "latte", "qty": 1}]), "closed")
admin("update settings set takeaway_preorder = true")
res, err = order(dict(base, mode="takeaway", pickup_at=pick, phone="0122222222", lines=[{"item": "latte", "qty": 1}]))
ok("takeaway pre-order allowed when switched on", res is not None, err)
admin("update settings set takeaway_preorder = false, hours = '{\"mon\":[[\"00:00\",\"00:00\"]],\"tue\":[[\"00:00\",\"00:00\"]],\"wed\":[[\"00:00\",\"00:00\"]],"
      "\"thu\":[[\"00:00\",\"00:00\"]],\"fri\":[[\"00:00\",\"00:00\"]],\"sat\":[[\"00:00\",\"00:00\"]],\"sun\":[[\"00:00\",\"00:00\"]]}'")
code, far, _ = sql("select to_char(now() + interval '13 hours', 'YYYY-MM-DD\"T\"HH24:MI:SSOF')")
expect_error("pickup more than 12 h ahead refused", dict(base, mode="takeaway", pickup_at=far, phone="0123333333", lines=[{"item": "latte", "qty": 1}]), "bad_pickup_time")

# --- staff
staff_id, other_id = str(uuid.uuid4()), str(uuid.uuid4())
admin(f"insert into auth.users values ('{staff_id}'), ('{other_id}'); insert into staff (user_id) values ('{staff_id}')")
code, out, err = sql("select count(*) from orders", "authenticated", staff_id)
ok("staff can read orders", code == 0 and int(out) >= 2, err)
code, out, err = sql("select count(*) from orders", "authenticated", other_id)
ok("signed-in non-staff sees no orders", code == 0 and out == "0", out or err)
code, out, err = sql("update orders set status = 'preparing', payment_status = 'paid' returning status", "authenticated", staff_id)
ok("staff can change status/payment", code == 0 and "preparing" in out, err)
code, out, err = sql("update orders set total_sen = 1", "authenticated", staff_id)
ok("staff cannot change totals", code != 0 and "permission denied" in err, out)
code, out, err = sql("update items set sold_out = true where id = 'mocha' returning id", "authenticated", staff_id)
ok("staff can mark sold out", code == 0 and out.startswith("mocha"), err)
code, out, err = sql("update items set price_sen = 1 where id = 'mocha' returning id", "authenticated", other_id)
ok("non-staff cannot edit menu", code == 0 and out in ("", "UPDATE 0"), out or err)
code, out, err = sql("update settings set accepting_orders = false returning accepting_orders", "authenticated", staff_id)
ok("staff can pause orders", code == 0 and out.startswith("f"), err)
admin("update settings set accepting_orders = true; update items set sold_out = false")
for stmt, what in (("update settings set halal_cert = '{\"number\":\"X\",\"expires\":\"2099-01-01\"}'", "halal certificate"),
                   ("update settings set payment = '{\"counter\":true,\"online\":true}'", "payment methods"),
                   ("update items set name = '{\"en\":\"Free\"}' where id = 'latte'", "item names"),
                   ("insert into items (id, category_id, name, price_sen) values ('x', 'tea', '{}', 1)", "new items")):
    code, out, err = sql(stmt, "authenticated", staff_id)
    ok(f"staff cannot change {what}", code != 0 and "permission denied" in err, out or err)
code, out, err = sql("update options set price_sen = 160, sold_out = true where group_id = 'toppings' and id = 'pearl' returning id", "authenticated", staff_id)
ok("staff can change option price / sold out", code == 0 and out.startswith("pearl"), err)
code, out, err = sql("update settings set closed_dates = '{2026-12-25}', prep_minutes = 12 returning prep_minutes", "authenticated", staff_id)
ok("staff can change hours-type settings", code == 0 and out.startswith("12"), err)

# re-running the seed keeps what staff changed; --overwrite resets it
import os
site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "order-site")
admin("update items set price_sen = 1111, sold_out = true where id = 'latte'")
for flag, want in (("", "1111|t|12"), ("--overwrite", "990|f|10")):
    seed = subprocess.run(["python3", os.path.join(site, "tools", "menu_tool.py"), "sql"] + ([flag] if flag else []) +
                          [os.path.join(site, "menu.sample.json")], capture_output=True, text=True).stdout
    r = subprocess.run(PG + ["-q"], input=seed, capture_output=True, text=True)
    code, out, _ = sql("select i.price_sen || '|' || case when i.sold_out then 't' else 'f' end || '|' || s.prep_minutes from items i, settings s where i.id = 'latte'")
    ok(f"seed {flag or '(normal)'} -> {want}", r.returncode == 0 and out == want, (out, r.stderr[-300:]))

code, out, err = sql("delete from orders", "authenticated", staff_id)
ok("staff cannot delete orders", code != 0 and "permission denied" in err, out)

print(f"\n{len(FAIL)} failed" if FAIL else "\nall passed")
sys.exit(1 if FAIL else 0)
