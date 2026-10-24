"""Private Windows bootstrap for hash-authorized process-tree execution."""

from __future__ import annotations

import ctypes
import json
import msvcrt
import os
import subprocess  # nosec B404 - launches only the received authorized argv
import sys
from ctypes import wintypes
from typing import Any, Protocol, cast

_MAX_CONFIG_BYTES = 1_048_576
_KILL_ON_JOB_CLOSE = 0x2000
_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9


class _WindowsMsvcrt(Protocol):
    def open_osfhandle(self, handle: int, flags: int) -> int: ...


class _WindowsOS(Protocol):
    O_BINARY: int


class _Win32Function(Protocol):
    argtypes: Any
    restype: Any

    def __call__(self, *args: Any) -> Any: ...


class _Kernel32(Protocol):
    CreateJobObjectW: _Win32Function
    SetInformationJobObject: _Win32Function
    GetCurrentProcess: _Win32Function
    AssignProcessToJobObject: _Win32Function
    CloseHandle: _Win32Function


class _WindowsCtypes(Protocol):
    def WinDLL(self, name: str, *, use_last_error: bool) -> _Kernel32: ...

    def WinError(self, code: int) -> OSError: ...

    def get_last_error(self) -> int: ...


class _BasicLimitInformation(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]


class _ExtendedLimitInformation(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimitInformation),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def _status(handle: int, value: dict[str, Any]) -> None:
    # Typeshed omits these Windows-only members when tests run on POSIX.
    windows_msvcrt = cast(_WindowsMsvcrt, msvcrt)
    windows_os = cast(_WindowsOS, os)
    descriptor = windows_msvcrt.open_osfhandle(handle, os.O_WRONLY | windows_os.O_BINARY)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode("ascii"))


def _read_config(handle: int) -> dict[str, Any]:
    windows_msvcrt = cast(_WindowsMsvcrt, msvcrt)
    windows_os = cast(_WindowsOS, os)
    descriptor = windows_msvcrt.open_osfhandle(handle, os.O_RDONLY | windows_os.O_BINARY)
    with os.fdopen(descriptor, "rb") as stream:
        payload = stream.read(_MAX_CONFIG_BYTES + 1)
    if len(payload) > _MAX_CONFIG_BYTES:
        raise ValueError("authorized process configuration exceeds the size limit")
    data = json.loads(payload.decode("ascii"))
    if not isinstance(data, dict):
        raise ValueError("authorized process configuration must be an object")
    argv = data.get("argv")
    environment = data.get("environment")
    if (
        not isinstance(argv, list)
        or not argv
        or any(not isinstance(item, str) or not item for item in argv)
        or not isinstance(data.get("cwd"), str)
        or not isinstance(environment, dict)
        or any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in environment.items()
        )
    ):
        raise ValueError("authorized process configuration has invalid fields")
    return data


def _create_owned_job() -> int:
    windows_ctypes = cast(_WindowsCtypes, ctypes)
    kernel32 = windows_ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    kernel32.SetInformationJobObject.restype = wintypes.BOOL
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel32.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise windows_ctypes.WinError(windows_ctypes.get_last_error())
    limits = _ExtendedLimitInformation()
    limits.BasicLimitInformation.LimitFlags = _KILL_ON_JOB_CLOSE
    if not kernel32.SetInformationJobObject(
        job,
        _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
        ctypes.byref(limits),
        ctypes.sizeof(limits),
    ):
        error = windows_ctypes.WinError(windows_ctypes.get_last_error())
        kernel32.CloseHandle(job)
        raise error
    if not kernel32.AssignProcessToJobObject(job, kernel32.GetCurrentProcess()):
        error = windows_ctypes.WinError(windows_ctypes.get_last_error())
        kernel32.CloseHandle(job)
        raise error
    return job


def _close_job(job: int | None) -> None:
    if job is not None:
        windows_ctypes = cast(_WindowsCtypes, ctypes)
        kernel32 = windows_ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        if not kernel32.CloseHandle(job):
            raise windows_ctypes.WinError(windows_ctypes.get_last_error())


def main() -> int:
    if len(sys.argv) != 3:
        return 125
    try:
        config_handle = int(sys.argv[1])
        status_handle = int(sys.argv[2])
    except ValueError:
        return 125

    job: int | None = None
    try:
        config = _read_config(config_handle)
        try:
            job = _create_owned_job()
        except OSError as error:
            _status(status_handle, {"kind": "containment_error", "message": str(error)[:2048]})
            return 125
        try:
            child = subprocess.Popen(
                tuple(config["argv"]),
                cwd=config["cwd"],
                env=config["environment"],
                shell=False,  # nosec B603 - exact command was approved by the parent
                close_fds=True,
            )
        except OSError as error:
            _status(status_handle, {"kind": "launch_error", "message": str(error)[:2048]})
            return 126
        returncode = child.wait()
        _status(status_handle, {"kind": "result", "returncode": int(returncode)})
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError):
        return 125
    finally:
        _close_job(job)


if __name__ == "__main__":
    raise SystemExit(main())
