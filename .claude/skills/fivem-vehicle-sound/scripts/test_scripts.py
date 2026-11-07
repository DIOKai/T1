"""Tests for check_sound_resource.py and revoice_wav.py (standard library only).

    py -3 -I .claude/skills/fivem-vehicle-sound/scripts/test_scripts.py
"""
import math
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_sound_resource as chk  # noqa: E402

GOOD_MANIFEST = """fx_version 'cerulean'
game 'gta5'
files { 'audioconfig/*.dat151.rel', 'audioconfig/*.dat54.rel', 'sfx/**/*.awc' }
data_file 'AUDIO_GAMEDATA' 'audioconfig/{n}_game.dat'
data_file 'AUDIO_SOUNDDATA' 'audioconfig/{n}_sounds.dat'
data_file 'AUDIO_WAVEPACK' 'sfx/dlc_{n}'
"""


def write(root, rel, data):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'wb') as fh:
        fh.write(data if isinstance(data, bytes) else data.encode())


def make_pack(root, n, manifest=GOOD_MANIFEST, awc_magic=b'ADAT', credits=True):
    write(root, f'{n}/fxmanifest.lua', manifest.replace('{n}', n))
    write(root, f'{n}/audioconfig/{n}_game.dat151.rel', b'\x00' * 8)
    write(root, f'{n}/audioconfig/{n}_sounds.dat54.rel', b'\x00' * 8)
    write(root, f'{n}/sfx/dlc_{n}/{n}.awc', awc_magic + b'\x00' * 8)
    write(root, f'{n}/sfx/dlc_{n}/{n}_npc.awc', awc_magic + b'\x00' * 8)
    if credits:
        write(root, f'{n}/CREDITS.txt', 'x')


def car_meta(model, sound):
    return f'<CVehicleModelInfo__InitDataList><InitDatas><Item><modelName>{model}</modelName>' \
           f'<audioNameHash>{sound}</audioNameHash></Item></InitDatas></CVehicleModelInfo__InitDataList>'


def codes(findings, level=None):
    return {f['code'] for f in findings if level is None or f['level'] == level}


class CheckSound(unittest.TestCase):
    def test_good_pack_used_by_a_car(self):
        with tempfile.TemporaryDirectory() as d:
            make_pack(d, 'mysound')
            write(d, 'mycar/data/vehicles.meta', car_meta('mycar', 'mysound'))
            f = chk.check([d])
        self.assertFalse(codes(f, 'error') | codes(f, 'warn'), f)
        self.assertIn('AUDIO_HASH_OK', codes(f))

    def test_glob_missing_target_and_unmounted(self):
        bad = GOOD_MANIFEST.replace("'audioconfig/{n}_sounds.dat'", "'audioconfig/*.dat'") + \
            "data_file 'AUDIO_SYNTHDATA' 'audioconfig/{n}_amp.dat'\n"
        with tempfile.TemporaryDirectory() as d:
            make_pack(d, 'snd', manifest=bad)
            f = chk.check([d])
        self.assertIn('AUDIO_DATAFILE_GLOB', codes(f, 'error'))
        self.assertIn('DATAFILE_TARGET_MISSING', codes(f, 'error'))     # _amp.dat10.rel missing
        self.assertIn('REL_NOT_MOUNTED', codes(f, 'warn'))              # sounds.dat54 listed, not mounted

    def test_not_in_files_and_bad_magic_and_duplicates(self):
        man = GOOD_MANIFEST.replace("'sfx/**/*.awc'", "'sfx/dlc_{n}/{n}.awc'")
        with tempfile.TemporaryDirectory() as d:
            make_pack(d, 'aa', manifest=man, awc_magic=b'XXXX', credits=False)
            make_pack(d, 'bb')
            write(d, 'bb/sfx/dlc_bb/aa.awc', b'ADAT' + b'\x00' * 4)          # same awc name as pack aa
            f = chk.check([d])
        self.assertIn('NOT_IN_FILES', codes(f, 'error'))       # aa_npc.awc not listed
        self.assertIn('AWC_NOT_PLAIN', codes(f, 'warn'))
        self.assertIn('AWC_NAME_DUPLICATE', codes(f, 'error'))
        self.assertIn('NO_CREDITS', codes(f, 'info'))

    def test_pack_unused_and_prefix8(self):
        with tempfile.TemporaryDirectory() as d:
            make_pack(d, 'dominatorgrt')
            make_pack(d, 'dominatorbs')
            write(d, 'car/data/vehicles.meta', car_meta('car', 'dominatorgrt'))
            f = chk.check([d])
        self.assertIn('PACK_UNUSED', codes(f, 'warn'))          # dominatorbs used by no car
        self.assertIn('WAVEPACK_PREFIX8', codes(f, 'info'))

    def test_rel_suffix_convention(self):
        man = GOOD_MANIFEST.replace("'audioconfig/{n}_game.dat'", "'audioconfig/{n}_game.dat151.rel'")
        with tempfile.TemporaryDirectory() as d:
            make_pack(d, 's', manifest=man)
            f = chk.check([d])
        self.assertIn('DATAFILE_REL_SUFFIX', codes(f, 'warn'))


class Revoice(unittest.TestCase):
    def make_wav(self, path, n=30000, fs=30000, amp=0.5, ch=1):
        with wave.open(path, 'wb') as w:
            w.setnchannels(ch); w.setsampwidth(2); w.setframerate(fs)
            data = [int(amp * 32767 * math.sin(2 * math.pi * 120 * i / fs)) for i in range(n)]
            w.writeframes(struct.pack(f'<{n * ch}h', *[v for v in data for _ in range(ch)]))

    def run_tool(self, *args):
        return subprocess.run([sys.executable, '-I', os.path.join(HERE, 'revoice_wav.py'), *args],
                              capture_output=True, text=True, timeout=120)

    def test_keeps_rate_and_length_and_limits_peak(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = os.path.join(d, 'in'), os.path.join(d, 'out')
            os.makedirs(src)
            self.make_wav(os.path.join(src, 'exhaust_accel.wav'), n=45001, amp=0.9)
            self.make_wav(os.path.join(src, 'engine_accel.wav'))
            r = self.run_tool(src, out, '--only', 'exhaust_*', '--low-shelf', '110:6', '--drive', '0.4', '--gain', '3')
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(os.path.exists(os.path.join(out, 'engine_accel.wav')))   # --only respected
            with wave.open(os.path.join(out, 'exhaust_accel.wav')) as w:
                self.assertEqual((w.getframerate(), w.getnframes(), w.getnchannels()), (30000, 45001, 1))
                x = struct.unpack(f'<{w.getnframes()}h', w.readframes(w.getnframes()))
            self.assertLessEqual(max(abs(v) for v in x) / 32767, 10 ** (-0.3 / 20) + 1e-3)
            self.assertIn('lowered', r.stdout)

    def test_rejects_stereo_and_same_folder(self):
        with tempfile.TemporaryDirectory() as d:
            self.make_wav(os.path.join(d, 'a.wav'), ch=2)
            self.assertNotEqual(self.run_tool(d, os.path.join(d, 'o')).returncode, 0)
            self.assertNotEqual(self.run_tool(d, d).returncode, 0)

    def test_preset(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, 'in'); os.makedirs(src)
            self.make_wav(os.path.join(src, 'exhaust_idle.wav'), amp=0.3)
            r = self.run_tool(src, os.path.join(d, 'o'), '--preset', 'raspier')
            self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == '__main__':
    unittest.main()
