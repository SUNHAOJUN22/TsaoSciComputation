from __future__ import annotations

import os
import subprocess  # nosec B404
from collections.abc import Mapping, Sequence
from pathlib import Path

from ..errors import SecurityError

_PORTABLE_ENVIRONMENT_KEYS = ("PATH", "HOME", "TEMP", "TMP", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE")
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
_SAFE_OVERRIDE_KEYS = frozenset(
    {
        "CUDA_VISIBLE_DEVICES",
        "HIP_VISIBLE_DEVICES",
        "ROCR_VISIBLE_DEVICES",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    }
)


def _override_allowed(key: str) -> bool:
    normalized = key.upper()
    return (
        normalized in _SAFE_OVERRIDE_KEYS
        or normalized in _PORTABLE_ENVIRONMENT_KEYS
        or normalized in _WINDOWS_ENVIRONMENT_KEYS
        or normalized.startswith("TSAO_")
    )


def _subprocess_environment(
    overrides: Mapping[str, str] | None = None,
    *,
    parent: Mapping[str, str] | None = None,
    platform_name: str | None = None,
) -> dict[str, str]:
    source = os.environ if parent is None else parent
    platform = os.name if platform_name is None else platform_name
    allowed = _PORTABLE_ENVIRONMENT_KEYS + (_WINDOWS_ENVIRONMENT_KEYS if platform == "nt" else ())
    if platform == "nt":
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
        unsafe = sorted(str(key) for key in overrides if not _override_allowed(str(key)))
        if unsafe:
            raise SecurityError(f"unsafe subprocess environment overrides: {unsafe}")
        for raw_key, raw_value in overrides.items():
            key = str(raw_key)
            value = str(raw_value)
            if not value or "\x00" in value:
                raise SecurityError(f"invalid subprocess environment value: {key}")
            if platform == "nt":
                for existing in tuple(merged):
                    if existing.casefold() == key.casefold():
                        del merged[existing]
            merged[key] = value
    return merged


def safe_run(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout: float = 300.0,
    env: Mapping[str, str] | None = None,
    allow_process_execution: bool = False,
) -> subprocess.CompletedProcess[str]:
    if allow_process_execution is not True:
        raise SecurityError("process execution requires a verified hash-bound authorization")
    if not argv or any(not isinstance(item, str) or not item or "\x00" in item for item in argv):
        raise SecurityError("argv must be a non-empty sequence of non-empty strings")
    if timeout <= 0 or timeout > 86400:
        raise SecurityError("timeout must be within (0, 86400] seconds")
    try:
        resolved_cwd = cwd.expanduser().resolve(strict=True)
    except OSError as error:
        raise SecurityError(f"working directory does not exist: {cwd}") from error
    if not resolved_cwd.is_dir():
        raise SecurityError(f"working directory does not exist: {cwd}")
    return subprocess.run(
        tuple(argv),
        cwd=resolved_cwd,
        env=_subprocess_environment(env),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        shell=False,  # nosec B603
    )
