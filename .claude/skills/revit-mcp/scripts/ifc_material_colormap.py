#!/usr/bin/env python3
"""Read an IFC file (STEP text, IFC2X3 / IFC4 / IFC4X3) and build a colour map:
one flat colour per material, plus which element uses which material.

Standard library only, read-only: the IFC file is never changed. The output JSON is
meant for a three.js / web-ifc viewer that paints each element with its material's
colour (a "colour map" / material-ID render), or for checking which elements came
out of Revit without a material.

Usage:
    python ifc_material_colormap.py model.ifc -o colormap.json
    python ifc_material_colormap.py model.ifc --multi set --summary
    python ifc_material_colormap.py model.ifc --colors source   # keep Revit's own colours

Element keys in the output are the IFC step ids (the number after '#'). web-ifc's
`expressID` is the same number, so a viewer can look elements up directly.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import re
import sys
from collections import Counter, defaultdict

# --------------------------------------------------------------------------- STEP parsing


class Ref(int):
    """A '#123' reference."""


class Enum(str):
    """A '.ENUM.' value."""


class Typed:
    """A typed value such as IFCLABEL('x')."""

    __slots__ = ("type", "args")

    def __init__(self, type_, args):
        self.type = type_
        self.args = args


_X2 = re.compile(r"\\X2\\([0-9A-Fa-f]*)\\X0\\")
_X4 = re.compile(r"\\X4\\([0-9A-Fa-f]*)\\X0\\")
_X1 = re.compile(r"\\X\\([0-9A-Fa-f]{2})")
_S = re.compile(r"\\S\\(.)")


def decode_step_string(s: str) -> str:
    """Decode the ISO 10303-21 escapes Revit and others write in names."""
    s = _X2.sub(lambda m: "".join(chr(int(m.group(1)[i:i + 4], 16)) for i in range(0, len(m.group(1)), 4)), s)
    s = _X4.sub(lambda m: "".join(chr(int(m.group(1)[i:i + 8], 16)) for i in range(0, len(m.group(1)), 8)), s)
    s = _X1.sub(lambda m: bytes([int(m.group(1), 16)]).decode("latin-1"), s)
    s = _S.sub(lambda m: chr(ord(m.group(1)) + 128), s)
    return s.replace("\\\\", "\\")


_TOKENS = re.compile(r"'(?:[^']|'')*'|/\*.*?\*/|;|[^';/]+|/", re.S)


def split_statements(text: str):
    """Yield statements of the DATA section, splitting on ';' outside strings and comments."""
    start = text.find("DATA;")
    if start < 0:
        raise ValueError("no DATA; section - is this an IFC (STEP) file? (.ifcZIP / .ifcXML are not supported)")
    buf = []
    for m in _TOKENS.finditer(text, start + 5):
        tok = m.group(0)
        if tok == ";":
            stmt = "".join(buf).strip()
            buf = []
            if stmt == "ENDSEC":
                return
            if stmt:
                yield stmt
        elif tok.startswith("/*"):
            continue
        else:
            buf.append(tok)


_ENTITY = re.compile(r"#(\d+)\s*=\s*([A-Za-z0-9_]+)\s*\(", re.S)
_REF = re.compile(r"#(\d+)")
_TYPED = re.compile(r"([A-Za-z0-9_]+)\s*\(")
_NUM = re.compile(r"[-+0-9.Ee]+")


def parse_args(s: str, pos: int):
    """Parse a parenthesised argument list starting just after '('. Returns (list, new_pos)."""
    out = []
    n = len(s)
    while pos < n:
        c = s[pos]
        if c in " \t\r\n,":
            pos += 1
        elif c == ")":
            return out, pos + 1
        elif c == "(":
            sub, pos = parse_args(s, pos + 1)
            out.append(sub)
        elif c == "'":
            j = pos + 1
            parts = []
            while j < n:
                if s[j] == "'":
                    if j + 1 < n and s[j + 1] == "'":
                        parts.append("'")
                        j += 2
                        continue
                    break
                parts.append(s[j])
                j += 1
            out.append(decode_step_string("".join(parts)))
            pos = j + 1
        elif c == "#":
            m = _REF.match(s, pos)
            out.append(Ref(int(m.group(1))))
            pos = m.end()
        elif c == "$" or c == "*":
            out.append(None)
            pos += 1
        elif c == ".":
            j = s.index(".", pos + 1)
            out.append(Enum(s[pos + 1:j]))
            pos = j + 1
        elif c == '"':  # binary
            j = s.index('"', pos + 1)
            out.append(s[pos + 1:j])
            pos = j + 1
        elif c.isalpha():
            m = _TYPED.match(s, pos)
            if not m:
                raise ValueError("unexpected token near: " + s[pos:pos + 30])
            sub, pos = parse_args(s, m.end())
            out.append(Typed(m.group(1).upper(), sub))
        else:
            m = _NUM.match(s, pos)
            if not m:
                raise ValueError("unexpected token near: " + s[pos:pos + 30])
            tok = m.group(0)
            try:
                out.append(int(tok))
            except ValueError:
                out.append(float(tok))
            pos = m.end()
    raise ValueError("unbalanced parentheses")


def load_ifc(path: str):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    m = re.search(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']*)'", text)
    schema = m.group(1) if m else "unknown"
    ents = {}
    bad = 0
    for stmt in split_statements(text):
        m = _ENTITY.match(stmt)
        if not m:
            bad += 1
            continue
        try:
            args, _ = parse_args(stmt, m.end())
        except (ValueError, AttributeError):
            bad += 1
            continue
        ents[int(m.group(1))] = (m.group(2).upper(), args)
    return schema, ents, bad


# --------------------------------------------------------------------------- IFC semantics

BUILDING_ELEMENTS = {
    "IFCWALL", "IFCWALLSTANDARDCASE", "IFCWALLELEMENTEDCASE", "IFCCURTAINWALL", "IFCSLAB",
    "IFCSLABSTANDARDCASE", "IFCSLABELEMENTEDCASE", "IFCROOF", "IFCDOOR", "IFCDOORSTANDARDCASE",
    "IFCWINDOW", "IFCWINDOWSTANDARDCASE", "IFCCOLUMN", "IFCCOLUMNSTANDARDCASE", "IFCBEAM",
    "IFCBEAMSTANDARDCASE", "IFCSTAIR", "IFCSTAIRFLIGHT", "IFCRAMP", "IFCRAMPFLIGHT", "IFCRAILING",
    "IFCCOVERING", "IFCPLATE", "IFCPLATESTANDARDCASE", "IFCMEMBER", "IFCMEMBERSTANDARDCASE",
    "IFCFOOTING", "IFCPILE", "IFCBUILDINGELEMENTPROXY", "IFCFURNISHINGELEMENT", "IFCFURNITURE",
    "IFCSYSTEMFURNITUREELEMENT", "IFCCHIMNEY", "IFCSHADINGDEVICE", "IFCFLOWTERMINAL",
    "IFCSANITARYTERMINAL", "IFCLIGHTFIXTURE", "IFCGEOGRAPHICELEMENT", "IFCSITE",
}


def name_of(ents, rid):
    if rid is None or rid not in ents:
        return None
    t, a = ents[rid]
    if t == "IFCMATERIAL":
        return a[0] if a else None
    return None


def material_components(ents, rid, seen=None):
    """Return (set_name or None, [material names in order]) for any IfcMaterialSelect."""
    seen = seen or set()
    if rid is None or rid not in ents or rid in seen:
        return None, []
    seen.add(rid)
    t, a = ents[rid]
    if t == "IFCMATERIAL":
        return None, [a[0] or "(unnamed material)"]
    if t == "IFCMATERIALLAYER":
        return None, [n for n in [name_of(ents, a[0])] if n]
    if t == "IFCMATERIALLAYERSET":
        names = []
        for lr in a[0] or []:
            names += material_components(ents, lr, seen)[1]
        return (a[1] if len(a) > 1 else None), names
    if t == "IFCMATERIALLAYERSETUSAGE":
        return material_components(ents, a[0], seen)
    if t == "IFCMATERIALLIST":
        names = []
        for mr in a[0] or []:
            names += material_components(ents, mr, seen)[1]
        return None, names
    if t == "IFCMATERIALCONSTITUENTSET":
        names = []
        for cr in a[2] or []:
            names += material_components(ents, cr, seen)[1]
        return a[0], names
    if t == "IFCMATERIALCONSTITUENT":
        return None, [n for n in [name_of(ents, a[2])] if n]
    if t == "IFCMATERIALPROFILESET":
        names = []
        for pr in a[2] or []:
            names += material_components(ents, pr, seen)[1]
        return a[0], names
    if t == "IFCMATERIALPROFILE":
        return None, [n for n in [name_of(ents, a[2])] if n]
    if t in ("IFCMATERIALPROFILESETUSAGE", "IFCMATERIALPROFILESETUSAGETAPERING"):
        return material_components(ents, a[0], seen)
    return None, []


def material_source_colours(ents):
    """IfcMaterial name -> '#rrggbb' from IfcMaterialDefinitionRepresentation styles."""
    colours = {}
    for _, (t, a) in ents.items():
        if t != "IFCMATERIALDEFINITIONREPRESENTATION":
            continue
        mat = name_of(ents, a[3])
        if not mat:
            continue
        for rep in a[2] or []:
            for item in (ents.get(rep, (None, [None] * 4))[1][3] or []):
                col = styled_item_colour(ents, item)
                if col and mat not in colours:
                    colours[mat] = col
    return colours


def styled_item_colour(ents, rid):
    if rid not in ents:
        return None
    t, a = ents[rid]
    if t != "IFCSTYLEDITEM":
        return None
    stack = list(a[1] or [])
    while stack:
        s = stack.pop(0)
        if s not in ents:
            continue
        st, sa = ents[s]
        if st == "IFCPRESENTATIONSTYLEASSIGNMENT":
            stack += list(sa[0] or [])
        elif st == "IFCSURFACESTYLE":
            stack += list(sa[2] or [])
        elif st in ("IFCSURFACESTYLERENDERING", "IFCSURFACESTYLESHADING"):
            c = sa[0]
            if c in ents and ents[c][0] == "IFCCOLOURRGB":
                r, g, b = ents[c][1][1:4]
                return "#%02x%02x%02x" % tuple(max(0, min(255, round(float(v) * 255))) for v in (r, g, b))
    return None


def distinct_colour(i: int) -> str:
    """Deterministic, well-separated colours: golden-ratio hue steps, three value bands."""
    h = (i * 0.618033988749895) % 1.0
    s = (0.65, 0.45, 0.8)[i % 3]
    v = (0.9, 0.7, 0.55)[(i // 3) % 3]
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))


def build_colormap(ents, multi="first", colors="distinct"):
    warnings = []
    # type object -> instances
    type_instances = defaultdict(list)
    for _, (t, a) in ents.items():
        if t == "IFCRELDEFINESBYTYPE" and len(a) > 5:
            for o in a[4] or []:
                type_instances[a[5]].append(o)

    assoc_instance = {}
    assoc_type = {}
    for _, (t, a) in ents.items():
        if t != "IFCRELASSOCIATESMATERIAL" or len(a) < 6:
            continue
        for o in a[4] or []:
            if o not in ents:
                continue
            ot = ents[o][0]
            if ot.endswith("TYPE") or ot.endswith("STYLE"):
                assoc_type[o] = a[5]
            else:
                assoc_instance[o] = a[5]

    element_mat = dict(assoc_instance)
    for typ, matsel in assoc_type.items():
        for inst in type_instances.get(typ, []):
            element_mat.setdefault(inst, matsel)  # instance-level association wins

    src_colours = material_source_colours(ents)
    elements = {}
    multi_count = 0
    for eid, matsel in element_mat.items():
        t, a = ents[eid]
        set_name, comps = material_components(ents, matsel)
        comps = [c for c in comps if c]
        if len(set(comps)) > 1:
            multi_count += 1
        if not comps:
            key = set_name or "(no material)"
        elif multi == "set" and len(set(comps)) > 1:
            key = set_name or " + ".join(dict.fromkeys(comps))
        else:
            key = comps[0]
        elements[eid] = {
            "guid": a[0] if a and isinstance(a[0], str) else None,
            "type": t,
            "name": a[2] if len(a) > 2 and isinstance(a[2], str) else None,
            "material": key,
            "components": list(dict.fromkeys(comps)),
        }

    unassigned = []
    for eid, (t, a) in sorted(ents.items()):
        if t in BUILDING_ELEMENTS and eid not in elements and t != "IFCSITE":
            unassigned.append({"id": eid, "type": t, "name": a[2] if len(a) > 2 and isinstance(a[2], str) else None})

    counts = Counter(e["material"] for e in elements.values())
    materials = {}
    for i, name in enumerate(sorted(counts)):
        src = src_colours.get(name)
        colour = src if (colors == "source" and src) else distinct_colour(i)
        materials[name] = {"color": colour, "source_color": src, "elements": counts[name]}

    if colors == "source":
        dup = [c for c, k in Counter(m["color"] for m in materials.values()).items() if k > 1]
        if dup:
            warnings.append("several materials share the same source colour %s - the colour map can't tell them apart; use --colors distinct" % ", ".join(dup))
        missing = [n for n, m in materials.items() if not m["source_color"]]
        if missing:
            warnings.append("%d material(s) had no colour in the IFC and got a generated one" % len(missing))
    if multi == "first" and multi_count:
        warnings.append("%d element(s) have several materials (layered walls, windows); coloured by their FIRST material - use --multi set to colour by the whole set" % multi_count)
    if unassigned:
        warnings.append("%d building element(s) have no material in the IFC (check Revit material assignment / IFC export options)" % len(unassigned))
    return materials, elements, unassigned, warnings


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("ifc", help="input .ifc (STEP text)")
    p.add_argument("-o", "--out", help="write JSON here (default: print to stdout)")
    p.add_argument("--multi", choices=["first", "set"], default="first",
                   help="elements with several materials: colour by first material (default) or by the whole set")
    p.add_argument("--colors", choices=["distinct", "source"], default="distinct",
                   help="distinct generated colours (default) or the colours stored in the IFC")
    p.add_argument("--summary", action="store_true", help="print a material table to stderr")
    args = p.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # Windows consoles default to a legacy code page
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    try:
        schema, ents, bad = load_ifc(args.ifc)
    except (OSError, ValueError) as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 2
    materials, elements, unassigned, warnings = build_colormap(ents, args.multi, args.colors)
    if bad:
        warnings.append("%d statement(s) could not be parsed and were skipped" % bad)
    result = {
        "source": args.ifc,
        "schema": schema,
        "mode": {"multi": args.multi, "colors": args.colors},
        "materials": materials,
        "elements": {str(k): v for k, v in sorted(elements.items())},
        "unassigned": unassigned,
        "warnings": warnings,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    if args.summary or args.out:
        print("schema %s - %d entities, %d elements with material, %d materials, %d without material"
              % (schema, len(ents), len(elements), len(materials), len(unassigned)), file=sys.stderr)
        if args.summary:
            for name, m in sorted(materials.items(), key=lambda kv: -kv[1]["elements"]):
                print("  %s  %4d  %s%s" % (m["color"], m["elements"], name,
                                         ("  (IFC colour %s)" % m["source_color"]) if m["source_color"] else ""), file=sys.stderr)
        for w in warnings:
            print("WARN: " + w, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
