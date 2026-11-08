"""Tests for asset_gate.py (standard library only).

    py -3 -I .claude/skills/fivem-asset-acceptance/scripts/test_asset_gate.py

Per-type checkers are replaced by tiny fake scripts in a temporary skills folder, so these tests
exercise the gate (classification, subprocess, JSON normalisation, attribution, gate checks) and
not the real checkers (they have their own tests).
"""
import os
import struct
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_gate as gate  # noqa: E402

RSC = b'RSC7' + struct.pack('<III', 165, 0, 0) + b'\0' * 16
BIG = b'RSC7' + struct.pack('<III', 13, 0, (1 << 25) | 15) + b'\0' * 16   # 64 MiB physical


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode = 'wb' if isinstance(data, bytes) else 'w'
    with open(p, mode, **({} if isinstance(data, bytes) else {'encoding': 'utf-8'})) as fh:
        fh.write(data)


FAKE_LIST = textwrap.dedent("""
    import json, os, sys
    paths = [a for a in sys.argv[1:] if a != '--json']
    out = []
    for p in paths:
        name = os.path.basename(p)
        out.append({'level': 'warn', 'code': 'FAKE_WARN', 'file': name + '/stream/x.ydr', 'message': 'from ' + name})
        if os.path.exists(os.path.join(p, 'stream', 'locked.ydr')):
            out.append({'level': 'warn', 'code': 'NOT_RSC7', 'file': 'stream/locked.ydr', 'message': 'not rsc ' + name})
    if len(paths) > 1:
        out.append({'level': 'error', 'code': 'FAKE_CROSS', 'file': None, 'message': 'id clash between ' + str(len(paths))})
    print(json.dumps(out))
    sys.exit(0)
""")
FAKE_DICT = textwrap.dedent("""
    import json, os, sys
    paths = [a for a in sys.argv[1:] if a != '--json']
    print(json.dumps({'resources': [os.path.basename(p) for p in paths],
                      'findings': [{'level': 'error', 'code': 'FAKE_ERROR', 'resource': os.path.basename(p),
                                    'message': '坏了 ' + os.path.basename(p)} for p in paths]}, ensure_ascii=False))
    sys.exit(1)
""")
FAKE_CRASH = "raise SystemExit('boom')\n"


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        self.skills = os.path.join(self.root, 'skills')
        self.res = os.path.join(self.root, 'resources')
        self._skills, self._checkers = gate.SKILLS, gate.CHECKERS
        gate.SKILLS = self.skills
        gate.CHECKERS = {t: [] for t in self._checkers}

    def tearDown(self):
        gate.SKILLS, gate.CHECKERS = self._skills, self._checkers
        self.tmp.cleanup()

    def fake(self, typ, skill, body, optional=False):
        write(self.skills, f'{skill}/scripts/check.py', body)
        gate.CHECKERS[typ] = [(skill, 'check.py', optional)]

    def resource(self, name, files, manifest="fx_version 'cerulean'\ngame 'gta5'\n", credits=True):
        write(self.res, f'{name}/fxmanifest.lua', manifest)
        if credits:
            write(self.res, f'{name}/CREDITS.md', 'author, source, licence')
        for rel, data in files.items():
            write(self.res, f'{name}/{rel}', data)
        return os.path.join(self.res, name)

    # ---------- classification ----------
    def test_classify_each_type(self):
        cases = {
            'car': ({'data/vehicles.meta': '<x/>', 'stream/car.yft': RSC, 'stream/car_hi.yft': RSC}, "data_file 'VEHICLE_METADATA_FILE' 'data/vehicles.meta'", {'vehicle'}),
            'cloth': ({'stream/mp_m_freemode_01_ha^jbib_000_u.ydd': RSC}, '', {'clothing'}),
            'mymap': ({'stream/a.ymap': RSC, 'stream/a.ybn': RSC}, "this_is_a_map 'yes'", {'map'}),
            'props': ({'stream/p.ydr': RSC, 'stream/p.ytyp': RSC}, "data_file 'DLC_ITYP_REQUEST' 'stream/p.ytyp'", {'prop'}),
            'emotes': ({'stream/dance@a.ycd': RSC, 'AnimationListCustom.lua': ''}, '', {'anim'}),
            'snd': ({'audioconfig/x_game.dat151.rel': b'x', 'sfx/dlc_x/x.awc': b'ADAT'}, "data_file 'AUDIO_WAVEPACK' 'sfx/dlc_x'", {'sound'}),
            'gun': ({'meta/weapons.meta': '<x/>', 'stream/w_pi_x.ydr': RSC}, "data_file 'WEAPONINFO_FILE' 'meta/weapons.meta'", {'weapon'}),
            'tex': ({'stream/roads+hi.ytd': RSC}, '', {'graphics'}),
            'pedres': ({'peds.meta': '<x/>', 'stream/a_m_y_x.yft': RSC}, "data_file 'PED_METADATA_FILE' 'peds.meta'", {'ped'}),
            'ui': ({'html/index.html': ''}, "ui_page 'html/index.html'", {'script'}),
        }
        for name, (files, extra, want) in cases.items():
            r = gate.Res(self.resource(name, files, "fx_version 'cerulean'\ngame 'gta5'\n" + extra + '\n'))
            self.assertEqual(gate.classify(r), want, name)
        ui = gate.Res(os.path.join(self.res, 'ui'))
        self.assertEqual(gate.classify(ui, ui=True), {'nui'})

    # ---------- checkers ----------
    def test_runs_checker_normalises_and_attributes(self):
        self.fake('prop', 'fake-prop', FAKE_LIST)
        self.fake('vehicle', 'fake-car', FAKE_DICT)
        self.resource('props_a', {'stream/p.ydr': RSC, 'stream/p.ytyp': RSC})
        self.resource('props_b', {'stream/q.ydr': RSC, 'stream/q.ytyp': RSC})
        self.resource('car', {'data/vehicles.meta': '<x/>', 'stream/car.yft': RSC})
        rep = gate.gate([self.res])
        by = {r['name']: r for r in rep['resources']}
        self.assertEqual(by['props_a']['status'], 'warned')
        self.assertEqual([f['message'] for f in by['props_a']['findings'] if f['code'] == 'FAKE_WARN'], ['from props_a'])
        car = [f for f in by['car']['findings'] if f['code'] == 'FAKE_ERROR'][0]
        self.assertEqual(car['file'], 'car')          # 'resource' key normalised to 'file'
        self.assertEqual(by['car']['status'], 'failed')
        self.assertIn('FAKE_CROSS', [f['code'] for f in rep['cross']])   # only the combined run sees it
        self.assertEqual(rep['summary']['failed'], 1)

    def test_missing_checker_and_crash(self):
        gate.CHECKERS['prop'] = [('nowhere', 'check.py', False)]
        self.fake('map', 'fake-map', FAKE_CRASH)
        self.resource('props', {'stream/p.ydr': RSC, 'stream/p.ytyp': RSC})
        self.resource('mymap', {'stream/a.ymap': RSC})
        rep = gate.gate([self.res])
        self.assertIn('CHECKER_MISSING', [f['code'] for f in rep['cross']])
        by = {r['name']: r for r in rep['resources']}
        self.assertEqual(by['mymap']['status'], 'incomplete')
        self.assertGreater(rep['summary']['crashed'], 0)

    def test_optional_checker_missing_is_silent(self):
        gate.CHECKERS['vehicle'] = [('nowhere', 'check_livery.py', True)]
        self.resource('car', {'data/vehicles.meta': '<x/>', 'stream/car.yft': RSC})
        rep = gate.gate([self.res])
        self.assertNotIn('CHECKER_MISSING', [f['code'] for f in rep['cross']])

    def test_fxap_not_rsc7_is_translated(self):
        self.fake('prop', 'fake-prop', FAKE_LIST)
        self.resource('locked', {'stream/p.ydr': RSC, 'stream/p.ytyp': RSC, 'stream/locked.ydr': b'FXAP' + b'\0' * 30,
                                 '.fxap': b'FXAP'})
        rep = gate.gate([self.res])
        codes = [f['code'] for f in rep['resources'][0]['findings']]
        self.assertNotIn('NOT_RSC7', codes)
        self.assertIn('ESCROWED', codes)

    # ---------- gate checks ----------
    def test_gate_checks(self):
        self.resource('loose_map', {'stream/a.ymap': RSC, 'stream/a.ymap.xml': '<CMapData/>', 'stream/src.blend': b'B',
                                    'stream/Big Tex.ytd': BIG, 'stream_enhanced/a.ymap': RSC, 'stream/b.ybn': RSC},
                      credits=False)
        rep = gate.gate([self.res])
        codes = {f['code']: f['level'] for f in rep['resources'][0]['findings']}
        for code, level in (('XML_IN_STREAM', 'error'), ('SOURCE_IN_STREAM', 'warn'), ('NAME_CASE', 'warn'),
                            ('ASSET_OVER_48MIB', 'error'), ('NO_PROVENANCE', 'warn'), ('STREAM_ENHANCED_PARTIAL', 'warn')):
            self.assertEqual(codes.get(code), level, code)

    def test_cross_resource_duplicate_between_types(self):
        self.resource('mymap', {'stream/shared_name.ydr': RSC, 'stream/a.ymap': RSC})
        self.resource('car', {'data/vehicles.meta': '<x/>', 'stream/car.yft': RSC, 'stream/shared_name.ydr': RSC})
        rep = gate.gate([self.res])
        dup = [f for f in rep['cross'] if f['code'] == 'CROSS_RESOURCE_DUPLICATE']
        self.assertEqual(len(dup), 1)
        self.assertIn('shared_name.ydr', dup[0]['message'])

    def test_no_manifest_folder(self):
        write(self.res, 'export/stream/p.ydr', RSC)
        rep = gate.gate([os.path.join(self.res, 'export')])
        self.assertIn('NO_MANIFEST', [f['code'] for f in rep['resources'][0]['findings']])

    def test_ped_is_manual_and_list_mode_runs_nothing(self):
        self.resource('pedres', {'peds.meta': '<x/>', 'stream/a_m_y_x.yft': RSC}, "data_file 'PED_METADATA_FILE' 'peds.meta'\n")
        rep = gate.gate([self.res])
        self.assertEqual(rep['resources'][0]['status'], 'manual')
        self.assertIn('ped', rep['checklist'])
        listed = gate.gate([self.res], run=False)
        self.assertEqual(listed['resources'][0]['findings'], [])

    def test_only_filter(self):
        self.resource('props', {'stream/p.ydr': RSC, 'stream/p.ytyp': RSC})
        self.resource('car', {'data/vehicles.meta': '<x/>', 'stream/car.yft': RSC})
        rep = gate.gate([self.res], only={'vehicle'})
        self.assertEqual([r['name'] for r in rep['resources']], ['car'])


if __name__ == '__main__':
    unittest.main()
