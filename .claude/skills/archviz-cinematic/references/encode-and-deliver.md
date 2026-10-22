# Image sequence → video, and delivery

## Always render an image sequence first
The Blender manual: "It's not recommended to render directly to a video format in the first instance" — a crash can leave an unplayable file and you start over; a sequence resumes, and encoding takes seconds to minutes. Don't grade or post-process lossy video.

- Frame numbers are padded to 4 digits (`shot01_0001.png`); `#` in the path sets the padding.
- **Overwrite off + Placeholders on** = resume after a crash, or a poor man's render farm: several PCs render the same file to the same shared folder and skip frames already claimed.
- 5.0+: set `image_settings.media_type` (`'IMAGE'`, `'MULTI_LAYER_IMAGE'`, `'VIDEO'`) **before** `file_format`. Multilayer EXR is multi-part by default; 5.2 writes half-float EXR faster and can switch off saving the render output.
- Which format: **PNG 16-bit RGB** with the AgX view baked in = ready to encode; **EXR MultiLayer** = keeps passes and Denoising Data for later (must go through the compositor / a PNG export before ffmpeg — ffmpeg doesn't apply AgX, so linear EXR looks wrong). Many projects save both: EXR master + PNG for encoding (via a File Output node).

## Encode with ffmpeg (free)
`scripts/encode_sequence.py` builds these commands, checks for missing frames, pads odd sizes, refuses to overwrite without `--force`, and only runs ffmpeg with `--run`.

```
ffmpeg -framerate 24 -start_number 1 -i shot01_%04d.png -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart shot01.mp4
ffmpeg -framerate 24 -start_number 1 -i shot01_%04d.png -c:v libx265 -preset slow -crf 22 -pix_fmt yuv420p10le -tag:v hvc1 shot01_hevc.mp4
ffmpeg -framerate 24 -start_number 1 -i shot01_%04d.png -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le shot01_prores.mov
```

| Target | Codec | Quality | Why |
|---|---|---|---|
| Client review, web, WhatsApp | H.264 | CRF 18 (17–18 ≈ visually lossless; 23 default; +6 ≈ half the size) | plays everywhere |
| Smaller master, Apple devices | H.265 10-bit | CRF 22 (x265 CRF 28 ≈ x264 CRF 23 at ~half size) | `-tag:v hvc1` so QuickTime/iOS play it |
| Editing in DaVinci Resolve / Premiere | ProRes 422 HQ (`-profile:v 3`) | intra-frame, big | smooth scrubbing, survives re-encoding |

- Use the slowest preset you can wait for (smaller file at the same quality). `-tune film` / `animation` / `grain` are x264 options; CG archviz with clean gradients often looks fine without tune.
- `-pix_fmt yuv420p` for player compatibility and `-movflags +faststart` for web playback are common ffmpeg practice (not read in the wiki text itself). 4:2:0 needs even width and height — the script pads.
- Banding in skies: prefer 10-bit H.265, or add slight grain in the compositor (experience, unverified).
- Tested on this skill's authoring machine with ffmpeg 9.0.1: H.265 output was Main 10 with tag `hvc1`; ProRes `-profile:v 3` was reported by ffprobe as **HQ** (`apch`).
- Blender's own FFmpeg output exists (MKV default container, CRF presets, ProRes profiles, 10-bit H.264/H.265/AV1, 12-bit H.265/AV1) — fine for a quick preview of an already-rendered sequence (Video Sequencer), not for rendering the film directly.
- Editing, music, titles, social crops (9:16 reels), loudness → `ffmpeg-skill` (ask first). ffmpeg is free; ask before installing it.

## Delivery checklist
- [ ] 3–5 s test clip watched looping full screen: no flicker, no fireflies, no judder in pans.
- [ ] All frames present (no gaps, no black frames); frame count = seconds × fps.
- [ ] Verticals straight on every exterior shot; no floating objects; every window shows a real interior.
- [ ] Exposure consistent between shots (same Exposure / look unless intentional).
- [ ] Master kept: EXR or PNG-16 sequence + ProRes; delivery: H.264 MP4 (+ H.265 if wanted).
- [ ] Licences of every asset (Poly Haven / ambientCG CC0; Sketchfab models each have their own licence) noted for the client.
- [ ] Optional AI enhancement done on a copy, never on the master (`ai-archviz-render`).

## Render-time budgeting
Total frames = seconds × fps (30 s × 24 = 720 frames; at 2 min/frame = 24 h, at 6 min = 72 h). Measure 3 representative frames at final resolution, take the slowest, × frames × 1.2 margin ÷ machines. `scripts/render_budget.py` does this and estimates disk (estimate only) and trade-offs. Over budget → resolution → noise threshold → time limit → portals → bounces → EEVEE for less critical shots. Test renders at Format ▸ Percentage 50 % keep the same framing.

## Sources
- Output properties (don't render straight to video, placeholders): https://docs.blender.org/manual/en/latest/render/output/properties/output.html
- Format / percentage: https://docs.blender.org/manual/en/latest/render/output/properties/format.html
- ImageFormatSettings (media_type): https://docs.blender.org/api/current/bpy.types.ImageFormatSettings.html ; 5.0 pipeline notes: https://developer.blender.org/docs/release_notes/5.0/pipeline_io/ ; 5.2 pipeline notes: https://developer.blender.org/docs/release_notes/5.2/pipeline_io/
- FFmpegSettings API: https://docs.blender.org/api/current/bpy.types.FFmpegSettings.html
- ffmpeg H.264 wiki: https://trac.ffmpeg.org/wiki/Encode/H.264 ; H.265 wiki: https://trac.ffmpeg.org/wiki/Encode/H.265
