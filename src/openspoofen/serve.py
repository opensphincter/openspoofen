from __future__ import annotations

from gunicorn.app.base import BaseApplication

from openspoofen.config import AppConfig, load_config
from openspoofen.web import create_app


class OpenSpoofenGunicornApp(BaseApplication):
    def __init__(self, app, options: dict[str, object]) -> None:
        self._app = app
        self._options = options
        super().__init__()

    def load_config(self) -> None:
        for key, value in self._options.items():
            if value is None:
                continue
            if key in self.cfg.settings:
                self.cfg.set(key, value)

    def load(self):
        return self._app


def _gunicorn_options(config: AppConfig) -> dict[str, object]:
    options: dict[str, object] = {
        "bind": f"{config.host}:{config.port}",
        "worker_class": "gthread",
        "workers": 2,
        "threads": 4,
        "timeout": int(config.command_timeout_seconds),
    }

    if config.enable_https:
        if not config.tls_cert_path or not config.tls_key_path:
            raise RuntimeError("HTTPS is enabled but RP_TLS_CERT_PATH and RP_TLS_KEY_PATH are not both configured.")
        options["certfile"] = str(config.tls_cert_path)
        options["keyfile"] = str(config.tls_key_path)

    return options


def main() -> None:
    config = load_config()
    app = create_app(config)
    OpenSpoofenGunicornApp(app, _gunicorn_options(config)).run()


if __name__ == "__main__":
    main()