// Usage: node hours.js <order-site dir> <postgres socket dir> - JS isOpen() must match shop_is_open().
const { execFileSync } = require('child_process');
const [O, Q] = process.argv.slice(2);
global.window = globalThis; require(O + '/pricing.js');
const psql = (sql) => execFileSync('psql', ['-h', Q, '-p', '55432', '-U', 'postgres', '-d', 'shop', '-At', '-c', sql], { encoding: 'utf8' }).trim();
const hours = { mon: [['10:00', '14:00'], ['17:00', '22:00']], tue: [], wed: [['08:00', '08:00']], thu: [['10:00', '22:00']], fri: [['18:00', '02:00']], sat: [['20:00', '03:30']], sun: [['00:00', '06:00']] };
const closed_dates = ['2026-10-30', '2026-11-02'];
psql(`update settings set hours='${JSON.stringify(hours)}', closed_dates='{${closed_dates.join(',')}}'`);
const settings = { timezone: 'Asia/Kuala_Lumpur', hours, closed_dates };
let bad = 0, n = 0;
const start = Date.parse('2026-10-26T00:00:00+08:00'); // a Monday
const stamps = [];
for (let m = 0; m < 8 * 24 * 60; m += 23) stamps.push(start + m * 60000);
const sqlIn = stamps.map((t) => `('${new Date(t).toISOString()}'::timestamptz)`).join(',');
const db = psql(`select string_agg(case when public.shop_is_open(x) then 't' else 'f' end, '' order by x) from (values ${sqlIn}) v(x)`);
stamps.forEach((t, i) => { n++; const js = window.Pricing.isOpen(settings, new Date(t)) ? 't' : 'f'; if (js !== db[i]) { bad++; if (bad < 5) console.log('diff', new Date(t).toISOString(), js, db[i]); } });
console.log(`${n} times, ${bad} differences`);
process.exit(bad ? 1 : 0);
