# Where the dance motion comes from — and what you may do with it

Pick the source before anything else: it decides the cleanup work, the quality ceiling and whether the result may go on a public (or Tebex-funded) server. Citations: `[videoId mm:ss]` = YouTube transcript time; repo/README links are in `sources.md`. "(paid)" / "(freemium)" = costs money or has a capped free tier; the user's rule is **free tools first, never recommend paid ones**.

## Decision table

| Situation | Best free route | Then |
|---|---|---|
| A common move (hip-hop idle, salsa step, robot, Gangnam-style) | **Mixamo** (free Adobe ID) | `fivem-animation` `references/mixamo-to-gta.md` (muto-ped-rig) |
| The user can film the dance, has 2–3 phones | **FreeMoCap** (AGPL-3.0) | `mocap-cleanup-blender.md` |
| Only one phone video (TikTok / K-pop practice clip) | **Open Mocap** (MIT, Blender ≤ 4.0) or **PoseCap** MediaPipe Lite path (GPL-3.0; pelvis-locked = fine in place) | heavy cleanup; or hand-key over the video |
| Signature choreography, stylised hits, a dance no mocap gets right | **Hand-key** on a video plane | `dance-animation-craft.md` |
| BVH (CMU, FreeMoCap) or MMD `.vmd` and no Blender | **MotionConvertToEmote** (MIT, untested) | ask before installing |
| Already-made free dances | check the licence first (table below) | rpemotes entry only |

## Mixamo
- Free with an Adobe ID; royalty-free use inside games; **no redistribution of the raw files** (already in `fivem-animation`).
- Tick **In Place** for travelling clips; it makes looping and combining easier [3NrsSdEUSWI 2:34]. Download later clips "without skin" — faster, same rig [3NrsSdEUSWI 9:10].
- Retarget to the GTA skeleton with muto-ped-rig (`fivem-animation`). Rokoko Studio Live's free plugin also retargets (Source = imported rig, Target = GTA skeleton, Build Bone List, fill missing pairs, **untick Auto Scale**) but needs a free Rokoko login [AUltLxjesXw 19:46–21:48], [f4G1DpHyEHc 3:43–4:06]. Hips are the usual failure point after retargeting [f4G1DpHyEHc 4:06].
- Some tutorials pose the GTA rig into a T-pose and apply it as rest pose before retargeting [f4G1DpHyEHc 1:45–2:53]. **Don't** — `fivem-animation` keeps the vanilla rest pose; muto-ped-rig handles T→GTA. Mention it only to explain why such tutorials break later.

## Free video → mocap

| Tool | Licence / cost | Input | What to know |
|---|---|---|---|
| **FreeMoCap** | AGPL-3.0, free | **2+ synced cameras** (phones OK) + printed ChArUco board | Single camera is "pretty useless" [Fp6wqaJA7qg 1:26, 2:35]. Calibrate by "painting" each view with the board; cameras must not move [Fp6wqaJA7qg 3:18–5:27]. Lay the board flat on the floor 3–4 s to find the ground [Fp6wqaJA7qg 4:44]. Clap to sync clips, put them in `synchronized_videos` [Fp6wqaJA7qg 4:44–5:50]. Enter the board square size in mm [bTMxTiZKyys 2:21]. Built-in Butterworth filter [bTMxTiZKyys 3:56]; multiprocessing can run out of RAM [bTMxTiZKyys 3:56]. Blender export needs **Rigify enabled** and the right Blender path [bTMxTiZKyys 4:43]. Recorded at 30 fps but Blender opened at 24 → set 30 [Fp6wqaJA7qg 8:52]. Bake the Skelly armature (Visual Keying, Clear Constraints) before retargeting [Fp6wqaJA7qg 10:42]. Install `pip install freemocap[cuda]` or `[cpu]`, Python 3.9–3.11 (README). "Very high quality" with a good set-up; occluded legs flicker [Fp6wqaJA7qg 9:14–10:20] |
| **Open Mocap** (open-mocap-blender) | MIT, free | 1 video, or front + side | MediaPipe; **Blender 4.0.0 or earlier only** (Python 3.10); its button installs mediapipe 0.10.14 / opencv / cvzone, may need two tries [NWfkF-sr-dY 1:06–4:22]. Body + hands. Retarget = Copy Rotation/Location constraints per bone, then bake [NWfkF-sr-dY 16:37–24:10]. Use a separate portable Blender 4.0 for capture, then move the baked action to your Sollumz Blender |
| **BlendArMocap** | GPL-3.0, free | webcam / video | MediaPipe → Rigify; legs "experimental", the author advises transferring without legs [U9G2VlG9HbA 0:23–1:30]. Weak for dances |
| **PoseCap** (CorridorTech) | GPL-3.0 add-on + Apache-2.0 libs, free, early preview | webcam / video | Windows, Blender 4.2+/5.x. **MediaPipe Lite** (CPU) backend is free of SMPL; **PEAR** backend (NVIDIA, driver R570+) needs SMPL-X → non-commercial. **Pelvis-locked: no world translation** — fine for in-place dances (README) |
| Blender motion tracking + IK | free | 1 video with markers | Track dots, Copy Location on IK bones [mVLFRoL_ur4 0:23–1:37]. Crude; not for dances |

### The SMPL / SMPL-X licence trap
Many of the best single-camera models are free to download but sit on the **SMPL / SMPL-X body models, licensed for non-commercial research only**:
- **GVHMR** — code itself: education/research/non-profit only, commercial prohibited; needs SMPL/SMPL-X downloads with a login [cg9DODLvLg8 1:55–7:54] (that video also sells a convenience package — paid).
- **WHAM**, **4D-Humans** — MIT code, but SMPL models under the research licence.
- **mixamo-llm-mocap** — MIT code, GVHMR + SMPL-X underneath (~8 GB VRAM NVIDIA).
- **PoseCap PEAR** backend — SMPL-X, commercial use needs a Meshcapade licence.

A FiveM server that sells the emote, puts it behind a Tebex package or takes donations is arguably commercial use (unverified legal reading — **tell the user, don't decide for them**). FreeMoCap (AGPL), Open Mocap (MIT), BlendArMocap (GPL) and PoseCap's MediaPipe Lite path avoid SMPL.

### Filming for any video mocap
Wide angle, whole body in frame the whole time, subject contrasts with the background, little motion blur (bright light, fast shutter), start and end in a T-pose [mifGsXHitvs 0:49–1:36]; no occlusion, synced cameras, sharp frames [bTMxTiZKyys 5:55]. Results are best when the feet stay roughly in place [mifGsXHitvs 1:12]. Best free quality: FreeMoCap with 3+ phones and good calibration [Fp6wqaJA7qg 10:20].

## No-Blender converters
- **MotionConvertToEmote** (Acc-Off, MIT, Windows exe, .NET 10; created 2026-09, untested): `bvh2ycd` / `vmd2ycd` (MMD dances) → `.ycd` + printed rpemotes/scully entries. Options `--root-motion fixed|mover|keep` (default fixed = in place), `--fps 30`, `--frames a-b`, `--mirror`, `--foot-lock` (thresholds 5 cm height / 0.3 m/s), `--no-loop`. Its docs: the `.ycd` carries no loop flag — loop lives in the Lua entry. "Restarting the resource is not enough: disconnect and connect again" after replacing a `.ycd`. Ask before downloading/running an unsigned exe.
- **EmotePreviewer** (Acc-Off, MIT): previews rpemotes/scully emotes, shared emotes on two peds, upper-body layering and props from the user's own GTA V Legacy; needs key files extracted from GTA5.exe by a separate KeyTool; unsigned exe; Enhanced not supported. Useful for pair offsets. Ask first.
- `gta.mikes.dev` web tool (Mic Scripts): upload a Mixamo FBX/GLB, download a `.ycd` [L5bFzuVOTkU 0:01–1:38]. Third-party upload; price/terms unknown (unverified). The video itself warns about copyright if you sell [L5bFzuVOTkU 0:23].

## Paid / freemium — name only if asked, never recommend
| Tool | Cost (checked 2026-11) |
|---|---|
| Rokoko Vision | Starter $0 = **30 s of AI processing per month**; paid tiers above (rokoko.com/pricing; page shows conflicting prices). TikTok-dance demo [LZVNvFwwwko 0:22–1:07] |
| DeepMotion Animate 3D | freemium ≈ 60 credits/month, ~20 s cap, free tier non-commercial (unverified) |
| Plask | free tier ~15 s/day (unverified) [yYWGujCApNc 0:22] |
| Move.ai / Move One | one-time free credits, then paid (unverified numbers) |
| QuickMagic | freemium, limits unknown (unverified) |
| LMX Animation Creator | paid one-time; in-server phone video → clip [v79GNf0A_EY 0:22–1:54] (marketing claims, untested) |
| BlendCap | $60 one-time, ≥ 6 GB VRAM [FyFarx7RjT8 0:00–0:22] |
| Mimic / "Mim AI", Rokoko Smartsuit ($3,495) | paid [Fp6wqaJA7qg 11:51], [e34NrjX0ssA 0:22] |
| Animation Snapper Pro, Animation Layers, Copy World Space (€4) add-ons | paid [n9v5U5WV8vA 0:00, 1:13], [HGNEfE_ZD3Y 7:19] — Blender's built-in Global Transform and NLA do the same jobs |

## Existing free dance packs — licence first
| Resource | Licence | Use |
|---|---|---|
| rpemotes-reborn built-in dances (~132, vanilla GTA clips) | GPL-3.0 script; clips are the game's own | free to use on FiveM |
| rpemotes-reborn `stream/[Custom Emotes]` (423 files from creators) | "added with the creators' permission … not profit from it, claim it, or reupload it elsewhere" | use inside rpemotes only; don't repackage |
| TradieKM/Griddy (`tradie-griddy@animation.ycd`) | **no licence** = all rights reserved | ask the author before shipping |
| Xinerki/kgv-dance (GTAO-style dance script) | no licence | read for ideas only |
| bcortezf/bnj_dances, Knaak53/KnatusDanceSystem | GPL-3.0 (2021, old `__resource.lua`) | usable under GPL; old format |
| PichotM/fivem-nightclub-ped | MIT | dancing NPC peds (not read) |
| Sims 4 / other games' dances (Sims 4 Studio → Blender → retarget [AUltLxjesXw 8:31–10:05]) | owner's terms (EA etc.) | ripping is distribution — don't ship |

Other dancers' videos are fine as **private reference** to animate from, not to redistribute ("not royalty free" [x91ANmbiA88 0:28]). Copying a famous choreography move-for-move for a paid product may be a copyright question (unverified legal reading) — flag it, don't rule on it.
