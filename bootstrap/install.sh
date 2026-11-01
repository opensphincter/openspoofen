#!/usr/bin/env bash

set -euo pipefail

APP_ROOT="/opt/openspoofen"
VENV_PATH="$APP_ROOT/.venv"
SYSTEMD_WEB_UNIT="/etc/systemd/system/openspoofen-web.service"
SYSTEMD_WIFI_UNIT="/etc/systemd/system/openspoofen-wifi-uplink.service"
SYSTEMD_TV_UNIT="/etc/systemd/system/openspoofen-tv-lan.service"
SYSTEMD_NORDVPN_BOOTSTRAP_UNIT="/etc/systemd/system/openspoofen-nordvpn-bootstrap.service"
ENV_DIR="/etc/openspoofen"
ENV_FILE="$ENV_DIR/openspoofen.env"
STATE_DIR="/var/lib/openspoofen"
GETTY_OVERRIDE_DIR="/etc/systemd/system/getty@tty1.service.d"
GETTY_OVERRIDE_FILE="$GETTY_OVERRIDE_DIR/autologin.conf"

sudo apt-get update
sudo apt-get install -y \
    avahi-daemon \
    ca-certificates \
    curl \
    dnsmasq \
    jq \
    network-manager \
    nftables \
    openssh-server \
    python3 \
    python3-pip \
    python3-venv \
    rsync \
    sqlite3

sudo mkdir -p "$STATE_DIR"

if [[ -d "$APP_ROOT/var" ]]; then
    sudo find "$APP_ROOT/var" -maxdepth 1 -type f -name '*.json' -exec cp -n {} "$STATE_DIR"/ \;
fi

sudo mkdir -p "$APP_ROOT"
sudo rsync -a --delete ./ "$APP_ROOT/"
sudo mkdir -p "$ENV_DIR"
sudo chmod +x "$APP_ROOT/bootstrap/"*.sh

if [[ ! -f "$ENV_FILE" ]]; then
    sudo install -m 600 "$APP_ROOT/configs/openspoofen.env.example" "$ENV_FILE"
fi

if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
fi

configure_device_hostname() {
    local hostname_value="${RP_DEVICE_HOSTNAME:-openspoofen}"

    if [[ -z "$hostname_value" ]]; then
        return 0
    fi

    sudo hostnamectl set-hostname "$hostname_value"

    if sudo grep -qE '^127\.0\.1\.1[[:space:]]+' /etc/hosts; then
        sudo sed -i "s/^127\.0\.1\.1[[:space:]].*/127.0.1.1\t$hostname_value/" /etc/hosts
    else
        printf '127.0.1.1\t%s\n' "$hostname_value" | sudo tee -a /etc/hosts >/dev/null
    fi
}

configure_local_https() {
    local enabled="${RP_ENABLE_HTTPS:-false}"
    local cert_path="${RP_TLS_CERT_PATH:-/etc/openspoofen/tls/openspoofen.crt}"
    local key_path="${RP_TLS_KEY_PATH:-/etc/openspoofen/tls/openspoofen.key}"

    if [[ ! "${enabled,,}" =~ ^(1|true|yes|on|enable|enabled)$ ]]; then
        return 0
    fi

    if [[ -f "$cert_path" && -f "$key_path" ]]; then
        return 0
    fi

    sudo "$APP_ROOT/bootstrap/generate-local-tls-cert.sh" "$(dirname "$cert_path")" "${RP_DEVICE_HOSTNAME:-openspoofen}.local" "$cert_path" "$key_path"
    echo "Generated self-signed HTTPS certificate for https://${RP_DEVICE_HOSTNAME:-openspoofen}.local:${RP_PORT:-8080}"
}

configure_console_autologin() {
    local enabled="${RP_DEV_CONSOLE_AUTOLOGIN:-false}"
    local user="${RP_DEV_CONSOLE_AUTOLOGIN_USER:-${RP_PROVIDER_USER:-}}"

    if [[ "${enabled,,}" =~ ^(1|true|yes|on|enable|enabled)$ ]]; then
        if [[ -z "$user" ]]; then
            echo "RP_DEV_CONSOLE_AUTOLOGIN is enabled but no RP_DEV_CONSOLE_AUTOLOGIN_USER was provided; skipping tty1 autologin configuration."
            return 0
        fi

        if ! id "$user" >/dev/null 2>&1; then
            echo "RP_DEV_CONSOLE_AUTOLOGIN_USER=$user does not exist on this Pi; skipping tty1 autologin configuration."
            return 0
        fi

        sudo install -d -m 755 "$GETTY_OVERRIDE_DIR"
        sudo tee "$GETTY_OVERRIDE_FILE" >/dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --noissue --autologin $user --noclear %I \$TERM
Type=idle
EOF
        echo "Enabled tty1 console autologin for $user"
        return 0
    fi

    sudo rm -f "$GETTY_OVERRIDE_FILE"
    echo "tty1 console autologin disabled"
}

configure_device_hostname
configure_local_https

sudo python3 -m venv "$VENV_PATH"
sudo "$VENV_PATH/bin/pip" install --upgrade pip
cd "$APP_ROOT"
if ! sudo "$VENV_PATH/bin/pip" install --only-binary :all: .; then
    echo "pip install failed (see above). Systemd units will still be enabled."
    echo "Fix pip and run: sudo $VENV_PATH/bin/pip install --only-binary :all: $APP_ROOT"
fi

echo "Fixing SSH for Windows client compatibility..."
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#KbdInteractiveAuthentication yes/KbdInteractiveAuthentication yes/' /etc/ssh/sshd_config
if ! grep -q '^PasswordAuthentication' /etc/ssh/sshd_config; then
    echo 'PasswordAuthentication yes' | sudo tee -a /etc/ssh/sshd_config >/dev/null
fi
sudo systemctl restart sshd

if [[ -n "${RP_PROVIDER_HOME:-}" && -n "${RP_PROVIDER_USER:-}" ]]; then
    sudo install -d -m 700 -o "$RP_PROVIDER_USER" -g "$RP_PROVIDER_USER" "$RP_PROVIDER_HOME/.config"
    sudo install -d -m 700 -o "$RP_PROVIDER_USER" -g "$RP_PROVIDER_USER" "$RP_PROVIDER_HOME/.config/nordvpn"
fi

configure_console_autologin

sudo install -m 644 "$APP_ROOT/systemd/openspoofen-web.service" "$SYSTEMD_WEB_UNIT"
sudo install -m 644 "$APP_ROOT/systemd/openspoofen-wifi-uplink.service" "$SYSTEMD_WIFI_UNIT"
sudo install -m 644 "$APP_ROOT/systemd/openspoofen-tv-lan.service" "$SYSTEMD_TV_UNIT"
sudo install -m 644 "$APP_ROOT/systemd/openspoofen-nordvpn-bootstrap.service" "$SYSTEMD_NORDVPN_BOOTSTRAP_UNIT"
sudo install -m 644 "$APP_ROOT/configs/openspoofen-tcp.sysctl" "/etc/sysctl.d/90-openspoofen-tcp.conf"
sudo sysctl --system >/dev/null 2>&1 || true
sudo systemctl daemon-reload
sudo systemctl enable getty@tty1.service >/dev/null 2>&1 || true
sudo systemctl enable openspoofen-web.service
sudo systemctl enable openspoofen-wifi-uplink.service
sudo systemctl enable openspoofen-tv-lan.service
sudo systemctl enable openspoofen-nordvpn-bootstrap.service
sudo systemctl restart getty@tty1.service || true
sudo systemctl restart openspoofen-nordvpn-bootstrap.service || true
sudo systemctl restart openspoofen-wifi-uplink.service || true
sudo systemctl restart openspoofen-tv-lan.service || true
sudo systemctl restart openspoofen-web.service

echo "Installed repository scaffold to $APP_ROOT"
echo "Environment file available at $ENV_FILE"
echo "Web UI service enabled as openspoofen-web.service"
echo "Next: wire NetworkManager, nftables, dnsmasq, and the provider-specific system services on Raspberry Pi OS."