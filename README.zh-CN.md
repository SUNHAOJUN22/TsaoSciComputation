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
| 自动测试 | 443 通过，0 失败 |
| 语句 / 分支覆盖率 | 98.45% / 96.19% |
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

## 统一验证

最低支持 Python 3.10；发布门禁在 Python 3.10 与 3.13 上均完成验证。

README、CI 和 Release 共用一个跨平台入口：

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
```

`all` 只运行确定性的发布硬门禁：代码质量、自动测试与覆盖率、仓库/Schema/资源/manifest 校验、安全与变异检查、源码包可重复构建、Wheel 可重复构建和隔离安装。

仓库内的本地环境和生成缓存，包括 `.venv`、`.tox`、覆盖率产物及构建目录，会在仓库审计、安全扫描、Manifest 和源码打包中统一排除；真实源码与配置文件仍处于检查范围内。

性能基准受运行环境影响，因此单独执行：

```bash
python scripts/verify_all.py --profile benchmark
```

定位单项问题时，可使用 `core`、`quality` 或 `package`。CI 在 Ubuntu、Windows、macOS 上覆盖 Python 3.10 与 3.13，并单独执行质量、性能基准、打包和 CodeQL；Release 必须通过 `--profile all`。GitHub Actions 均固定到不可变提交。

## 科学可信边界

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

最终验收采用 fail-closed：缺少收敛、物理检查、不确定度、适用域、证据链或必要人工审批中的任一项，均不得标记为 `accepted`。反应器、控制、数字孪生、安全、失控反应和商业交接等高风险结论必须由领域专家审核。

性能数据以 `benchmarks/latest.json` 为事实源，测量边界见 `docs/performance.md`。

## 仓库策略

远程仓库只保留 `main`，它也是唯一权威开发线。历史分支头通过不可变归档标签保存，不再保留额外 branch；普通源码树禁止出现编码传输分片、恢复控制器、临时触发文件和构建缓存。
