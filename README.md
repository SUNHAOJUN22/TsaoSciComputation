# TsaoSciComputation

**Traceable computation across scales: connect a scientific question, a calculation contract, controlled execution and evidence that can be reviewed.**

[简体中文](README.zh-CN.md) · [Root Skill](SKILL.md) · [Architecture](docs/architecture.md) · [Capability index](capability-index/README.md) · [Validation](docs/scientific-validation.md)

![version](https://img.shields.io/badge/version-3.0.4-2563eb)

![English concept design: traceable scientific computation, mathematical checks and evidence boundaries](docs/assets/readme-vnext/hero.en.svg)

*AI-assisted concept illustration with deterministic typography. It is not a solver screenshot, a measured curve, or evidence of external execution. The mathematical contracts below identify their implementations and limitations.*

## 1. What you can deliver with this repository

TsaoSciComputation is a Python scientific-computation **control plane**. It creates explicit calculation contracts, selects declared methods and workflows, prepares bounded execution plans, parses supplied outputs and keeps numerical checks separate from scientific acceptance. External DFT, MD, CFD, FEM and process engines remain separately installed and qualified.

| Implemented capability | Main implementation | Concrete output and boundary |
|---|---|---|
| Question routing and strict contract validation | [routing](tsao_computation/routing/router.py), [CalculationContract](tsao_computation/contracts/calculation.py) | Routing decision, missing contract fields and machine-readable plan; a valid plan is not a computed result |
| Registered local functions | [orchestration planner](tsao_computation/orchestration/planner.py) | Seven allowlisted functions for balance, convergence, uncertainty, references, unit lookup and evidence gates |
| External adapter protocols | [Adapter](tsao_computation/adapters/base.py) | Resolved command/input protocol and text observations; unsupported execution protocols remain unavailable |
| Bounded, authorized local execution | [runner](tsao_computation/execution/runner.py), [resource broker](tsao_computation/execution/resources.py) | Process record, file identities, partial batch evidence, CPU/GPU/license admission and timeout containment |
| Dimensioned quantities and model handoffs | [ScientificQuantity](tsao_computation/scientific_quantity.py), [HandoffRecord](tsao_computation/contracts/handoff.py) | Controlled units, source-bound conversion and immutable handoff payloads |
| Scientific confidence and approval | [acceptance](tsao_computation/validation/acceptance.py), [confidence](tsao_computation/validation/confidence.py) | Missing evidence, verified approval counts and C0–C5 classification |
| Reproducible software delivery | [verify_all.py](scripts/verify_all.py), [native core](native/README.md) | Original quality gates, source/wheel reproducibility, SBOMs and native C ABI checks |

<!-- SUPER_SKILL_ORCHESTRATION:START -->
### Inventory is a routing contract

The current registries contain **164 capabilities, 27 external adapters and 20 workflows**. The orchestration layer declares **23 methods, 13 acceleration strategies and seven trusted local functions**. Inspect them with `list capabilities`, `list adapters`, `list workflows`, `list methods` and `list invocations`.

These counts describe registered contracts and integration paths. They do not mean that 27 numerical engines or 23 numerical algorithms are bundled. Generic service, container, scheduler and Skill targets are plan-only until an independently authorized implementation supplies execution evidence. See [orchestration documentation](docs/orchestration.md) and its [machine-readable audit](reports/ULTIMATE_COMPUTATION_SUPER_SKILL_AUDIT.json).
<!-- SUPER_SKILL_ORCHESTRATION:END -->

## 2. Install and obtain a first result

Python **3.10+** is required. The permanent CI matrix covers **Windows and Linux**, using Python 3.10 and 3.13. The package has no mandatory third-party runtime dependencies; validation and release tooling are installed separately from the hash-locked toolchain.

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m venv .venv
```

Activate with `source .venv/bin/activate` on Linux or `.venv\Scripts\Activate.ps1` in Windows PowerShell, then run:

```bash
python -m pip install --require-hashes --only-binary=:all: -r requirements-ci.txt
python -m pip install --no-index --no-deps --no-build-isolation -e '.[validation,quality,security]'
python -m tsao_computation --version
python -m tsao_computation route "DFT to MD to CFD with explicit uncertainty and handoff validation"
python -m tsao_computation validate-contract examples/dft-md-cfd/contract.json --strict
python -m tsao_computation plan examples/dft-md-cfd/contract.json --strict
python -m tsao_computation invoke scientific-benchmarks --execute
```

The example contract is a **preparation template**. It contains methodological intentions and placeholders requiring real material, geometry, parameter and reference data. Strict validation checks the contract's completeness and structure; it does not establish the truth of those inputs. The final command executes eight repository-local analytical/invariant checks, not a third-party solver.

For a small, fully local Python calculation:

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

Hash-locked dependencies and update policy are documented in [CI_DEPENDENCY_POLICY.md](docs/CI_DEPENDENCY_POLICY.md). A dependency hash proves file identity; vulnerability assessment is a separate release concern.

## 3. Choose an execution strategy

| Your situation | Recommended path | Evidence needed before proceeding |
|---|---|---|
| A scientific question with no installed solver | `route` → strict contract → `plan` | Observable, units, conditions, assumptions, parameter sources, convergence and validation plans |
| A small local mathematical check | `invoke` one of the seven registered functions, or use its Python API | Admitted finite inputs, explicit tolerance/unit interpretation and complete result record |
| An existing GROMACS, QE or ORCA installation | Probe identity → prepare input protocol → authorize exact plan → execute | Binary and input hashes, invocation path, environment, working directory and resource claim |
| A Python-module adapter | Use the interpreter that owns the required modules and a declared `.py` driver | Module-location probe and interpreter identity; another environment is not interchangeable |
| A multiscale study | Stage upstream calculation → immutable handoff → downstream model | Units, reference state, conditions, uncertainty, overlapping applicability and review of each transfer |
| A proposed GPU/MPI or native acceleration | Profile → trusted CPU reference → equivalence → same-problem performance | Solver capability fingerprint, numerical tolerance and workload/environment identities |

### Supported command construction

[`Adapter.build_command()`](tsao_computation/adapters/base.py) implements these specific input protocols:

| Adapter | Arguments after the resolved executable | Input requirement |
|---|---|---|
| GROMACS | `mdrun -s system.tpr` | Preprocessed `.tpr`; preprocessing is separate |
| Quantum ESPRESSO | `-i scf.in` | PWscf input deck |
| ORCA | `water.inp` | ORCA input file |
| Declared Python-module adapter | `driver.py` | Python driver and required modules in that interpreter |
| Other adapter records | No generic runnable command | Implement and qualify the engine-specific protocol first |

Constructed plans begin with `execute_allowed=False`. The execution layer binds authorization to the plan rather than treating an installed executable as permission. `invoke --execute` is restricted to registered repository-local callables; it does not launch arbitrary shell commands or turn every adapter into an executable service.

```bash
python -m tsao_computation probe --workers 4
python -m tsao_computation probe-solver gromacs --output .tsao-computation/gromacs-evidence.json
python -m tsao_computation plan-acceleration gromacs --solver-evidence .tsao-computation/gromacs-evidence.json --require-solver-evidence
```

These are availability and bounded version-discovery operations. `version-probed-unqualified` and `evidence-bound-unqualified` still require numerical qualification. Missing executables, incomplete evidence or unsupported protocols remain explicit holds.

Python module discovery uses an isolated `-I -S` subprocess without importing parent packages, executing `sitecustomize` or processing `.pth` hooks. Requests may be grouped only for adapters using the same invocation interpreter; different virtual-environment entry points remain separate. Grouped discovery has no cross-call availability cache. See [isolation tests](tests/test_module_probe_isolation.py), [grouped probe tests](tests/test_grouped_adapter_probe.py) and [interpreter execution tests](tests/test_python_environment_execution.py).

## 4. Mathematical contracts implemented in code

Every numerical formula here has a code reference. Method-selection records and scientific-approval rules are identified as contracts rather than fitted numerical models.

### 4.1 Quantities, dimensions and controlled affine conversion

A quantity records value $x$, unit $u$, seven-dimensional exponent vector $\mathbf d$, source $s$, basis $b$ and optional uncertainty $u_x$:

$$
Q=(x,u,\mathbf d,s,b,u_x),\qquad
\mathbf d=(d_L,d_M,d_T,d_\Theta,d_N,d_I,d_J).
$$

The vector order is length, mass, time, temperature, amount of substance, electric current and luminous intensity. The controlled [unit registry](tsao_computation/quantity_units.py) supplies scale $a$, divisor $d$ and pre-scale offset $o$:

$$
x_{\mathrm{SI}}=(x_s+o_s)\frac{a_s}{d_s},\qquad
x_t=x_{\mathrm{SI}}\frac{d_t}{a_t}-o_t,
\qquad
u_t=u_s\left|\frac{a_s d_t}{d_s a_t}\right|.
$$

For example, `degC` uses $o_s=273.15$, while `degF` uses $o_s=459.67$, $a_s=5$, $d_s=9$. Temperature intervals use the `delta_` units and zero offset. Absolute temperatures and intervals cannot be interconverted. An uncertainty magnitude is scaled, never shifted by an absolute-temperature offset.

[`ScientificQuantity.convert`](tsao_computation/scientific_quantity.py) uses a fully specified **50-significant-digit, round-half-even Decimal context**, independent of the caller's precision, rounding mode, exponent limits and traps. Absolute-temperature admission uses an exact zero-kelvin boundary and requires $T>0\,\mathrm K$. The supported nonzero decimal exponent range is $[-308,308]$. A conversion can still round at 50 digits or fail when its resulting quantity violates that range or physical boundary; it is not arbitrary-precision symbolic arithmetic.

Boolean values, unknown units, incompatible dimensions, negative uncertainty and a supplied factor contradicting the registry are rejected. Conversion records `basis="DERIVED"` and the original quantity digest. A digest identifies the canonical recorded representation, not equivalence between all differently formatted or differently unitized quantities. Regression: [Decimal context isolation](tests/test_decimal_context_isolation.py).

### 4.2 Finite scalar admission and final-pair convergence

[`convergence_check`](tsao_computation/validation/numerical.py) admits each observation, then compares the final two values:

$$
\Delta=|x_n-x_{n-1}|,\quad
s=\max(|x_n|,|x_{n-1}|,1),\quad
\tau=\max(a,r s),\quad
G_{\mathrm{conv}}=(\Delta\le\tau).
$$

$a\ge0$ has the observation's unit; $r\ge0$ is dimensionless. The numeric scale floor of one is expressed in the chosen input basis: normalize units or nondimensionalize before selecting tolerances. The implemented threshold is a **maximum**, not $a+r s$.

Booleans, nonfinite values and nonzero inputs that convert to floating-point zero are rejected. Numeric strings, `Decimal` and `Fraction` inputs follow that conversion guard; exact signed zero and representable subnormals remain valid. Fewer than two observations or an invalid observation fails. This test alone does not prove whole-trajectory convergence, sufficient sampling, mesh independence or a global optimum. Direct failure results can contain an infinite diagnostic sentinel; trusted invocation converts such diagnostics into JSON-safe evidence before hashing. See [underflow regression](tests/test_nonzero_underflow_contract.py).

### 4.3 Conservation with explicit accumulation

[`balance_check`](tsao_computation/validation/physical.py) evaluates quantities already in common units and a common time basis:

$$
r_b=\operatorname{fsum}(I,-O,-A),\qquad
s_b=\max(|I|,|O|,|A|,1),\qquad
e_b=\frac{|r_b|}{s_b},\qquad G_b=(e_b\le\varepsilon).
$$

$I$ is input, $O$ output and $A$ accumulation, positive when the control volume stores material or energy. The supplied tolerance $\varepsilon\ge0$ is dimensionless. Compensated summation preserves representable cancellation residuals. Overflow, nonfinite inputs and a nonzero normalized residual that underflows to zero are errors. Unit conversion, component stoichiometry and reaction-model validity must be established before calling this scalar function; they cannot be inferred from a small residual.

### 4.4 Independent standard uncertainty

[`combine_independent`](tsao_computation/uncertainty/model.py) computes

$$
u_c=\operatorname{hypot}(u_1,\ldots,u_k)
=\sqrt{\sum_{i=1}^k u_i^2},\qquad u_i\ge0.
$$

`UncertaintyBudget` names statistical, model and numerical components. Components must share one unit and compatible standard-uncertainty interpretations; the quadrature assumes uncorrelated contributions. `math.hypot` avoids avoidable intermediate square overflow, while a nonfinite final result or an underflowed nonzero input is rejected. An empty component list yields zero mathematically; it must not be used as evidence that all uncertainty sources were assessed.

For a correlated model the required first-order relationship is

$$
u_y^2=\mathbf J\,\boldsymbol\Sigma\,\mathbf J^{\mathsf T},
$$

with sensitivity row $\mathbf J$ and covariance matrix $\boldsymbol\Sigma$. This equation explains the **limitation**: covariance propagation is not performed by `combine_independent`. Supply a separately validated model when correlations matter. See [result-range regression](tests/test_uncertainty_result_range.py).

### 4.5 Model handoffs preserve scientific meaning

[`HandoffRecord`](tsao_computation/contracts/handoff.py) binds source and receiving models, observable, values, units, conditions, reference state, statistical/model uncertainty, applicability and transformation. Its identity is

$$
H_H=\operatorname{SHA256}\!\left(\operatorname{CanonicalJSON}(P_H)\right),
$$

where $P_H$ is exactly `canonical_payload()`. The review decision and signature are excluded from this payload to avoid circular signing. A review must bind to this exact digest; approval of another value or transformation is insufficient.

Values are finite scalars or nonempty rectangular arrays, at most six nesting levels and 100,000 scalar cells. Uncertainty is nonnegative and either shape-matched or an explicitly supplied scalar bound. Structured uncertainty includes a dimension-compatible unit; it is preserved in its own unit and must be converted before combination. Nested data are copied and frozen, so caller mutation cannot change the admitted record. `checked` is a software-contract status; `validated` additionally requires artifact-bound external approval.

### 4.6 Parsing observes supplied text

[`Adapter.parse`](tsao_computation/adapters/base.py) retains the text digest, parser version, detected engine-version text and the start of the active run. A later run start prevents an earlier success marker from certifying a truncated new run. Conceptually, its positive and negative observations obey

$$
G_{\mathrm{complete}}=P_c\land\neg N_c,\qquad
G_{\mathrm{converged}}=G_{\mathrm{complete}}\land P_v\land\neg N_v.
$$

$P_c,P_v$ denote recognized positive completion/convergence markers; $N_c,N_v$ denote their negative counterparts. Examples such as `not normal termination`, `SCF not yet converged` and `converged=false` do not become successes. These are text observations, not independent proof of executable identity or physics; parser `validated` stays false. Retain original output bytes and the execution record separately, especially when decoding changes text. See [parser regression](tests/test_performance_optimizations.py).

### 4.7 Resource admission and execution identity

The local [resource broker](tsao_computation/execution/resources.py) admits a set of concurrent jobs $\mathcal P$ only within declared additive capacities:

$$
\sum_{p\in\mathcal P}r_{p,j}\le c_j.
$$

$r_{p,j}$ is job $p$'s CPU or license claim and $c_j$ the corresponding capacity. GPUs additionally require device membership, exclusivity and consistent visibility. The broker is local; it does not replace an external cluster scheduler or prove license-server availability.

The [runner](tsao_computation/execution/runner.py) binds the exact command, executable invocation path and resolved target, executable/input bytes, working directory and environment into an authorized plan. File identity follows

$$
H_f=\operatorname{SHA256}(\mathrm{bytes}_f).
$$

Timeout containment terminates process trees. Batch failures retain completed records and identify their original request indices; a missing process record remains a failure, not a synthetic success. Resource release does not establish convergence or acceptance. See [execution boundary tests](tests/test_execution_boundary_contract.py) and [timeout tests](tests/test_process_timeout_containment.py).

### 4.8 Acceptance is an evidence gate

[`acceptance_gate`](tsao_computation/validation/acceptance.py) requires seven strict boolean conditions:

$$
G_S=C\land P\land V\land F\land U\land D\land E,
\qquad
G_A=G_S\land H\land A_{\mathrm{verified}}.
$$

$C$: completed; $P$: parsed; $V$: converged; $F$: physically validated; $U$: uncertainty quantified; $D$: applicability confirmed; $E$: evidence bound. $H$ is a valid artifact SHA-256 and $A_{\mathrm{verified}}$ is at least one valid, time-bounded external attestation with the required scope and role. These flags are declared evidence inputs, not an autonomous scientific truth detector.

The built-in gate verifies HMAC-SHA256 attestations using trusted keys supplied **outside** the result record. It requires scope `scientific-result-acceptance`, role `independent-domain-reviewer`, and distinct requester/approver identities. C5 additionally requires signed decision-scope, safety-review and independent-reproduction evidence. Duplicate eligible nonces cannot count for different governance purposes. The implementation is not a persistent cross-request replay database, institutional identity service or key-revocation system; deployments must supply those controls where required. The separate public `acceptance_is_verified` API delegates signature verification to a consumer-provided verifier and accepts only the literal result `True`.

### 4.9 Local provenance has a finite storage contract

The [hash-linked provenance ledger](tsao_computation/provenance/ledger.py) verifies existing records before append. Strict JSON rejects duplicate keys, nonfinite values and nonzero decimal-to-float underflow. The separate [concurrent event ledger](tsao_computation/execution_boundary.py) uses an exclusive sidecar lock and atomic replacement, with a 64 MiB bound:

$$
|\operatorname{UTF8}(E_{n+1})|\le64\times2^{20}\;\mathrm{bytes}.
$$

This is a cooperating local-file protocol. A lock timeout or corrupted previous ledger fails; an abandoned lock is not silently stolen. Confirm the writer has exited and preserve the ledger before recovery. Hash linkage establishes record integrity, not the truth of the measurements inside it.

## 5. Analytical reference checks and their assumptions

[`scientific_benchmarks.py`](tsao_computation/validation/scientific_benchmarks.py) executes eight deterministic software references:

| Reference | Mathematical target | Assumption or scope |
|---|---|---|
| 1D steady conduction | $T(x)=T_L+(T_R-T_L)x/L$ | Constant properties, no source; finite-difference profile |
| Poiseuille flow | $Q=\pi\Delta p R^4/(8\mu L)$ | Steady laminar Newtonian pipe flow; radial integration |
| First-order CSTR | $C=C_{in}/(1+k\tau)$ | Ideal steady mixing; reaction balance closure |
| First-order PFR | $C/C_0=e^{-k\tau}$ | Constant first-order rate; RK4 reference integration |
| Harmonic oscillator | $E=(x^2+v^2)/2$ | Unit mass and stiffness; velocity-Verlet energy drift |
| Gaussian chain | $\langle R^2\rangle=Nb^2$ | Ideal isotropic independent segments |
| Parallel plates | $\lvert\mathcal E\rvert=V/d$ | Linear potential, neglected fringing; central difference |
| Electrothermal balance | $VI=I^2R=G\Delta T$ | Steady lumped removal; constant resistance/conductance |

$k$ is rate constant, $\tau$ residence time, $\mu$ viscosity, $R$ pipe radius or electrical resistance as specified by the row, $G$ thermal conductance, and $b$ segment length. Each function fixes its reference parameters and tolerance in code. A pass verifies that fixture and numerical invariant; it does not validate an arbitrary material, constitutive law or external engine.

## 6. Verification and release evidence

```bash
python scripts/verify_all.py --profile all
python scripts/verify_native_core.py
python scripts/verify_all.py --profile benchmark
python -m pytest -q tests/test_performance_v9.py tests/test_performance_optimizations.py
python scripts/run_large_parser_regression.py
python scripts/final_acceptance_preflight.py --json
```

`all` executes the original quality, core and package profiles. It includes Ruff, formatting, Mypy, Bandit, repository security scanning, controlled mutation, the complete pytest suite, **95% total coverage**, critical-module coverage, scientific references, Schema/registry audits, generated-file checks, reproducible source/wheel builds, isolated installation, SBOMs and checksums. Native C ABI and benchmark/performance commands remain additional gates. The large-parser regression uses generated local text, not measured solver output.

<!-- CURRENT_MAIN_VERIFICATION:START -->
### Qualification belongs to an exact commit

| Metadata | Value |
|---|---|
| Version | 3.0.4 |

Use the permanent [CI workflow](.github/workflows/ci.yml) and original artifacts for the commit being deployed. Historical files under `reports/` are snapshots. Neither a previous green run nor focused tests qualify a newer commit. Six-hour regression requires original receipts binding the exact source SHA, elapsed successful test-process time and all failure evidence; this README does not predeclare its completion. External engines remain **EXTERNAL_HOLD** until their independent evidence is provided.
<!-- CURRENT_MAIN_VERIFICATION:END -->

## 7. Diagnose and recover without losing evidence

| Observation | Meaning | Next action |
|---|---|---|
| Strict contract rejects an example-derived study | Required scientific fields are absent or invalid | Replace placeholders with justified data and regenerate the plan |
| `candidate-only` / `detected-incomplete` | Registry or environment discovery is incomplete | Install/configure the intended engine separately and probe again |
| `version-probed-unqualified` | Binary/version evidence exists | Add fixed reference inputs, numerical tolerances and qualification outputs |
| `execute_allowed=False` | A prepared plan has not been authorized | Review the exact executable/input/environment identity and authorize in the receiving environment |
| Nonfinite/underflow/temperature-boundary error | Numerical or physical input is unsupported | Correct source units/range or model assumptions; retain the rejected original |
| Completed but not converged/validated | Execution or parsing alone succeeded | Inspect native diagnostics and execute the declared convergence/physical checks |
| Acceptance missing approvals or artifact binding | Scientific review evidence is absent or mismatched | Obtain an independently verified approval over the actual artifact digest |
| Manifest or derived-report drift | Checked-in evidence no longer describes the source | Regenerate using repository scripts, review the diff and rerun unchanged gates |

Do not repair missing evidence by writing `accepted=true`, inventing values or replacing unknowns with zero. When changing a model, unit transformation, input or executable, rebuild the affected plan and evidence chain.

## 8. Documentation, visual archive and project policy

The two root READMEs use their respective language-specific concept designs. The **43 legacy Scientific Research Console V13 SVGs** remain available in the [technical visual atlas](assets/visuals/README.md), with their original [design and safety policy](assets/visuals/DESIGN_SYSTEM.md). They explain methods and integration ambitions; they do not assert live external solver execution. The original source assets remain inspectable and safety-checked rather than being silently replaced.

Useful deeper references: [adapter documents](adapters), [workflow documents](skills/workflows), [scenario examples](examples), [release policy](docs/release.md), [acceptance guide](README_ACCEPTANCE.md), [native ABI](native/README.md) and [third-party boundaries](THIRD_PARTY.md).

`main` is the sole authoritative long-lived branch. Windows and Linux are the supported delivery platforms. No commercial solver, license or private dataset is bundled. MIT license: [LICENSE](LICENSE); citation metadata: [CITATION.cff](CITATION.cff).

<!-- CURRENT_MAIN_ACCEPTANCE_V2:START -->
### Maintained source index

[Adapter and parser](tsao_computation/adapters/base.py) · [Execution record](tsao_computation/execution/runner.py) · [Convergence](tsao_computation/validation/numerical.py) · [Uncertainty](tsao_computation/uncertainty/model.py) · [Legacy localized architecture](docs/current-main/tsao-scicomputation-current-main-en.svg)

The equations and strategies above describe current code. Concept figures and historical artifacts are not execution attestations. Changed source requires fresh qualification.
<!-- CURRENT_MAIN_ACCEPTANCE_V2:END -->
