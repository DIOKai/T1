"""Architectural cameras and eased camera moves for Blender 5.x (runs in Blender's Python).

NOT RUN IN BLENDER: written against the Blender 5.x Python API docs (5.0 release notes,
bpy.types.Keyframe, bpy_extras.anim_utils) on a machine without Blender; only syntax-checked
with `python -m py_compile`. Test it on a saved copy of the .blend first and fix what fails.

Send through the blender MCP's execute_blender_code:

    import runpy
    cm = runpy.run_path(r"<skill>/scripts/camera_moves_bpy.py")
    cam = cm["create_camera"]("CAM_01", location=(0, -20, 1.6), look_at=(0, 0, 4), lens=35)
    cm["keyframe_move"](cam, "push_in", start_frame=1, seconds=8, distance=2.0, fps=24)
    print(cm["describe"](cam))

Moves (all keep roll at 0 and, unless noted, keep the camera level = two-point perspective):
    dolly    straight move along the camera's view direction (distance m, + = forward)
    push_in  dolly toward the look_at target with a Track To constraint, optional lens change
    slider   sideways along the camera's right vector, rotation fixed (distance m, + = right)
    crane    straight up (distance m), camera stays level; frame with shift instead of tilting
    orbit    camera parented to an Empty at the target; Empty rotates angle_deg around Z

Interpolation: keys are inserted with keyframe_insert(), then every key on the camera's
F-curves gets interpolation SINE + easing EASE_IN_OUT (or BEZIER + AUTO_CLAMPED handles).
F-curves are reached through the action's channelbag, because Blender 5.0 removed
action.fcurves. User preferences are never changed.
"""
import math

import bpy
from mathutils import Vector

MOVES = ("dolly", "push_in", "slider", "crane", "orbit")


# ---------------------------------------------------------------- camera setup

def level_heading(location, look_at):
    """Z rotation (radians) for a level camera at `location` looking toward `look_at`.

    A camera with rotation (90 deg, 0, 0) looks along +Y; rotation Z = theta looks along
    (-sin theta, cos theta, 0), so theta = atan2(-dx, dy).
    """
    dx = look_at[0] - location[0]
    dy = look_at[1] - location[1]
    return math.atan2(-dx, dy)


def shift_for_target(location, look_at, lens, sensor_width=36.0):
    """Approximate shift_y that centres `look_at` vertically in a level, landscape frame.

    shift_y ~= (dh / d) * (lens / sensor_width). Derived from pinhole geometry (shift is a
    fraction of the larger sensor side), not quoted from the manual: check in camera view.
    """
    dx = look_at[0] - location[0]
    dy = look_at[1] - location[1]
    d = math.hypot(dx, dy)
    if d < 1e-6:
        return 0.0
    dh = look_at[2] - location[2]
    return (dh / d) * (lens / sensor_width)


def create_camera(name, location, look_at, lens=28.0, shift_x=0.0, shift_y=None,
                  level=True, sensor_width=36.0, dof_fstop=None, focus_object=None,
                  make_active=True, collection_name="CINE_Cameras"):
    """Create (or replace) a camera object. level=True keeps verticals straight.

    shift_y=None with level=True computes the shift that centres look_at vertically.
    level=False points the camera straight at look_at (three-point perspective).
    """
    scene = bpy.context.scene
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)

    data = bpy.data.cameras.new(name)
    data.lens_unit = 'MILLIMETERS'
    data.lens = lens
    data.sensor_fit = 'AUTO'
    data.sensor_width = sensor_width
    data.clip_start = 0.05
    data.clip_end = 2000.0
    cam = bpy.data.objects.new(name, data)

    coll = bpy.data.collections.get(collection_name)
    if coll is None:
        coll = bpy.data.collections.new(collection_name)
        scene.collection.children.link(coll)
    coll.objects.link(cam)

    cam.location = Vector(location)
    if level:
        cam.rotation_euler = (math.radians(90.0), 0.0, level_heading(location, look_at))
        if shift_y is None:
            shift_y = shift_for_target(location, look_at, lens, sensor_width)
    else:
        direction = Vector(look_at) - Vector(location)
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        shift_y = 0.0 if shift_y is None else shift_y
    data.shift_x = shift_x
    data.shift_y = shift_y

    if dof_fstop is not None:
        data.dof.use_dof = True
        data.dof.aperture_fstop = dof_fstop
        if focus_object is not None:
            data.dof.focus_object = focus_object
        else:
            data.dof.focus_distance = (Vector(look_at) - Vector(location)).length

    cam["cine_look_at"] = list(look_at)
    if make_active:
        scene.camera = cam
    return cam


# ---------------------------------------------------------------- F-curve access (5.x)

def _channelbag(id_owner):
    """Return the channelbag holding the F-curves of id_owner's assigned action slot."""
    ad = id_owner.animation_data
    if ad is None or ad.action is None:
        return None
    try:
        from bpy_extras import anim_utils
        return anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
    except (ImportError, AttributeError):
        # Fallback: walk layered action data directly (layers -> strips -> channelbag(slot)).
        for layer in ad.action.layers:
            for strip in layer.strips:
                cb = strip.channelbag(ad.action_slot)
                if cb is not None:
                    return cb
    return None


def ease_keys(id_owner, mode="SINE", frame_range=None):
    """Set ease-in/out on keys of id_owner's F-curves. mode: 'SINE' | 'BEZIER' | 'LINEAR'.

    frame_range=(a, b) limits it to keys inside that range (other shots stay untouched).
    Returns the number of keys changed.
    """
    cb = _channelbag(id_owner)
    if cb is None:
        return 0
    changed = 0
    for fc in cb.fcurves:
        for kp in fc.keyframe_points:
            if frame_range and not (frame_range[0] - 0.5 <= kp.co.x <= frame_range[1] + 0.5):
                continue
            if mode == "BEZIER":
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = 'AUTO_CLAMPED'
                kp.handle_right_type = 'AUTO_CLAMPED'
            elif mode == "LINEAR":
                kp.interpolation = 'LINEAR'
            else:
                kp.interpolation = 'SINE'
                kp.easing = 'EASE_IN_OUT'
            changed += 1
        fc.update()
    return changed


# ---------------------------------------------------------------- moves

def _key(obj, path, frame):
    obj.keyframe_insert(data_path=path, frame=frame)


def _ensure_track_to(cam, target_name, look_at):
    empty = bpy.data.objects.get(target_name)
    if empty is None:
        empty = bpy.data.objects.new(target_name, None)
        empty.empty_display_type = 'SPHERE'
        empty.empty_display_size = 0.3
        for coll in cam.users_collection:
            coll.objects.link(empty)
    empty.location = Vector(look_at)
    con = cam.constraints.get("CINE_TrackTo") or cam.constraints.new('TRACK_TO')
    con.name = "CINE_TrackTo"
    con.target = empty
    con.track_axis = 'TRACK_NEGATIVE_Z'
    con.up_axis = 'UP_Y'
    return empty


def keyframe_move(cam, move, start_frame=1, seconds=8.0, distance=2.0, fps=None,
                  angle_deg=25.0, end_lens=None, hold_seconds=0.0, ease="SINE",
                  look_at=None, set_scene_range=True):
    """Keyframe one named move on `cam`. Returns a dict describing what was keyed.

    seconds: length of the motion; hold_seconds: still frames added after it (end on a hold).
    distance: metres (dolly, push_in, slider, crane). angle_deg: orbit sweep.
    end_lens: optional focal length at the end (push_in / dolly) - keep the change small.
    """
    if move not in MOVES:
        raise ValueError("move must be one of %s" % (MOVES,))
    scene = bpy.context.scene
    fps = fps or scene.render.fps
    end_frame = start_frame + max(1, round(seconds * fps))
    look_at = look_at or tuple(cam.get("cine_look_at", (0.0, 0.0, 1.6)))
    report = {"camera": cam.name, "move": move, "frames": [start_frame, end_frame], "fps": fps}

    keyed = cam
    if move in ("dolly", "slider", "crane", "push_in"):
        rot = cam.rotation_euler.to_matrix()
        forward = rot @ Vector((0.0, 0.0, -1.0))
        right = rot @ Vector((1.0, 0.0, 0.0))
        if move == "dolly":
            forward.z = 0.0  # keep eye height: level dolly
            step = forward.normalized() * distance
        elif move == "slider":
            right.z = 0.0
            step = right.normalized() * distance
        elif move == "crane":
            step = Vector((0.0, 0.0, distance))
        else:  # push_in
            _ensure_track_to(cam, cam.name + "_target", look_at)
            to_target = Vector(look_at) - cam.location
            to_target.z = 0.0
            step = to_target.normalized() * distance
        start = cam.location.copy()
        cam.location = start
        _key(cam, "location", start_frame)
        cam.location = start + step
        _key(cam, "location", end_frame)
        cam.location = start
        report["metres"] = round(step.length, 3)
        report["speed_m_per_s"] = round(step.length / seconds, 3)
        if move == "crane":
            report["note"] = "camera stays level; animate data.shift_y if the framing must follow"
        if move == "push_in" and abs(cam.location.z - look_at[2]) > 0.3:
            report["note"] = "Track To tilts the camera toward the target: verticals converge"
    else:  # orbit
        pivot_name = cam.name + "_pivot"
        pivot = bpy.data.objects.get(pivot_name)
        if pivot is None:
            pivot = bpy.data.objects.new(pivot_name, None)
            pivot.empty_display_type = 'PLAIN_AXES'
            for coll in cam.users_collection:
                coll.objects.link(pivot)
        pivot.location = Vector((look_at[0], look_at[1], 0.0))
        pivot.rotation_euler = (0.0, 0.0, 0.0)
        world = cam.matrix_world.copy()
        cam.parent = pivot
        cam.matrix_parent_inverse = pivot.matrix_world.inverted()
        cam.matrix_world = world
        _key(pivot, "rotation_euler", start_frame)
        pivot.rotation_euler = (0.0, 0.0, math.radians(angle_deg))
        _key(pivot, "rotation_euler", end_frame)
        pivot.rotation_euler = (0.0, 0.0, 0.0)
        keyed = pivot
        radius = (Vector((cam.location.x, cam.location.y, 0.0)) - pivot.location).length
        arc = radius * math.radians(abs(angle_deg))
        report["degrees"] = angle_deg
        report["speed_m_per_s"] = round(arc / seconds, 3)

    if end_lens is not None and move in ("dolly", "push_in"):
        cam.data.keyframe_insert(data_path="lens", frame=start_frame)
        start_lens = cam.data.lens
        cam.data.lens = end_lens
        cam.data.keyframe_insert(data_path="lens", frame=end_frame)
        cam.data.lens = start_lens
        ease_keys(cam.data, ease, (start_frame, end_frame))

    report["eased_keys"] = ease_keys(keyed, ease, (start_frame, end_frame))
    last = end_frame + round(hold_seconds * fps)
    report["last_frame"] = last
    if set_scene_range:
        scene.render.fps = fps
        scene.frame_start = start_frame
        scene.frame_end = last
    return report


def describe(cam):
    """Short text summary of a camera for checking framing settings."""
    d = cam.data
    rot = [round(math.degrees(a), 2) for a in cam.rotation_euler]
    lines = [
        "camera %s at %s rot %s" % (cam.name, tuple(round(v, 3) for v in cam.location), rot),
        "lens %.1f mm, sensor %.1f mm, shift x %.3f y %.3f" % (d.lens, d.sensor_width, d.shift_x, d.shift_y),
        "level (two-point): %s" % (abs(rot[0] - 90.0) < 0.01 and abs(rot[1]) < 0.01),
        "dof: %s f/%.1f" % (d.dof.use_dof, d.dof.aperture_fstop),
    ]
    if abs(d.shift_y) > 0.3:
        lines.append("warning: shift_y > 0.3 stretches the frame edge; raise the camera instead")
    return "\n".join(lines)
