"""Parametric facade node groups for Blender 5.x Geometry Nodes (runs in Blender's Python).

Send through the blender MCP's execute_blender_code, for example:

    import runpy
    fn = runpy.run_path(r"<skill>/scripts/facade_nodes.py")
    print(fn["build_all"]())                       # creates / replaces FP_Fins, FP_FloorStack, FP_PlanarCheck
    obj = bpy.data.objects["Envelope"]
    fn["apply"](obj, "FP_Fins", Spacing=1.2, Max_Depth=0.6, Attractor=bpy.data.objects["Sun"])
    print(fn["planarity_report"](obj))             # how many faces are not flat (fabrication check)
    print(fn["find_floating"](obj))                # pieces that touch nothing (must be empty)

Groups (all are modifier node groups, `is_modifier = True`):

FP_Fins        Vertical fins on an envelope mesh. Fins stand on every horizontal edge
               of the mesh (= floor / slab lines, except the roof line), every `Spacing`
               metres, back face on the wall, from that line up `Fin Height` (set it to
               the floor-to-floor height so each fin runs slab to slab). An attractor
               object makes fins deeper near it. Output = envelope + fins (realized).
FP_FloorStack  Stacked floor slabs from a closed footprint curve (centred on the object
               origin): `Floors` storeys of `Floor Height`, `Slab Thickness`, `Twist`
               degrees per floor, plus a core (the footprint shrunk by `Core Scale`)
               running from the ground slab to the roof slab so no slab floats.
FP_PlanarCheck Paints flat faces grey and non-flat faces red and stores a boolean face
               attribute `fp_planar`. Flat quads can be cut from sheet glass/metal;
               red ones need triangulating, cold-bending or a different surface.

Node identifiers come from the Blender 5.2 API docs (checked in the research notes);
socket names follow the node UI and are looked up through `_sock()`, which raises an
error listing the real socket names if one differs, so a mismatch is quick to fix.
Save the .blend first: execute_blender_code can't be undone in one step.
"""
import math

GROUPS = ("FP_Fins", "FP_FloorStack", "FP_PlanarCheck")


# --------------------------------------------------------------------------------------
# Pure-Python helpers (no bpy; tested outside Blender)
# --------------------------------------------------------------------------------------
def islands(n_verts, edges):
    """Union-find: return a list mapping each vertex index to an island id (0..k-1)."""
    parent = list(range(n_verts))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    ids, out = {}, []
    for v in range(n_verts):
        out.append(ids.setdefault(find(v), len(ids)))
    return out


def unsupported(n_islands, grounded, touching):
    """Islands not connected to the ground through a chain of touching islands.

    grounded: set of island ids whose lowest point is on the ground.
    touching: iterable of (a, b) island pairs that touch or overlap.
    """
    nbrs = {i: set() for i in range(n_islands)}
    for a, b in touching:
        if a != b:
            nbrs[a].add(b)
            nbrs[b].add(a)
    seen, stack = set(grounded), list(grounded)
    while stack:
        i = stack.pop()
        for j in nbrs[i]:
            if j not in seen:
                seen.add(j)
                stack.append(j)
    return sorted(set(range(n_islands)) - seen)


def boxes_touch(a, b, tol):
    """Axis-aligned boxes ((minx,miny,minz),(maxx,maxy,maxz)) within tol of each other."""
    return all(a[0][k] - tol <= b[1][k] and b[0][k] - tol <= a[1][k] for k in range(3))


def face_flatness(points):
    """Max distance of a polygon's points from the plane through its centroid (Newell normal)."""
    n = len(points)
    nx = ny = nz = 0.0
    for i in range(n):
        x1, y1, z1 = points[i]
        x2, y2, z2 = points[(i + 1) % n]
        nx += (y1 - y2) * (z1 + z2)
        ny += (z1 - z2) * (x1 + x2)
        nz += (x1 - x2) * (y1 + y2)
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length == 0.0:
        return 0.0
    nx, ny, nz = nx / length, ny / length, nz / length
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    cz = sum(p[2] for p in points) / n
    return max(abs((p[0] - cx) * nx + (p[1] - cy) * ny + (p[2] - cz) * nz) for p in points)


# --------------------------------------------------------------------------------------
# Node-building helpers
# --------------------------------------------------------------------------------------
def _sock(sockets, *keys):
    """Find a socket by name (first match) or index; error lists what exists."""
    for k in keys:
        if isinstance(k, int):
            if k < len(sockets):
                return sockets[k]
        else:
            for s in sockets:
                if s.name == k and getattr(s, "enabled", True):
                    return s
            for s in sockets:
                if s.name == k:
                    return s
    names = [s.name for s in sockets]
    raise KeyError("socket %r not found; this Blender has %r" % (keys, names))


def _set_enum(node, prop, value, menu_socket=None):
    """Set an enum that is a node property in some versions and a menu input in others."""
    if hasattr(node, prop):
        setattr(node, prop, value)
        return True
    if menu_socket:
        for s in node.inputs:
            if s.name == menu_socket:
                for v in (value, value.title(), value.replace("_", " ").title()):
                    try:
                        s.default_value = v
                        return True
                    except (TypeError, ValueError):
                        continue
    print("facade_nodes: could not set %s.%s=%s; set it by hand" % (node.bl_idname, prop, value))
    return False


class _G:
    """Small wrapper: new nodes laid out in columns, links by socket name."""

    def __init__(self, ng):
        self.ng = ng
        self.col = 0
        self.row = 0

    def node(self, idname, col=None, **props):
        n = self.ng.nodes.new(idname)
        if col is not None and col != self.col:
            self.col, self.row = col, 0
        n.location = (self.col * 220, -self.row * 180)
        self.row += 1
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def link(self, out_node, out_key, in_node, in_key):
        o = _sock(out_node.outputs, *(out_key if isinstance(out_key, tuple) else (out_key,)))
        i = _sock(in_node.inputs, *(in_key if isinstance(in_key, tuple) else (in_key,)))
        self.ng.links.new(o, i)

    def math(self, op, a=None, b=None, col=None):
        n = self.node("ShaderNodeMath", col, operation=op)
        for idx, v in ((0, a), (1, b)):
            if v is None:
                continue
            if isinstance(v, tuple):
                self.link(v[0], v[1], n, idx)
            else:
                n.inputs[idx].default_value = v
        return n

    def vmath(self, op, a=None, b=None, scale=None, col=None):
        n = self.node("ShaderNodeVectorMath", col, operation=op)
        for idx, v in ((0, a), (1, b)):
            if v is None:
                continue
            if isinstance(v, tuple) and len(v) == 2 and not isinstance(v[0], (int, float)):
                self.link(v[0], v[1], n, idx)
            else:
                n.inputs[idx].default_value = v
        if scale is not None:
            s = _sock(n.inputs, "Scale", 3)
            if isinstance(scale, tuple):
                self.ng.links.new(_sock(scale[0].outputs, scale[1]), s)
            else:
                s.default_value = scale
        return n


def _new_group(name):
    import bpy

    old = bpy.data.node_groups.get(name)
    if old is not None:
        bpy.data.node_groups.remove(old)
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.is_modifier = True
    return ng


def _io(ng, name, socket_type, default=None, lo=None, hi=None, desc="", in_out="INPUT"):
    s = ng.interface.new_socket(name, in_out=in_out, socket_type=socket_type, description=desc)
    if default is not None:
        s.default_value = default
    if lo is not None:
        s.min_value = lo
    if hi is not None:
        s.max_value = hi
    return s


def _material(name, rgba, rough=0.6, metal=0.0):
    import bpy

    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = rgba
    m.roughness = rough
    m.metallic = metal
    return m


# --------------------------------------------------------------------------------------
# FP_Fins
# --------------------------------------------------------------------------------------
def build_fins():
    ng = _new_group("FP_Fins")
    _io(ng, "Geometry", "NodeSocketGeometry")
    _io(ng, "Spacing", "NodeSocketFloat", 1.2, 0.1, 50.0, "Distance between fins along each floor line (m)")
    _io(ng, "Fin Height", "NodeSocketFloat", 3.5, 0.1, 50.0, "Floor-to-floor height so fins run slab to slab (m)")
    _io(ng, "Thickness", "NodeSocketFloat", 0.08, 0.005, 2.0, "Fin thickness along the wall (m)")
    _io(ng, "Min Depth", "NodeSocketFloat", 0.25, 0.0, 10.0, "Fin depth far from the attractor (m)")
    _io(ng, "Max Depth", "NodeSocketFloat", 0.6, 0.0, 10.0, "Fin depth at the attractor (m)")
    _io(ng, "Attractor", "NodeSocketObject")
    _io(ng, "Radius", "NodeSocketFloat", 15.0, 0.01, 1000.0, "Attractor influence radius (m)")
    _io(ng, "Horizontal Tolerance", "NodeSocketFloat", 0.02, 0.0, 1.0, "Max |dir.z| of an edge counted as a floor line")
    _io(ng, "Material", "NodeSocketMaterial")
    _io(ng, "Geometry", "NodeSocketGeometry", in_out="OUTPUT")

    g = _G(ng)
    gin = g.node("NodeGroupInput", 0)
    gout = None

    # Horizontal edges below the roof line -> floor lines.
    ev = g.node("GeometryNodeInputMeshEdgeVertices", 1)
    bbox = g.node("GeometryNodeBoundBox", 1)
    g.link(gin, "Geometry", bbox, "Geometry")
    d = g.vmath("SUBTRACT", (ev, "Position 2"), (ev, "Position 1"), col=2)
    dn = g.vmath("NORMALIZE", (d, "Vector"), col=2)
    sep = g.node("ShaderNodeSeparateXYZ", 3)
    g.link(dn, "Vector", sep, "Vector")
    absz = g.math("ABSOLUTE", (sep, "Z"), col=3)
    flat = g.math("LESS_THAN", (absz, "Value"), col=4)
    g.link(gin, "Horizontal Tolerance", flat, 1)
    # Edge mid-height below roof: (z1 + z2)/2 < max.z - 0.01
    p1 = g.node("ShaderNodeSeparateXYZ", 2)
    p2 = g.node("ShaderNodeSeparateXYZ", 2)
    g.link(ev, "Position 1", p1, "Vector")
    g.link(ev, "Position 2", p2, "Vector")
    zsum = g.math("ADD", (p1, "Z"), (p2, "Z"), col=3)
    zmid = g.math("MULTIPLY", (zsum, "Value"), 0.5, col=3)
    bmax = g.node("ShaderNodeSeparateXYZ", 2)
    g.link(bbox, "Max", bmax, "Vector")
    roof = g.math("SUBTRACT", (bmax, "Z"), 0.01, col=3)
    below = g.math("LESS_THAN", (zmid, "Value"), (roof, "Value"), col=4)
    sel = g.math("MULTIPLY", (flat, "Value"), (below, "Value"), col=5)

    m2c = g.node("GeometryNodeMeshToCurve", 6)
    g.link(gin, "Geometry", m2c, "Mesh")
    g.link(sel, "Value", m2c, "Selection")
    res = g.node("GeometryNodeResampleCurve", 7)
    _set_enum(res, "mode", "LENGTH", "Mode")
    g.link(m2c, "Curve", res, "Curve")
    g.link(gin, "Spacing", res, "Length")

    # Outward wall normal at each fin point, flattened to horizontal.
    nrm = g.node("GeometryNodeInputNormal", 6)
    sns = g.node("GeometryNodeSampleNearestSurface", 7)
    _set_enum(sns, "data_type", "FLOAT_VECTOR")
    g.link(gin, "Geometry", sns, "Mesh")
    g.link(nrm, "Normal", sns, "Value")
    flatn = g.vmath("MULTIPLY", (sns, "Value"), (1.0, 1.0, 0.0), col=8)
    nh = g.vmath("NORMALIZE", (flatn, "Vector"), col=8)

    # Attractor -> depth.
    oinfo = g.node("GeometryNodeObjectInfo", 6)
    _set_enum(oinfo, "transform_space", "RELATIVE", "Transform Space")
    g.link(gin, "Attractor", oinfo, "Object")
    pos = g.node("GeometryNodeInputPosition", 6)
    dist = g.vmath("DISTANCE", (pos, "Position"), (oinfo, "Location"), col=7)
    mr = g.node("ShaderNodeMapRange", 8)
    mr.clamp = True
    g.link(dist, "Value", mr, "Value")
    _sock(mr.inputs, "From Min").default_value = 0.0
    g.link(gin, "Radius", mr, "From Max")
    g.link(gin, "Max Depth", mr, "To Min")
    g.link(gin, "Min Depth", mr, "To Max")

    # Move each point so the fin's back face sits on the wall and its bottom on the line.
    halfd = g.math("MULTIPLY", (mr, "Result"), 0.5, col=9)
    off_n = g.vmath("SCALE", (nh, "Vector"), scale=(halfd, "Value"), col=9)
    halfh = g.math("MULTIPLY", None, 0.5, col=9)
    g.link(gin, "Fin Height", halfh, 0)
    up = g.node("ShaderNodeCombineXYZ", 9)
    g.link(halfh, "Value", up, "Z")
    off = g.vmath("ADD", (off_n, "Vector"), (up, "Vector"), col=10)
    setp = g.node("GeometryNodeSetPosition", 11)
    g.link(res, "Curve", setp, "Geometry")
    g.link(off, "Vector", setp, "Offset")

    # One unit cube per point: X = depth (outward), Y = thickness, Z = height.
    cube = g.node("GeometryNodeMeshCube", 11)
    align = g.node("FunctionNodeAlignRotationToVector", 11)
    _set_enum(align, "axis", "X", "Axis")
    _set_enum(align, "pivot_axis", "Z", "Pivot Axis")
    g.link(nh, "Vector", align, "Vector")
    scl = g.node("ShaderNodeCombineXYZ", 11)
    g.link(mr, "Result", scl, "X")
    g.link(gin, "Thickness", scl, "Y")
    g.link(gin, "Fin Height", scl, "Z")
    iop = g.node("GeometryNodeInstanceOnPoints", 12)
    g.link(setp, "Geometry", iop, "Points")
    g.link(cube, "Mesh", iop, "Instance")
    g.link(align, "Rotation", iop, "Rotation")
    g.link(scl, "Vector", iop, "Scale")
    real = g.node("GeometryNodeRealizeInstances", 13)
    g.link(iop, "Instances", real, "Geometry")
    smat = g.node("GeometryNodeSetMaterial", 14)
    g.link(real, "Geometry", smat, "Geometry")
    g.link(gin, "Material", smat, "Material")

    join = g.node("GeometryNodeJoinGeometry", 15)
    g.link(gin, "Geometry", join, "Geometry")
    g.link(smat, "Geometry", join, "Geometry")
    gout = g.node("NodeGroupOutput", 16)
    g.link(join, "Geometry", gout, "Geometry")
    return ng


# --------------------------------------------------------------------------------------
# FP_FloorStack
# --------------------------------------------------------------------------------------
def build_floor_stack():
    ng = _new_group("FP_FloorStack")
    _io(ng, "Geometry", "NodeSocketGeometry", desc="Closed footprint curve, centred on the object origin")
    _io(ng, "Floors", "NodeSocketInt", 10, 1, 300, "Storeys above the ground slab")
    _io(ng, "Floor Height", "NodeSocketFloat", 3.5, 2.0, 20.0, "Floor-to-floor height (m)")
    _io(ng, "Slab Thickness", "NodeSocketFloat", 0.3, 0.05, 2.0, "Slab thickness below each level (m)")
    _io(ng, "Twist", "NodeSocketFloat", 3.0, -90.0, 90.0, "Rotation per floor (degrees)")
    _io(ng, "Core Scale", "NodeSocketFloat", 0.35, 0.05, 0.9, "Core footprint = footprint scaled by this")
    _io(ng, "Flip Normals", "NodeSocketBool", False, desc="Tick if the slabs render inside-out")
    _io(ng, "Slab Material", "NodeSocketMaterial")
    _io(ng, "Core Material", "NodeSocketMaterial")
    _io(ng, "Geometry", "NodeSocketGeometry", in_out="OUTPUT")

    g = _G(ng)
    gin = g.node("NodeGroupInput", 0)

    # Slab: footprint filled, top face at z=0, thickness downwards, closed with the cap.
    fill = g.node("GeometryNodeFillCurve", 1)
    g.link(gin, "Geometry", fill, "Curve")
    negt = g.math("MULTIPLY", None, -1.0, col=1)
    g.link(gin, "Slab Thickness", negt, 0)
    down = g.node("ShaderNodeCombineXYZ", 2)
    g.link(negt, "Value", down, "Z")
    ext = g.node("GeometryNodeExtrudeMesh", 3)
    g.link(fill, "Mesh", ext, "Mesh")
    g.link(down, "Vector", ext, "Offset")
    _sock(ext.inputs, "Individual").default_value = False
    cap = g.node("GeometryNodeFlipFaces", 3)
    g.link(fill, "Mesh", cap, "Mesh")
    slab = g.node("GeometryNodeJoinGeometry", 4)
    g.link(ext, "Mesh", slab, "Geometry")
    g.link(cap, "Mesh", slab, "Geometry")
    smat = g.node("GeometryNodeSetMaterial", 5)
    g.link(slab, "Geometry", smat, "Geometry")
    g.link(gin, "Slab Material", smat, "Material")

    # Levels: Floors + 1 points (ground slab .. roof slab), Floor Height apart.
    cnt = g.math("ADD", None, 1.0, col=1)
    g.link(gin, "Floors", cnt, 0)
    step = g.node("ShaderNodeCombineXYZ", 2)
    g.link(gin, "Floor Height", step, "Z")
    line = g.node("GeometryNodeMeshLine", 3)
    _set_enum(line, "mode", "OFFSET", "Mode")
    g.link(cnt, "Value", line, "Count")
    g.link(step, "Vector", line, "Offset")

    # Twist: rotation about Z = index * twist, built by aligning X to (cos a, sin a, 0).
    idx = g.node("GeometryNodeInputIndex", 3)
    rad = g.math("RADIANS", None, col=3)
    g.link(gin, "Twist", rad, 0)
    ang = g.math("MULTIPLY", (idx, "Index"), (rad, "Value"), col=4)
    cos = g.math("COSINE", (ang, "Value"), col=5)
    sin = g.math("SINE", (ang, "Value"), col=5)
    dirv = g.node("ShaderNodeCombineXYZ", 6)
    g.link(cos, "Value", dirv, "X")
    g.link(sin, "Value", dirv, "Y")
    align = g.node("FunctionNodeAlignRotationToVector", 6)
    _set_enum(align, "axis", "X", "Axis")
    _set_enum(align, "pivot_axis", "Z", "Pivot Axis")
    g.link(dirv, "Vector", align, "Vector")
    iop = g.node("GeometryNodeInstanceOnPoints", 7)
    g.link(line, "Mesh", iop, "Points")
    g.link(smat, "Geometry", iop, "Instance")
    g.link(align, "Rotation", iop, "Rotation")
    real = g.node("GeometryNodeRealizeInstances", 8)
    g.link(iop, "Instances", real, "Geometry")

    # Core: shrunk footprint from the top of the ground slab (z=0) to the roof level.
    cs = g.node("ShaderNodeCombineXYZ", 4)
    g.link(gin, "Core Scale", cs, "X")
    g.link(gin, "Core Scale", cs, "Y")
    _sock(cs.inputs, "Z").default_value = 1.0
    shrink = g.node("GeometryNodeTransform", 5)
    g.link(fill, "Mesh", shrink, "Geometry")
    g.link(cs, "Vector", shrink, "Scale")
    top = g.math("MULTIPLY", None, None, col=5)
    g.link(gin, "Floors", top, 0)
    g.link(gin, "Floor Height", top, 1)
    upv = g.node("ShaderNodeCombineXYZ", 6)
    g.link(top, "Value", upv, "Z")
    cext = g.node("GeometryNodeExtrudeMesh", 7)
    g.link(shrink, "Geometry", cext, "Mesh")
    g.link(upv, "Vector", cext, "Offset")
    _sock(cext.inputs, "Individual").default_value = False
    ccap = g.node("GeometryNodeFlipFaces", 7)
    g.link(shrink, "Geometry", ccap, "Mesh")
    core = g.node("GeometryNodeJoinGeometry", 8)
    g.link(cext, "Mesh", core, "Geometry")
    g.link(ccap, "Mesh", core, "Geometry")
    cmat = g.node("GeometryNodeSetMaterial", 9)
    g.link(core, "Geometry", cmat, "Geometry")
    g.link(gin, "Core Material", cmat, "Material")

    join = g.node("GeometryNodeJoinGeometry", 10)
    g.link(real, "Geometry", join, "Geometry")
    g.link(cmat, "Geometry", join, "Geometry")
    flip = g.node("GeometryNodeFlipFaces", 11)
    g.link(join, "Geometry", flip, "Mesh")
    g.link(gin, "Flip Normals", flip, "Selection")
    gout = g.node("NodeGroupOutput", 12)
    g.link(flip, "Mesh", gout, "Geometry")
    return ng


# --------------------------------------------------------------------------------------
# FP_PlanarCheck
# --------------------------------------------------------------------------------------
def build_planar_check():
    ng = _new_group("FP_PlanarCheck")
    _io(ng, "Geometry", "NodeSocketGeometry")
    _io(ng, "Threshold", "NodeSocketFloat", 0.001, 0.0, 1.0, "Allowed deviation from flat (m)")
    _io(ng, "Geometry", "NodeSocketGeometry", in_out="OUTPUT")
    red = _material("FP_NonPlanar", (0.9, 0.08, 0.05, 1.0), 0.5)
    grey = _material("FP_Planar", (0.6, 0.62, 0.65, 1.0), 0.4)

    g = _G(ng)
    gin = g.node("NodeGroupInput", 0)
    planar = g.node("GeometryNodeInputMeshFaceIsPlanar", 1)
    g.link(gin, "Threshold", planar, "Threshold")
    store = g.node("GeometryNodeStoreNamedAttribute", 2)
    _set_enum(store, "data_type", "BOOLEAN")
    _set_enum(store, "domain", "FACE")
    g.link(gin, "Geometry", store, "Geometry")
    _sock(store.inputs, "Name").default_value = "fp_planar"
    g.link(planar, "Planar", store, "Value")
    all_red = g.node("GeometryNodeSetMaterial", 3)
    g.link(store, "Geometry", all_red, "Geometry")
    _sock(all_red.inputs, "Material").default_value = red
    flat_grey = g.node("GeometryNodeSetMaterial", 4)
    g.link(all_red, "Geometry", flat_grey, "Geometry")
    g.link(planar, "Planar", flat_grey, "Selection")
    _sock(flat_grey.inputs, "Material").default_value = grey
    gout = g.node("NodeGroupOutput", 5)
    g.link(flat_grey, "Geometry", gout, "Geometry")
    return ng


# --------------------------------------------------------------------------------------
# Public entry points
# --------------------------------------------------------------------------------------
def build_all():
    """Create (or replace) all three node groups. Returns their names."""
    return [build_fins().name, build_floor_stack().name, build_planar_check().name]


def apply(obj, group_name, **values):
    """Add a Geometry Nodes modifier using `group_name` to `obj` and set its inputs.

    Keyword names are the input names with spaces replaced by underscores, e.g.
    apply(obj, "FP_FloorStack", Floors=24, Floor_Height=3.6, Twist=2.5).
    Returns the modifier.
    """
    import bpy

    ng = bpy.data.node_groups.get(group_name)
    if ng is None:
        raise KeyError("%s not built yet; run build_all() first" % group_name)
    mod = obj.modifiers.new(group_name, "NODES")
    mod.node_group = ng
    ids = {}
    for item in ng.interface.items_tree:
        if getattr(item, "item_type", "SOCKET") == "SOCKET" and item.in_out == "INPUT":
            ids[item.name.replace(" ", "_")] = (item.identifier, item.socket_type)
    casts = {"NodeSocketFloat": float, "NodeSocketInt": int, "NodeSocketBool": bool}
    for k, v in values.items():
        if k not in ids:
            raise KeyError("%s has no input %r; inputs: %r" % (group_name, k, sorted(ids)))
        ident, stype = ids[k]
        # An int written into a float input would change the property type and break it.
        mod[ident] = casts[stype](v) if stype in casts else v
    obj.update_tag()
    return mod


def _evaluated_mesh(obj):
    import bpy

    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    return ev, ev.to_mesh()


def planarity_report(obj, tol=0.001):
    """Count faces of the evaluated mesh whose corners leave their plane by more than tol (m)."""
    ev, me = _evaluated_mesh(obj)
    try:
        mw = obj.matrix_world
        bad, worst, quads = [], 0.0, 0
        for p in me.polygons:
            if p.loop_total < 4:
                continue
            quads += 1
            pts = [tuple(mw @ me.vertices[v].co) for v in p.vertices]
            dev = face_flatness(pts)
            worst = max(worst, dev)
            if dev > tol:
                bad.append(p.index)
        return {"faces": len(me.polygons), "quads_or_more": quads, "non_planar": len(bad),
                "worst_deviation_m": round(worst, 5), "tolerance_m": tol, "first_bad": bad[:20]}
    finally:
        ev.to_mesh_clear()


def find_floating(obj, tol=0.02, ground_z=None):
    """Pieces of the evaluated mesh that are not connected to the ground.

    Two pieces count as connected when one's vertices lie within tol of the other's
    faces, or their faces intersect. Ground = lowest z of the whole mesh unless given.
    Returns {"pieces": n, "floating": [{"piece": i, "min": (...), "max": (...)}...]}.
    """
    from mathutils.bvhtree import BVHTree

    ev, me = _evaluated_mesh(obj)
    try:
        mw = obj.matrix_world
        co = [mw @ v.co for v in me.vertices]
        if not co:
            return {"pieces": 0, "floating": []}
        isl = islands(len(co), [tuple(e.vertices) for e in me.edges])
        k = max(isl) + 1
        lo = [[1e18] * 3 for _ in range(k)]
        hi = [[-1e18] * 3 for _ in range(k)]
        for i, c in enumerate(co):
            b = isl[i]
            for a in range(3):
                lo[b][a] = min(lo[b][a], c[a])
                hi[b][a] = max(hi[b][a], c[a])
        gz = min(v[2] for v in lo) if ground_z is None else ground_z
        grounded = {i for i in range(k) if lo[i][2] <= gz + tol}

        polys = [list(p.vertices) for p in me.polygons]
        by_island = {i: [] for i in range(k)}
        for p in polys:
            by_island[isl[p[0]]].append(p)
        verts_of = {i: [] for i in range(k)}
        for i, b in enumerate(isl):
            verts_of[b].append(i)
        trees = {}

        def tree(i):
            if i not in trees:
                ps = by_island[i]
                trees[i] = BVHTree.FromPolygons(co, ps, epsilon=0.0) if ps else None
            return trees[i]

        touching = []
        boxes = [(lo[i], hi[i]) for i in range(k)]
        for a in range(k):
            for b in range(a + 1, k):
                if not boxes_touch(boxes[a], boxes[b], tol):
                    continue
                ta, tb = tree(a), tree(b)
                hit = bool(ta and tb and ta.overlap(tb))
                if not hit and tb:
                    hit = any(tb.find_nearest(co[v], tol)[0] is not None for v in verts_of[a])
                if not hit and ta:
                    hit = any(ta.find_nearest(co[v], tol)[0] is not None for v in verts_of[b])
                if hit:
                    touching.append((a, b))
        bad = unsupported(k, grounded, touching)
        return {"pieces": k, "ground_z": round(gz, 4), "floating": [
            {"piece": i, "min": tuple(round(x, 3) for x in lo[i]), "max": tuple(round(x, 3) for x in hi[i])}
            for i in bad]}
    finally:
        ev.to_mesh_clear()


__all__ = ["build_all", "build_fins", "build_floor_stack", "build_planar_check", "apply",
           "planarity_report", "find_floating", "islands", "unsupported", "boxes_touch", "face_flatness"]
