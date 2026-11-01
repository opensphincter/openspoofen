import base64
from pathlib import Path

import openspoofen.tv_remote as tv_remote_module
from openspoofen.config import AppConfig
from openspoofen.tv_remote import TvRemoteManager


def build_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        runtime_dir=tmp_path / "runtime",
        tv_remote_state_path=tmp_path / "tv-remote.json",
        tv_remote_name="OpenSpoofen Remote",
        tv_remote_vendor="samsung",
    )


def test_status_reports_detected_host_when_remote_not_saved(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(tv_remote_module, "SamsungTVWS", object())

    manager = TvRemoteManager(build_config(tmp_path))

    status = manager.status(latest_lease={"hostname": "Samsung", "address": "192.168.50.57"})

    assert status["configured"] is False
    assert status["ready"] is True
    assert status["auto_detected"] is True
    assert status["effective_host"] == "192.168.50.57"
    assert "automatically" in str(status["status_summary"])


def test_send_key_uses_detected_host_and_persists_it(tmp_path: Path, monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeSamsungTVWS:
        def __init__(self, *, host, port, timeout, key_press_delay, name, token_file):
            captured["host"] = host
            captured["port"] = port
            captured["name"] = name
            captured["token_file"] = token_file

        def open(self) -> None:
            captured["opened"] = True

        def send_key(self, key, key_press_delay=0.12) -> None:
            captured["key"] = key
            captured["key_press_delay"] = key_press_delay

        def close(self) -> None:
            captured["closed"] = True

    monkeypatch.setattr(tv_remote_module, "SamsungTVWS", FakeSamsungTVWS)

    manager = TvRemoteManager(build_config(tmp_path))

    status = manager.send_key("home", latest_lease={"hostname": "Samsung", "address": "192.168.50.57"})

    assert captured["host"] == "192.168.50.57"
    assert captured["port"] == 8002
    assert captured["key"] == "KEY_HOME"
    assert captured["opened"] is True
    assert captured["closed"] is True
    assert manager.load_state().host == "192.168.50.57"
    assert status["effective_host"] == "192.168.50.57"
    assert status["auto_detected"] is False


def test_send_text_uses_detected_host_and_sends_input_commands(tmp_path: Path, monkeypatch) -> None:
    captured: dict[str, object] = {}
    commands: list[tuple[object, float | None]] = []

    class FakeSamsungTVWS:
        def __init__(self, *, host, port, timeout, key_press_delay, name, token_file):
            captured["host"] = host
            captured["port"] = port
            captured["name"] = name
            captured["token_file"] = token_file

        def open(self) -> None:
            captured["opened"] = True

        def send_command(self, command, key_press_delay=None) -> None:
            commands.append((command, key_press_delay))

        def close(self) -> None:
            captured["closed"] = True

    monkeypatch.setattr(tv_remote_module, "SamsungTVWS", FakeSamsungTVWS)

    manager = TvRemoteManager(build_config(tmp_path))

    status = manager.send_text("hello", latest_lease={"hostname": "Samsung", "address": "192.168.50.57"}, submit=True)

    assert captured["host"] == "192.168.50.57"
    assert captured["port"] == 8002
    assert captured["opened"] is True
    assert captured["closed"] is True
    assert commands[0][0] == {
        "method": "ms.channel.emit",
        "params": {"event": "custom.remote.textReceived", "to": "broadcast"},
    }
    assert commands[1][0] == {
        "method": "ms.remote.control",
        "params": {
            "Cmd": base64.b64encode(b"hello").decode("ascii"),
            "DataOfCmd": "base64",
            "TypeOfRemote": "SendInputString",
        },
    }
    assert commands[2][0] == {
        "method": "ms.remote.control",
        "params": {"TypeOfRemote": "SendInputEnd"},
    }
    assert manager.load_state().host == "192.168.50.57"
    assert status["effective_host"] == "192.168.50.57"
