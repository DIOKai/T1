---
name: video-downloader
description: Download YouTube videos with customizable quality and format options. Use this skill when the user asks to download, save, or grab YouTube videos. Supports various quality settings (best, 1080p, 720p, 480p, 360p), multiple formats (mp4, webm, mkv), and audio-only downloads as MP3.
---

# YouTube Video Downloader

Download YouTube videos with full control over quality and format settings.

## Quick Start

The simplest way to download a video:

```bash
python .claude/skills/video-downloader/scripts/download_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This downloads the video in best available quality as MP4 to the user's `Downloads` folder (`~/Downloads`, on Windows `C:\Users\<name>\Downloads`).

Needs `yt-dlp` (and `ffmpeg` to merge video + audio or make MP3). The script does not install anything; if yt-dlp is missing it prints the install command (`python -m pip install yt-dlp`) — ask the user before running it.

## Options

### Quality Settings

Use `-q` or `--quality` to specify video quality:

- `best` (default): Highest quality available
- `1080p`: Full HD
- `720p`: HD
- `480p`: Standard definition
- `360p`: Lower quality
- `worst`: Lowest quality available

Example:
```bash
python .claude/skills/video-downloader/scripts/download_video.py "URL" -q 720p
```

### Format Options

Use `-f` or `--format` to specify output format (video downloads only):

- `mp4` (default): Most compatible
- `webm`: Modern format
- `mkv`: Matroska container

Example:
```bash
python .claude/skills/video-downloader/scripts/download_video.py "URL" -f webm
```

### Audio Only

Use `-a` or `--audio-only` to download only audio as MP3:

```bash
python .claude/skills/video-downloader/scripts/download_video.py "URL" -a
```

### Custom Output Directory

Use `-o` or `--output` to specify a different output directory:

```bash
python .claude/skills/video-downloader/scripts/download_video.py "URL" -o /path/to/directory
```

## Complete Examples

1. Download video in 1080p as MP4:
```bash
python .claude/skills/video-downloader/scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 1080p
```

2. Download audio only as MP3:
```bash
python .claude/skills/video-downloader/scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -a
```

3. Download in 720p as WebM to custom directory:
```bash
python .claude/skills/video-downloader/scripts/download_video.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 720p -f webm -o /custom/path
```

## How It Works

The skill uses `yt-dlp`, a robust YouTube downloader that:
- Is found on PATH or as the `yt_dlp` Python module (never auto-installed)
- Fetches video information before downloading
- Selects the best available streams matching your criteria
- Merges video and audio streams when needed
- Supports a wide range of YouTube video formats

## Important Notes

- Downloads are saved to the user's `Downloads` folder by default (created if missing)
- Video filename is automatically generated from the video title
- yt-dlp must be installed first; the script only prints the install command
- Only single videos are downloaded (playlists are skipped by default)
- Higher quality videos may take longer to download and use more disk space