// The lesson loop shared by the 2D and 3D views: hook → predict (locks) → test → prove (flap) → stamp,
// then "explore more" (extra controls) and a short quiz. One state object drives every view, readout,
// bar and the canvas description, all updated in the same animation frame.
import { createStepper, fmt } from './physics.js';

const $ = (sel, root = document) => root.querySelector(sel);
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') n.className = v;
    else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? '' : v);
  }
  for (const kid of kids.flat(Infinity)) if (kid != null && kid !== false) n.append(kid.nodeType ? kid : String(kid));
  return n;
};

export function createLesson({ lessons, ui, makeView, lang: startLang = 'zh' }) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const st = {
    lang: startLang, index: 0, lesson: null, params: {}, sim: null, stepper: null,
    choice: null, sure: null, locked: false, ran: false, finished: false, flapOpen: false,
    stamped: new Set(), series: [], running: false, view: null, lastTime: 0, announceAt: 0
  };
  const T = (o) => (o == null ? '' : typeof o === 'string' ? o : o[st.lang] ?? o.en ?? Object.values(o)[0]);

  // ---------------------------------------------------------------- frame loop (only while running)
  let raf = 0;
  function frame(now) {
    raf = 0;
    if (!st.running || document.hidden) return;
    const dtFrame = st.lastTime ? (now - st.lastTime) / 1000 : 0;
    st.lastTime = now;
    advance(dtFrame);
    if (st.running) raf = requestAnimationFrame(frame);
  }
  function start() { if (!raf) { st.lastTime = 0; raf = requestAnimationFrame(frame); } }
  document.addEventListener('visibilitychange', () => { if (!document.hidden && st.running) start(); });

  /** Step the experiment by real seconds (also used by the ?debug hook), then redraw everything once. */
  function advance(seconds) {
    if (!st.sim) return;
    st.stepper.advance(seconds);
    const L = st.lesson;
    st.series.push(L.sample(st.sim));
    if (st.series.length > 2000) st.series.splice(0, st.series.length - 2000);
    if (L.done(st.sim, st.params)) finish();
    render();
  }

  function finish() {
    st.running = false;
    if (!st.ran) { st.ran = true; st.finished = true; }
    ui.run.textContent = T(ui.text.again);
    ui.flapBtn.disabled = !st.locked;
    announce(T(st.lesson.result(st.sim, st.params, st.lang)));
    render();
  }

  // ---------------------------------------------------------------- one render for every representation
  function render() {
    const L = st.lesson, sim = st.sim;
    if (!sim) return;
    const energy = sim.energy();
    const frameData = L.frame(sim, st.params);
    // glow follows what the readout shows: a store that rounds to 0.00 J does not glow
    const shown = (j) => (Math.abs(j) < 0.005 ? 0 : j);
    const share = (j) => (energy.total > 0 ? shown(j) / energy.total : 0);
    frameData.glow = { kinetic: share(energy.kinetic), potential: share(energy.potential), lost: share(energy.lost) };
    st.view.draw(frameData, L);
    // readouts
    ui.readouts.replaceChildren(...L.readouts(sim, st.params).map(([label, value]) =>
      el('div', { class: 'readout' }, el('span', {}, T(label)), el('output', {}, value))));
    // energy bars (stores have a colour AND a pattern AND a text label)
    const stores = L.stores || ['kinetic', 'potential', 'lost'];
    ui.bars.replaceChildren(...stores.map((k) => {
      const pct = energy.total > 0 ? Math.max(0, shown(energy[k])) / energy.total * 100 : 0;
      return el('div', { class: 'bar bar-' + k },
        el('span', { class: 'bar-label' }, T(ui.text.store[k])),
        el('span', { class: 'bar-track' }, el('span', { class: 'bar-fill', style: `width:${pct.toFixed(1)}%` })),
        el('output', {}, fmt(shown(energy[k]), 'J')));
    }), el('div', { class: 'bar-total' }, T(ui.text.total), ' ', el('output', {}, fmt(energy.total, 'J'))));
    drawGraph();
    const desc = T(L.describe(sim, st.params, st.lang));
    ui.canvasHost.setAttribute('aria-label', desc);
    const now = performance.now();
    if (!st.running || now - st.announceAt > 2500) { ui.desc.textContent = desc; st.announceAt = now; }
  }

  function drawGraph() {
    const c = ui.graph, g = c.getContext('2d');
    const w = c.width = c.clientWidth * devicePixelRatio, h = c.height = c.clientHeight * devicePixelRatio;
    g.clearRect(0, 0, w, h);
    const L = st.lesson, data = st.series;
    if (!data.length || !L.graph) return;
    const tMax = Math.max(L.graph.tMax(st.params), data[data.length - 1][0]);
    const yMax = L.graph.yMax(st.params), yMin = L.graph.yMin ? L.graph.yMin(st.params) : 0;
    g.strokeStyle = '#222'; g.lineWidth = devicePixelRatio;
    const Yp = (v) => h - ((v - yMin) / (yMax - yMin)) * (h - 4) - 2;
    g.beginPath(); g.moveTo(1, 0); g.lineTo(1, h - 1); g.lineTo(w, h - 1); g.stroke();
    if (yMin < 0) { g.setLineDash([4, 4]); g.beginPath(); g.moveTo(0, Yp(0)); g.lineTo(w, Yp(0)); g.stroke(); g.setLineDash([]); }
    g.lineWidth = 2 * devicePixelRatio; g.strokeStyle = '#d2551e';
    g.beginPath();
    data.forEach(([t, v], i) => { const x = (t / tMax) * w, y = Yp(v); i ? g.lineTo(x, y) : g.moveTo(x, y); });
    g.stroke();
    ui.graphLabel.textContent = T(L.graph.label);
  }

  // ---------------------------------------------------------------- live region (polite, never steals focus)
  function announce(text) { ui.live.textContent = ''; requestAnimationFrame(() => { ui.live.textContent = text; }); }

  // ---------------------------------------------------------------- building a lesson page
  function load(i) {
    st.index = i; st.lesson = lessons[i];
    st.choice = null; st.sure = null; st.locked = false; st.ran = false; st.finished = false; st.flapOpen = false;
    st.params = Object.fromEntries(st.lesson.controls.concat(st.lesson.more || []).map((c) => [c.id, c.value]));
    st.view.setLesson(st.lesson, { animate: !reduce.matches });
    buildText();
    reset();
  }

  function reset() {
    st.running = false;
    st.sim = st.lesson.make(st.params);
    st.stepper = createStepper(st.sim.step, { dt: 1 / 240 });
    st.stepper.speed = st.lesson.speed || 1;
    st.series = [st.lesson.sample(st.sim)];
    ui.run.textContent = T(ui.text.run);
    render();
  }

  function slider(c, extra) {
    const id = 'ctl-' + c.id;
    const valueText = (v) => `${Number(v).toFixed(c.decimals ?? 1)} ${T(c.unitName ?? c.unit ?? '')}`.trim();
    const input = el('input', { type: 'range', id, min: c.min, max: c.max, step: c.step, value: st.params[c.id],
      'aria-valuetext': valueText(st.params[c.id]) });
    const out = el('output', { for: id }, fmt(Number(st.params[c.id]), c.unit, c.decimals ?? 1));
    input.addEventListener('input', () => {
      st.params[c.id] = Number(input.value);
      input.setAttribute('aria-valuetext', valueText(input.value));
      out.textContent = fmt(st.params[c.id], c.unit, c.decimals ?? 1);
      reset();
    });
    return el('div', { class: 'control' + (extra ? ' more' : '') }, el('label', { for: id }, T(c.label)), input, out);
  }

  function buildText() {
    const L = st.lesson;
    document.documentElement.lang = st.lang === 'zh' ? 'zh-Hans' : 'en';
    ui.tabs.querySelectorAll('button').forEach((b, i) => {
      b.setAttribute('aria-selected', String(i === st.index));
      b.textContent = (st.stamped.has(lessons[i].id) ? '★ ' : '') + T(lessons[i].title);
    });
    ui.title.textContent = T(L.title);
    ui.hook.textContent = T(L.hook);
    ui.question.textContent = T(L.predict.question);
    ui.options.replaceChildren(...L.predict.options.map((o) => el('label', { class: 'option' },
      el('input', { type: 'radio', name: 'predict', value: o.id, checked: st.choice === o.id, disabled: st.locked,
        onchange: () => { st.choice = o.id; ui.lock.disabled = false; } }),
      el('span', {}, T(o.text)))));
    ui.sureRow.replaceChildren(el('span', {}, T(ui.text.sureQ)), ...['sure', 'unsure'].map((k) => el('label', {},
      el('input', { type: 'radio', name: 'sure', value: k, checked: st.sure === k, disabled: st.locked, onchange: () => { st.sure = k; } }),
      T(ui.text[k]))));
    ui.lock.disabled = !st.choice || st.locked;
    ui.lock.textContent = T(st.locked ? ui.text.locked : ui.text.lock);
    ui.controls.replaceChildren(...L.controls.map((c) => slider(c)));
    ui.more.replaceChildren(...(L.more || []).map((c) => slider(c, true)));
    ui.moreBox.hidden = !st.stamped.has(L.id) || !(L.more || []).length;
    ui.moreIntro.textContent = T(L.moreIntro || '');
    ui.run.disabled = !st.locked;
    ui.skip.disabled = !st.locked;
    ui.flapBtn.disabled = !(st.locked && st.ran);
    ui.flapBtn.setAttribute('aria-expanded', String(st.flapOpen));
    ui.flapBtn.textContent = T(ui.text.flap);
    ui.flap.hidden = !st.flapOpen;
    ui.ignores.textContent = T(L.ignores);
    ui.speedNote.textContent = (L.speed || 1) < 1 ? T(ui.text.slow).replace('{x}', String(L.speed)) : '';
    ui.quizBox.hidden = !st.stamped.has(L.id);
    buildQuiz();
    ui.teacher.replaceChildren(...L.teacher(st.lang));
  }

  function buildQuiz() {
    const L = st.lesson;
    ui.quiz.replaceChildren(...L.quiz.map((q, qi) => {
      const fb = el('p', { class: 'quiz-feedback', 'aria-live': 'polite' });
      return el('fieldset', { class: 'quiz-item' }, el('legend', {}, `${qi + 1}. ${T(q.q)}`),
        ...q.options.map((o, oi) => el('label', { class: 'option' },
          el('input', { type: 'radio', name: `quiz-${L.id}-${qi}`, onchange: () => {
            fb.textContent = (oi === q.answer ? '✓ ' : '↺ ') + T(q.why[oi]);
          } }), el('span', {}, T(o)))), fb);
    }));
  }

  function openFlap() {
    if (!st.locked || !st.ran) return;
    st.flapOpen = !st.flapOpen;
    ui.flapBtn.setAttribute('aria-expanded', String(st.flapOpen));
    ui.flap.hidden = !st.flapOpen;
    if (!st.flapOpen) return;
    const L = st.lesson;
    const correct = st.choice === L.predict.correct;
    const picked = L.predict.options.find((o) => o.id === st.choice);
    ui.explain.replaceChildren(
      el('p', { class: 'verdict' }, T(correct ? ui.text.right : ui.text.surprised)),
      ...(correct ? [] : [el('p', {}, T(picked.why))]),
      ...L.explain(st.sim, st.params, st.lang).map((p) => el('p', {}, p)));
    awardStamp(correct);
  }

  /** The stamp is for finishing the loop (predict + test + flap), right or wrong; a right guess adds a small mark. */
  function awardStamp(correct) {
    const L = st.lesson;
    st.stamped.add(L.id);
    ui.stamp.hidden = false;
    ui.stamp.classList.toggle('animate', !reduce.matches);
    ui.stampText.textContent = T(L.stamp);
    ui.stampMark.hidden = !correct;
    ui.stampMark.textContent = T(ui.text.predictedRight);
    announce(T(ui.text.stamped) + ' ' + T(L.stamp));
    ui.moreBox.hidden = !(L.more || []).length;
    ui.quizBox.hidden = false;
    ui.tabs.querySelectorAll('button')[st.index].textContent = '★ ' + T(L.title);
  }

  // ---------------------------------------------------------------- wiring
  ui.lock.addEventListener('click', () => {
    if (!st.choice) return;
    st.locked = true;
    buildText();
    announce(T(ui.text.lockedNow));
    ui.run.focus();
  });
  ui.run.addEventListener('click', () => {
    if (!st.locked) return;
    if (st.finished || st.running) reset();
    st.running = true; st.finished = false;
    ui.run.textContent = T(ui.text.running);
    start();
  });
  ui.skip.addEventListener('click', () => {         // jump to the result: for reduced motion, or the impatient
    if (!st.locked) return;
    if (st.finished) reset();
    st.running = false;
    for (let i = 0; i < 4000 && !st.lesson.done(st.sim, st.params); i++) st.stepper.advance(0.05), st.series.push(st.lesson.sample(st.sim));
    finish();
  });
  ui.resetBtn.addEventListener('click', reset);
  ui.flapBtn.addEventListener('click', openFlap);
  ui.stampClose?.addEventListener('click', () => { ui.stamp.hidden = true; });
  ui.tabs.replaceChildren(...lessons.map((L, i) => el('button', { role: 'tab', type: 'button', onclick: () => { ui.stamp.hidden = true; load(i); } }, '')));
  ui.langBtns.forEach((b) => b.addEventListener('click', () => {
    st.lang = b.dataset.lang;
    ui.langBtns.forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    applyStatic(); buildText(); render();
  }));

  function applyStatic() {
    document.querySelectorAll('[data-t]').forEach((n) => { n.textContent = T(ui.text[n.dataset.t]); });
  }

  return {
    async init() {
      st.view = await makeView(ui.canvasHost);
      applyStatic();
      load(0);
      if (new URLSearchParams(location.search).has('debug')) {
        // test hook, only with ?debug: step the simulation without relying on requestAnimationFrame
        window.__lesson = { st, advance, finish, load, choose: (id) => { st.choice = id; }, lock: () => ui.lock.click() };
      }
    },
    switchView: async (makeNew) => {
      st.view.destroy();
      st.view = await makeNew(ui.canvasHost);
      st.view.setLesson(st.lesson, { animate: false });
      render();
    },
    get state() { return st; }
  };
}
