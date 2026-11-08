"""Tests for check_prop_resource.py and rsc_probe.py (standard library only).

    py -3 -I .claude/skills/fivem-prop-creator/scripts/test_check_prop_resource.py

Binary fixtures are synthetic: tiny RSC7 files built here with the same layout rsc_probe reads
(CodeWalker Texture.cs / Drawable.cs / Meta.cs offsets), not copies of game files.
"""
import os
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_prop_resource as chk  # noqa: E402
import rsc_probe as rp  # noqa: E402

VIRT_FLAGS = 1 << 4          # 128 KiB virtual block - plenty for the fixtures
DXT1, A8R8G8B8 = 0x31545844, 21
F_DYNAMIC, F_DOOR = 1 << 17, 1 << 26


def rsc(block, version=165, virt_flags=VIRT_FLAGS, phys_flags=0):
    comp = zlib.compressobj(9, zlib.DEFLATED, -15)
    return b'RSC7' + struct.pack('<III', version, virt_flags, phys_flags) + comp.compress(bytes(block)) + comp.flush()


def vptr(off):
    return 0x50000000 | off


class Block:
    def __init__(self, size=0x4000):
        self.b = bytearray(size)

    def put(self, off, fmt, *vals):
        struct.pack_into(fmt, self.b, off, *vals)

    def ptr_list(self, off, array_off, ptrs):
        self.put(off, '<QH', vptr(array_off), len(ptrs))
        for i, p in enumerate(ptrs):
            self.put(array_off + 8 * i, '<Q', vptr(p))

    def string(self, off, text):
        self.b[off:off + len(text) + 1] = text.encode() + b'\0'


def texture_dict(blk, base, textures):
    """TextureDictionary at base; textures = [(name, w, h, fmt, mips)]."""
    tex_offs = [base + 0x100 + i * 0x90 for i in range(len(textures))]
    blk.ptr_list(base + 0x30, base + 0x40, tex_offs)
    for i, (name, w, h, fmt, mips) in enumerate(textures):
        t = tex_offs[i]
        s = base + 0x800 + i * 0x40
        blk.string(s, name)
        blk.put(t + 0x28, '<Q', vptr(s))
        blk.put(t + 0x50, '<HHHHI', w, h, 1, w, fmt)
        blk.b[t + 0x5D] = mips


def ytd_bytes(textures):
    blk = Block()
    texture_dict(blk, 0, textures)
    return rsc(blk.b, version=13)


def ydr_bytes(high=300, med=0, radius=0.8, bound_type=3, embedded=None, lod_high=9998.0):
    blk = Block(0x8000)
    blk.put(0x2C, '<f', radius)
    for slot, tris, base in ((0, high, 0x1000), (1, med, 0x1400)):
        if not tris:
            continue
        # model list -> model -> geometry list -> geometry (IndicesCount at +0x58)
        blk.ptr_list(base, base + 0x20, [base + 0x40])
        blk.ptr_list(base + 0x40 + 0x08, base + 0x80, [base + 0xA0])
        blk.put(base + 0xA0 + 0x58, '<II', tris * 3, tris)
        blk.put(0x50 + 8 * slot, '<Q', vptr(base))
    blk.put(0x70, '<4f', lod_high, 9998.0, 9998.0, 9998.0)
    if bound_type is not None:
        blk.b[0x1800 + 0x10] = bound_type
        blk.put(0xC8, '<Q', vptr(0x1800))
    if embedded:
        blk.put(0x10, '<Q', vptr(0x1900))           # shader group
        blk.put(0x1900 + 0x08, '<Q', vptr(0x2000))  # its texture dictionary
        texture_dict(blk, 0x2000, embedded)
    return rsc(blk.b)


def ytyp_bytes(archetypes, mlo=False):
    """archetypes = [dict(name, lod=60.0, flags=F_DYNAMIC, attr=0, radius=0.8, hd=15.0, txd='', clip='', phys='', atype=2)]."""
    blk = Block()
    blk.put(0x10, '<I', 0x50524430)
    blocks = [(rp.META_CBASEARCHETYPEDEF, 0x90 * len(archetypes), 0x400)]
    if mlo:
        blocks.append((rp.META_CMLOARCHETYPEDEF, 0xF0, 0x400 + 0x90 * len(archetypes)))
    blk.put(0x30, '<Q', vptr(0x100))
    blk.put(0x4C, '<h', len(blocks))
    for i, (h, ln, off) in enumerate(blocks):
        blk.put(0x100 + 0x10 * i, '<IiQ', h, ln, vptr(off))
    for i, a in enumerate(archetypes):
        o = 0x400 + 0x90 * i
        j = lambda s: rp.joaat(s) if s else 0  # noqa: E731
        blk.put(o + 0x08, '<fII', a.get('lod', 60.0), a.get('flags', F_DYNAMIC), a.get('attr', 0))
        blk.put(o + 0x50, '<ff', a.get('radius', 0.8), a.get('hd', 15.0))
        blk.put(o + 0x58, '<7I', j(a['name']), j(a.get('txd', '')), j(a.get('clip', '')), 0, j(a.get('phys', '')),
                a.get('atype', 2), j(a.get('asset', a['name'])))
    if mlo:
        o = 0x400 + 0x90 * len(archetypes)
        blk.put(o + 0x58, '<I', rp.joaat('test_mlo'))
        blk.put(o + 0x70, '<I', rp.joaat('test_mlo'))
    return rsc(blk.b, version=2)


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb' if isinstance(data, bytes) else 'w', **({} if isinstance(data, bytes) else {'encoding': 'utf-8'})) as fh:
        fh.write(data)


MANIFEST = "fx_version 'cerulean'\ngame 'gta5'\n"
GOOD_TEX = [('ha_crate_d', 256, 256, DXT1, 9)]


def good_resource(d, name='ha_crate', manifest_extra=None):
    write(d, f'res/fxmanifest.lua', MANIFEST + (manifest_extra if manifest_extra is not None else f"data_file 'DLC_ITYP_REQUEST' 'stream/{name}.ytyp'\n"))
    write(d, f'res/stream/{name}.ydr', ydr_bytes(high=700, med=150, lod_high=20.0))
    write(d, f'res/stream/{name}.ytd', ytd_bytes(GOOD_TEX))
    write(d, f'res/stream/{name}.ytyp', ytyp_bytes([dict(name=name, txd=name, lod=60.0)]))
    write(d, 'res/CREDITS.md', 'made by me')


def run(d):
    return chk.check([d])


def codes(findings, level=None):
    return {f['code'] for f in findings if level is None or f['level'] == level}


class Probe(unittest.TestCase):
    def test_ytd_textures(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'a.ytd', ytd_bytes([('one', 512, 256, DXT1, 8), ('two', 128, 128, A8R8G8B8, 1)]))
            tex = rp.read_ytd(os.path.join(d, 'a.ytd'))
        self.assertEqual([(t['name'], t['width'], t['height'], t['format'], t['mips']) for t in tex],
                         [('one', 512, 256, 'DXT1', 8), ('two', 128, 128, 'A8R8G8B8', 1)])

    def test_ydr_lods_bound_textures(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'a.ydr', ydr_bytes(high=620, med=136, radius=0.9, bound_type=10, embedded=[('e', 256, 256, DXT1, 9)]))
            info = rp.read_ydr(os.path.join(d, 'a.ydr'))
        self.assertEqual((info['lods']['high']['tris'], info['lods']['med']['tris']), (620, 136))
        self.assertEqual(info['bound'], 'Composite')
        self.assertAlmostEqual(info['bs_radius'], 0.9, places=5)
        self.assertEqual(info['textures'][0]['name'], 'e')

    def test_ytyp_records_and_mlo(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'a.ytyp', ytyp_bytes([dict(name='ha_door', attr=10, flags=0)], mlo=True))
            y = rp.read_ytyp(os.path.join(d, 'a.ytyp'))
        self.assertTrue(y['mlo'])
        base = [a for a in y['archetypes'] if not a['mlo']][0]
        self.assertEqual((base['name_hash'], base['special_attribute'], base['asset_type']), (rp.joaat('ha_door'), 10, 'DRAWABLE'))

    def test_page_size_and_joaat(self):
        self.assertEqual(rp.page_size((1 << 26) | 15), 32 * 1024 * 1024)
        self.assertEqual(rp.joaat('wood_table'), 3086238520)   # value read from the user's wood_table.ytyp

    def test_parse_base_name_like_fivem(self):
        self.assertEqual(chk.parse_base_name('stream/[Props]/Brummiee/brummie_props.ytyp'), 'brummie_props')
        self.assertEqual(chk.parse_base_name('stream/prideprops_ytyp'), 'prideprops_ytyp')
        self.assertEqual(chk.parse_base_name('a.b.ytyp'), 'a.b')


class CheckProp(unittest.TestCase):
    def test_good_resource_is_clean(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            found = run(d)
        self.assertEqual(codes(found, 'error') | codes(found, 'warn'), set(), found)

    def test_rpemotes_style_path_is_only_a_note(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            os.makedirs(os.path.join(d, 'res/stream/[Props]/Brummiee'))
            os.replace(os.path.join(d, 'res/stream/ha_crate.ytyp'), os.path.join(d, 'res/stream/[Props]/Brummiee/ha_crate.ytyp'))
            found = run(d)
        self.assertIn('ITYP_REQUEST_PATH', codes(found, 'info'))
        self.assertNotIn('ITYP_REQUEST_MISSING', codes(found))

    def test_missing_and_unrequested_ytyp(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d, manifest_extra="data_file 'DLC_ITYP_REQUEST' 'stream/other_props.ytyp'\n")
            found = run(d)
        self.assertIn('ITYP_REQUEST_MISSING', codes(found, 'error'))
        self.assertIn('ITYP_NOT_REQUESTED', codes(found, 'warn'))

    def test_glob_that_matches_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d, manifest_extra="data_file 'DLC_ITYP_REQUEST' 'stream/[Props]/*ytyp.'\n")
            found = run(d)
        self.assertIn('ITYP_REQUEST_GLOB', codes(found, 'warn'))
        self.assertIn('ITYP_NOT_REQUESTED', codes(found, 'warn'))

    def test_glob_that_matches(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d, manifest_extra="data_file 'DLC_ITYP_REQUEST' 'stream/*.ytyp'\n")
            found = run(d)
        self.assertNotIn('ITYP_REQUEST_GLOB', codes(found))
        self.assertNotIn('ITYP_NOT_REQUESTED', codes(found))

    def test_mlo_ytyp_requested(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'res/fxmanifest.lua', MANIFEST + "this_is_a_map 'yes'\ndata_file 'DLC_ITYP_REQUEST' 'stream/shop.ytyp'\n")
            write(d, 'res/stream/shop.ytyp', ytyp_bytes([dict(name='shop_shell', flags=1 << 5)], mlo=True))
            write(d, 'res/stream/shop_shell.ydr', ydr_bytes())
            found = run(d)
        self.assertIn('ITYP_REQUEST_MLO', codes(found, 'error'))

    def test_xml_source_fxap_and_sizes(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_crate.ydr.xml', '<Drawable />')
            write(d, 'res/stream/ha_crate.blend', b'BLENDER')
            write(d, 'res/stream/locked.ydr', b'FXAP' + b'\0' * 60)
            write(d, 'res/stream/big_a.ybn', b'RSC7' + struct.pack('<III', 43, 0, (1 << 26) | 15) + b'\0' * 16)   # 32 MiB
            write(d, 'res/stream/big_b.ybn', b'RSC7' + struct.pack('<III', 43, 0, (1 << 25) | 15) + b'\0' * 16)   # 64 MiB
            write(d, 'res/stream/Bad Name.ybn', b'RSC7' + struct.pack('<III', 43, 0, 0) + b'\0' * 16)
            found = run(d)
        self.assertIn('XML_IN_STREAM', codes(found, 'error'))
        self.assertIn('SOURCE_IN_STREAM', codes(found, 'warn'))
        self.assertIn('ESCROWED', codes(found, 'info'))
        self.assertNotIn('NOT_RSC7', codes(found))
        self.assertIn('ASSET_OVER_16MIB', codes(found, 'warn'))
        self.assertIn('ASSET_OVER_48MIB', codes(found, 'error'))
        self.assertIn('NAME_CASE', codes(found, 'warn'))

    def test_door_attribute_10_needs_flags(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_crate.ytyp', ytyp_bytes([dict(name='ha_crate', txd='ha_crate', attr=10, flags=F_DYNAMIC)]))
            found = run(d)
        self.assertIn('DOOR_FLAGS', codes(found, 'warn'))
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_crate.ytyp', ytyp_bytes([dict(name='ha_crate', txd='ha_crate', attr=10, flags=F_DYNAMIC | F_DOOR)]))
            found = run(d)
        self.assertNotIn('DOOR_FLAGS', codes(found))

    def test_door_physics_with_attribute_zero_is_a_note(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_crate.ytyp', ytyp_bytes([dict(name='ha_crate', txd='ha_crate', flags=F_DYNAMIC | F_DOOR)]))
            found = run(d)
        self.assertIn('DOOR_ATTR_ZERO', codes(found, 'info'))

    def test_xml_ytyp_fragment_not_dynamic_and_physdict(self):
        xml = """<CMapTypes><archetypes><Item type="CBaseArchetypeDef">
          <lodDist value="100" /><flags value="0" /><specialAttribute value="0" /><bsRadius value="1.0" />
          <hdTextureDist value="15" /><name>ha_bin</name><textureDictionary /><clipDictionary />
          <drawableDictionary /><physicsDictionary>ha_bin</physicsDictionary>
          <assetType>ASSET_TYPE_FRAGMENT</assetType><assetName>ha_bin</assetName></Item></archetypes></CMapTypes>"""
        with tempfile.TemporaryDirectory() as d:
            write(d, 'export/ha_bin.ytyp.xml', xml)
            write(d, 'export/ha_bin.yft.xml', '<Fragment><Drawable><DrawableModelsHigh /></Drawable></Fragment>')
            found = run(d)
        self.assertIn('FRAGMENT_NOT_DYNAMIC', codes(found, 'warn'))
        self.assertFalse([f for f in found if 'physics' in f['message'].lower() and f['level'] != 'info'])

    def test_bvh_without_flags_and_heavy_poly(self):
        polys = ''.join('<Triangle m="0" v1="0" v2="1" v3="2" />' for _ in range(301))
        xml = f"""<Drawable><BoundingSphereRadius value="0.8" />
          <DrawableModelsHigh><Item><Geometries><Item><IndexBuffer><Data>0 1 2 0 2 3</Data></IndexBuffer></Item></Geometries></Item></DrawableModelsHigh>
          <Bounds type="Composite"><Children><Item type="GeometryBVH"><CompositeFlags1 /><CompositeFlags2 />
          <Polygons>{polys}</Polygons></Item></Children></Bounds></Drawable>"""
        with tempfile.TemporaryDirectory() as d:
            write(d, 'export/ha_chair.ydr.xml', xml)
            found = run(d)
        self.assertIn('BVH_NO_FLAGS', codes(found, 'error'))
        self.assertIn('POLY_COLLISION_HEAVY', codes(found, 'warn'))

    def test_textures_uncompressed_and_no_mips(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_crate.ytd', ytd_bytes([('big', 2048, 2048, A8R8G8B8, 12), ('flat', 512, 512, DXT1, 1),
                                                          ('odd', 1000, 1000, DXT1, 10)]))
            found = run(d)
        self.assertIn('TEX_UNCOMPRESSED', codes(found, 'warn'))
        self.assertIn('TEX_LARGE', codes(found, 'info'))
        self.assertIn('TEX_NO_MIPS', codes(found, 'warn'))
        self.assertIn('TEX_NOT_POW2', codes(found, 'warn'))

    def test_lod_collision_and_defaults_like_wood_table(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_crate.ydr', ydr_bytes(high=1048, med=0, radius=1.4, bound_type=None))
            write(d, 'res/stream/ha_crate.ytyp', ytyp_bytes([dict(name='ha_crate', txd='ha_crate', lod=200.0, hd=100.0, flags=0, radius=1.4)]))
            found = run(d)
        self.assertIn('NO_LOD', codes(found, 'info'))
        self.assertIn('NO_COLLISION', codes(found, 'warn'))
        self.assertIn('LODDIST_DEFAULT', codes(found, 'info'))
        self.assertIn('FLAGS_ZERO', codes(found, 'info'))
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_crate.ydr', ydr_bytes(high=1048, med=1000, bound_type=None))
            write(d, 'res/stream/ha_crate.ybn', b'RSC7' + struct.pack('<III', 43, 0, 0) + b'\0' * 16)
            found = run(d)
        self.assertIn('LOD_NOT_REDUCED', codes(found, 'warn'))
        self.assertIn('EXTERNAL_YBN', codes(found, 'info'))
        self.assertNotIn('NO_COLLISION', codes(found))

    def test_model_without_archetype_and_duplicates(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_extra.ydr', ydr_bytes())
            write(d, 'res/stream/prop_cs_burger_01.ydr', ydr_bytes(radius=0.1))
            write(d, 'res/stream/sub/ha_crate.ytd', ytd_bytes(GOOD_TEX))
            write(d, 'res/stream/ha_more.ytyp', ytyp_bytes([dict(name='ha_crate', txd='ha_crate', lod=90.0)]))
            found = run(d)
        self.assertIn('MODEL_NO_ARCHETYPE', codes(found, 'warn'))
        self.assertIn('MODEL_REPLACES_VANILLA', codes(found, 'info'))
        self.assertIn('DUPLICATE_ASSET', codes(found, 'error'))
        self.assertIn('ARCHETYPE_DUPLICATE', codes(found, 'warn'))

    def test_corrupt_binary_does_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            good_resource(d)
            write(d, 'res/stream/ha_crate.ydr', b'RSC7' + struct.pack('<III', 165, VIRT_FLAGS, 0) + b'garbage')
            found = run(d)
        self.assertIn('PARSE_FAILED', codes(found, 'info'))

    def test_loose_stream_without_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'res/stream/ha_crate.ydr', ydr_bytes())
            found = run(os.path.join(d, 'res'))
        self.assertIn('NO_MANIFEST', codes(found, 'error'))


if __name__ == '__main__':
    unittest.main()
