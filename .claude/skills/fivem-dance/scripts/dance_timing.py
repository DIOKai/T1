#!/usr/bin/env python3
"""Beat timing for GTA V / FiveM dance loops (Python standard library only).

GTA clips run at 30 fps. A dance loop stays on the beat only when its length is
a whole number of beats AND a whole number of frames; otherwise every repeat
drifts a little further off the music.

    frames per beat = fps * 60 / BPM          (30 fps: 1800 / BPM)

Examples
    py -3 dance_timing.py 128                    # shortest exact loop + table
    py -3 dance_timing.py 128 --beats 16         # a two-8-count loop
    py -3 dance_timing.py 98 --bars 4            # 4 bars of 4/4 = 16 beats
    py -3 dance_timing.py 128 --beats 16 --markers-json beats.json
    py -3 dance_timing.py 128 --check 224        # does a 224-frame clip loop on the beat?

FRAMES for --check is the loop period: last frame - first frame when the last
frame repeats the first pose (Sollumz Duration x fps). Local arithmetic only:
reads nothing, writes only the JSON file you name.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction

DEFAULT_FPS = 30
MAX_BPM = 400
PRACTICAL_MAX_BEATS = 64  # longer than ~8 eight-counts is not a sensible emote loop


def parse_positive(text: str, what: str) -> Fraction:
    """Parse '128', '127.5' or '256/2' exactly; reject zero, negatives, nan, inf."""
    try:
        value = Fraction(str(text).strip())
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"{what} must be a number, got {text!r}") from None
    if value <= 0:
        raise ValueError(f"{what} must be greater than 0, got {text!r}")
    return value


def frames_per_beat(bpm, fps=DEFAULT_FPS) -> Fraction:
    bpm = parse_positive(bpm, "BPM")
    fps = parse_positive(fps, "fps")
    if bpm > MAX_BPM:
        raise ValueError(f"BPM {float(bpm):g} is above {MAX_BPM}; halve it (count every other beat)")
    return fps * 60 / bpm


def shortest_loop(bpm, fps=DEFAULT_FPS) -> tuple[int, int]:
    """Smallest (beats, frames) with both whole numbers."""
    fpb = frames_per_beat(bpm, fps)
    beats = fpb.denominator
    frames = fpb * beats
    if frames.denominator != 1:  # only possible with a fractional fps
        lcm = frames.denominator
        beats *= lcm
        frames *= lcm
    return int(beats), int(frames)


def round_half_up(x: Fraction) -> int:
    return math.floor(x + Fraction(1, 2))


def beat_table(bpm, beats: int, fps=DEFAULT_FPS, start: int = 0, beats_per_count: int = 8):
    """Rows for beat 0..beats (the last row is the loop end = next loop's first beat)."""
    if beats < 1:
        raise ValueError("beats must be at least 1")
    fpb = frames_per_beat(bpm, fps)
    rows = []
    for i in range(beats + 1):
        exact = start + fpb * i
        rows.append({
            "beat": i,
            "count": f"{i // beats_per_count + 1}-{i % beats_per_count + 1}",  # eight-count number - count
            "exact_frame": float(exact),
            "frame": round_half_up(exact),
            "time_s": float(exact / parse_positive(fps, "fps")),
        })
    return rows


def check_loop(frames, bpm, fps=DEFAULT_FPS) -> dict:
    """Is a loop period of `frames` frames a whole number of beats?"""
    frames_f = parse_positive(frames, "FRAMES")
    if frames_f.denominator != 1:
        raise ValueError("FRAMES must be a whole number of frames")
    fpb = frames_per_beat(bpm, fps)
    fps_f = parse_positive(fps, "fps")
    beats_exact = frames_f / fpb
    nearest = max(1, round_half_up(beats_exact))
    drift_frames = frames_f - fpb * nearest  # + = clip longer than the beats
    loop_beats, loop_frames = shortest_loop(bpm, fps)
    lower = (int(frames_f) // loop_frames) * loop_frames
    suggestions = sorted({x for x in (lower, lower + loop_frames) if x > 0})
    result = {
        "frames": int(frames_f),
        "beats_exact": float(beats_exact),
        "on_beat": beats_exact.denominator == 1,
        "nearest_beats": nearest,
        "drift_frames_per_loop": float(drift_frames),
        "drift_ms_per_loop": float(drift_frames / fps_f * 1000),
        "loops_until_half_beat_off": None,
        "whole_eight_counts": beats_exact.denominator == 1 and beats_exact.numerator % 8 == 0,
        "valid_lengths_nearby": [{"frames": s, "beats": int(s / fpb)} for s in suggestions],
    }
    if drift_frames != 0:
        result["loops_until_half_beat_off"] = math.ceil((fpb / 2) / abs(drift_frames))
    return result


def nearby_bpms(beats: int, bpm, fps=DEFAULT_FPS):
    """Tempos close to `bpm` at which `beats` beats are exactly a whole number of frames."""
    fpb = frames_per_beat(bpm, fps)
    fps_f = parse_positive(fps, "fps")
    exact = fpb * beats
    out = []
    for frames in sorted({math.floor(exact), math.ceil(exact)}):
        if frames > 0:
            out.append({"frames": frames, "bpm": float(fps_f * 60 * beats / frames)})
    return out


def default_beats(loop_beats: int) -> int:
    """One or two 8-counts when they land on whole frames, else the shortest exact loop."""
    for b in (8, 16):
        if b % loop_beats == 0:
            return b
    return loop_beats if loop_beats <= PRACTICAL_MAX_BEATS else 16


def fmt(x: float) -> str:
    return f"{x:.4f}".rstrip("0").rstrip(".")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="BPM -> frames for GTA/FiveM dance loops (30 fps by default).")
    p.add_argument("bpm", help="tempo in beats per minute, e.g. 128 or 127.5")
    p.add_argument("--fps", default=str(DEFAULT_FPS), help="frame rate (GTA clips: 30)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--beats", type=int, help="loop length in beats (8 = one 8-count)")
    g.add_argument("--bars", type=int, help="loop length in bars (see --beats-per-bar)")
    p.add_argument("--beats-per-bar", type=int, default=4, help="time signature top number (default 4)")
    p.add_argument("--start", type=int, default=0, help="first frame of the loop (default 0)")
    p.add_argument("--markers-json", metavar="PATH", help="write beat marker frames as JSON")
    p.add_argument("--check", metavar="FRAMES", help="check whether a loop of FRAMES frames is on the beat")
    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        fpb = frames_per_beat(args.bpm, args.fps)
        bpm = float(parse_positive(args.bpm, "BPM"))
        fps = float(parse_positive(args.fps, "fps"))
        if args.beats is not None and args.beats < 1:
            raise ValueError("--beats must be at least 1")
        if args.bars is not None and (args.bars < 1 or args.beats_per_bar < 1):
            raise ValueError("--bars and --beats-per-bar must be at least 1")
        if args.start < 0:
            raise ValueError("--start must be 0 or more")
        loop_beats, loop_frames = shortest_loop(args.bpm, args.fps)
    except ValueError as e:
        parser.error(str(e))
        return 2

    print(f"{fmt(bpm)} BPM at {fmt(fps)} fps: {fmt(float(fpb))} frames per beat, "
          f"{fmt(float(fpb * 8))} frames per 8-count, {fmt(60 / bpm)} s per beat")
    print(f"Shortest loop on the beat: {loop_beats} beat(s) = {loop_frames} frames "
          f"({fmt(loop_frames / fps)} s)")
    eight = math.lcm(loop_beats, 8)
    if eight <= PRACTICAL_MAX_BEATS:
        print(f"Shortest loop of whole 8-counts: {eight} beats = {int(fpb * eight)} frames "
              f"({eight // 8} x 8-count)")
    if loop_beats > PRACTICAL_MAX_BEATS:
        print(f"WARNING: no practical exact loop at this tempo (> {PRACTICAL_MAX_BEATS} beats).")
        for b in (8, 16, 32):
            alts = ", ".join(f"{a['frames']} f = {fmt(a['bpm'])} BPM" for a in nearby_bpms(b, args.bpm, args.fps))
            print(f"  {b} beats exact at: {alts}")
        print("  Pick one of these lengths and accept the small drift, or animate to the nearby tempo.")

    if args.check is not None:
        try:
            r = check_loop(args.check, args.bpm, args.fps)
        except ValueError as e:
            parser.error(str(e))
            return 2
        print()
        if r["on_beat"]:
            extra = " (whole 8-counts)" if r["whole_eight_counts"] else " (not a whole 8-count; fine if intended)"
            print(f"CHECK {r['frames']} frames: OK, exactly {int(r['beats_exact'])} beats{extra}.")
        else:
            print(f"CHECK {r['frames']} frames: OFF BEAT. {fmt(r['beats_exact'])} beats; nearest "
                  f"{r['nearest_beats']} beats -> clip is {fmt(abs(r['drift_frames_per_loop']))} f "
                  f"{'too long' if r['drift_frames_per_loop'] > 0 else 'too short'} "
                  f"({fmt(abs(r['drift_ms_per_loop']))} ms) per loop, half a beat off after "
                  f"{r['loops_until_half_beat_off']} loop(s).")
            near = ", ".join(f"{s['frames']} f ({s['beats']} beats)" for s in r["valid_lengths_nearby"])
            print(f"  Valid loop lengths nearby: {near}")
        return 0 if r["on_beat"] else 1

    if args.beats is not None:
        beats = args.beats
    elif args.bars is not None:
        beats = args.bars * args.beats_per_bar
    else:
        beats = default_beats(loop_beats)

    total = fpb * beats
    end = args.start + round_half_up(total)
    print()
    if total.denominator == 1:
        print(f"Loop of {beats} beats = {int(total)} frames: frame {args.start} -> {end} "
              f"(last frame = first pose). On the beat.")
    else:
        print(f"Loop of {beats} beats = {fmt(float(total))} frames - NOT a whole number of frames; "
              f"rounded to {end - args.start} it drifts {fmt(float(round_half_up(total) - total))} f per loop. "
              + (f"Use a multiple of {loop_beats} beats instead." if loop_beats <= PRACTICAL_MAX_BEATS
                 else "Pick a length from the WARNING list above."))
    rows = beat_table(args.bpm, beats, args.fps, args.start)
    print(f"{'beat':>4}  {'count':>5}  {'frame':>5}  {'exact':>9}  {'time s':>7}")
    for r in rows:
        tag = "  <- loop end / next loop beat 1" if r["beat"] == beats else ""
        print(f"{r['beat']:>4}  {r['count']:>5}  {r['frame']:>5}  {fmt(r['exact_frame']):>9}  "
              f"{fmt(r['time_s']):>7}{tag}")

    if args.markers_json:
        data = {
            "bpm": bpm, "fps": fps, "beats": beats, "start_frame": args.start,
            "end_frame": end, "frames_per_beat": float(fpb),
            "loop_on_beat": total.denominator == 1,
            "markers": [{"name": f"b{r['beat'] + 1:02d}_{r['count']}", "frame": r["frame"]}
                        for r in rows[:-1]],
        }
        try:
            with open(args.markers_json, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
        except OSError as e:
            print(f"error: cannot write {args.markers_json}: {e}", file=sys.stderr)
            return 2
        print(f"\nWrote {len(data['markers'])} markers to {args.markers_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
