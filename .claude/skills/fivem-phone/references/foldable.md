# Foldable phone UI

No free FiveM phone folds out of the box. A foldable is a phone frame with a **fold state** that changes the screen shape and the layout of every app. Design guidance below comes from Android's foldable docs (developer.android.com: "Learn about foldables", "Make your app fold aware", "Use window size classes"). Samsung-specific details (Flex mode, Flex Window) weren't reachable from here and are marked unverified.

## Pick a form factor

Copy a real device. `real-foldables.md` has the specs and the software behaviour of iPhone Duo, Galaxy Z Fold8 / Fold8 Ultra / Flip8 / TriFold and Huawei Mate XTs. `assets/phone-template/` implements all six styles (`bar`, `passport`, `wide`, `tall`, `flip`, `trifold`), so start from it.

| | Book-style (Fold, Duo) | Flip-style (clamshell) | Tri-fold |
|---|---|---|---|
| closed | a full phone on the cover. Fold8 Ultra is tall 21:9, Fold8 is wide 10:16, Duo is short and wide | small cover screen: clock, widgets, 5 pinned apps, notifications | a full 21:9 phone on the cover |
| open | near-square or landscape inner screen, **2 panes** | tall normal phone with a horizontal crease | 10" 4:3, **3 panes**, two hinges at ⅓ and ⅔ |
| half-open | **book posture** (Duo moves content off the crease) | **Flex mode**: content on top, controls below | not supported (Samsung): only fully folded or open |
| opening ritual | swing open from the outer edge | flip up from the bottom edge | right panel first, then left; warns on a wrong order |

Pick one per server, or let players choose (the template's Settings → 手机型号) if you want variety. Every app then needs 1-, 2- and 3-pane layouts.

## States

```
folded (cover) ⇄ unfolded (inner)        optional: half-open (book / tabletop)
```
- Store `foldState` in the phone shell, alongside open/closed. A key (e.g. a second keybind) or a hinge button on the frame toggles it.
- Apps never read the frame size directly. They read the **screen width class** of their container (below).

## Layout by screen width (Android window size classes)

Android uses width breakpoints: **compact < 600dp** (phones in portrait), **medium 600–840dp** (tablets in portrait, most unfolded inner displays in portrait), **expanded 840–1200dp** (tablets/unfolded in landscape). Android also says size classes depend on the window, not the device type.

Scale the inner screen with the same `--pt` unit as the rest of the phone (`phone-design.md` §1). A cover screen ≈ 390 pt wide and an inner screen ≈ 720–760 pt wide (≈, roughly a Z Fold's proportions) put it in Android's "medium" class, which is the two-pane case.

Because the whole phone scales with the game resolution, a pixel breakpoint would flip at different fold states on 720p and 1440p. **Drive the layout from the fold state, not from pixels.** Set `data-fold="open" | "closed"` on the screen and let apps style against it:
```css
.app { display: grid; grid-template-columns: 1fr; }
[data-fold="open"] .app { grid-template-columns: minmax(calc(260 * var(--pt)), 2fr) 3fr; }  /* list | detail */
[data-fold="open"] .app .detail-empty { display: grid; }   /* "pick a chat" placeholder on the right */
```
Container queries in container units (`cqi`) are an alternative for apps that also run in other frames. Test them in FiveM's CEF first (unverified).

Canonical layouts to use when unfolded:
- **list-detail**: messages, contacts, mail, garage, bank transactions. Folded shows list *or* detail; unfolded shows both.
- **supporting pane**: maps/GPS with a side panel, music with a queue, a shop item with specs/reviews.
- **feed/grid**: gallery, social, marketplace. More columns when unfolded.

## Continuity: folding must never lose the player's place

Android: the app must keep its state across fold/unfold. Folded and unfolded layouts should *complement* each other (the same product image and description, plus specs and reviews when unfolded).
- Keep app state (selected chat, scroll position, half-typed message, open item) in a store above the layout (React context/zustand/a plain object), not inside a pane that unmounts.
- Folded → unfolded: show what was on screen plus the extra pane (the open chat appears on the right, the list on the left).
- Unfolded → folded: show the pane with focus (the open chat). If nothing was selected, show the list.
- A text field with focus keeps its focus and caret.

## The fold itself

Android guidance, applied:
- Don't put buttons, text or dialogs **across the fold**. Treat it as a natural divider between panes. Keep controls a little away from it.
- Book posture: content left/right. Tabletop: content (video, camera, map) on the top half, controls on the bottom half (Samsung's Flex mode follows the same idea; unverified).
- Dialogs and pop-ups go in one half or centred over one pane, never over the hinge.

Draw a subtle hinge line on the inner screen (a 1px gradient or a soft shadow column) so players read it as one folded screen.

## Fold animation (cheap)

Animate **only** `transform` and `opacity`. Don't animate `width`/`height`, which relays out every app. Two approaches:

**A. Crossfade + frame scale (cheapest, recommended):** the frame shell scales from the cover size to the inner size (`transform: scaleX()` on an empty shell element), while the cover screen fades out and the inner screen (already laid out at its final size, hidden) fades in. Use `--spring-soft` (404 ms, from `phone-design.md` §4). Transitions, not keyframes, so pressing fold again mid-way reverses smoothly. `assets/phone-template/` implements this one.

**B. 3D hinge (nicer, a bit more GPU):**
```css
.fold { perspective: 1400px; }
.half { transform-style: preserve-3d; backface-visibility: hidden; transition: transform var(--spring-soft-dur) var(--spring-soft); }
.half.left  { transform-origin: right center; }
.folded .half.left { transform: rotateY(180deg); }   /* left half closes over the right */
.cover { backface-visibility: hidden; transform: rotateY(180deg); }  /* cover screen on the back of the left half */
```
Without `perspective` on the parent, the rotation looks flat. During the 3D turn, show a static snapshot of the app (no live animations, no blur behind it), then swap in the live layout when it ends.

Add a short "click" sound on fold/unfold if the server uses UI sounds. Make interrupting work: pressing fold again mid-animation reverses from the current position (`apple-design`, "Interruptibility").

## Cover screen content

Keep it glanceable: time and date (game clock), battery/signal (cosmetic), the latest notifications, an incoming call with answer/decline, music controls, and maybe quick replies. Opening the phone while a notification shows opens that app on the inner screen (continuity again). On a flip-style cover, use a short list instead of an app grid.

## In the hand

The base game has no foldable phone prop. Either use `prop_amb_phone` and accept that it doesn't fold, or make a custom prop with two states (two models, or one model with a hinge animated by a `.ycd`). That means Blender + Sollumz + `fivem-animation`, so ask before using those skills. Keep the `cellphone@` animations for holding it.

## Performance checklist for foldables

- Render only the active screen. Unmount the cover when unfolded, and the reverse.
- One fold animation at a time, ≤ 400 ms, nothing animating when idle.
- No `backdrop-filter` on both screens. The inner screen is bigger, so blur costs more there.
- Wallpapers as WebP sized for the inner screen (e.g. ~1200 px wide), not 4K images.
