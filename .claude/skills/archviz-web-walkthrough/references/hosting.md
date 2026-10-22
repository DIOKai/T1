# Hosting the tour (free static hosts)

The template is plain static files: `index.html`, `main.js`, `model.glb`, `lightmaps/`, optional furniture GLBs and decoder files. Any static host works. Deployment mechanics, cache headers and base paths in general: `threejs-deployment`. Publishing is the user's decision — ask before deploying, and never push a client's model to a public repo without permission.

## Limits (checked 2026-10-22)
| Host | Limits that matter for tours | Notes |
|---|---|---|
| **Cloudflare Pages** (free) | **25 MiB per file**; 20,000 files on Free; 500 builds/month; > 100 sites → Workers Static Assets recommended | `wrangler pages deploy <dir>` or Git integration |
| **GitHub Pages** (free) | site ≤ 1 GB; ~100 GB/month bandwidth (soft); 10 builds/hour (soft, not for custom Actions workflows); **not for running an online business or commercial transactions** | fine for a portfolio or a personal demo; a commercial sales site → Cloudflare |
| GitHub repo files | > 50 MiB warning, > 100 MiB rejected (needs Git LFS); web upload ≤ 25 MiB | whether Pages serves LFS files: 未验证 — don't rely on it |

## Before upload
1. `python scripts/check_walkthrough_build.py dist/model.glb` — no file over 25 MiB.
2. Split big tours: one GLB per floor (load the ground floor first, the rest on demand). Same rule helps first-load time on phones.
3. Self-host three.js and decoders (copy `build/three.module.js`, `examples/jsm/...` used, `libs/basis/*`, `libs/draco/gltf/*` from the **same** three version) and change the importmap and decoder paths in `main.js`. CDN links are fine for prototypes; a production tour shouldn't break when a CDN changes.
4. Compression and MIME types: meshopt GLBs compress well with gzip/brotli. Check the host serves `.wasm` as `application/wasm`, `.glb` as `model/gltf-binary`, `.ktx2` as `image/ktx2` (each host's defaults: 未逐项核对 — check the response headers in DevTools after deploying).
5. Relative paths only (`./model.glb`), so the site works in a sub-folder like `user.github.io/tour/`.

## Local test server
ES modules and `fetch` don't work from `file://`. From the tour folder:
```bash
python -m http.server 8000
```
Then open http://localhost:8000. To test on a phone on the same Wi-Fi, use the PC's LAN IP; pointer lock and some APIs need HTTPS except on localhost, so real phone tests are easiest on the deployed (HTTPS) preview URL.

## Sources
- GitHub Pages limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- GitHub large files: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- Cloudflare Pages limits: https://developers.cloudflare.com/pages/platform/limits/
