---
name: app-patterns
description: Design patterns for web apps, dashboards, SaaS products, admin panels, and internal tools. Use this skill when building any authenticated, interaction-heavy interface where users return daily and the goal is productivity, not conversion. Trigger whenever the agent is building a dashboard, admin panel, settings UI, data-heavy interface, or any app where users navigate between views to get work done. For marketing sites and landing pages, use the other skills directly — this skill covers what's different about apps.
---

# App Patterns

This skill covers what's different when you're building a web app instead of a marketing
site. The universal skills (typography, color, spacing, accessibility, etc.) all apply — this
skill adds the layout structures, components, and patterns specific to apps where users
log in, navigate between views, and get work done.

For marketing/landing page patterns, see `content-structure` and `ui-components`.
For app-specific UX flows (dashboards, empty states, settings, notifications, search,
data tables, feature discovery), see the "Web App & Dashboard Patterns" section in `ux-flows`.

## App Shell Layouts

Every web app has a shell — the persistent structure that wraps page content. Pick one
and use it consistently across the entire app.

### Sidebar + Main Content (Most Common)

The dominant pattern for apps with many sections (Slack, Figma, Notion, GitHub):

- **Sidebar**: 240-280px wide, fixed or collapsible
- **Main content**: fills remaining width, scrolls independently
- **When to use**: 8+ navigation items, deep hierarchy, or users need to see where they are at all times
- **Collapsible sidebar**: icon-only mode at 56-64px wide. Toggle with a hamburger or chevron. Remember the user's preference
- **Mobile**: sidebar becomes a slide-over drawer, triggered by hamburger icon

```
┌──────┬──────────────────────────┐
│      │                          │
│ Side │     Main Content         │
│ bar  │                          │
│      │                          │
│      │                          │
└──────┴──────────────────────────┘
```

### Top Bar + Content (Simpler Apps)

For apps with fewer sections (Stripe Dashboard, simple SaaS):

- **Top bar**: 48-64px tall, logo left, primary nav center or left, user menu right
- **Main content**: full width below, with a max-width container (1200-1400px)
- **When to use**: 3-7 navigation items, flat hierarchy, content-focused
- **Mobile**: top bar stays, nav items collapse into hamburger

```
┌─────────────────────────────────┐
│         Top Bar / Nav           │
├─────────────────────────────────┤
│                                 │
│        Main Content             │
│                                 │
└─────────────────────────────────┘
```

### Sidebar + Top Bar + Content (Complex Apps)

For apps that need both global nav and section-level nav (AWS Console, Jira):

- **Top bar**: global actions (search, notifications, user menu, app switcher)
- **Sidebar**: section-level navigation, changes based on active area
- **When to use**: very large apps with distinct product areas
- **Caution**: adds complexity — only use when the information architecture truly demands it

```
┌─────────────────────────────────┐
│           Top Bar               │
├──────┬──────────────────────────┤
│      │                          │
│ Side │     Main Content         │
│ bar  │                          │
│      │                          │
└──────┴──────────────────────────┘
```

### Split Pane (Master-Detail)

For list → detail workflows (email clients, file managers, CRM):

- **Left pane**: scrollable list of items, 300-400px wide
- **Right pane**: detail view of selected item, fills remaining space
- **When to use**: users scan a list and drill into individual items repeatedly
- **Mobile**: list and detail become separate views with back navigation

```
┌──────────────┬──────────────────┐
│              │                  │
│   List       │   Detail         │
│              │                  │
│  > Item 1    │   Item 2 content │
│    Item 2  ← │                  │
│    Item 3    │                  │
└──────────────┴──────────────────┘
```

### Shell Design Rules

- **Persistent elements stay fixed**: sidebar and top bar don't scroll with content
- **Content area scrolls independently**: use `overflow-y: auto` on the main content region, not the whole page
- **Sticky sub-headers within content**: page titles, tab bars, and filter bars often stick to the top of the content area
- **Z-index layers**: sidebar (z-20) > top bar (z-30) > modals (z-40) > toasts (z-50). Pick a convention and document it
- **Transitions between views**: keep the shell stable, only swap the content area. The shell is the user's anchor

## Sidebar Navigation

### Structure

- **Logo or app name** at the top (links to home/dashboard)
- **Primary nav items**: icon + label, 8-12px vertical padding per item
- **Sections/groups**: separate with subtle dividers or group headings (lightweight labels, not heavy borders)
- **Active state**: background highlight + stronger text color or left border accent
- **Nested items**: indent one level (16-20px). Collapse by default, expand on click. Show a chevron to indicate expandability
- **Bottom section**: settings, help, user profile — pin these to the bottom of the sidebar

### Collapsible Sidebar

- Collapsed width: 56-64px, show only icons (with tooltips on hover)
- Expanded width: 240-280px, show icon + label
- Transition: 200ms ease — the sidebar should feel snappy, not cinematic
- Persist collapsed/expanded state in localStorage
- On mobile: collapsed = hidden, expanded = full-width overlay with backdrop

### Sidebar Scrolling

- If nav items exceed viewport height, the sidebar scrolls independently
- Keep the logo and bottom section (settings/profile) pinned — only the middle nav items scroll
- Use a subtle scroll shadow or fade at top/bottom to indicate more content

## Tabs

### When to Use

- Related content that shares a context but not a view (profile sections, settings categories, report views)
- The user needs to switch between views without losing their place in the app

### Design Rules

- **Active tab**: strong indicator — bottom border (2-3px), background color change, or both
- **Inactive tabs**: subdued text, no background
- **Tab bar position**: directly above the content it controls, visually connected (no gap)
- **Don't use tabs for primary navigation** — tabs are for sub-views within a page, not app-level routing
- **Overflow**: if tabs don't fit, use horizontal scroll with arrows or a "More" dropdown — never wrap tabs to a second line
- **Keyboard**: arrow keys to move between tabs, Enter/Space to activate
- **ARIA**: `role="tablist"` on the container, `role="tab"` on each tab, `role="tabpanel"` on the content, `aria-selected` on the active tab

### Tab Variants

- **Underline tabs**: minimal, clean — default choice for most apps
- **Boxed/pill tabs**: each tab has a background — use when tabs need more visual weight
- **Vertical tabs**: stack tabs on the left side — use for settings pages with many categories

## Breadcrumbs

- Show the path from root to current page: `Home / Projects / Project Alpha / Settings`
- Use for apps with hierarchical navigation (3+ levels deep)
- Each segment is a link except the current page (display as plain text)
- Separator: `/` or `›` — keep it subtle
- Don't use breadcrumbs alongside tabs — pick one navigation pattern per context
- ARIA: `nav` with `aria-label="Breadcrumb"`, current page marked with `aria-current="page"`

## Command Palette (Cmd+K)

The power-user navigation pattern (VS Code, Figma, Linear, Notion):

- **Trigger**: `Cmd+K` (Mac) / `Ctrl+K` (Windows) — always this shortcut, users expect it
- **Behavior**: modal search input at top of screen, results appear below as user types
- **Content**: recent items, navigation destinations, actions ("Create project", "Open settings"), and search results
- **Keyboard-first**: arrow keys to navigate results, Enter to select, Escape to close
- **Fuzzy matching**: "sett" should find "Settings" — don't require exact matches
- **When to add one**: any app with 10+ navigable pages or frequent actions. It's not just for power users — it's the fastest way to get anywhere
- **Recency**: show recently visited pages and recently used actions first

## Status Badges and Tags

### Badges

Small visual indicators attached to other elements:

- **Notification count**: red circle with number on bell/inbox icons. Show "9+" for counts above 9
- **Status dot**: 8-10px colored circle (green = active, yellow = away, red = error, gray = offline)
- **Position**: top-right corner of the element they describe, offset by -4px to overlap the edge

### Tags / Chips

Inline labels for categorization and metadata:

- **Padding**: 2-4px vertical, 8-12px horizontal
- **Border radius**: pill shape (9999px) or rounded (4-6px) — pick one and be consistent
- **Colors**: use semantic colors (green for success/active, amber for warning, red for error, blue for info, gray for neutral)
- **Removable tags**: include an X button inside the tag, adequate touch target (24px+)
- **Don't overload**: max 3-4 tags per item in a list view — more than that is noise

## Avatars

- **Sizes**: 24px (inline/compact), 32px (lists), 40px (cards), 64px (profiles), 96-128px (profile pages)
- **Shape**: circle for people, rounded square for teams/orgs/apps
- **Fallback**: initials on a colored background when no image is available. Generate the background color from the user's name (hash → hue) for consistency
- **Avatar groups**: overlap by 25-30%, show a "+N" indicator for overflow. Max 4-5 visible before collapsing
- **Border**: 2px solid in the background color to separate overlapping avatars

## Tooltips and Popovers

### Tooltips

- **Purpose**: explain a UI element on hover — icon-only buttons, truncated text, abbreviated labels
- **Delay**: 300-500ms before showing (prevents flickering on casual mouse movement)
- **Duration**: disappear immediately on mouse leave
- **Content**: one line of text, no interactable content (links, buttons). If you need interactable content, use a popover
- **Position**: above the element by default, flip to below if clipped by viewport
- **Mobile**: tooltips don't work on touch — provide the information another way (aria-label, visible label)

### Popovers

- **Purpose**: small interactive panel attached to a trigger (filter options, user card, date picker)
- **Behavior**: click to open (not hover), click outside or Escape to close
- **Focus management**: focus moves into the popover on open, returns to trigger on close
- **Position**: use a positioning library (Floating UI / Popper) to handle viewport clipping and flipping
- **Arrow**: optional connector pointing to the trigger element

## Dropdown Menus

- **Trigger**: button with a chevron (▼) indicating a menu will open
- **Menu items**: 32-40px row height, icon (optional) + label + optional shortcut hint
- **Sections**: separate groups of actions with subtle dividers
- **Destructive actions**: red text, positioned last in the menu
- **Keyboard**: arrow keys to navigate, Enter to select, Escape to close, type-ahead to jump to an item
- **Max height**: if items exceed viewport, scroll within the menu (max-height + overflow-y)
- **ARIA**: `role="menu"` on the container, `role="menuitem"` on each item

## Skeleton Screens

App-specific loading pattern (more relevant than spinners for data-heavy views):

- **Match the layout**: skeleton shapes should mirror the real content structure (rectangles for text, circles for avatars, cards for cards)
- **Animation**: subtle pulse or shimmer (left-to-right gradient animation), 1.5-2s cycle
- **Don't skeleton everything**: if the shell (sidebar, top bar) is already loaded, only skeleton the content area
- **Transition**: fade the real content in over 150-200ms when data arrives — don't just snap it in
- **Avoid skeletons for fast loads**: if data typically arrives in under 200ms, show nothing and let it pop in. Skeletons for instant data feel slower than no loading state at all

## App-Specific Responsive Patterns

### Sidebar Behavior

| Viewport | Sidebar |
|----------|---------|
| Desktop (1024px+) | Visible, collapsible |
| Tablet (768-1023px) | Collapsed to icons by default |
| Mobile (< 768px) | Hidden, opens as overlay drawer |

### Content Density

- **Desktop**: comfortable spacing, multi-column layouts, full data tables
- **Tablet**: reduce columns, consider collapsing secondary panels
- **Mobile**: single column, stack everything, simplify data tables to essential columns or switch to card view

### Mobile App Patterns

- **Bottom navigation bar**: for the 3-5 most important destinations (replaces sidebar on mobile). 48-56px tall, icon + small label
- **Pull-to-refresh**: expected in list/feed views
- **Swipe actions**: reveal action buttons (archive, delete) on horizontal swipe — always provide a non-swipe alternative
- **Floating action button (FAB)**: for the single most important action on a screen ("New message", "Create"). Position bottom-right, 56px, high-contrast

## App Color Patterns

Apps use color differently than marketing sites:

- **Neutral-heavy**: 80-90% of the interface is neutral (backgrounds, text, borders). Color is reserved for meaning
- **Semantic colors do more work**: green/amber/red/blue carry status meaning throughout — success, warning, error, info
- **Accent color is functional**: it marks interactive elements (active nav, primary buttons, selected states), not decorative sections
- **Dark mode is expected**: most app users work in apps for hours — dark mode reduces eye strain. Plan for it from day one, not as an afterthought
- **Data visualization colors**: if your app has charts, define a 5-8 color palette for data series that works in both light and dark mode and is distinguishable by colorblind users

## See Also

- **`ux-flows`** — Web App & Dashboard Patterns section: dashboard design, empty states, settings pages, data tables, notifications, search, feature discovery, permission requests
- **`ui-components`** — shared components: buttons, cards, forms, modals, navigation, images
- **`interaction-patterns`** — animation, loading states, error handling, optimistic UI
- **`accessibility`** — ARIA roles for tabs, menus, dialogs; keyboard navigation; focus management
- **`color-systems`** — building the neutral + semantic + accent palette that apps rely on
