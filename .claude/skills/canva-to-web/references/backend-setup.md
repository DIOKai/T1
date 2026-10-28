# Going live: Supabase, staff accounts, Telegram alerts, hosting

Everything here is on free plans. Dashboard menu names change often: if a name below doesn't match, search the Supabase docs for the feature rather than guessing. Steps the owner must do themselves (sign-ups, logins, keys) are marked **owner**.

## 1. Supabase project (owner)
1. Sign up at supabase.com, create a project on the Free plan, region **Southeast Asia (Singapore)** for Malaysian customers.
2. Free plan facts to tell the owner (from Supabase pricing/docs, check the current page): 500 MB database, 2 active projects, **the project pauses after about a week with no activity** (it's restarted from the dashboard), and no downloadable daily backups on Free. A shop that takes orders every day stays active; still export the `orders` table to CSV monthly (Table Editor → orders → Export).
3. **SQL Editor** → paste and run `supabase/schema.sql` once.
4. Load the menu: `python tools/menu_tool.py check menu.json` (fix every error), then `python tools/menu_tool.py sql menu.json > seed.sql`, paste `seed.sql` into the SQL Editor and run. Re-running is safe (upserts); it does not delete items — hide one with `update items set active = false where id = '...'`.
5. **Project Settings → API Keys**: copy the project URL and the **publishable** key (`sb_publishable_...`; older projects show a legacy `anon` key, which also works) into `config.js`. Never put the **secret / service_role** key in any file the browser loads: it bypasses all row level security.

What the schema guarantees (tested in `tests/test_sql.py`): the public key can read the menu, call `place_order()` and `order_status(token)`, nothing else. Prices are always recalculated in the database, so a customer editing the page can't change what they pay.

## 2. Staff accounts (owner)
1. **Authentication → Sign In / Providers**: turn off "Allow new users to sign up". Otherwise anyone can create an account (they still can't see orders, but there's no reason to allow it).
2. **Authentication → Users → Add user → Create new user**, email + password, auto-confirm. One account per device or per person.
3. Give the account staff rights in the SQL Editor:
   ```sql
   insert into public.staff (user_id, display_name)
   select id, 'Counter tablet' from auth.users where email = 'counter@yourshop.my';
   ```
   Remove someone: `delete from public.staff where user_id = (select id from auth.users where email = '...');` then delete the user.
4. Staff sign in at `/staff.html`. The page refreshes every `pollSeconds` (8 s), beeps on new orders once "Sound on" is tapped (browsers block sound until a tap) and keeps the screen awake where the browser supports it.

Staff can change an order's status, payment status and note, mark items/options sold out, edit prices, hours, closed dates, charges and the pause switch. They cannot change an order's amounts or delete orders. If the owner wants staff who can't edit prices, add an `owner` flag to `staff` and tighten the `staff_edit` policies (not done in the template).

## 3. Telegram alerts for new orders (free, optional)
1. In Telegram, talk to **@BotFather** → `/newbot` → copy the token (**owner**; it's a secret).
2. Add the bot to the staff group (or message it directly), send any message, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and read `chat.id` (groups are negative numbers).
3. Deploy the function, either with the Supabase CLI:
   ```bash
   npx supabase login
   npx supabase link --project-ref <ref>
   npx supabase secrets set TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... WEBHOOK_SECRET=$(openssl rand -hex 24)
   npx supabase functions deploy notify-telegram --no-verify-jwt
   ```
   or in the dashboard (**Edge Functions → Deploy a new function → via editor**, paste `supabase/functions/notify-telegram/index.ts`, add the three secrets, turn JWT verification off for this function). `--no-verify-jwt` is safe here because the function checks `x-webhook-secret` itself.
4. **Database → Webhooks → Create**: table `public.orders`, event **Insert**, type HTTP request, POST to `https://<ref>.supabase.co/functions/v1/notify-telegram`, add header `x-webhook-secret: <same secret>`.
5. Place a test order and check the message arrives. If not: **Edge Functions → notify-telegram → Logs**.
The message leaves out the phone number (Telegram is a third party; share the minimum). Plain text only, so customer-typed names can't inject links. The function code was type-checked by eye and is **未测试** against real Telegram; test it before relying on it.

## 4. PDPA clean-up (optional, free)
`purge_personal_data(days)` blanks names, phones and notes on orders older than `days` and keeps amounts for the books. Schedule it: **Integrations → Cron** (enable pg_cron), then
```sql
select cron.schedule('purge-personal-data', '15 3 * * *', $c$select public.purge_personal_data(90)$c$);
```
Pick the number of days with the owner and write the same number in `privacy.html`.

## 5. Hosting the site
The site is static files: upload the folder, no build step.

| Host | Commerce on free plan | Notes |
|---|---|---|
| Cloudflare Pages | not forbidden in the terms we read (未验证 — owner should read the current terms) | **Workers & Pages → Create → Pages → Upload assets**, drag the folder. Reads `_headers` (security headers). Free subdomain `*.pages.dev`, custom domain free |
| Netlify | check current terms (未验证) | drag-and-drop deploy; also reads `_headers` |
| GitHub Pages | **forbidden**: GitHub's terms say Pages isn't for online business / e-commerce / commercial transactions | demo only |

Before uploading:
- `config.js`: real URL + publishable key; `duitnowQrImage` set if DuitNow is on.
- `_headers`: replace `YOUR-PROJECT` with the project ref so the Content-Security-Policy allows the API.
- `privacy.html`: every [bracket] filled in, English + Bahasa Melayu.
- Remove `menu.sample.json` and `tools/` from the upload (not secret, just not needed). Don't upload `tests/`.
Publishing is the owner's decision: ask before deploying anywhere.

## 6. First live test (do it before printing table QR codes)
1. Open the site on a phone with `?t=1`: menu loads, no "Demo mode" banner.
2. Place an order at the counter-payment option. It appears on `/staff.html` within ~8 s with a beep; Telegram message arrives.
3. Staff: Start → Ready → Collected, Mark paid; the customer page follows.
4. Mark an item sold out; the menu shows it as sold out after a refresh. Pause orders; the banner shows.
5. Takeaway without `?t`: pickup times only inside opening hours; phone is required.
6. Turn SST on in the Shop tab only after entering the registration number; check the cart shows it.
7. In a private window, open `https://<ref>.supabase.co/rest/v1/orders?select=*` with header `apikey: <publishable key>` (e.g. `curl -H "apikey: ..."`): it must be refused. If it returns orders, stop and re-run schema.sql.
8. Print one table QR from the **Table QR** tab, scan it, then print the rest.

## Optional: Supabase MCP for the agent
Not needed (pasting SQL into the SQL Editor works). If the owner wants the agent to run SQL directly, ask first — it gets full access to the project. Hosted server URL `https://mcp.supabase.com/mcp`:
- Claude Code: `claude mcp add --transport http supabase https://mcp.supabase.com/mcp` then `/mcp` → authenticate.
- Codex: in `~/.codex/config.toml` add `[mcp_servers.supabase]` with `url = "https://mcp.supabase.com/mcp"`, then `codex mcp login supabase` (未验证; check `codex mcp --help`).
Point it at a test project first, never at a live shop without the owner watching.

## Sources
- API keys (publishable/secret, headers): https://supabase.com/docs/guides/api/api-keys
- Row level security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Database webhooks: https://supabase.com/docs/guides/database/webhooks
- Edge Functions secrets and deploy: https://supabase.com/docs/guides/functions
- Telegram Bot API (`sendMessage`, `getUpdates`): https://core.telegram.org/bots/api
- GitHub Pages limits / prohibited uses: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Cloudflare Pages limits: https://developers.cloudflare.com/pages/platform/limits/
