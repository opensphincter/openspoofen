from pathlib import Path

from openspoofen.config import AppConfig
from openspoofen.providers.base import ProviderError
from openspoofen.providers.mock import MockVpnProvider


def test_mock_provider_requires_authentication(tmp_path: Path) -> None:
    provider = MockVpnProvider(AppConfig(state_path=tmp_path / "state.json"))

    try:
        provider.connect("United States")
    except ProviderError as error:
        assert "Authenticate" in str(error)
    else:
        raise AssertionError("Expected ProviderError before login")


def test_mock_provider_login_and_connect(tmp_path: Path) -> None:
    provider = MockVpnProvider(AppConfig(state_path=tmp_path / "state.json"))

    provider.login({"token": "demo-token"})
    provider.connect("United States", "Los Angeles")

    state = provider.get_state()
    assert state.authenticated is True
    assert state.connected is True
    assert state.current_location is not None
    assert state.current_location.country == "United States"
    assert state.current_location.city == "Los Angeles"


def test_mock_provider_disconnect(tmp_path: Path) -> None:
    provider = MockVpnProvider(AppConfig(state_path=tmp_path / "state.json"))

    provider.login({"token": "demo-token"})
    provider.connect("Canada", "Toronto")
    provider.disconnect()

    state = provider.get_state()
    assert state.connected is False