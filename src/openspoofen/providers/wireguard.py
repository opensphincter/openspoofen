from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from openspoofen.config import AppConfig
from openspoofen.providers.base import (
    ConnectionState,
    Location,
    ProviderError,
    ProviderMetadata,
    VpnProvider,
)


class WireGuardProfileProvider(VpnProvider):
    metadata = ProviderMetadata(
        provider_id="wireguard",
        provider_name="WireGuard Profiles",
        setup_steps=(
            "Place one WireGuard config per region under configs/wireguard/.",
            "Name files by region, for example us-new-york.conf or uk-london.conf, or add '# label:' comments for cleaner names.",
            "Use the LAN dashboard to switch the active egress profile.",
        ),
        notes=(
            "This is the preferred dataplane for the appliance UX.",
            "Kill-switch, DNS, and TV-side routing still need the nftables and dnsmasq dataplane work behind this UI.",
        ),
    )

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._config_dir = config.wireguard_config_dir
        self._state_path = config.runtime_dir / "wireguard-state.json"

    def list_locations(self) -> list[Location]:
        if not self._config_dir.exists():
            return []

        locations: list[Location] = []
        seen: set[str] = set()
        for config_path in sorted(self._config_dir.glob("*.conf")):
            location = self._location_from_config_path(config_path)
            key = location.label.casefold()
            if key in seen:
                continue
            seen.add(key)
            locations.append(location)
        return locations

    def get_state(self) -> ConnectionState:
        raw_state = self._read_state()
        current_path = Path(raw_state.get("config_path", "")) if raw_state.get("config_path") else None
        current_location = self._location_from_config_path(current_path) if current_path and current_path.exists() else None

        if current_path is None:
            return ConnectionState(
                provider_name=self.provider_name,
                authenticated=True,
                connected=False,
                current_location=None,
                public_ip=None,
                status_summary="No WireGuard region is active",
            )

        wg_executable = shutil.which("wg")
        if wg_executable is None:
            return ConnectionState(
                provider_name=self.provider_name,
                authenticated=True,
                connected=False,
                current_location=current_location,
                public_ip=None,
                status_summary="WireGuard tools are not installed on this machine",
            )

        interface_name = raw_state.get("interface_name") or current_path.stem
        try:
            result = subprocess.run(
                [wg_executable, "show", str(interface_name)],
                check=False,
                capture_output=True,
                text=True,
                timeout=self._config.command_timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            return ConnectionState(
                provider_name=self.provider_name,
                authenticated=True,
                connected=False,
                current_location=current_location,
                public_ip=None,
                status_summary=f"WireGuard state probe timed out after {self._config.command_timeout_seconds:g}s",
            )

        if result.returncode != 0:
            error_text = (result.stderr or result.stdout).strip() or "WireGuard interface is down"
            return ConnectionState(
                provider_name=self.provider_name,
                authenticated=True,
                connected=False,
                current_location=current_location,
                public_ip=None,
                status_summary=error_text,
            )

        transfer = self._parse_transfer_summary(result.stdout)
        handshake = self._parse_handshake_summary(result.stdout)
        status_bits = ["WireGuard connected"]
        if handshake:
            status_bits.append(handshake)
        if transfer:
            status_bits.append(transfer)

        return ConnectionState(
            provider_name=self.provider_name,
            authenticated=True,
            connected=True,
            current_location=current_location,
            public_ip=None,
            status_summary=" | ".join(status_bits),
        )

    def login(self, credentials: dict[str, str]) -> None:
        raise ProviderError("WireGuard profile switching does not use a provider login flow.")

    def connect(self, country: str, city: str | None = None) -> None:
        location = self.resolve_location(country, city)
        target_path = Path(location.target or "")
        if not target_path.exists():
            raise ProviderError(f"WireGuard profile not found: {target_path}")

        wg_quick = shutil.which("wg-quick")
        if wg_quick is None:
            raise ProviderError("The wg-quick command is required for WireGuard profile switching.")

        previous_state = self._read_state()
        previous_path = Path(previous_state.get("config_path", "")) if previous_state.get("config_path") else None
        if previous_path and previous_path.exists():
            self._run_wg_quick(wg_quick, "down", previous_path)

        self._run_wg_quick(wg_quick, "up", target_path)
        self._write_state(
            {
                "config_path": str(target_path),
                "interface_name": target_path.stem,
            }
        )

    def disconnect(self) -> None:
        raw_state = self._read_state()
        config_path = Path(raw_state.get("config_path", "")) if raw_state.get("config_path") else None
        if config_path is None:
            return

        wg_quick = shutil.which("wg-quick")
        if wg_quick is None:
            raise ProviderError("The wg-quick command is required for WireGuard profile switching.")

        self._run_wg_quick(wg_quick, "down", config_path)
        self._write_state({})

    def _run_wg_quick(self, executable: str, action: str, config_path: Path) -> None:
        try:
            result = subprocess.run(
                [executable, action, str(config_path)],
                check=False,
                capture_output=True,
                text=True,
                timeout=self._config.command_timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise ProviderError(f"wg-quick {action} timed out after {self._config.command_timeout_seconds:g}s") from error
        if result.returncode != 0:
            error_text = (result.stderr or result.stdout).strip() or f"wg-quick {action} failed"
            raise ProviderError(error_text)

    def _read_state(self) -> dict[str, str]:
        if not self._state_path.exists():
            return {}
        try:
            raw_state = json.loads(self._state_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {}
        return raw_state if isinstance(raw_state, dict) else {}

    def _write_state(self, payload: dict[str, str]) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def _location_from_config_path(cls, config_path: Path | None) -> Location:
        if config_path is None:
            raise ProviderError("No WireGuard config path was supplied.")

        label_override = cls._read_label_override(config_path)
        if label_override:
            return cls._location_from_label(label_override, config_path)

        stem = config_path.stem.replace("_", "-")
        tokens = [token for token in stem.split("-") if token]
        country_code = tokens[0] if tokens else stem
        country = cls._country_from_code(country_code)
        city_tokens = tokens[1:]
        city = " ".join(token.title() for token in city_tokens) or None
        return Location(country=country, city=city, target=str(config_path))

    @staticmethod
    def _read_label_override(config_path: Path) -> str | None:
        try:
            for line in config_path.read_text(encoding="utf-8").splitlines()[:10]:
                if line.lower().startswith("# label:"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            return None
        return None

    @classmethod
    def _location_from_label(cls, label: str, config_path: Path) -> Location:
        if "/" in label:
            country, city = [part.strip() for part in label.split("/", 1)]
            return Location(country=country, city=city or None, target=str(config_path))
        if " - " in label:
            country, city = [part.strip() for part in label.split(" - ", 1)]
            return Location(country=country, city=city or None, target=str(config_path))
        return Location(country=label.strip(), target=str(config_path))

    @staticmethod
    def _country_from_code(code: str) -> str:
        country_codes = {
            "au": "Australia",
            "ca": "Canada",
            "de": "Germany",
            "fr": "France",
            "jp": "Japan",
            "nl": "Netherlands",
            "sg": "Singapore",
            "uk": "United Kingdom",
            "us": "United States",
        }
        return country_codes.get(code.lower(), code.upper())

    @staticmethod
    def _parse_handshake_summary(output: str) -> str | None:
        match = re.search(r"latest handshake:\s*(?P<value>.+)", output)
        return f"Handshake {match.group('value').strip()}" if match else None

    @staticmethod
    def _parse_transfer_summary(output: str) -> str | None:
        match = re.search(r"transfer:\s*(?P<value>.+)", output)
        return match.group("value").strip() if match else None