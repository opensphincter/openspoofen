# Testing And Simulation

## Goal

This project needs a layered test stack:

- fast UI and provider-behavior checks that run anywhere
- Linux network-path checks that exercise routing, DNS, and fail-closed logic
- image-build and first-boot validation
- real Raspberry Pi validation for release confidence

No single tool covers all of that. The useful approach is to combine open-source tools by failure mode.

## Layer 1: local unit and UI tests

This is the fastest loop and should run on every change.

What it covers:

- Flask UI rendering
- provider metadata and onboarding flow shape
- mock-provider behavior
- parser tests for provider CLI output

How to run:

1. Install the development dependencies with `pip install -e .[dev]`.
2. Set `RP_PROVIDER=mock` if you want to run the UI in mock mode.
3. Run `pytest`.
4. Optionally run `python -m openspoofen.web` and use `http://127.0.0.1:8080`.

This layer is intentionally safe. It does not touch real VPN connections or system networking.

## Layer 2: Linux namespace lab

This remains the most useful non-hardware network test strategy.

Model:

- `wan` namespace represents upstream internet
- `pi` namespace represents the appliance
- `tv` namespace represents the downstream device

Suggested shape:

```text
wan <-> pi <-> tv
```

Use Linux network namespaces and `veth` pairs to validate:

- upstream and downstream interface assumptions
- routing and NAT behavior
- dnsmasq DHCP and DNS behavior
- nftables forwarding and fail-closed rules
- DNS and IPv6 leak posture

What it still does not prove:

- provider app behavior on Raspberry Pi OS
- USB NIC quirks
- thermal, power, or reboot behavior on real hardware

## Layer 3: image-build testing

Two open-source tools are worth tracking here.

### `pi-gen`

Why it matters:

- this is the standard Raspberry Pi OS image build pipeline
- it is the best fit when the project is ready to ship a reproducible appliance image
- it can use QEMU during image generation to support non-Pi hosts

Use it for:

- release image generation
- first-boot content injection
- reproducible OS customizations

### `rpi-image-gen`

Why it matters:

- modern YAML-driven Raspberry Pi image generation
- built-in hook model and test harness
- useful for experimenting with repeatable appliance builds before fully committing to a release pipeline

Use it for:

- faster iteration on image composition
- build hooks and integration experiments
- validating installer and first-boot artifacts in a structured pipeline

## Layer 4: VM and infrastructure validation

### QEMU

QEMU supports Arm guests and Raspberry Pi board models, and also supports the generic `virt` machine for faster Linux-focused validation.

Use it for:

- boot validation of generic Arm userspace images
- first-boot and service smoke tests
- exercising systemd, dnsmasq, and the web UI in a Linux environment closer to production than the mock runtime

Important limitation:

- real Raspberry Pi images do not automatically boot on arbitrary QEMU machine models, so image-level emulation has to be planned carefully

### Testinfra

`pytest-testinfra` is a good fit for asserting host state over `local`, `ssh`, `docker`, or `podman` backends.

Use it for checks like:

- expected packages are installed
- systemd services are enabled and running
- nftables or sysctl state is present
- configuration files exist with the expected permissions

This repo includes a starter example at `examples/testinfra/test_appliance.py`.

### openQA

openQA is the heaviest tool in this list, but it is the strongest open-source option for appliance-style image testing when the project reaches that maturity level.

Why it matters:

- automated OS installation and boot testing
- screenshot and serial-console driven validation
- QEMU-backed image tests
- multi-machine and network-oriented test support
- CI-triggered job scheduling and result reporting

Use it for:

- release-grade image smoke tests
- first-boot wizard or onboarding validation
- regression testing across image revisions

It is not the right first step for this repo, but it is a credible later-stage path once the image pipeline stabilizes.

## Optional network-topology tooling

`containerlab` is not Raspberry Pi specific, but it is useful when you want repeatable Linux network topologies and virtual wiring on a Linux host.

Good uses here:

- network-topology experimentation
- testing supporting services and Linux network clients in a declarative lab
- CI-friendly network-lab bring-up on Linux workers

It is optional. Linux namespaces are the simpler first stop for this project.

## Recommended test strategy by milestone

### Early development

- run unit tests and the mock UI on every change
- keep parser tests for provider CLI output samples

### Networking milestone

- add Linux namespace lab scripts
- validate default route, DNS path, and fail-closed behavior
- add Testinfra checks for expected host configuration

### Image milestone

- use `pi-gen` or `rpi-image-gen` for repeatable images
- smoke test images in QEMU where practical
- verify first-boot services, systemd units, and config ingestion

### Release candidate

- run namespace lab plus real Pi hardware tests
- validate the target provider clients on Raspberry Pi OS
- document manual hardware results in release notes or validation docs

## Release blocking checks

Before calling the appliance usable, verify all of these on hardware:

- downstream TV gets DHCP and DNS from the Pi
- public IP matches the selected VPN region
- DNS egress matches the intended path
- no unintended IPv6 path exists
- switching region updates tunnel state and keeps downstream connectivity working
- VPN loss blocks downstream egress if fail-closed mode is enabled
- reboot preserves the configured routing and control-plane state