"""Blender 5.x: export ControlNet-ready passes through compositor File Output nodes.

Run inside Blender (e.g. through the blender MCP's execute_blender_code):

    import runpy
    ep = runpy.run_path(r"<skill>/scripts/export_passes_bpy.py")
    print(ep["setup"](r"C:/proj/passes"))
    print(ep["render_still"]())
    ep["restore"]()

Written against the Blender 5.0 release notes (compositing_node_group, File Output
directory/file_name/file_output_items, pass "Depth" instead of "Z") and the 5.2 API docs.
NOT RUN IN BLENDER when written: names marked UNVERIFIED have fallbacks; if something
still fails, read the error, fix this file and tell the user.

Outputs (in out_dir):
  beauty.png              8-bit RGBA      img2img base / clay reference
  depth.png               16-bit BW       normalized, inverted: near = white
  mist.png                16-bit BW       inverted: near = white (set mist start/depth!)
  normal.exr              float           WORLD-space normal (convert or use a preprocessor)
  index_<n>.png           8-bit BW        ID mask for each pass_index in mask_indices
  passes.exr              multilayer EXR  every Render Layers output incl. Cryptomatte
"""
import os
import bpy

TREE_NAME = "AIR_Passes"
PREV_KEY = "air_prev_compositor"
ALL_PASSES = ("beauty", "depth", "mist", "normal", "index", "crypto", "lines")


def _first_type(nodes, type_names):
    """Create the first node type that exists in this Blender version."""
    last = None
    for t in type_names:
        try:
            return nodes.new(t)
        except Exception as exc:  # unknown type in this version
            last = exc
    raise RuntimeError("none of these node types exist: %s (%s)" % (type_names, last))


def _out(node, names):
    """Find an enabled output socket by any of several names (names changed in 5.0)."""
    for n in names:
        s = node.outputs.get(n)
        if s is not None and getattr(s, "enabled", True):
            return s
    raise KeyError("Render Layers has none of %s enabled; outputs: %s"
                   % (names, [o.name for o in node.outputs if getattr(o, "enabled", True)]))


def _file_output(tree, out_dir, name, fmt="PNG", depth="8", mode="RGBA", multilayer=False):
    fo = tree.nodes.new("CompositorNodeOutputFile")
    fo.label = "AIR " + name
    fo.directory = out_dir                      # 5.0: was base_path
    fo.file_name = "" if not multilayer else name
    f = fo.format
    if hasattr(f, "media_type"):                # UNVERIFIED: 5.x image/multilayer/video switch
        try:
            f.media_type = "MULTI_LAYER_IMAGE" if multilayer else "IMAGE"
        except Exception:
            pass
    f.file_format = "OPEN_EXR_MULTILAYER" if (multilayer and not hasattr(f, "media_type")) else fmt
    if multilayer and hasattr(f, "media_type"):
        try:
            f.file_format = "OPEN_EXR"
        except Exception:
            pass
    try:
        f.color_depth = depth
        f.color_mode = mode
    except Exception:
        pass
    items = fo.file_output_items                # 5.0: was file_slots / layer_slots
    items.clear() if hasattr(items, "clear") else None
    return fo


def _add_item(fo, name, socket_type="RGBA"):
    items = fo.file_output_items
    for call in (lambda: items.new(socket_type, name),          # UNVERIFIED signature
                 lambda: items.new(socket_type=socket_type, name=name),
                 lambda: items.new(name=name)):
        try:
            call()
            return fo.inputs[name] if name in fo.inputs else fo.inputs[-1]
        except Exception:
            continue
    raise RuntimeError("could not add a File Output item; check file_output_items.new() in this version")


def _invert(tree, src):
    """1 - x, via a Math node (compositor Math may be the shader Math node in 5.x)."""
    m = _first_type(tree.nodes, ("ShaderNodeMath", "CompositorNodeMath"))
    m.operation = "SUBTRACT"
    m.inputs[0].default_value = 1.0
    tree.links.new(src, m.inputs[1])
    return m.outputs[0]


def setup(out_dir, passes=("beauty", "depth", "mist", "normal", "index", "crypto"),
          mask_indices=(), mist_start=None, mist_depth=None, scene=None):
    scene = scene or bpy.context.scene
    if not hasattr(scene, "compositing_node_group"):
        raise RuntimeError("Blender < 5.0: this script uses the 5.x compositor API "
                           "(scene.compositing_node_group). Use scene.node_tree on older versions.")
    bad = set(passes) - set(ALL_PASSES)
    if bad:
        raise ValueError("unknown passes %s; choose from %s" % (sorted(bad), ALL_PASSES))
    out_dir = os.path.abspath(bpy.path.abspath(out_dir))
    os.makedirs(out_dir, exist_ok=True)
    vl = bpy.context.view_layer

    # 1. view-layer passes
    if "depth" in passes:
        vl.use_pass_z = True
    if "mist" in passes:
        vl.use_pass_mist = True
        w = scene.world
        if w is not None:
            if mist_start is not None:
                w.mist_settings.start = mist_start
            if mist_depth is not None:
                w.mist_settings.depth = mist_depth
    if "normal" in passes:
        vl.use_pass_normal = True
    if "index" in passes or mask_indices:
        vl.use_pass_object_index = True
    if "crypto" in passes:
        vl.use_pass_cryptomatte_object = True
        vl.use_pass_cryptomatte_material = True
    if "lines" in passes:
        scene.render.use_freestyle = True
        vl.use_freestyle = True
        try:
            vl.freestyle_settings.as_render_pass = True  # UNVERIFIED in 5.x
        except Exception:
            pass

    # 2. our own compositor tree; remember the user's
    prev = scene.compositing_node_group
    if prev is not None and prev.name != TREE_NAME:
        scene[PREV_KEY] = prev.name
    tree = bpy.data.node_groups.get(TREE_NAME)
    if tree is not None:
        bpy.data.node_groups.remove(tree)
    tree = bpy.data.node_groups.new(TREE_NAME, "CompositorNodeTree")
    scene.compositing_node_group = tree
    rl = tree.nodes.new("CompositorNodeRLayers")
    rl.scene = scene
    rl.layer = vl.name
    written = []

    def single(name, src, fmt, depth, mode, stype="RGBA"):
        fo = _file_output(tree, out_dir, name, fmt, depth, mode)
        tree.links.new(src, _add_item(fo, name, stype))
        written.append(name + (".exr" if fmt == "OPEN_EXR" else ".png"))

    if "beauty" in passes:
        single("beauty", _out(rl, ("Image",)), "PNG", "8", "RGBA")
    if "depth" in passes:
        norm = tree.nodes.new("CompositorNodeNormalize")
        tree.links.new(_out(rl, ("Depth", "Z")), norm.inputs[0])
        single("depth", _invert(tree, norm.outputs[0]), "PNG", "16", "BW", "FLOAT")
    if "mist" in passes:
        single("mist", _invert(tree, _out(rl, ("Mist",))), "PNG", "16", "BW", "FLOAT")
    if "normal" in passes:
        single("normal", _out(rl, ("Normal",)), "OPEN_EXR", "32", "RGB", "VECTOR")
    if "lines" in passes:
        try:
            single("lines", _out(rl, ("Freestyle",)), "PNG", "8", "RGBA")
        except KeyError as exc:
            written.append("lines: skipped (%s)" % exc)
    for idx in mask_indices:
        idm = tree.nodes.new("CompositorNodeIDMask")
        try:
            idm.index = int(idx)
        except Exception:  # UNVERIFIED: index may be an input socket in 5.x
            idm.inputs[-1].default_value = int(idx)
        tree.links.new(_out(rl, ("Object Index", "IndexOB")), idm.inputs[0])
        single("index_%d" % int(idx), idm.outputs[0], "PNG", "8", "BW", "FLOAT")
    if "index" in passes or "crypto" in passes:
        ml = _file_output(tree, out_dir, "passes", multilayer=True)
        for o in rl.outputs:
            if getattr(o, "enabled", True):
                tree.links.new(o, _add_item(ml, o.name, "RGBA" if o.type == "RGBA" else
                                            ("VECTOR" if o.type == "VECTOR" else "FLOAT")))
        written.append("passes.exr (multilayer)")

    return {"out_dir": out_dir, "tree": TREE_NAME, "files": written,
            "note": "Depth/Index have no anti-aliasing; mist needs start/depth covering the building."}


def render_still(scene=None):
    """Render the current frame; the File Output nodes write the files."""
    scene = scene or bpy.context.scene
    bpy.ops.render.render(write_still=False, scene=scene.name)
    return {"frame": scene.frame_current, "camera": scene.camera.name if scene.camera else None}


def restore(scene=None, remove_tree=False):
    """Put the user's previous compositor tree back."""
    scene = scene or bpy.context.scene
    prev = scene.get(PREV_KEY)
    scene.compositing_node_group = bpy.data.node_groups.get(prev) if prev else None
    if PREV_KEY in scene:
        del scene[PREV_KEY]
    if remove_tree and TREE_NAME in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[TREE_NAME])
    return {"restored": prev}
