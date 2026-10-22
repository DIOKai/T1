"""Colour-map pass for Blender 5.x: one flat colour per material (or per object).

Renders the same camera move as the beauty film, but every material is a flat,
unlit colour with no anti-aliasing, so an AI video/image model (ComfyUI
segmentation ControlNet, or a paid service the user chose) can follow the
regions. Uses the Workbench engine (Flat lighting, Material colour), so it is
fast and needs no material node changes. Everything it changes is stored and
put back by restore().

NOT RUN in Blender (no Blender on the authoring machine) - syntax-checked only.
Written against the Blender 5.x API pages for View3DShading (light 'FLAT',
color_type 'MATERIAL'/'OBJECT'), SceneDisplay.render_aa ('OFF'),
Material.diffuse_color and Object.color. If a call fails, fix it and tell the user.

Use through the blender MCP (ask the user first, save the .blend first):

    import runpy
    cm = runpy.run_path(r"<skill>/scripts/colormap_pass_bpy.py")
    print(cm["setup"](mode="semantic"))          # or "material" / "object"
    print(cm["legend"]())                       # material -> colour table
    cm["render_animation"](r"<project>/colormap/frame_")   # PNG sequence
    cm["restore"]()

mode="semantic": materials whose names contain a keyword (wall, floor, glass,
sofa...) get the ADE20K palette colour for that class (what segmentation
ControlNets were trained on); everything else gets a distinct hashed colour.
mode="material": a distinct colour per material. mode="object": per object.
"""

import colorsys
import hashlib
import json

import bpy

# ADE20K class colours (sRGB 0-255), from mmsegmentation's ADE20KDataset palette.
ADE20K = {
    "wall": (120, 120, 120), "building": (180, 120, 120), "sky": (6, 230, 230),
    "floor": (80, 50, 50), "tree": (4, 200, 3), "ceiling": (120, 120, 80),
    "road": (140, 140, 140), "bed": (204, 5, 255), "windowpane": (230, 230, 230),
    "grass": (4, 250, 7), "cabinet": (224, 5, 255), "sidewalk": (235, 255, 7),
    "person": (150, 5, 61), "earth": (120, 120, 70), "door": (8, 255, 51),
    "table": (255, 6, 82), "plant": (204, 255, 4), "curtain": (255, 51, 7),
    "chair": (204, 70, 3), "water": (61, 230, 250), "painting": (255, 6, 51),
    "sofa": (11, 102, 255), "shelf": (255, 7, 71), "mirror": (220, 220, 220),
    "rug": (255, 9, 92), "armchair": (8, 255, 214), "fence": (255, 184, 6),
    "desk": (10, 255, 71), "wardrobe": (7, 255, 255), "lamp": (224, 255, 8),
    "bathtub": (102, 8, 255), "railing": (255, 61, 6), "cushion": (255, 194, 7),
    "column": (255, 8, 41), "counter": (235, 12, 255), "sink": (0, 163, 255),
    "fireplace": (250, 10, 15), "refrigerator": (20, 255, 0), "stairs": (255, 224, 0),
    "pillow": (0, 235, 255), "blind": (0, 61, 255), "coffee table": (0, 255, 112),
    "toilet": (0, 255, 133), "kitchen island": (0, 255, 41), "light": (255, 173, 0),
    "chandelier": (0, 31, 255), "television receiver": (0, 255, 194),
    "swimming pool": (0, 184, 255), "vase": (0, 255, 204),
}

# Name keyword -> ADE20K class. Longer keywords are tested first.
KEYWORDS = {
    "coffee": "coffee table", "island": "kitchen island", "pool": "swimming pool",
    "glass": "windowpane", "window": "windowpane", "pane": "windowpane",
    "wall": "wall", "plaster": "wall", "brick": "wall", "concrete": "wall",
    "facade": "building", "floor": "floor", "parquet": "floor", "tile": "floor",
    "ceiling": "ceiling", "roof": "building", "door": "door", "sofa": "sofa",
    "couch": "sofa", "armchair": "armchair", "chair": "chair", "table": "table",
    "desk": "desk", "bed": "bed", "cabinet": "cabinet", "wardrobe": "wardrobe",
    "shelf": "shelf", "counter": "counter", "worktop": "counter", "curtain": "curtain",
    "blind": "blind", "rug": "rug", "carpet": "rug", "cushion": "cushion",
    "pillow": "pillow", "plant": "plant", "leaf": "plant", "tree": "tree",
    "grass": "grass", "lawn": "grass", "water": "water", "lamp": "lamp",
    "chandelier": "chandelier", "mirror": "mirror", "sink": "sink", "toilet": "toilet",
    "bath": "bathtub", "stair": "stairs", "step": "stairs", "rail": "railing",
    "column": "column", "pillar": "column", "fence": "fence", "fireplace": "fireplace",
    "fridge": "refrigerator", "tv": "television receiver", "painting": "painting",
    "vase": "vase", "road": "road", "pavement": "sidewalk",
    "sidewalk": "sidewalk", "soil": "earth", "earth": "earth",
}

_STATE = {}


def srgb_to_linear(c):
    """sRGB 0-255 -> linear 0-1 (Blender colours are linear; the Standard view transform encodes back to sRGB)."""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hashed_colour(name):
    """Stable, well-separated colour from a name (same name -> same colour every run)."""
    h = int(hashlib.md5(name.encode("utf-8")).hexdigest()[:8], 16)
    hue = (h * 0.618033988749895) % 1.0
    sat = 0.55 + ((h >> 8) % 40) / 100.0
    val = 0.65 + ((h >> 16) % 30) / 100.0
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return (round(r * 255), round(g * 255), round(b * 255))


def classify(name):
    low = name.lower()
    for kw in sorted(KEYWORDS, key=len, reverse=True):
        if kw in low:
            return KEYWORDS[kw]
    return None


def _rgba(rgb255):
    return (srgb_to_linear(rgb255[0]), srgb_to_linear(rgb255[1]), srgb_to_linear(rgb255[2]), 1.0)


def setup(mode="semantic", scene=None, sky=(6, 230, 230)):
    """Switch the scene to a flat colour-map render. Returns a summary string."""
    if mode not in ("semantic", "material", "object"):
        raise ValueError("mode must be 'semantic', 'material' or 'object'")
    if _STATE:
        raise RuntimeError("setup() already active - call restore() first")
    scene = scene or bpy.context.scene
    shading = scene.display.shading
    vs = scene.view_settings
    _STATE.update({
        "scene": scene.name,
        "engine": scene.render.engine,
        "light": shading.light,
        "color_type": shading.color_type,
        "specular": shading.show_specular_highlight,
        "shadows": shading.show_shadows,
        "cavity": shading.show_cavity,
        "outline": shading.show_object_outline,
        "render_aa": scene.display.render_aa,
        "view_transform": vs.view_transform,
        "look": vs.look,
        "exposure": vs.exposure,
        "gamma": vs.gamma,
        "world_color": tuple(scene.world.color) if scene.world else None,
        "materials": {},
        "objects": {},
    })
    legend = {}
    if mode == "object":
        for ob in scene.objects:
            if ob.type not in {"MESH", "CURVE", "SURFACE", "META", "FONT"}:
                continue
            _STATE["objects"][ob.name] = tuple(ob.color)
            rgb = hashed_colour(ob.name)
            ob.color = _rgba(rgb)
            legend[ob.name] = rgb
    else:
        for mat in bpy.data.materials:
            if mat.users == 0:
                continue
            _STATE["materials"][mat.name] = tuple(mat.diffuse_color)
            cls = classify(mat.name) if mode == "semantic" else None
            rgb = ADE20K[cls] if cls else hashed_colour(mat.name)
            mat.diffuse_color = _rgba(rgb)
            legend[mat.name] = {"rgb": rgb, "class": cls}
    _STATE["legend"] = legend

    scene.render.engine = "BLENDER_WORKBENCH"
    shading.light = "FLAT"
    shading.color_type = "OBJECT" if mode == "object" else "MATERIAL"
    shading.show_specular_highlight = False
    shading.show_shadows = False
    shading.show_cavity = False
    shading.show_object_outline = False
    scene.display.render_aa = "OFF"          # hard edges: no blended in-between colours
    vs.view_transform = "Standard"           # AgX would shift the colours
    vs.look = "None"
    vs.exposure = 0.0
    vs.gamma = 1.0
    if scene.world:
        scene.world.color = _rgba(sky)[:3]   # Workbench renders the World viewport colour as background (未验证 for 5.x)
    return f"colour map ready: mode={mode}, {len(legend)} colours, engine=BLENDER_WORKBENCH, AA off"


def legend(as_json=False):
    """Name -> colour table (send it with the frames so the AI prompt can name the regions)."""
    data = _STATE.get("legend", {})
    if as_json:
        return json.dumps(data, indent=2, ensure_ascii=False)
    lines = []
    for name, v in sorted(data.items()):
        rgb = v["rgb"] if isinstance(v, dict) else v
        cls = v.get("class") if isinstance(v, dict) else None
        lines.append(f"{name:40s} #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}  {cls or ''}")
    return "\n".join(lines)


def render_animation(filepath_prefix, scene=None):
    """Render the scene's frame range as a lossless PNG sequence (8-bit RGB) to filepath_prefix####.png."""
    scene = scene or bpy.context.scene
    img = scene.render.image_settings
    old = (scene.render.filepath, img.file_format, img.color_mode, img.color_depth, img.compression)
    try:
        if hasattr(img, "media_type"):       # 5.x: media_type must be set before file_format
            img.media_type = "IMAGE"
        img.file_format = "PNG"
        img.color_mode = "RGB"
        img.color_depth = "8"
        img.compression = 15
        scene.render.filepath = filepath_prefix
        bpy.ops.render.render(animation=True, scene=scene.name)
    finally:
        scene.render.filepath, img.file_format, img.color_mode, img.color_depth, img.compression = old
    return f"rendered frames {scene.frame_start}-{scene.frame_end} to {filepath_prefix}####.png"


def restore():
    """Put every changed setting and colour back."""
    if not _STATE:
        return "nothing to restore"
    scene = bpy.data.scenes.get(_STATE["scene"]) or bpy.context.scene
    shading = scene.display.shading
    vs = scene.view_settings
    for name, col in _STATE["materials"].items():
        mat = bpy.data.materials.get(name)
        if mat:
            mat.diffuse_color = col
    for name, col in _STATE["objects"].items():
        ob = bpy.data.objects.get(name)
        if ob:
            ob.color = col
    scene.render.engine = _STATE["engine"]
    shading.light = _STATE["light"]
    shading.color_type = _STATE["color_type"]
    shading.show_specular_highlight = _STATE["specular"]
    shading.show_shadows = _STATE["shadows"]
    shading.show_cavity = _STATE["cavity"]
    shading.show_object_outline = _STATE["outline"]
    scene.display.render_aa = _STATE["render_aa"]
    vs.view_transform = _STATE["view_transform"]
    vs.look = _STATE["look"]
    vs.exposure = _STATE["exposure"]
    vs.gamma = _STATE["gamma"]
    if scene.world and _STATE["world_color"] is not None:
        scene.world.color = _STATE["world_color"]
    _STATE.clear()
    return "restored"
