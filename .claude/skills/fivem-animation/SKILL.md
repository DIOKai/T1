---
name: fivem-animation
description: Make and ship custom GTA V / FiveM character animations — emotes, dances, poses, idle loops, prop animations — from Blender through Sollumz (.ycd.xml) and CodeWalker (.ycd) into a FiveM resource, and play them with rpemotes-reborn custom emotes, TaskPlayAnim or ox_lib. Covers the GTA ped skeleton and bone tags, 30 fps, quaternions, baking IK/constraints, mover/root motion, clip Hash/Duration/Rate, AnimationListCustom.lua, prop attachment, walk styles, stream_enhanced, and why an animation T-poses, slides or doesn't play. Use whenever the user wants to animate a GTA character, make or add an emote, convert a Mixamo/mocap animation for FiveM, fix a .ycd, or learn Blender animation for FiveM — even if they only say "做个动作", "自定义表情", "emote", "ycd", "动画不动", "T-pose".
---

# FiveM custom animations

A custom animation reaches the game through a short, unforgiving chain: **Blender armature → Sollumz clip dictionary (.ycd.xml) → CodeWalker compile (.ycd) → `stream/` of a resource → `RequestAnimDict` + `TaskPlayAnim`** (or an rpemotes entry). Almost every failure is silent — no error, the ped just T-poses, freezes a limb, slides, or nothing plays — and comes from one of a few causes: wrong bone tags, non-quaternion or unbaked channels, a wrong frame rate, an empty clip Hash, or a name mismatch between the file, the clip and the script. The workflow is built to avoid exactly those.

Read the reference you need:
- `references/skeleton-and-authoring.md` — ped skeleton, bone tags, 30 fps, quaternions, baking, mover/root motion, looping, retargeting tools and licences.
- `references/sollumz-export.md` — clip dictionary objects, every field that matters, compiling with CodeWalker.
- `references/playing-and-rpemotes.md` — streaming, natives and flags, ox_lib, rpemotes custom emotes, props, shared emotes, walk styles.
- `references/troubleshooting.md` — symptom → cause → fix.

Related skills: `motion-design` (timing, spacing, easing, the 12 principles), `blender-animation-rigging` and `animation` (Blender keyframing, Graph Editor, NLA), `anthropic-skills:learn` (teaching), muto-atlas `/anim` (vanilla dictionary/clip names, real durations, skeleton bones — needs its data layers built first; ask before `/asset-setup`).

## Teaching mode

When the user is learning, teach one step at a time and let them do it in Blender: explain the why, give the exact menu path or setting, ask them to confirm or send a screenshot, then move on. Start with a small first win — a 2-second upper-body wave loop on the freemode male — before full-body or moving animations. Use `motion-design` for the art side (anticipation, follow-through, arcs, ease) so the result looks good, not just valid.

Driving Blender through the `blender` MCP (`execute_blender_code`) is allowed only after asking, per the project rules.

## Workflow

### 1. Set up (once)
- Blender ≥ 4.2 with Sollumz (free, GPL-3) and CodeWalker (free) on the user's PC.
- Extract the base skeleton from **their own** game with CodeWalker: `mp_m_freemode_01.yft` (and `mp_f_freemode_01.yft` to test female). Import it with Sollumz. Never build or rename ped bones by hand — Sollumz keys channels by **bone tag**, and a hand-made bone gets an automatic hash instead of GTA's tag (e.g. `SKEL_R_Hand` would become 22798 instead of 57005), so the animation silently does nothing.
- To study or edit a vanilla clip, export the `.ycd` to XML in CodeWalker first; Sollumz can't read binary `.ycd` (it imports an empty scene).

### 2. Scene rules before animating
- Scene frame rate **30 fps** (Sollumz computes durations from it; GTA clips are 30 fps).
- Pose bones in **Quaternion** rotation mode — Euler channels are skipped on export.
- Meters, Z-up, ped facing −Y in rest pose; keep the vanilla rest pose.

### 3. Animate
- Rotate limbs; keep position keys off limbs (helps male/female compatibility).
- Hips: animate `SKEL_ROOT`. Travel across the ground goes on the **mover** — the armature object's Delta Transform — or keep the clip in place (emotes usually are).
- Loops: first and last pose identical.
- If you used IK, constraints or drivers: **bake** them (Pose ▸ Animation ▸ Bake Action, Visual Keying, Clear Constraints, quaternion rotation). The exporter only reads keyframed F-curves.
- Retargeting a Mixamo/mocap clip: see `references/skeleton-and-authoring.md` (free options, licences).

### 4. Export with Sollumz
Clip Dictionary ▸ Animation (Hash, Action, **Target = the armature data**) ▸ Clip (**Hash = the clip name you'll play**, Duration = (end − start) / 30, linked animation range). Export `.ycd.xml`. Details and pitfalls: `references/sollumz-export.md`.

### 5. Compile and name
CodeWalker ▸ RPF Explorer ▸ Import XML turns `<dict>.ycd.xml` into `<dict>.ycd`. The **file name is the dictionary name** — use lowercase, no spaces, unique (e.g. `dio@wave.ycd` → dict `dio@wave`).

### 6. Ship and play
- rpemotes: put the `.ycd` in `rpemotes/stream/[Custom Emotes]/<folder>/`, add an entry to `client/AnimationListCustom.lua`, keep a `BackUpAnimationListCustom.lua` copy (updates overwrite the file).
- Own script: put it in the resource's `stream/` (no `data_file` needed), then `RequestAnimDict` → `TaskPlayAnim` → `RemoveAnimDict`. Flags and examples: `references/playing-and-rpemotes.md`.
- If the resource has `stream_enhanced/`, put a copy there too (the Enhanced client reads only that folder).
- After adding a new `.ycd`, rejoin the server (reported that a resource restart isn't enough).

### 7. Check
Run `python .claude/skills/fivem-animation/scripts/check_anim_resource.py <resource-or-export-folder>` (local, read-only, Python only). It catches: empty/duplicate clip Hash, clip↔animation links, Rate ≠ 1 (wrong speed), animations not at 30 fps, `.ycd.xml` left in `stream/`, uncompiled/corrupt `.ycd` (no RSC7 header), bad names, missing `stream_enhanced` copies, duplicate dictionaries, and rpemotes entries whose clip isn't in the matching `.ycd.xml`. Point it at both the export folder (the `.ycd.xml`) and the resource. Then test in game on male and female peds.

## Ground rules
- Don't invent bone tags, flags, natives or rpemotes option names — use the reference tables or the sources they cite.
- Free tools only. Auto-Rig Pro and AI video-to-animation services (DeepMotion, Move.ai, Plask, Rokoko Vision) are paid/credit-based — don't recommend them. Rokoko's free Blender plugin needs an account login for retargeting; muto-ped-rig and FreeMoCap are free but install software — ask first.
- Licences: animations ripped from other games or taken from paid/"personal use" packs stay under their owners' terms; streaming them to a public server is distribution. Mixamo allows use in games but forbids redistributing raw files. Prefer the user's own work.
