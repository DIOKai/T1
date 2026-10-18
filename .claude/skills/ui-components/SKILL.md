---
name: ui-components
description: UI component design patterns and implementation guidance. Use this skill when building common web components like buttons, cards, navigation, forms, hero sections, modals, or any reusable UI element. Trigger whenever the agent is creating HTML/CSS components, needs guidance on component anatomy and states, or wants to ensure components follow professional design standards.
---

# UI Component Design Patterns

## Buttons

### Anatomy

- **Primary**: high contrast, filled background, main CTA color — ONE per section/view
- **Secondary**: outlined or ghost style, lower visual weight
- **Touch target**: minimum 44x44px, ideally 48x48px

### Styling Rules

- Vertical padding < horizontal padding (optical weight: text is wider than tall)
- Typical ratio: `padding: 0.75rem 1.5rem` (2x horizontal)
- Use the single accent/CTA color for primary buttons — users learn "this color = action"
- Action-oriented labels: "Download the guide" not "Submit" or "Click here"
- Tell users exactly what happens when they click

### States

- Default, hover, active/pressed, focused, disabled, loading
- **Hover**: subtle background shift or shadow
- **Focus**: visible outline (keyboard accessibility)
- **Disabled**: reduced opacity (0.5–0.6), `cursor: not-allowed`
- **Loading**: spinner or skeleton, disable clicks during loading

## Cards

- Wrap related content in a container with consistent padding
- Card padding should match or relate to the gap between cards
- Use subtle shadow OR border, not both
- **Shadow**: never pure black — use `rgba(0,0,0,0.1)` or `hsl(0,0%,0%,0.1)`, 30% opacity at most
- Cards can replace tables/lists to make content more engaging and scannable
- Consistent internal spacing: all child elements use the same gap
- **Card backgrounds**: 5–10% lighter/darker than the page background for subtle elevation

## Navigation

### Patterns

- Logo top-left, primary links center or right, login/CTA far right
- Buttons look like buttons, links look like links, icons look like icons
- Magnifying glass = search, cart = checkout — respect universal conventions
- Keep primary actions in the same place across ALL pages

### Mobile Navigation

- Hamburger menu on mobile (users expect it)
- Keep the most critical 2–3 links always visible
- Simple nav: just logo + key links + search (minimize choices)

## Hero Sections

- The first section users see — most visitors never scroll past the fold
- Make it crystal clear and super motivating
- **Include**: headline, subheadline (optional), CTA, and supporting image/visual
- **One column**: simple and direct, great for single messages
- **Two column**: image + text side by side
- Clear value proposition immediately visible

## Forms

- Submit on Enter when a single text input is focused
- Label every input clearly
- Show validation errors inline, next to the field
- Group related fields together
- Use appropriate input types (email, tel, number, date)
- Auto-detect or pre-fill when possible (e.g., zip codes for location)

## Modals / Dialogs

Use the native `<dialog>` element first — it handles focus trapping, backdrop, and Escape
key natively via `.showModal()`. Only reach for custom modal implementations when you need
behavior the native element doesn't support.

- **Focus trap**: keyboard focus stays within the modal (`<dialog>` does this automatically)
- **Close on Escape key** (`<dialog>` does this automatically)
- **Close on backdrop click** (add a click handler on the `::backdrop` or outer element)
- **Return focus** to trigger element on close
- Prevent body scroll while open

## Images

### Selection

- Use images where people look toward key content (gaze direction guides attention)
- Good stock photos: natural expression, good lighting, candid feel
- Avoid staged, generic stock photos

### Technical

- Save as WebP when possible (faster loading, smaller files)
- Target ~300KB max per image
- Use rule of thirds for cropping (subject at 1/3 intersections)
- Always set explicit width and height to prevent layout shift
- Use `loading="lazy"` for below-fold images
- Write descriptive alt text for every image

## Design All States

For every component, design these states:

1. **Empty state**: What does it look like with no data?
2. **Loading state**: Skeleton screens or spinners
3. **Sparse state**: Minimal data, still looks good
4. **Dense state**: Lots of data, still scannable
5. **Error state**: Clear feedback on what went wrong and how to fix it

## Shadows

See `color-systems` for the complete shadow reference. Key rules:
- Never use pure black shadows — use `rgba(0,0,0,0.08)` to `rgba(0,0,0,0.15)`
- Layer two shadows for realism (short tight + longer diffuse)
- Shadows replace borders — use one or the other, rarely both

## Gradients & Depth

- Replace flat solid colors with subtle gradients for depth
- Use blurred background images (10–20px Gaussian blur) instead of solid colors for hero sections
- Subtle noise textures add organic warmth
- Depth cues: lighter elements appear closer, shadow = elevated

## When to Abstract Components

- **Create a reusable component** when you use the same structure 3+ times with only data changes (cards, list items, buttons with variants)
- **Keep it inline** for one-off layouts or sections that won't repeat
- **Small API surface**: a component with 10+ props is too complex — split it or use composition (children/slots) instead
- **Composition over configuration**: prefer passing children/slots over adding props for every variation — `<Card><CardHeader>` beats `<Card headerTitle="..." headerIcon="..." headerAction="...">`
- **Name by purpose**: `<PricingCard>` not `<CardVariant3>`

## See Also

- **`color-systems`** — canonical shadow reference, color tokens, dark/light mode
- **`accessibility`** — component accessibility states, ARIA, keyboard navigation
