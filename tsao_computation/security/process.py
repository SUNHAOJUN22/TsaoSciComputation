from __future__ import annotations

import os
import subprocess  # nosec B404
from collections.abc import Mapping, Sequence
from pathlib import Path

from ..errors import SecurityError


def safe_run(
    argv: Sequence[str], *, cwd: Path, timeout: float = 300.0, env: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    if not argv or any(not isinstance(x, str) or not x for x in argv):
        raise SecurityError("argv must be a non-empty sequence of non-empty strings")
    if timeout <= 0 or timeout > 86400:
        raise SecurityError("timeout must be within (0, 86400] seconds")
    if not cwd.is_dir():
        raise SecurityError(f"working directory does not exist: {cwd}")
    merged = {"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"}
    if env:
        merged.update({str(k): str(v) for k, v in env.items()})
    return subprocess.run(
        tuple(argv),
        cwd=cwd,
        env=merged,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        shell=False,  # nosec B603
    )
