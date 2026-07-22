# TsaoSciComputation 3.0.0

TsaoSciComputation 是一个覆盖电子、原子、介观、连续介质、反应器、流程与数字孪生尺度的科学计算编排系统。它不把软件命令堆在一起，也不把“程序正常退出”误写成“科学结论成立”，而是建立：

```text
科学问题 → 计算合同 → 尺度/方法路由 → 环境探测 → 输入预检
        → 受控执行 → 保守解析 → 数值收敛 → 物理验证
        → 不确定度/适用域 → 证据绑定 → 人工审批 → 科学验收
```

## 当前规模

- 164 项经过工作流差异化定义的能力；
- 27 个求解器/平台适配器；
- 20 条领域工作流；
- 运行时零强制第三方依赖；
- 431 项测试全部通过；
- 语句覆盖率 98.80%，分支覆盖率 96.81%；
- 64/64 受控非等价变异探针被识别；
- 仓库安全扫描 0 项发现；
- source ZIP、source tar.gz 与 wheel 均通过字节级可重复构建；
- wheel 已在脱离源码目录的隔离虚拟环境中安装验证。

## 科学可信边界

状态必须严格区分：

`completed ≠ parsed ≠ converged ≠ validated ≠ accepted`

最终验收采用 fail-closed。缺少收敛、守恒/量纲、UQ、适用域、证据或必要审批中的任一项，均不得标记为 accepted。仓库测试不声称 Gaussian、VASP、Aspen、GROMACS、OpenFOAM 等第三方软件已完成生产计算，也不声称商业许可证可用。

## 快速开始

```bash
python -m tsao_computation --version
python -m tsao_computation route "使用 DFT、MD 和非牛顿 CFD 研究聚合物挤出"
python -m tsao_computation probe
python scripts/init_project.py --name demo --question "形貌如何影响导电性能？"
```

## 完整验证

```bash
python -m pip install -e '.[validation]'
python scripts/run_tests.py --coverage
python scripts/quality_check.py
python scripts/validate_repository.py
python scripts/validate_schemas.py
python scripts/security_scan.py
python scripts/run_mutation_gate.py
python scripts/sync_package_assets.py --check
python scripts/build_capability_index.py --check
python scripts/build_manifest.py --check
python scripts/benchmark.py
python scripts/package_release.py
python scripts/verify_wheel.py
```

## 分支策略

`main` 是唯一长期权威分支。临时开发、审计和恢复分支只有在独有内容完成审计并整合或形成明确淘汰结论后才可删除；普通源码中禁止保留 Base64/Zstandard 传输分片。
