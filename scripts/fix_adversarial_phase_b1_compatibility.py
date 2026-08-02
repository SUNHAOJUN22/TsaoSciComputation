from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one {label}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


model = ROOT / "tsao_computation/accelerators/model.py"
replace_once(
    model,
    '''    if non_empty and not parsed:
        raise ContractError(f"{field_name} must be non-empty")
    if len(set(parsed)) != len(parsed):
        raise ContractError(f"{field_name} must be unique")
''',
    '''    if (non_empty and not parsed) or len(set(parsed)) != len(parsed):
        raise ContractError(f"{field_name} must be non-empty and unique")
''',
    "enum tuple diagnostic",
)

planner = ROOT / "tsao_computation/accelerators/planner.py"
replace_once(
    planner,
    '''    if request.accelerator_policy is AcceleratorPolicy.DISABLED:
        selected = _cpu_fallback(supported=supported, adapter_slug=adapter_slug)
''',
    '''    if request.accelerator_policy is AcceleratorPolicy.DISABLED:
        selected = _cpu_fallback(supported=supported, adapter_slug=adapter_slug)
        fallback = fallback or first_requested is not AcceleratorBackend.CPU
''',
    "disabled accelerator fallback evidence",
)

print("Phase B1 compatibility corrections applied")
