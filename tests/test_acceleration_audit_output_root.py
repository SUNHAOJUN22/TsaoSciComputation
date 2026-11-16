from __future__ import annotations

import sys
from pathlib import Path

import pytest

from scripts.build_acceleration_audits import main, render_all


def test_audit_builder_writes_and_checks_only_requested_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    requested = tmp_path / "audited"
    requested.mkdir()
    (requested / "solver.py").write_text(
        "def solve():\n    return sum(range(8))\n", encoding="utf-8"
    )
    caller = tmp_path / "caller"
    caller.mkdir()
    monkeypatch.chdir(caller)
    monkeypatch.setattr(sys, "argv", ["build_acceleration_audits", "--root", str(requested)])

    assert main() == 0

    assert not (caller / "reports").exists()
    for relative, expected in render_all(requested).items():
        assert (requested / relative).read_text(encoding="utf-8") == expected

    monkeypatch.setattr(sys, "argv", [*sys.argv, "--check"])
    assert main() == 0
    (requested / "reports/ACCELERATION_OPPORTUNITIES_V2.json").unlink()
    assert main() == 1
