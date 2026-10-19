"""Resolve official channels once; write the CI build matrix and manifest."""
import base64
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path


def gh(path):
    return json.loads(subprocess.check_output(['gh', 'api', f'repos/gprMax/gprMax/{path}'], text=True))


def commit(ref):
    obj = gh(f'git/ref/{ref}')['object']
    while obj['type'] == 'tag':
        obj = gh('git/tags/' + obj['sha'])['object']
    if obj['type'] != 'commit':
        raise ValueError(obj)
    return obj['sha']


def main():
    releases = gh('releases?per_page=100')
    packaging = os.environ['GITHUB_SHA']
    # Documentation-only commits must not force a scheduled rebuild.
    inputs = [Path('Dockerfile.cpu'), Path('Dockerfile.gpu'), Path('.github/workflows/publish.yml')]
    inputs += sorted(p for p in Path('scripts').iterdir() if p.is_file())
    fingerprint = hashlib.sha256(b''.join(str(p).encode() + b'\0' + p.read_bytes() for p in inputs)).hexdigest()
    image = os.environ['IMAGE']
    entries, channels = [], []
    for channel in ['v4', 'v3', 'devel']:
        if channel == 'devel':
            revision = commit('heads/master')
            content = base64.b64decode(gh(f'contents/gprMax/_version.py?ref={revision}')['content']).decode()
            version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]+)', content, re.M)[1]
            source = 'master'
        else:
            matches = []
            for release in releases:
                match = re.fullmatch(r'v\.(\d+)\.(\d+)\.(\d+)', release['tag_name'])
                if match and not release['draft'] and not release['prerelease'] and match[1] == channel[1:]:
                    matches.append((tuple(map(int, match.groups())), release['tag_name']))
            source = max(matches)[1]
            version = source[2:]
            revision = commit('tags/' + source)
        row = dict(channel=channel, version=version, revision=revision, source=source, packaging=packaging)
        candidates = [f'{image}:build-{fingerprint[:12]}-{revision[:12]}-{channel}-{kind}' for kind in ['cpu', 'gpu']]
        exists = os.environ.get('GITHUB_EVENT_NAME') == 'schedule' and all(
            published(candidate, f'{image}:{channel}-{kind}')
            for kind, candidate in zip(['cpu', 'gpu'], candidates)
        )
        row['rebuild'] = not exists
        channels.append(row)
        if exists:
            continue
        for kind, candidate in zip(['cpu', 'gpu'], candidates):
            tags = [f'{image}:{channel}-{kind}']
            if channel != 'devel':
                tags.append(f'{image}:{version}-{kind}')
            if channel == 'v4':
                tags.append(f'{image}:latest-{kind}')
            entries.append(dict(row, kind=kind, candidate=candidate, tags=tags))
    Path('channels.json').write_text(json.dumps(channels, indent=2) + '\n')
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        print('matrix=' + json.dumps({'include': entries}), file=output)
        print('changed=' + str(bool(entries)).lower(), file=output)
    print(json.dumps(channels, indent=2))


def published(candidate, alias):
    # A pushed candidate alone does not prove that promotion succeeded.
    manifests = [subprocess.run(['docker', 'manifest', 'inspect', ref], capture_output=True, text=True) for ref in [candidate, alias]]
    return all(p.returncode == 0 for p in manifests) and json.loads(manifests[0].stdout) == json.loads(manifests[1].stdout)


if __name__ == '__main__':
    main()
