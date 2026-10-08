# Making a FiveM phone feel like a real phone

Players compare every FiveM phone with the one in their pocket, so platform conventions matter more here than in other menus. The differences: it's used with a **mouse and keyboard**, it sits over a moving game scene, and it shares the GPU with the game.

Pair with (ask first): `mobile-ios-design` (Human Interface Guidelines: navigation, lists, sheets, tab bars; its SwiftUI code is a reference, not something to copy), `mobile-android-design` (Material 3: theming, navigation bar/rail, list items, adaptive layouts), `apple-design` (springs, interruptible motion, materials, typography), `make-interfaces-feel-better` / `emil-design-eng` (details), `impeccable` (audit/critique/polish), `ui-ux-pro-max` (palettes, fonts with licences).

## Pick a look and stick to it

| Style | Feels like | Key traits |
|---|---|---|
| iOS-like | iPhone | large bold titles, inset grouped lists, bottom tab bar, translucent bars, SF-like type, sheets from the bottom, home indicator |
| Android/Material-like | Pixel/Samsung | top app bar, navigation bar with pill indicator, dynamic colour from wallpaper, FAB for the main action, Roboto-like type |
| GTA-like | in-game phones | bold flat colours, chunky icons, in-universe app names, playful |

Mixing styles inside one phone looks cheap. Third-party apps (npwd, lb-phone) should follow the **host phone's** style and theme tokens.

## Structure of an app screen

- **Header**: title, back (`‹`), at most 1–2 actions. Large title on the top screen of an app, small title deeper in.
- **Content**: one task per screen. Lists with clear rows (icon/avatar, title, secondary line, trailing value or chevron).
- **Bottom tab bar** for 3–5 top-level sections. More than 5 → rethink, or use a "More" tab.
- **Primary action**: a FAB (Android-like) or a header button (iOS-like). Destructive actions are last, red, and confirmed.
- **Sheets** from the bottom for quick choices (amount, confirm, share). Avoid full-screen dialogs for small decisions.
- **Empty, loading and error states** for every list (no messages yet, loading skeleton, "couldn't reach server, retry").

## Sizes (translated to rem, root ≈ 1.6vh)

- Hit targets: iOS 44pt / Android 48dp. On a FiveM phone that is ≈ **2.75–3rem** rows and buttons, even though players click with a mouse. The phone is small on a 1080p screen.
- Body text ≥ ~0.9rem, secondary ≥ 0.78rem, titles 1.6–2rem. Check at 1280×720.
- Safe areas: keep content clear of the notch/punch-hole and the home indicator (padding top ≈ status bar height, bottom ≈ 1.5rem).
- Consistent corner radii: the frame ≈ 3rem, cards ≈ 1–1.25rem, buttons ≈ 0.75rem or full pill.
- Home grid: 4 columns, icon ≈ 3.5rem, label below at ~0.7rem, a dock of 4.

## Input in FiveM

- Mouse first: wheel scrolls lists, click everything. Drag-to-scroll and swipe are optional extras, never the only way.
- Keyboard: ESC closes the phone; Backspace goes back one screen **except while typing**; Enter sends in chats.
- With `SetNuiFocusKeepInput`, switch keep-input off while a text field has focus (`phone-frame.md`).

## Motion (keep it short, transform/opacity only)

- Open an app: scale from the icon's position (0.85 → 1) + fade, ~250–320 ms ease-out. Close: reverse toward the icon (spatial consistency, `apple-design`).
- Push/back inside an app: slide 20–30% + fade, ~220 ms.
- Sheets: slide up 250 ms. Toasts/notifications: slide down from the status bar.
- No idle animation (pulsing badges, animated wallpapers). They keep CEF repainting at up to 240 fps (`fivem-menu-design` rules).
- CSS springs: the `linear()` easing function can approximate a spring without a JS library (Chromium supports it; check FiveM's CEF once, unverified).

## Theme and colour

- Light and dark themes, following the host phone's setting (lb-phone `getSettings().display.theme`, npwd theme tokens). Dark is the safer default at night in game.
- One accent colour (the server's brand, or per-app accent on the icon only).
- Wallpaper: dim it behind the home grid for icon contrast. Text contrast ≥ 4.5:1.

## Fonts and icons (free, bundled)

- SF Pro and other Apple fonts are licensed for Apple platforms only. **Don't bundle them.** Free look-alikes: Inter (OFL), and Roboto / Roboto Flex (OFL/Apache) for an Android look.
- Icons: Lucide (ISC, npwd v4 ships `lucide-react`), Phosphor (MIT), Font Awesome Free (qb-phone uses it). Download into the resource; no CDN.

## In-universe flavour

Use GTA-world app names and brands instead of real trademarks (the game's own parodies, or the server's own names): a "Chat" app instead of "WhatsApp", "Birdy" instead of "Twitter/X". It fits the role-play and avoids trademark trouble. qb-phone's stock names ("Whatsapp", "Twitter") are worth renaming in a fork.

## Quick self-review

- Would a player understand every screen without instructions? Is back always in the same place?
- Readable at 720p, usable with mouse only and with keyboard only? ESC/Backspace correct?
- Does it follow the host phone's theme in light and dark?
- Nothing animating while idle? FPS the same with the phone open and closed?
- Foldable: does folding/unfolding keep the place (`foldable.md`)?
