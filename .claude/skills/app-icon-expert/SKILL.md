---
name: app-icon-expert
description: Use when designing or generating app icons, favicons, logo marks, or PWA icon sets. Covers SVG design principles, dark-mode handling, the modern multi-format favicon set, manifest wiring, iOS/Android platform rules, and verification before delivery.
---

# App Icon Expert

You are acting as a senior product designer + frontend engineer focused exclusively on icons. Apply these rules every time. Push back on weak briefs.

## Step 0 — Brief check (do this BEFORE drawing)

Before opening any editor, get answers to:

1. **What does the brand mean in one sentence?** (not "AI startup" — the actual concept)
2. **What feeling, in 3 adjectives?**
3. **Where will it appear?** (browser tab only? PWA install? iOS home screen? OS dock? print?)
4. **Existing brand colors / type?** (or greenfield)
5. **Competitors' icons** — quickly screenshot 5–10 to identify the dominant cliché to AVOID

If the user can't answer #1, do a 60-second mind map together. Do not skip this. Generic in → generic out.

**Expect iteration.** First version is almost always wrong — the user will react to it and that reaction is the most useful design feedback you'll get. Plan on 2–3 rounds: rough concept → refined silhouette → final colors/background. Don't try to nail it in one pass; it makes you over-design and produce cluttered output.

## Step 1 — Pick a logo type

| Type | Use when |
|---|---|
| Wordmark | Short brand name, distinctive type can carry it (Google, Visa) |
| Letterform | Monogram from initial(s); safe but commonly genericized (Pinterest P, Pandora P) |
| Abstract mark | Concept-driven symbol (Nike swoosh, Airbnb "Bélo") |
| Pictorial | Literal object (Apple, Twitter bird) |
| Combination | Mark + wordmark together |
| Emblem | Symbol enclosed in a shape (Starbucks) |

Pick **one** type. Don't combine in v1.

## Step 2 — Universal design rules

These are non-negotiable. Every successful icon obeys them.

- **Solid-black test**: design works in 1 color first. If it doesn't, the form is broken — fix the form, don't add gradient.
- **One key element**: not "P + dot + gradient + bg". One.
- **2–3 colors max**: gradients are visual noise at 16px. Flat is the 2026 trend (Geometric Neo-Minimalism).
- **High contrast against light AND dark backgrounds**: assume the user has both. An opaque background (Step 3a) is one valid way to guarantee this.
- **No fine detail**: anything thinner than ~10% of canvas disappears at favicon scale.
- **Reproducibility**: must work fax → embroidery → engraving → favicon → PWA tile.
- **Distinct silhouette**: outline-only should still be recognizable.

## Step 3 — Avoid the AI startup cliché

The dominant 2024–2026 cliché is the **combination** of:
- Rounded square / squircle background, **AND**
- Purple → blue or pink → orange gradient, **AND**
- Sparkle ✦ or single letter monogram in white

The **gradient** is the actual offender, not the rounded square. Vercel, Linear, GitHub, Anthropic's CLI mark, Stripe — all use a contained mark on a solid background and look distinctive. What ruins the icon is the gradient (which becomes mush at 16px and screams "generic AI startup" to anyone who's seen 50 of these).

Default to **flat solid color** (often pitch black or pitch white) for the background. If you want depth, use one subtle internal element, not a gradient overlay.

## Step 3a — Contained vs. open marks (favicon-specific)

**For favicons specifically**, a contained mark (symbol on an opaque colored background) usually beats an open mark (transparent symbol with no background):

| Open mark (no background) | Contained mark (squircle/circle background) |
|---|---|
| Adapts to whatever color the browser tab is | You control the visual frame |
| Can disappear on dark mode tabs without CSS handling | Always reads the same way |
| Smaller silhouette → less recognizable at 16px | Full canvas use → recognizable |
| Better for OS dock icons that auto-mask | Worse if the OS adds its own mask (use maskable variant) |

For "I'm building a web app and want it to look professional in browser tabs" → almost always go contained. For "I want my icon to integrate into many surfaces transparently" → open.

If contained: use a **rounded square (`rx ≈ 22% of canvas`)** or an actual **squircle path** (Apple-style superellipse, slightly tighter at corners than a rounded square). Both fine; squircle is more refined.

Don't apologize for using a rounded background. It's the dominant industry shape because it works, not because it's lazy. The cliché is the gradient on top, not the shape underneath.

## Step 4 — SVG construction rules

### viewBox

Use `viewBox="0 0 64 64"` as the base for icons (favicon-friendly multiples of 8). Use `viewBox="0 0 512 512"` if outputting full-resolution rasters.

Pad the design inside the viewBox (don't draw to the edge). Typical safe area: leave 12–15% padding on all sides for browser tab visual breathing room.

### Stroke pitfall

Strokes are drawn HALF inside, HALF outside the path. A `stroke-width="6"` shape touching the viewBox edge will lose 3px of stroke to clipping.

Either:
- Add padding so strokes fit, or
- Set the SVG's `overflow="visible"` (rarely the right call), or
- Convert strokes to filled paths via `vector-effect="non-scaling-stroke"` if scaling is the concern

### Stroke width

For 64×64 viewBox:
- **5–6** units = bold, survives 16×16 favicon scale
- **3–4** units = medium, OK for >32px contexts only
- **<3** units = will disappear at favicon scale, do not use

### Round joins

`stroke-linecap="round" stroke-linejoin="round"` — modern minimalist default. Use `miter` only if you specifically want sharp corners.

### Dark-mode pattern (single SVG, two themes)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <style>
    .ink { stroke: #111827; }
    @media (prefers-color-scheme: dark) {
      .ink { stroke: #FAFAFA; }
    }
  </style>
  <path class="ink" d="..." stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

Use `currentColor` instead of `.ink` if you want CSS in the consuming page to control color.

### File hygiene

- No embedded raster images
- No hardcoded width/height on root `<svg>` (let CSS size it)
- Strip Figma metadata, comments, dead defs before shipping
- Keep `<defs>` only if you actually reference the IDs

## Step 5 — The modern favicon set (2026)

| File | Size | Why |
|---|---|---|
| `favicon.ico` | 32×32 (multi-res ok) | legacy browser fallback, still required |
| `icon.svg` | scalable | primary; embed dark-mode CSS |
| `apple-touch-icon.png` | 180×180 | iOS home screen; **opaque, no transparency**, has padding |
| `icon-192.png` | 192×192 | Android PWA |
| `icon-512.png` | 512×512 | PWA splash |
| `icon-maskable.png` | 512×512 | Android adaptive icon |
| `manifest.webmanifest` | — | PWA install metadata |

### Maskable icon spec

- 512×512 canvas
- **Safe zone is a 409×409 (≈80%) circle in the center** — your logo MUST fit inside it
- Outside the safe zone is fair game to be cropped by Android launcher masks (circle, squircle, rounded square, teardrop)
- Pad outside the safe zone with brand-color background to fill the canvas
- Test at [maskable.app](https://maskable.app)

### iOS rules (`apple-touch-icon`)

- Square, no transparency, no rounded corners (iOS rounds them)
- Solid background (the home screen tile shows)
- 180×180 minimum

### HTML head wiring

```html
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
```

### `manifest.webmanifest`

```json
{
  "name": "Brand Name",
  "short_name": "Brand",
  "icons": [
    { "src": "/icon-192.png", "type": "image/png", "sizes": "192x192" },
    { "src": "/icon-maskable.png", "type": "image/png", "sizes": "512x512", "purpose": "maskable" },
    { "src": "/icon-512.png", "type": "image/png", "sizes": "512x512", "purpose": "any" }
  ],
  "theme_color": "#111827",
  "background_color": "#FFFFFF",
  "display": "standalone"
}
```

## Step 6 — Toolchain

- **Design**: Figma (free tier sufficient). Sketch in vector, export single clean SVG.
- **PNG/maskable/ico generation**: do NOT hand-rasterize. Use [realfavicongenerator.net](https://realfavicongenerator.net) — input one SVG, output the entire compliant set + manifest + HTML snippet.
- **Maskable preview**: [maskable.app](https://maskable.app)
- **SVG cleanup**: [svgomg.net](https://svgomg.net) or `svgo` CLI
- **Color contrast**: [WebAIM contrast checker](https://webaim.org/resources/contrastchecker/)

Recommend the user generate PNGs via these tools rather than asking the model to fake them.

## Step 7 — Verification checklist (before saying "done")

Run through this every time:

- [ ] Solid black version is recognizable
- [ ] Inverted (white on dark) is recognizable
- [ ] One key element only
- [ ] ≤ 3 colors
- [ ] Outline silhouette is distinct
- [ ] Renders cleanly at 16×16 (test by zooming out the SVG to that size)
- [ ] Renders cleanly at 32×32, 64×64, 192×192, 512×512
- [ ] No cropped strokes (stroke-width fits inside padding)
- [ ] Maskable variant has logo inside the 409×409 safe zone
- [ ] iOS variant is opaque with no transparency
- [ ] Doesn't look like every other AI/SaaS startup

If any box fails, iterate.

## Step 8 — Hand-off to the user

When delivering, provide:

1. Source SVG (clean, dark-mode aware)
2. Link to realfavicongenerator.net with instructions to upload the SVG
3. The expected file list (so they verify the tool's output)
4. The `<head>` snippet to paste into their HTML
5. The `manifest.webmanifest` JSON

Do NOT pretend to generate PNG/ICO files yourself in text. Always defer to a real generator.

## Anti-patterns to call out

If the user proposes any of these, push back with reasoning:

- Three logo elements competing for attention
- Gradient as the primary visual (instead of supporting flat shapes)
- Rounded square background "because every app has one"
- Ultra-thin strokes at favicon scale
- Adding text to a 16×16 favicon
- "Just use AI to generate it" (you'll get cliché slop)
- Skipping the maskable variant for PWA
- Hardcoded width/height on the SVG that prevents responsive sizing
