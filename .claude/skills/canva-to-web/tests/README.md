# Tests for assets/order-site

Run these after changing the schema, pricing, backend or pages. All local and free: Postgres 16, Node 18+, Python 3, Playwright with Chromium.

| File | What it proves |
|---|---|
| `test_sql.py` | schema.sql security and rules on a real Postgres: anon can only read the menu and call two functions, prices are recalculated on the server, every validation error fires, staff can change only order status/payment/note and the staff-screen settings (not halal, payment methods, names or new items), nobody can delete orders, retries with the same `client_ref` don't duplicate, SST needs a registration number, closed dates, no takeaway while closed unless `takeaway_preorder`, re-running the seed keeps staff edits (`--overwrite` resets), PDPA purge |
| `parity.js` | 175 random carts (dine-in and takeaway, 7 tax settings): `Pricing.totals()` in the page = what `place_order()` charges |
| `hours.js` | 501 timestamps over 8 days with split shifts, past-midnight windows and closed dates: `Pricing.isOpen()` = `shop_is_open()` |
| `flow.js` | demo mode in Chromium: order at a table, toppings limits, option allergens, service charge + SST, consent, staff board, status updates, sold out while in the cart, takeaway in Chinese, DuitNow, closed (dine-in and takeaway) and paused banners in Malay, staff screen in Chinese, trilingual QR cards, 320 px layout, 44 px targets |
| `telegram.mjs` | the Edge Function under Node with a fake Deno + fetch: wrong secret refused, message in zh / en / ms, no phone number, no `parse_mode` |
| `mock.py` + `live.js` | the Supabase branch of backend.js against a small PostgREST look-alike on the real schema + RLS: lost reply then retry gives one order, staff login (wrong password, non-staff, staff), staff edits saved, the public key cannot list orders, headers |

All of these use `menu.sample.json` and its item names: they test the template, not a shop's real menu. Keep the sample menu when running them after a template change.

`mock.py` is not Supabase. Real Supabase was not available when these were written, so the first live run on a real project still needs the checklist in `references/backend-setup.md`.

## Run

```bash
SKILL=path/to/canva-to-web; SITE=$SKILL/assets/order-site; T=$SKILL/tests
# Postgres as the postgres user, socket in its home (scratch dirs may lose permissions)
Q=/var/lib/postgresql/shoptest
su postgres -c "mkdir -p $Q && /usr/lib/postgresql/16/bin/initdb -D $Q/data -A trust -U postgres && \
  /usr/lib/postgresql/16/bin/pg_ctl -D $Q/data -o '-k $Q -p 55432 -c listen_addresses=' -l $Q/log start"
PS="psql -h $Q -p 55432 -U postgres -q"
$PS -d postgres -c "create database shop"
$PS -d shop -f $T/shim.sql                       # fake auth schema + anon/authenticated roles (safe to re-run)
$PS -v ON_ERROR_STOP=1 -d shop -f $SITE/supabase/schema.sql
python3 $SITE/tools/menu_tool.py sql $SITE/menu.sample.json | $PS -d shop
python3 $T/test_sql.py $Q
node $T/parity.js $SITE $Q
node $T/hours.js $SITE $Q

# demo mode in the browser
(cd $SITE && python3 -m http.server 8765 &)
NODE_PATH=$(npm root -g) node $T/flow.js /tmp/shots
node --experimental-strip-types $T/telegram.mjs $SITE      # Node 22+

# live mode through the mock
python3 $T/mock.py $Q 11111111-1111-4111-8111-111111111111 22222222-2222-4222-8222-222222222222 &
$PS -d shop -c "insert into auth.users values ('11111111-1111-4111-8111-111111111111'),('22222222-2222-4222-8222-222222222222');
  insert into staff(user_id) values ('11111111-1111-4111-8111-111111111111');
  update settings set sst_reg_no='W10-TEST', sst_rate=0.06, service_charge_rate=0.10,
    hours='{\"mon\":[[\"00:00\",\"00:00\"]],\"tue\":[[\"00:00\",\"00:00\"]],\"wed\":[[\"00:00\",\"00:00\"]],\"thu\":[[\"00:00\",\"00:00\"]],\"fri\":[[\"00:00\",\"00:00\"]],\"sat\":[[\"00:00\",\"00:00\"]],\"sun\":[[\"00:00\",\"00:00\"]]}'"
cp -r $SITE /tmp/livesite && sed -i "s#supabaseUrl: ''#supabaseUrl: 'http://127.0.0.1:8766'#; s#publishableKey: ''#publishableKey: 'sb_publishable_test'#" /tmp/livesite/config.js
(cd /tmp/livesite && python3 -m http.server 8767 &)
NODE_PATH=$(npm root -g) node $T/live.js $Q /tmp/shots
```

`test_sql.py` and the live test change the data; recreate the database before running them again.
