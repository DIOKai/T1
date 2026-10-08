#!/usr/bin/env python3
"""Search and download free Pixabay images and videos, with a credits file.

Standard library only. Needs a free Pixabay API key in the PIXABAY_API_KEY environment variable
(get it at https://pixabay.com/api/docs/ after logging in). The key is never printed.

  python pixabay.py search "burger" [--type photo] [--orientation horizontal] [--per-page 20] [--json]
  python pixabay.py search "rain city" --video [--video-type film]
  python pixabay.py get 195893 [--video]
  python pixabay.py download 195893 --out assets/ [--size large]
  python pixabay.py download 125 --video --size medium --out assets/

API facts (pixabay.com/api/docs): images at https://pixabay.com/api/, videos at /api/videos/;
per_page 3-200; results cached 24 h by us as Pixabay asks; free keys get previewURL (150 px),
webformatURL (640 px) and largeImageURL (1280 px). Videos come in large/medium/small/tiny and a size
the clip doesn't have is an empty URL. Download files to your own storage: no permanent hotlinking.

Environment for tests: PIXABAY_API_BASE (default https://pixabay.com/api/), PIXABAY_ALLOW_HOSTS
(extra download hosts, comma separated; plain http is only allowed for these), PIXABAY_CACHE_DIR.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_BASE = os.environ.get("PIXABAY_API_BASE", "https://pixabay.com/api/")
CACHE_DIR = os.environ.get("PIXABAY_CACHE_DIR") or os.path.join(
    os.path.expanduser("~"), ".cache", "pixabay-assets")
CACHE_SECONDS = 24 * 3600
EXTRA_HOSTS = [h.strip().lower() for h in os.environ.get("PIXABAY_ALLOW_HOSTS", "").split(",") if h.strip()]
MAX_DOWNLOAD_BYTES = 500 * 1024 * 1024
UA = "pixabay-assets-skill/1.0"

IMAGE_SIZES = {"preview": "previewURL", "web": "webformatURL", "large": "largeImageURL",
               "full": "fullHDURL", "original": "imageURL", "vector": "vectorURL"}
VIDEO_SIZES = ["large", "medium", "small", "tiny"]
CREDITS_JSON = "pixabay_credits.json"
CREDITS_MD = "CREDITS-pixabay.md"


def fail(msg, code=1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def api_key():
    key = os.environ.get("PIXABAY_API_KEY", "").strip()
    if not key:
        fail("set PIXABAY_API_KEY to your free Pixabay API key (log in, then see https://pixabay.com/api/docs/)")
    return key


def redact(text, key):
    return text.replace(key, "***") if key else text


# ---------- API with cache and rate limits ----------

def cache_path(params):
    clean = sorted((k, v) for k, v in params.items() if k != "key")
    digest = hashlib.sha256(json.dumps(clean).encode()).hexdigest()[:32]
    return os.path.join(CACHE_DIR, digest + ".json")


def api_get(endpoint, params, use_cache=True):
    key = api_key()
    path = cache_path(dict(params, _endpoint=endpoint))
    if use_cache and os.path.isfile(path) and time.time() - os.path.getmtime(path) < CACHE_SECONDS:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    url = urllib.parse.urljoin(API_BASE, endpoint) + "?" + urllib.parse.urlencode(dict(params, key=key))
    for attempt in range(2):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                remaining = r.headers.get("X-RateLimit-Remaining")
                body = r.read()
        except urllib.error.HTTPError as e:
            text = redact(e.read()[:500].decode("utf-8", "replace"), key)
            if e.code == 429 and attempt == 0:
                wait = min(int(e.headers.get("X-RateLimit-Reset", "30") or 30), 60)
                print(f"rate limited by Pixabay, waiting {wait} s...", file=sys.stderr)
                time.sleep(wait)
                continue
            if e.code == 429:
                fail("Pixabay rate limit reached. Wait a few minutes and retry (cached searches don't count).")
            if e.code in (400, 401, 403) and "key" in text.lower():
                fail(f"Pixabay rejected the API key: {text.strip()}")
            fail(f"Pixabay API HTTP {e.code}: {text.strip()}")
        except (urllib.error.URLError, OSError) as e:
            fail(redact(f"can't reach Pixabay: {getattr(e, 'reason', e)}", key))
        break
    try:
        data = json.loads(body)
    except ValueError:
        fail("Pixabay returned something that isn't JSON: " + redact(body[:200].decode("utf-8", "replace"), key))
    if remaining is not None and remaining.isdigit() and int(remaining) < 5:
        print(f"note: only {remaining} Pixabay requests left in this rate-limit window", file=sys.stderr)
    os.makedirs(CACHE_DIR, exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(tmp, path)
    return data


# ---------- helpers ----------

def host_allowed(url):
    p = urllib.parse.urlsplit(url)
    host = (p.hostname or "").lower()
    if host in EXTRA_HOSTS:
        return p.scheme in ("http", "https")
    return p.scheme == "https" and (host == "pixabay.com" or host.endswith(".pixabay.com"))


def slug(text, limit=40):
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return s[:limit].strip("_") or "asset"


def first_tag(hit):
    return (hit.get("tags") or "").split(",")[0].strip()


def video_files(hit):
    out = []
    for size in VIDEO_SIZES:
        v = (hit.get("videos") or {}).get(size) or {}
        if v.get("url"):
            out.append((size, v))
    return out


def summarize(hit, video):
    base = {"id": hit.get("id"), "page": hit.get("pageURL"), "tags": hit.get("tags"),
            "user": hit.get("user"), "type": hit.get("type")}
    if video:
        base["duration_s"] = hit.get("duration")
        base["sizes"] = {s: f"{v.get('width')}x{v.get('height')} {round((v.get('size') or 0) / 1e6, 1)} MB"
                         for s, v in video_files(hit)}
    else:
        base["size"] = f"{hit.get('imageWidth')}x{hit.get('imageHeight')}"
        base["preview"] = hit.get("previewURL")
        base["sizes"] = [s for s, f in IMAGE_SIZES.items() if hit.get(f)]
    return base


# ---------- commands ----------

def cmd_search(args):
    params = {"q": args.query[:100], "page": args.page, "per_page": args.per_page,
              "safesearch": "false" if args.no_safesearch else "true", "order": args.order}
    if args.lang:
        params["lang"] = args.lang
    if args.orientation != "all" and not args.video:
        params["orientation"] = args.orientation
    if args.category:
        params["category"] = args.category
    if args.min_width:
        params["min_width"] = args.min_width
    if args.min_height:
        params["min_height"] = args.min_height
    if args.editors_choice:
        params["editors_choice"] = "true"
    if args.video:
        params["video_type"] = args.video_type
        data = api_get("videos/", params, use_cache=not args.no_cache)
    else:
        params["image_type"] = args.type
        if args.colors:
            params["colors"] = args.colors
        data = api_get("", params, use_cache=not args.no_cache)

    hits = [summarize(h, args.video) for h in data.get("hits", [])]
    if args.json:
        print(json.dumps({"total": data.get("totalHits", 0), "hits": hits}, ensure_ascii=False, indent=1))
        return 0
    print(f"{data.get('totalHits', 0)} results (Pixabay returns at most 500 per query); page {args.page}")
    for h in hits:
        sizes = ", ".join(h["sizes"]) if not args.video else ", ".join(f"{k} {v}" for k, v in h["sizes"].items())
        extra = f"{h.get('duration_s')} s" if args.video else h["size"]
        print(f"- {h['id']}  {extra}  [{h['tags']}] by {h['user']}\n    {h['page']}\n    sizes: {sizes}")
    print("Source: Pixabay (pixabay.com). Download with: pixabay.py download <id> --out <folder>")
    return 0


def fetch_hit(item_id, video, no_cache=False):
    data = api_get("videos/" if video else "", {"id": str(item_id)}, use_cache=not no_cache)
    hits = data.get("hits") or []
    if not hits:
        fail(f"no {'video' if video else 'image'} with id {item_id} (use --video for video ids)")
    return hits[0]


def cmd_get(args):
    hit = fetch_hit(args.id, args.video, args.no_cache)
    print(json.dumps(summarize(hit, args.video), ensure_ascii=False, indent=1))
    return 0


def pick_url(hit, video, size):
    if video:
        files = dict(video_files(hit))
        order = VIDEO_SIZES[VIDEO_SIZES.index(size):] + list(reversed(VIDEO_SIZES[:VIDEO_SIZES.index(size)]))
        for s in order:
            if s in files:
                if s != size:
                    print(f"note: size '{size}' not available for this clip, using '{s}'", file=sys.stderr)
                return files[s]["url"], s, f"{files[s].get('width')}x{files[s].get('height')}"
        fail("this video has no downloadable files")
    field = IMAGE_SIZES[size]
    url = hit.get(field)
    if not url:
        if size in ("full", "original", "vector"):
            fail(f"'{size}' needs full API access, which Pixabay grants on request; use --size large (1280 px)")
        fail(f"size '{size}' not available for this image")
    return url, size, None


class PixabayOnlyRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not host_allowed(newurl):
            fail(f"download was redirected to {urllib.parse.urlsplit(newurl).hostname}, not pixabay.com; stopped")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url, dest):
    if not host_allowed(url):
        fail(f"refusing to download from {urllib.parse.urlsplit(url).hostname}: not a pixabay.com address")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    opener = urllib.request.build_opener(PixabayOnlyRedirects)
    tmp = dest + ".part"
    total = 0
    try:
        with opener.open(req, timeout=120) as r:
            with open(tmp, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        f.close()
                        os.remove(tmp)
                        fail("file is larger than 500 MB; stopped")
                    f.write(chunk)
    except urllib.error.HTTPError as e:
        fail(f"download failed: HTTP {e.code} (image URLs expire after 24 h; run the command again)")
    except (urllib.error.URLError, OSError) as e:
        fail(f"download failed: {getattr(e, 'reason', e)}")
    os.replace(tmp, dest)
    return total


def write_credits(out_dir, entry):
    jpath = os.path.join(out_dir, CREDITS_JSON)
    items = []
    if os.path.isfile(jpath):
        try:
            with open(jpath, encoding="utf-8") as f:
                items = json.load(f)
        except ValueError:
            items = []
    items = [i for i in items if i.get("file") != entry["file"]] + [entry]
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    lines = ["# Pixabay credits", "",
             "Content from Pixabay under the Pixabay Content License (https://pixabay.com/service/license-summary/). "
             "Attribution isn't required; this list records where each file came from.", "",
             "| File | Pixabay page | Author | Type | Downloaded |", "|---|---|---|---|---|"]
    for i in items:
        lines.append(f"| {i['file']} | {i['page']} | {i['user']} | {i['kind']} | {i['date']} |")
    with open(os.path.join(out_dir, CREDITS_MD), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def cmd_download(args):
    size = args.size or ("medium" if args.video else "large")
    if args.video and size not in VIDEO_SIZES:
        fail(f"video sizes: {', '.join(VIDEO_SIZES)}")
    if not args.video and size not in IMAGE_SIZES:
        fail(f"image sizes: {', '.join(IMAGE_SIZES)}")
    # Fresh lookup: image URLs from the API are only valid for 24 h.
    hit = fetch_hit(args.id, args.video, no_cache=True)
    url, got, dims = pick_url(hit, args.video, size)
    ext = os.path.splitext(urllib.parse.urlsplit(url).path)[1].lower() or (".mp4" if args.video else ".jpg")
    if not re.fullmatch(r"\.[a-z0-9]{2,5}", ext):
        ext = ".mp4" if args.video else ".jpg"
    os.makedirs(args.out, exist_ok=True)
    name = f"pixabay_{hit.get('id')}_{slug(args.name or first_tag(hit))}_{got}{ext}"
    dest = os.path.join(args.out, name)
    if os.path.exists(dest) and not args.force:
        fail(f"{dest} already exists (use --force)")
    nbytes = download(url, dest)
    entry = {"file": name, "id": hit.get("id"), "page": hit.get("pageURL"), "user": hit.get("user"),
             "kind": ("video " if args.video else "image ") + got + (f" {dims}" if dims else ""),
             "tags": hit.get("tags"), "date": time.strftime("%Y-%m-%d")}
    write_credits(args.out, entry)
    print(json.dumps({"file": dest, "bytes": nbytes, "size": got, "page": hit.get("pageURL"),
                      "credits": os.path.join(args.out, CREDITS_MD)}, ensure_ascii=False))
    return 0


def per_page(text):
    n = int(text)
    if not 3 <= n <= 200:
        raise argparse.ArgumentTypeError("must be 3-200 (Pixabay limit)")
    return n


def main(argv=None):
    p = argparse.ArgumentParser(description="Pixabay images and videos for game/UI assets")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="search images (or --video)")
    s.add_argument("query")
    s.add_argument("--video", action="store_true")
    s.add_argument("--type", default="all", choices=["all", "photo", "illustration", "vector"])
    s.add_argument("--video-type", default="all", choices=["all", "film", "animation"])
    s.add_argument("--orientation", default="all", choices=["all", "horizontal", "vertical"])
    s.add_argument("--category", help="e.g. backgrounds, food, places, buildings, transportation, nature")
    s.add_argument("--colors", help="images: e.g. grayscale,transparent,red")
    s.add_argument("--min-width", type=int)
    s.add_argument("--min-height", type=int)
    s.add_argument("--editors-choice", action="store_true")
    s.add_argument("--order", default="popular", choices=["popular", "latest"])
    s.add_argument("--lang", help="search language, e.g. en, zh (default en)")
    s.add_argument("--per-page", type=per_page, default=20, metavar="3-200")
    s.add_argument("--page", type=int, default=1)
    s.add_argument("--no-safesearch", action="store_true")
    s.add_argument("--no-cache", action="store_true")
    s.add_argument("--json", action="store_true")

    g = sub.add_parser("get", help="details for one id")
    g.add_argument("id", type=int)
    g.add_argument("--video", action="store_true")
    g.add_argument("--no-cache", action="store_true")

    d = sub.add_parser("download", help="download one id into a folder and update the credits file")
    d.add_argument("id", type=int)
    d.add_argument("--out", required=True)
    d.add_argument("--video", action="store_true")
    d.add_argument("--size", help="images: preview|web|large (default large, 1280 px); videos: large|medium|small|tiny (default medium)")
    d.add_argument("--name", help="name part of the file (default: first tag)")
    d.add_argument("--force", action="store_true")

    args = p.parse_args(argv)
    return {"search": cmd_search, "get": cmd_get, "download": cmd_download}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
