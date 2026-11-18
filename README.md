# 7amoody1985's MGU lab

> [!CAUTION]
> **This is my test area, not an app source for general use.** It holds personal, very experimental apps for BMW
> iDrive 7 head units (MGU) that I try on my own car (a G05 X5). They may not work, may break your head unit's
> setup, and can change or disappear without notice. There's no support, and nothing here comes with a warranty.
> Please don't add this source to your car unless you know what you're doing and can recover the head unit
> yourself. Apps I consider ready are in [7amoody1985/mgu-apps](https://github.com/7amoody1985/mgu-apps).

The repository is public so that my own car can read it without a token. You're welcome to read the code, and if
you're a developer and something here is useful to you, feel free to build on it. The RideTube fork stays under its
own licence (GPL-3.0-or-later, see below).

Unofficial: nothing here is made, endorsed or supported by BMW AG, Google or JustAnotherPU.

## Add it to a car (for my own cars)

In the [MGU Store](https://github.com/robertnisipeanu/mgu-store): **Settings → Add source**,
`7amoody1985/mgu-apps-lab`, **Releases**, then **Check now**. No token is needed since the repository went public
(2026-11-18). A car that was set up with a token can keep it, or you can delete the token on github.com
(Settings → Developer settings → Fine-grained tokens).

## Apps

| App | Version | What it is |
|---|---|---|
| RideTube (fork) | app 0.4.0, service 0.4.2 | A modified build of [JustAnotherPU's RideTube](https://github.com/JustAnotherPU/ridetube), a YouTube client. Fixes the Search menu (which holds the settings) closing right after it opens; the service streams the video in RAM instead of writing it to the head unit's flash, and keeps a debug report. Not endorsed by the original developer. Its own ids (`mdq_ridetube`, `mdq-ridetube-d`): it installs beside the original. Source and changes: [7amoody1985/ridetube](https://github.com/7amoody1985/ridetube). |
| CarLink (experimental) | 0.1.4 | The next turn from HudHud or Google Maps on your phone, in the middle of the instrument cluster and as a home-screen widget. **Not yet tried in a car.** Source: `7amoody1985/carlink` (private). |
| Android Auto log (for CarLink) | tool 0.1.1 | The car's Android Auto daemon's log and state, for CarLink's Car log on the phone. Experimental, a debugging aid. |

**Moved here from 7amoody1985/mgu-apps (2026-11-17), ids unchanged.** The Store won't install a catalog package
over an app another source installed: if the car has either installed from `mgu-apps`, uninstall it (the RideTube
app, then its service) and install it again from this source. RideTube needs a YouTube sign-in again after that.

### CarLink (experimental)

- **Status: first version, not yet tried in a car.** Tested on a PC in the kit's emulator only.
- It shows what the CarLink phone app sends: that app reads the navigation notification of HudHud or Google
  Maps and draws the turn card (arrow, distance, street, arrival time). The phone app isn't published yet.
- **The link** (0.1.4): with the car on the phone's hotspot (the Store's Wi-Fi uplink), the car app calls the
  phone (its uplink's router, port 47801): the uplink drops every connection coming in to the car, and lets
  this app out (`mguInternet`). On the car's own Wi-Fi or USB tethering, the phone calls the car (port 47800).
- **Demo** (on the app's screen) shows turns without the phone, to try the cluster and the widget.
- Needs **cluster-render**, the cluster renderer from the `robertnisipeanu/idrive-apps` source (Waze on cluster
  installs it too); the Store installs it first. It doesn't touch CarPlay or Android Auto.
- Settings: show on the cluster (on), on the HUD (off), and how long a quiet phone may be before the card goes.
- **Debug mode** (0.1.1): the phone app's Car log screen reads this app's log file, its live log and a status
  snapshot (the phone link, the route, cluster-render's layers and targets) over the same link. Since 0.1.2
  also the RideTube fork service's debug report (`status.json` and its recent plays from `sessions.jsonl`),
  when that service is installed; neither holds what was watched. (0.1.3: from `mdq-ridetube-d`.)
- **Android Auto** (0.1.3, with the tool **Android Auto log (for CarLink)**, `mdq-aapd-log`): the Car log shows
  the car's Android Auto daemon (`aapd`): its journal (the last 2000 lines), whether it runs and listens, what
  waze-on-cluster's patch changed and how `/etc/aapd.conf` differs from its backup; since the tool's 0.1.1 also
  the network: addresses, routes and the firewall rules (iptables, nftables). The tool runs as root but
  only reads; it writes only `/run/mdq-aapd-log`, which goes when it stops or is removed. It starts at the next
  head-unit start after its install.

### RideTube (fork)

- **Status: the service's RAM streaming is not yet tried in a car.** Tested on a PC: its tests, and a live
  streaming check against YouTube.
- **Its own ids:** the app is `mdq_ridetube` (the tile says "RideTube (fork)"), its service `mdq-ridetube-d`.
  It installs beside JustAnotherPU's RideTube (`jap_ridetube`, `jap-ridetube-d`) and never over it; both can be
  installed, but only one plays at a time. Keep `JustAnotherPU/mgu-apps:releases`: Node.js 22 (`jap-node22`)
  comes from it.
- **The video in RAM:** the service mounts a 256 MB RAM disk and keeps only about two and a half minutes of the
  playing video in it, instead of writing the whole video to flash. Seeking back more than 45 s fetches it again
  (a short pause). Videos it can't stream that way (very long ones, about 90 minutes and up) go to flash as before.
- **Debug report:** `/run/mdq-ridetube-d/status.json` (RAM, memory, the stream, refreshed every 10 s while in use)
  and `/var/opt/mdq-ridetube-d/log/sessions.jsonl` (one line a play). Neither holds what you watched. Over the
  car's hotspot: `ssh root@172.16.222.97 cat /run/mdq-ridetube-d/status.json`. The fields:
  [the service's README](https://github.com/7amoody1985/ridetube/blob/main/native/mdq-ridetube-d/README.md).
- Licence: GPL-3.0-or-later, as the original (the licence texts are in the packages); the source of this build is
  [7amoody1985/ridetube](https://github.com/7amoody1985/ridetube), its packages made with its
  `tools/build_app.sh` and `tools/build_service.sh`.

## Adding an app

The checklist (also for coding agents) is [AGENTS.md](AGENTS.md). In short: the package in `packages/`, an entry in
`apps.json`, then `powershell -File tools\publish.ps1` and `python -I tools/verify.py` (ends with `all ok`).
