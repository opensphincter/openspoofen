from pathlib import Path
from textwrap import dedent

from openspoofen.config import AppConfig
from openspoofen.providers.base import Location, ProviderError
from openspoofen.providers.expressvpn import ExpressVpnProvider
from openspoofen.providers.mullvad import MullvadProvider
from openspoofen.providers.nordvpn import NordVpnProvider
from openspoofen.providers.protonvpn import ProtonVpnProvider
from openspoofen.providers.surfshark import SurfsharkProvider


def test_expressvpn_region_parser_handles_country_and_city() -> None:
    output = dedent(
        """
        All Locations
          Americas
            United States - New York
            Canada
          Europe
            Germany - Frankfurt
        """
    )

    locations = ExpressVpnProvider._parse_regions(output)
    labels = [location.label for location in locations]
    assert "United States / New York" in labels
    assert "Canada" in labels
    assert "Germany / Frankfurt" in labels


def test_location_normalizes_underscores_for_display() -> None:
    location = Location(country="United_States", city="New_York", target="United_States")

    assert location.country == "United States"
    assert location.city == "New York"
    assert location.label == "United States / New York"


def test_mullvad_relay_parser_keeps_country_codes() -> None:
    output = dedent(
        """
        Sweden (se)
          Gothenburg (got)
        United States (us)
          New York (nyc)
          Los Angeles (lax)
        """
    )

    locations = MullvadProvider._parse_relays(output)
    targets = {location.label: location.target for location in locations}
    assert targets["Sweden"] == "se"
    assert targets["United States / New York"] == "us nyc"
    assert targets["United States / Los Angeles"] == "us lax"


def test_protonvpn_country_parser_accepts_country_codes() -> None:
    output = dedent(
        """
        US United States
        CA Canada
        JP Japan
        """
    )

    locations = ProtonVpnProvider._parse_countries(output)
    assert [location.country for location in locations] == ["United States", "Canada", "Japan"]


def stub_nordvpn(monkeypatch, outputs: dict[str, str]) -> NordVpnProvider:
    provider = NordVpnProvider(AppConfig())

    def fake_run(*args: str) -> str:
        command = args[0]
        if command in outputs:
            return outputs[command]
        raise ProviderError(f"unexpected command: {command}")

    monkeypatch.setattr(provider, "_run", fake_run)
    return provider


def test_nordvpn_location_list_filters_placeholder_sections(monkeypatch) -> None:
    provider = stub_nordvpn(monkeypatch, {"countries": "All Regions\nCanada\nGermany\nUnited States\n"})

    locations = provider.list_locations()

    assert [location.country for location in locations] == ["Canada", "Germany", "United States"]


def test_nordvpn_state_parses_status_output(monkeypatch) -> None:
    status = dedent(
        """\
        Status: Connected
        Hostname: us1234.nordvpn.com
        Country: United States
        City: New York
        Your new IP: 198.51.100.23
        """
    )
    provider = stub_nordvpn(monkeypatch, {"status": status, "account": "Email: owner@example.com"})

    state = provider.get_state()

    assert state.connected is True
    assert state.authenticated is True
    assert state.public_ip == "198.51.100.23"
    assert state.current_location is not None
    assert state.current_location.label == "United States / New York"


def test_nordvpn_state_marks_unauthenticated_when_account_fails(monkeypatch) -> None:
    provider = stub_nordvpn(monkeypatch, {"status": "Status: Disconnected"})

    def fake_run(*args: str) -> str:
        if args[0] == "account":
            raise ProviderError("You are not logged in.")
        return "Status: Disconnected"

    monkeypatch.setattr(provider, "_run", fake_run)

    state = provider.get_state()

    assert state.connected is False
    assert state.authenticated is False


def test_surfshark_profile_discovery_uses_filenames(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "runtime"
    config_dir = tmp_path / "surfshark"
    config_dir.mkdir(parents=True)
    (config_dir / "us-new-york.prod.surfshark.com_udp.ovpn").write_text("client\n", encoding="utf-8")
    (config_dir / "gb-london.prod.surfshark.com_tcp.ovpn").write_text("client\n", encoding="utf-8")

    provider = SurfsharkProvider(
        AppConfig(
            runtime_dir=runtime_dir,
            state_path=runtime_dir / "mock-state.json",
            surfshark_config_dir=config_dir,
        )
    )

    labels = [location.label for location in provider.list_locations()]
    assert "United States / New York" in labels
    assert "United Kingdom / London" in labels