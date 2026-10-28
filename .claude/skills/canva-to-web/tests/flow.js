// Usage: serve order-site on :8765 (python3 -m http.server 8765), then: node flow.js <screenshot dir>
// Demo-mode end-to-end test of the customer page and staff screen.
const { chromium } = require('playwright');
const B = 'http://localhost:8765/';
const SHOTS = process.argv[2];
const results = [];
const ok = (name, cond, detail) => { results.push([cond ? 'PASS' : 'FAIL', name, cond ? '' : detail]); };
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'en-GB' });
  const errors = [];
  ctx.on('page', (p) => { p.on('pageerror', (e) => errors.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); }); });

  // staff: open 24h, 10% service, 6% SST
  const staff = await ctx.newPage();
  await staff.goto(B + 'staff.html');
  await staff.click('[data-tab=shop]');
  for (const d of ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) await staff.fill('#h-' + d, '00:00-00:00');
  await staff.fill('#svc', '10'); await staff.fill('#sst', '6'); await staff.fill('#sstReg', 'W10-1808-31000099');
  await staff.click('#shopForm button[type=submit]');
  await staff.waitForSelector('#shopSaved:has-text("Saved")');
  ok('staff saves shop settings', true);

  const page = await ctx.newPage();
  await page.goto(B + 'index.html?t=7');
  await page.waitForSelector('.item');
  ok('table pill', (await page.textContent('#modePill')) === 'Table 7', await page.textContent('#modePill'));
  ok('demo notice shown', (await page.textContent('#notices')).includes('Demo mode'));
  ok('no halal badge without certificate', !(await page.textContent('body')).toLowerCase().includes('halal'));
  await page.screenshot({ path: SHOTS + '/01-menu.png', fullPage: true });

  // latte large + oat x2
  await page.click('.item:has-text("Caffè Latte")');
  await page.check('input[name=size][value=large]', { force: true });
  await page.check('input[name=milk][value=oat]', { force: true });
  await page.click('#qPlus');
  ok('live price on add button', (await page.textContent('#addBtn')).includes('RM 26.80'), await page.textContent('#addBtn'));
  await page.screenshot({ path: SHOTS + '/02-item.png' });
  await page.click('#addBtn');
  // matcha + 2 pearls + foam; foam max 1, toppings max 4
  await page.click('.item:has-text("Uji Matcha")');
  const plus = (o) => page.click(`button[data-o=${o}][data-d="1"]`);
  ok('option allergen shown (cheese foam: milk)', (await page.textContent('.multi-row:has-text("Cheese foam")')).includes('Contains: Milk'), await page.textContent('.multi-row:has-text("Cheese foam")'));
  await plus('pearl'); await plus('pearl'); await plus('foam');
  ok('foam capped at 1', await page.isDisabled('button[data-o=foam][data-d="1"]'));
  await plus('jelly');
  ok('toppings capped at 4 total', await page.isDisabled('button[data-o=pearl][data-d="1"]') && await page.isDisabled('button[data-o=jelly][data-d="1"]'));
  await page.click('button[data-o=jelly][data-d="-1"]');
  await page.click('#addBtn');
  ok('bar total', (await page.textContent('#cartTotal')) === 'RM 52.70', await page.textContent('#cartTotal'));

  await page.click('#cartBtn');
  const sum = await page.textContent('#sum');
  ok('SST registration number shown', sum.includes('SST reg. no. W10-1808-31000099'), sum);
  ok('cart shows service + SST', sum.includes('Service charge (10%)') && sum.includes('RM 4.52') && sum.includes('SST (6%)') && sum.includes('RM 2.98') && sum.includes('RM 52.70'), sum);
  ok('pickup time hidden for dine-in', await page.isHidden('#pickupField'));
  ok('no stray 0 on items without allergens', !(await page.textContent('.item:has-text("Sparkling Lemon") .chips')).includes('0'), await page.textContent('.item:has-text("Sparkling Lemon") .chips'));
  await page.click('#placeBtn');
  ok('name required message', (await page.textContent('#checkoutError')).includes('name'), await page.textContent('#checkoutError'));
  await page.fill('#name', 'Ali <b>x</b>');
  await page.click('#placeBtn');
  ok('consent required message', (await page.textContent('#checkoutError')).includes('consent'), await page.textContent('#checkoutError'));
  await page.check('#consent');
  await page.screenshot({ path: SHOTS + '/03-cart.png', fullPage: false });
  await page.click('#placeBtn');
  await page.waitForSelector('#doneView:not([hidden])');
  ok('order number A001', (await page.textContent('#orderNo')) === 'A001', await page.textContent('#orderNo'));
  ok('counter payment text with cash', (await page.textContent('#payBox')).includes('RM 52.70'), await page.textContent('#payBox'));
  ok('url has order token', /#order=[0-9a-f-]{36}$/.test(page.url()), page.url());
  await page.screenshot({ path: SHOTS + '/04-done.png', fullPage: true });

  // staff sees it, moves it, marks paid
  await staff.bringToFront();
  await staff.click('[data-tab=orders]');
  await staff.waitForSelector('.ticket:has-text("A001")', { timeout: 15000 });
  const tk = await staff.textContent('.ticket:has-text("A001")');
  ok('staff ticket details', tk.includes('Table 7') && tk.includes('2 × Caffè Latte') && tk.includes('Pearl') === false && tk.includes('Brown sugar pearls ×2') && tk.includes('Ali <b>x</b>'), tk);
  await staff.click('.ticket:has-text("A001") button:has-text("Start")');
  await staff.click('.ticket:has-text("A001") button:has-text("Mark paid")');
  await staff.screenshot({ path: SHOTS + '/05-staff.png', fullPage: true });
  await page.bringToFront();
  await page.waitForFunction(() => document.querySelector('#steps li[aria-current=step]')?.textContent === 'Preparing', null, { timeout: 15000 });
  ok('customer sees preparing + paid', (await page.textContent('#payBox')).includes('Paid'), await page.textContent('#payBox'));

  // sold out while in cart -> server-side rejection is explained
  await page.click('#orderMore');
  await page.click('.item:has-text("Sparkling Lemon")');
  await page.click('#addBtn');
  await staff.click('[data-tab=menu]');
  await staff.check('input[aria-label="Sold out: Sparkling Lemon Tea"]');
  await page.click('#cartBtn');
  await page.fill('#name', 'Mei'); await page.check('#consent');
  await page.click('#placeBtn');
  await page.waitForFunction(() => document.querySelector('#checkoutError').textContent.length > 0);
  ok('sold-out error shown', (await page.textContent('#checkoutError')).includes('sold out'), await page.textContent('#checkoutError'));
  ok('sold-out line marked, button disabled', (await page.$('#lines li.out')) !== null && await page.isDisabled('#placeBtn'));
  await page.screenshot({ path: SHOTS + '/06-soldout.png' });
  await page.click('#lines li.out button:first-child');
  await page.keyboard.press('Escape');
  await page.reload(); await page.waitForSelector('.item');
  ok('sold-out item disabled on menu', await page.isDisabled('.item:has-text("Sparkling Lemon")'));

  // takeaway (no table), Chinese
  await page.goto(B + 'index.html?lang=zh');
  await page.waitForSelector('.item');
  ok('chinese ui', (await page.textContent('#notices')).includes('试玩模式') && (await page.getAttribute('html', 'lang')) === 'zh-Hans');
  await page.click('.item:has(h3:text-is("拿铁"))');
  await page.click('#addBtn');
  await page.click('#cartBtn');
  ok('pickup slots offered', (await page.$$('#pickup option')).length > 3);
  await page.fill('#name', '小明'); await page.check('#consent');
  await page.click('#placeBtn');
  ok('takeaway needs phone (zh)', (await page.textContent('#checkoutError')).includes('电话'), await page.textContent('#checkoutError'));
  await page.fill('#phone', '012-345 6789');
  await page.click('#placeBtn');
  await page.waitForSelector('#doneView:not([hidden])');
  ok('takeaway order A002 with pickup time', (await page.textContent('#orderNo')) === 'A002' && (await page.textContent('#doneWhere')).includes('取餐'), await page.textContent('#doneWhere'));
  await page.screenshot({ path: SHOTS + '/07-zh-done.png', fullPage: true });

  // DuitNow payment instructions (no QR image configured in the test)
  await page.click('#orderMore');
  await page.click('.item:has(h3:text-is("拿铁"))'); await page.click('#addBtn'); await page.click('#cartBtn');
  await page.check('input[name=payment][value=duitnow_qr]', { force: true });
  await page.click('#placeBtn');
  await page.waitForSelector('#doneView:not([hidden])');
  const pb = await page.textContent('#payBox');
  ok('duitnow instructions with order ref', pb.includes('DuitNow') && pb.includes('A003') && !pb.includes('false'), pb);

  // closed all week: banner lists hours, ordering blocked
  await staff.bringToFront();
  await staff.click('[data-tab=shop]');
  for (const d of ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) await staff.fill('#h-' + d, d === 'mon' ? '10:00-14:00, 17:00-22:00' : '');
  // closed today whatever the time: today is also a closed date
  await staff.fill('#closedDates', await staff.evaluate(() => window.Pricing.localDate(new Date(), 'Asia/Kuala_Lumpur')));
  await staff.click('#shopForm button[type=submit]');
  await staff.waitForSelector('#shopSaved:has-text("Saved")');
  await page.bringToFront();
  await page.goto(B + 'index.html?t=4');
  await page.waitForSelector('.item');
  const nt = await page.textContent('#notices');
  ok('closed banner with hours', nt.includes('closed') && nt.includes('10:00–14:00, 17:00–22:00') && !nt.includes('object'), nt);
  await page.screenshot({ path: SHOTS + '/07b-closed.png' });
  await page.click('.item:has-text("Caffè Latte")'); await page.click('#addBtn'); await page.click('#cartBtn');
  ok('cannot place dine-in order while closed', await page.isDisabled('#placeBtn'));
  await page.keyboard.press('Escape');
  await page.goto(B + 'index.html'); await page.waitForSelector('.item');
  await page.click('#cartBtn');
  ok('no takeaway pickup slots while closed', (await page.$$eval('#pickup option', (os) => os.map((o) => o.value))).join() === '' && await page.isDisabled('#placeBtn'));
  await page.keyboard.press('Escape');
  await staff.bringToFront();
  for (const d of ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) await staff.fill('#h-' + d, '00:00-00:00');
  await staff.fill('#closedDates', '');
  await staff.click('#shopForm button[type=submit]');
  await staff.waitForSelector('#shopSaved:has-text("Saved")');

  // SST cannot be switched on without a registration number
  await staff.bringToFront();
  await staff.fill('#sstReg', '');
  await staff.click('#shopForm button[type=submit]');
  ok('staff form refuses SST without reg no', (await staff.textContent('#shopError')).includes('registration'), await staff.textContent('#shopError'));
  await staff.fill('#sstReg', 'W10-1808-31000099');
  // a closed date blocks dine-in ordering today
  const today = await page.evaluate(() => window.Pricing.localDate(new Date(), 'Asia/Kuala_Lumpur'));
  await staff.fill('#closedDates', today);
  await staff.click('#shopForm button[type=submit]');
  await staff.waitForSelector('#shopSaved:has-text("Saved")');
  await page.bringToFront();
  await page.goto(B + 'index.html?t=4'); await page.waitForSelector('.item');
  ok('closed date shows closed banner', (await page.textContent('#notices')).includes('closed'), await page.textContent('#notices'));
  await staff.bringToFront();
  await staff.fill('#closedDates', '');
  await staff.click('#shopForm button[type=submit]');
  await staff.waitForSelector('#shopSaved:has-text("Saved")');

  // staff screen in Chinese
  const zh = await ctx.newPage();
  await zh.goto(B + 'staff.html?lang=zh');
  await zh.waitForSelector('#board .col');
  ok('staff screen in Chinese', (await zh.textContent('[data-tab=orders]')) === '订单' && (await zh.textContent('#board')).includes('新订单') && (await zh.getAttribute('html', 'lang')) === 'zh-Hans', await zh.textContent('#board'));
  await zh.close();

  // pause orders
  await staff.bringToFront();
  await staff.uncheck('#accepting');
  await page.bringToFront();
  await page.goto(B + 'index.html?t=2&lang=ms');
  await page.waitForSelector('.item');
  ok('paused banner (ms)', (await page.textContent('#notices')).includes('dihentikan'), await page.textContent('#notices'));
  await staff.check('#accepting');

  // QR codes
  await staff.bringToFront();
  await staff.click('[data-tab=qr]');
  await staff.click('#makeQr');
  ok('21 QR cards (takeaway + 20 tables)', (await staff.$$('.qr-card svg')).length === 21);
  ok('QR card title in all shop languages', (await staff.$eval('.qr-card:nth-child(3) svg title', (n) => n.textContent)) === 'Table 2 · 2 号桌 · Meja 2', await staff.$eval('.qr-card:nth-child(3) svg title', (n) => n.textContent));
  await staff.screenshot({ path: SHOTS + '/08-qr.png' });

  // layout: no sideways scroll at 320px, and dark mode
  const small = await ctx.newPage();
  await small.setViewportSize({ width: 320, height: 640 });
  await small.goto(B + 'index.html?t=1'); await small.waitForSelector('.item');
  ok('no horizontal overflow at 320px', await small.evaluate(() => document.documentElement.scrollWidth <= 320), await small.evaluate(() => document.documentElement.scrollWidth));
  const small44 = await small.evaluate(() => [...document.querySelectorAll('button:not([disabled])')].filter((b) => b.offsetParent && (b.offsetHeight < 44 || b.offsetWidth < 44)).map((b) => b.textContent.trim()));
  ok('buttons at least 44px', small44.length === 0, JSON.stringify(small44));
  const dark = await browser.newPage({ colorScheme: 'dark', viewport: { width: 390, height: 844 } });
  await dark.goto(B + 'index.html?t=1'); await dark.waitForSelector('.item');
  await dark.screenshot({ path: SHOTS + '/09-dark.png' });

  ok('no console errors', errors.length === 0, errors.join(' | '));
  for (const r of results) console.log(r.join('  '));
  console.log(results.filter((r) => r[0] === 'FAIL').length + ' failed of ' + results.length);
  await browser.close();
})().catch((e) => { console.error(e); for (const r of results) console.log(r.join('  ')); process.exit(1); });
