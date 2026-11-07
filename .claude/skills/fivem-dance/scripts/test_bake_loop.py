"""Headless test for bake_loop.py (builds its own scene; never opens a user .blend).

Run:
    blender --background --factory-startup --python-exit-code 1 --python test_bake_loop.py
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bake_loop  # noqa: E402

TOL = 1e-4


def build_rig():
    scene = bpy.context.scene
    scene.render.fps, scene.render.fps_base = 30, 1.0
    arm = bpy.data.armatures.new("rig")
    obj = bpy.data.objects.new("rig", arm)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    root = arm.edit_bones.new("SKEL_ROOT")
    root.head, root.tail = (0, 0, 1), (0, 0, 1.2)
    limb = arm.edit_bones.new("SKEL_R_UpperArm")
    limb.head, limb.tail = (0.2, 0, 1.4), (0.5, 0, 1.4)
    limb.parent = root
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in obj.pose.bones:
        pb.rotation_mode = 'QUATERNION'
    return obj


def key_20_frame_loop(obj, name="dance20"):
    """Keys at 0, 10, 20 (first == last) on the arm rotation and root height."""
    ad = obj.animation_data_create()
    ad.action = bpy.data.actions.new(name)
    arm = obj.pose.bones["SKEL_R_UpperArm"]
    root = obj.pose.bones["SKEL_ROOT"]
    for f, ang, z in ((0, 0.0, 0.0), (10, 60.0, -0.08), (20, 0.0, 0.0)):
        a = math.radians(ang)
        arm.rotation_quaternion = (math.cos(a / 2), 0.0, 0.0, math.sin(a / 2))
        arm.keyframe_insert("rotation_quaternion", frame=f, group=arm.name)
        root.location = (0.0, 0.0, z)
        root.keyframe_insert("location", frame=f, group=root.name)
    return ad.action


def add_cycles(action):
    n = 0
    for fc in bake_loop.fcurves_of(action):
        fc.modifiers.new('CYCLES')
        n += 1
    return n


def channel_values(action, frames):
    out = {}
    for fc in bake_loop.fcurves_of(action):
        keys = {round(kp.co.x): kp.co.y for kp in fc.keyframe_points}
        missing = [f for f in frames if f not in keys]
        assert not missing, f"{fc.data_path}[{fc.array_index}] missing keys {missing[:5]}"
        assert len(fc.modifiers) == 0, "baked curve still has modifiers"
        out[(fc.data_path, fc.array_index)] = keys
    return out


def assert_periodic(values, period, frames):
    for key, keys in values.items():
        for f in frames:
            if f + period in keys:
                d = abs(keys[f] - keys[f + period])
                assert d < TOL, f"{key} frame {f} vs {f + period}: diff {d}"
        assert abs(keys[frames[0]] - keys[frames[-1]]) < TOL, f"{key} first != last"


def test_cycles_modifier():
    obj = build_rig()
    act = key_20_frame_loop(obj)
    assert add_cycles(act) > 0
    # What Sollumz would sample: action.frame_range covers only the keys (0-20),
    # so the Cycles repeat 20-40 is outside it -> must bake.
    fr = tuple(act.frame_range)
    assert fr == (0.0, 20.0), f"unexpected frame_range {fr}"
    # the modifier does evaluate past the keys (frame 30 == frame 10)
    fc = next(f for f in bake_loop.fcurves_of(act) if f.data_path.endswith("rotation_quaternion") and f.array_index == 3)
    assert abs(fc.evaluate(30) - fc.evaluate(10)) < TOL
    report = bake_loop.bake_loop(obj, 0, 40)
    baked = obj.animation_data.action
    assert baked.name == "dance20_baked", baked.name
    assert tuple(baked.frame_range) == (0.0, 40.0), tuple(baked.frame_range)
    frames = list(range(0, 41))
    vals = channel_values(baked, frames)
    assert_periodic(vals, 20, frames)
    paths = {p for p, _ in vals}
    assert any("SKEL_ROOT" in p and p.endswith("location") for p in paths), "root location not keyed"
    assert not any("SKEL_R_UpperArm" in p and p.endswith("location") for p in paths), "limb location keyed"
    q = vals[('pose.bones["SKEL_R_UpperArm"].rotation_quaternion', 3)]
    assert abs(q[30] - math.sin(math.radians(30))) < TOL, q[30]  # frame 30 = peak of 2nd cycle
    assert report["seam_error_before_fix"] < TOL, report
    assert bpy.data.actions.get("dance20") is not None, "original action was removed"
    print("cycles test OK:", report)
    bpy.data.objects.remove(obj)


def test_nla_repeat():
    obj = build_rig()
    act = key_20_frame_loop(obj, "nla20")
    ad = obj.animation_data
    track = ad.nla_tracks.new()
    strip = track.strips.new("nla20", 0, act)
    strip.repeat = 2.0
    ad.action = None
    report = bake_loop.bake_loop(obj, 0, 40, action_name="nla_baked")
    baked = ad.action
    assert baked.name == "nla_baked"
    assert track.mute, "NLA track should be muted after baking"
    assert report["muted_nla_tracks"], report
    frames = list(range(0, 41))
    vals = channel_values(baked, frames)
    assert_periodic(vals, 20, frames)
    print("nla test OK:", report)
    bpy.data.objects.remove(obj)


def test_seam_fix():
    obj = build_rig()
    act = key_20_frame_loop(obj, "openloop")
    # break the loop: last key differs from the first
    arm = obj.pose.bones["SKEL_R_UpperArm"]
    a = math.radians(20)
    arm.rotation_quaternion = (math.cos(a / 2), 0.0, 0.0, math.sin(a / 2))
    arm.keyframe_insert("rotation_quaternion", frame=20, group=arm.name)
    report = bake_loop.bake_loop(obj, 0, 20)
    assert report["seam_error_before_fix"] > 0.05, report
    vals = channel_values(obj.animation_data.action, list(range(0, 21)))
    for key, keys in vals.items():
        assert abs(keys[0] - keys[20]) < TOL, f"{key} seam not fixed"
    print("seam test OK:", report)
    bpy.data.objects.remove(obj)


def test_bad_input():
    obj = build_rig()
    for args in ((None, 0, 10), (obj, 10, 10)):
        try:
            bake_loop.bake_loop(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {args}")
    print("bad input test OK")


test_cycles_modifier()
test_nla_repeat()
test_seam_fix()
test_bad_input()
print("ALL BAKE TESTS PASSED on Blender", bpy.app.version_string)
