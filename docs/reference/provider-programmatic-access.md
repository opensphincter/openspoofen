# Provider Programmatic Access

## Purpose

This document answers a narrower question than the general onboarding guide:

- does each supported provider expose a usable machine path for authentication or connection material?
- can the project obtain a token, credential, config file, or local control surface without scraping secrets from a desktop app?

These findings were checked against the providers' official support material on 2026-04-08.

## Summary matrix

| Provider | Repo support | Programmatic auth material | Programmatic control surface | Practical verdict |
| --- | --- | --- | --- | --- |
| WireGuard profiles | Native profile adapter | Yes, but user-managed `.conf` files rather than provider tokens | `wg-quick`, `wg`, or `nmcli` against imported configs | Strongest dataplane if configs are available |
| NordVPN | Native CLI adapter | Yes: account-generated access token | Yes: official Linux CLI | Best token-backed path in this repo |
| Mullvad | Native CLI adapter | Yes: account number, plus CLI-managed WireGuard key material | Yes: official CLI | Strong machine-friendly path even without tokens |
| ExpressVPN | Native CLI adapter | Partial: activation code, not a reusable token API | Yes: official CLI, and local MCP server after login | Scriptable after activation, but weaker for unattended onboarding |
| Proton VPN | Native CLI adapter | Partial: account password for CLI, or manual OpenVPN/WireGuard credentials/configs from dashboard | Yes: official CLI, but not headless-safe; manual configs also work | Usable, but not a clean headless token path |
| Surfshark | Manual OpenVPN adapter | Yes: manual connection username/password and downloadable configs | Manual OpenVPN/WireGuard config path; no first-class Linux CLI in this project | Works through exported credentials, not tokens |
| Mock | Test-only adapter | Yes: arbitrary local test token | Local-only simulated provider | Development only |

## Design conclusion

For this project, the providers fall into three groups.

### 1. True machine-friendly onboarding

- NordVPN
- Mullvad
- WireGuard profile ingestion

These are the cleanest fits for a Raspberry Pi appliance because they do not depend on desktop-only interaction patterns once the operator has obtained the account material.

### 2. Scriptable, but not truly token-centric

- ExpressVPN
- Proton VPN
- Surfshark

These can still be automated to a degree, but the automation depends on activation codes, account passwords, manual service credentials, or exported config files rather than a dedicated headless token flow.

### 3. Local test-only

- Mock provider

## Provider findings

## WireGuard profiles

Repo status:

- supported as the preferred dataplane through the `wireguard` provider

Automation material:

- one `.conf` file per region
- embedded keypair and endpoint information inside each WireGuard config

Programmatic control path:

- `wg-quick up/down`
- `wg show`
- `nmcli conn import type wireguard file ...` when using NetworkManager-backed imports

What this means for the project:

- this is not a provider token model
- the machine-readable artifact is the WireGuard config itself
- if the VPN vendor exposes WireGuard config download in its account dashboard, that is enough for this adapter

Verdict:

- strongest steady-state dataplane once configs are provisioned

## NordVPN

Repo status:

- supported through the official Linux CLI adapter

Verified official path:

- NordVPN documents headless Linux login with `nordvpn login --token <token>`
- the token is generated from Nord Account advanced settings
- temporary and non-expiring token options are documented
- NordVPN also documents CLI-driven connection and disconnection flows

Programmatic auth material:

- access token generated in the Nord account dashboard

Programmatic control path:

- official `nordvpn` CLI

Operational notes:

- the token is shown once and should be treated as a secret
- `nordvpn logout` expires the token unless the operator uses the persistent-token logout mode
- this project should never attempt to scrape tokens from a local desktop app or browser session

Verdict:

- best supported token-based onboarding path in this repo

## Mullvad

Repo status:

- supported through the official CLI adapter

Verified official path:

- Mullvad documents CLI-only operation on headless systems
- login is done with `mullvad account login <account-number>`
- WireGuard usage and tunnel inspection are documented in the CLI
- Mullvad documents `mullvad tunnel get`, which exposes tunnel options and current WireGuard key information

Programmatic auth material:

- Mullvad account number

Programmatic control path:

- official `mullvad` CLI

Important distinction:

- Mullvad does not need a token in the same way NordVPN does
- the machine credential is the account number itself
- for this project, that is sufficient to classify Mullvad as machine-friendly even without a dashboard-issued token

Verdict:

- strong programmatic fit; second-best provider in the repo after NordVPN for appliance automation

## ExpressVPN

Repo status:

- supported through the official CLI adapter

Verified official path:

- ExpressVPN documents Linux CLI installation and activation using an activation code file
- official commands exist for login, region listing, connect, disconnect, protocol changes, split tunneling, and network lock
- connection commands require either the GUI to be running or background mode to be enabled
- ExpressVPN now also documents a local MCP server, which exposes a local programmatic control surface after app login

Programmatic auth material:

- activation code from the account setup flow

Programmatic control path:

- official `expressvpnctl` CLI
- local MCP server after the app has been installed and authenticated

Limitations:

- this is not a clean reusable token flow for unattended bootstrap
- the MCP server is local control after activation, not a substitute for account bootstrap material
- activation is still less appliance-friendly than NordVPN token login or Mullvad account-number login

Verdict:

- scriptable after activation, but not as strong as NordVPN or Mullvad for headless onboarding

## Proton VPN

Repo status:

- supported through the official CLI adapter

Verified official path:

- Proton documents an official Linux CLI with `protonvpn signin [username]`
- Proton explicitly notes that the CLI does not currently work on headless setups
- Proton also documents manual OpenVPN setup using downloadable config files plus OpenVPN-specific username and password from the account dashboard
- Proton documents manual WireGuard setup using downloadable WireGuard config files from the account dashboard

Programmatic auth material:

- Proton account username and password for the official CLI
- manual OpenVPN username and password for OpenVPN exports
- downloadable WireGuard config files for manual WireGuard use

Programmatic control path:

- official `protonvpn` CLI on supported desktop-like Linux installs
- `openvpn` or `wg-quick`/`nmcli` using downloaded manual configs

Limitations:

- no clean headless token flow was identified in the official consumer docs reviewed here
- the official CLI is explicitly not suitable for headless setups right now
- this means Proton is only partially appliance-friendly unless the project leans on manual OpenVPN or WireGuard exports instead of the official CLI

Verdict:

- usable through exported credentials and configs, but not a top-tier headless automation path

## Surfshark

Repo status:

- supported in this repo through manual OpenVPN profiles

Verified official path:

- Surfshark documents manual connection credentials in the account dashboard under VPN -> Manual Setup
- these credentials are separate from the account email and password
- Surfshark documents downloading OpenVPN configuration bundles from a direct configuration endpoint used in its Linux guide
- Surfshark also documents manual WireGuard setup for Linux, though this repo currently models Surfshark through OpenVPN profiles

Programmatic auth material:

- manual service username and password
- downloadable OpenVPN configs
- manually generated WireGuard configuration material for WireGuard-based manual setups

Programmatic control path:

- `openvpn` with downloaded `.ovpn` files in the current repo design
- potential WireGuard import path if the project later adds a dedicated Surfshark WireGuard adapter

Limitations:

- no first-class native Linux CLI token flow is represented in this repo
- this is a manual credential and config export model, not a token model

Verdict:

- workable for programmatic use, but only through exported manual credentials and configuration files

## Mock provider

Repo status:

- local development and test only

Programmatic auth material:

- arbitrary token string accepted by the mock adapter

Programmatic control path:

- local state file only

Verdict:

- not a real VPN integration; included only so UI and workflow tests do not depend on a live provider

## Recommendations for this repo

### Best providers for unattended or semi-attended appliance onboarding

1. NordVPN
2. Mullvad
3. WireGuard profile import from providers that let the operator download configs directly

### Providers that should be documented as manual-export driven

- Proton VPN
- Surfshark
- ExpressVPN

### Security boundary

The repo should continue to follow this rule:

- never try to extract tokens or credentials from an installed desktop app, browser storage, or local system keychain

Supported acquisition paths should stay limited to:

- provider dashboard token generation
- provider dashboard manual credential export
- provider dashboard config download
- official CLI login with operator-supplied material