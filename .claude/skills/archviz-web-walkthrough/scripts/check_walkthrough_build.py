#!/usr/bin/env python3
"""Read-only build check for a web walkthrough .glb / .gltf (Python stdlib only).

Usage:
    python check_walkthrough_build.py model.glb [--mobile|--desktop] [--json]

Reports file size vs the 25 MiB Cloudflare Pages per-file limit, counts, texture
formats and sizes (estimated GPU memory), TEXCOORD_1 (lightmap UV), tour extras
(spawn / hotspot / room / lightmap / collider / nocollide / slot), KHR_materials_variants
and a draw-call estimate. Budgets are rules of thumb, not official limits.
Exit code: 0 = no errors, 1 = errors found, 2 = could not read the file.
"""
import argparse
import json
import os
import struct
import sys

MIB = 1024 * 1024
CLOUDFLARE_FILE_LIMIT = 25 * MIB
FIRST_LOAD_WARN = 20 * MIB  # rule of thumb
BUDGETS = {  # rules of thumb (see SKILL.md); measure on real devices
    "mobile": {"draw_calls": 100, "max_texture": 2048, "gpu_mib": 200, "triangles": 500_000},
    "desktop": {"draw_calls": 300, "max_texture": 4096, "gpu_mib": 1000, "triangles": 3_000_000},
}
TOUR_KEYS = ("spawn", "hotspot", "room", "lightmap", "collider", "nocollide", "slot")


def read_gltf(path):
    """Return (json_dict, bin_chunk_bytes_or_None)."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] == b"glTF":
        magic, version, length = struct.unpack_from("<4sII", data, 0)
        if version != 2:
            raise ValueError(f"GLB version {version}, expected 2")
        if length != len(data):
            raise ValueError(f"GLB header length {length} != file size {len(data)}")
        off, doc, binchunk = 12, None, None
        while off + 8 <= len(data):
            clen, ctype = struct.unpack_from("<I4s", data, off)
            chunk = data[off + 8: off + 8 + clen]
            if ctype == b"JSON":
                doc = json.loads(chunk.decode("utf-8"))
            elif ctype == b"BIN\x00":
                binchunk = chunk
            off += 8 + clen
        if doc is None:
            raise ValueError("GLB has no JSON chunk")
        return doc, binchunk
    return json.loads(data.decode("utf-8-sig")), None


def image_bytes(doc, binchunk, img, base_dir):
    if "bufferView" in img and binchunk is not None:
        bv = doc["bufferViews"][img["bufferView"]]
        if bv.get("buffer", 0) == 0:
            start = bv.get("byteOffset", 0)
            return binchunk[start:start + bv["byteLength"]]
    uri = img.get("uri", "")
    if uri and not uri.startswith("data:"):
        p = os.path.join(base_dir, uri.replace("%20", " "))
        if os.path.isfile(p):
            with open(p, "rb") as f:
                return f.read(1 << 16)  # header is enough
    return None


def image_info(b):
    """Return (format, width, height) from the file header, or (fmt, None, None)."""
    if not b:
        return "unknown", None, None
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", b[16:24])
        return "png", w, h
    if b[:12] == b"\xabKTX 20\xbb\r\n\x1a\n":
        w, h = struct.unpack_from("<II", b, 20)
        return "ktx2", w, h
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        kind = b[12:16]
        if kind == b"VP8X":
            w = 1 + int.from_bytes(b[24:27], "little")
            h = 1 + int.from_bytes(b[27:30], "little")
            return "webp", w, h
        if kind == b"VP8L":
            bits = int.from_bytes(b[21:25], "little")
            return "webp", (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if kind == b"VP8 ":
            w, h = struct.unpack_from("<HH", b, 26)
            return "webp", w & 0x3FFF, h & 0x3FFF
        return "webp", None, None
    if b[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(b):
            if b[i] != 0xFF:
                i += 1
                continue
            marker = b[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", b[i + 5:i + 9])
                return "jpeg", w, h
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
        return "jpeg", None, None
    return "unknown", None, None


def gpu_mib(fmt, w, h):
    """Rough decoded size with mipmaps. KTX2 assumed transcoded to 8 bpp (BC7/ASTC4x4)."""
    if not w or not h:
        return 0.0
    bpp = 1.0 if fmt == "ktx2" else 4.0
    return w * h * bpp * 4 / 3 / MIB


def scene_nodes(doc):
    """Yield node indices reachable from the default scene (or all scenes)."""
    scenes = doc.get("scenes", [])
    roots = []
    if "scene" in doc and scenes:
        roots = scenes[doc["scene"]].get("nodes", [])
    else:
        for s in scenes:
            roots += s.get("nodes", [])
    seen, stack = set(), list(roots)
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        yield n
        stack += doc["nodes"][n].get("children", [])


def check(path, profile):
    errors, warns, info = [], [], []
    size = os.path.getsize(path)
    base_dir = os.path.dirname(os.path.abspath(path))
    doc, binchunk = read_gltf(path)

    ext_total = 0
    for buf in doc.get("buffers", []):
        uri = buf.get("uri")
        if uri and not uri.startswith("data:"):
            p = os.path.join(base_dir, uri)
            if os.path.isfile(p):
                s = os.path.getsize(p)
                ext_total += s
                if s > CLOUDFLARE_FILE_LIMIT:
                    errors.append(f"{uri} is {s / MIB:.1f} MiB > 25 MiB (Cloudflare Pages per-file limit)")
            else:
                errors.append(f"missing buffer file {uri}")
    if size > CLOUDFLARE_FILE_LIMIT:
        errors.append(f"file is {size / MIB:.1f} MiB > 25 MiB (Cloudflare Pages per-file limit) - split per floor")
    elif size + ext_total > FIRST_LOAD_WARN:
        warns.append(f"download {(size + ext_total) / MIB:.1f} MiB > ~20 MiB first-load rule of thumb")

    nodes, meshes = doc.get("nodes", []), doc.get("meshes", [])
    materials, textures, images = doc.get("materials", []), doc.get("textures", []), doc.get("images", [])
    used = doc.get("extensionsUsed", [])
    counts = {k: len(doc.get(k, [])) for k in ("nodes", "meshes", "materials", "textures", "images", "accessors")}
    counts["primitives"] = sum(len(m.get("primitives", [])) for m in meshes)

    # Draw calls / triangles: each mesh instance draws once per primitive; GPU instancing = 1.
    draw_calls, triangles, uv1_prims, prims_total = 0, 0, 0, 0
    accessors = doc.get("accessors", [])
    for ni in scene_nodes(doc):
        n = nodes[ni]
        if "mesh" not in n:
            continue
        for p in meshes[n["mesh"]].get("primitives", []):
            draw_calls += 1
            mode = p.get("mode", 4)
            cnt = accessors[p["indices"]]["count"] if "indices" in p else accessors[p["attributes"]["POSITION"]]["count"]
            inst = 1
            gi = n.get("extensions", {}).get("EXT_mesh_gpu_instancing")
            if gi and "TRANSLATION" in gi.get("attributes", {}):
                inst = accessors[gi["attributes"]["TRANSLATION"]]["count"]
            if mode == 4:
                triangles += cnt // 3 * inst
    for m in meshes:
        for p in m.get("primitives", []):
            prims_total += 1
            if "TEXCOORD_1" in p.get("attributes", {}):
                uv1_prims += 1

    # Textures
    tex_rows, total_gpu, non_ktx2, max_dim = [], 0.0, 0, 0
    for ti, t in enumerate(textures):
        src = t.get("source")
        exts = t.get("extensions", {})
        for e in ("KHR_texture_basisu", "EXT_texture_webp", "EXT_texture_avif"):
            if e in exts:
                src = exts[e].get("source", src)
        if src is None or src >= len(images):
            continue
        img = images[src]
        fmt, w, h = image_info(image_bytes(doc, binchunk, img, base_dir))
        if fmt == "unknown":
            mt = img.get("mimeType", "") or os.path.splitext(img.get("uri", ""))[1]
            fmt = mt.split("/")[-1].lstrip(".") or "unknown"
        mem = gpu_mib(fmt, w, h)
        total_gpu += mem
        non_ktx2 += fmt != "ktx2"
        max_dim = max(max_dim, w or 0, h or 0)
        tex_rows.append({"texture": ti, "name": img.get("name", ""), "format": fmt, "size": f"{w}x{h}" if w else "?", "gpu_mib": round(mem, 1)})

    # Tour extras
    tour = {k: [] for k in TOUR_KEYS}
    colliders = []
    for i, n in enumerate(nodes):
        ex = n.get("extras") or {}
        name = n.get("name", f"node{i}")
        for k in TOUR_KEYS:
            if k in ex:
                tour[k].append({"node": name, "value": ex[k]})
        if name.upper().startswith("COL_") or ex.get("collider"):
            colliders.append(name)
    for m in meshes:  # extras can also sit on meshes
        ex = m.get("extras") or {}
        for k in TOUR_KEYS:
            if k in ex:
                tour[k].append({"mesh": m.get("name", "?"), "value": ex[k]})

    # Variants
    variants = [v.get("name") for v in doc.get("extensions", {}).get("KHR_materials_variants", {}).get("variants", [])]
    mapped = sum(1 for m in meshes for p in m.get("primitives", []) if "KHR_materials_variants" in p.get("extensions", {}))

    # --- findings ---
    b = BUDGETS[profile]
    info.append(f"{os.path.basename(path)}: {size / MIB:.2f} MiB" + (f" + {ext_total / MIB:.2f} MiB external buffers" if ext_total else ""))
    info.append("counts: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    info.append(f"draw calls (est., before culling): {draw_calls}; triangles (est.): {triangles:,}")
    info.append("extensionsUsed: " + (", ".join(used) if used else "none"))
    if draw_calls > b["draw_calls"]:
        warns.append(f"~{draw_calls} draw calls > {b['draw_calls']} ({profile} rule of thumb) - merge static meshes per room, use GPU instancing")
    if triangles > b["triangles"]:
        warns.append(f"~{triangles:,} triangles > {b['triangles']:,} ({profile} rule of thumb)")

    if textures:
        info.append(f"textures: {len(textures)}, {non_ktx2} not KTX2, max {max_dim}px, est. GPU {total_gpu:.0f} MiB (with mipmaps)")
        if non_ktx2:
            warns.append(f"{non_ktx2} texture(s) not KTX2 - full RGBA8 in GPU memory (fine for small tours)")
        if max_dim > b["max_texture"]:
            warns.append(f"largest texture {max_dim}px > {b['max_texture']} ({profile} rule of thumb)")
        if total_gpu > b["gpu_mib"]:
            warns.append(f"est. texture GPU memory {total_gpu:.0f} MiB > {b['gpu_mib']} MiB ({profile} rule of thumb)")
    if "KHR_texture_basisu" in used:
        info.append("KTX2 used: page needs KTX2Loader + basis transcoder files")
    for e, need in (("KHR_draco_mesh_compression", "DRACOLoader + draco decoder"),
                    ("EXT_meshopt_compression", "MeshoptDecoder"), ("KHR_meshopt_compression", "MeshoptDecoder (r186+)")):
        if e in used:
            info.append(f"{e}: page needs {need}")

    lm_users = tour["lightmap"]
    info.append(f"TEXCOORD_1 (lightmap UV) on {uv1_prims}/{prims_total} primitives")
    if lm_users and uv1_prims == 0:
        errors.append("lightmap extras present but no TEXCOORD_1 - lost in export or pruned (use prune --keep-attributes true)")
    elif uv1_prims == 0:
        info.append("no TEXCOORD_1: fine for unlit/baseColor-baked or real-time lighting")
    for lm in lm_users:
        f = os.path.join(base_dir, str(lm["value"]))
        if not os.path.isfile(f):
            warns.append(f"lightmap file not found next to the model: {lm['value']} ({lm.get('node') or lm.get('mesh')})")

    if not tour["spawn"]:
        warns.append("no 'spawn' extra - the template starts at the model centre (may be inside a wall)")
    elif len(tour["spawn"]) > 1:
        warns.append(f"{len(tour['spawn'])} spawn markers; the last one found wins")
    info.append(f"hotspots: {', '.join(str(h['value']) for h in tour['hotspot']) or 'none'}")
    info.append(f"rooms: {', '.join(sorted({str(r['value']) for r in tour['room']})) or 'none'}")
    if tour["slot"]:
        info.append(f"furniture slots: {', '.join(str(s['value']) for s in tour['slot'])}")
    if colliders:
        info.append(f"collision meshes (COL_* / collider): {len(colliders)}")
    else:
        warns.append("no COL_* / collider meshes - visual meshes will be used for collision (slower, furniture snags)")
    if variants:
        info.append(f"KHR_materials_variants: {len(variants)} variant(s) [{', '.join(map(str, variants))}], {mapped} primitive(s) mapped")
    if not any(tour.values()) and nodes:
        warns.append("no tour extras at all - Custom Properties off at export, or removed by prune (use --keep-extras true --keep-leaves true)")

    return {"errors": errors, "warnings": warns, "info": info, "textures": tex_rows, "tour": tour,
            "variants": variants, "counts": counts, "draw_calls": draw_calls, "triangles": triangles}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--mobile", dest="profile", action="store_const", const="mobile")
    g.add_argument("--desktop", dest="profile", action="store_const", const="desktop")
    ap.add_argument("--json", action="store_true", help="print the full report as JSON")
    a = ap.parse_args()
    profile = a.profile or "mobile"
    try:
        r = check(a.model, profile)
    except (OSError, ValueError, KeyError, IndexError, struct.error, json.JSONDecodeError) as e:
        print(f"ERROR could not read {a.model}: {e}")
        return 2
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print(f"Budget profile: {profile} (rules of thumb)")
        for line in r["info"]:
            print("INFO ", line)
        for t in r["textures"]:
            print(f"  tex {t['texture']}: {t['format']} {t['size']} ~{t['gpu_mib']} MiB {t['name']}")
        for line in r["warnings"]:
            print("WARN ", line)
        for line in r["errors"]:
            print("ERROR", line)
        print(f"-- {len(r['errors'])} error(s), {len(r['warnings'])} warning(s)")
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
