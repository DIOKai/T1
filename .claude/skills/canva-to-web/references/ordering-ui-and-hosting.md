# Ordering UI rules (how the template behaves and why)

"Rule of thumb" = common practice, not a standard. Restyle freely; keep these behaviours.

- **Targets ≥ 44 px.** WCAG 2.2 SC 2.5.8 minimum is 24×24 CSS px; Apple suggests 44 pt. `flow.js` checks every visible button is ≥ 44 px at 320 px wide.
- **No horizontal page scroll at 320 px.** Only the "Popular" row and category tabs scroll sideways, and both are also reachable by Tab.
- **Swiping is never the only way:** the Popular row is native scroll-snap; every item is also in the list below.
- **Single-choice options** (size, sweetness, milk) are native radio buttons styled as segments: arrow keys work, and the default is pre-selected so a customer can add a drink in one tap.
- **Multi-choice toppings** use −/+ steppers with the count in `aria-live`; per-topping `max` and group `max_total` disable the + button instead of showing an error afterwards.
- **Price on the button** ("Add to order · RM 26.80", "Place order · RM 52.70") updates live; the cart lists subtotal, service charge, SST and total separately so nothing is a surprise.
- **Sheets** are native `<dialog>` with `showModal()` (focus trap, Esc, focus return). Tapping the backdrop closes.
- **Errors say what to do:** sold out while in the cart → menu reloads, the line turns red, "Place order" stays disabled until it's removed. All server error codes map to `err_*` texts in three languages.
- **Confirmation page** has a big order number, the table or pickup time, a 4-step status that refreshes itself, and payment instructions (exact amount; 5-sen cash total only when different).
- **Text from the menu or customers is untrusted:** inserted with `textContent` only. The one `innerHTML` is the QR library's SVG of the shop's own URL.
- **Reduced motion:** all animations collapse to instant under `prefers-reduced-motion: reduce`.
- **Dark mode** via `prefers-color-scheme`; colours are tokens in `:root` of `styles.css`.
- **No external scripts or fonts** are loaded (the QR library is vendored), so the CSP in `_headers` can be strict and the page works on slow mobile data. If adding a Google Font, also allow it in the CSP.

## Polishing (ask first, per T1 rules)
`impeccable` (critique/polish), `animate` (motion), `mobile-ios-design` (iOS-like sheets), `design:ux-copy` (button and error wording), `break-ui` (extreme data: 40-character drink names, 30 lines, Malay text length).

## Hosting
See `backend-setup.md` §5. GitHub Pages forbids commerce, so it's only for the demo. A private Claude Artifact link is fine for showing the owner a demo (inline the menu JSON; artifacts can't fetch sibling files).

## Sources
- WCAG 2.5.8: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- prefers-reduced-motion: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- dialog: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog
