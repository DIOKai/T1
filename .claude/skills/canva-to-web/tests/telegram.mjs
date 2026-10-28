// Usage: node --experimental-strip-types tests/telegram.mjs <order-site dir>
// Runs the notify-telegram Edge Function with a fake Deno and fetch: secret check, message text, no phone, no parse_mode.
import { pathToFileURL } from 'node:url';
import { copyFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const tmp = mkdtempSync(join(tmpdir(), 'tg-'));
const site = process.argv[2];
let handler = null; const sent = []; const env = {};
globalThis.Deno = { env: { get: (k) => env[k] }, serve: (h) => { handler = h; } };
globalThis.fetch = async (url, init) => { sent.push({ url, body: JSON.parse(init.body) }); return new Response('{}', { status: 200 }); };
const fails = []; const ok = (n, c, d) => { console.log((c ? 'PASS ' : 'FAIL ') + n + (c ? '' : '  -> ' + d)); if (!c) fails.push(n); };
const order = { order_no: 'A007', mode: 'dine_in', table_no: 4, customer_name: 'Mei <b>', phone: '0123456789', notes: 'less ice',
  total_sen: 1154, payment_method: 'duitnow_qr', payment_status: 'unpaid',
  lines: [{ qty: 2, name: { en: 'Latte', zh: '拿铁' }, options: [{ label: { en: 'Large', zh: '大杯' }, qty: 1 }, { label: { en: 'Pearls', zh: '珍珠' }, qty: 2 }] }] };
const call = (headers, body) => handler(new Request('http://x/', { method: 'POST', headers, body: JSON.stringify(body) }));

for (const lang of ['zh', 'en', 'ms']) {
  Object.assign(env, { WEBHOOK_SECRET: 's3cret-value', TELEGRAM_BOT_TOKEN: 'T', TELEGRAM_CHAT_ID: '-100', MESSAGE_LANG: lang });
  handler = null;
  // a fresh copy per language: the module reads MESSAGE_LANG once when it loads
  const copy = join(tmp, `index-${lang}.ts`);
  copyFileSync(site + '/supabase/functions/notify-telegram/index.ts', copy);
  await import(pathToFileURL(copy).href);
  sent.length = 0;
  const bad = await call({ 'x-webhook-secret': 'wrong-secret' }, { type: 'INSERT', table: 'orders', record: order });
  ok(`${lang}: wrong secret refused`, bad.status === 403 && sent.length === 0, bad.status);
  const res = await call({ 'x-webhook-secret': 's3cret-value' }, { type: 'INSERT', table: 'orders', record: order });
  const msg = sent[0]?.body;
  ok(`${lang}: message sent`, res.status === 200 && msg && msg.chat_id === '-100', res.status);
  ok(`${lang}: no phone, no parse_mode`, !msg.text.includes('0123456789') && !('parse_mode' in msg), msg.text);
  const want = { zh: ['新订单 A007', '桌号 4', '2 x 拿铁 (大杯, 珍珠 x2)', '备注: less ice', 'DuitNow QR', '未付款'],
                 en: ['New order A007', 'Table 4', '2 x Latte (Large, Pearls x2)', 'Note: less ice', 'unpaid'],
                 ms: ['Pesanan baharu A007', 'Meja 4', '2 x Latte (Large, Pearls x2)', 'belum bayar'] }[lang];
  ok(`${lang}: text`, want.every((w) => msg.text.includes(w)), msg.text);
}
const ignored = await call({ 'x-webhook-secret': 's3cret-value' }, { type: 'UPDATE', table: 'orders', record: order });
ok('updates ignored', (await ignored.text()) === 'ignored');
console.log(fails.length ? `${fails.length} failed` : 'all passed');
process.exit(fails.length ? 1 : 0);
