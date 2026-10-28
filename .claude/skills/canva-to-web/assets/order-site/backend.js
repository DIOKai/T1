/* Data layer shared by the customer page (index.html) and the staff page (staff.html).
   Backend.create() returns the Supabase backend when config.js has a URL and key, otherwise a demo
   backend that keeps everything in localStorage so the whole flow can be tried without an account.
   Both return the same shapes; errors are thrown as Error(code) using the codes raised by
   supabase/schema.sql (closed, paused, sold_out:<id>, bad_pickup_time, ...). */
(function (global) {
  'use strict';
  const P = global.Pricing;

  // ------------------------------------------------------------ menu shape used by the pages
  // { settings, categories:[{id,label}], groups:{gid:{id,label,type,required,default_option,max_total,
  //   options:[{id,label,price_sen,max_qty,sold_out}]}}, items:[{id,category_id,name,description,price_sen,
  //   color,image_url,allergens,dietary,featured,sold_out,groups:[gid]}] }

  function fromFile(json) {
    const shop = json.shop;
    const settings = Object.assign({}, shop, {
      halal_cert: shop.halal_cert || null,
      accepting_orders: shop.accepting_orders !== false
    });
    const groups = {};
    (json.option_groups || []).forEach((g, gi) => {
      groups[g.id] = {
        id: g.id, label: g.label, type: g.type, required: !!g.required, default_option: g.default || null,
        max_total: g.max_total || null, sort: gi,
        options: g.options.map((o) => ({ id: o.id, label: o.label, price_sen: P.toSen(o.price || 0), max_qty: o.max || 1, sold_out: !!o.sold_out }))
      };
    });
    return {
      settings,
      categories: json.categories.map((c) => ({ id: c.id, label: c.label })),
      groups,
      items: json.items.filter((i) => i.active !== false).map((i) => ({
        id: i.id, category_id: i.category, name: i.name, description: i.desc || {}, price_sen: P.toSen(i.price),
        color: i.color || null, image_url: i.image || null, allergens: i.allergens || [], dietary: i.dietary || [],
        featured: !!i.featured, sold_out: !!i.sold_out, groups: i.groups || []
      }))
    };
  }

  function fromRows(r) {
    const s = r.settings[0];
    if (!s) throw new Error('not_configured');
    const settings = Object.assign({}, s, { sst_rate: Number(s.sst_rate), service_charge_rate: Number(s.service_charge_rate) });
    const groups = {};
    r.option_groups.sort((a, b) => a.sort - b.sort).forEach((g) => { groups[g.id] = Object.assign({}, g, { options: [] }); });
    r.options.sort((a, b) => a.sort - b.sort).forEach((o) => { if (groups[o.group_id]) groups[o.group_id].options.push(o); });
    const byItem = {};
    r.item_groups.sort((a, b) => a.sort - b.sort).forEach((ig) => { (byItem[ig.item_id] = byItem[ig.item_id] || []).push(ig.group_id); });
    return {
      settings,
      categories: r.categories.sort((a, b) => a.sort - b.sort),
      groups,
      items: r.items.filter((i) => i.active).sort((a, b) => a.sort - b.sort).map((i) => Object.assign({}, i, { groups: byItem[i.id] || [] }))
    };
  }

  // ------------------------------------------------------------ Supabase (PostgREST + Auth over fetch)
  function SupabaseBackend(cfg) {
    const base = cfg.supabaseUrl.replace(/\/+$/, '');
    const key = cfg.publishableKey;
    const SESSION = 'order-site-staff-session';
    let session = null;
    try { session = JSON.parse(localStorage.getItem(SESSION) || 'null'); } catch (e) { session = null; }

    function saveSession(s) {
      session = s;
      try { s ? localStorage.setItem(SESSION, JSON.stringify(s)) : localStorage.removeItem(SESSION); } catch (e) { /* private mode */ }
    }

    function headers(extra) {
      const h = { apikey: key, 'Content-Type': 'application/json' };
      // As in Supabase's REST examples: the key goes in both headers for public calls; a signed-in staff
      // member's token replaces it in Authorization, which makes PostgREST use the `authenticated` role.
      h.Authorization = 'Bearer ' + (session && session.access_token ? session.access_token : key);
      return Object.assign(h, extra || {});
    }

    async function refreshIfNeeded() {
      if (!session || !session.refresh_token) return;
      if (Date.now() < (session.expires_at - 60) * 1000) return;
      const res = await fetch(base + '/auth/v1/token?grant_type=refresh_token', {
        method: 'POST', headers: { apikey: key, 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: session.refresh_token })
      });
      if (!res.ok) { saveSession(null); throw new Error('signed_out'); }
      const j = await res.json();
      saveSession({ access_token: j.access_token, refresh_token: j.refresh_token, expires_at: j.expires_at || Math.floor(Date.now() / 1000) + j.expires_in, email: session.email });
    }

    async function call(path, opts) {
      await refreshIfNeeded();
      let res;
      try {
        res = await fetch(base + '/rest/v1/' + path, Object.assign({}, opts, { headers: headers((opts || {}).headers) }));
      } catch (e) { throw new Error('network'); }
      const text = await res.text();
      const body = text ? JSON.parse(text) : null;
      if (!res.ok) {
        // place_order raises plain messages such as "sold_out:lemon"; PostgREST puts them in `message`
        const msg = (body && body.message) || 'http_' + res.status;
        if (res.status === 401 && session) saveSession(null);
        throw new Error(/^[a-z_]+(:[a-z0-9_.-]+)?$/.test(msg) ? msg : (res.status === 401 || res.status === 403 ? 'forbidden' : 'generic'));
      }
      return body;
    }

    const get = (path) => call(path, { method: 'GET' });
    const rpc = (fn, args) => call('rpc/' + fn, { method: 'POST', body: JSON.stringify(args) });
    async function patch(path, values) {
      const rows = await call(path, { method: 'PATCH', headers: { Prefer: 'return=representation' }, body: JSON.stringify(values) });
      // RLS hides rows from non-staff, so an update that matched nothing means "not allowed"
      if (!rows || !rows.length) throw new Error('forbidden');
      return rows[0];
    }

    return {
      demo: false,
      async getMenu() {
        const [settings, categories, option_groups, options, items, item_groups] = await Promise.all(
          ['settings', 'categories', 'option_groups', 'options', 'items', 'item_groups'].map((t) => get(t + '?select=*')));
        return fromRows({ settings, categories, option_groups, options, items, item_groups });
      },
      placeOrder: (payload) => rpc('place_order', { p: payload }),
      orderStatus: (token) => rpc('order_status', { p_token: token }),

      // staff
      async signIn(email, password) {
        const res = await fetch(base + '/auth/v1/token?grant_type=password', {
          method: 'POST', headers: { apikey: key, 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password })
        }).catch(() => { throw new Error('network'); });
        if (!res.ok) throw new Error('bad_login');
        const j = await res.json();
        saveSession({ access_token: j.access_token, refresh_token: j.refresh_token, expires_at: j.expires_at || Math.floor(Date.now() / 1000) + j.expires_in, email });
        const isStaff = await rpc('is_staff', {});
        if (!isStaff) { saveSession(null); throw new Error('not_staff'); }
      },
      signOut() { saveSession(null); },
      signedIn: () => !!session,
      staffEmail: () => (session && session.email) || '',
      listOrders(sinceIso) {
        return get('orders?select=*&created_at=gte.' + encodeURIComponent(sinceIso) + '&order=created_at.asc');
      },
      updateOrder: (id, values) => patch('orders?id=eq.' + encodeURIComponent(id), values),
      updateItem: (id, values) => patch('items?id=eq.' + encodeURIComponent(id), values),
      updateOption: (gid, oid, values) => patch('options?group_id=eq.' + encodeURIComponent(gid) + '&id=eq.' + encodeURIComponent(oid), values),
      updateSettings: (values) => patch('settings?id=eq.1', values)
    };
  }

  // ------------------------------------------------------------ demo (localStorage, same rules as place_order)
  function DemoBackend(cfg) {
    const KEY = 'order-site-demo-v2';
    let base = null;

    function load() {
      try { return JSON.parse(localStorage.getItem(KEY) || 'null') || { orders: [], counters: {}, items: {}, options: {}, settings: {} }; }
      catch (e) { return { orders: [], counters: {}, items: {}, options: {}, settings: {} }; }
    }
    function save(db) { try { localStorage.setItem(KEY, JSON.stringify(db)); } catch (e) { /* storage full or blocked */ } }

    async function menu() {
      if (!base) {
        const res = await fetch(cfg.menuFile || 'menu.sample.json').catch(() => { throw new Error('network'); });
        if (!res.ok) throw new Error('network');
        base = fromFile(await res.json());
      }
      // apply staff edits saved in this browser
      const db = load();
      const m = JSON.parse(JSON.stringify(base));
      Object.assign(m.settings, db.settings);
      m.items.forEach((i) => Object.assign(i, db.items[i.id] || {}));
      Object.values(m.groups).forEach((g) => g.options.forEach((o) => Object.assign(o, db.options[g.id + '.' + o.id] || {})));
      return m;
    }

    function localDay(date, tz) {
      return new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(date);
    }

    async function placeOrder(p) {
      const m = await menu();
      const s = m.settings;
      const now = new Date();
      const fail = (code) => { throw new Error(code); };
      const name = String(p.name || '').trim();
      const phone = String(p.phone || '').replace(/[^0-9+]/g, '') || null;
      const notes = String(p.notes || '').trim() || null;
      if (!s.accepting_orders) fail('paused');
      if (p.consent !== true) fail('consent_required');
      if (!p.payment || !(s.payment || {})[p.payment]) fail('payment_not_allowed');
      if (name.length < 1 || name.length > 60) fail('bad_name');
      if (phone && !/^\+?[0-9]{8,15}$/.test(phone)) fail('bad_phone');
      if (notes && notes.length > 200) fail('notes_too_long');
      let table = null, pickup = null;
      if (p.mode === 'dine_in') {
        if (!s.dine_in) fail('mode_not_allowed');
        table = parseInt(p.table, 10);
        if (!(table >= 1 && table <= s.max_tables)) fail('bad_table');
        if (!P.isOpen(s, now)) fail('closed');
      } else if (p.mode === 'takeaway') {
        if (!s.takeaway) fail('mode_not_allowed');
        if (!phone) fail('phone_required');
        pickup = p.pickup_at ? new Date(p.pickup_at) : null;
        if (!pickup || isNaN(pickup) || pickup < new Date(now.getTime() + (s.prep_minutes - 2) * 60000) ||
            pickup > new Date(now.getTime() + 24 * 3600000) || !P.isOpen(s, pickup)) fail('bad_pickup_time');
      } else fail('bad_mode');

      const db = load();
      const again = p.client_ref && db.orders.find((o) => o.client_ref === p.client_ref);
      if (again) return again;
      if (phone && db.orders.filter((o) => o.phone === phone && now - new Date(o.created_at) < 600000).length >= 5) fail('too_many_orders');
      if (!Array.isArray(p.lines) || p.lines.length < 1 || p.lines.length > 30) fail('bad_lines');

      const lines = p.lines.map((ln) => {
        const it = m.items.find((i) => i.id === ln.item);
        if (!it) fail('unknown_item');
        if (it.sold_out) fail('sold_out:' + it.id);
        if (!(ln.qty >= 1 && ln.qty <= 20 && Number.isInteger(ln.qty))) fail('bad_qty');
        if (Object.keys(ln.options || {}).some((k) => !it.groups.includes(k))) fail('bad_option');
        const opts = [];
        for (const gid of it.groups) {
          const g = m.groups[gid];
          const pick = (ln.options || {})[gid];
          if (g.type === 'single') {
            const oid = pick || g.default_option;
            if (!oid) { if (g.required) fail('missing_option:' + gid); continue; }
            const o = g.options.find((x) => x.id === oid) || fail('bad_option');
            if (o.sold_out) fail('sold_out:' + gid + '.' + o.id);
            opts.push({ group: gid, option: o.id, label: o.label, qty: 1, price_sen: o.price_sen });
          } else {
            for (const [oid, q] of Object.entries(pick || {})) {
              if (!q) continue;
              const o = g.options.find((x) => x.id === oid);
              if (!o || q < 0 || q > o.max_qty) fail('bad_option');
              if (o.sold_out) fail('sold_out:' + gid + '.' + o.id);
              opts.push({ group: gid, option: o.id, label: o.label, qty: q, price_sen: o.price_sen });
            }
          }
        }
        let unit;
        try { unit = P.unitPrice(m, it.id, ln.options); } catch (e) { fail(e.message); }
        return { item: it.id, name: it.name, qty: ln.qty, options: opts, unit_sen: unit, line_sen: unit * ln.qty };
      });

      const t = P.totals(m, p.lines, p.mode);
      const day = localDay(now, s.timezone);
      db.counters[day] = (db.counters[day] || 0) + 1;
      const order = {
        id: crypto.randomUUID(), token: crypto.randomUUID(), client_ref: p.client_ref || null, order_no: 'A' + String(db.counters[day]).padStart(3, '0'),
        order_day: day, created_at: now.toISOString(), mode: p.mode, table_no: table, pickup_at: pickup && pickup.toISOString(),
        customer_name: name, phone, notes, lang: p.lang || 'en', lines, subtotal_sen: t.subtotal, service_sen: t.service,
        sst_sen: t.sst, total_sen: t.total, cash_total_sen: t.cash, payment_method: p.payment, payment_status: 'unpaid',
        status: 'new', staff_note: null, consent: true
      };
      db.orders.push(order);
      save(db);
      return order;
    }

    function setOverride(bucket, id, values) {
      const db = load();
      db[bucket][id] = Object.assign(db[bucket][id] || {}, values);
      save(db);
    }

    return {
      demo: true,
      getMenu: menu,
      placeOrder,
      async orderStatus(token) {
        const o = load().orders.find((x) => x.token === token);
        return o ? { order_no: o.order_no, status: o.status, payment_status: o.payment_status, payment_method: o.payment_method,
          total_sen: o.total_sen, cash_total_sen: o.cash_total_sen, mode: o.mode, table_no: o.table_no, pickup_at: o.pickup_at, created_at: o.created_at } : null;
      },
      async signIn() { /* demo: no accounts */ },
      signOut() {},
      signedIn: () => true,
      staffEmail: () => 'demo',
      async listOrders(sinceIso) { return load().orders.filter((o) => o.created_at >= sinceIso); },
      async updateOrder(id, values) {
        const db = load();
        const o = db.orders.find((x) => x.id === id);
        if (!o) throw new Error('forbidden');
        ['status', 'payment_status', 'staff_note'].forEach((k) => { if (k in values) o[k] = values[k]; });
        save(db);
        return o;
      },
      async updateItem(id, values) { setOverride('items', id, values); return values; },
      async updateOption(gid, oid, values) { setOverride('options', gid + '.' + oid, values); return values; },
      async updateSettings(values) { const db = load(); Object.assign(db.settings, values); save(db); return values; },
      resetDemo() { try { localStorage.removeItem(KEY); } catch (e) { /* ignore */ } }
    };
  }

  global.Backend = {
    create(cfg) { return cfg.supabaseUrl && cfg.publishableKey ? SupabaseBackend(cfg) : DemoBackend(cfg); },
    fromFile,
    fromRows
  };
})(window);
