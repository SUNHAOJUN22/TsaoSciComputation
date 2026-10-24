# Architecture

TsaoSciComputation uses eight responsibility layers:

1. **Skill and CLI entry** — capture intent without eagerly loading the full knowledge base.
2. **Contracts and state** — machine-readable calculation, result, and handoff contracts with guarded transitions.
3. **Registries and routing** — 164 differentiated capabilities, 27 solver adapters, 20 workflows, and unit records.
4. **Scientific workflows** — method assumptions, required evidence, failure modes, and acceptance gates by domain.
5. **Adapter boundary** — executable discovery, argv-only command planning, and conservative output parsing.
6. **Execution and security** — path confinement, atomic writes, bounded subprocesses, timeouts, and immutable records.
7. **Validation and uncertainty** — numerical convergence, conservation, units, UQ, applicability, and human approval.
8. **Provenance and release** — event ledgers, manifests, reproducible archives, isolated wheel installation, and CI.

Runtime code has no mandatory third-party dependency. Solver executables, commercial licenses, pseudopotentials, basis databases, and proprietary manuals are never bundled.

## Local execution authorization

`authorize_plan` binds the normalized command, executable and declared input bytes,
environment, working directory, declaring identity and purpose. A private runtime
HMAC seals that complete authorization payload. `run_plan` verifies the seal before
resolving the current plan or starting a process; copying a grant cannot authorize
changed commands, identities or purposes. Unchanged grants remain reusable within
the issuing runtime, including unchanged object copies. A changed plan requires a
new explicit authorization.

This is a local API integrity boundary, not authentication of a human identity, a
cross-process credential, or a single-use/expiring capability. It does not sandbox
arbitrary Python code already running in the same trusted interpreter. External
identity, expiry and replay policy belong to the deploying authorization service;
scientific result acceptance remains a separate gate.

### 本地执行授权

`authorize_plan` 将命令、可执行文件与声明输入的字节、环境、工作目录、声明身份和用途绑定到同一授权载荷，并使用运行时私有密钥生成 HMAC。`run_plan` 在解析当前命令及启动进程前复核该载荷；复制授权对象不能改变获批命令、身份或用途。同一载荷的授权及其未修改副本仍可在当前运行时重复使用；修改计划必须重新显式授权。

该机制保护本地 API 的授权载荷完整性，不验证真人身份，不提供跨进程凭据、单次使用或到期语义，也不是同一可信 Python 解释器内任意代码的隔离沙箱。部署方负责外部身份、时效与重复使用策略；科学结果验收仍须单独执行。
