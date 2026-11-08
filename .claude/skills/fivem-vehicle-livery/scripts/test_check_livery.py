"""Tests for check_livery.py (standard library only). Builds tiny RSC7 .ytd/.yft files in a temp folder.

    py -3 -I .claude/skills/fivem-vehicle-livery/scripts/test_check_livery.py
"""
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_livery as chk  # noqa: E402

V = 0x50000000
FMT = {'DXT1': 0x31545844, 'DXT5': 0x35545844, 'BC7': 0x20374342, 'A8R8G8B8': 21}
VFLAGS = 0x10            # 256 pages x 512 bytes = 128 KiB virtual block (rsc_page_size)


class Blob:
    def __init__(self, size=0x20000):
        self.b = bytearray(size)

    def q(self, o, v):
        struct.pack_into('<Q', self.b, o, v)

    def h(self, o, v):
        struct.pack_into('<H', self.b, o, v)

    def i(self, o, v):
        struct.pack_into('<I', self.b, o, v)

    def s(self, o, text):
        self.b[o:o + len(text) + 1] = text.encode() + b'\0'

    def rsc(self, path):
        assert chk.rsc_page_size(VFLAGS) == len(self.b)
        comp = zlib.compressobj(6, zlib.DEFLATED, -15)
        data = comp.compress(bytes(self.b)) + comp.flush()
        with open(path, 'wb') as fh:
            fh.write(struct.pack('<4sIII', b'RSC7', 13, VFLAGS, 0) + data)


def put_dict(bl, base, textures, area):
    """pgDictionary<grcTexture> at `base`; texture structs placed from `area`."""
    arr = area
    bl.q(base + 0x30, V + arr)
    bl.h(base + 0x38, len(textures))
    bl.h(base + 0x3A, len(textures))
    for k, (name, w, h, fmt, levels) in enumerate(textures):
        t = area + 0x100 + k * 0x100
        bl.q(arr + 8 * k, V + t)
        bl.s(t + 0x90, name)
        bl.q(t + 0x28, V + t + 0x90)
        bl.h(t + 0x50, w)
        bl.h(t + 0x52, h)
        bl.i(t + 0x58, FMT[fmt])
        bl.b[t + 0x5D] = levels


def make_ytd(path, textures):
    bl = Blob()
    put_dict(bl, 0, textures, 0x1000)
    bl.rsc(path)


def make_yft(path, shaders, lods=None, embedded=None):
    """shaders: list of {sampler: texture}; lods: {'high': [shader idx...], 'med': [...]}."""
    bl = Blob()
    drw, sg, sp = 0x100, 0x200, 0x300
    bl.q(0x30, V + drw)
    bl.q(drw + 0x10, V + sg)
    bl.q(sg + 0x10, V + sp)
    bl.h(sg + 0x18, len(shaders))
    for k, samplers in enumerate(shaders):
        s, pp = 0x400 + k * 0x40, 0x2000 + k * 0x800
        bl.q(sp + 8 * k, V + s)
        bl.q(s, V + pp)
        bl.i(s + 8, chk.joaat('vehicle_paint3'))
        bl.b[s + 0x10] = len(samplers)
        for j, (sampler, tex) in enumerate(samplers.items()):
            tb = pp + 0x400 + j * 0x80
            bl.b[pp + 16 * j] = 0                                   # texture parameter
            bl.q(pp + 16 * j + 8, V + tb)
            bl.s(tb + 0x40, tex)
            bl.q(tb + 0x28, V + tb + 0x40)
            bl.i(pp + 16 * len(samplers) + 4 * j, chk.joaat(sampler))
    if embedded:
        put_dict(bl, 0x8000, embedded, 0x8100)
        bl.q(sg + 0x08, V + 0x8000)
    for n, lod in enumerate(('high', 'med', 'low', 'vlow')):
        used = (lods or {'high': list(range(len(shaders)))}).get(lod)
        if used is None:
            continue
        lst, arr, mdl, smap = 0xA000 + n * 0x400, 0xA010 + n * 0x400, 0xA100 + n * 0x400, 0xA200 + n * 0x400
        bl.q(drw + 0x50 + 8 * n, V + lst)
        bl.q(lst, V + arr)
        bl.h(lst + 8, 1)
        bl.q(arr, V + mdl)
        bl.h(mdl + 0x10, len(used))
        bl.q(mdl + 0x20, V + smap)
        for g, si in enumerate(used):
            bl.h(smap + 2 * g, si)
    bl.rsc(path)


VEHICLES = """<?xml version="1.0" encoding="UTF-8"?>
<CVehicleModelInfo__InitDataList><InitDatas>{items}</InitDatas></CVehicleModelInfo__InitDataList>"""
VEH_ITEM = "<Item><modelName>{m}</modelName><txdName>{m}</txdName><flags>{flags}</flags></Item>"
CARCOLS = """<?xml version="1.0" encoding="UTF-8"?>
<CVehicleModelInfoVarGlobal><Kits><Item><kitName>{kit}</kitName><id value="4100" /><kitType>MKT_SPECIAL</kitType>
<visibleMods>{mods}</visibleMods><linkMods /><statMods /><slotNames /><liveryNames>{names}</liveryNames></Item></Kits>
</CVehicleModelInfoVarGlobal>"""
MOD = "<Item><modelName>{m}</modelName><modShopLabel>{label}</modShopLabel><type>{type}</type><bone>chassis</bone></Item>"
VARIATIONS = """<?xml version="1.0" encoding="UTF-8"?>
<CVehicleModelInfoVariation><variationData><Item><modelName>{m}</modelName><kits><Item>{kit}</Item></kits></Item>
</variationData></CVehicleModelInfoVariation>"""


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return p


def mk(root, rel):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def codes(findings):
    return {f['code'] for f in findings}


class Readers(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            make_ytd(os.path.join(d, 'a.ytd'), [('car_sign_1', 2048, 2048, 'DXT5', 12), ('car_sign_2', 1024, 512, 'DXT1', 11)])
            t = chk.read_ytd(os.path.join(d, 'a.ytd'))
            self.assertEqual([(x['name'], x['width'], x['height'], x['format'], x['levels']) for x in t],
                             [('car_sign_1', 2048, 2048, 'DXT5', 12), ('car_sign_2', 1024, 512, 'DXT1', 11)])
            make_yft(os.path.join(d, 'a.yft'), [{'DiffuseSampler': 'x', 'DiffuseSampler2': 'car_sign_1'}, {'DiffuseSampler': 'y'}],
                     lods={'high': [0, 1], 'med': [1]}, embedded=[('liv', 64, 64, 'DXT5', 7)])
            y = chk.read_yft(os.path.join(d, 'a.yft'))
            self.assertEqual(y['shaders'][0]['samplers']['DiffuseSampler2'], 'car_sign_1')
            self.assertEqual(y['lods'], {'high': {0, 1}, 'med': {1}})
            self.assertEqual(y['embedded'][0]['name'], 'liv')

    def test_memory_and_rsc8(self):
        self.assertAlmostEqual(chk.tex_mib({'width': 2048, 'height': 2048, 'format': 'DXT5', 'levels': 12}), 5.333, places=2)
        self.assertAlmostEqual(chk.tex_mib({'width': 4096, 'height': 4096, 'format': 'A8R8G8B8', 'levels': 1}), 64.0, places=2)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'e.ytd')
            with open(p, 'wb') as fh:
                fh.write(b'RSC8' + bytes(60))
            with self.assertRaises(ValueError):
                chk.read_ytd(p)


class Check(unittest.TestCase):
    def test_method_a_problems(self):
        with tempfile.TemporaryDirectory() as d:
            r = 'res'
            write(d, f'{r}/fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\n")
            write(d, f'{r}/data/vehicles.meta', VEHICLES.format(items=VEH_ITEM.format(m='lscsoa', flags='FLAG_EMERGENCY_SERVICE')
                                                              + VEH_ITEM.format(m='lscsob', flags='FLAG_HAS_LIVERY')))
            # lscsoa: three signs, no flag, a gap, a 4096 uncompressed sign, no mips, a junk texture
            make_yft(mk(d, f'{r}/stream/lscsoa.yft'), [{'DiffuseSampler2': 'lscso_sign_1'}, {'DiffuseSampler': 'body'}],
                     lods={'high': [0, 1], 'med': [1]})
            make_ytd(mk(d, f'{r}/stream/lscsoa.ytd'), [
                ('lscso_sign_1', 2048, 2048, 'DXT5', 12), ('lscso_sign_2', 4096, 4096, 'A8R8G8B8', 1),
                ('lscso_sign_4', 5792, 5792, 'DXT5', 13), ('Untitled design - 2023', 512, 512, 'DXT5', 10)])
            make_ytd(mk(d, f'{r}/stream/lscsoa+hi.ytd'), [('lscso_sign_1', 2048, 2048, 'DXT5', 12)])
            # lscsob: flag, but shader points at a texture that is not there, and _sign_0
            make_yft(mk(d, f'{r}/stream/lscsob.yft'), [{'DiffuseSampler2': 'redeye_sign_1'}])
            make_ytd(mk(d, f'{r}/stream/lscsob.ytd'), [('other_sign_0', 2048, 2048, 'BC7', 12)])
            f = chk.check([d])
            c = codes(f)
            for code in ('SIGNS_NO_FLAG', 'SIGN_GAP', 'TEX_UNCOMPRESSED', 'TEX_OVER_2048', 'TEX_NOT_POW2', 'TEX_NO_MIPS',
                         'JUNK_TEXTURE', 'HI_DUPLICATE', 'LOD_NO_LIVERY', 'LIVERY_TEX_MISSING', 'LIVERY_MEMORY', 'TEX_BC7'):
                self.assertIn(code, c, code)
            missing = [x for x in f if x['code'] == 'LIVERY_TEX_MISSING'][0]
            self.assertEqual(missing['level'], 'error')
            self.assertNotIn('tex', missing)

    def test_flag_without_layer_and_baked(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'res/fxmanifest.lua', '')
            write(d, 'res/data/vehicles.meta', VEHICLES.format(items=VEH_ITEM.format(m='sast1', flags='FLAG_HAS_LIVERY')))
            make_yft(mk(d, 'res/stream/sast1.yft'), [{'DiffuseSampler': 'sast_sign_1'}])
            make_ytd(mk(d, 'res/stream/sast1.ytd'), [('sast_sign_1', 2048, 2048, 'DXT5', 12)])
            f = chk.check([d])
            x = [y for y in f if y['code'] == 'FLAG_NO_LIVERY_LAYER']
            self.assertEqual(len(x), 1)
            self.assertIn('方法 C', x[0]['message'])

    def test_clean_resource(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'res/fxmanifest.lua', '')
            write(d, 'res/client.lua', "AddTextEntry('LSPD_LIV1', 'LSPD Patrol')\n")
            write(d, 'res/data/vehicles.meta', VEHICLES.format(items=VEH_ITEM.format(m='lspd1', flags='FLAG_HAS_LIVERY FLAG_LAW_ENFORCEMENT')))
            write(d, 'res/data/carcols.meta', CARCOLS.format(kit='4100_lspd1_modkit', mods='', names='<Item>LSPD_LIV1</Item>'))
            make_yft(mk(d, 'res/stream/lspd1.yft'), [{'DiffuseSampler2': 'lspd1_sign_1'}], lods={'high': [0], 'med': [0]})
            make_ytd(mk(d, 'res/stream/lspd1.ytd'), [('lspd1_sign_1', 2048, 2048, 'DXT5', 12), ('lspd1_sign_2', 2048, 2048, 'DXT5', 12)])
            f = chk.check([d])
            self.assertEqual([x for x in f if x['level'] != 'info'], [], f)

    def test_vmt_livery_mod(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'res/fxmanifest.lua', '')
            write(d, 'res/data/vehicles.meta', VEHICLES.format(items=VEH_ITEM.format(m='bcso1', flags='FLAG_EMERGENCY_SERVICE')))
            mods = (MOD.format(m='bcso1_livery1', label='BCSO1_LIV1', type='VMT_LIVERY_MOD')
                    + MOD.format(m='bcso1_livery2', label='BCSO1_LIV2', type='VMT_LIVERY_MOD')
                    + MOD.format(m='bcso1_bumf', label='BCSO1_BUMF', type='VMT_BUMPER_F'))
            write(d, 'res/data/carcols.meta', CARCOLS.format(kit='4101_bcso1_modkit', mods=mods, names=''))
            make_yft(mk(d, 'res/stream/bcso1.yft'), [{'DiffuseSampler2': 'blank'}])
            make_ytd(mk(d, 'res/stream/bcso1.ytd'), [('blank', 4, 4, 'DXT5', 1)])
            make_yft(mk(d, 'res/stream/bcso1_livery1.yft'), [{'DiffuseSampler2': 'bcso1_livery1'}],
                     embedded=[('bcso1_livery_1', 2048, 2048, 'DXT5', 12)])                   # name does not match
            make_yft(mk(d, 'res/stream/bcso1_bumf.yft'), [{'DiffuseSampler2': 'bcso1_sign_1'}])   # tuning part: skipped
            f = chk.check([d])
            c = codes(f)
            self.assertIn('LIVERY_MOD_YFT_MISSING', c)          # livery2 yft missing
            self.assertIn('LIVERY_MOD_TEX_MISSING', c)          # embedded name mismatch
            self.assertIn('LIVERY_KIT_UNUSED', c)               # no carvariations
            self.assertIn('LABEL_NO_TEXT', c)
            self.assertNotIn('LIVERY_TEX_MISSING', c)           # bumper part not treated as a car
            write(d, 'res/data/carvariations.meta', VARIATIONS.format(m='bcso1', kit='4101_bcso1_modkit'))
            self.assertNotIn('LIVERY_KIT_UNUSED', codes(chk.check([d])))

    def test_xml_exports_and_cli(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, 'loose/fbi9.yft.xml', """<?xml version="1.0"?><Fragment><Drawable><ShaderGroup><Shaders>
<Item><Name>vehicle_paint3</Name><Parameters><Item name="DiffuseSampler2" type="Texture"><Name>fbi9_sign_1</Name></Item>
</Parameters></Item></Shaders></ShaderGroup></Drawable></Fragment>""")
            write(d, 'loose/fbi9.ytd.xml', """<?xml version="1.0"?><TextureDictionary>
<Item><Name>fbi9_sign_2</Name><Width value="2048" /><Height value="2048" /><MipLevels value="12" /><Format>D3DFMT_DXT5</Format></Item>
</TextureDictionary>""")
            r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'check_livery.py'), d],
                               capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn('LIVERY_TEX_MISSING', r.stdout)
            self.assertIn('fbi9_sign_1', r.stdout)


if __name__ == '__main__':
    unittest.main()
