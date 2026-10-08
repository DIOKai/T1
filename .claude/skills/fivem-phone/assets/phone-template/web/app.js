/* FiveM phone template: devices, fold, lock screen, control centre, home, apps (Messages, Wallet, Settings).
   Plain JS, no build step. In game it talks to client.lua through NUI callbacks. In a normal browser it runs as a
   preview with mock data. Preview-only keys: O open/close, N demo notification. URL parameters for screenshots:
   ?device=wide&fold=open&app=messages&thread=1&theme=light&sheet=1&unlock=1&cc=1&note=1
   Everything the player touches is inside the phone. Rules (references/*.md):
   - the page sends intent only; the server decides (amounts, targets)
   - player text is always escaped before it goes into innerHTML
   - folding never resets app state (selected chat, drafts, scroll)
   - transform/opacity animation only; the phone is display:none when closed */

const IN_GAME = typeof window.GetParentResourceName === 'function';
const RES = IN_GAME ? window.GetParentResourceName() : 'phone-template';
const params = new URLSearchParams(location.search);

/* Screen canvases in points (≈152 pt per inch), from real devices (references/real-foldables.md).
   Labels shown to players are generic. */
const DEVICES = {
  bar:      { label: '直板手机', brand: 'apple', fold: '', closed: [390, 844] },
  passport: { label: '护照折叠（书本式，宽）', brand: 'apple', fold: 'book', closed: [465, 676], open: [945, 665], hinges: [0.5] },      // iPhone Duo
  wide:     { label: '宽折叠（书本式）', brand: 'samsung', fold: 'book', closed: [443, 709], open: [924, 693], hinges: [0.5] },           // Galaxy Z Fold8
  tall:     { label: '长折叠（书本式）', brand: 'samsung', fold: 'book', closed: [389, 908], open: [903, 813], hinges: [0.5] },           // Galaxy Z Fold8 Ultra
  flip:     { label: '翻盖折叠', brand: 'samsung', fold: 'clam', closed: [418, 462], open: [413, 964], hinges: [0.5], hingeDir: 'h' },  // Galaxy Z Flip8
  trifold:  { label: '三折叠', brand: 'samsung', fold: 'tri', closed: [389, 908], open: [1225, 899], hinges: [1 / 3, 2 / 3] },      // Galaxy Z TriFold
};

const T = {
  messages: '信息', wallet: '钱包', settings: '设置', camera: '相机', maps: '地图', music: '音乐', garage: '车库', contacts: '联系人', shop: '商店',
  search: '搜索', send: '发送', typeMessage: '输入信息', today: '今天',
  noChats: '还没有对话', noChatsSub: '收到的信息会出现在这里。', pickChat: '选择一个对话', pickChatSub: '从左边的列表打开聊天。',
  loadFailed: '加载失败', retry: '重试', balance: '银行余额', transfer: '转账', history: '最近交易', noTx: '还没有交易',
  to: '对方电话号码', amount: '金额', confirm: (a, n) => `确认转 ${a} 给 ${n}`, next: '下一步', sending: '处理中…',
  sent: '转账成功', darkMode: '深色模式', phoneSize: '手机大小', about: '关于本机', appearance: '外观', model: '手机型号',
  dnd: '勿扰', unfold: '展开', foldUp: '合上', unlockHint: '上滑或点击解锁', call: '电话', mute: '静音',
  badNumber: '请输入正确的电话号码', badAmount: '金额要是 1 到 1,000,000 的整数', demoApp: '这个 app 只是示范图标',
};

const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const $ = (sel, root = document) => root.querySelector(sel);
const raf2 = (fn) => requestAnimationFrame(() => requestAnimationFrame(fn));
const SPRING_SOFT = CSS.supports('transition-timing-function', 'linear(0, 1)')
  ? 'linear(0, 0.051, 0.17, 0.315, 0.462, 0.597, 0.711, 0.803, 0.874, 0.926, 0.963, 0.987, 1.002, 1.011, 1.014, 1.015, 1.014, 1.012, 1.01, 1.008, 1.006, 1.004, 1.003, 1.002, 1)'
  : 'cubic-bezier(0.2, 0, 0, 1)';
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ───────── NUI bridge ───────── */
const mock = {
  'messages:threads': () => ({ ok: true, threads: MOCK.threads.map(({ messages, ...t }) => t) }),
  'messages:thread': ({ id }) => ({ ok: true, messages: (MOCK.threads.find((t) => t.id === id) || { messages: [] }).messages.map((m) => ({ ...m })) }),
  'messages:send': ({ text }) => ({ ok: true, message: { id: Date.now(), out: true, text, time: state.clock } }),
  'wallet:get': () => ({ ok: true, balance: MOCK.balance, tx: MOCK.tx }),
  'wallet:transfer': ({ to, amount }) => (to === '5550000' ? { ok: false, error: '找不到这个号码' } : { ok: true, balance: (state.wallet.balance ?? MOCK.balance) - amount }),
};
async function nui(name, data = {}) {
  if (!IN_GAME) {
    await new Promise((r) => setTimeout(r, 220));
    return mock[name] ? mock[name](data) : { ok: true };
  }
  try {
    const res = await fetch(`https://${RES}/${name}`, { method: 'POST', headers: { 'Content-Type': 'application/json; charset=UTF-8' }, body: JSON.stringify(data) });
    return await res.json();
  } catch {
    return { ok: false, error: 'network' };
  }
}

/* ───────── state ───────── */
const state = {
  open: false, locked: true, lockScreen: true, device: 'bar', fold: 'closed', theme: 'dark', scale: 0.85,
  allowDeviceChange: true, dnd: false, clock: '12:00', app: null, notes: [],
  msg: { threads: null, error: false, selected: null, messages: {}, drafts: {} },
  wallet: { balance: null, tx: null, error: false, prefill: '' },
};
const phone = $('#phone');
const dev = () => DEVICES[state.device] || DEVICES.bar;
const isOpenState = () => !!dev().fold && state.fold === 'open';
const panes = () => (isOpenState() ? (dev().fold === 'book' ? 2 : dev().fold === 'tri' ? 3 : 1) : 1);
const isCover = () => dev().fold === 'clam' && state.fold === 'closed';

const APPS = [
  { id: 'messages', icon: 'message-circle', bg: 'linear-gradient(180deg,#5af575,#14c13a)' },
  { id: 'wallet', icon: 'wallet', bg: 'linear-gradient(180deg,#3f8cff,#1f4fd1)' },
  { id: 'contacts', icon: 'users', bg: 'linear-gradient(180deg,#a0a6b4,#6b7080)' },
  { id: 'maps', icon: 'map-pin', bg: 'linear-gradient(180deg,#ff8a5c,#f0513b)' },
  { id: 'garage', icon: 'car', bg: 'linear-gradient(180deg,#ffd25c,#f5a623)' },
  { id: 'shop', icon: 'shopping-bag', bg: 'linear-gradient(180deg,#d07bff,#8a3ffc)' },
  { id: 'music', icon: 'music', bg: 'linear-gradient(180deg,#ff6b8b,#ff2d55)' },
  { id: 'camera', icon: 'camera', bg: 'linear-gradient(180deg,#5d6170,#2c2e36)' },
  { id: 'settings', icon: 'settings', bg: 'linear-gradient(180deg,#9aa0ac,#5c616d)' },
];
const DOCK = ['messages', 'wallet', 'camera', 'settings'];
const appMeta = (id) => APPS.find((a) => a.id === id) || APPS[APPS.length - 1];
const tileHTML = (id) => `<span class="tile" style="background:${appMeta(id).bg}">${icon(appMeta(id).icon)}</span>`;

/* ───────── device + fold ───────── */
function applyDevice() {
  const d = dev();
  const [w, h] = isOpenState() ? d.open : d.closed;
  Object.assign(phone.dataset, { device: state.device, brand: d.brand, fold: d.fold, state: d.fold ? state.fold : 'closed', panes: panes() });
  phone.style.setProperty('--sw', w);
  phone.style.setProperty('--sh', h);
  phone.style.setProperty('--panes', panes());
  $('#hinges').innerHTML = isOpenState()
    ? d.hinges.map((p) => (d.hingeDir === 'h' ? `<div class="hinge h" style="top:${p * 100}%"></div>` : `<div class="hinge v" style="left:${p * 100}%"></div>`)).join('')
    : '';
  renderHome();
  syncMessagesLayout();
  if (state.app === 'wallet' && panes() < 3) { /* inline form hides; nothing to do */ }
  renderStatus();
}

/* FLIP: change the layout once, then animate the frame from its old size (transform only). */
function morph(change) {
  const before = phone.getBoundingClientRect();
  const animate = state.open && !phone.hidden && !REDUCED;
  if (!animate) { change(); return; }
  phone.classList.add('is-swapping');
  setTimeout(() => {
    const twoStep = change(); // true for the trifold: right panel first, then left
    const after = phone.getBoundingClientRect();
    const sx = before.width / after.width, sy = before.height / after.height;
    const frames = twoStep
      ? [{ transform: `scale(${sx}, ${sy})` }, { transform: `scale(${(sx + 1) / 2 + 0.04}, 1)`, offset: 0.5 }, { transform: 'none' }]
      : [{ transform: `scale(${sx}, ${sy})` }, { transform: 'none' }];
    phone.animate(frames, { duration: twoStep ? 780 : 404, easing: twoStep ? 'cubic-bezier(0.2, 0, 0, 1)' : SPRING_SOFT });
    phone.classList.remove('is-swapping');
  }, 90);
}
function setFold(fold, notify = true) {
  if (!dev().fold || fold === state.fold) return;
  const opening = fold === 'open';
  morph(() => { state.fold = fold; applyDevice(); return opening && dev().fold === 'tri'; });
  if (notify) nui('fold', { folded: fold === 'closed' });
}
const toggleFold = () => setFold(state.fold === 'open' ? 'closed' : 'open');
function setDevice(id, notify = true) {
  if (!DEVICES[id] || id === state.device) return;
  morph(() => { state.device = id; if (!DEVICES[id].fold) state.fold = 'closed'; applyDevice(); });
  if (notify) saveSettings();
}
function setTheme(theme) { state.theme = theme; phone.dataset.theme = theme; }
function setScale(scale) { state.scale = scale; document.documentElement.style.setProperty('--phone-scale', scale); }
function saveSettings() { nui('settings', { theme: state.theme, scale: state.scale, device: state.device }); }

/* edge grip: drag the outer edge (left for book/tri, top for flip), or click it */
(function grip() {
  const g = $('#grip');
  let start = null, moved = false;
  g.addEventListener('pointerdown', (e) => { start = { x: e.clientX, y: e.clientY }; moved = false; g.setPointerCapture(e.pointerId); });
  g.addEventListener('pointermove', (e) => {
    if (!start || moved) return;
    const d = dev().fold === 'clam' ? e.clientY - start.y : e.clientX - start.x;
    if (Math.abs(d) < 28) return;
    moved = true;
    if (d < 0 && state.fold === 'closed') setFold('open');
    else if (d > 0 && state.fold === 'open') setFold('closed');
  });
  g.addEventListener('pointerup', () => { if (start && !moved) toggleFold(); start = null; });
})();

/* ───────── open / close / lock ───────── */
function setOpen(open) {
  if (open === state.open) return;
  state.open = open;
  if (open) {
    phone.hidden = false;
    hidePeek();
    renderLock();
    raf2(() => phone.classList.add('is-open'));
  } else {
    phone.classList.remove('is-open');
    hideCC();
    document.activeElement?.blur();
    if (state.lockScreen) state.locked = true;
    const done = (e) => {
      if (e && e.target !== phone) return;
      phone.removeEventListener('transitionend', done);
      if (!state.open) phone.hidden = true; // stop compositing while closed
    };
    phone.addEventListener('transitionend', done);
  }
}
function requestClose() { if (IN_GAME) nui('close'); setOpen(false); }

function renderLock() {
  const lock = $('#lock');
  lock.classList.toggle('is-unlocked', !state.locked);
  lock.innerHTML = `
    <div class="date">${esc(dateLine())}</div>
    <div class="time num">${esc(state.clock)}</div>
    <div class="notes">${state.notes.slice(0, 3).map((n) => `<div class="note">${tileHTML(n.app || 'messages')}<span><span class="t" style="display:block">${esc(n.title)}</span><span class="s" style="display:block">${esc(n.text)}</span></span></div>`).join('')}</div>
    <div class="bottom"><span class="round">${icon('flashlight')}</span><span class="lock-hint">${T.unlockHint}</span><span class="round">${icon('camera')}</span></div>`;
  renderStatus();
}
function unlock() {
  if (!state.locked) return;
  state.locked = false;
  $('#lock').classList.add('is-unlocked');
  renderStatus();
}
(function lockGestures() {
  const lock = $('#lock');
  let y0 = null;
  lock.addEventListener('pointerdown', (e) => { y0 = e.clientY; });
  lock.addEventListener('pointerup', (e) => { if (y0 != null && (y0 - e.clientY > 20 || Math.abs(y0 - e.clientY) < 6)) unlock(); y0 = null; });
})();

/* ───────── status bar + control centre ───────── */
function renderStatus() {
  const onWallpaper = state.locked || !state.app;
  $('#statusbar').classList.toggle('on-wallpaper', onWallpaper);
  $('#homeBar').classList.toggle('on-wallpaper', onWallpaper);
  $('#clock').textContent = state.clock;
}
function renderCC() {
  const foldable = !!dev().fold;
  $('#cc').innerHTML = `
    <div class="cc-grid">
      <button class="cc-tile ${state.theme === 'dark' ? 'on' : ''}" data-cc="theme">${icon('moon')}<span class="cap">${T.darkMode}</span></button>
      <button class="cc-tile ${state.dnd ? 'on' : ''}" data-cc="dnd">${icon('bell-off')}<span class="cap">${T.dnd}</span></button>
      ${foldable ? `<button class="cc-tile" data-cc="fold">${icon(dev().fold === 'tri' ? 'columns-3' : 'columns-2')}<span class="cap">${state.fold === 'open' ? T.foldUp : T.unfold}</span></button>` : ''}
      ${state.allowDeviceChange ? `<button class="cc-tile" data-cc="model">${icon('smartphone')}<span class="cap">${T.model}</span></button>` : ''}
      <label class="cc-tile cc-wide"><span>${T.phoneSize}</span><input type="range" data-cc="size" min="0.65" max="1" step="0.01" value="${state.scale}" /></label>
    </div>`;
}
function showCC() { if (state.locked) return; renderCC(); $('#cc').classList.add('show'); }
function hideCC() { const cc = $('#cc'); if (!cc.classList.contains('show')) return false; cc.classList.remove('show'); return true; }

/* ───────── home ───────── */
function renderHome() {
  const layer = $('#homeLayer');
  if (!layer) return;
  const unread = (state.msg.threads || []).reduce((n, t) => n + (t.unread || 0), 0);
  const appIcon = (id) => `<button class="app-icon" data-open="${id}">${tileHTML(id)}${id === 'messages' && unread ? `<span class="badge num">${unread}</span>` : ''}<span class="label">${T[id]}</span></button>`;
  if (isCover()) { // flip cover: clock, a live card, five pinned apps
    const last = state.notes[0];
    layer.innerHTML = `<div class="cover wallpaper">
      <div class="time num">${esc(state.clock)}</div><div class="date">${esc(dateLine())}</div>
      <button class="card" data-open="${last ? last.app || 'messages' : 'music'}">${tileHTML(last ? last.app || 'messages' : 'music')}<span><span class="t" style="display:block;font-weight:600">${esc(last ? last.title : '正在播放')}</span><span class="s" style="display:block;opacity:.8">${esc(last ? last.text : 'Radio Los Santos')}</span></span></button>
      <div class="pinned">${['messages', 'wallet', 'camera', 'maps', 'settings'].map((id) => `<button class="app-icon" data-open="${id}" style="width:auto">${tileHTML(id)}</button>`).join('')}</div>
    </div>`;
    return;
  }
  const grid = `<div class="grid">${APPS.filter((a) => !DOCK.includes(a.id)).map((a) => appIcon(a.id)).join('')}</div>`;
  const clockW = `<div class="widget"><div class="sub">洛圣都 · 晴 24°</div><div><div class="big num">${esc(state.clock)}</div><div class="sub">${esc(dateLine())}</div></div></div>`;
  const weatherW = `<div class="widget"><div class="row2"><span class="sub">本周天气</span>${icon('cloud-sun')}</div><div class="sub">周五 26° · 周六 23° · 周日 21°</div></div>`;
  const walletW = `<button class="widget" data-open="wallet" style="text-align:left"><div class="row2"><span class="sub">${T.balance}</span>${icon('wallet')}</div><div class="big num" style="font-size:calc(32*var(--pt))">${state.wallet.balance == null ? '—' : money.format(state.wallet.balance)}</div></button>`;
  const musicW = `<div class="widget"><div class="row2"><span class="sub">正在播放</span>${icon('music')}</div><div><div style="font-weight:600">Radio Los Santos</div><div class="sub">${icon('play')} &nbsp; ${icon('skip-forward')}</div></div></div>`;
  const pages = panes() === 3 ? [clockW + weatherW, grid, walletW + musicW] : panes() === 2 ? [clockW + weatherW, grid] : [clockW + grid];
  layer.innerHTML = `<div class="home wallpaper">
    <div class="pages">${pages.map((p) => `<div class="page">${p}</div>`).join('')}</div>
    <div class="dock">${DOCK.map(appIcon).join('')}</div>
  </div>`;
}

/* app opens from its icon (FLIP from the icon rect) and closes back into it */
function openApp(id) {
  if (!RENDER[id]) return banner(T[id] || id, T.demoApp, id);
  hideCC();
  const iconEl = $(`#homeLayer [data-open="${id}"] .tile`);
  const layer = $('#appLayer');
  layer.innerHTML = `<section class="app from-icon" data-app="${id}"></section>`;
  const el = layer.firstElementChild;
  state.app = id;
  RENDER[id](el);
  placeOnIcon(el, iconEl);
  el.getBoundingClientRect();
  raf2(() => { el.classList.remove('from-icon'); el.style.transform = ''; });
  LOAD[id]?.();
  renderStatus();
}
function closeApp() {
  const el = $('#appLayer .app');
  if (!el) return;
  renderHome();
  const iconEl = $(`#homeLayer [data-open="${state.app}"] .tile`);
  state.app = null;
  el.classList.add('from-icon');
  placeOnIcon(el, iconEl);
  setTimeout(() => el.remove(), 320);
  document.activeElement?.blur();
  renderStatus();
}
function placeOnIcon(el, iconEl) {
  if (!iconEl) { el.style.transform = 'scale(0.92)'; return; }
  const s = $('#screen').getBoundingClientRect();
  const r = iconEl.getBoundingClientRect();
  el.style.transform = `translate(${r.left - s.left}px, ${r.top - s.top}px) scale(${r.width / s.width}, ${r.height / s.height})`;
}

/* ───────── Messages: list | chat | contact (1, 2 or 3 panes) ───────── */
const AVATAR = ['#ff9f0a', '#30b0c7', '#5e5ce6', '#ff375f', '#34c759', '#bf5af2', '#64d2ff'];
const avatarBg = (name) => { let h = 0; for (const c of String(name)) { h = Math.imul(h + c.codePointAt(0), 2654435761); h ^= h >>> 15; } return AVATAR[(h >>> 0) % AVATAR.length]; };
const initial = (name) => esc([...String(name)][0] || '?');

function renderMessages(el) {
  el.innerHTML = `
    <div class="split">
      <div class="view pane-list">
        <div class="nav"><span></span><button class="action" data-demo="new" title="新信息">${icon('plus')}</button></div>
        <div class="large-title">${T.messages}</div>
        <label class="search">${icon('search')}<input id="msgSearch" placeholder="${T.search}" /></label>
        <div class="scroll" id="threadList"></div>
      </div>
      <div class="view pane-detail is-pushed is-empty" id="detail"></div>
      <div class="view pane-extra" id="profile"></div>
    </div>`;
  $('#msgSearch', el).addEventListener('input', renderThreadList);
  renderThreadList();
  renderDetail(); // restores the open chat and its draft when the app is reopened
  syncMessagesLayout();
}
async function loadThreads() {
  state.msg.error = false;
  const res = await nui('messages:threads');
  if (res.ok) state.msg.threads = res.threads; else state.msg.error = true;
  renderThreadList();
  if (!state.app) renderHome();
  if (params.get('thread') && state.msg.selected == null) selectThread(Number(params.get('thread')));
}
function renderThreadList() {
  const list = $('#threadList');
  if (!list) return;
  const m = state.msg;
  if (m.error) { list.innerHTML = `<div class="error">${T.loadFailed}<button class="pill" data-retry="threads">${T.retry}</button></div>`; return; }
  if (!m.threads) { list.innerHTML = `<div class="group">${skeletonRows(6)}</div>`; return; }
  const q = ($('#msgSearch')?.value || '').trim().toLowerCase();
  const rows = m.threads.filter((t) => !q || t.name.toLowerCase().includes(q) || t.last.toLowerCase().includes(q));
  if (!rows.length) { list.innerHTML = empty('message-circle', T.noChats, T.noChatsSub); return; }
  list.innerHTML = `<div class="group" style="--inset:72">${rows.map((t) => `
    <button class="row ${t.id === m.selected ? 'is-selected' : ''}" data-thread="${t.id}">
      <span class="dot ${t.unread ? '' : 'off'}"></span>
      <span class="avatar" style="background:${avatarBg(t.name)}">${initial(t.name)}</span>
      <span class="grow"><span class="t" style="font-weight:${t.unread ? 600 : 400}">${esc(t.name)}</span><span class="s">${esc(t.last)}</span></span>
      <span class="meta num">${esc(t.time)}</span>
    </button>`).join('')}</div>`;
}
async function selectThread(id) {
  const m = state.msg;
  const t = (m.threads || []).find((x) => x.id === id);
  if (!t) return;
  m.selected = id;
  t.unread = 0;
  renderThreadList();
  renderDetail();
  syncMessagesLayout();
  if (!m.messages[id]) {
    const res = await nui('messages:thread', { id });
    m.messages[id] = res.ok ? res.messages : [];
    if (m.selected === id) renderBubbles(true);
  }
}
function renderDetail() {
  const d = $('#detail');
  if (!d) return;
  const m = state.msg;
  const t = (m.threads || []).find((x) => x.id === m.selected);
  d.classList.toggle('is-empty', !t);
  renderProfile(t);
  if (!t) { d.innerHTML = empty('message-circle', T.pickChat, T.pickChatSub); return; }
  d.innerHTML = `
    <div class="nav"><button class="back" data-back>${icon('chevron-left')}${T.messages}</button><span class="title">${esc(t.name)}</span><button class="action" data-demo="call" title="${T.call}">${icon('phone')}</button></div>
    <div class="thread" id="bubbles"></div>
    <form class="composer" id="composer">
      <input id="draft" maxlength="500" placeholder="${T.typeMessage}" value="${esc(m.drafts[t.id] || '')}" autocomplete="off" />
      <button class="send" id="sendBtn" ${(m.drafts[t.id] || '').trim() ? '' : 'disabled'} aria-label="${T.send}">${icon('send')}</button>
    </form>`;
  const input = $('#draft', d);
  input.addEventListener('input', () => { m.drafts[t.id] = input.value; $('#sendBtn', d).disabled = !input.value.trim(); });
  $('#composer', d).addEventListener('submit', (e) => { e.preventDefault(); sendMessage(t.id); });
  renderBubbles(true);
}
function renderProfile(t) {
  const p = $('#profile');
  if (!p) return;
  if (!t) { p.innerHTML = empty('user', T.contacts, '选中对话后会显示对方资料。'); return; }
  p.innerHTML = `
    <div class="nav"><span></span></div>
    <div class="profile">
      <span class="avatar" style="background:${avatarBg(t.name)}">${initial(t.name)}</span>
      <div class="name">${esc(t.name)}</div>
      <div class="num" style="color:var(--label-2)">${esc(t.phone || '')}</div>
      <div class="actions">
        <button class="act" data-demo="call">${icon('phone')}<span>${T.call}</span></button>
        <button class="act" data-pay="${esc((t.phone || '').replace(/\s/g, ''))}">${icon('wallet')}<span>${T.transfer}</span></button>
        <button class="act" data-demo="mute">${icon('bell-off')}<span>${T.mute}</span></button>
      </div>
    </div>`;
}
function renderBubbles(scrollToEnd) {
  const box = $('#bubbles');
  if (!box) return;
  const list = state.msg.messages[state.msg.selected];
  if (!list) { box.innerHTML = '<span class="skeleton" style="width:55%;height:calc(36*var(--pt));border-radius:calc(18*var(--pt))"></span><span class="skeleton" style="width:40%;height:calc(36*var(--pt));border-radius:calc(18*var(--pt));align-self:flex-end"></span>'; return; }
  box.innerHTML = `<div class="stamp">${T.today}</div>` + list.map((b) => `<div class="bubble ${b.out ? 'out' : 'in'} ${b.pending ? 'pending' : ''}">${esc(b.text)}</div>`).join('');
  if (scrollToEnd) box.scrollTop = box.scrollHeight;
}
async function sendMessage(id) {
  const m = state.msg;
  const text = (m.drafts[id] || '').trim();
  if (!text) return;
  const temp = { id: `tmp${Date.now()}`, out: true, text, pending: true };
  (m.messages[id] ||= []).push(temp);
  m.drafts[id] = '';
  const input = $('#draft');
  if (input) { input.value = ''; $('#sendBtn').disabled = true; }
  renderBubbles(true);
  const res = await nui('messages:send', { threadId: id, text }); // the server checks length, rate and the target
  const list = m.messages[id];
  const i = list.indexOf(temp);
  if (res.ok) list[i] = res.message; else list.splice(i, 1, { ...temp, pending: false, text: `${text} ⚠` });
  const t = m.threads.find((x) => x.id === id);
  if (t && res.ok) { t.last = text; t.time = res.message.time; renderThreadList(); }
  if (m.selected === id) renderBubbles(true);
}
/* 1 pane: list OR chat (push). 2–3 panes: side by side. Same DOM, so folding loses nothing. */
function syncMessagesLayout() {
  const list = $('.pane-list'), detail = $('#detail');
  if (!list || !detail) return;
  const showDetail = state.msg.selected != null;
  detail.classList.toggle('is-pushed', !showDetail);
  list.classList.toggle('is-under', showDetail);
}
function messagesBack() {
  if (panes() === 1 && state.msg.selected != null) {
    state.msg.selected = null;
    syncMessagesLayout();
    renderThreadList();
    setTimeout(renderDetail, 300);
    document.activeElement?.blur();
    return true;
  }
  return false;
}

/* ───────── Wallet: balance | history | transfer (1, 2 or 3 panes) ───────── */
const transferForm = (id) => `
  <form class="transfer-form" data-form="${id}" autocomplete="off">
    <label class="field"><span>${T.to}</span><input data-f="to" inputmode="numeric" maxlength="10" placeholder="5550123" value="${esc(state.wallet.prefill)}" /></label>
    <label class="field"><span>${T.amount}</span><input data-f="amt" class="big num" inputmode="numeric" maxlength="11" placeholder="$0" /></label>
    <div class="hint" data-f="hint"></div>
    <button class="pill primary" data-f="btn" disabled>${T.next}</button>
  </form>`;
function renderWallet(el) {
  el.innerHTML = `
    <div class="view">
      <div class="nav"><button class="back" data-back>${icon('chevron-left')}</button><span></span></div>
      <div class="large-title">${T.wallet}</div>
      <div class="scroll"><div class="wallet-body" id="walletBody"></div></div>
      <div class="scrim" data-sheet-close></div>
      <div class="sheet"><div class="grabber"></div><h3>${T.transfer}</h3>${transferForm('sheet')}</div>
    </div>`;
  bindTransferForm($('[data-form="sheet"]', el));
  renderWalletBody();
}
async function loadWallet() {
  state.wallet.error = false;
  const res = await nui('wallet:get');
  if (res.ok) Object.assign(state.wallet, { balance: res.balance, tx: res.tx }); else state.wallet.error = true;
  renderWalletBody();
  if (params.get('sheet') || state.wallet.prefill) openSheet();
}
function renderWalletBody() {
  const b = $('#walletBody');
  if (!b) return;
  const w = state.wallet;
  if (w.error) { b.innerHTML = `<div class="error">${T.loadFailed}<button class="pill" data-retry="wallet">${T.retry}</button></div>`; return; }
  const keep = $('[data-form="inline"]', b); // keep a half-typed inline form across re-renders
  if (keep) keep.remove();
  b.innerHTML = `
    <section>
      <div class="balance">
        <div class="k">${T.balance}</div>
        <div class="v num">${w.balance == null ? '<span class="skeleton" style="width:60%;height:calc(40*var(--pt));background:rgba(255,255,255,.2)"></span>' : money.format(w.balance)}</div>
        <button class="pill light" data-sheet-open ${w.balance == null ? 'disabled' : ''}>${icon('arrow-up-right')}${T.transfer}</button>
      </div>
    </section>
    <section>
      <div class="group-title">${T.history}</div>
      ${!w.tx ? `<div class="group">${skeletonRows(4)}</div>` : !w.tx.length ? empty('landmark', T.noTx, '') :
        `<div class="group" style="--inset:64">${w.tx.map((t) => `
          <div class="row">
            <span class="tx-ico" style="color:${t.amount > 0 ? 'var(--green)' : 'var(--label-2)'}">${icon(t.amount > 0 ? 'arrow-down-left' : 'arrow-up-right')}</span>
            <span class="grow"><span class="t">${esc(t.title)}</span><span class="s">${esc(t.time)}</span></span>
            <span class="amt num ${t.amount > 0 ? 'plus' : ''}">${t.amount > 0 ? '+' : '−'}${money.format(Math.abs(t.amount))}</span>
          </div>`).join('')}</div>`}
    </section>
    <section class="transfer-inline"><div class="form-card"><h3>${T.transfer}</h3><div id="inlineSlot"></div></div></section>`;
  const slot = $('#inlineSlot', b);
  if (keep) slot.replaceWith(keep);
  else { slot.outerHTML = transferForm('inline'); bindTransferForm($('[data-form="inline"]', b)); }
}
function bindTransferForm(form) {
  const f = (k) => $(`[data-f="${k}"]`, form);
  const to = f('to'), amt = f('amt'), btn = f('btn'), hint = f('hint');
  let step = 'form';
  const parse = () => ({ number: to.value.replace(/\s/g, ''), amount: Number(amt.value.replace(/[$,]/g, '')) });
  const valid = () => { const { number, amount } = parse(); return /^\d{3,10}$/.test(number) && Number.isInteger(amount) && amount >= 1 && amount <= 1e6; };
  const reset = () => { step = 'form'; btn.textContent = T.next; hint.textContent = ''; btn.disabled = !valid(); };
  form.resetForm = reset;
  to.addEventListener('input', reset);
  amt.addEventListener('input', () => { const n = amt.value.replace(/\D/g, '').slice(0, 7); amt.value = n ? money.format(Number(n)) : ''; reset(); });
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const { number, amount } = parse();
    if (!/^\d{3,10}$/.test(number)) { hint.textContent = T.badNumber; return; }
    if (!Number.isInteger(amount) || amount < 1 || amount > 1e6) { hint.textContent = T.badAmount; return; }
    if (step === 'form') { step = 'confirm'; btn.textContent = T.confirm(money.format(amount), number); return; } // explicit confirm step
    btn.disabled = true; btn.textContent = T.sending;
    const res = await nui('wallet:transfer', { to: number, amount }); // intent only; the server re-checks everything
    btn.disabled = false;
    if (!res.ok) { step = 'form'; btn.textContent = T.next; hint.textContent = res.error || T.loadFailed; return; }
    state.wallet.balance = res.balance;
    state.wallet.tx = [{ title: `${T.transfer} · ${number}`, time: state.clock, amount: -amount }, ...(state.wallet.tx || [])];
    state.wallet.prefill = '';
    to.value = ''; amt.value = ''; reset();
    closeSheet();
    renderWalletBody();
    banner(T.sent, `${money.format(amount)} → ${number}`, 'wallet');
  });
  reset();
}
function openSheet() {
  const a = $('#appLayer .app');
  if (!a) return;
  const which = panes() === 3 ? 'inline' : 'sheet';
  const to = $(`[data-form="${which}"] [data-f="to"]`);
  if (state.wallet.prefill && to) { to.value = state.wallet.prefill; to.closest('form').resetForm?.(); }
  if (which === 'sheet') a.classList.add('sheet-open');
  setTimeout(() => (state.wallet.prefill ? $(`[data-form="${which}"] [data-f="amt"]`) : to)?.focus(), which === 'sheet' ? 260 : 0);
}
function closeSheet() { const a = $('#appLayer .app'); if (!a?.classList.contains('sheet-open')) return false; a.classList.remove('sheet-open'); document.activeElement?.blur(); return true; }

/* ───────── Settings ───────── */
function renderSettings(el) {
  el.innerHTML = `
    <div class="view">
      <div class="nav"><button class="back" data-back>${icon('chevron-left')}</button><span></span></div>
      <div class="large-title">${T.settings}</div>
      <div class="scroll"><div class="settings-body">
        <div><div class="group-title">${T.appearance}</div>
        <div class="group">
          <div class="row"><span class="grow t">${T.darkMode}</span><button class="switch ${state.theme === 'dark' ? 'on' : ''}" data-set="theme" role="switch" aria-checked="${state.theme === 'dark'}"></button></div>
          <div class="row"><span class="grow t">${T.phoneSize}</span><input type="range" data-set="size" min="0.65" max="1" step="0.01" value="${state.scale}" /></div>
        </div></div>
        ${state.allowDeviceChange ? `<div id="model"><div class="group-title">${T.model}</div><div class="group">${Object.entries(DEVICES).map(([id, d]) => `
          <button class="row" data-device="${id}"><span class="grow t">${esc(d.label)}</span>${id === state.device ? `<span class="check">${icon('check')}</span>` : ''}</button>`).join('')}</div></div>` : ''}
        <div><div class="group-title">${T.about}</div><div class="group"><div class="row"><span class="grow t">${esc(dev().label)}</span><span class="meta">1.1</span></div></div></div>
      </div></div>
    </div>`;
}

const RENDER = { messages: renderMessages, wallet: renderWallet, settings: renderSettings };
const LOAD = { messages: loadThreads, wallet: loadWallet };

/* ───────── helpers ───────── */
function skeletonRows(n) {
  return Array.from({ length: n }, () => `<div class="row"><span class="avatar" style="background:var(--fill)"></span><span class="grow"><span class="skeleton" style="width:45%;margin-bottom:calc(8*var(--pt))"></span><span class="skeleton" style="width:75%"></span></span></div>`).join('');
}
function empty(ic, title, sub) { return `<div class="empty">${icon(ic)}<div class="t">${esc(title)}</div><div>${esc(sub)}</div></div>`; }
function dateLine() { return new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' }); }
let bannerTimer, peekTimer;
function banner(title, text, app) {
  const b = $('#banner');
  b.innerHTML = `${tileHTML(app || 'messages')}<span><span class="t">${esc(title)}</span><span class="s">${esc(text)}</span></span>`;
  b.dataset.app = app || '';
  b.classList.add('show');
  clearTimeout(bannerTimer);
  bannerTimer = setTimeout(() => b.classList.remove('show'), 3500);
}
function peek(title, text, app) { // phone closed: a banner without NUI focus
  const p = $('#peek');
  p.dataset.theme = state.theme;
  p.dataset.brand = dev().brand;
  p.innerHTML = `<div class="banner">${tileHTML(app || 'messages')}<span><span class="t">${esc(title)}</span><span class="s">${esc(text)}</span></span></div>`;
  p.classList.add('show');
  clearTimeout(peekTimer);
  peekTimer = setTimeout(hidePeek, 4000);
}
function hidePeek() { $('#peek').classList.remove('show'); }
function notify(title, text, app) {
  state.notes.unshift({ title, text, app });
  state.notes = state.notes.slice(0, 10);
  if (isCover() && !state.app) renderHome();
  if (state.dnd) return;
  if (!state.open) peek(title, text, app);
  else if (state.locked) renderLock();
  else banner(title, text, app);
}
function goBack() {
  if (hideCC()) return;
  if (closeSheet()) return;
  if (state.app === 'messages' && messagesBack()) return;
  if (state.app) closeApp();
}
function setClock(c) {
  state.clock = c;
  renderStatus();
  const big = $('#homeLayer .widget .big, #homeLayer .cover .time');
  if (big) big.textContent = c;
  const lt = $('#lock .time');
  if (lt) lt.textContent = c;
}

/* ───────── events ───────── */
document.addEventListener('click', (e) => {
  const t = e.target.closest('[data-open],[data-thread],[data-back],[data-retry],[data-sheet-open],[data-sheet-close],[data-cc],[data-set],[data-device],[data-pay],[data-demo],#homeBar,#sbIcons,#banner,#cc');
  if (!t || t.closest('#lock') || t.id === 'phone') return;
  const ds = t.dataset;
  if (ds.open) openApp(ds.open);
  else if (ds.thread) selectThread(Number(ds.thread));
  else if ('back' in ds) goBack();
  else if (ds.retry === 'threads') { state.msg.threads = null; renderThreadList(); loadThreads(); }
  else if (ds.retry === 'wallet') { state.wallet.error = false; renderWalletBody(); loadWallet(); }
  else if ('sheetOpen' in ds) openSheet();
  else if ('sheetClose' in ds) closeSheet();
  else if (ds.pay !== undefined) { state.wallet.prefill = ds.pay; closeApp(); setTimeout(() => openApp('wallet'), 280); }
  else if (ds.demo) banner(ds.demo === 'call' ? T.call : ds.demo === 'mute' ? T.mute : T.messages, T.demoApp, ds.demo === 'new' ? 'messages' : 'contacts');
  else if (ds.cc === 'theme') { setTheme(state.theme === 'dark' ? 'light' : 'dark'); saveSettings(); renderCC(); }
  else if (ds.cc === 'dnd') { state.dnd = !state.dnd; renderCC(); }
  else if (ds.cc === 'fold') { hideCC(); toggleFold(); }
  else if (ds.cc === 'model') { hideCC(); openApp('settings'); setTimeout(() => $('#model')?.scrollIntoView({ behavior: 'smooth' }), 450); }
  else if (ds.set === 'theme') { setTheme(state.theme === 'dark' ? 'light' : 'dark'); t.classList.toggle('on', state.theme === 'dark'); saveSettings(); }
  else if (ds.device) { setDevice(ds.device); setTimeout(() => state.app === 'settings' && renderSettings($('#appLayer .app')), 520); }
  else if (t.id === 'homeBar') { hideCC(); closeSheet(); if (state.app) closeApp(); }
  else if (t.id === 'sbIcons') { $('#cc').classList.contains('show') ? hideCC() : showCC(); }
  else if (t.id === 'cc') { if (e.target === t) hideCC(); }
  else if (t.id === 'banner') { t.classList.remove('show'); if (ds.app && RENDER[ds.app] && ds.app !== state.app) { if (state.app) closeApp(); setTimeout(() => openApp(ds.app), 260); } }
});
document.addEventListener('change', (e) => {
  if (e.target.matches('[data-cc="size"],[data-set="size"]')) { setScale(Number(e.target.value)); saveSettings(); }
});
const typing = () => ['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName) && document.activeElement.type !== 'range';
window.addEventListener('keydown', (e) => {
  if (!IN_GAME && !typing() && (e.key === 'o' || e.key === 'O')) { state.open ? setOpen(false) : window.postMessage({ action: 'open' }, '*'); return; }
  if (!IN_GAME && !typing() && (e.key === 'n' || e.key === 'N')) { notify('阿杰', '老地方见？', 'messages'); return; }
  if (!state.open) return;
  if (state.locked && (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowUp')) { e.preventDefault(); unlock(); return; }
  if (e.key === 'Escape') { e.preventDefault(); if (!hideCC() && !closeSheet()) requestClose(); }
  else if (e.key === 'Backspace' && !typing()) { e.preventDefault(); goBack(); }
  else if ((e.key === 'f' || e.key === 'F') && !typing() && !state.locked) toggleFold();
});
// typing must not walk the character: keep-input off while a text field has focus
document.addEventListener('focusin', (e) => { if (e.target.matches('input:not([type=range])')) nui('keepInput', { value: false }); });
document.addEventListener('focusout', (e) => { if (e.target.matches('input:not([type=range])')) nui('keepInput', { value: true }); });

window.addEventListener('message', ({ data: d }) => {
  if (!d || typeof d !== 'object') return;
  switch (d.action) {
    case 'open':
      if (d.theme) setTheme(d.theme);
      if (d.scale) setScale(d.scale);
      if (typeof d.lockScreen === 'boolean') state.lockScreen = d.lockScreen;
      if (typeof d.allowDeviceChange === 'boolean') state.allowDeviceChange = d.allowDeviceChange;
      if (d.device && DEVICES[d.device]) state.device = d.device;
      if (d.fold) state.fold = d.fold;
      if (d.clock) state.clock = d.clock;
      if (!state.lockScreen) state.locked = false;
      applyDevice();
      setOpen(true);
      if (!state.msg.threads) loadThreads();
      if (state.wallet.balance == null) nui('wallet:get').then((r) => { if (r.ok) { Object.assign(state.wallet, { balance: r.balance, tx: r.tx }); if (!state.app) renderHome(); } });
      break;
    case 'close': setOpen(false); break;
    case 'clock': setClock(d.clock); break;
    case 'notify': notify(d.title, d.text, d.app); break;
    case 'message': { // the server pushed an incoming message
      const m = state.msg;
      const t = (m.threads || []).find((x) => x.id === d.threadId);
      if (t) { t.last = d.message.text; t.time = d.message.time; if (m.selected !== d.threadId || !state.open) t.unread = (t.unread || 0) + 1; }
      if (m.messages[d.threadId]) m.messages[d.threadId].push(d.message);
      renderThreadList();
      if (m.selected === d.threadId) renderBubbles(true);
      if (!state.app) renderHome();
      break;
    }
  }
});

/* ───────── boot ───────── */
$('#content').innerHTML = '<div id="homeLayer"></div><div id="appLayer"></div>';
$('#sbIcons').innerHTML = icon('signal') + icon('wifi') + icon('battery-full');
setScale(state.scale);
applyDevice();
if (!IN_GAME) {
  document.body.classList.add('preview');
  const now = new Date();
  const p = (k) => params.get(k);
  if (p('theme')) setTheme(p('theme'));
  if (p('unlock')) state.locked = false;
  if (p('note')) state.notes.push({ title: '阿杰', text: '老地方见？', app: 'messages' }, { title: '钱包', text: '收到工资 $3,200', app: 'wallet' });
  window.postMessage({ action: 'open', clock: `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`, device: p('device') || 'bar', fold: p('fold') || 'closed' }, '*');
  if (p('app')) setTimeout(() => openApp(p('app')), 600);
  if (p('cc')) setTimeout(showCC, 600);
}

const MOCK = {
  balance: 48250,
  tx: [
    { title: '工资 · 洛圣都运输', time: '今天 09:00', amount: 3200 },
    { title: '转账 · 5551834', time: '昨天 22:14', amount: -500 },
    { title: 'Benny 修车厂', time: '昨天 18:40', amount: -1850 },
    { title: '24/7 便利店', time: '周一', amount: -64 },
  ],
  threads: [
    { id: 1, name: '阿杰', phone: '555 2091', last: '老地方见？', time: '21:42', unread: 2, messages: [
      { id: 1, out: false, text: '今晚有空吗' }, { id: 2, out: true, text: '有，几点？' }, { id: 3, out: false, text: '十点，带上车' }, { id: 4, out: false, text: '老地方见？' }] },
    { id: 2, name: '小雨', phone: '555 1834', last: '收到，谢谢！', time: '20:15', unread: 0, messages: [
      { id: 1, out: true, text: '钱转给你了' }, { id: 2, out: false, text: '收到，谢谢！' }] },
    { id: 3, name: 'Benny 修车厂', phone: '555 7712', last: '你的车修好了，可以来拿', time: '18:02', unread: 1, messages: [
      { id: 1, out: false, text: '你的车修好了，可以来拿' }] },
    { id: 4, name: '洛圣都警局', phone: '911', last: '请于明天到局里做笔录。', time: '周二', unread: 0, messages: [
      { id: 1, out: false, text: '请于明天到局里做笔录。' }] },
  ],
};
