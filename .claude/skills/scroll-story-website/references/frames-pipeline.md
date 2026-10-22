# Making the frame sequence (free)

## How the scrub works
A tall section (`height: 400vh`, 300vh on phones) holds a sticky full-screen `<canvas>`. Scroll progress = how far the section has moved past the top ÷ (section height − viewport height). Frame = `round(progress × (count − 1))`. The scroll listener is passive and only requests an animation frame; drawing happens in `requestAnimationFrame`, and the same frame is never drawn twice. This is the Apple product-page technique as written up by CSS-Tricks (148 JPEGs, preloaded with `new Image()`): https://css-tricks.com/lets-make-one-of-those-fancy-scrolling-animations-used-on-apple-product-pages/

The template adds: first frame first, then coarse-to-fine loading (every 12th, every 4th, all) so early scrolling still shows pictures; nearest-loaded-frame fallback; `devicePixelRatio` capped at 2; reduced-motion loads one still frame only.

## Budgets (经验值, test on a phone)
| | Desktop | Mobile |
|---|---|---|
| Width | 1600–1920 px | 720–960 px |
| Frames | 90–150 | 60–100 (drop every other frame) |
| Format | WebP q 70–80 | WebP q 65–75 |
| Total | ≤ 8 MB | ≤ 4 MB |

Decoded memory is width × height × 4 bytes per frame (1280×720 ≈ 3.7 MB), so 150 full-HD frames is over 1 GB if all stay decoded — another reason for a smaller mobile set. Large or leaked canvases are a known cause of mobile Safari tab crashes (https://bugs.webkit.org/show_bug.cgi?id=172533). WebP over AVIF for sequences: AVIF is smaller but slower to decode (未验证 per device; measure).

Serving a mobile set: put frames in `frames/desktop/` and `frames/mobile/` and set `SITE_CONFIG.frames.path` from `matchMedia('(max-width: 760px)')` before `app.js` loads.

## Sources of footage, cheapest first
1. **The shop's own phone video.** Tripod or a fixed spot, same framing before and after; a slow walk-around with a gimbal; a light bar or torch dragged across the bonnet for the "light sweep". Shoot 4K/60 if possible, landscape for desktop and a vertical take for mobile.
2. **Blender** (`archviz-cinematic` skill, ask first): keyframe a push-in / orbit, render a PNG sequence in Cycles, then convert. A free car model from `free-3d-assets` (check the licence; CC-BY needs credit on the site).
3. **Stock video** via `pixabay-assets` (free API key, ask first).
4. **AI video** (Kling, Runway, Veo, Seedance …): mostly **付费**, ask first. Free local route: `ai-archviz-render` (ComfyUI + Wan2.2 first/last frame) — good for "dirty → clean" from two stills.

## ffmpeg recipes (ffmpeg is free; the user's PC has it)
```bash
# 30 s clip -> ~120 desktop frames (4 fps of source), 1600 wide, WebP
ffmpeg -i clip.mp4 -vf "fps=4,scale=1600:-2" -c:v libwebp -quality 78 frames/desktop/f_%04d.webp
# mobile set, vertical crop to 9:16 then 900 wide
ffmpeg -i clip.mp4 -vf "fps=3,crop=ih*9/16:ih,scale=900:-2" -c:v libwebp -quality 70 frames/mobile/f_%04d.webp
# Blender PNG sequence -> WebP
ffmpeg -i render/%04d.png -c:v libwebp -quality 78 frames/desktop/f_%04d.webp
```
Pick `fps` so the frame count lands in the budget: frames ≈ clip seconds × fps. Numbering starts at 0001 — matches the template (`pad: 4`). Check total size before shipping (`du -sh frames/*`).

## Story beats for a detailing / tint shop
dirty wide shot → foam/wash → polished panel close-up → push into the badge → light sweep → final hero with the CTA. Three to five captions, each 3–7 words, placed with `data-at="0.25-0.5"`.
