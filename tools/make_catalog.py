#!/usr/bin/env python3
"""Builds this Store source's catalog from apps.json: dist/ gets catalog.json, every package and every icon,
ready to upload as the assets of the GitHub release tagged `catalog` (tools/publish.ps1 does both).

apps.json lists each component the source offers: an app or tool with its package file in packages/
(not committed: release assets only) and, optionally, an icon in icons/ (PNG, at most 128 KiB).
Requirements may name components of other sources (Node.js 22 for RideTube comes from JustAnotherPU/mgu-apps).

    python3 tools/make_catalog.py [--repo owner/name] [--private]

--repo: where the release lives (default: the `origin` remote's GitHub repository).
--private: this repository is private, so the car downloads each artifact with its token from the asset's API
    URL (https://api.github.com/repos/<owner>/<repo>/releases/assets/<n>), as the Store's PUBLISHING.md says.
    Those URLs exist once the assets are uploaded: tools/publish.ps1 uploads the packages and icons first, then
    runs this with --private and uploads catalog.json last.
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tarfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ID_RE = re.compile(r'^[a-z0-9][a-z0-9_-]*$')
VER_RE = re.compile(r'^\d+\.\d+\.\d+$')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def origin_repo():
    url = subprocess.run(['git', '-C', ROOT, 'remote', 'get-url', 'origin'], capture_output=True, text=True).stdout.strip()
    m = re.search(r'github\.com[:/]([^/]+/[^/]+?)(\.git)?$', url)
    if not m:
        sys.exit('make_catalog.py: no GitHub origin remote; pass --repo owner/name')
    return m.group(1)


def release_assets(repo):
    """{asset name: its API URL} of the `catalog` release, through the GitHub CLI (signed in)."""
    gh = shutil.which('gh') or r'C:\Program Files\GitHub CLI\gh.exe'
    r = subprocess.run([gh, 'api', 'repos/%s/releases/tags/catalog' % repo, '--jq', '.assets[] | [.name, .url] | @tsv'],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit('make_catalog.py: cannot read the catalog release of %s: %s' % (repo, r.stderr.strip()))
    return dict(line.split('\t', 1) for line in r.stdout.splitlines() if '\t' in line)


def package_version(path):
    """(id, version) from the package's package.json (an app) or component.json (a tool)."""
    with tarfile.open(path, 'r:gz') as t:
        for n in ('package/package.json', 'package.json', 'component.json', './component.json'):
            try:
                j = json.load(t.extractfile(n))
                return j.get('name') or j.get('id'), j.get('version')
            except KeyError:
                continue
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo')
    ap.add_argument('--private', action='store_true')
    a = ap.parse_args()
    repo = a.repo or origin_repo()
    base = 'https://github.com/%s/releases/download/catalog/' % repo
    assets = release_assets(repo) if a.private else None
    spec = json.load(open(os.path.join(ROOT, 'apps.json'), encoding='utf-8'))
    out = os.path.join(ROOT, 'dist')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    comps, seen = [], set()
    for c in spec['components']:
        cid, ver = c['id'], c['version']
        if not ID_RE.match(cid) or cid in seen:
            sys.exit('make_catalog.py: bad or repeated id %r' % cid)
        if not VER_RE.match(ver):
            sys.exit('make_catalog.py: %s: version %r is not x.y.z' % (cid, ver))
        seen.add(cid)
        name = '%s@%s.tgz' % (cid, ver)
        src = os.path.join(ROOT, 'packages', name)
        if not os.path.isfile(src):
            sys.exit('make_catalog.py: packages/%s missing' % name)
        pid, pver = package_version(src)
        if (pid, pver) != (cid, ver) and not c.get('build') == 'unit':
            sys.exit('make_catalog.py: packages/%s says %s@%s' % (name, pid, pver))
        shutil.copy(src, os.path.join(out, name))
        e = {k: c[k] for k in ('id', 'kind', 'title', 'description', 'author', 'version') if k in c}
        if assets is not None and name not in assets:
            sys.exit('make_catalog.py: %s is not uploaded to the catalog release yet (tools/publish.ps1 uploads it first)' % name)
        url = assets[name] if assets is not None else base + name
        e['artifact'] = {'name': name, 'size': os.path.getsize(src), 'sha256': sha256(src), 'url': url}
        for k in ('build', 'requires', 'optional', 'uninstallable', 'mguHmi', 'mguProvides'):
            if k in c:
                e[k] = c[k]
        if c.get('icon'):
            ic = os.path.join(ROOT, 'icons', c['icon'])
            if os.path.getsize(ic) > 128 * 1024:
                sys.exit('make_catalog.py: icons/%s is over 128 KiB' % c['icon'])
            shutil.copy(ic, os.path.join(out, c['icon']))
            e['icon'], e['iconSha256'] = c['icon'], sha256(ic)
        comps.append(e)
    with open(os.path.join(out, 'catalog.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'schema': 2, 'components': comps}, f, indent=2, ensure_ascii=False)
        f.write('\n')
    for n in sorted(os.listdir(out)):
        print('%10d  %s' % (os.path.getsize(os.path.join(out, n)), n))


if __name__ == '__main__':
    main()
