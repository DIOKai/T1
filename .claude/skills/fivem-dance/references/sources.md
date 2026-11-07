# Sources

Researched 2026-11-08: YouTube subtitles only (yt-dlp `--skip-download`), official docs, public GitHub READMEs and source text. Nothing installed. Notes are original summaries. Citation format in the other files: `[videoId mm:ss]` = start of the ~20 s caption chunk.

## Videos
| ID | Title (channel) | Used for |
|---|---|---|
| Dc9E53_Y4Xw | [Tutorial] Create custom GTAV animations using Sollumz Blender (Anurag Verma) | Sollumz chain, frame 0, extreme rotations, CodeWalker Ped Viewer preview |
| AUltLxjesXw | How to Create & Retarget The Sims 4 to FiveM Ready Dance Animations (Eishabeesha) | Rokoko retarget, preview from a mods RPF |
| f4G1DpHyEHc | How to retarget animations for GTA 5 / FiveM (ook_3D) | Rokoko retarget, rest-pose conflict, hips |
| e34NrjX0ssA | Record MoCap Animations / Convert ANY animation to GTA 5 & FiveM (SKRTsese) | foot locks, root centring, smoothing, 60 fps practice |
| DqjcLN_jtKc | Baking Animations with Blender/Sollumz (Stumpy Mason) | why bake; duplicate loop frame |
| Eacadwz6g_I | Advanced Animation Tutorial (Stumpy Mason) | animated props via ytyp |
| KLfwxH7XfxQ | Converting Sketchfab Animations to GTA Animations (Stumpy Mason) | animated prop flags |
| L5bFzuVOTkU | Any Dance or Emote in FiveM in Minutes (Mic Scripts) | web converter |
| v79GNf0A_EY | Create Custom FiveM Animations From a Phone Video (LMX Development) | paid tool — flagged |
| SI9ysKQpevY | How to Install Custom Emotes … RPEMOTES (Dragons Lab) | XML → YCD, old EmoteLoop |
| fKwBgz5gn3E | How To Add Custom Emotes … Using DPemotes (Eishabeesha) | old dpemotes format |
| uch19GzxrUk | Make Your OWN Animations & Poses for FiveM & GTA 5 (5-Star Extras, outdated) | visual-keying bake, 60 fps |
| l_0VtJsBVKk | GTA 5 Synchronizing Animations in Menyoo (Kaz Productions) | paired clips, root-motion collisions |
| Fp6wqaJA7qg | FreeMocap Complete Tutorial (CGDive) | FreeMoCap multi-camera |
| bTMxTiZKyys | FreeMoCap Pre-recorded Videos Tutorial (Flux Renders) | processing, Butterworth, Rigify |
| NWfkF-sr-dY | FREE AI Motion Capture in Blender – Open Mocap (Larenju Kirat Gorkhali) | Open Mocap, Blender 4.0 limit |
| U9G2VlG9HbA | BlendArMocap (cg tinker) | legs experimental |
| Oa3W3F-AMlk | PoseCap: Free Webcam Motion Capture in Blender | no captions; README used |
| yYWGujCApNc | Free AI MoCap that DOESN'T SUCK (Benji 3D) | Plask (freemium) |
| LZVNvFwwwko | Free & Easy Mocap with Rokoko Video & Blender (Bad Decisions Studio) | TikTok dance (freemium) |
| mifGsXHitvs | How to Animate in Blender - FREE Mocap Ai Tools! (ProductionCrate) | filming tips, Gaussian, NLA Combine |
| cg9DODLvLg8 | Mocap, locally, on your PC GVHMR (CEB Studios) | GVHMR set-up, SMPL login |
| FyFarx7RjT8 | BlendCap (Arcomade) | paid — flagged |
| mVLFRoL_ur4 | Motion Capture in Blender for Free (RedLab Effects) | tracking route |
| YKhP2QfULDw | 3 Mocap Fixes Every Animator Should Know (Sir Wade Neistadt) | cleanup order, layers, contacts, props |
| n9v5U5WV8vA | Fix Foot Slide Without Killing the Feet (Melowilo) | foot-plant concept |
| HGNEfE_ZD3Y | Stop foot slipping in your Blender animation (Joey Carlino) | linear contacts, Global Transform |
| n5o0GS4ZYLQ | How to Clean Up motion Capture Data (Markom3D) | smooth, clean, spikes |
| NHQtU2v3zBU | Easy Dancing Character Animation (Joey Carlino) | dance loop: flip, Cycles, overlap, easing |
| nmg21jX9IpE | Behind the scenes making Luna (and Wayne) dance (CG Cookie) | motion matching from self-filmed reference |
| zAUmgEzR1xA | How to Film Good Reference for Animation (AnimSchool) | reference rules |
| UkWnwHwMapQ | How to use video reference for Animation (Chester Sampson) | extremes + contacts, retiming |
| o-FWoJs3GZE | Animation Breakdown (Opimation) | hips first |
| H08RNC0rB3U | Animating a FORTNITE Dance From Scratch (Nathanimator) | emote passes |
| x91ANmbiA88 | Shuffle Dance Tutorial Animation in Blender 4.1 (Caleb Josue Ruiz Torres) | shuffle timing |
| xn-oiDILZg4 | Animating a simple dance loop for a 2D character (Toniko Pantoja) | beats, metronome, hits |
| eFWN3x84NcU | How to sync animation to music in blender (Architecture Topics) | Bake Sound to F-Curves |
| AvKf22KPbZs | How to Create LOOPING ANIMATIONS in Blender! (The CG Essentials) | Cycles modes |
| pEg04DFV4kw | Seamless looping animations in Blender 4.2 (Index 3D) | loop check, duplicate frame |
| 3NrsSdEUSWI | Combine Mixamo Animations with the NLA Editor (Brandon 3D) | NLA repeat, Auto Blend |
| MBIypQzs1F0 | 2D Twitch emote | silhouette tip only |

Not used: 9I6vDuI4qq8 (no speech), ovWTBO0pB0E (music only); not fetched: m84_yFvAM48, ymfAsbPAmrY (BPM Marker Tool, no captions).

All videos: `https://www.youtube.com/watch?v=<ID>`.

## Code and docs
- rpemotes-reborn (GPL-3.0, commit d3553c1): https://github.com/alberttheprince/rpemotes-reborn — `client/AnimationList.lua`, `AnimationListCustom.lua`, `Emote.lua`, `Syncing.lua`, `GroupEmote.lua`, `types.lua`, `config.lua`, README.
- Sollumz (main @ 22b7947, 2026-11-06): https://github.com/Sollumz/Sollumz — `ycd/ycdexport.py` (`sequence_items_from_action`), `tools/animationhelper.py` (`get_action_export_frame_count`, `action_fcurves`). Sollumz docs YCD pages still "[TODO]": https://docs.sollumz.org/llms.txt
- Blender 5.2 manual: https://docs.blender.org/manual/en/latest/ — `editors/graph_editor/fcurves/editing.html` (Smooth Gaussian/Legacy/Butterworth, Decimate, Bake, Clean, Time Offset, Snap to marker), `editors/graph_editor/fcurves/modifiers.html` (Cycles, trivially cyclic, cycle-aware keying), `animation/markers.html`, `editors/nla/`, `editors/3dview/animation/copy_global_transform.html`, `video_editing/edit/montage/strips/sound.html`.
- Mocap: FreeMoCap https://github.com/freemocap/freemocap (AGPL-3.0); Open Mocap https://github.com/Larenju-Rai/open-mocap-blender (MIT); BlendArMocap https://github.com/cgtinker/BlendArMocap (GPL-3.0); PoseCap https://github.com/CorridorTech/PoseCap (GPL-3.0 + Apache-2.0 libs); GVHMR https://github.com/zju3dv/GVHMR (non-commercial); WHAM https://github.com/yohanshin/WHAM; mixamo-llm-mocap https://github.com/squall01337/mixamo-llm-mocap.
- Converters/previewers: https://github.com/Acc-Off/MotionConvertToEmote (MIT), https://github.com/Acc-Off/EmotePreviewer (MIT).
- Dance resources: https://github.com/TradieKM/Griddy (no licence), https://github.com/Xinerki/kgv-dance (no licence), bcortezf/bnj_dances and Knaak53/KnatusDanceSystem (GPL-3.0), PichotM/fivem-nightclub-ped (MIT).
- Pricing: https://www.rokoko.com/pricing (checked 2026-11; page shows conflicting prices).

## Local checks done for this skill (2026-11-08)
- Blender 5.2.3 headless: `bpy.utils.flip_name` leaves GTA names (`SKEL_L_Hand`, `PH_L_Hand`, `RB_L_ArmRoll`) unchanged → Paste Flipped doesn't swap sides on the GTA rig.
- Blender 5.2.3 headless: an action keyed 0–20 with a Cycles modifier reports `frame_range = (0, 20)` while `fcurve.evaluate(30)` returns the cycled value → Sollumz's sampled range excludes the repeats (in-game confirmation still pending).
- `scripts/test_dance_timing.py` and `scripts/test_bake_loop.py` pass.
