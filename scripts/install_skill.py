from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import _bootstrap  # noqa: F401

from tsao_computation.provenance.manifest import iter_repository_entries

SKILL_NAME = "TsaoSciComputation"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_NAME = ".tsao-install.json"
AGENT_ROOTS = {
    "codex": ".codex/skills",
    "claude": ".claude/skills",
    "open-agent-skills": ".agents/skills",
}


def resolve_destination(
    agent: str,
    scope: str,
    target: Path | None,
    *,
    cwd: Path | None = None,
    home: Path | None = None,
) -> Path:
    if target is not None:
        expanded = target.expanduser().resolve()
        return expanded if expanded.name == SKILL_NAME else expanded / SKILL_NAME
    base = (home or Path.home()) if scope == "user" else (cwd or Path.cwd())
    return (base / AGENT_ROOTS[agent] / SKILL_NAME).resolve()


def validate_installation(destination: Path) -> list[str]:
    problems: list[str] = []
    required = ("SKILL.md", "VERSION", "manifest.json", "scripts/verify_all.py")
    for relative in required:
        if not (destination / relative).is_file():
            problems.append(f"missing required file: {relative}")
    skill_path = destination / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        if "name: TsaoSciComputation" not in text:
            problems.append("SKILL.md does not register TsaoSciComputation")
    return problems


def _source_files(source: Path, destination: Path) -> list[tuple[Path, Path]]:
    source = source.resolve()
    destination = destination.resolve()
    files: list[tuple[Path, Path]] = []
    for path in iter_repository_entries(source):
        if path == destination or destination in path.parents:
            continue
        relative = path.relative_to(source)
        if path.is_symlink():
            raise ValueError(f"source tree contains symlink: {relative.as_posix()}")
        if path.is_file():
            files.append((path, relative))
    return files


def install_skill(
    source: Path,
    destination: Path,
    *,
    agent: str,
    scope: str,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    files = _source_files(source, destination)
    if destination.exists() and not force:
        raise FileExistsError(f"destination exists; use --force: {destination}")
    if dry_run:
        print(f"DRY-RUN install {len(files)} files to {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tsao-install-", dir=destination.parent) as temporary:
        staging = Path(temporary) / SKILL_NAME
        staging.mkdir()
        for source_path, relative in files:
            target_path = staging / relative
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)
        receipt = {
            "agent": agent,
            "schema_version": "1.0",
            "scope": scope,
            "skill": SKILL_NAME,
            "version": (source / "VERSION").read_text(encoding="utf-8").strip(),
        }
        (staging / RECEIPT_NAME).write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        problems = validate_installation(staging)
        if problems:
            raise ValueError(f"staged installation is invalid: {problems}")
        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(staging), destination)


def uninstall_skill(destination: Path, *, force: bool = False, dry_run: bool = False) -> None:
    if not destination.exists():
        raise FileNotFoundError(f"installation not found: {destination}")
    receipt = destination / RECEIPT_NAME
    if not receipt.is_file() and not force:
        raise ValueError(f"refusing to remove an unverified directory; use --force: {destination}")
    if receipt.is_file():
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        if payload.get("skill") != SKILL_NAME and not force:
            raise ValueError(f"receipt does not belong to {SKILL_NAME}")
    if dry_run:
        print(f"DRY-RUN uninstall {destination}")
        return
    shutil.rmtree(destination)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install or validate TsaoSciComputation.")
    parser.add_argument("--agent", choices=tuple(AGENT_ROOTS), default="codex")
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--target", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--uninstall", action="store_true")
    action.add_argument("--validate", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    destination = resolve_destination(args.agent, args.scope, args.target)
    try:
        if args.uninstall:
            uninstall_skill(destination, force=args.force, dry_run=args.dry_run)
        elif args.validate:
            problems = validate_installation(destination)
            if problems:
                print(json.dumps({"destination": str(destination), "problems": problems}, indent=2))
                return 1
            print(json.dumps({"destination": str(destination), "status": "VALID"}, indent=2))
        else:
            install_skill(
                REPOSITORY_ROOT,
                destination,
                agent=args.agent,
                scope=args.scope,
                force=args.force,
                dry_run=args.dry_run,
            )
            print(json.dumps({"destination": str(destination), "status": "INSTALLED"}, indent=2))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
