from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from scripts.verify_all import run_commands_parallel, verification_workers
from tsao_computation.adapters import get_adapter
from tsao_computation.provenance.manifest import _file_size_and_sha256
from tsao_computation.registries import clear_registry_caches
from tsao_computation.routing import route_question
from tsao_computation.routing.router import _route_cached


def test_verification_worker_policy_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TSAO_VERIFY_WORKERS", raising=False)
    assert 1 <= verification_workers(20) <= 3
    monkeypatch.setenv("TSAO_VERIFY_WORKERS", "8")
    assert verification_workers(2) == 2
    monkeypatch.setenv("TSAO_VERIFY_WORKERS", "1")
    assert verification_workers(5) == 1
    monkeypatch.setenv("TSAO_VERIFY_WORKERS", "0")
    with pytest.raises(ValueError, match="positive"):
        verification_workers(2)


def test_parallel_gate_output_is_deterministic_and_failure_propagates(
    capsys: pytest.CaptureFixture[str],
) -> None:
    commands = (
        ("first", (sys.executable, "-c", "import time; time.sleep(0.05); print('FIRST')")),
        ("second", (sys.executable, "-c", "print('SECOND'); raise SystemExit(3)")),
    )
    assert run_commands_parallel(commands, max_workers=2) == 3
    output = capsys.readouterr().out
    assert output.index("FIRST") < output.index("SECOND")


def test_repeated_route_cache_is_bounded_and_explicitly_invalidated() -> None:
    clear_registry_caches()
    question = "OpenFOAM non-Newtonian polymer extrusion"
    first = route_question(question)
    assert route_question(question) is first
    for index in range(300):
        route_question(f"OpenFOAM non-Newtonian polymer extrusion case {index}")
    assert _route_cached.cache_info().currsize == 256
    clear_registry_caches()
    assert _route_cached.cache_info().currsize == 0
    assert route_question(question) == first


def test_large_file_hashing_preserves_manifest_bytes(tmp_path: Path) -> None:
    payload = (b"TsaoSciComputation-V9\n" * 100_000) + b"tail"
    path = tmp_path / "large.bin"
    path.write_bytes(payload)
    size, digest = _file_size_and_sha256(path)
    assert size == len(payload)
    assert digest == hashlib.sha256(payload).hexdigest()


def test_fifty_mib_parser_keeps_failure_precedence() -> None:
    size = 50 * 1024 * 1024
    prefix = "normal termination; converged\n"
    suffix = "\nfailed to converge"
    payload = prefix + ("x" * (size - len(prefix) - len(suffix))) + suffix
    parsed = get_adapter("orca").parse(payload)
    assert parsed["completed"] is True
    assert parsed["converged"] is False
    assert parsed["raw_length"] == size
