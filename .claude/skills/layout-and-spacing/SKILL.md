---
name: layout-and-spacing
description: Comprehensive layout and spacing system for web design. Use this skill when building page layouts, structuring sections, setting margins/padding/gaps, or arranging elements on a webpage. Trigger whenever the agent is creating HTML/CSS layouts, working with grids or flexbox, positioning elements, or needs guidance on whitespace and spatial relationships between UI elements.
---

# Layout and Spacing Skill

## Layout Fundamentals

### Think in Boxes
Every element on a webpage is a rectangular box. Understanding parent-child relationships and box nesting is fundamental to layout:
- **Parent container**: Controls how children are positioned (flex, grid, block)
- **Child elements**: Positioned relative to parent rules
- **Nesting depth**: Keep reasonable (avoid 10+ levels)
- **Box model**: Remember margin → border → padding → content

### 12-Column Grid Foundation
Use a 12-column grid system as your foundational structure, but rarely use more than 1-3 columns per section:
- Full width section: 12 columns
- Two-column layout: 6 + 6 columns (or 4 + 8 for asymmetry)
- Three-column layout: 4 + 4 + 4 columns
- Most effective layouts are actually quite simple

### Common Layout Patterns

**One-Column Layouts**
- Simple, direct, great for storytelling
- Perfect for hero sections and CTAs
- Use for mobile-first design
- Example: Hero → Features → CTA → Footer

**Two-Column Layouts**
- Image on one side, text on the other
- Great for features, testimonials, and value props
- Creates visual balance and interest
- Consider alternating image side (left/right) for variety

**Bento Box Layouts**
- Creative grid arrangement with varying cell sizes — visually engaging
- **Caution**: Bento boxes easily confuse users ("where do my eyes go?")
- Whatever has the most priority MUST get the most attention via contrast, color, size, or surrounding white space
- Don't let the cool layout override hierarchy — if the user can't find the focal point in 2 seconds, simplify
- Avoid pure randomness — use a structured grid underneath

## The Three Pillars of Layout

### 1. Focal Point
The center of visual interest on the page (not necessarily the geometric center):
- **Filled/solid elements** draw the eye
- **Rule of thirds positioning**: Place focal point at 1/3 or 2/3 marks horizontally and vertically
- **Intersecting lines**: Guide eyes toward key elements
- **Contrast**: Use color, size, or weight to emphasize
- **Example**: A bold headline intersecting with a striking image creates a natural focal point

### 2. White Space (Negative Space)
Quiet areas that let elements breathe and rest the eye:
- **Not literally white**: Just empty, unoccupied space
- **Like silence in music**: Makes the loud moments impactful
- **Improves readability**: Reduces cognitive load
- **Increases luxury feel**: Generous spacing signals premium quality
- **Refocus attention**: Draws eyes back to focal elements
- **Start with excess**: Reduce spacing only if necessary; adding back is harder than cutting

### 3. Hierarchy
Give priority to important elements:
- **If everything is emphasized, nothing is**: Selective emphasis is key
- **Visual weight order**: Headlines > Subheads > Body copy > Details
- **Size matters**: Larger elements appear more important
- **Color matters**: Saturated colors pop; grays recede
- **Position matters**: Top/left of page perceived as more important (F-pattern reading)
- **Weight matters**: Bold text commands attention

## Spacing System

### Base Spacing Scale
Use a consistent, predictable spacing scale based on powers of 2 or multiples of 4/8.
See `frontend-implementation` for the complete named token table.

**Pixel values:**
```
4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px, 96px, 128px
```

**In rem units (divide by 16px base):**
```
0.25rem, 0.5rem, 0.75rem, 1rem, 1.5rem, 2rem, 3rem, 4rem, 6rem, 8rem
```

### Spacing Principles
- **Start with MORE spacing and reduce**: Tighter spacing literally hurts UX; generous spacing is safer
- **Consistency is #1**: Even "wrong" values look professional if applied consistently throughout
- **Predictability**: Users should intuitively predict where spacing will be used
- **Scale proportionally**: As elements grow, spacing should grow too

## Spacing Relationships (Law of Proximity)

### The Proximity Principle
Elements close together are perceived as related; elements far apart are perceived as separate:
- **Related elements**: Get LESS space between them (1 unit or less)
- **Unrelated elements**: Get MORE space between them (1.5-2 units)
- **Group separation**: Create visual groups by varying spacing

### Inner vs. Outer Spacing
- **Inner spacing (padding)**: Space inside a container
- **Outer spacing (margin/gap)**: Space outside/between containers
- **Rule**: Inner spacing should ALWAYS be smaller than outer spacing
- **Example**: Container padding 1rem, gap between containers 2rem

### The 2x Multiplier
Create rhythm by doubling spacing between hierarchy levels:
- **Heading to body gap**: 1rem (tight, they're related)
- **Body to next heading gap**: 2rem (larger gap, new group)
- **Section to section gap**: 4rem (breathing room between major sections)
- **This creates visual rhythm**: Predictable and professional

### Grouping Strategy
```
Component spacing: < 1rem (elements that belong together)
Section spacing: 1.5rem - 2rem (visually group sections)
Major break spacing: 3rem - 4rem (significant content shift)
```

## Padding Rules

### Vertical vs. Horizontal Padding
- **Vertical padding**: Should be SMALLER than horizontal
- **Why**: Text has more visual noise horizontally; vertical whitespace feels more generous
- **Ratio**: Typically 1:2 to 1:3 (vertical:horizontal)
- **Example**: 1rem vertical, 2rem horizontal on a card

### Button Padding
Buttons should look "clickable" with comfortable touch targets:
```
Desktop: 12px vertical (0.75rem), 24px horizontal (1.5rem)
Mobile: 16px vertical (1rem), 24px horizontal (1.5rem)
Ratio: 1:2 vertical to horizontal
```

### Container Padding Strategy
- **Start generous**: 1.5rem to 2rem, then reduce if cramped
- **Match spacing**: Outer spacing/gap should echo inner padding for visual balance
- **Responsive**: Reduce padding on mobile (1rem on small screens, 2rem on desktop)
- **Cards**: Padding should match gap between cards for cohesion

## Spatial Rhythm

### Spatial Echo (Echo Spacing Across Unrelated Sections)
Create subconscious harmony by deliberately repeating spacing values in unrelated areas:
- If a hero image has 40px bottom margin, use 40px on a quote block three sections down
- If a logo sits 40px from the bottom of a card, use 40px as the track list margin on a separate page
- Double the base value for related-but-different elements: 40px for names → 80px for titles
- The viewer doesn't know what you did, but they *feel* it — the design breathes in tempo
- This is "invisible rhythm": no visible grid lines, just consistent spacing relationships echoed throughout
- **Example architecture** (pick values and stick to them everywhere):
  - Headlines: Always 1.5rem below
  - Feature cards: Always 2rem gap
  - Section breaks: Always 4rem gap
  - Logos/motifs at section bottoms: Always 2.5rem from edge

### Building Rhythm
```
0.5rem - micro spacing (tight pairing)
1rem - primary spacing (related elements)
1.5rem - secondary spacing (element groups)
2rem - tertiary spacing (content sections)
3-4rem - major breaks (distinct sections)
```

## Choosing a Layout Method

### Flexbox vs. Grid

**Use Flexbox when:**
- Layout is one-dimensional (a row OR a column, not both)
- Children should determine their own size (content-driven)
- You need flexible, wrapping arrangements
- Building: nav bars, button groups, icon+text pairs, tag lists

**Use Grid when:**
- Layout is two-dimensional (rows AND columns)
- Parent should dictate structure (design-driven)
- You need precise alignment across both axes
- Building: page layouts, card grids, bento boxes, dashboards

**Default to Flexbox** for component-level layouts. Use Grid for page-level structure.

**Subgrid**: When grid children need to align their internal contents across rows (e.g.,
card titles, descriptions, and buttons all lining up), use `grid-template-rows: subgrid`
on the child. This lets inner elements participate in the parent's grid tracks. Common use
case: a row of cards where all titles, all descriptions, and all CTAs align horizontally
regardless of content length. Supported in all major browsers.

### Key Layout Values

| Pattern | Approach | Key values |
|---------|----------|------------|
| Page container | Centered, max-width | max-width: 1200px, horizontal padding: 1rem mobile / 2rem desktop |
| Auto-reflow grid | Grid with auto-fit | min column width: 300px, gap: 1.5rem |
| Two-column split | Grid or flex | 1fr 1fr (equal) or 2fr 1fr (weighted), gap: 2-3rem |
| Vertical stack | Flex column or flow | gap: 1rem between siblings, 2-3rem between groups |
| Text container | Max-width constraint | 600px or 65ch for body text (50-75 characters per line) |

### Gap vs. Margins
Prefer `gap` for spacing between layout children. Margins create inconsistencies (the last child
still has a trailing margin). Gap is clean, predictable, and works in both Flex and Grid contexts.

## Layout Variation

### Variation with Purpose (Not for Its Own Sake)
Monotonous layouts feel static, but random variation feels chaotic:
- **Mix layout types**: Alternate between 1-column, 2-column, bento — but each shift must serve the content
- **Bad**: 1-col → 2-col → 3-col just to look interesting
- **Good**: 1-col hero (single message) → 2-col features (comparison) → card grid testimonials (social proof)
- **Vary backgrounds**: Solid, gradient, image, color blocks — to signal section boundaries
- **Vary density**: Dense content → breathing room → dense content
- **Vary imagery**: Large hero → small thumbnails → embedded video
- Every layout change should align with what the user expects at that point in the page

### Cognitive Relief Zones
After dense, high-energy content, provide visual rest — the design equivalent of silence in music:
- **Pattern**: Every 3-4 content-heavy sections → 1 low-density relief section
- **Relief zones are NOT just empty white space** — they are intentional calm:
  - Warm gray or muted-tone background block
  - Soft type, generous padding, minimal elements
  - A single testimonial quote with breathing room
  - Large whitespace with a centered single CTA
  - Image-only section without text overlay
- **Styling**: Use warm tones, soft structure, limited contrast (not stark white)
- **Purpose**: Resets the viewer's visual energy so the next loud moment hits harder
- **Think of it like music pacing**: verse → chorus → bridge (rest) → chorus (impact)

### Alternating Columns Example
A typical engaging page flow:
1. **Section 1** — Two-column: text left, image right (2-3rem gap, vertically centered)
2. **Section 2** — Two-column reversed: image left, text right (same gap, mirrored)
3. **Section 3** — Single-column testimonial: centered, max-width 800px, generous vertical padding
4. **Section 4** — Card grid: 3 columns on desktop, auto-reflow to 1 on mobile

The variation keeps users scrolling. Each shift in layout serves a content purpose.

## Balance

### Balance ≠ Symmetry
Balance means visual equilibrium, not mirror symmetry:
- **Visual weight**: Text, images, colors, whitespace all have weight
- **Asymmetrical balance**: Heavy on one side, light on other with different element types
- **Dynamic feel**: Asymmetrical layouts feel more modern and interesting
- **Still stable**: Avoid tilting sensation by carefully distributing weight

### Asymmetrical Balance Examples

**Diagonal Balance:**
- Heavy text (top-left) balanced by striking image (bottom-right)
- Creates dynamic tension while feeling stable
- Natural eye movement along diagonal

**Contrast Balance:**
- Large block of color on one side
- Multiple smaller elements on other side
- Different element types can balance each other despite size differences

**Weight Distribution:**
- Bold, dark element on left
- Delicate, light element on right
- They feel balanced despite different visual weights

## Quick Reference Checklist

When building a layout, verify:
- [ ] Clear focal point established (not just centered)
- [ ] Adequate white space between major elements
- [ ] Clear visual hierarchy (headlines > subheads > body > details)
- [ ] Spacing is consistent with defined scale (base-4 or base-8)
- [ ] Related elements have tight spacing, unrelated elements have generous spacing
- [ ] 2x multiplier rule applied (next heading gap is 2x body-heading gap)
- [ ] Padding is proportional (vertical < horizontal)
- [ ] Gap used instead of margins for layout children
- [ ] Text max-width set (600px or 65ch for body text)
- [ ] Layouts vary across page (1-col, 2-col, bento mix)
- [ ] Breathing zones included after dense sections
- [ ] Layout feels balanced (not necessarily symmetrical)
- [ ] Spacing tokens used for consistency
- [ ] Responsive breakpoints tested
