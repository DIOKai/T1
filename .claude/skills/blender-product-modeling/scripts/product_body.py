"""Rounded-rectangle product body (method A: quad plane -> Bevel(Vertices) -> Solidify -> edge Bevel) from real millimetres.

Run inside Blender (e.g. through the blender MCP: exec this file, then call make_body). 1 Blender unit = 1 metre, the
scene only *displays* millimetres, so the result is already at real size for GTA/FiveM export.

    body = make_body("phone_body", width_mm=78.0, height_mm=163.4, depth_mm=8.25,
                     corner_radius_mm=11.0, edge_radius_mm=1.2)
    body = make_body("prop_phone", 78.0, 163.4, 8.25, 11.0, edge_radius_mm=1.2, corner_segments=6, for_game=True)

Front face looks down -Y (Numpad 1 front view), thickness goes to +Y. Modifiers stay live; call apply_all(body) before
booleans or before handing the mesh to Sollumz.

For a game prop, finish with
    col = game_ready(body)   # applies modifiers, box-unwraps UVs into 0-1 ("UVMap" -> Sollumz UV 0), adds <name>_col box
Turn the body to the orientation of a similar vanilla prop (check it in CodeWalker) before game_ready; the collision box
follows the body. In Sollumz, convert <name>_col to a Bound Box (or Composite) with a flag preset; it is a separate,
simple collision, never the visual mesh.
"""
import bmesh
import bpy


def use_millimetre_display(scene=None):
    """Show lengths in mm without changing the unit scale (1 BU stays 1 m)."""
    us = (scene or bpy.context.scene).unit_settings
    us.system = 'METRIC'
    us.scale_length = 1.0
    us.length_unit = 'MILLIMETERS'


def make_body(name, width_mm, height_mm, depth_mm, corner_radius_mm, edge_radius_mm=1.0,
              corner_segments=10, edge_segments=3, for_game=False, location=(0.0, 0.0, 0.0)):
    w, h, d = width_mm / 1000.0, height_mm / 1000.0, depth_mm / 1000.0
    r = min(corner_radius_mm / 1000.0, w / 2 - 1e-5, h / 2 - 1e-5)
    er = min(edge_radius_mm / 1000.0, d / 2 - 1e-5)
    if for_game:                       # game props: few segments, the normals do the rest
        corner_segments = min(corner_segments, 6)
        edge_segments = min(edge_segments, 2)

    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new(c) for c in ((-w / 2, 0, -h / 2), (-w / 2, 0, h / 2), (w / 2, 0, h / 2), (w / 2, 0, -h / 2))]
    f = bm.faces.new(vs)
    bm.normal_update()
    if f.normal.y > 0:                 # front must face -Y
        f.normal_flip()
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.location = location
    bpy.context.collection.objects.link(ob)

    corners = ob.modifiers.new("corner_radius", 'BEVEL')
    corners.affect = 'VERTICES'
    corners.width = r
    corners.segments = corner_segments
    corners.limit_method = 'NONE'

    shell = ob.modifiers.new("thickness", 'SOLIDIFY')
    shell.thickness = d
    shell.offset = -1.0                # grow away from the front face (+Y)
    shell.use_even_offset = True
    shell.use_rim = True

    edges = ob.modifiers.new("edge_round", 'BEVEL')
    edges.affect = 'EDGES'
    edges.width = er
    edges.segments = edge_segments
    edges.limit_method = 'ANGLE'
    edges.angle_limit = 0.5236         # 30 degrees: only the rim edges, not the rounded corners' facets
    edges.miter_outer = 'MITER_ARC'
    edges.harden_normals = True        # crisp flat faces with soft highlights (game and render)
    return ob


def apply_all(ob):
    """Apply every modifier in stack order (needed before booleans / Sollumz conversion)."""
    with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob], selected_editable_objects=[ob]):
        for m in list(ob.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
    return ob


def box_unwrap(ob, margin=0.02):
    """Box-project every face along its main normal axis, pack the six groups into 0-1 at one texel density.

    No operators, so it also works headless. Good for convex bodies (phone, box, remote); for complex shapes
    use UV > Smart UV Project in the UI instead."""
    me = ob.data
    uvl = me.uv_layers.get("UVMap") or me.uv_layers.new(name="UVMap")
    bm = bmesh.new()
    bm.from_mesh(me)
    lay = bm.loops.layers.uv.get(uvl.name)
    groups = {}
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        groups.setdefault((ax, n[ax] > 0), []).append(f)
    boxes = []
    for (ax, pos), faces in groups.items():
        u_i, v_i = [i for i in range(3) if i != ax]
        pts = [(l.vert.co[u_i] * (1 if pos else -1), l.vert.co[v_i]) for f in faces for l in f.loops]
        lo_u, lo_v = min(p[0] for p in pts), min(p[1] for p in pts)
        boxes.append([faces, u_i, v_i, pos, lo_u, lo_v,
                      max(p[0] for p in pts) - lo_u, max(p[1] for p in pts) - lo_v])
    boxes.sort(key=lambda bx: -bx[7])
    gap = margin * max(max(bx[6] for bx in boxes), max(bx[7] for bx in boxes))
    row_w = max(sum(bx[6] for bx in boxes) ** 0.5, max(bx[6] for bx in boxes))   # simple shelf packing
    x = y = shelf = 0.0
    for bx in boxes:
        if x > 0 and x + bx[6] > row_w * 1.6:
            x, y, shelf = 0.0, y + shelf + gap, 0.0
        bx.append((x, y))
        x += bx[6] + gap
        shelf = max(shelf, bx[7])
    size = max(max(bx[8][0] + bx[6] for bx in boxes), max(bx[8][1] + bx[7] for bx in boxes))
    k = (1 - 2 * margin) / size
    for faces, u_i, v_i, pos, lo_u, lo_v, w, h, (ox, oy) in boxes:
        for f in faces:
            for l in f.loops:
                u = l.vert.co[u_i] * (1 if pos else -1) - lo_u
                l[lay].uv = (margin + (ox + u) * k, margin + (oy + l.vert.co[v_i] - lo_v) * k)
    bm.to_mesh(me)
    bm.free()
    return uvl


def game_ready(ob, uv_margin=0.02):
    """Apply modifiers, unwrap UVs into 0-1 and create a matching box collision object. Returns the collision object."""
    apply_all(ob)
    me = ob.data
    box_unwrap(ob, uv_margin)
    lo = [min(v.co[i] for v in me.vertices) for i in range(3)]
    hi = [max(v.co[i] for v in me.vertices) for i in range(3)]
    cme = bpy.data.meshes.new(f"{ob.name}_col")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = [lo[i] + (v.co[i] + 0.5) * (hi[i] - lo[i]) for i in range(3)]
    bm.to_mesh(cme)
    bm.free()
    col = bpy.data.objects.new(f"{ob.name}_col", cme)
    col.display_type = 'WIRE'
    col.parent = ob
    for c in ob.users_collection:
        c.objects.link(col)
    return col


def report(ob):
    """Real-world size in mm and evaluated triangle count, to compare with the spec / a vanilla prop."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    dims = tuple(round(v * 1000, 2) for v in ev.dimensions)
    ev.to_mesh_clear()
    return {"size_mm_xyz": dims, "triangles": tris, "uv_layers": len(ob.data.uv_layers)}
