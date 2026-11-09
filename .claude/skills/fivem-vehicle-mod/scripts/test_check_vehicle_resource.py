"""Tests for check_vehicle_resource.py (standard library only).

    py -3 -I .claude/skills/fivem-vehicle-mod/scripts/test_check_vehicle_resource.py

Focus: data_file matching. FiveM audio entries do not name the file on disk:
AUDIO_GAMEDATA 'x_game.dat' loads x_game.dat151.rel, AUDIO_WAVEPACK names a folder of .awc.
"""
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_vehicle_resource as cvr  # noqa: E402

VEHICLES_META = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <CVehicleModelInfo__InitDataList>
      <InitDatas>
        <Item>
          <modelName>testcar</modelName>
          <txdName>testcar</txdName>
          <handlingId>TESTCAR</handlingId>
          <gameName>TESTCAR</gameName>
          <audioNameHash>testcar</audioNameHash>
        </Item>
      </InitDatas>
    </CVehicleModelInfo__InitDataList>
""")

AUDIO_MANIFEST = textwrap.dedent("""\
    fx_version 'cerulean'
    game 'gta5'
    files {
        'data/vehicles.meta',
        'audioconfig/*.dat151.rel',
        'audioconfig/*.dat54.rel',
        'audioconfig/*.dat10.rel',
        'sfx/**/*.awc',
    }
    data_file 'VEHICLE_METADATA_FILE' 'data/vehicles.meta'
    data_file 'AUDIO_GAMEDATA' 'audioconfig/testcar_game.dat'
    data_file 'AUDIO_SOUNDDATA' 'audioconfig/testcar_sounds.dat'
    data_file 'AUDIO_WAVEPACK' 'sfx/dlc_testcar'
""")


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode = 'wb' if isinstance(data, bytes) else 'w'
    with open(p, mode, **({} if isinstance(data, bytes) else {'encoding': 'utf-8'})) as fh:
        fh.write(data)


def make_resource(root, manifest, files):
    write(root, 'fxmanifest.lua', manifest)
    write(root, 'data/vehicles.meta', VEHICLES_META)
    for rel in files:
        write(root, rel, b'\0' * 8)


def no_match(findings):
    return [f['message'] for f in findings if f['code'] == 'DATA_FILE_NO_MATCH']


class DataFileMatches(unittest.TestCase):
    def test_rel_suffixes_for_every_audio_rel_type(self):
        cases = [
            ('AUDIO_GAMEDATA', 'a/x_game.dat', 'a/x_game.dat151.rel'),
            ('AUDIO_SOUNDDATA', 'a/x_sounds.dat', 'a/x_sounds.dat54.rel'),
            ('AUDIO_SYNTHDATA', 'a/x_amp.dat', 'a/x_amp.dat10.rel'),
            ('AUDIO_DYNAMIXDATA', 'a/x_mix.dat', 'a/x_mix.dat15.rel'),
            ('AUDIO_CURVEDATA', 'a/x_curves.dat', 'a/x_curves.dat16.rel'),
            ('AUDIO_SPEECHDATA', 'a/x_speech.dat', 'a/x_speech.dat4.rel'),
        ]
        for dtype, pattern, rel in cases:
            with self.subTest(dtype=dtype):
                self.assertTrue(cvr.data_file_matches(dtype, pattern, rel))

    def test_rel_suffix_is_case_insensitive_and_accepts_globs(self):
        self.assertTrue(cvr.data_file_matches('AUDIO_GAMEDATA', 'AudioConfig/X_Game.dat', 'audioconfig/x_game.DAT151.REL'))
        self.assertTrue(cvr.data_file_matches('AUDIO_GAMEDATA', 'audioconfig/*_game.dat', 'audioconfig/x_game.dat151.rel'))

    def test_full_rel_path_still_matches(self):
        self.assertTrue(cvr.data_file_matches('AUDIO_GAMEDATA', 'a/x_game.dat151.rel', 'a/x_game.dat151.rel'))

    def test_rel_suffix_needs_digits_and_same_stem(self):
        self.assertFalse(cvr.data_file_matches('AUDIO_GAMEDATA', 'a/x_game.dat', 'a/x_game.datXX.rel'))
        self.assertFalse(cvr.data_file_matches('AUDIO_GAMEDATA', 'a/x_game.dat', 'a/y_game.dat151.rel'))
        self.assertFalse(cvr.data_file_matches('AUDIO_SYNTHDATA', 'a/x_amp.dat', 'a/x_game.dat151.rel'))

    def test_rel_suffix_only_for_audio_rel_types(self):
        self.assertFalse(cvr.data_file_matches('HANDLING_FILE', 'data/handling', 'data/handling151.rel'))
        self.assertFalse(cvr.data_file_matches('AUDIO_WAVEPACK', 'a/x_game.dat', 'a/x_game.dat151.rel'))

    def test_wavepack_folder_matches_files_below_it(self):
        self.assertTrue(cvr.data_file_matches('AUDIO_WAVEPACK', 'sfx/dlc_x', 'sfx/dlc_x/x.awc'))
        self.assertTrue(cvr.data_file_matches('AUDIO_WAVEPACK', 'sfx/dlc_x/', 'sfx/dlc_x/x_npc.awc'))
        self.assertTrue(cvr.data_file_matches('AUDIO_WAVEPACK', 'sfx\\DLC_X', 'sfx/dlc_x/sub/x.awc'))

    def test_wavepack_does_not_match_sibling_folder_with_same_prefix(self):
        self.assertFalse(cvr.data_file_matches('AUDIO_WAVEPACK', 'sfx/dlc_x', 'sfx/dlc_x2/x.awc'))
        self.assertFalse(cvr.data_file_matches('AUDIO_WAVEPACK', 'sfx/dlc_x', 'sfx/dlc_x.awc'))

    def test_other_types_keep_plain_glob(self):
        self.assertTrue(cvr.data_file_matches('HANDLING_FILE', 'data/**/handling.meta', 'data/a/b/handling.meta'))
        self.assertFalse(cvr.data_file_matches('HANDLING_FILE', 'data/handling.meta', 'data/sub/handling.meta'))


class CheckAudioResource(unittest.TestCase):
    """End to end through check(), the same layout as a real converted car (redeye)."""

    GOOD_FILES = [
        'audioconfig/testcar_game.dat151.rel',
        'audioconfig/testcar_sounds.dat54.rel',
        'sfx/dlc_testcar/testcar.awc',
        'sfx/dlc_testcar/testcar_npc.awc',
    ]

    def run_check(self, manifest, files):
        with tempfile.TemporaryDirectory() as tmp:
            res = os.path.join(tmp, 'testcar')
            make_resource(res, manifest, files)
            findings, resources = cvr.check([res])
        self.assertEqual(len(resources), 1)
        return findings

    def test_standard_audio_declarations_are_not_errors(self):
        self.assertEqual(no_match(self.run_check(AUDIO_MANIFEST, self.GOOD_FILES)), [])

    def test_declared_amp_without_rel_is_reported(self):
        manifest = AUDIO_MANIFEST + "data_file 'AUDIO_SYNTHDATA' 'audioconfig/testcar_amp.dat'\n"
        msgs = no_match(self.run_check(manifest, self.GOOD_FILES))
        self.assertEqual(len(msgs), 1)
        self.assertIn('testcar_amp.dat', msgs[0])
        self.assertIn('AUDIO_SYNTHDATA', msgs[0])

    def test_declared_amp_with_rel_is_fine(self):
        manifest = AUDIO_MANIFEST + "data_file 'AUDIO_SYNTHDATA' 'audioconfig/testcar_amp.dat'\n"
        files = self.GOOD_FILES + ['audioconfig/testcar_amp.dat10.rel']
        self.assertEqual(no_match(self.run_check(manifest, files)), [])

    def test_missing_game_rel_is_reported(self):
        files = [f for f in self.GOOD_FILES if not f.endswith('.dat151.rel')]
        msgs = no_match(self.run_check(AUDIO_MANIFEST, files))
        self.assertEqual(len(msgs), 1)
        self.assertIn('AUDIO_GAMEDATA', msgs[0])

    def test_empty_or_missing_wavepack_folder_is_reported(self):
        files = [f for f in self.GOOD_FILES if not f.endswith('.awc')]
        msgs = no_match(self.run_check(AUDIO_MANIFEST, files))
        self.assertEqual(len(msgs), 1)
        self.assertIn('AUDIO_WAVEPACK', msgs[0])

    def test_misspelled_meta_path_is_still_reported(self):
        manifest = AUDIO_MANIFEST + "data_file 'HANDLING_FILE' 'data/handlnig.meta'\n"
        msgs = no_match(self.run_check(manifest, self.GOOD_FILES + ['data/handling.meta']))
        self.assertEqual(len(msgs), 1)
        self.assertIn('handlnig.meta', msgs[0])


class CommandLine(unittest.TestCase):
    def test_prints_chinese_on_a_cp1252_console(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = os.path.join(tmp, 'testcar')
            make_resource(res, AUDIO_MANIFEST, CheckAudioResource.GOOD_FILES)
            env = dict(os.environ, PYTHONIOENCODING='cp1252')
            for extra in ([], ['--json']):
                with self.subTest(args=extra):
                    proc = subprocess.run(
                        [sys.executable, os.path.join(HERE, 'check_vehicle_resource.py'), res] + extra,
                        capture_output=True, env=env)
                    self.assertNotIn(b'UnicodeEncodeError', proc.stderr)
                    self.assertIn('扫描了' if not extra else '"resources"', proc.stdout.decode('utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
