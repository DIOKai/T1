# Mixamo → GTA V / FiveM, step by step

Mixamo gives free, decent humanoid animations (dances, idles, fights, sitting, waving). They use Mixamo's own skeleton, so they have to be **retargeted** onto the GTA ped skeleton before Sollumz can export them. The free, local tool that does this for GTA is **muto-ped-rig** (GPL-3, Blender 4.2+, Sollumz 2.9). It recognises Mixamo bone names, corrects the T-pose → GTA rest pose difference, writes root motion to the mover track and exports a clip dictionary.

Sources: muto-ped-rig v0.3.2 source (`bl/anim_ops.py`, `bl/props.py`, `core/animmap.py`) and README; Adobe Mixamo FAQ (helpx.adobe.com) for terms. The Mixamo dialog wording is from memory and is marked UNVERIFIED; check it on the site.

## Terms (read once)

- Mixamo is free with an Adobe ID; no Creative Cloud subscription needed. Enterprise/Federated IDs and China-region accounts are excluded (Adobe FAQ).
- Characters and animations are royalty-free for personal, commercial and non-profit work, including video games (Adobe FAQ).
- You may **not** distribute the raw files (FBX/animation packs, asset-store listings). A compiled `.ycd` in your own server's resource is the normal use. Selling or publicly sharing a `.ycd` pack made from Mixamo clips is a grey area, so tell the user.
- There is no official API. Community tools (gnuton/mixamo_anims_downloader console script, V1xel/mixamo-mcp with Playwright and a saved login session) call internal endpoints and can break at any time. Don't install them unless the user asks. Downloading by hand is fine for a handful of clips.

## 1. Download from Mixamo (by hand)

1. mixamo.com → log in → Characters: any (for example Y Bot). The character's mesh is not used, only its skeleton.
2. Animations: pick one. Adjust the sliders (speed, arm space, "Overdrive"…) until it looks right.
3. For walking/running clips, the **In Place** checkbox stops the character travelling. Leave it off if you want real root motion (the mover track, step 3).
4. Download (UNVERIFIED dialog wording): **Format: FBX Binary (.fbx)**, **Skin: Without Skin** (smaller; the armature is enough), **Frames per Second: 30**, **Keyframe Reduction: none**.

Download each clip separately. Put them in one folder, e.g. `mixamo/`.

## 2. Import into Blender

1. File ▸ Import ▸ FBX → the `.fbx`. Defaults are fine. You get an armature (usually named `Armature`) with an action.
2. Rename the action to the **clip name you will play in game**. muto-ped-rig derives the clip name from the action name (lowercase, `[a-z0-9_]`, the `.001` suffix and the `Armature|` prefix removed), so an action left as `mixamo.com` becomes a clip called something like `mixamo_com`. Use names like `wave_loop`, `sit_chill`, `dance_shuffle`.
3. Import more clips the same way. Each FBX brings its own armature. That's fine: pick each armature as the Source in turn, or keep one armature and switch actions.

## 3. Retarget with muto-ped-rig

Install once (ask first; it installs a Blender extension): open https://b7kompirine.github.io/muto-ped-rig/ and drag the link into Blender, or Edit ▸ Preferences ▸ Get Extensions ▸ Install from Disk with the release zip. Sollumz must be enabled. Panel: 3D Viewport ▸ N ▸ **Muto Rig** ▸ *Animation (Retarget)*.

1. **Source** = the Mixamo armature. **Clip** = its action (or tick **All Clips**).
2. **Root Motion**:
   - **Root Motion (Mover)**: walking, running. The hips' horizontal path goes to the GTA mover track, as in vanilla locomotion.
   - **In Place**: drops the horizontal travel and keeps the up-down hip bounce.
   - **Rotations Only**: emotes, upper-body clips, sitting. No root position.
3. **Retarget to GTA**. The clip is baked onto `MPR_AnimRig` (the vanilla ped skeleton in GTA rest pose) at **30 fps**. A clip at another frame rate is resampled by time, so its duration stays the same.
   - Mixamo has 3 spine joints, so `SKEL_Spine3` stays at rest.
   - Fingers that never move in the source keep the GTA hand pose.
   - `SKEL_Pelvis` and `SKEL_Spine_Root` are never keyed. Limbs get rotations only, which suits male and female peds.
4. **Dictionary** = the `.ycd` name, which is also the dictionary for `TaskPlayAnim` (lowercase, digits, `_`, `@`; e.g. `dio@dances`). **Output Folder** (default `//mpr_export/`).
5. **Export Clip Dictionary** writes `<Dictionary>.ycd.xml` and reads it back. The report lists the clip names to use in game.

### Same thing through the `blender` MCP (ask before running code in the user's Blender)

Property and operator names checked against muto-ped-rig 0.3.2 source:
```python
import bpy
s = bpy.context.scene.mpr
src = bpy.data.objects["Armature"]              # the imported Mixamo armature
src.animation_data.action.name = "wave_loop"    # becomes the clip name
s.anim_source = src
s.anim_all_clips = False                         # or True: every clip that animates src
s.anim_action = src.animation_data.action
s.anim_root_motion = "NONE"                      # "MOVER" | "IN_PLACE" | "NONE"
s.anim_dict_name = "dio@emotes"
s.export_dir = "//mpr_export/"
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.mpr.retarget()
bpy.ops.mpr.export_clips()                       # needs Sollumz enabled
```
Run one clip first, look at it in the viewport (`MPR_AnimRig`), then batch.

## 4. Compile, ship, play

Continue with the normal chain in `SKILL.md`: CodeWalker turns `<dict>.ycd.xml` into `<dict>.ycd` → `stream/` of a resource (rpemotes: `stream/[Custom Emotes]/…` and `AnimationListCustom.lua`) → **rejoin the server** (a restart isn't enough) → `TaskPlayAnim(ped, "<dict>", "<clip>", …)`. Then run `scripts/check_anim_resource.py` on the export folder and the resource.

## Common problems

| Symptom | Cause / fix |
|---|---|
| Arms float out sideways or sink into the body | Mixamo arm-space slider. Re-download with "Character Arm-Space" adjusted, or accept a small offset (muto corrects T-/A-pose, not the slider) |
| Feet slide when walking | Wrong root mode. Use **Root Motion (Mover)** with a clip downloaded **without** In Place |
| The ped walks away during an emote | Use **Rotations Only** or **In Place** |
| Clip plays twice as slow/fast | Mixed frame rates. Download at 30 fps and let muto resample. Don't change the scene fps by hand afterwards |
| Clip name in game is `mixamo_com` | The action wasn't renamed before retargeting (step 2) |
| Nothing plays, the ped T-poses | Dictionary/clip name mismatch, `.ycd.xml` instead of `.ycd` in `stream/`, or no rejoin. See `troubleshooting.md` |
| Fingers frozen | Expected when the source doesn't animate fingers. Mixamo clips with hand motion keep it |

## Beyond Mixamo (free, all ask-first)

- Your own motion from video: squall01337/mixamo-llm-mocap (GVHMR pose estimation → Mixamo rig in Blender through MCP; Blender 5.1+ and an NVIDIA GPU). Then retarget with muto as above. Not tested here.
- FreeMoCap (free, multi-webcam) exports BVH; muto lists Biped/Rigify/SOMA rigs, so BVH needs converting to one of those first (UNVERIFIED).
