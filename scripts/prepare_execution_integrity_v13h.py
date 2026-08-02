from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    path = ROOT / "scripts/prepare_execution_integrity_v13g.py"
    text = path.read_text(encoding="utf-8")
    old = '''    runpy.run_path(str(ROOT / "scripts/prepare_execution_integrity_v13e.py"), run_name="__main__")
    write_coverage_tests()
'''
    new = '''    namespace = runpy.run_path(
        str(ROOT / "scripts/prepare_execution_integrity_v13e.py"),
        run_name="execution_integrity_v13e",
    )
    namespace["main"]()
    write_coverage_tests()
'''
    if text.count(old) != 1:
        raise SystemExit("V13G nested preparer invocation anchor mismatch")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
    namespace = runpy.run_path(str(path), run_name="execution_integrity_v13g")
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
