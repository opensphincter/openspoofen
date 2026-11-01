# OpenSpoofen Project Plan

## Objective

Build a Raspberry Pi appliance that routes a smart TV or streaming device through NordVPN, allows the user to change exit location with minimal friction, and can be deployed by flashing a single image rather than hand-configuring Linux each time.

## Product goals

- Make the Pi behave like a dedicated VPN router for one downstream device or a very small downstream segment.
- Support headless setup and recovery.
- Use officially supported NordVPN flows where possible.
- Produce a repeatable, versioned image artifact that can be loaded with Raspberry Pi Imager.
- Expose an easy location-switching control surface without forcing the user into shell commands.

## Assumptions

- The user already has a working NordVPN subscription.
- The downstream use case is media access on a smart TV or streaming device.
- The first supported hardware target is a Pi 4 or Pi 5.
- The first supported network shape is a single downstream client or small downstream LAN, not a whole-home router replacement.
- We can require a one-time NordVPN token or login step during provisioning.

## Non-goals for v1

- Replacing a full home router or mesh system.
- Multi-tenant user management.
- Remote cloud control outside the local network.
- Supporting every VPN provider.
- Guaranteeing compatibility with every streaming app or every region pair.

## Success criteria

- A fresh Pi can be flashed, booted, provisioned, and connected to NordVPN without manual package-by-package setup.
- A downstream TV gets internet only when the intended VPN path is healthy or explicitly configured otherwise.
- The user can switch country from a local UI in less than 30 seconds under normal conditions.
- DNS leak and default-route leak tests pass for supported topologies.
- Rebuilding the image from source produces the same functional appliance behavior.

## Recommended v1 architecture

- Base OS: Raspberry Pi OS Lite 64-bit
- Provisioning: first-boot systemd service plus Raspberry Pi Imager customization
- Runtime language: Python for orchestration and local UI
- Runtime web stack: Flask with server-rendered templates
- Runtime persistence: small local SQLite database or structured state files under `/var/lib/openspoofen`
- Networking: NetworkManager for interface profiles, nftables for forwarding and kill-switch policy, dnsmasq for DHCP and local DNS on the downstream side
- VPN: official NordVPN Linux CLI with token-based headless login support
- Packaging: custom image built with `pi-gen` after the installer path works

## Workstreams

### 1. Foundation and repo structure

Deliverables:

- repo layout for installer, runtime app, systemd units, image customization, and tests
- environment conventions and config schema
- security boundaries for secrets and local admin auth

Proposed layout:

- `bootstrap/`: first-boot installer and idempotent setup scripts
- `app/`: Python web UI and command wrappers
- `systemd/`: service and timer units
- `image/`: `pi-gen` customization files and build configs
- `configs/`: example config templates and reference policy files
- `tests/`: integration and leak-test scripts
- `docs/`: architecture, operations, and release docs

### 2. Network appliance core

Deliverables:

- deterministic upstream and downstream interface handling
- static downstream addressing plan
- DHCP and DNS service for downstream clients
- IPv4 forwarding and explicit firewall policy
- kill-switch semantics for forwarded traffic

Tasks:

- pick and document the supported topology matrix
- create NetworkManager profiles for upstream and downstream interfaces
- enable `net.ipv4.ip_forward=1`
- define nftables rules for NAT, forwarding, and non-VPN fallback behavior
- disable or tightly control IPv6 until it is proven safe in the shipped configuration
- ensure DNS from downstream clients is handled by the Pi and not leaked upstream outside the intended path

### 3. NordVPN integration

Deliverables:

- supported install path for NordVPN CLI
- supported login path for headless devices
- country and server switching abstraction
- health checks and tunnel state reporting

Tasks:

- install NordVPN with the official Linux method
- handle `nordvpn` group membership and reboot or re-login requirements
- support `nordvpn login --token <token>` for headless auth
- apply safe defaults: `NordLynx` first, `killswitch on`, explicit LAN/subnet allowlist, controlled auto-connect
- wrap `nordvpn countries`, `nordvpn connect`, `nordvpn disconnect`, and `nordvpn status` in a constrained service layer
- define timeout and rollback behavior when a location change fails

### 4. Local control surface

Deliverables:

- authenticated local web UI
- current status view
- country selection flow
- logs and diagnostics page

Tasks:

- build a minimal Flask UI with server-rendered forms
- show VPN state, public IP, resolved region, downstream client state, and recent actions
- support favorite countries and recent selections
- restrict commands to an allowlisted wrapper instead of shelling directly from HTTP handlers
- bind management only to intended interfaces and require local authentication

### 5. First-boot experience

Deliverables:

- zero-to-working first-boot flow
- secure secret ingestion path
- cleanup of one-time provisioning material

Tasks:

- rely on Raspberry Pi Imager for hostname, user, password, Wi-Fi, and SSH where possible
- read product-specific config from a boot-partition file or a secure onboarding step
- import NordVPN token once, log in, persist only what is required, then remove the token source if present on the boot partition
- generate downstream networking config automatically
- produce a clear success or failure marker for the user

### 6. Image build and release

Deliverables:

- reproducible custom image pipeline
- versioned release artifacts
- checksum and release notes

Tasks:

- make the installer work on stock Raspberry Pi OS Lite first
- move to a `pi-gen`-based custom image pipeline once the runtime is stable
- pin base release, packages, and build configuration
- export `.img.xz` artifacts for Raspberry Pi Imager
- document dev image versus release image differences

### 7. Hardening and operations

Deliverables:

- safe defaults for a consumer-style appliance
- diagnosable failure states
- recovery path without reimaging in every case

Tasks:

- require explicit admin auth for the UI
- do not leave NordVPN tokens in logs, shell history, or persistent boot files
- restrict inbound services to SSH, the local admin UI, and only on intended interfaces
- add structured logs and a support bundle generator
- add a rollback path if a bad config locks out the downstream device
- document factory reset behavior

## External dependencies

System packages and platform components expected for v1:

- Raspberry Pi OS Lite 64-bit
- NetworkManager
- nftables
- dnsmasq
- curl
- jq
- ca-certificates
- openssh-server
- python3
- python3-venv
- python3-pip
- sqlite3
- avahi-daemon

Python dependencies expected for v1:

- Flask
- Jinja2
- gunicorn or waitress
- pydantic or a similarly small config-validation library

Build-time dependencies for release imaging:

- `pi-gen`
- Debian-based build host or Docker-backed build flow supported by `pi-gen`
- image signing or checksum tooling

## Milestones

### Milestone 0: planning complete

- architecture agreed
- topology chosen
- repo conventions and security rules written

### Milestone 1: stock OS installer works

- provisioning scripts configure a stock Raspberry Pi OS Lite install
- NordVPN connects and downstream traffic routes through the tunnel

### Milestone 2: switching UI works

- user can log in locally and switch country from the web UI
- failed switches recover cleanly

### Milestone 3: custom image works

- custom image boots into the appliance flow with minimal user input
- first-boot configuration is documented and repeatable

### Milestone 4: release candidate

- leak tests, boot tests, upgrade tests, and recovery tests pass
- release artifact, checksums, and operator docs are published

## Acceptance test matrix

### Provisioning

- fresh flash with Raspberry Pi Imager customization only
- fresh flash with product config file present on boot partition
- first boot with Wi-Fi upstream
- first boot with Ethernet upstream

### VPN and routing

- connect to default location automatically after onboarding
- switch between two countries repeatedly without leaving stale routes
- disconnect and reconnect after reboot
- kill-switch behavior when NordVPN is down or reconnecting

### Leak and correctness

- downstream public IP matches VPN endpoint, not ISP
- downstream DNS requests resolve through the intended path
- no unintended IPv6 egress from downstream clients
- LAN allowlisting enables forwarding without exposing extra inbound paths

### Client compatibility

- smart TV or streaming stick gets DHCP lease and DNS
- major apps open and resolve locations consistently enough for the supported use case
- recovery is possible after app-level failures or region switch failures

### Reliability

- reboot with last-known country
- power loss during boot
- bad token or expired token handling
- upstream network changes or temporary outage

## Known risks

- Some media providers block datacenter IP ranges or VPN endpoints outright.
- Some services derive location from more than IP address alone.
- NordVPN Linux behavior around forwarded LAN traffic has changed before and must be regression-tested across client updates.
- Interface naming and routing behavior can vary by Pi model and attached adapters.
- A single-interface setup cannot behave like an inline wired router without a second usable network path.

## Open decisions to settle early

- Primary supported topology for v1: Wi-Fi upstream plus Ethernet downstream, or dual-Ethernet with a USB adapter.
- Whether to ship the first UI on the upstream interface only, or also on the downstream side.
- Whether to persist an access token on-device after first boot, or require a re-auth flow for sensitive resets.
- Whether to allow fallback internet without VPN when the tunnel is unavailable, or enforce fail-closed only.

## Recommended next implementation order

1. Build and test the stock Raspberry Pi OS Lite installer path.
2. Prove routed traffic, DNS handling, and fail-closed nftables behavior before building any UI.
3. Add the country-switching service layer and CLI wrappers.
4. Add the local web UI.
5. Move the working setup into a `pi-gen` image pipeline.
6. Add diagnostics, reset, and release automation.