from __future__ import annotations

import os

from openspoofen.config import AppConfig
from openspoofen.providers.base import (
    AuthField,
    ConnectionState,
    Location,
    ProviderError,
    ProviderMetadata,
)
from openspoofen.providers.command import CommandVpnProvider


class NordVpnProvider(CommandVpnProvider):
    metadata = ProviderMetadata(
        provider_id="nordvpn",
        provider_name="NordVPN",
        auth_fields=(
            AuthField(
                key="token",
                label="Access token",
                placeholder="nordvpn token",
                help_text="Use a NordVPN token-based headless login for appliance onboarding. The device token is reused automatically when it is loaded into the Pi service environment.",
            ),
        ),
        setup_steps=(
            "Install the official NordVPN Linux CLI on Raspberry Pi OS Lite 64-bit.",
            "Load a headless access token into the Pi once, or use the UI field only for manual recovery.",
            "Confirm LAN access is allowed for the downstream routed device.",
        ),
        notes=(
            "This is the strongest appliance-fit provider in the current repo.",
            "Validate DNS, IPv6, and fail-closed behavior on real Pi hardware before release.",
        ),
    )
    command_names = ("nordvpn",)

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def list_locations(self) -> list[Location]:
        output = self._run("countries")
        countries = [line.strip() for line in output.splitlines() if line.strip()]
        return [
            Location(country=country, target=country)
            for country in countries
            if country.strip().casefold() not in {"all regions", "all locations"}
        ]

    def get_state(self) -> ConnectionState:
        status_output = self._run("status")
        status_map = self._parse_key_value_output(status_output)
        status = status_map.get("Status", "Unknown")
        country = status_map.get("Country")
        city = status_map.get("City")
        public_ip = status_map.get("Your new IP")

        authenticated = True
        try:
            self._run("account")
        except ProviderError:
            authenticated = False

        location = None
        if country:
            location = Location(country=country, city=city)

        return ConnectionState(
            provider_name=self.provider_name,
            authenticated=authenticated,
            connected=status.lower() == "connected",
            current_location=location,
            public_ip=public_ip,
            status_summary=status,
        )

    def login(self, credentials: dict[str, str]) -> None:
        token = credentials.get("token", "").strip() or os.getenv("NORDVPN_ACCESS_TOKEN", "").strip()
        if not token:
            raise ProviderError(f"{self.provider_name} requires an access token.")
        self._run("login", "--token", token)

    def connect(self, country: str, city: str | None = None) -> None:
        if city:
            self._run("connect", city)
            return

        self._run("connect", country)

    def disconnect(self) -> None:
        self._run("disconnect")

    def _parse_key_value_output(self, output: str) -> dict[str, str]:
        data: dict[str, str] = {}
        for line in output.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
        return data