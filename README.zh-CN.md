# TsaoSciComputation

**科学计算控制面：把问题整理成明确的计算合同、经授权的执行与可审阅的证据。**

[English](README.md) · [根 Skill](SKILL.md) · [实现指南](docs/scientific-contracts.zh-CN.md) · [能力索引](capability-index/README.md) · [验收说明](README_ACCEPTANCE.md)

![version](https://img.shields.io/badge/version-3.0.4-2563eb)

![AI 生成架构图：问题、合同、有边界的执行与证据审阅](docs/assets/readme-vnext/hero.zh-CN.svg)

*图 1：AI 生成的架构示意。SVG 仅为无障碍兼容外壳，内嵌一张完整且未经修改的生成 PNG，没有额外绘制标签或图形。软件负责准备与检查证据；外部引擎、许可证及科学审批分别提供。[图像原件、完整提示词与来源](docs/assets/ai-generated/README.md)。*

## 本仓库实际执行什么

本仓库实现 Python 合同、加权关键词路由、本地数值检查、适配器专属命令准备、受控子进程执行、输出解析与证据治理。路由到某个方法表示存在已登记的集成路径。进程完成、计算收敛与科学结论通过验收具有不同含义。

| 任务 | 已实现入口 | 产物与边界 |
|---|---|---|
| 从问题生成计划 | [路由器](tsao_computation/routing/router.py)、[计算合同](tsao_computation/contracts/calculation.py) | 关键词匹配排序与显式假设；路由分数不是概率 |
| 执行本地检查 | [允许列表中的调用](tsao_computation/orchestration/planner.py) | 守恒、收敛、不确定度、固定参考、单位或证据门禁结果 |
| 准备外部计算 | [适配器协议](tsao_computation/adapters/base.py) | GROMACS、Quantum ESPRESSO、ORCA 或声明的 Python 驱动参数；其他协议需另行实现 |
| 执行授权计划 | [执行器](tsao_computation/execution/runner.py)、[资源准入](tsao_computation/execution/resources.py) | 精确可执行文件/输入/环境身份、资源准入、超时约束与部分批次证据 |
| 跨尺度传递目标量 | [ScientificQuantity](tsao_computation/scientific_quantity.py)、[交接合同](tsao_computation/contracts/handoff.py) | 单位、条件、参考态、不确定度及不可变载荷身份 |
| 审阅结论 | [验收门禁](tsao_computation/validation/acceptance.py)、[置信分级](tsao_computation/validation/confidence.py) | 缺失证据与已验证审批检查；不自动进行科学认证 |

<!-- SUPER_SKILL_ORCHESTRATION:START -->
### 能力清单是路由合同

当前注册表包含 **164 项能力、27 个外部适配器和 20 套工作流**；编排层声明 **23 类方法、13 类加速策略和七个可信本地函数**。可以通过 `list capabilities`、`list adapters`、`list workflows`、`list methods` 和 `list invocations` 检查实际清单。

这些数量描述已登记的合同与集成路径，不表示仓库内置了 27 个数值引擎或 23 套数值算法。通用服务、容器、调度器和 Skill 目标在独立授权实现提供执行证据前仅用于规划。详见[编排文档](docs/orchestration.md)及其[机器可读审计](reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json)。
<!-- SUPER_SKILL_ORCHESTRATION:END -->

## 从本地结果开始

要求 Python **3.10+**。永久 CI 矩阵覆盖 **Windows 和 Linux**，使用 Python 3.10 与 3.13。运行时没有强制第三方依赖；验证和发布工具从带文件哈希的锁定依赖中独立安装。

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m venv .venv
```

Linux 使用 `source .venv/bin/activate`，Windows PowerShell 使用 `.venv\Scripts\Activate.ps1` 激活，然后执行：

```bash
python -m pip install --require-hashes --only-binary=:all: -r requirements-ci.txt
python -m pip install --no-index --no-deps --no-build-isolation -e '.[validation,quality,security]'
python -m tsao_computation --version
python -m tsao_computation route "DFT to MD to CFD with explicit uncertainty and handoff validation"
python -m tsao_computation validate-contract examples/dft-md-cfd/contract.json --strict
python -m tsao_computation plan examples/dft-md-cfd/contract.json --strict
python -m tsao_computation invoke scientific-benchmarks --execute
```

示例合同是**准备阶段模板**，其中的方法意图与占位内容需要替换为真实材料、几何、参数和参考数据。严格验证检查字段完整性与结构，并不证明输入内容真实。最后一条命令执行仓库本地的八项解析解/不变量检查，不运行第三方求解器。

下面的 Python 示例完全在本地执行：

```python
from decimal import Decimal

from tsao_computation import ScientificQuantity
from tsao_computation.uncertainty import combine_independent
from tsao_computation.validation import balance_check, convergence_check

pressure = ScientificQuantity(
    value=Decimal("1.25"),
    unit="MPa",
    dimension=(-1, 1, -2, 0, 0, 0, 0),
    source_id="synthetic-readme-example",
    basis="REFERENCE",
    uncertainty=Decimal("0.05"),
)
converted = pressure.convert(unit="Pa", dimension=pressure.dimension)
assert converted.value == Decimal("1250000")
assert converted.uncertainty == Decimal("50000")
assert converted.source_quantity_digest == pressure.digest
assert balance_check(10.0, 7.0, 3.0, tolerance=1e-12)["passed"]
assert convergence_check([1.0, 1.0000001], absolute_tolerance=1e-6)["passed"]
assert combine_independent(3.0, 4.0, 0.0) == 5.0
```

依赖锁和更新策略见 [CI_DEPENDENCY_POLICY.md](docs/CI_DEPENDENCY_POLICY.md)。依赖哈希证明文件身份，漏洞评估仍是独立的发布检查。

## 带有假设边界的物理参考

![AI 生成物理参考图：理想链、层流圆管、振子和独立不确定度](docs/assets/ai-generated/algorithm.png)

*图 2：AI 生成的已实现参考关系示意。链模型检查协方差恒等式，不进行随机采样；振子采用单位质量与刚度；不确定度合成要求分量非负、不相关且采用共同单位。图中没有实测曲线。*

[`scientific_benchmarks.py`](tsao_computation/validation/scientific_benchmarks.py) 的八项确定性算例检查固定解析极限与数值不变量：

| 参考算例 | 关系式 | 假设与实际检查 |
|---|---|---|
| 稳态导热 | $T(x)=T_L+(T_R-T_L)x/L$ | 常物性、无热源；有限差分线性剖面 |
| 泊肃叶流动 | $Q=\pi\Delta pR^4/(8\mu L)$ | 稳态、不可压缩、牛顿流体、充分发展无滑移圆管层流；径向积分 |
| 一级反应 CSTR | $C=C_{in}/(1+k\tau)$ | 理想稳态全混；反应衡算残差 |
| 一级反应 PFR | $C/C_0=e^{-k\tau}$ | 恒定一级反应速率；RK4 积分 |
| 简谐振子 | $H=(x^2+v^2)/2$ | 无量纲单位质量/刚度、单位初始振幅；速度 Verlet 能量漂移 |
| 理想各向同性链 | $\langle R^2\rangle=Nb^2$ | 独立链段；对角协方差的迹，不生成采样系综 |
| 平行板 | $\lvert\mathcal E\rvert=V/d$ | 无边缘效应的线性电势；中心差分 |
| 电热平衡 | $VI=I^2R=G\Delta T$ | 稳态集总散热与常系数 |

$N$ 是链段数，$b$ 是链段长度，$\mu$ 是黏度，$k$ 是速率常数，$\tau$ 是停留时间，$G$ 是热导；$R$ 按所在行分别表示管半径或电阻。输入需采用一致单位基准。每项夹具都有固定参数与容差，通过不代表任意材料、离散格式或外部求解器已获验证。[参数、容差与源码对应](docs/scientific-contracts.zh-CN.md#参考夹具)。

**统计力学用于解释科学合同，不用于宣称尚未实现的求解器。** 固定 $N,V,T>0$ 时，$Z=\sum_i e^{-\beta E_i}$、$p_i=e^{-\beta E_i}/Z$、$F=-k_BT\ln Z$，其中 $\beta=(k_BT)^{-1}$。系综、能量模型和目标量需要先写入科学合同。本地链模型只是闭式极限检查，不能据此声称实现了配分函数求解或证明采样充分。[理论与实现边界](docs/scientific-contracts.zh-CN.md#统计力学背景)，参考 [Tong 的统计物理讲义](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S1.html)。

## 简洁技术路线

![AI 生成简洁技术路线：收敛、守恒与证据身份公式](docs/assets/ai-generated/roadmap.png)

*图 3：AI 生成技术路线。声明单位与假设，准备严格计划，授权精确身份，保留输出，检查数值和物理条件，最后独立审阅。缺失执行或审批证据时保持待证。*

已实现的标量门禁很紧凑，但前提不可省略：

$$
\Delta=|x_n-x_{n-1}|,\quad
\tau=\max\!\left(a,r\max(|x_n|,|x_{n-1}|,1)\right),\quad
\Delta\le\tau,
$$

$$
e_b=\frac{|\operatorname{fsum}(I,-O,-A)|}{\max(|I|,|O|,|A|,1)}\le\varepsilon,
\qquad u_c=\operatorname{hypot}(u_1,\ldots,u_k).
$$

[`convergence_check`](tsao_computation/validation/numerical.py) 先检查有限输入，再比较**末两点**；不能证明全局收敛、网格无关或充分混合。阈值取 `max`，不是相加。[`balance_check`](tsao_computation/validation/physical.py) 在 $I-O-A$ 中使用**正积累** $A$，要求共同单位与时间基准；尺度下限 1 需要明确单位基准或先无量纲化。[`combine_independent`](tsao_computation/uncertainty/model.py) 不实现协方差传播。[实现指南](docs/scientific-contracts.zh-CN.md) 保留完整物理量、解析器、交接、资源、账本和审批合同。

## 选择执行路径

| 场景 | 下一步 | 所需证据 |
|---|---|---|
| 尚未安装求解器 | `route` → 严格合同 → `plan` | 目标量、单位、条件、假设、参数来源与验证计划 |
| 小规模本地计算 | 注册的 `invoke` 或 Python API | 已准入数值、容差解释与结果记录 |
| 已有 GROMACS / QE / ORCA | 探测 → 引擎输入 → 精确计划授权 → 执行 | 二进制、输入、环境身份和 CPU/GPU/许可证声明 |
| Python 模块适配器 | 选择所属解释器与声明的 `.py` 驱动 | 模块位置及解释器身份；环境不能互换 |
| 多尺度研究 | 上游资格 → 不可变交接 → 下游 | 每次传递的单位、参考态、不确定度与重叠适用域 |
| 原生或 GPU 加速候选 | 剖析 → 参考 → 等价 → 同工作负载计时 | 方法/构建/设备身份、数值容差与完整端到端成本 |

[`Adapter.build_command()`](tsao_computation/adapters/base.py) 对 GROMACS 构建 `mdrun -s system.tpr`，对 QE 构建 `-i scf.in`，对 ORCA 构建 `water.inp`，对声明的 Python 模块适配器构建 `driver.py`。GROMACS 预处理单独进行。其他注册条目没有通用可执行命令。新计划初始为 `execute_allowed=False`；本地 `invoke --execute` 始终限制在七个注册函数内。[完整执行与隔离发现合同](docs/scientific-contracts.zh-CN.md#执行协议)。

解析器观察输入文本：完成和收敛的正标记分开处理，负标记否决对应结论，前一次成功不能替代后一次截断运行的证据。保留原始输出字节、解析器身份与进程记录。解析器的 `validated` 始终为 false。[解析实现](tsao_computation/adapters/base.py)。

## 性能证据与原生边界

[剖析器](tsao_computation/performance/runner.py) 记录指定工作负载的墙钟/进程时间、Python 分配峰值、中位数、MAD、P95 和操作吞吐。静态计数准入在 setup/operation 前完成，包括先物化批次中的每个计数。计数必须是满足下限的真正整数；有效大整数原样保留，没有统一的 $2^{53}$ 截断。[样本准入](tsao_computation/performance/model.py) 拒绝布尔、非有限、溢出以及非零转零的时间输入，同时保留可表示的次正规数与带符号零。

**实际吞吐在执行后检查。** 有限操作数除以很短的实测时间仍可能溢出；结果会被拒绝，但已执行的操作不会回滚。测得零时长保留原有有限回退值，不代表无限速度。计数准入不预先验证任意迭代器副作用、可调用对象行为或全部元数据。默认七次重复、一次预热；合格对比仍需同输入、缓存策略、环境与数值等价证据。[详细性能合同](docs/scientific-contracts.zh-CN.md#性能准入)。

可选 [C++ 原生核心](native/README.md) 提供版本化 C ABI 与 Python `ctypes` 桥接，支持 CPU/OpenMP/可选 CUDA Runtime 发现。设备发现不是科学内核性能测试。纯 Python 包不依赖 CUDA。[CMake 命令与加速判断流程](docs/scientific-contracts.zh-CN.md#原生构建与资格验证)。

## 验证与交付证据

```bash
python scripts/verify_all.py --profile all
python scripts/verify_native_core.py
python scripts/verify_all.py --profile benchmark
python -m pytest -q tests/test_performance_v9.py tests/test_performance_optimizations.py
python scripts/run_large_parser_regression.py
python scripts/final_acceptance_preflight.py --json
```

`all` 执行原有 quality、core 和 package 配置，包含 Ruff、格式、Mypy、Bandit、仓库安全扫描、受控变异、完整 pytest、**95% 总覆盖率**、关键模块覆盖率、科学参考、Schema/注册表审计、派生文件一致性、可重复源码/wheel 构建、隔离安装、SBOM 和校验和。原生 C ABI、benchmark 和性能命令仍是额外门禁。大日志解析回归使用生成的本地文本，不是实测求解器输出。

<!-- CURRENT_MAIN_VERIFICATION:START -->
### 资格属于精确提交

| 元数据 | 内容 |
|---|---|
| 版本 | 3.0.4 |

请查阅待交付提交对应的永久 [CI 工作流](.github/workflows/ci.yml)和原始工件。`reports/` 中的历史文件是快照；此前的绿灯或局部测试不能验证新提交。六小时回归需要原始回执绑定精确源码 SHA、成功测试进程的累计耗时和全部失败证据，本 README 不预先宣称其完成。外部引擎在独立证据补齐前保持 **EXTERNAL_HOLD**。
<!-- CURRENT_MAIN_VERIFICATION:END -->

## 外部批准合同

[验收门禁](tsao_computation/validation/acceptance.py) 要求七个严格布尔证据条件：完成、解析、收敛、物理验证、不确定度量化、适用域确认、证据绑定；此外还要求有效工件 SHA-256 和经过验证、处于时间窗口内的独立审批。可信密钥由部署方提供，调用者自行填写批准标记不能替代它。交接的 `checked` 与 `validated` 也保持区分。[治理的精确边界](docs/scientific-contracts.zh-CN.md#48-验收是证据门禁)。

外部执行、方法专属验证或独立批准缺失时，使用 `EXTERNAL_HOLD`。[双语验收指南](README_ACCEPTANCE.md) 解释交付预检实际检查的内容。历史报告与绿灯不构成已变化源码的资格证据。

## 七仓库科研路线

![AI 生成七仓库科研总路线](docs/assets/ai-generated/seven-repo-roadmap.png)

*图 4：共享 AI 生成科研总路线。本仓库在整体研究路线中提供计算合同和证据控制。图示表达预期交接关系，不证明七个仓库已经连成并执行完整流水线。[原始生成记录](docs/assets/ai-generated/manifest.json)。*

## 维护与深入阅读

可继续阅读[双语实现指南](docs/scientific-contracts.zh-CN.md)、[架构](docs/architecture.md)、[科学验证](docs/scientific-validation.md)、[编排](docs/orchestration.md)、[场景示例](examples)、[发布策略](docs/release.md)和[第三方边界](THIRD_PARTY.md)。合同或数值输入被拒绝时，应修正来源记录并保留失败证据；可执行文件、输入、单位换算或模型变化时，重建受影响的计划与证据。不要把缺失观测填成零，也不要用验收标记替代审阅。

当前四张图均为完整 imagegen 输出，首图通过兼容外壳展示。**43 张历史 Scientific Research Console V13 SVG** 保留于[历史技术图谱](assets/visuals/README.md)，继续遵守原有[设计与安全约定](assets/visuals/DESIGN_SYSTEM.md)。历史图采用文本链接或明确归档，不冒充本轮 AI 生成图。下方维护中的源码索引本来就是纯文本索引。

`main` 是唯一权威长期分支。Windows 与 Linux 是支持的交付平台。不捆绑商业求解器、许可证或私有数据集。[MIT 许可](LICENSE) · [引用元数据](CITATION.cff)。

<!-- CURRENT_MAIN_ACCEPTANCE_V2:START -->
### 维护中的源码索引

[适配器与解析](tsao_computation/adapters/base.py) · [执行记录](tsao_computation/execution/runner.py) · [收敛](tsao_computation/validation/numerical.py) · [不确定度](tsao_computation/uncertainty/model.py) · [历史中文架构图](docs/current-main/tsao-scicomputation-current-main-zh.svg)

上文公式与策略描述当前实现。概念图和历史工件不是执行证明，源码变化后必须重新取得资格证据。
<!-- CURRENT_MAIN_ACCEPTANCE_V2:END -->
