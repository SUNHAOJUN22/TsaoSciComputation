from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import tomllib

from . import __version__
from .paths import SOURCE_REGISTRY_ROOT
from .provenance.manifest import iter_repository_entries
from .registries import adapters, capabilities, workflows

REQUIRED_FILES = (
    "README.md",
    "README.zh-CN.md",
    "SKILL.md",
    "VERSION",
    "LICENSE",
    "THIRD_PARTY.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "CITATION.cff",
    "pyproject.toml",
    "manifest.json",
)
REQUIRED_DIRECTORIES = (
    "tsao_computation",
    "scripts",
    "tests",
    "schemas",
    "registry",
    "capability-index/capabilities",
    "adapters",
    "skills/workflows",
    "examples",
    ".github/workflows",
)
FORBIDDEN_PATHS = (
    ".release_source",
    ".audit_source_v101",
    ".audit_patch_v102",
    ".bootstrap",
)
CAPABILITY_REQUIRED = {
    "id",
    "slug",
    "name_en",
    "name_cn",
    "workflow",
    "description",
    "triggers",
    "inputs",
    "outputs",
    "validators",
    "required_evidence",
    "failure_modes",
    "risk_level",
    "human_approval_required",
    "implementation_level",
    "maturity",
    "applicability",
    "claim_boundary",
}


def _load_json(path: Path, problems: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        problems.append(f"invalid JSON-compatible file {path.as_posix()}: {exc}")
        return None


def audit_repository(root: Path) -> dict[str, object]:
    root = root.resolve()
    problems: list[str] = []

    for item in REQUIRED_FILES:
        if not (root / item).is_file():
            problems.append(f"missing required file: {item}")
    for item in REQUIRED_DIRECTORIES:
        if not (root / item).is_dir():
            problems.append(f"missing required directory: {item}")
    for item in FORBIDDEN_PATHS:
        if (root / item).exists():
            problems.append(f"forbidden transfer path: {item}")

    version_path = root / "VERSION"
    if version_path.is_file() and version_path.read_text(encoding="utf-8").strip() != __version__:
        problems.append("VERSION and package __version__ differ")
    pyproject_path = root / "pyproject.toml"
    if pyproject_path.is_file():
        try:
            project_version = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))["project"][
                "version"
            ]
            if project_version != __version__:
                problems.append("pyproject version and package __version__ differ")
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
            problems.append(f"invalid pyproject.toml: {exc}")

    capability_records = capabilities()
    adapter_records = adapters()
    workflow_records = workflows()
    if len(capability_records) != 164:
        problems.append("capability count is not 164")
    if len(adapter_records) != 27:
        problems.append("adapter count is not 27")
    if len(workflow_records) != 20:
        problems.append("workflow count is not 20")

    capability_ids = [str(record.get("id", "")) for record in capability_records]
    capability_slugs = [str(record.get("slug", "")) for record in capability_records]
    adapter_slugs = [str(record.get("slug", "")) for record in adapter_records]
    workflow_slugs = [str(record.get("slug", "")) for record in workflow_records]
    if len(capability_ids) != len(set(capability_ids)):
        problems.append("duplicate capability ID")
    if len(capability_slugs) != len(set(capability_slugs)):
        problems.append("duplicate capability slug")
    if len(adapter_slugs) != len(set(adapter_slugs)):
        problems.append("duplicate adapter slug")
    if len(workflow_slugs) != len(set(workflow_slugs)):
        problems.append("duplicate workflow slug")

    workflow_set = set(workflow_slugs)
    adapter_set = set(adapter_slugs)
    input_profiles: set[tuple[str, ...]] = set()
    output_profiles: set[tuple[str, ...]] = set()
    descriptions: set[str] = set()
    for record in capability_records:
        missing = sorted(CAPABILITY_REQUIRED - record.keys())
        if missing:
            problems.append(f"capability {record.get('id')} missing fields: {missing}")
        workflow_slug = str(record.get("workflow", ""))
        if workflow_slug not in workflow_set:
            problems.append(
                f"capability {record.get('id')} references unknown workflow: {workflow_slug}"
            )
        recommended = set(map(str, record.get("recommended_adapters", [])))
        unknown = sorted(recommended - adapter_set)
        if unknown:
            problems.append(f"capability {record.get('id')} references unknown adapters: {unknown}")
        for key, minimum in (
            ("triggers", 2),
            ("inputs", 3),
            ("outputs", 3),
            ("validators", 3),
            ("required_evidence", 3),
            ("failure_modes", 2),
        ):
            values = record.get(key)
            if (
                not isinstance(values, list)
                or len(values) < minimum
                or any(not str(value).strip() for value in values)
            ):
                problems.append(f"capability {record.get('id')} has weak or empty {key}")
        if record.get("maturity") not in {f"A{index}" for index in range(8)}:
            problems.append(f"capability {record.get('id')} has invalid maturity")
        if record.get("implementation_level") not in {"native", "orchestrated", "delegated"}:
            problems.append(f"capability {record.get('id')} has invalid implementation_level")
        if record.get("risk_level") not in {"low", "medium", "high", "critical"}:
            problems.append(f"capability {record.get('id')} has invalid risk_level")
        input_profiles.add(tuple(map(str, record.get("inputs", []))))
        output_profiles.add(tuple(map(str, record.get("outputs", []))))
        descriptions.add(str(record.get("description", "")))

        capability_file = (
            root / "capability-index" / "capabilities" / f"{record['id']}_{record['slug']}.yaml"
        )
        payload = _load_json(capability_file, problems) if capability_file.is_file() else None
        if payload != record:
            problems.append(f"capability file is not synchronized: {record['id']}")

    if len(input_profiles) < 15 or len(output_profiles) < 15:
        problems.append("capability contracts are insufficiently differentiated across workflows")
    if len(descriptions) != len(capability_records):
        problems.append("capability descriptions are not unique")

    capability_id_set = set(capability_ids)
    for workflow_record in workflow_records:
        ids = list(map(str, workflow_record.get("capability_ids", [])))
        if not ids:
            problems.append(f"workflow {workflow_record.get('slug')} has no capabilities")
        unknown = sorted(set(ids) - capability_id_set)
        if unknown:
            problems.append(
                f"workflow {workflow_record.get('slug')} references unknown capability IDs: {unknown}"
            )
        recommended = set(map(str, workflow_record.get("recommended_adapters", [])))
        unknown_adapters = sorted(recommended - adapter_set)
        if unknown_adapters:
            problems.append(
                f"workflow {workflow_record.get('slug')} references unknown adapters: {unknown_adapters}"
            )

    for adapter in adapter_records:
        if str(adapter.get("workflow", "")) not in workflow_set:
            problems.append(f"adapter {adapter.get('slug')} references unknown workflow")
        if adapter.get("live_execution_verified") is not False:
            problems.append(
                f"adapter {adapter.get('slug')} has an unsupported live execution claim"
            )
        if not isinstance(adapter.get("executables"), list):
            problems.append(f"adapter {adapter.get('slug')} lacks executable declarations")

    source_registry = SOURCE_REGISTRY_ROOT
    package_registry = root / "tsao_computation" / "data" / "registry"
    for source in sorted(source_registry.glob("*.json")):
        target = package_registry / source.name
        if not target.is_file() or source.read_bytes() != target.read_bytes():
            problems.append(f"package registry asset is not synchronized: {source.name}")

    for path in sorted((root / "schemas").glob("*.json")):
        _load_json(path, problems)
    for path in sorted((root / "registry").glob("*.json")):
        _load_json(path, problems)
    for path in sorted((root / "examples").glob("*/contract.json")):
        _load_json(path, problems)

    symlinks = [
        path.relative_to(root).as_posix()
        for path in iter_repository_entries(root)
        if path.is_symlink()
    ]
    if symlinks:
        problems.append(f"symlinks are forbidden in the release tree: {symlinks}")

    return {
        "schema_version": "1.0",
        "passed": not problems,
        "problems": problems,
        "counts": {
            "capabilities": len(capability_records),
            "adapters": len(adapter_records),
            "workflows": len(workflow_records),
            "capability_input_profiles": len(input_profiles),
            "capability_output_profiles": len(output_profiles),
        },
    }
