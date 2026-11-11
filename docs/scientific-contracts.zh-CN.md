# 科学合同与实现指南

[English](scientific-contracts.md) · [主 README](../README.zh-CN.md) · [验收说明](../README_ACCEPTANCE.md)

本指南是四张 AI 生成 README 图的详细配套文档。每项已实现数值结论均对应源码，完整保留执行与解析器合同，并区分本地软件参考与外部科学资格。

## 如何理解结果

分别记录科学问题、模型、数值实现和证据。先选择目标量与单位，声明边界条件与假设，再绑定精确输入和执行身份，最后检查数值、物理与审批条件。哈希绑定字节，不证明科学内容真实；命令成功只证明该命令的结果。

## 执行协议

### 策略与前提

| 你的场景 | 建议路径 | 继续前必须具备的证据 |
|---|---|---|
| 有科学问题，但没有安装求解器 | `route` → 严格合同 → `plan` | 目标量、单位、条件、假设、参数来源、收敛和验证计划 |
| 小规模本地数学检查 | `invoke` 七个注册函数之一，或调用其 Python API | 有限输入、明确容差/单位解释和完整结果记录 |
| 已有 GROMACS、QE 或 ORCA | 探测身份 → 准备输入协议 → 授权精确计划 → 执行 | 二进制/输入哈希、调用入口、环境、工作目录和资源声明 |
| Python 模块适配器 | 使用拥有依赖模块的解释器及声明的 `.py` 驱动 | 模块位置探测和解释器身份；不同虚拟环境不能混用 |
| 多尺度研究 | 上游计算 → 不可变交接 → 下游模型 | 单位、参考态、条件、不确定度、重叠适用域及每次转移的审阅 |
| GPU/MPI 或原生加速方案 | 剖析 → 可信 CPU 参考 → 等价性 → 同问题性能比较 | 求解器能力指纹、数值容差以及工作负载/环境身份 |

### 已实现的命令构建协议

[`Adapter.build_command()`](../tsao_computation/adapters/base.py) 支持以下具体输入协议：

| 适配器 | 已解析可执行文件之后的参数 | 输入要求 |
|---|---|---|
| GROMACS | `mdrun -s system.tpr` | 已预处理的 `.tpr`；预处理单独执行 |
| Quantum ESPRESSO | `-i scf.in` | PWscf 输入文件 |
| ORCA | `water.inp` | ORCA 输入文件 |
| 已声明的 Python 模块适配器 | `driver.py` | Python 驱动及同一解释器中的必要模块 |
| 其它适配器记录 | 没有通用可执行命令 | 先实现并验证对应引擎协议 |

构建的计划初始为 `execute_allowed=False`。执行层把授权绑定到具体计划，不把“已发现软件”当成执行许可。`invoke --execute` 仅适用于注册的仓库本地函数，不运行任意 shell，也不会让所有适配器自动变成可执行服务。

```bash
python -m tsao_computation probe --workers 4
python -m tsao_computation probe-solver gromacs --output .tsao-computation/gromacs-evidence.json
python -m tsao_computation plan-acceleration gromacs --solver-evidence .tsao-computation/gromacs-evidence.json --require-solver-evidence
```

这些命令检查可用性并进行有边界的版本探测。`version-probed-unqualified` 与 `evidence-bound-unqualified` 仍需要数值资格验证。缺失可执行文件、证据不完整或协议未实现时，系统保留明确的待证状态。

Python 模块发现使用隔离的 `-I -S` 子进程，不导入父包，不执行 `sitecustomize`，不处理 `.pth` 启动钩子。只有使用同一调用解释器的适配器才可以合并探测；不同虚拟环境入口分别检查，合并探测没有跨调用的可用性缓存。对应[模块隔离测试](../tests/test_module_probe_isolation.py)、[合并探测测试](../tests/test_grouped_adapter_probe.py)及[解释器执行测试](../tests/test_python_environment_execution.py)。

## 已实现数学合同

本节每个数值公式都链接到实现。方法选择记录与科学审批规则明确作为合同说明，不描述成拟合数值模型。

### 4.1 物理量、量纲与受控仿射换算

一个物理量记录数值 $x$、单位 $u$、七维量纲指数 $\mathbf d$、来源 $s$、数值依据 $b$ 及可选不确定度 $u_x$：

$$
Q=(x,u,\mathbf d,s,b,u_x),\qquad
\mathbf d=(d_L,d_M,d_T,d_\Theta,d_N,d_I,d_J).
$$

量纲顺序是长度、质量、时间、温度、物质的量、电流和发光强度。受控[单位注册表](../tsao_computation/quantity_units.py)给出比例 $a$、除数 $d$ 与缩放前偏移 $o$：

$$
x_{\mathrm{SI}}=(x_s+o_s)\frac{a_s}{d_s},\qquad
x_t=x_{\mathrm{SI}}\frac{d_t}{a_t}-o_t,
\qquad
u_t=u_s\left|\frac{a_s d_t}{d_s a_t}\right|.
$$

例如 `degC` 使用 $o_s=273.15$；`degF` 使用 $o_s=459.67$、$a_s=5$、$d_s=9$。温差使用 `delta_` 单位且偏移为零。绝对温度与温差不能互转；不确定度只缩放，不能加上绝对温度的偏移。

[`ScientificQuantity.convert`](../tsao_computation/scientific_quantity.py)采用完全指定的 **50 位有效十进制数字、ROUND_HALF_EVEN 舍入上下文**，不继承调用方的精度、舍入方式、指数限制或异常设置。绝对温度准入使用精确的零开尔文边界，要求 $T>0\,\mathrm K$。支持的非零十进制指数范围为 $[-308,308]$。换算仍可能在 50 位处舍入，结果越界或违反物理边界时仍会失败；它不是任意精度符号运算。

布尔值、未知单位、不相容量纲、负不确定度，以及与注册表矛盾的自定义换算因子都会被拒绝。换算结果记录 `basis="DERIVED"` 和原始物理量摘要。摘要识别规范化记录的具体表示，不保证所有不同格式或不同单位的等价物理量拥有同一摘要。回归测试：[Decimal 上下文隔离](../tests/test_decimal_context_isolation.py)。

### 4.2 有限标量准入与末两点收敛

[`convergence_check`](../tsao_computation/validation/numerical.py)先检查每个观测值，再比较末两个值：

$$
\Delta=|x_n-x_{n-1}|,\quad
s=\max(|x_n|,|x_{n-1}|,1),\quad
\tau=\max(a,r s),\quad
G_{\mathrm{conv}}=(\Delta\le\tau).
$$

$a\ge0$ 与观测值同单位，$r\ge0$ 无量纲。尺度下限 1 按输入的数值单位解释，因此应先规范单位或无量纲化，再选容差。实际阈值是**取最大值**，不是 $a+r s$。

布尔值、非有限值及转换为浮点数时变成零的非零输入都被拒绝。数字字符串、`Decimal`、`Fraction` 使用同一转换检查；真正的带符号零和可表示的次正规数仍有效。少于两个观测值或存在无效观测值都会失败。仅通过该检查不能证明整条轨迹收敛、采样充分、网格独立或达到全局最优。直接调用的失败诊断可能包含无穷哨兵；可信调用层在哈希前把这些诊断转成 JSON 安全的证据。参见[下溢回归](../tests/test_nonzero_underflow_contract.py)。

### 4.3 明确积累方向的守恒检查

[`balance_check`](../tsao_computation/validation/physical.py)计算已经统一单位与时间基准的输入：

$$
r_b=\operatorname{fsum}(I,-O,-A),\qquad
s_b=\max(|I|,|O|,|A|,1),\qquad
e_b=\frac{|r_b|}{s_b},\qquad G_b=(e_b\le\varepsilon).
$$

$I$ 是输入，$O$ 是输出，$A$ 是积累，控制体内物质或能量增加时取正。容差 $\varepsilon\ge0$ 无量纲。补偿求和保留可表示的抵消残差；溢出、非有限输入和归一化后被下溢抹成零的非零残差都属于错误。单位换算、组分化学计量和反应模型适用性必须在调用前建立，不能由小残差反推成立。

### 4.4 独立标准不确定度

[`combine_independent`](../tsao_computation/uncertainty/model.py)计算

$$
u_c=\operatorname{hypot}(u_1,\ldots,u_k)
=\sqrt{\sum_{i=1}^k u_i^2},\qquad u_i\ge0.
$$

`UncertaintyBudget` 分别命名统计、模型和数值分量。各分量必须同单位、具有兼容的标准不确定度解释；平方和假设分量不相关。`math.hypot` 避免可避免的中间平方溢出，最终非有限结果或被下溢抹零的非零输入仍被拒绝。空分量列表的数学结果是零，不能把它当成“所有不确定度来源都已评估”的证据。

存在相关性时，一阶传播需要

$$
u_y^2=\mathbf J\,\boldsymbol\Sigma\,\mathbf J^{\mathsf T},
$$

其中 $\mathbf J$ 是灵敏度行向量，$\boldsymbol\Sigma$ 是协方差矩阵。这个公式用于说明**边界**：`combine_independent` 没有实现协方差传播，存在相关性时必须另行提供经过验证的模型。参见[结果范围回归](../tests/test_uncertainty_result_range.py)。

### 4.5 模型交接保留科学含义

[`HandoffRecord`](../tsao_computation/contracts/handoff.py)绑定来源模型、接收模型、目标量、数值、单位、条件、参考态、统计/模型不确定度、适用域和变换过程。身份定义为

$$
H_H=\operatorname{SHA256}\!\left(\operatorname{CanonicalJSON}(P_H)\right),
$$

$P_H$ 严格对应 `canonical_payload()`。审阅决定和签名不进入该载荷，避免循环签名；审阅必须绑定其精确摘要，另一个数值或变换过程的审批不能复用。

数值允许有限标量或非空矩形数组，最多六层嵌套、100,000 个标量单元。不确定度非负，并与数组形状一致，或者显式提供一个标量上界。结构化不确定度必须带量纲兼容的单位；接口保留其原单位，组合前必须换算。嵌套数据会复制并冻结，调用者修改原列表不能改变已准入记录。`checked` 表示软件合同检查，`validated` 还需要绑定该载荷的外部已验证审批。

### 4.6 解析器观察输入文本

[`Adapter.parse`](../tsao_computation/adapters/base.py)保留文本摘要、解析器版本、检测到的引擎版本文本和当前运行起点。检测到新的运行开始后，前一次运行的成功标记不能替代后一次被截断运行的成功。正反观察概括为

$$
G_{\mathrm{complete}}=P_c\land\neg N_c,\qquad
G_{\mathrm{converged}}=G_{\mathrm{complete}}\land P_v\land\neg N_v.
$$

$P_c,P_v$ 分别是识别出的完成/收敛正标记，$N_c,N_v$ 是相应负标记。`not normal termination`、`SCF not yet converged` 和 `converged=false` 不会变成成功。这些是文本观察，不独立证明可执行文件身份或物理正确性；解析器的 `validated` 保持 false。应另外保留原始输出字节及执行记录，尤其在解码改变了文本时。参见[解析回归](../tests/test_performance_optimizations.py)。

### 4.7 资源准入与执行身份

本地[资源准入器](../tsao_computation/execution/resources.py)只在声明的可加容量内接纳并发任务集合 $\mathcal P$：

$$
\sum_{p\in\mathcal P}r_{p,j}\le c_j.
$$

$r_{p,j}$ 是任务 $p$ 的 CPU 或许可证资源需求，$c_j$ 是对应容量。GPU 还要求设备属于许可集合、独占使用且可见性设置一致。这是本地资源控制，不能替代外部集群调度器，也不能证明许可证服务器可用。

[执行器](../tsao_computation/execution/runner.py)把精确命令、可执行文件调用路径及解析后的目标、可执行文件/输入字节、工作目录和环境绑定到授权计划。文件身份为

$$
H_f=\operatorname{SHA256}(\mathrm{bytes}_f).
$$

超时清理覆盖进程树。批次失败保留已完成记录，并通过索引对应原始请求；缺失进程记录是失败，不会补造成功。资源释放不表示收敛或验收通过。参见[执行边界测试](../tests/test_execution_boundary_contract.py)及[超时测试](../tests/test_process_timeout_containment.py)。

### 4.8 验收是证据门禁

[`acceptance_gate`](../tsao_computation/validation/acceptance.py)要求七个严格布尔条件：

$$
G_S=C\land P\land V\land F\land U\land D\land E,
\qquad
G_A=G_S\land H\land A_{\mathrm{verified}}.
$$

$C$：已完成；$P$：已解析；$V$：已收敛；$F$：已做物理验证；$U$：已量化不确定度；$D$：已确认适用域；$E$：已绑定证据。$H$ 是有效的工件 SHA-256，$A_{\mathrm{verified}}$ 是至少一份有效且在时间窗口内、角色和用途符合要求的外部证明。这些标记是声明的证据输入，不是自动判断科学真假的算法。

内置门禁使用记录**外部**提供的可信密钥验证 HMAC-SHA256 证明，要求用途 `scientific-result-acceptance`、角色 `independent-domain-reviewer`，并要求申请人与审批人身份不同。C5 额外要求决策范围、安全审查和独立复现的签名证据；重复的合格 nonce 不能跨不同治理用途计数。实现不是持久化的跨请求重放数据库、机构身份服务或密钥撤销服务，需要这些能力的部署必须另行提供。独立的公开 `acceptance_is_verified` API 把签名验证交给调用方验证器，且只接受字面布尔值 `True`。

### 4.9 本地溯源具有明确存储上限

[哈希链溯源账本](../tsao_computation/provenance/ledger.py)在追加前验证已有记录。严格 JSON 拒绝重复键、非有限值，以及非零十进制数转浮点后消失的下溢。另一个[并发事件账本](../tsao_computation/execution_boundary.py)采用排他侧车锁与原子替换，并设置 64 MiB 上界：

$$
|\operatorname{UTF8}(E_{n+1})|\le64\times2^{20}\;\mathrm{bytes}.
$$

这是协作式本地文件协议。等待锁超时或旧账本损坏时会失败，不会默默抢占遗留锁。恢复前应确认写入进程已退出并保留账本。哈希链证明记录完整性，不证明其中测量值真实。

## 7. 保留证据地诊断与恢复

| 观察到的现象 | 含义 | 下一步 |
|---|---|---|
| 严格合同拒绝由示例改出的研究 | 必需科学字段缺失或无效 | 用有依据的数据替换占位内容，再生成计划 |
| `candidate-only` / `detected-incomplete` | 注册或环境发现不完整 | 独立安装/配置目标引擎，再次探测 |
| `version-probed-unqualified` | 已有二进制/版本身份 | 补充固定参考输入、数值容差和资格验证输出 |
| `execute_allowed=False` | 准备好的计划尚未授权 | 审阅具体可执行文件/输入/环境身份，在接收环境授权 |
| 非有限值、下溢或温度边界错误 | 数值或物理输入不受支持 | 修正来源单位、范围或模型假设，保留被拒原始记录 |
| 已完成但未收敛/验证 | 仅执行或解析成功 | 查原生诊断，并执行声明的收敛/物理检查 |
| 验收缺失审批或工件绑定 | 科学审阅证据缺失或不匹配 | 对实际工件摘要取得独立验证的审批 |
| Manifest 或派生报告漂移 | 已提交证据不再描述当前源码 | 用仓库脚本重建，审阅差异，再跑原有门禁 |

不要通过写入 `accepted=true`、编造数值或把未知量填成零来补证据。模型、单位变换、输入或可执行文件发生改变时，重新构建受影响的计划与证据链。

## 参考夹具

[`BENCHMARKS` 元组](../tsao_computation/validation/scientific_benchmarks.py) 执行以下八项确定性算例。下表是代码固定参考输入，不是测量值。浮点夹具本身不携带单位元数据；解释有量纲公式时必须使用一致单位基准。

| 函数 | 固定输入 / 离散化 | 比较量 | 容差规则 |
|---|---|---|---|
| `steady_conduction` | 41 节点，$T_L=350$、$T_R=300$，归一化长度 1 | 对线性剖面的最大偏差，参考 0 | 温度基准下绝对 $10^{-11}$ |
| `poiseuille_flow` | $R=0.01$、$\Delta p=100$、$\mu=10^{-3}$、$L=1$；4,000 径向区间 | 积分流量与 $\pi\Delta pR^4/(8\mu L)$ | 相对 $2\times10^{-7}$ |
| `cstr_mass_balance` | $C_{in}=2$、$k=0.4$、$\tau=3$ | $(C_{in}-C)/\tau-kC$，参考 0 | 浓度/时间基准下绝对 $10^{-14}$ |
| `pfr_first_order` | $C_0=1$、$k=0.7$、$\tau=2$；1,000 个 RK4 步 | $C/C_0$ 与 $e^{-k\tau}$ | 相对 $10^{-11}$ |
| `harmonic_oscillator` | $x_0=1$、$v_0=0$、$\Delta t=0.002$，5,000 步 | 最大相对能量漂移，参考 0 | 对无量纲漂移取绝对 $1.1\times10^{-6}$ |
| `gaussian_chain` | $N=120$、$b=0.154$，长度基准另行选择 | $3(Nb^2/3)$ 与 $Nb^2$ | 相对 $10^{-14}$ |
| `parallel_plate_capacitor` | $V=1000$、$d=0.01$；101 节点 | 中心差分场强大小的均值与 $V/d$ | 相对 $10^{-14}$ |
| `electrothermal_balance` | $V=24$、$R=12$、$G=0.8$ | $VI$、$I^2R$、$G\Delta T$ 的最大失配，参考 0 | 功率基准下绝对 $10^{-14}$ |

圆管中 $R,L$ 使用相同长度基准，$\Delta p$ 是压差，$\mu$ 是动力黏度，$Q$ 是体积/时间；解析解假设稳态不可压缩牛顿流体、充分发展的无滑移层流。该夹具不检查密度或雷诺数资格。反应器中 $k\tau$ 必须无量纲，浓度项必须同单位，并假设理想全混/活塞流及恒定一级速率。静电算例的 $V/d$ 具有电场单位；电热模型要求热导为功率/温度，采用稳态集总假设。振子使用无量纲单位质量与刚度；单位初始振幅是夹具选择，不是对外部 MD 的通用归一化要求。

`assess()` 准入有限观测值、参考值与容差，使用有限的补偿差值。实际规则为：

$$
e_{\rm abs}=|\operatorname{fsum}(y,-y_{\rm ref})|,\qquad
G=\begin{cases}
e_{\rm abs}/|y_{\rm ref}|\le t,&y_{\rm ref}\ne0,\\
e_{\rm abs}\le t,&y_{\rm ref}=0.
\end{cases}
$$

零参考分支的 `relative_error` 字段记录绝对误差。没有通用 epsilon 分母，也没有学习得到的容差；一个参数组成功不能证明收敛阶。理想链检查的是独立各向同性链段的协方差迹，不生成随机构象、不估计自相关、不验证力场。这些固定参考与 golden 回归检查本地软件行为。外部科学资格仍需引擎专属输入、可执行文件/构建/环境身份、实际输出、适用参考、收敛研究及独立审阅的解释。

## 统计力学背景

平衡正则系综固定粒子数 $N$、体积 $V$ 和温度 $T>0$：

$$
\beta=\frac{1}{k_BT},\qquad
Z=\sum_i e^{-\beta E_i},\qquad
p_i=\frac{e^{-\beta E_i}}{Z},\qquad
F=-k_BT\ln Z.
$$

$E_i$ 是状态能量，$k_B$ 是玻尔兹曼常数，$\beta E_i$ 必须无量纲；能量与 $k_BT$ 采用共同能量基准，$p_i$ 对声明的状态集合归一化。以上为 [David Tong 统计物理讲义中的正则系综与自由能背景](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S1.html)，不是本包实现的配分函数或自由能引擎。它们解释了为什么计算合同必须先声明系综、状态空间、模型和目标量。

已实现的理想链极限可写成 $\mathbf R=\sum_{j=1}^N\mathbf b_j$。独立各向同性链段满足 $\langle\mathbf b_j\rangle=0$、$\langle|\mathbf b_j|^2\rangle=b^2$，因此 $\langle R^2\rangle=Nb^2$；代码检查 $\operatorname{Cov}(\mathbf R)=(Nb^2/3)\mathbf I_3$ 的迹。排除体积、链段相关和有限链化学需要不同模型。协方差恒等式与很小的末两点差值都不能证明平衡采样。

不确定度同样需要区分：统计、模型与数值分量回答不同问题。已实现的独立分量范数组合已准入标准不确定度，不从轨迹估计这些分量，也不判断模型失配能否当成随机误差。相关性、偏差与缺失机制必须显式处理。

## 性能准入

[`WorkloadSample`](../tsao_computation/performance/model.py) 与 [`profile_workload(s)`](../tsao_computation/performance/runner.py) 区分证据值的准入与实际执行行为。默认 `repeats=7`、`warmups=1`；这是默认值，不证明统计上已经充分。

| 边界 | 实际行为 | 限制 |
|---|---|---|
| 样本墙钟/CPU 时间 | 共用有限标量转换；非负；拒绝布尔、非有限、溢出和非零转零 | 可表示的数值字符串/bytes/Decimal/Fraction、带符号零与次正规数仍允许 |
| `peak_bytes`、`operations` | 真整数检查；峰值非负、操作数为正；拒绝 bool | 保留有效大整数，不统一限制为 $2^{53}$ |
| 重复/预热/计数 | setup 或 operation 前检查；重复/操作数为正，预热非负；操作数还需能转成有限浮点数用于吞吐运算 | 只是计数合同，不是所有元数据或可调用性验证 |
| 批次准备 | 先物化迭代器，再检查全部选中静态计数，之后才运行任何工作负载 setup/operation | 输入迭代本身可能有副作用，并未预验证任意迭代器行为 |
| 实际吞吐 | 中位时长为正时 $q=n_{ops}/\operatorname{median}(t_{wall})$，再检查商是否有限 | 有限分子除以很短的实测时长仍会溢出；拒绝发生在执行之后 |
| 零中位时长 | 保留有限 `float(sys.maxsize)` 回退 | 计时器分辨率或微小工作负载不能证明无限速度 |

有限值检查不撤销副作用，不把失败记录变成成功；应保存原始失败证据。预热不进入采样序列，setup 不在计时间隔内。墙钟时间与进程 CPU 时间不同；`tracemalloc` 记录 Python 分配，并非全部原生或 GPU 内存。P95 使用已实现的最近秩选择。工作负载输入摘要绑定声明的元数据，剖析摘要与环境记录绑定输出载荷；它们不构成通用加速比或外部求解器执行证明。[标量/计数专项回归](../tests/test_performance_evidence_scalar_contract.py)。

优化建议应先识别真实昂贵路径。在同主机、同源码、同工作负载下明确缓存和预热策略，检查行为及数值等价之后再解释计时。缓存、更少文件系统遍历、有界任务并行或引擎原生 GPU 路径可能有效，但都需要具体测量。不要让重型基准相互竞争，再将资源争用归因于实现。

## 原生构建与资格验证

可选 [C++20 核心](../native/README.md) 提供版本化 C ABI、只读 CPU/OpenMP/可选 CUDA Runtime 发现和 Python `ctypes` 桥接。HIP 与 SYCL 能力位保留给独立构建与验证的后端。CUDA Runtime 发现是可选能力；有工具链或可见设备不能证明数值兼容或加速。

从仓库根目录执行：

```bash
cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build/native --config Release --parallel
ctest --test-dir build/native -C Release --output-on-failure
python scripts/verify_native_core.py
```

明确选择 CPU 构建：

```bash
cmake -S native -B build/native-cpu \
  -DTSAO_NATIVE_ENABLE_CUDA_RUNTIME=OFF \
  -DTSAO_NATIVE_ENABLE_OPENMP=ON
```

共享库不在加载搜索路径时，将 `TSAO_NATIVE_LIBRARY` 指向目标库。保持 C ABI 稳定；未来数值内核需提供形状/所有权/精度合同、参考实现、边界与非有限行为、数值/收敛/物理等价、内存检查、CPU 回退及同工作负载端到端性能证据。[原生架构与阶段计划](accelerated-native-backend.md)。

## 验证配置与维护

原有[验证驱动](../scripts/verify_all.py) 是门禁组成的权威。`--profile all` 执行已有 quality、core 与 package 工作；主 README 另外列出 native、benchmark、性能和大日志解析命令。保留原有 95% 总覆盖率、关键模块阈值、受控变异、科学参考、注册表/Schema 检查、派生文件固定点以及源码/wheel 可重复构建。本地子集不能替代这些要求或永久 Windows/Linux CI 矩阵。

[`refresh-current-main-readme.mjs`](../scripts/refresh-current-main-readme.mjs) 保留原有**纯文本源码索引**和确定性的历史输出；它不会向当前主页插入内联 SVG 图库。除两个首图路径现在改为完整图像无障碍外壳，其他历史 SVG 不变。当前四张图记录于 [AI 图像清单](assets/ai-generated/manifest.json)，提示词与模型 ID 是否可得均如实记录，不猜模型版本。

历史报告是快照。源码变化后，用原有生成器重建派生报告，审阅差异，再对精确候选运行必要配置，保留失败和真实退出码。Windows 与 Linux 是支持交付平台，外部引擎及其平台资格仍然独立。
