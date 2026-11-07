#!/usr/bin/env python3
"""Re-voice exported engine-sound WAVs without breaking GTA's granular grain tables.

Reads the mono 16-bit PCM WAVs that `sound_pack.ps1 dump -Wav` exported, applies EQ / saturation / gain and writes
WAVs with the SAME sample rate and the SAME number of samples (grain offsets are sample positions, so any trim,
time-stretch or resample would break the engine). Standard library only. Originals are never overwritten.

    python revoice_wav.py IN_DIR OUT_DIR --only "exhaust_*" --low-shelf 110:3 --peak 450:1.5:1.0 --drive 0.3 --gain 1
    python revoice_wav.py IN_DIR OUT_DIR --preset deeper        # see PRESETS

Options (repeatable where it makes sense):
  --only GLOB         process only matching file names (default all *.wav); unmatched files are not written
  --low-shelf F:DB    RBJ low shelf at F Hz            --high-shelf F:DB   high shelf
  --peak F:DB[:Q]     peaking EQ (Q default 1.0)       --highpass F / --lowpass F (12 dB/oct)
  --drive X           tanh saturation 0..1 (rasp); output is level-matched to the input RMS
  --gain DB           overall gain
  --ceiling DB        peak limit in dBFS (default -0.3); if the result would clip, gain is lowered and reported
The IIR filters are minimum-phase (small, frequency-dependent delay) — fine for grain timing; do not use long
linear-phase FIR filters on granular streams.
"""
import argparse
import fnmatch
import math
import os
import struct
import sys
import wave

PRESETS = {
    'deeper': ['--low-shelf', '110:3', '--peak', '450:1.5:1.0', '--high-shelf', '6000:-1.5'],
    'raspier': ['--peak', '2500:2:1.2', '--drive', '0.35'],
    'straight-pipe': ['--low-shelf', '90:2', '--peak', '1800:2.5:0.9', '--drive', '0.25', '--gain', '2'],
    'muffled': ['--high-shelf', '2500:-6', '--lowpass', '7000'],
}


def biquad(kind, f, fs, db=0.0, q=0.7071):
    a = 10 ** (db / 40.0)
    w = 2 * math.pi * f / fs
    cw, sw = math.cos(w), math.sin(w)
    al = sw / (2 * q)
    if kind == 'peak':
        b = (1 + al * a, -2 * cw, 1 - al * a); den = (1 + al / a, -2 * cw, 1 - al / a)
    elif kind in ('low', 'high'):
        s = 2 * math.sqrt(a) * (sw / (2 * 0.7071))
        if kind == 'low':
            b = (a * ((a + 1) - (a - 1) * cw + s), 2 * a * ((a - 1) - (a + 1) * cw), a * ((a + 1) - (a - 1) * cw - s))
            den = ((a + 1) + (a - 1) * cw + s, -2 * ((a - 1) + (a + 1) * cw), (a + 1) + (a - 1) * cw - s)
        else:
            b = (a * ((a + 1) + (a - 1) * cw + s), -2 * a * ((a - 1) + (a + 1) * cw), a * ((a + 1) + (a - 1) * cw - s))
            den = ((a + 1) - (a - 1) * cw + s, 2 * ((a - 1) - (a + 1) * cw), (a + 1) - (a - 1) * cw - s)
    elif kind == 'hp':
        b = ((1 + cw) / 2, -(1 + cw), (1 + cw) / 2); den = (1 + al, -2 * cw, 1 - al)
    elif kind == 'lp':
        b = ((1 - cw) / 2, 1 - cw, (1 - cw) / 2); den = (1 + al, -2 * cw, 1 - al)
    else:
        raise ValueError(kind)
    a0 = den[0]
    return [x / a0 for x in b], [den[1] / a0, den[2] / a0]


def run_filter(x, coef):
    (b0, b1, b2), (a1, a2) = coef
    y = [0.0] * len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        o = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, o
        y[i] = o
    return y


def rms(x):
    return math.sqrt(sum(v * v for v in x) / max(1, len(x)))


def read_wav(path):
    with wave.open(path, 'rb') as w:
        ch, sw, fs, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        if ch != 1 or sw != 2:
            raise SystemExit(f'{path}: need mono 16-bit PCM (got {ch} ch, {8 * sw} bit) — CodeWalker only imports that')
        raw = w.readframes(n)
    return fs, [s / 32768.0 for s in struct.unpack(f'<{n}h', raw)]


def write_wav(path, fs, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(fs)
        w.writeframes(struct.pack(f'<{len(x)}h', *(max(-32768, min(32767, int(round(v * 32767)))) for v in x)))


def process(x, fs, args):
    y = list(x)
    for spec in args.low_shelf:
        f, db = map(float, spec.split(':')); y = run_filter(y, biquad('low', f, fs, db))
    for spec in args.high_shelf:
        f, db = map(float, spec.split(':')); y = run_filter(y, biquad('high', f, fs, db))
    for spec in args.peak:
        p = [float(v) for v in spec.split(':')]
        y = run_filter(y, biquad('peak', p[0], fs, p[1], p[2] if len(p) > 2 else 1.0))
    for f in args.highpass:
        y = run_filter(y, biquad('hp', float(f), fs))
    for f in args.lowpass:
        y = run_filter(y, biquad('lp', float(f), fs))
    if args.drive > 0:
        before = rms(y) or 1e-9
        k = 1 + 9 * args.drive
        y = [math.tanh(k * v) / math.tanh(k) for v in y]
        m = before / (rms(y) or 1e-9)          # computed once: level-match to the pre-saturation RMS
        y = [v * m for v in y]
    g = 10 ** (args.gain / 20.0)
    y = [v * g for v in y]
    peak = max((abs(v) for v in y), default=0.0)
    ceil = 10 ** (args.ceiling / 20.0)
    reduced = 0.0
    if peak > ceil:
        reduced = 20 * math.log10(peak / ceil)
        y = [v * ceil / peak for v in y]
    return y, peak, reduced


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('in_dir'); ap.add_argument('out_dir')
    ap.add_argument('--preset', choices=sorted(PRESETS))
    ap.add_argument('--only', default='*.wav')
    ap.add_argument('--low-shelf', action='append', default=[])
    ap.add_argument('--high-shelf', action='append', default=[])
    ap.add_argument('--peak', action='append', default=[])
    ap.add_argument('--highpass', action='append', default=[])
    ap.add_argument('--lowpass', action='append', default=[])
    ap.add_argument('--drive', type=float, default=0.0)
    ap.add_argument('--gain', type=float, default=0.0)
    ap.add_argument('--ceiling', type=float, default=-0.3)
    argv = sys.argv[1:]
    pre = ap.parse_known_args(argv)[0]
    if pre.preset:
        argv = argv + PRESETS[pre.preset]
    args = ap.parse_args(argv)
    if os.path.abspath(args.in_dir) == os.path.abspath(args.out_dir):
        raise SystemExit('OUT_DIR must differ from IN_DIR (originals are never overwritten)')
    os.makedirs(args.out_dir, exist_ok=True)
    files = sorted(f for f in os.listdir(args.in_dir) if f.lower().endswith('.wav') and fnmatch.fnmatch(f.lower(), args.only.lower()))
    if not files:
        raise SystemExit(f'no WAV in {args.in_dir} matches {args.only}')
    for f in files:
        fs, x = read_wav(os.path.join(args.in_dir, f))
        y, peak, red = process(x, fs, args)
        assert len(y) == len(x)
        write_wav(os.path.join(args.out_dir, f), fs, y)
        note = f', peak would be {20 * math.log10(peak):+.1f} dBFS -> lowered {red:.1f} dB' if red else ''
        print(f'{f}: {fs} Hz, {len(x)} samples kept, RMS {20 * math.log10(rms(x) or 1e-9):.1f} -> {20 * math.log10(rms(y) or 1e-9):.1f} dBFS{note}')


if __name__ == '__main__':
    main()
