from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sub_once(text: str, pattern: str, replacement: str, *, label: str, flags: int = 0) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise ValueError(f"expected exactly one match for {label}; found {count}")
    return updated


def patch_planner() -> None:
    path = ROOT / "tsao_computation" / "orchestration" / "planner.py"
    text = path.read_text(encoding="utf-8")

    text = sub_once(
        text,
        r"from \.\.validation import balance_check, convergence_check\n",
        "from ..validation import (\n"
        "    acceptance_gate,\n"
        "    assess_confidence,\n"
        "    balance_check,\n"
        "    convergence_check,\n"
        "    unit_known,\n"
        ")\n",
        label="validation imports",
    )

    method_pattern = (
        r'\n        _method\(\s*'
        r'"surrogate-machine-learning",\s*'
        r'"Surrogate and machine learning",\s*'
        r'"machine-learning",\s*'
        r'\("data", "all"\),\s*'
        r'local \+ service,\s*'
        r'\("batched training", "GPU tensor cores", "quantized inference"\),\s*'
        r'\),'
    )
    method_replacement = "\n" + textwrap.dedent(
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
    ).rstrip()
    text = sub_once(text, method_pattern, method_replacement, label="method catalog expansion")

    get_method_pattern = (
        r'def get_method\(slug: str\) -> MethodSpec:\n'
        r'    try:\n'
        r'        return _method_index\(\)\[slug\.strip\(\)\.casefold\(\)\.replace\("_", "-"\)\]\n'
    )
    get_method_replacement = (
        'def get_method(slug: str) -> MethodSpec:\n'
        '    normalized = slug.strip().casefold().replace("_", "-").replace(" ", "-")\n'
        '    normalized = {"surrogate-machine-learning": "surrogate-model"}.get(\n'
        '        normalized, normalized\n'
        '    )\n'
        '    try:\n'
        '        return _method_index()[normalized]\n'
    )
    text = sub_once(text, get_method_pattern, get_method_replacement, label="method aliases")

    benchmark_anchor = (
        'def _invoke_benchmarks(payload: Mapping[str, Any]) -> object:\n'
        '    if payload:\n'
        '        raise ContractError("scientific-benchmarks accepts an empty payload")\n'
        '    return [item.to_dict() for item in run_all()]\n\n\n'
    )
    if benchmark_anchor not in text:
        raise ValueError("scientific benchmark callable anchor not found")
    extra_functions = (
        'def _invoke_unit_known(payload: Mapping[str, Any]) -> object:\n'
        '    unit = payload.get("unit")\n'
        '    if not isinstance(unit, str) or not unit.strip():\n'
        '        raise ContractError("unit must be a non-empty string")\n'
        '    return {"unit": unit, "known": unit_known(unit)}\n\n\n'
        'def _invoke_acceptance(payload: Mapping[str, Any]) -> object:\n'
        '    return acceptance_gate(dict(payload))\n\n\n'
        'def _invoke_confidence(payload: Mapping[str, Any]) -> object:\n'
        '    return assess_confidence(payload).to_dict()\n\n\n'
    )
    text = text.replace(benchmark_anchor, benchmark_anchor + extra_functions, 1)

    callable_anchor = (
        '    "scientific-benchmarks": (\n'
        '        "Deterministic scientific reference benchmarks",\n'
        '        _invoke_benchmarks,\n'
        '        (),\n'
        '    ),\n'
    )
    if callable_anchor not in text:
        raise ValueError("trusted callable registry anchor not found")
    callable_additions = (
        '    "unit-known": ("Scientific unit registry lookup", _invoke_unit_known, ("unit",)),\n'
        '    "acceptance-gate": ("Fail-closed scientific acceptance gate", _invoke_acceptance, ()),\n'
        '    "confidence-assessment": (\n'
        '        "Scientific confidence ladder assessment",\n'
        '        _invoke_confidence,\n'
        '        (),\n'
        '    ),\n'
    )
    text = text.replace(callable_anchor, callable_anchor + callable_additions, 1)

    text = sub_once(
        text,
        r"    blockers = tuple\(key for key in spec\.required_inputs if key not in normalized_payload\)\n",
        "    blockers = tuple(\n"
        "        key\n"
        "        for key in spec.required_inputs\n"
        "        if key not in normalized_payload or normalized_payload[key] is None\n"
        "    )\n",
        label="required input validation",
    )

    adapter_start = text.index('    if slug.startswith("adapter:"):\n')
    generic_marker = (
        '    return InvocationPlan(\n'
        '        slug=spec.slug,\n'
        '        kind=spec.kind,\n'
        '        target=spec.target,\n'
        '        ready=False,\n'
        '        execute_allowed=False,\n'
        '        argv=(),\n'
        '        cwd=None,\n'
        '        environment={},\n'
        '        blockers=("runtime target, availability probe and explicit authorization are required",),\n'
    )
    adapter_end = text.index(generic_marker, adapter_start)
    hardened_adapter = textwrap.dedent(
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
    text = text[:adapter_start] + hardened_adapter + text[adapter_end:]

    digital_old = '("digital", ("digital-twin", "surrogate-machine-learning")),\n'
    hpc_old = '("hpc", ("sparse-linear-algebra", "monte-carlo")),\n'
    if digital_old not in text or hpc_old not in text:
        raise ValueError("workflow method mapping anchors not found")
    text = text.replace(
        digital_old,
        '("digital", ("digital-twin", "surrogate-model")),\n',
        1,
    ).replace(
        hpc_old,
        '("hpc", ("hpc-execution", "sparse-linear-algebra", "monte-carlo")),\n'
        '        ("data", ("data-processing", "statistical-inference")),\n',
        1,
    )

    text = sub_once(
        text,
        r"def recommend_acceleration\(\n",
        "def acceleration_strategies() -> tuple[AccelerationAdvice, ...]:\n"
        "    return tuple(item[0] for item in _STRATEGIES)\n\n\n"
        "def recommend_acceleration(\n",
        label="acceleration strategy catalog",
    )

    if "def clear_orchestration_caches()" not in text:
        text += (
            "\n\ndef clear_orchestration_caches() -> None:\n"
            "    methods.cache_clear()\n"
            "    _method_index.cache_clear()\n"
            "    list_invocations.cache_clear()\n"
        )
    path.write_text(text, encoding="utf-8", newline="\n")


def patch_exports_and_registry_clear() -> None:
    init_path = ROOT / "tsao_computation" / "orchestration" / "__init__.py"
    text = init_path.read_text(encoding="utf-8")
    text = text.replace(
        "    build_invocation_plan,\n",
        "    acceleration_strategies,\n    build_invocation_plan,\n",
        1,
    ).replace(
        "    build_orchestration_plan,\n",
        "    build_orchestration_plan,\n    clear_orchestration_caches,\n",
        1,
    ).replace(
        '    "build_invocation_plan",\n',
        '    "acceleration_strategies",\n    "build_invocation_plan",\n',
        1,
    ).replace(
        '    "build_orchestration_plan",\n',
        '    "build_orchestration_plan",\n    "clear_orchestration_caches",\n',
        1,
    )
    init_path.write_text(text, encoding="utf-8", newline="\n")

    loader = ROOT / "tsao_computation" / "registries" / "loader.py"
    loader_text = loader.read_text(encoding="utf-8")
    if "clear_orchestration_caches" not in loader_text:
        loader_text = loader_text.replace(
            "    from ..routing.router import clear_routing_caches\n",
            "    from ..orchestration import clear_orchestration_caches\n"
            "    from ..routing.router import clear_routing_caches\n",
            1,
        ).replace(
            "    clear_routing_caches()\n",
            "    clear_routing_caches()\n    clear_orchestration_caches()\n",
            1,
        )
    loader.write_text(loader_text, encoding="utf-8", newline="\n")


def patch_existing_tests() -> None:
    path = ROOT / "tests" / "test_super_skill_orchestration.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace("assert len(catalog) == 20", "assert len(catalog) == 23")
    text = text.replace("assert len(listed) == 20", "assert len(listed) == 23")
    text = text.replace(
        'assert missing_input.blockers == ("native_input_file",)',
        'assert set(missing_input.blockers) == {\n'
        '        "native_input_file",\n'
        '        "lawful_environment",\n'
        '        "explicit_authorization",\n'
        '    }',
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def patch_docs() -> None:
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
    update(ROOT / "SKILL.md", skill_block, "## Core Operating Model")


if __name__ == "__main__":
    patch_planner()
    patch_exports_and_registry_clear()
    patch_existing_tests()
    patch_docs()
