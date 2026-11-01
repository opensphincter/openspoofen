from __future__ import annotations

import json

from openspoofen.config import AppConfig
from openspoofen.providers.base import (
    AuthField,
    ConnectionState,
    Location,
    ProviderError,
    ProviderMetadata,
    VpnProvider,
)


class MockVpnProvider(VpnProvider):
    metadata = ProviderMetadata(
        provider_id="mock",
        provider_name="Mock Provider",
        auth_fields=(
            AuthField(
                key="token",
                label="Demo token",
                placeholder="any non-empty value",
                help_text="Used only to exercise the login and location-switch flow.",
            ),
        ),
        setup_steps=(
            "Set RP_PROVIDER=mock for local UI development.",
            "Run the Flask app without installing any VPN client.",
        ),
        notes=(
            "Mock mode does not touch system networking.",
            "Use it for UI development, tests, and onboarding flow validation.",
        ),
    )

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._state_path = config.state_path
        self._locations = [
            Location(country="United States", target="United States"),
            Location(country="United States", city="New York", target="United States/New York"),
            Location(country="United States", city="Los Angeles", target="United States/Los Angeles"),
            Location(country="Canada", target="Canada"),
            Location(country="Canada", city="Toronto", target="Canada/Toronto"),
            Location(country="United Kingdom", target="United Kingdom"),
            Location(country="United Kingdom", city="London", target="United Kingdom/London"),
            Location(country="Germany", city="Frankfurt", target="Germany/Frankfurt"),
            Location(country="Japan", city="Tokyo", target="Japan/Tokyo"),
        ]
        self._public_ips = {
            "United States/New York": "198.51.100.14",
            "United States/Los Angeles": "198.51.100.29",
            "Canada/Toronto": "203.0.113.21",
            "United Kingdom/London": "203.0.113.44",
            "Germany/Frankfurt": "203.0.113.78",
            "Japan/Tokyo": "203.0.113.99",
        }

    def list_locations(self) -> list[Location]:
        return list(self._locations)

    def get_state(self) -> ConnectionState:
        raw_state = self._read_state()
        location = self._location_from_raw(raw_state)
        location_key = location.target if location else None

        return ConnectionState(
            provider_name=self.provider_name,
            authenticated=bool(raw_state.get("authenticated", False)),
            connected=bool(raw_state.get("connected", False)),
            current_location=location,
            public_ip=self._public_ips.get(location_key) if location else None,
            status_summary=raw_state.get("status_summary", "Ready for simulation"),
        )

    def login(self, credentials: dict[str, str]) -> None:
        token = credentials.get("token", "")
        if not token.strip():
            raise ProviderError("Mock login requires a non-empty token or account string.")

        state = self._read_state()
        state["authenticated"] = True
        state["status_summary"] = "Authenticated in mock mode"
        self._write_state(state)

    def connect(self, country: str, city: str | None = None) -> None:
        state = self._read_state()
        if not state.get("authenticated"):
            raise ProviderError("Authenticate with the mock provider before switching regions.")

        target = self.resolve_location(country, city)
        state["connected"] = True
        state["country"] = target.country
        state["city"] = target.city
        state["status_summary"] = f"Connected to {target.label} in mock mode"
        self._write_state(state)

    def disconnect(self) -> None:
        state = self._read_state()
        state["connected"] = False
        state["status_summary"] = "Disconnected in mock mode"
        self._write_state(state)

    def _read_state(self) -> dict[str, object]:
        default_state: dict[str, object] = {
            "authenticated": False,
            "connected": False,
            "status_summary": "Ready for simulation",
        }
        if not self._state_path.exists():
            return default_state

        try:
            raw_state = json.loads(self._state_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return default_state
        return raw_state if isinstance(raw_state, dict) else default_state

    def _write_state(self, state: dict[str, object]) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _location_from_raw(self, state: dict[str, object]) -> Location | None:
        country = state.get("country")
        if not isinstance(country, str) or not country:
            return None

        city = state.get("city")
        return Location(
            country=country,
            city=city if isinstance(city, str) else None,
            target=f"{country}/{city}".rstrip("/") if isinstance(city, str) and city else country,
        )