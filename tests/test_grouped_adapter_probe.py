from __future__ import annotations

import json
import os
import site
import subprocess
import sys
import venv
from pathlib import Path

import pytest

from tsao_computation.adapters import base, registry
from tsao_computation.adapters.base import Adapter
from tsao_computation.security import process


def adapter(slug: str, modules: list[str], executable: str = sys.executable) -> Adapter:
    return Adapter({"slug": slug, "executables": [executable], "python_modules": modules})


def count_processes(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, ...]]:
    original = process._run_sanitized
    calls: list[tuple[str, ...]] = []

    def observed(argv, **kwargs):
        calls.append(tuple(argv))
        assert argv[1:3] == ("-I", "-S")
        return original(argv, **kwargs)

    monkeypatch.setattr(process, "_run_sanitized", observed)
    return calls


@pytest.mark.parametrize("workers", [1, 8])
def test_one_environment_uses_one_bound_probe_and_preserves_all_results(
    monkeypatch: pytest.MonkeyPatch, workers: int
) -> None:
    items = (
        adapter("z-missing", ["absent_tsao_group_fixture", "json"]),
        adapter("a-present", ["json.decoder", "sys"]),
        adapter("m-duplicate", ["sys", "absent_tsao_group_fixture", "absent_tsao_group_fixture"]),
    )
    expected = tuple(sorted((item.probe() for item in items), key=lambda result: result.slug))
    monkeypatch.setattr(registry, "list_adapters", lambda: items)
    calls = count_processes(monkeypatch)
    assert registry.probe_all(workers) == expected
    assert len(calls) == 1
    assert calls[0][0] == sys.executable
    assert calls[0][4:] == ("absent_tsao_group_fixture", "json", "json.decoder", "sys")


def installation(directory: Path) -> tuple[Path, Path]:
    venv.EnvBuilder(with_pip=False, symlinks=os.name != "nt").create(directory)
    executable = directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    installed = Path(site.getsitepackages([str(directory)])[0])
    installed.mkdir(parents=True, exist_ok=True)
    return executable, installed


def test_distinct_venv_paths_stay_separate_even_when_binary_target_is_shared(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    python_a, packages_a = installation(tmp_path / "a")
    python_b, packages_b = installation(tmp_path / "b")
    marker = tmp_path / "unexpected-import.txt"
    source = f"raise RuntimeError({str(marker)!r})\n"
    (packages_a / "grouped_fixture.py").write_text(source, encoding="utf-8")
    for packages in (packages_a, packages_b):
        (packages / "hook.pth").write_text(
            f"import pathlib; pathlib.Path({str(marker)!r}).touch()\n", encoding="utf-8"
        )
    items = (
        adapter("a", ["grouped_fixture"], str(python_a)),
        adapter("b", ["grouped_fixture"], str(python_b)),
    )
    monkeypatch.setattr(registry, "list_adapters", lambda: items)
    calls = count_processes(monkeypatch)
    results = registry.probe_all()
    assert [result.available for result in results] == [True, False]
    assert {call[0] for call in calls} == {str(python_a), str(python_b)}
    assert len(calls) == 2
    assert not marker.exists()


def test_metadata_changes_are_observed_on_the_next_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    executable, packages = installation(tmp_path / "venv")
    module = packages / "changing_grouped_fixture.py"
    module.write_text("raise RuntimeError('must not import')\n", encoding="utf-8")
    items = (
        adapter("one", ["changing_grouped_fixture"], str(executable)),
        adapter("two", ["changing_grouped_fixture"], str(executable)),
    )
    monkeypatch.setattr(registry, "list_adapters", lambda: items)
    calls = count_processes(monkeypatch)
    assert all(result.available for result in registry.probe_all())
    module.unlink()
    assert not any(result.available for result in registry.probe_all())
    assert len(calls) == 2


def test_multi_candidate_fallback_keeps_original_order_and_short_circuit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    item = Adapter(
        {
            "slug": "fallback",
            "executables": ["absent_tsao_executable", sys.executable, "unused"],
            "python_modules": ["json"],
        }
    )
    monkeypatch.setattr(registry, "list_adapters", lambda: (item,))
    original = base._resolve_executable
    attempts: list[str] = []

    def resolve(candidate: str) -> str | None:
        attempts.append(candidate)
        return original(candidate)

    monkeypatch.setattr(base, "_resolve_executable", resolve)
    assert registry.probe_all()[0].available
    assert attempts == ["absent_tsao_executable", sys.executable]


@pytest.mark.parametrize("failure", ["malformed", "unbound", "timeout", "exit"])
def test_group_failure_never_promotes_any_member(
    monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    items = (adapter("one", ["json"]), adapter("two", ["sys"]))
    monkeypatch.setattr(registry, "list_adapters", lambda: items)

    def response(argv, **kwargs):
        assert argv[1:3] == ("-I", "-S")
        if failure == "timeout":
            raise subprocess.TimeoutExpired(argv, 10)
        payload = '{"schema_version":1,"requested":[],"missing":[]}'
        return subprocess.CompletedProcess(
            argv, int(failure == "exit"), "invalid" if failure == "malformed" else payload, ""
        )

    monkeypatch.setattr(process, "_run_sanitized", response)
    results = registry.probe_all()
    assert not any(result.available for result in results)
    assert all(result.executable is None for result in results)
    assert results[0].reason.endswith(": json")
    assert results[1].reason.endswith(": sys")


def test_invalid_names_do_not_poison_an_independent_valid_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    items = (adapter("bad", ["bad-name"]), adapter("good", ["json"]))
    monkeypatch.setattr(registry, "list_adapters", lambda: items)
    calls = count_processes(monkeypatch)
    assert [result.available for result in registry.probe_all()] == [False, True]
    assert len(calls) == 1


def test_failed_group_retries_members_without_disqualifying_healthy_adapters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    items = (adapter("bad", ["broken_fixture"]), adapter("good", ["json"]))
    monkeypatch.setattr(registry, "list_adapters", lambda: items)
    requests: list[tuple[str, ...]] = []

    def response(argv, **kwargs):
        requested = tuple(argv[4:])
        requests.append(requested)
        payload = {"schema_version": 1, "requested": list(requested), "missing": []}
        return subprocess.CompletedProcess(
            argv, int("broken_fixture" in requested), json.dumps(payload), ""
        )

    monkeypatch.setattr(process, "_run_sanitized", response)
    results = registry.probe_all()
    assert [result.available for result in results] == [False, True]
    assert results[0].reason.endswith(": broken_fixture")
    assert results[1].executable == sys.executable
    assert requests[0] == ("broken_fixture", "json")
    assert set(requests[1:]) == {("broken_fixture",), ("json",)}


def test_cancellation_propagates_without_launching_fallback_probes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    items = (adapter("one", ["json"]), adapter("two", ["sys"]))
    monkeypatch.setattr(registry, "list_adapters", lambda: items)
    calls = []

    def cancel(argv, **kwargs):
        calls.append(argv)
        raise KeyboardInterrupt

    monkeypatch.setattr(process, "_run_sanitized", cancel)
    with pytest.raises(KeyboardInterrupt):
        registry.probe_all()
    assert len(calls) == 1


def test_large_union_retains_individual_bounded_probes(monkeypatch: pytest.MonkeyPatch) -> None:
    items = (adapter("a", ["a" * 9000]), adapter("b", ["b" * 9000]))
    monkeypatch.setattr(registry, "list_adapters", lambda: items)
    requests: list[tuple[str, ...]] = []

    def missing(executable: str, modules: tuple[str, ...]) -> tuple[str, ...]:
        assert executable == sys.executable
        requests.append(modules)
        return modules

    monkeypatch.setattr(base, "_missing_python_modules", missing)
    assert not any(result.available for result in registry.probe_all())
    assert sorted(requests) == sorted(item.python_modules for item in items)


def test_empty_inventory_and_missing_or_module_free_candidates_are_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(registry, "list_adapters", lambda: ())
    assert registry.probe_all(0) == ()
    items = (
        adapter("missing", ["json"], "absent_tsao_executable"),
        adapter("plain", []),
        Adapter({"slug": "no-executable", "executables": []}),
    )
    monkeypatch.setattr(registry, "list_adapters", lambda: items)
    expected = tuple(sorted((item.probe() for item in items), key=lambda item: item.slug))
    assert registry.probe_all(0) == expected
