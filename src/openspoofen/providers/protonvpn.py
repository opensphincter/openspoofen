from __future__ import annotations

import re

from openspoofen.config import AppConfig
from openspoofen.providers.base import (
    AuthField,
    ConnectionState,
    Location,
    ProviderMetadata,
)
from openspoofen.providers.command import CommandVpnProvider


class ProtonVpnProvider(CommandVpnProvider):
    metadata = ProviderMetadata(
        provider_id="protonvpn",
        provider_name="Proton VPN",
        auth_fields=(
            AuthField(
                key="username",
                label="Username",
                placeholder="Proton username",
                secret=False,
                help_text="The official CLI integrates with NetworkManager and keyring-backed login flows.",
            ),
            AuthField(
                key="password",
                label="Password",
                placeholder="Proton password",
            ),
        ),
        setup_steps=(
            "Install the official Proton VPN Linux CLI with NetworkManager support.",
            "Confirm the target Pi image includes the required keyring components.",
            "Validate the exact headless login behavior on Raspberry Pi OS before calling this production-ready.",
        ),
        notes=(
            "Proton VPN support is included, but its Linux onboarding remains less appliance-friendly than NordVPN or Mullvad.",
            "Treat it as a supported adapter with extra validation requirements rather than the default path.",
        ),
        supports_city_selection=False,
    )
    command_names = ("protonvpn-cli", "protonvpn")

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def list_locations(self) -> list[Location]:
        return self._parse_countries(self._run("countries"))

    def get_state(self) -> ConnectionState:
        status_output = self._run("status")
        connected = "connected" in status_output.lower() and "disconnected" not in status_output.lower()
        authenticated = "not logged in" not in status_output.lower() and "sign in" not in status_output.lower()
        current_location = None

        country_match = re.search(r"country\s*[:=]\s*(?P<country>.+)$", status_output, re.IGNORECASE | re.MULTILINE)
        if country_match:
            current_location = Location(country=country_match.group("country").strip())

        return ConnectionState(
            provider_name=self.provider_name,
            authenticated=authenticated,
            connected=connected,
            current_location=current_location,
            public_ip=None,
            status_summary=status_output.splitlines()[0].strip() if status_output else "Unknown",
        )

    def login(self, credentials: dict[str, str]) -> None:
        username = self.require_credential(credentials, "username", "a username")
        password = self.require_credential(credentials, "password", "a password")
        self._run("signin", username, input_text=f"{password}\n")

    def connect(self, country: str, city: str | None = None) -> None:
        if city:
            self._run("connect", "--city", city)
            return
        self._run("connect", "--country", country)

    def disconnect(self) -> None:
        self._run("disconnect")

    @staticmethod
    def _parse_countries(output: str) -> list[Location]:
        locations: list[Location] = []
        seen: set[str] = set()
        for raw_line in output.splitlines():
            line = raw_line.strip().lstrip("-*0123456789. ")
            if not line:
                continue
            if line.casefold() in {"country", "countries", "available countries"}:
                continue

            match = re.match(r"^(?P<code>[A-Z]{2})\s+(?P<name>.+)$", line)
            country_name = match.group("name").strip() if match else line
            if country_name.casefold() in seen:
                continue
            seen.add(country_name.casefold())
            locations.append(Location(country=country_name, target=country_name))
        return locations