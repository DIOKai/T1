# Dance animation craft — reference, passes, groove

How animators make a dance read as dancing. Citations: `[videoId mm:ss]`. The GTA rules (30 fps, quaternions, rotations on limbs, vanilla rest pose) come from `fivem-animation`; this file is the art side. For general timing/spacing/easing theory use `motion-design`.

## 1. Reference first
- Film yourself or a friend who can actually do the move, from the camera angle you'll judge from; include every beat and "thinking" moment; use real weight and props; "if you don't look dumb enough, go harder" [zAUmgEzR1xA 0:26–3:05, 8:06–8:51]. Speeding up or slowing reference is fine [zAUmgEzR1xA 7:44].
- Dance **to the actual song at the actual spot** in the track while filming; flip some takes so not every move faces one way [nmg21jX9IpE 0:45–1:09].
- Put the footage on a plane: File ▸ Import ▸ **Images as Planes** with the video, scale it to the character [nmg21jX9IpE 1:31]. Set the scene to 30 fps first; trim/re-time the clip so the music beat lands on the markers from `dance_timing.py`.
- A K-pop / TikTok video the user didn't make is **private reference only** — fine to animate from, not to ship ("not royalty free" [x91ANmbiA88 0:28]).

## 2. Motion matching on the video plane
- Key poses = where a body part **starts, stops or changes direction**; mark them with keys on one root control so you can jump between them; for dance never leave gaps > 4 frames [nmg21jX9IpE 1:54–2:39].
- Extremes of the centre of gravity and foot contacts are the keys; contacts are breakdowns [UkWnwHwMapQ 0:44–3:01].
- Pose A, then C, let Blender give B and adjust (bouncing-ball logic) — halves the work [nmg21jX9IpE 3:45–4:31]. Match the first pose most carefully [nmg21jX9IpE 3:01] — in a loop it is also the last.
- Then leave the reference: hold the cool poses longer, snap faster between them for a stylised feel; real motion never fully stops [UkWnwHwMapQ 8:25–9:55].
- "On twos" (key every 2nd frame, Constant interpolation) is a style [nmg21jX9IpE 4:55–5:19]; GTA peds usually look better smooth (opinion, unverified).

## 3. Passes
Blocking (key poses, popping) → blocking plus (breakdowns, arcs) → spline (Blender fills in; usually looks worse at first) → polish (arcs, head/arm overlap, personality). Popular game emotes take the real dance "then just enhance it" [H08RNC0rB3U 0:51–5:08].
- Hips are a bouncing ball: clean the hip arc first, then the torso/head that drags after it [o-FWoJs3GZE 5:51–8:40]. On the GTA rig the hips are `SKEL_ROOT` (`SKEL_Pelvis` is never keyed — `fivem-animation`).
- Tone down a heavy head if the weight feels wrong, even if it matches the reference [nmg21jX9IpE 5:43].
- Build a basic bob loop first, use it as the timing layer for the real moves [xn-oiDILZg4 7:03–8:59]. A long loop made of several moves must still return to frame 0's pose [xn-oiDILZg4 8:36–9:45].

## 4. What makes it groove
| Principle | How | Source |
|---|---|---|
| Groove = bounce on every beat | hips/torso are "a bouncing ball but on beat"; down pose **on** the beat | [xn-oiDILZg4 0:54] |
| Hit the beat | ease **into** the down, snap **out** | [xn-oiDILZg4 4:44–6:16] |
| Weight shift | start asymmetrical, bend knees, turn the hips, then mirror | [NHQtU2v3zBU 10:11–11:17] |
| Counter-rotation | hips one way, chest/head counter, shoulders level | consistent with the LESSONS female-gait rule |
| Overlap / follow-through | arms and head **~2 frames after** the hips; do it last (messy dope sheet) | [NHQtU2v3zBU 24:38–25:42, 31:12] |
| Gravity | arms rise when the body dips | [xn-oiDILZg4 5:08] |
| Easing per style | steep curve = fast; handles scaled to 0 = robotic; sharper middle = snappier | [NHQtU2v3zBU 26:05–27:31] |
| Readability | don't let limbs or key shapes vanish into the body mid-swing | [MBIypQzs1F0 4:14] |
| Hands over head | if arms go through the head, scale the arm poses outward | [NHQtU2v3zBU 30:28] |

Overlap after the loop is finished: Graph Editor ▸ Key ▸ Blend ▸ **Time Offset** shifts a dense (baked/mocap) curve in time and wraps it — offset arms/head inside a loop without breaking the seam (Blender manual, fcurves/editing).

## 5. Style notes
Captioned 3D tutorials were found only for a few styles; the rest are **experience-based recommendations (unverified)**.
- **Floss / Fortnite-style:** stiff arms read realistic, bendy arms add appeal [H08RNC0rB3U 2:26].
- **Shuffle:** a pose every 10 f, then the mirrored half, then retimed to 5 f per pose, ~35–40 f cycle [x91ANmbiA88 17:32–19:41]. At 30 fps and 128 BPM a running-man step per beat is ~14 f.
- **K-pop point choreography (recommendation):** sharp hits on the beat, short 2–4 f holds, clean silhouettes facing camera, arms lead, small knee bounce underneath. One or two 8-counts.
- **Hip-hop groove (recommendation):** constant soft bounce (down on the beat or on the "and"), relaxed arms with 2–3 f overlap, chest pops as accents.
- **TikTok loop (recommendation):** 1–2 8-counts, upper body does the "trend", feet mostly planted — candidate for MOVING (upper body only) in rpemotes.
- **Pair / ballroom:** no captioned 3D source found; see `group-and-pair-dances.md`.
- **Female ped:** follow LESSONS: hips tilt with chest counter so the shoulders stay level, chest up, arms close to the body swinging mainly from the elbow, wrists half a beat late; don't make the whole body sway side to side. Test the clip on `mp_f_freemode_01` too — hands through the hips/chest is the usual fix [YKhP2QfULDw 1:29].

## 6. GTA limits while animating
- Rotations only on limbs, in a sane range: extreme rotations "will definitely break" the skeleton in game [Dc9E53_Y4Xw 9:40]. Start at frame 0 [Dc9E53_Y4Xw 9:18].
- In place: no horizontal travel on the root; feet on the ground line; the first pose centred (otherwise the ped teleports or floats when the emote starts) [e34NrjX0ssA 15:12–17:54].
- Travelling dance (a shuffle that moves): travel on the mover (`fivem-animation`), constant speed (Linear), linear foot contacts [HGNEfE_ZD3Y 2:14–3:18]; measure distance per cycle once [HGNEfE_ZD3Y 5:09]. Most emote dances should stay in place.
- Facial: animate the body only; add a vanilla facial mood on top in script (`rpemotes-dances-and-shared.md` §6). Custom face clips are unverified.
