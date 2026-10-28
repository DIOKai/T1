// Usage: node parity.js <order-site dir> <postgres socket dir>
// Random carts: JS Pricing.totals() must equal what place_order() charges in Postgres.
const { execFileSync } = require('child_process');
const O = process.argv[2], Q = process.argv[3];
global.window = globalThis;
require(O + '/pricing.js');
const fs = require('fs');
global.localStorage = { getItem: () => null, setItem() {}, removeItem() {} };
require(O + '/backend.js');
const menu = window.Backend.fromFile(JSON.parse(fs.readFileSync(O + '/menu.sample.json', 'utf8')));
const psql = (sql) => execFileSync('psql', ['-h', Q, '-p', '55432', '-U', 'postgres', '-d', 'shop', '-At', '-c', sql], { encoding: 'utf8' }).trim();
const allOpen = JSON.stringify(Object.fromEntries(['mon','tue','wed','thu','fri','sat','sun'].map((d) => [d, [['00:00','00:00']]])));
let rnd = 7; const r = (n) => { rnd = (rnd * 1103515245 + 12345) % 2147483648; return rnd % n; };
const rates = [[0.10, 0.06, true, true], [0.10, 0.06, false], [0, 0.06, true], [0.05, 0.08, true], [0.065, 0.0625, true], [0.0, 0.0, true], [0.1, 0.1, true]];
let fails = 0, n = 0;
for (const [svc, sst, onSvc, svcTa = false] of rates) {
  psql(`delete from orders; update settings set sst_reg_no='W10-TEST', service_charge_rate=${svc}, sst_rate=${sst}, sst_on_service_charge=${onSvc}, service_charge_takeaway=${svcTa}, hours='${allOpen}', accepting_orders=true`);
  Object.assign(menu.settings, { service_charge_rate: svc, sst_rate: sst, sst_on_service_charge: onSvc, service_charge_takeaway: svcTa });
  for (let k = 0; k < 25; k++) {
    const lines = Array.from({ length: 1 + r(4) }, () => {
      const it = menu.items[r(menu.items.length)];
      const options = {};
      for (const gid of it.groups) {
        const g = menu.groups[gid];
        if (g.type === 'single') { if (r(2)) options[gid] = g.options[r(g.options.length)].id; }
        else { const o = g.options[r(g.options.length)]; const q = r(Math.min(o.max_qty, g.max_total || 9) + 1); if (q) options[gid] = { [o.id]: q }; }
      }
      return { item: it.id, qty: 1 + r(5), options };
    });
    const mode = r(2) ? 'takeaway' : 'dine_in';
    const js = window.Pricing.totals(menu, lines, mode);
    const p = { mode, pickup_at: new Date(Date.now() + 40 * 60000).toISOString(), table: 3, name: 'T', phone: '01' + String(10000000 + n), payment: 'counter', consent: true, lines };
    const db = JSON.parse(psql(`select public.place_order($J$${JSON.stringify(p)}$J$::jsonb)`));
    n++;
    const same = db.subtotal_sen === js.subtotal && db.service_sen === js.service && db.sst_sen === js.sst && db.total_sen === js.total && db.cash_total_sen === js.cash;
    if (!same) { fails++; console.log('MISMATCH', mode, svc, sst, onSvc, JSON.stringify(js), JSON.stringify({ s: db.subtotal_sen, sv: db.service_sen, t: db.sst_sen, tot: db.total_sen, c: db.cash_total_sen })); }
  }
}
// the documented example
Object.assign(menu.settings, { service_charge_rate: 0.10, sst_rate: 0.06, sst_on_service_charge: true });
const ex = window.Pricing.totals(menu, [{ item: 'latte', qty: 2, options: { size: 'large', milk: 'oat' } }, { item: 'matcha', qty: 1, options: { toppings: { pearl: 2, foam: 1 } } }]);
console.log('example', JSON.stringify(ex), ex.total === 5270 ? 'OK' : 'WRONG');
console.log(`${n} carts, ${fails} mismatches`);
process.exit(fails ? 1 : 0);
