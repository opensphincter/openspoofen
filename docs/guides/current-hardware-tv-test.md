# Current Hardware TV Test Path

This is the right bench topology for the current single-Ethernet Raspberry Pi when no second NIC is available:

1. Pi power: use the Pi's normal power supply.
2. Pi upstream internet: use built-in Wi-Fi on `wlan0`.
3. TV downstream link: plug the TV's Ethernet port directly into the Pi's built-in `eth0`.
4. Control device: keep your phone or laptop on the same home Wi-Fi as the Pi so it can open the dashboard.

## What to plug in

- TV Ethernet cable -> Pi `eth0`
- Pi power -> normal power supply
- Phone or laptop -> same Wi-Fi network used by the Pi uplink

No unmanaged switch is needed for this bench mode. The Pi is acting like a tiny routed appliance, not a transparent bridge.

## Better immediate mode with a USB Ethernet adapter

If you have a USB-to-Ethernet adapter, this is the better immediate test mode:

1. Pi power: use the Pi's normal power supply.
2. Pi upstream internet: plug your router or modem LAN into the USB Ethernet adapter attached to the Pi.
3. TV downstream link: plug the TV's Ethernet port directly into the Pi's built-in `eth0`.
4. Control device: keep your phone or laptop on the same normal home LAN so it can still open the dashboard.

### What to plug in

- Router or modem LAN -> USB Ethernet adapter -> Pi USB port
- TV Ethernet cable -> Pi built-in `eth0`
- Pi power -> normal power supply

This is the cleanest immediate way to get a wired-in, wired-out appliance shape on the current board.

## Current repo support

The repo now includes two opt-in Pi services:

- `openspoofen-wifi-uplink.service`: reads `/etc/openspoofen/secrets/wifi-uplink.local.env` and configures `wlan0` with NetworkManager.
- `openspoofen-tv-lan.service`: reads `/etc/openspoofen/tv-ethernet-mode.env`, assigns a static address to the TV-facing Ethernet port, enables DHCP through `dnsmasq`, enables IPv4 forwarding, and applies bench NAT rules through `nft`.

### OS performance tuning

Run `sudo /opt/openspoofen/bootstrap/tune-pi-os.sh` on the Pi after installation to apply RAM, CPU, I/O, and kernel optimizations for a headless appliance. See the [README OS Tuning section](../../README.md#os-level-performance-tuning) for details.

## Activation files on the Pi

### Wi-Fi uplink

Create `/etc/openspoofen/secrets/wifi-uplink.local.env` from `configs/wifi-uplink.env.example` and set:

- `RP_WIFI_COUNTRY`
- `RP_WIFI_SSID`
- `RP_WIFI_PASSWORD`

`RP_WIFI_COUNTRY` must use the operator's real local 2-letter ISO 3166-1 alpha-2 regulatory country code. Do not assume `US` outside the United States.

### TV Ethernet bench mode

Create `/etc/openspoofen/tv-ethernet-mode.env` from `configs/tv-ethernet-mode.env.example`.

For USB-Ethernet upstream mode, set:

- `RP_TV_LAN_IFACE=eth0`
- `RP_TV_UPLINK_IFACE=<your USB Ethernet interface>`

Typical Linux names will be `eth1` or an `enx...` interface, depending on the adapter chipset and driver.

If you are deploying from Windows, you can install this file during the initial repo deployment instead of creating it later by hand:

```powershell
.\bootstrap\deploy-to-pi.ps1 \
	-HostName openspoofen.local \
	-UserName <pi-username> \
	-LocalTvModeEnvFile .\configs\tv-ethernet-mode.env.example
```

For the USB-Ethernet bench topology on the current board, the intended first-pass values are:

- `RP_TV_LAN_IFACE=eth0`
- `RP_TV_UPLINK_IFACE=eth1` or the adapter's `enx...` name
- `RP_TV_VPN_IFACE=nordlynx`

Default behavior:

- Pi TV-facing address: `192.168.50.1/24`
- TV DHCP range: `192.168.50.50` to `192.168.50.150`
- TV LAN MTU defaults to `1420` so NordLynx-backed paths do not depend on consumer-TV PMTU behavior
- Downstream TV traffic is VPN-only and fail-closed by default; direct uplink fallback stays off unless `RP_TV_ALLOW_UPLINK_FALLBACK=true`
- NordVPN bootstrap derives the downstream allowlist subnet from `RP_TV_LAN_ADDRESS` when an older `/etc/openspoofen/openspoofen.env` does not already declare `RP_NORDVPN_ALLOWLIST_SUBNET`
- In TV Ethernet router mode, NordVPN bootstrap disables NordVPN's own firewall and kill switch so the appliance's nftables policy remains the only forwarded-client filter

## Expected live-test flow

1. Bring up Wi-Fi uplink on the Pi.
2. Enable TV Ethernet bench mode.
3. Plug the TV into the Pi's Ethernet port.
4. On the TV, renew network settings so it requests DHCP from the Pi.
5. Open the dashboard from your phone or laptop.
6. Switch regions from the route-control panel.
7. On the TV, restart the streaming app and verify the region-dependent result.

Useful live verification on the Pi:

- `systemctl status openspoofen-nordvpn-bootstrap.service --no-pager`
- `sudo nordvpn settings`
- `ip route get 1.1.1.1 from <tv-ip> iif eth0`

## Expected live-test flow with USB Ethernet upstream

1. Plug the USB Ethernet adapter into the Pi and confirm Linux sees a second Ethernet interface.
2. Set `RP_TV_UPLINK_IFACE` to that adapter interface name.
3. Leave `RP_TV_LAN_IFACE=eth0` for the TV-facing port.
4. Enable TV Ethernet bench mode.
5. Plug the TV into the Pi's built-in Ethernet port.
6. On the TV, renew network settings so it gets DHCP from the Pi.
7. Switch regions from the dashboard and verify the TV-side result.

## Important limitation

This bench mode is for current-hardware testing. It is not yet the repo's release-grade dataplane. Kill-switch hardening, IPv6 handling, and DNS-leak validation still need explicit test coverage.