---
name: fivem-dance
description: Use when the user wants a custom dance emote for GTA V / FiveM — a dance loop, K-pop, TikTok, hip-hop or shuffle moves, a dance copied from a phone or reference video, dance mocap (FreeMoCap, Mixamo, BVH, MMD), loops synced to a song's BPM, glow-stick or other prop dances, two-person or group dances in rpemotes — or when a dance drifts off the beat, bumps at the loop point, exports at half length, or the legs don't move. Triggers include 跳舞, 舞蹈动作, 自定义舞蹈, 双人舞, 群舞, 荧光棒, 卡点, 节拍, 动捕, mocap, rpemotes 舞蹈, dance emote.
---

# FiveM custom dances

A dance must **groove**, **loop** without a hitch and stay **on the beat** every repeat. The shared pipeline (skeleton, Sollumz, CodeWalker, `stream/`, `check_anim_resource.py`) lives in `fivem-animation` — read it first; this skill owns the dance-specific parts.

Ask before installing anything (mocap tools, converters, muto-ped-rig) or using the `blender` MCP. `scripts/dance_timing.py` is local arithmetic — run it directly.

## 1. Choose the motion source
| Source | Cost / licence | Best for |
|---|---|---|
| Mixamo | free; no raw-file redistribution | common moves (`fivem-animation` `mixamo-to-gta.md`) |
| FreeMoCap | free, AGPL-3.0; **2+ cameras** + ChArUco board | the user's own dance, best free quality |
| Open Mocap / PoseCap MediaPipe Lite | free, MIT / GPL-3.0; one video | single phone (Blender ≤ 4.0 / pelvis-locked) |
| Hand-key over the video | free | signature choreography, sharp hits |
| Existing packs | check licence | no licence = ask the author |

**Licence trap:** GVHMR, WHAM, 4D-Humans, mixamo-llm-mocap and PoseCap's PEAR backend use **SMPL / SMPL-X = non-commercial only**. Selling the emote / Tebex is arguably commercial (unverified legal reading — tell the user, don't decide). **Paid/freemium, don't recommend:** Rokoko Vision (free 30 s/month), DeepMotion, Plask, Move.ai, QuickMagic, LMX, BlendCap. Details: `references/motion-sources-and-licences.md`.

## 2. Workflow
1. **Tempo.** `py -3 scripts/dance_timing.py <BPM>` → frames per beat, the shortest loop that is **whole beats AND whole frames**, beat markers (`--markers-json`). Loops are one or two 8-counts.
2. **Reference.** The video (private reference) on a plane via **Images as Planes**, scene at **30 fps**, song as a sound strip, beat markers loaded.
3. **Motion.** Mocap: jitter first (Butterworth Smooth keeps the hits), then contacts (Global Transform ▸ Paste and Bake), then creative fixes on an NLA Combine layer (`references/mocap-cleanup-blender.md`). Hand-key: poses where a part starts, stops or turns; gaps ≤ 4 frames; blocking → spline → polish (`references/dance-animation-craft.md`).
4. **Groove pass.** Hips = bouncing ball, down on the beat; ease into hits, snap out; arms/head ~2 frames after the hips; chest counters the hips, shoulders level.
5. **Loop.** First pose = last pose; all channels start/end on the same frames; preview with a Cycles modifier (trivially cyclic + Cycle-Aware Keying). Paste Flipped does **not** swap GTA `SKEL_L_`/`SKEL_R_` bones (tested) — mirror on a `.L/.R` source rig or by hand.
6. **Bake to one action.** Sollumz samples only `action.frame_range` of one action, so Cycles repeats and NLA strips are dropped (inferred from Sollumz source + a Blender 5.2 test; **needs an in-game test**). `scripts/bake_loop.py` bakes action + modifiers + NLA + constraints over the full loop, last = first, keeps the original. Then `dance_timing.py <BPM> --check <frames>`.
7. **Export** as in `fivem-animation` (Clip Hash = clip name, Duration = frames / 30, in place). Fast preview: a `.ycd` inside an **RPF archive** under `mods\update\x64\dlcpacks\…` plays in CodeWalker's Ped Viewer; a loose `.ycd` isn't listed.
8. **rpemotes entry**, then test.

| BPM (30 fps) | frames/beat | exact loop |
|---:|---:|---|
| 100 | 18 | 8 beats = 144 f |
| 120 | 15 | 8 beats = 120 f |
| 128 | 14.0625 | 16 beats = 225 f (8 beats = 112.5 ✗) |
| 140 | 12.86 | 7 beats = 90 f |

## 3. rpemotes entries
- Solo: `CustomDP.Dances["name"] = { "dict", "clip", "Label", AnimationOptions = { onFootFlag = AnimFlag.LOOP } }`.
- `AnimFlag.LOOP` (1) = full body, ped stands still. `AnimFlag.MOVING` (51) = **upper body only**, legs walk or take another dance's legs.
- `EmoteLoop` / `EmoteMoving` are **deprecated** (tutorials still print them).
- Glow sticks: `Prop = 'ba_prop_battle_glowstick_01', PropBone = 28422` (right hand) + `SecondProp…, SecondPropBone = 60309` (left), `onFootFlag = AnimFlag.MOVING`.
- Pair: `CustomDP.Shared` with the partner emote as 4th element; `SyncOffsetFront` (default 1.0), `SyncOffsetSide`, `SyncOffsetHeight`, `SyncOffsetHeading` (default 180); the **initiator's** offset is used. `/nearby <emote>` → partner presses Y / L.
- Group: `/gemote <emote>` (radius 5–10 m, 10 s countdown) with a Dances clip; shared emotes can't be group emotes.
- Emotes carry **no music**; players start out of phase.

## 4. Test checklist
- [ ] `dance_timing.py --check` OK; the baked action is the Sollumz Animation's action.
- [ ] `check_anim_resource.py` (`fivem-animation`) clean; Ped Viewer: no float or teleport.
- [ ] Rejoin. Loop 10+ times on male **and** female peds: no seam bump, hands clear of the body, feet planted.
- [ ] MOVING version walks; props sit in the hands; pairs tested with two clients, each role initiating.

## 5. Common mistakes
| Symptom | Cause → fix |
|---|---|
| Drifts off the beat after a few loops | not whole beats + whole frames (224 instead of 225 at 128 BPM) → `--check` |
| Only the first half plays in game | Cycles "Repeat Mirrored" / NLA not exported → `bake_loop.py` |
| Bump at the loop point | first ≠ last, or duplicated end frame → bake last = first; try one frame shorter (unverified which GTA prefers) |
| Legs don't dance | `AnimFlag.MOVING` → LOOP |
| Ped teleports/floats at start | root not centred / feet off the ground line → fix root curves |
| Partners collide | root motion in paired clips → keep both in place |

## References
`references/`: `motion-sources-and-licences.md` (sources, SMPL, packs), `music-sync-and-loops.md` (BPM, markers, seam, baking, music), `dance-animation-craft.md` (reference, passes, groove, styles), `mocap-cleanup-blender.md`, `rpemotes-dances-and-shared.md` (entries, flags, props, GTAO-style system), `group-and-pair-dances.md`, `sources.md`. Scripts: `dance_timing.py`, `bake_loop.py` (+ tests).

Related (ask first): `fivem-animation`, `motion-design`, `blender-animation-rigging`, `anthropic-skills:learn`, `sound-and-music-sync` (music licensing).
