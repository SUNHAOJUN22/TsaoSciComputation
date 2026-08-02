from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts/apply_adversarial_super_skill_phase_a.py"
text = path.read_text(encoding="utf-8")
old = (
    "            ready=not blockers, execute_allowed=False, argv=(), cwd=None, environment={},\n"
    "            blockers=blockers or (\"runtime execution remains disabled until a dedicated authorized executor is bound\",),\n"
)
new = (
    "            ready=False, execute_allowed=False, argv=(), cwd=None, environment={},\n"
    "            blockers=blockers or (\"runtime execution remains disabled until a dedicated authorized executor is bound\",),\n"
)
if text.count(old) != 1:
    raise SystemExit(f"generator readiness block not found exactly once: {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
print("Phase A generator prepared")
