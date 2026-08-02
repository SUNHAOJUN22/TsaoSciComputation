from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "tsao_computation/immutable.py"
text = path.read_text(encoding="utf-8")
old_import = "from collections.abc import Mapping\nfrom typing import Any, NoReturn\n"
new_import = (
    "from collections.abc import Iterable, Mapping\n"
    "from typing import Any, NoReturn, SupportsIndex\n"
)
if text.count(old_import) != 1:
    raise SystemExit("immutable import block not found exactly once")
text = text.replace(old_import, new_import, 1)
replacements = {
    "    def __ior__(self, value: Mapping[str, Any]) -> NoReturn:\n": (
        "    def __ior__(self, value: Any) -> FrozenDict:  "
        "# type: ignore[override,misc]\n"
    ),
    "    def __iadd__(self, value: Any) -> NoReturn:\n": (
        "    def __iadd__(self, value: Iterable[Any]) -> FrozenList:  "
        "# type: ignore[misc]\n"
    ),
    "    def __imul__(self, value: Any) -> NoReturn:\n": (
        "    def __imul__(self, value: SupportsIndex) -> FrozenList:\n"
    ),
    "    def insert(self, index: int, value: Any) -> NoReturn:\n": (
        "    def insert(self, index: SupportsIndex, value: Any) -> NoReturn:\n"
    ),
    "    def pop(self, index: int = -1) -> NoReturn:\n": (
        "    def pop(self, index: SupportsIndex = -1) -> NoReturn:\n"
    ),
}
for old, new in replacements.items():
    if text.count(old) != 1:
        raise SystemExit(f"immutable signature not found exactly once: {old!r}")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8", newline="\n")
print("Phase A immutable signatures finalized")
