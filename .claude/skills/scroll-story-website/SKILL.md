---
name: scroll-story-website
description: Build a cinematic scroll-story website for a small business (car detailing, tint or wrap shop, salon, property) the way the "$900 website" reels do — scrolling scrubs a canvas image sequence (dirty car turns clean, camera pushes into the badge, light sweeps the paint), a "try it on" colour or film picker, a slide-in booking drawer that books in 30 seconds, and leads landing in a free Supabase table with a free Telegram or email alert to the owner. Ships a zero-dependency static template plus the frame pipeline (Blender, ffmpeg), reduced motion, performance budgets, spam protection, PDPA consent and free hosting. Use whenever the user wants a scroll animation site, Apple-style product scroll, landing page with booking, or a client website to sell — even if they only say "滚动网站", "滑动动画网站", "滚动动画", "洗车网站", "贴膜店网站", "改色膜网站", "预约网站", "商家官网", "帮客户做网站", "苹果那种滚动", "网站收订单".
---

# Scroll-story website

The reels sell three things together: a **film the visitor drives with the scroll wheel**, a **toy** (pick a colour, see it on the car), and a **booking that takes 30 seconds and reaches the owner's phone**. The film is just pictures drawn on a `<canvas>` — no video player, no 3D engine. The hard parts are making it light enough for a phone, not trapping people who can't or won't scroll through it, and getting leads to the owner without paying for SMS.

Research notes with sources: `docs/skill-batches/archviz-batch2-2026-10-22-research/scroll-story-website.md` (in the T1 repo).

## T1 rules that apply here
- Ask before using any other skill named below, in one go (what it does, whether it edits files, runs scripts or goes online).
- Free first. **付费** items (Twilio SMS, paid AI video, Supabase Pro, paid form services) are only mentioned with the price and used after the user says yes.
- Never put secret keys in the page. The Supabase publishable/anon key is fine in the browser **only** with RLS set as in `references/leads-backend.md`.

## Workflow

### 1. Brief (one round of questions)
Business name, services and prices to show, the story beats (3–5, e.g. dirty → washed → polished → coated), brand colours, which colours/films the picker offers, booking fields, how the owner wants alerts (Telegram, email, WhatsApp), the domain, and whether they have footage. Language of the copy (English / 中文 / Bahasa Melayu).

### 2. Start from the template
Copy `assets/scroll-template/` into the project. It runs by opening `index.html` (no build, no network). With no `frames/` folder it draws a procedural placeholder film (dusty car → wash → push-in to badge → light sweep) so the client can scroll a demo on day one. Everything a client changes sits in `window.SITE_CONFIG` in `index.html` and the `:root` tokens in `styles.css`.

### 3. Make the frames (free)
Read `references/frames-pipeline.md`. Order of preference: the shop's own phone footage (tripod, before/after on the same spot) → Blender camera move via `archviz-cinematic` → stock video (`pixabay-assets`). Extract with ffmpeg to WebP, ~90–150 frames, separate desktop and mobile sets. AI video tools are mostly **付费** — ask; `ai-archviz-render` has a free local ComfyUI route. Then set `frames.count` and the story works with real images; captions are `data-at="start-end"` ranges of scroll progress (0–1).

If the client has a licensed glTF model and wants real 3D (any colour from any angle), use the threejs skills instead of frames (`threejs-web`, `threejs-materials`, `threejs-performance`) — heavier on phones; say so.

### 4. Leads and alerts
Read `references/leads-backend.md`: a `leads` table where the browser may only **insert**, a database webhook → Edge Function → Telegram bot or email. Use the repo's `supabase` skill for the setup (ask first). The owner's "dashboard table" is the Supabase Table Editor (or a Google Sheet) — don't build a custom admin unless asked. WhatsApp click-to-chat is a free extra (`whatsapp` in config).

### 5. Accessibility, performance, privacy
Read `references/quality-checklist.md` and go through it before delivery: reduced-motion still view, no scroll-jacking, keyboard-only booking, LCP ≤ 2.5 s, frame weight budget, honeypot/Turnstile, PDPA consent text, privacy note.

### 6. Visual polish (optional, ask first)
Hand the layout to `impeccable` (critique/polish), `animate` or `designer-frontend-design` for type, spacing and motion; `make-interfaces-feel-better` for details. Keep the template's accessibility and performance rules when they change the look.

### 7. Host and hand over
Free static hosting (Cloudflare Pages, GitHub Pages, Netlify). Hand the owner: the URL, how to open the leads table, how alerts arrive, how to change prices/colours, and that a free Supabase project pauses after a week without activity.

## Limits (say them, don't hide them)
- The template was checked with `node --check`, a stubbed-DOM smoke run and an HTML/JS id cross-check; it was **not** opened in a real browser or on a phone when this skill was written. Test on a real iPhone and Android before handing over.
- CSS scroll-driven animations (`animation-timeline`) are not Baseline yet (Firefox stable still behind a flag as of mid-2026, 未验证); the template uses plain JS so it works everywhere. Use the CSS feature only for decorative extras behind `@supports`.
- Frame budgets and quality numbers are community rules of thumb (经验值), not standards.
- Telegram alerts need the owner to press Start on the bot first; SMS alerts cost money (Twilio ~US$0.34 per SMS to Malaysia, 付费, 未验证 exact column).
- Not legal advice: the PDPA text is a sensible minimum for a booking form; a business handling sensitive data needs proper advice.
- Don't copy another shop's footage, logo or site design from a reel; use the client's own material.
