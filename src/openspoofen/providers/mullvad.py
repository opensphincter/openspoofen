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


class MullvadProvider(CommandVpnProvider):
    metadata = ProviderMetadata(
        provider_id="mullvad",
        provider_name="Mullvad",
        auth_fields=(
            AuthField(
                key="account_number",
                label="Account number",
                placeholder="1234 5678 9012 3456",
                help_text="Mullvad uses an account-number-based login flow rather than an email and password pair.",
            ),
        ),
        setup_steps=(
            "Install the Mullvad Linux app and CLI.",
            "Log in with your Mullvad account number.",
            "Allow LAN access and enable lockdown mode if the appliance is operating in fail-closed mode.",
        ),
        notes=(
            "Mullvad is the strongest non-Nord alternative in this repo.",
            "Its Linux story is mature, but Raspberry Pi OS validation still needs hardware sign-off.",
        ),
    )
    command_names = ("mullvad",)

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def list_locations(self) -> list[Location]:
        return self._parse_relays(self._run("relay", "list"))

    def get_state(self) -> ConnectionState:
        status_output = self._run("status")
        connected = "connected" in status_output.lower() and "disconnected" not in status_output.lower()
        account_result = self._run_result("account", "get")
        account_text = self._result_text(account_result).lower()
        authenticated = account_result.returncode == 0 and "not logged in" not in account_text

        return ConnectionState(
            provider_name=self.provider_name,
            authenticated=authenticated,
            connected=connected,
            current_location=self._location_from_status(status_output),
            public_ip=None,
            status_summary=status_output.splitlines()[0].strip() if status_output else "Unknown",
        )

    def login(self, credentials: dict[str, str]) -> None:
        account_number = self.require_credential(credentials, "account_number", "an account number")
        self._run("account", "login", account_number)

    def connect(self, country: str, city: str | None = None) -> None:
        location = self.resolve_location(country, city)
        target_parts = (location.target or location.country).split()
        self._run("relay", "set", "location", *target_parts)
        self._run("connect")

    def disconnect(self) -> None:
        self._run("disconnect")

    @classmethod
    def _parse_relays(cls, output: str) -> list[Location]:
        locations: list[Location] = []
        current_country_name: str | None = None
        current_country_code: str | None = None

        for raw_line in output.splitlines():
            if not raw_line.strip():
                continue

            if raw_line[:1].isspace():
                if current_country_name is None or current_country_code is None:
                    continue
                parsed = cls._parse_name_and_code(raw_line.strip())
                if parsed is None:
                    continue
                city_name, city_code = parsed
                locations.append(
                    Location(
                        country=current_country_name,
                        city=city_name,
                        target=f"{current_country_code} {city_code}" if city_code else current_country_code,
                    )
                )
                continue

            parsed = cls._parse_name_and_code(raw_line.strip())
            if parsed is None:
                continue
            current_country_name, current_country_code = parsed
            locations.append(Location(country=current_country_name, target=current_country_code or current_country_name))

        return locations

    @staticmethod
    def _parse_name_and_code(line: str) -> tuple[str, str | None] | None:
        normalized = line.strip().lstrip("-*0123456789. ")
        if not normalized:
            return None

        name_code_match = re.match(r"^(?P<name>.+?)\s+\((?P<code>[a-z0-9-]+)\)$", normalized, re.IGNORECASE)
        if name_code_match:
            return name_code_match.group("name"), name_code_match.group("code")

        code_name_match = re.match(r"^(?P<code>[a-z0-9-]+)\s+\((?P<name>.+)\)$", normalized, re.IGNORECASE)
        if code_name_match:
            return code_name_match.group("name"), code_name_match.group("code")

        return normalized, None

    @classmethod
    def _location_from_status(cls, output: str) -> Location | None:
        match = re.search(r"connected to\s+(?P<label>.+)$", output, re.IGNORECASE | re.MULTILINE)
        if not match:
            return None

        label = match.group("label").strip()
        if " (" in label:
            parsed = cls._parse_name_and_code(label)
            if parsed is not None:
                country_name, country_code = parsed
                return Location(country=country_name, target=country_code or country_name)

        if "-" in label:
            parts = [segment for segment in label.split("-") if segment]
            if len(parts) >= 2:
                return Location(country=parts[0].upper(), city=parts[1].upper(), target=" ".join(parts[:2]))

        return Location(country=label, target=label)