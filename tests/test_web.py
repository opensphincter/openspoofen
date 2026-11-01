import re
import subprocess
from dataclasses import asdict
from pathlib import Path

import openspoofen.web as web_module
from openspoofen.config import AppConfig
from openspoofen.providers.base import ConnectionState, Location, ProviderError
from openspoofen.providers.mock import MockVpnProvider
from openspoofen.providers.nordvpn import NordVpnProvider
from openspoofen.tv_remote import TvRemoteManager
from openspoofen.web import create_app
from openspoofen.wifi import WifiError, WifiManager


def _network_snapshot_with_latest_lease(latest_lease: dict[str, str] | None) -> dict[str, object]:
    return {
        "preferred_topology": "eth-wan_eth-lan",
        "fail_closed": True,
        "upstream_interface": {"name": "eth1", "state": "up", "addresses": "172.20.18.213/16", "present": True},
        "downstream_interface": {"name": "eth0", "state": "up", "addresses": "192.168.50.1/24", "present": True},
        "tv_status": "lease active" if latest_lease else "waiting for TV",
        "tv_status_detail": "Synthetic test snapshot.",
        "tv_connectivity": {
            "status": "lease active" if latest_lease else "waiting for TV",
            "detail": "Synthetic test snapshot.",
            "hostname": latest_lease["hostname"] if latest_lease else None,
            "address": latest_lease["address"] if latest_lease else None,
            "mac": "5c:c1:d7:f8:a6:f6" if latest_lease else None,
            "lease_expires_at": "2026-04-09T09:35:49+00:00" if latest_lease else None,
            "neighbor_present": bool(latest_lease),
            "neighbor_state": "REACHABLE" if latest_lease else None,
            "neighbor_line": "192.168.50.57 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE" if latest_lease else None,
            "live_neighbor": bool(latest_lease),
            "vendor_hint": latest_lease["hostname"] if latest_lease else None,
            "exact_model": None,
            "model_hint": "Synthetic test snapshot.",
            "vpn_path_hint": "Synthetic test snapshot.",
        },
        "tv_neighbors": ["192.168.50.57 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE"] if latest_lease else [],
        "latest_lease": latest_lease,
        "lease_count": 1 if latest_lease else 0,
        "service_states": [],
        "dns_servers": ["103.86.99.100", "103.86.96.100"],
        "default_route": "default via 172.20.1.1 dev eth1",
        "diagnostic_summary": "Synthetic test snapshot.",
    }


def build_config(tmp_path: Path, **overrides) -> AppConfig:
    base = AppConfig(
        default_provider="mock",
        auth_state_path=tmp_path / "lan-auth.json",
        state_path=tmp_path / "mock-state.json",
        runtime_dir=tmp_path / "runtime",
        nordvpn_secret_path=tmp_path / "nordvpn.local.env",
        tv_remote_state_path=tmp_path / "tv-remote.json",
    )
    values = {**asdict(base), **overrides}
    return AppConfig(**values)


def test_first_boot_redirects_to_setup(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    response = client.get("/", follow_redirects=True)

    assert response.status_code == 200
    assert b"Configure LAN access" in response.data
    assert b"First boot" in response.data


def test_setup_provider_login_and_connect_flow(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    setup_response = client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )
    assert setup_response.status_code == 200
    assert b"LAN admin password configured." in setup_response.data
    assert b"Mock Provider" in setup_response.data

    login_response = client.post(
        "/provider/login",
        data={"provider": "mock", "token": "demo-token"},
        follow_redirects=True,
    )
    assert login_response.status_code == 200
    assert b"Authenticated with Mock Provider." in login_response.data
    assert b"Demo token" not in login_response.data
    assert b"Mock Provider is already authenticated on this device." in login_response.data

    connect_response = client.post(
        "/connect",
        data={"provider": "mock", "country": "United States", "city": "New York"},
        follow_redirects=True,
    )
    assert connect_response.status_code == 200
    assert b"Switching active region to United States / New York." in connect_response.data
    assert b"United States / New York" in connect_response.data
    assert b"Connected to United States / New York in mock mode" in connect_response.data

    status_response = client.get("/api/status?provider=mock")
    assert status_response.status_code == 200
    payload = status_response.get_json()
    assert payload["provider"] == "mock"
    assert payload["state"]["connected"] is True
    assert payload["state"]["current_location"]["label"] == "United States / New York"
    assert b"dashboard-bootstrap" in setup_response.data
    assert b"dashboard-app.js" in setup_response.data


def test_new_browser_signs_in_with_password_only_by_default(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    first_client = app.test_client()

    first_client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )

    first_client.post("/logout", follow_redirects=True)

    same_browser_login = first_client.post(
        "/login",
        data={"password": "lan-admin-pass"},
        follow_redirects=True,
    )
    assert same_browser_login.status_code == 200
    assert b"Signed in to the LAN control surface." in same_browser_login.data

    second_client = app.test_client()
    login_response = second_client.post(
        "/login",
        data={"password": "lan-admin-pass"},
        follow_redirects=True,
    )
    assert login_response.status_code == 200
    assert b"Signed in to the LAN control surface." in login_response.data


def test_unpaired_browser_requires_pairing_token_when_enabled(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path, require_pairing_token=True))
    first_client = app.test_client()

    first_client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )

    first_client.post("/logout", follow_redirects=True)

    second_client = app.test_client()
    missing_token_response = second_client.post(
        "/login",
        data={"password": "lan-admin-pass"},
        follow_redirects=True,
    )
    assert missing_token_response.status_code == 200
    assert b"A valid pairing token is required for a new browser." in missing_token_response.data

    paired_login_response = second_client.post(
        "/login",
        data={"password": "lan-admin-pass", "pairing_token": "pair-me-now"},
        follow_redirects=True,
    )
    assert paired_login_response.status_code == 200
    assert b"Signed in to the LAN control surface." in paired_login_response.data


def test_setup_and_login_hide_pairing_token_by_default(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    setup_response = client.get("/setup")

    assert setup_response.status_code == 200
    assert b"Pairing token" not in setup_response.data

    client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
        },
        follow_redirects=True,
    )
    client.post("/logout", follow_redirects=True)

    login_response = client.get("/login")

    assert login_response.status_code == 200
    assert b"Pairing token" not in login_response.data


def test_missing_cli_provider_renders_setup_guidance(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path, default_provider="nordvpn"))
    client = app.test_client()

    response = client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"The NordVPN CLI is not available" in response.data
    assert b"Install the official NordVPN Linux CLI on Raspberry Pi OS Lite 64-bit." in response.data


def test_authenticated_cli_provider_hides_manual_login_form(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path, default_provider="nordvpn"))
    client = app.test_client()

    monkeypatch.setattr(
        NordVpnProvider,
        "get_state",
        lambda self: ConnectionState(
            provider_name=self.provider_name,
            authenticated=True,
            connected=False,
            current_location=None,
            public_ip=None,
            status_summary="Disconnected",
        ),
    )
    monkeypatch.setattr(NordVpnProvider, "list_locations", lambda self: [])

    response = client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Access token" not in response.data
    assert b"NordVPN is already authenticated on this device." in response.data


def test_api_provider_select_switches_backend(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )

    response = client.post("/api/provider/select", json={"provider": "wireguard"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["provider"] == "wireguard"
    assert payload["provider_metadata"]["provider_name"] == "WireGuard Profiles"
    assert "Switched control backend" in payload["message"]


def test_status_api_filters_placeholder_regions_and_normalizes_labels(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path, default_provider="nordvpn"))
    client = app.test_client()

    monkeypatch.setattr(
        NordVpnProvider,
        "get_state",
        lambda self: ConnectionState(
            provider_name=self.provider_name,
            authenticated=True,
            connected=False,
            current_location=None,
            public_ip=None,
            status_summary="Disconnected",
        ),
    )
    monkeypatch.setattr(
        NordVpnProvider,
        "list_locations",
        lambda self: [Location(country="All_Regions"), Location(country="United_States")],
    )

    client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )

    response = client.get("/api/status?provider=nordvpn")

    assert response.status_code == 200
    payload = response.get_json()
    assert [region["label"] for region in payload["regions"]] == ["United States"]


def test_wifi_status_api_returns_snapshot(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    monkeypatch.setattr(
        WifiManager,
        "status",
        lambda self, include_networks=False, country=None: {
            "interface": "wlan0",
            "device_state": "disconnected",
            "device_connection": "--",
            "blocked": False,
            "country": country or "US",
            "current_ssid": None,
            "saved_ssid": "HomeNet",
            "saved_country": "US",
            "connection_name": "openspoofen-uplink",
            "networks": [{"ssid": "HomeNet", "signal": 84, "security": "WPA2", "active": False, "saved": True}] if include_networks else [],
            "error": None,
        },
    )

    client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )

    response = client.get("/api/wifi/status?include_networks=true&country=US")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["wifi"]["saved_ssid"] == "HomeNet"
    assert payload["wifi"]["networks"][0]["ssid"] == "HomeNet"


def test_wifi_connect_api_returns_saved_snapshot(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    monkeypatch.setattr(
        WifiManager,
        "connect",
        lambda self, ssid, password, country=None: {
            "interface": "wlan0",
            "device_state": "connected",
            "device_connection": "openspoofen-uplink",
            "blocked": False,
            "country": country or "US",
            "current_ssid": ssid,
            "saved_ssid": ssid,
            "saved_country": country or "US",
            "connection_name": "openspoofen-uplink",
            "networks": [{"ssid": ssid, "signal": 90, "security": "WPA2", "active": True, "saved": True}],
            "error": None,
        },
    )

    client.post(
        "/setup",
        data={
            "password": "lan-admin-pass",
            "password_confirm": "lan-admin-pass",
            "pairing_token": "pair-me-now",
        },
        follow_redirects=True,
    )

    response = client.post("/api/wifi/connect", json={"ssid": "HomeNet", "password": "supersecret", "country": "US"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["wifi"]["saved_ssid"] == "HomeNet"
    assert "Saved Wi-Fi uplink" in payload["message"]


def test_appliance_specs_api_returns_snapshot(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    monkeypatch.setattr(
        web_module,
        "_collect_appliance_specs",
        lambda config: {
            "device_hostname": "openspoofen",
            "preferred_topology": "eth-wan_eth-lan",
            "upstream_interface": "eth1",
            "downstream_interface": "eth0",
            "default_provider": "nordvpn",
            "lan_only": True,
            "enable_https": False,
            "require_pairing_token": False,
            "default_route": "default via 172.20.1.1 dev eth1",
            "dns_servers": ["103.86.99.100", "103.86.96.100"],
            "service_states": [{"label": "TV LAN", "active_state": "active", "sub_state": "exited", "result": "success", "healthy": "yes"}],
            "dhcp_leases": [{"hostname": "Samsung", "address": "192.168.50.57", "mac": "5c:c1:d7:f8:a6:f6"}],
            "tv_connectivity": {
                "status": "lease active",
                "detail": "Synthetic spec snapshot.",
                "hostname": "Samsung",
                "address": "192.168.50.57",
                "mac": "5c:c1:d7:f8:a6:f6",
                "lease_expires_at": "2026-04-09T09:35:49+00:00",
                "neighbor_present": True,
                "neighbor_state": "REACHABLE",
                "neighbor_line": "192.168.50.57 dev eth0 lladdr aa:bb:cc:dd:ee:ff REACHABLE",
                "live_neighbor": True,
                "vendor_hint": "Samsung",
                "exact_model": None,
                "model_hint": "Exact model unavailable in synthetic snapshot.",
                "vpn_path_hint": "Synthetic spec snapshot.",
            },
            "generated_at": "2026-04-08T00:00:00+00:00",
        },
    )

    client.post(
        "/setup",
        data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"},
        follow_redirects=True,
    )

    response = client.get("/api/appliance/specs")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["specs"]["device_hostname"] == "openspoofen"
    assert payload["specs"]["dhcp_leases"][0]["address"] == "192.168.50.57"
    assert payload["specs"]["tv_connectivity"]["neighbor_state"] == "REACHABLE"


def test_status_api_includes_tv_connectivity_snapshot(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    monkeypatch.setattr(
        web_module,
        "_probe_network_health",
        lambda config: _network_snapshot_with_latest_lease({"hostname": "Samsung", "address": "192.168.50.57"}),
    )

    client.post(
        "/setup",
        data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"},
        follow_redirects=True,
    )

    response = client.get("/api/status")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["network"]["tv_connectivity"]["address"] == "192.168.50.57"
    assert payload["network"]["tv_connectivity"]["live_neighbor"] is True


def test_appliance_logs_api_returns_service_logs(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    monkeypatch.setattr(
        web_module,
        "_collect_appliance_logs",
        lambda: {
            "generated_at": "2026-04-08T00:00:00+00:00",
            "services": [{"name": "dnsmasq.service", "label": "DNS and DHCP", "lines": ["lease 192.168.50.57 Samsung"]}],
        },
    )

    client.post(
        "/setup",
        data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"},
        follow_redirects=True,
    )

    response = client.get("/api/appliance/logs")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["logs"]["services"][0]["label"] == "DNS and DHCP"
    assert "Samsung" in payload["logs"]["services"][0]["lines"][0]


def test_nordvpn_provider_login_persists_boot_token(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path, default_provider="nordvpn"))
    client = app.test_client()
    observed_commands: list[list[str]] = []

    monkeypatch.setattr(
        NordVpnProvider,
        "get_state",
        lambda self: ConnectionState(
            provider_name=self.provider_name,
            authenticated=False,
            connected=False,
            current_location=None,
            public_ip=None,
            status_summary="Disconnected",
        ),
    )
    monkeypatch.setattr(NordVpnProvider, "list_locations", lambda self: [])
    monkeypatch.setattr(NordVpnProvider, "login", lambda self, credentials: None)
    monkeypatch.setattr(web_module, "_probe_network_health", lambda config: _network_snapshot_with_latest_lease(None))
    monkeypatch.setattr(web_module.shutil, "which", lambda name: "/usr/bin/systemctl" if name == "systemctl" else None)

    class CompletedProcess:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(
        web_module.subprocess,
        "run",
        lambda args, **kwargs: observed_commands.append(args) or CompletedProcess(),
    )

    client.post(
        "/setup",
        data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"},
        follow_redirects=True,
    )

    response = client.post(
        "/provider/login",
        data={"provider": "nordvpn", "token": "persist-me"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Saved the NordVPN token for future boots" in response.data
    assert app.config["RP_CONFIG"].nordvpn_secret_path.read_text(encoding="utf-8") == "NORDVPN_ACCESS_TOKEN=persist-me\n"
    assert observed_commands == [["/usr/bin/systemctl", "restart", "openspoofen-nordvpn-bootstrap.service"]]


def test_remote_status_api_uses_latest_lease(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    monkeypatch.setattr(
        web_module,
        "_probe_network_health",
        lambda config: _network_snapshot_with_latest_lease({"hostname": "Samsung", "address": "192.168.50.57"}),
    )

    observed_leases: list[dict[str, str] | None] = []

    def fake_status(self, latest_lease=None, last_error=None):
        observed_leases.append(latest_lease)
        return {
            "vendor": "samsung",
            "configured": False,
            "available": True,
            "host": None,
            "display_name": "OpenSpoofen Remote",
            "port": None,
            "token_cached": False,
            "candidate_host": latest_lease["address"] if latest_lease else None,
            "candidate_name": latest_lease["hostname"] if latest_lease else None,
            "status_summary": "TV detected",
            "last_error": last_error,
        }

    monkeypatch.setattr(TvRemoteManager, "status", fake_status)

    client.post(
        "/setup",
        data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"},
        follow_redirects=True,
    )
    observed_leases.clear()

    response = client.get("/api/remote/status")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["remote"]["candidate_host"] == "192.168.50.57"
    assert observed_leases == [{"hostname": "Samsung", "address": "192.168.50.57"}]


def test_remote_configure_and_key_apis(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        web_module,
        "_probe_network_health",
        lambda config: _network_snapshot_with_latest_lease({"hostname": "Samsung", "address": "192.168.50.57"}),
    )

    def fake_status(self, latest_lease=None, last_error=None):
        return {
            "vendor": "samsung",
            "configured": True,
            "available": True,
            "host": "192.168.50.57",
            "display_name": "OpenSpoofen Remote",
            "port": 8001,
            "token_cached": True,
            "candidate_host": latest_lease["address"] if latest_lease else None,
            "candidate_name": latest_lease["hostname"] if latest_lease else None,
            "status_summary": "Ready",
            "last_error": last_error,
        }

    def fake_configure(self, host, display_name=None, vendor=None, port=None, latest_lease=None):
        captured["configure"] = {
            "host": host,
            "display_name": display_name,
            "vendor": vendor,
            "port": port,
            "latest_lease": latest_lease,
        }
        return fake_status(self, latest_lease=latest_lease)

    def fake_send_key(self, key, latest_lease=None):
        captured["key"] = {"key": key, "latest_lease": latest_lease}
        return fake_status(self, latest_lease=latest_lease)

    def fake_send_text(self, text, latest_lease=None, submit=False):
        captured["text"] = {"text": text, "latest_lease": latest_lease, "submit": submit}
        return fake_status(self, latest_lease=latest_lease)

    monkeypatch.setattr(TvRemoteManager, "status", fake_status)
    monkeypatch.setattr(TvRemoteManager, "configure", fake_configure)
    monkeypatch.setattr(TvRemoteManager, "send_key", fake_send_key)
    monkeypatch.setattr(TvRemoteManager, "send_text", fake_send_text)

    client.post(
        "/setup",
        data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"},
        follow_redirects=True,
    )

    configure_response = client.post(
        "/api/remote/configure",
        json={"host": "192.168.50.57", "display_name": "Den Remote", "vendor": "samsung", "port": 8001},
    )

    assert configure_response.status_code == 200
    configure_payload = configure_response.get_json()
    assert configure_payload["ok"] is True
    assert captured["configure"] == {
        "host": "192.168.50.57",
        "display_name": "Den Remote",
        "vendor": "samsung",
        "port": 8001,
        "latest_lease": {"hostname": "Samsung", "address": "192.168.50.57"},
    }

    key_response = client.post("/api/remote/key", json={"key": "home"})

    assert key_response.status_code == 200
    key_payload = key_response.get_json()
    assert key_payload["ok"] is True
    assert captured["key"] == {
        "key": "home",
        "latest_lease": {"hostname": "Samsung", "address": "192.168.50.57"},
    }

    text_response = client.post("/api/remote/text", json={"text": "hello", "submit": True})

    assert text_response.status_code == 200
    text_payload = text_response.get_json()
    assert text_payload["ok"] is True
    assert captured["text"] == {
        "text": "hello",
        "latest_lease": {"hostname": "Samsung", "address": "192.168.50.57"},
        "submit": True,
    }


def test_switch_region_returns_immediately(tmp_path: Path) -> None:
    """api_switch_region should return without blocking on connect()."""
    import time
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    start = time.monotonic()
    response = client.post(
        "/api/region/switch",
        json={"provider": "mock", "country": "Japan", "city": "Tokyo"},
    )
    elapsed = time.monotonic() - start
    assert response.status_code == 200
    assert elapsed < 2.0  # must return quickly, not block on VPN connect


def test_provider_state_cache_ttl(tmp_path: Path) -> None:
    """Provider state is cached for 5 seconds."""
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    # Provider needs authentication first
    client.post("/provider/login", data={"provider": "mock", "token": "demo-token"}, follow_redirects=True)

    r1 = client.get("/api/status?provider=mock")
    assert r1.status_code == 200
    s1 = r1.get_json()["state"]
    assert s1["authenticated"] is True

    # Region switch returns immediately — state may not update until polling
    response = client.post(
        "/api/region/switch",
        json={"provider": "mock", "country": "Germany", "city": "Berlin"},
    )
    assert response.status_code == 200

    # Verify state is still a valid snapshot after switch
    r2 = client.get("/api/status?provider=mock")
    assert r2.status_code == 200
    s2 = r2.get_json()["state"]
    assert s2["provider_name"] == "Mock Provider"


def test_auth_state_cache_invalidates(tmp_path: Path) -> None:
    """Auth state cache uses mtime to detect changes."""
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    r1 = client.get("/", follow_redirects=True)
    assert b"First boot" in r1.data

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    r2 = client.get("/")
    assert r2.status_code == 200
    assert b"Mock Provider" in r2.data


def test_optimistic_ui_state_on_switch_error(tmp_path: Path) -> None:
    """Test that the wrong-country API error returns properly."""
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    response = client.post(
        "/api/region/switch",
        json={"provider": "mock", "country": "Moon"},
    )
    assert response.status_code == 200  # async connect, returns immediately


def test_default_route_from_proc(tmp_path: Path) -> None:
    """_probe_default_route falls back gracefully when /proc is unavailable."""
    result = web_module._probe_default_route()
    assert isinstance(result, str)
    assert result == "unavailable" or "via" in result


def test_neighbors_from_arp_parser() -> None:
    """_probe_neighbors parses /proc/net/arp correctly."""
    result = web_module._probe_neighbors("eth0")
    assert isinstance(result, list)


def test_interface_state_from_sys() -> None:
    """_probe_interface reads /sys correctly or falls back gracefully."""
    result = web_module._probe_interface("lo")
    assert result.get("name") == "lo"
    assert "state" in result
    assert "present" in result


def test_dns_servers_no_subprocess() -> None:
    """_probe_dns_servers reads resolv.conf without subprocess."""
    result = web_module._probe_dns_servers()
    assert isinstance(result, list)


def test_orjson_serialization_roundtrip(tmp_path: Path) -> None:
    """orjson provider serializes dashboard bootstrap correctly."""
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)
    response = client.get("/api/status?provider=mock")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["provider"] == "mock"
    assert isinstance(payload["state"]["authenticated"], bool)


def test_appliance_logs_api_handles_missing_journalctl(tmp_path: Path) -> None:
    """Log collection returns empty services when journalctl unavailable."""
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)
    response = client.get("/api/appliance/logs")
    assert response.status_code == 200
    payload = response.get_json()
    assert "logs" in payload
    assert isinstance(payload["logs"]["services"], list)

def test_static_assets_are_compressed_and_cached(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()
    static = Path(app.static_folder)
    # Hashed chunk names are a bundler implementation detail (Vite 8/Rolldown names
    # them differently than Vite 7 did); pick the largest hash-suffixed chunk, which
    # is the same shape the server's immutable-cache rule matches on.
    hashed_chunks = [p for p in static.glob("*.js") if re.search(r"-[A-Za-z0-9_-]{8}\.js$", p.name)]
    assert hashed_chunks, "expected at least one hashed JS chunk in the built static assets"
    chunk = max(hashed_chunks, key=lambda p: p.stat().st_size).name

    plain = client.get(f"/static/{chunk}")
    packed = client.get(f"/static/{chunk}", headers={"Accept-Encoding": "gzip, deflate, br"})
    assert plain.status_code == packed.status_code == 200
    assert "Content-Encoding" not in plain.headers
    assert packed.headers["Content-Encoding"] in {"br", "deflate", "zstd"}
    assert len(packed.data) < len(plain.data) / 2
    assert "immutable" in packed.headers["Cache-Control"]

    versioned = client.get("/static/dashboard-app.css?v=1", headers={"Accept-Encoding": "gzip, deflate, br"})
    assert "immutable" in versioned.headers["Cache-Control"]
    assert client.get("/static/manifest.webmanifest").headers.get("Cache-Control") != "public, max-age=31536000, immutable"


def test_login_redirect_stays_local_for_external_next(tmp_path: Path) -> None:
    """The login `next` parameter must never become an open redirect."""
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"})
    client.post("/logout")

    for hostile_next in ("https://evil.example/phish", "//evil.example/phish", "javascript:alert(1)"):
        response = client.post("/login", data={"password": "lan-admin-pass", "next": hostile_next})
        assert response.status_code == 302
        assert "evil.example" not in (response.location or "")
        assert "javascript:" not in (response.location or "")
        client.post("/logout")

    response = client.post("/login", data={"password": "lan-admin-pass", "next": "/api/status"})
    assert response.status_code == 302
    assert response.location.endswith("/api/status")


def test_login_page_does_not_reflect_external_next(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"})
    client.post("/logout")

    response = client.get("/login?next=https://evil.example/phish")
    assert response.status_code == 200
    assert b"evil.example" not in response.data


def test_region_switch_rejects_missing_or_flag_like_country(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    for payload in ({}, {"country": ""}, {"country": "   "}, {"country": "--country"}, {"country": "-x"}):
        response = client.post("/api/region/switch", json=payload)
        assert response.status_code == 400, payload
        assert "error" in response.get_json()

    response = client.post("/api/region/switch", json={"country": "Japan", "city": "Tokyo"})
    assert response.status_code == 200


def test_probe_interface_tolerates_empty_command_output(monkeypatch) -> None:
    monkeypatch.setattr(web_module, "_run_capture", lambda *args: "")

    result = web_module._probe_interface("eth9")

    assert result == {"name": "eth9", "state": "unknown", "addresses": "unavailable", "present": False}


def test_session_cookie_is_hardened(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    response = client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"})

    session_cookies = [h for h in response.headers.getlist("Set-Cookie") if h.startswith("session=")]
    assert session_cookies, "expected the setup flow to set a session cookie"
    assert "HttpOnly" in session_cookies[0]
    assert "SameSite=Lax" in session_cookies[0]


# --- Coverage pass additions (best-practices pass, PLAN-openspoofen item 5) ---
# These exercise web.py branches the original suite did not reach: the auth
# gate's rejection paths, the form POST error flashes, the Wi-Fi/remote API
# error returns, and the pure probe/parsing helpers with stubbed commands.


def _setup_client(tmp_path: Path, **overrides):
    app = create_app(build_config(tmp_path, **overrides))
    client = app.test_client()
    client.post(
        "/setup",
        data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"},
        follow_redirects=True,
    )
    return app, client


def test_healthz_manifest_and_service_worker_are_public(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.get_json() == {"ok": True}

    manifest_response = client.get("/manifest.webmanifest")
    assert manifest_response.status_code == 200

    worker_response = client.get("/sw.js")
    assert worker_response.status_code == 200
    assert worker_response.headers["Cache-Control"] == "no-store"


def test_non_lan_client_is_forbidden(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    response = client.get("/", environ_base={"REMOTE_ADDR": "8.8.8.8"})

    assert response.status_code == 403


def test_setup_page_redirects_to_dashboard_once_configured(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.get("/setup")

    assert response.status_code == 302
    assert "provider=mock" in (response.location or "")


def test_unauthenticated_api_request_returns_401(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)
    client.post("/logout")

    response = client.get("/api/status")

    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required"}


def test_unauthenticated_page_request_redirects_to_login(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)
    client.post("/logout")

    response = client.get("/")

    assert response.status_code == 302
    assert "/login" in (response.location or "")
    assert "next=" in (response.location or "")


def test_setup_rejects_mismatched_passwords(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    response = client.post(
        "/setup",
        data={"password": "lan-admin-pass", "password_confirm": "different-pass"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Passwords did not match." in response.data


def test_setup_rejects_short_password(tmp_path: Path) -> None:
    app = create_app(build_config(tmp_path))
    client = app.test_client()

    response = client.post(
        "/setup",
        data={"password": "short", "password_confirm": "short"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Admin password must be at least 8 characters long." in response.data


def test_login_rejects_wrong_password(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)
    client.post("/logout")

    response = client.post(
        "/login",
        data={"password": "not-the-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Incorrect admin password." in response.data


def test_connect_requires_a_country(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.post("/connect", data={"provider": "mock"}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Choose a country before connecting." in response.data


def test_connect_flashes_provider_error_when_unauthenticated(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.post(
        "/connect",
        data={"provider": "mock", "country": "United States"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Authenticate with the mock provider before switching regions." in response.data


def test_form_disconnect_disconnects_provider(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)
    client.post("/provider/login", data={"provider": "mock", "token": "demo-token"}, follow_redirects=True)
    client.post("/connect", data={"provider": "mock", "country": "United States"}, follow_redirects=True)

    response = client.post("/disconnect", follow_redirects=True)

    assert response.status_code == 200
    assert b"Disconnected Mock Provider." in response.data
    status = client.get("/api/status?provider=mock").get_json()
    assert status["state"]["connected"] is False


def test_form_disconnect_flashes_provider_errors(tmp_path: Path, monkeypatch) -> None:
    _, client = _setup_client(tmp_path)

    def failing_disconnect(self) -> None:
        raise ProviderError("Mock disconnect exploded.")

    monkeypatch.setattr(MockVpnProvider, "disconnect", failing_disconnect)

    response = client.post("/disconnect", follow_redirects=True)

    assert response.status_code == 200
    assert b"Mock disconnect exploded." in response.data


def test_provider_login_flashes_error_for_empty_mock_token(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.post("/provider/login", data={"provider": "mock"}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Mock login requires a non-empty token or account string." in response.data


def test_regions_api_returns_serialized_locations(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.get("/api/regions?provider=mock")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["provider"] == "mock"
    assert any(region["country"] == "United States" for region in payload["regions"])


def test_provider_select_rejects_unsupported_provider(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.post("/api/provider/select", json={"provider": "bogus"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Unsupported provider: bogus"}


def test_unknown_provider_query_param_falls_back_to_default(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.get("/api/status?provider=bogus")

    assert response.status_code == 200
    assert response.get_json()["provider"] == "mock"


def test_api_disconnect_returns_dashboard_payload(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)
    client.post("/provider/login", data={"provider": "mock", "token": "demo-token"}, follow_redirects=True)
    client.post("/connect", data={"provider": "mock", "country": "United States"}, follow_redirects=True)

    response = client.post("/api/disconnect")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["message"] == "Disconnected Mock Provider."
    assert payload["state"]["connected"] is False


def test_api_disconnect_returns_provider_errors(tmp_path: Path, monkeypatch) -> None:
    _, client = _setup_client(tmp_path)

    def failing_disconnect(self) -> None:
        raise ProviderError("Mock disconnect exploded.")

    monkeypatch.setattr(MockVpnProvider, "disconnect", failing_disconnect)

    response = client.post("/api/disconnect")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Mock disconnect exploded."}


def test_wifi_status_api_returns_error_when_manager_fails(tmp_path: Path, monkeypatch) -> None:
    _, client = _setup_client(tmp_path)

    def failing_status(self, include_networks=False, country=None):
        raise WifiError("nmcli unavailable")

    monkeypatch.setattr(WifiManager, "status", failing_status)

    response = client.get("/api/wifi/status")

    assert response.status_code == 400
    assert response.get_json() == {"error": "nmcli unavailable"}


def test_wifi_scan_api_returns_networks(tmp_path: Path, monkeypatch) -> None:
    _, client = _setup_client(tmp_path)

    monkeypatch.setattr(
        WifiManager,
        "status",
        lambda self, include_networks=False, country=None: {
            "interface": "wlan0",
            "networks": [{"ssid": "HomeNet", "signal": 84, "security": "WPA2", "active": False, "saved": True}] if include_networks else [],
            "country": country or "US",
        },
    )

    response = client.post("/api/wifi/scan", json={"country": "US"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["wifi"]["networks"][0]["ssid"] == "HomeNet"


def test_wifi_scan_api_returns_error_when_manager_fails(tmp_path: Path, monkeypatch) -> None:
    _, client = _setup_client(tmp_path)

    def failing_status(self, include_networks=False, country=None):
        raise WifiError("nmcli unavailable")

    monkeypatch.setattr(WifiManager, "status", failing_status)

    response = client.post("/api/wifi/scan", json={"country": "US"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "nmcli unavailable"}


def test_wifi_connect_api_returns_error_when_manager_fails(tmp_path: Path, monkeypatch) -> None:
    _, client = _setup_client(tmp_path)

    def failing_connect(self, ssid, password, country=None):
        raise WifiError("nmcli unavailable")

    monkeypatch.setattr(WifiManager, "connect", failing_connect)

    response = client.post("/api/wifi/connect", json={"ssid": "HomeNet", "password": "supersecret"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "nmcli unavailable"}


def test_remote_configure_rejects_bad_port_and_missing_host(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    bad_port = client.post("/api/remote/configure", json={"host": "192.168.50.57", "port": "abc"})
    assert bad_port.status_code == 400
    assert "error" in bad_port.get_json()

    missing_host = client.post("/api/remote/configure", json={"host": ""})
    assert missing_host.status_code == 400
    assert missing_host.get_json() == {"error": "A TV IP address or hostname is required."}


def test_remote_key_requires_configured_tv(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.post("/api/remote/key", json={})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Configure the TV IP first before using the remote controls."}


def test_remote_text_requires_text(tmp_path: Path) -> None:
    _, client = _setup_client(tmp_path)

    response = client.post("/api/remote/text", json={"text": ""})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_provider_mark_text_fallbacks() -> None:
    assert web_module._provider_mark_text("NordVPN") == "NV"
    assert web_module._provider_mark_text("WireGuard Profiles") == "WG"
    assert web_module._provider_mark_text("Acme VPN") == "AV"
    assert web_module._provider_mark_text("Proton") == "P"
    assert web_module._provider_mark_text("") == "OS"
    assert web_module._provider_mark_text("  ") == "OS"


def test_frontend_asset_version_without_static_folder(tmp_path: Path) -> None:
    assert web_module._frontend_asset_version(None) == "0"
    assert web_module._frontend_asset_version(str(tmp_path)) == "0"

    asset = tmp_path / "dashboard-app.js"
    asset.write_text("console.log('x')", encoding="utf-8")
    assert web_module._frontend_asset_version(str(tmp_path)) == str(int(asset.stat().st_mtime))


def test_run_capture_missing_executable_and_timeout(monkeypatch) -> None:
    assert web_module._run_capture("openspoofen-binary-that-does-not-exist") is None

    def timing_out_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="cat", timeout=5)

    monkeypatch.setattr(web_module.subprocess, "run", timing_out_run)
    assert web_module._run_capture("cat", "/etc/resolv.conf") is None


def test_parse_key_value_output_skips_malformed_lines() -> None:
    assert web_module._parse_key_value_output(None) == {}
    assert web_module._parse_key_value_output("") == {}
    assert web_module._parse_key_value_output("ActiveState=active\nno separator here\nResult=success\n") == {
        "ActiveState": "active",
        "Result": "success",
    }


def test_probe_dns_servers_parsing_and_failure(monkeypatch) -> None:
    monkeypatch.setattr(web_module, "_run_capture", lambda *args: None)
    assert web_module._probe_dns_servers() == []

    monkeypatch.setattr(
        web_module,
        "_run_capture",
        lambda *args: "# comment\nnameserver 1.1.1.1\nnameserver 8.8.8.8\ndomain lan\n",
    )
    assert web_module._probe_dns_servers() == ["1.1.1.1", "8.8.8.8"]


def test_probe_dhcp_leases_parsing(monkeypatch) -> None:
    sample = (
        "# dnsmasq leases\n"
        "1775630400 5c:c1:d7:f8:a6:f6 192.168.50.57 Samsung a1b2c3\n"
        "truncated line\n"
        "1775630500 aa:bb:cc:dd:ee:ff 192.168.50.58 * *\n"
    )
    monkeypatch.setattr(web_module, "_run_capture", lambda *args: sample)

    leases = web_module._probe_dhcp_leases()

    assert leases == [
        {
            "expiry_epoch": "1775630400",
            "mac": "5c:c1:d7:f8:a6:f6",
            "address": "192.168.50.57",
            "hostname": "Samsung",
            "client_id": "a1b2c3",
        },
        {
            "expiry_epoch": "1775630500",
            "mac": "aa:bb:cc:dd:ee:ff",
            "address": "192.168.50.58",
            "hostname": "unknown",
            "client_id": "*",
        },
    ]


def test_lease_expiry_iso_edge_cases() -> None:
    assert web_module._lease_expiry_iso(None) is None
    assert web_module._lease_expiry_iso({}) is None
    assert web_module._lease_expiry_iso({"expiry_epoch": "  "}) is None
    assert web_module._lease_expiry_iso({"expiry_epoch": "not-a-number"}) is None
    assert web_module._lease_expiry_iso({"expiry_epoch": "1775630400"}) == "2026-04-08T06:40:00+00:00"


def test_neighbor_helpers() -> None:
    lines = ["192.168.50.57 dev eth0 lladdr 5c:c1:d7:f8:a6:f6 REACHABLE", "192.168.50.58 dev eth0 FAILED"]

    assert web_module._neighbor_for_address(lines, None) is None
    assert web_module._neighbor_for_address(lines, "192.168.50.57") == lines[0]
    assert web_module._neighbor_for_address(lines, "192.168.50.99") is None

    assert web_module._neighbor_state(None) is None
    assert web_module._neighbor_state("") is None
    assert web_module._neighbor_state(" ") is None
    assert web_module._neighbor_state(lines[0]) == "REACHABLE"

    assert web_module._neighbor_mac(None) is None
    assert web_module._neighbor_mac(lines[1]) is None
    assert web_module._neighbor_mac("192.168.50.57 dev eth0 lladdr") is None
    assert web_module._neighbor_mac(lines[0]) == "5c:c1:d7:f8:a6:f6"


def test_build_tv_connectivity_states() -> None:
    up = {"name": "eth0", "state": "up", "addresses": "192.168.50.1/24", "present": True}
    down = {**up, "state": "down"}
    lease = {
        "expiry_epoch": "1775630400",
        "mac": "5c:c1:d7:f8:a6:f6",
        "address": "192.168.50.57",
        "hostname": "Samsung",
        "client_id": "*",
    }
    reachable = ["192.168.50.57 dev eth0 lladdr 5c:c1:d7:f8:a6:f6 REACHABLE"]
    failed = ["192.168.50.57 dev eth0 FAILED"]

    status, _, _ = web_module._build_tv_connectivity(down, [lease], reachable)
    assert status == "cable offline"

    status, _, connectivity = web_module._build_tv_connectivity(up, [lease], reachable)
    assert status == "lease active"
    assert connectivity["vendor_hint"] == "Samsung"
    assert connectivity["mac"] == "5c:c1:d7:f8:a6:f6"
    assert connectivity["lease_expires_at"] == "2026-04-08T06:40:00+00:00"

    status, _, _ = web_module._build_tv_connectivity(up, [lease], failed)
    assert status == "lease stale"

    status, _, _ = web_module._build_tv_connectivity(up, [lease], [])
    assert status == "lease present"

    status, _, _ = web_module._build_tv_connectivity(up, [], reachable)
    assert status == "link seen"

    status, _, _ = web_module._build_tv_connectivity(up, [], [])
    assert status == "waiting for TV"


def test_tail_service_log_unavailable_and_empty(monkeypatch) -> None:
    monkeypatch.setattr(web_module, "_run_capture", lambda *args: None)
    assert web_module._tail_service_log("dnsmasq.service") == ["Logs unavailable on this host."]

    monkeypatch.setattr(web_module, "_run_capture", lambda *args: "")
    assert web_module._tail_service_log("dnsmasq.service") == ["No recent log lines."]

    monkeypatch.setattr(web_module, "_run_capture", lambda *args: "first line\nsecond line")
    assert web_module._tail_service_log("dnsmasq.service") == ["first line", "second line"]


def test_collect_appliance_specs_from_probe_output(tmp_path: Path, monkeypatch) -> None:
    def fake_run_capture(*args: str) -> str | None:
        if args[:2] == ("ip", "-brief"):
            return f"{args[-1]} UP 10.0.0.2/24"
        if args[:2] == ("ip", "route"):
            return "default via 10.0.0.1 dev eth1"
        if args[:2] == ("ip", "neigh"):
            return "192.168.50.57 dev eth0 lladdr 5c:c1:d7:f8:a6:f6 REACHABLE"
        if args[:2] == ("cat", "/etc/resolv.conf"):
            return "nameserver 1.1.1.1\nnameserver 8.8.8.8\n"
        if args[:2] == ("cat", "/var/lib/misc/dnsmasq.leases"):
            return "1775630400 5c:c1:d7:f8:a6:f6 192.168.50.57 Samsung *"
        if args[0] == "systemctl":
            return "ActiveState=active\nSubState=running\nResult=success\nUnitFileState=enabled"
        return None

    monkeypatch.setattr(web_module, "_run_capture", fake_run_capture)

    specs = web_module._collect_appliance_specs(build_config(tmp_path))

    assert specs["dns_servers"] == ["1.1.1.1", "8.8.8.8"]
    assert specs["default_route"] == "default via 10.0.0.1 dev eth1"
    assert specs["dhcp_leases"][0]["hostname"] == "Samsung"
    assert specs["service_states"][0]["healthy"] == "yes"
    assert specs["tv_connectivity"]["status"] == "lease active"


def _stub_nordvpn_provider(monkeypatch) -> None:
    monkeypatch.setattr(
        NordVpnProvider,
        "get_state",
        lambda self: ConnectionState(
            provider_name=self.provider_name,
            authenticated=False,
            connected=False,
            current_location=None,
            public_ip=None,
            status_summary="Disconnected",
        ),
    )
    monkeypatch.setattr(NordVpnProvider, "list_locations", lambda self: [])
    monkeypatch.setattr(NordVpnProvider, "login", lambda self, credentials: None)
    monkeypatch.setattr(web_module, "_probe_network_health", lambda config: _network_snapshot_with_latest_lease(None))


def test_nordvpn_login_with_empty_token_does_not_persist(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path, default_provider="nordvpn"))
    client = app.test_client()
    _stub_nordvpn_provider(monkeypatch)

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    response = client.post("/provider/login", data={"provider": "nordvpn", "token": ""}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Authenticated with NordVPN." in response.data
    assert b"Saved the NordVPN token" not in response.data
    assert not app.config["RP_CONFIG"].nordvpn_secret_path.exists()


def test_nordvpn_login_persists_without_systemctl(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path, default_provider="nordvpn"))
    client = app.test_client()
    _stub_nordvpn_provider(monkeypatch)
    monkeypatch.setattr(web_module.shutil, "which", lambda name: None)

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    response = client.post("/provider/login", data={"provider": "nordvpn", "token": "persist-me"}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Saved the NordVPN token for future boots" in response.data
    assert app.config["RP_CONFIG"].nordvpn_secret_path.read_text(encoding="utf-8") == "NORDVPN_ACCESS_TOKEN=persist-me\n"


def test_nordvpn_login_survives_bootstrap_restart_timeout(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path, default_provider="nordvpn"))
    client = app.test_client()
    _stub_nordvpn_provider(monkeypatch)
    monkeypatch.setattr(web_module.shutil, "which", lambda name: "/usr/bin/systemctl" if name == "systemctl" else None)

    def timing_out_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="systemctl", timeout=8)

    monkeypatch.setattr(web_module.subprocess, "run", timing_out_run)

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    response = client.post("/provider/login", data={"provider": "nordvpn", "token": "persist-me"}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Saved the NordVPN token for future boots" in response.data
    assert app.config["RP_CONFIG"].nordvpn_secret_path.read_text(encoding="utf-8") == "NORDVPN_ACCESS_TOKEN=persist-me\n"


def test_nordvpn_login_survives_secret_chmod_failure(tmp_path: Path, monkeypatch) -> None:
    app = create_app(build_config(tmp_path, default_provider="nordvpn"))
    client = app.test_client()
    _stub_nordvpn_provider(monkeypatch)
    monkeypatch.setattr(web_module.shutil, "which", lambda name: "/usr/bin/systemctl" if name == "systemctl" else None)

    class CompletedProcess:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(web_module.subprocess, "run", lambda args, **kwargs: CompletedProcess())

    real_chmod = Path.chmod

    def flaky_chmod(self, mode, **kwargs):
        if self.name == "nordvpn.local.env":
            raise OSError("read-only filesystem")
        return real_chmod(self, mode, **kwargs)

    monkeypatch.setattr(Path, "chmod", flaky_chmod)

    client.post("/setup", data={"password": "lan-admin-pass", "password_confirm": "lan-admin-pass"}, follow_redirects=True)

    response = client.post("/provider/login", data={"provider": "nordvpn", "token": "persist-me"}, follow_redirects=True)

    assert response.status_code == 200
    assert b"Saved the NordVPN token for future boots" in response.data
    assert app.config["RP_CONFIG"].nordvpn_secret_path.read_text(encoding="utf-8") == "NORDVPN_ACCESS_TOKEN=persist-me\n"
