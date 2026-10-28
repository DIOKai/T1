# Online payment (付费 — ask the user before connecting any of these)

The template's free defaults are **pay at the counter** and the shop's **static DuitNow QR**. Online payment through a gateway costs a fee per transaction and needs a merchant account (SSM registration, bank account, KYC). Under T1's rules: don't recommend signing up; describe the options when the owner asks, and wait for their OK before writing gateway code into their site.

## Options (fees from third-party comparisons, 2026 — check the gateway's own pricing page)
| Gateway | Methods | Fee (approx.) | Notes |
|---|---|---|---|
| Billplz | FPX, cards, e-wallets | FPX ~RM1.25 per payment on the free Basic plan; lower on paid plans; +8% SST on fees | popular with Malaysian SMEs |
| ToyyibPay | FPX, cards | per-transaction; the RM0 FPX "Santai" plan is for non-profits only | |
| Stripe | cards, FPX, GrabPay | ~3% + RM1.00 per payment (+1% international cards) | good docs, test mode |
| Dynamic DuitNow QR | via a provider/bank | per provider | confirms payment automatically, unlike the static QR |

## How to wire one in safely (pattern; the code is **未测试**)
The rule: **the amount always comes from the database, never from the browser**, and an order becomes `paid` only from the gateway's signed callback.

1. Turn on `payment.online = true` in settings (staff can't; owner runs SQL) — the customer page shows "Pay online" only when `window.startOnlinePayment` exists as well.
2. Edge Function `create-payment` (POST `{token}`): look up the order by `token` with the service role key, refuse if not `unpaid`, create a bill/checkout session at the gateway for `total_sen` with your order id as reference, return the gateway URL.
3. In the page, define the hook (e.g. in a small `payment.js` loaded after `app.js`):
   ```js
   window.startOnlinePayment = async (order) => {
     const r = await fetch(SITE_CONFIG.supabaseUrl + '/functions/v1/create-payment', {
       method: 'POST', headers: { 'Content-Type': 'application/json', apikey: SITE_CONFIG.publishableKey },
       body: JSON.stringify({ token: order.token }) });
     if (r.ok) location.href = (await r.json()).url;   // gateway page; it returns to index.html#order=<token>
   };
   ```
4. Edge Function `payment-callback`: **verify the gateway signature** (Billplz X-Signature, ToyyibPay callback hash, Stripe `Stripe-Signature` with the webhook secret), check the amount equals `total_sen`, then `update orders set payment_status = 'paid' where id = ...` with the service role. Ignore repeats (already paid).
5. Use the gateway's sandbox / test mode end to end before going live; keep secrets in `supabase secrets`, never in `config.js`.
6. Refunds: do them in the gateway dashboard, then staff set `payment_status = 'refunded'` (add that button if needed — the column already allows it).

Also add the gateway to `privacy.html` (it receives the customer's payment details) and to the `_headers` CSP if its script or form is loaded on your page.

## Sources (third-party comparisons — verify with the gateway)
- https://hitpayapp.com/hitpay-vs-billplz
- https://www.toyyibpay.com/toyyibpay/pricing-plans
- https://hitpayapp.com/my/blog/hitpay-vs-stripe-malaysia
