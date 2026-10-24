from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from .acceptance import acceptance_gate
from .approval_attestation import verify_approval_attestation

LEVEL_ORDER = ("C0", "C1", "C2", "C3", "C4", "C5")
LEVEL_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "C0": ("completed",),
    "C1": ("completed", "parsed", "converged"),
    "C2": ("completed", "parsed", "converged", "physically_validated"),
    "C3": (
        "completed",
        "parsed",
        "converged",
        "physically_validated",
        "uncertainty_quantified",
        "applicability_confirmed",
        "evidence_bound",
    ),
    "C4": (
        "completed",
        "parsed",
        "converged",
        "physically_validated",
        "uncertainty_quantified",
        "applicability_confirmed",
        "evidence_bound",
        "expert_reviewed",
        "approvals",
    ),
    "C5": (
        "completed",
        "parsed",
        "converged",
        "physically_validated",
        "uncertainty_quantified",
        "applicability_confirmed",
        "evidence_bound",
        "expert_reviewed",
        "approvals",
        "decision_scope_confirmed",
        "safety_review_completed",
        "independent_reproduction",
    ),
}

CLAIM_BOUNDARIES = {
    "UNASSESSED": "No completed result is available; no scientific claim is supported.",
    "C0": "Process completion only; parsing, convergence, and scientific validity are not established.",
    "C1": "Numerically completed and converged; physical validity and applicability are not established.",
    "C2": "Numerical and physical checks passed; uncertainty and applicability remain incomplete.",
    "C3": "Research evidence is bounded by quantified uncertainty and applicability; expert acceptance is not established.",
    "C4": "Expert-reviewed scientific acceptance; engineering or safety-critical authorization is not implied.",
    "C5": "Decision scope, safety review, and independent reproduction are recorded; use remains limited to the documented applicability domain.",
}


@dataclass(frozen=True, slots=True)
class ConfidenceAssessment:
    schema_version: str
    level: str
    level_rank: int
    satisfied_requirements: tuple[str, ...]
    next_level: str | None
    missing_for_next: tuple[str, ...]
    engineering_decision_ready: bool
    claim_boundary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["satisfied_requirements"] = list(self.satisfied_requirements)
        payload["missing_for_next"] = list(self.missing_for_next)
        return payload


_GOVERNANCE_SCOPES = {
    "decision_scope_confirmed": ("engineering-decision", "independent-domain-reviewer"),
    "safety_review_completed": ("safety-review", "safety-reviewer"),
    "independent_reproduction": ("independent-reproduction", "independent-reproducer"),
}


def assess_confidence(
    record: Mapping[str, Any],
    *,
    trusted_approval_keys: Mapping[str, bytes] | None = None,
    now: datetime | None = None,
) -> ConfidenceAssessment:
    """Classify evidence; C4/C5 require artifact-bound external verification.

    Trust keys are supplied by the consumer, never read from the result record.
    C5 additionally requires signed, scope-specific governance attestations.
    """
    if not isinstance(record, Mapping):
        raise TypeError("confidence input must be a mapping")
    accepted = acceptance_gate(dict(record), trusted_approval_keys=trusted_approval_keys, now=now)[
        "accepted"
    ]
    governance: set[str] = set()
    nonce_requirements: dict[str, set[str]] = {}
    approvals = record.get("approvals", ())
    decision_scope = record.get("decision_scope")
    if accepted and isinstance(approvals, (list, tuple)):
        for approval in approvals:
            valid, _ = verify_approval_attestation(
                approval,
                trusted_keys=trusted_approval_keys or {},
                artifact_sha256=record["artifact_sha256"],
                now=now,
            )
            if not valid:
                continue
            nonce = approval["nonce"]
            if (
                approval["scope"] == "scientific-result-acceptance"
                and approval["role"] == "independent-domain-reviewer"
            ):
                nonce_requirements.setdefault(nonce, set()).add("approvals")
                continue
            for requirement, (scope, role) in _GOVERNANCE_SCOPES.items():
                if (
                    approval["scope"] == scope
                    and approval["role"] == role
                    and isinstance(decision_scope, str)
                    and bool(decision_scope.strip())
                    and approval.get("decision_scope") == decision_scope
                ):
                    nonce_requirements.setdefault(nonce, set()).add(requirement)

        # Collect every eligible use before counting governance: a nonce reused
        # across acceptance/governance purposes cannot count, regardless of order.
        # Repeated proofs for one requirement remain idempotent; an independent
        # clean proof can still satisfy a requirement with a conflicting alternative.
        for nonce_uses in nonce_requirements.values():
            if len(nonce_uses) == 1:
                governance.update(nonce_uses.intersection(_GOVERNANCE_SCOPES))

    def requirement_satisfied(requirement: str) -> bool:
        if requirement == "approvals":
            return bool(accepted)
        if requirement in _GOVERNANCE_SCOPES:
            return record.get(requirement) is True and requirement in governance
        return record.get(requirement) is True

    level = "UNASSESSED"
    satisfied: tuple[str, ...] = ()
    for candidate in LEVEL_ORDER:
        requirements = LEVEL_REQUIREMENTS[candidate]
        if all(requirement_satisfied(item) for item in requirements):
            level = candidate
            satisfied = requirements
        else:
            break

    rank = LEVEL_ORDER.index(level) if level in LEVEL_ORDER else -1
    next_level = LEVEL_ORDER[rank + 1] if rank + 1 < len(LEVEL_ORDER) else None
    missing = (
        tuple(item for item in LEVEL_REQUIREMENTS[next_level] if not requirement_satisfied(item))
        if next_level is not None
        else ()
    )
    return ConfidenceAssessment(
        schema_version="1.0",
        level=level,
        level_rank=rank,
        satisfied_requirements=satisfied,
        next_level=next_level,
        missing_for_next=missing,
        engineering_decision_ready=level == "C5",
        claim_boundary=CLAIM_BOUNDARIES[level],
    )
