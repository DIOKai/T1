# Ped skeleton and authoring in Blender

Sources: Sollumz source (commit 82817d1, 2026-09-28, 2.9.0-dev), citizenfx/natives `PED/GetPedBoneIndex.md`, muto-atlas (`trunk/bone-tags.md`, `trunk/tool-pitfalls.md`, `trunk/gta-fundamentals.md`), muto-ped-rig (GPL-3, third-party measurements). UNVERIFIED marks things not confirmed from a primary source.

## Getting the skeleton
- Extract `mp_m_freemode_01.yft` / `mp_f_freemode_01.yft` from your own game with CodeWalker's RPF Explorer (Sollumz knows the paths: `x64v.rpf\models\cdimages\streamedpeds_mp.rpf\…`) and import with Sollumz. If your Sollumz build can't open the binary, export the `.yft` to XML in CodeWalker and import that.
- Sollumz does not ship a ped skeleton. muto-ped-rig (GPL-3, github.com/B7Kompirine/muto-ped-rig) ships a vanilla-derived 128-bone freemode template `.blend` plus a retargeter — free and local, but it installs a Blender extension (ask first).
- To load a vanilla animation for reference: CodeWalker ▸ export the `.ycd` to XML ▸ Sollumz import `.ycd.xml` ▸ "Set Animations Target" to your armature ▸ preview with "Apply Clip to NLA". A binary `.ycd` gives "Binary resource format '.ycd' is not supported yet" and an empty scene.

## Bone tags — why you must never rebuild bones
Every animation channel is keyed by **bone tag**, not name (Sollumz `build_name_bone_map` → `bone_properties.tag`; export writes `bone_id = tag`; the game binds the same way). Importing a vanilla `.yft` stores the real tags as manual tags. A bone you create or rename gets an automatic name hash (`calc_tag_hash`), which does not match GTA:

| Bone | Auto hash (wrong) | Real tag |
|---|---:|---:|
| `SKEL_Head` | 21030 | 31086 |
| `SKEL_R_Hand` | 22798 | 57005 |
| `SKEL_Pelvis` | 56200 | 11816 |
| `PH_R_Hand` | 7966 | 28422 |

Result of wrong tags: T-pose or frozen limbs with no error.

### Main ped bone tags (decimal; GetPedBoneIndex.md, cross-checked with muto-atlas)
| Bone | Tag | Bone | Tag |
|---|---:|---|---:|
| SKEL_ROOT | 0 | SKEL_Pelvis | 11816 |
| SKEL_Spine_Root | 57597 | SKEL_Spine0 / 1 / 2 / 3 | 23553 / 24816 / 24817 / 24818 |
| SKEL_Neck_1 | 39317 | SKEL_Head | 31086 |
| IK_Head | 12844 | IK_Root | 56604 |
| SKEL_L_Thigh / SKEL_R_Thigh | 58271 / 51826 | SKEL_L_Calf / SKEL_R_Calf | 63931 / 36864 |
| SKEL_L_Foot / SKEL_R_Foot | 14201 / 52301 | SKEL_L_UpperArm / SKEL_R_UpperArm | 45509 / 40269 |
| SKEL_L_Forearm / SKEL_R_Forearm | 61163 / 28252 | SKEL_L_Hand / SKEL_R_Hand | 18905 / 57005 |
| PH_L_Hand / PH_R_Hand (prop holders) | 60309 / 28422 | IK_L_Hand / IK_R_Hand | 36029 / 6286 |
| FACIAL_facialRoot | 65068 | | |

Helper bones: `RB_*ThighRoll` are driven at runtime by expressions (.yed); Sollumz adds a Copy Rotation only for preview. muto-ped-rig's measurement over 84 vanilla clips: hip rotation lives on `SKEL_ROOT`; `SKEL_Pelvis` and `SKEL_Spine_Root` are fixed converters and never keyed; limbs get rotations only (third-party).

Facial bones (`FB_*`) are named differently in `.ydd` and `.yft` (same tags) — Blender binds by name, so a face rig from the wrong file won't deform. Use the `.yft` skeleton.

## Scene rules
- **30 fps.** Sollumz computes durations from the scene fps (`render.fps / fps_base`); a vanilla test asset has 501 frames over 16.666 s = 30 fps. A 24 fps source taken frame-by-frame plays 25% fast — resample by time.
- **Quaternion rotation.** The exporter reads only `location`, `rotation_quaternion`, `scale` (and Sollumz animation tracks). `rotation_euler` channels log "Channel '…' is unsupported, skipping…" and are dropped.
- 1 unit = 1 m, Z-up; the ped faces −Y in rest pose (clip-space forward is +Y). Rest pose arms are about 57° below horizontal — keep the vanilla rest pose.
- Blender 4.4+ / 5.x layered actions are supported; when assigning an action by script also set `animation_data.action_slot`.

## Animating
- **Bake before export:** constraints, IK and drivers are not exported (only F-curves are evaluated). Pose ▸ Animation ▸ Bake Action with Visual Keying and Clear Constraints, keeping quaternion rotation.
- **Mover / root motion:** the mover is separate from `SKEL_ROOT` bone tracks (track 5 MoverPosition, 6 MoverRotation). In Blender, Sollumz maps it to the **armature object's Delta Transform** (`delta_location`, `delta_rotation_quaternion`); exporting with mover keys sets the RootMotion flag. Put horizontal travel on the mover; keep vertical bounce on the bone. Emotes are usually "in place" or rotations-only.
- **Limbs:** rotations only — position keys on limbs break on peds with different bone lengths (e.g. female).
- **Loops:** match first and last pose; looping itself is a play flag (`AF_LOOPING`), not a clip property.
- Quaternion sign flips are already fixed by the exporter (it flips consecutive quaternions with negative dot product).
- Interpolation: muto-atlas recommends Linear for clip/UV animation (measured on props); for character motion Bezier vs Linear is a style choice.

## Retargeting Mixamo / mocap (free options)
| Tool | Licence / cost | Notes |
|---|---|---|
| muto-ped-rig | GPL-3, free, local | Accepts Mixamo, Unreal, Biped, Rigify, NVIDIA SOMA rigs; modes Root Motion / In Place / Rotations Only; exports `<dict>.ycd.xml` directly. Installs a Blender extension — ask first |
| Rokoko Studio Live for Blender | free (LGPL-3 per LICENSE.md) | Retargeting panel requires a free Rokoko account login — ask first. Turn "Auto Scale" off or root motion is deleted (muto-atlas) |
| FreeMoCap | AGPL-3, free | Webcam markerless mocap → Blender add-on |
| "Retarget" extension / Expy Kit | free per listings | Licence and repo UNVERIFIED |
| Auto-Rig Pro | **paid** | don't recommend |
| DeepMotion, Move.ai, Plask, Rokoko Vision | **paid / credits** | don't recommend |

Mixamo is free with an Adobe login and allows royalty-free use in games, but forbids distributing the raw character/animation files. Using a Mixamo clip on your own server is fine; publishing a .ycd pack built from them is a grey area.
