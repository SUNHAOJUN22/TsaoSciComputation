from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise ValueError(f"expected one {label}, found {text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


process = ROOT / "tsao_computation/security/process.py"
replace_once(
    process,
    '''    resolved_cwd = cwd.expanduser().resolve(strict=True)
    if not resolved_cwd.is_dir():
        raise SecurityError(f"working directory does not exist: {cwd}")
''',
    '''    try:
        resolved_cwd = cwd.expanduser().resolve(strict=True)
    except OSError as error:
        raise SecurityError(f"working directory does not exist: {cwd}") from error
    if not resolved_cwd.is_dir():
        raise SecurityError(f"working directory does not exist: {cwd}")
''',
    "safe_run working directory normalization",
)

extended = ROOT / "tests/test_extended.py"
replace_once(
    extended,
    '    assert plan.argv == (sys.executable, "input.inp")\n',
    '    assert Path(plan.argv[0]).resolve() == Path(sys.executable).resolve()\n    assert plan.argv[1:] == ("input.inp",)\n',
    "resolved executable assertion",
)

print("phase A runtime edge corrections applied")
