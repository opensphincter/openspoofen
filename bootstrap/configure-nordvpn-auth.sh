#!/usr/bin/env bash

set -euo pipefail

if [[ "${RP_NORDVPN_BOOTSTRAP_ENABLED:-true}" != "true" ]]; then
    echo "NordVPN bootstrap disabled; skipping."
    exit 0
fi

if ! command -v nordvpn >/dev/null 2>&1; then
    echo "NordVPN CLI not installed; skipping bootstrap."
    exit 0
fi

TOKEN="${NORDVPN_ACCESS_TOKEN:-${RP_NORDVPN_ACCESS_TOKEN:-}}"
PROVIDER_USER="${RP_PROVIDER_USER:-}"
LAN_DISCOVERY="${RP_NORDVPN_LAN_DISCOVERY:-true}"
AUTO_CONNECT="${RP_NORDVPN_AUTOCONNECT:-true}"
FIREWALL="${RP_NORDVPN_FIREWALL:-true}"
KILLSWITCH="${RP_NORDVPN_KILLSWITCH:-true}"
ALLOWLIST_SUBNET="${RP_NORDVPN_ALLOWLIST_SUBNET:-}"
TV_ENV_FILE="${RP_TV_ENV_FILE:-/etc/openspoofen/tv-ethernet-mode.env}"

is_true() {
    local value="${1:-}"
    [[ "${value,,}" =~ ^(1|true|yes|on|enable|enabled)$ ]]
}

if [[ -f "$TV_ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    . "$TV_ENV_FILE"
fi

if is_true "${RP_TV_ETHERNET_MODE:-false}"; then
    FIREWALL="false"
    KILLSWITCH="false"
    echo "TV Ethernet mode detected; disabling NordVPN firewall and kill switch so appliance nftables owns forwarded fail-closed behavior."
fi

derive_tv_allowlist_subnet() {
    local lan_address="${1:-}"
    if [[ -z "$lan_address" ]]; then
        return 1
    fi

    python3 - "$lan_address" <<'PY'
import ipaddress
import sys

try:
    network = ipaddress.ip_interface(sys.argv[1]).network
except ValueError:
    sys.exit(1)

print(network)
PY
}

resolve_allowlist_subnet() {
    if [[ -n "$ALLOWLIST_SUBNET" ]]; then
        printf '%s\n' "$ALLOWLIST_SUBNET"
        return 0
    fi

    if [[ -f "$TV_ENV_FILE" ]]; then
        local tv_lan_address=""
        # shellcheck disable=SC1090
        . "$TV_ENV_FILE"
        tv_lan_address="${RP_TV_LAN_ADDRESS:-}"
        if [[ -n "$tv_lan_address" ]]; then
            derive_tv_allowlist_subnet "$tv_lan_address"
            return 0
        fi
    fi

    printf '%s\n' '192.168.50.0/24'
}

run_nordvpn() {
    if [[ -n "$PROVIDER_USER" ]] && [[ "$(id -u)" == "0" ]] && command -v runuser >/dev/null 2>&1; then
        runuser -u "$PROVIDER_USER" -- nordvpn "$@"
        return
    fi

    nordvpn "$@"
}

if ! run_nordvpn account >/dev/null 2>&1; then
    if [[ -z "$TOKEN" ]]; then
        echo "NordVPN token not present; skipping bootstrap login."
        exit 0
    fi

    run_nordvpn login --token "$TOKEN"
fi

run_nordvpn set technology nordlynx >/dev/null 2>&1 || true
run_nordvpn set lan-discovery "$([[ "$LAN_DISCOVERY" == "true" ]] && echo enabled || echo disabled)" >/dev/null 2>&1 || true
run_nordvpn set autoconnect "$([[ "$AUTO_CONNECT" == "true" ]] && echo enabled || echo disabled)" >/dev/null 2>&1 || true
run_nordvpn set firewall "$([[ "$FIREWALL" == "true" ]] && echo enabled || echo disabled)" >/dev/null 2>&1 || true
run_nordvpn set killswitch "$([[ "$KILLSWITCH" == "true" ]] && echo enabled || echo disabled)" >/dev/null 2>&1 || true

ALLOWLIST_SUBNET="$(resolve_allowlist_subnet || true)"

if [[ -n "$ALLOWLIST_SUBNET" ]]; then
    run_nordvpn allowlist add subnet "$ALLOWLIST_SUBNET" >/dev/null 2>&1 || true
fi

echo "NordVPN bootstrap settings ensured. firewall=${FIREWALL} killswitch=${KILLSWITCH} allowlist_subnet=${ALLOWLIST_SUBNET:-none}"