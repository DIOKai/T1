# Phone design that doesn't look third-rate

Players compare every FiveM phone with the phone in their pocket, so "almost like a phone" reads as cheap. The fastest way to look premium is to **use the real platforms' numbers** instead of inventing sizes, then adapt them to FiveM's differences: the player uses a **mouse and keyboard**, the phone sits over a moving game scene, and it shares the GPU with the game.

Every number below marked ✔ was checked against a primary source: Apple HIG data files (accessibility, typography, sheets, tab bars, dark mode, motion), or Material 3 token files in androidx (`compose/material3/.../tokens`: AppBarSmall, FabBaseline, List, NavigationBar, TypeScale, Shape, Motion, SheetBottom), or the Android docs. Numbers marked ≈ are rules of thumb: tune them in game.

Pair with (ask first): `mobile-ios-design`, `mobile-android-design`, `apple-design`, `make-interfaces-feel-better`, `emil-design-eng`, `impeccable`. The template in `assets/phone-template/` already applies everything here. Start from it.

## 1. Scale system: design in phone points

Design on a **390 × 844 pt** canvas (the logical size of a 6.1" iPhone) and scale the whole phone with one variable, so every HIG/Material number can be used directly:

```css
:root {
  --phone-scale: 0.8;                    /* player setting, 0.65–0.9 */
  --phone-h: calc(var(--phone-scale) * 100vh);  /* ≈ 864px at 1080p, 576px at 720p, 1728px at 4K */
  --pt: calc(var(--phone-h) / 844);      /* 1 design point */
}
.phone   { height: var(--phone-h); aspect-ratio: 390 / 844; }
.row     { min-height: calc(44 * var(--pt)); }
.body    { font-size: calc(17 * var(--pt)); line-height: calc(22 * var(--pt)); }
```
Why: the phone stays proportional from 720p to 4K, and a "44pt row" really is 44pt on the virtual phone. At 720p the phone is ~576 px tall, so 1 pt ≈ 0.68 px. Check that body text (17 pt ≈ 11.6 px) stays readable there. If it doesn't, raise `--phone-scale` at small heights with a media query instead of shrinking type, and give players a phone-size setting (saved with KVP).

For Android-style phones use the same variable and read dp as pt (Material's 1 dp and Apple's 1 pt are both ~1/160 inch logical units).

## 2. The numbers

| | iOS-style ✔ | Material 3 ✔ |
|---|---|---|
| min hit target | 44 × 44 pt (HIG default control size; absolute minimum 28 × 28) | 48 × 48 dp |
| top bar | large title 34 pt bold on the first screen of an app; small title deeper in (17 pt semibold) | small top app bar 64 dp |
| bottom navigation | tab bar, single-word labels, prefer ≤ 5 tabs | navigation bar 64 dp (80 dp tall variant) |
| list rows | grouped/inset style for settings-like lists; row ≥ 44 pt | one-line 56, two-line 72, three-line 88 dp |
| primary action | button in the nav bar, or a prominent button in content | FAB 56 dp, corner 16 dp |
| sheets | `medium` (≈ half) and `large` detents, grabber on resizable sheets | bottom sheet with 28 dp top corners |
| corner radii | ≈ cards 10–16 pt, buttons 8–12 pt or capsule | small 8, medium 12, large 16, extra-large 28 dp, full |
| contrast | ≥ 4.5:1, aim for 7:1 for small custom-coloured text | same WCAG basis |

**Type ramps (default size / line height)**
- iOS ✔ (Large/default Dynamic Type): Large Title 34/41, Title 1 28/34, Title 2 22/28, Title 3 20/25, Headline 17/22 semibold, Body 17/22, Callout 16/21, Subhead 15/20, Footnote 13/18, Caption 1 12/16, Caption 2 11/13.
- Material ✔: Display S 36/44, Headline S 24/32, Title L 22/28, Title M 16/24, Body L 16/24, Body M 14/20, Body S 12/16, Label L 14/20, Label M 12/16.

Use one ramp per phone. Mixing iOS and Material sizes is a classic cheap look.

## 3. Navigation rules worth following (HIG ✔)

- The tab bar is for **navigation, not actions**. Keep it visible on every top-level section. Don't hide or disable tabs. If a section is empty, show the tab and explain why it's empty.
- Badges only for **critical** new information (unread messages, an incoming payment), not for promotion.
- Sheets: a medium detent for quick tasks (share, pick amount), large or full for composing. Add a grabber when it can be resized.
- Dark mode uses two background levels: **base** (dimmer, recedes) and **elevated** (brighter, comes forward), e.g. a sheet over a list. That gives depth without shadows.

## 4. Motion (verified tokens, FiveM-safe)

Animate only `transform` and `opacity`. Nothing moves while idle.

**Material 3 ✔ durations:** short 50/100/150/200 ms, medium 250/300/350/400 ms, long 450–600 ms. **Easing:** emphasized `cubic-bezier(0.2, 0, 0, 1)`, emphasized-decelerate `cubic-bezier(0.05, 0.7, 0.1, 1)` (enter), emphasized-accelerate `cubic-bezier(0.3, 0, 0.8, 0.15)` (exit), standard/legacy `cubic-bezier(0.4, 0, 0.2, 1)`.

**Apple-style springs** (`apple-design`: default damping 1.0, response 0.3–0.4 s; sheets/drawers damping 0.8, response 0.3 s). The CSS `linear()` curves below were computed from the spring equation (ω = 2π / response) and sampled at 25 points. Use the duration shown (time to settle within 0.1 %):

```css
:root {
  /* damping 1.0, response 0.35 s → 514 ms. Default: app open/close, push/back */
  --spring: linear(0, 0.057, 0.18, 0.32, 0.455, 0.573, 0.671, 0.75, 0.812, 0.86, 0.896, 0.924,
    0.944, 0.96, 0.971, 0.979, 0.985, 0.989, 0.992, 0.994, 0.996, 0.997, 0.998, 0.999, 1);
  --spring-dur: 514ms;
  /* damping 0.8, response 0.3 s → 404 ms. Sheets, drawers, fold/unfold: a 1.5 % overshoot */
  --spring-soft: linear(0, 0.051, 0.17, 0.315, 0.462, 0.597, 0.711, 0.803, 0.874, 0.926, 0.963,
    0.987, 1.002, 1.011, 1.014, 1.015, 1.014, 1.012, 1.01, 1.008, 1.006, 1.004, 1.003, 1.002, 1);
  --spring-soft-dur: 404ms;
}
@media (prefers-reduced-motion: reduce) { :root { --spring-dur: 1ms; --spring-soft-dur: 1ms; } }
```
`linear()` needs Chromium 113+. FiveM's CEF is newer than that, but that is unverified: test once. The fallback is `cubic-bezier(0.2, 0, 0, 1)` at 350 ms.

Patterns:
- **Open app:** scale from the icon's rectangle (`transform-origin` at the icon) 0.6 → 1 with opacity, `--spring`. Close: back into the same icon (spatial consistency).
- **Push / back:** the new screen slides in from 100 % → 0 while the old one shifts −30 % and dims slightly.
- **Interruptible:** CSS transitions (not keyframe animations) re-target from the current value when the class flips mid-way, so use transitions for anything the player can toggle quickly (open/close, fold).
- Feedback on press: `:active { transform: scale(0.97) }`, 100 ms. It feels responsive without any JS.

## 5. Glass and blur inside a FiveM phone

`apple-design` builds bars and sheets from translucent material (`backdrop-filter: blur(20px) saturate(180%)`). In FiveM, blur that sits over the **game** re-blurs every game frame, so never do that. Blur **inside** the phone only re-renders when the phone content behind it changes. So:
- blur only small chrome (status bar, tab bar, sheet header) over **phone content**, never over the game;
- or fake it: a pre-blurred copy of the wallpaper as the bar background (zero runtime cost);
- never stack translucent layers on each other (HIG/apple-design: legibility collapses);
- over translucent surfaces, use slightly heavier text weight and higher contrast.

## 6. What separates premium from third-rate (checklist)

- One type ramp, one corner-radius family, one accent colour, a 4/8-pt spacing grid ≈.
- **Numbers:** `font-variant-numeric: tabular-nums` for money, times and phone numbers. Use currency formatting with grouping (`Intl.NumberFormat`), and show negative amounts in red with a sign, not colour alone.
- **Real states:** an empty state with an icon, one line of text and an action. Skeleton rows while loading (not spinners everywhere). Inline errors with a retry.
- **Hierarchy:** one primary action per screen. Secondary text at ~60 % contrast, not a random grey.
- **Optical details:** icons aligned to the text's cap height. A 1 px hairline at 50 % alpha instead of heavy borders. Content padding 16 pt (iOS) / 16 dp (Material) ≈.
- **Status bar:** the in-game clock, cosmetic signal/battery, and keeping out of the notch/Dynamic Island area (≈ 54 pt top safe area on current iPhones, ≈ 34 pt home-indicator area at the bottom; unverified for exact models).
- **Copy:** short, specific labels ("转账", "已到账 $2,500"), in-universe app names instead of real trademarks.
- **Sound:** soft UI clicks via `PlaySoundFrontend` only if the server already uses them.

## 7. Input in FiveM

- Mouse first: the wheel scrolls, everything is clickable. Drag/swipe is an extra, never the only way.
- Keyboard: ESC closes the phone. Backspace goes back one screen, **except while typing**. Enter sends.
- Hover states matter (desktop users hover): a subtle background change on rows (+4 % white in dark mode).
- With `SetNuiFocusKeepInput`, turn keep-input off while a text field has focus (`phone-frame.md`).

## 8. Fonts and icons (free, bundled)

- SF Pro and other Apple fonts are licensed for Apple platforms only, so don't bundle them. Free look-alikes: **Inter** (OFL) for iOS-style, **Roboto / Roboto Flex** (OFL/Apache) for Material-style.
- Icons: Lucide (ISC; npwd v4 provides `lucide-react`), Phosphor (MIT), Material Symbols (Apache 2.0), Font Awesome Free. Download them into the resource; no CDN.

## 9. Self-review before calling it done

Screenshot the phone at 1280×720, 1920×1080 and 2560×1440 (headless Chromium is enough) and check:
- Same proportions at every size? Body text readable at 720p?
- Every tap target ≥ 44 pt? One type ramp? Tabular numbers on money?
- Empty, loading and error states exist for every list?
- Light and dark both ≥ 4.5:1? Nothing animating while idle?
- Would the screen pass for a real app screenshot at a glance? If not, compare it side by side with the matching iOS/Material screen and fix the biggest difference first.
