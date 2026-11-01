from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

_PLACEHOLDER_LOCATION_NAMES = {
    "all countries",
    "all locations",
    "all regions",
    "available countries",
    "countries",
    "country",
    "locations",
    "recommended",
    "regions",
    "smart location",
}


def normalize_location_name(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = re.sub(r"_+", " ", value).strip()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized or None


def is_placeholder_location_name(value: str | None) -> bool:
    normalized = normalize_location_name(value)
    if not normalized:
        return True
    return normalized.casefold() in _PLACEHOLDER_LOCATION_NAMES


class ProviderError(RuntimeError):
    """Raised when a provider operation cannot be completed."""


@dataclass(slots=True, frozen=True)
class AuthField:
    key: str
    label: str
    placeholder: str = ""
    secret: bool = True
    help_text: str = ""


@dataclass(slots=True, frozen=True)
class ProviderMetadata:
    provider_id: str
    provider_name: str
    auth_fields: tuple[AuthField, ...] = ()
    setup_steps: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    supports_city_selection: bool = True


@dataclass(slots=True, frozen=True)
class Location:
    country: str
    city: str | None = None
    target: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "country", normalize_location_name(self.country) or "Unknown")
        object.__setattr__(self, "city", normalize_location_name(self.city))

    @property
    def label(self) -> str:
        if self.city:
            return f"{self.country} / {self.city}"
        return self.country


@dataclass(slots=True)
class ConnectionState:
    provider_name: str
    authenticated: bool
    connected: bool
    current_location: Location | None
    public_ip: str | None
    status_summary: str


class VpnProvider(ABC):
    metadata: ProviderMetadata

    @property
    def provider_id(self) -> str:
        return self.metadata.provider_id

    @property
    def provider_name(self) -> str:
        return self.metadata.provider_name

    def resolve_location(self, country: str, city: str | None = None) -> Location:
        normalized_country = country.strip().casefold()
        normalized_city = city.strip().casefold() if city else None
        matches: list[Location] = []

        for location in self.list_locations():
            if location.country.casefold() != normalized_country:
                continue
            if normalized_city is not None and (location.city or "").casefold() != normalized_city:
                continue
            matches.append(location)

        if not matches:
            location_label = country if not city else f"{country} / {city}"
            raise ProviderError(f"Unknown location for {self.provider_name}: {location_label}")

        if normalized_city is None:
            for location in matches:
                if location.city is None:
                    return location

        return matches[0]

    def require_credential(self, credentials: dict[str, str], key: str, label: str) -> str:
        value = credentials.get(key, "").strip()
        if value:
            return value
        raise ProviderError(f"{self.provider_name} requires {label}.")

    @abstractmethod
    def list_locations(self) -> list[Location]:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> ConnectionState:
        raise NotImplementedError

    @abstractmethod
    def login(self, credentials: dict[str, str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def connect(self, country: str, city: str | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        raise NotImplementedError