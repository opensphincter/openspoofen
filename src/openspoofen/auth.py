from __future__ import annotations

import hmac
import ipaddress
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from secrets import token_urlsafe

from flask import Request
from itsdangerous import BadSignature, URLSafeSerializer
from werkzeug.security import check_password_hash, generate_password_hash


@dataclass(slots=True)
class AuthState:
    password_hash: str | None
    pairing_token: str

    @property
    def setup_complete(self) -> bool:
        return bool(self.password_hash)


class LanAuthManager:
    cookie_name = "rp_pairing"

    def __init__(self, state_path: Path, secret_key: str) -> None:
        self._state_path = state_path
        self._serializer = URLSafeSerializer(secret_key, salt="openspoofen-pairing")

    def load_state(self) -> AuthState:
        if not self._state_path.exists():
            return self._bootstrap_state()

        try:
            raw_state = json.loads(self._state_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            # A corrupt auth state file must not wedge every request with a 500.
            # Recover into first-boot setup mode; the owner re-creates the LAN
            # password from the setup page (LAN presence is the trust anchor).
            logging.getLogger(__name__).warning("Auth state at %s is unreadable (%s); resetting to setup mode.", self._state_path, error)
            return self._bootstrap_state()
        if not isinstance(raw_state, dict):
            return self._bootstrap_state()
        pairing_token = str(raw_state.get("pairing_token") or token_urlsafe(8))
        password_hash = raw_state.get("password_hash")

        return AuthState(
            password_hash=str(password_hash) if isinstance(password_hash, str) and password_hash else None,
            pairing_token=pairing_token,
        )

    def save_state(self, state: AuthState) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "password_hash": state.password_hash,
            "pairing_token": state.pairing_token,
        }
        self._state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def configure(self, password: str, pairing_token: str | None = None) -> AuthState:
        clean_password = password.strip()
        if len(clean_password) < 8:
            raise ValueError("Admin password must be at least 8 characters long.")

        token = (pairing_token or "").strip() or token_urlsafe(8)
        state = AuthState(password_hash=generate_password_hash(clean_password), pairing_token=token)
        self.save_state(state)
        return state

    def verify_password(self, state: AuthState, password: str) -> bool:
        if not state.password_hash:
            return False
        return check_password_hash(state.password_hash, password)

    def pairing_cookie_value(self, state: AuthState) -> str:
        return self._serializer.dumps({"pairing_token": state.pairing_token})

    def request_is_paired(self, state: AuthState, request: Request) -> bool:
        cookie_value = request.cookies.get(self.cookie_name)
        if not cookie_value:
            return False

        try:
            payload = self._serializer.loads(cookie_value)
        except BadSignature:
            return False

        return payload.get("pairing_token") == state.pairing_token

    def pairing_token_matches(self, state: AuthState, candidate: str) -> bool:
        return hmac.compare_digest(state.pairing_token, candidate.strip())

    def _bootstrap_state(self) -> AuthState:
        state = AuthState(password_hash=None, pairing_token=token_urlsafe(8))
        self.save_state(state)
        return state


def is_private_lan_address(remote_addr: str | None) -> bool:
    if not remote_addr:
        return False

    candidate = remote_addr.split("%", 1)[0]
    try:
        ip_address = ipaddress.ip_address(candidate)
    except ValueError:
        return False

    return ip_address.is_private or ip_address.is_loopback or ip_address.is_link_local