---
name: canva-to-web
description: Use when a café, bubble-tea shop, restaurant or food stall wants its menu (a Canva design, a menu photo, PDF or typed price list) turned into a mobile ordering website — table QR ordering, takeaway with pickup times, a staff/counter screen for incoming orders, sold-out and opening-hours control, multi-language menus (English / 中文 / Bahasa Melayu), SST and service charge, halal or allergen labels, DuitNow QR or pay-at-counter, Telegram order alerts, or a swipeable ordering demo. Also when they say "Canva 转网页", "把菜单做成点餐网站", "扫码点餐", "桌号 QR 点餐", "饮料店点单系统", "咖啡店菜单网站", "店员看订单的页面", "做一个可以滑动选饮料的网页", "手机点餐 demo", "Canva 设计变成可以互动的网站", "make my Canva menu a website", "QR ordering for my shop", even if Canva isn't mentioned.
---

# Menu → mobile ordering site (demo or real)

A menu design becomes **data** (`menu.json`), and a tested site is built around it. Canva's connector gives text and images, not working HTML, and a poster pasted as one image can't be tapped, read aloud or updated. `assets/order-site/` is a complete, tested ordering system — start from it; don't write one from scratch.

**What it is:** static pages (no build step, no CDN scripts) + a free Supabase Postgres database that does all the pricing and security. Without Supabase keys it runs as a **demo** in the browser, so the owner can try everything first.

| File | Role |
|---|---|
| `index.html`, `app.js` | customer page: table (`?t=12`) or takeaway, Popular row, categories, options sheet, cart, checkout, live order status |
| `staff.html`, `staff.js`, `staff-i18n.js` | staff screen in 中文 / English / BM: order board with beep, status / paid / cancel, prices, sold out, hours, closed dates, charges, pause switch, printable table QR codes (card titles in every shop language) |
| `supabase/schema.sql` | tables, row level security, `place_order()` (recalculates every price, checks hours, sold out, options, flood limits, idempotent retries), `order_status(token)`, `purge_personal_data()` |
| `pricing.js` | the same price / hours rules for display; proven equal to the SQL by `tests/parity.js` and `tests/hours.js` |
| `backend.js` | Supabase REST client + localStorage demo backend, same interface |
| `i18n.js` | customer page text in en / zh / ms (AI-written, like `staff-i18n.js`: a native speaker should read the Malay and Chinese) |
| `tools/menu_tool.py` | `check menu.json` (prices, ids, translations, halal wording, SST registration, hours) and `sql menu.json` (seed; a re-run keeps prices, sold out, hours and charges changed on the staff screen, `--overwrite` resets them) |
| `supabase/functions/notify-telegram/` | free Telegram message per new order, in the language set by `MESSAGE_LANG` (`zh` for a Chinese-speaking owner) |
| `privacy.html`, `_headers`, `robots.txt`, `config.js`, `vendor/qrcode.js` (MIT) | PDPA notice template, security headers, settings |

## Workflow

### 1. Get the menu content
- **Canva** (ask before using the connector — T1 rule): the user authorizes it themselves (`/mcp` → canva). `read-design` gives all text and page thumbnails; `export-design` gives PNG/JPG/PDF for colours and photos — **never HTML or SVG**. Details, Codex setup and plan limits: `references/canva-connector-and-licensing.md`.
- **No Canva:** a photo/PDF of the menu or typed text works the same.

### 2. Write `menu.json` and confirm it with the user
Copy `menu.sample.json`. Fill shop name (3 languages — ask the owner if the menu doesn't show it), items with categories, prices in RM, option groups (single: size/sweetness/milk with a default; multi: toppings with per-item `max` and group `max_total`), allergens on items **and on options** (cheese foam → milk), dietary, featured, opening hours (`["18:00","02:00"]` runs past midnight), closed dates, payment methods. `takeaway_preorder: false` (default) means no orders at all while closed, which is what "打烊时不能下单" asks for; set it true only if the owner wants takeaway booked ahead for the next opening.
Then `python tools/menu_tool.py check menu.json` and fix every error. **Show the user the extracted names and prices** before building — stylised menu fonts are misread, and this is the cheapest moment to fix it. Mark guessed items, translations and allergens as guesses; allergens must be checked by the owner against supplier labels.

### 3. Brand it
Colours are tokens at the top of `styles.css` (`--bg`, `--accent`, …, light and dark). Item art: `color` swatches, or `image` paths for photos the licence allows. Free web font only (Canva fonts can't be extracted). Keep the structure and behaviours in `references/ordering-ui-and-hosting.md`.

### 4. Demo first
`python -m http.server` in the folder (fetch doesn't work from `file://`), open `index.html?t=3` and `staff.html` in two tabs. The owner can place orders, move them on the staff board, mark sold out, change hours — all stored in that browser only.

### 5. Go live (only when the user wants real orders)
Follow `references/backend-setup.md`: Supabase project → run `schema.sql` → `menu_tool.py sql` seed → keys into `config.js` → staff accounts (sign-ups off, `insert into staff`) → optional Telegram alerts and PDPA purge → host on Cloudflare Pages (**not GitHub Pages: it forbids commerce**) → first live test checklist → print QR codes from the staff screen. The owner does every signup, login and key step; publishing is their decision.

### 6. Malaysian rules the site must respect
Read `references/malaysia-rules.md` before switching any of these on:
- **SST** 6% for F&B, only if registered (turnover ≥ RM1.5m); the template refuses SST without `sst_reg_no`.
- **Service charge** dine-in only by default; SST on service charge is a setting.
- **Halal** wording/logo only with a JAKIM certificate (number + expiry); the template hides it otherwise and `menu_tool.py` blocks the word.
- **5-sen rounding** applies to cash totals only; card/e-wallet pay the exact amount.
- **PDPA:** consent box, privacy notice in BM + English, minimal data, purge old names/phones, 72 h breach notification.

### 7. Payment
Free defaults: pay at counter, and the shop's static **DuitNow QR** (customer types the order number as reference; staff confirm in the bank app and tap "Mark paid" — nothing is automatic, say so). Gateways (Billplz, ToyyibPay, Stripe, dynamic QR) are **付费**: describe them only if asked, ask before wiring one, follow `references/online-payments.md` (amount from the database, signed callbacks; code there is untested).

### 8. Test before handing over
`tests/` runs against `menu.sample.json` and proves the **template** (see `tests/README.md`): SQL security + rules, JS/SQL price and hours parity, demo and live-mode browser flows, the Telegram function. Run it after changing schema, pricing or page code — keep the sample menu for that run. For the owner's real menu: `menu_tool.py check`, `node --check *.js`, open both pages with no console errors at 320 px, place one order of each kind; if you change behaviour, add a test rather than editing the sample-based ones until they pass.

## Mistakes this template already prevents (don't reintroduce them)
| Tempting shortcut | Why it's wrong |
|---|---|
| Let the page send prices/totals, or give `anon` insert on `orders` | anyone can edit the page and pay RM0.01; all orders go through `place_order()` |
| Put the service_role / secret key in `config.js` | it bypasses RLS: every customer could read every phone number |
| Load supabase-js or fonts from a CDN | extra failure point and CSP holes; the REST calls are ~100 lines in `backend.js` |
| "Halal", "pork-free" or SST shown to look official | illegal without certification / registration |
| Status via direct `select` on `orders` for customers | leaks other customers; customers use `order_status(token)` only |
| Retry a failed submit with a new request | duplicates orders; the page reuses `client_ref` until the cart changes |
| GitHub Pages for a live shop | its terms forbid commercial transactions |

## Limits to tell the user
- Tested on local Postgres 16 with Supabase-like roles and a PostgREST look-alike, **not on a live Supabase project** — run the live checklist in `backend-setup.md` §6 before printing QR codes.
- `?t=12` table numbers can be guessed; a prank order still has to be made by staff. If it happens, add random table tokens (not built).
- Staff can change prices, sold out, hours, closed dates, charges and the pause switch — nothing else (column-level grants). Names, new items, payment methods and the halal certificate are owner-only: `menu.json` + seed, or the SQL editor. There is no separate owner login on the staff screen.
- Not built: online payment, kitchen/receipt printing, reports beyond CSV export from Supabase, adding new items from the staff screen, e-invoice, allergens that change with the chosen option in the item's chips (options show their own allergens next to the option).
- Supabase Free pauses after about a week without activity and has no downloadable backups: export orders monthly.
- The site is a rebuild in the design's style, not a pixel copy of the Canva poster.

## Licence checklist for Canva content (not legal advice)
- Pro images on a website: each unedited file ≤ **480,000 px** (e.g. 600×800). Free content: no pixel limit. Mixed design → strictest rule.
- Fonts can't be extracted → use a free web font.
- Canva content can't be a logo/trademark → the shop logo must be the owner's own.
- No downloadable galleries of raw Canva images.
Full rules and sources in `references/canva-connector-and-licensing.md`.
