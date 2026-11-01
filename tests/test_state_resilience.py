"""Corrupt or stale on-disk state must degrade to defaults, never crash.

The appliance writes small JSON state files (mock provider, WireGuard,
Surfshark, TV remote, LAN auth). A power cut mid-write can leave any of
them truncated; every reader is expected to fall back to its default
instead of taking the whole control surface down with a 500.
"""

import os
from pathlib import Path

from openspoofen.config import AppConfig
from openspoofen.providers.mock import MockVpnProvider
from openspoofen.providers.surfshark import SurfsharkProvider
from openspoofen.providers.wireguard import WireGuardProfileProvider
from openspoofen.tv_remote import TvRemoteManager


def test_mock_provider_tolerates_corrupt_state(tmp_path: Path) -> None:
    state_path = tmp_path / "mock-state.json"
    state_path.write_text("{truncated", encoding="utf-8")
    provider = MockVpnProvider(AppConfig(state_path=state_path))

    state = provider.get_state()

    assert state.authenticated is False
    assert state.connected is False


def test_wireguard_provider_tolerates_corrupt_state(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    (runtime_dir / "wireguard-state.json").write_text('["not", "a", "dict"]', encoding="utf-8")
    provider = WireGuardProfileProvider(
        AppConfig(runtime_dir=runtime_dir, wireguard_config_dir=tmp_path / "wg")
    )

    state = provider.get_state()

    assert state.connected is False
    assert "No WireGuard region is active" in state.status_summary


def test_surfshark_provider_tolerates_corrupt_state(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "runtime"
    runtime_dir.mkdir()
    (runtime_dir / "surfshark-state.json").write_text("{oops", encoding="utf-8")
    provider = SurfsharkProvider(AppConfig(runtime_dir=runtime_dir, surfshark_config_dir=tmp_path / "ss"))

    state = provider.get_state()

    assert state.connected is False
    assert state.authenticated is False


def test_tv_remote_tolerates_corrupt_state_and_bad_port(tmp_path: Path) -> None:
    state_path = tmp_path / "tv-remote.json"
    manager = TvRemoteManager(AppConfig(tv_remote_state_path=state_path, runtime_dir=tmp_path / "runtime"))

    state_path.write_text("{corrupt", encoding="utf-8")
    assert manager.load_state().host is None

    state_path.write_text('{"host": "192.168.50.57", "port": "banana"}', encoding="utf-8")
    loaded = manager.load_state()
    assert loaded.host == "192.168.50.57"
    assert loaded.port is None

    state_path.write_text('{"host": "192.168.50.57", "port": 70000}', encoding="utf-8")
    assert manager.load_state().port is None

    state_path.write_text('{"host": "192.168.50.57", "port": 8002}', encoding="utf-8")
    assert manager.load_state().port == 8002

    # status() is what the dashboard calls on every render; it must not raise.
    assert manager.status()["effective_host"] == "192.168.50.57"


def build_surfshark(tmp_path: Path) -> SurfsharkProvider:
    return SurfsharkProvider(AppConfig(runtime_dir=tmp_path / "runtime", surfshark_config_dir=tmp_path / "ss"))


def test_surfshark_ignores_recycled_pid(tmp_path: Path) -> None:
    """A PID file pointing at a live non-OpenVPN process is not "connected".

    Uses this test process's own PID: it is guaranteed alive and guaranteed
    not to be OpenVPN, which is exactly the recycled-PID situation.
    """
    provider = build_surfshark(tmp_path)
    provider._runtime_dir.mkdir(parents=True, exist_ok=True)
    provider._pid_file.write_text(str(os.getpid()), encoding="utf-8")

    assert SurfsharkProvider._pid_is_running(os.getpid()) is True
    assert provider._pid_is_openvpn(os.getpid()) is False
    assert provider.get_state().connected is False

    # disconnect() must not signal the unrelated process; it only updates state.
    provider.disconnect()
    assert provider.get_state().connected is False


def test_surfshark_read_pid_rejects_nonpositive_and_junk(tmp_path: Path) -> None:
    provider = build_surfshark(tmp_path)
    provider._runtime_dir.mkdir(parents=True, exist_ok=True)

    for contents in ("-1", "0", "banana", ""):
        provider._pid_file.write_text(contents, encoding="utf-8")
        assert provider._read_pid() is None, contents

    provider._pid_file.write_text("12345", encoding="utf-8")
    assert provider._read_pid() == 12345
