<div align="center">

# TsaoSciComputation

**从电子尺度到流程尺度的证据约束型科学计算编排系统。**

[English](README.md) · [根 Skill](SKILL.md) · [能力索引](capability-index/README.md) · [覆盖矩阵](docs/coverage-matrix.md) · [架构](docs/architecture.md) · [安全](SECURITY.md)

</div>

## 用途

TsaoSciComputation 将科学问题转化为可追溯的计算程序：

```text
科学问题 → 严格计算合同 → 方法/尺度路由 → 环境前检
         → 有界执行 → 保守解析 → 数值/物理验证
         → 不确定度/适用域 → 证据验收 → 跨尺度交接
```

它负责组织和约束科学计算，不打包或冒充外部求解器、许可证、数据库、基组、赝势、私有数据或生产 HPC 环境。

## 已验证基线

| 项目 | 结果 |
|---|---:|
| 版本 | 3.0.0 |
| 能力 / 适配器 / 工作流 | 164 / 27 / 20 |
| 强制运行时第三方依赖 | 0 |
| 自动测试 | 514 通过，0 失败 |
| 语句 / 分支覆盖率 | 97.02% / 93.06% |
| 受控变异探针 | 64/64 被识别 |
| 仓库安全扫描 | 0 项发现 |
| 源码包 | ZIP 与 tar.gz 字节级可重复构建 |
| Wheel | 字节级可重复构建并通过隔离安装 |
| 远程分支 | 仅 `main` |

权威机器可读证据位于 `reports/FINAL_VERIFICATION.json`、`evidence/quality-baseline.json`、`reports/REMOTE_FINALIZATION.json` 和 `benchmarks/latest.json`。

## 开始使用

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

严格计算合同是总控制点：字段格式错误、前检信息缺失、可执行程序或 Python 模块不可用、路径越界、状态跳级以及验收证据不完整，均按 fail-closed 拒绝继续。

## 覆盖范围

仓库包含 164 项差异化能力、20 条带验证门的工作流和 27 个核心适配器。源清单列出的 32 个引擎中，21 个由独立或组合适配器表示，11 个明确保留为非独立适配边界。详见 [`docs/coverage-matrix.md`](docs/coverage-matrix.md)。

## 统一验证

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark
```

`all` 是确定性的发布硬门禁，覆盖代码质量、测试与覆盖率、仓库/Schema/资源/Manifest 校验、安全扫描、受控变异探针、源码包与 Wheel 可重复构建以及 Wheel 隔离安装。`benchmark` 受运行环境影响，只作为独立性能观测，不参与发布验收。CI 在 Ubuntu、Windows、macOS 上验证 Python 3.10 与 3.13，所有 GitHub Actions 均固定到不可变提交。

## 安装为 Agent Skill

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent codex --scope user --validate
```

只有经过明确审核的替换或卸载覆盖才使用 `--force`。

## 科学可信边界

适配器只有在全部声明的可执行程序和 Python 模块均通过探测后才可标记为可用；正常退出不等于数值收敛。安装副本按完整 SHA-256 Manifest 校验，12 类场景合同均通过严格前检。

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

最终验收始终采用 fail-closed：缺少收敛、物理检查、不确定度、适用域、溯源、证据或必要人工审批中的任一项，均不得进入科学接受状态。反应器、控制、数字孪生、安全、失控反应和商业交接等高风险结论必须由领域专家审核。

## 仓库策略

远程仓库只保留 `main`，并以其作为唯一权威开发线。历史分支头应保存为不可变归档标签，而不是额外 branch。生成环境和缓存统一排除，真实源码、配置、测试、证据与发布元数据保持可审计。
