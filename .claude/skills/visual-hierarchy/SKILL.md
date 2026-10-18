---
name: visual-hierarchy
description: Visual hierarchy principles for guiding user attention in web interfaces. Use this skill when deciding what to emphasize or de-emphasize on a page, structuring content importance, designing hero sections, or making layout decisions about size, weight, color, and positioning of elements. Trigger whenever the agent needs to create clear information flow, design scannable pages, or ensure users see the right things in the right order.
---

# Visual Hierarchy

## What Visual Hierarchy Is

Visual hierarchy is the arrangement of elements to show their order of importance. It guides the user's eye through content in a deliberate sequence, ensuring that without hierarchy, everything competes for attention and nothing wins. Think of it like a music mix: lead vocals in front, rhythm in the middle, bass in the back.

## The Three Levels of Importance

### 1. Primary / Large
The biggest, boldest elements — headlines, hero images, main CTAs. The thing users see first and should understand instantly.

### 2. Secondary / Medium
Supporting content — subheadings, feature descriptions, secondary buttons. Easy to find and scan but doesn't compete with primary elements.

### 3. Tertiary / Small
Background details — metadata, timestamps, fine print, footnotes. Available for those who want it, but visually quiet.

## Tools for Creating Hierarchy

### Size
- Larger = more important (the brain processes size first)
- Headlines should be noticeably larger than body text
- Use size differences that are clearly distinct — subtle size variations look like mistakes

### Weight
- Bolder = more important
- Use weight variation even at the same font size to create hierarchy
- Combining size + weight creates strong emphasis without needing more colors

### Color and Contrast
- High contrast = important (dark on light, or bright accent on neutrals)
- Low contrast = de-emphasized (gray text, muted tones)
- A single bold color in a sea of neutrals creates instant focus
- Reduce secondary text to ~60% lightness to push it to the background (see `color-systems` for the de-emphasis sweet spot)
- The most important elements get the highest contrast

### Position
- Top-left is where Western readers start (Z-pattern / F-pattern scanning)
- Above the fold = highest priority real estate
- Focal point doesn't have to be the center — use rule of thirds
- Elements at intersecting thirds naturally draw the eye

### Spacing and White Space
- More space around an element = more importance
- Crowded elements lose hierarchy — they all compete
- Generous white space frames and elevates what's inside it

## The Emphasis/De-emphasis Principle

To make something stand out, often the best move is to de-emphasize everything around it. Don't just increase size/weight of important elements — reduce contrast/weight/size of secondary elements. Emphasis is relative: an element only stands out in contrast to its neighbors.

## Scanability

Users scan, they don't read (especially above the fold). Create clear "landmarks" for the scanning eye: large headline, bold CTA, images with people. People skim for the first reasonable option, not the best option. Make the obvious choice the most prominent one.

## Visual Hierarchy in Practice

### Hero Sections
- Headline: largest, boldest, highest contrast
- Subheadline: smaller, lighter weight, lower contrast
- CTA button: distinct color, clear action text
- Supporting image: complements, doesn't compete with text

### Card Layouts
- Title: bold, larger or heavier weight
- Description: regular weight, lighter color
- Metadata: smallest, lightest (date, category, author)
- CTA: clear button or link, stands apart from text

### Navigation
- Active state: highlighted with background color, weight change, or underline
- Other items: neutral, lower contrast
- Never let navigation compete with main content

## Variation and Rhythm

Alternate between heavy and light sections to maintain interest. After a dense, information-heavy section, include a "relief zone" (light section, soft tones, minimal content). Visual rhythm keeps users scrolling — monotonous layouts make them leave. Like music: contrast between loud and quiet sections creates engagement.

## Balance

Balance ≠ symmetry. Diagonal balance, asymmetrical weight distribution, and intentional tension all work. If a layout feels like it's "tipping" to one side, redistribute visual weight. A large image bottom-right can be balanced by a bold headline top-left.

## Visual Compression

On shrinking screens and shorter attention spans, the ability to compress meaning into
minimal forms is critical. Think in layers:

1. **Core message**: What's the single idea? Strip everything else.
2. **Supporting shape/color**: Can a shape or color add meaning without more words?
3. **Text/tone**: Only add text for what visuals alone can't carry.

Ask: "Can a supporting shape or color add meaning without more clutter? Can text or tone
carry what visuals don't?" This skill makes designs more iconic, adaptable, and memorable.
It's the difference between a busy feature list and a single compelling visual that says the
same thing.

## Inverted Hierarchy (Advanced)

Occasionally break the rules on purpose: make the fine print huge, the headline small.
Like dropping a whisper in the middle of a loud song — the audience stops and takes notice.

- Example: A music festival poster where "18+ only" is set big, bold, dead center instead of
  tiny at the bottom. The act name becomes the small supporting text.
- Creates tension by breaking the natural reading order
- Only use when the brief allows and the context is creative/editorial
- Must feel deliberate, not accidental — if it looks like a mistake, it IS a mistake

## See Also

- **`color-systems`** — color contrast for emphasis, the 60% de-emphasis rule, lightness inversion formula
- **`typography`** — creating hierarchy through font size, weight, and color
- **`layout-and-spacing`** — spatial hierarchy, white space, focal points
