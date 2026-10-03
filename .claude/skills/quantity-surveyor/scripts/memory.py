#!/usr/bin/env python3
"""Optional, explicit user/project scoped local memory. Python standard library only."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid


def now():
    return datetime.now(timezone.utc).isoformat()


def validate_record(record):
    if not isinstance(record, dict):
        raise ValueError('record must be an object')
    for field in ('summary',):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(field + ' must be nonempty text')
    if record.get('status') not in ('tentative', 'verified', 'superseded'):
        raise ValueError('invalid status')
    if record.get('kind') not in ('decision', 'observation', 'lesson'):
        raise ValueError('invalid kind')
    evidence = record.get('evidence')
    if not isinstance(evidence, list) or not evidence:
        raise ValueError('nonempty evidence list required')
    for entry in evidence:
        if not isinstance(entry, dict) or any(
            not isinstance(entry.get(key), str) or not entry[key].strip()
            for key in ('source', 'locator', 'verification')
        ):
            raise ValueError('evidence needs source, locator and verification')
    if 'details' in record and not isinstance(record['details'], dict):
        raise ValueError('details must be an object')


def validate(data, scope):
    if not isinstance(data, dict) or data.get('schema') != 1 or data.get('scope') != scope:
        raise ValueError('invalid schema or scope mismatch')
    rows = data.get('records')
    if not isinstance(rows, list):
        raise ValueError('invalid records')
    by_id = {}
    for row in rows:
        validate_record(row)
        if row.get('scope') != scope or not isinstance(row.get('created_at'), str):
            raise ValueError('record scope or timestamp missing')
        rid = row.get('id')
        if not isinstance(rid, str) or not rid or rid in by_id:
            raise ValueError('missing or duplicate record id')
        by_id[rid] = row
    for row in rows:
        if row['status'] == 'superseded':
            replacement = by_id.get(row.get('superseded_by'))
            if replacement is None or replacement.get('replaces') != row['id']:
                raise ValueError('broken correction history')
        if 'replaces' in row:
            prior = by_id.get(row['replaces'])
            if prior is None or prior.get('superseded_by') != row['id']:
                raise ValueError('broken correction link')
    return data


def read(path, scope, allow_missing=False):
    if not path.exists():
        if allow_missing:
            if path.with_suffix('.previous.json').exists():
                raise ValueError('primary store missing but previous copy exists; inspect and recover explicitly')
            return {'schema': 1, 'scope': scope, 'records': []}
        raise ValueError('store does not exist')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError('unreadable/corrupt store: ' + str(exc)) from exc
    return validate(data, scope)


def atomic(path, data):
    encoded = (json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        # Best effort directory sync where supported. Atomic replacement is required.
        try:
            directory = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError:
            pass
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = path.with_suffix('.lock')
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError('store locked; do not remove lock until no writer is active') from exc
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write(json.dumps({'pid': os.getpid(), 'at': now()}))
        yield
    finally:
        lock.unlink()


def new_record(file, scope):
    incoming = json.loads(Path(file).read_text(encoding='utf-8'))
    validate_record(incoming)
    if incoming['status'] == 'superseded':
        raise ValueError('new records cannot be superseded')
    # Only public input fields; identities/correction links cannot be injected.
    record = {key: incoming[key] for key in ('summary', 'kind', 'status', 'evidence', 'details') if key in incoming}
    record.update(id=uuid.uuid4().hex, scope=scope, created_at=now())
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--user', required=True)
    parser.add_argument('--project', required=True)
    subs = parser.add_subparsers(dest='command', required=True)
    add = subs.add_parser('add')
    add.add_argument('--file', required=True)
    listing = subs.add_parser('list')
    listing.add_argument('--status', choices=('tentative', 'verified', 'superseded', 'all'), default='verified')
    correction = subs.add_parser('correct')
    correction.add_argument('id')
    correction.add_argument('--file', required=True)
    subs.add_parser('check')
    recover = subs.add_parser('recover')
    recover.add_argument('--confirm', action='store_true')
    args = parser.parse_args()
    if not args.user.strip() or not args.project.strip() or not args.root.strip():
        raise ValueError('root and scope identifiers must be explicit and nonempty')
    scope = {'user': args.user, 'project': args.project}
    key = hashlib.sha256(json.dumps(scope, sort_keys=True).encode()).hexdigest()
    path = Path(args.root).expanduser().resolve() / (key + '.json')
    backup = path.with_suffix('.previous.json')
    if args.command in ('list', 'check'):
        data = read(path, scope, allow_missing=True)
        if args.command == 'list':
            result = [row for row in data['records'] if args.status == 'all' or row['status'] == args.status]
        else:
            result = {'ok': True, 'exists': path.exists(), 'records': len(data['records']), 'scope': scope}
    elif args.command == 'recover':
        if not args.confirm:
            raise ValueError('recovery requires --confirm after inspecting current and previous copies')
        with locked(path):
            previous = read(backup, scope)
            archived = None
            if path.exists():
                archived = path.with_suffix('.recovery-' + uuid.uuid4().hex + '.json')
                # Copy bytes before rollback; never silently discard current/damaged state.
                archived.write_bytes(path.read_bytes())
                os.chmod(archived, 0o600)
            atomic(path, previous)
        result = {'ok': True, 'restored': str(path), 'preserved_current': str(archived) if archived else None}
    else:
        replacement = new_record(args.file, scope)
        with locked(path):
            data = read(path, scope, allow_missing=True)
            old = json.loads(json.dumps(data))
            if args.command == 'correct':
                candidates = [row for row in data['records'] if row['id'] == args.id]
                if len(candidates) != 1:
                    raise ValueError('record id not found in this scope')
                prior = candidates[0]
                if prior['status'] == 'superseded':
                    raise ValueError('record already superseded; correct the current record')
                if prior['status'] == 'verified' and replacement['status'] != 'verified':
                    raise ValueError('tentative correction cannot supersede verified evidence')
                prior['previous_status'] = prior['status']
                prior['status'] = 'superseded'
                prior['superseded_by'] = replacement['id']
                prior['superseded_at'] = now()
                replacement['replaces'] = prior['id']
            data['records'].append(replacement)
            validate(data, scope)
            atomic(backup, old)
            atomic(path, data)
        result = replacement
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(2)
