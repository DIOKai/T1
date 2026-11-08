"""Tests for check_map_resource.py (standard library only, temp fixtures).

    py -3 -I .claude/skills/fivem-map-world-editor/scripts/test_check_map_resource.py
"""
import os
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_map_resource as chk  # noqa: E402

MANIFEST = "fx_version 'cerulean'\ngame 'gta5'\nthis_is_a_map 'yes'\n"
RSC = b'RSC7' + struct.pack('<III', 2, 0x10, 0x10) + b'\0' * 32     # tiny, valid header


def ent(arch, x, y, z, level='HD', pidx=-1, flags=1572864, guid=0, nch=0, lod=100, child=0, kind='CEntityDef'):
    return f"""<Item type="{kind}"><archetypeName>{arch}</archetypeName><flags value="{flags}" /><guid value="{guid}" />
 <position x="{x}" y="{y}" z="{z}" /><rotation x="0" y="0" z="0" w="1" /><scaleXY value="1" /><scaleZ value="1" />
 <parentIndex value="{pidx}" /><lodDist value="{lod}" /><childLodDist value="{child}" /><lodLevel>LODTYPES_DEPTH_{level}</lodLevel>
 <numChildren value="{nch}" /><priorityLevel>PRI_REQUIRED</priorityLevel></Item>"""


def ymap(name, ents, parent='', flags=None, cflags=None, ext=((-1000, -1000, -100), (1000, 1000, 400)),
         eext=None, cargens=(), boxes=0):
    levels = [e.split('LODTYPES_DEPTH_')[1].split('<')[0] for e in ents]
    if flags is None or cflags is None:
        y = chk.Ymap('x', 'x', 'r', 'xml')
        y.ents = [chk.Ent(level=lv, mlo='CMloInstanceDef' in e) for lv, e in zip(levels, ents)]
        y.n['box'] = boxes
        f, c = chk.calc_flags(y)
        flags = f if flags is None else flags
        cflags = c if cflags is None else cflags
    eext = eext or ext
    cg = ''.join(f'<Item><position x="{x}" y="{y}" z="{z}" /></Item>' for x, y, z in cargens)
    bx = '<Item />' * boxes
    v = lambda t, p: f'<{t} x="{p[0]}" y="{p[1]}" z="{p[2]}" />'   # noqa: E731
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CMapData><name>{name}</name><parent>{parent}</parent><flags value="{flags}" /><contentFlags value="{cflags}" />
{v('streamingExtentsMin', ext[0])}{v('streamingExtentsMax', ext[1])}{v('entitiesExtentsMin', eext[0])}{v('entitiesExtentsMax', eext[1])}
<entities>{''.join(ents)}</entities><boxOccluders>{bx}</boxOccluders><carGenerators>{cg}</carGenerators></CMapData>"""


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb' if isinstance(data, bytes) else 'w', **({} if isinstance(data, bytes) else {'encoding': 'utf-8'})) as fh:
        fh.write(data)
    return p


def build_bin_ymap(name, parent, ents, smin=(-10, -10, -10), smax=(10, 10, 10)):
    """Minimal compiled ymap (RSC7 meta) with the layout check_map_resource.read_ymap_bin expects."""
    blocks_off, map_off, ent_off = 0x100, 0x200, 0x400
    arr_off = ent_off + 128 * len(ents)
    d = bytearray(arr_off + 8 * max(len(ents), 1) + 64)
    struct.pack_into('<I', d, 0x10, 0x50524430)
    struct.pack_into('<I', d, 0x1C, 1)
    struct.pack_into('<Q', d, 0x30, 0x50000000 | blocks_off)
    struct.pack_into('<h', d, 0x4C, 3)
    for i, (h, ln, off) in enumerate(((chk.META_CMAPDATA, 512, map_off), (chk.META_CENTITYDEF, 128 * len(ents), ent_off),
                                      (7, 8 * len(ents), arr_off))):
        struct.pack_into('<IiQ', d, blocks_off + 16 * i, h, ln, 0x50000000 | off)
    struct.pack_into('<IIII', d, map_off + 8, chk.joaat(name), chk.joaat(parent) if parent else 0, 0, 1)
    struct.pack_into('<3f', d, map_off + 32, *smin)
    struct.pack_into('<3f', d, map_off + 48, *smax)
    struct.pack_into('<3f', d, map_off + 64, *smin)
    struct.pack_into('<3f', d, map_off + 80, *smax)
    if ents:
        struct.pack_into('<IIHH', d, map_off + 96, 3, 0, len(ents), len(ents))
    levels = {v: k for k, v in chk.LEVELS.items()}
    for i, (arch, pos, level, pidx, flags) in enumerate(ents):
        o = ent_off + 128 * i
        struct.pack_into('<III', d, o + 8, chk.joaat(arch), flags, 100 + i)
        struct.pack_into('<3f', d, o + 32, *pos)
        struct.pack_into('<ffi', d, o + 64, 1.0, 1.0, pidx)
        struct.pack_into('<ffII', d, o + 76, 100.0, 0.0, levels[level], 0)
        struct.pack_into('<II', d, arr_off + 8 * i, 2 | ((128 * i) << 12), 0)
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    body = comp.compress(bytes(d)) + comp.flush()
    return b'RSC7' + struct.pack('<III', 2, 0x10, 0x10) + body   # virtual flags 0x10 -> 128 KiB pages


def codes(findings, level=None):
    return {f['code'] for f in findings if level is None or f['level'] == level}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def run_chk(self, *paths, **kw):
        return chk.check([os.path.join(self.d, p) for p in paths], **kw)


class Helpers(unittest.TestCase):
    def test_joaat_and_hash_names(self):
        self.assertEqual(chk.joaat('kt1_lod'), 0x6E7D72BB)         # CodeWalker XML: <parent>hash_6E7D72BB</parent>
        self.assertEqual(chk.name_key('hash_6E7D72BB'), chk.joaat('KT1_LOD'))

    def test_vanilla_heuristic(self):
        for s in ('kt1_13_strm_0', 'hei_kt1_lod', 'hi@kt1_13_0', 'vb_43', 'nodes650', 'navmesh[100][50]', 'v_int_24'):
            self.assertTrue(chk.looks_vanilla(s), s)
        for s in ('lpt_t3', 'sa_euro_legion', 'borderv2', 'pio_chtp'):
            self.assertFalse(chk.looks_vanilla(s), s)
        self.assertTrue(chk.looks_vanilla('lpt_t3', {'lpt_t3'}))

    def test_calc_flags_like_codewalker(self):
        y = chk.Ymap('x', 'x', 'r', 'xml')
        y.ents = [chk.Ent(level='LOD', mlo=False), chk.Ent(level='SLOD1', mlo=False)]
        self.assertEqual(chk.calc_flags(y), (2, 18))                 # vanilla kt1_13: flags 2, contentFlags 18
        y.ents = [chk.Ent(level='SLOD2', mlo=False), chk.Ent(level='SLOD3', mlo=False)]
        self.assertEqual(chk.calc_flags(y), (2, 20))                 # vanilla kt1_lod: contentFlags 20
        y.ents, y.n['box'] = [], 3
        self.assertEqual(chk.calc_flags(y), (0, 32))                 # occluder ymaps: 32


class Manifest(Base):
    def test_resource_level_checks(self):
        write(self.d, 'res/fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\n")
        write(self.d, 'res/stream/my_props.ytyp', RSC)
        write(self.d, 'res/stream/my_map.ymap.xml', '<CMapData/>')
        write(self.d, 'res/stream/fake.ybn', b'<xml/>' + b'\0' * 20)
        write(self.d, 'res/water_custom.xml', '<WaterData/>')
        write(self.d, 'res/stream/mytex+hi.ytd', RSC)
        f = self.run_chk('res')
        c = codes(f)
        for code in ('NO_THIS_IS_A_MAP', 'XML_IN_STREAM', 'NOT_RSC7', 'YTYP_NOT_LOADED', 'WATER_XML_NOT_LOADED', 'HD_TXD_PRESENT'):
            self.assertIn(code, c, code)

    def test_water_loaded_and_ymf_ok(self):
        write(self.d, 'res/fxmanifest.lua', MANIFEST + "files { 'water_custom.xml' }\nclient_script 'c.lua'\n")
        write(self.d, 'res/c.lua', "LoadWaterFromPath(GetCurrentResourceName(), 'water_custom.xml')\n")
        write(self.d, 'res/water_custom.xml', '<WaterData/>')
        write(self.d, 'res/stream/my_props.ytyp', RSC)
        write(self.d, 'res/stream/_manifest.ymf', b'PSIN' + b'\0' * 12)
        c = codes(self.run_chk('res'))
        self.assertNotIn('WATER_XML_NOT_LOADED', c)
        self.assertNotIn('YTYP_NOT_LOADED', c)

    def test_vehicle_resource_is_ignored(self):
        big = b'RSC7' + struct.pack('<III', 2, 0, 0x7F << 17) + b'\0' * 8       # huge physical size
        write(self.d, 'car/fxmanifest.lua', "fx_version 'cerulean'\n")
        write(self.d, 'car/stream/car.ytd', big)
        self.assertEqual(self.run_chk('car'), [])

    def test_ynd_name(self):
        write(self.d, 'res/fxmanifest.lua', MANIFEST)
        write(self.d, 'res/stream/nodes2000.ynd', RSC)
        write(self.d, 'res/stream/nodes650.ynd', RSC)
        f = [x for x in self.run_chk('res') if x['code'] == 'YND_NAME']
        self.assertEqual(len(f), 1)
        self.assertIn('nodes2000', f[0]['file'])


class Cross(Base):
    def test_duplicate_owner_and_ymf(self):
        for r in ('a', 'b'):
            write(self.d, f'[maps]/{r}/fxmanifest.lua', MANIFEST)
            write(self.d, f'[maps]/{r}/stream/kt1_13.ymap', RSC)
            write(self.d, f'[maps]/{r}/stream/_manifest.ymf', b'PSIN')
        f = self.run_chk('[maps]')
        dup = {x['message'].split("'")[1]: x['level'] for x in f if x['code'] == 'DUPLICATE_STREAM_FILE'}
        self.assertEqual(dup.get('kt1_13.ymap'), 'error')
        self.assertEqual(dup.get('_manifest.ymf'), 'warn')

    def test_category_clash_and_hei_pairs(self):
        write(self.d, 'resources/[maps]/x/fxmanifest.lua', MANIFEST)
        write(self.d, 'resources/[maps]/x/stream/kt1_13_strm_0.ymap', RSC)
        write(self.d, 'resources/[cfx-default]/[maps]/y/fxmanifest.lua', MANIFEST)
        write(self.d, 'resources/[cfx-default]/[maps]/y/stream/hei_dt1_05.ymap', RSC)
        f = self.run_chk('resources')
        c = codes(f)
        self.assertIn('CATEGORY_NAME_CLASH', c)
        hei = [x for x in f if x['code'] == 'HEI_PAIR_MISSING']
        self.assertEqual({x['level'] for x in hei}, {'info'})
        self.assertIn('OCCLUDER_CHECK', c)
        lst = write(self.d, 'vanilla.txt', 'kt1_13_strm_0.ymap\nhei_kt1_13_strm_0.ymap\n')
        f = chk.check([os.path.join(self.d, 'resources')], vanilla_list=lst)
        self.assertIn('warn', {x['level'] for x in f if x['code'] == 'HEI_PAIR_MISSING'})


class YmapChecks(Base):
    def test_good_custom_map_has_no_errors(self):
        write(self.d, 'res/fxmanifest.lua', MANIFEST)
        write(self.d, 'res/stream/_manifest.ymf', b'PSIN')
        write(self.d, 'xml/lore_plaza.ymap.xml', ymap('lore_plaza', [ent('prop_bench_01a', 10, 10, 30, 'ORPHANHD')],
                                                       ext=((-90, -90, -70), (110, 110, 130)), eext=((9, 9, 29), (11, 11, 31))))
        f = self.run_chk('res', 'xml')
        self.assertEqual(codes(f, 'error') | codes(f, 'warn'), set(), f)

    def test_zero_extents_flags_and_lod_distance(self):
        write(self.d, 'xml/lore_a.ymap.xml', ymap('lore_a', [ent('prop_a', 1, 1, 1, 'ORPHANHD', lod=3000)], ext=((0, 0, 0), (0, 0, 0)),
                                                  cflags=0))
        f = self.run_chk('xml')
        c = codes(f)
        self.assertIn('ZERO_EXTENTS', codes(f, 'error'))
        self.assertIn('FLAGS_MISMATCH', codes(f, 'warn'))
        self.assertIn('LOD_DIST_SUSPICIOUS', c)

    def test_lod_resolution_rule(self):
        # parent ymap with 2 LODs; child uses flag 8 -> index into parent ymap
        lod = ymap('lore_lod', [ent('lore_a_lod', 0, 0, 0, 'LOD', nch=1, lod=300, child=100),
                                ent('lore_b_lod', 50, 0, 0, 'LOD', nch=1, lod=300, child=100)])
        hd = ymap('lore_hd', [ent('lore_a', 0, 0, 0, 'HD', pidx=0, flags=1572872),
                              ent('lore_b', 50, 0, 0, 'HD', pidx=1, flags=1572864),     # no flag 8, index 1 is HD -> parent ymap
                              ent('lore_c', 9, 0, 0, 'HD', pidx=5, flags=1572872)], parent='lore_lod')
        write(self.d, 'xml/lore_lod.ymap.xml', lod)
        write(self.d, 'xml/lore_hd.ymap.xml', hd)
        f = self.run_chk('xml')
        oor = [x for x in f if x['code'] == 'LOD_INDEX_OUT_OF_RANGE']
        self.assertEqual(len(oor), 1)
        self.assertIn('#2', oor[0]['message'])
        self.assertNotIn('LOD_RANK', codes(f))

    def test_rank_and_missing_parent(self):
        write(self.d, 'xml/lore_x.ymap.xml', ymap('lore_x', [ent('a', 0, 0, 0, 'LOD', pidx=1, flags=1572864),
                                                             ent('b', 0, 0, 0, 'HD')]))
        write(self.d, 'xml/lore_y.ymap.xml', ymap('lore_y', [ent('c', 0, 0, 0, 'HD', pidx=3, flags=1572872)], parent='kt1_lod'))
        f = self.run_chk('xml')
        self.assertIn('LOD_NO_PARENT_MAP', codes(f))
        self.assertIn('LOD_PARENT_MISSING', codes(f, 'info'))

    def test_index_shifted_by_one(self):
        lods = [ent(f'lod{i}', 100 * i, 0, 0, 'LOD', nch=1, lod=300, child=100) for i in range(6)]
        hds = [ent(f'hd{i}', 100 * i + 1, 0, 0, 'HD', pidx=i + 1, flags=1572872) for i in range(5)]
        write(self.d, 'xml/veg_lod.ymap.xml', ymap('veg_lod', lods))
        write(self.d, 'xml/veg.ymap.xml', ymap('veg', hds, parent='veg_lod'))
        f = [x for x in self.run_chk('xml') if x['code'] == 'LOD_INDEX_SHIFTED']
        self.assertEqual(len(f), 1)
        self.assertIn('+1', f[0]['message'])

    def test_duplicate_entities_but_not_hei_copies(self):
        same = [ent('prop_x', 5, 5, 5, 'HD')]
        write(self.d, 'xml/kt1_13_strm_0.ymap.xml', ymap('kt1_13_strm_0', same))
        write(self.d, 'xml/hei_kt1_13_strm_0.ymap.xml', ymap('hei_kt1_13_strm_0', same))
        self.assertNotIn('DUPLICATE_ENTITY', codes(self.run_chk('xml')))
        write(self.d, 'xml/lore_dup.ymap.xml', ymap('lore_dup', same * 2))
        self.assertIn('DUPLICATE_ENTITY', codes(self.run_chk('xml')))

    def test_custom_lod_pair_needs_manifest_and_custom_model_archetype(self):
        write(self.d, 'res/fxmanifest.lua', MANIFEST)
        write(self.d, 'res/stream/lore_tower.ydr', RSC)
        write(self.d, 'res/stream/lore_tower_lod.ydr', RSC)
        write(self.d, 'res/lore_tower_hd.ymap.xml', ymap('lore_tower_hd', [ent('lore_tower', 0, 0, 0, 'HD', pidx=0, flags=1572872)], parent='lore_tower_lodmap'))
        write(self.d, 'res/lore_tower_lodmap.ymap.xml', ymap('lore_tower_lodmap', [ent('lore_tower_lod', 0, 0, 0, 'LOD', nch=1, lod=500, child=100)]))
        write(self.d, 'res/lore.ytyp.xml', '<CMapTypes><archetypes><Item><name>lore_tower_lod</name></Item></archetypes></CMapTypes>')
        c = codes(self.run_chk('res'))
        self.assertIn('CUSTOM_LOD_NO_MANIFEST', c)
        self.assertIn('CUSTOM_MODEL_NO_ARCHETYPE', c)


class Binary(Base):
    def test_binary_ymap_roundtrip_and_checks(self):
        data = build_bin_ymap('lore_bin', 'lore_bin_lod', [('lore_a', (1, 2, 3), 'HD', 4, 1572872), ('prop_b', (5, 5, 5), 'ORPHANHD', -1, 0)],
                              smin=(0, 0, 0), smax=(0, 0, 0))
        p = write(self.d, 'res/stream/lore_bin.ymap', data)
        write(self.d, 'res/fxmanifest.lua', MANIFEST)
        info = chk.read_ymap_bin(p)
        self.assertEqual(info['name'], chk.joaat('lore_bin'))
        self.assertEqual(info['parent'], chk.joaat('lore_bin_lod'))
        self.assertEqual([e.level for e in info['ents']], ['HD', 'ORPHANHD'])
        self.assertEqual(info['ents'][0].pidx, 4)
        self.assertAlmostEqual(info['ents'][0].pos[1], 2.0)
        lod = build_bin_ymap('lore_bin_lod', '', [('lore_a_lod', (1, 2, 3), 'LOD', -1, 0)])
        write(self.d, 'res/stream/lore_bin_lod.ymap', lod)
        c = codes(self.run_chk('res'))
        self.assertIn('ZERO_EXTENTS', c)
        self.assertIn('LOD_INDEX_OUT_OF_RANGE', c)


class Diff(Base):
    def setUp(self):
        super().setUp()
        lod = [ent('kt1_13_lod', 0, 0, 20, 'LOD', nch=2, lod=500, child=150, guid=1),
               ent('kt1_14_lod', 300, 0, 20, 'LOD', nch=1, lod=500, child=150, guid=2)]
        hd = [ent('kt1_13_bld', 0, 0, 20, 'HD', pidx=0, flags=1572872, guid=10),
              ent('kt1_13_crane', 5, 5, 20, 'HD', pidx=0, flags=1572872, guid=11),
              ent('kt1_14_bld', 300, 0, 20, 'HD', pidx=1, flags=1572872, guid=12)]
        for pre in ('', 'hei_'):
            write(self.d, f'orig/{pre}kt1_13.ymap.xml', ymap(f'{pre}kt1_13', lod))
            write(self.d, f'orig/{pre}kt1_13_strm_0.ymap.xml', ymap(f'{pre}kt1_13_strm_0', hd, parent=f'{pre}kt1_13',
                                                                     cargens=[(2, 2, 20)]))
        self.lod, self.hd = lod, hd

    def test_bad_delete(self):
        # deleted the first LOD from the LOD ymap (index shift) and only one HD; numChildren untouched; no occluders
        write(self.d, 'edit/kt1_13.ymap.xml', ymap('kt1_13', [self.lod[1]]))
        write(self.d, 'edit/kt1_13_strm_0.ymap.xml', ymap('kt1_13_strm_0', [self.hd[1], self.hd[2]], parent='kt1_13', cargens=[(2, 2, 20)]))
        write(self.d, 'edit/hei_kt1_13_strm_0.ymap.xml', ymap('hei_kt1_13_strm_0', self.hd, parent='hei_kt1_13', cargens=[(2, 2, 20)]))
        f = self.run_chk('edit', orig=os.path.join(self.d, 'orig'))
        c = codes(f)
        for code in ('REMOVED_HAS_LOD_CHILDREN', 'INDEX_SHIFT', 'OCCLUDER_NOT_EDITED', 'COLLISION_NOT_EDITED',
                     'CARGEN_IN_REMOVED_AREA', 'HEI_EDIT_DIFFERS', 'SLOD_REMINDER', 'DIFF_SUMMARY'):
            self.assertIn(code, c, code)

    def test_good_bury(self):
        # the user's way: HDs deleted, LOD parent kept in the list but buried, numChildren lowered, occluder cut
        buried = ent('kt1_13_lod', 0, 0, -500, 'LOD', nch=0, lod=500, child=150, guid=1)
        for pre in ('', 'hei_'):
            write(self.d, f'edit/{pre}kt1_13.ymap.xml', ymap(f'{pre}kt1_13', [buried, self.lod[1]]))
            write(self.d, f'edit/{pre}kt1_13_strm_0.ymap.xml', ymap(f'{pre}kt1_13_strm_0', [self.hd[2]], parent=f'{pre}kt1_13'))
            write(self.d, f'edit/{pre}kt1_occl_00.ymap.xml', ymap(f'{pre}kt1_occl_00', [], boxes=1, eext=((-50, -50, 0), (50, 50, 60))))
            write(self.d, f'edit/{pre}kt1_13_0.ybn.xml', '<BoundsFile><Bounds type="Composite"><Children /></Bounds></BoundsFile>')
        f = self.run_chk('edit', orig=os.path.join(self.d, 'orig'))
        bad = codes(f, 'error') | (codes(f, 'warn') - {'YBN_EMPTY'})
        self.assertEqual(bad, set(), [x for x in f if x['level'] != 'info'])

    def test_numchildren_stale_and_lod_left_behind(self):
        write(self.d, 'edit/kt1_13.ymap.xml', ymap('kt1_13', self.lod))
        write(self.d, 'edit/kt1_13_strm_0.ymap.xml', ymap('kt1_13_strm_0', [self.hd[2]], parent='kt1_13'))
        c = codes(self.run_chk('edit', orig=os.path.join(self.d, 'orig')))
        self.assertIn('NUMCHILDREN_STALE', c)
        self.assertIn('LOD_LEFT_BEHIND', c)


class OtherXml(Base):
    def test_ybn_and_ydr(self):
        polys = '<Triangle m="0" v1="0" v2="1" v3="2" />' * 32768
        write(self.d, 'x/big.ybn.xml', f"""<BoundsFile><Bounds type="Composite"><Children>
<Item type="GeometryBVH"><CompositeFlags1>MAP_WEAPON</CompositeFlags1><CompositeFlags2>PED</CompositeFlags2><Polygons>{polys}</Polygons></Item>
<Item type="GeometryBVH"><CompositeFlags1>NONE</CompositeFlags1><CompositeFlags2 /><Polygons /></Item></Children></Bounds></BoundsFile>""")
        write(self.d, 'x/road.ydr.xml', """<Drawable><VertexBuffer><Layout type="GTAV1"><Position /><Normal /><TexCoord0 /></Layout>
<Data>0 0 0   0 0 1   120.5 -3.0
1 0 0   0 0 1   1.0 0.5</Data></VertexBuffer>
<TextureDictionary><Item><Name>road_d</Name><Width value="3000" /><Height value="1024" /></Item></TextureDictionary></Drawable>""")
        c = codes(self.run_chk('x'))
        for code in ('BVH_TOO_MANY_POLYS', 'BVH_NO_FLAGS', 'UV_TOO_LARGE', 'NO_VERTEX_COLOUR', 'TEXTURE_SIZE'):
            self.assertIn(code, c, code)

    def test_ynd_xml_area(self):
        write(self.d, 'x/nodes650.ynd.xml', """<NodeDictionary><Nodes>
<Item><AreaID value="650" /><Position x="-8192" y="-8192" z="0" /></Item></Nodes></NodeDictionary>""")
        self.assertIn('YND_AREA_MISMATCH', codes(self.run_chk('x')))


class Cli(Base):
    def test_exit_code_and_json(self):
        import subprocess
        write(self.d, 'xml/lore_a.ymap.xml', ymap('lore_a', [ent('a', 1, 1, 1, 'ORPHANHD')], ext=((0, 0, 0), (0, 0, 0))))
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'check_map_resource.py')
        p = subprocess.run([sys.executable, '-I', script, os.path.join(self.d, 'xml'), '--json'], capture_output=True,
                           encoding='utf-8')
        self.assertEqual(p.returncode, 1)
        import json
        self.assertIn('ZERO_EXTENTS', {x['code'] for x in json.loads(p.stdout)})


if __name__ == '__main__':
    unittest.main()
