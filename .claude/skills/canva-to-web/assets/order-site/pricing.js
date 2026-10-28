/* Pricing, rounding and opening hours. Mirrors supabase/schema.sql so the price the customer sees
   is the price the server charges. The server recalculates everything; this is only for display
   (and for the offline demo backend). Money is integer sen. */
(function (global) {
  'use strict';

  const DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];

  const toSen = (rm) => Math.round(Number(rm) * 100);
  // rate * 10000 is exact for rates like 0.06 or 0.10; integer maths rounds half up like Postgres round()
  const applyRate = (sen, rate) => Math.floor((sen * Math.round(rate * 10000) + 5000) / 10000);
  // Bank Negara rounding of a total bill: last digit 1,2,6,7 down; 3,4,8,9 up
  const round5 = (sen) => (sen % 5 <= 2 ? sen - (sen % 5) : sen + (5 - (sen % 5)));

  function money(sen, currency) {
    return `${currency || 'RM'} ${(sen / 100).toFixed(2)}`;
  }

  /** Unit price of one configured item, in sen. `menu` is the normalised menu from backend.getMenu(). */
  function unitPrice(menu, itemId, options) {
    const item = menu.items.find((i) => i.id === itemId);
    if (!item) throw new Error('unknown_item');
    let unit = item.price_sen;
    for (const gid of item.groups) {
      const g = menu.groups[gid];
      const pick = (options || {})[gid];
      if (g.type === 'single') {
        const oid = pick || g.default_option;
        if (!oid) { if (g.required) throw new Error('missing_option:' + gid); continue; }
        const o = g.options.find((x) => x.id === oid);
        if (!o) throw new Error('bad_option');
        unit += o.price_sen;
      } else {
        let total = 0;
        for (const [oid, qty] of Object.entries(pick || {})) {
          if (!qty) continue;
          const o = g.options.find((x) => x.id === oid);
          if (!o || qty < 0 || qty > o.max_qty) throw new Error('bad_option');
          total += qty;
          unit += o.price_sen * qty;
        }
        if (g.max_total && total > g.max_total) throw new Error('too_many_toppings');
      }
    }
    return unit;
  }

  /** Totals for a cart: [{item, qty, options}] -> {subtotal, service, sst, total, cash} in sen.
      `mode` is 'dine_in' or 'takeaway'; takeaway has no service charge unless service_charge_takeaway is on. */
  function totals(menu, lines, mode) {
    const s = menu.settings;
    const subtotal = lines.reduce((sum, l) => sum + unitPrice(menu, l.item, l.options) * l.qty, 0);
    const service = mode === 'takeaway' && !s.service_charge_takeaway ? 0 : applyRate(subtotal, s.service_charge_rate);
    const sst = applyRate(subtotal + (s.sst_on_service_charge ? service : 0), s.sst_rate);
    const total = subtotal + service + sst;
    return { subtotal, service, sst, total, cash: s.round_cash_to_5sen ? round5(total) : total };
  }

  /** Local wall-clock parts of `date` in the shop's time zone. */
  function localParts(date, tz) {
    const f = new Intl.DateTimeFormat('en-GB', { timeZone: tz, weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
    const parts = Object.fromEntries(f.formatToParts(date).map((p) => [p.type, p.value]));
    return { day: parts.weekday.toLowerCase().slice(0, 3), minutes: Number(parts.hour) * 60 + Number(parts.minute) };
  }

  /** YYYY-MM-DD of `date` in the shop's time zone. */
  const localDate = (date, tz) => new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(date);

  const hm = (t) => { const [h, m] = t.split(':').map(Number); return h * 60 + m; };

  /** Same rules as public.shop_is_open(): close <= open means the window runs past midnight. */
  function isOpen(settings, date) {
    const { day, minutes } = localParts(date, settings.timezone);
    const today = DAYS.indexOf(day);
    const yesterday = DAYS[(today + 6) % 7];
    const closed = settings.closed_dates || [];
    const dayOff = (d) => closed.includes(localDate(d, settings.timezone));
    if (!dayOff(date)) for (const [o, c] of settings.hours[day] || []) {
      const O = hm(o), C = hm(c);
      if (C > O && minutes >= O && minutes < C) return true;
      if (C <= O && minutes >= O) return true;
    }
    if (!dayOff(new Date(date.getTime() - 86400000))) for (const [o, c] of settings.hours[yesterday] || []) {
      if (hm(c) <= hm(o) && minutes < hm(c)) return true;
    }
    return false;
  }

  /** Pickup slots from now + prep time, on the slot grid, while open, for the next 12 hours (max 40). */
  function pickupSlots(settings, now) {
    const step = settings.slot_minutes * 60000;
    const start = Math.ceil((now.getTime() + settings.prep_minutes * 60000) / step) * step;
    const slots = [];
    for (let t = start; t < now.getTime() + 12 * 3600000 && slots.length < 40; t += step) {
      const d = new Date(t);
      if (isOpen(settings, d)) slots.push(d);
    }
    return slots;
  }

  global.Pricing = { toSen, applyRate, round5, money, unitPrice, totals, isOpen, pickupSlots, localParts, localDate };
})(typeof window !== 'undefined' ? window : globalThis);
