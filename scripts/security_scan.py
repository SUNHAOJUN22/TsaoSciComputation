from __future__ import annotations

import json
import re
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "dist",
    "dist-a",
    "dist-b",
    "build",
}
SKIP_FILES = {".coverage"}
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".zip", ".whl", ".gz", ".pyc"}
PATTERNS = {
    "private_key": re.compile("-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile("gh[pousr]_[A-Za-z0-9]{30,}"),
    "aws_key": re.compile("AKIA[0-9A-Z]{16}"),
    "dangerous_eval": re.compile("\\b(?:eval|exec)\\s*\\("),
    "shell_true": re.compile("shell\\s*=\\s*True"),
}


def scan(root: Path) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    scanned = 0
    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if (
            not path.is_file()
            or path.name in SKIP_FILES
            or any(part in SKIP_DIRS or part.endswith(".egg-info") for part in relative_parts)
            or path.suffix.lower() in BINARY_SUFFIXES
        ):
            continue
        relative = path.relative_to(root).as_posix()
        if relative == "scripts/security_scan.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scanned += 1
        for name, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                findings.append({"path": relative, "rule": name, "offset": match.start()})
    return {"schema_version": "1.0", "files_scanned": scanned, "findings": findings}


def main() -> int:
    report = scan(Path("."))
    output = Path("evidence/security-scan.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
