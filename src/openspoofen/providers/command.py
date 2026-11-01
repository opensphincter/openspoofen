from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path

from openspoofen.providers.base import ProviderError, VpnProvider


class CommandVpnProvider(VpnProvider):
    command_names: tuple[str, ...] = ()

    def _timeout_seconds(self) -> float | None:
        config = getattr(self, "_config", None)
        timeout = getattr(config, "command_timeout_seconds", None)
        return timeout if isinstance(timeout, int | float) and timeout > 0 else None

    def _resolve_executable(self) -> str:
        for command_name in self.command_names:
            executable = shutil.which(command_name)
            if executable is not None:
                return executable

        choices = ", ".join(self.command_names) or "provider CLI"
        raise ProviderError(f"The {self.provider_name} CLI is not available. Expected one of: {choices}.")

    def _command_env(self, env: Mapping[str, str] | None = None) -> dict[str, str]:
        merged_env = os.environ.copy()
        config = getattr(self, "_config", None)

        provider_home = getattr(config, "provider_home", None)
        provider_user = getattr(config, "provider_user", None)

        merged_env.setdefault("HOME", str(provider_home or Path.home()))
        if provider_user:
            merged_env.setdefault("USER", provider_user)
            merged_env.setdefault("LOGNAME", provider_user)

        if env is not None:
            merged_env.update(dict(env))

        return merged_env

    def _run_result(
        self,
        *args: str,
        input_text: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        executable = self._resolve_executable()
        command = [executable, *args]
        config = getattr(self, "_config", None)
        provider_user = getattr(config, "provider_user", None)
        runuser = shutil.which("runuser")
        if provider_user and os.geteuid() == 0 and runuser is not None:
            command = [runuser, "-u", provider_user, "--", *command]
        try:
            return subprocess.run(
                command,
                check=False,
                capture_output=True,
                input=input_text,
                text=True,
                env=self._command_env(env),
                timeout=self._timeout_seconds(),
            )
        except subprocess.TimeoutExpired as error:
            timeout = self._timeout_seconds()
            raise ProviderError(f"{self.provider_name} command timed out after {timeout:g}s.") from error

    def _result_text(self, result: subprocess.CompletedProcess[str]) -> str:
        return (result.stdout or result.stderr or "").strip()

    def _run(
        self,
        *args: str,
        input_text: str | None = None,
        env: Mapping[str, str] | None = None,
        allowed_return_codes: tuple[int, ...] = (0,),
    ) -> str:
        result = self._run_result(*args, input_text=input_text, env=env)
        if result.returncode not in allowed_return_codes:
            error_text = self._result_text(result) or f"{self.provider_name} command failed"
            raise ProviderError(error_text)
        return self._result_text(result)