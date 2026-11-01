# OpenSpoofen

![OpenSpoofen logo](docs/assets/openspoofen-logo.png)

[![CI](https://github.com/opensphincter/openspoofen/actions/workflows/ci.yml/badge.svg)](https://github.com/opensphincter/openspoofen/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/opensphincter/openspoofen/badge)](https://scorecard.dev/viewer/?uri=github.com/opensphincter/openspoofen)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

OpenSpoofen turns a Raspberry Pi into a VPN switch for a smart TV or streaming box. The TV plugs into the Pi, the Pi sends its traffic through your VPN account, and you change the exit location from a web page on your phone.

It is a focused appliance, not a general-purpose router:

- flash Raspberry Pi OS, then install OpenSpoofen over SSH;
- connect the TV to the Pi's Ethernet port;
- sign in to a supported VPN account once;
- switch locations from the dashboard without touching the network setup again.

> **Status: alpha.** It runs on the maintainer's own hardware. Expect rough edges, and read the [security policy](SECURITY.md) before exposing it to anyone else's network.

## Responsible use

OpenSpoofen changes where your traffic appears to come from. Use it only where that is legal, and only in ways the services you use allow. Many streaming services prohibit location changes in their terms and detect VPNs through more than the IP address (account region, payment country, GPS). OpenSpoofen does not try to defeat those checks, and the project accepts no responsibility for how it is used.

## What you need

- A Raspberry Pi 4 or 5 (a Pi 3 works for testing), with a power supply and a microSD card.
- Raspberry Pi OS Lite, 64-bit.
- An upstream connection: the Pi's Wi-Fi, or a USB 3 Ethernet adapter.
- An Ethernet cable from the Pi to the TV.
- An account with a supported VPN provider.

For the lowest latency, use a Pi 5 with wired upstream and downstream and WireGuard profiles. See [Hardware I/O and form factor](docs/design/hardware-io-and-form-factor.md). A printable case is in [`designs/pi3-case/`](designs/pi3-case/README.md).

## Supported providers

| Provider | How it connects |
| --- | --- |
| WireGuard profiles | One config file per region; the default and fastest path |
| NordVPN | Official Linux CLI; the best-supported account path |
| Mullvad | Official Linux CLI |
| ExpressVPN | Official Linux CLI, with a less appliance-friendly activation |
| Proton VPN | Official Linux CLI, with headless caveats |
| Surfshark and others | Manual OpenVPN profiles |
| Mock | No network changes; for development and demos |

Details: [provider comparison](docs/reference/vpn-provider-comparison.md) and [connecting an account](docs/guides/provider-account-integration.md).

## Try it without hardware

The mock provider runs the whole dashboard on your computer without touching its network. You need Python 3.11 or newer.

```bash
git clone https://github.com/opensphincter/openspoofen.git
cd openspoofen
python -m venv .venv && . .venv/bin/activate
pip install -e .
RP_PROVIDER=mock RP_SECRET_KEY=dev python -m openspoofen.serve
```

Open <http://127.0.0.1:8080>, set an admin password on the setup screen, and switch locations.

## Install on a Raspberry Pi

1. Flash Raspberry Pi OS Lite 64-bit with Raspberry Pi Imager. In its settings, set the hostname, a user, your Wi-Fi country and network if needed, and enable SSH.
2. Copy the example settings and fill in your own values: [`configs/openspoofen.env.example`](configs/openspoofen.env.example), [`configs/wifi-uplink.env.example`](configs/wifi-uplink.env.example) and [`configs/tv-ethernet-mode.env.example`](configs/tv-ethernet-mode.env.example).
3. Install from a Windows laptop with `bootstrap/deploy-to-pi.ps1`, or on the Pi itself by cloning the repository and running `./bootstrap/install.sh` from its root (it calls `sudo` where it needs to).
4. Open `http://openspoofen.local:8080` from a phone on the same network and finish setup.

The full walkthrough, with the parts list, is [Windows laptop to Raspberry Pi deployment](docs/guides/windows-laptop-deployment.md). For bench wiring, see [Current hardware TV test](docs/guides/current-hardware-tv-test.md).

The UI listens on the LAN only. It asks for an admin password, and can additionally require a per-browser pairing token (`RP_REQUIRE_PAIRING_TOKEN=true`). With `RP_ENABLE_HTTPS=true`, the installer generates a self-signed certificate for `openspoofen.local`. Phones won't trust it until you install it on the device.

## OS-level performance tuning

`bootstrap/tune-pi-os.sh` tunes a headless Pi for this job. Run it once after installing (or pass `-TunePiOs` to `deploy-to-pi.ps1`); it is safe to run again.

- zram compressed swap at half of RAM, using zstd;
- GPU memory down to 16 MB, since there is no desktop;
- the `performance` CPU governor, for lower subprocess latency;
- `noatime` on the root filesystem and the `none` I/O scheduler for the SD card;
- the WireGuard kernel module loaded, which is much faster than userspace;
- Bluetooth and ModemManager disabled, and a quiet boot console.

## Documentation

The [documentation index](docs/README.md) lists guides, design notes and reference pages, including [testing without hardware](docs/guides/testing-and-simulation.md) in a Linux network-namespace lab.

## Contributing

Bug reports, provider adapters and hardware test results are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup and checks, and the [code of conduct](CODE_OF_CONDUCT.md). For help, see [SUPPORT.md](SUPPORT.md).

Report security problems privately, as described in [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE). VPN provider names belong to their owners. OpenSpoofen is not affiliated with or endorsed by any provider or streaming service.
