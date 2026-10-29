from __future__ import annotations

import io
import json
import locale
import os
import re
import shutil
import signal
import subprocess  # nosec B404
import sys
import threading
import time
from collections.abc import Mapping, Sequence
from contextlib import suppress
from pathlib import Path
from typing import BinaryIO, Protocol, cast

from ..errors import SecurityError
from ..hashing import strict_json_loads


class _WindowsMsvcrt(Protocol):
    def get_osfhandle(self, fd: int) -> int: ...


class _WindowsOS(Protocol):
    def set_handle_inheritable(self, handle: int, inheritable: bool) -> None: ...


class _WindowsStartupInfo(Protocol):
    lpAttributeList: dict[str, list[int]]


class _WindowsSubprocess(Protocol):
    def STARTUPINFO(self) -> _WindowsStartupInfo: ...


_PORTABLE_ENVIRONMENT_KEYS = ("PATH", "HOME", "TEMP", "TMP", "TMPDIR", "LANG", "LC_ALL", "LC_CTYPE")
_WINDOWS_ENVIRONMENT_KEYS = (
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "SYSTEMDRIVE",
    "USERPROFILE",
    "APPDATA",
    "LOCALAPPDATA",
)
_SAFE_OVERRIDE_KEYS = frozenset(
    {
        "CUDA_VISIBLE_DEVICES",
        "HIP_VISIBLE_DEVICES",
        "ROCR_VISIBLE_DEVICES",
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    }
)
_READ_ONLY_PROBE_ARGUMENTS = frozenset(
    {
        ("--version",),
        ("-version",),
        ("version",),
        ("info",),
        ("info", "--version"),
        ("-v",),
        ("-h",),
        ("--help",),
        ("-help",),
        ("mdrun", "-h"),
    }
)
_MAX_PROBE_OUTPUT_CHARS = 65_536
_MAX_PROCESS_CONFIG_BYTES = 1_048_576
_PROCESS_CLEANUP_TIMEOUT_SECONDS = 5.0


def _write_process_config(
    channel: BinaryIO,
    payload: bytes,
    errors: list[OSError],
) -> None:
    try:
        with channel:
            channel.write(payload)
    except OSError as error:
        errors.append(error)


def _decode_process_output(output: bytes | None) -> str | None:
    if output is None:
        return None
    with io.TextIOWrapper(
        io.BytesIO(output),
        encoding=locale.getpreferredencoding(False),
        newline=None,
    ) as stream:
        return stream.read()


_PROBE_ARGUMENTS: dict[str, frozenset[tuple[str, ...]]] = {
    "nvidia-smi": frozenset(
        {
            (
                "--query-gpu=index,name,memory.total,compute_cap",
                "--format=csv,noheader,nounits",
            ),
            (
                "--query-gpu=index,name,memory.total",
                "--format=csv,noheader,nounits",
            ),
        }
    ),
    "rocminfo": frozenset({()}),
    "sycl-ls": frozenset({()}),
    "clinfo": frozenset({("-l",)}),
}
_PYTHON_MODULE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")
_PROCESS_EXECUTION_PERMIT = object()


def _override_allowed(key: str) -> bool:
    normalized = key.upper()
    return (
        normalized in _SAFE_OVERRIDE_KEYS
        or normalized in _PORTABLE_ENVIRONMENT_KEYS
        or normalized in _WINDOWS_ENVIRONMENT_KEYS
        or normalized.startswith("TSAO_")
    )


def _subprocess_environment(
    overrides: Mapping[str, str] | None = None,
    *,
    parent: Mapping[str, str] | None = None,
    platform_name: str | None = None,
) -> dict[str, str]:
    source = os.environ if parent is None else parent
    platform = os.name if platform_name is None else platform_name
    allowed = _PORTABLE_ENVIRONMENT_KEYS + (_WINDOWS_ENVIRONMENT_KEYS if platform == "nt" else ())
    if platform == "nt":
        source_by_name = {str(key).casefold(): str(value) for key, value in source.items()}
        merged = {
            name: source_by_name[name.casefold()]
            for name in allowed
            if name.casefold() in source_by_name
        }
    else:
        merged = {name: str(source[name]) for name in allowed if name in source}
    merged.setdefault("PATH", "")
    merged["LANG"] = "C.UTF-8"
    if overrides:
        unsafe = sorted(str(key) for key in overrides if not _override_allowed(str(key)))
        if unsafe:
            raise SecurityError(f"unsafe subprocess environment overrides: {unsafe}")
        for raw_key, raw_value in overrides.items():
            key = str(raw_key)
            value = str(raw_value)
            if not value or "\x00" in value:
                raise SecurityError(f"invalid subprocess environment value: {key}")
            if platform == "nt":
                for existing in tuple(merged):
                    if existing.casefold() == key.casefold():
                        del merged[existing]
            merged[key] = value
    return merged


def _validated_cwd(cwd: Path) -> Path:
    try:
        resolved = cwd.expanduser().resolve(strict=True)
    except OSError as error:
        raise SecurityError(f"working directory does not exist: {cwd}") from error
    if not resolved.is_dir():
        raise SecurityError(f"working directory does not exist: {cwd}")
    return resolved


def _validated_executable(executable: str, *, preserve_symlink: bool = False) -> Path:
    if not isinstance(executable, str) or not executable or "\x00" in executable:
        raise SecurityError("executable must be a non-empty string")
    candidate = Path(executable).expanduser()
    found = str(candidate) if candidate.is_absolute() else shutil.which(executable)
    if not found:
        raise SecurityError(f"executable not detected: {executable}")
    try:
        resolved = Path(found).resolve(strict=True)
    except OSError as error:
        raise SecurityError(f"executable not detected: {executable}") from error
    if not resolved.is_file() or (os.name != "nt" and not os.access(resolved, os.X_OK)):
        raise SecurityError(f"executable is not runnable: {executable}")
    # Python derives virtual-environment identity from its invoked path. Checking
    # the target is necessary, but replacing a venv symlink with that target
    # would inspect the base interpreter's packages instead of the selected venv.
    return Path(found).absolute() if preserve_symlink else resolved


def _run_prepared(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout: float,
    environment: Mapping[str, str],
) -> subprocess.CompletedProcess[str]:
    if not argv or any(not isinstance(item, str) or not item or "\x00" in item for item in argv):
        raise SecurityError("argv must be a non-empty sequence of non-empty strings")
    if timeout <= 0 or timeout > 86400:
        raise SecurityError("timeout must be within (0, 86400] seconds")
    if any(
        not key or not value or "\x00" in key or "\x00" in value
        for key, value in environment.items()
    ):
        raise SecurityError("prepared subprocess environment contains invalid entries")
    validated_cwd = _validated_cwd(cwd)
    if os.name == "nt":
        return _run_windows_job(
            tuple(argv),
            cwd=validated_cwd,
            timeout=timeout,
            environment=environment,
        )
    return _run_posix_group(
        tuple(argv),
        cwd=validated_cwd,
        timeout=timeout,
        environment=environment,
    )


def _run_posix_group(
    argv: tuple[str, ...],
    *,
    cwd: Path,
    timeout: float,
    environment: Mapping[str, str],
) -> subprocess.CompletedProcess[str]:
    """Kill same-process-group descendants on timeout; setsid() can escape this boundary."""

    process: subprocess.Popen[bytes] = subprocess.Popen(
        argv,
        cwd=cwd,
        env=dict(environment),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,  # nosec B603
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as error:
        termination_error = _terminate_posix_group(process)
        final_stdout, final_stderr = _finish_terminated_process(process)
        if termination_error is not None:
            raise SecurityError(
                "unable to terminate the timed-out process group"
            ) from termination_error
        raise subprocess.TimeoutExpired(
            argv,
            timeout,
            output=final_stdout,
            stderr=final_stderr,
        ) from error
    except BaseException:
        termination_error = _terminate_posix_group(process)
        _finish_terminated_process(process)
        if termination_error is not None:
            raise SecurityError(
                "unable to terminate the interrupted process group"
            ) from termination_error
        raise

    return subprocess.CompletedProcess(
        argv,
        process.returncode,
        _decode_process_output(stdout),
        _decode_process_output(stderr),
    )


def _terminate_posix_group(process: subprocess.Popen[bytes]) -> OSError | None:
    try:
        killpg = getattr(os, "killpg", None)
        sigkill = getattr(signal, "SIGKILL", None)
        if killpg is None or sigkill is None:
            raise OSError("process-group termination is unavailable")
        killpg(process.pid, sigkill)
    except ProcessLookupError:
        return None
    except OSError as error:
        with suppress(OSError):
            process.kill()
        return error
    return None


def _finish_terminated_process(
    process: subprocess.Popen[bytes],
) -> tuple[bytes | None, bytes | None]:
    try:
        return process.communicate(timeout=_PROCESS_CLEANUP_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        process.kill()
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()
        try:
            process.wait(timeout=_PROCESS_CLEANUP_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as wait_error:
            raise SecurityError("timed-out process could not be reaped") from wait_error
        raise SecurityError(
            "process descendants retained output pipes after termination"
        ) from error


def _run_windows_job(
    argv: tuple[str, ...],
    *,
    cwd: Path,
    timeout: float,
    environment: Mapping[str, str],
) -> subprocess.CompletedProcess[str]:
    """Run through a gated bootstrap so the solver starts inside a kill-on-close Job."""

    import msvcrt

    # Typeshed omits these Windows-only members when this module is checked on POSIX.
    windows_msvcrt = cast(_WindowsMsvcrt, msvcrt)
    windows_os = cast(_WindowsOS, os)
    windows_subprocess = cast(_WindowsSubprocess, subprocess)

    config = json.dumps(
        {"argv": argv, "cwd": str(cwd), "environment": dict(environment)},
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")
    if len(config) > _MAX_PROCESS_CONFIG_BYTES:
        raise SecurityError("prepared subprocess configuration exceeds its size limit")

    config_read, config_write = os.pipe()
    status_read, status_write = os.pipe()
    inherited_handles: list[int] = []
    process: subprocess.Popen[bytes] | None = None
    config_writer: threading.Thread | None = None
    config_channel: BinaryIO | None = None
    config_write_errors: list[OSError] = []
    remaining_fds = {config_read, config_write, status_read, status_write}
    try:
        config_handle = windows_msvcrt.get_osfhandle(config_read)
        status_handle = windows_msvcrt.get_osfhandle(status_write)
        for handle in (config_handle, status_handle):
            windows_os.set_handle_inheritable(handle, True)
            inherited_handles.append(handle)

        startup = windows_subprocess.STARTUPINFO()
        startup.lpAttributeList = {"handle_list": [config_handle, status_handle]}
        bootstrap = Path(__file__).with_name("windows_process_bootstrap.py")
        bootstrap_process = subprocess.Popen(
            (
                sys.executable,
                "-I",
                "-S",
                str(bootstrap),
                str(config_handle),
                str(status_handle),
            ),
            cwd=cwd,
            env=dict(environment),
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,  # nosec B603
            startupinfo=startup,
            close_fds=True,
        )
        process = bootstrap_process
        started = time.monotonic()
        for handle in inherited_handles:
            windows_os.set_handle_inheritable(handle, False)
        inherited_handles.clear()

        os.close(config_read)
        remaining_fds.remove(config_read)
        os.close(status_write)
        remaining_fds.remove(status_write)

        config_channel = os.fdopen(config_write, "wb")
        remaining_fds.remove(config_write)
        config_writer = threading.Thread(
            target=_write_process_config,
            args=(config_channel, config, config_write_errors),
            name="tsao-process-config-writer",
            daemon=True,
        )
        config_writer.start()

        remaining = max(0.0, timeout - (time.monotonic() - started))
        try:
            stdout, stderr = bootstrap_process.communicate(timeout=remaining)
        except subprocess.TimeoutExpired as error:
            bootstrap_process.kill()
            final_stdout, final_stderr = _finish_terminated_process(bootstrap_process)
            config_writer.join(timeout=_PROCESS_CLEANUP_TIMEOUT_SECONDS)
            if config_writer.is_alive():
                raise SecurityError("timed-out process configuration pipe did not close") from error
            raise subprocess.TimeoutExpired(
                argv,
                timeout,
                output=final_stdout,
                stderr=final_stderr,
            ) from error
        config_writer.join(timeout=_PROCESS_CLEANUP_TIMEOUT_SECONDS)
        if config_writer.is_alive():
            raise SecurityError("completed process configuration pipe did not close")

        with os.fdopen(status_read, "rb") as channel:
            remaining_fds.remove(status_read)
            status_bytes = channel.read(65_537)
        if len(status_bytes) > 65_536:
            raise SecurityError("Windows process bootstrap returned oversized status")
        try:
            status = json.loads(status_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SecurityError("Windows process bootstrap returned invalid status") from error
        if not isinstance(status, dict):
            raise SecurityError("Windows process bootstrap status is not an object")
        if config_write_errors and status.get("kind") != "containment_error":
            raise SecurityError(
                "Windows process configuration pipe failed"
            ) from config_write_errors[0]
        if status.get("kind") == "containment_error":
            raise SecurityError(str(status.get("message", "Windows Job Object setup failed")))
        if status.get("kind") == "launch_error":
            raise OSError(str(status.get("message", "authorized process could not start")))
        if bootstrap_process.returncode != 0:
            raise SecurityError("Windows process bootstrap exited unexpectedly")
        returncode = status.get("returncode")
        if (
            status.get("kind") != "result"
            or isinstance(returncode, bool)
            or not isinstance(returncode, int)
        ):
            raise SecurityError("Windows process bootstrap returned an incomplete result")
        return subprocess.CompletedProcess(
            argv,
            returncode,
            _decode_process_output(stdout),
            _decode_process_output(stderr),
        )
    except subprocess.TimeoutExpired:
        raise
    except BaseException:
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=_PROCESS_CLEANUP_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()
                process.wait(timeout=_PROCESS_CLEANUP_TIMEOUT_SECONDS)
        if config_writer is not None and config_writer.is_alive():
            config_writer.join(timeout=_PROCESS_CLEANUP_TIMEOUT_SECONDS)
        raise
    finally:
        if config_channel is not None:
            with suppress(OSError):
                config_channel.close()
        for handle in inherited_handles:
            with suppress(OSError):
                windows_os.set_handle_inheritable(handle, False)
        for fd in remaining_fds:
            with suppress(OSError):
                os.close(fd)


def _run_sanitized(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout: float,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run_prepared(
        argv,
        cwd=cwd,
        timeout=timeout,
        environment=_subprocess_environment(env),
    )


def safe_run(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout: float = 300.0,
    env: Mapping[str, str] | None = None,
    allow_process_execution: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Compatibility entrypoint that always denies direct process execution.

    External computation must use :func:`tsao_computation.execution.run_plan` with a
    matching hash-bound authorization. The legacy boolean is intentionally ignored
    as an authorization mechanism.
    """

    del argv, cwd, timeout, allow_process_execution
    if env:
        _subprocess_environment(env)
    raise SecurityError(
        "direct process execution is disabled; use run_plan with hash-bound authorization"
    )


def _issue_process_execution_permit() -> object:
    return _PROCESS_EXECUTION_PERMIT


def _authorized_run(
    argv: Sequence[str],
    *,
    cwd: Path,
    timeout: float = 300.0,
    environment: Mapping[str, str],
    permit: object,
) -> subprocess.CompletedProcess[str]:
    if permit is not _PROCESS_EXECUTION_PERMIT:
        raise SecurityError("internal process execution permit is invalid")
    return _run_prepared(
        argv,
        cwd=cwd,
        timeout=timeout,
        environment=environment,
    )


def probe_command_output(executable: str, arguments: tuple[str, ...]) -> str:
    """Run one allowlisted, read-only hardware discovery command."""

    resolved = _validated_executable(executable)
    slug = resolved.stem.casefold()
    allowed = _PROBE_ARGUMENTS.get(slug)
    if allowed is None or arguments not in allowed:
        raise SecurityError(f"unsupported read-only probe command: {resolved.name} {arguments}")
    try:
        result = _run_sanitized(
            (str(resolved), *arguments),
            cwd=Path.cwd(),
            timeout=8.0,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def probe_python_modules(executable: str, modules: tuple[str, ...]) -> tuple[str, ...]:
    """Inspect installed module locations without importing packages or startup hooks.

    A failed or unverifiable probe reports every requested module as unavailable;
    an empty result is returned only for a complete, request-bound response.
    """

    missing = _verified_python_modules(executable, modules)
    return modules if missing is None else missing


def _verified_python_modules(executable: str, modules: tuple[str, ...]) -> tuple[str, ...] | None:
    """Distinguish a bound metadata observation from a failed inspection.

    A group caller can retry individual requests after failure without treating
    a valid observation that every module is missing as a transport failure.
    """

    if not modules:
        return ()
    if isinstance(modules, (str, bytes)) or any(
        not isinstance(name, str) or _PYTHON_MODULE.fullmatch(name) is None for name in modules
    ):
        raise SecurityError("Python module probe names must be dotted identifiers")
    resolved = _validated_executable(executable, preserve_symlink=True)
    name = resolved.stem.casefold()
    current = Path(sys.executable).resolve(strict=True)
    if not name.startswith(("python", "pypy")) and resolved.resolve(strict=True) != current:
        raise SecurityError("Python module probes require a Python interpreter")
    script = Path(__file__).with_name("python_module_probe.py")
    try:
        result = _run_sanitized(
            (str(resolved), "-I", "-S", str(script), *modules),
            cwd=Path.cwd(),
            timeout=10.0,
        )
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None
    if result.returncode != 0 or not result.stdout or len(result.stdout) > _MAX_PROBE_OUTPUT_CHARS:
        return None
    try:
        payload = strict_json_loads(result.stdout)
    except (ValueError, RecursionError):
        return None
    if (
        not isinstance(payload, dict)
        or set(payload) != {"schema_version", "requested", "missing"}
        or type(payload["schema_version"]) is not int
        or payload["schema_version"] != 1
        or payload["requested"] != list(modules)
        or not isinstance(payload["missing"], list)
        or any(not isinstance(item, str) or item not in modules for item in payload["missing"])
    ):
        return None
    missing = tuple(payload["missing"])
    return missing if missing == tuple(name for name in modules if name in missing) else None


def read_only_probe_arguments_allowed(arguments: tuple[str, ...]) -> bool:
    return arguments in _READ_ONLY_PROBE_ARGUMENTS


def probe_read_only_command_output(
    executable: str,
    arguments: tuple[str, ...],
) -> tuple[int, str, str]:
    """Run one bounded, shell-free version/help probe.

    Only a small fixed argument set is accepted. Callers remain responsible for
    ensuring that the executable is declared by an adapter registry record.
    The result is discovery evidence only and never authorizes a calculation.
    """

    if arguments not in _READ_ONLY_PROBE_ARGUMENTS:
        raise SecurityError(f"unsupported read-only executable probe arguments: {arguments}")
    resolved = _validated_executable(executable)
    try:
        result = _run_sanitized(
            (str(resolved), *arguments),
            cwd=Path.cwd(),
            timeout=8.0,
        )
    except (OSError, subprocess.SubprocessError):
        return 127, "", ""
    return (
        result.returncode,
        result.stdout[:_MAX_PROBE_OUTPUT_CHARS],
        result.stderr[:_MAX_PROBE_OUTPUT_CHARS],
    )
