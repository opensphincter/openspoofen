from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _optional_env(name: str) -> str | None:
    raw_value = os.getenv(name)
    if raw_value is None:
        return None

    value = raw_value.strip()
    return value or None


def _bool_from_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    return raw_value.strip().lower() in {"1", "true", "yes", "on", "enable", "enabled"}


def _int_from_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default
    try:
        return int(raw_value.strip())
    except ValueError:
        raise ValueError(f"Invalid value for {name}: {raw_value!r} (expected an integer).") from None


def _float_from_env(name: str, default: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default
    try:
        return float(raw_value.strip())
    except ValueError:
        raise ValueError(f"Invalid value for {name}: {raw_value!r} (expected a number).") from None


def _env_file_values(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _tv_mode_overrides(path: Path) -> dict[str, str]:
    values = _env_file_values(path)
    if str(values.get("RP_TV_ETHERNET_MODE", "")).strip().lower() not in {"1", "true", "yes", "on", "enable", "enabled"}:
        return {}

    downstream = values.get("RP_TV_LAN_IFACE")
    upstream = values.get("RP_TV_UPLINK_IFACE")
    preferred_topology = "wifi-wan_eth-lan" if str(upstream or "").startswith("wl") else "eth-wan_eth-lan"

    return {
        "downstream_interface": downstream or "eth0",
        "upstream_interface": upstream or "wlan0",
        "preferred_topology": preferred_topology,
    }


@dataclass(slots=True)
class AppConfig:
    device_hostname: str = "openspoofen"
    host: str = "0.0.0.0"
    port: int = 8080
    secret_key: str = "change-me"
    default_provider: str = "wireguard"
    preferred_topology: str = "wifi-wan_eth-lan"
    fail_closed: bool = True
    lan_only: bool = True
    enable_https: bool = False
    require_pairing_token: bool = False
    runtime_dir: Path = Path("var")
    auth_state_path: Path = Path("var/lan-auth.json")
    state_path: Path = Path("var/mock-state.json")
    wireguard_config_dir: Path = Path("configs/wireguard")
    surfshark_config_dir: Path = Path("configs/surfshark")
    downstream_interface: str = "eth0"
    upstream_interface: str = "wlan0"
    command_timeout_seconds: float = 15.0
    network_probe_cache_ttl_seconds: float = 2.0
    location_cache_ttl_seconds: float = 30.0
    provider_home: Path | None = None
    provider_user: str | None = None
    tls_cert_path: Path | None = None
    tls_key_path: Path | None = None
    wifi_interface: str = "wlan0"
    wifi_secret_path: Path = Path("/etc/openspoofen/secrets/wifi-uplink.local.env")
    wifi_connection_name: str = "openspoofen-uplink"
    session_persist_days: int = 30
    nordvpn_secret_path: Path = Path("/etc/openspoofen/secrets/nordvpn.local.env")
    nordvpn_bootstrap_enabled: bool = True
    nordvpn_autoconnect: bool = True
    nordvpn_lan_discovery: bool = True
    nordvpn_killswitch: bool = True
    nordvpn_allowlist_subnet: str | None = "192.168.50.0/24"
    tv_mode_env_path: Path = Path("/etc/openspoofen/tv-ethernet-mode.env")
    tv_remote_state_path: Path = Path("var/tv-remote.json")
    tv_remote_vendor: str = "samsung"
    tv_remote_name: str = "OpenSpoofen Remote"


def load_config() -> AppConfig:
    tv_mode_env_path = Path(os.getenv("RP_TV_ENV_FILE", "/etc/openspoofen/tv-ethernet-mode.env"))
    tv_mode = _tv_mode_overrides(tv_mode_env_path)
    device_hostname = _optional_env("RP_DEVICE_HOSTNAME") or "openspoofen"
    enable_https = _bool_from_env("RP_ENABLE_HTTPS", False)
    tls_cert_path = Path(value) if (value := _optional_env("RP_TLS_CERT_PATH")) else (Path("/etc/openspoofen/tls/openspoofen.crt") if enable_https else None)
    tls_key_path = Path(value) if (value := _optional_env("RP_TLS_KEY_PATH")) else (Path("/etc/openspoofen/tls/openspoofen.key") if enable_https else None)

    return AppConfig(
        device_hostname=device_hostname,
        wifi_interface=os.getenv("RP_WIFI_INTERFACE", "wlan0"),
        wifi_secret_path=Path(os.getenv("RP_WIFI_SECRET_PATH", "/etc/openspoofen/secrets/wifi-uplink.local.env")),
        wifi_connection_name=os.getenv("RP_WIFI_CONNECTION_NAME", "openspoofen-uplink"),
        session_persist_days=_int_from_env("RP_SESSION_PERSIST_DAYS", 30),
        nordvpn_secret_path=Path(os.getenv("RP_NORDVPN_SECRET_PATH", "/etc/openspoofen/secrets/nordvpn.local.env")),
        nordvpn_bootstrap_enabled=_bool_from_env("RP_NORDVPN_BOOTSTRAP_ENABLED", True),
        nordvpn_autoconnect=_bool_from_env("RP_NORDVPN_AUTOCONNECT", True),
        nordvpn_lan_discovery=_bool_from_env("RP_NORDVPN_LAN_DISCOVERY", True),
        nordvpn_killswitch=_bool_from_env("RP_NORDVPN_KILLSWITCH", True),
        nordvpn_allowlist_subnet=_optional_env("RP_NORDVPN_ALLOWLIST_SUBNET") or "192.168.50.0/24",
        tv_mode_env_path=tv_mode_env_path,
        tv_remote_state_path=Path(os.getenv("RP_TV_REMOTE_STATE_PATH", "var/tv-remote.json")),
        tv_remote_vendor=os.getenv("RP_TV_REMOTE_VENDOR", "samsung"),
        tv_remote_name=os.getenv("RP_TV_REMOTE_NAME", "OpenSpoofen Remote"),
        host=os.getenv("RP_HOST", "0.0.0.0"),
        port=_int_from_env("RP_PORT", 8080),
        secret_key=os.getenv("RP_SECRET_KEY", "change-me"),
        default_provider=os.getenv("RP_PROVIDER", "wireguard"),
        preferred_topology=tv_mode.get("preferred_topology") or os.getenv("RP_PREFERRED_TOPOLOGY", "wifi-wan_eth-lan"),
        fail_closed=_bool_from_env("RP_FAIL_CLOSED", True),
        lan_only=_bool_from_env("RP_LAN_ONLY", True),
        enable_https=enable_https,
        require_pairing_token=_bool_from_env("RP_REQUIRE_PAIRING_TOKEN", False),
        runtime_dir=Path(os.getenv("RP_RUNTIME_DIR", "var")),
        auth_state_path=Path(os.getenv("RP_AUTH_STATE_PATH", "var/lan-auth.json")),
        state_path=Path(os.getenv("RP_STATE_PATH", "var/mock-state.json")),
        wireguard_config_dir=Path(os.getenv("RP_WIREGUARD_CONFIG_DIR", "configs/wireguard")),
        surfshark_config_dir=Path(os.getenv("RP_SURFSHARK_CONFIG_DIR", "configs/surfshark")),
        downstream_interface=tv_mode.get("downstream_interface") or os.getenv("RP_DOWNSTREAM_INTERFACE", "eth0"),
        upstream_interface=tv_mode.get("upstream_interface") or os.getenv("RP_UPSTREAM_INTERFACE", "wlan0"),
        command_timeout_seconds=_float_from_env("RP_COMMAND_TIMEOUT_SECONDS", 15.0),
        network_probe_cache_ttl_seconds=_float_from_env("RP_NETWORK_PROBE_CACHE_TTL_SECONDS", 2.0),
        location_cache_ttl_seconds=_float_from_env("RP_LOCATION_CACHE_TTL_SECONDS", 30.0),
        provider_home=Path(value) if (value := _optional_env("RP_PROVIDER_HOME")) else None,
        provider_user=_optional_env("RP_PROVIDER_USER"),
        tls_cert_path=tls_cert_path,
        tls_key_path=tls_key_path,
    )