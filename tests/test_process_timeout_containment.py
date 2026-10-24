from __future__ import annotations

import importlib.util
import io
import json
import os
import runpy
import signal
import subprocess
import sys
import threading
import types
from pathlib import Path
from typing import Any

import pytest

from tsao_computation.errors import SecurityError
from tsao_computation.security import process as process_module


class _FakeProcess:
    def __init__(
        self,
        responses: list[tuple[bytes | None, bytes | None] | BaseException],
    ) -> None:
        self.pid = 12345
        self.returncode = 0
        self.responses = responses
        self.killed = False
        self.stdout = io.BytesIO()
        self.stderr = io.BytesIO()
        self.reader_threads: list[threading.Thread] = []

    def communicate(self, timeout: float | None = None) -> tuple[bytes | None, bytes | None]:
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        for reader in self.reader_threads:
            reader.join(timeout=2.0)
        return response

    def kill(self) -> None:
        self.killed = True

    def wait(self, timeout: float | None = None) -> int:
        return 0

    def poll(self) -> int:
        return self.returncode


def test_posix_group_runner_decodes_success_with_text_newlines(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeProcess([(b"a\r\nb\rc\n", b"")])
    monkeypatch.setattr(process_module.subprocess, "Popen", lambda *_a, **_k: fake)

    result = process_module._run_posix_group(
        ("fixture",), cwd=tmp_path, timeout=2.0, environment={}
    )

    assert result.stdout == "a\nb\nc\n"
    assert result.stderr == ""


def test_posix_group_timeout_preserves_bytes_and_kills_group(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = _FakeProcess(
        [
            subprocess.TimeoutExpired(("fixture",), 0.5, output=b"partial", stderr=b"error"),
            (b"partial", b"error"),
        ]
    )
    killed_groups: list[tuple[int, int]] = []
    monkeypatch.setattr(process_module.subprocess, "Popen", lambda *_a, **_k: fake)
    monkeypatch.setattr(
        os, "killpg", lambda pid, sig: killed_groups.append((pid, sig)), raising=False
    )
    monkeypatch.setattr(signal, "SIGKILL", 9, raising=False)

    with pytest.raises(subprocess.TimeoutExpired) as captured:
        process_module._run_posix_group(("fixture",), cwd=tmp_path, timeout=0.5, environment={})

    assert killed_groups == [(fake.pid, signal.SIGKILL)]
    assert captured.value.stdout == b"partial"
    assert captured.value.stderr == b"error"


@pytest.mark.parametrize("group_error", [None, PermissionError("denied")])
def test_posix_group_interrupt_cleans_up_before_propagating(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    group_error: OSError | None,
) -> None:
    fake = _FakeProcess([KeyboardInterrupt(), (b"", b"")])  # type: ignore[list-item]
    monkeypatch.setattr(process_module.subprocess, "Popen", lambda *_a, **_k: fake)

    def terminate(_process: subprocess.Popen[bytes]) -> OSError | None:
        return group_error

    monkeypatch.setattr(process_module, "_terminate_posix_group", terminate)
    if group_error is None:
        with pytest.raises(KeyboardInterrupt):
            process_module._run_posix_group(("fixture",), cwd=tmp_path, timeout=1.0, environment={})
    else:
        with pytest.raises(SecurityError, match="unable to terminate the interrupted"):
            process_module._run_posix_group(("fixture",), cwd=tmp_path, timeout=1.0, environment={})


@pytest.mark.parametrize("failure", ["lookup", "permission", "unavailable"])
def test_posix_group_termination_falls_back_to_direct_child(
    monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    fake = _FakeProcess([])

    def fail_killpg(_pid: int, _signal: int) -> None:
        if failure == "lookup":
            raise ProcessLookupError("already gone")
        if failure == "permission":
            raise PermissionError("not permitted")
        raise OSError("group termination unavailable")

    monkeypatch.setattr(os, "killpg", fail_killpg, raising=False)
    monkeypatch.setattr(signal, "SIGKILL", 9, raising=False)

    error = process_module._terminate_posix_group(fake)  # type: ignore[arg-type]

    if failure == "lookup":
        assert error is None
        assert not fake.killed
    else:
        assert isinstance(error, OSError)
        assert fake.killed


def test_finish_terminated_process_fails_closed_when_pipe_never_closes() -> None:
    fake = _FakeProcess(
        [
            subprocess.TimeoutExpired(("fixture",), 5.0),
        ]
    )

    with pytest.raises(SecurityError, match="retained output pipes"):
        process_module._finish_terminated_process(fake)  # type: ignore[arg-type]

    assert fake.killed
    assert fake.stdout.closed
    assert fake.stderr.closed


def test_finish_terminated_process_fails_closed_when_child_cannot_be_reaped() -> None:
    fake = _FakeProcess([subprocess.TimeoutExpired(("fixture",), 5.0)])

    def fail_wait(*_args: Any, **_kwargs: Any) -> int:
        raise subprocess.TimeoutExpired(("fixture",), 5.0)

    fake.wait = fail_wait  # type: ignore[method-assign]
    with pytest.raises(SecurityError, match="could not be reaped"):
        process_module._finish_terminated_process(fake)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("argv", "timeout", "environment"),
    [
        ([], 1.0, {}),
        (["solver", ""], 1.0, {}),
        (["solver"], 0.0, {}),
        (["solver"], 1.0, {"BAD": ""}),
    ],
)
def test_prepared_runner_rejects_invalid_command_contract(
    tmp_path: Path,
    argv: list[str],
    timeout: float,
    environment: dict[str, str],
) -> None:
    with pytest.raises(SecurityError):
        process_module._run_prepared(argv, cwd=tmp_path, timeout=timeout, environment=environment)


def test_prepared_runner_dispatches_to_posix_process_group(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    expected = subprocess.CompletedProcess(("fixture",), 0, "", "")
    monkeypatch.setattr(process_module, "_run_posix_group", lambda *_a, **_k: expected)
    monkeypatch.setattr(process_module.os, "name", "posix")

    result = process_module._run_prepared(["fixture"], cwd=tmp_path, timeout=1.0, environment={})

    assert result is expected


def test_windows_runner_rejects_oversized_bootstrap_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake_msvcrt = types.ModuleType("msvcrt")
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)

    with pytest.raises(SecurityError, match="configuration exceeds its size limit"):
        process_module._run_windows_job(
            ("solver",),
            cwd=tmp_path,
            timeout=1.0,
            environment={"LARGE": "x" * process_module._MAX_PROCESS_CONFIG_BYTES},
        )


def _load_windows_bootstrap(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    fake_msvcrt = types.ModuleType("msvcrt")
    fake_msvcrt.open_osfhandle = lambda handle, _flags: handle  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(os, "O_BINARY", 0, raising=False)
    path = Path(process_module.__file__).with_name("windows_process_bootstrap.py")
    spec = importlib.util.spec_from_file_location("test_windows_process_bootstrap", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _WinApiFunction:
    def __init__(self, result: int) -> None:
        self.result = result
        self.argtypes: Any = None
        self.restype: Any = None
        self.calls: list[tuple[Any, ...]] = []

    def __call__(self, *args: Any) -> int:
        self.calls.append(args)
        return self.result


def _fake_kernel32(
    *, create: int = 11, set_info: int = 1, assign: int = 1
) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        CreateJobObjectW=_WinApiFunction(create),
        SetInformationJobObject=_WinApiFunction(set_info),
        GetCurrentProcess=_WinApiFunction(22),
        AssignProcessToJobObject=_WinApiFunction(assign),
        CloseHandle=_WinApiFunction(1),
    )


def _run_mock_windows_runner(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    status_payload: bytes,
    *,
    fake_process: _FakeProcess | None = None,
    read_config: bool = True,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    fake_msvcrt = types.ModuleType("msvcrt")
    fake_msvcrt.get_osfhandle = lambda descriptor: descriptor  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(os, "set_handle_inheritable", lambda *_args: None, raising=False)
    monkeypatch.setattr(
        process_module.subprocess,
        "STARTUPINFO",
        lambda: types.SimpleNamespace(),
        raising=False,
    )
    process = fake_process or _FakeProcess([(b"worker\r\n", b"worker error\r")])
    process.responses = (
        [(b"worker\r\n", b"worker error\r")] if not process.responses else process.responses
    )

    def fake_popen(command: tuple[str, ...], **_kwargs: Any) -> _FakeProcess:
        if read_config:
            reader_fd = os.dup(int(command[-2]))

            def drain() -> None:
                try:
                    while os.read(reader_fd, 65_536):
                        pass
                finally:
                    os.close(reader_fd)

            reader = threading.Thread(target=drain, daemon=True)
            reader.start()
            process.reader_threads.append(reader)
        os.write(int(command[-1]), status_payload)
        return process

    monkeypatch.setattr(process_module.subprocess, "Popen", fake_popen)
    return process_module._run_windows_job(
        ("solver", "--fixture"),
        cwd=tmp_path,
        timeout=2.0,
        environment=environment or {"PATH": ""},
    )


def test_windows_runner_validates_bootstrap_result_and_decodes_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = json.dumps({"kind": "result", "returncode": 0}).encode("ascii")

    result = _run_mock_windows_runner(monkeypatch, tmp_path, payload)

    assert result.returncode == 0
    assert result.stdout == "worker\n"
    assert result.stderr == "worker error\n"


@pytest.mark.parametrize(
    ("payload", "error_type", "message"),
    [
        (b"invalid", SecurityError, "invalid status"),
        (b"[]", SecurityError, "not an object"),
        (b'{"kind":"containment_error"}', SecurityError, "Job Object setup failed"),
        (b'{"kind":"launch_error"}', OSError, "authorized process could not start"),
        (b'{"kind":"result","returncode":true}', SecurityError, "incomplete result"),
    ],
)
def test_windows_runner_rejects_invalid_bootstrap_status(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    payload: bytes,
    error_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error_type, match=message):
        _run_mock_windows_runner(monkeypatch, tmp_path, payload)


def test_windows_runner_fails_closed_if_config_pipe_cannot_be_written(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = json.dumps({"kind": "result", "returncode": 0}).encode("ascii")

    with pytest.raises(SecurityError, match="configuration pipe failed"):
        _run_mock_windows_runner(monkeypatch, tmp_path, payload, read_config=False)


def test_windows_runner_rejects_unexpected_bootstrap_exit_after_result(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = json.dumps({"kind": "result", "returncode": 0}).encode("ascii")
    process = _FakeProcess([(b"", b"")])
    process.returncode = 1

    with pytest.raises(SecurityError, match="bootstrap exited unexpectedly"):
        _run_mock_windows_runner(monkeypatch, tmp_path, payload, fake_process=process)


@pytest.mark.parametrize("timed_out", [True, False])
def test_windows_runner_rejects_configuration_writer_that_does_not_finish(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    timed_out: bool,
) -> None:
    class StuckThread:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def start(self) -> None:
            pass

        def join(self, timeout: float | None = None) -> None:
            pass

        def is_alive(self) -> bool:
            return True

    monkeypatch.setattr(process_module, "_PROCESS_CLEANUP_TIMEOUT_SECONDS", 0.01)
    monkeypatch.setattr(process_module.threading, "Thread", StuckThread)
    if timed_out:
        fake_process = _FakeProcess(
            [
                subprocess.TimeoutExpired(("bootstrap",), 2.0),
                (b"", b""),
            ]
        )
        expected_message = "timed-out process configuration pipe did not close"
    else:
        fake_process = _FakeProcess([(b"", b"")])
        expected_message = "completed process configuration pipe did not close"
    status = json.dumps({"kind": "result", "returncode": 0}).encode("ascii")

    with pytest.raises(SecurityError, match=expected_message):
        _run_mock_windows_runner(
            monkeypatch,
            tmp_path,
            status,
            fake_process=fake_process,
            read_config=False,
        )


@pytest.mark.parametrize(
    "payload",
    [
        b"[]",
        b'{"argv":[""],"cwd":".","environment":{}}',
        b'{"argv":["solver"],"cwd":".","environment":{"X":1}}',
    ],
)
def test_windows_bootstrap_rejects_malformed_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    payload: bytes,
) -> None:
    module = _load_windows_bootstrap(monkeypatch)
    config_path = tmp_path / "invalid-config.json"
    config_path.write_bytes(payload)
    descriptor = os.open(config_path, os.O_RDONLY)

    with pytest.raises(ValueError):
        module._read_config(descriptor)


def test_windows_bootstrap_rejects_oversized_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_windows_bootstrap(monkeypatch)
    config_path = tmp_path / "oversized-config.json"
    config_path.write_bytes(b" " * (module._MAX_CONFIG_BYTES + 1))
    descriptor = os.open(config_path, os.O_RDONLY)

    with pytest.raises(ValueError, match="exceeds the size limit"):
        module._read_config(descriptor)


def test_windows_bootstrap_job_setup_sets_kill_on_close(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_windows_bootstrap(monkeypatch)
    kernel = _fake_kernel32()
    monkeypatch.setattr(module.ctypes, "WinDLL", lambda *_a, **_k: kernel, raising=False)

    assert module._create_owned_job() == 11
    assert (
        kernel.SetInformationJobObject.calls[0][1] == module._JOB_OBJECT_EXTENDED_LIMIT_INFORMATION
    )
    assert (
        module.ctypes.cast(
            kernel.SetInformationJobObject.calls[0][2],
            module.ctypes.POINTER(module._ExtendedLimitInformation),
        ).contents.BasicLimitInformation.LimitFlags
        == module._KILL_ON_JOB_CLOSE
    )
    assert kernel.AssignProcessToJobObject.calls[0][1] == 22

    module._close_job(11)
    assert kernel.CloseHandle.calls == [(11,)]


def test_windows_bootstrap_does_not_hide_job_handle_close_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_windows_bootstrap(monkeypatch)
    kernel = _fake_kernel32()
    kernel.CloseHandle.result = 0
    monkeypatch.setattr(module.ctypes, "WinDLL", lambda *_a, **_k: kernel, raising=False)
    monkeypatch.setattr(
        module.ctypes,
        "WinError",
        lambda *_a: OSError("CloseHandle failed"),
        raising=False,
    )
    monkeypatch.setattr(module.ctypes, "get_last_error", lambda: 5, raising=False)

    with pytest.raises(OSError, match="CloseHandle failed"):
        module._close_job(11)


@pytest.mark.parametrize("failed_api", ["create", "set_info", "assign"])
def test_windows_bootstrap_job_setup_fails_closed(
    monkeypatch: pytest.MonkeyPatch, failed_api: str
) -> None:
    module = _load_windows_bootstrap(monkeypatch)
    values = {"create": 11, "set_info": 1, "assign": 1}
    values[failed_api] = 0
    kernel = _fake_kernel32(**values)
    monkeypatch.setattr(module.ctypes, "WinDLL", lambda *_a, **_k: kernel, raising=False)
    monkeypatch.setattr(
        module.ctypes, "WinError", lambda *_a: OSError("Windows API failure"), raising=False
    )

    with pytest.raises(OSError, match="Windows API failure"):
        module._create_owned_job()

    if failed_api != "create":
        assert kernel.CloseHandle.calls == [(11,)]


def _run_bootstrap_main(
    monkeypatch: pytest.MonkeyPatch,
    module: types.ModuleType,
    config: bytes,
    *,
    child_factory: Any,
    job_error: OSError | None = None,
) -> tuple[int, dict[str, Any] | None]:
    config_read, config_write = os.pipe()
    os.write(config_write, config)
    os.close(config_write)
    status_read, status_write = os.pipe()
    monkeypatch.setattr(module.sys, "argv", ["bootstrap", str(config_read), str(status_write)])
    closed_jobs: list[int] = []
    if job_error is None:
        monkeypatch.setattr(module, "_create_owned_job", lambda: 77)
    else:

        def fail_job() -> int:
            raise job_error

        monkeypatch.setattr(module, "_create_owned_job", fail_job)
    monkeypatch.setattr(
        module, "_close_job", lambda job: closed_jobs.append(job) if job is not None else None
    )
    monkeypatch.setattr(module.subprocess, "Popen", child_factory)
    result = module.main()
    try:
        payload = os.read(status_read, 65_537)
    finally:
        os.close(status_read)
    status = json.loads(payload.decode("ascii")) if payload else None
    if job_error is None:
        assert closed_jobs == [77]
    else:
        assert closed_jobs == []
    return result, status


def test_windows_bootstrap_main_reports_result_and_launch_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_windows_bootstrap(monkeypatch)
    config = json.dumps({"argv": ["solver"], "cwd": ".", "environment": {}}).encode("ascii")

    class Child:
        returncode = 4

        def wait(self) -> int:
            return self.returncode

    result, status = _run_bootstrap_main(
        monkeypatch, module, config, child_factory=lambda *_a, **_k: Child()
    )
    assert result == 0
    assert status == {"kind": "result", "returncode": 4}

    result, status = _run_bootstrap_main(
        monkeypatch,
        module,
        config,
        child_factory=lambda *_a, **_k: (_ for _ in ()).throw(OSError("launch denied")),
    )
    assert result == 126
    assert status is not None and status["kind"] == "launch_error"


def test_windows_bootstrap_main_fails_closed_before_child_launch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_windows_bootstrap(monkeypatch)
    config = json.dumps({"argv": ["solver"], "cwd": ".", "environment": {}}).encode("ascii")
    launched = False

    def forbidden_child(*_args: Any, **_kwargs: Any) -> None:
        nonlocal launched
        launched = True

    result, status = _run_bootstrap_main(
        monkeypatch,
        module,
        config,
        child_factory=forbidden_child,
        job_error=OSError("job unavailable"),
    )
    assert result == 125
    assert status is not None and status["kind"] == "containment_error"
    assert not launched


@pytest.mark.parametrize("arguments", [["bootstrap"], ["bootstrap", "bad", "2"]])
def test_windows_bootstrap_main_rejects_invalid_handles(
    monkeypatch: pytest.MonkeyPatch,
    arguments: list[str],
) -> None:
    module = _load_windows_bootstrap(monkeypatch)
    monkeypatch.setattr(module.sys, "argv", arguments)

    assert module.main() == 125


def test_windows_bootstrap_script_exit_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    _load_windows_bootstrap(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["bootstrap"])
    path = Path(process_module.__file__).with_name("windows_process_bootstrap.py")

    with pytest.raises(SystemExit) as captured:
        runpy.run_path(str(path), run_name="__main__")

    assert captured.value.code == 125
