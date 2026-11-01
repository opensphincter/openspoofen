# LAN deployment patterns

How OpenSpoofen runs as a LAN appliance: how it binds, how it stays findable,
how its UI authenticates, how its boot sequence is ordered, and how it recovers
when the LAN side goes wrong. Written for reuse by sibling projects, in
particular a home server that other devices talk to (Küğ) and a home sync host
that a mobile device checks in with (Ulak).

Every claim is grounded in this repository: the systemd units in `systemd/`,
the scripts in `bootstrap/`, and the application code in `src/openspoofen/`.
Anything that is an interpretation rather than a direct reading is marked
*(inferred)*. Line-level pointers are given so a reader can verify each pattern
against the source before copying it.

## The patterns at a glance

| # | Pattern | Where it lives |
| --- | --- | --- |
| 1 | Bind wide, gate per request by source address | `serve.py`, `web.py`, `auth.py` |
| 2 | Non-LAN sources get 404, not 403 | `web.py` (`enforce_lan_access_and_authentication`) |
| 3 | Password plus device pairing, set up on first boot | `auth.py`, `web.py` setup flow |
| 4 | One hostname, advertised by mDNS as `<hostname>.local` | `bootstrap/install.sh`, avahi-daemon |
| 5 | If you serve a downstream network, own it: static address, your own DHCP/DNS, fail-closed forwarding | `bootstrap/configure-tv-ethernet-mode.sh` |
| 6 | Boot as a chain of idempotent oneshots, then one supervised service | `systemd/*.service` |
| 7 | Bootstrap steps skip, never fail, when their inputs are absent | `bootstrap/configure-*.sh` |
| 8 | Coordinate units through env files, not only through systemd ordering | `/etc/openspoofen/*.env`, unit `EnvironmentFile=` lines |
| 9 | Secrets only in root-owned env files, mode 600, outside the repo | `bootstrap/install.sh`, unit files |
| 10 | On-disk state is small JSON that must heal, not wedge | `auth.py`, provider state readers |

## 1. LAN-only posture: bind wide, gate per request

The web UI does **not** bind to a LAN interface. Gunicorn binds
`{RP_HOST}:{RP_PORT}`, defaulting to `0.0.0.0:8080` (`serve.py`,
`config.py`), so the socket listens on every interface, including the VPN
tunnel and any future interface.

LAN-only is enforced one layer up, on every request. A Flask `before_request`
handler (`web.py: enforce_lan_access_and_authentication`) resolves
`request.remote_addr` and refuses the request unless the address is loopback,
RFC1918-private, or link-local (`auth.py: is_private_lan_address`, built on
`ipaddress`; IPv6 zone ids are stripped before parsing). Refusal is a **404**,
so from outside the LAN the service does not confirm it exists.

Why this shape *(inferred from the topology code)*: the appliance has several
interfaces whose roles change with configuration (Wi-Fi uplink, Ethernet
uplink, a downstream TV-facing Ethernet port, the `nordlynx` tunnel). Binding
to one address at process start would break whenever the topology flips;
gating by source address is stable across all of them. The home router is
expected never to port-forward to the box; the gate is the second line of
defense if that assumption ever fails, and it also keeps the UI unreachable
from the far side of the VPN tunnel.

The network layer backs the application layer in TV Ethernet mode (pattern
5): the nftables forward chain defaults to drop, and in normal mode the
NordVPN firewall and kill switch are enabled by the bootstrap unit (section
5).

Practical consequences for reuse:

- Even `/healthz` sits behind the gate; health checks must originate on the
  LAN (or loopback).
- Anything that proxies or NATs in front of the service changes
  `remote_addr` and can lock everyone out or let everyone in. The pattern
  assumes the service sees real client addresses, which holds on a flat home
  LAN.
- When copying this, keep the 404. A 403 tells a scanner the service exists
  and is worth attacking.

## 2. Addressing and findability

**Uplink address: DHCP.** The box does not pick its own home-network address.
The Wi-Fi uplink profile created by `bootstrap/configure-wifi-uplink.sh` sets
`ipv4.method auto` and `connection.autoconnect yes` in NetworkManager, so the
home router assigns the address and the box rejoins on its own after outages
or reboots.

**Name: one hostname, mDNS-advertised.** `bootstrap/install.sh` sets the
system hostname from `RP_DEVICE_HOSTNAME` (default `openspoofen`) via
`hostnamectl` and maintains the `127.0.1.1` entry in `/etc/hosts`. The
installer also installs `avahi-daemon`, which advertises the host as
`openspoofen.local` on the LAN (README: "browse to
`http://openspoofen.local:8080`"). Clients never need to know the DHCP
address; the `.local` name survives address changes. If HTTPS is enabled and
no certificate is configured, the installer generates a self-signed
certificate for `<hostname>.local` (`bootstrap/generate-local-tls-cert.sh`),
so the name and the certificate always match.

**Downstream address: static, because the box is the network.** In TV
Ethernet mode the roles invert. The TV-facing interface gets a fixed
`192.168.50.1/24` (NetworkManager, `ipv4.method manual`,
`ipv4.never-default yes`, so it never steals the default route), and the box
runs dnsmasq as DHCP and DNS server for that segment (pool
`192.168.50.50` to `192.168.50.150`, 12h leases), handing out itself as
router and DNS (`bootstrap/configure-tv-ethernet-mode.sh`). The UI then reads
the dnsmasq leases file (`RP_TV_LEASES_PATH`, default
`/var/lib/misc/dnsmasq.leases`) plus `ip neigh` output to know whether the TV
is present and which address it took (`web.py` network snapshot). The
dashboard's "TV is connected" signal is the lease, not a ping *(grounded in
the probe code; the leases file and neighbor table are the only presence
sources it consults)*.

Transfer notes:

- Küğ (home server): the DHCP-plus-mDNS half is the reusable part. A service
  that other LAN devices must find should take a hostname, advertise
  `<hostname>.local` via avahi, and never hardcode an address.
- Ulak (sync host): the same applies to the machine the phone syncs with on
  home Wi-Fi. The sync endpoint should be discoverable by name, because the
  host's DHCP address will change eventually *(inferred: consumer routers
  rotate leases; nothing in either project pins them)*.

## 3. LAN UI authentication

Three layers, in the order a request meets them (`web.py`, `auth.py`):

1. **Source gate** (pattern 1). Non-LAN sources never reach authentication.
2. **Password.** First boot has no password: the app boots into a setup mode
   (`auth.py` bootstrap state) and every page redirects to `/setup`, where
   the owner creates the LAN password (minimum 8 characters). Passwords are
   stored as a salted scrypt hash (Werkzeug `generate_password_hash`) in the
   auth state file under `/var/lib/openspoofen`, never in the repo or the env
   files. `RP_SECRET_KEY` signs the Flask session; sessions persist for
   `RP_SESSION_PERSIST_DAYS` (default 30) so the TV browser is not asked for
   the password daily. As of 0.2.0 the session cookie is HttpOnly +
   SameSite=Lax, plus Secure when HTTPS is enabled.
3. **Browser pairing.** Setup also mints a pairing token. Browsers prove
   pairing with a long-lived `rp_pairing` cookie whose value is the
   HMAC-SHA256 of the pairing token under the app secret, so the token itself
   never travels after setup. Login from an unpaired browser works with the
   password alone by default; setting `RP_REQUIRE_PAIRING_TOKEN=true` makes
   the pairing token mandatory for new browsers, which is the stricter
   posture for a busier household. The pairing token is shown once on the
   setup surface and is also displayed in the config panel for the owner.

The trust anchor is presence: anyone already on the LAN who reaches first
boot can claim the appliance. That is deliberate for a single-owner device
and is the main thing to reconsider before copying this model to anything
multi-tenant *(inferred: the code has no concept of a second user; all
state is a single owner record)*.

What the 0.2.0 upgrade changed here: constant-time pairing token comparison
(`hmac.compare_digest`), the cookie flags above, an open-redirect fix on the
login `next` parameter, and corrupt-auth-state recovery (section 6).

## 4. Boot sequence and systemd ordering

Four units, three idempotent oneshots and one supervised service:

| Unit | Type | Runs after | Job |
| --- | --- | --- | --- |
| `openspoofen-wifi-uplink.service` | oneshot, `RemainAfterExit` | `NetworkManager.service` | Create/update the NetworkManager Wi-Fi profile from the secrets env file (autoconnect on, WPA-PSK), set Wi-Fi country, unblock rfkill, bring the connection up |
| `openspoofen-tv-lan.service` | oneshot, `RemainAfterExit` | `NetworkManager.service`, `openspoofen-wifi-uplink.service` | TV Ethernet mode: static downstream address, dnsmasq config + restart, IPv4 forwarding sysctls, nftables tables (fail-closed forward, NAT masquerade via the VPN interface only) |
| `openspoofen-nordvpn-bootstrap.service` | oneshot, `RemainAfterExit` | `network-online.target` | Log NordVPN in with the token if not already logged in; set technology (NordLynx), LAN discovery, autoconnect, firewall, kill switch; allowlist the LAN subnet so the TV segment stays reachable |
| `openspoofen-web.service` | simple, `Restart=on-failure`, `RestartSec=5` | `network-online.target`, `openspoofen-nordvpn-bootstrap.service` | Run the UI from `/opt/openspoofen` under gunicorn (`python -m openspoofen.serve`) |

Why the order matters:

- **NetworkManager before everything network-shaped.** Both network
  oneshots drive `nmcli`; running before NetworkManager exists would fail
  pointlessly. They declare `After=` and `Wants=` on it rather than letting
  enablement order decide.
- **Uplink before TV-LAN.** `tv-lan` declares `After`/`Wants` on
  `wifi-uplink`, so the internet path profile exists before the downstream
  segment and its firewall rules (which reference the uplink and VPN
  interfaces) are applied.
- **network-online before the provider bootstrap.** The NordVPN bootstrap
  may need to log in, which needs working internet; `network-online.target`
  is the honest gate for that. The web service also waits for it.
- **Provider bootstrap before the web UI.** The UI renders provider state
  from the first request; starting it after the bootstrap oneshot means the
  first dashboard read already sees a logged-in, configured provider.
- **tv-lan and nordvpn-bootstrap are deliberately not ordered against each
  other.** They coordinate through a file instead: both read
  `/etc/openspoofen/tv-ethernet-mode.env`, and when TV Ethernet mode is on,
  the NordVPN script forces the NordVPN firewall and kill switch **off** so
  the appliance's own nftables owns the fail-closed behavior (two competing
  firewalls would be worse than one). Coordination-by-shared-env is the
  pattern to copy when two boot steps must agree but neither is truly
  "before" the other.

`bootstrap/install.sh` is the entry point that makes this real: it installs
packages (including avahi-daemon, dnsmasq, NetworkManager, nftables),
rsyncs the repo to `/opt/openspoofen`, creates `/etc/openspoofen/openspoofen.env`
(mode 600) from the example only if absent, creates `/var/lib/openspoofen`
and migrates any legacy `var/*.json` state into it without overwriting,
installs the four units, enables all of them, and restarts them in
dependency order. Re-running it is the upgrade path; nothing in it requires
manual cleanup first *(grounded in the script's guards: `install` only if
missing, `cp -n` for state, `rsync --delete` for code)*.

Secrets placement (pattern 9): each unit loads only the env files it needs
via `EnvironmentFile=-` (the leading dash makes a missing file non-fatal).
Owner secrets live in `/etc/openspoofen/secrets/*.local.env` (Wi-Fi PSK,
NordVPN token), referenced by the units, created outside this repository,
and never committed. The application-level rule matches: secrets reach the
box as env files at install time, full stop.

## 5. Fail-closed forwarding (the LAN safety property)

TV Ethernet mode exists so the TV can only reach the internet through the
VPN. The enforcement is in `configure-tv-ethernet-mode.sh`'s nftables
tables, rebuilt from scratch at every boot (`nft delete table` then load):

-
...[truncated 3122 chars]