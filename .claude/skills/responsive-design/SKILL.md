---
name: responsive-design
description: Responsive web design patterns and implementation guide. Use this skill when building layouts that need to work across screen sizes, implementing media queries, choosing between flexbox and grid, or making any design decisions about how a website adapts from mobile to desktop. Trigger whenever the agent is building responsive pages, components that need to reflow, or any layout that must work on phones, tablets, and desktops.
---

# Responsive Design

## Core Mental Model
- Everything on a website is a box inside a box
- Responsive design = dynamically moving boxes into different rows and columns based on screen width
- Think parent-child relationships: parent controls layout, children hold content
- Before writing HTML, sketch a family tree: define parent-child relationships at each breakpoint

## Flexbox Essentials
- Wrap children so they flow to the next line when space runs out
- Set a minimum width (basis) on children for predictable wrapping — e.g., 300px basis means items won't shrink below 300px before wrapping
- `grow, shrink, basis` — the three flex controls: (1) should it stretch to fill? (2) should it compress? (3) what's its ideal size?
- Distribute children evenly with space-between, or use gap for fixed spacing

## Grid Essentials
- `auto-fit` + `minmax(300px, 1fr)` = responsive columns without ANY breakpoints
- `fr` = fraction unit (proportional sizing)
- Grid is ideal for card layouts: equal-width columns that auto-reflow
- Set a gap of 1-2rem between grid items

## Container Queries

Container queries (`@container`) let components respond to their parent's size instead of
the viewport. Use them for truly reusable components that live in different layout contexts:

- **Media queries**: respond to the viewport — use for page-level layout decisions
- **Container queries**: respond to the parent container — use for component-level responsiveness
- Set `container-type: inline-size` on the parent, then query it with `@container (min-width: 400px)`
- Ideal for: cards that appear in both a sidebar (narrow) and main content (wide), reusable widgets, design system components
- Supported in all major browsers since early 2023

## Key Breakpoints (mobile-first)

| Breakpoint | Target | Typical columns |
|------------|--------|-----------------|
| Base (no query) | Small phones (< 768px) | 1 column |
| 768px | Tablets | 1-2 columns |
| 1024px | Desktops | 2-3 columns |
| 1280px | Large desktops | 3-4 columns |

- Always design mobile-first: base styles are mobile, then add complexity at wider breakpoints
- Test at: 320px, 768px, 1024px, 1280px, 1920px

## Responsive Patterns
- **Navigation**: horizontal on desktop → hamburger/toggleable on mobile
- **Sidebar**: side-by-side on desktop → stacked above or hidden on mobile (use `position: absolute` + toggle `display: none`)
- **Cards/Grid**: 3 columns → 2 columns → 1 column
- **Images**: use `max-width: 100%` by default
- **Tables**: scroll horizontally or stack rows vertically on mobile

## Mobile Considerations
- Mobile = usually 1 column, max 2
- Stack 2-column desktop layouts into single column on mobile
- On mobile, simplify: reduce content shown, not just shrink it
- Touch targets: minimum 24x24px (WCAG 2.2), recommended 44x44px, ideal 48x48px (Material Design)

## Responsive Typography
- Use `rem` units so text scales with user preferences
- Consider `clamp()` for fluid type: `font-size: clamp(1rem, 2.5vw, 2rem)`
- At smaller scales: tight letter spacing collapses, thin fonts vanish, margins feel exaggerated
- **Design once, test four times**: test at 1920px (full desktop), 768px (tablet), 320px (phone), and a thumbnail size (~64px equivalent) — because screenshots, social previews, and thumbnails will show your design at scales you didn't intend

## Sticky Elements
- Use `position: sticky` for headers and sidebars that should stay visible on scroll
- **Gotcha**: Sticky elements inside flex containers need `align-self: flex-start` to work properly
- Account for sticky header height in the sidebar's top offset (typically `top: 60-80px`)
- Test with varying content lengths — sticky sidebars can behave oddly when shorter than viewport

## Using rem for Spacing
- `1rem = 16px` by default
- Spacing scales with font size preference
- Use rem for margins, padding, and gaps for consistent responsive behavior

## The Pre-Code Sketch Rule
- Before any project: sketch how the layout responds at mobile, tablet, and desktop
- Decide which elements hide, stack, or reflow
- This prevents the sunk-cost fallacy of rebuilding layouts mid-project

## Respect User Preferences

Handle these system-level media queries in every project:
- **prefers-reduced-motion: reduce** — disable or minimize all animations and transitions
- **prefers-color-scheme: dark** — swap to dark mode color tokens
- **prefers-contrast: more** — increase contrast ratios beyond minimums:
  - Use thicker borders (2px+) instead of subtle 1px lines
  - Remove decorative gradients and replace with solid colors
  - Increase font weight by one step (400 → 500, 500 → 600)
  - Remove low-contrast placeholder text styling
  - Ensure all text meets AAA contrast ratio (7:1) when possible

Most frameworks have built-in utilities for these (e.g., Tailwind's `motion-safe:`, `dark:`).
