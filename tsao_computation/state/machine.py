from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from ..errors import StateTransitionError

STATES = (
    "proposed",
    "planned",
    "prepared",
    "submitted",
    "running",
    "completed",
    "parsed",
    "converged",
    "validated",
    "accepted",
    "rejected",
    "failed",
    "superseded",
)
TRANSITIONS = {
    "proposed": {"planned", "rejected", "superseded"},
    "planned": {"prepared", "rejected", "superseded"},
    "prepared": {"submitted", "rejected", "superseded"},
    "submitted": {"running", "failed", "superseded"},
    "running": {"completed", "failed", "superseded"},
    "completed": {"parsed", "failed", "superseded"},
    "parsed": {"converged", "failed", "rejected", "superseded"},
    "converged": {"validated", "rejected", "superseded"},
    "validated": {"accepted", "rejected", "superseded"},
    "accepted": {"superseded"},
    "rejected": {"superseded"},
    "failed": {"planned", "superseded"},
    "superseded": set(),
}


@dataclass(slots=True)
class ScientificStateMachine:
    state: str = "proposed"
    events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.state not in STATES:
            raise StateTransitionError(f"unknown initial state: {self.state}")

    def can_transition(self, target: str) -> bool:
        return target in TRANSITIONS[self.state]

    def transition(self, target: str, *, evidence: str, actor: str = "system") -> dict[str, Any]:
        if not evidence.strip():
            raise StateTransitionError("state transitions require evidence")
        if target not in STATES or not self.can_transition(target):
            raise StateTransitionError(f"illegal transition: {self.state} -> {target}")
        event = {
            "from": self.state,
            "to": target,
            "evidence": evidence,
            "actor": actor,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.state = target
        self.events.append(event)
        return event
