# Leads table and owner alerts (free tier)

Use the repo's `supabase` skill for project setup and SQL (ask first). Free plan: 500 MB database, 5 GB egress, 2 active projects, **paused after 1 week of inactivity** — tell the owner (https://supabase.com/pricing). Staying awake for sure means Pro (**付费**).

## 1. Table + Row Level Security (browser may only insert)
RLS must be on for every table in an exposed schema; without it a table "is readable and writable by any role with a grant on it". Secret keys never go in the browser. (https://supabase.com/docs/guides/database/postgres/row-level-security)

```sql
create table public.leads (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  name text not null check (char_length(name) between 1 and 80),
  phone text not null check (phone ~ '^\+?[0-9 \-]{8,16}$'),
  vehicle text not null check (char_length(vehicle) <= 80),
  service text not null check (service in ('Full detail','Ceramic coating','Window tint','Colour wrap')),
  date date not null,
  paint text, tint text, source text,
  consent boolean not null check (consent),
  status text not null default 'new'
);
alter table public.leads enable row level security;
revoke all on table public.leads from anon, authenticated;
grant insert (name, phone, vehicle, service, date, paint, tint, source, consent) on public.leads to anon;
create policy "public can submit a lead" on public.leads
  for insert to anon with check (consent and date >= current_date);
```
No select policy → nobody can read leads with the public key. The owner reads them in Studio's Table Editor (the "dashboard table"), sorting by `created_at`, editing `status`.

Front end (`index.html` → `SITE_CONFIG`):
```js
endpoint: 'https://YOUR-REF.supabase.co/rest/v1/leads',
headers: { apikey: 'PUBLISHABLE_KEY', Authorization: 'Bearer PUBLISHABLE_KEY', Prefer: 'return=minimal' }
```
`return=minimal` matters: returning the row would need select rights and fail (42501) — 未验证 in this exact setup, test one insert. Check that a `select` with the same key returns nothing.

## 2. Alert the owner
Trigger: Database Webhook on `insert` into `leads` → POST (async via `pg_net`, doesn't slow the insert) to an Edge Function (https://supabase.com/docs/guides/database/webhooks). The function holds the bot token / email key as secrets and sends the message.

| Channel | Cost | Notes |
|---|---|---|
| Telegram bot | free | `POST https://api.telegram.org/bot<TOKEN>/sendMessage` with `chat_id`, `text` (https://core.telegram.org/bots/api). ≤ 1 msg/s per chat (https://core.telegram.org/bots/faq). Owner must press Start on the bot first. Best default. |
| Email (Resend) | free 3,000/month, 100/day (https://resend.com/pricing) | needs a verified domain |
| WhatsApp click-to-chat | free | `https://wa.me/<number>?text=…` — the customer sends it, not the server (format 未验证 on official page) |
| SMS (Twilio) | **付费** ~US$0.34 per SMS to Malaysia + number from ~US$1.15/month (https://www.twilio.com/en-us/sms/pricing/my, 未验证 column) | only if the owner insists; ask with the price |

Minimal Edge Function body (Deno; adapt with the `supabase` skill):
```ts
Deno.serve(async (req) => {
  const { record: r } = await req.json();
  const text = `New booking: ${r.name} ${r.phone}\n${r.service} on ${r.date}\n${r.vehicle} · ${r.paint ?? ''} ${r.tint ?? ''}`;
  await fetch(`https://api.telegram.org/bot${Deno.env.get('TG_TOKEN')}/sendMessage`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: Deno.env.get('TG_CHAT_ID'), text }) });
  return new Response('ok');
});
```
Protect the function: check a shared secret header set in the webhook config, or the webhook can be called by anyone (未验证 which header the dashboard sends; set your own).

## 3. Spam
- Template: hidden honeypot `company` field and "submitted < 3 s after opening" are silently dropped.
- Database `check` constraints reject junk shapes.
- Cloudflare Turnstile is free (20 widgets, unlimited challenges, https://developers.cloudflare.com/turnstile/plans/); verify the token server-side in the Edge Function (insert via the function instead of directly) when spam starts.

## No-database alternative
Form-to-email services (Formspree, Web3Forms …) have free tiers (limits 未验证). Point `endpoint` at them; you lose the table.
