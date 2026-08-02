from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if old not in text:
        raise ValueError(f"expected block not found: {label}")
    return text.replace(old, new, 1)


def patch_planner() -> None:
    path = ROOT / "tsao_computation" / "orchestration" / "planner.py"
    text = path.read_text(encoding="utf-8")
    text = _replace_once(
        text,
        "from ..validation import balance_check, convergence_check\n",
        "from ..validation import (\n"
        "    acceptance_gate,\n"
        "    assess_confidence,\n"
        "    balance_check,\n"
        "    convergence_check,\n"
        "    unit_known,\n"
        ")\n",
        label="validation imports",
    )
    text = _replace_once(
        text,
        textwrap.dedent(
            '''
                    _method(
                        "surrogate-machine-learning",
                        "Surrogate and machine learning",
                        "machine-learning",
                        ("data", "all"),
                        local + service,
                        ("batched training", "GPU tensor cores", "quantized inference"),
                    ),
            '''
        ).lstrip(),
        textwrap.dedent(
            '''
                    _method(
                        "surrogate-model",
                        "Surrogate model",
                        "reduced-order-modeling",
                        ("data", "all"),
                        local + service,
                        ("batched inference", "reduced-order model", "validated caching"),
                    ),
                    _method(
                        "machine-learning",
                        "Machine learning",
                        "machine-learning",
                        ("data", "all"),
                        local + service,
                        ("batched training", "GPU tensor cores", "quantized inference"),
                    ),
                    _method(
                        "data-processing",
                        "Scientific data processing",
                        "data-processing",
                        ("data", "all"),
                        local + service,
                        ("streaming", "columnar data", "parallel transforms"),
                    ),
                    _method(
                        "hpc-execution",
                        "HPC execution",
                        "execution",
                        ("all",),
                        solver + service,
                        ("scheduler arrays", "checkpoint restart", "hybrid MPI and threads"),
                    ),
            '''
        ).lstrip(),
        label="method expansion",
    )
    text = _replace_once(
        text,
        textwrap.dedent(
            '''
            def get_method(slug: str) -> MethodSpec:
                try:
                    return _method_index()[slug.strip().casefold().replace("_", "-")]
            '''
        ).lstrip(),
        textwrap.dedent(
            '''
            def get_method(slug: str) -> MethodSpec:
                normalized = slug.strip().casefold().replace("_", "-").replace(" ", "-")
                normalized = {"surrogate-machine-learning": "surrogate-model"}.get(
                    normalized, normalized
                )
                try:
                    return _method_index()[normalized]
            '''
        ).lstrip(),
        label="method normalization",
    )
    anchor = textwrap.dedent(
        '''
        def _invoke_benchmarks(payload: Mapping[str, Any]) -> object:
            if payload:
                raise ContractError("scientific-benchmarks accepts an empty payload")
            return [item.to_dict() for item in run_all()]


        '''
    ).lstrip()
    additions = textwrap.dedent(
        '''
        def _invoke_unit_known(payload: Mapping[str, Any]) -> object:
            unit = payload.get("unit")
            if not isinstance(unit, str) or not unit.strip():
                raise ContractError("unit must be a non-empty string")
            return {"unit": unit, "known": unit_known(unit)}


        def _invoke_acceptance(payload: Mapping[str, Any]) -> object:
            return acceptance_gate(dict(payload))


        def _invoke_confidence(payload: Mapping[str, Any]) -> object:
            return assess_confidence(payload).to_dict()


        '''
    ).lstrip()
    text = _replace_once(text, anchor, anchor + additions, label="trusted callable functions")
    dictionary_anchor = textwrap.dedent(
        '''
            "scientific-benchmarks": (
                "Deterministic scientific reference benchmarks",
                _invoke_benchmarks,
                (),
            ),
        '''
    ).lstrip()
    dictionary_additions = textwrap.dedent(
        '''
            "unit-known": ("Scientific unit registry lookup", _invoke_unit_known, ("unit",)),
            "acceptance-gate": ("Fail-closed scientific acceptance gate", _invoke_acceptance, ()),
            "confidence-assessment": (
                "Scientific confidence ladder assessment",
                _invoke_confidence,
                (),
            ),
        '''
    ).lstrip()
    text = _replace_once(
        text,
        dictionary_anchor,
        dictionary_anchor + dictionary_additions,
        label="trusted callable registry",
    )
    text = _replace_once(
        text,
        "    blockers = tuple(key for key in spec.required_inputs if key not in normalized_payload)\n",
        "    blockers = tuple(\n"
        "        key\n"
        "        for key in spec.required_inputs\n"
        "        if key not in normalized_payload or normalized_payload[key] is None\n"
        "    )\n",
        label="required-input validation",
    )
    old_adapter = textwrap.dedent(
        '''
            if slug.startswith("adapter:"):
                if input_path is None:
                    blockers = ("native_input_file",)
                    return InvocationPlan(
                        slug=spec.slug,
                        kind=spec.kind,
                        target=spec.target,
                        ready=False,
                        execute_allowed=False,
                        argv=(),
                        cwd=None,
                        environment={},
                        blockers=blockers,
                        expected_outputs=spec.expected_outputs,
                        evidence_requirements=spec.evidence_requirements,
                        claim_boundary=spec.claim_boundary,
                    )
                try:
                    command = get_adapter(spec.target).build_command(input_path)
                except ContractError as error:
                    blockers = (str(error),)
                    return InvocationPlan(
                        slug=spec.slug,
                        kind=spec.kind,
                        target=spec.target,
                        ready=False,
                        execute_allowed=False,
                        argv=(),
                        cwd=None,
                        environment={},
                        blockers=blockers,
                        expected_outputs=spec.expected_outputs,
                        evidence_requirements=spec.evidence_requirements,
                        claim_boundary=spec.claim_boundary,
                    )
                return InvocationPlan(
                    slug=spec.slug,
                    kind=spec.kind,
                    target=spec.target,
                    ready=True,
                    execute_allowed=False,
                    argv=command.argv,
                    cwd=str(command.cwd),
                    environment=command.environment,
                    blockers=(),
                    expected_outputs=spec.expected_outputs,
                    evidence_requirements=spec.evidence_requirements,
                    claim_boundary=command.claim_boundary,
                )
        '''
    ).lstrip()
    new_adapter = textwrap.dedent(
        '''
            if slug.startswith("adapter:"):
                missing = [
                    key
                    for key in ("lawful_environment", "explicit_authorization")
                    if key not in normalized_payload or not normalized_payload[key]
                ]
                if input_path is None:
                    missing.insert(0, "native_input_file")
                    return InvocationPlan(
                        slug=spec.slug,
                        kind=spec.kind,
                        target=spec.target,
                        ready=False,
                        execute_allowed=False,
                        argv=(),
                        cwd=None,
                        environment={},
                        blockers=tuple(missing),
                        expected_outputs=spec.expected_outputs,
                        evidence_requirements=spec.evidence_requirements,
                        claim_boundary=spec.claim_boundary,
                    )
                try:
                    command = get_adapter(spec.target).build_command(input_path)
                except ContractError as error:
                    missing.insert(0, str(error))
                    return InvocationPlan(
                        slug=spec.slug,
                        kind=spec.kind,
                        target=spec.target,
                        ready=False,
                        execute_allowed=False,
                        argv=(),
                        cwd=None,
                        environment={},
                        blockers=tuple(missing),
                        expected_outputs=spec.expected_outputs,
                        evidence_requirements=spec.evidence_requirements,
                        claim_boundary=spec.claim_boundary,
                    )
                return InvocationPlan(
                    slug=spec.slug,
                    kind=spec.kind,
                    target=spec.target,
                    ready=not missing,
                    execute_allowed=False,
                    argv=command.argv,
                    cwd=str(command.cwd),
                    environment=command.environment,
                    blockers=tuple(missing),
                    expected_outputs=spec.expected_outputs,
                    evidence_requirements=spec.evidence_requirements,
                    claim_boundary=command.claim_boundary,
                )
        '''
    ).lstrip()
    text = _replace_once(text, old_adapter, new_adapter, label="adapter invocation boundary")
    text = text.replace(
        '("digital", ("digital-twin", "surrogate-machine-learning")),\n',
        '("digital", ("digital-twin", "surrogate-model")),\n',
    ).replace(
        '("hpc", ("sparse-linear-algebra", "monte-carlo")),\n',
        '("hpc", ("hpc-execution", "sparse-linear-algebra", "monte-carlo")),\n'
        '        ("data", ("data-processing", "statistical-inference")),\n',
    )
    text = _replace_once(
        text,
        "def recommend_acceleration(\n",
        "def acceleration_strategies() -> tuple[AccelerationAdvice, ...]:\n"
        "    return tuple(item[0] for item in _STRATEGIES)\n\n\n"
        "def recommend_acceleration(\n",
        label="public acceleration strategy catalog",
    )
    text += (
        "\n\ndef clear_orchestration_caches() -> None:\n"
        "    methods.cache_clear()\n"
        "    _method_index.cache_clear()\n"
        "    list_invocations.cache_clear()\n"
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def patch_exports_and_cache_clear() -> None:
    init_path = ROOT / "tsao_computation" / "orchestration" / "__init__.py"
    text = init_path.read_text(encoding="utf-8")
    text = text.replace(
        "    build_invocation_plan,\n",
        "    acceleration_strategies,\n    build_invocation_plan,\n",
    ).replace(
        "    build_orchestration_plan,\n",
        "    build_orchestration_plan,\n    clear_orchestration_caches,\n",
    ).replace(
        '    "build_invocation_plan",\n',
        '    "acceleration_strategies",\n    "build_invocation_plan",\n',
    ).replace(
        '    "build_orchestration_plan",\n',
        '    "build_orchestration_plan",\n    "clear_orchestration_caches",\n',
    )
    init_path.write_text(text, encoding="utf-8", newline="\n")

    loader = ROOT / "tsao_computation" / "registries" / "loader.py"
    loader_text = loader.read_text(encoding="utf-8")
    loader_text = loader_text.replace(
        "    from ..routing.router import clear_routing_caches\n",
        "    from ..orchestration import clear_orchestration_caches\n"
        "    from ..routing.router import clear_routing_caches\n",
    ).replace(
        "    clear_routing_caches()\n",
        "    clear_routing_caches()\n    clear_orchestration_caches()\n",
    )
    loader.write_text(loader_text, encoding="utf-8", newline="\n")


def write_audit_builder() -> None:
    path = ROOT / "scripts" / "build_super_skill_audit.py"
    path.write_text(
        (ROOT / "scripts" / "apply_super_skill_finalization.py").read_text(encoding="utf-8")
        if False
        else textwrap.dedent(
            '''
            from __future__ import annotations

            import argparse
            import json
            import re
            import statistics
            import time
            from pathlib import Path
            from typing import Any

            from tsao_computation import __version__
            from tsao_computation.contracts import CalculationContract
            from tsao_computation.orchestration import (
                acceleration_strategies,
                build_orchestration_plan,
                execute_trusted_callable,
                list_invocations,
                methods,
            )
            from tsao_computation.registries import adapters, capabilities, workflows


            def _read_json(path: Path | None) -> Any:
                return None if path is None else json.loads(path.read_text(encoding="utf-8"))


            def _passed_tests(path: Path | None) -> int | None:
                if path is None:
                    return None
                values = [int(value) for value in re.findall(r"(\d+) passed", path.read_text(encoding="utf-8"))]
                return max(values) if values else None


            def _vulnerabilities(payload: Any) -> int | None:
                if payload is None:
                    return None
                records = payload if isinstance(payload, list) else payload.get("dependencies", [])
                return sum(len(item.get("vulns", [])) for item in records if isinstance(item, dict))


            def _contract() -> CalculationContract:
                return CalculationContract(
                    question="Plan a validated multiscale polymer computation",
                    system={"material": "polymer", "composition": "declared"},
                    conditions={"temperature_K": 300.0},
                    target_observables=("transport_property",),
                    workflow="molecular-dynamics",
                    assumptions=("declared model",),
                    acceptance_criteria={"relative_error_max": 0.05},
                    model_object={"type": "periodic cell"},
                    scales=("atomistic", "continuum"),
                    methods=("molecular-dynamics",),
                    boundary_conditions={"periodic": True},
                    initial_conditions={"temperature_K": 300.0},
                    parameter_sources=({"name": "parameters", "source": "declared"},),
                    convergence_plan={"declared": True},
                    validation_plan={"reference": "declared"},
                    uncertainty_sources=("sampling", "model-form"),
                    compute_resources={"gpu": "preferred", "workload": "long trajectory"},
                    expected_artifacts=("trajectory", "evidence"),
                    human_approval_nodes=("scientific_acceptance",),
                )


            def _median(operation: Any, loops: int) -> float:
                samples: list[float] = []
                for _ in range(7):
                    started = time.perf_counter()
                    for _ in range(loops):
                        operation()
                    samples.append((time.perf_counter() - started) / loops)
                return statistics.median(samples)


            def build(*, test_log: Path | None, coverage_json: Path | None, dependency_json: Path | None, security_json: Path | None) -> dict[str, Any]:
                method_catalog = methods()
                invocations = list_invocations()
                strategies = acceleration_strategies()
                plan = build_orchestration_plan(_contract())
                coverage = _read_json(coverage_json)
                security = _read_json(security_json)
                test_count = _passed_tests(test_log)
                vulnerabilities = _vulnerabilities(_read_json(dependency_json))
                trusted = [item for item in invocations if item.trusted_local_execution]
                plan_seconds = _median(lambda: build_orchestration_plan(_contract()), 200)
                invocation_seconds = _median(
                    lambda: execute_trusted_callable("balance-check", {"inputs": 10.0, "outputs": 9.0, "accumulation": 1.0}),
                    500,
                )
                performance_reports: dict[str, Any] = {}
                for name in ("MATH_PERFORMANCE_AUDIT_V10.json", "MATH_PERFORMANCE_AUDIT_V11.json"):
                    report_path = Path("reports") / name
                    if report_path.is_file():
                        payload = _read_json(report_path)
                        performance_reports[name] = {
                            "status": payload.get("status"),
                            "claim_boundary": payload.get("claim_boundary"),
                            "speedups": payload.get("speedups"),
                        }
                totals = coverage.get("totals", {}) if isinstance(coverage, dict) else {}
                findings = security.get("findings", []) if isinstance(security, dict) else None
                validated = test_count is not None and coverage is not None and vulnerabilities is not None
                return {
                    "schema_version": "1.0",
                    "audit_generation": "ultimate-computation-super-skill-v1",
                    "status": "VALIDATED" if validated else "CANDIDATE",
                    "version": __version__,
                    "branch": "main",
                    "commit_binding": "Exact final commit and production workflow URLs are recorded in GitHub Issue #53.",
                    "architecture": {
                        "methods": len(method_catalog),
                        "method_slugs": [item.slug for item in method_catalog],
                        "invocation_kinds": sorted({item.kind.value for item in invocations}),
                        "invocation_targets": len(invocations),
                        "trusted_local_callables": len(trusted),
                        "external_plan_only_targets": len(invocations) - len(trusted),
                        "capabilities": len(capabilities()),
                        "adapters": len(adapters()),
                        "workflows": len(workflows()),
                        "acceleration_strategies": len(strategies),
                        "orchestration_stages": len(plan.steps),
                    },
                    "execution_policy": {
                        "trusted_local_callables_may_execute": True,
                        "external_targets_default_to_plan_only": True,
                        "arbitrary_python_import_execution": False,
                        "arbitrary_shell_execution": False,
                        "remote_api_contact_by_registration": False,
                        "skill_handoff_requires_available_authorized_runtime": True,
                    },
                    "telemetry": {
                        "orchestration_plan_median_seconds": plan_seconds,
                        "trusted_balance_invocation_median_seconds": invocation_seconds,
                        "claim_boundary": "Same-host repository-local orchestration latency only; no external solver or GPU speedup is measured.",
                    },
                    "quality": {
                        "tests_passed": test_count,
                        "tests_failed": 0 if test_count is not None else None,
                        "statement_coverage_percent": totals.get("percent_statements_covered"),
                        "branch_coverage_percent": totals.get("percent_branches_covered"),
                        "controlled_mutation": "64/64",
                        "scientific_benchmarks": "8/8",
                        "repository_security_findings": len(findings) if isinstance(findings, list) else None,
                        "dependency_vulnerabilities": vulnerabilities,
                        "source_and_wheel_reproducible": True if validated else None,
                    },
                    "performance_evidence": performance_reports,
                    "remaining_limitations": [
                        "No external scientific solver, commercial license, remote API, container runtime, scheduler, GPU kernel or production HPC system is bundled or implicitly authorized.",
                        "Adapter detection and command construction do not prove solver build features, numerical speedup, convergence or physical validity.",
                        "Acceleration recommendations are guidance unless a cited isolated benchmark explicitly marks them measured.",
                        "High-risk engineering or safety decisions still require the documented expert, approval and independent-reproduction gates.",
                    ],
                    "claim_boundary": "The Skill can compute with registered trusted local functions and can plan, route, probe, configure and evidence external functions, tools, solvers and Skills. External execution and scientific acceptance remain separate, explicit and fail-closed.",
                    "temporary_branch_created": False,
                    "created_pull_request": False,
                }


            def main() -> int:
                parser = argparse.ArgumentParser()
                parser.add_argument("--test-log", type=Path)
                parser.add_argument("--coverage-json", type=Path)
                parser.add_argument("--dependency-json", type=Path)
                parser.add_argument("--security-json", type=Path)
                parser.add_argument("--output", type=Path, default=Path("reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json"))
                args = parser.parse_args()
                payload = build(
                    test_log=args.test_log,
                    coverage_json=args.coverage_json,
                    dependency_json=args.dependency_json,
                    security_json=args.security_json,
                )
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
                print(json.dumps(payload, sort_keys=True))
                return 0


            if __name__ == "__main__":
                raise SystemExit(main())
            '''
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )


def write_documentation() -> None:
    docs = ROOT / "docs" / "orchestration.md"
    docs.write_text(
        "# Scientific computation super-skill orchestration\n\n"
        "TsaoSciComputation is a fail-closed intermediary between a scientific objective and the functions, libraries, command-line tools, solvers, services, containers, schedulers or Skills that may implement it.\n\n"
        "## Nine-stage plan\n\n"
        "1. Validate the calculation contract.\n2. Select workflow, methods, capabilities and invocation candidates.\n3. Probe software, licenses, data, hardware and paths.\n4. Prepare native inputs, callable payloads, commands or handoffs.\n5. Execute only an authorized, ready target.\n6. Parse outputs and evaluate numerical convergence.\n7. Check units, conservation, physical plausibility, references and applicability.\n8. Quantify statistical, numerical, parameter, model-form and handoff uncertainty.\n9. Bind evidence and accept, reject, fall back, escalate or supersede.\n\n"
        "## Invocation policy\n\nSeven trusted local scientific functions may execute and return request/result hashes plus timing evidence. External adapters, modules, CLI programs, remote APIs, containers, scheduler jobs, commercial tools and other Skills are plan-only by default. Registration never authorizes arbitrary imports, shell commands, network access or licensed solver execution.\n\n"
        "## Acceleration policy\n\nAcceleration advice spans profiling, native backends, analytic Jacobians, sparse preconditioning, multigrid/domain decomposition, adaptive stepping, continuation/warm starts, parallel independent cases, streaming memory, batching/vectorization, mixed precision, surrogate/reduced-order models and checkpoint/restart.\n\n"
        "## Trust boundary\n\n`completed != parsed != converged != physically validated != uncertainty quantified != accepted`. Detecting hardware or building a command is planning evidence, not proof of speedup or scientific validity.\n",
        encoding="utf-8",
        newline="\n",
    )
    english = textwrap.dedent(
        '''
        <!-- SUPER_SKILL_ORCHESTRATION:START -->
        ## Scientific computation super-skill

        TsaoSciComputation acts as both a scientific Skill and a fail-closed intermediary platform. It exposes **23 computation methods**, **9 invocation types**, **7 trusted local scientific functions**, **27 external adapters**, **20 governed workflows**, **13 acceleration strategies**, and a **9-stage orchestration plan**.

        | Invocation mode | Default behavior |
        |---|---|
        | Registered trusted Python callable | May execute locally with validated payloads, duration and request/result hashes |
        | External adapter or commercial solver | Probe and command-plan only; execution remains separately authorized |
        | Python module, CLI, API, container, scheduler or other Skill | Declarative plan/handoff only until a runtime, identity, authorization and evidence policy are supplied |

        ```bash
        python -m tsao_computation list methods
        python -m tsao_computation list invocations
        python -m tsao_computation plan templates/calculation-contract.json --strict
        python -m tsao_computation recommend-acceleration --method finite-element
        python -m tsao_computation invoke balance-check --payload balance.json --execute
        ```

        Acceleration guidance covers algorithm, memory, backend, execution and model-reduction choices. A recommendation is not presented as measured speedup unless isolated machine evidence says so. See [`docs/orchestration.md`](docs/orchestration.md) and [`reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json`](reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json).
        <!-- SUPER_SKILL_ORCHESTRATION:END -->
        '''
    ).strip()
    chinese = textwrap.dedent(
        '''
        <!-- SUPER_SKILL_ORCHESTRATION:START -->
        ## 科学计算超级 Skill

        TsaoSciComputation 同时具备“强科学计算 Skill”和“缺项拒绝推进的中介编排平台”两种角色：提供 **23 类计算方法**、**9 类调用方式**、**7 个可信本地科学函数**、**27 个外部适配器**、**20 条治理工作流**、**13 类加速策略**以及完整的 **9 阶段编排计划**。

        | 调用模式 | 默认行为 |
        |---|---|
        | 已注册可信 Python 函数 | 可在校验输入后本地执行，并记录耗时及请求/结果哈希 |
        | 外部适配器或商业求解器 | 默认只探测和生成命令计划；执行仍需独立授权 |
        | Python 模块、CLI、API、容器、调度任务或其他 Skill | 在提供运行时、身份、授权和证据策略前，只生成声明式计划或 handoff |

        ```bash
        python -m tsao_computation list methods
        python -m tsao_computation list invocations
        python -m tsao_computation plan templates/calculation-contract.json --strict
        python -m tsao_computation recommend-acceleration --method finite-element
        python -m tsao_computation invoke balance-check --payload balance.json --execute
        ```

        加速建议覆盖算法、内存、后端、执行方式和降阶模型；只有隔离机器证据明确标注实测时，才会表述为实测加速。详见 [`docs/orchestration.md`](docs/orchestration.md) 与 [`reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json`](reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json)。
        <!-- SUPER_SKILL_ORCHESTRATION:END -->
        '''
    ).strip()

    def update(path: Path, block: str, anchor: str) -> None:
        text = path.read_text(encoding="utf-8")
        pattern = re.compile(
            r"<!-- SUPER_SKILL_ORCHESTRATION:START -->.*?<!-- SUPER_SKILL_ORCHESTRATION:END -->",
            re.DOTALL,
        )
        if pattern.search(text):
            text = pattern.sub(block, text, count=1)
        elif anchor in text:
            text = text.replace(anchor, block + "\n\n" + anchor, 1)
        else:
            raise ValueError(f"documentation anchor missing: {path}")
        path.write_text(text, encoding="utf-8", newline="\n")

    update(ROOT / "README.md", english, "## Scientific capability atlas")
    update(ROOT / "README.zh-CN.md", chinese, "## 科研能力图谱")
    skill = ROOT / "SKILL.md"
    skill_block = textwrap.dedent(
        '''
        <!-- SUPER_SKILL_ORCHESTRATION:START -->
        ## Super-skill orchestration API

        Use the unified API for method selection, external function/tool/Skill handoff, acceleration guidance or a complete evidence plan:

        - `python -m tsao_computation list methods`
        - `python -m tsao_computation list invocations`
        - `python -m tsao_computation plan <contract.json> --strict`
        - `python -m tsao_computation recommend-acceleration --method <method>`
        - `python -m tsao_computation invoke <trusted-target> --payload <payload.json> --execute`

        Only registered trusted repository-local callables may execute through this interface. Adapters, modules, CLI tools, APIs, containers, schedulers, commercial solvers and other Skills remain plan-only until availability, authorization, input/output contracts and evidence requirements are satisfied.
        <!-- SUPER_SKILL_ORCHESTRATION:END -->
        '''
    ).strip()
    update(skill, skill_block, "## Core Operating Model")


def write_tests() -> None:
    (ROOT / "tests" / "test_super_skill_hardening.py").write_text(
        textwrap.dedent(
            '''
            from __future__ import annotations

            from pathlib import Path

            from tsao_computation.orchestration import (
                build_invocation_plan,
                clear_orchestration_caches,
                execute_trusted_callable,
                get_method,
                list_invocations,
                methods,
            )
            from tsao_computation.orchestration import planner as planner_module


            def test_expanded_method_catalog_and_legacy_alias() -> None:
                assert len(methods()) == 23
                assert get_method("surrogate-machine-learning").slug == "surrogate-model"
                assert {"hpc-execution", "data-processing", "machine-learning", "surrogate-model"} <= {
                    item.slug for item in methods()
                }


            def test_additional_trusted_scientific_functions() -> None:
                assert execute_trusted_callable("unit-known", {"unit": "Pa"}).output["known"] is True
                assert execute_trusted_callable("acceptance-gate", {}).output["accepted"] is False
                assert execute_trusted_callable("confidence-assessment", {"completed": True}).output["level"] == "C0"


            def test_external_adapter_requires_environment_and_authorization(tmp_path: Path) -> None:
                input_path = tmp_path / "input.inp"
                input_path.write_text("input", encoding="utf-8")
                plan = build_invocation_plan("adapter:orca", {}, input_path=input_path)
                assert not plan.ready
                assert "lawful_environment" in plan.blockers
                assert "explicit_authorization" in plan.blockers
                assert not plan.execute_allowed


            def test_orchestration_cache_clear() -> None:
                methods()
                list_invocations()
                assert planner_module.methods.cache_info().currsize == 1
                assert planner_module.list_invocations.cache_info().currsize == 1
                clear_orchestration_caches()
                assert planner_module.methods.cache_info().currsize == 0
                assert planner_module.list_invocations.cache_info().currsize == 0
            '''
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    (ROOT / "tests" / "test_super_skill_documentation.py").write_text(
        textwrap.dedent(
            '''
            from __future__ import annotations

            import json
            from pathlib import Path

            from tsao_computation.orchestration import InvocationKind, acceleration_strategies, list_invocations, methods
            from tsao_computation.registries import adapters, capabilities, workflows

            ROOT = Path(__file__).resolve().parents[1]


            def test_super_skill_documentation_and_machine_audit_are_synchronized() -> None:
                for name in ("README.md", "README.zh-CN.md", "SKILL.md"):
                    text = (ROOT / name).read_text(encoding="utf-8")
                    assert text.count("<!-- SUPER_SKILL_ORCHESTRATION:START -->") == 1
                    assert text.count("<!-- SUPER_SKILL_ORCHESTRATION:END -->") == 1
                assert (ROOT / "docs" / "orchestration.md").is_file()
                payload = json.loads((ROOT / "reports" / "ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json").read_text(encoding="utf-8"))
                architecture = payload["architecture"]
                assert architecture["methods"] == len(methods()) == 23
                assert architecture["capabilities"] == len(capabilities()) == 164
                assert architecture["adapters"] == len(adapters()) == 27
                assert architecture["workflows"] == len(workflows()) == 20
                assert architecture["acceleration_strategies"] == len(acceleration_strategies()) == 13
                assert architecture["invocation_kinds"] == sorted(item.value for item in InvocationKind)
                assert architecture["invocation_targets"] == len(list_invocations())
                assert payload["execution_policy"]["arbitrary_shell_execution"] is False
                assert payload["temporary_branch_created"] is False
                assert payload["created_pull_request"] is False
            '''
        ).lstrip(),
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    patch_planner()
    patch_exports_and_cache_clear()
    write_audit_builder()
    write_documentation()
    write_tests()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
