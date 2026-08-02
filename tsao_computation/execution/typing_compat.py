from __future__ import annotations

from pathlib import Path
from typing import Protocol


class CommandPlanLike(Protocol):
    argv: tuple[str, ...]
    cwd: Path
    environment: dict[str, str]
