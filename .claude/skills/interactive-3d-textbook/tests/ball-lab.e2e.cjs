// Usage: node tests/ball-lab.e2e.cjs <dir with node_modules/three and node_modules/postprocessing> <screenshot dir>
// Serves assets/ball-lab on :8781, routes the CDN import map to the local packages (no network needed),
// and walks every lesson in 2D and 3D. Needs Playwright + Chromium.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');

const [mods, shots] = process.argv.slice(2);
const root = path.join(__dirname, '..', 'assets', 'ball-lab');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' };
const server = http.createServer((req, res) => {
  const file = path.join(root, decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!file.startsWith(root) || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
}).listen(8781);

const results = [];
const ok = (n, c, d = '') => results.push([c ? 'PASS' : 'FAIL', n, c ? '' : String(d).slice(0, 300)]);

async function cdn(page) {
  await page.route('https://cdn.jsdelivr.net/npm/**', (route) => {
    const u = new URL(route.request().url()).pathname;           // /npm/three@0.170.0/build/three.module.js
    const m = u.match(/^\/npm\/(three|postprocessing)@[^/]+\/(.*)$/);
    if (!m) return route.abort();
    route.fulfill({ path: path.join(mods, 'node_modules', m[1], m[2]), contentType: 'text/javascript' });
  });
}

async function loop(page, lesson, choice, label, reload = true) {
  if (reload) await page.click(`#tabs button:nth-child(${lesson + 1})`);   // opening a tab starts the lesson fresh
  await page.check(`input[name=predict][value=${choice}]`);
  ok(`${label}: run is disabled before locking`, await page.isDisabled('#run'));
  await page.click('#lock');
  ok(`${label}: prediction locks`, await page.isDisabled(`input[name=predict][value=${choice}]`));
  await page.click('#skip');
  await page.waitForFunction(() => !document.querySelector('#flapBtn').disabled);
  await page.click('#flapBtn');
  const stamp = await page.isVisible('#stamp');
  const explain = await page.textContent('#explain');
  return { stamp, explain };
}

(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message + ' @ ' + (e.stack || '').split('\n').slice(0, 3).join(' / ')));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  await cdn(page);
  await page.goto('http://localhost:8781/lesson.html?debug');
  await page.waitForSelector('#options input');

  // ---------------------------------------------------------------- 2D: every lesson, wrong then right
  const lessons = [['bounce', 'a', 'c'], ['launch', 'b', 'c'], ['collision', 'a', 'c'], ['pendulum', 'a', 'c']];
  for (const [i, [id, wrong, right]] of lessons.entries()) {
    const w = await loop(page, i, wrong, `${id} wrong`);
    ok(`${id}: stamp for a WRONG prediction too`, w.stamp);
    ok(`${id}: wrong prediction explains that misconception`, (await page.textContent('#explain')).includes('意外吗'), w.explain);
    ok(`${id}: no "predicted right" mark when wrong`, await page.isHidden('#stampMark'));
    await page.screenshot({ path: `${shots}/2d-${id}.png`, fullPage: true });
    await page.click(`#tabs button:nth-child(${i + 1})`);   // reload the lesson for a second pass
    const r = await loop(page, i, right, `${id} right`);
    ok(`${id}: stamp + "predicted right" mark when right`, r.stamp && await page.isVisible('#stampMark'));
    ok(`${id}: quiz and "explore more" unlock after the stamp`, await page.isVisible('#quizBox') && await page.isVisible('#moreBox'));
  }
  // numbers in the explanation are the student's own run
  await page.click('#tabs button:nth-child(1)');
  const setRange = (sel, v) => page.$eval(sel, (n, v) => { n.value = v; n.dispatchEvent(new Event('input', { bubbles: true })); }, v);
  await setRange('#ctl-h0', '2.0'); await setRange('#ctl-e', '0.8');
  const own = await loop(page, 0, 'c', 'bounce own numbers', false);
  ok('flap reuses the student\'s numbers (2.00 m, 1.28 m, e² = 0.64)', own.explain.includes('2.00 m') && own.explain.includes('1.28 m') && own.explain.includes('0.64'), own.explain);
  // energy bars add up to the total
  await page.click('details.rep summary');
  const sums = await page.$$eval('.bar output', (os) => os.map((o) => parseFloat(o.textContent)));
  const total = await page.$eval('.bar-total output', (o) => parseFloat(o.textContent));
  ok('energy bars add up to the total', Math.abs(sums.reduce((a, b) => a + b, 0) - total) <= 0.011, [sums, total]);
  ok('slider has aria-valuetext with unit', (await page.getAttribute('#ctl-h0', 'aria-valuetext')).includes('米'));
  ok('canvas host has a live text alternative', (await page.getAttribute('#canvasHost', 'aria-label')).includes('弹跳球'));
  // English
  await page.click('.lang[data-lang=en]');
  ok('English text', (await page.textContent('#title')) === 'Bouncing ball' && (await page.textContent('#run')).length > 0);
  await page.click('.lang[data-lang=zh]');
  // keyboard: prediction radios and lock reachable
  await page.click('#tabs button:nth-child(4)');
  await page.focus('input[name=predict][value=a]'); await page.keyboard.press('ArrowDown');
  ok('keyboard moves between prediction options', await page.isChecked('input[name=predict][value=b]'));
  // slow motion is labelled
  await page.click('#tabs button:nth-child(2)');
  ok('slow motion labelled on screen', (await page.textContent('#speedNote')).includes('0.5'));
  // live run (not skip) reaches the end through requestAnimationFrame
  await page.check('input[name=predict][value=c]'); await page.click('#lock'); await page.click('#run');
  await page.waitForFunction(() => !document.querySelector('#flapBtn').disabled, null, { timeout: 15000 });
  ok('a real-time run finishes on its own', true);

  // ---------------------------------------------------------------- 3D
  await page.click('#tabs button:nth-child(1)');
  await page.click('#view3d');
  await page.waitForSelector('#canvasHost canvas.diagram-3d', { timeout: 15000 });
  ok('3D view loads (no fallback note)', (await page.textContent('#viewNote')) === '', await page.textContent('#viewNote'));
  await page.waitForTimeout(1200);                       // pop-up rise finishes
  const box = await page.$eval('#canvasHost', (n) => { const r = n.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; });
  await page.screenshot({ path: `${shots}/3d-start.png`, clip: box });
  const px = async (fx, fy) => {
    const buf = await page.screenshot({ clip: { x: box.x + box.width * fx, y: box.y + box.height * fy, width: 1, height: 1 } });
    return await page.evaluate(async (b64) => {
      const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
      const c = document.createElement('canvas'); c.width = c.height = 1; const g = c.getContext('2d'); g.drawImage(img, 0, 0);
      return [...g.getImageData(0, 0, 1, 1).data.slice(0, 3)];
    }, buf.toString('base64'));
  };
  const paper = await px(0.8, 0.8);                      // a blank part of the right-hand page
  const target = [0xfb, 0xf8, 0xf1];
  ok('blank paper is white (within 3 % of #fbf8f1)', paper.every((v, i) => Math.abs(v - target[i]) <= 8), paper);
  const st = await page.evaluate(() => { const s = window.__lesson.st; const e = s.sim.energy(); return { ke: e.kinetic, pe: e.potential }; });
  ok('at the start all energy is potential, none kinetic', st.ke === 0 && st.pe > 0, JSON.stringify(st));
  const glowBall0 = await page.evaluate(() => window.__lesson.st.view.renderer.info && true);
  ok('3D renderer exposed for checks', glowBall0);
  const frames = () => page.evaluate(() => window.__lesson.st.view.renderer.info.render.frame);
  const f1 = await frames(); await page.waitForTimeout(1500); const f2 = await frames();
  ok('idle: no frames rendered while nothing moves', f2 === f1, [f1, f2]);
  await page.check('input[name=predict][value=c]'); await page.click('#lock');
  await page.evaluate(() => { window.__lesson.st.running = false; window.__lesson.advance(0.55); });   // mid-fall, fast
  await page.waitForTimeout(200);
  await page.screenshot({ path: `${shots}/3d-falling.png`, clip: box });
  const f3 = await frames();
  ok('a state change renders exactly on demand', f3 > f2, [f2, f3]);
  await page.evaluate(() => { for (let i = 0; i < 400; i++) window.__lesson.advance(0.05); });
  await page.waitForTimeout(200);
  await page.screenshot({ path: `${shots}/3d-rest.png`, clip: box });
  const heat = await page.evaluate(() => window.__lesson.st.sim.energy());
  ok('at rest the energy is all in thermal + sound', Math.abs(heat.lost - heat.total) < 1e-9, JSON.stringify(heat));
  await page.click('#angle');
  await page.waitForTimeout(200);
  await page.screenshot({ path: `${shots}/3d-angle.png`, clip: box });
  for (const i of [2, 3, 4]) {
    await page.click(`#tabs button:nth-child(${i})`);
    await page.waitForTimeout(900);
    await page.evaluate(() => { window.__lesson.choose('c'); window.__lesson.lock(); for (let k = 0; k < 30; k++) window.__lesson.advance(0.05); });
    await page.waitForTimeout(200);
    await page.screenshot({ path: `${shots}/3d-lesson${i}.png`, clip: box });
  }
  await page.click('#view2d');
  ok('back to 2D', await page.isVisible('#canvasHost svg'));

  // ---------------------------------------------------------------- phone width, reduced motion, no WebGL fallback
  const phone = await browser.newPage({ viewport: { width: 375, height: 812 }, reducedMotion: 'reduce' });
  await cdn(phone);
  await phone.goto('http://localhost:8781/lesson.html');
  await phone.waitForSelector('#options input');
  ok('no horizontal scroll at 375 px', await phone.evaluate(() => document.documentElement.scrollWidth <= 375), await phone.evaluate(() => document.documentElement.scrollWidth));
  const small = await phone.evaluate(() => [...document.querySelectorAll('button:not([disabled])')].filter((b) => b.offsetParent && (b.offsetHeight < 44 || b.offsetWidth < 44)).map((b) => b.textContent.trim()));
  ok('buttons at least 44 px on a phone', small.length === 0, JSON.stringify(small));
  ok('reduced motion: no rise animation class', !(await phone.$eval('#canvasHost svg', (n) => n.classList.contains('rise'))));
  await phone.screenshot({ path: `${shots}/phone.png`, fullPage: true });
  const nogl = await browser.newPage();
  await nogl.addInitScript(() => { const orig = HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext = function (t, ...a) { return /webgl/.test(t) ? null : orig.call(this, t, ...a); }; });
  await cdn(nogl);
  await nogl.goto('http://localhost:8781/lesson.html?view=3d');
  await nogl.waitForFunction(() => document.querySelector('#viewNote').textContent.length > 0, null, { timeout: 15000 });
  ok('no WebGL: falls back to 2D with a note', await nogl.isVisible('#canvasHost svg'));

  ok('no console errors', errors.length === 0, errors.join(' | '));
  for (const r of results) console.log(r.join('  '));
  console.log(results.filter((r) => r[0] === 'FAIL').length + ' failed of ' + results.length);
  await browser.close(); server.close();
  process.exit(results.some((r) => r[0] === 'FAIL') ? 1 : 0);
})().catch((e) => { console.error(e); for (const r of results) console.log(r.join('  ')); server.close(); process.exit(1); });
