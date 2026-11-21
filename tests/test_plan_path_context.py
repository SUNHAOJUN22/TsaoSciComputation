from __future__ import annotations

import hashlib
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from tsao_computation.errors import SecurityError
from tsao_computation.execution import authorize_plan, plan_sha256, runner
from tsao_computation.security import process as process_security


def _executable(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    path.chmod(path.stat().st_mode | 0o111)
    return path


def _authorize(work: Path, environment: dict[str, str]):
    return authorize_plan(
        SimpleNamespace(argv=("solver",), cwd=work, environment=environment),
        authorized_by="pytest",
        purpose="verify the declared command search context",
        explicit_authorization=True,
    )


@pytest.mark.parametrize("entry", ["bin", "./bin", '"bin"'])
def test_relative_path_uses_plan_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, entry: str
) -> None:
    caller = tmp_path / "caller"
    work = tmp_path / "work"
    _executable(caller / "bin" / "solver", b"unrelated caller executable\n")
    expected = _executable(work / "bin" / "solver", b"planned executable\n")
    monkeypatch.chdir(caller)

    authorization = _authorize(work, {"PATH": entry})

    assert authorization.executable_sha256 == hashlib.sha256(expected.read_bytes()).hexdigest()


def test_literal_path_fallback_also_uses_plan_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work = tmp_path / "work"
    expected = _executable(work / "bin" / "solver", b"planned literal executable\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(runner.shutil, "which", lambda *_args, **_kwargs: None)

    authorization = _authorize(work, {"PATH": "bin"})

    assert authorization.executable_sha256 == hashlib.sha256(expected.read_bytes()).hexdigest()


def test_plan_identity_does_not_depend_on_callers_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    work = tmp_path / "work"
    _executable(work / "bin" / "solver", b"planned executable\n")
    callers = [tmp_path / "caller-a", tmp_path / "caller-b"]
    for index, caller in enumerate(callers):
        _executable(caller / "bin" / "solver", f"caller {index}\n".encode())
    plan = SimpleNamespace(argv=("solver",), cwd=work, environment={"PATH": "bin"})
    monkeypatch.chdir(callers[0])
    first = plan_sha256(plan)

    monkeypatch.chdir(callers[1])

    assert plan_sha256(plan) == first


def test_missing_plan_path_cannot_borrow_callers_executable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    caller = tmp_path / "caller"
    work = tmp_path / "work"
    work.mkdir()
    _executable(caller / "bin" / "solver", b"not present in declared plan context\n")
    monkeypatch.chdir(caller)

    with pytest.raises(SecurityError, match="executable is unavailable"):
        _authorize(work, {"PATH": "bin"})


@pytest.mark.parametrize("platform_name", ["nt", "posix"])
@pytest.mark.parametrize("path_key", ["PATH", "Path", "path"])
def test_path_override_obeys_platform_environment_name_rules(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    platform_name: str,
    path_key: str,
) -> None:
    original = _executable(tmp_path / "original" / "solver", b"original PATH\n")
    overridden = _executable(tmp_path / "overridden" / "solver", b"overridden PATH\n")
    normalize = process_security._subprocess_environment

    def platform_environment(overrides):
        return normalize(
            overrides,
            parent={"PATH": str(original.parent)},
            platform_name=platform_name,
        )

    # Exercise the real environment normalizer and public authorizer with a
    # controlled OS boundary; no scientific process or foreign binary is run.
    monkeypatch.setattr(runner, "_subprocess_environment", platform_environment)
    monkeypatch.setattr(
        runner,
        "os",
        SimpleNamespace(name=platform_name, pathsep=os.pathsep, access=os.access, X_OK=os.X_OK),
    )

    authorization = _authorize(tmp_path, {path_key: str(overridden.parent)})

    expected = overridden if platform_name == "nt" or path_key == "PATH" else original
    assert authorization.executable_sha256 == hashlib.sha256(expected.read_bytes()).hexdigest()


def test_path_directory_spaces_are_literal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    expected = _executable(tmp_path / " spaced directory " / "solver", b"literal spaces\n")
    monkeypatch.chdir(tmp_path)

    authorization = _authorize(tmp_path, {"PATH": str(expected.parent)})

    assert authorization.executable_sha256 == hashlib.sha256(expected.read_bytes()).hexdigest()
