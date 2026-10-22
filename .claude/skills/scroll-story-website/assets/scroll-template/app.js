/* Scroll-story template: canvas frame sequence scrubbed by scroll, colour picker, booking drawer.
   No dependencies. Config: window.SITE_CONFIG in index.html. */
(() => {
  'use strict';
  const CFG = Object.assign({ frames: { path: 'frames/f_', ext: '.webp', count: 0, pad: 4 },
    endpoint: '', headers: {}, whatsapp: '', stillAt: 0.5 }, window.SITE_CONFIG || {});
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a)); return t * t * (3 - 2 * t); };
  const motionQuery = matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------- Scroll story ---------- */
  const story = $('#story'), canvas = $('#story-canvas'), ctx = canvas.getContext('2d');
  const bar = $('.progress span'), caps = $$('.cap[data-at]');
  const N = CFG.frames.count > 0 ? CFG.frames.count : 120;   // placeholder uses 120 virtual frames
  let useImages = CFG.frames.count > 0;
  const imgs = new Array(N);
  let paint = '#c8102e', tint = 70, want = 0, drawn = -1, queued = false, W = 0, H = 0;

  const frameUrl = (i) => CFG.frames.path + String(i + 1).padStart(CFG.frames.pad, '0') + CFG.frames.ext;
  function load(i) {
    if (imgs[i]) return;
    const im = new Image();
    im.decoding = 'async';
    im.onload = () => { if (Math.abs(i - want) < 8) request(true); };
    im.onerror = () => { if (i === 0) { useImages = false; request(true); } };  // no frames folder: fall back
    im.src = frameUrl(i);
    imgs[i] = im;
  }
  function preload() {          // first frame, then coarse-to-fine so early scrolling still has pictures
    if (!useImages) return;
    if (motionQuery.matches) { load(Math.round(CFG.stillAt * (N - 1))); return; }  // still image only
    load(0);
    for (const step of [12, 4, 1]) for (let i = 0; i < N; i += step) load(i);
  }
  function nearestLoaded(i) {
    for (let d = 0; d < N; d++) {
      for (const j of [i - d, i + d]) { const im = imgs[j]; if (im && im.complete && im.naturalWidth) return im; }
    }
    return null;
  }

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);   // cap: huge canvases crash mobile Safari
    W = Math.round(canvas.clientWidth * dpr); H = Math.round(canvas.clientHeight * dpr);
    if (canvas.width !== W || canvas.height !== H) { canvas.width = W; canvas.height = H; }
    request(true);
  }

  function progress() {
    if (motionQuery.matches) return CFG.stillAt;
    const r = story.getBoundingClientRect();
    return clamp(-r.top / Math.max(1, story.offsetHeight - innerHeight));
  }
  function request(force) {
    if (force) drawn = -1;
    if (!queued) { queued = true; requestAnimationFrame(frame); }
  }
  function frame() {                       // only rAF draws; scroll just asks for a frame
    queued = false;
    const p = progress();
    want = Math.round(p * (N - 1));
    if (bar) bar.style.setProperty('--p', p.toFixed(3));
    for (const c of caps) {
      const [a, b] = c.dataset.at.split('-').map(Number);
      c.classList.toggle('is-on', motionQuery.matches || (p >= a && p <= b));
    }
    if (want === drawn) return;
    const im = useImages && nearestLoaded(want);
    if (im) drawCover(im); else drawPlaceholder(want / (N - 1));
    drawn = want;
  }
  function drawCover(im) {
    const s = Math.max(W / im.naturalWidth, H / im.naturalHeight);
    const w = im.naturalWidth * s, h = im.naturalHeight * s;
    ctx.drawImage(im, (W - w) / 2, (H - h) / 2, w, h);
  }

  /* Placeholder "film": dusty car -> clean -> camera pushes to badge -> light sweep. Replace with real frames. */
  const BODY = new Path2D('M40 190 Q40 150 90 142 L170 132 Q215 82 280 76 L380 76 Q430 80 470 128 L540 140 Q570 148 570 182 L570 200 L40 200 Z');
  const GLASS = new Path2D('M190 132 Q228 92 282 88 L322 88 L322 132 Z M334 88 L378 88 Q420 92 452 132 L334 132 Z');
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const DIRT = Array.from({ length: 70 }, () => [40 + rnd() * 530, 80 + rnd() * 125, 6 + rnd() * 26, 0.25 + rnd() * 0.5]);
  const BADGE = [552, 166];

  function drawPlaceholder(p) {
    const bg = ctx.createRadialGradient(W / 2, H * 0.55, 0, W / 2, H * 0.55, Math.max(W, H) * 0.7);
    bg.addColorStop(0, '#2a2c33'); bg.addColorStop(1, '#0c0d10');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);
    const zoom = smooth(0.5, 0.8, p);                       // camera push-in to the badge
    const base = Math.min(W / 680, H / 380);
    const s = base * (1 + zoom * 3.2);
    const fx = 305 + (BADGE[0] - 305) * zoom, fy = 150 + (BADGE[1] - 150) * zoom;
    ctx.save();
    ctx.translate(W / 2, H * 0.5); ctx.scale(s, s); ctx.translate(-fx, -fy);
    ctx.fillStyle = 'rgba(0,0,0,.4)';
    ctx.beginPath(); ctx.ellipse(305, 232, 260, 14, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = paint; ctx.fill(BODY);
    ctx.save(); ctx.clip(BODY);
    const dirt = 1 - smooth(0.18, 0.48, p);                 // wash
    for (const [x, y, r, a] of DIRT) {
      ctx.fillStyle = `rgba(110,92,64,${a * dirt})`;
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
    }
    const gloss = ctx.createLinearGradient(0, 80, 0, 200);
    gloss.addColorStop(0, `rgba(255,255,255,${0.28 * (1 - dirt)})`); gloss.addColorStop(0.5, 'rgba(255,255,255,0)');
    ctx.fillStyle = gloss; ctx.fillRect(0, 60, 620, 150);
    const sweep = smooth(0.8, 1, p);                        // light sweep across the paint
    if (sweep > 0 && sweep < 1) {
      const x = -150 + sweep * 900;
      const g = ctx.createLinearGradient(x - 90, 0, x + 90, 0);
      g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,255,255,.55)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = g; ctx.fillRect(x - 90, 60, 180, 150);
    }
    ctx.restore();
    ctx.fillStyle = `rgba(14,17,22,${0.35 + (1 - tint / 100) * 0.6})`;  // darker film = less light
    ctx.fill(GLASS);
    ctx.fillStyle = '#111';
    for (const cx of [150, 460]) { ctx.beginPath(); ctx.arc(cx, 200, 36, 0, Math.PI * 2); ctx.fill(); }
    ctx.fillStyle = '#8b8f98';
    for (const cx of [150, 460]) { ctx.beginPath(); ctx.arc(cx, 200, 14, 0, Math.PI * 2); ctx.fill(); }
    ctx.fillStyle = '#e8c26a';
    ctx.beginPath(); ctx.arc(BADGE[0], BADGE[1], 6, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  addEventListener('scroll', () => request(false), { passive: true });   // passive: never blocks scrolling
  addEventListener('resize', resize);
  motionQuery.addEventListener('change', resize);
  preload(); resize();

  /* ---------- Colour + film picker ---------- */
  const car = $('.car'), choice = $('.choice');
  function updatePick() {
    const pr = $('input[name=paint]:checked'), tr = $('input[name=tint]:checked');
    paint = pr.value; tint = Number(tr.value);
    car.style.setProperty('--paint', paint);
    car.style.setProperty('--glass-alpha', (tint / 100 * 0.6).toFixed(2));
    choice.textContent = `${pr.dataset.name} · ${tint}% film`;
    request(true);
  }
  $$('input[name=paint], input[name=tint]').forEach((r) => r.addEventListener('change', updatePick));
  updatePick();

  /* ---------- Booking drawer ---------- */
  const dlg = $('#booking'), form = $('#booking-form'), done = $('.done', dlg), status = $('.form-status', dlg);
  let opener = null, openedAt = 0;
  const today = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  form.date.min = today;
  $$('[data-open-booking]').forEach((b) => b.addEventListener('click', () => {
    opener = b; openedAt = Date.now();
    form.hidden = false; done.hidden = true; status.textContent = '';
    dlg.showModal();                     // native modal: focus trap, Esc to close, page behind is inert
  }));
  $$('[data-close]', dlg).forEach((b) => b.addEventListener('click', () => dlg.close()));
  dlg.addEventListener('click', (e) => {   // click on the backdrop (outside the drawer box) closes it
    const r = dlg.getBoundingClientRect();
    if (e.target === dlg && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) dlg.close();
  });
  dlg.addEventListener('close', () => opener && opener.focus());

  const messages = {
    name: 'Please enter your name.', phone: 'Enter a mobile number, digits only (8–16).',
    vehicle: 'Tell us the car make and model.', service: 'Choose a service.',
    date: 'Pick a date from today on.', consent: 'Please agree so we can contact you.'
  };
  function check(el) {
    let ok = el.checkValidity();
    if (ok && el.name === 'phone') ok = (el.value.match(/\d/g) || []).length >= 8;
    el.setAttribute('aria-invalid', String(!ok));
    $('#e-' + el.name).textContent = ok ? '' : messages[el.name];
    return ok;
  }
  const fields = Object.keys(messages).map((n) => form.elements[n]);
  fields.forEach((el) => el.addEventListener('blur', () => el.value && check(el)));

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const bad = fields.filter((el) => !check(el));
    if (bad.length) { status.textContent = `Please fix ${bad.length} field${bad.length > 1 ? 's' : ''}.`; bad[0].focus(); return; }
    const data = Object.fromEntries(new FormData(form));
    const isBot = data.company || Date.now() - openedAt < 3000;          // honeypot + too-fast
    delete data.company;
    Object.assign(data, { consent: true, paint: $('input[name=paint]:checked').dataset.name, tint: tint + '%',
      source: location.pathname });
    const btn = form.querySelector('[type=submit]');
    btn.disabled = true; status.textContent = 'Sending…';
    try {
      if (!isBot && CFG.endpoint) {
        const res = await fetch(CFG.endpoint, { method: 'POST',
          headers: Object.assign({ 'Content-Type': 'application/json' }, CFG.headers), body: JSON.stringify(data) });
        if (!res.ok) throw new Error('HTTP ' + res.status);
      } else {
        await new Promise((r) => setTimeout(r, 500));   // local demo: nothing leaves the browser
      }
      form.reset(); updatePick();
      form.hidden = true; done.hidden = false;
      const wa = $('.wa', done);
      if (CFG.whatsapp) {
        wa.href = `https://wa.me/${CFG.whatsapp}?text=` + encodeURIComponent(`Hi, I just booked ${data.service} for ${data.date}.`);
        wa.hidden = false;
      }
      $('h2', done).focus();
    } catch (err) {
      status.textContent = 'Could not send. Please try again, or call us.';
    } finally {
      btn.disabled = false;
    }
  });
})();
