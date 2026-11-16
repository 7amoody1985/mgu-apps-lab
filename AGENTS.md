# Publishing to 7amoody1985/mgu-apps-lab (for agents)

This repository is a **private** MGU Store source (BMW iDrive 7 head units): the user's personal, very experimental
apps (the RideTube fork, CarLink). Released apps go to the public source 7amoody1985/mgu-apps (`..\mgu-apps`), never
here. An app is in one of the two, never both: the Store refuses a catalog package whose id another source's app
already holds on the car. The repository stays private: each car reads it with its own read-only token.

The car reads `catalog.json` from the GitHub release tagged `catalog`; that file lists **every** app of this source.
`apps.json` (committed) is the list it is made from. Packages are release assets only, never committed.

- Local checkout: `C:\Users\PC\Documents\Code\Personal\bmw-idrive-apps\mgu-apps-lab`
- GitHub: https://github.com/7amoody1985/mgu-apps-lab (private; the GitHub CLI is installed and signed in as
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
   `tools/make_catalog.py` (writes `dist\`, checks names and versions), uploads the packages and icons to the
   `catalog` release, then writes `catalog.json` with their API URLs (`make_catalog.py --private`: a private
   repository's assets download only that way, with a token) and uploads it last, deleting assets no longer listed.
   All of `packages\` must be there for every entry: if one is missing, download it from the release first
   (`gh release download catalog --pattern "<id>@<version>.tgz" --dir packages`).
5. **Verify**: `python -I tools/verify.py` (downloads the published catalog with the GitHub CLI's token, as the car
   does with its own, and checks that nothing downloads without one). It must end with `all ok`.
6. **Commit and push** `apps.json` (and `icons\`, `README.md`). Commits use the repo's local identity (the GitHub
   noreply address): do not change it.
7. Tell the user: in the Store, **Settings → Check now**, then install or update the app.

## Do not

- Commit packages, `dist\` or anything holding BMW's SDK.
- Make the repository public, or put a token in any file here: each car has its own read-only token, which the user
  makes (README.md, "Add it to a car").
- Change how the `mdq_ridetube` / `mdq-ridetube-d` packages are made: they come from the RideTube fork
  (https://github.com/7amoody1985/ridetube, checkout `..\ridetube`), its `tools/build_app.sh` and
  `tools/build_service.sh`.
- List an app here that the public source `mgu-apps` also lists.
- Re-create or rename the `catalog` release, or publish it as a draft or prerelease: the Store reads only a
  published release named exactly `catalog`.
