from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, got {count} for {old!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def replace_between(path: str, start: str, end: str, replacement: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"{path}: section markers are not unique")
    before, remainder = text.split(start, 1)
    _, after = remainder.split(end, 1)
    target.write_text(before + replacement + end + after, encoding="utf-8", newline="\n")


Path("tsao_computation/accelerators/audit.py").write_bytes(
    Path(".github/payloads/acceleration-audit-v3/audit.py").read_bytes()
)
Path("tests/test_acceleration_opportunity_audit.py").write_bytes(
    Path(".github/payloads/acceleration-audit-v3/test_acceleration_opportunity_audit.py").read_bytes()
)
Path("assets/visuals/acceleration-opportunity-pipeline.svg").write_bytes(
    Path(".github/payloads/acceleration-audit-v3/acceleration-opportunity-pipeline.svg").read_bytes()
)

audit_import = '''from .audit import (\n    AccelerationOpportunity,\n    RepositoryAccelerationAudit,\n    audit_acceleration,\n    audit_repository_acceleration,\n)\n'''
replace_once(
    "tsao_computation/accelerators/__init__.py",
    "from .catalog import (",
    audit_import + "from .catalog import (",
)
replace_once(
    "tsao_computation/accelerators/__init__.py",
    '__all__ = [\n    "AccelerationLibrary",',
    '__all__ = [\n    "AccelerationLibrary",\n    "AccelerationOpportunity",',
)
replace_once(
    "tsao_computation/accelerators/__init__.py",
    '    "ResourceRequest",\n    "acceleration_libraries",',
    '    "RepositoryAccelerationAudit",\n    "ResourceRequest",\n    "acceleration_libraries",\n    "audit_acceleration",\n    "audit_repository_acceleration",',
)

replace_once(
    "tsao_computation/acceleration.py",
    "from .accelerators import (\n    AccelerationLibrary,",
    "from .accelerators import (\n    AccelerationLibrary,\n    AccelerationOpportunity,",
)
replace_once(
    "tsao_computation/acceleration.py",
    "    PrecisionPolicy,\n    ResourceRequest,",
    "    PrecisionPolicy,\n    RepositoryAccelerationAudit,\n    ResourceRequest,",
)
replace_once(
    "tsao_computation/acceleration.py",
    "    acceleration_libraries,\n    acceleration_plan,",
    "    acceleration_libraries,\n    acceleration_plan,\n    audit_acceleration,\n    audit_repository_acceleration,",
)
replace_once(
    "tsao_computation/acceleration.py",
    '__all__ = [\n    "AccelerationLibrary",',
    '__all__ = [\n    "AccelerationLibrary",\n    "AccelerationOpportunity",',
)
replace_once(
    "tsao_computation/acceleration.py",
    '    "PrecisionPolicy",\n    "ResourceRequest",',
    '    "PrecisionPolicy",\n    "RepositoryAccelerationAudit",\n    "ResourceRequest",',
)
replace_once(
    "tsao_computation/acceleration.py",
    '    "acceleration_libraries",\n    "acceleration_plan",',
    '    "acceleration_libraries",\n    "acceleration_plan",\n    "audit_acceleration",\n    "audit_repository_acceleration",',
)

parser_marker = '    advice.add_argument("--limit", type=int, default=8)\n\n    orchestrate = subparsers.add_parser('
parser_addition = '''    advice.add_argument("--limit", type=int, default=8)\n\n    audit = subparsers.add_parser(\n        "audit-acceleration",\n        help="statically audit repository source for evidence-bound acceleration candidates",\n    )\n    audit.add_argument("--root", type=Path, default=Path("."))\n    audit.add_argument("--include-tests", action="store_true")\n    audit.add_argument("--limit", type=int, default=40)\n    audit.add_argument("--min-score", type=int, default=40)\n    audit.add_argument("--max-python-bytes", type=int, default=2_000_000)\n    audit.add_argument("--output", type=Path)\n\n    orchestrate = subparsers.add_parser('''
replace_once("tsao_computation/cli.py", parser_marker, parser_addition)

command_marker = '        elif args.command == "plan":\n'
command_addition = '''        elif args.command == "audit-acceleration":\n            from .accelerators import audit_repository_acceleration\n\n            payload = audit_repository_acceleration(\n                args.root,\n                include_tests=args.include_tests,\n                limit=args.limit,\n                min_score=args.min_score,\n                max_python_bytes=args.max_python_bytes,\n            ).to_dict()\n            if args.output is not None:\n                args.output.parent.mkdir(parents=True, exist_ok=True)\n                args.output.write_text(\n                    json.dumps(\n                        payload,\n                        ensure_ascii=False,\n                        indent=2,\n                        sort_keys=True,\n                        allow_nan=False,\n                    )\n                    + "\\n",\n                    encoding="utf-8",\n                    newline="\\n",\n                )\n            _json(payload)\n        elif args.command == "plan":\n'''
replace_once("tsao_computation/cli.py", command_marker, command_addition)

replace_once(
    "README.md",
    "The 42 self-contained SVGs use **Scientific Research Console V13**. The root README showcases 11 representative diagrams;",
    "The 43 self-contained SVGs use **Scientific Research Console V13**. The root README showcases 12 representative diagrams;",
)
readme_marker = '<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC checkpointing and bounded recovery" width="100%">\n\nArchitecture, CUDA-X selection rules and C++ migration gates:'
readme_addition = '''<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC checkpointing and bounded recovery" width="100%">\n<img src="assets/visuals/acceleration-opportunity-pipeline.svg" alt="Evidence-bound repository acceleration opportunity audit" width="100%">\n\n### Executable repository source audit\n\n```bash\npython -m tsao_computation audit-acceleration \\\n  --root . --limit 50 --min-score 40 \\\n  --output reports/ACCELERATION_OPPORTUNITIES_V2.json\n```\n\nThe audit inventories Python, C, C++, CUDA, Fortran, Rust and Julia source; parses Python without executing it; records file, line and symbol evidence; and ranks dense, sparse, FFT, tensor, equivariant-ML, stochastic, solver-dispatch, filesystem and arithmetic-loop candidates. It recommends profiling, CPU/vectorized baselines, C++20/OpenMP, solver-native acceleration or CUDA-X candidates without claiming measured speedup.\n\n<!-- ACCELERATION_AUDIT_SUMMARY:START -->\nThe machine-readable report is refreshed by the qualification workflow.\n<!-- ACCELERATION_AUDIT_SUMMARY:END -->\n\nArchitecture, CUDA-X selection rules and C++ migration gates:'''
replace_once("README.md", readme_marker, readme_addition)

replace_once(
    "README.zh-CN.md",
    "仓库内 42 幅自包含 SVG 使用 **Scientific Research Console V13**。根 README 展示 11 幅代表性示意图；",
    "仓库内 43 幅自包含 SVG 使用 **Scientific Research Console V13**。根 README 展示 12 幅代表性示意图；",
)
zh_marker = '<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC 检查点与有边界恢复" width="100%">\n\n架构、CUDA-X 选型和 C++ 迁移门禁见'
zh_addition = '''<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC 检查点与有边界恢复" width="100%">\n<img src="assets/visuals/acceleration-opportunity-pipeline.svg" alt="证据约束型仓库加速机会审计" width="100%">\n\n### 可执行的仓库源码审计\n\n```bash\npython -m tsao_computation audit-acceleration \\\n  --root . --limit 50 --min-score 40 \\\n  --output reports/ACCELERATION_OPPORTUNITIES_V2.json\n```\n\n该审计统计 Python、C、C++、CUDA、Fortran、Rust 与 Julia 源码；在不执行源码的前提下解析 Python AST；保留文件、行号和符号证据；并对稠密/稀疏线性代数、FFT、张量收缩、等变机器学习、随机采样、外部求解器调度、文件系统扫描和算术循环进行排序。它可以推荐性能剖析、CPU/向量化基线、C++20/OpenMP、求解器原生加速或 CUDA-X 候选，但不声称已经取得实测加速。\n\n<!-- ACCELERATION_AUDIT_SUMMARY:START -->\n机器可读报告由资格验证工作流刷新。\n<!-- ACCELERATION_AUDIT_SUMMARY:END -->\n\n架构、CUDA-X 选型和 C++ 迁移门禁见'''
replace_once("README.zh-CN.md", zh_marker, zh_addition)

replace_once(
    "assets/visuals/README.md",
    "The root READMEs showcase 11 representative diagrams",
    "The root READMEs showcase 12 representative diagrams",
)
replace_once(
    "assets/visuals/README.md",
    "All 42 assets declare",
    "All 43 assets declare",
)
replace_once(
    "assets/visuals/README.md",
    "The root READMEs show 11 representative images",
    "The root READMEs show 12 representative images",
)
replace_once(
    "assets/visuals/README.md",
    "- `hpc-failure-recovery.svg` — checkpoints, failure classification and bounded recovery",
    "- `hpc-failure-recovery.svg` — checkpoints, failure classification and bounded recovery\n- `acceleration-opportunity-pipeline.svg` — source inventory, AST evidence, candidate ranking and qualification gates",
)

replace_once(
    "assets/visuals/DESIGN_SYSTEM.md",
    "the root READMEs surface 11 representative diagrams while the atlas retains all 42.",
    "the root READMEs surface 12 representative diagrams while the atlas retains all 43.",
)
replace_once(
    "assets/visuals/DESIGN_SYSTEM.md",
    "the hero and eight detailed diagrams are full width",
    "the hero and nine detailed diagrams are full width",
)

replace_once(
    "tests/test_readme_visuals.py",
    '    "workflow": 23,',
    '    "workflow": 24,',
)
replace_once(
    "tests/test_readme_visuals.py",
    '    "hpc-failure-recovery.svg",\n}',
    '    "hpc-failure-recovery.svg",\n    "acceleration-opportunity-pipeline.svg",\n}',
)
replace_once(
    "tests/test_readme_visuals.py",
    "assert len(FEATURED_FILES) == 11",
    "assert len(FEATURED_FILES) == 12",
)
replace_once(
    "tests/test_readme_visuals.py",
    "assert len(names) == 42",
    "assert len(names) == 43",
)

docs_start = "The current `main` baseline contains 570 source and project files before this change:\n"
docs_end = "## Implemented native boundary"
docs_replacement = '''The repository now provides a deterministic executable audit instead of relying on stale prose counts.\n\n```bash\npython -m tsao_computation audit-acceleration \\\n  --root . --limit 50 --min-score 40 \\\n  --output reports/ACCELERATION_OPPORTUNITIES_V2.json\n```\n\nThe audit inventories Python, C, C++, CUDA, Fortran, Rust and Julia files and lines, parses\nPython ASTs without importing or executing target modules, records file/line/symbol evidence,\nand ranks explicit dense, sparse, FFT, tensor, equivariant-ML, stochastic, solver-dispatch,\nfilesystem and arithmetic-loop patterns. Its report is static evidence, not a profiler result.\n\nRepository-local work remains predominantly orchestration, validation, registries, hashing,\nI/O and bounded process planning. Those paths should first use caching, streaming, fewer\nfilesystem passes and bounded task parallelism. Expensive scientific numerics should continue\nto prefer external solvers' supported GPU, MPI, OpenMP, Kokkos or vendor-library paths before\na repository-owned kernel is created.\n\n'''
replace_between("docs/accelerated-native-backend.md", docs_start, docs_end, docs_replacement)
replace_once(
    "docs/accelerated-native-backend.md",
    "- CTest and pytest coverage with CPU-only fallback.",
    "- CTest and pytest coverage with CPU-only fallback.\n- Deterministic AST-based repository acceleration audit with machine-readable ranking evidence.",
)

replace_once(
    "CHANGELOG.md",
    "## Unreleased\n\n",
    "## Unreleased\n\n- Added a deterministic repository acceleration audit with language composition, Python AST evidence, ranked C++/OpenMP/CUDA-X candidates, a machine-readable report, CLI coverage and a dedicated qualification visual.\n",
)

for payload in Path(".github/payloads/acceleration-audit-v3").glob("*"):
    payload.unlink()
Path(".github/payloads/acceleration-audit-v3").rmdir()
Path(".github/workflows/apply-acceleration-audit-v3-once.yml").unlink()
