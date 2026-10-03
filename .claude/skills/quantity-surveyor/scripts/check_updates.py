#!/usr/bin/env python3
"""Optional read-only release checker. No state, credentials, downloads or installs."""
import argparse
from http.client import HTTPException
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

REPOSITORY = 'MuscleOtter/quantity-surveyor'
RELEASES = 'https://github.com/' + REPOSITORY + '/releases'
API = 'https://api.github.com/repos/' + REPOSITORY + '/releases/latest'
MAX_BYTES = 1024 * 1024


def version(value):
    if not isinstance(value, str) or not re.fullmatch(r'v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', value):
        raise ValueError('expected a stable major.minor.patch version')
    return tuple(int(part) for part in value.removeprefix('v').split('.'))


def compare(current, release):
    """Treat remote metadata as data. Accept only stable releases of this repository."""
    local = version(current)
    if not isinstance(release, dict):
        raise ValueError('release metadata must be an object')
    if release.get('draft') is not False or release.get('prerelease') is not False:
        raise ValueError('not a published stable release')
    tag = release.get('tag_name')
    remote = version(tag)
    expected_url = RELEASES + '/tag/' + tag
    if release.get('html_url') != expected_url:
        raise ValueError('unexpected release URL')
    return {
        'status': 'update_available' if remote > local else 'current' if remote == local else 'local_ahead',
        'installed_version': current,
        'latest_version': tag.removeprefix('v'),
        'release_url': expected_url,
        'action': 'Read the release notes and ask the user before installation.' if remote > local else 'No replacement needed.',
    }


def check(current, online=False):
    version(current)
    if not online:
        return {'status': 'not_checked', 'installed_version': current, 'releases_url': RELEASES,
                'action': 'Open Releases manually or explicitly enable an online check.'}
    request = urllib.request.Request(API, headers={
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'quantity-surveyor-release-check',
        'X-GitHub-Api-Version': '2026-03-10',
    })
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            raise ValueError('release metadata too large')
        return compare(current, json.loads(payload))
    except (OSError, ValueError, HTTPException):
        # Do not echo arbitrary server content, local paths or untrusted release prose.
        return {'status': 'unavailable', 'installed_version': current, 'releases_url': RELEASES,
                'reason': 'Public release metadata could not be verified.',
                'action': 'Continue the QS task; check Releases manually when useful.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--online', action='store_true', help='Explicitly fetch public GitHub stable-release metadata')
    args = parser.parse_args()
    try:
        manifest = json.loads((Path(__file__).resolve().parents[1] / 'version.json').read_text(encoding='utf-8'))
        result = check(manifest['version'], online=args.online)
    except (OSError, ValueError, KeyError, TypeError):
        result = {'status': 'unavailable', 'reason': 'Installed version manifest could not be verified.'}
    print(json.dumps(result, indent=2))
    # An optional failed check must not block construction cost work.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
