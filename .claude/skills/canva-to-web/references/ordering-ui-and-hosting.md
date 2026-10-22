# Ordering UI rules and free hosting

"Rule of thumb" = common practice, not a standard.

## Interaction rules
- **Targets:** WCAG 2.2 SC 2.5.8 minimum is **24×24 CSS px** (with spacing/inline exceptions). Apple's HIG suggests 44×44 pt (HIG page could not be fetched, 未验证 from memory). The template uses ≥ 44 px for everything tappable.
- **Swipe is never the only way:** horizontal scroll-snap gives touch swiping for free; add prev/next buttons and arrow keys on the carousel region. Cards get `aria-roledescription="slide"` and a "2 of 5" label (rule of thumb).
- **Sweetness:** a radio group / segmented control (0/30/50/70/100 %) — one choice, arrow-key navigable for free with native radios.
- **Toppings:** −/+ steppers (≥ 44 px) with the count in `aria-live="polite"`; respect a max per topping.
- **Cart:** bottom sheet; the badge bumps when the count changes (reduced motion: colour change instead).
- **Order complete:** CSS animation < 1.5 s plus a text confirmation in a `role="status"` region, saying clearly it's a demo and nothing was charged.
- **Reduced motion:** `@media (prefers-reduced-motion: reduce)`: override with selectors of equal specificity, written after the defaults; **replace** scale/slide with fades rather than just slowing them. Supported by all browsers since 2020.
- **Sheets:** native `<dialog>` with `showModal()` gives focus trapping, Esc to close and focus return in current browsers.
- **Data from the design is untrusted text:** insert with `textContent`, never `innerHTML`.
- **Copy:** short verbs on buttons ("Add · RM 12.40", "Place order"); empty cart says what to do next. `design:ux-copy` can help (ask first).

## Free static hosting
| Host | Free limits | Notes |
|---|---|---|
| GitHub Pages | site ≤ 1 GB, soft 100 GB/month bandwidth | **forbidden:** "facilitating commercial transactions", passwords, credit cards → demo only |
| Cloudflare Pages | 500 builds/month, 20,000 files/site, **25 MiB per file**, 100 custom domains/project | bandwidth not stated on the limits page |
| Netlify | Free plan capped at 300 credits; bandwidth 20 credits/GB (~15 GB if nothing else is used) | what happens past the cap isn't stated |
| Claude Artifact | one private HTML page, shareable link | inline menu data into the page (no separate fetch) |

Publishing is a public action: ask the user before deploying anywhere, and go through the licence checklist in SKILL.md first.

## Sources
- WCAG 2.5.8: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- GitHub Pages limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Cloudflare Pages limits: https://developers.cloudflare.com/pages/platform/limits/
- Netlify pricing: https://www.netlify.com/pricing/
