# TsaoSciComputation 3.0.0

TsaoSciComputation 是一个从电子尺度延伸到流程与数字孪生尺度的**证据约束型科学计算编排系统**。它负责组织计算，不冒充 Gaussian、VASP、GROMACS、OpenFOAM、Aspen 等外部求解器，也不声称商业许可证或生产 HPC 环境已经可用。

## 它做什么

```text
科学问题 → 计算合同 → 工作流路由 → 环境预检 → 受控执行
        → 保守解析 → 收敛/物理检查 → 不确定度/适用域
        → 证据绑定验收 → 报告与跨尺度交接
```

仓库提供合同、能力与适配器注册表、验证器、安全执行组件、保守解析器、示例、测试和可重复发布工具。

## 已验证基线

| 项目 | 结果 |
|---|---:|
| 版本 | 3.0.0 |
| 能力 / 适配器 / 工作流 | 164 / 27 / 20 |
| 强制运行时第三方依赖 | 0 |
| 自动测试 | 432 通过，0 失败 |
| 语句 / 分支覆盖率 | 98.80% / 96.81% |
| 受控变异探针 | 64/64 被识别 |
| 仓库安全扫描 | 0 项发现 |
| 源码包 | ZIP 与 tar.gz 字节级可重复构建 |
| Wheel | 字节级可重复构建并通过隔离安装 |
| 远程分支 | 仅 `main` |

机器可读证据位于 `evidence/quality-baseline.json`、`reports/REMOTE_FINALIZATION.json` 和 `benchmarks/latest.json`。这些结果验证的是编排仓库本身，不代表外部科学软件已经完成真实生产计算。

## 快速开始

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e .

python -m tsao_computation --version
python -m tsao_computation route "使用 DFT、MD 和非牛顿 CFD 研究聚合物挤出"
python -m tsao_computation probe
python scripts/init_project.py --root demo --name demo \
  --question "形貌如何影响导电性能？"
```

常用命令：

```bash
python -m tsao_computation list capabilities
python -m tsao_computation list adapters
python -m tsao_computation list workflows
python -m tsao_computation validate-contract examples/organic-dft/contract.json
python -m tsao_computation validate-repository --root .
```

## 完整验证

```bash
python -m pip install -e '.[validation,quality]'
python scripts/run_tests.py --coverage
python scripts/quality_check.py
python -m ruff check tsao_computation scripts tests
python -m ruff format --check tsao_computation scripts tests
python -m mypy --python-version 3.13 tsao_computation scripts
python -m bandit -q -r tsao_computation scripts
python scripts/validate_repository.py
python scripts/validate_schemas.py
python scripts/security_scan.py
python scripts/run_mutation_gate.py
python scripts/sync_package_assets.py --check
python scripts/build_capability_index.py --check
python scripts/build_manifest.py --check
SOURCE_DATE_EPOCH=1700000000 python scripts/package_release.py
python scripts/verify_wheel.py
```

CI 在 Ubuntu、Windows、macOS 上覆盖 Python 3.10 与 3.13，并执行质量、安全、可重复打包、隔离 Wheel 安装和 CodeQL 检查。

## 科学可信边界

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

最终验收采用 fail-closed：缺少收敛、物理检查、不确定度、适用域、证据链或必要人工审批中的任一项，均不得标记为 `accepted`。反应器、控制、数字孪生、安全、失控反应和商业交接等高风险结论必须由领域专家审核。

## 性能与分支策略

性能数据与测量边界以 `benchmarks/latest.json` 和 `docs/performance.md` 为准，避免在多处复制后产生过期数字。

远程仓库只保留 `main`。历史分支头通过不可变归档标签保存，不再保留额外 branch；普通源码树禁止出现编码传输分片、恢复控制器、临时触发文件和构建缓存。
