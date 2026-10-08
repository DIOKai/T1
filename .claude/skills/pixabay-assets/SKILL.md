---
name: pixabay-assets
description: Use when the user needs free stock images or videos for a game server or UI — FiveM NUI backgrounds, phone wallpapers, shop/menu item pictures, loading-screen backgrounds and videos, textures or decals for props, reference photos for image-to-3D (Hunyuan3D) — or free music and sound effects. Searches and downloads from Pixabay with a free API key through a bundled script that caches results, respects rate limits and writes a credits file. Also use when they say "Pixabay", "免费图片", "免费素材", "背景图", "壁纸", "loading screen 视频", "音效", "背景音乐", "stock photo", or ask where to get free pictures, videos or sounds they can use on their server.
---

# Pixabay assets (free images, videos, music, sound effects)

Pixabay content is free to use, commercially too, without attribution (Pixabay Content License). The API is free with an account. Use it instead of paid stock sites or paid AI image generators (project rule: no paid tools).

What the API covers: **images and videos only.** Pixabay's music and sound effects have **no API**. Download them by hand from the site, or use Freesound (see `references/licenses-and-audio.md`).

Read `references/licenses-and-audio.md` before putting Pixabay files into a **public** or **sold** resource, and for music/SFX.

## Setup (once)

1. The user logs in at pixabay.com (free) and copies their key from https://pixabay.com/api/docs/ (shown on that page when logged in).
2. They put it in an environment variable, so it never lands in a file you commit:
   - Windows PowerShell: `setx PIXABAY_API_KEY "their-key"`. It only reaches programs started afterwards, so restart the terminal and Claude Code.
   - Linux/macOS: `export PIXABAY_API_KEY=their-key`
3. Never paste the key into code, `config.lua`, NUI JavaScript or a commit. A key in client-side NUI is public.

## The script

`scripts/pixabay.py`, Python standard library only. Runs on the user's machine (talks to pixabay.com).

The script runs where the user works (their project folder, not necessarily T1). Use the full path to it; on Windows use `py` if `python` opens the Microsoft Store.

```powershell
$S = "C:\path\to\T1\.claude\skills\pixabay-assets\scripts\pixabay.py"
py $S search "city night" --type photo --orientation horizontal
py $S search "rain window" --video --video-type film
py $S search "汉堡" --lang zh --type photo           # Chinese keywords; English ones find more
py $S search "burger" --type photo --json           # machine-readable for picking
py $S get 195893                                    # details of one image
py $S download 195893 --out web\img                # 1280 px JPG + credits
py $S download 125 --video --size medium --out loadscreen
py $S credit --out loadscreen --file rain_theme.ogg --page https://pixabay.com/music/... --user "Author" --kind music
```
(bash: `S=/path/to/pixabay.py; python3 $S ...`)

- `download` names files `pixabay_<id>_<tag>_<size>.<ext>`, and keeps `pixabay_credits.json` + `CREDITS-pixabay.md` in that folder up to date (page URL, author, date). The `.md` is rebuilt from the JSON each time: record hand-downloaded files (music, SFX, originals) with `credit`, not by editing the `.md`. Ship the `.md` with the resource.
- Image sizes through a free key: `preview` (150 px), `web` (640 px), `large` (**1280 px max**, default). For anything bigger (a 1920×1080 loading screen, a sharp wallpaper), **download the original by hand** from the image's page (free, log in), then `credit` it. Full-size API URLs need "full API access", which Pixabay grants on request.
- Video sizes: `large`, `medium` (default), `small`, `tiny`; if a clip lacks the size, the script falls back to the next one. Video search ignores `--orientation`, `--colors` and `--type` (the script warns), so check width × height for vertical clips.
- Results are cached for 24 h (Pixabay's docs require caching), so repeated searches don't use up the rate limit. The published limit is unclear (copies of the docs say 5,000 per hour per key, other guides say 100 per minute; UNVERIFIED, pixabay.com is unreachable from here). The script reads the `X-RateLimit-*` headers, warns when few requests are left, and on HTTP 429 waits once and retries.
- The API is meant for real use by people. Don't script mass downloads of whole categories; Pixabay forbids systematic mass downloading.
- It only downloads from `pixabay.com` addresses, refuses redirects elsewhere, and stops at 500 MB.

Show the user the page URLs (or previews) and let them pick before downloading a batch. Searching is cheap; their taste matters.

## Using the files in FiveM

| Use | What to get | Prepare |
|---|---|---|
| In-game phone wallpaper (NUI) | `--orientation vertical`, `large` | convert to **WebP** (~80 % quality), size to the screen (phone: ~1200 px tall), not 4K. See `fivem-phone`. For a real phone's wallpaper, download the original by hand |
| Menu / shop item pictures | `--type photo` or `illustration`, `--colors transparent` for cut-outs | crop square, 256–512 px WebP |
| Loading screen background | photo (original by hand for 1920 px) or a video | video: `small` or `medium`, convert to **WebM**, mute, keep it short (< 10–15 MB); players download it before joining |
| Prop textures / decals | `--type photo`, flat front-on shots | power-of-two size (512/1024), DDS via Sollumz. See `free-3d-assets` |
| Reference for image-to-3D | one object, plain background, three-quarter view | feed to Hunyuan3D (`free-3d-assets`) |

**Video format:** Pixabay delivers MP4 (H.264). FiveM's built-in browser (CEF) is widely reported not to play H.264, since Chromium without proprietary codecs doesn't (UNVERIFIED from FiveM source; test it). Convert to WebM with free ffmpeg to be safe:
```
ffmpeg -i in.mp4 -an -c:v libvpx-vp9 -crf 34 -b:v 0 -vf scale=1920:-2 -row-mt 1 loadscreen.webm
ffmpeg -i music.mp3 -c:a libvorbis -q:a 4 music.ogg
ffmpeg -i wallpaper.jpg -q:v 80 wallpaper.webp
```

Bundle downloaded files with the resource. Don't load Pixabay URLs live in NUI: no permanent hotlinking, and `webformatURL` links expire after 24 h.

## Ground rules
- Free key only. Don't sign up for paid plans or other stock sites on the user's behalf.
- Don't commit the API key, and don't put it in client-side code.
- Recognisable people in photos: not in a misleading, offensive or illegal context (licence restrictions).
- Pixabay doesn't allow selling or distributing its files "on a standalone basis" (substantially unchanged: wallpaper packs, music packs, stock collections), using logos/trademarks commercially, or using an image as a server logo or brand. Using files inside your own server's UI is normal use. Details in the reference.
