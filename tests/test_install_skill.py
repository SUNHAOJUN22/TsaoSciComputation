from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts import install_skill


def _write_manifest(source: Path) -> None:
    records = []
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        if path.name == "manifest.json":
            continue
        data = path.read_bytes()
        records.append(
            {
                "bytes": len(data),
                "path": path.relative_to(source).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    (source / "manifest.json").write_text(
        json.dumps({"files": records}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def make_source(root: Path) -> Path:
    source = root / "source"
    (source / "scripts").mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: TsaoSciComputation\ndescription: test\n---\n", encoding="utf-8"
    )
    (source / "VERSION").write_text("3.0.0\n", encoding="utf-8")
    (source / "scripts" / "verify_all.py").write_text("print('ok')\n", encoding="utf-8")
    _write_manifest(source)
    return source


def test_resolve_destination_for_user_and_project(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    assert (
        install_skill.resolve_destination("codex", "user", None, home=home, cwd=project)
        == (home / ".codex/skills/TsaoSciComputation").resolve()
    )
    assert (
        install_skill.resolve_destination("claude", "project", None, home=home, cwd=project)
        == (project / ".claude/skills/TsaoSciComputation").resolve()
    )


def test_install_validate_and_uninstall_roundtrip(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    destination = tmp_path / "installed" / "TsaoSciComputation"
    install_skill.install_skill(
        source,
        destination,
        agent="codex",
        scope="project",
    )
    assert install_skill.validate_installation(destination) == []
    receipt = json.loads((destination / install_skill.RECEIPT_NAME).read_text(encoding="utf-8"))
    assert receipt["skill"] == "TsaoSciComputation"
    install_skill.uninstall_skill(destination)
    assert not destination.exists()


def test_validation_detects_tampering_and_unlisted_files(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    destination = tmp_path / "installed" / "TsaoSciComputation"
    install_skill.install_skill(source, destination, agent="codex", scope="project")
    (destination / "SKILL.md").write_text("tampered\n", encoding="utf-8")
    (destination / "unexpected.txt").write_text("unlisted\n", encoding="utf-8")

    problems = install_skill.validate_installation(destination)

    assert any("hash differs" in problem and "SKILL.md" in problem for problem in problems)
    assert any("unlisted files" in problem and "unexpected.txt" in problem for problem in problems)


def test_validation_rejects_manifest_path_escape(tmp_path: Path) -> None:
    destination = tmp_path / "TsaoSciComputation"
    destination.mkdir()
    (destination / "SKILL.md").write_text("name: TsaoSciComputation\n", encoding="utf-8")
    (destination / "VERSION").write_text("3.0.0\n", encoding="utf-8")
    (destination / "scripts").mkdir()
    (destination / "scripts" / "verify_all.py").write_text("pass\n", encoding="utf-8")
    (destination / install_skill.RECEIPT_NAME).write_text(
        json.dumps({"skill": "TsaoSciComputation", "version": "3.0.0"}), encoding="utf-8"
    )
    (destination / "manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {"bytes": 0, "path": "../escape", "sha256": "0" * 64},
                ]
            }
        ),
        encoding="utf-8",
    )

    assert any("escapes the installation root" in item for item in install_skill.validate_installation(destination))


def test_dry_run_does_not_modify_destination(tmp_path: Path) -> None:
    source = make_source(tmp_path)
    destination = tmp_path / "dry" / "TsaoSciComputation"
    install_skill.install_skill(
        source,
        destination,
        agent="open-agent-skills",
        scope="user",
        dry_run=True,
    )
    assert not destination.exists()


def test_parser_exposes_required_flags() -> None:
    help_text = install_skill.build_parser().format_help()
    for flag in (
        "--agent",
        "--scope",
        "--target",
        "--force",
        "--dry-run",
        "--uninstall",
        "--validate",
    ):
        assert flag in help_text
