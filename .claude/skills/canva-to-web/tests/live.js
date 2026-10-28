// Usage: mock.py on :8766, a copy of order-site with config.js pointing at it served on :8767, then
//   node live.js <postgres socket dir> <screenshot dir>
// Live mode (Supabase branch of backend.js) against the PostgREST-like mock + real schema/RLS.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const B = 'http://127.0.0.1:8767/', Q = process.argv[2], SHOTS = process.argv[3];
const db = (sql) => execFileSync('psql', ['-h', Q, '-p', '55432', '-U', 'postgres', '-d', 'shop', '-At', '-c', sql], { encoding: 'utf8' }).trim();
const results = []; const ok = (n, c, d) => results.push([c ? 'PASS' : 'FAIL', n, c ? '' : d]);
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const errors = [];
  ctx.on('page', (p) => p.on('pageerror', (e) => errors.push(e.message)));
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(B + 'index.html?t=5');
  await page.waitForSelector('.item');
  ok('menu loaded from database, no demo notice', !(await page.textContent('#notices')).includes('Demo'), await page.textContent('#notices'));
  await page.click('.item:has-text("Caffè Latte")'); await page.click('#addBtn');
  await page.click('#cartBtn'); await page.fill('#name', 'Siti'); await page.check('#consent');

  // first reply is lost after the server saved the order -> retry must not create a second order
  let dropped = false;
  await page.route('**/rest/v1/rpc/place_order', async (route) => {
    if (!dropped) { dropped = true; await route.fetch(); return route.abort('connectionreset'); }
    return route.continue();
  });
  await page.click('#placeBtn');
  await page.waitForFunction(() => document.querySelector('#checkoutError').textContent.length > 0);
  ok('network error explained', (await page.textContent('#checkoutError')).includes('connection'), await page.textContent('#checkoutError'));
  ok('server did save the first attempt', db('select count(*) from orders') === '1');
  await page.click('#placeBtn');
  await page.waitForSelector('#doneView:not([hidden])');
  ok('retry returned the same order, still one row', db('select count(*) from orders') === '1' && (await page.textContent('#orderNo')) === 'A001', db('select count(*) from orders'));
  ok('server totals incl. service + SST (9.90 -> 11.54)', db("select total_sen from orders") === '1154', db('select total_sen from orders'));
  await page.unroute('**/rest/v1/rpc/place_order');

  // staff: wrong password, non-staff account, real staff
  const staff = await ctx.newPage();
  await staff.goto(B + 'staff.html');
  await staff.fill('#email', 'staff@shop.test'); await staff.fill('#password', 'nope'); await staff.click('#login button');
  await staff.waitForFunction(() => document.querySelector('#loginError').textContent);
  ok('wrong password message', (await staff.textContent('#loginError')).includes('Wrong'), await staff.textContent('#loginError'));
  await staff.fill('#email', 'outsider@shop.test'); await staff.fill('#password', 'pw123456'); await staff.click('#login button');
  await staff.waitForFunction(() => document.querySelector('#loginError').textContent.includes('staff list'));
  ok('signed-in non-staff refused', true);
  await staff.fill('#email', 'staff@shop.test'); await staff.fill('#password', 'pw123456'); await staff.click('#login button');
  await staff.waitForSelector('.ticket:has-text("A001")');
  ok('staff board shows order', (await staff.textContent('.ticket')).includes('Table 5'));
  await staff.click('.ticket:has-text("A001") button:has-text("Start")');
  await staff.click('.ticket:has-text("A001") button:has-text("Mark paid")');
  await staff.waitForFunction(() => !document.querySelector('.ticket button.primary')?.textContent.includes('Start'));
  ok('status + paid saved in database', db("select status || ',' || payment_status from orders") === 'preparing,paid', db("select status || ',' || payment_status from orders"));
  await staff.click('[data-tab=menu]');
  await staff.check('input[aria-label="Sold out: Dark Mocha"]');
  await staff.fill('#itemRows tr:has-text("Caffè Latte") input[type=number]', '10.50');
  await staff.press('#itemRows tr:has-text("Caffè Latte") input[type=number]', 'Tab');
  await staff.waitForTimeout(800);
  ok('menu edits saved', db("select string_agg(id || '=' || price_sen || '/' || sold_out, ' ' order by id) from items where id in ('latte','mocha')") === 'latte=1050/false mocha=990/true' || db("select sold_out from items where id='mocha'") === 't' && db("select price_sen from items where id='latte'") === '1050',
    db("select string_agg(id || '=' || price_sen || '/' || sold_out, ' ' order by id) from items where id in ('latte','mocha')"));
  await staff.click('[data-tab=shop]');
  await staff.fill('#h-mon', '09:00-13:00, 18:00-01:00');
  await staff.click('#shopForm button[type=submit]');
  await staff.waitForSelector('#shopSaved:has-text("Saved")');
  ok('hours saved', db("select hours->>'mon' from settings") === '[["09:00", "13:00"], ["18:00", "01:00"]]', db("select hours->>'mon' from settings"));
  db(`update settings set hours = jsonb_set(hours, '{mon}', '[["00:00","00:00"]]')`);

  // customer status page follows staff changes; customer cannot read others' orders
  await page.bringToFront();
  await page.waitForFunction(() => document.querySelector('#payBox').textContent.includes('Paid'), null, { timeout: 15000 });
  ok('customer sees paid + preparing', (await page.textContent('#steps [aria-current=step]')) === 'Preparing');
  const leak = await page.evaluate(async () => (await fetch('http://127.0.0.1:8766/rest/v1/orders?select=*', { headers: { apikey: 'sb_publishable_test' } })).status);
  ok('public key cannot list orders (401)', leak === 401, leak);

  // headers: anon calls carry no Authorization; staff calls carry the user token
  const log = await (await fetch('http://127.0.0.1:8766/__log')).json();
  const anonRpc = log.filter((l) => l[1].startsWith('/rest/v1/rpc/place_order'));
  const staffPatch = log.filter((l) => l[0] === 'PATCH');
  ok('anon requests: key in apikey + Bearer', anonRpc.length >= 2 && anonRpc.every((l) => l[2] === 'sb_publishable_test' && l[3] === 'Bearer sb_publishable_test'), JSON.stringify(anonRpc));
  ok('staff requests: Bearer user token', staffPatch.length >= 4 && staffPatch.every((l) => /^Bearer tok-/.test(l[3] || '')), JSON.stringify(staffPatch));
  await staff.screenshot({ path: SHOTS + '/10-live-staff.png', fullPage: true });
  ok('no page errors', errors.length === 0, errors.join(' | '));
  for (const r of results) console.log(r.join('  '));
  console.log(results.filter((r) => r[0] === 'FAIL').length + ' failed of ' + results.length);
  await browser.close();
})().catch((e) => { console.error(e); for (const r of results) console.log(r.join('  ')); process.exit(1); });
