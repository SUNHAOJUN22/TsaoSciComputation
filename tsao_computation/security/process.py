from __future__ import annotations

import os
import subprocess  # nosec B404
from collections.abc import Mapping, Sequence
from pathlib import Path

from ..errors import SecurityError

_PORTABLE_ENVIRONMENT_KEYS = (
    "PATH",
    "HOME",
    "TEMP",
    "TMP",
    "TMPDIR",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
)
_WINDOWS_ENVIRONMENT_KEYS = (
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "SYSTEMDRIVE",
    "USERPROFILE",
    "APPDATA",
    "LOCALAPPDATA",
)


def _subprocess_environment(
    overrides: Mapping[str, str] | None = None,
    *,
    parent: Mapping[str, str] | None = None,
    platform_name: str | None = None,
) -> dict[str, str]:
    """Build a minimal operational environment without leaking arbitrary host variables."""

    source = os.environ if parent is None else parent
    platform = os.name if platform_name is None else platform_name
    allowed: tuple[str, ...] = _PORTABLE_ENVIRONMENT_KEYS
    if platform == "nt":
        allowed += _WINDOWS_ENVIRONMENT_KEYS
        source_by_name = {str(key).casefold(): str(value) for key, value in source.items()}
        merged = {
            name: source_by_name[name.casefold()]
            for name in allowed
            if name.casefold() in source_by_name
        }
    else:
        merged = {name: str(source[name]) for name in allowed if name in source}

    merged.setdefault("PATH", "")
    merged["LANG"] = "C.UTF-8"
    if overrides:
        for raw_key, raw_value in overrides.items():
            key = str(raw_key)
            value = str(raw_value)
            if platform == "nt":
                for existing in tuple(merged):
                    if existing.casefold() == key.casefold():
                        del merged[existing]
            merged[key] = value
    return merged


def safe_run(
    argv: Sequence[str], *, cwd: Path, timeout: float = 300.0, env: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    if not argv or any(not isinstance(x, str) or not x for x in argv):
        raise SecurityError("argv must be a non-empty sequence of non-empty strings")
    if timeout <= 0 or timeout > 86400:
        raise SecurityError("timeout must be within (0, 86400] seconds")
    if not cwd.is_dir():
        raise SecurityError(f"working directory does not exist: {cwd}")
    return subprocess.run(
        tuple(argv),
        cwd=cwd,
        env=_subprocess_environment(env),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        shell=False,  # nosec B603
    )
