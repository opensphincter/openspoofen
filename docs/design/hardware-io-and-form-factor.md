# Hardware I/O And Form Factor

## Why this matters

The product goal sounds simple: put a Raspberry Pi between the internet and a TV, then switch regions. The hardware reality is stricter. A network appliance needs a clear upstream path and a clear downstream path. With Raspberry Pi boards, that constraint determines whether the product is easy, awkward, or misleading.

## Standard Raspberry Pi inputs and outputs relevant to this project

## Raspberry Pi 4

Relevant standard I/O:

- 1 x Gigabit Ethernet
- dual-band Wi-Fi
- Bluetooth
- 2 x USB 3.0 ports
- 2 x USB 2.0 ports
- 2 x micro HDMI
- microSD boot media
- USB-C power input
- 40-pin GPIO header

Practical implications:

- It already has one wired network port for either WAN or LAN.
- It has built-in Wi-Fi, which makes a one-Ethernet-port appliance realistic if Wi-Fi is used for the opposite side.
- USB 3 gives enough bandwidth for a second Gigabit Ethernet adapter if dual-Ethernet routing is required.

## Raspberry Pi 5

Relevant standard I/O:

- 1 x Gigabit Ethernet
- dual-band Wi-Fi
- Bluetooth 5.0 / BLE
- 2 x USB 3.0 ports
- 2 x USB 2.0 ports
- 2 x micro HDMI
- microSD boot media
- USB-C power input
- PCIe 2.0 x1 for fast peripherals
- 40-pin GPIO header
- power button
- RTC support

Practical implications:

- It solves the same single-Ethernet limitation the same way as Pi 4 if using Wi-Fi upstream.
- It provides a cleaner path to premium dual-Ethernet or NVMe-backed release builds through PCIe.
- It benefits from active cooling under sustained load.

## What the appliance actually needs

To function as a geo-switch for a TV over Ethernet, the device needs:

- one upstream network path to the internet
- one downstream network path to the TV or streaming device
- a control path for onboarding and region switching

Those three paths do not all need separate ports, but they do need separate planning.

## Feasible topologies

## Option A: Wi-Fi upstream, Ethernet downstream

Shape:

- Pi connects to home Wi-Fi for internet
- TV plugs into Pi Ethernet
- user manages the device from phone or laptop over the home network

Why this is the easiest form factor:

- no extra hardware is required on Pi 4 or Pi 5
- TV still gets the stable wired link people expect
- the appliance can stay headless
- Raspberry Pi Imager can preconfigure Wi-Fi and SSH before first boot

Tradeoffs:

- upstream bandwidth and latency depend on Wi-Fi quality
- the Pi must maintain stable Wi-Fi while also routing traffic

Verdict:

- Best default v1 form factor.

## Option B: Ethernet upstream, Wi-Fi downstream hotspot

Shape:

- Pi plugs into the home router by Ethernet
- TV or streaming stick connects to a Pi-hosted Wi-Fi network

Pros:

- easy to implement without extra network hardware
- good if the downstream device uses Wi-Fi anyway

Cons:

- does not satisfy a strict “Ethernet to TV” requirement
- less attractive for TVs that are near the Pi and already wired

Verdict:

- Good fallback mode, not the main appliance identity if Ethernet to TV matters.

## Option C: Ethernet upstream, Ethernet downstream via second NIC

Shape:

- built-in Ethernet used for WAN
- USB 3 Ethernet adapter or Pi 5 PCIe Ethernet used for LAN
- TV connects by Ethernet

Pros:

- the cleanest router-like story
- avoids Wi-Fi as the upstream bottleneck
- easiest to explain to users who want a pure “inline” box

Cons:

- requires extra hardware selection and validation
- some USB Ethernet adapters behave differently under Linux or under sustained load

Verdict:

- Best premium or advanced mode.
- Strong candidate for a later release or a “recommended kit” bundle.

## Option D: Transparent Ethernet bridge

Shape:

- Pi tries to sit invisibly inline between router and TV as if it were a bump-in-the-wire device

Why this is not the recommended v1 design:

- bridging and fail-closed VPN behavior are harder to reason about than routed mode
- debugging DNS and kill-switch behavior becomes less obvious
- provider clients often assume host-level routing, not arbitrary bridged transit

Verdict:

- Avoid for v1. Use routed/NAT mode instead.

## Easiest headless control interface

The easiest screen-free control surface is a local web UI.

Recommended access pattern:

- Pi advertises itself on the home network as `openspoofen.local`
- user opens the UI from a phone, tablet, or laptop
- UI allows login/onboarding, current status, and region switching

Fallback admin paths:

- SSH
- Raspberry Pi Connect

This is substantially better than requiring a monitor, keyboard, or direct terminal use.

## What the TV app will and will not believe

What the Pi can influence:

- public IP geolocation
- DNS path if the Pi owns DNS forwarding correctly
- traffic egress path for the connected device

What the Pi cannot guarantee:

- that every app accepts VPN-backed IP ranges
- that the app ignores account-region metadata
- that the app ignores device firmware region or app-store region
- that anti-VPN detection will not block playback

This is not literal GPS spoofing. It is network-path and IP-region control.

## Recommended hardware spec for v1

## Baseline recommendation

- Raspberry Pi 4 or Raspberry Pi 5
- 4 GB RAM preferred
- 16 GB microSD minimum, 32 GB preferred
- official or high-quality power supply
- case suitable for continuous operation

## Required peripherals and operator kit

For the supported laptop-assisted install path, the minimum practical kit is:

- Raspberry Pi 4 or Raspberry Pi 5 board
- microSD card: 16 GB minimum, 32 GB recommended
- microSD reader for the laptop
- proper USB-C power supply
- one Ethernet cable for either TV downstream or direct bench deployment
- a phone or laptop browser for the LAN UI

If the operator laptop does not have native Ethernet, add:

- USB-to-Ethernet adapter for the laptop

If you choose Raspberry Pi 5, add:

- active cooling or the official Pi 5 case with integrated fan

Why:

- Raspberry Pi officially recommends 5V/3A power for Pi 4 and 5V/5A for Pi 5.
- Raspberry Pi's getting-started guidance recommends at least 16 GB for Lite and 32 GB for typical Raspberry Pi OS installs.
- Pi 5 performs best with active cooling under sustained load.

## Best default SKU recommendation

- Raspberry Pi 4, 4 GB
- good quality 32 GB microSD
- Wi-Fi upstream
- Ethernet downstream to TV
- 15 W USB-C power supply
- simple passively cooled case or light active cooling

Why:

- lowest hardware complexity
- enough CPU for VPN routing and a small local UI
- avoids second-NIC dependency for the first release

## Best advanced SKU recommendation

- Raspberry Pi 5, 4 GB or 8 GB
- active cooling
- USB 3 Gigabit Ethernet adapter or validated PCIe Ethernet solution
- Ethernet upstream and Ethernet downstream
- 27 W USB-C power supply

Why:

- cleaner appliance story for users who want all-wired operation
- more future-proof for custom image builds and diagnostics

## Pitfalls to design around

- Single Ethernet on the board means one cable alone cannot represent both WAN and LAN.
- USB Ethernet adapters vary; not all are equal for stability and driver support.
- Some TVs cache DNS aggressively or behave oddly after region changes, so reboot or app restart workflows may still be needed.
- IPv6 can leak around an otherwise correct IPv4 VPN path if not handled deliberately.
- VPN provider LAN allowlisting rules can break forwarded traffic unless explicitly configured.

## Recommended product decision

For the first open-source version, document and support this default form factor first:

- upstream: Wi-Fi
- downstream: Ethernet to TV
- control interface: local web UI from another device
- provisioning: Raspberry Pi Imager plus first-boot onboarding

Then add a validated dual-Ethernet kit path once the core routing and VPN logic are stable.

## Highest-performance recommendation

If the goal is lowest latency and the highest headroom rather than the easiest first install, prefer this design:

- Raspberry Pi 5
- active cooling
- WireGuard as the primary dataplane
- Ethernet upstream
- Ethernet downstream through a second validated NIC
- no Wi-Fi in the steady-state traffic path unless used only for recovery or management

Why:

- WireGuard generally has lower overhead than OpenVPN-style paths on a Raspberry Pi.
- Removing Wi-Fi from the main traffic path removes extra airtime contention and jitter.
- Pi 5 has materially more CPU headroom for encrypted forwarding and status collection.
- Active cooling helps the device sustain throughput instead of throttling under continuous VPN load.

## Recommended supported install path

For operators working from a Windows laptop, document and support this as the easiest loading path:

- flash Raspberry Pi OS Lite with Raspberry Pi Imager on the laptop
- preconfigure hostname, user, password, Wi-Fi, and SSH in Imager
- boot the Pi headless
- deploy this repo over SSH from the laptop

This avoids requiring:

- monitor
- keyboard
- mouse
- direct serial console

It is a better fit than a direct single-cable USB provisioning story for Pi 4 and Pi 5.