#!/usr/bin/env python3
"""Build (and with --run, execute) the ffmpeg command that turns an image sequence into a video.

Stdlib only. Without --run it only prints the command (dry run). It never overwrites an
existing output unless --force is given (passes -n to ffmpeg otherwise, as a second guard).

Examples:
    python encode_sequence.py renders/shot01/ --fps 24 --codec h264 --out shot01.mp4
    python encode_sequence.py "renders/shot01/img_%04d.png" --fps 24 --codec h265 --out shot01.mp4 --run
    python encode_sequence.py renders/shot01/ --fps 24 --codec prores --out shot01.mov --run --force

Defaults (ffmpeg wiki rules + common practice):
    h264   libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart   (.mp4)
    h265   libx265 -preset slow -crf 22 -pix_fmt yuv420p10le -tag:v hvc1        (.mp4, Apple-playable)
    prores prores_ks -profile:v 3 (422 HQ) -pix_fmt yuv422p10le                  (.mov, for editing)
Odd frame sizes are padded to even numbers for 4:2:0 codecs.
EXR input is linear scene data: ffmpeg will not apply AgX, so colours look wrong. Render or
convert to PNG/TIFF with the view transform applied first.
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr", ".bmp")
CODECS = {
    "h264": {"ext": (".mp4", ".mov", ".mkv"), "crf": 18},
    "h265": {"ext": (".mp4", ".mov", ".mkv"), "crf": 22},
    "prores": {"ext": (".mov",), "crf": None},
}
PRORES_PROFILES = {"proxy": 0, "lt": 1, "422": 2, "hq": 3, "4444": 4, "4444xq": 5}


def detect_sequence(path):
    """Return (pattern, start_number, frame_numbers, ext) for a folder or a %0Nd pattern."""
    if os.path.isdir(path):
        groups = {}
        for name in sorted(os.listdir(path)):
            stem, ext = os.path.splitext(name)
            if ext.lower() not in IMAGE_EXT:
                continue
            m = re.match(r"^(.*?)(\d+)$", stem)
            if not m:
                continue
            key = (m.group(1), len(m.group(2)), ext)
            groups.setdefault(key, []).append(int(m.group(2)))
        if not groups:
            raise SystemExit("ERROR: no numbered image files (name0001.png ...) in %s" % path)
        key = max(groups, key=lambda k: len(groups[k]))
        if len(groups) > 1:
            print("WARN: several sequences in the folder; using '%s####%s' (%d frames)"
                  % (key[0], key[2], len(groups[key])), file=sys.stderr)
        prefix, width, ext = key
        pattern = os.path.join(path, "%s%%0%dd%s" % (prefix, width, ext))
        frames = sorted(groups[key])
        return pattern, frames[0], frames, ext.lower()
    m = re.search(r"%0?(\d*)d", path)
    if not m:
        raise SystemExit("ERROR: give a folder or a pattern like frames/img_%04d.png")
    folder = os.path.dirname(path) or "."
    base = os.path.basename(path)
    rx = re.escape(base).replace(re.escape(m.group(0)), r"(\d+)")
    frames = []
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            mm = re.fullmatch(rx, name)
            if mm:
                frames.append(int(mm.group(1)))
    frames.sort()
    ext = os.path.splitext(base)[1].lower()
    return path, (frames[0] if frames else 1), frames, ext


def png_size(path):
    """Width, height from a PNG header (None if not a PNG)."""
    try:
        with open(path, "rb") as f:
            head = f.read(24)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            return None
        return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
    except OSError:
        return None


def build_command(pattern, start, fps, codec, out, crf=None, preset="slow",
                  prores_profile="hq", force=False, ffmpeg="ffmpeg", tune=None):
    cmd = [ffmpeg, "-hide_banner", "-y" if force else "-n",
           "-framerate", "%g" % fps, "-start_number", str(start), "-i", pattern]
    if codec in ("h264", "h265"):
        cmd += ["-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2"]
    if codec == "h264":
        cmd += ["-c:v", "libx264", "-preset", preset, "-crf", str(crf if crf is not None else 18)]
        if tune:
            cmd += ["-tune", tune]
        cmd += ["-pix_fmt", "yuv420p"]
    elif codec == "h265":
        cmd += ["-c:v", "libx265", "-preset", preset, "-crf", str(crf if crf is not None else 22),
                "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1"]
    else:
        cmd += ["-c:v", "prores_ks", "-profile:v", str(PRORES_PROFILES[prores_profile]),
                "-pix_fmt", "yuv444p10le" if prores_profile.startswith("4444") else "yuv422p10le"]
    if out.lower().endswith((".mp4", ".mov")):
        cmd += ["-movflags", "+faststart"]
    cmd += ["-r", "%g" % fps, out]
    return cmd


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="folder of numbered frames, or a pattern like frames/img_%%04d.png")
    p.add_argument("--fps", type=float, required=True)
    p.add_argument("--codec", choices=sorted(CODECS), default="h264")
    p.add_argument("--out", required=True)
    p.add_argument("--crf", type=int, help="0-51; h264 default 18, h265 default 22 (+6 ~ half the size)")
    p.add_argument("--preset", default="slow", help="x264/x265 preset (slower = smaller file)")
    p.add_argument("--tune", choices=["film", "animation", "grain"], help="x264 only")
    p.add_argument("--prores-profile", choices=sorted(PRORES_PROFILES), default="hq")
    p.add_argument("--run", action="store_true", help="execute ffmpeg (default: print only)")
    p.add_argument("--force", action="store_true", help="allow overwriting --out")
    a = p.parse_args(argv)

    if a.crf is not None and not 0 <= a.crf <= 51:
        p.error("--crf must be 0-51")
    if a.tune and a.codec != "h264":
        p.error("--tune is for h264 only")
    ext = os.path.splitext(a.out)[1].lower()
    if ext not in CODECS[a.codec]["ext"]:
        p.error("%s output should be one of %s" % (a.codec, ", ".join(CODECS[a.codec]["ext"])))

    pattern, start, frames, img_ext = detect_sequence(a.input)
    problems = 0
    if not frames:
        print("WARN: no frames found for %s (fine for a dry run)" % pattern, file=sys.stderr)
    else:
        expected = set(range(frames[0], frames[-1] + 1))
        missing = sorted(expected - set(frames))
        print("Frames: %d (%d-%d) = %.2f s at %g fps"
              % (len(frames), frames[0], frames[-1], len(frames) / a.fps, a.fps))
        if missing:
            problems += 1
            show = ", ".join(str(n) for n in missing[:10]) + (" ..." if len(missing) > 10 else "")
            print("WARN: %d missing frame(s): %s - ffmpeg stops at the first gap" % (len(missing), show),
                  file=sys.stderr)
        if img_ext == ".png":
            size = png_size(pattern % frames[0])
            if size:
                print("Frame size: %dx%d" % size)
                if a.codec != "prores" and (size[0] % 2 or size[1] % 2):
                    print("NOTE: odd size, padded to even for 4:2:0", file=sys.stderr)
    if img_ext == ".exr":
        print("WARN: EXR is linear data; ffmpeg won't apply AgX/Filmic - colours will look wrong. "
              "Encode from PNG/TIFF saved with the view transform.", file=sys.stderr)
    if os.path.exists(a.out) and not a.force:
        print("ERROR: %s exists; pass --force to overwrite or choose another --out" % a.out, file=sys.stderr)
        return 2

    ffmpeg = shutil.which("ffmpeg")
    cmd = build_command(pattern, start, a.fps, a.codec, a.out, a.crf, a.preset, a.prores_profile,
                        a.force, ffmpeg or "ffmpeg", a.tune)
    printable = subprocess.list2cmdline(cmd) if os.name == "nt" else " ".join(shlex.quote(c) for c in cmd)
    print("Command:\n  " + printable)
    if not a.run:
        print("(dry run: add --run to execute)")
        if not ffmpeg:
            print("NOTE: ffmpeg is not on PATH. It is free (ffmpeg.org); ask the user before installing.")
        return 0
    if not ffmpeg:
        print("ERROR: ffmpeg not found on PATH. It is free (ffmpeg.org); ask the user before installing.",
              file=sys.stderr)
        return 3
    if not frames:
        print("ERROR: no input frames", file=sys.stderr)
        return 2
    rc = subprocess.call(cmd)
    if rc == 0:
        print("Wrote %s (%s)" % (a.out, "%.1f MB" % (os.path.getsize(a.out) / 1048576.0)))
    else:
        print("ERROR: ffmpeg exited with %d" % rc, file=sys.stderr)
    if problems:
        print("Check the warnings above before delivering.", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
