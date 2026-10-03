# Troubleshooting: symptom → cause → fix

Start with `check_anim_resource.py` on both the Sollumz export folder (.ycd.xml) and the resource, then `DoesAnimDictExist(dict)` in game.

| Symptom | Likely cause | Fix |
|---|---|---|
| Nothing plays, no error | dict not streamed or misnamed (dict = file name); `.ycd.xml` left uncompiled in `stream/`; clip Hash empty or not equal to the clip name used; dict not loaded yet | `DoesAnimDictExist`; compile with CodeWalker; set Clip Hash = clip name; Request/HasLoaded loop; rejoin after adding a new .ycd |
| Works on Legacy, not Enhanced | resource has `stream_enhanced/` without the .ycd | copy the .ycd into `stream_enhanced/` |
| T-pose, frozen or twisted limbs | wrong bone tags (skeleton rebuilt or bones renamed → auto-hash tags); Animation Target set to the object instead of the armature data; Euler channels skipped | use an imported vanilla `.yft` skeleton; Target = armature data; quaternion rotation; bake IK/constraints |
| Legs look odd in Blender preview only | thigh-roll bones are driven at runtime by expressions | preview artefact — Sollumz adds a Copy Rotation workaround |
| Ped slides, floats, or snaps back at the end | hip travel keyed on `SKEL_ROOT` position instead of the mover; vertical offset; IGNORE_GRAVITY / OVERRIDE_PHYSICS flags | put horizontal travel on the armature object's Delta Transform (mover) or make the clip in place; check flags 1024 / 2048 / 4096 |
| Should move but plays in place (or the reverse) | mover keys missing or present | add/remove keys on the armature object's Delta Transform |
| Jitter or sudden flips | Euler gimbal issues before conversion; sparse Bezier keys | bake to quaternion at 30 fps; consider Linear interpolation |
| Too fast / too slow | scene not at 30 fps; clip Duration ≠ (end − start)/30 so Rate ≠ 1; 24 fps source copied frame-by-frame | set 30 fps before building clips; fix Duration; resample by time |
| Prop in the wrong place | bone index vs tag mix-up; rotation order mismatch; prop origin not at the grip | `GetPedBoneIndex(ped, tag)`; match rotation order (rpemotes 1, ox_lib 0); fix the origin in the .ydr; tune live |
| Fine on male, broken on female | position keys on limbs; different bone lengths | rotations only on limbs; test both freemode peds |
| Face doesn't move | `FB_*` bone names differ between .ydd and .yft | use the .yft skeleton; bind by tag |
| `StopAnimTask` locks the ped | exitSpeed 0 or an integer | pass a float > 0.0 |
| Script error on the last TaskPlayAnim parameters | `use_experimental_fxv2_oal` rejects ints there | pass booleans |
| rpemotes emote missing after an update | `AnimationListCustom.lua` overwritten | restore from `BackUpAnimationListCustom.lua` |
