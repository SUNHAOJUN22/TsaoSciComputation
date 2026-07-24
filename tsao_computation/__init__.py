from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

__all__ = ["__version__"]

try:
    __version__ = version("tsao-scicomputation")
except PackageNotFoundError:
    __version__ = (
        (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
    )
