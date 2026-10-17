#!/usr/bin/env python3
"""Read one stable regular file; emit hashes and tentative format evidence only."""
import argparse
import codecs
import hashlib
import json
import os
from pathlib import Path
import stat

PREFIX_BYTES = 4096
BLOCK_BYTES = 1024 * 1024


def is_linklike(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def identity(info):
    return info.st_dev, info.st_ino


def snapshot(info):
    return identity(info), info.st_size, info.st_mtime_ns


def classify(prefix, size):
    hints = {'complete_format_validation': False, 'encryption': 'not determined'}
    if size == 0:
        return dict(hints, candidate='empty')
    if prefix.startswith(b'\x1bLua'):
        version = prefix[4] if len(prefix) > 4 else None
        label = f'{version >> 4}.{version & 15}' if version is not None else None
        return dict(hints, candidate='lua-bytecode-signature', version_byte_hint=label,
                    format_byte_hint=prefix[5] if len(prefix) > 5 and version in (0x51, 0x52, 0x53, 0x54) else None,
                    six_byte_prefix_truncated=len(prefix) < 6)
    if any(value < 32 and value not in (9, 10, 13) for value in prefix):
        return dict(hints, candidate='unknown-binary')
    try:
        decoder = codecs.getincrementaldecoder('utf-8')('strict')
        decoded = decoder.decode(prefix, final=size <= len(prefix))
    except UnicodeDecodeError:
        return dict(hints, candidate='unknown-binary')
    if not decoded:
        return dict(hints, candidate='unknown-binary')
    return dict(hints, candidate='utf8-text-prefix', whole_file_text_validated=False)


def inspect_file(filename):
    path = Path(os.path.abspath(os.fspath(filename)))
    report = {'path': str(path), 'status': 'error', 'executed_input': False,
              'content_written': False, 'suffix_hint': path.suffix.lower(),
              'limits': 'Header evidence only; stable input required; not an adversarial path sandbox.'}
    try:
        before = path.lstat()
        if is_linklike(before) or not stat.S_ISREG(before.st_mode):
            report['error'] = 'Input is a link, reparse point or non-regular file.'
            return report, 2
        digest = hashlib.sha256()
        prefix = b''
        total = 0
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or snapshot(before) != snapshot(opened):
                report['error'] = 'Input identity or metadata changed before reading.'
                return report, 2
            while True:
                block = stream.read(BLOCK_BYTES)
                if not block:
                    break
                if len(prefix) < PREFIX_BYTES:
                    prefix += block[:PREFIX_BYTES-len(prefix)]
                digest.update(block)
                total += len(block)
            after = os.fstat(stream.fileno())
        current = path.lstat()
        if (is_linklike(current) or not stat.S_ISREG(current.st_mode)
                or snapshot(before) != snapshot(after)
                or snapshot(before) != snapshot(current) or total != before.st_size):
            report['error'] = 'Input changed during inspection; hash not accepted.'
            return report, 2
        report.update(status='read-complete', size_bytes=total, sha256=digest.hexdigest(),
                      prefix_bytes_inspected=len(prefix), evidence=classify(prefix, total))
        return report, 0
    except (OSError, ValueError):
        report['error'] = 'Input missing, unreadable or invalid; no encryption conclusion.'
        return report, 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', help='One explicit local regular file; originals are read only.')
    args = parser.parse_args()
    report, code = inspect_file(args.file)
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
