---
name: accessibility
description: Web accessibility (a11y) guidelines and WCAG compliance for building inclusive websites. Use this skill when building any web interface to ensure it's usable by people with disabilities. Trigger whenever the agent is creating HTML, forms, interactive elements, navigation, color schemes, or any user-facing feature. Accessibility should be considered from the start, not bolted on afterward.
---

# Web Accessibility (a11y) — WCAG 2.2 Level AA

## Core Principle

Design should be accessible to all users, including people with visual, motor, auditory, and cognitive disabilities. Accessibility isn't optional—it's a legal requirement in many jurisdictions (ADA, EAA) and the right thing to do. Accessible design is better design for EVERYONE.

## Semantic HTML First

Use native HTML elements before reaching for ARIA:
- `<button>` not `<div onclick>`
- `<a>` not `<span onclick>`
- Landmark elements: `<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<section>`
- `<label>` for every form input (explicitly linked with `for` attribute)
- `<table>` for tabular data with `<th>` headers
- **Headings**: one `<h1>` per page, then logical `<h2>`→`<h6>` hierarchy (no skipping levels)

## Color Contrast

- **Body text**: minimum 4.5:1 contrast ratio against background (WCAG AA)
- **Large text** (18px+ bold or 24px+ regular): minimum 3:1 ratio
- **UI components and icons**: minimum 3:1 ratio
- Never use pure white on pure black for long text—too much contrast causes eye strain
- Don't rely on color alone to communicate meaning—always add icons, labels, or patterns as secondary cues
- Test with color blindness simulators

## Keyboard Navigation

- Every interactive element must be reachable via Tab key
- Visible focus indicators on all focusable elements — never remove `outline` without replacing it. Use `focus-visible` to show focus rings only for keyboard users (not mouse clicks)
- Custom focus styles: 2px solid outline in a visible color, with 2px offset from the element
- Logical tab order follows the visual layout
- Escape to close modals/dropdowns
- Arrow keys for navigation within components (tabs, menus)
- Enter/Space to activate buttons and links

### Tabindex Rules

- **Never use positive tabindex values** (1, 2, 3…) — they override natural tab order and create a confusing experience
- **tabindex="0"**: adds a non-interactive element to the tab order (use for scrollable containers, custom widgets)
- **tabindex="-1"**: allows programmatic focus (via JS) but not keyboard tabbing — useful for elements you want to focus on open/reveal but keep out of the tab flow
- **Scrollable containers** with `overflow: auto/scroll` need `tabindex="0"` so keyboard users can scroll them

## Focus Management

- When opening a modal, move focus into it
- When closing a modal, return focus to the trigger element
- **Focus trapping**: Tab cycles within the modal while it's open
- **"Skip to content" link** as the first focusable element on every page

## ARIA Guidelines

- Prefer native semantics: `<button>` over `<div role="button">`
- `aria-label` for icon-only buttons: `<button aria-label="Close menu">X</button>`
- `aria-hidden="true"` on purely decorative elements
- `aria-expanded` on toggle buttons controlling collapsible content
- Verify ARIA usage in browser accessibility tree (Chrome DevTools: Ctrl+Shift+P → "Show accessibility")

### aria-live for Dynamic Content

Use `aria-live` on containers where content updates dynamically (toasts, status messages, live data):
- **polite**: waits for the screen reader to finish its current announcement, then reads the update — use for most cases (save confirmations, status updates)
- **assertive**: interrupts whatever the screen reader is doing — only use for critical errors or urgent alerts
- **off** (or omit): no announcement — for content the user doesn't need to know about immediately

## Images and Media

- `alt` text on every meaningful image—describe what the image conveys, not what it is
- Empty `alt=""` on decorative images (also set `aria-hidden="true"`)
- **Video**: provide captions and transcripts
- **Audio**: provide transcripts
- Avoid autoplay; if used, provide pause/stop controls

## Forms

- Every input needs a visible `<label>`
- Group related inputs with `<fieldset>` and `<legend>`
- **Error messages**: associate with `aria-describedby`, announce with `aria-live`
- Don't rely solely on placeholder text as labels
- Use `autocomplete` attributes for common fields (name, email, address)
- **Autofocus**: use on the primary input when a page has one clear purpose (e.g., search field, login form) — saves keyboard users extra tabbing

## Touch and Click Targets

- Minimum 24x24 CSS pixels (WCAG 2.2)
- Recommended: 44x44px minimum, 48x48px ideal
- Adequate spacing between targets to prevent mis-taps
- **Dragging**: always provide a non-dragging alternative (WCAG 2.2 new)

## Motor Impairment Considerations

- **No timing restrictions**: never auto-delete, auto-dismiss, or require timed actions — users with motor impairments need more time to reach buttons and controls
- Space clickable elements far enough apart to prevent accidental taps, especially at high zoom levels
- Custom checkboxes with labels linked via `for` attribute give a much larger click area than the tiny default checkbox

## Motion and Animation

Respect the `prefers-reduced-motion: reduce` media query — when active, disable or
minimize all animations, transitions, and smooth scrolling. Most frameworks have built-in
utilities for this (e.g., Tailwind's `motion-safe:` and `motion-reduce:` variants).

- No content that flashes more than 3 times per second
- Auto-playing carousels must have pause controls

## Text and Readability

- Text must be resizable up to 200% without loss of function (WCAG 2.1 AA)
- Use rem/em units, not px for font sizes
- Ensure content reflows at 400% zoom (no horizontal scrolling)
- Sufficient line height (1.5x for body), paragraph spacing, word spacing
- For text-heavy sites (blogs, documentation): consider offering a dyslexic-friendly font option — fonts like OpenDyslexic are designed for easier reading

## Responsive Accessibility

- Touch targets appropriate for device
- Zoom-friendly: no fixed positioning that blocks zoomed content
- Test on real devices and screen readers
- Respect user preferences: dark mode, reduced motion, increased font size

## Testing Checklist

- [ ] Tab through entire page — can you reach and use everything?
- [ ] Screen reader test (VoiceOver, NVDA, or browser accessibility tree)
- [ ] Color contrast checker (DevTools built-in color picker shows AA/AAA lines)
- [ ] Resize text to 200% — does everything still work?
- [ ] Test without a mouse — keyboard only
- [ ] Check heading hierarchy with an outlining tool
- [ ] Test with OS high contrast mode enabled (Windows: Left Alt + Left Shift + Print Screen)
- [ ] Color blindness emulation (DevTools → Rendering → Emulate vision deficiencies)
- [ ] Test with sound completely off (for sites using audio cues)
- [ ] **Automated**: Lighthouse accessibility audit (target >90), ESLint `jsx-a11y` plugin for JSX/React projects
- [ ] **CI integration**: axe-core (via `@axe-core/playwright`, `cypress-axe`, or `jest-axe`) for automated regression testing in CI pipelines
- [ ] **CLI audits**: pa11y for quick command-line accessibility checks on URLs
