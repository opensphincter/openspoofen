# First Boot And Image Strategy

## Goal

Make deployment feel close to “flash, boot, sign in, choose a location” instead of “install an OS, SSH in, install packages, debug routing, and hope the TV uses the right path.”

## Deployment modes

### Mode 1: development and early validation

Use stock Raspberry Pi OS Lite plus a repo installer.

Best for:

- proving the network and VPN design
- debugging interface behavior on real hardware
- avoiding premature investment in a custom image pipeline

### Mode 2: release appliance

Use a custom Raspberry Pi image produced by `pi-gen` and distributed as a `.img.xz` artifact.

Best for:

- the actual “one-step load” experience
- repeatable releases
- minimizing operator error

## Recommended first-boot UX

### What Raspberry Pi Imager should handle

Use Raspberry Pi Imager customization for:

- hostname
- admin username
- admin password
- Wi-Fi credentials if Wi-Fi is the upstream path
- SSH enablement
- optional Raspberry Pi Connect enablement for support and recovery

This avoids inventing parallel mechanisms for basic Pi setup.

For local development only, the repo installer can also enable tty1 console autologin through `/etc/openspoofen/openspoofen.env` using:

- `RP_DEV_CONSOLE_AUTOLOGIN=true`
- `RP_DEV_CONSOLE_AUTOLOGIN_USER=<pi username>`

This is intentionally a dev-only convenience and should stay off in release images.

### What the product onboarding should handle

The appliance-specific onboarding should collect or read:

- NordVPN access token
- initial desired country
- selected device mode or topology
- downstream subnet, if non-default
- optional local admin UI settings if they differ from the main Pi admin account

## Recommended onboarding input methods

### Preferred release approach

Allow one of these supported input paths:

1. Boot-partition config file consumed once on first boot.
2. Local onboarding web page on the upstream network if the token is not supplied in advance.

The boot-partition file should exist only to simplify day-zero setup. If it is used, the first-boot service should remove or neutralize it after successful import.

### Example one-time config file

File name:

- `/boot/firmware/openspoofen.env`

Example fields:

```env
DEVICE_MODE=wifi-wan_eth-lan
DOWNSTREAM_CIDR=10.55.0.1/24
NORDVPN_TOKEN=replace_me
DEFAULT_COUNTRY=United_States
FAIL_CLOSED=true
```

Notes:

- Do not treat this format as a stable public API until the installer is finalized.
- Token material should be deleted from the boot partition after successful onboarding.
- A missing token should not brick the device; it should move the appliance into an “onboarding required” state.

## First-boot service flow

### Proposed sequence

1. Wait for the upstream interface to become usable.
2. Validate the expected topology and interface availability.
3. Install or validate required packages.
4. Create NetworkManager profiles for upstream and downstream interfaces.
5. Write dnsmasq and nftables configuration.
6. Enable forwarding and related sysctl settings.
7. Install NordVPN using the official Linux installer path.
8. Ensure the admin user belongs to the `nordvpn` group.
9. If a token is available, authenticate with `nordvpn login --token`.
10. Apply VPN defaults:
    - technology `NordLynx`
    - kill switch enabled
    - required LAN allowlist or discovery settings
    - optional auto-connect and default country
11. Start the web UI and health monitor services.
12. Mark onboarding success and remove one-time secrets from the boot partition.

### Failure handling

- If networking fails, keep SSH or Raspberry Pi Connect available if possible.
- If NordVPN authentication fails, leave the local UI reachable for re-auth.
- If package installation fails, log the exact stage and avoid half-configured service loops.
- If the downstream network is not safe to enable yet, keep it disabled rather than leaking direct traffic unexpectedly.

## One-step image strategy

## Phase 1: prove stock-image installation

Deliver first:

- installer scripts
- systemd units
- config templates
- documentation for flashing stock Pi OS Lite and running the installer

Reason:

- faster iteration
- easier debugging on live systems
- simpler separation between product logic and image-building logic

## Phase 2: move to custom image builds

Once the stock install path is stable, move the exact runtime into a custom image built with `pi-gen`.

### Why `pi-gen`

- it is the standard Raspberry Pi OS image build system
- it supports stage-based customization
- it produces artifacts already suited to Raspberry Pi Imager

### Build pipeline targets

- pin the base Pi OS release and architecture
- add a custom stage that installs system packages, copies app files, installs Python dependencies, places systemd units, and enables needed services
- emit compressed image artifacts in `.img.xz` format
- produce checksums and release notes

### Build host expectations

- Debian-based build environment or Docker-backed `pi-gen` flow
- sufficient storage and CPU for repeated image builds
- pinned build configuration checked into the repo

## UX states to design explicitly

### 1. Fresh but not onboarded

- Pi has booted and basic networking works
- downstream path is not fully active yet
- UI shows that NordVPN authentication is still required

### 2. Onboarded and connected

- current country is shown
- public IP is shown
- downstream client has working internet through the tunnel

### 3. Reauth required

- token expired, was revoked, or onboarding failed
- UI provides a re-auth path without reimaging

### 4. Safe-fail state

- upstream exists but VPN is down
- downstream traffic is blocked if fail-closed mode is enabled
- diagnostics are available locally

## Release packaging recommendation

Ship these artifacts for each release:

- `openspoofen-<version>.img.xz`
- `SHA256SUMS`
- `RELEASE_NOTES.md`
- a short “flash and onboard” operator guide

## Support and recovery recommendations

- Keep SSH enabled for development and advanced users.
- Consider Raspberry Pi Connect as an optional recovery path for supported operators.
- Add a factory-reset action that clears appliance config and VPN auth without requiring a full reimage.
- Keep a text status file on-device so support can quickly see the last onboarding stage reached.