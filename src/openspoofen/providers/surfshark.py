from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
from pathlib import Path
from typing import ClassVar

from openspoofen.config import AppConfig
from openspoofen.providers.base import (
    AuthField,
    ConnectionState,
    Location,
    ProviderError,
    ProviderMetadata,
    VpnProvider,
)


class SurfsharkProvider(VpnProvider):
    metadata = ProviderMetadata(
        provider_id="surfshark",
        provider_name="Surfshark",
        auth_fields=(
            AuthField(
                key="service_username",
                label="Service username",
                placeholder="Surfshark manual OpenVPN username",
                secret=False,
                help_text="Use the manual OpenVPN service credentials from your Surfshark account dashboard.",
            ),
            AuthField(
                key="service_password",
                label="Service password",
                placeholder="Surfshark manual OpenVPN password",
            ),
        ),
        setup_steps=(
            "Download Surfshark OpenVPN configuration files and place them under configs/surfshark/.",
            "Save your manual service credentials through the UI once.",
            "Install openvpn on the Pi image used for the appliance.",
        ),
        notes=(
            "Surfshark support is implemented through manual OpenVPN profiles rather than a native Linux CLI.",
            "Profile filenames determine the available country and city choices shown in the UI.",
        ),
    )

    _COUNTRY_CODES: ClassVar[dict[str, str]] = {
        "au": "Australia",
        "ca": "Canada",
        "de": "Germany",
        "fr": "France",
        "gb": "United Kingdom",
        "ie": "Ireland",
        "jp": "Japan",
        "nl": "Netherlands",
        "sg": "Singapore",
        "uk": "United Kingdom",
        "us": "United States",
    }

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._config_dir = config.surfshark_config_dir
        self._runtime_dir = config.runtime_dir
        self._state_file = self._runtime_dir / "surfshark-state.json"
        self._auth_file = self._runtime_dir / "surfshark.auth"
        self._pid_file = self._runtime_dir / "surfshark.pid"
        self._log_file = self._runtime_dir / "surfshark-openvpn.log"

    def list_locations(self) -> list[Location]:
        if not self._config_dir.exists():
            return []

        locations: list[Location] = []
        seen: set[str] = set()
        for config_path in sorted(self._config_dir.glob("*.ovpn")):
            location = self._location_from_path(config_path)
            if location is None:
                continue
            key = location.label.casefold()
            if key in seen:
                continue
            seen.add(key)
            locations.append(location)
        return locations

    def get_state(self) -> ConnectionState:
        raw_state = self._read_state()
        pid = self._read_pid()
        connected = self._pid_is_openvpn(pid)
        location = None
        if raw_state.get("country"):
            location = Location(
                country=str(raw_state["country"]),
                city=str(raw_state["city"]) if raw_state.get("city") else None,
                target=str(raw_state["config_path"]) if raw_state.get("config_path") else None,
            )

        status_summary = raw_state.get("status_summary", "Surfshark manual OpenVPN is ready")
        if raw_state.get("connected") and not connected:
            status_summary = "OpenVPN process is not running"

        return ConnectionState(
            provider_name=self.provider_name,
            authenticated=self._auth_file.exists() and bool(self._auth_file.read_text(encoding="utf-8").strip()),
            connected=connected,
            current_location=location,
            public_ip=None,
            status_summary=str(status_summary),
        )

    def login(self, credentials: dict[str, str]) -> None:
        username = self.require_credential(credentials, "service_username", "a service username")
        password = self.require_credential(credentials, "service_password", "a service password")
        self._runtime_dir.mkdir(parents=True, exist_ok=True)
        self._auth_file.write_text(f"{username}\n{password}\n", encoding="utf-8")

        state = self._read_state()
        state["authenticated"] = True
        state["status_summary"] = "Saved Surfshark manual OpenVPN credentials"
        self._write_state(state)

    def connect(self, country: str, city: str | None = None) -> None:
        if not self._auth_file.exists():
            raise ProviderError("Surfshark manual OpenVPN requires saved service credentials before connect.")

        location = self.resolve_location(country, city)
        config_path = Path(location.target or "")
        if not config_path.exists():
            raise ProviderError(f"Surfshark profile not found: {config_path}")

        executable = shutil.which("openvpn")
        if executable is None:
            raise ProviderError("The openvpn binary is required for Surfshark manual profile support.")

        self.disconnect()
        self._runtime_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = subprocess.run(
                [
                    executable,
                    "--config",
                    str(config_path),
                    "--auth-user-pass",
                    str(self._auth_file),
                    "--writepid",
                    str(self._pid_file),
                    "--log",
                    str(self._log_file),
                    "--daemon",
                    "openspoofen-surfshark",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=self._config.command_timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise ProviderError(f"OpenVPN startup timed out after {self._config.command_timeout_seconds:g}s") from error
        if result.returncode != 0:
            error_text = (result.stderr or result.stdout).strip() or "OpenVPN failed to start"
            raise ProviderError(error_text)

        state = {
            "authenticated": True,
            "connected": True,
            "country": location.country,
            "city": location.city,
            "config_path": str(config_path),
            "status_summary": f"Started OpenVPN profile for {location.label}",
        }
        self._write_state(state)

    def disconnect(self) -> None:
        pid = self._read_pid()
        if pid is not None and self._pid_is_openvpn(pid):
            os.kill(pid, signal.SIGTERM)

        state = self._read_state()
        state["connected"] = False
        state["status_summary"] = "Disconnected manual Surfshark OpenVPN profile"
        self._write_state(state)

    @classmethod
    def _location_from_path(cls, config_path: Path) -> Location | None:
        name = config_path.stem
        name = name.split(".prod", 1)[0]
        name = name.split(".udp", 1)[0]
        name = name.split(".tcp", 1)[0]
        tokens = [token for token in re.split(r"[-_]+", name.lower()) if token]
        if not tokens:
            return None

        country_code = tokens[0]
        country = cls._COUNTRY_CODES.get(country_code, country_code.upper())
        city_tokens = [token for token in tokens[1:] if token not in {"udp", "tcp"}]
        city = " ".join(token.title() for token in city_tokens) or None
        return Location(country=country, city=city, target=str(config_path))

    def _read_state(self) -> dict[str, object]:
        if not self._state_file.exists():
            return {}
        try:
            raw_state = json.loads(self._state_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return {}
        return raw_state if isinstance(raw_state, dict) else {}

    def _write_state(self, state: dict[str, object]) -> None:
        self._runtime_dir.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _read_pid(self) -> int | None:
        if not self._pid_file.exists():
            return None
        try:
            pid = int(self._pid_file.read_text(encoding="utf-8").strip())
        except ValueError:
            return None
        # Never hand os.kill a non-positive PID: 0 probes our own process
        # group and negatives address process groups, not a single process.
        return pid if pid > 0 else None

    @staticmethod
    def _pid_is_running(pid: int | None) -> bool:
        if pid is None:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    @classmethod
    def _pid_is_openvpn(cls, pid: int | None) -> bool:
        """True only when the PID exists *and* is the OpenVPN process we started.

        A stale PID file can outlive the OpenVPN process; if the PID has since
        been recycled by an unrelated process, trusting it would report a false
        "connected" and, worse, disconnect() would SIGTERM an innocent process.
        On Linux the /proc cmdline settles ownership; where /proc is unavailable
        (developer machines) fall back to the plain existence check.
        """
        if not cls._pid_is_running(pid):
            return False
        cmdline_path = Path(f"/proc/{pid}/cmdline")
        try:
            cmdline = cmdline_path.read_bytes().replace(b"\x00", b" ").decode("utf-8", errors="replace")
        except OSError:
            return True
        return "openvpn" in cmdline