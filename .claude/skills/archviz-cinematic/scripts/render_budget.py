#!/usr/bin/env python3
"""Render-time and disk budget for an animation (stdlib only, read-only, writes nothing).

Measure first: render 3 representative frames at FINAL resolution and settings (brightest,
most complex, most glass) and pass their times with --spf; the slowest one is used.

Examples:
    python render_budget.py --seconds 40 --fps 24 --spf 95 120 140 --width 1920 --height 1080
    python render_budget.py --frames 960 --spf 180 --machines 2 --format png16 --deadline-hours 36
    python render_budget.py --seconds 30 --fps 24 --spf 60 --format exr-multilayer --passes 8 --json

Disk sizes are ESTIMATES (bytes per pixel x typical compression); real files vary with
content, noise and codec. Time trade-offs assume render time scales with pixel count and
with sample count - a rough rule, check with one more test frame.
"""
import argparse
import json
import math
import sys

# Bytes per pixel before compression, and a rough lossless compression ratio (estimate).
FORMATS = {
    "png8": {"bpp": 3, "ratio": 0.45, "label": "PNG 8-bit RGB"},
    "png8a": {"bpp": 4, "ratio": 0.45, "label": "PNG 8-bit RGBA"},
    "png16": {"bpp": 6, "ratio": 0.6, "label": "PNG 16-bit RGB"},
    "exr": {"bpp": 8, "ratio": 0.55, "label": "OpenEXR half RGBA, ZIP"},
    "exr-multilayer": {"bpp": 8, "ratio": 0.55, "label": "OpenEXR MultiLayer half, ZIP (per pass)"},
}


def human_time(seconds):
    seconds = max(0, int(round(seconds)))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d:
        parts.append("%dd" % d)
    if h or d:
        parts.append("%dh" % h)
    parts.append("%02dm" % m if (h or d) else "%dm %02ds" % (m, s))
    return " ".join(parts)


def human_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return "%.1f %s" % (n, unit) if unit != "B" else "%d B" % n
        n /= 1024.0
    return "%.1f TB" % n


def frame_bytes(width, height, fmt, passes=1):
    spec = FORMATS[fmt]
    layers = max(1, passes) if fmt == "exr-multilayer" else 1
    return width * height * spec["bpp"] * spec["ratio"] * layers


def budget(frames, spf, machines=1, margin=1.2, width=1920, height=1080, fmt="png16",
           passes=1, deadline_hours=None, fps=24):
    worst = max(spf)
    total_s = frames * worst * margin / max(1, machines)
    per_frame = frame_bytes(width, height, fmt, passes)
    result = {
        "frames": frames,
        "fps": fps,
        "film_seconds": round(frames / fps, 2),
        "seconds_per_frame_used": worst,
        "seconds_per_frame_measured": list(spf),
        "machines": machines,
        "margin": margin,
        "total_seconds": round(total_s),
        "total_human": human_time(total_s),
        "resolution": [width, height],
        "format": FORMATS[fmt]["label"],
        "passes": passes if fmt == "exr-multilayer" else 1,
        "disk_per_frame_estimate": round(per_frame),
        "disk_total_estimate": round(per_frame * frames),
        "disk_per_frame_human": human_bytes(per_frame),
        "disk_total_human": human_bytes(per_frame * frames),
        "suggestions": [],
    }
    if spf and max(spf) > 2.5 * min(spf):
        result["suggestions"].append(
            "Frame times vary %.1fx: the slow shot drives the budget; consider different "
            "settings per shot (separate scenes or files)." % (max(spf) / min(spf)))
    if worst > 600:
        result["suggestions"].append(
            "Over 10 min per frame: check the Render Time pass (5.0+) for the slow area, add "
            "light portals for interiors, enable Persistent Data for animations.")

    if deadline_hours:
        target_s = deadline_hours * 3600.0
        result["deadline_seconds"] = round(target_s)
        factor = total_s / target_s
        result["over_budget_factor"] = round(factor, 2)
        if factor <= 1.0:
            result["suggestions"].append(
                "Fits the deadline with %.0f%% headroom. Spare time can go to more samples "
                "(less flicker)." % ((1 - factor) * 100))
        else:
            need = 1.0 / factor  # fraction of current cost allowed
            res_pct = math.sqrt(need) * 100
            result["suggestions"].append(
                "Over budget by %.2fx. Options (each alone, rough):" % factor)
            if res_pct >= 50:
                result["suggestions"].append(
                    "- render at %d%% resolution (%dx%d), upscale later; time ~ pixel count"
                    % (int(res_pct), int(width * res_pct / 100), int(height * res_pct / 100)))
            else:
                result["suggestions"].append(
                    "- resolution alone would need %d%%: too low; combine with other options"
                    % int(res_pct))
            result["suggestions"].append(
                "- cut samples / raise Noise Threshold to ~%d%% of the current cost "
                "(more noise -> more flicker: test 3-5 s first)" % int(need * 100))
            m_needed = math.ceil(machines * factor)
            result["suggestions"].append(
                "- use %d machines (Overwrite off + Placeholders on, same output folder)"
                % m_needed)
            result["suggestions"].append(
                "- shorten: %d frames fit (%.1f s at %d fps)"
                % (int(frames * need), frames * need / fps, fps))
            result["suggestions"].append(
                "- EEVEE for the less critical shots (exteriors); keep Cycles for glass-heavy interiors")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--frames", type=int, help="total frame count")
    g.add_argument("--seconds", type=float, help="film length in seconds (with --fps)")
    p.add_argument("--fps", type=float, default=24.0)
    p.add_argument("--spf", type=float, nargs="+", required=True,
                   help="measured seconds per frame from test renders (slowest is used)")
    p.add_argument("--machines", type=int, default=1)
    p.add_argument("--margin", type=float, default=1.2, help="safety factor (default 1.2)")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--format", choices=sorted(FORMATS), default="png16")
    p.add_argument("--passes", type=int, default=1, help="render passes in a multilayer EXR")
    p.add_argument("--deadline-hours", type=float)
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    a = p.parse_args(argv)

    if any(s <= 0 for s in a.spf) or a.fps <= 0 or a.machines < 1:
        p.error("--spf and --fps must be > 0, --machines >= 1")
    frames = a.frames if a.frames else int(round(a.seconds * a.fps))
    if frames < 1:
        p.error("need at least one frame")
    r = budget(frames, a.spf, a.machines, a.margin, a.width, a.height, a.format, a.passes,
               a.deadline_hours, a.fps)
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0
    print("Frames: %d (%.1f s at %g fps)" % (r["frames"], r["film_seconds"], r["fps"]))
    print("Seconds/frame used: %g (slowest of %s) x margin %.2f / %d machine(s)"
          % (r["seconds_per_frame_used"], r["seconds_per_frame_measured"], r["margin"], r["machines"]))
    print("Total render time: %s" % r["total_human"])
    print("Disk (estimate): %s per frame, %s total  [%s, %dx%d%s]"
          % (r["disk_per_frame_human"], r["disk_total_human"], r["format"], a.width, a.height,
             ", %d passes" % r["passes"] if a.format == "exr-multilayer" else ""))
    if "deadline_seconds" in r:
        print("Deadline: %s -> load %.2fx" % (human_time(r["deadline_seconds"]), r["over_budget_factor"]))
    for s in r["suggestions"]:
        print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
