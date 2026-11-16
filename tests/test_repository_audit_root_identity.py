from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tsao_computation.cli import main
from tsao_computation.registries import adapters
from tsao_computation.repository_audit import (
    REQUIRED_DIRECTORIES,
    REQUIRED_FILES,
    audit_repository,
)


@pytest.fixture
def audited_copy(tmp_path: Path) -> Path:
    source = Path(__file__).resolve().parents[1]
    target = tmp_path / "candidate"
    target.mkdir()
    for relative in REQUIRED_DIRECTORIES:
        (target / relative).mkdir(parents=True, exist_ok=True)
    for relative in REQUIRED_FILES:
        shutil.copy2(source / relative, target / relative)
    for relative in ("registry", "tsao_computation/data/registry", "capability-index/capabilities"):
        shutil.copytree(source / relative, target / relative, dirs_exist_ok=True)
    assert audit_repository(target)["passed"] is True
    return target


@pytest.mark.parametrize("also_change_package", [False, True])
def test_requested_root_registries_determine_counts_and_validation(
    audited_copy: Path, also_change_package: bool
) -> None:
    assert len(adapters()) == 27  # Populate the installed registry cache first.
    (audited_copy / "registry/adapters.json").write_text("[]\n", encoding="utf-8")
    if also_change_package:
        (audited_copy / "tsao_computation/data/registry/adapters.json").write_text(
            "[]\n", encoding="utf-8"
        )
    report = audit_repository(audited_copy)
    assert report["passed"] is False
    assert report["counts"]["adapters"] == 0
    assert "adapter count is not 27" in report["problems"]
    assert len(adapters()) == 27


def test_cli_repository_audit_rejects_source_only_mutation_in_requested_root(
    audited_copy: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (audited_copy / "registry/adapters.json").write_text("[]\n", encoding="utf-8")
    assert main(["validate-repository", "--root", str(audited_copy)]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["counts"]["adapters"] == 0
    assert "package registry asset is not synchronized: adapters.json" in report["problems"]


@pytest.mark.parametrize("body", ["{}", "[1]", '[{"slug":"first","slug":"second"}]'])
def test_malformed_requested_root_registry_fails_closed(audited_copy: Path, body: str) -> None:
    (audited_copy / "registry/adapters.json").write_text(body, encoding="utf-8")
    report = audit_repository(audited_copy)
    assert report["passed"] is False
    assert report["counts"]["adapters"] == 0
    assert any("registry must contain an array of objects" in item for item in report["problems"])


def test_registry_file_set_must_match_inside_requested_root(audited_copy: Path) -> None:
    (audited_copy / "tsao_computation/data/registry/extra.json").write_text(
        "[]\n", encoding="utf-8"
    )
    report = audit_repository(audited_copy)
    assert report["passed"] is False
    assert "package registry asset is not synchronized: extra.json" in report["problems"]


def test_untrusted_capability_identity_cannot_select_another_path(audited_copy: Path) -> None:
    path = audited_copy / "registry/capabilities.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    records[0]["id"] = "../outside"
    path.write_text(json.dumps(records), encoding="utf-8")
    report = audit_repository(audited_copy)
    assert report["passed"] is False
    assert any("safe non-empty path components" in item for item in report["problems"])


@pytest.mark.parametrize(
    ("registry", "field", "value"),
    [
        ("capabilities", "inputs", None),
        ("capabilities", "outputs", 1),
        ("capabilities", "recommended_adapters", None),
        ("capabilities", "maturity", []),
        ("capabilities", "implementation_level", {}),
        ("capabilities", "risk_level", []),
        ("capabilities", "description", {}),
        ("capabilities", "triggers", [None, "valid"]),
        ("workflows", "capability_ids", None),
        ("workflows", "recommended_adapters", 1),
        ("adapters", "slug", []),
        ("adapters", "executables", [None]),
        ("accelerators", "preferred_backends", [None]),
        ("accelerators", "candidate_backends", "cpu"),
    ],
)
def test_malformed_nested_registry_fields_return_failed_audit(
    audited_copy: Path, registry: str, field: str, value: object
) -> None:
    path = audited_copy / "registry" / f"{registry}.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    records[0][field] = value
    path.write_text(json.dumps(records), encoding="utf-8")

    report = audit_repository(audited_copy)

    assert report["passed"] is False
    assert any(f"{registry}.json[0].{field}" in problem for problem in report["problems"])


@pytest.mark.parametrize("name", ["VERSION", "pyproject.toml"])
def test_audit_never_reads_metadata_symlink_target(
    audited_copy: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    path = audited_copy / name
    outside = audited_copy.parent / f"external-{name}"
    outside.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(outside)
    original_read = Path.read_text

    def guarded_read(target: Path, *args: object, **kwargs: object) -> str:
        if target in (path, outside):
            pytest.fail("metadata outside the audited tree must not be read")
        return original_read(target, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read)
    report = audit_repository(audited_copy)
    assert report["passed"] is False
    assert any(
        f"metadata file is not confined to audited root: {name}" in item
        for item in report["problems"]
    )


def test_non_utf8_version_is_reported_as_invalid_metadata(audited_copy: Path) -> None:
    (audited_copy / "VERSION").write_bytes(b"\xff\xfe")
    report = audit_repository(audited_copy)
    assert report["passed"] is False
    assert any("invalid VERSION" in item for item in report["problems"])


@pytest.mark.parametrize(
    "relative",
    [
        "registry/adapters.json",
        "tsao_computation/data/registry/adapters.json",
        "schemas/loop.json",
        "registry",
    ],
)
def test_symlink_cycles_return_failed_audit(audited_copy: Path, relative: str) -> None:
    path = audited_copy / relative
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
    path.symlink_to(path.name, target_is_directory=relative == "registry")

    report = audit_repository(audited_copy)

    assert report["passed"] is False
    assert any("not confined to audited root" in item for item in report["problems"])
