#!/usr/bin/env bash
set -euo pipefail

if [[ "$(id -u)" != "0" ]]; then
    echo "This script must be run as root." >&2
    exit 1
fi

IS_PI=false
if grep -qi "raspberry pi" /proc/device-tree/model 2>/dev/null; then
    IS_PI=true
fi

declare -A CHANGES=()
REBOOT_NEEDED=false
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
RESET="\033[0m"

section() {
    echo
    echo -e "${CYAN}── $1${RESET}"
}

applied() {
    echo -e "  ${GREEN}✓${RESET} $1"
    CHANGES["$1"]=1
}

skipped() {
    echo -e "  ${YELLOW}•${RESET} $1"
}

# ──────────────────────────────────

section "CPU governor: performance"

for gov_path in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    if [[ -f "$gov_path" ]]; then
        current="$(cat "$gov_path")"
        if [[ "$current" != "performance" ]]; then
            echo "performance" > "$gov_path"
            applied "CPU $gov_path: $current → performance"
        else
            skipped "CPU $gov_path: already performance"
        fi
    fi
done

# ──────────────────────────────────

section "GPU memory: 16MB"

CONFIG_FILE="/boot/config.txt"
if [[ ! -f "$CONFIG_FILE" ]]; then
    CONFIG_FILE="/boot/firmware/config.txt"
fi

if [[ "$IS_PI" == "true" && -f "$CONFIG_FILE" ]]; then
    current_gpu="$(sed -n 's/^\s*gpu_mem\s*=\s*\([0-9]*\).*/\1/p' "$CONFIG_FILE" | tail -1)"
    if [[ -z "$current_gpu" ]]; then
        echo "gpu_mem=16" >> "$CONFIG_FILE"
        applied "gpu_mem: unset → 16MB"
        REBOOT_NEEDED=true
    elif [[ "$current_gpu" -gt 32 ]]; then
        sed -i 's/^\s*gpu_mem\s*=\s*[0-9]*/gpu_mem=16/' "$CONFIG_FILE"
        applied "gpu_mem: ${current_gpu}MB → 16MB"
        REBOOT_NEEDED=true
    else
        skipped "gpu_mem: ${current_gpu}MB (already ≤32, left unchanged)"
    fi
else
    skipped "gpu_mem: not a Pi or no config.txt found"
fi

# ──────────────────────────────────

section "Zram compressed swap"

if command -v zramctl >/dev/null 2>&1; then
    zram_devs="$(zramctl --noheadings 2>/dev/null | wc -l)"
    if [[ "$zram_devs" -gt 0 ]]; then
        skipped "Zram: ${zram_devs} device(s) already active"
    fi
elif dpkg -s zram-tools >/dev/null 2>&1; then
    skipped "Zram: zram-tools installed but not active"
else
    apt-get update -qq
    apt-get install -y -qq zram-tools >/dev/null 2>&1
    if [[ -f /etc/default/zramswap ]]; then
        sed -i 's/^PERCENT=.*/PERCENT=50/' /etc/default/zramswap
        sed -i 's/^ALGO=.*/ALGO=zstd/' /etc/default/zramswap
    fi
    systemctl restart zramswap >/dev/null 2>&1 || true
    applied "Zram: installed, 50% of RAM compressed with zstd"
fi

# ──────────────────────────────────

section "Unused services"

disable_and_stop() {
    local svc="$1"
    if systemctl is-enabled "$svc" >/dev/null 2>&1; then
        systemctl disable --now "$svc" >/dev/null 2>&1 || true
        applied "Disabled: $svc"
    else
        skipped "$svc: not enabled"
    fi
}

disable_and_stop bluetooth
disable_and_stop hciuart
disable_and_stop ModemManager
disable_and_stop triggerhappy

# ──────────────────────────────────

section "avahi-daemon (mDNS)"

if systemctl is-enabled avahi-daemon >/dev/null 2>&1; then
    ENV_FILE="${RP_ENV_FILE:-/etc/openspoofen/openspoofen.env}"
    hostname_set=false
    if [[ -f "$ENV_FILE" ]]; then
        if grep -q "RP_DEVICE_HOSTNAME=" "$ENV_FILE" 2>/dev/null; then
            hostname_set=true
        fi
    fi
    if [[ "$hostname_set" == "true" ]]; then
        skipped "avahi-daemon: kept (mDNS needed for openspoofen.local)"
    else
        disable_and_stop avahi-daemon
    fi
fi

# ──────────────────────────────────

section "Filesystem: noatime"

FSTAB="/etc/fstab"
applied_flag=false
while read -r line; do
    if [[ -z "$line" || "$line" == \#* ]]; then continue; fi
    dev="$(echo "$line" | awk '{print $1}')"
    mountpoint="$(echo "$line" | awk '{print $2}')"
    opts="$(echo "$line" | awk '{print $4}')"
    if [[ "$dev" == PARTUUID=* || "$dev" == UUID=* ]]; then
        if [[ "$mountpoint" == "/" || "$mountpoint" == "/boot" || "$mountpoint" == "/boot/firmware" ]]; then
            if [[ "$opts" != *noatime* ]]; then
                sed -i "\|^${dev//\//\\/}|s|${opts}|${opts},noatime,nodiratime|" "$FSTAB"
                applied "noatime: added to $mountpoint ($dev)"
                applied_flag=true
            else
                skipped "noatime: already set on $mountpoint"
            fi
        fi
    fi
done < "$FSTAB"
if [[ "$applied_flag" != "true" ]]; then
    skipped "noatime: no applicable mounts found"
fi

# ──────────────────────────────────

section "WireGuard kernel module"

if lsmod | grep -q "^wireguard"; then
    skipped "WireGuard kernel module: already loaded"
else
    if modprobe wireguard 2>/dev/null; then
        if ! grep -q "^wireguard" /etc/modules 2>/dev/null; then
            echo "wireguard" >> /etc/modules
        fi
        applied "WireGuard kernel module: loaded and added to /etc/modules"
    else
        skipped "WireGuard kernel module: unavailable (will use userspace fallback)"
    fi
fi

# ──────────────────────────────────

section "I/O scheduler: none"

for disk in mmcblk0 sda sdb; do
    sched_file="/sys/block/${disk}/queue/scheduler"
    if [[ -f "$sched_file" ]]; then
        current="$(cat "$sched_file" | grep -oP '\[.*?\]' | tr -d '[]')"
        if [[ "$current" != "none" ]]; then
            echo "none" > "$sched_file" 2>/dev/null && applied "I/O: $disk: $current → none" || skipped "I/O: $disk: write failed (permission or hw)"
        else
            skipped "I/O: $disk: already none"
        fi
    fi
done

# ──────────────────────────────────

section "Boot: quiet console"

CMDLINE="/boot/cmdline.txt"
if [[ ! -f "$CMDLINE" ]]; then
    CMDLINE="/boot/firmware/cmdline.txt"
fi
if [[ -f "$CMDLINE" ]]; then
    current="$(cat "$CMDLINE")"
    if [[ "$current" != *"quiet"* ]]; then
        echo "${current} quiet loglevel=3 udev.log_level=3" > "$CMDLINE"
        applied "boot: quiet console enabled"
        REBOOT_NEEDED=true
    else
        skipped "boot: quiet already set"
    fi
fi

# ──────────────────────────────────

echo
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}Tuning complete. Changes applied: ${#CHANGES[@]}${RESET}"
for change in "${!CHANGES[@]}"; do
    echo -e "  ${GREEN}✓${RESET} $change"
done

if [[ "$REBOOT_NEEDED" == "true" ]]; then
    echo
    echo -e "${YELLOW}⚠ Reboot required for gpu_mem and cmdline.txt changes.${RESET}"
    echo "  Run: sudo systemctl reboot"
fi
