from __future__ import annotations

import json
from pathlib import Path

from scripts import install_skill


def make_source(root: Path) -> Path:
    source = root / "source"
    (source / "scripts").mkdir(parents=True)
    (source / "SKILL.md").write_text(
        "---\nname: TsaoSciComputation\ndescription: test\n---\n", encoding="utf-8"
    )
    (source / "VERSION").write_text("3.0.0\n", encoding="utf-8")
    (source / "manifest.json").write_text("{}\n", encoding="utf-8")
    (source / "scripts" / "verify_all.py").write_text("print('ok')\n", encoding="utf-8")
    return source


def test_resolve_destination_for_user_and_project(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    assert install_skill.resolve_destination(
        "codex", "user", None, home=home, cwd=project
    ) == (home / ".codex/skills/TsaoSciComputation").resolve()
    assert install_skill.resolve_destination(
        "claude", "project", None, home=home, cwd=project
    ) == (project / ".claude/skills/TsaoSciComputation").resolve()


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
