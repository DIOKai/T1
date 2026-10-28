/* Staff screen: live orders, menu prices / sold out, opening hours and charges, table QR codes.
   Staff sign in with a Supabase Auth email + password and must be listed in public.staff. */
(function () {
  'use strict';
  const cfg = window.SITE_CONFIG;
  const api = window.Backend.create(cfg);
  const P = window.Pricing;
  const $ = (id) => document.getElementById(id);
  const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
  const NEXT = { new: 'preparing', preparing: 'ready', ready: 'collected' };
  const LANG_KEY = 'order-site-staff-lang';
  const HTML_LANG = { en: 'en', zh: 'zh-Hans', ms: 'ms' };

  let menu = null;
  let seen = null;           // order ids already shown, to spot new ones
  let soundOn = false;
  let audio = null;
  let timer = null;
  let lastOrders = [];
  let lang = pickLang();

  function pickLang() {
    let saved = null;
    try { saved = localStorage.getItem(LANG_KEY); } catch (e) { /* private mode */ }
    const want = new URLSearchParams(location.search).get('lang') || saved || (navigator.language || 'en').slice(0, 2);
    return window.STAFF_I18N[want] ? want : 'en';
  }
  const t = (key, vars) => String(window.STAFF_I18N[lang][key] ?? window.STAFF_I18N.en[key] ?? key)
    .replace(/\{(\w+)\}/g, (_, k) => (vars && vars[k] != null ? vars[k] : ''));

  function el(tag, attrs, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === 'class') n.className = v;
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? '' : v);
    }
    for (const kid of kids.flat(Infinity)) if (kid != null && kid !== false) n.append(kid.nodeType ? kid : String(kid));
    return n;
  }
  // menu names in the staff language, falling back to English
  const L = (o) => (o && (o[lang] || o.en || Object.values(o)[0])) || '';
  const money = (sen) => P.money(sen, menu.settings.currency);
  const clock = (iso) => new Intl.DateTimeFormat('en-GB', { timeZone: menu.settings.timezone, hour: '2-digit', minute: '2-digit' }).format(new Date(iso));
  const notice = (text, kind) => $('notices').replaceChildren(text ? el('div', { class: 'notice ' + (kind || 'bad') }, text) : '');

  function explain(e) {
    return ['forbidden', 'network', 'signed_out'].includes(e.message) ? t('err_' + e.message) : t('err_save', { e: e.message });
  }

  // static text (data-t), language buttons, and everything drawn from data
  function applyLang() {
    document.documentElement.lang = HTML_LANG[lang];
    document.querySelectorAll('[data-t]').forEach((n) => { n.textContent = t(n.dataset.t); });
    $('sound').textContent = soundOn ? t('sound_on') : t('sound_off');
    $('staffLangs').replaceChildren(...Object.keys(window.STAFF_I18N).map((code) => el('button', {
      'aria-pressed': String(code === lang), lang: HTML_LANG[code], 'aria-label': window.I18N[code].lang_name,
      onclick: () => { lang = code; try { localStorage.setItem(LANG_KEY, code); } catch (e) { /* ignore */ } applyLang(); }
    }, window.I18N[code].lang_short)));
    if (menu) { renderMenuTab(); renderShopTab(); renderBoard(lastOrders, new Set()); }
    if (api.demo && menu) notice(t('demo'), 'warn');
  }

  // ------------------------------------------------------------ sign-in
  async function start() {
    if (!api.signedIn()) return showLogin();
    try { menu = await api.getMenu(); } catch (e) { notice(explain(e)); return; }
    $('login').hidden = true;
    $('app').hidden = false;
    if (api.demo) notice(t('demo'), 'warn');
    $('accepting').checked = menu.settings.accepting_orders;
    renderMenuTab();
    renderShopTab();
    $('siteUrl').value = new URL('index.html', location.href).href;
    await refresh();
    clearInterval(timer);
    timer = setInterval(refresh, (cfg.pollSeconds || 8) * 1000);
  }

  function showLogin() {
    $('app').hidden = true;
    $('login').hidden = false;
    $('email').focus();
  }

  $('login').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    $('loginError').textContent = '';
    try {
      await api.signIn($('email').value.trim(), $('password').value);
      $('password').value = '';
      start();
    } catch (e) {
      $('loginError').textContent = ['bad_login', 'not_staff'].includes(e.message) ? t(e.message) : e.message === 'network' ? t('err_network') : e.message;
    }
  });
  $('signOut').addEventListener('click', () => { api.signOut(); clearInterval(timer); location.reload(); });

  // ------------------------------------------------------------ tabs
  document.querySelectorAll('[data-tab]').forEach((b) => b.addEventListener('click', () => {
    document.querySelectorAll('[data-tab]').forEach((x) => x.setAttribute('aria-selected', String(x === b)));
    document.querySelectorAll('[data-panel]').forEach((p) => { p.hidden = p.dataset.panel !== b.dataset.tab; });
  }));

  // ------------------------------------------------------------ orders
  async function refresh() {
    let orders;
    try {
      orders = await api.listOrders(new Date(Date.now() - 18 * 3600000).toISOString());
    } catch (e) {
      notice(explain(e));
      if (e.message === 'signed_out' || e.message === 'forbidden') { clearInterval(timer); showLogin(); }
      return;
    }
    if (!api.demo) notice('');
    const fresh = seen ? orders.filter((o) => !seen.has(o.id)) : [];
    seen = new Set(orders.map((o) => o.id));
    lastOrders = orders;
    if (fresh.length) beep();
    renderBoard(orders, new Set(fresh.map((o) => o.id)));
  }

  function renderBoard(orders, fresh) {
    const cols = ['new', 'preparing', 'ready', 'done'].map((c) => [c, t('col_' + c)]);
    const inCol = (o, c) => (c === 'done' ? ['collected', 'cancelled'].includes(o.status) : o.status === c);
    $('board').replaceChildren(...cols.map(([c, title]) => {
      let list = orders.filter((o) => inCol(o, c));
      if (c === 'done') list = list.reverse().slice(0, 30);
      return el('section', { class: 'col', 'aria-label': title }, el('h2', {}, el('span', {}, title), el('span', { class: 'num' }, list.length)),
        list.map((o) => ticket(o, fresh.has(o.id))));
    }));
  }

  function ticket(o, isFresh) {
    const where = o.mode === 'dine_in' ? t('table', { n: o.table_no }) : t('takeaway_at', { time: clock(o.pickup_at) });
    const next = NEXT[o.status];
    return el('article', { class: 'ticket' + (isFresh ? ' fresh' : '') },
      el('header', {}, el('span', { class: 'no num' }, o.order_no), el('span', { class: 'muted num' }, clock(o.created_at))),
      el('p', {}, el('strong', {}, where)),
      el('p', {}, o.customer_name, o.phone && [' · ', el('a', { href: 'tel:' + o.phone }, o.phone)]),
      el('ul', {}, o.lines.map((l) => el('li', {}, `${l.qty} × ${L(l.name)}`,
        l.options.length > 0 && el('div', { class: 'muted' }, l.options.map((x) => L(x.label) + (x.qty > 1 ? ' ×' + x.qty : '')).join(' · '))))),
      o.notes && el('p', { class: 'notice warn' }, t('note'), o.notes),
      el('p', {}, el('strong', { class: 'num' }, money(o.total_sen)), ' ',
        el('span', { class: 'tag' }, t('pay_' + o.payment_method)), ' ',
        el('span', { class: 'tag ' + o.payment_status }, t(o.payment_status)),
        o.payment_method === 'counter' && o.cash_total_sen !== o.total_sen && el('span', { class: 'muted num' }, ' ' + t('cash', { x: money(o.cash_total_sen) }))),
      el('div', { class: 'acts' },
        next && el('button', { class: 'primary', 'data-action': next, onclick: () => setOrder(o, { status: next }) }, t('btn_' + next)),
        o.payment_status === 'unpaid' && o.status !== 'cancelled' && el('button', { 'data-action': 'paid', onclick: () => setOrder(o, { payment_status: 'paid' }) }, t('mark_paid')),
        !['collected', 'cancelled'].includes(o.status) && el('button', { class: 'ghost', 'data-action': 'cancel', onclick: () => {
          if (confirm(t('confirm_cancel', { no: o.order_no }))) setOrder(o, { status: 'cancelled' });
        } }, t('cancel'))));
  }

  async function setOrder(o, values) {
    try { await api.updateOrder(o.id, values); await refresh(); } catch (e) { notice(explain(e)); }
  }

  function beep() {
    if (!soundOn || !audio) return;
    const now = audio.currentTime;
    [0, 0.25].forEach((dt) => {
      const osc = audio.createOscillator();
      const gain = audio.createGain();
      osc.frequency.value = 880;
      gain.gain.setValueAtTime(0.0001, now + dt);
      gain.gain.exponentialRampToValueAtTime(0.3, now + dt + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + dt + 0.2);
      osc.connect(gain).connect(audio.destination);
      osc.start(now + dt);
      osc.stop(now + dt + 0.22);
    });
  }
  $('sound').addEventListener('click', () => {
    // browsers only allow sound after a tap, so the tablet needs this once per session
    soundOn = !soundOn;
    if (soundOn && !audio) audio = new (window.AudioContext || window.webkitAudioContext)();
    if (audio && audio.state === 'suspended') audio.resume();
    $('sound').setAttribute('aria-pressed', String(soundOn));
    $('sound').textContent = soundOn ? t('sound_on') : t('sound_off');
    if (soundOn) beep();
    // keep the order tablet's screen on while the board is open (where the browser supports it)
    if (soundOn && navigator.wakeLock) navigator.wakeLock.request('screen').catch(() => {});
  });
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && soundOn && navigator.wakeLock) navigator.wakeLock.request('screen').catch(() => {});
  });

  $('accepting').addEventListener('change', async (ev) => {
    try { await api.updateSettings({ accepting_orders: ev.target.checked }); }
    catch (e) { ev.target.checked = !ev.target.checked; notice(explain(e)); }
  });

  // ------------------------------------------------------------ menu tab
  function priceInput(sen, save) {
    return el('input', { type: 'number', min: '0', step: '0.01', value: (sen / 100).toFixed(2), onchange: async (ev) => {
      const v = Number(ev.target.value);
      if (!(v >= 0) || Math.abs(v * 100 - Math.round(v * 100)) > 1e-6) { ev.target.setCustomValidity(t('price_invalid')); ev.target.reportValidity(); return; }
      ev.target.setCustomValidity('');
      try { await save(Math.round(v * 100)); ev.target.classList.add('saved'); } catch (e) { notice(explain(e)); }
    } });
  }
  function soldOutBox(checked, label, id, save) {
    return el('label', { class: 'switch' }, el('input', { type: 'checkbox', checked, 'aria-label': t('sold_out_of', { x: label }), 'data-id': id, onchange: async (ev) => {
      try { await save(ev.target.checked); } catch (e) { ev.target.checked = !ev.target.checked; notice(explain(e)); }
    } }), t('col_sold_out'));
  }

  function renderMenuTab() {
    $('itemRows').replaceChildren(...menu.items.map((i) => el('tr', { 'data-id': i.id },
      el('td', {}, L(i.name)),
      el('td', {}, priceInput(i.price_sen, (sen) => api.updateItem(i.id, { price_sen: sen }).then(() => { i.price_sen = sen; }))),
      el('td', {}, soldOutBox(i.sold_out, L(i.name), i.id, (v) => api.updateItem(i.id, { sold_out: v }).then(() => { i.sold_out = v; }))))));
    $('optionRows').replaceChildren(...Object.values(menu.groups).flatMap((g) => g.options.map((o) => el('tr', { 'data-id': g.id + '.' + o.id },
      el('td', {}, L(g.label) + ': ' + L(o.label)),
      el('td', {}, priceInput(o.price_sen, (sen) => api.updateOption(g.id, o.id, { price_sen: sen }).then(() => { o.price_sen = sen; }))),
      el('td', {}, soldOutBox(o.sold_out, L(o.label), g.id + '.' + o.id, (v) => api.updateOption(g.id, o.id, { sold_out: v }).then(() => { o.sold_out = v; })))))));
  }

  // ------------------------------------------------------------ shop tab
  function renderShopTab() {
    const s = menu.settings;
    $('hoursFields').replaceChildren(...DAYS.map((d) => el('label', { class: 'field' }, t(d),
      el('input', { type: 'text', id: 'h-' + d, value: (s.hours[d] || []).map((w) => w.join('-')).join(', '), placeholder: t('closed_placeholder') }))));
    $('svc').value = +(s.service_charge_rate * 100).toFixed(2);
    $('sst').value = +(s.sst_rate * 100).toFixed(2);
    $('sstReg').value = s.sst_reg_no || '';
    $('closedDates').value = (s.closed_dates || []).join(', ');
    $('sstOnSvc').checked = s.sst_on_service_charge;
    $('svcTakeaway').checked = s.service_charge_takeaway;
    $('round5').checked = s.round_cash_to_5sen;
    $('prep').value = s.prep_minutes;
    $('slot').value = s.slot_minutes;
  }

  function parseHours(text) {
    const out = [];
    for (const part of text.split(',').map((x) => x.trim()).filter(Boolean)) {
      const m = part.match(/^([01]?\d|2[0-3]):([0-5]\d)\s*[-–]\s*([01]?\d|2[0-3]):([0-5]\d)$/);
      if (!m) throw new Error(part);
      out.push([`${m[1].padStart(2, '0')}:${m[2]}`, `${m[3].padStart(2, '0')}:${m[4]}`]);
    }
    return out;
  }

  $('shopForm').addEventListener('submit', async (ev) => {
    ev.preventDefault();
    $('shopError').textContent = '';
    $('shopSaved').textContent = '';
    const hours = {};
    for (const d of DAYS) {
      try { hours[d] = parseHours($('h-' + d).value); }
      catch (e) { $('shopError').textContent = t('bad_hours', { d: t(d), x: e.message }); return; }
    }
    const closed = $('closedDates').value.split(',').map((x) => x.trim()).filter(Boolean);
    const badDate = closed.find((x) => !/^\d{4}-\d{2}-\d{2}$/.test(x) || isNaN(Date.parse(x)));
    if (badDate) { $('shopError').textContent = t('bad_date', { x: badDate }); return; }
    const rate = (id) => Math.round(Number($(id).value || 0) * 100) / 10000;   // % -> fraction with 4 decimals
    const values = { hours, service_charge_rate: rate('svc'), sst_rate: rate('sst'), sst_on_service_charge: $('sstOnSvc').checked,
      service_charge_takeaway: $('svcTakeaway').checked, sst_reg_no: $('sstReg').value.trim() || null, closed_dates: closed,
      round_cash_to_5sen: $('round5').checked, prep_minutes: parseInt($('prep').value, 10), slot_minutes: parseInt($('slot').value, 10) };
    if (values.service_charge_rate > 0.2 || values.sst_rate > 0.2) { $('shopError').textContent = t('pct_max'); return; }
    if (values.sst_rate > 0 && !values.sst_reg_no) { $('shopError').textContent = t('sst_needs_reg'); return; }
    try {
      await api.updateSettings(values);
      menu = await api.getMenu();
      $('shopSaved').textContent = t('saved');
    } catch (e) { $('shopError').textContent = explain(e); }
  });

  // ------------------------------------------------------------ table QR codes
  // QR cards are read by customers, so they show every shop language: "Table 3 · 3 号桌 · Meja 3"
  const customerText = (key, vars) => menu.settings.languages.map((code) =>
    String(window.I18N[code][key]).replace(/\{(\w+)\}/g, (_, k) => vars[k])).join(' · ');
  function qrCard(url, title) {
    const qr = window.qrcode(0, 'M');
    qr.addData(url);
    qr.make();
    const card = el('div', { class: 'qr-card' });
    card.innerHTML = qr.createSvgTag({ cellSize: 4, margin: 4, scalable: true, title });   // library output: an SVG of our own URL
    card.append(el('p', { style: 'font-weight:800;font-size:1.3rem;margin-top:6px' }, title), el('p', { style: 'font-size:.8rem' }, L(menu.settings.name)));
    return card;
  }
  $('makeQr').addEventListener('click', () => {
    let base;
    try { base = new URL($('siteUrl').value); } catch (e) { notice(t('bad_url')); return; }
    if (base.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(base.hostname)) notice(t('need_https'), 'warn');
    base.search = '';
    base.hash = '';
    const cards = [];
    if (menu.settings.takeaway) cards.push(qrCard(base.href, customerText('takeaway', {})));
    if (menu.settings.dine_in) {
      for (let n = 1; n <= menu.settings.max_tables; n++) {
        const u = new URL(base.href);
        u.searchParams.set('t', n);
        cards.push(qrCard(u.href, customerText('table', { n })));
      }
    }
    $('qrGrid').replaceChildren(...cards);
  });
  $('printQr').addEventListener('click', () => window.print());

  applyLang();
  start();
})();
