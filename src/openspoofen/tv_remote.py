from __future__ import annotations

import base64
import ipaddress
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import ClassVar

from openspoofen.config import AppConfig

try:
    from samsungtvws import SamsungTVWS
except ImportError:  # pragma: no cover - exercised through status() when dependency is absent.
    SamsungTVWS = None


class TvRemoteError(RuntimeError):
    pass


@dataclass(slots=True)
class TvRemoteState:
    vendor: str = "samsung"
    host: str | None = None
    display_name: str = "OpenSpoofen Remote"
    port: int | None = None

    @property
    def configured(self) -> bool:
        return bool(self.host)


class TvRemoteManager:
    FRIENDLY_KEYS: ClassVar[dict[str, str]] = {
        "up": "KEY_UP",
        "down": "KEY_DOWN",
        "left": "KEY_LEFT",
        "right": "KEY_RIGHT",
        "ok": "KEY_ENTER",
        "enter": "KEY_ENTER",
        "home": "KEY_HOME",
        "back": "KEY_RETURN",
        "exit": "KEY_EXIT",
        "mute": "KEY_MUTE",
        "volume_up": "KEY_VOLUP",
        "volume_down": "KEY_VOLDOWN",
        "channel_up": "KEY_CHUP",
        "channel_down": "KEY_CHDOWN",
        "play_pause": "KEY_PLAY",
        "rewind": "KEY_REWIND",
        "fast_forward": "KEY_FF",
        "source": "KEY_SOURCE",
        "power": "KEY_POWER",
    }

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def load_state(self) -> TvRemoteState:
        default_state = TvRemoteState(vendor=self._config.tv_remote_vendor, display_name=self._config.tv_remote_name)
        if not self._config.tv_remote_state_path.exists():
            return default_state

        try:
            raw_state = json.loads(self._config.tv_remote_state_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return default_state
        if not isinstance(raw_state, dict):
            return default_state

        port: int | None = None
        try:
            candidate_port = int(raw_state["port"]) if raw_state.get("port") else None
        except (TypeError, ValueError):
            candidate_port = None
        if candidate_port is not None and 1 <= candidate_port <= 65535:
            port = candidate_port

        return TvRemoteState(
            vendor=str(raw_state.get("vendor") or self._config.tv_remote_vendor),
            host=str(raw_state.get("host") or "").strip() or None,
            display_name=str(raw_state.get("display_name") or self._config.tv_remote_name),
            port=port,
        )

    def save_state(self, state: TvRemoteState) -> None:
        self._config.tv_remote_state_path.parent.mkdir(parents=True, exist_ok=True)
        self._config.tv_remote_state_path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")

    def status(self, latest_lease: dict[str, str] | None = None, last_error: str | None = None) -> dict[str, object]:
        state = self.load_state()
        candidate_host = None
        if latest_lease and latest_lease.get("address"):
            candidate_host = latest_lease["address"]

        dependency_available = SamsungTVWS is not None
        token_cached = self._token_path(state).exists()
        effective_host = state.host or candidate_host
        auto_detected = bool(candidate_host and not state.host)

        if not dependency_available:
            summary = "Samsung remote support is not installed on this device."
        elif effective_host and token_cached:
            summary = "Ready to send TV remote keys from this phone."
        elif auto_detected:
            summary = f"TV detected on {candidate_host}. Remote keys will use that address automatically."
        elif effective_host:
            summary = "Configured. The TV may prompt once to allow this remote."
        else:
            summary = "Waiting for a TV lease before remote control can be configured."

        return {
            "vendor": state.vendor,
            "configured": state.configured,
            "available": dependency_available,
            "ready": dependency_available and bool(effective_host),
            "auto_detected": auto_detected,
            "host": state.host,
            "effective_host": effective_host,
            "display_name": state.display_name,
            "port": state.port,
            "token_cached": token_cached,
            "candidate_host": candidate_host,
            "candidate_name": latest_lease.get("hostname") if latest_lease else None,
            "status_summary": summary,
            "last_error": last_error,
        }

    def configure(
        self,
        host: str,
        display_name: str | None = None,
        vendor: str | None = None,
        port: int | None = None,
        latest_lease: dict[str, str] | None = None,
    ) -> dict[str, object]:
        clean_host = host.strip()
        if not clean_host:
            raise TvRemoteError("A TV IP address or hostname is required.")

        try:
            ipaddress.ip_address(clean_host)
        except ValueError:
            if "." not in clean_host and ":" not in clean_host:
                raise TvRemoteError("Enter a valid TV IP address or hostname.") from None

        state = self.load_state()
        state.host = clean_host
        state.display_name = (display_name or state.display_name or self._config.tv_remote_name).strip() or self._config.tv_remote_name
        state.vendor = (vendor or state.vendor or self._config.tv_remote_vendor).strip().lower() or "samsung"
        state.port = port if port else None
        self.save_state(state)
        return self.status(latest_lease=latest_lease)

    def send_key(self, key: str, latest_lease: dict[str, str] | None = None) -> dict[str, object]:
        state = self._resolve_active_state(latest_lease)

        resolved_key = self._resolve_key(key)
        last_error = "Unable to contact the TV remote interface."
        for port in self._ports_to_try(state):
            client = None
            try:
                client = self._build_client(state, port)
                client.open()
                client.send_key(resolved_key, key_press_delay=0.12)
                client.close()
                self._remember_port(state, port)
                return self.status(latest_lease=latest_lease)
            except Exception as error:  # pragma: no cover - depends on live TV responses.  # noqa: BLE001
                last_error = str(error) or last_error
                try:
                    if client is not None:
                        client.close()
                except Exception:  # noqa: BLE001, S110 - best-effort client close
                    pass

        raise TvRemoteError(last_error)

    def send_text(self, text: str, latest_lease: dict[str, str] | None = None, submit: bool = False) -> dict[str, object]:
        clean_text = str(text)
        if not clean_text:
            raise TvRemoteError("Enter text before sending it to the TV.")

        state = self._resolve_active_state(latest_lease)
        encoded_text = base64.b64encode(clean_text.encode("utf-8")).decode("ascii")
        last_error = "Unable to send text to the TV input field."

        for port in self._ports_to_try(state):
            client = None
            try:
                client = self._build_client(state, port)
                client.open()
                client.send_command(
                    {
                        "method": "ms.channel.emit",
                        "params": {
                            "event": "custom.remote.textReceived",
                            "to": "broadcast",
                        },
                    },
                    key_press_delay=0.04,
                )
                client.send_command(
                    {
                        "method": "ms.remote.control",
                        "params": {
                            "Cmd": encoded_text,
                            "DataOfCmd": "base64",
                            "TypeOfRemote": "SendInputString",
                        },
                    },
                    key_press_delay=0.04,
                )
                if submit:
                    client.send_command(
                        {
                            "method": "ms.remote.control",
                            "params": {
                                "TypeOfRemote": "SendInputEnd",
                            },
                        },
                        key_press_delay=0.04,
                    )
                client.close()
                self._remember_port(state, port)
                return self.status(latest_lease=latest_lease)
            except Exception as error:  # pragma: no cover - depends on live TV responses.  # noqa: BLE001
                last_error = str(error) or last_error
                try:
                    if client is not None:
                        client.close()
                except Exception:  # noqa: BLE001, S110 - best-effort client close
                    pass

        raise TvRemoteError(last_error)

    def _resolve_key(self, key: str) -> str:
        clean_key = key.strip()
        if not clean_key:
            raise TvRemoteError("A remote key is required.")
        if clean_key.startswith("KEY_"):
            return clean_key
        friendly = self.FRIENDLY_KEYS.get(clean_key.lower())
        if not friendly:
            raise TvRemoteError(f"Unsupported remote key: {clean_key}")
        return friendly

    def _ports_to_try(self, state: TvRemoteState) -> tuple[int, ...]:
        if state.port:
            return (state.port,)
        return (8002, 8001)

    def _resolve_active_state(self, latest_lease: dict[str, str] | None) -> TvRemoteState:
        state = self.load_state()
        if not state.host and latest_lease and latest_lease.get("address"):
            state.host = str(latest_lease["address"]).strip() or None
            if state.host:
                self.save_state(state)
        if not state.configured or not state.host:
            raise TvRemoteError("Configure the TV IP first before using the remote controls.")
        if state.vendor != "samsung":
            raise TvRemoteError(f"Unsupported TV remote vendor: {state.vendor}")
        if SamsungTVWS is None:
            raise TvRemoteError("Samsung remote support is not installed on this device.")
        return state

    def _build_client(self, state: TvRemoteState, port: int):
        return SamsungTVWS(
            host=state.host,
            port=port,
            timeout=4,
            key_press_delay=0.18,
            name=state.display_name,
            token_file=str(self._token_path(state)),
        )

    def _remember_port(self, state: TvRemoteState, port: int) -> None:
        if state.port == port:
            return
        state.port = port
        self.save_state(state)

    def _token_path(self, state: TvRemoteState) -> Path:
        safe_vendor = state.vendor.replace("/", "-")
        return self._config.runtime_dir / f"tv-remote-{safe_vendor}.token"