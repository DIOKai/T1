# Cleaning dance mocap in Blender (free, built-in tools)

For Mixamo, FreeMoCap, Open Mocap, PoseCap or any BVH. Retargeting to the GTA skeleton itself is in `fivem-animation` (`references/mixamo-to-gta.md`). Citations: `[videoId mm:ss]`; Blender manual 5.2 pages are listed in `sources.md`.

## Order of work
Sir Wade's three kinds of fix [YKhP2QfULDw 0:21] — do them in this order:
1. **Functional:** jitter and spikes.
2. **Technical:** contacts — feet on the floor, hands not through the body, root centred.
3. **Creative:** poses, hits, style — on a separate layer so the mocap stays intact.

## 0. Before cleaning
- Scene at 30 fps (FreeMoCap opened at 24 in one test — set 30 [Fp6wqaJA7qg 8:52]).
- Trim the T-pose frames at the start of the clip [e34NrjX0ssA 19:04].
- Root sanity for an in-place dance: move the root's X/Y/Z F-curves in the Graph Editor so the feet stand on the GTA ground line and the first pose is centred — otherwise the ped teleports or floats when the emote starts [e34NrjX0ssA 14:49–17:54].
- Mute channels one by one to find which curve causes an odd motion [YKhP2QfULDw 4:52].

## 1. Jitter and spikes (Graph Editor ▸ Key)
| Tool | Use | Notes |
|---|---|---|
| **Butterworth Smooth** | first choice for dances | "ideal for smoothing large amounts of data because it preserves the peaks" (manual) — keeps the hits. Frequency Cutoff, Filter Order, Samples per Frame (2 for 60 fps keys in a 30 fps scene), Blend, Blend In/Out |
| Smooth (Gaussian) | softer noise | Factor, Sigma, Filter Width; up to 100 % if needed [mifGsXHitvs 5:07] |
| Smooth (Legacy), Alt+O | quick pass | "quite a strong smoothing", never changes first/last key; max ~2–3 passes — more removes detail [e34NrjX0ssA 18:17–19:04] |
| Delete 2–3 keys | an isolated spike | then let the curve interpolate [n5o0GS4ZYLQ 1:50–2:14] |
| Clean Keyframes (X) / Density ▸ Decimate | fewer keys to edit | after smoothing [n5o0GS4ZYLQ 0:46]; Decimate by Ratio / Allowed Change |
| Bake Keyframes (Shift+Alt+O) | back to one key per frame | before export (or `scripts/bake_loop.py`) |

Butterworth vs Gaussian for dance: Butterworth keeps the sharp beat hits, Gaussian rounds them (recommendation from the manual's description; compare both on the hips curve).

## 2. Feet and contacts
- Mocap is FK only, so the feet aren't locked; the strongest fix is FK → IK with a control rig, then fix on top [YKhP2QfULDw 6:48–8:18].
- Free built-in route: **3D Viewport ▸ Sidebar ▸ Animation ▸ Global Transform** — at the contact frame Copy the foot's world transform, then **Paste to Selected Keys** or **Paste and Bake** over the contact frames; "Mirrored" handles the other foot (manual: copy_global_transform). Same idea with auto-key copy/paste per frame [HGNEfE_ZD3Y 7:19–9:34]. (The €4 Copy World Space add-on is not needed.)
- Contact segments Linear [HGNEfE_ZD3Y 2:35–3:18].
- Foot-lock timing (any tool, incl. MotionConvertToEmote `--foot-lock`): start the lock when the foot lands, end it just after the heel lifts; too long = foot stuck, missing = jitter [e34NrjX0ssA 4:35–6:57].
- Pivot idea (free concept, the presenter's tool is paid): pivot on the toe/ball, keep rotation, remove only travel; ease out on a layer [n9v5U5WV8vA 2:11–6:35].
- Travelling clips: feet slide when walking motion is converted "fixed" — use the mover (MotionConvertToEmote README); see `fivem-animation` for mover rules.

## 3. Fix layer (non-destructive)
Push the mocap down to an NLA strip, add a track above with blend **Combine**, and key corrections there [mifGsXHitvs 5:55–6:42], [YKhP2QfULDw 1:52–2:59]. Typical small fixes: hands through the body or hips (worse on the female ped) [YKhP2QfULDw 1:29], arms through the head (scale arm poses outward) [NHQtU2v3zBU 30:28], hips wrong after retarget [f4G1DpHyEHc 4:06].

**Sollumz exports only one action** — bake the strip + layer into one action before export (`scripts/bake_loop.py`, which mutes the NLA tracks it baked; or Pose ▸ Animation ▸ Bake Action with Visual Keying). See `music-sync-and-loops.md` §4.

## 4. Props in the hands
Real grips loosen and re-adjust; don't freeze one hand pose with a constraint [YKhP2QfULDw 8:41–9:49]. For glow sticks/fans the prop itself is attached in rpemotes (`rpemotes-dances-and-shared.md` §3); animate the fingers closed around where it will sit.

## 5. Making the mocap a loop
1. Find two similar poses one or two 8-counts apart (`dance_timing.py <BPM>` gives the frame distance).
2. Trim the clip to that range, shift it to start at frame 0.
3. Blend the seam: NLA — two copies overlapping a few frames with **Auto Blend** [3NrsSdEUSWI 11:09–15:24]; or key the last frame = first and fix the last 4–8 frames on the Combine layer.
4. Bake the full range into one action, last = first (`bake_loop.py` does both and reports the seam error before fixing).
5. `dance_timing.py <BPM> --check <frames>`.

## 6. Combining clips (NLA)
Push Down each action to a strip; arrange on tracks; Strip ▸ Action Clip ▸ **Repeat**; set Extrapolation from Hold to Nothing if the next strip won't start; overlap strips and use **Auto Blend** [3NrsSdEUSWI 11:09–15:24]. Playback Scale changes speed [HGNEfE_ZD3Y 5:32] — after changing speed, re-check the beat. Then bake into one action.
