"""Tests for check_mlo_resource.py (standard library only).

    python -I .claude/skills/fivem-mlo-housing/scripts/test_check_mlo_resource.py
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_mlo_resource as chk  # noqa: E402

OUT_CORNERS = [(4, 1, 0), (4, 2, 0), (4, 2, 2), (4, 1, 2)]   # normal +X: room -> outside (correct)
IN_CORNERS = [(4, 1, 0), (4, 1, 2), (4, 2, 2), (4, 2, 0)]    # normal -X: points back into the room


def ytyp_xml(name, corners, door_in_room=False):
    c = ''.join(f'<Item>{x},{y},{z}</Item>' for x, y, z in corners)   # Sollumz/CodeWalker corner format
    room_objs = '0 1' if door_in_room else '0'
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CMapTypes><archetypes>
 <Item type="CMloArchetypeDef"><name>{name}</name>
  <entities><Item type="CEntityDef"><archetypeName>shell</archetypeName></Item>
            <Item type="CEntityDef"><archetypeName>door</archetypeName></Item></entities>
  <rooms>
   <Item><name>limbo</name><bbMin x="0" y="0" z="0" /><bbMax x="0" y="0" z="0" /><portalCount value="1" /><attachedObjects /></Item>
   <Item><name>room1</name><bbMin x="0" y="0" z="0" /><bbMax x="4" y="4" z="3" /><portalCount value="1" /><attachedObjects>{room_objs}</attachedObjects></Item>
  </rooms>
  <portals><Item><roomFrom value="1" /><roomTo value="0" /><flags value="0" /><corners>{c}</corners><attachedObjects>1</attachedObjects></Item></portals>
 </Item>
</archetypes></CMapTypes>"""


def ymap_xml(instances, plain=0):
    ents = ''.join(f'<Item type="CMloInstanceDef"><archetypeName>{a}</archetypeName></Item>' for a in instances)
    ents += '<Item type="CEntityDef"><archetypeName>prop_bin_01a</archetypeName></Item>' * plain
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CMapData><streamingExtentsMin x="-10" y="-10" z="-10" /><streamingExtentsMax x="10" y="10" z="10" />
<entities>{ents}</entities></CMapData>"""


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(text)


def codes(findings):
    return {f['code'] for f in findings}


class CheckMlo(unittest.TestCase):
    def test_bad_resource(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'res/fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\nthis_is_a_map 'yes'\n"
                                           "data_file 'DLC_ITYP_REQUEST' 'stream/test_mlo.ytyp'\n")
            write(d, 'res/stream/test_mlo.ytyp', 'x')
            write(d, 'res/stream/test_manifest.ymf', 'x')
            write(d, 'export/test_mlo.ytyp.xml', ytyp_xml('test_mlo_col', IN_CORNERS, door_in_room=True))
            write(d, 'export/testmlo.ymap.xml', ymap_xml(['test_mlo_col', 'test_mlo_col']))
            write(d, 'export/shop.ymap.xml', ymap_xml(['test_mlo_col'], plain=1))
            found = codes(chk.check([d]))
        for c in ('ITYP_REQUEST_MLO', 'PORTAL_FACING', 'PORTAL_AND_ROOM', 'YMAP_MULTI_MLO',
                  'YMAP_MLO_MIXED', 'YMAP_MLO_NAME'):
            self.assertIn(c, found)
        self.assertNotIn('ITYP_REQUEST_CHECK', found)   # already reported as an error

    def test_good_resource(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'res/fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\nthis_is_a_map 'yes'\n")
            write(d, 'res/stream/test_mlo.ytyp', 'x')
            write(d, 'res/stream/test_manifest.ymf', 'x')
            write(d, 'export/test_mlo.ytyp.xml', ytyp_xml('test_mlo_col', OUT_CORNERS))
            write(d, 'export/test_milo_.ymap.xml', ymap_xml(['test_mlo_col']))
            found = codes(chk.check([d]))
        for c in ('ITYP_REQUEST_MLO', 'ITYP_REQUEST_CHECK', 'PORTAL_FACING', 'PORTAL_AND_ROOM',
                  'YMAP_MULTI_MLO', 'YMAP_MLO_MIXED', 'YMAP_MLO_NAME', 'NO_YTYP_MANIFEST'):
            self.assertNotIn(c, found)

    def test_prop_ytyp_request_is_only_a_note(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'res/fxmanifest.lua', "this_is_a_map 'yes'\ndata_file 'DLC_ITYP_REQUEST' 'stream/props.ytyp'\n")
            write(d, 'res/stream/props.ytyp', 'x')
            write(d, 'res/stream/test_manifest.ymf', 'x')
            found = codes(chk.check([d]))
        self.assertIn('ITYP_REQUEST_CHECK', found)
        self.assertNotIn('ITYP_REQUEST_MLO', found)

    def test_facing_undecidable_when_box_spans_both_sides(self):
        box = ((0, 0, 0), (8, 4, 3))   # room box reaches past the portal plane
        self.assertIsNone(chk.portal_facing(OUT_CORNERS, box, None))
        self.assertEqual(chk.portal_facing(OUT_CORNERS, ((0, 0, 0), (4, 4, 3)), None), 'ok')
        self.assertEqual(chk.portal_facing(IN_CORNERS, ((0, 0, 0), (4, 4, 3)), None), 'flipped')


if __name__ == '__main__':
    unittest.main()
