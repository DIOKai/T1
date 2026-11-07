# Music sync and loops that survive export

Citations: `[videoId mm:ss]` = transcript time; Blender manual = 5.2 pages (see `sources.md`); Sollumz = source at main @ 22b7947.

## 1. BPM → frames (GTA = 30 fps)

**frames per beat = fps × 60 / BPM = 1800 / BPM at 30 fps.** One 8-count = 8 beats = 2 bars of 4/4. A loop of one or two 8-counts is the natural emote unit (dance-practice recommendation; no captioned source).

| BPM | frames/beat | one 8-count | shortest loop that is whole beats AND whole frames |
|---:|---:|---:|---|
| 90 | 20 | 160 | 1 beat = 20 f |
| 100 | 18 | 144 | 1 beat = 18 f |
| 105 | 17.14 | 137.1 | 7 beats = 120 f |
| 110 | 16.36 | 130.9 | 11 beats = 180 f |
| 120 | 15 | 120 | 1 beat = 15 f |
| 125 | 14.4 | 115.2 | 5 beats = 72 f |
| 128 | 14.0625 | 112.5 | **16 beats (two 8-counts) = 225 f** |
| 130 | 13.85 | 110.8 | 13 beats = 180 f |
| 140 | 12.86 | 102.9 | 7 beats = 90 f |
| 150 | 12 | 96 | 1 beat = 12 f |
| 160 | 11.25 | 90 | 4 beats = 45 f |

**Rule:** the loop length must be a whole number of beats **and** a whole number of frames, or every repeat drifts further off the music. At 128 BPM one 8-count is 112.5 frames — impossible — so the loop is two 8-counts = 225 frames. A prime tempo like 127 BPM needs 127 beats (60 s) for an exact loop; pick 16 beats = 226 or 227 frames and accept a small drift, or animate to a nearby tempo.

`scripts/dance_timing.py` does all of this:
```
py -3 scripts/dance_timing.py 128                     # shortest loop + beat table (counts 1-1 … 2-8)
py -3 scripts/dance_timing.py 98 --bars 4             # 16 beats at 98 BPM
py -3 scripts/dance_timing.py 128 --beats 16 --markers-json beats.json
py -3 scripts/dance_timing.py 128 --check 224         # exit 1: 1 f short, half a beat off after 8 loops
```
`--check FRAMES` takes the loop period = last frame − first frame when the last frame repeats the first pose (= Sollumz clip Duration × 30).

Markers sit on whole frames only (Blender manual, animation/markers), so at 128 BPM the beats fall 14/14/14/14/14/14/14/15 frames apart — round each beat to the nearest frame (the script does).

Load the JSON as timeline markers (paste in Blender's Python console; through the `blender` MCP only after asking):
```python
import json, bpy
d = json.load(open(r"C:\path\beats.json", encoding="utf-8"))
sc = bpy.context.scene
sc.render.fps, sc.render.fps_base = 30, 1.0
sc.frame_start, sc.frame_end = d["start_frame"], d["end_frame"]
for m in d["markers"]:
    sc.timeline_markers.new(m["name"], frame=m["frame"])
```

### 60 fps tutorials
Some creators animate at 60 fps and set Duration = frames / 60 [e34NrjX0ssA 7:43, 22:15], [uch19GzxrUk 1:32, 9:23]; it plays at the right speed because Sollumz derives the rate from Duration. Not wrong, just twice the data and it no longer matches vanilla clips or `check_anim_resource.py`. This skill stays at 30 fps. (Unverified on current Sollumz.)

## 2. Getting the beat into Blender
- Put the track in the scene: Video Sequencer sound strip (or Add ▸ Speaker). Sound strips can show a **waveform** (Sequencer overlay / strip "Display Waveform") (manual: sequencer sound strip).
- Turn on audio sync so scrubbing plays the song in time: Timeline ▸ Playback ▸ Sync "Sync to Audio" + "Scrubbing" (menu names from memory — unverified in the 5.2 manual).
- Tap beats live: press **M** during playback to drop markers (manual: "Markers can also be added during playback"). Markers show in Graph Editor, Dope Sheet, NLA and Sequencer.
- Snap keys onto beats: Key ▸ Snap ▸ **Selection to Nearest Marker** (manual: graph editor editing "Snap").
- See the kick drum: Graph Editor ▸ Channel ▸ **Bake Sound to F-Curves** onto a dummy property; raise Attack to ~0.1 to reduce flicker [eFWN3x84NcU 0:46–1:22]. Use it to *see* beats, not to drive bones.
- Visual metronome (no maths): a ball bouncing on the beat beside the character; hit the down pose on the ball's contacts [xn-oiDILZg4 2:49–4:38].
- A "BPM Marker Tool" add-on exists [ymfAsbPAmrY, no captions] — licence/price unknown (unverified); the JSON above does the same for free.
- The song is for timing only — it never reaches the `.ycd` (see §5).

## 3. Making the loop seamless in Blender
1. **Mirror half (symmetrical moves).** Key pose A at frame 0, copy it, go to the half point and **Ctrl+Shift+V (Paste Flipped)**; bones must be named `.L/.R` to flip [NHQtU2v3zBU 8:43–10:11, 11:59]. **GTA bone names don't flip:** tested in Blender 5.2, `bpy.utils.flip_name("SKEL_L_Hand")` returns `SKEL_L_Hand` unchanged (same for `SKEL_R_UpperArm`, `PH_L_Hand`, `RB_L_ArmRoll`), so Paste Flipped won't swap sides on the GTA rig. Do the mirrored half on a `.L/.R` source rig (Mixamo/Rigify control rig) before retargeting, or copy the poses side to side by hand. Don't rename GTA bones to make it work.
2. **Cycles F-modifier** to preview the loop: Graph Editor ▸ Channel ▸ Extrapolation ▸ **Make Cyclic** (Shift+E), or Sidebar ▸ Modifiers ▸ Add **Cycles** [NHQtU2v3zBU 19:35–21:21], [AvKf22KPbZs 1:49, 5:07]. Cycles must be the first modifier; Count 0 = infinite. With both ends on Repeat Motion the curve is "trivially cyclic": Bézier handles adapt across the seam and **Cycle-Aware Keying** can be turned on (manual: fcurves/modifiers). Use that, not "Repeat Mirrored" (mirrored playback makes a loop that only exists through the modifier — see §4).
3. **All channels start and end on the same frames**, or they drift apart [NHQtU2v3zBU 21:43–22:04]. Channels without keys get no modifier — key them too [NHQtU2v3zBU 23:10].
4. **Check the seam:** jump first/last frame with Shift+← / Shift+→ [pEg04DFV4kw 0:45–1:06]; play the loop several times with the song.

### The duplicate end frame
If frame 0 and the last frame both hold the same pose and both play, the pose holds for two frames — a tiny hitch. One tutorial starts keys at frame 1 for that reason [DqjcLN_jtKc 1:15]; another sets start to 1 "to avoid duplicate frames" [pEg04DFV4kw 0:45–1:06]. Sollumz exports `ceil(duration + 1)` frames, i.e. both ends inclusive (animationhelper.py `get_action_export_frame_count`). Whether GTA's looping wrap shows that duplicate as a hitch is **unverified** — if a loop "bumps" in game, export a second version ending one frame earlier (last = first − 1 frame) and compare.

## 4. Bake before export — loops that survive Sollumz
Sollumz samples each F-curve with `fcurve.evaluate()` over **`action.frame_range` of one action only** (ycdexport.py `sequence_items_from_action`). Consequences, **inferred from the Sollumz source + a headless Blender 5.2 test, not yet confirmed in game**:
- A Cycles modifier's repeats **outside** the keyed range are not exported. Verified in Blender 5.2: an action keyed 0–20 with a Cycles modifier reports `frame_range = (0, 20)`, so a loop keyed 0–20 with "Repeat Mirrored" would export only the first half, not the 40-frame dance.
- **NLA strips and tracks are not exported** — Sollumz reads one action. Combine clips in the NLA, then bake.
- Whether in-range modifiers (e.g. Noise) are applied by `evaluate()` — likely yes, unverified. Bake anyway.
- An unbaked animation has also shown unwanted scaling in game while the baked copy played right [DqjcLN_jtKc 2:31–11:21].

**How:** `scripts/bake_loop.py` evaluates the current animation (action + modifiers + NLA + constraints, visual transform) frame by frame over the full loop, writes one key per frame into a new action `<name>_baked`, sets last = first, keys rotations as quaternions, keys location only on bones that really move (normally `SKEL_ROOT`), mutes the NLA tracks it baked from and keeps the original action. Tested headless on Blender 5.2.3 (`scripts/test_bake_loop.py`: Cycles 20 → 40 frames, NLA repeat, seam fix). Built-in alternative: Pose ▸ Animation ▸ **Bake Action** (Visual Keying, Clear Constraints, frame range = whole loop, Bake Data = Pose) — then delete the Cycles modifiers and point the Sollumz Animation at the baked action.

After baking: Sollumz Animation ▸ Action = the baked action; clip Duration = loop frames / 30 (e.g. 225 / 30 = 7.5 s); run `py -3 scripts/dance_timing.py <BPM> --check <frames>`.

## 5. Music in game — what an emote can't do
- **The `.ycd` carries no audio.** rpemotes has no sound field in AnimationOptions (types.lua); a dance emote is silent.
- Players dance **out of phase** anyway: shared emotes start after `EmoteCancel(); Wait(300)` on each client separately (Syncing.lua) and group emotes start on a 10 s countdown over the network — not frame-locked (exact drift unverified). A perfect beat loop still matters: it keeps *each* dancer on their own beat with a club speaker or the user's own music.
- Synced music needs a separate audio resource (e.g. xsound or NUI audio — not researched, unverified) plus the music's own licence. Ripping a song from YouTube for a server is a copyright issue — say so, don't help work around it. For the licensing side, `sound-and-music-sync` (ask first).
