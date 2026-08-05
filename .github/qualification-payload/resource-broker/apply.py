from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAYLOAD = Path(__file__).resolve().parent
WORKFLOW = ROOT / ".github" / "workflows" / "qualify-resource-broker-gpu-binding-hardening-once.yml"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label} anchor mismatch: {text.count(old)}")
    return text.replace(old, new, 1)


resources_path = ROOT / "tsao_computation" / "execution" / "resources.py"
resources = resources_path.read_text(encoding="utf-8")
start = resources.find("def validate_resource_binding(")
if start < 0 or resources.count("def validate_resource_binding(") != 1:
    raise SystemExit("resource binding function anchor mismatch")
replacement = (PAYLOAD / "resource_binding_replacement.txt").read_text(encoding="utf-8")
resources_path.write_text(
    resources[:start] + replacement,
    encoding="utf-8",
    newline="\n",
)

batch_path = ROOT / "tests" / "test_acceleration_batch.py"
batch = batch_path.read_text(encoding="utf-8")
old_license_fixture = """            resource_claims=[ExecutionResourceClaim(license_tokens=((\"solver\", 2),))],
            resource_capacity=ExecutionResourceCapacity(
                cpu_cores=1,
                license_tokens=((\"solver\", 1),),
            ),
"""
new_license_fixture = """            resource_claims=[
                ExecutionResourceClaim(
                    gpu_devices=(0,),
                    license_tokens=((\"solver\", 2),),
                )
            ],
            resource_capacity=ExecutionResourceCapacity(
                cpu_cores=1,
                gpu_devices=(0,),
                license_tokens=((\"solver\", 1),),
            ),
"""
batch = replace_once(
    batch,
    old_license_fixture,
    new_license_fixture,
    "license-capacity test fixture",
)
old_cpu_fixture = """            resource_claims=[ExecutionResourceClaim(cpu_cores=2)],
            resource_capacity=ExecutionResourceCapacity(cpu_cores=1),
"""
new_cpu_fixture = """            resource_claims=[
                ExecutionResourceClaim(cpu_cores=2, gpu_devices=(1,))
            ],
            resource_capacity=ExecutionResourceCapacity(
                cpu_cores=1,
                gpu_devices=(1,),
            ),
"""
batch = replace_once(
    batch,
    old_cpu_fixture,
    new_cpu_fixture,
    "CPU-capacity test fixture",
)
marker = "def test_resource_binding_rejects_unclaimed_visible_gpu()"
if marker in batch:
    raise SystemExit("resource binding hardening tests already exist")
appendix = (PAYLOAD / "test_acceleration_batch_append.txt").read_text(encoding="utf-8")
batch_path.write_text(batch.rstrip() + appendix + "\n", encoding="utf-8", newline="\n")

shutil.copyfile(
    PAYLOAD / "build_resource_broker_evidence.py",
    ROOT / "scripts" / "build_resource_broker_evidence.py",
)
shutil.copyfile(
    PAYLOAD / "resource-broker-gpu-binding-evidence.schema.json",
    ROOT / "schemas" / "resource-broker-gpu-binding-evidence.schema.json",
)
shutil.copyfile(
    PAYLOAD / "test_resource_broker_evidence.py",
    ROOT / "tests" / "test_resource_broker_evidence.py",
)

verify_path = ROOT / "scripts" / "verify_all.py"
verify = verify_path.read_text(encoding="utf-8")
old_verify = """        (
            "acceleration audit reports",
            (PYTHON, "scripts/build_acceleration_audits.py", "--check"),
        ),
        ("capability index", (PYTHON, "scripts/build_capability_index.py", "--check")),
"""
new_verify = """        (
            "acceleration audit reports",
            (PYTHON, "scripts/build_acceleration_audits.py", "--check"),
        ),
        (
            "resource broker GPU binding evidence",
            (PYTHON, "scripts/build_resource_broker_evidence.py", "--check"),
        ),
        ("capability index", (PYTHON, "scripts/build_capability_index.py", "--check")),
"""
verify_path.write_text(
    replace_once(verify, old_verify, new_verify, "verify_all"),
    encoding="utf-8",
    newline="\n",
)

readme_path = ROOT / "README.md"
readme = readme_path.read_text(encoding="utf-8")
old_readme = (
    "The batch execution layer now accepts immutable per-plan CPU, GPU and license-token "
    "claims plus a host capacity envelope. A condition-based resource broker prevents CPU "
    "oversubscription, exclusive-GPU collisions and license over-allocation, while binding "
    "the allocation hashes into the batch result.\n"
)
new_readme = old_readme + (
    "\nGPU admission is fail-closed in both directions: every non-empty CUDA/HIP/ROCR "
    "visible-device binding requires a matching GPU claim, and every visibility alias present "
    "in the immutable command environment must agree with that claim. Deterministic hardening "
    "evidence: [`reports/RESOURCE_BROKER_GPU_BINDING_V6_HARDENING.json`]"
    "(reports/RESOURCE_BROKER_GPU_BINDING_V6_HARDENING.json).\n"
)
readme_path.write_text(
    replace_once(readme, old_readme, new_readme, "README"),
    encoding="utf-8",
    newline="\n",
)

zh_path = ROOT / "README.zh-CN.md"
zh = zh_path.read_text(encoding="utf-8")
old_zh = (
    "批量执行层现可接收每个计划不可变的 CPU、GPU、许可证令牌声明以及主机容量包络。"
    "基于条件变量的资源代理会阻止 CPU 过度订阅、独占 GPU 冲突和许可证超额分配，"
    "并将容量与声明哈希写入批执行结果。\n"
)
new_zh = old_zh + (
    "\nGPU 准入现采用双向失败关闭：任何非空 CUDA/HIP/ROCR 可见设备绑定都必须有"
    "匹配的 GPU 资源声明；不可变命令环境中出现的每个可见设备别名都必须与该声明一致。"
    "确定性加固证据：[`reports/RESOURCE_BROKER_GPU_BINDING_V6_HARDENING.json`]"
    "(reports/RESOURCE_BROKER_GPU_BINDING_V6_HARDENING.json)。\n"
)
zh_path.write_text(
    replace_once(zh, old_zh, new_zh, "README.zh-CN"),
    encoding="utf-8",
    newline="\n",
)

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
anchor = "## Unreleased\n\n"
bullet = (
    "- Hardened GPU resource admission so non-empty CUDA/HIP/ROCR visibility cannot bypass "
    "an empty GPU claim, all present visibility aliases must agree, and malformed or duplicate "
    "device lists fail closed; added deterministic Schema-bound evidence and regression gates.\n"
)
if bullet in changelog:
    raise SystemExit("CHANGELOG entry already exists")
changelog_path.write_text(
    replace_once(changelog, anchor, anchor + bullet, "CHANGELOG"),
    encoding="utf-8",
    newline="\n",
)

shutil.rmtree(PAYLOAD)
WORKFLOW.unlink()
