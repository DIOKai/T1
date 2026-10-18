---
name: internationalization
description: Designing web interfaces that work across languages, scripts, and cultures. Use this skill when building a site that may need to support multiple languages, right-to-left scripts, or international audiences. Trigger whenever the agent is making decisions about text layout, date/number formatting, content expansion, or any design that needs to work beyond a single language or locale. This skill covers design principles, not specific i18n libraries.
---

# Internationalization

## Core Principle

Internationalization is designing so that localization is possible without redesigning.
It's not about translation files or library choice — it's about building layouts, components,
and content patterns that don't break when the language changes. A well-internationalized
design works in English, Arabic, Japanese, and German without structural changes.

## Text Expansion

Translated text is almost never the same length as the source. Design for this from the start:

| Source length | Typical expansion |
|---------------|-------------------|
| 1-10 characters | 200-300% (buttons, labels) |
| 11-20 characters | 150-200% |
| 21-70 characters | 130-150% |
| 70+ characters | 120-130% |

### Design Implications

- **Never fix widths on text containers** — use `min-width` + flexible growth instead
- **Buttons**: size by padding, not fixed width. A "Save" button that fits in English needs to fit "Speichern" (German) or "Enregistrer" (French)
- **Navigation**: plan for labels that are 50-100% longer. Horizontal nav that fits 5 English words may not fit 5 German words — ensure it wraps or truncates gracefully
- **Tables**: column widths should be flexible, not pixel-fixed
- **Truncation**: use `text-overflow: ellipsis` as a safety net, not a design choice — if you're truncating frequently, the layout needs more room
- **Test with long strings**: paste "Geschwindigkeitsbegrenzung" into every text field and label during development to catch overflow issues early

## Right-to-Left (RTL) Layout

Arabic, Hebrew, Farsi, and Urdu read right-to-left. This mirrors the entire layout, not just the text:

### What Flips

- **Reading direction**: text flows right-to-left
- **Layout direction**: sidebars, navigation, content order — everything mirrors
- **Icons with direction**: arrows, progress bars, "forward/back" icons flip
- **Margin/padding asymmetry**: `margin-left: 1rem` becomes `margin-right: 1rem`

### What Does NOT Flip

- **Phone numbers, code, URLs**: always left-to-right
- **Logos and brand marks**: stay in their original orientation
- **Media controls**: play/pause buttons follow universal conventions (play points right everywhere)
- **Clocks and calendars**: time flows left-to-right universally
- **Icons without direction**: checkmarks, stars, settings gear — no flip needed

### CSS for RTL

- Use **logical properties** instead of physical ones — this is the single most important habit:
  - `margin-inline-start` instead of `margin-left`
  - `padding-inline-end` instead of `padding-right`
  - `inset-inline-start` instead of `left`
  - `border-inline-end` instead of `border-right`
- Set `dir="rtl"` on `<html>` (or per-section for mixed content)
- Flexbox and Grid respect `direction` automatically — `justify-content: flex-start` moves to the right in RTL
- **Test by adding `dir="rtl"` to your `<html>` tag** — if the layout breaks, you're using physical properties somewhere

## Number, Date, and Currency Formatting

Formats vary dramatically by locale — never hardcode these:

| Format | US English | German | Japanese | Arabic |
|--------|-----------|--------|----------|--------|
| Number | 1,234.56 | 1.234,56 | 1,234.56 | ١٬٢٣٤٫٥٦ |
| Date | 04/14/2026 | 14.04.2026 | 2026/04/14 | ١٤/٠٤/٢٠٢٦ |
| Currency | $1,234 | 1.234 € | ¥1,234 | ١٬٢٣٤ ر.س |

### Design Implications

- **Don't assume date format** — "04/05/2026" is April 5th in the US and May 4th in most of Europe
- **Currency symbols vary in position** — some before the number ($100), some after (100 €), some with spaces
- **Number grouping separators differ** — comma vs period vs thin space
- **Don't bake formatted values into designs** — always use the platform's locale-aware formatting APIs (Intl.NumberFormat, Intl.DateTimeFormat)
- **Calendar start day** — some locales start the week on Sunday, others on Monday

## Typography Across Scripts

Different writing systems have different typographic needs:

- **CJK (Chinese, Japanese, Korean)**: no spaces between words, different line-breaking rules (can break mid-word at any character), typically need more line height (1.6-1.8x)
- **Arabic/Hebrew**: connected cursive scripts — letter forms change based on position in the word. Font selection is critical; not all fonts support proper ligatures
- **Devanagari, Thai, Burmese**: complex scripts with stacking diacritics — need extra line height to avoid clipping
- **Latin extended**: accented characters (Ö, ñ, ç, ą) must not clip against line boxes or container edges

### Font Considerations

- System fonts handle most scripts well — prefer them over custom fonts for body text in multilingual sites
- If using custom fonts, ensure they include the character ranges you need (or subset per locale)
- Font loading strategy: load Latin subset immediately, load other scripts on demand
- Some scripts render poorly at small sizes — test your minimum font size in all target scripts

## Content and Copy

- **Avoid concatenating strings** in code ("You have " + count + " items") — word order varies by language and this pattern is untranslatable
- **Don't embed text in images** — it can't be translated. Use text overlays with CSS instead
- **Avoid idioms and cultural references** in UI text — "home run," "ballpark figure," "piece of cake" don't translate
- **Pluralization rules vary wildly** — English has 2 forms (1 item, 2 items), Arabic has 6, some languages have none. Use locale-aware plural rules, not `count === 1 ? "item" : "items"`
- **Icon meaning varies by culture** — a mailbox, a thumbs-up, or a hand gesture may mean different things. Prefer universal symbols (magnifying glass for search, gear for settings)

## Color and Cultural Sensitivity

- **Color meaning varies by culture**: red means luck/prosperity in China, danger/stop in the West, mourning in South Africa
- **Don't rely on color alone** to communicate meaning (this is also an accessibility requirement)
- For global audiences, pair color with icons, labels, or patterns as secondary cues
- **Images with people**: ensure representation across demographics for global products. Avoid imagery that's culturally specific unless intentional

## Layout Considerations

- **Leave room for UI growth**: translated UIs are almost always larger than the source
- **Responsive design helps**: flexible layouts that reflow for screen size also handle text expansion well
- **Fixed-height containers are dangerous**: a 3-line English paragraph may be 5 lines in Finnish
- **Form labels**: place labels above inputs (not beside) — this handles text expansion and works for both LTR and RTL
- **Error messages**: allow generous space — translated error messages can be significantly longer

## Testing Checklist

- [ ] Add `dir="rtl"` to `<html>` — does the layout mirror correctly?
- [ ] Replace all visible text with strings 50% longer — does anything overflow or truncate badly?
- [ ] Check number and date formatting with a non-US locale
- [ ] Verify no text is embedded in images
- [ ] Test with a CJK font — do line heights and containers accommodate taller characters?
- [ ] Check for hardcoded concatenated strings in the codebase
- [ ] Verify buttons and navigation handle longer labels without breaking

## See Also

- **`typography`** — font selection, line height, and text width (foundation for multilingual type)
- **`responsive-design`** — flexible layouts that handle text expansion
- **`accessibility`** — language attributes, semantic HTML, color-independent communication
