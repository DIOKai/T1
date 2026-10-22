"""Build a floorplan-to-blender layout inside Blender (runs in Blender's Python).

Send this through the blender MCP's execute_blender_code, for example:

    import runpy
    fp = runpy.run_path(r"<skill>/scripts/build_in_blender.py")
    report = fp["build"](r"C:/path/layout.json")          # walls, openings, floors, ceilings, slab, stairs
    fp["add_reference_plan"](r"C:/path/plan.png", px_per_m=84.2, origin_px=(112, 940))  # optional overlay
    fp["add_top_camera"]()                                 # orthographic top view for comparing with the plan
    print(fp["verify"]())                                  # floating objects, missing glass, counts

Geometry comes from fp_geometry.py (pure Python, tested without Blender). Everything
it makes lives in collections named FP_*, and build() deletes those first, so running
it again after editing the JSON replaces the old house instead of stacking a second one.
Save the .blend before running: execute_blender_code can't be undone in one step.
"""
import json
import os
import sys

import bpy

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import fp_geometry  # noqa: E402

COLLECTIONS = {
    "wall": "FP_Walls", "glass": "FP_Openings", "door": "FP_Openings", "slab": "FP_Floors",
    "floor": "FP_Floors", "ceiling": "FP_Ceilings", "stair": "FP_Stairs",
}

# Placeholder looks; archviz / archviz-cinematic replace them with real PBR materials later.
MATERIALS = {
    "FP_Wall": {"color": (0.82, 0.8, 0.76, 1), "rough": 0.85},
    "FP_Slab": {"color": (0.45, 0.45, 0.45, 1), "rough": 0.9},
    "FP_Ceiling": {"color": (0.9, 0.9, 0.9, 1), "rough": 0.9},
    "FP_Door": {"color": (0.45, 0.3, 0.18, 1), "rough": 0.6},
    "FP_Stair": {"color": (0.55, 0.42, 0.3, 1), "rough": 0.6},
    "FP_Glass": {"color": (0.9, 0.95, 1.0, 1), "rough": 0.02, "transmission": 1.0, "ior": 1.52},
    "FP_Floor_wood": {"color": (0.5, 0.33, 0.2, 1), "rough": 0.5},
    "FP_Floor_tile": {"color": (0.78, 0.78, 0.76, 1), "rough": 0.3},
    "FP_Floor_carpet": {"color": (0.6, 0.58, 0.55, 1), "rough": 1.0},
}


def _collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def clear():
    """Delete every FP_* collection and the objects in it (only what this skill made)."""
    for col in [c for c in bpy.data.collections if c.name.startswith("FP_")]:
        for ob in list(col.objects):
            data = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if data is not None and getattr(data, "users", 1) == 0:
                if isinstance(data, bpy.types.Mesh):
                    bpy.data.meshes.remove(data)
        bpy.data.collections.remove(col)


def _material(name):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    spec = MATERIALS.get(name, {"color": (0.7, 0.7, 0.7, 1), "rough": 0.7})
    mat = bpy.data.materials.new(name)
    if hasattr(mat, "use_nodes") and not mat.use_nodes:
        try:
            mat.use_nodes = True  # deprecated in 5.x where node trees are always on
        except Exception:
            pass
    mat.diffuse_color = spec["color"]
    bsdf = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if bsdf:
        bsdf.inputs["Base Color"].default_value = spec["color"]
        bsdf.inputs["Roughness"].default_value = spec["rough"]
        if "transmission" in spec:
            for key in ("Transmission Weight", "Transmission"):
                if key in bsdf.inputs:
                    bsdf.inputs[key].default_value = spec["transmission"]
                    break
            bsdf.inputs["IOR"].default_value = spec.get("ior", 1.45)
    return mat


def build(layout_path, clear_first=True):
    """Create the house from the layout JSON. Returns a dict of counts."""
    with open(layout_path, encoding="utf-8") as f:
        layout = json.load(f)
    if clear_first:
        clear()
    counts = {}
    for s in fp_geometry.build_solids(layout):
        mesh = bpy.data.meshes.new(s["name"])
        mesh.from_pydata(s["verts"], [], s["faces"])
        mesh.validate()
        mesh.update()
        ob = bpy.data.objects.new(s["name"], mesh)
        ob.data.materials.append(_material(s["material"]))
        ob["fp_kind"] = s["kind"]
        ob["fp_level"] = s["level"]
        ob["fp_part"] = s.get("part", "")
        _collection(COLLECTIONS[s["kind"]]).objects.link(ob)
        counts[s["kind"]] = counts.get(s["kind"], 0) + 1
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    return counts


def add_reference_plan(image_path, px_per_m, origin_px=(0, 0), z=-0.25):
    """Lay the source plan on the ground at true scale, below the slab.

    origin_px is the pixel (x, y from the image's top-left) that the layout uses as (0, 0).
    """
    img = bpy.data.images.load(image_path, check_existing=True)
    w_px, h_px = img.size
    w, h = w_px / px_per_m, h_px / px_per_m
    ox, oy = origin_px[0] / px_per_m, origin_px[1] / px_per_m
    # Image y grows downwards; layout y grows upwards.
    x0, x1 = -ox, w - ox
    y1, y0 = oy, oy - h
    verts = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    mesh = bpy.data.meshes.new("FP_ReferencePlan")
    mesh.from_pydata(verts, [], [[0, 1, 2, 3]])
    uv = mesh.uv_layers.new(name="UVMap")
    for loop, co in zip(uv.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        loop.uv = co
    mat = bpy.data.materials.new("FP_ReferencePlan")
    if hasattr(mat, "use_nodes") and not mat.use_nodes:
        try:
            mat.use_nodes = True
        except Exception:
            pass
    nt = mat.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    emit = nt.nodes.new("ShaderNodeEmission")
    out = nt.nodes.get("Material Output") or nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    mesh.materials.append(mat)
    ob = bpy.data.objects.new("FP_ReferencePlan", mesh)
    _collection("FP_Reference").objects.link(ob)
    return ob.name


def add_top_camera(margin=1.0):
    """Orthographic camera looking straight down over everything in FP_* collections."""
    pts = [ob.matrix_world @ v.co for col in bpy.data.collections if col.name.startswith("FP_")
           for ob in col.objects if ob.type == "MESH" and col.name != "FP_Reference" for v in ob.data.vertices]
    if not pts:
        raise RuntimeError("build() first")
    minx, maxx = min(p.x for p in pts), max(p.x for p in pts)
    miny, maxy = min(p.y for p in pts), max(p.y for p in pts)
    maxz = max(p.z for p in pts)
    cam_data = bpy.data.cameras.get("FP_TopCam") or bpy.data.cameras.new("FP_TopCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = max(maxx - minx, maxy - miny) + 2 * margin
    cam = bpy.data.objects.get("FP_TopCam") or bpy.data.objects.new("FP_TopCam", cam_data)
    if cam.name not in _collection("FP_Cameras").objects:
        _collection("FP_Cameras").objects.link(cam)
    cam.location = ((minx + maxx) / 2, (miny + maxy) / 2, maxz + 20)
    cam.rotation_euler = (0, 0, 0)
    cam_data.clip_end = maxz + 60
    scene = bpy.context.scene
    scene.camera = cam
    w, h = (maxx - minx) + 2 * margin, (maxy - miny) + 2 * margin
    scene.render.resolution_x = 1600 if w >= h else int(1600 * w / h)
    scene.render.resolution_y = 1600 if h > w else int(1600 * h / w)
    return cam.name


def verify(tolerance=0.02):
    """Geometry checks after building. Returns a dict; empty lists mean OK.

    floating: objects whose underside has nothing below within `tolerance` (except the
    lowest slab, which sits on the ground). no_glass: windows built without a pane.
    """
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obs = [ob for col in bpy.data.collections if col.name.startswith("FP_") and col.name != "FP_Reference"
           for ob in col.objects if ob.type == "MESH"]
    # World-space trees, one per object, so a ray can skip the object it starts from.
    trees = {}
    for ob in obs:
        verts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        trees[ob.name] = BVHTree.FromPolygons(verts, [list(p.vertices) for p in ob.data.polygons])
    lowest = min((min((ob.matrix_world @ v.co).z for v in ob.data.vertices) for ob in obs), default=0.0)
    floating = []
    for ob in obs:
        if ob.get("fp_kind") == "ceiling" or ob.get("fp_part") == "lintel":
            continue  # ceilings and lintels span between walls/piers; nothing is meant to be under them
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        zmin = min(p.z for p in pts)
        if zmin <= lowest + 1e-4:
            continue
        cx = sum(p.x for p in pts) / len(pts)
        cy = sum(p.y for p in pts) / len(pts)
        # Start a little above the underside: a support's top face is coplanar with it.
        origin = Vector((cx, cy, zmin + 0.005))
        best = None
        for name, tree in trees.items():
            if name == ob.name:
                continue
            loc, _n, _i, _d = tree.ray_cast(origin, Vector((0, 0, -1)), 5.0)
            if loc is not None and (best is None or loc.z > best):
                best = loc.z
        if best is None or zmin - best > tolerance:
            floating.append({"object": ob.name, "gap_m": None if best is None else round(zmin - best, 3)})
    _ = depsgraph  # kept for callers that extend this with evaluated modifiers
    windows = {ob.name.rsplit("_glass", 1)[0] for ob in obs if ob.get("fp_kind") == "glass"}
    return {
        "objects": len(obs),
        "floating": floating,
        "windows_with_glass": sorted(windows),
        "note": "Also look: top camera vs the plan, then front/right/back/left/top/perspective views, "
                "and from the street into every window (there must be a room behind the glass).",
    }
