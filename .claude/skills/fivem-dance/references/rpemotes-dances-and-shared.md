# rpemotes-reborn dance entries (solo, props, shared syntax) and a GTAO-style system

Source: alberttheprince/rpemotes-reborn, GPL-3.0, commit d3553c1 (`client/AnimationList.lua`, `AnimationListCustom.lua`, `types.lua`, `Emote.lua`, `Syncing.lua`, `GroupEmote.lua`, `config.lua`). General custom-emote install (stream folder, BackUp file, rejoin) is in `fivem-animation` `references/playing-and-rpemotes.md`. Pair/group *authoring* and the request flow: `group-and-pair-dances.md`.

## 1. Where dances go
`client/AnimationListCustom.lua` has `CustomDP.Dances = {}` (also `Shared`, `PropEmotes`, `Exits`, `Emotes`, `Expressions`, `Walks`, `AnimalEmotes`). `LoadAddonEmotes()` merges each table into `RP.Dances` etc. Several custom list files must sit **between AnimationList.lua and Emote.lua** in `fxmanifest.lua` (comment in AnimationListCustom.lua). Keep a `BackUpAnimationListCustom.lua` copy — updates overwrite the file.

Entry shape (`types.lua`): `["name"] = { "dict", "clip", "Label", AnimationOptions = { … } }`. `dict` = the `.ycd` file name, `clip` = the clip Hash set in Sollumz.

```lua
CustomDP.Dances = {
  -- full-body loop: legs dance too, ped stands still
  ["kpopa"] = { "dio@kpop_a", "kpop_a_clip", "K-pop A (128)", AnimationOptions = {
      onFootFlag = AnimFlag.LOOP,
  } },
  -- upper-body only: legs walk / take another dance's legs
  ["kpopa_arms"] = { "dio@kpop_a", "kpop_a_clip", "K-pop A arms", AnimationOptions = {
      onFootFlag = AnimFlag.MOVING,
  } },
}
```

## 2. LOOP vs MOVING (the one choice that matters)
`AnimFlag = { MOVING = 51, LOOP = 1, STUCK = 50 }` (types.lua). Playback is `TaskPlayAnim(ped, dict, anim, BlendInSpeed or 5.0, BlendOutSpeed or 5.0, EmoteDuration or -1, flag, 0, …)` (Emote.lua).

| Flag | Value | Effect for a dance |
|---|---|---|
| `AnimFlag.LOOP` | 1 | **Full-body** loop; the ped can't walk. 127 of ~132 built-in dances use it |
| `AnimFlag.MOVING` | 51 = 1 loop + 2 hold last + 16 upper body + 32 secondary | **Upper body only**, legs follow movement; lets two dances combine — rpemotes' comment on `danceold`: MOVING "will allow for you to mix and match dance emotes, ie /e danceold and /e dance to control the bottom half of the body". The glowstick dances use it |
| `AnimFlag.STUCK` | 50 | hold last frame, upper body — not a dance |

- `Flag = <number>` overrides `onFootFlag`.
- **Deprecated:** `EmoteLoop`, `EmoteMoving`, `EmoteStuck` ("deprecated. Set onFootFlag instead", types.lua). Most YouTube tutorials, old dpemotes lists and generated entries (Griddy README, MotionConvertToEmote output) still print `EmoteLoop = true` [SI9ysKQpevY 5:58], [fKwBgz5gn3E 10:50] — convert them: `EmoteLoop = true` → `onFootFlag = AnimFlag.LOOP`; `EmoteMoving = true` → `onFootFlag = AnimFlag.MOVING`.
- The `.ycd` carries no loop flag; the clip only sets how long one cycle is.
- `EmoteDuration = <ms>` stops the loop after that time (shared emotes use it, e.g. handshake 3000).

## 3. Prop dances (glow sticks and similar)
Vanilla example `danceglowstick` (AnimationList.lua):
```lua
["danceglowstick"] = { "anim@amb@nightclub@lazlow@hi_railing@", "ambclub_13_mi_hi_sexualgriding_laz", "Dance Glowsticks",
  AnimationOptions = {
    Prop = 'ba_prop_battle_glowstick_01', PropBone = 28422,           -- PH_R_Hand
    PropPlacement = { 0.0700, 0.1400, 0.0, -80.0, 20.0, 0.0 },
    SecondProp = 'ba_prop_battle_glowstick_01', SecondPropBone = 60309, -- PH_L_Hand
    SecondPropPlacement = { 0.0700, 0.0900, 0.0, -120.0, -20.0, 0.0 },
    onFootFlag = AnimFlag.MOVING,
  } },
```
Template for a custom prop dance (fans, mic, bottle): copy the two-prop block onto your own clip. `PropPlacement = {x, y, z, rx, ry, rz}` in the hand bone's space; fine-tune live in game while the loop plays (Blender→offset formula unverified — `fivem-animation`). Use `PropNoCollision = true` if the prop knocks things. Put it in `CustomDP.PropEmotes` or `CustomDP.Dances`; both work as tables of the same shape (types.lua). A custom prop model needs `.ydr` + `.ytyp` + `data_file 'DLC_ITYP_REQUEST'` (`fivem-animation`).

## 4. Other options useful for dances (types.lua)
- `StartDelay` (ms) — wait before starting.
- `ExitEmote = "<Exits entry>"` — played when the dance is cancelled; an `EmoteDuration` on the exit emote locks input until it ends (Emote.lua). Use it for a bow / pose-out.
- `BlendInSpeed` / `BlendOutSpeed` (default 5.0) — softer start/stop of a loop.
- Club effects: `PtfxAsset`, `PtfxName`, `PtfxPlacement`, `PtfxBone`, `PtfxWait`, `PtfxCanHold`, `PtfxColor`, `PtfxInfo`, `PtfxNoProp` (which assets look good for confetti/smoke — unverified).
- `PlacementOffset` — for the placement feature.
- Categories: `Config.CustomCategories["Sports & Dances"] = { [EmoteType.DANCES] = {}, … }` (config.lua example). Dances share the "Emotes" ACE category (types.lua `AceCategoryFromEmoteType`).
- After adding or replacing a `.ycd`, players must **reconnect** — a resource restart isn't enough (`fivem-animation`; MotionConvertToEmote README).

## 5. Shared (two-player) entry syntax
`RP.Shared` shape: `[name] = { dict, anim, label, targetEmoteName, AnimationOptions }`. "You don't have to specify targetemotename; If you don't, it will just play the same animation on both"; "Emotes will work with either SyncOffset or Attachto" (AnimationList.lua). Partners reference each other:
```lua
CustomDP.Shared = {
  ["duo_a"] = { "dio@duo", "duo_a_clip", "Duo Dance (lead)", "duo_b", AnimationOptions = {
      onFootFlag = AnimFlag.LOOP, SyncOffsetFront = 1.0, SyncOffsetSide = 0.0, SyncOffsetHeading = 180.0 } },
  ["duo_b"] = { "dio@duo", "duo_b_clip", "Duo Dance (follow)", "duo_a", AnimationOptions = {
      onFootFlag = AnimFlag.LOOP } },
}
```
Offset defaults: `SyncOffsetFront` 1.0, `SyncOffsetSide` 0.0, `SyncOffsetHeight` 0.0, `SyncOffsetHeading` 180.0 (types.lua). Real examples: handshake sets `SyncOffsetFront = 0.9` on one side only; romantic hug `hugr`/`hugr2` uses `SyncOffsetSide = -0.05, SyncOffsetFront = 0.52`. `Attachto = true` + `bone` (tag) / `pos` / `rot` attaches instead of teleporting. Geometry, who moves, and how to author both clips: `group-and-pair-dances.md`.

## 6. Built-in vanilla dance clips worth knowing
- Club solo: `anim@amb@nightclub@mini@dance@dance_solo@male@var_b@` with clips like `high_center`, `high_center_up`, `high_center_down`, `med_center`, `med_center_up`.
- Club paired: `anim@amb@nightclub@mini@dance@dance_paired@dance_a@` (…`_b@`, `_d@`) clip `ped_a_dance_idle` (used solo in rpemotes; partner clip `ped_b_…` unverified).
- Facial moods for dancing: `PlayFacialAnim(ped, "mood_dancing_<low|med|high>_2", "anim@amb@nightclub@dancers@club_ambientpedsfaces@")` (kgv-dance client.lua). rpemotes expressions use `SetFacialIdleAnimOverride` (Emote.lua). Recommend a vanilla facial mood on top of a custom body dance; a custom face clip is unverified.

## 7. Own script: GTAO-style multi-variant dances
Pattern from Xinerki/kgv-dance (no licence — read for ideas, don't copy code):
- One dictionary per style, clips named `<low|med|high>_<left|center|right>[_up|_down]`, **all the same length and beat phase** (vanilla "right" naming unverified).
- Switch intensity without losing the beat: `local t = GetEntityAnimCurrentTime(ped, dict, lastClip)` then `TaskPlayAnimAdvanced(ped, dict, newClip, coords, rot, 4.0, 4.0, -1, 1, t, false, false, false)`.
- Facial mood per intensity (above); `ShakeGameplayCam("CLUB_DANCE_SHAKE", 0.5)` scaled by intensity.
- Intro: GTAO dictionaries ship an `intro` clip; kgv-dance played it and waited `GetAnimDuration(dict, "intro") * 1000` before the loop (commented out). rpemotes has **no intro→loop chain** (only `ExitEmote`). For a custom intro either ship a separate non-looping emote or script intro → loop yourself (design note, unverified in rpemotes).
- For custom variants: animate all intensities on the same beat grid (`dance_timing.py`), same loop length, so phase switching works.

## 8. scully_emotemenu equivalent
scully_emotemenu (GPL-3.0) entries carry `CanGroupEmote = true` and `Options.Flags.Loop` (MotionConvertToEmote README example). Field names beyond that example: unverified — read the user's installed scully config before writing entries.
