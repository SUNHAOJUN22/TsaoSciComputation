# TsaoSciComputation — Final Debug Closure

## Acceptance model

The acceptance path now separates deterministic readiness from independently verifiable acceptance:

```text
software_ready
  = completed
  ∧ parsed
  ∧ converged
  ∧ physically_validated
  ∧ uncertainty_quantified
  ∧ applicability_confirmed
  ∧ evidence_bound

accepted
  = software_ready
  ∧ exact_artifact_sha256
  ∧ verified_external_approval_attestation
```

A caller-controlled `human_approval_required` Boolean and free-form approval strings are non-authoritative. They cannot produce `accepted=true`.

## Approval attestation

`tsao_computation.validation.approval_attestation` binds:

- issuer, approver, requester and authorized role;
- explicit scope;
- exact artifact SHA-256;
- timezone-aware issue and expiry times;
- nonce and key identifier;
- HMAC-SHA256 signature verified against a key supplied outside the result record.

The approver and requester must be different identities. Tampering, an unknown key, a mismatched artifact, a reused nonce inside one decision, an invalid interval, a future approval or an expired approval fails closed.

## Regression commands

```bash
python -m pytest -q \
  tests/test_core.py \
  tests/test_extended.py \
  tests/test_validation_fail_closed.py
python scripts/validate_repo.py
python scripts/run_all_tests.py
```

## Boundary

A passing software gate does not establish that a real solver, cluster, engineering workflow or external reviewer was available. Real external execution and scientific acceptance require separately issued evidence and remain unclaimed when those artifacts are absent.
