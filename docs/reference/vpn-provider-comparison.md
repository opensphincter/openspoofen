# VPN Provider Comparison

## Purpose

This comparison is about appliance fit for a Raspberry Pi geo-switch, not consumer marketing rankings.

The relevant questions are:

- Does the provider expose a workable Linux command path?
- Does it fit Raspberry Pi OS or a similar Debian base?
- Is headless onboarding realistic?
- Can location switching be wrapped safely?
- Does the implementation need a native CLI or a manual OpenVPN fallback?

## Current adapter summary

| Provider | Current repo support | Appliance fit | Notes |
| --- | --- | --- | --- |
| NordVPN | Native CLI adapter | Best default choice | Official Raspberry Pi OS support and token-based login make it the cleanest production target |
| Mullvad | Native CLI adapter | Strong alternative | Good Linux CLI and region controls, but still needs Pi-specific validation |
| ExpressVPN | Native CLI adapter | Good but secondary | CLI works, but activation and background-mode assumptions are less appliance-friendly |
| Proton VPN | Native CLI adapter | Medium with caveats | Works as an adapter target, but headless onboarding still needs careful validation |
| Surfshark | Manual OpenVPN adapter | Medium | Realistic only through downloaded `.ovpn` profiles and manual service credentials |
| Mock | Test-only adapter | Development only | Safe local simulator for UI and workflow development |

## NordVPN

Why it fits best:

- official Linux support includes Raspberry Pi OS
- official CLI exists
- token-based headless login exists
- country switching and status queries are scriptable
- LAN allowlisting requirements are documented

Recommendation:

- keep NordVPN as the default production provider target

## Mullvad

Why it is attractive:

- mature Linux support
- strong CLI
- account-number-based onboarding works well in a headless UI
- lockdown mode and LAN settings fit the appliance security model

Recommendation:

- treat Mullvad as the primary alternative provider

## ExpressVPN

Why it is viable:

- official Linux client supports Raspberry Pi OS 64-bit
- CLI exposes connect, disconnect, regions, protocol, and network-lock controls

Why it is not the best default:

- activation is less appliance-friendly than a token-based flow
- connect and disconnect behavior depends on background mode

Recommendation:

- support it, but do not make it the default appliance path

## Proton VPN

Why it is mixed:

- CLI exists and can be wrapped
- Linux integration depends more heavily on NetworkManager and keyring behavior
- headless behavior needs direct validation on the exact image shipped by this project

Recommendation:

- keep it supported, but document it as a higher-risk path than NordVPN or Mullvad

## Surfshark

Why the implementation differs:

- the practical Linux path for this project is manual OpenVPN configuration rather than a first-class native CLI
- this means profile management and service credentials must be handled explicitly

Recommendation:

- support it through manual OpenVPN profiles and be explicit that this is not equivalent to a native app integration

## Product strategy

### Default production path

- NordVPN first

### Strong alternative path

- Mullvad second

### Additional supported paths

- ExpressVPN
- Proton VPN
- Surfshark through manual OpenVPN

## UI implications

The UI should stay generic and render provider-specific behavior through metadata.

That means the product surface needs to keep these concepts generic:

- provider
- authentication fields
- onboarding steps
- location catalog
- connect and disconnect actions
- status summary
- provider caveats

## Practical conclusion

If the goal is an open-source Raspberry Pi geo-switch that can be delivered without fragile manual setup, NordVPN remains the best default target and Mullvad is the best alternative. The other providers are now represented in the repo, but they carry different operational constraints and should be documented that way instead of being treated as identical.