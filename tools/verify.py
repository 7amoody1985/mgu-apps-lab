#!/usr/bin/env python3
"""Checks the published catalog as the car reads it: with a token (this repository is private), the catalog.json of
the `catalog` release and every artifact and icon from their API URLs, against the catalog's size and sha256; the
package naming its id and version, no BMW SDK in it, and every component of apps.json listed at its version. The
token is the GitHub CLI's (`gh auth token`); it is never printed.

    python3 tools/verify.py [--repo owner/name]
"""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tarfile, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_catalog import ROOT, origin_repo, release_assets      # noqa: E402

GH = shutil.which('gh') or r'C:\Program Files\GitHub CLI\gh.exe'


def token():
    r = subprocess.run([GH, 'auth', 'token'], capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        sys.exit('verify.py: no GitHub CLI token (gh auth login)')
    return r.stdout.strip()


def get(url, tok):
    """An asset by its API URL, as the car fetches it with its token."""
    req = urllib.request.Request(url, headers={'User-Agent': 'mgu-apps-lab-verify', 'Accept': 'application/octet-stream',
                                               'Authorization': 'Bearer ' + tok})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo')
    a = ap.parse_args()
    repo = a.repo or origin_repo()
    tok = token()
    assets = release_assets(repo)
    if 'catalog.json' not in assets:
        sys.exit('verify.py: no catalog.json in the catalog release (run tools/publish.ps1)')
    # anonymous downloads must fail: the source is private
    try:
        urllib.request.urlopen(urllib.request.Request('https://github.com/%s/releases/download/catalog/catalog.json' % repo,
                                                      headers={'User-Agent': 'mgu-apps-lab-verify'}), timeout=30)
        print('FAIL the catalog downloads without a token: is the repository public?')
        anon_bad = 1
    except Exception:
        anon_bad = 0
    cat = json.loads(get(assets['catalog.json'], tok))
    want = {c['id']: c['version'] for c in json.load(open(os.path.join(ROOT, 'apps.json'), encoding='utf-8'))['components']}
    bad = anon_bad
    for e in cat['components']:
        art = e['artifact']
        msg = []
        if not art['url'].startswith('https://api.github.com/repos/%s/releases/assets/' % repo):
            msg.append('url is not the asset\'s API URL: %s' % art['url'])
        data = get(art['url'], tok)
        ok = len(data) == art['size'] and hashlib.sha256(data).hexdigest() == art['sha256']
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as t:
            names = t.getnames()
        if not ok:
            msg.append('size/sha256 differ from the catalog')
        if any('node_modules/oap-sdk' in n for n in names):
            msg.append('BMW oap-sdk inside: must not be published')
        if want.get(e['id']) != e['version']:
            msg.append('apps.json says %s' % want.get(e['id']))
        if e.get('icon'):
            if e['icon'] not in assets:
                msg.append('icon %s not in the release' % e['icon'])
            else:
                ic = get(assets[e['icon']], tok)
                if e.get('iconSha256') and hashlib.sha256(ic).hexdigest() != e['iconSha256']:
                    msg.append('icon sha256 differs')
        bad += bool(msg)
        print('%-4s %s@%s  %d bytes%s' % ('FAIL' if msg else 'ok', e['id'], e['version'], len(data), ': ' + '; '.join(msg) if msg else ''))
    for cid in sorted(set(want) - {e['id'] for e in cat['components']}):
        bad += 1
        print('FAIL %s: in apps.json, not in the published catalog (run tools/publish.ps1)' % cid)
    print('published catalog: ' + ('%d problem(s)' % bad if bad else 'all ok (private: no download without a token)'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
