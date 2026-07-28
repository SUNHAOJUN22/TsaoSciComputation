from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

from . import __version__
from .errors import TsaoError


def _json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tsao-computation", description="Evidence-bound scientific computation orchestration"
    )
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    route = subparsers.add_parser("route")
    route.add_argument("question")

    listing = subparsers.add_parser("list")
    listing.add_argument("kind", choices=("capabilities", "adapters", "accelerators", "workflows"))

    probe = subparsers.add_parser("probe")
    probe.add_argument("--workers", type=int, default=8)

    subparsers.add_parser(
        "probe-accelerators",
        help="detect CPU, accelerator, MPI, scheduler and edge-planning evidence",
    )

    libraries = subparsers.add_parser(
        "list-acceleration-libraries",
        help="list optional acceleration-library candidates without installing them",
    )
    libraries.add_argument("--backend")
    libraries.add_argument("--workload")

    planning = subparsers.add_parser(
        "plan-acceleration",
        help="build a fail-closed acceleration plan for one adapter",
    )
    planning.add_argument("adapter")
    planning.add_argument(
        "--resources",
        type=Path,
        help="JSON resource request; omitted means the conservative default request",
    )

    initialize = subparsers.add_parser("init")
    initialize.add_argument("--root", type=Path, default=Path("."))
    initialize.add_argument("--name", required=True)
    initialize.add_argument("--question", required=True)

    contract = subparsers.add_parser("validate-contract")
    contract.add_argument("path", type=Path)
    contract.add_argument(
        "--strict",
        action="store_true",
        help="require every field needed before solver preflight",
    )

    repository = subparsers.add_parser("validate-repository")
    repository.add_argument("--root", type=Path, default=Path("."))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "route":
            from .routing import route_question

            decision = route_question(args.question)
            _json(asdict(decision) if is_dataclass(decision) else decision)
        elif args.command == "list":
            from .registries import accelerators, adapters, capabilities, workflows

            loaders = {
                "capabilities": capabilities,
                "adapters": adapters,
                "accelerators": accelerators,
                "workflows": workflows,
            }
            _json(loaders[args.kind]())
        elif args.command == "probe":
            from .adapters import probe_all

            _json([asdict(item) for item in probe_all(args.workers)])
        elif args.command == "probe-accelerators":
            from .accelerators import probe_accelerators

            _json(probe_accelerators().to_dict())
        elif args.command == "list-acceleration-libraries":
            from .accelerators import recommend_acceleration_libraries

            _json(
                [
                    item.to_dict()
                    for item in recommend_acceleration_libraries(
                        backend=args.backend,
                        workload=args.workload,
                    )
                ]
            )
        elif args.command == "plan-acceleration":
            from .accelerators import plan_acceleration

            resources = (
                None
                if args.resources is None
                else json.loads(args.resources.read_text(encoding="utf-8"))
            )
            _json(plan_acceleration(args.adapter, resources).to_dict())
        elif args.command == "init":
            from .project import initialize_project

            print(initialize_project(args.root, name=args.name, question=args.question))
        elif args.command == "validate-contract":
            from .contracts import CalculationContract

            payload = json.loads(args.path.read_text(encoding="utf-8"))
            parsed = CalculationContract.from_dict(payload)
            if args.strict:
                parsed.assert_ready_for_preflight()
            _json(parsed.to_dict())
        elif args.command == "validate-repository":
            from .repository_audit import audit_repository

            result = audit_repository(args.root)
            _json(result)
            return 0 if result["passed"] else 1
        return 0
    except (OSError, ValueError, KeyError, TsaoError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
