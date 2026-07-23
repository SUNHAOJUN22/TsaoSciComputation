from __future__ import annotations

from typing import Any

REQUIRED = (
    "completed",
    "parsed",
    "converged",
    "physically_validated",
    "uncertainty_quantified",
    "applicability_confirmed",
    "evidence_bound",
)


def _valid_approvals(value: object) -> bool:
    return (
        isinstance(value, (list, tuple))
        and bool(value)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def acceptance_gate(record: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in REQUIRED if record.get(key) is not True]
    if record.get("human_approval_required") and not _valid_approvals(record.get("approvals")):
        missing.append("human_approval")
    return {"accepted": not missing, "missing": sorted(set(missing)), "policy": "fail-closed"}
