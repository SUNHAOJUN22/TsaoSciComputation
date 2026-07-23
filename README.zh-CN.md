<div align="center">

# TsaoSciComputation

**从电子尺度到流程尺度的证据约束型科学计算编排系统。**

[English](README.md) · [根 Skill](SKILL.md) · [能力索引](capability-index/README.md) · [覆盖矩阵](docs/coverage-matrix.md) · [架构](docs/architecture.md) · [安全](SECURITY.md)

</div>

## 它是什么

```text
科学问题 → 严格计算合同 → 尺度/方法路由 → 环境前检
        → 有界执行 → 保守解析 → 数值/物理验证
        → 不确定度/适用域 → 证据约束验收 → 跨尺度交接
```

仓库不打包或冒充外部求解器、许可证、数据库、赝势、基组、私有数据或生产 HPC 环境。

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

机器可读证据位于 `evidence/quality-baseline.json`、`reports/REMOTE_FINALIZATION.json` 和 `benchmarks/latest.json`。

## 覆盖边界

上传目录共有 322 项 Skill，其中全尺度计算相关子集为 164 项，并列出 32 个科学计算引擎。仓库同样包含 164 项能力，但按 20 条带验证门的工作流重新组织，并非复制目录 slug。当前有 27 个核心适配器：32 个引擎条目中 21 个由独立或组合适配器覆盖，11 个仍明确列为非独立适配边界。详见 [`docs/coverage-matrix.md`](docs/coverage-matrix.md)。

## 快速开始

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e .

python -m tsao_computation --version
python -m tsao_computation route "使用 DFT、MD 和非牛顿 CFD 研究聚合物挤出"
python scripts/init_project.py --root demo --name demo \
  --question "形貌如何影响导电性能？"
```

从 `templates/calculation-contract.json` 建立合同，并在前检前执行严格验证：

```bash
python -m tsao_computation validate-contract contract.json --strict
python -m tsao_computation probe
```

## 安装为 Agent Skill

```bash
python scripts/install_skill.py --agent codex --scope user --dry-run
python scripts/install_skill.py --agent codex --scope user
python scripts/install_skill.py --agent claude --scope project
python scripts/install_skill.py --agent open-agent-skills --target /custom/skills
python scripts/install_skill.py --agent codex --scope user --validate
python scripts/install_skill.py --agent codex --scope user --uninstall
```

只有明确替换或经过核验的卸载才使用 `--force`。安装器支持 Windows、Linux、macOS、离线复制和自定义目标目录。

## 统一验证

最低支持 Python 3.10；发布门禁在 Python 3.10 与 3.13 上均完成验证。

```bash
python -m pip install -e '.[validation,quality]'
python scripts/verify_all.py --profile all
python scripts/verify_all.py --profile benchmark  # 环境相关，独立于发布硬门禁
```

`all` 会执行代码质量、测试与覆盖率、仓库/Schema/资源/Manifest 校验、安全与变异检查、源码包和 Wheel 可重复构建以及隔离安装。CI 还覆盖 Ubuntu、Windows、macOS 上的 Python 3.10 与 3.13，GitHub Actions 固定到不可变提交。

## 科学可信边界

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

最终验收采用 fail-closed：缺少收敛、物理检查、不确定度、适用域、证据链、溯源或必要人工审批中的任一项，均不得标记为 `scientifically-accepted`。反应器、控制、数字孪生、安全、失控反应和商业交接等高风险结论必须由领域专家审核。

## 仓库策略

远程仓库只保留 `main`，它也是唯一权威开发线。历史分支头通过不可变归档标签保存，不再保留额外 branch；生成环境和缓存统一排除，真实源码与配置仍处于检查范围内。
