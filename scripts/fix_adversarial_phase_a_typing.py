from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise ValueError(f"expected one {label}, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


(ROOT / "tsao_computation/immutable.py").write_text(
    '''from __future__ import annotations

from collections.abc import Mapping
from typing import Any, NoReturn


class FrozenDict(dict[str, Any]):
    """JSON-compatible dictionary that rejects in-place mutation."""

    __slots__ = ()

    @staticmethod
    def _immutable() -> NoReturn:
        raise TypeError("immutable mapping cannot be modified")

    def __setitem__(self, key: str, value: Any) -> NoReturn:
        self._immutable()

    def __delitem__(self, key: str) -> NoReturn:
        self._immutable()

    def clear(self) -> NoReturn:
        self._immutable()

    def pop(self, key: str, default: Any = None) -> NoReturn:
        self._immutable()

    def popitem(self) -> NoReturn:
        self._immutable()

    def setdefault(self, key: str, default: Any = None) -> NoReturn:
        self._immutable()

    def update(self, *args: Any, **kwargs: Any) -> NoReturn:
        self._immutable()

    def __ior__(self, value: Mapping[str, Any]) -> NoReturn:
        self._immutable()

    def __copy__(self) -> FrozenDict:
        return self

    def __deepcopy__(self, memo: dict[int, object]) -> FrozenDict:
        return self


class FrozenList(list[Any]):
    """JSON-compatible list that rejects in-place mutation."""

    __slots__ = ()

    @staticmethod
    def _immutable() -> NoReturn:
        raise TypeError("immutable sequence cannot be modified")

    def __setitem__(self, key: Any, value: Any) -> NoReturn:
        self._immutable()

    def __delitem__(self, key: Any) -> NoReturn:
        self._immutable()

    def __iadd__(self, value: Any) -> NoReturn:
        self._immutable()

    def __imul__(self, value: Any) -> NoReturn:
        self._immutable()

    def append(self, value: Any) -> NoReturn:
        self._immutable()

    def clear(self) -> NoReturn:
        self._immutable()

    def extend(self, values: Any) -> NoReturn:
        self._immutable()

    def insert(self, index: int, value: Any) -> NoReturn:
        self._immutable()

    def pop(self, index: int = -1) -> NoReturn:
        self._immutable()

    def remove(self, value: Any) -> NoReturn:
        self._immutable()

    def reverse(self) -> NoReturn:
        self._immutable()

    def sort(self, *args: Any, **kwargs: Any) -> NoReturn:
        self._immutable()

    def __copy__(self) -> FrozenList:
        return self

    def __deepcopy__(self, memo: dict[int, object]) -> FrozenList:
        return self


def freeze_json(value: Any) -> Any:
    if isinstance(value, (FrozenDict, FrozenList)):
        return value
    if isinstance(value, Mapping):
        return FrozenDict({str(key): freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return FrozenList(freeze_json(item) for item in value)
    if isinstance(value, tuple):
        return tuple(freeze_json(item) for item in value)
    return value


def thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): thaw_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [thaw_json(item) for item in value]
    return value
''',
    encoding="utf-8",
    newline="\n",
)

for relative in (
    "tsao_computation/uncertainty/model.py",
    "tsao_computation/validation/physical.py",
):
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if "from typing import Any, cast" not in text:
        marker = "from dataclasses import dataclass\n" if "uncertainty" in relative else "from functools import cache\n"
        text = text.replace(marker, marker + "from typing import Any, cast\n", 1)
    text = text.replace("converted = float(value)", "converted = float(cast(Any, value))", 1)
    path.write_text(text, encoding="utf-8", newline="\n")

adapter = ROOT / "tsao_computation/adapters/base.py"
replace_once(
    adapter,
    "def _resolve_executable(candidate: str) -> str | None:\n    path = Path(candidate).expanduser()\n",
    "def _resolve_executable(candidate: str) -> str | None:\n    path = Path(candidate).expanduser()\n    resolved: str | None\n",
    "resolved executable annotation",
)

orchestration_test = ROOT / "tests/test_super_skill_orchestration.py"
replace_once(
    orchestration_test,
    '    assert "authorization" in abstract.blockers[0]\n',
    '    assert {"target", "input schema", "authorization", "evidence policy"} <= set(abstract.blockers)\n',
    "external template blocker assertion",
)

print("phase A typing corrections applied")
