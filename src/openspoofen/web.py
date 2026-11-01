from __future__ import annotations

import logging
import re
import shutil
import subprocess
import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import orjson
from flask import (
    Flask,
    abort,
    flash,
    g,
    get_flashed_messages,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask.json.provider import JSONProvider
from flask_compress import Compress

from openspoofen.auth import LanAuthManager, is_private_lan_address
from openspoofen.config import AppConfig, load_config
from openspoofen.providers.base import (
    ConnectionState,
    Location,
    ProviderError,
    VpnProvider,
    is_placeholder_location_name,
)
from openspoofen.providers.registry import available_provider_metadata, create_provider
from openspoofen.tv_remote import TvRemoteError, TvRemoteManager
from openspoofen.wifi import WifiError, WifiManager

SERVICE_LABELS = {
    "openspoofen-web.service": "Web UI",
    "openspoofen-tv-lan.service": "TV LAN",
    "openspoofen-wifi-uplink.service": "Wi-Fi uplink",
    "dnsmasq.service": "DNS and DHCP",
}

PROVIDER_MARKS = {
    "NordVPN": "NV",
    "WireGuard Profiles": "WG",
    "ExpressVPN": "EX",
    "Proton VPN": "PV",
    "Mock Provider": "MK",
    "Mullvad": "MU",
    "Surfshark": "SS",
}


def _provider_mark_text(provider_name: str) -> str:
    explicit = PROVIDER_MARKS.get(provider_name)
    if explicit:
        return explicit

    words = [part for part in provider_name.replace("/", " ").split() if part]
    if not words:
        return "OS"
    if len(words) == 1:
        return words[0][0].upper()
    return "".join(word[0] for word in words[:2]).upper()


class _OrjsonProvider(JSONProvider):
    def dumps(self, obj, **kwargs) -> str:
        return orjson.dumps(obj, default=str).decode()

    def loads(self, s, **kwargs):
        return orjson.loads(s)


def _safe_next_path(candidate: str | None) -> str:
    """Only allow same-site paths as post-login redirect targets.

    A ``next`` value like ``https://evil.example`` or ``//evil.example`` would
    turn the login form into an open redirect, so anything that is not a
    plain absolute path falls back to the dashboard.
    """
    if candidate and candidate.startswith("/") and not candidate.startswith("//") and "\\" not in candidate:
        return candidate
    return "/"


def _clean_location_value(value: object) -> str:
    """Normalize a user-supplied country/city before it reaches a provider CLI.

    Values are passed as argv to provider commands, so reject anything that
    could be mistaken for a CLI flag or smuggle control characters.
    """
    cleaned = str(value or "").strip()
    if cleaned.startswith("-") or any(ord(char) < 32 or ord(char) == 127 for char in cleaned):
        return ""
    return cleaned


def _frontend_asset_version(static_folder: str | None) -> str:
    if not static_folder:
        return "0"

    static_root = Path(static_folder)
    versions: list[str] = []
    for filename in ("dashboard-app.css", "dashboard-app.js", "service-worker.js"):
        asset_path = static_root / filename
        if asset_path.exists():
            versions.append(str(int(asset_path.stat().st_mtime)))

    return max(versions, default="0")


def create_app(config: AppConfig | None = None) -> Flask:
    app_config = config or load_config()

    app = Flask(__name__, template_folder="templates")
    app.json = _OrjsonProvider(app)
    Compress(app)
    app.config["SECRET_KEY"] = app_config.secret_key
    app.config["RP_CONFIG"] = app_config
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = app_config.enable_https
    app.permanent_session_lifetime = timedelta(days=app_config.session_persist_days)

    auth_manager = LanAuthManager(app_config.auth_state_path, app_config.secret_key)
    wifi_manager = WifiManager(app_config)
    tv_remote_manager = TvRemoteManager(app_config)
    app.extensions["rp_wifi_manager"] = wifi_manager
    app.extensions["rp_tv_remote_manager"] = tv_remote_manager
    provider_metadata = tuple(available_provider_metadata())
    provider_catalog = {metadata.provider_id: metadata for metadata in provider_metadata}
    provider_keys = frozenset(provider_catalog)
    public_endpoints = {"setup", "complete_setup", "login", "do_login", "healthz", "manifest", "service_worker", "static"}
    location_cache: dict[str, tuple[float, list[Location]]] = {}
    location_cache_lock = threading.Lock()
    network_cache: dict[str, float | dict[str, object] | None] = {"expires_at": 0.0, "value": None}
    network_cache_lock = threading.Lock()

    def _provider_key() -> str:
        cached = getattr(g, "provider_key", None)
        if cached is not None:
            return cached

        candidate = request.values.get("provider") or session.get("active_provider") or app_config.default_provider
        if candidate not in provider_keys:
            candidate = app_config.default_provider

        if session.get("active_provider") != candidate:
            session["active_provider"] = candidate
        g.provider_key = candidate
        return candidate

    def _provider() -> VpnProvider:
        cached = getattr(g, "provider", None)
        if cached is not None:
            return cached
        provider = create_provider(_provider_key(), app_config)
        g.provider = provider
        return provider

    def _invalidate_provider_cache(provider_key: str) -> None:
        with location_cache_lock:
            location_cache.pop(provider_key, None)

    def _cached_locations(provider: VpnProvider, provider_key: str) -> list[Location]:
        now = time.monotonic()
        with location_cache_lock:
            cached = location_cache.get(provider_key)
            if cached is not None and cached[0] > now:
                return cached[1]

        locations = [location for location in provider.list_locations() if not is_placeholder_location_name(location.country)]
        with location_cache_lock:
            location_cache[provider_key] = (now + app_config.location_cache_ttl_seconds, locations)
        return locations

    def _cached_network_snapshot() -> dict[str, object]:
        now = time.monotonic()
        with network_cache_lock:
            expires_at = float(network_cache["expires_at"])
            value = network_cache["value"]
            if isinstance(value, dict) and expires_at > now:
                return value

        snapshot = _probe_network_health(app_config)
        with network_cache_lock:
            network_cache["expires_at"] = now + app_config.network_probe_cache_ttl_seconds
            network_cache["value"] = snapshot
        return snapshot

    def _redirect_dashboard() -> str:
        return url_for("dashboard", provider=_provider_key())

    def _error_state(provider: VpnProvider, error: ProviderError) -> ConnectionState:
        return ConnectionState(
            provider_name=provider.provider_name,
            authenticated=False,
            connected=False,
            current_location=None,
            public_ip=None,
            status_summary=str(error),
        )

    def _serialize_location(location: Location) -> dict[str, str | None]:
        return {
            "country": location.country,
            "city": location.city,
            "label": location.label,
            "target": location.target,
        }

    def _serialize_state(state: ConnectionState) -> dict[str, object]:
        return {
            "provider_name": state.provider_name,
            "authenticated": state.authenticated,
            "connected": state.connected,
            "current_location": _serialize_location(state.current_location) if state.current_location else None,
            "public_ip": state.public_ip,
            "status_summary": state.status_summary,
        }

    def _serialize_provider_metadata(provider_key: str, *, include_auth_fields: bool = False) -> dict[str, object]:
        metadata = provider_catalog[provider_key]
        return {
            "provider_id": metadata.provider_id,
            "provider_name": metadata.provider_name,
            "supports_city_selection": metadata.supports_city_selection,
            "setup_steps": list(metadata.setup_steps),
            "notes": list(metadata.notes),
            "auth_fields": (
                [
                    {
                        "key": field.key,
                        "label": field.label,
                        "placeholder": field.placeholder,
                        "secret": field.secret,
                        "help_text": field.help_text,
                    }
                    for field in metadata.auth_fields
                ]
                if include_auth_fields
                else []
            ),
        }

    def _group_locations(locations: list[Location]) -> dict[str, list[str]]:
        grouped_locations: dict[str, list[str]] = {}
        for location in locations:
            grouped_locations.setdefault(location.country, [])
            if location.city:
                grouped_locations[location.country].append(location.city)
        return grouped_locations

    def _collect_dashboard_snapshot() -> dict[str, object]:
        provider_key = _provider_key()
        provider = _provider()
        try:
            state = provider.get_state()
        except ProviderError as error:
            state = _error_state(provider, error)

        try:
            locations = _cached_locations(provider, provider_key)
        except ProviderError:
            locations = []

        network_snapshot = _cached_network_snapshot()

        return {
            "provider": provider,
            "provider_key": provider_key,
            "provider_metadata": provider_catalog[provider_key],
            "state": state,
            "show_provider_login": bool(provider.metadata.auth_fields) and not state.authenticated,
            "grouped_locations": _group_locations(locations),
            "locations": locations,
            "network": network_snapshot,
            "tv_remote": tv_remote_manager.status(latest_lease=_latest_lease(network_snapshot)),
            "checked_at": datetime.now(UTC).isoformat(),
        }

    def _dashboard_payload(snapshot: dict[str, object], message: str | None = None) -> dict[str, object]:
        provider_key = str(snapshot["provider_key"])
        payload = {
            "provider": provider_key,
            "provider_name": snapshot["provider_metadata"].provider_name,
            "provider_metadata": _serialize_provider_metadata(provider_key, include_auth_fields=bool(snapshot["show_provider_login"])),
            "state": _serialize_state(snapshot["state"]),
            "regions": [_serialize_location(location) for location in snapshot["locations"]],
            "grouped_locations": snapshot["grouped_locations"],
            "network": snapshot["network"],
            "tv_remote": snapshot["tv_remote"],
            "checked_at": snapshot["checked_at"],
            "show_provider_login": snapshot["show_provider_login"],
            "provider_auth_summary": (
                f"{snapshot['provider_metadata'].provider_name} is already authenticated on this device."
                if snapshot["state"].authenticated
                else None
            ),
        }
        if message:
            payload["message"] = message
        return payload

    def _latest_lease(network_snapshot: dict[str, object]) -> dict[str, str] | None:
        candidate = network_snapshot.get("latest_lease")
        return candidate if isinstance(candidate, dict) else None

    def _persist_nordvpn_token(token: str) -> bool:
        clean_token = token.strip()
        if not clean_token:
            return False

        app_config.nordvpn_secret_path.parent.mkdir(parents=True, exist_ok=True)
        app_config.nordvpn_secret_path.write_text(f"NORDVPN_ACCESS_TOKEN={clean_token}\n", encoding="utf-8")
        try:
            app_config.nordvpn_secret_path.chmod(0o600)
        except OSError:
            pass
        return True

    def _restart_nordvpn_bootstrap() -> None:
        executable = shutil.which("systemctl")
        if executable is None:
            return
        try:
            subprocess.run(
                [executable, "restart", "openspoofen-nordvpn-bootstrap.service"],
                check=False,
                capture_output=True,
                text=True,
                timeout=8,
            )
        except subprocess.TimeoutExpired:
            return

    def _authenticated_response(response, auth_state, persist_pairing: bool):
        session.permanent = True
        session["authenticated"] = True
        session["active_provider"] = _provider_key()
        if persist_pairing:
            response.set_cookie(
                auth_manager.cookie_name,
                auth_manager.pairing_cookie_value(auth_state),
                httponly=True,
                samesite="Lax",
                secure=app_config.enable_https,
                max_age=60 * 60 * 24 * 30,
            )
        return response

    @app.before_request
    def enforce_lan_access_and_authentication():
        if app_config.lan_only and not is_private_lan_address(request.remote_addr):
            abort(403)

        auth_state = auth_manager.load_state()
        request.auth_state = auth_state  # type: ignore[attr-defined]

        if not auth_state.setup_complete:
            if request.endpoint not in {"setup", "complete_setup", "healthz", "manifest", "service_worker", "static"}:
                return redirect(url_for("setup"))
            return None

        if request.endpoint in {"setup", "complete_setup"}:
            return redirect(_redirect_dashboard())

        if request.endpoint in public_endpoints:
            return None

        if session.get("authenticated"):
            return None

        if request.endpoint and request.endpoint.startswith("api_"):
            return jsonify({"error": "Authentication required"}), 401

        return redirect(url_for("login", next=request.full_path if request.query_string else request.path))

    @app.get("/healthz")
    def healthz():
        return jsonify({"ok": True})

    @app.after_request
    def cache_static(response):
        # Hashed chunks and ?v= asset URLs change whenever content does, so cache them hard.
        if (
            request.endpoint == "static"
            and response.status_code == 200
            and (request.args.get("v") or re.search(r"-[A-Za-z0-9_-]{8}\.(js|css)$", request.path))
        ):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response

    @app.get("/manifest.webmanifest")
    def manifest():
        return send_from_directory(app.static_folder or "static", "manifest.webmanifest")

    @app.get("/sw.js")
    def service_worker():
        response = make_response(send_from_directory(app.static_folder or "static", "service-worker.js"))
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def dashboard() -> str:
        auth_state = request.auth_state  # type: ignore[attr-defined]
        snapshot = _collect_dashboard_snapshot()
        payload = _dashboard_payload(snapshot)
        payload["available_providers"] = [_serialize_provider_metadata(metadata.provider_id) for metadata in provider_metadata]
        payload["provider_mark"] = _provider_mark_text(snapshot["provider_metadata"].provider_name)
        payload["access"] = {
            "paired_browser": auth_manager.request_is_paired(auth_state, request),
            "pairing_token": auth_state.pairing_token,
            "require_pairing_token": app_config.require_pairing_token,
            "device_origin": request.host_url.rstrip("/"),
            "mdns_origin": f"{'https' if app_config.enable_https else 'http'}://{app_config.device_hostname}.local:{app_config.port}",
            "session_persist_days": app_config.session_persist_days,
        }
        payload["urls"] = {
            "dashboard": url_for("dashboard", provider=snapshot["provider_key"]),
            "status": url_for("api_status", provider=snapshot["provider_key"]),
            "provider_select": url_for("api_select_provider"),
            "region_switch": url_for("api_switch_region"),
            "disconnect": url_for("api_disconnect"),
            "wifi_status": url_for("api_wifi_status"),
            "wifi_scan": url_for("api_wifi_scan"),
            "wifi_connect": url_for("api_wifi_connect"),
            "appliance_specs": url_for("api_appliance_specs"),
            "appliance_logs": url_for("api_appliance_logs"),
            "remote_status": url_for("api_remote_status"),
            "remote_config": url_for("api_remote_configure"),
            "remote_key": url_for("api_remote_key"),
            "remote_text": url_for("api_remote_text"),
            "provider_login": url_for("provider_login"),
            "logout": url_for("logout"),
        }
        payload["messages"] = [
            {"category": category, "message": message}
            for category, message in get_flashed_messages(with_categories=True)
        ]
        response = make_response(
            render_template(
                "dashboard.html",
                dashboard_bootstrap=payload,
                frontend_asset_version=_frontend_asset_version(app.static_folder),
            )
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/setup")
    def setup() -> str:
        auth_state = request.auth_state  # type: ignore[attr-defined]
        return render_template(
            "setup.html",
            pairing_token=auth_state.pairing_token,
            require_pairing_token=app_config.require_pairing_token,
            app_config=app_config,
        )

    @app.post("/setup")
    def complete_setup():
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        pairing_token = request.form.get("pairing_token", "")

        if password != password_confirm:
            flash("Passwords did not match.", "error")
            return redirect(url_for("setup"))

        try:
            auth_state = auth_manager.configure(password=password, pairing_token=pairing_token)
        except ValueError as error:
            flash(str(error), "error")
            return redirect(url_for("setup"))

        flash("LAN admin password configured.", "success")
        response = make_response(redirect(_redirect_dashboard()))
        return _authenticated_response(response, auth_state, persist_pairing=app_config.require_pairing_token)

    @app.get("/login")
    def login() -> str:
        auth_state = request.auth_state  # type: ignore[attr-defined]
        return render_template(
            "login.html",
            paired_browser=auth_manager.request_is_paired(auth_state, request),
            require_pairing_token=app_config.require_pairing_token,
            next_path=_safe_next_path(request.args.get("next")) if request.args.get("next") else url_for("dashboard"),
        )

    @app.post("/login")
    def do_login():
        auth_state = request.auth_state  # type: ignore[attr-defined]
        password = request.form.get("password", "")
        pairing_token = request.form.get("pairing_token", "")
        next_path = _safe_next_path(request.form.get("next")) if request.form.get("next") else url_for("dashboard")

        if not auth_manager.verify_password(auth_state, password):
            flash("Incorrect admin password.", "error")
            return redirect(url_for("login", next=next_path))

        paired_browser = auth_manager.request_is_paired(auth_state, request)
        persist_pairing = False
        if app_config.require_pairing_token and not paired_browser:
            if not auth_manager.pairing_token_matches(auth_state, pairing_token):
                flash("A valid pairing token is required for a new browser.", "error")
                return redirect(url_for("login", next=next_path))
            persist_pairing = True

        flash("Signed in to the LAN control surface.", "success")
        response = make_response(redirect(next_path))
        return _authenticated_response(response, auth_state, persist_pairing=persist_pairing)

    @app.post("/logout")
    def logout():
        session.clear()
        flash("Signed out.", "success")
        return redirect(url_for("login"))

    @app.post("/connect")
    def connect():
        provider = _provider()
        country = _clean_location_value(request.form.get("country", ""))
        city = _clean_location_value(request.form.get("city", "")) or None
        if not country:
            flash("Choose a country before connecting.", "error")
            return redirect(_redirect_dashboard())
        try:
            provider.connect(country=country, city=city)
        except ProviderError as error:
            flash(str(error), "error")
        else:
            _invalidate_provider_cache(provider.provider_id)
            flash(f"Switching active region to {country}{f' / {city}' if city else ''}.", "success")
        return redirect(_redirect_dashboard())

    @app.post("/disconnect")
    def disconnect():
        provider = _provider()
        try:
            provider.disconnect()
        except ProviderError as error:
            flash(str(error), "error")
        else:
            _invalidate_provider_cache(provider.provider_id)
            flash(f"Disconnected {provider.provider_name}.", "success")
        return redirect(_redirect_dashboard())

    @app.post("/provider/login")
    def provider_login():
        provider = _provider()
        credentials = {field.key: request.form.get(field.key, "") for field in provider.metadata.auth_fields}
        try:
            provider.login(credentials)
        except ProviderError as error:
            flash(str(error), "error")
        else:
            if provider.provider_id == "nordvpn" and _persist_nordvpn_token(credentials.get("token", "")):
                _restart_nordvpn_bootstrap()
                flash("Saved the NordVPN token for future boots so terminal re-auth is no longer required.", "success")
            _invalidate_provider_cache(provider.provider_id)
            flash(f"Authenticated with {provider.provider_name}.", "success")
        return redirect(_redirect_dashboard())

    @app.get("/api/status")
    def api_status():
        snapshot = _collect_dashboard_snapshot()
        return jsonify(_dashboard_payload(snapshot))

    @app.get("/api/regions")
    def api_regions():
        snapshot = _collect_dashboard_snapshot()
        return jsonify(
            {
                "provider": snapshot["provider_key"],
                "regions": [_serialize_location(location) for location in snapshot["locations"]],
            }
        )

    @app.post("/api/provider/select")
    def api_select_provider():
        payload = request.get_json(silent=True) or request.form
        provider_key = str(payload.get("provider", "")).strip().lower()
        if provider_key not in provider_keys:
            return jsonify({"error": f"Unsupported provider: {provider_key}"}), 400

        session["active_provider"] = provider_key
        g.provider_key = provider_key
        if hasattr(g, "provider"):
            delattr(g, "provider")
        snapshot = _collect_dashboard_snapshot()
        return jsonify(_dashboard_payload(snapshot, message=f"Switched control backend to {snapshot['provider_metadata'].provider_name}."))

    @app.post("/api/region/switch")
    def api_switch_region():
        provider = _provider()
        payload = request.get_json(silent=True) or request.form
        country = _clean_location_value(payload.get("country", ""))
        if not country:
            return jsonify({"error": "A valid country is required to switch regions."}), 400
        city = payload.get("city")
        city_value = _clean_location_value(city) if city else None

        def _connect() -> None:
            try:
                provider.connect(country=country, city=city_value)
            except ProviderError as error:
                logging.getLogger(__name__).warning("Region switch failed: %s", error)

        threading.Thread(target=_connect, name="region-switch", daemon=True).start()

        snapshot = _collect_dashboard_snapshot()
        return jsonify(_dashboard_payload(snapshot, message=f"Switching active region to {country}{f' / {city_value}' if city_value else ''}."))

    @app.post("/api/disconnect")
    def api_disconnect():
        provider = _provider()
        try:
            provider.disconnect()
        except ProviderError as error:
            return jsonify({"error": str(error)}), 400

        snapshot = _collect_dashboard_snapshot()
        return jsonify(_dashboard_payload(snapshot, message=f"Disconnected {provider.provider_name}."))

    @app.get("/api/wifi/status")
    def api_wifi_status():
        include_networks = request.args.get("include_networks", "false").strip().lower() in {"1", "true", "yes"}
        country = request.args.get("country") or None
        try:
            return jsonify({"wifi": wifi_manager.status(include_networks=include_networks, country=country)})
        except WifiError as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/wifi/scan")
    def api_wifi_scan():
        payload = request.get_json(silent=True) or request.form
        country = str(payload.get("country", "")).strip() or None
        try:
            return jsonify({"wifi": wifi_manager.status(include_networks=True, country=country)})
        except WifiError as error:
            return jsonify({"error": str(error)}), 400

    @app.post("/api/wifi/connect")
    def api_wifi_connect():
        payload = request.get_json(silent=True) or request.form
        ssid = str(payload.get("ssid", ""))
        password = str(payload.get("password", ""))
        country = str(payload.get("country", "")).strip() or None
        try:
            snapshot = wifi_manager.connect(ssid=ssid, password=password, country=country)
        except WifiError as error:
            return jsonify({"error": str(error)}), 400
        return jsonify({"ok": True, "message": f"Saved Wi-Fi uplink for {ssid.strip()}.", "wifi": snapshot})

    @app.get("/api/appliance/specs")
    def api_appliance_specs():
        specs = _collect_appliance_specs(app_config)
        dhcp_leases = specs.get("dhcp_leases") if isinstance(specs, dict) else []
        latest_lease = dhcp_leases[-1] if isinstance(dhcp_leases, list) and dhcp_leases else None
        specs["tv_remote"] = tv_remote_manager.status(latest_lease=latest_lease if isinstance(latest_lease, dict) else None)
        return jsonify({"specs": specs})

    @app.get("/api/appliance/logs")
    def api_appliance_logs():
        return jsonify({"logs": _collect_appliance_logs()})

    @app.get("/api/remote/status")
    def api_remote_status():
        network_snapshot = _cached_network_snapshot()
        return jsonify({"remote": tv_remote_manager.status(latest_lease=_latest_lease(network_snapshot))})

    @app.post("/api/remote/configure")
    def api_remote_configure():
        payload = request.get_json(silent=True) or request.form
        network_snapshot = _cached_network_snapshot()
        try:
            remote = tv_remote_manager.configure(
                host=str(payload.get("host", "")),
                display_name=str(payload.get("display_name", "") or app_config.tv_remote_name),
                vendor=str(payload.get("vendor", "") or app_config.tv_remote_vendor),
                port=int(str(payload.get("port", "")).strip()) if str(payload.get("port", "")).strip() else None,
                latest_lease=_latest_lease(network_snapshot),
            )
        except (TvRemoteError, ValueError) as error:
            return jsonify({"error": str(error)}), 400
        return jsonify({"ok": True, "message": f"Saved TV remote target {remote['host']}", "remote": remote})

    @app.post("/api/remote/key")
    def api_remote_key():
        payload = request.get_json(silent=True) or request.form
        network_snapshot = _cached_network_snapshot()
        try:
            remote = tv_remote_manager.send_key(str(payload.get("key", "")), latest_lease=_latest_lease(network_snapshot))
        except TvRemoteError as error:
            return jsonify({"error": str(error)}), 400
        return jsonify({"ok": True, "message": "TV remote key sent.", "remote": remote})

    @app.post("/api/remote/text")
    def api_remote_text():
        payload = request.get_json(silent=True) or request.form
        network_snapshot = _cached_network_snapshot()
        submit_value = payload.get("submit", False)
        submit = submit_value if isinstance(submit_value, bool) else str(submit_value).strip().lower() in {"1", "true", "yes", "on"}
        try:
            remote = tv_remote_manager.send_text(
                str(payload.get("text", "")),
                latest_lease=_latest_lease(network_snapshot),
                submit=submit,
            )
        except TvRemoteError as error:
            return jsonify({"error": str(error)}), 400
        return jsonify({"ok": True, "message": "TV text sent.", "remote": remote})

    return app


def _run_capture(*args: str) -> str | None:
    executable = shutil.which(args[0])
    if executable is None:
        return None

    try:
        result = subprocess.run([executable, *args[1:]], check=False, capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _strip_ansi(value: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", value)


def _parse_key_value_output(output: str | None) -> dict[str, str]:
    if not output:
        return {}

    values: dict[str, str] = {}
    for line in output.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def _probe_service_state(service_name: str) -> dict[str, str]:
    metadata = _parse_key_value_output(
        _run_capture(
            "systemctl",
            "show",
            service_name,
            "-p",
            "ActiveState",
            "-p",
            "SubState",
            "-p",
            "Result",
            "-p",
            "UnitFileState",
        )
    )
    active_state = metadata.get("ActiveState", "unknown")
    sub_state = metadata.get("SubState", "unknown")
    result = metadata.get("Result", "unknown")
    unit_file_state = metadata.get("UnitFileState", "unknown")
    return {
        "name": service_name,
        "label": SERVICE_LABELS.get(service_name, service_name),
        "active_state": active_state,
        "sub_state": sub_state,
        "result": result,
        "unit_file_state": unit_file_state,
        "healthy": "yes" if active_state == "active" and result in {"success", ""} else "no",
    }


def _probe_service_states() -> list[dict[str, str]]:
    return [_probe_service_state(service_name) for service_name in SERVICE_LABELS]


def _probe_default_route() -> str:
    return _run_capture("ip", "route", "show", "default") or "unavailable"


def _probe_dns_servers() -> list[str]:
    output = _run_capture("cat", "/etc/resolv.conf")
    if output is None:
        return []
    servers: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped.startswith("nameserver "):
            continue
        _, value = stripped.split(None, 1)
        servers.append(value)
    return servers


def _probe_dhcp_leases() -> list[dict[str, str]]:
    output = _run_capture("cat", "/var/lib/misc/dnsmasq.leases")
    if output is None:
        return []

    leases: list[dict[str, str]] = []
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 5:
            continue
        expiry, mac, address, hostname, client_id = parts[:5]
        leases.append(
            {
                "expiry_epoch": expiry,
                "mac": mac,
                "address": address,
                "hostname": hostname if hostname != "*" else "unknown",
                "client_id": client_id,
            }
        )
    return leases


def _lease_expiry_iso(lease: dict[str, str] | None) -> str | None:
    if not lease:
        return None

    raw_value = lease.get("expiry_epoch", "").strip()
    if not raw_value:
        return None

    try:
        return datetime.fromtimestamp(int(raw_value), UTC).isoformat()
    except (TypeError, ValueError, OSError):
        return None


def _neighbor_for_address(neighbors: list[str], address: str | None) -> str | None:
    if not address:
        return None

    prefix = f"{address} "
    for neighbor in neighbors:
        if neighbor.startswith(prefix):
            return neighbor
    return None


def _neighbor_state(neighbor: str | None) -> str | None:
    if not neighbor:
        return None

    parts = neighbor.split()
    if not parts:
        return None
    return parts[-1]


def _neighbor_mac(neighbor: str | None) -> str | None:
    if not neighbor:
        return None

    parts = neighbor.split()
    if "lladdr" not in parts:
        return None

    index = parts.index("lladdr")
    if index + 1 >= len(parts):
        return None
    return parts[index + 1]


def _build_tv_connectivity(downstream: dict[str, str | bool], dhcp_leases: list[dict[str, str]], downstream_neighbors: list[str]) -> tuple[str, str, dict[str, object]]:
    latest_lease = dhcp_leases[-1] if dhcp_leases else None
    lease_address = latest_lease.get("address") if latest_lease else None
    lease_hostname = latest_lease.get("hostname") if latest_lease else None
    neighbor_line = _neighbor_for_address(downstream_neighbors, lease_address)
    neighbor_state = _neighbor_state(neighbor_line)
    live_neighbor_states = {"REACHABLE", "STALE", "DELAY", "PROBE", "PERMANENT"}
    live_neighbor = bool(neighbor_state in live_neighbor_states)
    vendor_hint = "Samsung" if lease_hostname and "samsung" in lease_hostname.lower() else None

    if downstream["state"] != "up":
        tv_status = "cable offline"
        tv_status_detail = "The TV-facing Ethernet link is not up on the Pi."
    elif latest_lease and live_neighbor:
        tv_status = "lease active"
        tv_status_detail = (
            f"{lease_hostname} has {lease_address} on the TV LAN and the Pi still sees live neighbor activity. "
            "OpenSpoofen can verify the local path, but not whether the TV app itself can reach its upstream service."
        )
    elif latest_lease and neighbor_state in {"FAILED", "INCOMPLETE"}:
        tv_status = "lease stale"
        tv_status_detail = (
            f"{lease_hostname} still owns {lease_address}, but the Pi currently sees the neighbor as {neighbor_state.lower()}. "
            "That usually means the TV is asleep, unplugged, or retrying the wired path."
        )
    elif latest_lease:
        tv_status = "lease present"
        tv_status_detail = (
            f"A downstream client holds {lease_address}, but no fresh neighbor activity is visible right now."
        )
    elif downstream_neighbors:
        tv_status = "link seen"
        tv_status_detail = "The TV-side link is up and the Pi sees a neighbor, but no DHCP lease is recorded yet."
    else:
        tv_status = "waiting for TV"
        tv_status_detail = "The Pi is ready, but no downstream TV lease or neighbor has been observed yet."

    tv_connectivity = {
        "status": tv_status,
        "detail": tv_status_detail,
        "hostname": lease_hostname,
        "address": lease_address,
        "mac": (latest_lease.get("mac") if latest_lease else None) or _neighbor_mac(neighbor_line),
        "lease_expires_at": _lease_expiry_iso(latest_lease),
        "neighbor_present": bool(neighbor_line),
        "neighbor_state": neighbor_state,
        "neighbor_line": neighbor_line,
        "live_neighbor": live_neighbor,
        "vendor_hint": vendor_hint,
        "exact_model": None,
        "model_hint": (
            "The DHCP lease only identifies the set as Samsung. Exact model discovery requires the TV to be awake and responding on the LAN."
            if vendor_hint
            else "No exact TV model has been discovered from the downstream LAN yet."
        ),
        "vpn_path_hint": "The TV LAN advertises a VPN-safe MTU to reduce Samsung-style wired tests stalling behind NordLynx.",
    }
    return tv_status, tv_status_detail, tv_connectivity


def _tail_service_log(service_name: str, lines: int = 18) -> list[str]:
    output = _run_capture("journalctl", "-u", service_name, "-n", str(lines), "--no-pager", "-o", "short-iso")
    if output is None:
        return ["Logs unavailable on this host."]
    cleaned = _strip_ansi(output).strip()
    return cleaned.splitlines() if cleaned else ["No recent log lines."]


def _collect_appliance_logs() -> dict[str, object]:
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "services": [
            {
                "name": service_name,
                "label": SERVICE_LABELS.get(service_name, service_name),
                "lines": _tail_service_log(service_name),
            }
            for service_name in SERVICE_LABELS
        ],
    }


def _collect_appliance_specs(config: AppConfig) -> dict[str, object]:
    upstream = _probe_interface(config.upstream_interface)
    downstream = _probe_interface(config.downstream_interface)
    dhcp_leases = _probe_dhcp_leases()
    downstream_neighbors = _probe_neighbors(config.downstream_interface)
    _, _, tv_connectivity = _build_tv_connectivity(downstream, dhcp_leases, downstream_neighbors)
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "device_hostname": config.device_hostname,
        "preferred_topology": config.preferred_topology,
        "upstream_interface": config.upstream_interface,
        "downstream_interface": config.downstream_interface,
        "upstream_interface_status": upstream,
        "downstream_interface_status": downstream,
        "default_provider": config.default_provider,
        "lan_only": config.lan_only,
        "enable_https": config.enable_https,
        "require_pairing_token": config.require_pairing_token,
        "default_route": _probe_default_route(),
        "dns_servers": _probe_dns_servers(),
        "service_states": _probe_service_states(),
        "dhcp_leases": dhcp_leases,
        "tv_neighbors": downstream_neighbors,
        "tv_connectivity": tv_connectivity,
    }


def _probe_network_health(config: AppConfig) -> dict[str, object]:
    upstream = _probe_interface(config.upstream_interface)
    downstream = _probe_interface(config.downstream_interface)
    downstream_neighbors = _probe_neighbors(config.downstream_interface)
    dhcp_leases = _probe_dhcp_leases()
    latest_lease = dhcp_leases[-1] if dhcp_leases else None
    service_states = _probe_service_states()
    dns_servers = _probe_dns_servers()
    default_route = _probe_default_route()
    tv_status, tv_status_detail, tv_connectivity = _build_tv_connectivity(downstream, dhcp_leases, downstream_neighbors)

    return {
        "preferred_topology": config.preferred_topology,
        "fail_closed": config.fail_closed,
        "upstream_interface": upstream,
        "downstream_interface": downstream,
        "tv_status": tv_status,
        "tv_status_detail": tv_status_detail,
        "tv_connectivity": tv_connectivity,
        "tv_neighbors": downstream_neighbors,
        "latest_lease": latest_lease,
        "lease_count": len(dhcp_leases),
        "service_states": service_states,
        "dns_servers": dns_servers,
        "default_route": default_route,
        "diagnostic_summary": "Pi-side VPN connectivity does not guarantee TV app reachability; use the live lease, neighbor state, and service logs to confirm the downstream path.",
    }


def _probe_interface(interface_name: str) -> dict[str, str | bool]:
    output = _run_capture("ip", "-brief", "address", "show", "dev", interface_name)
    if not output:
        return {"name": interface_name, "state": "unknown", "addresses": "unavailable", "present": False}

    line = output.splitlines()[0]
    parts = line.split(maxsplit=2)
    state = parts[1] if len(parts) > 1 else "unknown"
    addresses = parts[2] if len(parts) > 2 else ""
    return {"name": interface_name, "state": state.lower(), "addresses": addresses or "none", "present": True}


def _probe_neighbors(interface_name: str) -> list[str]:
    output = _run_capture("ip", "neigh", "show", "dev", interface_name)
    if output is None:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> None:
    app = create_app()
    config: AppConfig = app.config["RP_CONFIG"]
    ssl_context = None
    if config.enable_https:
        if config.tls_cert_path and config.tls_key_path:
            ssl_context = (str(config.tls_cert_path), str(config.tls_key_path))
        else:
            ssl_context = "adhoc"
    app.run(host=config.host, port=config.port, debug=False, ssl_context=ssl_context)


if __name__ == "__main__":
    main()