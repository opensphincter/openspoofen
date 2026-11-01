from pathlib import Path

import pytest

from openspoofen.config import load_config


def test_load_config_prefers_active_tv_mode_env(monkeypatch, tmp_path: Path) -> None:
    tv_env = tmp_path / "tv-ethernet-mode.env"
    tv_env.write_text(
        "RP_TV_ETHERNET_MODE=true\nRP_TV_LAN_IFACE=eth0\nRP_TV_UPLINK_IFACE=eth1\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("RP_TV_ENV_FILE", str(tv_env))
    monkeypatch.setenv("RP_UPSTREAM_INTERFACE", "eth0")
    monkeypatch.setenv("RP_DOWNSTREAM_INTERFACE", "wlan0")

    config = load_config()

    assert config.downstream_interface == "eth0"
    assert config.upstream_interface == "eth1"
    assert config.preferred_topology == "eth-wan_eth-lan"


def test_load_config_uses_explicit_env_without_tv_mode_file(monkeypatch, tmp_path: Path) -> None:
    tv_env = tmp_path / "missing-tv-ethernet-mode.env"

    monkeypatch.setenv("RP_TV_ENV_FILE", str(tv_env))
    monkeypatch.setenv("RP_UPSTREAM_INTERFACE", "usb0")
    monkeypatch.setenv("RP_DOWNSTREAM_INTERFACE", "eth9")
    monkeypatch.setenv("RP_PREFERRED_TOPOLOGY", "custom-topology")

    config = load_config()

    assert config.upstream_interface == "usb0"
    assert config.downstream_interface == "eth9"
    assert config.preferred_topology == "custom-topology"


def test_load_config_defaults_hostname_and_https_paths(monkeypatch, tmp_path: Path) -> None:
    tv_env = tmp_path / "missing-tv-ethernet-mode.env"

    monkeypatch.setenv("RP_TV_ENV_FILE", str(tv_env))
    monkeypatch.delenv("RP_DEVICE_HOSTNAME", raising=False)
    monkeypatch.setenv("RP_ENABLE_HTTPS", "true")
    monkeypatch.delenv("RP_TLS_CERT_PATH", raising=False)
    monkeypatch.delenv("RP_TLS_KEY_PATH", raising=False)

    config = load_config()

    assert config.device_hostname == "openspoofen"
    assert config.tls_cert_path == Path("/etc/openspoofen/tls/openspoofen.crt")
    assert config.tls_key_path == Path("/etc/openspoofen/tls/openspoofen.key")


def test_load_config_rejects_non_numeric_port_with_named_error(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RP_TV_ENV_FILE", str(tmp_path / "missing-tv-ethernet-mode.env"))
    monkeypatch.setenv("RP_PORT", "eighty-eighty")

    with pytest.raises(ValueError, match="RP_PORT"):
        load_config()


def test_load_config_rejects_non_numeric_timeout_with_named_error(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RP_TV_ENV_FILE", str(tmp_path / "missing-tv-ethernet-mode.env"))
    monkeypatch.setenv("RP_COMMAND_TIMEOUT_SECONDS", "whenever")

    with pytest.raises(ValueError, match="RP_COMMAND_TIMEOUT_SECONDS"):
        load_config()


def test_load_config_accepts_numeric_overrides(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("RP_TV_ENV_FILE", str(tmp_path / "missing-tv-ethernet-mode.env"))
    monkeypatch.setenv("RP_PORT", "9090")
    monkeypatch.setenv("RP_COMMAND_TIMEOUT_SECONDS", "7.5")

    config = load_config()

    assert config.port == 9090
    assert config.command_timeout_seconds == 7.5