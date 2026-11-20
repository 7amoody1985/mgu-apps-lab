# Publishing to 7amoody1985/mgu-apps-lab (for agents)

This repository is a **public test** MGU Store source (BMW iDrive 7 head units): the user's personal, very experimental
apps (the RideTube fork, CarLink). Released apps go to the public source 7amoody1985/mgu-apps (`..\mgu-apps`), never
here. An app is in one of the two, never both: the Store refuses a catalog package whose id another source's app
already holds on the car. The repository is public (since 2026-11-18) so the car reads it without a token; its
README warns visitors that it is a test source, not for general use. Keep that warning.

The car reads `catalog.json` from the GitHub release tagged `catalog`; that file lists **every** app of this source.
`apps.json` (committed) is the list it is made from. Packages are release assets only, never committed.

- Local checkout: `C:\Users\PC\Documents\Code\Personal\bmw-idrive-apps\mgu-apps-lab`
- GitHub: https://github.com/7amoody1985/mgu-apps-lab (public; the GitHub CLI is installed and signed in as
  7amoody1985; `gh` may not be on PATH: `C:\Program Files\GitHub CLI\gh.exe`)
- The Store's own rules: https://github.com/robertnisipeanu/mgu-store/blob/main/docs/PUBLISHING.md

## Publish a new app, or a new version

1. **Check the package** (`<id>@<x.y.z>.tgz`, an OAP package with its files under `package/` or at the root):
   - its `package.json` `name` is the id and `version` the same x.y.z;
   - **no `node_modules/oap-sdk`** in it (BMW's SDK is not redistributable; the head unit generates it);
   - the id has the prefix **`mdq_`** / **`mdq-`**, never an id BMW or another source uses;
   - `"mguInternet": true` in `package.json` if it needs the internet;
   - a native daemon or binary ships as a separate tool kit (`kind: "tool"`, a tgz with `component.json`),
     listed as its own entry and named in the app's `requires`.
2. **Copy it** to `packages\` (git-ignored).
3. **Add or update its entry in `apps.json`**; leave the other entries alone. A new version: bump `version` here
   and in the file name.
4. **Publish**: `powershell -NoProfile -ExecutionPolicy Bypass -File tools\publish.ps1` (needs Python 3). It runs
   `tools/make_catalog.py` (writes `dist\`, checks names and versions, the release's public download URLs) and
   uploads all of `dist\` to the `catalog` release, deleting assets no longer listed.
   All of `packages\` must be there for every entry: if one is missing, download it from the release first
   (`gh release download catalog --pattern "<id>@<version>.tgz" --dir packages`).
5. **Verify**: `python -I tools/verify.py` (downloads the published catalog anonymously, as the car does). It must
   end with `all ok`.
6. **Commit and push** `apps.json` (and `icons\`, `README.md`). Commits use the repo's local identity (the GitHub
   noreply address): do not change it.
7. Tell the user: in the Store, **Settings → Check now**, then install or update the app.

## Do not

- Commit packages, `dist\` or anything holding BMW's SDK.
- Put a token, key, VIN or anything else private in any file or release asset here: the repository is public.
- Remove the README's warning that this is a test source, not for general use.
- Change how the `mdq_ridetube` / `mdq-ridetube-d` packages are made: since 2026-11-20 they come from the RideTube
  fork's branch `lab-ram` (https://github.com/7amoody1985/ridetube, checkout `..\ridetube`), its
  `tools/lab_build.sh` (JustAnotherPU's RideTube with the RAM streaming and the stats overlay, renamed to the
  `mdq` ids in a copy). The fork's branch `ram-streaming` keeps his ids: it is the pull request, never built here.
- List an app here that the public source `mgu-apps` also lists.
- Re-create or rename the `catalog` release, or publish it as a draft or prerelease: the Store reads only a
  published release named exactly `catalog`.
