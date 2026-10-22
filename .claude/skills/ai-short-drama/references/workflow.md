# Workflow and craft

Numbers marked 经验值 are rules of thumb from writing guides and creator practice, not standards. Sources are in the research note.

## Format
- Vertical **9:16, 1080×1920**, 24 or 30 fps. Keep faces and subtitles inside the middle ~70 % of the height — platform buttons and captions cover the top and bottom (经验值; check on a phone).
- Episode length: sources disagree — 1–2 min, 1–3 min, 2–3 min; China's regulator defines micro-drama episodes as tens of seconds to ~15 min. Start at 60–90 s.
- Most viewers watch with sound off at first → every line needs a subtitle, big and high-contrast.

## Story
1. **Logline** — who wants what, what stops them, in one sentence.
2. **Characters** — name, one fixed look line (age, hair, outfit, one unique detail), what they want. Reuse the look line word-for-word in every image prompt.
3. **Beats per episode** — hook (0–3 s, 经验值: a slap, a reveal, a line that raises a question) → escalation → turn → **cliffhanger**. Each episode needs its own start, middle and end. Paid series usually put the first paywall right after a strong cliffhanger a few episodes in.
4. **Script** — short lines (one breath), visible action, few locations (each location = one more reference sheet).
5. Content limits: no real people's likeness without consent, nothing a platform would treat as misleading news, nothing vulgar for its own sake (China has removed low-quality micro-dramas).

## Character consistency
- Reference sheet per character: front, side, back, 2–3 expressions, plain grey background, same outfit. Location sheet per recurring set.
- Pass the sheet into every shot (Toonflow asset node, 火宝 `@character` reference, ComfyUI IP-Adapter / reference image). Fixed seed while testing a shot.
- A character LoRA (trained on 15–30 consistent images, 经验值) gives the most stable face on local models; only train on images you have rights to.
- Video models drift over long shots: keep clips short (one model clip, often ~5 s) and cut on action.

## storyboard.json (input to `scripts/storyboard_to_shotlist.py`)
```json
{
  "title": "ep01",
  "speaker_in_subtitles": false,
  "characters": {"lin": {"name": "林夏", "ref": "refs/lin_sheet.png", "look": "..."}},
  "shots": [
    {"id": "01", "scene": "天台 夜", "shot": "close-up", "camera": "push-in",
     "characters": ["lin"], "action": "...", "line": {"speaker": "lin", "text": "..."},
     "duration": 3, "sfx": "wind", "prompt": "...", "cliffhanger": "..."}
  ]
}
```
- Required: `shots` (non-empty). Everything else optional.
- `duration` (seconds) wins; without it the script estimates from the line (CJK 4.5 chars/s, other languages 2.5 words/s, +0.5 s, min 1.5 s — 经验值, change with `--cps`, `--wps`, `--min-shot`).
- `line` may be a plain string. Speakers `narrator`, `VO`, `旁白` don't need a character entry.
- Outputs: `<name>_shotlist.csv` (UTF-8 with BOM so Excel shows Chinese) and `<name>.srt`.
- Options: `--target-seconds` (episode length check), `--max-clip` (one model clip, default 5), `--line-chars` (CJK per subtitle line, default 16), `--latin-chars` (default 42), `--out-dir`.

## Generation loop (per shot)
1. Image first (keyframe) from the reference sheet + shot prompt; approve it.
2. Image-to-video from that keyframe (or first + last frame for controlled moves); prompt the **motion**, not the whole scene again.
3. 2–4 takes, pick one, log seed and model in the shot list.
4. Check: face and outfit match the sheet, hands, background continuity with the previous shot, no garbled text, nothing important under the platform UI.

## Assembly (ask before using `ffmpeg-skill`)
Concatenate clips in shot-list order, add voice track, music ducked under voice (`audio-design` explains ducking), subtitles from the SRT (burn in for Douyin/TikTok reach; also upload the SRT where supported), loudness-normalise, export H.264 1080×1920. Keep the project folder: refs/, shots/, audio/, storyboard.json, shotlist.csv, .srt.

## Related skills (ask before using each)
- `ai-archviz-render` — install local ComfyUI, model licences, Wan2.2 image-to-video, consistency tricks.
- `ffmpeg-skill` — cut, concat, subtitles, loudness, export.
- `narrative-design` — story structure and dialogue.
- `audio-design` — mixing, ducking; `pixabay-assets` — free music/SFX (needs the user's free API key).
- `remotion` — only if installed; programmatic titles/subtitles; paid licence for companies over 3 people.
