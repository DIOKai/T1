/* Customer ordering page. Table QR codes open index.html?t=<table>; without ?t the page takes takeaway
   orders (if the shop allows them). The server recalculates every price; totals here are for display. */
(function () {
  'use strict';
  const cfg = window.SITE_CONFIG;
  const api = window.Backend.create(cfg);
  const P = window.Pricing;
  const $ = (id) => document.getElementById(id);
  const params = new URLSearchParams(location.search);
  const CART_KEY = 'order-site-cart';
  const HTML_LANG = { en: 'en', zh: 'zh-Hans', ms: 'ms' };

  let menu = null;
  let lang = 'en';
  let table = null;          // set from ?t=, dine-in only
  let mode = null;           // 'dine_in' | 'takeaway' | null (cannot order)
  let cart = [];
  let editing = null;        // {item, options, qty} while the item sheet is open
  let pollTimer = null;
  let clientRef = null;      // one id per checkout attempt, so a retry after a dropped reply cannot order twice

  // ------------------------------------------------------------ helpers
  function el(tag, attrs, ...kids) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === 'class') n.className = v;
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
      else if (k === 'style') n.setAttribute('style', v);
      else n.setAttribute(k, v === true ? '' : v);
    }
    for (const kid of kids.flat(Infinity)) if (kid != null && kid !== false) n.append(kid.nodeType ? kid : String(kid));
    return n;
  }
  const t = (key, vars) => String((window.I18N[lang] || {})[key] ?? window.I18N.en[key] ?? key)
    .replace(/\{(\w+)\}/g, (_, k) => (vars && vars[k] != null ? vars[k] : ''));
  const L = (obj) => (obj && (obj[lang] || obj.en || Object.values(obj)[0])) || '';
  const money = (sen) => P.money(sen, menu.settings.currency);
  const timeText = (d) => new Intl.DateTimeFormat(HTML_LANG[lang], { timeZone: menu.settings.timezone, hour: '2-digit', minute: '2-digit' }).format(d);
  const store = {
    get(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* private mode: cart lives in memory only */ } }
  };
  const item = (id) => menu.items.find((i) => i.id === id);
  const lineKey = (l) => JSON.stringify([l.item, l.options]);

  function errorText(code) {
    const base = String(code || '').split(':')[0];
    return window.I18N.en['err_' + base] ? t('err_' + base) : t('err_generic');
  }

  // ------------------------------------------------------------ start
  async function start() {
    lang = pickLang();
    try {
      menu = await api.getMenu();
    } catch (e) {
      $('shopName').textContent = '';
      $('notices').replaceChildren(el('div', { class: 'notice bad' }, t('err_network'), ' ',
        el('button', { onclick: () => location.reload() }, '↻')));
      return;
    }
    if (!menu.settings.languages.includes(lang)) lang = menu.settings.languages[0] || 'en';
    const tn = parseInt(params.get('t'), 10);
    if (menu.settings.dine_in && tn >= 1 && tn <= menu.settings.max_tables) table = tn;
    mode = table ? 'dine_in' : (menu.settings.takeaway ? 'takeaway' : null);
    cart = (store.get(CART_KEY) || []).filter((l) => item(l.item));
    bindStatic();
    render();
    const m = location.hash.match(/order=([0-9a-f-]{36})/);
    if (m) showDone(m[1]);
  }

  function pickLang() {
    const want = params.get('lang') || store.get('order-site-lang') || (navigator.language || 'en').slice(0, 2);
    return window.I18N[want] ? want : 'en';
  }

  // ------------------------------------------------------------ render
  function render() {
    const s = menu.settings;
    document.documentElement.lang = HTML_LANG[lang] || lang;
    document.title = L(s.name);
    $('shopName').textContent = L(s.name);
    $('tagline').textContent = L(s.tagline);
    $('modePill').hidden = !table;
    $('modePill').textContent = table ? t('table', { n: table }) : '';
    $('langs').replaceChildren(...s.languages.map((code) => el('button', {
      'aria-pressed': String(code === lang), lang: HTML_LANG[code], 'aria-label': window.I18N[code].lang_name,
      onclick: () => { lang = code; store.set('order-site-lang', code); render(); if (!$('doneView').hidden) refreshDone(); }
    }, window.I18N[code].lang_short)));
    renderNotices();
    renderMenu();
    renderBar();
    staticText();
  }

  function renderNotices() {
    const s = menu.settings;
    const n = [];
    if (api.demo) n.push(el('div', { class: 'notice warn' }, t('demo_mode')));
    if (!s.accepting_orders) n.push(el('div', { class: 'notice bad' }, t('paused_banner')));
    else if (!P.isOpen(s, new Date())) n.push(el('div', { class: 'notice warn' }, t('closed_banner'), hoursList()));
    if (!mode) n.push(el('div', { class: 'notice' }, t('scan_table')));
    if (s.halal_cert && s.halal_cert.number && s.halal_cert.expires >= P.localDate(new Date(), s.timezone)) n.push(el('div', { class: 'notice ok' }, t('halal_cert', { no: s.halal_cert.number })));
    $('notices').replaceChildren(...n);
  }

  function hoursList() {
    const days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
    return el('ul', { class: 'hours num' }, days.map((d) => [
      el('li', {}, t(d)),
      el('li', {}, (menu.settings.hours[d] || []).map((w) => w.join('–')).join(', ') || '—')
    ]));
  }

  function art(i) {
    return el('div', { class: 'art', 'aria-hidden': 'true',
      style: `--c:${i.color || 'var(--surface-2)'};${i.image_url ? `background-image:url("${encodeURI(i.image_url)}")` : ''}` });
  }

  function chips(i) {
    return el('div', { class: 'chips' },
      i.sold_out && el('span', { class: 'chip out' }, t('sold_out')),
      i.dietary.map((d) => el('span', { class: 'chip diet' }, t('diet_' + d))),
      i.allergens.length > 0 && el('span', { class: 'chip' }, t('contains') + ': ' + i.allergens.map((a) => t('allergen_' + a)).join(', ')));
  }

  function renderMenu() {
    const feats = menu.items.filter((i) => i.featured);
    $('featuredWrap').hidden = !feats.length;
    $('featuredTitle').textContent = t('featured');
    $('featured').replaceChildren(...feats.map((i) => el('button', {
      class: 'feat', role: 'listitem', disabled: i.sold_out || !mode, onclick: () => openItem(i),
      'aria-label': `${L(i.name)}, ${money(i.price_sen)}${i.sold_out ? ', ' + t('sold_out') : ''}`
    }, art(i), el('h3', {}, L(i.name)), el('p', { class: 'muted num' }, money(i.price_sen)))));

    const cats = menu.categories.filter((c) => menu.items.some((i) => i.category_id === c.id));
    $('tabs').replaceChildren(...cats.map((c, n) => el('a', { href: '#cat-' + c.id, 'aria-current': String(n === 0) }, L(c.label))));
    $('sections').replaceChildren(...cats.map((c) => el('section', { class: 'cat', id: 'cat-' + c.id, 'aria-labelledby': 'h-' + c.id },
      el('h2', { id: 'h-' + c.id }, L(c.label)),
      menu.items.filter((i) => i.category_id === c.id).map((i) => el('button', {
        class: 'item' + (i.sold_out ? ' out' : ''), disabled: i.sold_out || !mode, onclick: () => openItem(i)
      }, art(i), el('div', {}, el('h3', {}, L(i.name)), el('p', { class: 'desc' }, L(i.description)), chips(i)),
      el('span', { class: 'price num' }, money(i.price_sen)))))));
    watchTabs();
  }

  let tabObserver = null;
  function watchTabs() {
    if (tabObserver) tabObserver.disconnect();
    if (!('IntersectionObserver' in window)) return;
    tabObserver = new IntersectionObserver((entries) => {
      entries.filter((e) => e.isIntersecting).forEach((e) => {
        document.querySelectorAll('#tabs a').forEach((a) => a.setAttribute('aria-current', String(a.hash === '#' + e.target.id)));
      });
    }, { rootMargin: '-64px 0px -60% 0px' });
    document.querySelectorAll('.cat').forEach((s) => tabObserver.observe(s));
  }

  function renderBar() {
    const count = cart.reduce((n, l) => n + l.qty, 0);
    $('bar').hidden = !count || !$('doneView').hidden;
    if (!count) return;
    $('cartCount').textContent = t('view_order') + ' · ' + t('items_count', { n: count });
    let total = 0;
    try { total = P.totals(menu, cart, mode).total; } catch (e) { /* an item changed; the cart sheet shows which */ }
    $('cartTotal').textContent = money(total);
  }

  function staticText() {
    document.querySelectorAll('[data-close]').forEach((b) => b.setAttribute('aria-label', t('close')));
    $('cartTitle').textContent = t('your_order');
    $('emptyCart').textContent = t('empty_cart');
    $('modeLegend').textContent = t('choose_mode');
    $('pickupLabel').textContent = t('pickup_time');
    $('nameLabel').textContent = t('your_name');
    $('notesLabel').textContent = t('notes');
    $('payLegend').textContent = t('pay_how');
    $('orderNoLabel').textContent = t('order_no');
    $('autoUpdate').textContent = t('status_updates');
    $('orderMore').textContent = t('order_again');
    const consent = $('consentText');
    consent.replaceChildren(t('consent', { shop: L(menu.settings.name) }), ' ',
      el('a', { href: cfg.privacyUrl, target: '_blank', rel: 'noopener' }, t('privacy')));
  }

  // ------------------------------------------------------------ item sheet
  function openItem(i) {
    if (i.sold_out || !mode) return;
    editing = { item: i.id, qty: 1, options: {} };
    $('itemTitle').textContent = L(i.name);
    $('itemDesc').textContent = L(i.description);
    $('itemChips').replaceChildren(chips(i));
    const form = $('itemForm');
    form.replaceChildren(...i.groups.map((gid) => groupField(menu.groups[gid])));
    updateItemSheet();
    $('itemSheet').showModal();
  }

  function priceTag(sen) { return sen ? ' +' + money(sen) : ''; }

  function groupField(g) {
    if (g.type === 'single') {
      return el('fieldset', {}, el('legend', {}, L(g.label), g.required && el('span', { class: 'muted' }, t('required'))),
        el('div', { class: 'seg' }, g.options.map((o) => el('label', {},
          el('input', { type: 'radio', name: g.id, value: o.id, checked: o.id === g.default_option, disabled: o.sold_out,
            onchange: () => { editing.options[g.id] = o.id; updateItemSheet(); } }),
          el('span', {}, L(o.label), el('span', { class: 'num' }, priceTag(o.price_sen)), o.sold_out && ' · ' + t('sold_out'))))));
    }
    return el('fieldset', {}, el('legend', {}, L(g.label), g.max_total && el('span', { class: 'muted' }, t('up_to', { n: g.max_total }))),
      g.options.map((o) => el('div', { class: 'multi-row' },
        el('span', {}, L(o.label), el('span', { class: 'muted num' }, priceTag(o.price_sen)), o.sold_out && ' · ' + t('sold_out')),
        el('div', { class: 'stepper' },
          el('button', { type: 'button', 'data-g': g.id, 'data-o': o.id, 'data-d': '-1', 'aria-label': t('decrease', { x: L(o.label) }), onclick: stepOption }, '−'),
          el('output', { id: `o-${g.id}-${o.id}`, 'aria-live': 'polite' }, '0'),
          el('button', { type: 'button', 'data-g': g.id, 'data-o': o.id, 'data-d': '1', 'aria-label': t('increase', { x: L(o.label) }), disabled: o.sold_out, onclick: stepOption }, '+')))));
  }

  function stepOption(ev) {
    const { g, o, d } = ev.currentTarget.dataset;
    const group = menu.groups[g];
    const picks = Object.assign({}, editing.options[g]);
    const total = Object.values(picks).reduce((a, b) => a + b, 0);
    const opt = group.options.find((x) => x.id === o);
    const next = (picks[o] || 0) + Number(d);
    if (next < 0 || next > opt.max_qty || (Number(d) > 0 && group.max_total && total >= group.max_total)) return;
    if (next) picks[o] = next; else delete picks[o];
    if (Object.keys(picks).length) editing.options[g] = picks; else delete editing.options[g];
    updateItemSheet();
  }

  function updateItemSheet() {
    const i = item(editing.item);
    for (const gid of i.groups) {
      const g = menu.groups[gid];
      if (g.type !== 'multi') continue;
      const picks = editing.options[gid] || {};
      const total = Object.values(picks).reduce((a, b) => a + b, 0);
      for (const o of g.options) {
        const n = picks[o.id] || 0;
        $(`o-${gid}-${o.id}`).textContent = n;
        const [minus, plus] = $(`o-${gid}-${o.id}`).parentNode.querySelectorAll('button');
        minus.disabled = n === 0;
        plus.disabled = o.sold_out || n >= o.max_qty || (g.max_total && total >= g.max_total);
      }
    }
    $('qty').textContent = editing.qty;
    $('qMinus').disabled = editing.qty <= 1;
    $('qPlus').disabled = editing.qty >= 20;
    $('qMinus').setAttribute('aria-label', t('decrease', { x: L(i.name) }));
    $('qPlus').setAttribute('aria-label', t('increase', { x: L(i.name) }));
    $('addBtn').textContent = t('add_to_order') + ' · ' + money(P.unitPrice(menu, i.id, editing.options) * editing.qty);
  }

  function addToCart() {
    // store the full choice (defaults filled in) so identical drinks merge into one line
    const i = item(editing.item);
    const options = {};
    for (const gid of i.groups) {
      const g = menu.groups[gid];
      if (g.type === 'single') { const v = editing.options[gid] || g.default_option; if (v) options[gid] = v; }
      else if (editing.options[gid]) options[gid] = Object.fromEntries(Object.entries(editing.options[gid]).sort());
    }
    const line = { item: i.id, options, qty: editing.qty };
    const same = cart.find((l) => lineKey(l) === lineKey(line));
    if (same) same.qty = Math.min(20, same.qty + line.qty); else cart.push(line);
    saveCart();
    $('itemSheet').close();
    renderBar();
    const btn = $('cartBtn');
    btn.classList.remove('bump'); void btn.offsetWidth; btn.classList.add('bump');
  }

  function saveCart() { clientRef = null; store.set(CART_KEY, cart); }
  const newRef = () => (crypto.randomUUID ? crypto.randomUUID()
    : '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (c) => (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)));

  // ------------------------------------------------------------ cart + checkout
  function optionText(l) {
    const i = item(l.item);
    const parts = [];
    for (const gid of i.groups) {
      const g = menu.groups[gid];
      const v = l.options[gid];
      if (!v) continue;
      if (g.type === 'single') parts.push(L((g.options.find((o) => o.id === v) || {}).label));
      else for (const [oid, n] of Object.entries(v)) parts.push(L((g.options.find((o) => o.id === oid) || {}).label) + ' ×' + n);
    }
    return parts.join(' · ');
  }

  function lineProblem(l) {
    const i = item(l.item);
    if (!i || i.sold_out) return true;
    try { P.unitPrice(menu, l.item, l.options); } catch (e) { return true; }
    return i.groups.some((gid) => {
      const g = menu.groups[gid];
      const v = l.options[gid];
      if (!v) return false;
      const ids = g.type === 'single' ? [v] : Object.keys(v);
      return ids.some((oid) => (g.options.find((o) => o.id === oid) || { sold_out: true }).sold_out);
    });
  }

  function openCart() {
    $('checkoutError').textContent = '';
    renderCart();
    $('cartSheet').showModal();
  }

  function renderCart() {
    $('emptyCart').hidden = cart.length > 0;
    $('checkout').hidden = !cart.length;
    $('placeBtn').hidden = !cart.length;
    $('lines').replaceChildren(...cart.map((l, idx) => {
      const i = item(l.item);
      const bad = lineProblem(l);
      let unit = 0;
      try { unit = P.unitPrice(menu, l.item, l.options); } catch (e) { /* shown as a problem */ }
      return el('li', { class: bad ? 'out' : '' },
        el('div', {}, el('strong', {}, L(i.name)), el('div', { class: 'opts' }, optionText(l)), bad && el('div', {}, t('sold_out'))),
        el('span', { class: 'num' }, money(unit * l.qty)),
        el('div', { class: 'stepper' },
          el('button', { type: 'button', 'aria-label': l.qty === 1 ? t('remove') + ' ' + L(i.name) : t('decrease', { x: L(i.name) }), onclick: () => changeQty(idx, -1) }, l.qty === 1 ? '🗑' : '−'),
          el('output', { 'aria-live': 'polite' }, l.qty),
          el('button', { type: 'button', 'aria-label': t('increase', { x: L(i.name) }), disabled: l.qty >= 20 || bad, onclick: () => changeQty(idx, 1) }, '+')));
    }));
    if (!cart.length) { $('sum').replaceChildren(); renderBar(); return; }

    const s = menu.settings;
    let tot = { subtotal: 0, service: 0, sst: 0, total: 0, cash: 0 };
    try { tot = P.totals(menu, cart.filter((l) => !lineProblem(l)), mode); } catch (e) { /* keep zeros */ }
    const pct = (r) => +(r * 100).toFixed(2);
    $('sum').replaceChildren(...[
      el('dt', {}, t('subtotal')), el('dd', {}, money(tot.subtotal)),
      tot.service > 0 && [el('dt', {}, t('service_charge', { p: pct(s.service_charge_rate) })), el('dd', {}, money(tot.service))],
      s.sst_rate > 0 && [el('dt', {}, t('sst', { p: pct(s.sst_rate) })), el('dd', {}, money(tot.sst))],
      el('dt', { class: 'total' }, t('total')), el('dd', { class: 'total' }, money(tot.total)),
      tot.sst > 0 && s.sst_reg_no && el('dt', { class: 'muted', style: 'grid-column: 1 / -1' }, t('sst_reg', { no: s.sst_reg_no }))].flat().filter(Boolean));
    $('sum').querySelectorAll('dd').forEach((d) => { d.style.margin = '0'; d.style.textAlign = 'right'; });

    // mode: a customer at a table may still switch to takeaway if the shop allows it
    const both = table && s.takeaway;
    $('modeSet').hidden = !both;
    if (both) {
      $('modeSeg').replaceChildren(...[['dine_in', t('table', { n: table })], ['takeaway', t('takeaway')]].map(([v, text]) => el('label', {},
        el('input', { type: 'radio', name: 'mode', value: v, checked: mode === v, onchange: () => { mode = v; renderCart(); } }), el('span', {}, text))));
    }
    const slots = mode === 'takeaway' ? P.pickupSlots(s, new Date()) : [];
    $('pickupField').hidden = mode !== 'takeaway';
    const prev = $('pickup').value;
    $('pickup').replaceChildren(...(slots.length ? slots.map((d) => el('option', { value: d.toISOString(), selected: d.toISOString() === prev }, timeText(d)))
      : [el('option', { value: '' }, t('no_slots'))]));
    $('phoneLabel').textContent = mode === 'takeaway' ? t('phone') : t('phone_optional');
    $('phone').required = mode === 'takeaway';
    $('phoneHint').textContent = t('phone_hint');

    const methods = ['counter', 'duitnow_qr', 'online'].filter((m) => s.payment[m] && (m !== 'online' || typeof window.startOnlinePayment === 'function'));
    const chosen = $('paySeg').querySelector('input:checked');
    const keep = chosen && methods.includes(chosen.value) ? chosen.value : methods[0];
    $('paySeg').replaceChildren(...methods.map((m) => el('label', {},
      el('input', { type: 'radio', name: 'payment', value: m, checked: m === keep }), el('span', {}, t({ counter: 'pay_counter', duitnow_qr: 'pay_duitnow', online: 'pay_online' }[m])))));

    const blocked = !s.accepting_orders || cart.some(lineProblem) || (mode === 'dine_in' && !P.isOpen(s, new Date())) || (mode === 'takeaway' && !slots.length) || !methods.length;
    $('placeBtn').disabled = blocked;
    $('placeBtn').textContent = t('place_order', { total: money(tot.total) });
    renderBar();
  }

  function changeQty(idx, d) {
    cart[idx].qty += d;
    if (cart[idx].qty <= 0) cart.splice(idx, 1);
    saveCart();
    renderCart();
  }

  async function submit(ev) {
    ev.preventDefault();
    const err = $('checkoutError');
    err.textContent = '';
    const name = $('name').value.trim();
    const phone = $('phone').value.trim();
    if (!name) { err.textContent = t('err_bad_name'); $('name').focus(); return; }
    if (mode === 'takeaway' && !phone) { err.textContent = t('err_phone_required'); $('phone').focus(); return; }
    if (phone && !/^\+?[0-9]{8,15}$/.test(phone.replace(/[^0-9+]/g, ''))) { err.textContent = t('err_bad_phone'); $('phone').focus(); return; }
    if (!$('consent').checked) { err.textContent = t('err_consent_required'); $('consent').focus(); return; }
    const payment = ($('paySeg').querySelector('input:checked') || {}).value;
    const btn = $('placeBtn');
    btn.disabled = true;
    btn.textContent = t('placing');
    clientRef = clientRef || newRef();
    try {
      const res = await api.placeOrder({
        mode, table: mode === 'dine_in' ? table : null, pickup_at: mode === 'takeaway' ? $('pickup').value : null,
        name, phone, notes: $('notes').value.trim(), payment, consent: true, lang, client_ref: clientRef,
        lines: cart.map((l) => ({ item: l.item, qty: l.qty, options: l.options }))
      });
      cart = [];
      saveCart();
      $('cartSheet').close();
      history.replaceState(null, '', location.pathname + location.search + '#order=' + res.token);
      showDone(res.token, res);
      if (payment === 'online' && typeof window.startOnlinePayment === 'function') window.startOnlinePayment(res);
    } catch (e) {
      err.textContent = errorText(e.message);
      if (/^(sold_out|closed|paused|bad_pickup_time|unknown_item|bad_option)/.test(e.message)) {
        try { menu = await api.getMenu(); render(); } catch (e2) { /* keep the old menu */ }
      }
      renderCart();
      err.textContent = errorText(e.message);
    }
  }

  // ------------------------------------------------------------ confirmation + live status
  let doneToken = null;
  let doneData = null;

  async function showDone(token, first) {
    doneToken = token;
    $('menuView').hidden = true;
    $('doneView').hidden = false;
    $('bar').hidden = true;
    doneData = first || null;
    await refreshDone();
    $('doneTitle').focus();
    clearInterval(pollTimer);
    pollTimer = setInterval(refreshDone, (cfg.pollSeconds || 8) * 1000);
  }

  async function refreshDone() {
    try { doneData = (await api.orderStatus(doneToken)) || doneData; } catch (e) { /* keep last known status */ }
    const o = doneData;
    if (!o) { backToMenu(); return; }
    $('doneTitle').textContent = t('order_received');
    $('orderNo').textContent = o.order_no;
    $('doneWhere').textContent = o.mode === 'dine_in' ? t('table', { n: o.table_no }) : t('pickup_at', { time: timeText(new Date(o.pickup_at)) });
    const flow = o.status === 'cancelled' ? ['cancelled'] : ['new', 'preparing', 'ready', 'collected'];
    const at = flow.indexOf(o.status);
    $('steps').replaceChildren(...flow.map((st, n) => el('li', { class: n <= at ? 'on' : '', 'aria-current': n === at ? 'step' : null }, t('status_' + st))));

    const box = $('payBox');
    const total = money(o.total_sen);
    if (o.payment_status === 'paid') box.replaceChildren(el('p', {}, '✓ ', t('paid'), ' · ', total));
    else if (o.status === 'cancelled') box.replaceChildren(el('p', {}, t('status_cancelled')));
    else if (o.payment_method === 'duitnow_qr') box.replaceChildren(...[
      el('p', {}, t('duitnow_msg', { total, no: o.order_no })),
      cfg.duitnowQrImage && el('img', { src: cfg.duitnowQrImage, alt: 'DuitNow QR', width: 240, height: 240 })].filter(Boolean));
    else if (o.payment_method === 'online') box.replaceChildren(...[el('p', {}, t('unpaid'), ' · ', total),
      typeof window.startOnlinePayment === 'function' && el('button', { class: 'primary', onclick: () => window.startOnlinePayment(o) }, t('pay_online'))].filter(Boolean));
    else box.replaceChildren(el('p', {}, o.cash_total_sen !== o.total_sen
      ? t('pay_at_counter_msg', { total, cash: money(o.cash_total_sen) }) : t('pay_at_counter_simple', { total })));

    if (['collected', 'cancelled'].includes(o.status)) clearInterval(pollTimer);
  }

  function backToMenu() {
    clearInterval(pollTimer);
    history.replaceState(null, '', location.pathname + location.search);
    $('doneView').hidden = true;
    $('menuView').hidden = false;
    render();
  }

  // ------------------------------------------------------------ events
  function bindStatic() {
    document.querySelectorAll('[data-close]').forEach((b) => b.addEventListener('click', () => b.closest('dialog').close()));
    document.querySelectorAll('dialog').forEach((d) => d.addEventListener('click', (e) => { if (e.target === d) d.close(); }));
    $('qMinus').addEventListener('click', () => { editing.qty = Math.max(1, editing.qty - 1); updateItemSheet(); });
    $('qPlus').addEventListener('click', () => { editing.qty = Math.min(20, editing.qty + 1); updateItemSheet(); });
    $('addBtn').addEventListener('click', addToCart);
    $('cartBtn').addEventListener('click', openCart);
    $('checkout').addEventListener('submit', submit);
    $('orderMore').addEventListener('click', backToMenu);
    // re-check opening hours and sold-out items every few minutes while the page stays open
    setInterval(async () => {
      if (document.hidden || $('itemSheet').open || $('cartSheet').open || !$('doneView').hidden) return;
      try { menu = await api.getMenu(); render(); } catch (e) { /* offline for a moment */ }
    }, 180000);
  }

  start();
})();
