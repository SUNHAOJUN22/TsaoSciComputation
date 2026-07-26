from __future__ import annotations

import json
from pathlib import Path

from scripts.update_main_audit_evidence import update_evidence


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def test_update_evidence_synchronizes_bilingual_main_records(tmp_path: Path) -> None:
    root = tmp_path
    _write(
        root / "README.md",
        "before\n<!-- CURRENT_MAIN_VERIFICATION:START -->old<!-- CURRENT_MAIN_VERIFICATION:END -->\nafter\n",
    )
    _write(
        root / "README.zh-CN.md",
        "之前\n<!-- CURRENT_MAIN_VERIFICATION:START -->旧<!-- CURRENT_MAIN_VERIFICATION:END -->\n之后\n",
    )
    _write(
        root / "reports" / "CURRENT_MAIN_VERIFICATION.json",
        json.dumps(
            {
                "version": "3.0.2",
                "counts": {
                    "adapters": 27,
                    "capabilities": 164,
                    "visual_assets": 18,
                    "workflows": 20,
                },
            }
        ),
    )
    test_log = _write(root / "pytest.log", "560 passed in 1.0s\n")
    coverage = _write(
        root / "coverage.json",
        json.dumps(
            {
                "totals": {
                    "percent_statements_covered": 97.5,
                    "percent_branches_covered": 94.0,
                }
            }
        ),
    )
    dependency = _write(root / "dependency.json", json.dumps([]))
    security = _write(root / "security.json", json.dumps({"findings": []}))
    remote_heads = _write(root / "heads.txt", "abc refs/heads/main\n")

    evidence = update_evidence(
        root=root,
        run_id=12345,
        issue_number=24,
        test_log=test_log,
        coverage_json=coverage,
        dependency_json=dependency,
        security_json=security,
        remote_heads=remote_heads,
        parent_commit="abc123",
        verified_at="2026-07-26T00:00:00+00:00",
    )

    assert evidence["tests"] == {"failed": 0, "passed": 560}
    assert evidence["counts"]["visual_assets"] == 24
    assert evidence["remote_branches"] == ["main"]
    assert evidence["audit_generation"] == "ultimate-main-audit-v4"
    assert "560 passed, 0 failed" in (root / "README.md").read_text(encoding="utf-8")
    assert "560 通过，0 失败" in (root / "README.zh-CN.md").read_text(encoding="utf-8")
    assert "Scientific visuals: `24`" in (root / "reports" / "ULTIMATE_MAIN_AUDIT_V4.md").read_text(
        encoding="utf-8"
    )
