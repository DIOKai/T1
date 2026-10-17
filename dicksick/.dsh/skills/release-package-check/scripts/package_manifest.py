#!/usr/bin/env python3
"""Read-only staging inventory. No archives, installs, execution, or uploads."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat


def required_path(value):
    if (not value or "\\" in value or ":" in value or "\x00" in value
            or any(p in {"", ".", ".."} for p in value.split("/"))):
        raise argparse.ArgumentTypeError("required paths must be normalized relative file paths")
    return value


def linklike(info):
    return (stat.S_ISLNK(info.st_mode)
            or bool(getattr(info, "st_file_attributes", 0) & 0x400))


def inventory(root, required=()):
    root = Path(os.path.abspath(os.fspath(root)))
    report = {"root": str(root), "files": [], "findings": [], "required": [],
              "scan_status": "incomplete", "release_approval": "not assessed"}
    findings = report["findings"]

    def finding(kind, path, detail, severity="error"):
        findings.append({"kind": kind, "path": path, "detail": detail, "severity": severity})

    try:
        info = root.lstat()
        if linklike(info) or not stat.S_ISDIR(info.st_mode):
            finding("invalid_root", ".", "root must be a regular directory, not a link/reparse point")
            return report
    except OSError as exc:
        finding("invalid_root", ".", type(exc).__name__)
        return report

    seen = {}
    def register(relative):
        key = relative.casefold()
        previous = seen.get(key)
        if previous is not None and previous != relative:
            finding("case_collision", relative, "collides with " + previous)
        else:
            seen[key] = relative

    def walk_error(exc):
        candidate = Path(exc.filename) if exc.filename else root
        try:
            relative = candidate.relative_to(root).as_posix()
        except ValueError:
            relative = "."
        finding("directory_unreadable", relative, type(exc).__name__)

    for current, dirs, names in os.walk(root, topdown=True, followlinks=False, onerror=walk_error):
        dirs.sort()
        names.sort()
        for name in list(dirs):
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            register(relative)
            try:
                child = path.lstat()
                if linklike(child) or not stat.S_ISDIR(child.st_mode):
                    dirs.remove(name)
                    finding("skipped_link_or_special", relative, "directory was not traversed")
                elif name in {".git", "node_modules", "__pycache__"}:
                    finding("development_directory", relative, "review whether this belongs in the artifact", "warning")
            except OSError as exc:
                dirs.remove(name)
                finding("directory_unreadable", relative, type(exc).__name__)

        for name in names:
            path = Path(current) / name
            relative = path.relative_to(root).as_posix()
            register(relative)
            try:
                before = path.lstat()
                if linklike(before) or not stat.S_ISREG(before.st_mode):
                    finding("skipped_link_or_special", relative, "not hashed")
                    continue
                digest = hashlib.sha256()
                length = 0
                with path.open("rb") as source:
                    while True:
                        chunk = source.read(1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                        length += len(chunk)
                after = path.lstat()
                signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
                if (signature(before) != signature(after) or linklike(after)
                        or length != before.st_size):
                    finding("changed_during_read", relative, "use a stable staging snapshot")
                    continue
                report["files"].append({"path": relative, "size": length, "sha256": digest.hexdigest()})
                low = name.casefold()
                sample_env = low in {".env.example", ".env.sample", ".env.template"}
                if ((low == ".env" or low.startswith(".env.")) and not sample_env
                        or low in {"id_rsa", "id_ed25519", ".npmrc", ".pypirc"}
                        or low.endswith((".pem", ".key", ".p12", ".pfx"))):
                    finding("potential_sensitive_filename", relative,
                            "filename warning only; content not inspected for secrets", "warning")
            except OSError as exc:
                finding("file_unreadable", relative, type(exc).__name__)

    report["files"].sort(key=lambda entry: entry["path"])
    included = {entry["path"] for entry in report["files"]}
    for value in dict.fromkeys(required):
        value = required_path(value)
        present = value in included
        report["required"].append({"path": value, "present": present})
        if not present:
            finding("required_missing", value, "not included as a successfully hashed regular file")
    if not report["files"]:
        finding("empty_package", ".", "no regular files were successfully inventoried")
    if not any(item["severity"] == "error" for item in findings):
        report["scan_status"] = "complete"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="explicit local staging directory")
    parser.add_argument("--required", action="append", type=required_path, default=[])
    args = parser.parse_args()
    report = inventory(args.root, args.required)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["scan_status"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
