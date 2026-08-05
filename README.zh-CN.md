<div align="center">

<img src="assets/visuals/hero-multiscale.svg" alt="TsaoSciComputation 从电子到流程的多尺度架构" width="100%">

# TsaoSciComputation

**从电子尺度到工业流程尺度的证据约束型科学计算编排系统。**

![version](https://img.shields.io/badge/version-3.0.4-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[English](README.md) · [根 Skill](SKILL.md) · [能力索引](capability-index/README.md) · [视觉图谱](assets/visuals/README.md) · [科学验证](docs/scientific-validation.md) · [系统架构](docs/architecture.md) · [安全说明](SECURITY.md)

</div>

## 它做什么

TsaoSciComputation 将科学问题转化为可追溯的计算程序：

```text
问题 → 合同 → 路由 → 环境预检 → 执行 → 解析
     → 收敛 → 验证 → 不确定度 → 接受或拒绝
```

它提供合同、方法与尺度路由、环境检查、有边界执行、保守解析、验证、不确定度、溯源和验收门禁。它是编排与治理层，不打包外部求解器、许可证、数据库、私有数据或生产 HPC 环境。

## 快速开始

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e .

python -m tsao_computation route "使用 DFT 和 MD 研究聚合物界面"
python -m tsao_computation validate-contract templates/calculation-contract.json --strict
python -m tsao_computation probe
```

外部工具均为可选项，必须独立安装、授权、许可和验证。

<!-- SUPER_SKILL_ORCHESTRATION:START -->
## 能力与执行模型

仓库提供 **164 项能力**、**23 类计算方法**、**9 类调用方式**、**7 个可信本地函数**、**27 个外部适配器**、**20 套工作流**、**13 类加速策略**和**9 阶段编排计划**。

| 调用方式 | 默认行为 |
|---|---|
| 已注册可信本地函数 | 通过载荷校验和请求/结果哈希后可本地执行 |
| 外部求解器或适配器 | 默认仅探测并生成命令计划，执行需另行授权 |
| Python 模块、CLI、API、容器、调度器或其他 Skill | 在运行时、身份、授权和证据条件满足前仅生成声明式交接 |

执行策略为 fail-closed：旧低层进程接口不能直接执行；硬件探测仅允许固定只读命令；外部执行在启动前重新绑定可执行文件、声明输入和规范化环境。
<!-- SUPER_SKILL_ORCHESTRATION:END -->

## 架构概览

<table>
<tr>
<td width="50%"><img src="assets/visuals/agent-orchestration.svg" alt="受治理的科学智能体编排" width="100%"></td>
<td width="50%"><img src="assets/visuals/capability-landscape.svg" alt="科学计算能力全景" width="100%"></td>
</tr>
<tr>
<td align="center"><strong>受治理的科学智能体</strong></td>
<td align="center"><strong>基于合同的能力系统</strong></td>
</tr>
</table>

<!-- V13_VISUAL_SYSTEM:START -->
仓库内 42 幅自包含 SVG 使用 **Scientific Research Console V13**。根 README 展示 11 幅代表性示意图；完整可检索图谱见 [`assets/visuals/README.md`](assets/visuals/README.md)，设计规范见 [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md)。
<!-- V13_VISUAL_SYSTEM:END -->

## 多尺度科学计算视觉图谱

这些配图采用 AI 辅助信息设计，并以确定性、仓库自持的 SVG 源码交付，不包含外部脚本、字体、位图或伪造的求解器输出。

<img src="assets/visuals/quantum-to-md.svg" alt="从电子结构计算到分子动力学的尺度交接" width="100%">
<img src="assets/visuals/reaction-kinetics-network.svg" alt="反应路径、动力学证据与反应器交接" width="100%">
<img src="assets/visuals/polymer-process.svg" alt="从分子结构到加工过程的多尺度传递" width="100%">
<img src="assets/visuals/continuum-multiphysics.svg" alt="连续介质多物理场耦合" width="100%">
<img src="assets/visuals/process-optimization-uq.svg" alt="流程优化与不确定度量化" width="100%">
<img src="assets/visuals/uncertainty-sensitivity.svg" alt="不确定度传播与敏感性排序" width="100%">

## 加速计算与原生互操作

Python 保留为合同、路由、溯源和验收控制平面。经剖析确认的热点可通过版本化 C ABI 迁移到 C++20/OpenMP 或可选 CUDA 后端，同时保留纯 CPU 构建。只有在性能剖析和数值等价门禁通过后，才采用求解器原生 GPU 路径或 CUDA-X Libraries。

<img src="assets/visuals/hpc-execution-provenance.svg" alt="有边界的 HPC 执行与溯源" width="100%">
<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC 检查点与有边界恢复" width="100%">

架构、CUDA-X 选型和 C++ 迁移门禁见 [`docs/accelerated-native-backend.md`](docs/accelerated-native-backend.md)。原生验证命令：`python scripts/verify_native_core.py`。

## 验证

```bash
python -m pip install -e '.[validation,quality,security]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` 覆盖质量、安全、测试、覆盖率、科学基准、Schema 与注册表校验、受控变异测试、可重复源码/Wheel 构建、隔离安装、SBOM、校验和与发布清单。`benchmark` 属于环境相关遥测，不作为发布门禁。

### 当前 `main` 验证状态

<!-- CURRENT_MAIN_VERIFICATION:START -->
已于 `2026-08-02T19:04:13.872746+00:00` 由确定性终验运行 `30762511647` 完成验证。

| 当前主线项目 | 结果 |
|---|---:|
| 版本 | 3.0.4 |
| 能力 / 适配器 / 工作流 | 164 / 27 / 20 |
| 自动测试 | 774 通过，0 失败 |
| 语句 / 分支覆盖率 | 96.63% / 90.99% |
| Windows 核心支持 | Python 3.10 与 3.13；最终结果记录于 Issue #49 |
| Linux 兼容支持 | Ubuntu 验证；最终结果记录于 Issue #49 |
| 受控变异探针 | 64/64 被识别 |
| 科学参考基准 | 8/8 通过 |
| 仓库 / 依赖安全发现 | 0 / 0 |
| 源码包 / Wheel | 可重复 / 可重复并通过隔离安装 |
| 生成文本 / Manifest | 统一 LF / 跨平台稳定 |
| 科研视觉资产 | 42 幅自包含 SVG |
| 远程分支 | 仅 `main` |

final-exact-tree-v3 最终提交只有在 [Issue #49](../../issues/49) 记录 Ubuntu/Windows × Python 3.10/3.13 正式 CI 成功后才被接受。机器可读证据：[`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json)。
<!-- CURRENT_MAIN_VERIFICATION:END -->

## 性能证据

<!-- PERFORMANCE_V9:START -->
**V9：** 同机验收将 `verify_all --profile all` 从 12.270 s 降至 8.129 s（1.51×），并保持确定性并行验证与更低峰值内存。证据：[`reports/PERFORMANCE_COMPARISON_V9.json`](reports/PERFORMANCE_COMPARISON_V9.json)。
<!-- PERFORMANCE_V9:END -->

<!-- MATH_PERFORMANCE_V10:START -->
**V10：** 优化仓库内不确定度、收敛与加速规划内核；实测变慢的解析器候选被拒绝。证据：[`reports/MATH_PERFORMANCE_AUDIT_V10.json`](reports/MATH_PERFORMANCE_AUDIT_V10.json)。
<!-- MATH_PERFORMANCE_V10:END -->

<!-- MATH_PERFORMANCE_V11:START -->
**V11：** 缓存静态加速配置、规范化语义等价的路由缓存键，并将科学基准中的不变量移出循环；方程与容差不变。证据：[`reports/MATH_PERFORMANCE_AUDIT_V11.json`](reports/MATH_PERFORMANCE_AUDIT_V11.json)。
<!-- MATH_PERFORMANCE_V11:END -->

所有性能结论仅覆盖仓库内编排或确定性内核，不代表外部求解器、GPU 内核或生产 HPC 加速。

## 可信边界

```text
完成 ≠ 已解析 ≠ 已收敛 ≠ 已验证 ≠ 已接受
```

命令或基准成功不等于第三方求解器结果有效。缺少收敛性、物理校验、不确定度、适用域、溯源、证据或必要专家审批时，科学结论不得通过验收。

## 平台、发布与仓库策略

- **Windows：** 核心支持工作流。
- **Linux：** 兼容并通过 CI 验证。
- **仓库：** `main` 是唯一权威上游分支，不保留功能分支。
- **发布：** 受治理标签包含可重复构建、SPDX/CycloneDX SBOM、SHA-256 校验和与溯源证据。

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent codex --scope user --validate
```

仅在明确评审并准备替换时使用 `--force`。

## 许可证与引用

采用 MIT 许可证。引用信息见 [`CITATION.cff`](CITATION.cff)，第三方边界见 [`THIRD_PARTY.md`](THIRD_PARTY.md)。
