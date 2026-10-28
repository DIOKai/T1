/* Staff screen: live orders, menu prices / sold out, opening hours and charges, table QR codes.
   Staff sign in with a Supabase Auth email + password and must be listed in public.staff. */
(function () {
  'use strict';
  const cfg = window.SITE_CONFIG;
  const api = window.Backend.create(cfg);
  const P = window.Pricing;
  const $ = (id) => document.getElementById(id);
  const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
  const NEXT = { new: ['preparing', 'Start'], preparing: ['ready', 'Ready'], ready: ['collected', 'Collected'] };

  let menu = null;
  let seen = null;           // order ids already shown, to spot new ones
  let soundOn = false;
  let audio = null;
  let timer = null;

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
  const en = (o) => (o && (o.en || Object.values(o)[0])) || '';
  const money = (sen) => P.money(sen, menu.settings.currency);
  const clock = (iso) => new Intl.DateTimeFormat('en-GB', { timeZone: menu.settings.timezone, hour: '2-digit', minute: '2-digit' }).format(new Date(iso));
  const notice = (text, kind) => $('notices').replaceChildren(text ? el('div', { class: 'notice ' + (kind || 'bad') }, text) : '');

  function explain(e) {
    return { forbidden: 'This account is not allowed to do that (is it in the staff table?).', network: 'No connection. Retrying…',
      signed_out: 'Signed out. Please sign in again.' }[e.message] || 'Could not save: ' + e.message;
  }

  // ------------------------------------------------------------ sign-in
  async function start() {
    if (!api.signedIn()) return showLogin();
    try { menu = await api.getMenu(); } catch (e) { notice(explain(e)); return; }
    $('login').hidden = true;
    $('app').hidden = false;
    if (api.demo) notice('Demo mode: no sign-in, and changes are saved in this browser only. Open index.html in another tab to place test orders.', 'warn');
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
      $('loginError').textContent = { bad_login: 'Wrong email or password.', not_staff: 'This account is not in the staff list. Ask the owner to add it.', network: 'No connection.' }[e.message] || e.message;
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
    if (fresh.length) beep();
    renderBoard(orders, new Set(fresh.map((o) => o.id)));
  }

  function renderBoard(orders, fresh) {
    const cols = [['new', 'New'], ['preparing', 'Preparing'], ['ready', 'Ready'], ['done', 'Done (last 18 h)']];
    const inCol = (o, c) => (c === 'done' ? ['collected', 'cancelled'].includes(o.status) : o.status === c);
    $('board').replaceChildren(...cols.map(([c, title]) => {
      let list = orders.filter((o) => inCol(o, c));
      if (c === 'done') list = list.reverse().slice(0, 30);
      return el('section', { class: 'col', 'aria-label': title }, el('h2', {}, el('span', {}, title), el('span', { class: 'num' }, list.length)),
        list.map((o) => ticket(o, fresh.has(o.id))));
    }));
  }

  function ticket(o, isFresh) {
    const where = o.mode === 'dine_in' ? 'Table ' + o.table_no : 'Takeaway · pick up ' + clock(o.pickup_at);
    const next = NEXT[o.status];
    return el('article', { class: 'ticket' + (isFresh ? ' fresh' : '') },
      el('header', {}, el('span', { class: 'no num' }, o.order_no), el('span', { class: 'muted num' }, clock(o.created_at))),
      el('p', {}, el('strong', {}, where)),
      el('p', {}, o.customer_name, o.phone && [' · ', el('a', { href: 'tel:' + o.phone }, o.phone)]),
      el('ul', {}, o.lines.map((l) => el('li', {}, `${l.qty} × ${en(l.name)}`,
        l.options.length > 0 && el('div', { class: 'muted' }, l.options.map((x) => en(x.label) + (x.qty > 1 ? ' ×' + x.qty : '')).join(' · '))))),
      o.notes && el('p', { class: 'notice warn' }, 'Note: ', o.notes),
      el('p', {}, el('strong', { class: 'num' }, money(o.total_sen)), ' ',
        el('span', { class: 'tag' }, { counter: 'Counter', duitnow_qr: 'DuitNow QR', online: 'Online' }[o.payment_method]), ' ',
        el('span', { class: 'tag ' + o.payment_status }, o.payment_status),
        o.payment_method === 'counter' && o.cash_total_sen !== o.total_sen && el('span', { class: 'muted num' }, ' cash ' + money(o.cash_total_sen))),
      el('div', { class: 'acts' },
        next && el('button', { class: 'primary', onclick: () => setOrder(o, { status: next[0] }) }, next[1]),
        o.payment_status === 'unpaid' && o.status !== 'cancelled' && el('button', { onclick: () => setOrder(o, { payment_status: 'paid' }) }, 'Mark paid'),
        !['collected', 'cancelled'].includes(o.status) && el('button', { class: 'ghost', onclick: () => {
          if (confirm(`Cancel order ${o.order_no}?`)) setOrder(o, { status: 'cancelled' });
        } }, 'Cancel')));
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
    $('sound').textContent = soundOn ? '🔔 Sound on' : '🔔 Sound off';
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
      if (!(v >= 0) || Math.abs(v * 100 - Math.round(v * 100)) > 1e-6) { ev.target.setCustomValidity('Use RM with at most 2 decimals'); ev.target.reportValidity(); return; }
      ev.target.setCustomValidity('');
      try { await save(Math.round(v * 100)); ev.target.classList.add('saved'); } catch (e) { notice(explain(e)); }
    } });
  }
  function soldOutBox(checked, label, save) {
    return el('label', { class: 'switch' }, el('input', { type: 'checkbox', checked, 'aria-label': 'Sold out: ' + label, onchange: async (ev) => {
      try { await save(ev.target.checked); } catch (e) { ev.target.checked = !ev.target.checked; notice(explain(e)); }
    } }), 'Sold out');
  }

  function renderMenuTab() {
    $('itemRows').replaceChildren(...menu.items.map((i) => el('tr', {},
      el('td', {}, en(i.name)),
      el('td', {}, priceInput(i.price_sen, (sen) => api.updateItem(i.id, { price_sen: sen }))),
      el('td', {}, soldOutBox(i.sold_out, en(i.name), (v) => api.updateItem(i.id, { sold_out: v }))))));
    $('optionRows').replaceChildren(...Object.values(menu.groups).flatMap((g) => g.options.map((o) => el('tr', {},
      el('td', {}, en(g.label) + ': ' + en(o.label)),
      el('td', {}, priceInput(o.price_sen, (sen) => api.updateOption(g.id, o.id, { price_sen: sen }))),
      el('td', {}, soldOutBox(o.sold_out, en(o.label), (v) => api.updateOption(g.id, o.id, { sold_out: v })))))));
  }

  // ------------------------------------------------------------ shop tab
  function renderShopTab() {
    const s = menu.settings;
    $('hoursFields').replaceChildren(...DAYS.map((d) => el('label', { class: 'field' }, d.toUpperCase(),
      el('input', { type: 'text', id: 'h-' + d, value: (s.hours[d] || []).map((w) => w.join('-')).join(', '), placeholder: 'closed' }))));
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
      catch (e) { $('shopError').textContent = `${d.toUpperCase()}: "${e.message}" is not like 10:00-22:00`; return; }
    }
    const closed = $('closedDates').value.split(',').map((x) => x.trim()).filter(Boolean);
    const badDate = closed.find((x) => !/^\d{4}-\d{2}-\d{2}$/.test(x) || isNaN(Date.parse(x)));
    if (badDate) { $('shopError').textContent = `Closed date "${badDate}" is not like 2026-03-20`; return; }
    const rate = (id) => Math.round(Number($(id).value || 0) * 100) / 10000;   // % -> fraction with 4 decimals
    const values = { hours, service_charge_rate: rate('svc'), sst_rate: rate('sst'), sst_on_service_charge: $('sstOnSvc').checked,
      service_charge_takeaway: $('svcTakeaway').checked, sst_reg_no: $('sstReg').value.trim() || null, closed_dates: closed,
      round_cash_to_5sen: $('round5').checked, prep_minutes: parseInt($('prep').value, 10), slot_minutes: parseInt($('slot').value, 10) };
    if (values.service_charge_rate > 0.2 || values.sst_rate > 0.2) { $('shopError').textContent = 'Percentages must be 20 or less.'; return; }
    if (values.sst_rate > 0 && !values.sst_reg_no) { $('shopError').textContent = 'Enter the SST registration number first. Only a business registered with Customs may charge SST.'; return; }
    try {
      await api.updateSettings(values);
      menu = await api.getMenu();
      $('shopSaved').textContent = 'Saved.';
    } catch (e) { $('shopError').textContent = explain(e); }
  });

  // ------------------------------------------------------------ table QR codes
  function qrCard(url, title) {
    const qr = window.qrcode(0, 'M');
    qr.addData(url);
    qr.make();
    const card = el('div', { class: 'qr-card' });
    card.innerHTML = qr.createSvgTag({ cellSize: 4, margin: 4, scalable: true, title });   // library output: an SVG of our own URL
    card.append(el('p', { style: 'font-weight:800;font-size:1.3rem;margin-top:6px' }, title), el('p', { style: 'font-size:.8rem' }, en(menu.settings.name)));
    return card;
  }
  $('makeQr').addEventListener('click', () => {
    let base;
    try { base = new URL($('siteUrl').value); } catch (e) { notice('The site address is not a valid URL.'); return; }
    if (base.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(base.hostname)) notice('Use the https:// address of the live site, or customers\' phones may warn them.', 'warn');
    base.search = '';
    base.hash = '';
    const cards = [];
    if (menu.settings.takeaway) cards.push(qrCard(base.href, 'Takeaway'));
    if (menu.settings.dine_in) {
      for (let n = 1; n <= menu.settings.max_tables; n++) {
        const u = new URL(base.href);
        u.searchParams.set('t', n);
        cards.push(qrCard(u.href, 'Table ' + n));
      }
    }
    $('qrGrid').replaceChildren(...cards);
  });
  $('printQr').addEventListener('click', () => window.print());

  start();
})();
