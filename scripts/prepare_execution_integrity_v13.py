from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch_generator() -> None:
    path = ROOT / "scripts/apply_execution_integrity_v13.py"
    text = path.read_text(encoding="utf-8")
    old = r'(tmp_path / "shadow_probe.py").write_text("VALUE = 1\n", encoding="utf-8")'
    new = r'(tmp_path / "shadow_probe.py").write_text("VALUE = 1\\n", encoding="utf-8")'
    if text.count(old) != 1:
        raise SystemExit("execution-integrity generator escape anchor mismatch")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def patch_changelog() -> None:
    path = ROOT / "CHANGELOG.md"
    text = path.read_text(encoding="utf-8")
    anchor = "## Unreleased\n"
    release = """## Unreleased

## 3.0.4 — 2026-08-03

- Disabled direct execution through the legacy low-level process API; external computation now requires a sealed, hash-bound authorization created for the exact command plan.
- Bound every authorized run to the current executable SHA-256, declared input-file SHA-256 and normalized subprocess environment immediately before launch.
- Separated fixed, allowlisted read-only hardware discovery from scientific computation execution and repaired default accelerator probing on real systems.
- Routed Python-module availability probes through the sanitized environment and made adapter command-plan environments immutable.
- Added execution-integrity fault injection, machine evidence and bilingual documentation for the strengthened boundary.
"""
    if text.count(anchor) != 1:
        raise SystemExit("CHANGELOG Unreleased anchor mismatch")
    path.write_text(text.replace(anchor, release, 1), encoding="utf-8", newline="\n")


def write_report() -> None:
    (ROOT / "reports/EXECUTION_INTEGRITY_V13.md").write_text(
        """# Execution Integrity V13

This audit closes the public low-level process bypass, separates fixed read-only probes from computation execution, binds authorization to the current executable and declared input contents, and hashes the normalized subprocess environment.

External solver execution remains plan-only until a matching authorization is created through `authorize_plan`; scientific acceptance remains a separate gate.
""",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    patch_generator()
    runpy.run_path(str(ROOT / "scripts/apply_execution_integrity_v13.py"), run_name="__main__")
    patch_changelog()
    (ROOT / "VERSION").write_text("3.0.4\n", encoding="utf-8", newline="\n")
    write_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
