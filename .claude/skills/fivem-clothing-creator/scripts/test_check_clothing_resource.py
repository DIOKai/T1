"""Tests for check_clothing_resource.py (standard library only).

    py -3 -I .claude/skills/fivem-clothing-creator/scripts/test_check_clothing_resource.py
"""
import importlib.util
import os
import random
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_clothing_resource as chk  # noqa: E402

SMALL = 1 << 27          # one 512-byte page
MIB32 = (1 << 26) | 0xF  # s=2, base 16 MiB -> 32 MiB
MIB64 = (1 << 25) | 0xF  # s=4 -> 64 MiB


def rsc(virt=SMALL, phys=SMALL):
    return b'RSC7' + struct.pack('<III', 165, virt, phys) + b'\0' * 16


def meta(ped, dlc, echar=None, full=None, creature=None):
    echar = echar or chk.ECHAR[ped]
    full = full or f'{ped}_{dlc}'
    creature = creature if creature is not None else f'mp_creaturemetadata_{ped[3]}_{dlc}'
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ShopPedApparel>
    <pedName>{ped}</pedName>
    <dlcName>{dlc}</dlcName>
    <fullDlcName>{full}</fullDlcName>
    <eCharacter>{echar}</eCharacter>
    <creatureMetaData>{creature}</creatureMetaData>
    <pedOutfits></pedOutfits>
    <pedComponents></pedComponents>
    <pedProps></pedProps>
</ShopPedApparel>
"""


def manifest(metas, declare=None, extra=''):
    declare = metas if declare is None else declare
    files = ',\n  '.join(f"'{m}'" for m in metas)
    lines = '\n'.join(f"data_file 'SHOP_PED_APPAREL_META_FILE' '{m}'" for m in declare)
    return f"fx_version 'cerulean'\ngame 'gta5'\n\nfiles {{\n  {files}\n}}\n\n{lines}\n{extra}"


def write(root, rel, data):
    path = os.path.join(root, *rel.split('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fh:
        fh.write(data.encode('utf-8') if isinstance(data, str) else data)


def addon(root, dlc='goodpack', male=None, female=None, man=True, metas=True, extra_manifest=''):
    """Write an add-on pack. male/female: dict stream-name-without-prefix -> bytes ('p:' prefix for props)."""
    res = os.path.join(root, dlc)
    meta_names = []
    for ped, items in (('mp_m_freemode_01', male), ('mp_f_freemode_01', female)):
        if items is None:
            continue
        write(res, f'stream/{ped}_{dlc}.ymt', rsc())
        if metas:
            write(res, f'{ped}_{dlc}.meta', meta(ped, dlc))
            meta_names.append(f'{ped}_{dlc}.meta')
        for name, data in items.items():
            if name.startswith('p:'):
                write(res, f'stream/{ped}_p_{dlc}^{name[2:]}', data)
            else:
                write(res, f'stream/{ped}_{dlc}^{name}', data)
    if man:
        write(res, 'fxmanifest.lua', manifest(meta_names, extra=extra_manifest))
    return res


def codes(findings, level=None):
    return {f['code'] for f in findings if level is None or f['level'] == level}


GOOD_MALE = {
    'jbib_000_u.ydd': rsc(), 'jbib_diff_000_a_uni.ytd': rsc(), 'jbib_diff_000_b_uni.ytd': rsc(),
    'jbib_001_u.ydd': rsc(), 'jbib_diff_001_a_uni.ytd': rsc(),
    'feet_000_r.ydd': rsc(), 'feet_diff_000_a_whi.ytd': rsc(),
    'p:p_head_000.ydd': rsc(), 'p:p_head_diff_000_a.ytd': rsc(),
    'p:p_eyes_000.ydd': rsc(), 'p:p_eyes_diff_000_a.ytd': rsc(),
}
GOOD_FEMALE = {'lowr_000_u.ydd': rsc(), 'lowr_diff_000_a_uni.ytd': rsc()}


class GoodPack(unittest.TestCase):
    def test_good_pack_has_no_errors_or_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male=GOOD_MALE, female=GOOD_FEMALE)
            write(res, 'stream/mp_creaturemetadata_m_goodpack.ymt', rsc())
            findings, summary = chk.check([tmp])
            self.assertEqual(codes(findings, 'error'), set(), findings)
            self.assertEqual(codes(findings, 'warn'), set(), findings)
            # female meta names a creaturemetadata YMT that is not streamed: info only
            self.assertIn('CREATURE_YMT_ABSENT', codes(findings, 'info'))
            male = next(s for s in summary if s['collection'] == 'mp_m_freemode_01_goodpack')
            self.assertEqual(male['types'], {'feet': 1, 'jbib': 2, 'p_eyes': 1, 'p_head': 1})
            self.assertEqual(male['shop_entries'], 6)

    def test_subfolders_in_stream_are_fine(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male={}, female=None)
            write(res, 'stream/male/jbib/mp_m_freemode_01_goodpack^jbib_000_u.ydd', rsc())
            write(res, 'stream/male/jbib/mp_m_freemode_01_goodpack^jbib_diff_000_a_uni.ytd', rsc())
            findings, _ = chk.check([tmp])
            self.assertEqual(codes(findings, 'error') | codes(findings, 'warn'), set(), findings)

    def test_exit_codes_and_utf8_output(self):
        script = os.path.join(HERE, 'check_clothing_resource.py')
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male=GOOD_MALE)
            ok = subprocess.run([sys.executable, '-I', script, tmp], capture_output=True)
            self.assertEqual(ok.returncode, 0, ok.stdout.decode('utf-8', 'replace'))
            self.assertIn('集合统计', ok.stdout.decode('utf-8'))
            write(os.path.join(tmp, 'goodpack'), 'stream/mp_m_freemode_01_goodpack^jbib_diff_009_a_uni.ytd', rsc())
            bad = subprocess.run([sys.executable, '-I', script, tmp], capture_output=True)
            self.assertEqual(bad.returncode, 1)


class Manifest(unittest.TestCase):
    def test_no_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male=GOOD_MALE, man=False)
            self.assertIn('NO_MANIFEST', codes(chk.check([tmp])[0], 'error'))

    def test_meta_not_declared_and_not_in_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male=GOOD_MALE, man=False)
            write(res, 'fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\nfiles { }\n")
            self.assertIn('META_NOT_DECLARED', codes(chk.check([tmp])[0], 'error'))
            write(res, 'fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\ndata_file 'SHOP_PED_APPAREL_META_FILE' 'mp_m_freemode_01_goodpack.meta'\n")
            self.assertIn('META_NOT_IN_FILES', codes(chk.check([tmp])[0], 'error'))

    def test_data_file_missing_and_wrong_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            extra = ("data_file 'SHOP_PED_APPAREL_META_FILE' 'gone.meta'\n"
                     "data_file 'SHOP_PED_APPAREL_META_FILE' 'first_person_alternates_goodpack.meta'\n")
            res = addon(tmp, male=GOOD_MALE, extra_manifest=extra)
            write(res, 'first_person_alternates_goodpack.meta', '<CPedVariationInfo/>')
            f = chk.check([tmp])[0]
            self.assertIn('DATA_FILE_MISSING', codes(f, 'error'))
            self.assertIn('DATA_FILE_TYPE', codes(f, 'warn'))

    def test_game_not_gta5(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male=GOOD_MALE)
            with open(os.path.join(res, 'fxmanifest.lua'), encoding='utf-8') as fh:
                text = fh.read().replace("game 'gta5'", "game 'rdr3'")
            write(res, 'fxmanifest.lua', text)
            self.assertIn('GAME_NOT_GTA5', codes(chk.check([tmp])[0], 'warn'))

    def test_alternates_not_declared(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male=dict(GOOD_MALE, **{'jbib_000_u_1.ydd': rsc()}))
            self.assertIn('ALT_NOT_DECLARED', codes(chk.check([tmp])[0], 'warn'))


class Meta(unittest.TestCase):
    def test_fullname_echaracter_and_missing_ymt(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male=GOOD_MALE)
            write(res, 'mp_m_freemode_01_goodpack.meta', meta('mp_m_freemode_01', 'goodpack', echar='SCR_CHAR_MULTIPLAYER_F', full='mp_m_freemode_01_other'))
            f = chk.check([tmp])[0]
            self.assertIn('META_FULLNAME', codes(f, 'error'))
            self.assertIn('META_ECHARACTER', codes(f, 'error'))
            self.assertIn('META_NO_YMT', codes(f, 'error'))
            self.assertIn('YMT_NO_META', codes(f, 'error'))

    def test_creature_unreferenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male=GOOD_MALE)
            write(res, 'stream/mp_creaturemetadata_heels.ymt', rsc())
            self.assertIn('CREATURE_UNREFERENCED', codes(chk.check([tmp])[0], 'warn'))


class Names(unittest.TestCase):
    def test_hand_named_files_get_a_slot_hint(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, 'myclothes/fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\n")
            for f in ('jacket_000_u.ydd', 'jacket_diff_000_a_uni.ytd', 'hat_000.ydd'):
                write(tmp, 'myclothes/stream/' + f, rsc())
            found = chk.check([tmp])[0]
        msgs = [f['message'] for f in found if f['code'] == 'NOT_CLOTHING_NAMED']
        self.assertEqual(len(msgs), 3)
        self.assertTrue(any('jbib' in m for m in msgs) and any('p_head' in m for m in msgs))

    def test_orphan_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male=GOOD_MALE)
            write(res, 'stream/mp_m_freemode_01_oldname^jbib_000_u.ydd', rsc())
            self.assertIn('ORPHAN_PREFIX', codes(chk.check([tmp])[0], 'error'))

    def test_uppercase_space_xml_raw_badname_noprefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male=GOOD_MALE)
            write(res, 'stream/mp_m_freemode_01_goodpack^JBIB_002_u.ydd', rsc())
            write(res, 'stream/mp_m_freemode_01_goodpack^jbib_3_u.ydd', rsc())
            write(res, 'stream/mp_m_freemode_01_goodpack^jbib 004_u.ydd', rsc())
            write(res, 'stream/jbib_005_u.ydd', rsc())
            write(res, 'stream/mp_m_freemode_01_goodpack^jbib_006_u.ydd.xml', '<x/>')
            write(res, 'stream/jbib_diff_000_c.dds', b'DDS ')
            write(res, 'stream/mp_fm_skin_m_up_whi - Kopya.ytd', rsc())
            f = chk.check([tmp])[0]
            self.assertIn('SPACED_NAMES', codes(f, 'warn'))
            self.assertIn('NAME_UPPERCASE', codes(f, 'warn'))
            self.assertIn('BAD_NAME', codes(f, 'warn'))
            self.assertIn('NAME_SPACE', codes(f, 'error'))
            self.assertIn('NO_PREFIX', codes(f, 'warn'))
            self.assertIn('XML_IN_STREAM', codes(f, 'error'))
            self.assertIn('RAW_IMAGE_IN_STREAM', codes(f, 'warn'))
            self.assertTrue(any('3 位' in x['message'] for x in f if x['code'] == 'BAD_NAME'))

    def test_replacing_base_ymt(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = addon(tmp, male=GOOD_MALE)
            write(res, 'stream/mp_m_freemode_01.ymt', rsc())
            self.assertIn('REPLACES_BASE_YMT', codes(chk.check([tmp])[0], 'warn'))


class Pairing(unittest.TestCase):
    def test_texture_without_drawable_and_drawable_without_texture(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male={'jbib_000_u.ydd': rsc(), 'jbib_diff_001_a_uni.ytd': rsc()})
            f = chk.check([tmp])[0]
            self.assertIn('TEXTURE_NO_DRAWABLE', codes(f, 'error'))
            self.assertIn('NO_TEXTURE', codes(f, 'warn'))

    def test_skin_mismatch_both_ways(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male={'jbib_000_u.ydd': rsc(), 'jbib_diff_000_a_whi.ytd': rsc(),
                             'uppr_000_r.ydd': rsc(), 'uppr_diff_000_a_uni.ytd': rsc()})
            f = [x for x in chk.check([tmp])[0] if x['code'] == 'SKIN_MISMATCH']
            self.assertEqual(len(f), 2)

    def test_both_u_and_r_and_skin_on_wrong_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male={'jbib_000_u.ydd': rsc(), 'jbib_000_r.ydd': rsc(), 'jbib_diff_000_a_uni.ytd': rsc()})
            f = chk.check([tmp])[0]
            self.assertIn('BOTH_U_AND_R', codes(f, 'error'))
            self.assertIn('SKIN_ON_TYPE', codes(f, 'warn'))

    def test_texture_letters(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male={'jbib_000_u.ydd': rsc(), 'jbib_diff_000_a_uni.ytd': rsc(), 'jbib_diff_000_c_uni.ytd': rsc(),
                             'jbib_diff_000_aa_uni.ytd': rsc()})
            f = chk.check([tmp])[0]
            self.assertIn('TEXTURE_GAP', codes(f, 'warn'))
            self.assertIn('TEXTURE_LETTER', codes(f, 'error'))

    def test_prop_texture_with_uni(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male={'p:p_head_000.ydd': rsc(), 'p:p_head_diff_000_a_uni.ytd': rsc()})
            self.assertIn('PROP_TEXTURE_SUFFIX', codes(chk.check([tmp])[0], 'error'))

    def test_companion_without_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male=dict(GOOD_MALE, **{'jbib_002_u.yld': rsc()}))
            self.assertIn('COMPANION_NO_BASE', codes(chk.check([tmp])[0], 'warn'))


class Numbering(unittest.TestCase):
    def test_gap(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male={'jbib_000_u.ydd': rsc(), 'jbib_diff_000_a_uni.ytd': rsc(),
                             'jbib_002_u.ydd': rsc(), 'jbib_diff_002_a_uni.ytd': rsc()})
            f = [x for x in chk.check([tmp])[0] if x['code'] == 'NUMBER_GAP']
            self.assertEqual(len(f), 1)
            self.assertIn('001', f[0]['message'])

    def _many(self, n):
        items = {}
        for i in range(n):
            items[f'task_{i:03d}_u.ydd'] = rsc()
            items[f'task_diff_{i:03d}_a_uni.ytd'] = rsc()
        return items

    def test_over_128_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male=self._many(129))
            f = chk.check([tmp])[0]
            self.assertIn('COUNT_OVER_128', codes(f, 'warn'))
            self.assertNotIn('COUNT_256', codes(f))

    def test_256_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male=self._many(256))
            self.assertIn('COUNT_256', codes(chk.check([tmp])[0], 'error'))


class Header(unittest.TestCase):
    def test_same_formula_as_mlo_checker(self):
        mlo = os.path.join(HERE, '..', '..', 'fivem-mlo-housing', 'scripts', 'check_mlo_resource.py')
        if not os.path.exists(mlo):
            self.skipTest('fivem-mlo-housing not next to this skill')
        spec = importlib.util.spec_from_file_location('mlo_chk', mlo)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        rnd = random.Random(7)
        for _ in range(500):
            f = rnd.getrandbits(32)
            self.assertEqual(chk.rsc_page_size(f), mod.rsc_page_size(f))

    def test_sizes(self):
        self.assertEqual(chk.rsc_page_size(SMALL), 0x200)
        self.assertEqual(chk.rsc_page_size(MIB32), 32 * chk.MIB)
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male={'jbib_000_u.ydd': rsc(), 'jbib_diff_000_a_uni.ytd': rsc(SMALL, MIB32),
                             'jbib_001_u.ydd': rsc(), 'jbib_diff_001_a_uni.ytd': rsc(SMALL, MIB64)})
            f = chk.check([tmp])[0]
            self.assertIn('ASSET_OVER_16MIB', codes(f, 'warn'))
            self.assertIn('ASSET_OVER_48MIB', codes(f, 'warn'))

    def test_not_rsc_and_escrow(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, male={'jbib_000_u.ydd': b'<xml>not compiled</xml>', 'jbib_diff_000_a_uni.ytd': b'FXAP' + b'\0' * 20})
            f = chk.check([tmp])[0]
            self.assertIn('NOT_RSC7', codes(f, 'warn'))
            self.assertIn('ESCROWED', codes(f, 'info'))


class AcrossPacks(unittest.TestCase):
    def test_collection_clash_and_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = addon(os.path.join(tmp, 'a'), male=GOOD_MALE)
            addon(os.path.join(tmp, 'b'), male=GOOD_MALE)
            f = chk.check([tmp])[0]
            self.assertIn('COLLECTION_CLASH', codes(f, 'error'))
            self.assertIn('DUPLICATE_STREAM_FILE', codes(f, 'warn'))
            self.assertIn('DUPLICATE_CONTENT', codes(f, 'warn'))
            self.assertTrue(os.path.isdir(a))

    def test_different_names_do_not_clash(self):
        with tempfile.TemporaryDirectory() as tmp:
            addon(tmp, dlc='packone', male={'jbib_000_u.ydd': rsc(), 'jbib_diff_000_a_uni.ytd': rsc()})
            addon(tmp, dlc='packtwo', male={'jbib_000_u.ydd': rsc(SMALL, SMALL | 1), 'jbib_diff_000_a_uni.ytd': rsc()})
            f = chk.check([tmp])[0]
            self.assertNotIn('COLLECTION_CLASH', codes(f))
            self.assertEqual(codes(f, 'error'), set(), f)

    def test_replacement_pack_is_not_an_addon(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = os.path.join(tmp, 'facepack')
            write(res, 'fxmanifest.lua', "fx_version 'cerulean'\ngame 'gta5'\nfiles { }\n")
            write(res, 'stream/mp_f_freemode_01^head_diff_001_a_whi.ytd', rsc())
            write(res, 'stream/mp_f_freemode_01^head_diff_002_a_bla.ytd', rsc())
            write(res, 'stream/mp_f_freemode_01_mp_f_xmas_01^jbib_diff_004_a_uni.ytd', rsc())
            f = chk.check([tmp])[0]
            self.assertEqual(codes(f, 'error'), set(), f)
            self.assertIn('REPLACEMENT_PACK', codes(f, 'info'))
            self.assertNotIn('NUMBER_GAP', codes(f))


if __name__ == '__main__':
    unittest.main(verbosity=1)
