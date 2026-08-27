from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:  # pragma: no cover - temporary CI compatibility entrypoint
    args = sys.argv[1:]
    pattern: str | None = None
    glob_pattern: str | None = None
    roots: list[Path] = []
    index = 0
    while index < len(args):
        argument = args[index]
        if argument == "-n":
            index += 1
            continue
        if argument == "--glob":
            index += 1
            if index >= len(args):
                return 2
            glob_pattern = args[index]
            index += 1
            continue
        if pattern is None:
            pattern = argument
        else:
            roots.append(Path(argument))
        index += 1

    if pattern is None:
        return 2

    expression = re.compile(pattern)
    candidates: list[Path] = []
    for root in roots or [Path(".")]:
        if root.is_file():
            candidates.append(root)
        elif root.is_dir():
            candidates.extend(
                path
                for path in root.rglob(glob_pattern or "*")
                if path.is_file() and ".git" not in path.parts
            )

    matched = False
    for path in sorted(set(candidates)):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            if expression.search(line):
                print(f"{path}:{line_number}:{line}")
                matched = True
    return 0 if matched else 1
