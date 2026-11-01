from __future__ import annotations

import re
import shutil
import subprocess

from openspoofen.config import AppConfig


class WifiError(RuntimeError):
    """Raised when Wi-Fi operations cannot be completed."""


class WifiManager:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def status(self, include_networks: bool = False, country: str | None = None) -> dict[str, object]:
        error: str | None = None
        try:
            device = self._device_status()
        except WifiError as wifi_error:
            device = {"state": "unavailable", "connection": "--"}
            error = str(wifi_error)

        secret = self._read_secret_file()
        try:
            current_country = self._wifi_country()
        except WifiError as wifi_error:
            current_country = None
            error = error or str(wifi_error)

        try:
            blocked = self._rfkill_blocked()
        except WifiError as wifi_error:
            blocked = False
            error = error or str(wifi_error)

        networks: list[dict[str, object]] = []

        if include_networks:
            try:
                networks = self.scan_networks(country=country)
                if country:
                    current_country = country.strip().upper()
            except WifiError as wifi_error:
                error = str(wifi_error)

        return {
            "interface": self._config.wifi_interface,
            "device_state": device["state"],
            "device_connection": device["connection"],
            "blocked": blocked,
            "country": current_country,
            "current_ssid": self._current_ssid(networks),
            "saved_ssid": secret.get("RP_WIFI_SSID"),
            "saved_country": secret.get("RP_WIFI_COUNTRY"),
            "connection_name": self._config.wifi_connection_name,
            "networks": networks,
            "error": error,
        }

    def scan_networks(self, country: str | None = None) -> list[dict[str, object]]:
        self._prepare_radio(country=country)
        output = self._run(
            "nmcli",
            "-t",
            "-e",
            "yes",
            "-f",
            "ACTIVE,SSID,SIGNAL,SECURITY",
            "device",
            "wifi",
            "list",
            "ifname",
            self._config.wifi_interface,
            "--rescan",
            "yes",
        )

        saved_ssid = self._read_secret_file().get("RP_WIFI_SSID")
        seen: set[str] = set()
        networks: list[dict[str, object]] = []
        for raw_line in output.splitlines():
            parts = self._split_nmcli_escaped(raw_line)
            if len(parts) < 4:
                continue
            active, ssid, signal, security = parts[:4]
            clean_ssid = ssid.strip()
            if not clean_ssid or clean_ssid in seen:
                continue
            seen.add(clean_ssid)
            networks.append(
                {
                    "ssid": clean_ssid,
                    "signal": int(signal) if signal.isdigit() else 0,
                    "security": security or "Open",
                    "active": active.strip().lower() in {"yes", "*"},
                    "saved": clean_ssid == saved_ssid,
                }
            )

        networks.sort(key=lambda item: (not item["active"], not item["saved"], -int(item["signal"]), item["ssid"]))
        return networks

    def connect(self, ssid: str, password: str, country: str | None = None) -> dict[str, object]:
        clean_ssid = ssid.strip()
        clean_password = password.strip()
        if not clean_ssid:
            raise WifiError("Select a Wi-Fi network first.")
        if len(clean_password) < 8:
            raise WifiError("Wi-Fi passwords must be at least 8 characters long.")

        applied_country = self._prepare_radio(country=country)
        connection_name = self._config.wifi_connection_name

        self._run("nmcli", "connection", "delete", connection_name, allowed_return_codes=(0, 10))
        self._run(
            "nmcli",
            "connection",
            "add",
            "type",
            "wifi",
            "ifname",
            self._config.wifi_interface,
            "con-name",
            connection_name,
            "ssid",
            clean_ssid,
        )
        self._run(
            "nmcli",
            "connection",
            "modify",
            connection_name,
            "connection.autoconnect",
            "yes",
            "802-11-wireless.mode",
            "infrastructure",
            "802-11-wireless.ssid",
            clean_ssid,
            "wifi-sec.key-mgmt",
            "wpa-psk",
            "wifi-sec.psk",
            clean_password,
            "ipv4.method",
            "auto",
            "ipv6.method",
            "ignore",
        )
        self._run("nmcli", "connection", "up", connection_name)

        self._write_secret_file(
            {
                "RP_WIFI_COUNTRY": applied_country,
                "RP_WIFI_SSID": clean_ssid,
                "RP_WIFI_PASSWORD": clean_password,
                "RP_WIFI_CONNECTION_NAME": connection_name,
            }
        )
        return self.status(include_networks=True)

    def _prepare_radio(self, country: str | None = None) -> str:
        current_country = self._wifi_country()
        desired_country = (country or current_country or "").strip().upper()
        if not desired_country:
            raise WifiError("Set a 2-letter Wi-Fi country code before scanning networks.")
        if not re.fullmatch(r"[A-Za-z]{2}", desired_country):
            raise WifiError("Wi-Fi country codes must be 2 letters, for example US or GB.")

        self._run("rfkill", "unblock", "wifi")
        self._run("nmcli", "radio", "wifi", "on")

        raspi_config = shutil.which("raspi-config")
        if raspi_config is not None:
            self._run(raspi_config, "nonint", "do_wifi_country", desired_country, allowed_return_codes=(0, 1))

        iw = shutil.which("iw")
        if iw is not None:
            self._run(iw, "reg", "set", desired_country, allowed_return_codes=(0, 156))

        return desired_country

    def _device_status(self) -> dict[str, str]:
        output = self._run("nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status")
        for raw_line in output.splitlines():
            parts = self._split_nmcli_escaped(raw_line)
            if len(parts) < 4:
                continue
            device, device_type, state, connection = parts[:4]
            if device == self._config.wifi_interface and device_type == "wifi":
                return {"state": state or "unknown", "connection": connection or "--"}
        return {"state": "unknown", "connection": "--"}

    def _current_ssid(self, networks: list[dict[str, object]]) -> str | None:
        for network in networks:
            if network.get("active"):
                return str(network.get("ssid"))
        return None

    def _rfkill_blocked(self) -> bool:
        output = self._run("rfkill", "list")
        if "Wireless LAN" not in output:
            return False
        wireless_section = output.split("Wireless LAN", 1)[1]
        return "Soft blocked: yes" in wireless_section or "Hard blocked: yes" in wireless_section

    def _wifi_country(self) -> str | None:
        iw = shutil.which("iw")
        if iw is None:
            return None

        output = self._run(iw, "reg", "get")
        match = re.search(r"global\s+country\s+(?P<country>[A-Z0-9]{2})", output, re.IGNORECASE)
        if not match:
            return None
        country = match.group("country").upper()
        return None if country in {"00", "99"} else country

    def _run(self, *args: str, allowed_return_codes: tuple[int, ...] = (0,)) -> str:
        executable = shutil.which(args[0])
        if executable is None:
            raise WifiError(f"{args[0]} is not available on this platform.")
        command = [executable or args[0], *args[1:]]
        try:
            result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=20)
        except subprocess.TimeoutExpired as error:
            raise WifiError("Wi-Fi command timed out.") from error

        text = (result.stdout or result.stderr or "").strip()
        if result.returncode not in allowed_return_codes:
            raise WifiError(text or f"Wi-Fi command failed: {' '.join(args)}")
        return text

    def _read_secret_file(self) -> dict[str, str]:
        path = self._config.wifi_secret_path
        if not path.exists():
            return {}

        values: dict[str, str] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key] = value
        return values

    def _write_secret_file(self, values: dict[str, str]) -> None:
        path = self._config.wifi_secret_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n", encoding="utf-8")
        try:
            path.chmod(0o600)
        except OSError:
            pass

    @staticmethod
    def _split_nmcli_escaped(value: str) -> list[str]:
        parts: list[str] = []
        current: list[str] = []
        escape = False
        for char in value:
            if escape:
                current.append(char)
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if char == ":":
                parts.append("".join(current))
                current = []
                continue
            current.append(char)
        parts.append("".join(current))
        return parts