from __future__ import annotations

from openspoofen.config import AppConfig
from openspoofen.providers.base import ProviderMetadata, VpnProvider
from openspoofen.providers.expressvpn import ExpressVpnProvider
from openspoofen.providers.mock import MockVpnProvider
from openspoofen.providers.mullvad import MullvadProvider
from openspoofen.providers.nordvpn import NordVpnProvider
from openspoofen.providers.protonvpn import ProtonVpnProvider
from openspoofen.providers.surfshark import SurfsharkProvider
from openspoofen.providers.wireguard import WireGuardProfileProvider

PROVIDER_REGISTRY: dict[str, type[VpnProvider]] = {
    "wireguard": WireGuardProfileProvider,
    "mock": MockVpnProvider,
    "nordvpn": NordVpnProvider,
    "mullvad": MullvadProvider,
    "expressvpn": ExpressVpnProvider,
    "protonvpn": ProtonVpnProvider,
    "surfshark": SurfsharkProvider,
}


def available_provider_keys() -> list[str]:
    return list(PROVIDER_REGISTRY)


def available_provider_metadata() -> list[ProviderMetadata]:
    return [provider_class.metadata for provider_class in PROVIDER_REGISTRY.values()]


def create_provider(provider_key: str, config: AppConfig) -> VpnProvider:
    normalized_key = provider_key.strip().lower()
    provider_class = PROVIDER_REGISTRY.get(normalized_key)
    if provider_class is None:
        raise ValueError(f"Unsupported provider: {provider_key}")
    return provider_class(config)