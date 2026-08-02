<div align="center">

<img src="assets/visuals/hero-multiscale.svg" alt="TsaoSciComputation 从电子到流程的多尺度架构" width="100%">

# TsaoSciComputation

**从电子尺度到工业流程尺度的证据约束型科学计算编排系统。**

![version](https://img.shields.io/badge/version-3.0.2-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[English](README.md) · [根技能](SKILL.md) · [能力索引](capability-index/README.md) · [覆盖矩阵](docs/coverage-matrix.md) · [科学验证](docs/scientific-validation.md) · [可信等级](docs/scientific-confidence.md) · [架构](docs/architecture.md) · [发布治理](docs/release.md) · [安全](SECURITY.md)

</div>

<!-- V13_VISUAL_SYSTEM:START -->
## 配图设计系统

仓库内 42 幅 SVG 已升级为 **Scientific Research Console V13**，设计依据同时来自
UI/UX Pro Max 上游优先级模型及其中文教程适配。

- 无障碍与 GitHub 缩放后的可读性优先于装饰效果；
- 全部图采用统一、克制的技术编辑色板和线性图标语法；
- 信息同时通过文字、形状和位置表达，不依赖颜色单独传意；
- 详细工作流继续在语义化 `<details>` 分组中全宽展示；
- 图内文字不低于 16 px，且不使用外部字体、脚本、位图、渐变或滤镜。

详见 [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md)。
<!-- V13_VISUAL_SYSTEM:END -->

## 项目是什么

TsaoSciComputation 将科学问题转化为可追溯的计算程序：显式定义计算合同，完成方法与尺度路由、环境前检、有界执行、保守解析、数值与物理验证、不确定度和适用域分析、溯源记录以及证据验收。

```text
科学问题 → 计算合同 → 方法路由 → 环境前检 → 有界执行 → 保守解析
         → 收敛判断 → 物理验证 → 不确定度/适用域 → 接受或拒绝
```

它是**科学计算编排与治理层**，不打包、再分发、解锁或冒充外部求解器、许可证、数据库、基组、赝势、私有数据及生产级 HPC 基础设施。

## 科研能力图谱

首屏只展示两幅紧凑架构总览图；详细工作流、闭环和风险图采用全宽显示，并按领域折叠，减少滚动负担，同时保留全部 42 幅图的可发现性。

<table>
<tr>
<td width="50%"><img src="assets/visuals/agent-orchestration.svg" alt="Governed scientific agent orchestration" width="100%"></td>
<td width="50%"><img src="assets/visuals/capability-landscape.svg" alt="Scientific capability landscape" width="100%"></td>
</tr>
<tr>
<td align="center"><strong>受治理科研智能体</strong></td>
<td align="center"><strong>合同化能力体系</strong></td>
</tr>
</table>

核心设计采用缺项拒绝推进：声明能力不等于环境可用，进程完成不等于收敛，数值收敛不等于物理有效，验证通过也不等于获得高风险工程授权。


<details open>
<summary><strong>电子结构、分子模拟与反应</strong> — 量子、采样、动力学、光谱及跨尺度参数化</summary>

<img src="assets/visuals/quantum-to-md.svg" alt="Electronic structure to molecular dynamics handoff" width="100%">

<img src="assets/visuals/electronic-structure-landscape.svg" alt="Electronic structure evidence landscape" width="100%">

<img src="assets/visuals/free-energy-sampling.svg" alt="Enhanced sampling and free energy workflow" width="100%">

<img src="assets/visuals/reaction-kinetics-network.svg" alt="Reaction pathway and kinetic network" width="100%">

<img src="assets/visuals/ml-potential-active-learning.svg" alt="Machine learned potential active learning" width="100%">

<img src="assets/visuals/periodic-materials-stability.svg" alt="Periodic materials stability workflow" width="100%">

<img src="assets/visuals/catalysis-microkinetics.svg" alt="Catalysis microkinetic evidence workflow" width="100%">

<img src="assets/visuals/quantum-chemistry-thermochemistry.svg" alt="Quantum chemistry thermochemistry workflow" width="100%">

<img src="assets/visuals/molecular-dynamics-transport.svg" alt="Molecular dynamics transport workflow" width="100%">

<img src="assets/visuals/conformer-solvation-excited-state.svg" alt="Conformer solvation and excited state workflow" width="100%">

<img src="assets/visuals/surface-adsorption-migration.svg" alt="Surface adsorption defect and migration workflow" width="100%">

<img src="assets/visuals/spectroscopy-observables.svg" alt="Spectroscopy observable assignment workflow" width="100%">

</details>

<details>
<summary><strong>材料、界面与制造</strong> — 形貌、输运、聚合、复合材料及加工窗口</summary>

<img src="assets/visuals/polymer-process.svg" alt="Polymer structure to process workflow" width="100%">

<img src="assets/visuals/mesoscale-phase-field.svg" alt="Mesoscale phase field evidence workflow" width="100%">

<img src="assets/visuals/electrochemical-interface.svg" alt="Electrochemical interface evidence workflow" width="100%">

<img src="assets/visuals/transport-degradation.svg" alt="Coupled transport and degradation workflow" width="100%">

<img src="assets/visuals/polymerization-population-balance.svg" alt="Polymerization population balance workflow" width="100%">

<img src="assets/visuals/extrusion-rheology-window.svg" alt="Extrusion rheology processing window" width="100%">

<img src="assets/visuals/polymer-composite-topology.svg" alt="Polymer composite topology workflow" width="100%">

<img src="assets/visuals/multiscale-handoff-uncertainty.svg" alt="Multiscale handoff and uncertainty workflow" width="100%">

</details>

<details>
<summary><strong>连续介质、流程与运行</strong> — CFD、FEM、流程、反应器、控制与数字孪生</summary>

<img src="assets/visuals/continuum-multiphysics.svg" alt="Continuum multiphysics verification" width="100%">

<img src="assets/visuals/process-optimization-uq.svg" alt="Process optimization and uncertainty workflow" width="100%">

<img src="assets/visuals/reactor-safety-control.svg" alt="Reactor safety control workflow" width="100%">

<img src="assets/visuals/fem-verification-convergence.svg" alt="Finite element verification and convergence" width="100%">

<img src="assets/visuals/flowsheet-convergence-balances.svg" alt="Flowsheet convergence and balance workflow" width="100%">

<img src="assets/visuals/cfd-turbulence-multiphase.svg" alt="CFD turbulence multiphase transport workflow" width="100%">

<img src="assets/visuals/reactor-scaleup-thermal-risk.svg" alt="Reactor scale up and thermal risk workflow" width="100%">

<img src="assets/visuals/dynamic-control-estimation.svg" alt="Dynamic control and state estimation workflow" width="100%">

<img src="assets/visuals/digital-twin-drift.svg" alt="Digital twin drift aware lifecycle" width="100%">

</details>

<details>
<summary><strong>证据、治理与计算基础设施</strong> — 不确定度、适配器、HPC、可信等级与可重复性</summary>

<img src="assets/visuals/uncertainty-sensitivity.svg" alt="Uncertainty and sensitivity decision workflow" width="100%">

<img src="assets/visuals/inverse-design-loop.svg" alt="Inverse design evidence loop" width="100%">

<img src="assets/visuals/data-model-governance.svg" alt="Scientific data and model governance" width="100%">

<img src="assets/visuals/hpc-execution-provenance.svg" alt="Bounded HPC execution provenance" width="100%">

<img src="assets/visuals/engine-ecosystem.svg" alt="Scientific solver adapter ecosystem" width="100%">

<img src="assets/visuals/evidence-loop.svg" alt="Fail-closed scientific evidence loop" width="100%">

<img src="assets/visuals/confidence-ladder.svg" alt="Scientific confidence ladder C0 to C5" width="100%">

<img src="assets/visuals/digital-thread.svg" alt="Reproducible scientific digital thread" width="100%">

<img src="assets/visuals/scale-multifidelity-plan.svg" alt="Scientific scale and multi fidelity plan" width="100%">

<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC failure classification and recovery workflow" width="100%">

</details>

仓库包含 27 个保守适配器定义；外部求解器仍须独立安装、授权和验证。每次受治理交接均可保留单位、版本、种子、容差、原始产物、解析结果、哈希和发布证据。
## 快速开始

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e .

python -m tsao_computation route "使用 DFT 和 MD 研究聚合物界面"
python scripts/init_project.py --root demo --name demo \
  --question "形貌如何影响导电性能？"
python -m tsao_computation validate-contract \
  templates/calculation-contract.json --strict
python -m tsao_computation probe
```

外部求解器均为可选能力，必须另行合法安装、授权并验证。缺少可执行程序、计算合同格式错误、路径越界、状态跳级或证据不完整时，系统会拒绝继续，而不是静默放行。

<!-- PERFORMANCE_V9:START -->
## 性能工程

V9 只有在同一 Runner 上对已验收的 V8 基线与候选版本完成对照后，才接受效率提升结论。确定性审计运行 `30235135456` 记录：

| 测量路径 | V8 基线 | V9 候选 | 结果 |
|---|---:|---:|---:|
| `verify_all --profile all` 中位墙钟时间 | 12.270 s | 8.129 s | 1.51 倍 |
| `verify_all` 墙钟时间 p90 | 12.286 s | 8.135 s | 遥测 |
| 工作流路由 | 基线 | 候选 | 260.23 倍 |
| 5 MiB 求解器输出解析 | 基线 | 候选 | 0.98 倍 |
| 峰值 RSS 比值 | 1.00 倍 | 0.77 倍 | 上限 1.10 倍 |

优化后的验证器只并发执行相互独立的子进程门禁，各任务输出分别捕获，并继续按原声明顺序输出日志。源码可重复构建仅因输出目录彼此隔离而并行。零强制运行时依赖、失败关闭式解析、缓存失效、确定性 Manifest 和科学验收边界均保持不变。证据：[`reports/PERFORMANCE_COMPARISON_V9.json`](reports/PERFORMANCE_COMPARISON_V9.json)、[`reports/PERFORMANCE_PROFILE_V9.json`](reports/PERFORMANCE_PROFILE_V9.json) 与 [Issue #29](../../issues/29)。
<!-- PERFORMANCE_V9:END -->

## 统一验证

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` 运行确定性的发布硬门禁，包括代码质量与安全检查、测试和分支覆盖率、科学参考基准、关键覆盖率策略、版本与注册表同步、仓库及 Schema 校验、适配器与文档校验、受控变异探针、源码包与 Wheel 可重复构建、隔离安装、SPDX/CycloneDX SBOM、校验和以及发布 Manifest。`benchmark` 受运行环境影响，仅作为独立性能观测，不参与发布验收。

### 当前 `main` 验证状态

<!-- CURRENT_MAIN_VERIFICATION:START -->
已于 `2026-08-02T06:16:01.127780+00:00` 由确定性终验运行 `30735557078` 完成验证。

| 当前主线项目 | 结果 |
|---|---:|
| 版本 | 3.0.2 |
| 能力 / 适配器 / 工作流 | 164 / 27 / 20 |
| 自动测试 | 690 通过，0 失败 |
| 语句 / 分支覆盖率 | 97.61% / 93.80% |
| Windows core | Python 3.10 与 3.13；最终结果记录于 Issue #52 |
| 受控变异探针 | 64/64 被识别 |
| 科学参考基准 | 8/8 通过 |
| 仓库 / 依赖安全发现 | 0 / 0 |
| 源码包 / Wheel | 可重复 / 可重复并通过隔离安装 |
| 生成文本 / Manifest | 统一 LF / 跨平台稳定 |
| 科研视觉资产 | 42 幅自包含 SVG |
| 远程分支 | 仅 `main` |

V11-math-performance 最终提交只有在 [Issue #52](../../issues/52) 记录 Ubuntu/Windows/macOS × Python 3.10/3.13 正式 CI 成功后才被接受。机器可读证据：[`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json)。
<!-- CURRENT_MAIN_VERIFICATION:END -->

### v3.0.2 已验证发布基线

| 项目 | 机器记录结果 |
|---|---:|
| 版本 | 3.0.2 |
| 能力 / 适配器 / 工作流 | 164 / 27 / 20 |
| 强制运行时第三方依赖 | 0 |
| 自动测试 | 553 通过，0 失败 |
| 语句 / 分支覆盖率 | 97.27% / 93.48% |
| 受控变异探针 | 64/64 被识别 |
| 科学参考基准 | 8/8 通过 |
| 仓库 / 依赖安全发现 | 0 / 0 |
| 源码包 | ZIP 与 tar.gz 字节级可重复构建 |
| Wheel | 字节级可重复构建并通过隔离安装 |
| 供应链证据 | SPDX + CycloneDX SBOM、SHA-256 Manifest、Sigstore 证明 |
| 远程分支 | 仅 `main` |

本表对应 2026-07-24 形成的不可变 v3.0.2 验证证据。当前主线证据单独记录，避免后续文档和测试变更反向改写历史发布记录。权威发布记录位于 `reports/FINAL_VERIFICATION.json`、`evidence/quality-baseline.json`、`reports/REMOTE_FINALIZATION.json` 和 `benchmarks/latest.json`。

## CI、发布与 Skill 安装

CI 在 Ubuntu、Windows、macOS 上验证 Python 3.10 与 3.13。只读的周度依赖审计记录漏洞证据，不会在上游创建分支；第三方 GitHub Actions 均固定到不可变提交。

正式版本只能由受控 Release 工作流在全部确定性门禁通过后创建。每个不可变 `vX.Y.Z` Release 均包含可重复构建的源码包和 Wheel、SPDX/CycloneDX SBOM、`SHA256SUMS`、发布 Manifest、最终验证证据以及 GitHub/Sigstore 溯源证明。

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent codex --scope user --validate
```

只有经过明确审核的替换或卸载覆盖才使用 `--force`。

## 科学边界

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

内部基准通过不代表第三方求解器已经真实运行。缺少收敛、物理检查、不确定度、适用域、溯源、证据或必要人工审批中的任一项，均不得进入科学接受状态。反应器、控制、数字孪生、安全、失控反应和商业决策等高风险结论必须由合格的领域专家审核。

`assets/visuals/` 中的 42 幅图片是为本仓库生成的原创解释性矢量图，不是求解器截图、性能曲线或真实外部引擎运行证据。图片完整性、可访问性、源码分发收录以及中英文 README 引用均由自动测试检查。

## 仓库策略

`main` 是上游唯一权威分支。外部贡献使用 fork 内分支，上游仓库不保留功能分支。历史版本使用不可变标签保存。生成环境和缓存统一排除，源码、配置、测试、证据与发布元数据保持可审计。

<!-- MATH_PERFORMANCE_V10:START -->
### 数理正确性与性能 V10

当前主线采用稳定不确定度合成、O(1) 内存收敛判定、补偿式守恒残差、有限数基准误差计算和加速库推荐缓存。候选“编译正则解析预筛选”实测解析比值仅为 `0.30×`，因此已拒绝并回退。

相对于此前已认证主线的隔离同机结果：重复加速规划 **1.06×**、收敛判定 **1.24×**、不确定度合成 **1.57×**，收敛判定峰值跟踪内存为基线的 **0.006%**。8 项科学参考基准和完整确定性门禁全部通过。上述数据仅针对仓库内 Python 数理内核与编排逻辑，不代表外部求解器、GPU 内核或生产 HPC 加速。

机器证据：[`reports/MATH_PERFORMANCE_AUDIT_V10.json`](reports/MATH_PERFORMANCE_AUDIT_V10.json)。
<!-- MATH_PERFORMANCE_V10:END -->

<!-- MATH_PERFORMANCE_V11:START -->
### 数理正确性与性能 V11

第二轮审计缓存了静态加速配置解析，统一了语义等价问题的路由缓存键，并将 Poiseuille、RK4 与 velocity-Verlet 确定性基准循环中的不变量移出热点循环。数值方法、容差和科学验收标准均未改变。

相对于 V10 的隔离同机结果：预解析请求的加速规划 **1.09×**、语义等价路由输入 **184.03×**、8 项科学基准套件 **1.37×**。等价路由输入由 **256** 个缓存条目收敛为 **1** 个。映射式规划、解析器、收敛判定与不确定度内核均满足无实质回退门槛。上述结果仅针对仓库内 Python 内核。

机器证据：[`reports/MATH_PERFORMANCE_AUDIT_V11.json`](reports/MATH_PERFORMANCE_AUDIT_V11.json)。
<!-- MATH_PERFORMANCE_V11:END -->
