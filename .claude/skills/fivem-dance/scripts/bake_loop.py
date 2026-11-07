"""Bake a dance loop into ONE plain action before Sollumz export (Blender 4.2+ / 5.x, bpy).

Why: Sollumz samples each F-curve only over `action.frame_range` of a single
action (ycdexport.py, Sollumz main @ 22b7947). Cycles F-modifier repeats outside
the keyed range, NLA strips/tracks and layers on top are therefore not exported
(inferred from the source; confirm in game). This script evaluates whatever is
playing now - active action + Cycles/Noise modifiers + NLA + constraints/IK
(visual transform) - frame by frame over the loop range, writes one keyframe per
frame into a new action, makes the last frame equal the first (seamless seam),
mutes the NLA tracks it baked from and makes the new action active.

The original action is kept. Nothing is saved unless you pass --save-as.

Inside Blender (Text Editor or the `blender` MCP, after asking the user):
    import sys; sys.path.append(r"<path>\\fivem-dance\\scripts")
    import bake_loop
    report = bake_loop.bake_loop(bpy.data.objects["mp_m_freemode_01"], 0, 225)
    print(report)

Command line on a COPY of a .blend (never overwrites the input):
    blender --background copy.blend --python bake_loop.py -- \
        --object mp_m_freemode_01 --start 0 --end 225 --save-as baked.blend
"""
from __future__ import annotations

import sys

import bpy

EPS_MOVE = 1e-5


def _sample(obj, frames):
    """Visual local transforms per pose bone per frame: {bone: [(loc, quat, scale), ...]}."""
    scene = bpy.context.scene
    data = {pb.name: [] for pb in obj.pose.bones}
    for f in frames:
        scene.frame_set(f)
        for pb in obj.pose.bones:
            m = obj.convert_space(pose_bone=pb, matrix=pb.matrix, from_space='POSE', to_space='LOCAL')
            loc, quat, scale = m.decompose()
            seq = data[pb.name]
            if seq and seq[-1][1].dot(quat) < 0.0:  # keep quaternions continuous (no 360 deg flips)
                quat.negate()
            seq.append((loc.copy(), quat.copy(), scale.copy()))
    return data


def _changes(seq, index):
    first = seq[0][index]
    return any((v[index] - first).length > EPS_MOVE for v in seq)


def _seam_error(seq):
    """Largest first/last difference: metres for location/scale, radians for rotation."""
    (l0, q0, s0), (l1, q1, s1) = seq[0], seq[-1]
    return max((l1 - l0).length, q0.rotation_difference(q1).angle, (s1 - s0).length)


def bake_loop(obj, start, end, action_name=None, match_ends=True, key_location="auto",
              mute_nla=True):
    """Bake obj's current evaluated animation over start..end (inclusive) into a new action.

    key_location: "auto" = only bones whose location actually moves (usually SKEL_ROOT),
                  "all" = every bone, "none" = rotations only.
    Returns a report dict.
    """
    if obj is None or obj.type != 'ARMATURE':
        raise ValueError("bake_loop needs an armature object")
    if end <= start:
        raise ValueError("end must be after start")
    scene = bpy.context.scene
    old_frame = scene.frame_current
    warnings = []
    fps = scene.render.fps / scene.render.fps_base
    if abs(fps - 30.0) > 1e-6:
        warnings.append(f"scene runs at {fps:g} fps; GTA clips are 30 fps")

    frames = list(range(start, end + 1))
    data = _sample(obj, frames)
    scene.frame_set(old_frame)

    seam = max((_seam_error(seq) for seq in data.values()), default=0.0)
    if match_ends:
        for seq in data.values():
            seq[-1] = seq[0]

    ad = obj.animation_data or obj.animation_data_create()
    source = ad.action
    muted = []
    if mute_nla:
        for track in ad.nla_tracks:
            if not track.mute:
                track.mute = True
                muted.append(track.name)
    name = action_name or f"{(source.name if source else obj.name)}_baked"
    action = bpy.data.actions.new(name)
    ad.action = action
    action.use_fake_user = True

    for pb in obj.pose.bones:
        pb.rotation_mode = 'QUATERNION'  # Sollumz skips Euler channels

    keyed_location = []
    for pb in obj.pose.bones:
        seq = data[pb.name]
        do_loc = key_location == "all" or (key_location == "auto" and _changes(seq, 0))
        do_scale = _changes(seq, 2)
        if do_loc:
            keyed_location.append(pb.name)
        if do_scale:
            warnings.append(f"{pb.name} has animated scale (GTA ped clips normally do not)")
        for i, f in enumerate(frames):
            loc, quat, scale = seq[i]
            pb.rotation_quaternion = quat
            pb.keyframe_insert("rotation_quaternion", frame=f, group=pb.name)
            if do_loc:
                pb.location = loc
                pb.keyframe_insert("location", frame=f, group=pb.name)
            if do_scale:
                pb.scale = scale
                pb.keyframe_insert("scale", frame=f, group=pb.name)

    for fc in fcurves_of(action):
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'
    scene.frame_set(old_frame)
    return {
        "action": action.name,
        "source_action": source.name if source else None,
        "frames": f"{start}-{end} ({len(frames)} keys per channel)",
        "bones": len(obj.pose.bones),
        "location_keyed": keyed_location,
        "muted_nla_tracks": muted,
        "seam_error_before_fix": round(seam, 6),
        "seam_fixed": match_ends,
        "warnings": warnings,
    }


def fcurves_of(action):
    """F-curves of a legacy (4.x) or layered (5.x) action."""
    if hasattr(action, "layers") and len(action.layers):
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves
    elif hasattr(action, "fcurves"):
        yield from action.fcurves


def _cli(argv):
    import argparse
    p = argparse.ArgumentParser(prog="bake_loop.py")
    p.add_argument("--object", required=True)
    p.add_argument("--start", type=int, required=True)
    p.add_argument("--end", type=int, required=True)
    p.add_argument("--name")
    p.add_argument("--no-match-ends", action="store_true")
    p.add_argument("--save-as", help="write the result to this NEW .blend (input is never overwritten)")
    a = p.parse_args(argv)
    obj = bpy.data.objects.get(a.object)
    report = bake_loop(obj, a.start, a.end, a.name, match_ends=not a.no_match_ends)
    print(report)
    if a.save_as:
        if bpy.data.filepath and bpy.path.abspath(a.save_as) == bpy.data.filepath:
            raise SystemExit("refusing to overwrite the opened .blend; choose another --save-as")
        bpy.ops.wm.save_as_mainfile(filepath=a.save_as, copy=True)


if __name__ == "__main__" and "--" in sys.argv:
    _cli(sys.argv[sys.argv.index("--") + 1:])
