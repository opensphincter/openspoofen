#!/usr/bin/env bash

set -euo pipefail

if [[ "${RP_TV_ETHERNET_MODE:-false}" != "true" ]]; then
    echo "TV Ethernet mode disabled; skipping."
    exit 0
fi

LAN_IFACE="${RP_TV_LAN_IFACE:-eth0}"
UPLINK_IFACE="${RP_TV_UPLINK_IFACE:-wlan0}"
VPN_IFACE="${RP_TV_VPN_IFACE:-nordlynx}"
LAN_ADDRESS="${RP_TV_LAN_ADDRESS:-192.168.50.1/24}"
DHCP_START="${RP_TV_DHCP_START:-192.168.50.50}"
DHCP_END="${RP_TV_DHCP_END:-192.168.50.150}"
DHCP_LEASE="${RP_TV_DHCP_LEASE:-12h}"
CONNECTION_NAME="${RP_TV_CONNECTION_NAME:-openspoofen-tv-lan}"
LAN_MTU="${RP_TV_LAN_MTU:-1420}"
ALLOW_UPLINK_FALLBACK="${RP_TV_ALLOW_UPLINK_FALLBACK:-false}"

is_true() {
    local value="${1:-}"
    [[ "${value,,}" =~ ^(1|true|yes|on|enable|enabled)$ ]]
}

FORWARD_RULES=(
    '        ct state related,established accept'
    "        iifname \"$LAN_IFACE\" oifname \"$VPN_IFACE\" accept"
)

POSTROUTING_RULES=(
    "        oifname \"$VPN_IFACE\" masquerade"
)

UPLINK_SUMMARY="vpn-only fail-closed forwarding"

if is_true "$ALLOW_UPLINK_FALLBACK"; then
    FORWARD_RULES+=("        iifname \"$LAN_IFACE\" oifname \"$UPLINK_IFACE\" accept")
    POSTROUTING_RULES+=("        oifname \"$UPLINK_IFACE\" masquerade")
    UPLINK_SUMMARY="uplink fallback enabled"
fi

nmcli connection delete "$CONNECTION_NAME" >/dev/null 2>&1 || true
nmcli connection add type ethernet ifname "$LAN_IFACE" con-name "$CONNECTION_NAME" 802-3-ethernet.mtu "$LAN_MTU" ipv4.method manual ipv4.addresses "$LAN_ADDRESS" ipv4.never-default yes ipv6.method disabled autoconnect yes
nmcli connection up "$CONNECTION_NAME" || true

install -d /etc/dnsmasq.d
cat > /etc/dnsmasq.d/openspoofen-tv.conf <<EOF
interface=$LAN_IFACE
bind-interfaces
domain-needed
bogus-priv
dhcp-range=$DHCP_START,$DHCP_END,255.255.255.0,$DHCP_LEASE
dhcp-option=option:router,${LAN_ADDRESS%/*}
dhcp-option=option:dns-server,${LAN_ADDRESS%/*}
dhcp-option=option:mtu,$LAN_MTU
EOF
systemctl restart dnsmasq

cat > /etc/sysctl.d/90-openspoofen-tv.conf <<EOF
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=0
net.ipv6.conf.default.forwarding=0
EOF
sysctl --system >/dev/null

install -d /etc/openspoofen
nft delete table inet openspoofen >/dev/null 2>&1 || true
nft delete table ip openspoofen_nat >/dev/null 2>&1 || true
FORWARD_RULES_TEXT="$(printf '%s\n' "${FORWARD_RULES[@]}")"
POSTROUTING_RULES_TEXT="$(printf '%s\n' "${POSTROUTING_RULES[@]}")"
cat > /etc/openspoofen/tv-lan.nft <<EOF
table inet openspoofen {
    chain mss_clamp {
        type filter hook forward priority mangle;
        policy accept;
        oifname "$VPN_IFACE" tcp flags syn tcp option maxseg size set rt mtu
    }

    chain forward {
        type filter hook forward priority 0;
        policy drop;
$FORWARD_RULES_TEXT
    }
}

table ip openspoofen_nat {
    chain postrouting {
        type nat hook postrouting priority 100;
        policy accept;
$POSTROUTING_RULES_TEXT
    }
}
EOF
nft -f /etc/openspoofen/tv-lan.nft

echo "TV Ethernet bench mode applied on $LAN_IFACE with upstream $UPLINK_IFACE and VPN interface $VPN_IFACE ($UPLINK_SUMMARY)"