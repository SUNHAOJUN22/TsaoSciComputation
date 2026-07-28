from __future__ import annotations

import re
from pathlib import Path

from scripts import install_skill
from scripts.validate_skill_spec import validate_repository_skills

ROOT = Path(__file__).resolve().parents[1]


def test_all_agent_skills_follow_repository_contract() -> None:
    report = validate_repository_skills(ROOT)
    assert report["status"] == "PASS", report["problems"]
    assert report["skill_count"] == 21


def test_installer_uses_portable_skill_identifier_and_preserves_legacy_target(
    tmp_path: Path,
) -> None:
    assert install_skill.SKILL_NAME == "tsao-scicomputation"
    assert install_skill.LEGACY_SKILL_NAME == "TsaoSciComputation"

    home = tmp_path / "home"
    canonical = (home / ".codex/skills/tsao-scicomputation").resolve()
    assert install_skill.resolve_destination("codex", "user", None, home=home) == canonical

    legacy = home / ".codex/skills/TsaoSciComputation"
    legacy.mkdir(parents=True)
    assert install_skill.resolve_destination("codex", "user", None, home=home) == legacy.resolve()


def test_workflows_pin_actions_and_avoid_privileged_untrusted_triggers() -> None:
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    assert workflows
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        assert "pull_request_target:" not in text, path
        assert "workflow_run:" not in text, path
        for line in text.splitlines():
            if "uses:" not in line:
                continue
            reference = line.split("@", 1)[1].split()[0]
            assert re.fullmatch(r"[0-9a-f]{40}", reference), (path, line)


def test_release_workflow_does_not_interpolate_dispatch_input_into_shell() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert 'TAG="${{ inputs.tag }}"' not in workflow
    assert "REQUESTED_TAG: ${{ inputs.tag }}" in workflow
    assert 'TAG="$REQUESTED_TAG"' in workflow
    assert "ref: ${{ github.sha }}" in workflow
    assert 'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"' in workflow
    assert "python scripts/build_manifest.py --check" in workflow
    assert "git diff --exit-code" in workflow


def test_scorecard_workflow_is_pinned_and_least_privilege() -> None:
    workflow = (ROOT / ".github" / "workflows" / "scorecard.yml").read_text(encoding="utf-8")
    assert "permissions: read-all" in workflow
    assert "security-events: write" in workflow
    assert "id-token: write" in workflow
    assert "persist-credentials: false" in workflow
    assert "publish_results: true" in workflow
    assert "pull_request_target:" not in workflow
    assert "workflow_run:" not in workflow
    for line in workflow.splitlines():
        if "uses:" not in line:
            continue
        reference = line.split("@", 1)[1].split()[0]
        assert re.fullmatch(r"[0-9a-f]{40}", reference), line


def test_quality_gate_executes_skill_validation() -> None:
    source = (ROOT / "scripts" / "quality_check.py").read_text(encoding="utf-8")
    assert "validate_repository_skills" in source
    assert '"agent_skills"' in source
