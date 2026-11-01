#!/usr/bin/env bash

set -euo pipefail

SSID="${RP_WIFI_SSID:-}"
PASSWORD="${RP_WIFI_PASSWORD:-}"
COUNTRY="${RP_WIFI_COUNTRY:-}"
CONNECTION_NAME="${RP_WIFI_CONNECTION_NAME:-openspoofen-uplink}"

if [[ -z "$SSID" || -z "$PASSWORD" ]]; then
    echo "Wi-Fi uplink env not configured; skipping."
    exit 0
fi

if [[ -n "$COUNTRY" ]]; then
    if command -v raspi-config >/dev/null 2>&1; then
        raspi-config nonint do_wifi_country "$COUNTRY" || true
    fi
    if command -v iw >/dev/null 2>&1; then
        iw reg set "$COUNTRY" || true
    fi
fi

if command -v rfkill >/dev/null 2>&1; then
    rfkill unblock wifi || true
fi

nmcli radio wifi on || true

if ! nmcli -t -f NAME connection show | grep -Fxq "$CONNECTION_NAME"; then
    nmcli connection add type wifi ifname wlan0 con-name "$CONNECTION_NAME" ssid "$SSID"
fi

nmcli connection modify "$CONNECTION_NAME" \
    connection.autoconnect yes \
    802-11-wireless.mode infrastructure \
    802-11-wireless.ssid "$SSID" \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "$PASSWORD" \
    ipv4.method auto \
    ipv6.method ignore

nmcli connection up "$CONNECTION_NAME" || true

echo "Wi-Fi uplink profile updated: $CONNECTION_NAME"