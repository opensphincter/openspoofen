# Provider Account Integration

## Purpose

This document explains the easiest current onboarding path for each provider adapter in the repo.

For a provider-by-provider review of token access, manual credential export, and other machine-usable onboarding material, see `docs/reference/provider-programmatic-access.md`.

The important distinction is this:

- some providers have a real Linux CLI that can be wrapped directly
- some providers are only practical through manual OpenVPN profiles

## NordVPN

Recommended status: default production target

What you need:

- official NordVPN Linux CLI installed on Raspberry Pi OS Lite 64-bit
- a headless access token or another supported login flow

UI field:

- `Access token`

Typical steps:

1. Install the official NordVPN Linux client on the Pi.
2. Generate or retrieve a NordVPN access token.
3. Enter the token in the UI and authenticate.
4. Switch regions from the provider page.

Why this is the best path right now:

- official Raspberry Pi OS support
- documented CLI
- token-based headless onboarding

## Mullvad

Recommended status: strongest alternative provider

What you need:

- Mullvad Linux app and CLI installed
- your Mullvad account number

UI field:

- `Account number`

Typical steps:

1. Install Mullvad on the Pi.
2. Enter the account number in the UI.
3. Authenticate and then choose a country or city.
4. Validate LAN access and lockdown mode against the appliance firewall model.

Why it is attractive:

- mature Linux CLI
- good location control
- solid long-term alternative to NordVPN

## ExpressVPN

Recommended status: supported, but less appliance-friendly

What you need:

- official ExpressVPN Linux client for Raspberry Pi OS 64-bit
- an ExpressVPN activation code

UI field:

- `Activation code`

Typical steps:

1. Install ExpressVPN on the Pi.
2. Enter the activation code in the UI.
3. Authenticate.
4. Confirm `expressvpnctl background enable` has been applied so headless connect and disconnect commands work correctly.

Main caveat:

- the activation flow is workable, but not as clean for an appliance as NordVPN’s token approach

## Proton VPN

Recommended status: supported with extra validation required

What you need:

- official Proton VPN CLI installed
- NetworkManager and required keyring pieces available on the image
- Proton username and password

UI fields:

- `Username`
- `Password`

Typical steps:

1. Install the Proton VPN CLI and its dependencies.
2. Enter the username and password in the UI.
3. Authenticate.
4. Validate the exact headless behavior on the target Raspberry Pi OS build before treating this as production-ready.

Main caveat:

- Proton’s Linux onboarding is less predictable for a fully headless appliance than NordVPN or Mullvad

## Surfshark

Recommended status: supported through manual OpenVPN profiles

What you need:

- `openvpn` installed on the Pi
- Surfshark manual OpenVPN configuration files
- Surfshark manual service username and password

UI fields:

- `Service username`
- `Service password`

File placement:

- store `.ovpn` files under `configs/surfshark/`

Typical steps:

1. Download manual OpenVPN profiles from Surfshark.
2. Place them under `configs/surfshark/`.
3. Enter the service credentials in the UI once.
4. Connect using the profile-derived country and city list.

Main caveat:

- this is a manual OpenVPN path, not a first-class Surfshark Linux client integration

## Mock Provider

Recommended status: local development only

What you need:

- nothing beyond Python dependencies

UI field:

- `Demo token`

Use it for:

- onboarding flow development
- UI tests
- provider-selection behavior

## Operational Notes

- Do not store real tokens, passwords, or service credentials in the repository.
- Validate DNS, IPv6, and fail-closed behavior after every provider integration change.
- A connected VPN CLI is not sufficient evidence that the downstream client is safely routed.