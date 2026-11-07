"""Blender helpers for the vehicle workflow (run inside Blender, e.g. through the blender MCP; ask the user first).

    setup_blueprints({"side": r"...side.png", "top": r"...top.png", "front": r"...front.png", "rear": r"...rear.png"},
                     length_m=4.69, width_m=1.92, height_m=1.45)
        -> a gauge box of the real car size + one image empty per view, each scaled to the gauge and shown only in
           its orthographic view (the KG2 "default cube as alignment gauge" method, done numerically).
           Crop each blueprint to the car's outline first (no margins), or fine-tune the empty afterwards.
           Sheets sit behind the car for each view; if a sheet shows the car facing the wrong way, set its scale.x = -1.
           top_front="up" (default) means the top sheet has the car's nose at the top of the image; pass "right",
           "left" or "down" if your sheet is drawn another way and it is rotated to GTA's +Y.
    radial_array(obj, count)  -> Array around an empty at obj's origin. Default axis "X" = a GTA wheel's axle
           (car faces +Y, so wheels spin around X). Use axis="Z" for a main rotor, "Y" for a propeller or tail rotor
           mounted along the body.

Convention (GTA): the car faces +Y, X = right, Z = up, 1 unit = 1 m.
"""
import math
import bpy


VIEWS = {
    # view: (rotation_euler, which real dimensions map to image width / height, location axis offset)
    "side": ((math.radians(90), 0, math.radians(90)), ("length", "height")),   # seen from +X (right side)
    "top": ((0, 0, 0), ("width", "length")),                                    # seen from +Z, front up
    "front": ((math.radians(90), 0, math.radians(180)), ("width", "height")),   # seen from +Y
    "rear": ((math.radians(90), 0, 0), ("width", "height")),                    # seen from -Y
}


TOP_FRONT_ROT = {"up": 0.0, "right": math.radians(90), "down": math.radians(180), "left": math.radians(-90)}


def setup_blueprints(images, length_m, width_m, height_m, collection_name="blueprints", opacity=0.5, top_front="up"):
    dims = {"length": length_m, "width": width_m, "height": height_m}
    col = bpy.data.collections.get(collection_name) or bpy.data.collections.new(collection_name)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)

    gauge = bpy.data.objects.new("blueprint_gauge", None)          # wire box of the real size
    gauge.empty_display_type = 'CUBE'
    gauge.scale = (width_m / 2, length_m / 2, height_m / 2)
    gauge.location = (0, 0, height_m / 2)
    col.objects.link(gauge)

    made = {}
    for view, path in images.items():
        rot, (wdim, hdim) = VIEWS[view]
        if view == "top":
            if top_front not in TOP_FRONT_ROT:
                raise ValueError(f"top_front must be one of {sorted(TOP_FRONT_ROT)}")
            rot = (0, 0, TOP_FRONT_ROT[top_front])
            if top_front in ("left", "right"):              # nose runs along the image's width
                wdim, hdim = hdim, wdim
        img = bpy.data.images.load(path, check_existing=True)
        iw, ih = img.size
        if not iw or not ih:
            raise ValueError(f"cannot read {path}")
        e = bpy.data.objects.new(f"bp_{view}", None)
        e.empty_display_type = 'IMAGE'
        e.data = img
        e.rotation_euler = rot
        # empty_display_size = size of the image's longer side; fit the image's width to the real dimension
        e.empty_display_size = dims[wdim] * max(iw, ih) / iw
        e.empty_image_offset = (-0.5, -0.5)
        e.show_empty_image_orthographic = True
        e.show_empty_image_perspective = False
        e.show_empty_image_only_axis_aligned = True                # only in its own ortho view
        e.color[3] = opacity
        e.use_empty_image_alpha = True
        # push each sheet outside the car so it never hides the mesh
        off = {"side": (-width_m, 0, height_m / 2), "top": (0, 0, -0.01), "front": (0, -length_m, height_m / 2),
               "rear": (0, length_m, height_m / 2)}[view]
        e.location = off
        col.objects.link(e)
        made[view] = e
        rendered_h = dims[wdim] * ih / iw
        if abs(rendered_h - dims[hdim]) / dims[hdim] > 0.08:
            print(f"[setup_blueprints] {view}: image aspect gives {rendered_h:.3f} m for {hdim} "
                  f"but the car is {dims[hdim]:.3f} m - crop the sheet to the outline or adjust the empty")
    return gauge, made


def radial_array(obj, count, axis='X', name=None):
    """Repeat obj around its own origin: one empty at the origin rotated 360/count, Array with Object Offset.

    axis 'X' is a GTA wheel's axle (the car faces +Y). Model one spoke facing outward from the hub, with the
    obj origin on the axle, then call this."""
    pivot = bpy.data.objects.new(name or f"{obj.name}_radial", None)
    pivot.location = obj.matrix_world.translation
    rot = [0.0, 0.0, 0.0]
    rot["XYZ".index(axis)] = 2 * math.pi / count
    pivot.rotation_euler = rot
    for c in obj.users_collection:
        c.objects.link(pivot)
    arr = obj.modifiers.new("radial", 'ARRAY')
    arr.use_relative_offset = False
    arr.use_object_offset = True
    arr.offset_object = pivot
    arr.count = count
    arr.use_merge_vertices = True
    arr.use_merge_vertices_cap = True
    return arr, pivot
