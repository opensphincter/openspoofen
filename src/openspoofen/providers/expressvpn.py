from __future__ import annotations

import re
from typing import ClassVar

from openspoofen.config import AppConfig
from openspoofen.providers.base import (
    AuthField,
    ConnectionState,
    Location,
    ProviderMetadata,
)
from openspoofen.providers.command import CommandVpnProvider


class ExpressVpnProvider(CommandVpnProvider):
    metadata = ProviderMetadata(
        provider_id="expressvpn",
        provider_name="ExpressVPN",
        auth_fields=(
            AuthField(
                key="activation_code",
                label="Activation code",
                placeholder="ExpressVPN activation code",
                help_text="The CLI supports Raspberry Pi OS 64-bit, but the activation flow is less appliance-friendly than NordVPN.",
            ),
        ),
        setup_steps=(
            "Install the official ExpressVPN Linux client for Raspberry Pi OS 64-bit.",
            "Authenticate with your activation code.",
            "Enable background mode so connect and disconnect commands work headlessly.",
        ),
        notes=(
            "ExpressVPN is a viable secondary adapter, but its onboarding flow is less streamlined for a headless appliance.",
        ),
    )
    command_names = ("expressvpnctl",)
    _SECTION_HEADERS: ClassVar[frozenset[str]] = frozenset({
        "all locations",
        "recommended",
        "smart location",
        "americas",
        "europe",
        "middle east and africa",
        "asia pacific",
        "locations",
    })

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def list_locations(self) -> list[Location]:
        return self._parse_regions(self._run("get", "regions"))

    def get_state(self) -> ConnectionState:
        status_output = self._run("status")
        connected = "connected" in status_output.lower() and "not connected" not in status_output.lower()
        location = self._location_from_status(status_output)
        public_ip_match = re.search(r"(?:IP|Public IP)\s*[:=]\s*(?P<ip>\S+)", status_output, re.IGNORECASE)
        authenticated = "not logged in" not in status_output.lower() and "not activated" not in status_output.lower()

        return ConnectionState(
            provider_name=self.provider_name,
            authenticated=authenticated,
            connected=connected,
            current_location=location,
            public_ip=public_ip_match.group("ip") if public_ip_match else None,
            status_summary=status_output.splitlines()[0].strip() if status_output else "Unknown",
        )

    def login(self, credentials: dict[str, str]) -> None:
        activation_code = self.require_credential(credentials, "activation_code", "an activation code")
        self._run("login", activation_code)

    def connect(self, country: str, city: str | None = None) -> None:
        self._run("background", "enable")
        if city:
            location = self.resolve_location(country, city)
            self._run("connect", location.target or location.label)
            return
        self._run("connect", country)

    def disconnect(self) -> None:
        self._run("disconnect")

    @classmethod
    def _parse_regions(cls, output: str) -> list[Location]:
        locations: list[Location] = []
        seen: set[str] = set()
        for raw_line in output.splitlines():
            line = raw_line.strip().lstrip("-*0123456789. ")
            if not line:
                continue
            if line.casefold() in cls._SECTION_HEADERS:
                continue

            location = cls._parse_region_label(line)
            key = location.label.casefold()
            if key in seen:
                continue
            seen.add(key)
            locations.append(location)
        return locations

    @classmethod
    def _parse_region_label(cls, label: str) -> Location:
        normalized = label.replace(" – ", " - ").strip()
        if " - " in normalized:
            country, city = normalized.split(" - ", 1)
            return Location(country=country.strip(), city=city.strip(), target=normalized)
        return Location(country=normalized, target=normalized)

    @classmethod
    def _location_from_status(cls, output: str) -> Location | None:
        match = re.search(r"connected to\s+(?P<label>.+)$", output, re.IGNORECASE | re.MULTILINE)
        if not match:
            return None
        return cls._parse_region_label(match.group("label").strip())