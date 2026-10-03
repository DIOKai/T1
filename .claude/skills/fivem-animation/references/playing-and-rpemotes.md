# Streaming, playing, rpemotes custom emotes, props

Sources: citizenfx/fivem `LoadStreamingFile.cpp`, `ResourceStreamComponent.cpp`; citizenfx/natives (`TASK/TaskPlayAnim.md`, `STREAMING/*`, `ENTITY/AttachEntityToEntity.md`, `PED/*`); fivem-docs `legacy-vs-enhanced.md`, `alchemist/_index.md`, `data-files.md`; ox_lib (LGPL-3, commit 66906c5); rpemotes-reborn (GPL-3, v2.2.0, commit d3553c1).

## Streaming
- `.ycd` goes in `stream/` — **no data_file needed**; FiveM registers streamed files into the module for their extension, named after the file.
- Size: FXServer warns above 16 MiB memory per asset (clips are normally far below).
- Enhanced client: a resource with `stream_enhanced/` loads only that folder — copy the `.ycd` there too. Alchemist's list (YDR, YTD, YFT, YPT, YDD) doesn't include YCD; whether YCD needs conversion is UNVERIFIED.

## Playing from a script

```lua
local dict, clip = 'dio@wave', 'wave_clip'      -- dict = .ycd file name, clip = clip Hash
if not DoesAnimDictExist(dict) then return print('anim dict not streamed: ' .. dict) end
RequestAnimDict(dict)
while not HasAnimDictLoaded(dict) do Wait(0) end
TaskPlayAnim(PlayerPedId(), dict, clip, 3.0, 3.0, -1, 49, 0.0, false, false, false)
RemoveAnimDict(dict)
```

`TaskPlayAnim(ped, dict, clip, blendInSpeed, blendOutSpeed, duration, flag, …)`: blend 1.0 normal, 8.0 ≈ instant; duration in ms, -1 = until stopped. The 8th parameter is treated as **start phase (0–1)** by ox_lib and rpemotes (the natives doc calls it playback rate — follow the two working scripts). With `use_experimental_fxv2_oal 'yes'`, pass booleans for the last three parameters.

### Flags (eScriptedAnimFlags, TaskPlayAnim.md) — add values together
| Value | Flag | Value | Flag |
|---:|---|---:|---|
| 1 | LOOPING | 2 | HOLD_LAST_FRAME |
| 4 | REPOSITION_WHEN_FINISHED | 8 | NOT_INTERRUPTABLE |
| 16 | UPPERBODY | 32 | SECONDARY |
| 64 | REORIENT_WHEN_FINISHED | 128 | ABORT_ON_PED_MOVEMENT |
| 256 | ADDITIVE | 512 | TURN_OFF_COLLISION |
| 1024 | OVERRIDE_PHYSICS | 2048 | IGNORE_GRAVITY |
| 4096 | EXTRACT_INITIAL_OFFSET | 524288 | USE_MOVER_EXTRACTION |
| 1048576 | HIDE_WEAPON | 2097152 | ENDS_IN_DEAD_POSE |

Common combinations: **1** loop full body; **49** = 1+16+32 loop, upper body, secondary — walk while doing it (ox_lib progressBar default); **50** = 2+16+32 hold last frame upper body (rpemotes STUCK); **51** = 1+2+16+32 (rpemotes MOVING). "120 = cancelable" circulating online is just 8+16+32+64, not a named flag. Mover-related flags (4, 64, 4096, 524288): exact behaviour UNVERIFIED beyond their names.

### Stopping and inspecting
`StopAnimTask(ped, dict, clip, exitSpeed)` — exitSpeed must be a float > 0.0 (0.0 or an integer locks the animation); `ClearPedTasks` / `ClearPedTasksImmediately` / `ClearPedSecondaryTask`; `IsEntityPlayingAnim(ped, dict, clip, 3)`; `GetAnimDuration(dict, clip)`; `TaskPlayAnimAdvanced` adds position/rotation and start time.

### ox_lib
`lib.requestAnimDict(dict, timeout)` (errors on an invalid dict; default 10000 ms) and `lib.playAnim(ped, dict, clip, blendIn, blendOut, duration, flags, startPhase, …)` (requests, plays, removes). `lib.progressBar({ anim = { dict, clip, flag }, prop = { model, bone = 60309, pos, rot } })` for timed actions.

## rpemotes-reborn custom emotes
1. Put the `.ycd` in `rpemotes/stream/[Custom Emotes]/<your folder>/`.
2. Add the entry to `client/AnimationListCustom.lua` and keep a copy as `BackUpAnimationListCustom.lua` (updates overwrite the file). Files from before 1.5.0 aren't compatible.
3. Rejoin and use it from the menu (F4 by default) or `/e <name>`.

Entry shape (`types.lua`): `["name"] = { "dict", "clip", "Label", AnimationOptions = { … } }` inside `CustomDP.Emotes`, `CustomDP.Dances`, `CustomDP.PropEmotes`, `CustomDP.Shared`, `CustomDP.Walks`, `CustomDP.Expressions`, `CustomDP.Exits`, `CustomDP.AnimalEmotes`.

```lua
CustomDP.Emotes = {
  ["diowave"] = { "dio@wave", "wave_clip", "Dio Wave", AnimationOptions = { onFootFlag = AnimFlag.LOOP } },
}
CustomDP.PropEmotes = {
  ["diocoffee"] = { "dio@coffee", "hold_clip", "Dio Coffee", AnimationOptions = {
      Prop = "p_amb_coffeecup_01", PropBone = 28422, PropPlacement = { 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 },
      onFootFlag = AnimFlag.MOVING } },
}
```

Option keys: `onFootFlag`, `Flag`, `FullBody` (needed for full-body emotes in vehicles), `EmoteDuration`, `StartDelay`, `BlendInSpeed`/`BlendOutSpeed` (default 5.0), `vehicleRequirement`, `ExitEmote`, `PlacementOffset`. Props: `Prop`, `PropBone`, `PropPlacement = {x,y,z,rx,ry,rz}`, `PropNoCollision`, `SecondProp*`, `PropTextureVariations`. Particle effects: `PtfxAsset`, `PtfxName`, `PtfxPlacement`, `PtfxBone`, `PtfxWait`, `PtfxCanHold`. `AnimFlag` presets: LOOP = 1, STUCK = 50, MOVING = 51.

- Shared emotes: 4th element is the partner emote; sync with `SyncOffsetFront/Side/Height/Heading` or `Attachto` + `bone`/`pos`/`rot` (bone **tags**).
- Custom props: put `.ydr` + `.ytyp` in `stream/` and add `data_file 'DLC_ITYP_REQUEST' 'stream/<name>.ytyp'`.
- Config: `Config.CustomCategories`, `Config.Ace`, `MenuKeybind = 'F4'`, `CancelEmoteKey = 'X'`, `AllowEmoteInVehicle`, `AdultEmotesDisabled`, `AbusableEmotesDisabled`. Needs OneSync.
- Bundled creator animations were added with permission — that permission doesn't extend to reusing them elsewhere.

## Props attached to animations
- `AttachEntityToEntity(prop, ped, GetPedBoneIndex(ped, tag), x, y, z, rx, ry, rz, true, true, false, true, rotationOrder, true)`. `GetPedBoneIndex` takes the **tag** (57005 right hand, 18905 left hand, 28422 PH_R_Hand, 60309 PH_L_Hand); an invalid index silently attaches to the ped's centre.
- **Rotation order matters** when two rotation axes are non-zero: rpemotes uses 1, ox_lib defaults to 0. Port offsets together with their order.
- Offsets are in bone space from the prop's origin. In Blender, parent the prop to `PH_R_Hand` to get a starting offset, then fine-tune live in game while the clip loops (a direct Blender→offset formula is UNVERIFIED).
- A prop that animates itself needs its own skeleton and `PlayEntityAnim` (or a synced scene).

## Walk styles and facial
- Walk: `RequestAnimSet` → `SetPedMovementClipset(ped, "move_m@...", 0.2)` → `RemoveAnimSet`; reset with `ResetPedMovementClipset`. Custom clipsets need `data_file 'CLIP_SETS_FILE'`; an end-to-end custom walk clipset in FiveM is UNVERIFIED.
- Facial: `PlayFacialAnim(ped, animName, animDict)` and `SetFacialIdleAnimOverride(ped, animName, animDict)` — name before dict.
