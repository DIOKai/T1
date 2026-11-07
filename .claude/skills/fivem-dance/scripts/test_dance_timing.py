"""Tests for dance_timing.py. Run: py -3 -I test_dance_timing.py"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dance_timing as dt  # noqa: E402


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = dt.main(list(argv))
        except SystemExit as e:  # argparse errors
            code = e.code
    return code, out.getvalue(), err.getvalue()


class FramesPerBeat(unittest.TestCase):
    def test_120_bpm_is_15_frames(self):
        self.assertEqual(dt.frames_per_beat(120), 15)

    def test_100_bpm_is_18_frames(self):
        self.assertEqual(dt.frames_per_beat(100), 18)

    def test_128_bpm_is_exact_fraction(self):
        self.assertEqual(dt.frames_per_beat(128), Fraction(225, 16))

    def test_fps_60(self):
        self.assertEqual(dt.frames_per_beat(120, 60), 30)

    def test_decimal_bpm(self):
        self.assertEqual(dt.frames_per_beat("112.5"), 16)


class ShortestLoop(unittest.TestCase):
    def test_128_bpm_16_beats_225_frames(self):
        self.assertEqual(dt.shortest_loop(128), (16, 225))

    def test_whole_frame_tempos_loop_in_one_beat(self):
        for bpm, frames in ((90, 20), (100, 18), (120, 15), (150, 12)):
            self.assertEqual(dt.shortest_loop(bpm), (1, frames), bpm)

    def test_notes_table(self):
        # values from the research table (1800 / BPM)
        expected = {105: (7, 120), 110: (11, 180), 125: (5, 72), 130: (13, 180),
                    140: (7, 90), 160: (4, 45)}
        for bpm, pair in expected.items():
            self.assertEqual(dt.shortest_loop(bpm), pair, bpm)

    def test_odd_prime_bpm_is_impractical(self):
        beats, frames = dt.shortest_loop(127)
        self.assertEqual((beats, frames), (127, 1800))
        self.assertGreater(beats, dt.PRACTICAL_MAX_BEATS)

    def test_odd_bpm_97(self):
        self.assertEqual(dt.shortest_loop(97), (97, 1800))

    def test_fractional_fps_still_whole_frames(self):
        beats, frames = dt.shortest_loop(120, "29.97")
        self.assertEqual(Fraction(frames), dt.frames_per_beat(120, "29.97") * beats)


class BeatTable(unittest.TestCase):
    def test_128_markers_alternate_14_and_15(self):
        rows = dt.beat_table(128, 16)
        frames = [r["frame"] for r in rows]
        self.assertEqual(frames[0], 0)
        self.assertEqual(frames[-1], 225)
        gaps = {b - a for a, b in zip(frames, frames[1:])}
        self.assertEqual(gaps, {14, 15})

    def test_counts_and_start_offset(self):
        rows = dt.beat_table(120, 8, start=10)
        self.assertEqual(rows[0]["count"], "1-1")
        self.assertEqual(rows[7]["count"], "1-8")
        self.assertEqual(rows[8]["count"], "2-1")
        self.assertEqual(rows[8]["frame"], 130)

    def test_zero_beats_rejected(self):
        with self.assertRaises(ValueError):
            dt.beat_table(120, 0)


class CheckLoop(unittest.TestCase):
    def test_225_frames_on_beat_at_128(self):
        r = dt.check_loop(225, 128)
        self.assertTrue(r["on_beat"])
        self.assertEqual(r["beats_exact"], 16)
        self.assertTrue(r["whole_eight_counts"])
        self.assertIsNone(r["loops_until_half_beat_off"])

    def test_224_frames_drifts_at_128(self):
        r = dt.check_loop(224, 128)
        self.assertFalse(r["on_beat"])
        self.assertEqual(r["nearest_beats"], 16)
        self.assertEqual(r["drift_frames_per_loop"], -1)
        self.assertEqual(r["loops_until_half_beat_off"], 8)
        self.assertIn(225, [s["frames"] for s in r["valid_lengths_nearby"]])

    def test_on_beat_but_not_eight_count(self):
        r = dt.check_loop(90, 120)  # 6 beats
        self.assertTrue(r["on_beat"])
        self.assertFalse(r["whole_eight_counts"])

    def test_fractional_frames_rejected(self):
        with self.assertRaises(ValueError):
            dt.check_loop("224.5", 128)


class BadInput(unittest.TestCase):
    def test_bad_bpm_values(self):
        for bad in ("0", "-120", "abc", "nan", "inf", "", "1/0", "1000"):
            with self.assertRaises(ValueError, msg=bad):
                dt.frames_per_beat(bad)

    def test_bad_fps(self):
        with self.assertRaises(ValueError):
            dt.frames_per_beat(120, 0)

    def test_cli_rejects_bad_input_with_exit_2(self):
        for argv in (["abc"], ["0"], ["128", "--beats", "0"], ["128", "--fps", "-30"],
                     ["128", "--check", "0"], ["128", "--start", "-1"],
                     ["128", "--beats", "8", "--bars", "2"]):
            code, _, err = run_cli(*argv)
            self.assertEqual(code, 2, argv)
            self.assertIn("error", err.lower(), argv)


class Cli(unittest.TestCase):
    def test_default_128(self):
        code, out, _ = run_cli("128")
        self.assertEqual(code, 0)
        self.assertIn("16 beat(s) = 225 frames", out)
        self.assertIn("On the beat", out)

    def test_bars(self):
        code, out, _ = run_cli("100", "--bars", "2")
        self.assertEqual(code, 0)
        self.assertIn("Loop of 8 beats = 144 frames", out)

    def test_not_whole_frames_warns(self):
        code, out, _ = run_cli("128", "--beats", "8")
        self.assertEqual(code, 0)
        self.assertIn("NOT a whole number of frames", out)

    def test_odd_bpm_warning_and_suggestions(self):
        code, out, _ = run_cli("127")
        self.assertEqual(code, 0)
        self.assertIn("WARNING", out)
        self.assertIn("16 beats exact at", out)

    def test_check_exit_codes(self):
        self.assertEqual(run_cli("128", "--check", "225")[0], 0)
        code, out, _ = run_cli("128", "--check", "224")
        self.assertEqual(code, 1)
        self.assertIn("OFF BEAT", out)

    def test_markers_json(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "beats.json")
            code, out, _ = run_cli("128", "--beats", "16", "--markers-json", path)
            self.assertEqual(code, 0)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        self.assertEqual(data["end_frame"], 225)
        self.assertTrue(data["loop_on_beat"])
        self.assertEqual(len(data["markers"]), 16)
        self.assertEqual(data["markers"][0], {"name": "b01_1-1", "frame": 0})
        self.assertEqual(data["markers"][8]["name"], "b09_2-1")


if __name__ == "__main__":
    unittest.main(verbosity=1)
