/* Flex mode: a half-folded foldable standing on a table (references/real-foldables.md, foldable.md).
   Samsung's angle zones (Galaxy Z Fold support guide): 75–80° cover view, 80–115° Flex view, 115–180° full view;
   designed range 75–115°. This file renders the phone as two slabs in 3D (transform only):
   - 90–115° (obtuse): L shape, top half leans back; top = content, bottom = full control panel
   - 80–90°  (acute):  L shape, top half leans forward over the bottom; bottom keeps only big controls near the front edge
   - 75–80°  (tent, book folds with a cover screen): stood up like a tent, the cover screen faces you with wide media
   - drag the top edge to change the angle 1:1; past 115° the phone opens flat, below 75° it closes.
   Loaded after app.js and uses its globals. */

const FLEX = {
  tall: { kind: 'book', tent: true },   // Galaxy Z Fold8 Ultra (Samsung's Fold8 Ultra guide documents Flex mode)
  passport: { kind: 'book', tent: false }, // iPhone Duo tabletop (Apple: content moves off the crease)
  flip: { kind: 'clam', tent: false },  // Galaxy Z Flip8 Flex mode
  // wide (Fold8): Samsung US support lists Flex mode as not supported, so it is off here. trifold: no half-open state.
};
const ANGLE = { min: 75, tentMax: 80, acuteMax: 90, max: 115 };
const flexState = { on: false, angle: 100, playing: true };
const rig = document.getElementById('rig');
const anchor = document.querySelector('.anchor');

const flexSupported = () => !!FLEX[state.device];
const flexZone = () => (flexState.angle < ANGLE.tentMax && FLEX[state.device]?.tent ? 'tent' : flexState.angle < ANGLE.acuteMax ? 'acute' : 'obtuse');

/* geometry: the open (inner) screen turned so the hinge is horizontal; the flip already is */
function flexDims() {
  const d = dev();
  const o = d.open, c = d.closed;
  const turn = d.fold === 'book';
  const body = turn ? [o.body[1], o.body[0]] : o.body;
  const screen = turn ? [o.screen[1], o.screen[0]] : o.screen;
  const coverBody = [c.body[1], c.body[0]], coverScreen = [c.screen[1], c.screen[0]]; // tent: cover turned landscape
  return { body, screen, coverBody, coverScreen };
}

function enterFlex(angle = 100) {
  if (!flexSupported()) { banner('Flex 模式', '这个机型不支持 Flex 模式', 'settings'); return; }
  hideCC();
  const go = () => { flexState.on = true; flexState.angle = angle; anchor.classList.add('in-flex'); renderFlex(); };
  if (state.fold !== 'open') { setFold('open'); setTimeout(go, 520); } else go();
}
function exitFlex(to = 'open') {
  if (!flexState.on) return;
  flexState.on = false;
  anchor.classList.remove('in-flex');
  rig.innerHTML = '';
  if (to === 'closed') { state.fold = 'closed'; applyDevice(); nui('fold', { folded: true }); }
  else applyDevice();
}
window.exitFlex = exitFlex;
window.flexTile = () => (flexSupported() ? `<button class="cc-tile ${flexState.on ? 'on' : ''}" data-cc="flex">${icon('columns-2')}<span class="cap">Flex 模式</span></button>` : '');

/* ───────── content per zone ───────── */
function flexContent() {
  const app = state.app;
  const t = (state.msg.threads || []).find((x) => x.id === state.msg.selected) || (state.msg.threads || [])[0];
  const bubbles = (t && state.msg.messages[t.id]) || [];
  const last = state.notes[0];
  const song = { title: 'Los Santos Nights', artist: 'Radio Los Santos', pos: 74, len: 212 };
  const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
  const playBtn = `<button class="fx-round big" data-fx="play">${icon(flexState.playing ? 'pause' : 'play')}</button>`;
  const panel = `<div class="fx-panel"><button data-fx="shot" title="截图">${icon('camera')}</button><span class="fx-angle num">${Math.round(flexState.angle)}°</span><button data-fx="exit" title="退出 Flex 模式">${icon('x')}</button></div>`;

  if (app === 'messages' && t) {
    return {
      top: `<div class="fx-chat"><div class="fx-title">${esc(t.name)}</div><div class="fx-bubbles">${bubbles.slice(-4).map((b) => `<div class="bubble ${b.out ? 'out' : 'in'}">${esc(b.text)}</div>`).join('') || '<div class="fx-sub">还没有信息</div>'}</div></div>`,
      bottom: `<div class="fx-controls">
        <div class="fx-row secondary">${(state.msg.threads || []).slice(0, 5).map((x) => `<button class="fx-chip ${x.id === t.id ? 'on' : ''}" data-fx-thread="${x.id}"><span class="avatar" style="background:${avatarBg(x.name)}">${initial(x.name)}</span>${esc(x.name)}</button>`).join('')}</div>
        <div class="fx-row secondary">${['马上到', '好的', '晚点打给你'].map((q) => `<button class="fx-chip" data-fx-quick="${esc(q)}">${esc(q)}</button>`).join('')}</div>
        <form class="fx-compose" data-fx-form="${t.id}"><input placeholder="${T.typeMessage}" maxlength="500" /><button class="send" aria-label="${T.send}">${icon('send')}</button></form>
      </div>${panel}`,
      cover: `<div class="fx-cover-row"><span class="avatar" style="background:${avatarBg(t.name)}">${initial(t.name)}</span><div><div class="fx-title">${esc(t.name)}</div><div class="fx-sub">${esc(t.last)}</div></div></div>`,
    };
  }
  if (app === 'wallet') {
    return {
      top: `<div class="fx-wallet"><div class="fx-sub">${T.balance}</div><div class="fx-big num">${state.wallet.balance == null ? '—' : money.format(state.wallet.balance)}</div>
        <div class="fx-tx">${(state.wallet.tx || []).slice(0, 2).map((x) => `<span>${esc(x.title)}</span><span class="num ${x.amount > 0 ? 'plus' : ''}">${x.amount > 0 ? '+' : '−'}${money.format(Math.abs(x.amount))}</span>`).join('')}</div></div>`,
      bottom: `<div class="fx-controls"><div class="fx-row"><button class="fx-pill" data-fx="transfer">${icon('arrow-up-right')}${T.transfer}</button></div><div class="fx-sub secondary">展开手机输入金额，转账要在完整画面确认</div></div>${panel}`,
      cover: `<div class="fx-cover-row"><div><div class="fx-sub">${T.balance}</div><div class="fx-big num">${state.wallet.balance == null ? '—' : money.format(state.wallet.balance)}</div></div></div>`,
    };
  }
  // default + music: media is what Flex mode is for
  return {
    top: `<div class="fx-media"><div class="fx-art">${icon('music')}</div><div><div class="fx-title">${song.title}</div><div class="fx-sub">${song.artist}</div><div class="fx-sub num">${esc(state.clock)} · ${esc(dateLine())}</div></div></div>`,
    bottom: `<div class="fx-controls">
      <div class="fx-row secondary fx-progress"><span class="num">${fmt(song.pos)}</span><span class="fx-bar"><span style="width:${(song.pos / song.len) * 100}%"></span></span><span class="num">${fmt(song.len)}</span></div>
      <div class="fx-row"><button class="fx-round" data-fx="prev">${icon('chevron-left')}</button>${playBtn}<button class="fx-round" data-fx="next">${icon('skip-forward')}</button></div>
      <div class="fx-row secondary">${['messages', 'wallet', 'maps', 'camera'].map((id) => `<button class="app-icon" data-fx-open="${id}">${tileHTML(id)}</button>`).join('')}</div>
    </div>${panel}`,
    cover: `<div class="fx-cover-row"><div class="fx-art small">${icon('music')}</div><div><div class="fx-title">${song.title}</div><div class="fx-sub">${song.artist}</div></div>${playBtn}</div>
      ${last ? `<div class="fx-cover-note">${tileHTML(last.app || 'messages')}<span>${esc(last.title)}：${esc(last.text)}</span></div>` : ''}`,
  };
}

/* ───────── render ───────── */
function renderFlex() {
  if (!flexState.on) return;
  const { body, screen, coverBody, coverScreen } = flexDims();
  const zone = flexZone();
  const c = flexContent();
  const half = body[1] / 2, sHalf = screen[1] / 2;
  const bx = (body[0] - screen[0]) / 2, by = half - sHalf;
  rig.dataset.zone = zone;
  rig.dataset.theme = state.theme;
  rig.dataset.brand = dev().brand;
  rig.style.setProperty('--fw', zone === 'tent' ? coverBody[0] : body[0]);
  rig.style.setProperty('--fh', zone === 'tent' ? coverBody[1] : half);
  rig.style.setProperty('--fbx', zone === 'tent' ? (coverBody[0] - coverScreen[0]) / 2 : bx);
  rig.style.setProperty('--fby', zone === 'tent' ? (coverBody[1] - coverScreen[1]) / 2 : by);
  rig.innerHTML = zone === 'tent'
    ? `<div class="fx-stage">
        <div class="slab front"><div class="glass cover">${c.cover}</div><div class="grab" data-grab></div><div class="sheen"></div></div>
      </div><div class="fx-hint">${Math.round(flexState.angle)}° · 外屏模式</div>`
    : `<div class="fx-stage">
        <div class="slab top"><div class="glass top-half">${c.top}</div><div class="grab" data-grab></div><div class="sheen"></div></div>
        <div class="slab bottom"><div class="glass bottom-half">${c.bottom}</div><div class="sheen"></div></div>
      </div>`;
  applyAngle();
}
function applyAngle() {
  const a = flexState.angle;
  rig.style.setProperty('--lean', `${a - 90}deg`);          // top half: + leans back, − leans forward
  rig.style.setProperty('--half', `${a / 2}deg`);           // tent: each side tilts half the angle
  rig.style.setProperty('--shade', Math.max(0, (90 - a) / 30).toFixed(2)); // acute: top half faces down, darker
  rig.style.setProperty('--glare', Math.max(0, (a - 95) / 40).toFixed(2)); // obtuse: catches the ceiling light
  const chip = rig.querySelector('.fx-angle');
  if (chip) chip.textContent = `${Math.round(a)}°`;
  const hint = rig.querySelector('.fx-hint');
  if (hint) hint.textContent = `${Math.round(a)}° · 外屏模式`;
}

/* drag the top edge: 1:1, no transition while dragging; zones re-render when crossed */
let drag = null;
rig.addEventListener('pointerdown', (e) => {
  if (!e.target.closest('[data-grab]')) return;
  drag = { y: e.clientY, a: flexState.angle, zone: flexZone() };
  rig.classList.add('dragging');
  e.target.setPointerCapture(e.pointerId);
});
rig.addEventListener('pointermove', (e) => {
  if (!drag) return;
  flexState.angle = Math.min(130, Math.max(60, drag.a - (e.clientY - drag.y) * 0.25)); // pull toward you = smaller angle
  if (flexZone() !== drag.zone) { drag.zone = flexZone(); renderFlex(); } else applyAngle();
});
rig.addEventListener('pointerup', () => {
  if (!drag) return;
  drag = null;
  rig.classList.remove('dragging');
  if (flexState.angle > ANGLE.max) exitFlex('open');            // past 115°: full view
  else if (flexState.angle < ANGLE.min) exitFlex('closed');     // below 75°: closed
});

rig.addEventListener('click', (e) => {
  const b = e.target.closest('[data-fx],[data-fx-thread],[data-fx-quick],[data-fx-open]');
  if (!b) return;
  const fx = b.dataset.fx;
  if (fx === 'exit') exitFlex('open');
  else if (fx === 'play') { flexState.playing = !flexState.playing; renderFlex(); }
  else if (fx === 'shot') banner('截图', '已保存到相册（示范）', 'camera');
  else if (fx === 'transfer') { exitFlex('open'); if (state.app !== 'wallet') openApp('wallet'); setTimeout(openSheet, 500); }
  else if (b.dataset.fxThread) { state.msg.selected = Number(b.dataset.fxThread); selectThread(state.msg.selected).then(renderFlex); renderFlex(); }
  else if (b.dataset.fxQuick) sendFlex(b.dataset.fxQuick);
  else if (b.dataset.fxOpen) { if (state.app) closeApp(); setTimeout(() => { openApp(b.dataset.fxOpen); setTimeout(renderFlex, 400); }, 50); }
});
rig.addEventListener('submit', (e) => {
  const f = e.target.closest('[data-fx-form]');
  if (!f) return;
  e.preventDefault();
  const input = f.querySelector('input');
  if (input.value.trim()) sendFlex(input.value);
  input.value = '';
});
async function sendFlex(text) {
  const id = state.msg.selected ?? state.msg.threads?.[0]?.id;
  if (id == null) return;
  state.msg.selected = id;
  state.msg.drafts[id] = text;
  await sendMessage(id);
  renderFlex();
}

document.addEventListener('click', (e) => { if (e.target.closest('[data-cc="flex"]')) flexState.on ? exitFlex('open') : enterFlex(100); });
window.addEventListener('keydown', (e) => {
  if (!flexState.on || !state.open) return;
  if (e.key === 'ArrowUp' && !typing()) { flexState.angle = Math.min(ANGLE.max, flexState.angle + 5); renderFlex(); }
  if (e.key === 'ArrowDown' && !typing()) { flexState.angle = Math.max(ANGLE.min, flexState.angle - 5); renderFlex(); }
});

/* preview: ?flex=100 */
if (!IN_GAME && params.get('flex')) setTimeout(() => enterFlex(Number(params.get('flex')) || 100), 900);
