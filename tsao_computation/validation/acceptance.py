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


def acceptance_gate(record: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in REQUIRED if record.get(key) is not True]
    approvals = record.get("approvals") or []
    if record.get("human_approval_required") and (not approvals):
        missing.append("human_approval")
    return {"accepted": not missing, "missing": sorted(set(missing)), "policy": "fail-closed"}
