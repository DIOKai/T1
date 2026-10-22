# Pre-delivery checklist

## Motion and accessibility
- [ ] `prefers-reduced-motion: reduce` → story is one still image with all captions listed, drawer doesn't slide. WCAG 2.3.3 (AAA) calls scroll-added animation non-essential and lists `prefers-reduced-motion` in CSS (C39) and JS (SCR40) as techniques: https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
- [ ] No scroll-jacking: scroll listener is `passive`, no `preventDefault` on wheel/touch, keyboard (Space, PageDown, arrows) scrolls normally. No smooth-scroll library by default; if the client wants Lenis (MIT, respects reduced motion by default, no CSS scroll-snap: https://github.com/darkroomengineering/lenis), test on iOS.
- [ ] "Skip the animation" link is the first Tab stop and lands on the picker.
- [ ] Canvas has `role="img"` and an `aria-label` describing the story.
- [ ] Picker is a native radio group (arrow keys work), colour names written out, current choice announced (`aria-live`).
- [ ] Booking is a `<dialog>` opened with `showModal()` (focus stays inside, Esc closes); focus returns to the button that opened it; every error is text linked with `aria-describedby`, the first invalid field gets focus.
- [ ] Touch targets ≥ 44 px; text contrast ≥ 4.5:1 on the real frames (captions sit on video — keep the text shadow or a scrim).
- [ ] Captions stay readable at 200 % zoom and 320 px width.

## Performance (Core Web Vitals, 75th percentile: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 — https://web.dev/articles/vitals)
- [ ] First frame preloaded with `fetchpriority="high"` (it's the LCP element); other frames load after.
- [ ] Frame totals within `frames-pipeline.md` budgets; separate mobile set.
- [ ] No layout shift: canvas fills a fixed-size sticky stage.
- [ ] ≤ 2 web fonts, `font-display: swap`, or the system stack.
- [ ] Optional libraries pinned to an exact version (GSAP is free incl. all plugins since the Webflow deal; its licence forbids only no-code visual animation builders that compete with Webflow — fine for client sites: https://gsap.com/pricing/ and licence text mirror https://scancode-licensedb.aboutcode.org/gsap-standard-no-charge-2025.html).
- [ ] CSS `animation-timeline` only for decoration inside `@supports (animation-timeline: view())`, with the visible state as default (not Baseline; Firefox stable still flagged mid-2026, 未验证: https://developer.mozilla.org/en-US/docs/Web/CSS/animation-timeline).
- [ ] Lighthouse mobile run and a real mid-range Android + iPhone scroll test.

## Privacy (Malaysia PDPA — not legal advice)
- [ ] Consent checkbox is unticked by default and says who contacts them, why, how long data is kept, how to ask for deletion.
- [ ] Collect only what the booking needs (no IC number, no address unless mobile service).
- [ ] Privacy note page with the business name and contact. The 2024 amendment (in force in phases through 1 June 2025) adds breach notification, DPO and data portability duties for data controllers: https://insightplus.bakermckenzie.com/bm/data-technology/malaysia-personal-data-protection-amendment-act-2024-to-come-into-force — whether a tiny shop must appoint a DPO depends on the Commissioner's guidelines (未验证; tell the owner to check).
- [ ] No third-party trackers by default → no cookie banner needed. If the client adds analytics/pixels, add consent first.

## Hosting (free)
- Cloudflare Pages: 500 builds/month, 20,000 files, 25 MiB per file (https://developers.cloudflare.com/pages/platform/limits/). GitHub Pages / Netlify also work (limits 未验证).
- Custom domain: the client buys and owns it (付费, their account).

## Hand-over
URL; how to read leads; how alerts arrive; how to edit prices, colours and captions in `index.html`; free-tier pause warning; who to call when the form breaks.
