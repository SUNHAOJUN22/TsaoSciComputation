<div align="center">

<img src="assets/visuals/hero-multiscale.svg" alt="TsaoSciComputation 从电子到流程的多尺度架构" width="100%">

# TsaoSciComputation

**从电子尺度到工业流程尺度的证据约束型科学计算编排系统。**

![version](https://img.shields.io/badge/version-3.0.2-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2)

[English](README.md) · [根技能](SKILL.md) · [能力索引](capability-index/README.md) · [覆盖矩阵](docs/coverage-matrix.md) · [科学验证](docs/scientific-validation.md) · [可信等级](docs/scientific-confidence.md) · [架构](docs/architecture.md) · [发布治理](docs/release.md) · [安全](SECURITY.md)

</div>

## 项目是什么

TsaoSciComputation 将科学问题转化为可追溯的计算程序：显式定义计算合同，完成方法与尺度路由、环境前检、有界执行、保守解析、数值与物理验证、不确定度和适用域分析、溯源记录以及证据验收。

```text
科学问题 → 计算合同 → 方法路由 → 环境前检 → 有界执行 → 保守解析
         → 收敛判断 → 物理验证 → 不确定度/适用域 → 接受或拒绝
```

它是**科学计算编排与治理层**，不打包、再分发、解锁或冒充外部求解器、许可证、数据库、基组、赝势、私有数据及生产级 HPC 基础设施。

## 架构总览

<table>
<tr>
<td width="50%"><img src="assets/visuals/agent-orchestration.svg" alt="受治理的 AI 科研智能体编排架构" width="100%"></td>
<td width="50%"><img src="assets/visuals/capability-landscape.svg" alt="科学计算能力与工作流全景" width="100%"></td>
</tr>
<tr>
<td align="center"><b>受治理的科研智能体</b><br>规划、路由、执行、证据与人工审核相互分离。</td>
<td align="center"><b>合同化能力体系</b><br>164 项差异化能力由 20 条工作流组织。</td>
</tr>
</table>

核心设计采用缺项拒绝推进原则：

- 声明了适配器，不等于环境中已经可用；
- 进程正常退出，不等于结果已经解析或收敛；
- 数值收敛，不等于满足物理规律；
- 通过验证，不等于可外推到适用域之外；
- 自动化分析完成，不等于获得高风险工程决策授权。

## 多尺度科学工作流

<table>
<tr>
<td width="50%"><img src="assets/visuals/quantum-to-md.svg" alt="从量子化学到分子动力学的工作流" width="100%"></td>
<td width="50%"><img src="assets/visuals/polymer-process.svg" alt="从聚合物结构到流程模拟的跨尺度工作流" width="100%"></td>
</tr>
<tr>
<td align="center"><b>量子 → 分子</b><br>电子结构、参数化、统计系综和可验证观测量。</td>
<td align="center"><b>聚合物 → 流程</b><br>序列、形貌、连续场与工艺系统之间的受控交接。</td>
</tr>
</table>

代表性范围包括电子结构、量子化学、原子级模拟、增强采样、机器学习势、介观与连续介质模型、反应工程、CFD、多物理场、流程模拟、优化、不确定度、可重复性以及跨尺度交接。

## 专业能力图谱

<table>
<tr>
<td width="50%"><img src="assets/visuals/electronic-structure-landscape.svg" alt="DFT 电子结构与能量地形" width="100%"></td>
<td width="50%"><img src="assets/visuals/continuum-multiphysics.svg" alt="CFD FEM 与连续介质多物理场工作流" width="100%"></td>
</tr>
<tr>
<td align="center"><b>电子结构与 DFT</b><br>几何、电子密度、自洽、能量、力与观测量级验收。</td>
<td align="center"><b>CFD、FEM 与多物理场</b><br>网格质量、守恒、场耦合、稳定性和离散误差证据。</td>
</tr>
</table>

<img src="assets/visuals/process-optimization-uq.svg" alt="流程优化 不确定度量化与受审核工程决策工作流" width="100%">

流程层将流程图构建、模型校准、不确定度传播、敏感性分析、约束搜索和人工授权明确分离。可行性、不确定度、安全性、适用域或审核证据不完整时，数值最优解不得进入工程接受状态。

## 求解器感知型生态

<img src="assets/visuals/engine-ecosystem.svg" alt="科学计算求解器与适配器生态" width="100%">

仓库包含 27 个保守适配器定义。源清单中的 32 个引擎有 21 个由独立或组合适配器表示，另有 11 个被明确保留为非独立适配边界。只有全部声明的可执行程序和 Python 模块通过探测后，适配器才可标记为可用；没有独立的真实求解器证据时，`live_execution_verified` 必须保持为 false。

精确边界见[覆盖矩阵](docs/coverage-matrix.md)、[适配器认证](docs/adapter-certification.md)和各 `adapters/*/ADAPTER.md` 文件。

## 证据、可信等级与可重复性

<table>
<tr>
<td width="50%"><img src="assets/visuals/evidence-loop.svg" alt="证据约束的科学验证闭环" width="100%"></td>
<td width="50%"><img src="assets/visuals/confidence-ladder.svg" alt="C0 到 C5 科学可信等级" width="100%"></td>
</tr>
<tr>
<td align="center"><b>科学验收闭环</b><br>合同、执行、收敛、物理、不确定度和适用域逐级检查。</td>
<td align="center"><b>C0–C5 可信等级</b><br>结论越强，所需证据越强；C5 只能显式授权。</td>
</tr>
</table>

<img src="assets/visuals/digital-thread.svg" alt="可重复科学计算数字线程" width="100%">

受治理的交接可保留输入、单位、方法、版本、路径、随机种子、容差、原始与解析产物、验证结果、哈希和发布证据。可重复性通过源码包和 Wheel 的独立重建进行检验，而不是从文档表述中推断。

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

## 统一验证

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` 运行确定性的发布硬门禁，包括代码质量与安全检查、测试和分支覆盖率、科学参考基准、关键覆盖率策略、版本与注册表同步、仓库及 Schema 校验、适配器与文档校验、受控变异探针、源码包与 Wheel 可重复构建、隔离安装、SPDX/CycloneDX SBOM、校验和以及发布 Manifest。`benchmark` 受运行环境影响，仅作为独立性能观测，不参与发布验收。

### 当前 `main` 验证状态

<!-- CURRENT_MAIN_VERIFICATION:START -->
已于 `2026-07-25T19:56:18.624713+00:00` 由确定性终验运行 `30172561968` 完成验证。

| 当前主线项目 | 结果 |
|---|---:|
| 版本 | 3.0.2 |
| 能力 / 适配器 / 工作流 | 164 / 27 / 20 |
| 自动测试 | 559 通过，0 失败 |
| 语句 / 分支覆盖率 | 97.32% / 93.67% |
| Windows core | Python 3.10 与 3.13 通过 |
| 受控变异探针 | 64/64 被识别 |
| 科学参考基准 | 8/8 通过 |
| 仓库 / 依赖安全发现 | 0 / 0 |
| 源码包 / Wheel | 可重复 / 可重复并通过隔离安装 |
| 生成文本 / Manifest | 统一 LF / 跨平台稳定 |
| 科研视觉资产 | 12 幅自包含 SVG |
| 远程分支 | 仅 `main` |

最终提交只有在 [Issue #22](../../issues/22) 记录 Ubuntu/Windows/macOS × Python 3.10/3.13 正式 CI 成功后才被接受。机器可读证据：[`reports/CURRENT_MAIN_VERIFICATION.json`](reports/CURRENT_MAIN_VERIFICATION.json)。
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

`assets/visuals/` 中的 12 幅图片是为本仓库生成的原创解释性矢量图，不是求解器截图、性能曲线或真实外部引擎运行证据。图片完整性、可访问性、源码分发收录以及中英文 README 引用均由自动测试检查。

## 仓库策略

`main` 是上游唯一权威分支。外部贡献使用 fork 内分支，上游仓库不保留功能分支。历史版本使用不可变标签保存。生成环境和缓存统一排除，源码、配置、测试、证据与发布元数据保持可审计。
