#!/usr/bin/env python3
"""Read-only inventory of scoped GTA asset files; never parses or executes assets."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

EXTENSIONS = {".ydr", ".ydd", ".ytd", ".yft", ".ytyp", ".ymap",
              ".ybn", ".ycd", ".ymt", ".awc", ".ymf"}


def is_link(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def catalog(root, include_hash=False):
    root = Path(root).absolute()
    if is_link(root):
        raise ValueError("root must not be a symlink or reparse point")
    if not root.is_dir():
        raise ValueError("root must be a directory")
    entries, findings = [], []

    def issue(path, reason):
        findings.append({"path": str(Path(path).relative_to(root)), "reason": reason})

    def walk_error(error):
        issue(Path(error.filename), "unreadable_directory")

    for base, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(base)
        keep = []
        for name in sorted(dirs):
            p = base / name
            try:
                if is_link(p):
                    issue(p, "skipped_link_or_reparse_point")
                else:
                    keep.append(name)
            except OSError:
                issue(p, "unreadable_directory")
        dirs[:] = keep
        for name in sorted(files):
            p = base / name
            if p.suffix.lower() not in EXTENSIONS:
                continue
            try:
                if is_link(p):
                    issue(p, "skipped_link_or_reparse_point")
                    continue
                before = p.stat()
                if not stat.S_ISREG(before.st_mode):
                    issue(p, "not_regular_file")
                    continue
                digest = None
                if include_hash:
                    h = hashlib.sha256()
                    with p.open("rb") as stream:
                        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                            h.update(chunk)
                    after = p.stat()
                    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                        issue(p, "changed_during_scan")
                    else:
                        digest = h.hexdigest()
                resource = None
                for parent in (p.parent, *p.parent.parents):
                    if parent != root and root not in parent.parents:
                        break
                    manifests = [parent / "fxmanifest.lua", parent / "__resource.lua"]
                    if any(m.is_file() and not is_link(m) for m in manifests):
                        resource = parent.relative_to(root).as_posix()
                        break
                entries.append({
                    "path": p.relative_to(root).as_posix(), "resource": resource,
                    "extension": p.suffix.lower(), "bytes": before.st_size,
                    "modified_utc": datetime.fromtimestamp(before.st_mtime, timezone.utc).isoformat(),
                    "sha256": digest, "preview_status": "not_generated",
                    "format_validation": "not_performed"})
            except OSError:
                issue(p, "unreadable_file")
    entries.sort(key=lambda x: x["path"])
    by_name, by_hash = defaultdict(list), defaultdict(list)
    for entry in entries:
        by_name[Path(entry["path"]).name.casefold()].append(entry["path"])
        if entry["sha256"]:
            by_hash[entry["sha256"]].append(entry["path"])
    return {
        "root": str(root), "entries": entries, "findings": findings,
        "potential_filename_collisions": {k: v for k, v in by_name.items() if len(v) > 1},
        "identical_content_groups": {k: v for k, v in by_hash.items() if len(v) > 1},
        "not_checked": ["game load", "spawn names", "texture validity",
                        "licensing", "geometry", "preview appearance"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--hash", action="store_true")
    args = parser.parse_args()
    try:
        result = catalog(args.root, args.hash)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
        return 1 if result["findings"] else 0
    except (OSError, ValueError) as error:
        print(f"catalog_assets: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
