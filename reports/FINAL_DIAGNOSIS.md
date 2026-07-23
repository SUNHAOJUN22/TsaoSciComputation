# Final verification diagnosis

- Python 3.10: `core`
- Python 3.13: `quality`

## Python 3.10 log

```text
STAGE=core
EXIT_CODE=1
--- LOG TAIL ---

==> tests and coverage
    /opt/hostedtoolcache/Python/3.10.20/x64/bin/python scripts/run_tests.py --coverage
........................................................................ [ 14%]
........................................................................ [ 28%]
........................................................................ [ 42%]
........................................................................ [ 56%]
........................................................................ [ 70%]
..................................F.F................................... [ 84%]
........................F............................................... [ 98%]
..........                                                               [100%]
=================================== FAILURES ===================================
____________________________ test_004_handoff_valid ____________________________

    @pytest.mark.integration
    def test_004_handoff_valid():
        assert (
>           HandoffRecord(
                "a", "b", "q", 1, "1", {}, "r", 0, 0, "d", "identity", "validated"
            ).validation_status
            == "validated"
        )

tests/test_core.py:49: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
<string>:15: in __init__
    ???
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = HandoffRecord(source_model='a', target_model='b', quantity='q', value=1, unit='1', conditions={}, reference_state='r',...stical_uncertainty=0, model_uncertainty=0, applicability='d', transformation='identity', validation_status='validated')

    def __post_init__(self) -> None:
        required = (
            self.source_model,
            self.target_model,
            self.quantity,
            self.unit,
            self.reference_state,
            self.applicability,
            self.transformation,
        )
        if any(not isinstance(item, str) or not item.strip() for item in required):
            raise ContractError("handoff metadata must contain non-empty strings")
        if self.value is None:
            raise ContractError("handoff value must be explicit")
        if not isinstance(self.conditions, Mapping) or not self.conditions:
>           raise ContractError("handoff conditions must be a non-empty object")
E           tsao_computation.errors.ContractError: handoff conditions must be a non-empty object

tsao_computation/contracts/handoff.py:40: ContractError
__________________________ test_006_state_happy_path ___________________________

    @pytest.mark.integration
    def test_006_state_happy_path():
        m = ScientificStateMachine()
        for s in (
            "planned",
            "prepared",
            "submitted",
            "running",
            "completed",
            "parsed",
            "converged",
            "validated",
            "accepted",
        ):
>           m.transition(s, evidence=s)

tests/test_core.py:76: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = ScientificStateMachine(state='prepared', events=[{'from': 'proposed', 'to': 'specified', 'requested_to': 'planned', 'e...equested_to': 'prepared', 'evidence': 'prepared', 'actor': 'system', 'timestamp': '2026-07-23T17:10:28.700631+00:00'}])
target = 'submitted', evidence = 'submitted', actor = 'system'

    def transition(self, target: str, *, evidence: str, actor: str = "system") -> dict[str, Any]:
        if not evidence.strip():
            raise StateTransitionError("state transitions require evidence")
        normalized = canonical_state(target)
        if normalized not in STATES or not self.can_transition(normalized):
            allowed = sorted(TRANSITIONS[self.state])
>           raise StateTransitionError(
                f"illegal transition: {self.state} -> {normalized}; allowed targets: {allowed}"
            )
E           tsao_computation.errors.StateTransitionError: illegal transition: prepared -> submitted; allowed targets: ['preflight-passed', 'rejected', 'superseded']

tsao_computation/state/machine.py:74: StateTransitionError
_____________ test_uninstall_requires_valid_manifest_without_force _____________

tmp_path = PosixPath('/tmp/pytest-of-runner/pytest-0/test_uninstall_requires_valid_0')

    def test_uninstall_requires_valid_manifest_without_force(tmp_path: Path) -> None:
        source = make_source(tmp_path)
        destination = tmp_path / "installed" / "TsaoSciComputation"
        install_skill.install_skill(source, destination, agent="codex", scope="project")
        (destination / "SKILL.md").write_text("tampered\n", encoding="utf-8")
    
>       with pytest.raises(ValueError, match="invalid installation"):
E       Failed: DID NOT RAISE ValueError

tests/test_install_skill.py:91: Failed
=========================== short test summary info ============================
FAILED tests/test_core.py::test_004_handoff_valid - tsao_computation.errors.ContractError: handoff conditions must be a non-empty object
FAILED tests/test_core.py::test_006_state_happy_path - tsao_computation.errors.StateTransitionError: illegal transition: prepared -> submitted; allowed targets: ['preflight-passed', 'rejected', 'superseded']
FAILED tests/test_install_skill.py::test_uninstall_requires_valid_manifest_without_force - Failed: DID NOT RAISE ValueError
3 failed, 511 passed in 1.62s

FAILED: tests and coverage (exit 1)

```

## Python 3.13 log

```text
STAGE=quality
EXIT_CODE=1
--- LOG TAIL ---

==> repository quality rules
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python scripts/quality_check.py
{"passed": true, "problems": [], "python_files": 82, "schema_version": "1.0"}

==> Ruff lint
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python -m ruff check tsao_computation scripts tests
All checks passed!

==> Ruff formatting
    /opt/hostedtoolcache/Python/3.13.14/x64/bin/python -m ruff format --check tsao_computation scripts tests
Would reformat: scripts/build_adapter_docs.py
Would reformat: scripts/build_examples.py
Would reformat: tests/test_validation_fail_closed.py
Would reformat: tsao_computation/adapters/base.py
Would reformat: tsao_computation/contracts/calculation.py
5 files would be reformatted, 77 files already formatted

FAILED: Ruff formatting (exit 1)

```
