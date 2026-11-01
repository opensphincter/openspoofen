# Security policy

OpenSpoofen sits between a home network and a TV and holds VPN account tokens, so security reports get priority.

## Supported versions

Only the latest release receives security fixes.

| Version | Supported |
| --- | --- |
| 0.2.x | Yes |
| Older | No |

## Reporting a vulnerability

Please do not open a public issue for a vulnerability.

Report it privately through GitHub: on the repository's **Security** tab, choose **Report a vulnerability**. Include the version, your topology (upstream and downstream links), the steps to reproduce, and what an attacker gains.

You can expect an acknowledgement within 7 days and an assessment within 14. Fixes are released as a patch version and credited in the changelog unless you ask otherwise.

## Scope

In scope:

- The LAN web UI and its API: authentication, pairing, sessions, redirects and input handling.
- Provider credential handling: tokens and configs written to `/etc/openspoofen/` and passed to provider CLIs.
- Routing, DNS, IPv6 and kill-switch behaviour that could leak traffic outside the tunnel.
- The install and bootstrap scripts and the systemd units.

Out of scope:

- Vulnerabilities in the VPN providers' own clients or services. Report those to the provider.
- Streaming services detecting or blocking VPN use. That is expected behaviour, not a vulnerability.
- Attacks that need root on the Pi or physical access to it.
