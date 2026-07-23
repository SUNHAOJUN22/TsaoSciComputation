from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    source_path = root / "registry" / "adapters.json"
    packaged_path = root / "tsao_computation" / "data" / "registry" / "adapters.json"
    try:
        records = _load(source_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"invalid adapter registry: {exc}"]
    if not isinstance(records, list):
        return ["adapter registry must be an array"]
    if not packaged_path.is_file() or source_path.read_bytes() != packaged_path.read_bytes():
        problems.append("packaged adapter registry is not synchronized")

    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            problems.append(f"adapter entry {index} is not an object")
            continue
        slug = record.get("slug")
        if not isinstance(slug, str) or not slug:
            problems.append(f"adapter entry {index} has an invalid slug")
            continue
        if slug in seen:
            problems.append(f"duplicate adapter slug: {slug}")
        seen.add(slug)

        executables = record.get("executables")
        if not isinstance(executables, list) or any(
            not isinstance(item, str) or not item for item in executables
        ):
            problems.append(f"adapter {slug} has invalid executable declarations")
            executables = []
        modules = record.get("python_modules")
        if modules is not None and (
            not isinstance(modules, list)
            or not modules
            or any(not isinstance(item, str) or not item for item in modules)
        ):
            problems.append(f"adapter {slug} has invalid Python module declarations")
        if "python" in executables and not modules:
            problems.append(f"adapter {slug} uses Python but declares no required modules")

        adapter_path = root / "adapters" / slug / "adapter.yaml"
        try:
            adapter_payload = _load(adapter_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            problems.append(f"adapter {slug} has invalid adapter.yaml: {exc}")
        else:
            if adapter_payload != record:
                problems.append(f"adapter {slug} metadata is not synchronized")
    return problems


def main() -> int:
    problems = validate()
    print(json.dumps({"passed": not problems, "problems": problems}, indent=2, sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
