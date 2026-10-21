# Scientific confidence levels

TsaoSciComputation uses a fail-closed C0–C5 scale. The scale records the highest evidence level actually satisfied; it does not infer missing evidence from a successful process exit, parser result, or solver claim.

| Level | Minimum evidence | Permitted interpretation |
|---|---|---|
| UNASSESSED | No completed result | No scientific claim. |
| C0 | Completed | Process completion only. |
| C1 | Parsed and numerically converged | Numerical result only; physical validity is not established. |
| C2 | Physical validation added | Numerical and physical checks passed; uncertainty is incomplete. |
| C3 | Uncertainty, applicability, and evidence lineage added | Bounded research evidence; no expert acceptance is implied. |
| C4 | Artifact-bound signature verified with externally provisioned trust keys | Expert-reviewed scientific acceptance; no engineering authorization is implied. |
| C5 | Separately signed decision, safety and reproduction scopes bound to one artifact and decision domain | Engineering-decision readiness only within the documented applicability domain. |

The assessment is sequential. A record cannot reach C3 by supplying uncertainty while omitting convergence, and malformed or empty approvals cannot satisfy C4. C5 is deliberately strict and remains separate from ordinary scientific publication.

```python
from tsao_computation.validation import assess_confidence

assessment = assess_confidence(record, trusted_approval_keys=trusted_keys)
print(assessment.to_dict())
```

Machine-readable assessments validate against `schemas/confidence-assessment.schema.json`. High-risk reactor, control, runaway, digital-twin, plant-safety, and commercial decisions still require qualified domain governance outside this software.

## Verified acceptance boundary

`assess_confidence`, `ScientificStateMachine.transition` and `HandoffRecord` share the external `acceptance_gate`. Plain approval strings, caller-declared acceptance flags and keys embedded in the payload cannot produce C4/C5. Accepted states cannot be created directly. A scientific acceptance transition must identify the exact reviewed artifact digest.

C5 requires three additional HMAC attestations in `approvals`: `engineering-decision` / `independent-domain-reviewer`, `safety-review` / `safety-reviewer`, and `independent-reproduction` / `independent-reproducer`. Each must verify against external trust keys, carry a unique nonce in the decision, match the artifact and include the exact `decision_scope` from the assessment record. Lower-level evidence and governance booleans remain required; the signature adds an independent verification boundary.

Contract regressions: `tests/test_acceptance_repair.py`, `tests/test_confidence_model.py`, `tests/test_state_and_handoff.py`, and `tests/test_approval_attestation_boundaries.py`. No fixture is a claim that an external scientific result was qualified.
