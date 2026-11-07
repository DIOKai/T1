# Pair and group dances

Sources: rpemotes-reborn (GPL-3.0, commit d3553c1) `Syncing.lua`, `GroupEmote.lua`, `config.lua`, `types.lua`, `AnimationList.lua`, README; Menyoo sync tutorial [l_0VtJsBVKk]. Entry syntax: `rpemotes-dances-and-shared.md` §5.

## 1. Two kinds of "dancing together"
| Want | Use | Clips |
|---|---|---|
| Same dance, several players, side by side (crew dance) | **Group emote** `/gemote <emote>` | one ordinary `CustomDP.Dances` clip |
| Partners who face/touch each other (salsa, ballroom, duo K-pop) | **Shared emote** `/nearby <emote>` | two clips (A and B), or one clip played on both |

## 2. Shared emotes: how rpemotes places the partner
- Request: `/nearby <emote>` goes to the closest player within 3 m; they accept with **Y** (control 246) or refuse with **L** (182) within 10 s (Syncing.lua). Needs `Config.SharedEmotesEnabled = true`.
- Placement: the source player is moved to `GetOffsetFromEntityInWorldCoords(target, side, front, height)` with heading `targetHeading − SyncOffsetHeading`, then `EmoteCancel(); Wait(300)` and the emote plays (Syncing.lua). Defaults: Front 1.0 m, Side 0.0, Height 0.0, Heading 180° — i.e. 1 m in front, facing each other.
- README: the offset of the emote **the initiating player started** is used; `Attachto` attaches the player whose emote defines it; if both define it only the initiator is attached; `bone` is a bone **ID (tag)**, not an index. Attach uses `AttachEntityToEntity(..., false, false, false, true, 1, true)` — collision off (Syncing.lua), so attached pairs don't push each other.
- Real offsets to start from: handshake `SyncOffsetFront = 0.9` (one side only); hug `1.05` / `1.18`; romantic hug `SyncOffsetSide = -0.05, SyncOffsetFront = 0.52` on both.

## 3. Authoring a pair dance in Blender
Design, not tested end to end (unverified):
1. Import **two** freemode skeletons into one scene (male + female if that's the couple). Both rest at their own origin.
2. Place the two rigs the way rpemotes will: the **initiator** is moved `SyncOffsetFront` metres along the **partner's** facing direction and turned `SyncOffsetHeading` (180° = face to face). In Blender (rest pose faces −Y, `fivem-animation`): partner at the origin facing −Y, initiator at Y = −Front (e.g. −1.0, or −0.52 for a close hold), rotated 180° about Z. Set this on the **armature objects**, not on bones, so each clip stays relative to its own ped. Sign of `SyncOffsetSide` in Blender X: unverified — test with a visible side offset first.
3. Animate both on the same beat grid (`dance_timing.py`), the same frame range, the same loop length. Contacts (hands, waist) must meet in that shared space.
4. **No root travel** in either clip: paired clips with root motion make the peds collide and drift apart [l_0VtJsBVKk 4:37–5:26]; the Menyoo route freezes and turns collision off [l_0VtJsBVKk 9:50–14:37]. Keep both in place; any "travel" is just body sway.
5. Bake each armature separately (`scripts/bake_loop.py`), export two clips in one clip dictionary (`<dict>` with `duo_a_clip`, `duo_b_clip`) — Sollumz Clip Dictionary with two Animation/Clip pairs (`fivem-animation` `sollumz-export.md`).
6. Write the A/B entries with the offset matching step 2 on the **initiator's** entry. Who initiates matters — decide which role usually sends `/nearby` and put the offset there (or on both, the same).
7. Preview (optional): EmotePreviewer can show shared emotes on two peds from the user's own GTA V Legacy (MIT, unsigned exe, needs extracted keys — ask first). Otherwise test in game with two clients.

Heights differ between male and female peds; hands that meet in Blender may miss slightly in game — tune `SyncOffsetFront/Side/Height` live (unverified how much).

## 4. Group emotes (crew dance)
- `/gemote <emote>`: scroll wheel picks a radius (default `GroupEmoteDefaultArea = 5.0`, max `GroupEmoteMaxArea = 10.0`); everyone in the circle gets a request; accepted players start together after `GroupEmoteCountdownTime = 10` s; leaving the circle cancels (GroupEmote.lua, config.lua). README: "Dance, salute, and more with 2 or more people."
- **Shared emotes cannot be group emotes** (GroupEmote.lua) — a crew dance is one solo `CustomDP.Dances` clip.
- Formation (rows, V-shape) is up to the players standing in place; rpemotes doesn't position group members (unverified for future versions).

## 5. Sync limits — tell the user up front
- Not frame-locked: each client starts its own copy (shared: after a 300 ms wait on each side; group: after a networked countdown). Latency can shift the start (exact drift unverified). Over a long loop a few frames of offset is normal.
- Music is not part of any emote — dancers stay in phase with a song only if each loop is exactly on the beat (`dance_timing.py --check`) and everyone started together.
- Two different problems: network start offset (fixed size, doesn't grow) vs an off-beat loop length (grows every repeat — e.g. 224 instead of 225 frames at 128 BPM is half a beat off after 8 loops). The skill can only fix the second.
