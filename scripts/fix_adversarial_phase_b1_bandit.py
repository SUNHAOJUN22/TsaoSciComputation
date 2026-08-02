from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "tsao_computation/accelerators/model.py"
text = path.read_text(encoding="utf-8")
old = '''        cpu_count = _positive_int(self.logical_cpu_count, "logical_cpu_count")
        assert cpu_count is not None
        object.__setattr__(self, "logical_cpu_count", cpu_count)
'''
new = '''        cpu_count = _positive_int(self.logical_cpu_count, "logical_cpu_count")
        if cpu_count is None:
            raise ContractError("logical_cpu_count must be a positive integer")
        object.__setattr__(self, "logical_cpu_count", cpu_count)
'''
if text.count(old) != 1:
    raise SystemExit(f"logical CPU validation block not found exactly once: {text.count(old)}")
path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
print("Phase B1 Bandit correction applied")
