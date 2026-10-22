#!/usr/bin/env python3
"""Turn a simple storyboard JSON into a shot list CSV and a subtitle SRT.

Standard library only. Reads one JSON file, writes two new files, changes nothing else.

Usage:
    python storyboard_to_shotlist.py storyboard.json [--out-dir DIR]
        [--cps 4.5] [--wps 2.5] [--min-shot 1.5] [--max-clip 5]
        [--target-seconds 90] [--line-chars 16] [--latin-chars 42]

Schema: see ../references/workflow.md ("storyboard.json"). Minimal example:
{
  "title": "ep01",
  "characters": {"lin": {"name": "林夏", "ref": "refs/lin_sheet.png"}},
  "shots": [
    {"id": "01", "shot": "close-up", "camera": "push-in", "characters": ["lin"],
     "action": "林夏猛地抬头", "line": {"speaker": "lin", "text": "你骗了我三年。"}}
  ]
}

Durations: a shot's "duration" (seconds) wins. Otherwise it is estimated from the
subtitle: CJK characters / cps, or words / wps, plus 0.5 s breathing room, never
shorter than --min-shot. The reading speeds are rules of thumb, not a standard.

Exit code 0 = written (warnings may be printed), 1 = input error.
"""
import argparse
import csv
import json
import os
import re
import sys

CJK = re.compile(r"[぀-ヿ㐀-䶿一-鿿가-힯豈-﫿]")
PUNCT = re.compile(r"[\s，。！？、；：,.!?;:\"'“”‘’…—\-()（）《》]")


def spoken_seconds(text, cps, wps):
    """Estimated reading time of one subtitle in seconds."""
    if not text:
        return 0.0
    cjk = len(CJK.findall(text))
    rest = CJK.sub(" ", text)
    words = len([w for w in re.split(r"\s+", PUNCT.sub(" ", rest)) if w])
    return cjk / cps + words / wps


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def wrap(text, line_chars, latin_chars):
    """Wrap a subtitle into lines (CJK by characters, others by words); returns a list."""
    if CJK.search(text):
        return [text[i:i + line_chars] for i in range(0, len(text), line_chars)] or [""]
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > latin_chars:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return lines


def load(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"ERROR: cannot read {path}: {e}")
    if not isinstance(data, dict) or not isinstance(data.get("shots"), list) or not data["shots"]:
        sys.exit("ERROR: JSON needs a non-empty \"shots\" list")
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("storyboard")
    ap.add_argument("--out-dir", default=None, help="default: next to the JSON")
    ap.add_argument("--cps", type=float, default=4.5, help="CJK chars per second (rule of thumb)")
    ap.add_argument("--wps", type=float, default=2.5, help="words per second for non-CJK text")
    ap.add_argument("--min-shot", type=float, default=1.5, help="shortest estimated shot, seconds")
    ap.add_argument("--max-clip", type=float, default=5.0,
                    help="longest clip the video model makes in one go; longer shots get a warning")
    ap.add_argument("--target-seconds", type=float, default=None, help="episode length to check against")
    ap.add_argument("--line-chars", type=int, default=16, help="CJK chars per subtitle line (rule of thumb)")
    ap.add_argument("--latin-chars", type=int, default=42, help="Latin chars per subtitle line (rule of thumb)")
    a = ap.parse_args(argv)

    data = load(a.storyboard)
    chars = data.get("characters") or {}
    base = os.path.splitext(os.path.basename(a.storyboard))[0]
    out_dir = a.out_dir or os.path.dirname(os.path.abspath(a.storyboard))
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, base + "_shotlist.csv")
    srt_path = os.path.join(out_dir, base + ".srt")

    warnings, rows, subs, seen = [], [], [], set()
    t = 0.0
    for i, s in enumerate(data["shots"], 1):
        if not isinstance(s, dict):
            sys.exit(f"ERROR: shot {i} is not an object")
        sid = str(s.get("id") or f"{i:02d}")
        if sid in seen:
            warnings.append(f"shot {sid}: duplicate id")
        seen.add(sid)
        line = s.get("line") or {}
        if isinstance(line, str):
            line = {"text": line}
        text = (line.get("text") or "").strip()
        speaker_key = line.get("speaker") or ""
        speaker = (chars.get(speaker_key) or {}).get("name", speaker_key)

        if s.get("duration") is not None:
            try:
                dur = float(s["duration"])
            except (TypeError, ValueError):
                sys.exit(f"ERROR: shot {sid}: duration must be a number")
            if dur <= 0:
                sys.exit(f"ERROR: shot {sid}: duration must be > 0")
            need = spoken_seconds(text, a.cps, a.wps)
            if need > dur + 0.05:
                warnings.append(f"shot {sid}: line needs ~{need:.1f}s but shot is {dur:.1f}s (too fast to read)")
            src = "given"
        else:
            dur = max(a.min_shot, round(spoken_seconds(text, a.cps, a.wps) + 0.5, 1) if text else a.min_shot)
            src = "estimated"
        if dur > a.max_clip:
            warnings.append(f"shot {sid}: {dur:.1f}s is longer than one {a.max_clip:g}s model clip; split it or plan an extend")

        cast = s.get("characters") or []
        refs = []
        for c in cast:
            if c not in chars:
                warnings.append(f"shot {sid}: character '{c}' not in \"characters\"")
            elif not chars[c].get("ref"):
                warnings.append(f"shot {sid}: character '{c}' has no reference sheet (consistency risk)")
            else:
                refs.append(chars[c]["ref"])
        if speaker_key and speaker_key not in chars and speaker_key not in ("narrator", "VO", "旁白"):
            warnings.append(f"shot {sid}: speaker '{speaker_key}' not in \"characters\"")

        start, end = t, t + dur
        rows.append({
            "shot_id": sid, "start": f"{start:.2f}", "end": f"{end:.2f}", "duration": f"{dur:.2f}",
            "duration_source": src, "scene": s.get("scene", ""), "shot_size": s.get("shot", ""),
            "camera": s.get("camera", ""), "characters": " ".join(cast), "ref_images": " ".join(refs),
            "action": s.get("action", ""), "speaker": speaker, "line": text,
            "sfx_music": s.get("sfx", ""), "prompt": s.get("prompt", ""),
        })
        if text:
            label = f"{speaker}：" if speaker and data.get("speaker_in_subtitles") else ""
            lines = wrap(label + text, a.line_chars, a.latin_chars)
            if len(lines) > 2:
                warnings.append(f"shot {sid}: subtitle needs {len(lines)} lines; split the line across shots (max 2 on a phone)")
            subs.append((start, end, "\n".join(lines)))
        t = end

    first = float(rows[0]["duration"])
    if first > 3.0:
        warnings.append(f"first shot is {first:.1f}s; the hook usually lands in the first ~3s (rule of thumb)")
    if not rows[-1]["line"] and not data["shots"][-1].get("cliffhanger"):
        warnings.append("last shot has no line and no \"cliffhanger\" note; end the episode on a question")
    if a.target_seconds and t > a.target_seconds * 1.1:
        warnings.append(f"episode is {t:.1f}s, over the {a.target_seconds:g}s target by more than 10%")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel shows Chinese
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(srt_path, "w", encoding="utf-8") as f:
        for n, (st, en, tx) in enumerate(subs, 1):
            f.write(f"{n}\n{srt_time(st)} --> {srt_time(en)}\n{tx}\n\n")

    print(f"shots: {len(rows)}  total: {t:.1f}s  subtitles: {len(subs)}")
    print(f"wrote {csv_path}")
    print(f"wrote {srt_path}")
    for wmsg in warnings:
        print("WARN", wmsg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
