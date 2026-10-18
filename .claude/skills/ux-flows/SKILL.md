---
name: ux-flows
description: User experience flows, journey design, and conversion thinking for web projects. Use this skill when planning how users move through a site, designing signup/onboarding/checkout flows, placing CTAs and trust signals, reducing friction, or thinking about what users expect and need at each stage. Trigger whenever the agent is building a multi-page site, landing page, e-commerce flow, SaaS onboarding, or any experience where guiding users toward a goal matters.
---

# UX Flows: User Journeys, Conversion & Friction

## Think Entry → Goal → Exit

Every page exists to move the user closer to a goal. Before designing, answer three questions:

1. **Where did the user come from?** (Search, ad, social, direct, internal link)
2. **What do they want?** (Information, a product, to sign up, to compare)
3. **What should they do next?** (Click CTA, fill form, add to cart, read more)

If you can't answer all three, the page doesn't have a clear purpose yet.

## User Intent by Page Type

Different pages serve different mindsets. Match the design to the intent:

| Page type | User intent | What they expect to see |
|-----------|------------|------------------------|
| Landing page | Evaluate a pitch | Clear value prop, one CTA, social proof, no distractions |
| Product page | Decide whether to buy | Price, images, reviews, specs, add-to-cart |
| Pricing page | Compare options | Plans side by side, highlighted recommendation, FAQ |
| Blog/article | Learn something | Readable text, clear headings, related content |
| Documentation | Solve a problem | Search, sidebar nav, code examples, copy buttons |
| Homepage | Understand what this is | Hero with value prop, trust signals, clear paths forward |
| Dashboard | Get status and act | Key metrics visible, actions within reach, no clutter |

## The Friction Checklist

Friction is anything that makes the user pause, think, or give up. Audit every flow for these:

- **Too many steps**: Can any steps be combined or removed?
- **Too many fields**: Ask only for what you need right now — collect the rest later
- **Unclear next action**: Is there exactly one obvious thing to do next?
- **Surprise costs or requirements**: Price, shipping, account creation — show these early, not at the last step
- **Slow feedback**: Does the UI respond instantly? (See interaction-patterns for optimistic UI)
- **Dead ends**: Does every page have a clear next step? Never leave users stranded

## Progressive Disclosure

Don't show everything at once. Reveal complexity as the user needs it:

- **Multi-step forms**: Break long forms into 2-4 steps with a progress indicator. Users who see 3 fields are more likely to start than users who see 15
- **Expandable sections**: Summary visible, details on click (FAQ, feature specs, advanced settings)
- **Staged onboarding**: Collect essentials at signup (email + password), then gather profile details over the first few sessions
- **Contextual help**: Show tooltips and hints near the field that needs them, not in a separate help page

## Cognitive Load

The brain processes ~4 items at a time. Reduce choices to reduce effort:

- One primary CTA per view — if everything is important, nothing is
- Group related options (max 5-7 items per group)
- Use smart defaults so users can accept rather than choose
- Pre-fill what you can (location, currency, returning user data)
- Remove decisions that don't matter to the user (auto-select the best option, let them change later)

## Trust & Social Proof Placement

Trust signals work best placed exactly where hesitation happens:

- **Next to CTAs**: "30-day money-back guarantee" beside the buy button
- **Next to forms**: "We'll never share your email" near the signup field
- **Next to pricing**: Client logos, user count, or review score
- **Early on the page**: 2-3 strong testimonials with real names and faces beat 10 anonymous quotes
- **Checkout**: Security badges, payment provider logos, return policy

### What builds trust

- Real testimonials with names, photos, and specifics ("Increased our conversion by 34%")
- Third-party review scores (Google, Trustpilot, G2)
- Client/partner logos
- Case studies with measurable results
- "As seen in" press mentions
- Active user counts or social proof counters

### What erodes trust

- Stock photos of fake people
- Vague testimonials ("Great product!")
- No contact information or hidden pricing
- Aggressive popups and dark patterns
- Broken pages, outdated content, dead links

## CTA Strategy

- **One primary CTA per section** — don't compete with yourself
- **Action-oriented text**: "Start free trial" not "Submit", "Get the report" not "Click here"
- **Repeat the main CTA** at natural decision points (after hero, after features, after social proof, in footer)
- **Secondary CTAs** for users not ready yet: "See pricing" / "Watch demo" / "Read case study"
- **Sticky CTA** on mobile for long pages — keeps the action always reachable
- **Match CTA to intent**: a blog reader wants "Read more", not "Buy now"

## Signup & Login Flows

- Minimize fields: email + password is enough to start. Name, company, role — collect later
- Offer social login (Google, GitHub, etc.) — reduces drop-off by ~8%
- Show the value before asking for signup (let users explore first)
- Confirm success clearly: redirect to the product, not a "check your email" dead end
- Magic link / passwordless login reduces friction for returning users

## Onboarding Flows

- **First-run experience**: Guide new users to their first success moment as fast as possible
- **Progress indicators**: Show users how far along they are (step 2 of 4)
- **Skippable**: Never block the user from reaching the product — let them skip and come back
- **Contextual, not front-loaded**: Teach features when the user first encounters them, not all at once in a tutorial
- **Empty states that guide**: When a dashboard is empty, don't show a blank page — show what to do first ("Create your first project", "Import your data")

## Checkout & Payment Flows

- Show total cost (including shipping/tax) as early as possible — surprise costs are the #1 reason for cart abandonment
- Guest checkout option — don't force account creation to buy
- Minimize steps: shipping → payment → confirm (3 steps max)
- Auto-fill addresses and payment where possible
- Show security indicators (lock icon, "Encrypted", payment logos)
- Save cart state — if the user leaves and comes back, the cart should still be there
- Confirmation page with clear order summary, expected delivery, and next steps

## Multi-Step Flow Patterns

For any flow longer than one screen:

- **Progress bar or step indicator**: Users need to know where they are and how much is left
- **Back button that preserves input**: Never lose what the user already entered
- **Validation per step**: Check before advancing, not all at the end
- **Save draft / resume later**: For longer flows (applications, onboarding, complex forms)
- **Summary before submit**: Let users review everything before committing

## Drop-Off Prevention

- If users frequently abandon at a specific step, that step has too much friction — simplify it
- Exit-intent: offer to save progress, not a desperate discount popup
- Reduce "registration walls" — let users do as much as possible before requiring an account
- For e-commerce: abandoned cart emails with a direct link back to their cart
- For SaaS: re-engagement emails highlighting what they haven't tried yet

## Page-Level Flow Thinking

Within a single page, content should flow like a conversation:

1. **Hook**: What's in it for the user? (Hero / value prop)
2. **Credibility**: Why should they trust you? (Social proof / logos)
3. **Substance**: What exactly do you offer? (Features / benefits)
4. **Evidence**: Does it work? (Case studies / testimonials / data)
5. **Action**: What should they do now? (CTA)
6. **Objections**: What might hold them back? (FAQ / guarantees)
7. **Final push**: Last CTA for those who scrolled all the way

This mirrors how a conversation works: you don't ask someone to buy before they know what you're selling.

---

# Web App & Dashboard Patterns

The sections above focus on marketing sites and conversion flows. The patterns below
apply to web apps, dashboards, SaaS products, and internal tools — where users return
daily and the goal shifts from "convert" to "get things done efficiently."

## Dashboard Design

- **F-pattern scanning**: Users scan top-left first, then across, then down. Place the most important KPIs and status info top-left
- **Key metrics visible immediately**: The dashboard is a home base — show status at a glance without requiring clicks
- **Entry points, not dead ends**: Each card/widget should link deeper into the relevant section
- **Don't overload**: Show 5-8 key metrics, not every data point. Link to detail views for the rest
- **Default to the most useful time range** (last 7 days, current sprint, today) — let users change it
- **Charts need context**: A number alone means nothing. Show trends, comparisons, or targets alongside raw values
- **Loading and empty states matter here too**: A dashboard full of skeleton loaders or blank cards on first login feels broken

## Empty States

Empty states are not error states — they're opportunities to guide users. Three types:

### First-use empty states
The user just signed up and has no data yet. This is the most important empty state:
- Explain what will appear here once they take action
- Include a clear primary action ("Create your first project", "Import data", "Invite your team")
- Optional: show a preview or illustration of what the populated state looks like
- Never show a blank white page with no guidance

### No-results empty states
A search or filter returned nothing:
- Confirm what they searched for ("No results for 'xyz'")
- Suggest next steps: clear filters, broaden search, try different terms
- Don't just say "No results found" — help them recover

### Completed empty states
Everything is done (inbox zero, all tasks complete):
- Celebrate briefly ("All caught up!")
- Suggest what to do next or let them rest — don't manufacture urgency

## Settings Pages

- **Group by category**: Account, Profile, Notifications, Security, Billing, Integrations — not one giant list
- **Sidebar or tab navigation** for settings categories in complex apps
- **Use toggles for on/off**, dropdowns for multiple choice, text fields for custom values
- **Smart defaults**: Ship with sensible defaults so most users never need to touch settings
- **Save behavior**: Auto-save with confirmation toast, or explicit Save button — pick one and be consistent. Never mix both patterns
- **Dangerous actions isolated**: Delete account, reset data, revoke access — put these at the bottom, in a "Danger zone" section with confirmation dialogs
- **Search within settings** for apps with many options (follow VS Code, GitHub, Notion pattern)
- **Show current state**: If a setting is on, show that it's on. Don't make users guess

## Data Tables

### Structure
- **Left-align text**, **right-align numbers** — this follows natural reading patterns and makes numbers easy to compare
- **Sticky header row** so column labels stay visible on scroll
- **Reasonable row density**: Default to comfortable spacing, offer a compact toggle for power users
- **Zebra striping or subtle row borders** — pick one for scanability, not both

### Sorting and Filtering
- **Default sort**: Most recent first, or most relevant to the user's workflow
- **Sort indicators** on column headers (chevron showing direction)
- **Filters as chips/tags**: Show active filters visibly above the table so users know what's filtered
- **Show result count** after filtering ("Showing 12 of 348 items")
- **Instant filtering** feels faster than filter-then-apply, prefer it when dataset size allows

### Pagination and Actions
- **Pagination**: 10-50 rows per page with option to change. Show total count
- **Row actions**: 1-2 inline actions (edit, delete) at the end of each row. For 3+, use a "..." menu
- **Bulk actions**: Checkbox column + action toolbar that appears on selection ("Delete 3 items", "Export selected")
- **Responsive**: On mobile, show only essential columns. Use expandable rows or cards instead of horizontal scroll

## Notifications

### In-App Notifications
- **Bell icon with badge count** is the universal pattern — don't reinvent it
- **Group related notifications**: "3 comments on your post" not three separate items
- **Mark as read/unread** and **mark all as read**
- **Link directly to the relevant item** — don't just say "Something happened", take them there
- **Time-stamp everything** and show relative time ("2 hours ago", not "14:32 UTC")

### Notification Preferences
- Let users control: **what** they're notified about, **how** (in-app, email, push), and **how often** (real-time, daily digest, weekly)
- Group preferences by category (comments, mentions, status changes, billing)
- Offer a "mute all" or "quiet hours" option
- Default to reasonable settings — most users won't customize, so the defaults should work well

### Toast / Snackbar Notifications
- Use for confirmations of actions the user just took ("Saved", "Deleted", "Copied")
- Auto-dismiss after 3-5 seconds for success messages
- Error toasts should persist until dismissed (don't auto-hide errors)
- Include an undo action where applicable ("Item deleted. Undo")
- Position consistently: bottom-left or bottom-center for non-blocking, top-center for important

## Permission Requests

- **Never ask on page load**: Users who haven't used the product yet will deny by default
- **Ask in context**: Request notification permission after the user has done something they'd want to be notified about (e.g., placed an order → "Want delivery updates?")
- **Explain the benefit first**: Use a custom pre-prompt explaining what they'll get before triggering the browser's native permission dialog
- **Respect "no"**: If denied, don't ask again immediately. Offer a settings path to enable later
- **Degrade gracefully**: The app must work without the permission. Push notifications, location, camera — all optional enhancements

## Feature Discovery

Introduce features when users need them, not all at once during onboarding:

### Patterns (from least to most intrusive)
- **Hotspots**: Subtle pulsing dots on UI elements that reveal a tooltip on hover/click — lowest interruption
- **Tooltips**: Point to a specific element with a short explanation. Best for single features ("New! You can now filter by date")
- **Interactive walkthroughs**: Step-by-step tooltip sequences that guide the user through a feature by having them actually use it — much more effective than passive tours
- **Modals**: For major new features or important announcements. Use sparingly — they block the UI
- **Changelogs/What's New**: A dedicated section (often behind a sparkle icon) for users who want to see all updates

### Rules
- Always skippable — never gate the product behind a tutorial
- Show feature tips contextually: when the user first encounters the feature, not at login
- Don't re-show dismissed tips. Respect the dismissal
- Track what the user has seen so you don't repeat yourself

## Search

- **Always visible or one click away** in navigation for content-heavy apps
- **Instant results** as the user types (debounced at 200-300ms)
- **Show result categories** if searching across types (users, projects, documents)
- **Recent searches and popular queries** in the empty search dropdown
- **Keyboard shortcut** (Cmd/Ctrl+K is becoming standard) for power users
- **No results state**: Suggest corrections, show related results, or offer to create a new item
