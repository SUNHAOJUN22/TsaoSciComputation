from __future__ import annotations

import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(relative: str, content: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8", newline="\n")


def replace_function(text: str, name: str, replacement: str) -> str:
    pattern = rf"(?ms)^def {re.escape(name)}\(.*?(?=^(?:def |@|_STRATEGIES\b))"
    updated, count = re.subn(pattern, textwrap.dedent(replacement).lstrip(), text, count=1)
    if count != 1:
        raise ValueError(f"function replacement failed for {name}: {count}")
    return updated


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"expected one {label}, found {count}")
    return text.replace(old, new, 1)


write(
    "tsao_computation/immutable.py",
    r'''
    from __future__ import annotations

    from collections.abc import Mapping
    from typing import Any


    class FrozenDict(dict[str, Any]):
        """JSON-compatible dictionary that rejects in-place mutation."""

        __slots__ = ()

        def _immutable(self, *_: object, **__: object) -> None:
            raise TypeError("immutable mapping cannot be modified")

        __setitem__ = _immutable
        __delitem__ = _immutable
        clear = _immutable
        pop = _immutable
        popitem = _immutable
        setdefault = _immutable
        update = _immutable
        __ior__ = _immutable

        def __copy__(self) -> FrozenDict:
            return self

        def __deepcopy__(self, memo: dict[int, object]) -> FrozenDict:
            return self


    class FrozenList(list[Any]):
        """JSON-compatible list that rejects in-place mutation."""

        __slots__ = ()

        def _immutable(self, *_: object, **__: object) -> None:
            raise TypeError("immutable sequence cannot be modified")

        __setitem__ = _immutable
        __delitem__ = _immutable
        __iadd__ = _immutable
        __imul__ = _immutable
        append = _immutable
        clear = _immutable
        extend = _immutable
        insert = _immutable
        pop = _immutable
        remove = _immutable
        reverse = _immutable
        sort = _immutable

        def __copy__(self) -> FrozenList:
            return self

        def __deepcopy__(self, memo: dict[int, object]) -> FrozenList:
            return self


    def freeze_json(value: Any) -> Any:
        if isinstance(value, FrozenDict | FrozenList):
            return value
        if isinstance(value, Mapping):
            return FrozenDict({str(key): freeze_json(item) for key, item in value.items()})
        if isinstance(value, list):
            return FrozenList(freeze_json(item) for item in value)
        if isinstance(value, tuple):
            return tuple(freeze_json(item) for item in value)
        return value


    def thaw_json(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {str(key): thaw_json(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [thaw_json(item) for item in value]
        return value
    ''',
)

write(
    "tsao_computation/contracts/calculation.py",
    r'''
    from __future__ import annotations

    from collections.abc import Iterable, Mapping
    from dataclasses import dataclass, field
    from typing import Any, ClassVar

    from ..errors import ContractError
    from ..immutable import FrozenDict, freeze_json, thaw_json


    def _required_string(value: object, *, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ContractError(f"{field_name} must be a non-empty string")
        return value.strip()


    def _slug(value: object, *, field_name: str) -> str:
        return _required_string(value, field_name=field_name).casefold().replace("_", "-").replace(" ", "-")


    def _optional_slug(value: object, *, field_name: str) -> str | None:
        return None if value is None else _slug(value, field_name=field_name)


    def _mapping(value: object, *, field_name: str) -> FrozenDict:
        if not isinstance(value, Mapping):
            raise ContractError(f"{field_name} must be an object")
        if any(not isinstance(key, str) for key in value):
            raise ContractError(f"{field_name} keys must be strings")
        return freeze_json(dict(value))


    def _string_tuple(value: object, *, field_name: str, slugs: bool = False) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, str):
            values: Iterable[object] = (value,)
        elif isinstance(value, Mapping) or not isinstance(value, Iterable):
            raise ContractError(f"{field_name} must be a string or an array of strings")
        else:
            values = value
        normalized: list[str] = []
        for item in values:
            parsed = _slug(item, field_name=field_name) if slugs else _required_string(item, field_name=field_name)
            if parsed not in normalized:
                normalized.append(parsed)
        return tuple(normalized)


    def _mapping_tuple(value: object, *, field_name: str) -> tuple[FrozenDict, ...]:
        if value is None:
            return ()
        if isinstance(value, (str, bytes, Mapping)) or not isinstance(value, Iterable):
            raise ContractError(f"{field_name} must be an array of objects")
        result: list[FrozenDict] = []
        for item in value:
            normalized = _mapping(item, field_name=field_name)
            if not normalized:
                raise ContractError(f"{field_name} must not contain empty objects")
            result.append(normalized)
        return tuple(result)


    @dataclass(frozen=True, slots=True)
    class CalculationContract:
        question: str
        system: dict[str, Any]
        conditions: dict[str, Any]
        target_observables: tuple[str, ...]
        workflow: str | None = None
        assumptions: tuple[str, ...] = ()
        acceptance_criteria: dict[str, Any] = field(default_factory=FrozenDict)
        model_object: dict[str, Any] = field(default_factory=FrozenDict)
        scales: tuple[str, ...] = ()
        methods: tuple[str, ...] = ()
        boundary_conditions: dict[str, Any] = field(default_factory=FrozenDict)
        initial_conditions: dict[str, Any] = field(default_factory=FrozenDict)
        parameter_sources: tuple[dict[str, Any], ...] = ()
        convergence_plan: dict[str, Any] = field(default_factory=FrozenDict)
        validation_plan: dict[str, Any] = field(default_factory=FrozenDict)
        uncertainty_sources: tuple[str, ...] = ()
        compute_resources: dict[str, Any] = field(default_factory=FrozenDict)
        expected_artifacts: tuple[str, ...] = ()
        human_approval_nodes: tuple[str, ...] = ()
        schema_version: str = "1.0"

        PREFLIGHT_FIELDS: ClassVar[tuple[str, ...]] = (
            "assumptions", "model_object", "scales", "methods", "boundary_conditions",
            "initial_conditions", "parameter_sources", "convergence_plan", "validation_plan",
            "uncertainty_sources", "compute_resources", "expected_artifacts",
            "human_approval_nodes", "acceptance_criteria",
        )
        ALLOWED_FIELDS: ClassVar[frozenset[str]] = frozenset({
            "question", "system", "conditions", "target_observables", "workflow", "assumptions",
            "acceptance_criteria", "model_object", "scales", "scale", "methods", "method",
            "boundary_conditions", "initial_conditions", "parameter_sources", "convergence_plan",
            "validation_plan", "uncertainty_sources", "compute_resources", "expected_artifacts",
            "human_approval_nodes", "schema_version",
        })

        def __post_init__(self) -> None:
            normalized = {
                "question": _required_string(self.question, field_name="question"),
                "system": _mapping(self.system, field_name="system"),
                "conditions": _mapping(self.conditions, field_name="conditions"),
                "target_observables": _string_tuple(self.target_observables, field_name="target_observables"),
                "workflow": _optional_slug(self.workflow, field_name="workflow"),
                "assumptions": _string_tuple(self.assumptions, field_name="assumptions"),
                "acceptance_criteria": _mapping(self.acceptance_criteria, field_name="acceptance_criteria"),
                "model_object": _mapping(self.model_object, field_name="model_object"),
                "scales": _string_tuple(self.scales, field_name="scales", slugs=True),
                "methods": _string_tuple(self.methods, field_name="methods", slugs=True),
                "boundary_conditions": _mapping(self.boundary_conditions, field_name="boundary_conditions"),
                "initial_conditions": _mapping(self.initial_conditions, field_name="initial_conditions"),
                "parameter_sources": _mapping_tuple(self.parameter_sources, field_name="parameter_sources"),
                "convergence_plan": _mapping(self.convergence_plan, field_name="convergence_plan"),
                "validation_plan": _mapping(self.validation_plan, field_name="validation_plan"),
                "uncertainty_sources": _string_tuple(self.uncertainty_sources, field_name="uncertainty_sources"),
                "compute_resources": _mapping(self.compute_resources, field_name="compute_resources"),
                "expected_artifacts": _string_tuple(self.expected_artifacts, field_name="expected_artifacts"),
                "human_approval_nodes": _string_tuple(self.human_approval_nodes, field_name="human_approval_nodes"),
                "schema_version": _required_string(self.schema_version, field_name="schema_version"),
            }
            if not normalized["system"]:
                raise ContractError("system definition must be non-empty")
            if not normalized["target_observables"]:
                raise ContractError("at least one target observable is required")
            for name, value in normalized.items():
                object.__setattr__(self, name, value)

        @classmethod
        def from_dict(cls, data: Mapping[str, Any]) -> CalculationContract:
            if not isinstance(data, Mapping):
                raise ContractError("calculation contract must be an object")
            if any(not isinstance(key, str) for key in data):
                raise ContractError("contract field names must be strings")
            missing = sorted({"question", "system", "conditions", "target_observables"} - data.keys())
            if missing:
                raise ContractError(f"missing contract fields: {missing}")
            unknown = sorted(set(data) - cls.ALLOWED_FIELDS)
            if unknown:
                raise ContractError(f"unknown contract fields: {unknown}")
            return cls(
                question=data["question"], system=data["system"], conditions=data["conditions"],
                target_observables=data["target_observables"], workflow=data.get("workflow"),
                assumptions=data.get("assumptions", ()), acceptance_criteria=data.get("acceptance_criteria", {}),
                model_object=data.get("model_object", {}), scales=data.get("scales", data.get("scale", ())),
                methods=data.get("methods", data.get("method", ())),
                boundary_conditions=data.get("boundary_conditions", {}),
                initial_conditions=data.get("initial_conditions", {}),
                parameter_sources=data.get("parameter_sources", ()),
                convergence_plan=data.get("convergence_plan", {}), validation_plan=data.get("validation_plan", {}),
                uncertainty_sources=data.get("uncertainty_sources", ()), compute_resources=data.get("compute_resources", {}),
                expected_artifacts=data.get("expected_artifacts", ()),
                human_approval_nodes=data.get("human_approval_nodes", ()),
                schema_version=data.get("schema_version", "1.0"),
            )

        def specification_gaps(self) -> tuple[str, ...]:
            return tuple(name for name in self.PREFLIGHT_FIELDS if not getattr(self, name))

        def assert_ready_for_preflight(self) -> None:
            gaps = self.specification_gaps()
            if gaps:
                raise ContractError(f"contract is not ready for preflight; missing fields: {list(gaps)}")

        def to_dict(self) -> dict[str, Any]:
            return {
                "question": self.question, "system": thaw_json(self.system), "conditions": thaw_json(self.conditions),
                "target_observables": list(self.target_observables), "workflow": self.workflow,
                "assumptions": list(self.assumptions), "acceptance_criteria": thaw_json(self.acceptance_criteria),
                "model_object": thaw_json(self.model_object), "scales": list(self.scales), "methods": list(self.methods),
                "boundary_conditions": thaw_json(self.boundary_conditions),
                "initial_conditions": thaw_json(self.initial_conditions),
                "parameter_sources": [thaw_json(item) for item in self.parameter_sources],
                "convergence_plan": thaw_json(self.convergence_plan), "validation_plan": thaw_json(self.validation_plan),
                "uncertainty_sources": list(self.uncertainty_sources), "compute_resources": thaw_json(self.compute_resources),
                "expected_artifacts": list(self.expected_artifacts),
                "human_approval_nodes": list(self.human_approval_nodes), "schema_version": self.schema_version,
            }
    ''',
)

write(
    "tsao_computation/registries/loader.py",
    r'''
    from __future__ import annotations

    import json
    from functools import cache
    from typing import Any, cast

    from ..immutable import freeze_json
    from ..paths import REGISTRY_ROOT

    _RESOLVED_REGISTRY_ROOT = REGISTRY_ROOT.resolve()


    @cache
    def _load(name: str) -> tuple[Any, ...] | dict[str, Any]:
        path = (_RESOLVED_REGISTRY_ROOT / name).resolve()
        if path.parent != _RESOLVED_REGISTRY_ROOT:
            raise ValueError("registry path escaped root")
        data = freeze_json(json.loads(path.read_bytes()))
        return tuple(data) if isinstance(data, list) else data


    def capabilities() -> tuple[dict[str, Any], ...]:
        return cast(tuple[dict[str, Any], ...], _load("capabilities.json"))


    def adapters() -> tuple[dict[str, Any], ...]:
        return cast(tuple[dict[str, Any], ...], _load("adapters.json"))


    def accelerators() -> tuple[dict[str, Any], ...]:
        return cast(tuple[dict[str, Any], ...], _load("accelerators.json"))


    def workflows() -> tuple[dict[str, Any], ...]:
        return cast(tuple[dict[str, Any], ...], _load("workflows.json"))


    def units() -> dict[str, Any]:
        return cast(dict[str, Any], _load("units.json"))


    def clear_registry_caches() -> None:
        from ..accelerators.planner import clear_acceleration_caches
        from ..adapters.registry import clear_adapter_caches
        from ..orchestration import clear_orchestration_caches
        from ..routing.router import clear_routing_caches
        from ..validation.physical import clear_unit_cache

        clear_acceleration_caches()
        clear_adapter_caches()
        clear_routing_caches()
        clear_orchestration_caches()
        clear_unit_cache()
        _load.cache_clear()
    ''',
)

write(
    "tsao_computation/validation/physical.py",
    r'''
    from __future__ import annotations

    import math
    from functools import cache

    from ..registries import units


    @cache
    def _accepted_units() -> frozenset[str]:
        return frozenset(str(item) for record in units().values() for item in record["accepted"])


    def clear_unit_cache() -> None:
        _accepted_units.cache_clear()


    def unit_known(unit: str) -> bool:
        return isinstance(unit, str) and bool(unit.strip()) and unit.strip() in _accepted_units()


    def _number(value: object, *, name: str) -> float:
        if isinstance(value, bool):
            raise ValueError(f"{name} must be a finite number, not a boolean")
        try:
            converted = float(value)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"{name} must be a finite number") from error
        if not math.isfinite(converted):
            raise ValueError(f"{name} must be a finite number")
        return converted


    def balance_check(
        inputs: float, outputs: float, accumulation: float = 0.0, *, tolerance: float = 1e-08
    ) -> dict[str, float | bool]:
        input_value = _number(inputs, name="inputs")
        output_value = _number(outputs, name="outputs")
        accumulation_value = _number(accumulation, name="accumulation")
        tolerance_value = _number(tolerance, name="tolerance")
        if tolerance_value < 0:
            raise ValueError("tolerance must be non-negative")
        try:
            residual = math.fsum((input_value, -output_value, -accumulation_value))
        except OverflowError as error:
            raise ValueError("balance residual must be finite") from error
        if not math.isfinite(residual):
            raise ValueError("balance residual must be finite")
        scale = max(abs(input_value), abs(output_value), abs(accumulation_value), 1.0)
        normalized = abs(residual) / scale
        return {
            "passed": normalized <= tolerance_value,
            "residual": residual,
            "normalized_residual": normalized,
            "tolerance": tolerance_value,
        }
    ''',
)

write(
    "tsao_computation/uncertainty/model.py",
    r'''
    from __future__ import annotations

    import math
    from dataclasses import dataclass


    def _component(value: object) -> float:
        if isinstance(value, bool):
            raise ValueError("uncertainty components must be finite non-negative numbers")
        try:
            converted = float(value)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("uncertainty components must be finite non-negative numbers") from error
        if converted < 0 or not math.isfinite(converted):
            raise ValueError("uncertainty components must be finite and non-negative")
        return converted


    @dataclass(frozen=True, slots=True)
    class UncertaintyBudget:
        statistical: float
        model: float
        numerical: float
        unit: str

        def __post_init__(self) -> None:
            object.__setattr__(self, "statistical", _component(self.statistical))
            object.__setattr__(self, "model", _component(self.model))
            object.__setattr__(self, "numerical", _component(self.numerical))
            if not isinstance(self.unit, str) or not self.unit.strip():
                raise ValueError("uncertainty unit must be a non-empty string")
            object.__setattr__(self, "unit", self.unit.strip())

        @property
        def combined(self) -> float:
            return combine_independent(self.statistical, self.model, self.numerical)


    def combine_independent(*components: float) -> float:
        return math.hypot(*(_component(value) for value in components))
    ''',
)

write(
    "tsao_computation/adapters/base.py",
    r'''
    from __future__ import annotations

    import hashlib
    import json
    import os
    import re
    import shutil
    import subprocess  # nosec B404
    import sys
    from dataclasses import dataclass
    from pathlib import Path
    from typing import Any

    from ..errors import ContractError
    from ..immutable import FrozenDict, freeze_json

    _COMPLETION_SUCCESS = re.compile(
        r"\bnormal\s+termination\b|"
        r"\b(?:run|job|calculation|simulation)\s+(?:finished|completed)(?:\s+successfully)?\b|"
        r"\b(?:finished|completed)\s+successfully\b|"
        r"\btotal\s+wall\s+time\b"
    )
    _COMPLETION_FAILURE_PATTERN = (
        r"\b(?:abnormal|error|fatal)\s+termination\b|"
        r"\b(?:run|job|calculation|simulation)\s+(?:failed|aborted)\b|"
        r"\b(?:not|never)\s+(?:finished|completed)\b|"
        r"\bcompleted\s+with\s+(?:errors?|failures?)\b|"
        r"\bfatal\s+error\b"
    )
    _CONVERGENCE_SUCCESS = re.compile(r"\bconverged\b|\bconvergence\s+(?:achieved|reached)\b")
    _CONVERGENCE_FAILURE_PATTERN = (
        r"\bnot(?:\s+fully)?\s+converged\b|\bfailed\s+to\s+converge\b|"
        r"\bdid\s+not\s+converge\b|\bconvergence\s+(?:not\s+achieved|failed|failure)\b|"
        r"\bnon[-\s]?converged\b|\bunconverged\b"
    )
    _FAILURE_STATUS = re.compile(
        rf"(?P<completion>{_COMPLETION_FAILURE_PATTERN})|(?P<convergence>{_CONVERGENCE_FAILURE_PATTERN})"
    )
    _FAILURE_CUES = ("not", "fail", "error", "fatal", "abnormal", "abort", "never", "non-", "non ", "unconverged")


    @dataclass(frozen=True, slots=True)
    class AdapterProbe:
        slug: str
        available: bool
        executable: str | None
        reason: str


    @dataclass(frozen=True, slots=True)
    class CommandPlan:
        argv: tuple[str, ...]
        cwd: Path
        environment: dict[str, str]
        claim_boundary: str
        adapter_slug: str | None = None
        input_sha256: str | None = None
        execute_allowed: bool = False


    def _resolve_executable(candidate: str) -> str | None:
        path = Path(candidate).expanduser()
        if path.is_absolute() and path.is_file():
            resolved = str(path.resolve())
        elif path.parent != Path(".") and path.is_file():
            resolved = str(path.resolve())
        else:
            resolved = shutil.which(candidate)
        if resolved and os.name != "nt" and not os.access(resolved, os.X_OK):
            return None
        return resolved


    def _module_probe_interpreter(candidate: str, found: str) -> str:
        name = Path(found).name.casefold()
        return found if name.startswith(("python", "pypy")) else sys.executable


    def _missing_python_modules(executable: str, modules: tuple[str, ...]) -> tuple[str, ...]:
        if not modules:
            return ()
        script = (
            "import importlib.util,json,sys;"
            "missing=[name for name in sys.argv[1:] if importlib.util.find_spec(name) is None];"
            "print(json.dumps(missing));raise SystemExit(bool(missing))"
        )
        try:
            result = subprocess.run(  # nosec B603
                [executable, "-c", script, *modules], check=False, capture_output=True,
                text=True, timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return modules
        if result.returncode == 0:
            return ()
        try:
            payload = json.loads(result.stdout.strip() or "[]")
        except json.JSONDecodeError:
            return modules
        return tuple(str(item) for item in payload) if isinstance(payload, list) else modules


    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


    @dataclass(frozen=True, slots=True)
    class Adapter:
        record: dict[str, Any]

        def __post_init__(self) -> None:
            object.__setattr__(self, "record", freeze_json(dict(self.record)))

        @property
        def slug(self) -> str:
            return str(self.record["slug"])

        @property
        def python_modules(self) -> tuple[str, ...]:
            raw = self.record.get("python_modules", [])
            return tuple(str(item) for item in raw) if isinstance(raw, list) else ()

        def _probe_candidate(self, candidate: str) -> AdapterProbe:
            found = _resolve_executable(candidate)
            if not found:
                return AdapterProbe(self.slug, False, None, f"executable not detected: {candidate}")
            interpreter = _module_probe_interpreter(candidate, found)
            missing = _missing_python_modules(interpreter, self.python_modules)
            if missing:
                return AdapterProbe(
                    self.slug, False, found,
                    f"detected {candidate}, but required Python modules are missing from {interpreter}: {', '.join(missing)}",
                )
            reason = f"detected {candidate}"
            if self.python_modules:
                reason += f" with modules in {interpreter}: {', '.join(self.python_modules)}"
            return AdapterProbe(self.slug, True, found, reason)

        def probe(self) -> AdapterProbe:
            reasons: list[str] = []
            for executable in self.record.get("executables", []):
                result = self._probe_candidate(str(executable))
                if result.available:
                    return result
                reasons.append(result.reason)
            return AdapterProbe(
                self.slug, False, None,
                "; ".join(reasons) if reasons else "no declared executable detected",
            )

        def _explicit_probe(self, executable: str) -> AdapterProbe:
            requested = _resolve_executable(executable)
            declared = {
                found for candidate in self.record.get("executables", [])
                if (found := _resolve_executable(str(candidate))) is not None
            }
            if requested is None or requested not in declared:
                return AdapterProbe(self.slug, False, requested, "explicit executable is not a declared adapter executable")
            return self._probe_candidate(executable)

        def build_command(self, input_path: Path, *, executable: str | None = None) -> CommandPlan:
            try:
                source = input_path.expanduser().resolve(strict=True)
            except OSError as error:
                raise ContractError(f"input file does not exist: {input_path}") from error
            if not source.is_file():
                raise ContractError(f"input file does not exist: {input_path}")
            probe = self.probe() if executable is None else self._explicit_probe(executable)
            if not probe.available or not probe.executable:
                raise ContractError(f"adapter {self.slug} is not runnable in the current environment: {probe.reason}")
            return CommandPlan(
                (probe.executable, source.name), source.parent, {},
                "Command prepared only; execution requires hash-bound authorization and scientific acceptance requires separate evidence.",
                adapter_slug=self.slug, input_sha256=_sha256(source), execute_allowed=False,
            )

        def parse(self, output: str) -> dict[str, Any]:
            folded = output.casefold()
            completion_failed = convergence_failed = False
            if any(cue in folded for cue in _FAILURE_CUES):
                for match in _FAILURE_STATUS.finditer(folded):
                    completion_failed |= match.lastgroup == "completion"
                    convergence_failed |= match.lastgroup == "convergence"
                    if completion_failed and convergence_failed:
                        break
            completed = not completion_failed and _COMPLETION_SUCCESS.search(folded) is not None
            converged = completed and not convergence_failed and _CONVERGENCE_SUCCESS.search(folded) is not None
            return {"completed": completed, "converged": converged, "raw_length": len(output), "validated": False}
    ''',
)

write(
    "tsao_computation/security/process.py",
    r'''
    from __future__ import annotations

    import os
    import subprocess  # nosec B404
    from collections.abc import Mapping, Sequence
    from pathlib import Path

    from ..errors import SecurityError

    _PORTABLE_ENVIRONMENT_KEYS = ("PATH", "HOME", "TEMP", "TMP", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE")
    _WINDOWS_ENVIRONMENT_KEYS = (
        "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "SYSTEMDRIVE", "USERPROFILE", "APPDATA", "LOCALAPPDATA",
    )
    _SAFE_OVERRIDE_KEYS = frozenset({
        "CUDA_VISIBLE_DEVICES", "HIP_VISIBLE_DEVICES", "ROCR_VISIBLE_DEVICES", "OMP_NUM_THREADS",
        "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
    })


    def _subprocess_environment(
        overrides: Mapping[str, str] | None = None, *, parent: Mapping[str, str] | None = None,
        platform_name: str | None = None,
    ) -> dict[str, str]:
        source = os.environ if parent is None else parent
        platform = os.name if platform_name is None else platform_name
        allowed = _PORTABLE_ENVIRONMENT_KEYS + (_WINDOWS_ENVIRONMENT_KEYS if platform == "nt" else ())
        if platform == "nt":
            source_by_name = {str(key).casefold(): str(value) for key, value in source.items()}
            merged = {name: source_by_name[name.casefold()] for name in allowed if name.casefold() in source_by_name}
        else:
            merged = {name: str(source[name]) for name in allowed if name in source}
        merged.setdefault("PATH", "")
        merged["LANG"] = "C.UTF-8"
        if overrides:
            unsafe = sorted(str(key) for key in overrides if str(key).upper() not in _SAFE_OVERRIDE_KEYS)
            if unsafe:
                raise SecurityError(f"unsafe subprocess environment overrides: {unsafe}")
            for raw_key, raw_value in overrides.items():
                key = str(raw_key).upper()
                value = str(raw_value)
                if not value or "\x00" in value:
                    raise SecurityError(f"invalid subprocess environment value: {key}")
                merged[key] = value
        return merged


    def safe_run(
        argv: Sequence[str], *, cwd: Path, timeout: float = 300.0,
        env: Mapping[str, str] | None = None, allow_process_execution: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        if allow_process_execution is not True:
            raise SecurityError("process execution requires a verified hash-bound authorization")
        if not argv or any(not isinstance(item, str) or not item or "\x00" in item for item in argv):
            raise SecurityError("argv must be a non-empty sequence of non-empty strings")
        if timeout <= 0 or timeout > 86400:
            raise SecurityError("timeout must be within (0, 86400] seconds")
        resolved_cwd = cwd.expanduser().resolve(strict=True)
        if not resolved_cwd.is_dir():
            raise SecurityError(f"working directory does not exist: {cwd}")
        return subprocess.run(
            tuple(argv), cwd=resolved_cwd, env=_subprocess_environment(env), text=True,
            capture_output=True, timeout=timeout, check=False, shell=False,  # nosec B603
        )
    ''',
)

write(
    "tsao_computation/security/__init__.py",
    r'''
    from .paths import atomic_write_text, confined_path

    __all__ = ["confined_path", "atomic_write_text"]
    ''',
)

write(
    "tsao_computation/execution/typing_compat.py",
    r'''
    from __future__ import annotations

    from pathlib import Path
    from typing import Protocol


    class CommandPlanLike(Protocol):
        argv: tuple[str, ...]
        cwd: Path
        environment: dict[str, str]
    ''',
)

write(
    "tsao_computation/execution/runner.py",
    r'''
    from __future__ import annotations

    import hashlib
    import json
    from dataclasses import dataclass
    from datetime import datetime, timezone

    from ..errors import SecurityError
    from ..security.process import safe_run
    from .typing_compat import CommandPlanLike


    def plan_sha256(plan: CommandPlanLike) -> str:
        payload = {
            "argv": list(plan.argv), "cwd": str(plan.cwd.expanduser().resolve(strict=False)),
            "environment": dict(sorted(plan.environment.items())),
            "adapter_slug": getattr(plan, "adapter_slug", None),
            "input_sha256": getattr(plan, "input_sha256", None),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


    @dataclass(frozen=True, slots=True)
    class ExecutionAuthorization:
        plan_sha256: str
        authorized_by: str
        purpose: str
        explicit_authorization: bool

        @property
        def authorization_sha256(self) -> str:
            encoded = json.dumps(
                {"plan_sha256": self.plan_sha256, "authorized_by": self.authorized_by,
                 "purpose": self.purpose, "explicit_authorization": self.explicit_authorization},
                sort_keys=True, separators=(",", ":"),
            )
            return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


    def authorize_plan(
        plan: CommandPlanLike, *, authorized_by: str, purpose: str,
        explicit_authorization: bool,
    ) -> ExecutionAuthorization:
        if explicit_authorization is not True:
            raise SecurityError("explicit process execution authorization must be boolean true")
        if not isinstance(authorized_by, str) or not authorized_by.strip():
            raise SecurityError("authorized_by must be a non-empty identity")
        if not isinstance(purpose, str) or not purpose.strip():
            raise SecurityError("authorization purpose must be a non-empty string")
        return ExecutionAuthorization(plan_sha256(plan), authorized_by.strip(), purpose.strip(), True)


    @dataclass(frozen=True, slots=True)
    class ExecutionRecord:
        argv: tuple[str, ...]
        returncode: int
        stdout_sha256: str
        stderr_sha256: str
        started_at: str
        completed_at: str
        completed: bool
        plan_sha256: str
        authorization_sha256: str
        authorized_by: str


    def run_plan(
        plan: CommandPlanLike, *, authorization: ExecutionAuthorization | None = None,
        timeout: float = 300.0,
    ) -> ExecutionRecord:
        if authorization is None:
            raise SecurityError("external process execution is plan-only until explicitly authorized")
        digest = plan_sha256(plan)
        if authorization.explicit_authorization is not True or authorization.plan_sha256 != digest:
            raise SecurityError("execution authorization does not match the immutable command plan")
        started = datetime.now(timezone.utc).isoformat()
        result = safe_run(
            plan.argv, cwd=plan.cwd, timeout=timeout, env=plan.environment,
            allow_process_execution=True,
        )
        completed_at = datetime.now(timezone.utc).isoformat()
        return ExecutionRecord(
            tuple(plan.argv), result.returncode,
            hashlib.sha256(result.stdout.encode()).hexdigest(),
            hashlib.sha256(result.stderr.encode()).hexdigest(),
            started, completed_at, result.returncode == 0, digest,
            authorization.authorization_sha256, authorization.authorized_by,
        )
    ''',
)

write(
    "tsao_computation/execution/batch.py",
    r'''
    from __future__ import annotations

    import os
    from concurrent.futures import ThreadPoolExecutor
    from dataclasses import dataclass

    from ..errors import SecurityError
    from .runner import ExecutionAuthorization, ExecutionRecord, run_plan
    from .typing_compat import CommandPlanLike

    _DEFAULT_MAX_EXTERNAL_PLANS = 4


    @dataclass(frozen=True, slots=True)
    class BatchExecutionResult:
        records: tuple[ExecutionRecord, ...]
        completed: bool
        failed_indices: tuple[int, ...]


    def _default_workers(plan_count: int) -> int:
        return min(plan_count, max(1, min(_DEFAULT_MAX_EXTERNAL_PLANS, os.cpu_count() or 1)))


    def run_plan_batch(
        plans: tuple[CommandPlanLike, ...] | list[CommandPlanLike], *,
        authorizations: tuple[ExecutionAuthorization, ...] | list[ExecutionAuthorization] | None = None,
        timeout: float = 300.0, max_workers: int | None = None,
    ) -> BatchExecutionResult:
        items = tuple(plans)
        if not items:
            return BatchExecutionResult((), True, ())
        if authorizations is None or len(authorizations) != len(items):
            raise SecurityError("each external command plan requires one matching authorization")
        auth_items = tuple(authorizations)
        workers = _default_workers(len(items)) if max_workers is None else max_workers
        if workers < 1:
            raise ValueError("max_workers must be positive")
        workers = min(workers, len(items))
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="tsao-external-plan") as pool:
            futures = [
                pool.submit(run_plan, plan, authorization=authorization, timeout=timeout)
                for plan, authorization in zip(items, auth_items, strict=True)
            ]
            records = tuple(future.result() for future in futures)
        failed = tuple(index for index, record in enumerate(records) if not record.completed)
        return BatchExecutionResult(records, not failed, failed)


    run_plans = run_plan_batch
    ''',
)

write(
    "tsao_computation/execution/__init__.py",
    r'''
    from .batch import BatchExecutionResult, run_plan_batch, run_plans
    from .runner import ExecutionAuthorization, ExecutionRecord, authorize_plan, plan_sha256, run_plan

    __all__ = [
        "BatchExecutionResult", "ExecutionAuthorization", "ExecutionRecord", "authorize_plan",
        "plan_sha256", "run_plan", "run_plan_batch", "run_plans",
    ]
    ''',
)

planner_path = ROOT / "tsao_computation/orchestration/planner.py"
planner = planner_path.read_text(encoding="utf-8")

helper = r'''
def _required_value_present(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping | list | tuple | set | frozenset):
        return bool(value)
    return True


def _missing_required_inputs(spec: InvocationSpec, payload: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(key for key in spec.required_inputs if not _required_value_present(payload.get(key)))


'''
planner = replace_once(planner, "def _trusted_spec(slug: str) -> InvocationSpec:\n", helper + "def _trusted_spec(slug: str) -> InvocationSpec:\n", "planner validation helper")

planner = replace_function(
    planner,
    "get_invocation_spec",
    r'''
    def get_invocation_spec(slug: str) -> InvocationSpec:
        if not isinstance(slug, str) or not slug.strip():
            raise KeyError("invocation target must be a non-empty string")
        normalized = slug.strip().casefold()
        if normalized.startswith("skill:"):
            workflow = normalized.partition(":")[2]
            if not workflow:
                raise KeyError("skill invocation requires a workflow slug")
            _workflow_record(workflow)
            return InvocationSpec(
                slug=normalized,
                name=f"Workflow Skill: {workflow}",
                kind=InvocationKind.SKILL,
                target=workflow,
                workflow=workflow,
                trusted_local_execution=False,
                required_inputs=("calculation_contract", "skill_available", "explicit_authorization"),
                expected_outputs=("handoff record", "artifacts", "evidence"),
                evidence_requirements=("Skill identifier", "version", "input hash", "output hash"),
                claim_boundary="Skill handoff plan only; execution depends on an available authorized Skill runtime.",
            )
        for item in list_invocations():
            if item.slug == normalized:
                return item
        raise KeyError(f"unknown invocation target: {slug}")


    ''',
)

planner = replace_function(
    planner,
    "build_invocation_plan",
    r'''
    def build_invocation_plan(
        slug: str,
        payload: Mapping[str, Any] | None = None,
        *,
        input_path: Path | None = None,
    ) -> InvocationPlan:
        spec = get_invocation_spec(slug)
        normalized_payload = {} if payload is None else dict(payload)
        blockers = _missing_required_inputs(spec, normalized_payload)
        if spec.trusted_local_execution:
            return InvocationPlan(
                slug=spec.slug, kind=spec.kind, target=spec.target,
                ready=not blockers, execute_allowed=not blockers, argv=(), cwd=None,
                environment={}, blockers=blockers, expected_outputs=spec.expected_outputs,
                evidence_requirements=spec.evidence_requirements, claim_boundary=spec.claim_boundary,
            )
        if spec.slug.startswith("adapter:"):
            missing: list[str] = []
            if input_path is None:
                missing.append("native_input_file")
            if not _required_value_present(normalized_payload.get("lawful_environment")):
                missing.append("lawful_environment")
            if normalized_payload.get("explicit_authorization") is not True:
                missing.append("explicit_authorization")
            if input_path is None:
                return InvocationPlan(
                    slug=spec.slug, kind=spec.kind, target=spec.target, ready=False,
                    execute_allowed=False, argv=(), cwd=None, environment={}, blockers=tuple(missing),
                    expected_outputs=spec.expected_outputs, evidence_requirements=spec.evidence_requirements,
                    claim_boundary=spec.claim_boundary,
                )
            try:
                command = get_adapter(spec.target).build_command(input_path)
            except ContractError as error:
                return InvocationPlan(
                    slug=spec.slug, kind=spec.kind, target=spec.target, ready=False,
                    execute_allowed=False, argv=(), cwd=None, environment={},
                    blockers=(str(error), *missing), expected_outputs=spec.expected_outputs,
                    evidence_requirements=spec.evidence_requirements, claim_boundary=spec.claim_boundary,
                )
            return InvocationPlan(
                slug=spec.slug, kind=spec.kind, target=spec.target, ready=not missing,
                execute_allowed=False, argv=command.argv, cwd=str(command.cwd),
                environment=command.environment, blockers=tuple(missing),
                expected_outputs=spec.expected_outputs, evidence_requirements=spec.evidence_requirements,
                claim_boundary=command.claim_boundary,
            )
        return InvocationPlan(
            slug=spec.slug, kind=spec.kind, target=spec.target,
            ready=not blockers, execute_allowed=False, argv=(), cwd=None, environment={},
            blockers=blockers or ("runtime execution remains disabled until a dedicated authorized executor is bound",),
            expected_outputs=spec.expected_outputs, evidence_requirements=spec.evidence_requirements,
            claim_boundary=spec.claim_boundary,
        )


    ''',
)

planner = replace_function(
    planner,
    "recommend_acceleration",
    r'''
    def recommend_acceleration(
        workload: Mapping[str, object] | None = None,
        *,
        method_slugs: tuple[str, ...] = (),
        limit: int = 8,
    ) -> tuple[AccelerationAdvice, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        selected_methods = tuple(get_method(slug) for slug in method_slugs)
        external_kinds = {
            InvocationKind.LOCAL_SOLVER, InvocationKind.REMOTE_API, InvocationKind.CONTAINER,
            InvocationKind.SCHEDULER_JOB, InvocationKind.COMMERCIAL_ADAPTER, InvocationKind.SKILL,
        }
        supports_external_solver = any(
            external_kinds.intersection(method.invocation_kinds) for method in selected_methods
        )
        source = {} if workload is None else dict(workload)
        text = " ".join([
            *(item.slug for item in selected_methods),
            *(f"{key} {value}" for key, value in source.items()),
        ]).casefold()
        ranked: list[tuple[int, str, AccelerationAdvice]] = []
        for advice, tags in _STRATEGIES:
            score = sum(tag in text for tag in tags)
            if advice.slug == "profiling-first":
                score += 1
            if advice.slug == "native-solver-backend":
                if not supports_external_solver:
                    continue
                score += 1
            if score:
                ranked.append((score, advice.slug, advice))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return tuple(item[2] for item in ranked[:limit])


    ''',
)

planner = replace_function(
    planner,
    "_resolve_methods",
    r'''
    def _resolve_methods(contract: CalculationContract, workflow: str) -> tuple[MethodSpec, ...]:
        if contract.methods:
            selected = tuple(get_method(raw) for raw in contract.methods)
        else:
            selected = tuple(get_method(slug) for slug in _default_method_slugs(workflow))
        return tuple(dict.fromkeys(selected))


    ''',
)

old_route = '''    workflow = contract.workflow
    if workflow is None:
        from ..routing import route_question

        workflow = route_question(contract.question).workflow
    record = _workflow_record(workflow)
'''
new_route = '''    workflow = contract.workflow
    route_requires_clarification = False
    if workflow is None:
        from ..routing import route_question

        decision = route_question(contract.question)
        workflow = decision.workflow
        route_requires_clarification = decision.score <= 0
    record = _workflow_record(workflow)
'''
planner = replace_once(planner, old_route, new_route, "implicit route block")
old_blockers = '''    blockers = contract.specification_gaps()
    return OrchestrationPlan(
'''
new_blockers = '''    blocker_list = list(contract.specification_gaps())
    if route_requires_clarification:
        blocker_list.append("workflow_clarification_required")
    blockers = tuple(dict.fromkeys(blocker_list))
    return OrchestrationPlan(
'''
planner = replace_once(planner, old_blockers, new_blockers, "orchestration blockers")
planner_path.write_text(planner, encoding="utf-8", newline="\n")

# Tighten generic completion fixture and authorize batch execution tests.
adapter_test = ROOT / "tests/test_adapter_fail_closed.py"
text = adapter_test.read_text(encoding="utf-8")
text = replace_once(
    text,
    'Adapter({"slug": "generic"}).parse("SCF converged after 12 cycles; completed")',
    'Adapter({"slug": "generic"}).parse("SCF converged after 12 cycles; calculation completed")',
    "adapter positive completion fixture",
)
text = text.replace(
    'len("SCF converged after 12 cycles; completed")',
    'len("SCF converged after 12 cycles; calculation completed")',
)
adapter_test.write_text(text, encoding="utf-8", newline="\n")

batch_test = ROOT / "tests/test_acceleration_batch.py"
text = batch_test.read_text(encoding="utf-8")
text = text.replace(
    "from tsao_computation.execution import run_plan_batch",
    "from tsao_computation.execution import authorize_plan, run_plan_batch",
)
text = replace_once(
    text,
    "    result = run_plan_batch(plans, timeout=10, max_workers=2)\n",
    "    authorizations = [\n        authorize_plan(plan, authorized_by=\"pytest\", purpose=\"repository execution test\", explicit_authorization=True)\n        for plan in plans\n    ]\n    result = run_plan_batch(plans, authorizations=authorizations, timeout=10, max_workers=2)\n",
    "batch authorization fixture",
)
old_worker = '''        run_plan_batch(
            [
                CommandPlan(
                    (sys.executable, "-c", "pass"),
                    Path("."),
                    {},
                    "test",
                )
            ],
            max_workers=0,
        )
'''
new_worker = '''        plan = CommandPlan((sys.executable, "-c", "pass"), Path("."), {}, "test")
        run_plan_batch(
            [plan],
            authorizations=[
                authorize_plan(
                    plan,
                    authorized_by="pytest",
                    purpose="worker validation",
                    explicit_authorization=True,
                )
            ],
            max_workers=0,
        )
'''
text = replace_once(text, old_worker, new_worker, "worker validation fixture")
batch_test.write_text(text, encoding="utf-8", newline="\n")

write(
    "tests/test_adversarial_super_skill_phase_a.py",
    r'''
    from __future__ import annotations

    import sys
    from pathlib import Path

    import pytest

    from tsao_computation.adapters.base import Adapter, CommandPlan
    from tsao_computation.contracts import CalculationContract
    from tsao_computation.errors import ContractError, SecurityError
    from tsao_computation.execution import authorize_plan, plan_sha256, run_plan, run_plan_batch
    from tsao_computation.orchestration import (
        build_invocation_plan,
        build_orchestration_plan,
        execute_trusted_callable,
        get_invocation_spec,
        recommend_acceleration,
    )
    from tsao_computation.registries import capabilities, workflows
    from tsao_computation.security.process import safe_run
    from tsao_computation.uncertainty import UncertaintyBudget, combine_independent
    from tsao_computation.validation import balance_check


    def complete_contract(**overrides: object) -> CalculationContract:
        values: dict[str, object] = {
            "question": "Plan a declared scientific calculation",
            "system": {"name": "system"},
            "conditions": {"temperature_K": 300.0},
            "target_observables": ("observable",),
            "workflow": "scale-selection",
            "assumptions": ("declared",),
            "acceptance_criteria": {"declared": True},
            "model_object": {"type": "declared"},
            "scales": ("equation",),
            "methods": ("analytical-model",),
            "boundary_conditions": {"declared": True},
            "initial_conditions": {"declared": True},
            "parameter_sources": ({"source": "declared"},),
            "convergence_plan": {"declared": True},
            "validation_plan": {"declared": True},
            "uncertainty_sources": ("model",),
            "compute_resources": {"cpu": True},
            "expected_artifacts": ("result",),
            "human_approval_nodes": ("acceptance",),
        }
        values.update(overrides)
        return CalculationContract(**values)  # type: ignore[arg-type]


    def test_explicit_unknown_method_fails_closed() -> None:
        with pytest.raises(KeyError, match="unknown computation method"):
            build_orchestration_plan(complete_contract(methods=("invented-method",)))


    def test_unknown_skill_handoff_is_rejected() -> None:
        with pytest.raises(KeyError, match="unknown workflow"):
            get_invocation_spec("skill:invented-workflow")


    def test_ambiguous_implicit_route_cannot_enter_preflight() -> None:
        plan = build_orchestration_plan(
            complete_contract(question="zxqv unmatched terminology", workflow=None)
        )
        assert not plan.ready_for_preflight
        assert "workflow_clarification_required" in plan.blockers


    @pytest.mark.parametrize("authorization", (False, "false", "yes", 1, None))
    def test_adapter_authorization_requires_boolean_true(authorization: object) -> None:
        plan = build_invocation_plan(
            "adapter:orca",
            {"lawful_environment": "declared", "explicit_authorization": authorization},
        )
        assert "explicit_authorization" in plan.blockers
        assert not plan.execute_allowed


    def test_analytical_workload_does_not_receive_native_solver_advice() -> None:
        advice = recommend_acceleration(
            {"workload": "small closed-form equation"}, method_slugs=("analytical-model",)
        )
        assert "native-solver-backend" not in {item.slug for item in advice}
        with pytest.raises(KeyError, match="unknown computation method"):
            recommend_acceleration({}, method_slugs=("invented-method",))


    def test_contract_and_registry_snapshots_are_immutable() -> None:
        source = {"nested": {"values": [1, 2]}}
        contract = complete_contract(system=source)
        source["nested"]["values"].append(3)  # type: ignore[index,union-attr]
        assert contract.to_dict()["system"] == {"nested": {"values": [1, 2]}}
        with pytest.raises(TypeError, match="immutable"):
            contract.system["new"] = True
        with pytest.raises(TypeError, match="immutable"):
            capabilities()[0]["name_en"] = "tampered"
        with pytest.raises(TypeError, match="immutable"):
            workflows()[0]["keywords"].append("tampered")


    def test_completion_parser_rejects_intermediate_completed_messages() -> None:
        parsed = Adapter({"slug": "generic"}).parse(
            "Initialization completed; simulation still running; step 4 of 100"
        )
        assert parsed["completed"] is False
        assert parsed["converged"] is False


    def test_external_execution_requires_hash_bound_authorization(tmp_path: Path) -> None:
        plan = CommandPlan((sys.executable, "-c", "print('ok')"), tmp_path, {}, "test")
        with pytest.raises(SecurityError, match="plan-only"):
            run_plan(plan)
        authorization = authorize_plan(
            plan, authorized_by="pytest", purpose="authorization regression",
            explicit_authorization=True,
        )
        assert authorization.plan_sha256 == plan_sha256(plan)
        record = run_plan(plan, authorization=authorization, timeout=10)
        assert record.completed and record.authorized_by == "pytest"
        changed = CommandPlan((sys.executable, "-c", "print('changed')"), tmp_path, {}, "test")
        with pytest.raises(SecurityError, match="does not match"):
            run_plan(changed, authorization=authorization)
        with pytest.raises(SecurityError, match="matching authorization"):
            run_plan_batch([plan], authorizations=[])


    def test_low_level_process_api_defaults_to_deny(tmp_path: Path) -> None:
        with pytest.raises(SecurityError, match="hash-bound authorization"):
            safe_run((sys.executable, "-c", "pass"), cwd=tmp_path)
        with pytest.raises(SecurityError, match="unsafe subprocess environment"):
            safe_run(
                (sys.executable, "-c", "pass"), cwd=tmp_path,
                env={"PYTHONPATH": "attacker"}, allow_process_execution=True,
            )


    def test_scientific_numeric_primitives_reject_booleans() -> None:
        with pytest.raises(ValueError, match="boolean"):
            balance_check(True, 1.0)
        with pytest.raises(ValueError):
            combine_independent(True)
        with pytest.raises(ValueError):
            UncertaintyBudget(0.1, 0.2, 0.3, "")


    def test_trusted_required_inputs_reject_empty_payload_values() -> None:
        plan = build_invocation_plan(
            "convergence-check", {"values": [], "absolute_tolerance": 0.0}
        )
        assert not plan.ready and "values" in plan.blockers
        with pytest.raises(ContractError, match="not ready"):
            execute_trusted_callable(
                "convergence-check", {"values": [], "absolute_tolerance": 0.0}
            )
    ''',
)

print("adversarial phase A candidate applied")
