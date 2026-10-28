-- Ordering site schema for Supabase (Postgres 15+).
-- Run once in the SQL editor, then load the menu with `python tools/menu_tool.py sql menu.json > seed.sql`.
-- Security model:
--   * anon (the public site) may READ the menu and settings, and may only CREATE orders through
--     public.place_order(), which recalculates every price on the server. It can never read orders,
--     except one order's status through public.order_status(token).
--   * staff are signed-in users listed in public.staff; they read/update orders and edit the menu.
-- Money is stored as integer sen (RM 1.00 = 100) so the site and the database round the same way.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------- menu
create table public.settings (
  id int primary key default 1 check (id = 1),
  name jsonb not null,                       -- {"en": "...", "zh": "...", "ms": "..."}
  tagline jsonb not null default '{}',
  currency text not null default 'RM',
  timezone text not null default 'Asia/Kuala_Lumpur',
  languages text[] not null default '{en,zh,ms}',
  halal_cert jsonb,                          -- null, or {"number": "...", "expires": "YYYY-MM-DD"}; only then may the site say "halal"
  sst_rate numeric(5,4) not null default 0 check (sst_rate between 0 and 0.2),
  sst_reg_no text,                           -- Customs SST registration number; SST cannot be switched on without it
  service_charge_rate numeric(5,4) not null default 0 check (service_charge_rate between 0 and 0.2),
  sst_on_service_charge boolean not null default true,
  service_charge_takeaway boolean not null default false,   -- most shops charge service only for dine-in
  round_cash_to_5sen boolean not null default true,
  prep_minutes int not null default 10 check (prep_minutes between 0 and 240),
  slot_minutes int not null default 15 check (slot_minutes between 5 and 120),
  max_tables int not null default 20 check (max_tables between 0 and 500),
  dine_in boolean not null default true,
  takeaway boolean not null default true,
  payment jsonb not null default '{"counter": true, "duitnow_qr": true, "online": false}',
  hours jsonb not null,                      -- {"mon": [["10:00","22:00"]], ..., "sun": []}; close <= open means past midnight
  closed_dates date[] not null default '{}', -- public holidays and other days off, in shop-local dates
  accepting_orders boolean not null default true,  -- staff "pause orders" switch
  constraint sst_needs_registration check (sst_rate = 0 or coalesce(btrim(sst_reg_no), '') <> '')
);

create table public.categories (
  id text primary key check (id ~ '^[a-z0-9_-]{1,40}$'),
  label jsonb not null,
  sort int not null default 0
);

create table public.option_groups (
  id text primary key check (id ~ '^[a-z0-9_-]{1,40}$'),
  label jsonb not null,
  type text not null check (type in ('single', 'multi')),
  required boolean not null default false,
  default_option text,
  max_total int check (max_total is null or max_total between 1 and 50),
  sort int not null default 0
);

create table public.options (
  group_id text not null references public.option_groups(id) on delete cascade,
  id text not null check (id ~ '^[a-z0-9_-]{1,40}$'),
  label jsonb not null,
  price_sen int not null default 0 check (price_sen between 0 and 100000),
  max_qty int not null default 1 check (max_qty between 1 and 20),
  sold_out boolean not null default false,
  sort int not null default 0,
  primary key (group_id, id)
);

create table public.items (
  id text primary key check (id ~ '^[a-z0-9_-]{1,40}$'),
  category_id text not null references public.categories(id),
  name jsonb not null,
  description jsonb not null default '{}',
  price_sen int not null check (price_sen between 0 and 1000000),
  color text check (color is null or color ~ '^#[0-9a-fA-F]{6}$'),
  image_url text,
  allergens text[] not null default '{}',
  dietary text[] not null default '{}',
  featured boolean not null default false,
  sold_out boolean not null default false,
  active boolean not null default true,
  sort int not null default 0
);

create table public.item_groups (
  item_id text not null references public.items(id) on delete cascade,
  group_id text not null references public.option_groups(id) on delete cascade,
  sort int not null default 0,
  primary key (item_id, group_id)
);

-- ---------------------------------------------------------------- staff
create table public.staff (
  user_id uuid primary key references auth.users(id) on delete cascade,
  display_name text
);

create or replace function public.is_staff() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.staff where user_id = auth.uid());
$$;

-- ---------------------------------------------------------------- orders
create table public.order_counters (day date primary key, n int not null);

create table public.orders (
  id uuid primary key default gen_random_uuid(),
  token uuid not null unique default gen_random_uuid(),   -- the customer's private status link
  client_ref uuid unique,                   -- sent by the page; a retried request returns the same order instead of a duplicate
  order_no text not null,
  order_day date not null,
  created_at timestamptz not null default now(),
  mode text not null check (mode in ('dine_in', 'takeaway')),
  table_no int,
  pickup_at timestamptz,
  customer_name text not null,
  phone text,
  notes text,
  lang text not null default 'en',
  lines jsonb not null,                     -- server-built: [{item, name, qty, options:[...], unit_sen, line_sen}]
  subtotal_sen int not null,
  service_sen int not null,
  sst_sen int not null,
  total_sen int not null,
  cash_total_sen int not null,              -- total rounded to 5 sen for over-the-counter cash, if enabled
  payment_method text not null check (payment_method in ('counter', 'duitnow_qr', 'online')),
  payment_status text not null default 'unpaid' check (payment_status in ('unpaid', 'paid', 'refunded')),
  status text not null default 'new' check (status in ('new', 'preparing', 'ready', 'collected', 'cancelled')),
  staff_note text,
  consent boolean not null check (consent)
);
create index orders_day_idx on public.orders (order_day, created_at desc);
create index orders_phone_idx on public.orders (phone, created_at desc);

-- ---------------------------------------------------------------- helpers
create or replace function public.round_5sen(sen int) returns int
language sql immutable set search_path = '' as $$
  -- Bank Negara rounding of the total bill: last digit 1,2,6,7 down; 3,4,8,9 up.
  select case when sen % 5 <= 2 then sen - sen % 5 else sen + (5 - sen % 5) end;
$$;

create or replace function public.shop_is_open(at_time timestamptz) returns boolean
language plpgsql stable security definer set search_path = '' as $$
declare
  s public.settings;
  local_ts timestamp;
  win jsonb;
  d int;
  day_key text;
  t time;
  o time;
  c time;
begin
  select * into s from public.settings where id = 1;
  local_ts := at_time at time zone s.timezone;
  t := local_ts::time;
  for d in 0..1 loop   -- today's windows, then yesterday's windows that run past midnight
    if (local_ts - make_interval(days => d))::date = any(s.closed_dates) then continue; end if;
    day_key := lower(to_char(local_ts - make_interval(days => d), 'Dy'));
    for win in select * from jsonb_array_elements(coalesce(s.hours -> day_key, '[]'::jsonb)) loop
      o := (win ->> 0)::time;
      c := (win ->> 1)::time;
      if d = 0 and c > o and t >= o and t < c then return true; end if;
      if d = 0 and c <= o and t >= o then return true; end if;
      if d = 1 and c <= o and t < c then return true; end if;
    end loop;
  end loop;
  return false;
end;
$$;

-- what place_order returns to the customer's page
create or replace function public.order_result(rec public.orders) returns jsonb
language sql immutable set search_path = '' as $$
  select jsonb_build_object('order_no', rec.order_no, 'token', rec.token, 'status', rec.status,
    'payment_method', rec.payment_method, 'subtotal_sen', rec.subtotal_sen, 'service_sen', rec.service_sen,
    'sst_sen', rec.sst_sen, 'total_sen', rec.total_sen, 'cash_total_sen', rec.cash_total_sen,
    'mode', rec.mode, 'table_no', rec.table_no, 'pickup_at', rec.pickup_at, 'lines', rec.lines);
$$;

-- PDPA: keep order records for the books, but blank names, phones and notes after `days` days.
-- Schedule it daily with pg_cron (Dashboard > Integrations > Cron), e.g.
--   select cron.schedule('purge-personal-data', '15 3 * * *', $c$select public.purge_personal_data(90)$c$);
create or replace function public.purge_personal_data(days int default 90) returns int
language sql volatile security definer set search_path = '' as $$
  with done as (
    update public.orders set customer_name = '-', phone = null, notes = null
    where created_at < now() - make_interval(days => greatest(days, 1)) and customer_name <> '-'
    returning 1)
  select count(*)::int from done;
$$;

-- ---------------------------------------------------------------- place_order (the only way to create an order)
create or replace function public.place_order(p jsonb) returns jsonb
language plpgsql volatile security definer set search_path = '' as $$
declare
  s public.settings;
  now_ts timestamptz := now();
  v_mode text := p ->> 'mode';
  v_table int;
  v_pickup timestamptz;
  v_name text := btrim(coalesce(p ->> 'name', ''));
  v_phone text := nullif(regexp_replace(coalesce(p ->> 'phone', ''), '[^0-9+]', '', 'g'), '');
  v_notes text := nullif(btrim(coalesce(p ->> 'notes', '')), '');
  v_pay text := p ->> 'payment';
  v_lang text := coalesce(nullif(p ->> 'lang', ''), 'en');
  v_ref uuid;
  ln jsonb;
  it public.items;
  g record;
  opt public.options;
  chosen text;
  qty int;
  multi_total int;
  unit int;
  out_opts jsonb;
  out_lines jsonb := '[]'::jsonb;
  subtotal int := 0;
  service int;
  sst int;
  total int;
  n int;
  v_day date;
  v_no text;
  rec public.orders;
begin
  -- same client_ref as an order already placed (the network dropped the first reply): return that order
  if coalesce(p ->> 'client_ref', '') ~ '^[0-9a-fA-F-]{36}$' then
    v_ref := (p ->> 'client_ref')::uuid;
    select * into rec from public.orders where client_ref = v_ref;
    if rec.id is not null then return public.order_result(rec); end if;
  end if;

  select * into s from public.settings where id = 1;
  if s is null then raise exception 'not_configured'; end if;
  if not s.accepting_orders then raise exception 'paused'; end if;
  if coalesce((p ->> 'consent')::boolean, false) is not true then raise exception 'consent_required'; end if;
  if v_pay is null or coalesce((s.payment ->> v_pay)::boolean, false) is not true then raise exception 'payment_not_allowed'; end if;
  if char_length(v_name) not between 1 and 60 then raise exception 'bad_name'; end if;
  if v_phone is not null and v_phone !~ '^\+?[0-9]{8,15}$' then raise exception 'bad_phone'; end if;
  if v_notes is not null and char_length(v_notes) > 200 then raise exception 'notes_too_long'; end if;
  if v_lang not in ('en', 'zh', 'ms') then v_lang := 'en'; end if;

  if v_mode = 'dine_in' then
    if not s.dine_in then raise exception 'mode_not_allowed'; end if;
    v_table := (p ->> 'table')::int;
    if v_table is null or v_table < 1 or v_table > s.max_tables then raise exception 'bad_table'; end if;
    if not public.shop_is_open(now_ts) then raise exception 'closed'; end if;
  elsif v_mode = 'takeaway' then
    if not s.takeaway then raise exception 'mode_not_allowed'; end if;
    if v_phone is null then raise exception 'phone_required'; end if;
    v_pickup := (p ->> 'pickup_at')::timestamptz;
    if v_pickup is null
       or v_pickup < now_ts + make_interval(mins => s.prep_minutes) - interval '2 minutes'
       or v_pickup > now_ts + interval '24 hours'
       or not public.shop_is_open(v_pickup) then
      raise exception 'bad_pickup_time';
    end if;
  else
    raise exception 'bad_mode';
  end if;

  -- simple flood protection (see references for Turnstile when this is not enough)
  if v_phone is not null and (select count(*) from public.orders
      where phone = v_phone and created_at > now_ts - interval '10 minutes') >= 5 then
    raise exception 'too_many_orders';
  end if;
  if (select count(*) from public.orders where created_at > now_ts - interval '1 minute') >= 60 then
    raise exception 'busy';
  end if;

  if jsonb_typeof(p -> 'lines') is distinct from 'array'
     or jsonb_array_length(p -> 'lines') not between 1 and 30 then
    raise exception 'bad_lines';
  end if;

  for ln in select * from jsonb_array_elements(p -> 'lines') loop
    select * into it from public.items where id = ln ->> 'item' and active;
    if it is null then raise exception 'unknown_item'; end if;
    if it.sold_out then raise exception 'sold_out:%', it.id; end if;
    qty := coalesce((ln ->> 'qty')::int, 0);
    if qty not between 1 and 20 then raise exception 'bad_qty'; end if;
    -- options may only name groups this item has
    if exists (select 1 from jsonb_object_keys(coalesce(ln -> 'options', '{}'::jsonb)) k
               where k not in (select group_id from public.item_groups where item_id = it.id)) then
      raise exception 'bad_option';
    end if;

    unit := it.price_sen;
    out_opts := '[]'::jsonb;
    for g in select og.* from public.item_groups ig join public.option_groups og on og.id = ig.group_id
             where ig.item_id = it.id order by ig.sort, og.sort loop
      if g.type = 'single' then
        chosen := coalesce(ln -> 'options' ->> g.id, g.default_option);
        if chosen is null then
          if g.required then raise exception 'missing_option:%', g.id; end if;
          continue;
        end if;
        select * into opt from public.options where group_id = g.id and id = chosen;
        if opt is null then raise exception 'bad_option'; end if;
        if opt.sold_out then raise exception 'sold_out:%', g.id || '.' || opt.id; end if;
        unit := unit + opt.price_sen;
        out_opts := out_opts || jsonb_build_object('group', g.id, 'option', opt.id, 'label', opt.label, 'qty', 1, 'price_sen', opt.price_sen);
      else
        multi_total := 0;
        if jsonb_typeof(coalesce(ln -> 'options' -> g.id, '{}'::jsonb)) <> 'object' then raise exception 'bad_option'; end if;
        for chosen, qty in select key, value::int from jsonb_each_text(coalesce(ln -> 'options' -> g.id, '{}'::jsonb)) loop
          if qty = 0 then continue; end if;
          select * into opt from public.options where group_id = g.id and id = chosen;
          if opt is null or qty < 0 or qty > opt.max_qty then raise exception 'bad_option'; end if;
          if opt.sold_out then raise exception 'sold_out:%', g.id || '.' || opt.id; end if;
          multi_total := multi_total + qty;
          unit := unit + opt.price_sen * qty;
          out_opts := out_opts || jsonb_build_object('group', g.id, 'option', opt.id, 'label', opt.label, 'qty', qty, 'price_sen', opt.price_sen);
        end loop;
        if g.max_total is not null and multi_total > g.max_total then raise exception 'too_many_toppings'; end if;
        qty := coalesce((ln ->> 'qty')::int, 0);   -- restore the line quantity used by the loop variable
      end if;
    end loop;

    subtotal := subtotal + unit * qty;
    out_lines := out_lines || jsonb_build_object('item', it.id, 'name', it.name, 'qty', qty,
                                                 'options', out_opts, 'unit_sen', unit, 'line_sen', unit * qty);
  end loop;

  service := case when v_mode = 'takeaway' and not s.service_charge_takeaway then 0
                  else round(subtotal * s.service_charge_rate)::int end;
  sst := round((subtotal + case when s.sst_on_service_charge then service else 0 end) * s.sst_rate)::int;
  total := subtotal + service + sst;

  v_day := (now_ts at time zone s.timezone)::date;
  insert into public.order_counters as oc (day, n) values (v_day, 1)
    on conflict (day) do update set n = oc.n + 1 returning oc.n into n;
  v_no := 'A' || lpad(n::text, 3, '0');

  insert into public.orders (client_ref, order_no, order_day, mode, table_no, pickup_at, customer_name, phone, notes, lang,
                             lines, subtotal_sen, service_sen, sst_sen, total_sen, cash_total_sen, payment_method, consent)
  values (v_ref, v_no, v_day, v_mode, v_table, v_pickup, v_name, v_phone, v_notes, v_lang, out_lines, subtotal, service, sst,
          total, case when s.round_cash_to_5sen then public.round_5sen(total) else total end, v_pay, true)
  returning * into rec;

  return public.order_result(rec);
end;
$$;

-- one order's status, for the customer's confirmation screen (the token is the secret)
create or replace function public.order_status(p_token uuid) returns jsonb
language sql stable security definer set search_path = '' as $$
  select jsonb_build_object('order_no', order_no, 'status', status, 'payment_status', payment_status,
           'payment_method', payment_method, 'total_sen', total_sen, 'cash_total_sen', cash_total_sen,
           'mode', mode, 'table_no', table_no, 'pickup_at', pickup_at, 'created_at', created_at)
  from public.orders where token = p_token;
$$;

-- ---------------------------------------------------------------- privileges and row level security
-- Postgres grants EXECUTE on new functions to PUBLIC; take it back and grant only what the site needs.
revoke execute on all functions in schema public from public, anon, authenticated;
grant execute on function public.place_order(jsonb), public.order_status(uuid) to anon, authenticated;
grant execute on function public.is_staff(), public.shop_is_open(timestamptz), public.round_5sen(int) to anon, authenticated;

alter table public.settings enable row level security;
alter table public.categories enable row level security;
alter table public.option_groups enable row level security;
alter table public.options enable row level security;
alter table public.items enable row level security;
alter table public.item_groups enable row level security;
alter table public.staff enable row level security;
alter table public.orders enable row level security;
alter table public.order_counters enable row level security;

revoke all on all tables in schema public from anon, authenticated;

-- public menu (read only)
grant select on public.settings, public.categories, public.option_groups, public.options, public.items, public.item_groups to anon, authenticated;
create policy menu_read on public.settings for select to anon, authenticated using (true);
create policy menu_read on public.categories for select to anon, authenticated using (true);
create policy menu_read on public.option_groups for select to anon, authenticated using (true);
create policy menu_read on public.options for select to anon, authenticated using (true);
create policy menu_read on public.items for select to anon, authenticated using (active or public.is_staff());
create policy menu_read on public.item_groups for select to anon, authenticated using (true);

-- staff edit the menu (no deletes: hide items with active = false)
grant update on public.settings, public.categories, public.option_groups, public.options, public.items to authenticated;
grant insert on public.categories, public.option_groups, public.options, public.items, public.item_groups to authenticated;
grant delete on public.item_groups to authenticated;
create policy staff_edit on public.settings for update to authenticated using (public.is_staff()) with check (public.is_staff());
create policy staff_edit on public.categories for all to authenticated using (public.is_staff()) with check (public.is_staff());
create policy staff_edit on public.option_groups for all to authenticated using (public.is_staff()) with check (public.is_staff());
create policy staff_edit on public.options for all to authenticated using (public.is_staff()) with check (public.is_staff());
create policy staff_edit on public.items for all to authenticated using (public.is_staff()) with check (public.is_staff());
create policy staff_edit on public.item_groups for all to authenticated using (public.is_staff()) with check (public.is_staff());

-- staff see and move orders; only status, payment and a note can change
grant select on public.orders to authenticated;
grant update (status, payment_status, staff_note) on public.orders to authenticated;
create policy staff_orders_read on public.orders for select to authenticated using (public.is_staff());
create policy staff_orders_update on public.orders for update to authenticated using (public.is_staff()) with check (public.is_staff());

-- staff may see who is staff (to show names); adding staff is done by the owner in the SQL editor
grant select on public.staff to authenticated;
create policy staff_read on public.staff for select to authenticated using (public.is_staff());
