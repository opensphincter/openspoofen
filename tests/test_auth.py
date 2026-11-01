import json
from pathlib import Path

import pytest
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

from openspoofen.auth import LanAuthManager, is_private_lan_address


def build_manager(tmp_path: Path) -> LanAuthManager:
    return LanAuthManager(tmp_path / "lan-auth.json", "unit-test-secret")


def test_configure_rejects_short_passwords(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)

    with pytest.raises(ValueError, match="at least 8 characters"):
        manager.configure(password="short")


def test_configure_and_verify_password_roundtrip(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    state = manager.configure(password="correct horse battery")

    assert state.setup_complete is True
    assert manager.verify_password(state, "correct horse battery") is True
    assert manager.verify_password(state, "wrong password") is False

    reloaded = manager.load_state()
    assert reloaded.password_hash == state.password_hash
    assert reloaded.pairing_token == state.pairing_token


def test_verify_password_without_setup_is_false(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    state = manager.load_state()

    assert state.setup_complete is False
    assert manager.verify_password(state, "anything at all") is False


def test_pairing_cookie_roundtrip_and_tamper_resistance(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    state = manager.configure(password="correct horse battery")
    cookie_value = manager.pairing_cookie_value(state)

    def request_with_cookie(value: str | None) -> Request:
        headers = {"Cookie": f"{manager.cookie_name}={value}"} if value else {}
        return Request(EnvironBuilder(headers=headers).get_environ())

    assert manager.request_is_paired(state, request_with_cookie(cookie_value)) is True
    assert manager.request_is_paired(state, request_with_cookie(cookie_value + "tampered")) is False
    assert manager.request_is_paired(state, request_with_cookie(None)) is False

    other_manager = LanAuthManager(tmp_path / "lan-auth.json", "different-secret")
    assert other_manager.request_is_paired(state, request_with_cookie(cookie_value)) is False


def test_pairing_token_matches_strips_candidate(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    state = manager.configure(password="correct horse battery", pairing_token="pair-me-123")

    assert manager.pairing_token_matches(state, "pair-me-123") is True
    assert manager.pairing_token_matches(state, "  pair-me-123  ") is True
    assert manager.pairing_token_matches(state, "pair-me-124") is False


def test_load_state_recovers_from_corrupt_file(tmp_path: Path) -> None:
    state_path = tmp_path / "lan-auth.json"
    state_path.write_text("{not valid json", encoding="utf-8")
    manager = LanAuthManager(state_path, "unit-test-secret")

    state = manager.load_state()

    # Recovery lands in first-boot setup mode instead of raising, and the
    # rewritten state file is valid JSON the next load can read.
    assert state.setup_complete is False
    assert json.loads(state_path.read_text(encoding="utf-8"))["password_hash"] is None
    assert manager.load_state().pairing_token == state.pairing_token


@pytest.mark.parametrize(
    ("remote_addr", "expected"),
    [
        ("192.168.1.5", True),
        ("10.1.2.3", True),
        ("172.16.0.9", True),
        ("127.0.0.1", True),
        ("169.254.10.20", True),
        ("::1", True),
        ("fe80::1", True),
        ("fe80::1%eth0", True),
        ("8.8.8.8", False),
        ("1.1.1.1", False),
        ("2606:4700:4700::1111", False),
        ("192.168.1.1:8080", False),
        ("not-an-ip", False),
        ("", False),
        (None, False),
    ],
)
def test_is_private_lan_address(remote_addr: str | None, expected: bool) -> None:
    assert is_private_lan_address(remote_addr) is expected
