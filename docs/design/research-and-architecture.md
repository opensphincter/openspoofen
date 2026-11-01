# Research And Architecture

## Research summary

### Raspberry Pi platform findings

- Raspberry Pi Imager supports preconfiguring hostname, user, password, Wi-Fi, SSH, and Raspberry Pi Connect before first boot.
- Raspberry Pi OS uses NetworkManager by default on current releases, which makes interface profile management and headless Wi-Fi setup easier than older `dhcpcd`-centric guides.
- Recent Raspberry Pi models support several workable network shapes for this project, but the exact topology changes the hardware requirements significantly.

### NordVPN findings

- NordVPN officially supports Raspberry Pi OS in its Linux support matrix.
- NordVPN supports a headless token login flow with `nordvpn login --token <token>`.
- NordVPN documents that forwarded LAN traffic through a VPN-connected Linux host is blocked by default in recent client versions unless LAN discovery is enabled or the relevant subnet is allowlisted.
- NordVPN exposes the CLI commands needed for this project: login, status, countries, cities, connect, disconnect, auto-connect, kill switch, protocol and technology selection, and allowlisting.

### Linux networking findings

- Debian recommends nftables as the default firewalling and NAT framework.
- dnsmasq remains a lightweight fit for DHCP and local DNS on a very small routed network.
- For this use case, routing correctness is not enough on its own. The appliance also needs explicit rules for fail-closed behavior, DNS path control, and leak testing.

### Image build findings

- Raspberry Pi Imager supports writing custom `.img`, `.zip`, and `.xz` image artifacts.
- `pi-gen` is the standard tool used to build Raspberry Pi OS images and custom derivatives.
- `pi-gen` supports reproducible stage-based customization and is the right long-term path once the appliance works on a stock Pi OS Lite base.

## Design constraints derived from the research

- The product should not depend on an unsupported manual VPN configuration if the official NordVPN client can satisfy the requirements.
- The first provisioning flow must work headlessly.
- The runtime should be small, understandable, and debuggable on-device.
- The first release should target a narrow, explicit topology instead of pretending to support every interface combination.

## Recommended topology options

### Primary recommendation for v1

Support two modes, but ship one as the default:

1. Default consumer mode: Pi Wi-Fi as upstream WAN, Pi Ethernet as downstream LAN to the TV.
2. Secondary advanced mode: upstream Ethernet plus downstream Wi-Fi hotspot.

Why this default:

- It works on a stock Pi 4 or Pi 5 without requiring a USB Ethernet adapter.
- It still gives the TV a dedicated wired path through the Pi.
- It matches the intended “plug the device into the Pi and let the Pi own the egress location” behavior.

### Optional future mode

Dual-Ethernet wired inline mode:

- built-in Ethernet or USB Ethernet as WAN
- second Ethernet interface as downstream LAN

This is the cleanest pure wired appliance story, but it requires extra hardware and more adapter validation.

## Chosen v1 architecture

### Control plane

- Python application providing:
  - a small authenticated web UI
  - a service layer for validated NordVPN operations
  - health and status reporting
  - minimal local state persistence

### Network plane

- NetworkManager owns interface profiles and static addressing.
- dnsmasq serves DHCP and local DNS to downstream clients.
- nftables owns NAT, forwarding, and fail-closed policy.
- sysctl enables forwarding and disables or constrains IPv6 until fully validated.

### VPN plane

- Official NordVPN Linux CLI and daemon.
- Preferred technology: NordLynx, unless testing forces fallback.
- Token-based headless login for the first boot or re-onboarding flow.
- Country switching via controlled `nordvpn` wrappers, never arbitrary shell execution from the UI.

### Boot and provisioning plane

- Raspberry Pi Imager preconfigures user, password, Wi-Fi, and SSH.
- A first-boot oneshot service reads product-specific config, installs or validates dependencies, performs NordVPN onboarding, writes appliance config, and marks completion.
- A later image pipeline bakes these components into a custom image so the user only flashes, boots, enters the required credential material, and uses the UI.

## Recommended runtime behavior

### Normal flow

1. Pi boots and comes online on its upstream interface.
2. Downstream interface is configured with a fixed local subnet.
3. dnsmasq begins serving DHCP and DNS to the downstream client.
4. NordVPN is authenticated and connected.
5. nftables allows downstream forwarding only through the intended VPN path.
6. The local UI reports current location, public IP, and tunnel state.

### Location switch flow

1. User opens local admin UI.
2. User selects a country, and later possibly a city or specialty group.
3. App validates the request against an allowlisted command surface.
4. Existing tunnel is disconnected or switched using a controlled sequence.
5. Health checks confirm new tunnel state and external IP.
6. UI updates status and retains a concise audit entry.

### Failure flow

- If VPN auth fails, the UI reports onboarding failure and blocks downstream internet if fail-closed mode is enabled.
- If the VPN drops unexpectedly, nftables policy prevents traffic from escaping on the raw upstream path.
- If the token is invalid or expired, the appliance enters a recoverable “reauth required” state without wiping network settings.

## Dependency decisions

### Why NetworkManager

- It is the default on current Raspberry Pi OS releases.
- It simplifies Wi-Fi configuration, profile persistence, and headless interface management.
- It avoids inventing a custom network orchestration layer too early.

### Why nftables

- It is the Debian-default firewall and NAT framework.
- New firewalling work should target nftables rather than legacy iptables syntax.
- It gives explicit control for fail-closed forwarding behavior.

### Why dnsmasq

- It is small and well-suited to low-resource router-like devices.
- It covers the exact DHCP and DNS needs of a single-downstream or small-downstream-segment product.

### Why a server-rendered Python UI

- The UI requirements are small.
- The appliance does not need a full SPA build system.
- A simple Flask app is easier to audit, easier to package, and easier to keep functional on a constrained device.

## Security posture

- Do not commit or bake live NordVPN tokens into the repo.
- Do not leave one-time token material on the boot partition after successful onboarding.
- Bind the UI only to intended interfaces.
- Require local authentication for administrative actions.
- Sanitize command execution through a strict wrapper layer.
- Keep logs useful but non-sensitive.

## Product realities that must be documented honestly

- This appliance can change IP geolocation. It cannot guarantee that every media provider will accept that location as valid.
- Some apps may still infer region from device firmware, app account metadata, payment profile, DNS strategy, or anti-VPN controls.
- The user experience will be best when the downstream device is configured to use the Pi consistently, not intermittently.

## Recommended repository implementation targets

- `bootstrap/install.sh`: idempotent installer for stock Pi OS Lite
- `bootstrap/firstboot.sh`: one-time onboarding script
- `app/server.py`: Flask entrypoint
- `app/services/nordvpn.py`: controlled VPN operations
- `app/services/network.py`: status and validation helpers
- `configs/nftables.conf`: base firewall and NAT policy
- `configs/dnsmasq.conf`: downstream DHCP and DNS policy
- `systemd/openspoofen-firstboot.service`
- `systemd/openspoofen-web.service`
- `image/pi-gen/`: custom stage files and build config

## Architecture decision summary

- Use the official NordVPN Linux client instead of inventing a manual VPN setup first.
- Prioritize a headless-first appliance design.
- Use Raspberry Pi Imager customization for early onboarding convenience.
- Ship a stock-OS installer first, then move to `pi-gen` for a real one-step image.
- Keep the runtime small and explicit: Python app plus systemd plus Linux-native networking components.