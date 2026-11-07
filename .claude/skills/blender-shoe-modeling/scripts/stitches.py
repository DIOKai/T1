"""Geometry stitches along a seam (Array Fit Curve + Curve modifier), for renders / high-poly bake sources.
Run inside Blender (blender MCP, after asking). Never ship these on a GTA shoe — bake them into the normal map.

    curve = seam_curve_from_edges(panel_obj, edge_indices, name="seam_curve")   # or any existing curve object
    stitch = make_stitch(length_mm=3.0, width_mm=0.6, height_mm=0.4)
    stitches_along(stitch, curve, gap_mm=1.5)

Avoids the classic stretching bug: both objects get applied rotation/scale, the stitch starts at its own origin and
sits at the curve object's origin before the modifiers are added.
"""
import bmesh
import bpy


def _apply_transforms(ob):
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def make_stitch(length_mm=3.0, width_mm=0.6, height_mm=0.4, name="stitch"):
    """One rounded-ish stitch lying along +X (the Array/Curve direction)."""
    l, w, h = length_mm / 1000, width_mm / 1000, height_mm / 1000
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(l, w, h), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(l / 2, 0, h / 2), verts=bm.verts)     # origin at the stitch start
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges], offset=min(w, h) * 0.35, segments=2, affect='EDGES')
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def seam_curve_from_edges(src, edge_indices, name="seam_curve"):
    """Copy the chosen edges of a mesh object into a new curve object (world space)."""
    bm = bmesh.new()
    bm.from_mesh(src.data)
    bm.edges.ensure_lookup_table()
    keep = set(edge_indices)
    bmesh.ops.delete(bm, geom=[e for e in bm.edges if e.index not in keep], context='EDGES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_edges], context='VERTS')
    bm.transform(src.matrix_world)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        bpy.ops.object.convert(target='CURVE')
    return ob


def stitches_along(stitch, curve, gap_mm=1.5):
    """Array (Fit Curve) + Curve modifiers on the stitch; returns the stitch object."""
    _apply_transforms(stitch)
    _apply_transforms(curve)
    stitch.location = curve.location        # same space: the Curve modifier maps local +X onto the path from its start
    stitch.rotation_euler = curve.rotation_euler
    arr = stitch.modifiers.new("stitch_array", 'ARRAY')
    arr.fit_type = 'FIT_CURVE'
    arr.curve = curve
    arr.use_relative_offset = True
    length = stitch.dimensions.x
    arr.relative_offset_displace = (1.0 + (gap_mm / 1000) / max(length, 1e-6), 0, 0)
    cm = stitch.modifiers.new("follow_seam", 'CURVE')
    cm.object = curve
    cm.deform_axis = 'POS_X'
    return stitch
