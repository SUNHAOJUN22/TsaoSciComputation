# Scientific contracts and implementation guide

[简体中文](scientific-contracts.zh-CN.md) · [Main README](../README.md) · [Acceptance](../README_ACCEPTANCE.md)

This guide is the detailed companion to the four AI-generated README figures. It maps every implemented numerical claim to code, preserves the execution and parser contracts, and separates local software references from external scientific qualification.

## Reading a result

Treat the question, model, numerical realization and evidence as separate records. Choose an observable and units; specify boundary conditions and assumptions; bind exact inputs and execution identity; then check numerical, physical and approval criteria. A hash binds bytes, not scientific truth. A successful command is evidence of that command only.

## Execution protocols

### Strategy and prerequisites

| Your situation | Recommended path | Evidence needed before proceeding |
|---|---|---|
| A scientific question with no installed solver | `route` → strict contract → `plan` | Observable, units, conditions, assumptions, parameter sources, convergence and validation plans |
| A small local mathematical check | `invoke` one of the seven registered functions, or use its Python API | Admitted finite inputs, explicit tolerance/unit interpretation and complete result record |
| An existing GROMACS, QE or ORCA installation | Probe identity → prepare input protocol → authorize exact plan → execute | Binary and input hashes, invocation path, environment, working directory and resource claim |
| A Python-module adapter | Use the interpreter that owns the required modules and a declared `.py` driver | Module-location probe and interpreter identity; another environment is not interchangeable |
| A multiscale study | Stage upstream calculation → immutable handoff → downstream model | Units, reference state, conditions, uncertainty, overlapping applicability and review of each transfer |
| A proposed GPU/MPI or native acceleration | Profile → trusted CPU reference → equivalence → same-problem performance | Solver capability fingerprint, numerical tolerance and workload/environment identities |

### Supported command construction

[`Adapter.build_command()`](../tsao_computation/adapters/base.py) implements these specific input protocols:

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

Python module discovery uses an isolated `-I -S` subprocess without importing parent packages, executing `sitecustomize` or processing `.pth` hooks. Requests may be grouped only for adapters using the same invocation interpreter; different virtual-environment entry points remain separate. Grouped discovery has no cross-call availability cache. See [isolation tests](../tests/test_module_probe_isolation.py), [grouped probe tests](../tests/test_grouped_adapter_probe.py) and [interpreter execution tests](../tests/test_python_environment_execution.py).

## Implemented mathematical contracts

Every numerical formula here has a code reference. Method-selection records and scientific-approval rules are identified as contracts rather than fitted numerical models.

### 4.1 Quantities, dimensions and controlled affine conversion

A quantity records value $x$, unit $u$, seven-dimensional exponent vector $\mathbf d$, source $s$, basis $b$ and optional uncertainty $u_x$:

$$
Q=(x,u,\mathbf d,s,b,u_x),\qquad
\mathbf d=(d_L,d_M,d_T,d_\Theta,d_N,d_I,d_J).
$$

The vector order is length, mass, time, temperature, amount of substance, electric current and luminous intensity. The controlled [unit registry](../tsao_computation/quantity_units.py) supplies scale $a$, divisor $d$ and pre-scale offset $o$:

$$
x_{\mathrm{SI}}=(x_s+o_s)\frac{a_s}{d_s},\qquad
x_t=x_{\mathrm{SI}}\frac{d_t}{a_t}-o_t,
\qquad
u_t=u_s\left|\frac{a_s d_t}{d_s a_t}\right|.
$$

For example, `degC` uses $o_s=273.15$, while `degF` uses $o_s=459.67$, $a_s=5$, $d_s=9$. Temperature intervals use the `delta_` units and zero offset. Absolute temperatures and intervals cannot be interconverted. An uncertainty magnitude is scaled, never shifted by an absolute-temperature offset.

[`ScientificQuantity.convert`](../tsao_computation/scientific_quantity.py) uses a fully specified **50-significant-digit, round-half-even Decimal context**, independent of the caller's precision, rounding mode, exponent limits and traps. Absolute-temperature admission uses an exact zero-kelvin boundary and requires $T>0\,\mathrm K$. The supported nonzero decimal exponent range is $[-308,308]$. A conversion can still round at 50 digits or fail when its resulting quantity violates that range or physical boundary; it is not arbitrary-precision symbolic arithmetic.

Boolean values, unknown units, incompatible dimensions, negative uncertainty and a supplied factor contradicting the registry are rejected. Conversion records `basis="DERIVED"` and the original quantity digest. A digest identifies the canonical recorded representation, not equivalence between all differently formatted or differently unitized quantities. Regression: [Decimal context isolation](../tests/test_decimal_context_isolation.py).

### 4.2 Finite scalar admission and final-pair convergence

[`convergence_check`](../tsao_computation/validation/numerical.py) admits each observation, then compares the final two values:

$$
\Delta=|x_n-x_{n-1}|,\quad
s=\max(|x_n|,|x_{n-1}|,1),\quad
\tau=\max(a,r s),\quad
G_{\mathrm{conv}}=(\Delta\le\tau).
$$

$a\ge0$ has the observation's unit; $r\ge0$ is dimensionless. The numeric scale floor of one is expressed in the chosen input basis: normalize units or nondimensionalize before selecting tolerances. The implemented threshold is a **maximum**, not $a+r s$.

Booleans, nonfinite values and nonzero inputs that convert to floating-point zero are rejected. Numeric strings, `Decimal` and `Fraction` inputs follow that conversion guard; exact signed zero and representable subnormals remain valid. Fewer than two observations or an invalid observation fails. This test alone does not prove whole-trajectory convergence, sufficient sampling, mesh independence or a global optimum. Direct failure results can contain an infinite diagnostic sentinel; trusted invocation converts such diagnostics into JSON-safe evidence before hashing. See [underflow regression](../tests/test_nonzero_underflow_contract.py).

### 4.3 Conservation with explicit accumulation

[`balance_check`](../tsao_computation/validation/physical.py) evaluates quantities already in common units and a common time basis:

$$
r_b=\operatorname{fsum}(I,-O,-A),\qquad
s_b=\max(|I|,|O|,|A|,1),\qquad
e_b=\frac{|r_b|}{s_b},\qquad G_b=(e_b\le\varepsilon).
$$

$I$ is input, $O$ output and $A$ accumulation, positive when the control volume stores material or energy. The supplied tolerance $\varepsilon\ge0$ is dimensionless. Compensated summation preserves representable cancellation residuals. Overflow, nonfinite inputs and a nonzero normalized residual that underflows to zero are errors. Unit conversion, component stoichiometry and reaction-model validity must be established before calling this scalar function; they cannot be inferred from a small residual.

### 4.4 Independent standard uncertainty

[`combine_independent`](../tsao_computation/uncertainty/model.py) computes

$$
u_c=\operatorname{hypot}(u_1,\ldots,u_k)
=\sqrt{\sum_{i=1}^k u_i^2},\qquad u_i\ge0.
$$

`UncertaintyBudget` names statistical, model and numerical components. Components must share one unit and compatible standard-uncertainty interpretations; the quadrature assumes uncorrelated contributions. `math.hypot` avoids avoidable intermediate square overflow, while a nonfinite final result or an underflowed nonzero input is rejected. An empty component list yields zero mathematically; it must not be used as evidence that all uncertainty sources were assessed.

For a correlated model the required first-order relationship is

$$
u_y^2=\mathbf J\,\boldsymbol\Sigma\,\mathbf J^{\mathsf T},
$$

with sensitivity row $\mathbf J$ and covariance matrix $\boldsymbol\Sigma$. This equation explains the **limitation**: covariance propagation is not performed by `combine_independent`. Supply a separately validated model when correlations matter. See [result-range regression](../tests/test_uncertainty_result_range.py).

### 4.5 Model handoffs preserve scientific meaning

[`HandoffRecord`](../tsao_computation/contracts/handoff.py) binds source and receiving models, observable, values, units, conditions, reference state, statistical/model uncertainty, applicability and transformation. Its identity is

$$
H_H=\operatorname{SHA256}\!\left(\operatorname{CanonicalJSON}(P_H)\right),
$$

where $P_H$ is exactly `canonical_payload()`. The review decision and signature are excluded from this payload to avoid circular signing. A review must bind to this exact digest; approval of another value or transformation is insufficient.

Values are finite scalars or nonempty rectangular arrays, at most six nesting levels and 100,000 scalar cells. Uncertainty is nonnegative and either shape-matched or an explicitly supplied scalar bound. Structured uncertainty includes a dimension-compatible unit; it is preserved in its own unit and must be converted before combination. Nested data are copied and frozen, so caller mutation cannot change the admitted record. `checked` is a software-contract status; `validated` additionally requires artifact-bound external approval.

### 4.6 Parsing observes supplied text

[`Adapter.parse`](../tsao_computation/adapters/base.py) retains the text digest, parser version, detected engine-version text and the start of the active run. A later run start prevents an earlier success marker from certifying a truncated new run. Conceptually, its positive and negative observations obey

$$
G_{\mathrm{complete}}=P_c\land\neg N_c,\qquad
G_{\mathrm{converged}}=G_{\mathrm{complete}}\land P_v\land\neg N_v.
$$

$P_c,P_v$ denote recognized positive completion/convergence markers; $N_c,N_v$ denote their negative counterparts. Examples such as `not normal termination`, `SCF not yet converged` and `converged=false` do not become successes. These are text observations, not independent proof of executable identity or physics; parser `validated` stays false. Retain original output bytes and the execution record separately, especially when decoding changes text. See [parser regression](../tests/test_performance_optimizations.py).

### 4.7 Resource admission and execution identity

The local [resource broker](../tsao_computation/execution/resources.py) admits a set of concurrent jobs $\mathcal P$ only within declared additive capacities:

$$
\sum_{p\in\mathcal P}r_{p,j}\le c_j.
$$

$r_{p,j}$ is job $p$'s CPU or license claim and $c_j$ the corresponding capacity. GPUs additionally require device membership, exclusivity and consistent visibility. The broker is local; it does not replace an external cluster scheduler or prove license-server availability.

The [runner](../tsao_computation/execution/runner.py) binds the exact command, executable invocation path and resolved target, executable/input bytes, working directory and environment into an authorized plan. File identity follows

$$
H_f=\operatorname{SHA256}(\mathrm{bytes}_f).
$$

Timeout containment terminates process trees. Batch failures retain completed records and identify their original request indices; a missing process record remains a failure, not a synthetic success. Resource release does not establish convergence or acceptance. See [execution boundary tests](../tests/test_execution_boundary_contract.py) and [timeout tests](../tests/test_process_timeout_containment.py).

### 4.8 Acceptance is an evidence gate

[`acceptance_gate`](../tsao_computation/validation/acceptance.py) requires seven strict boolean conditions:

$$
G_S=C\land P\land V\land F\land U\land D\land E,
\qquad
G_A=G_S\land H\land A_{\mathrm{verified}}.
$$

$C$: completed; $P$: parsed; $V$: converged; $F$: physically validated; $U$: uncertainty quantified; $D$: applicability confirmed; $E$: evidence bound. $H$ is a valid artifact SHA-256 and $A_{\mathrm{verified}}$ is at least one valid, time-bounded external attestation with the required scope and role. These flags are declared evidence inputs, not an autonomous scientific truth detector.

The built-in gate verifies HMAC-SHA256 attestations using trusted keys supplied **outside** the result record. It requires scope `scientific-result-acceptance`, role `independent-domain-reviewer`, and distinct requester/approver identities. C5 additionally requires signed decision-scope, safety-review and independent-reproduction evidence. Duplicate eligible nonces cannot count for different governance purposes. The implementation is not a persistent cross-request replay database, institutional identity service or key-revocation system; deployments must supply those controls where required. The separate public `acceptance_is_verified` API delegates signature verification to a consumer-provided verifier and accepts only the literal result `True`.

### 4.9 Local provenance has a finite storage contract

The [hash-linked provenance ledger](../tsao_computation/provenance/ledger.py) verifies existing records before append. Strict JSON rejects duplicate keys, nonfinite values and nonzero decimal-to-float underflow. The separate [concurrent event ledger](../tsao_computation/execution_boundary.py) uses an exclusive sidecar lock and atomic replacement, with a 64 MiB bound:

$$
|\operatorname{UTF8}(E_{n+1})|\le64\times2^{20}\;\mathrm{bytes}.
$$

This is a cooperating local-file protocol. A lock timeout or corrupted previous ledger fails; an abandoned lock is not silently stolen. Confirm the writer has exited and preserve the ledger before recovery. Hash linkage establishes record integrity, not the truth of the measurements inside it.

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

## Reference fixtures

The [`BENCHMARKS` tuple](../tsao_computation/validation/scientific_benchmarks.py) runs these eight deterministic cases. The values below are hard-coded reference inputs, not measurements. The float fixtures do not carry unit metadata; use a coherent unit basis when interpreting dimensional formulas.

| Function | Fixed inputs / discretization | Compared quantity | Tolerance rule |
|---|---|---|---|
| `steady_conduction` | 41 nodes, $T_L=350$, $T_R=300$, normalized length 1 | Maximum deviation from the linear profile, expected 0 | Absolute $10^{-11}$ in the temperature basis |
| `poiseuille_flow` | $R=0.01$, $\Delta p=100$, $\mu=10^{-3}$, $L=1$; 4,000 radial intervals | Quadrature flow against $\pi\Delta pR^4/(8\mu L)$ | Relative $2\times10^{-7}$ |
| `cstr_mass_balance` | $C_{in}=2$, $k=0.4$, $\tau=3$ | $(C_{in}-C)/\tau-kC$, expected 0 | Absolute $10^{-14}$ in the concentration/time basis |
| `pfr_first_order` | $C_0=1$, $k=0.7$, $\tau=2$; 1,000 RK4 steps | $C/C_0$ against $e^{-k\tau}$ | Relative $10^{-11}$ |
| `harmonic_oscillator` | $x_0=1$, $v_0=0$, $\Delta t=0.002$, 5,000 steps | Maximum relative energy drift, expected 0 | Absolute $1.1\times10^{-6}$ on this dimensionless drift |
| `gaussian_chain` | $N=120$, $b=0.154$ in a chosen length basis | $3(Nb^2/3)$ against $Nb^2$ | Relative $10^{-14}$ |
| `parallel_plate_capacitor` | $V=1000$, $d=0.01$; 101 nodes | Mean central-difference field magnitude against $V/d$ | Relative $10^{-14}$ |
| `electrothermal_balance` | $V=24$, $R=12$, $G=0.8$ | Maximum mismatch among $VI$, $I^2R$, $G\Delta T$, expected 0 | Absolute $10^{-14}$ in the power basis |

For pipe flow, $R,L$ share a length basis, $\Delta p$ is pressure, $\mu$ is dynamic viscosity and $Q$ is volume/time. The analytical solution assumes steady incompressible, Newtonian, fully developed laminar flow with no slip. No density or Reynolds-number qualification is performed by this fixture. For the reactors, $k\tau$ must be dimensionless, concentration terms must share units, and ideal mixing/plug flow plus a constant first-order rate are assumptions. For electrostatics, $V/d$ has electric-field units. For electrothermal balance, conductance has power/temperature units and the model is steady and lumped. The oscillator uses dimensionless unit mass and stiffness; its unit initial amplitude is a fixture choice, not a general normalization imposed on external MD.

`assess()` admits finite observed/reference/tolerance values and uses a finite compensated difference. Its actual rule is

$$
e_{\rm abs}=|\operatorname{fsum}(y,-y_{\rm ref})|,\qquad
G=\begin{cases}
e_{\rm abs}/|y_{\rm ref}|\le t,&y_{\rm ref}\ne0,\\
e_{\rm abs}\le t,&y_{\rm ref}=0.
\end{cases}
$$

The reported `relative_error` is set to the absolute error in the zero-reference branch. There is no generic epsilon denominator, no learned tolerance and no claim that one successful parameter set establishes convergence order. The ideal-chain case is a covariance-trace identity with independent isotropic segments; it does not generate random conformations, estimate autocorrelation or test a force field. These fixed references and golden regressions validate local software behavior. External scientific qualification requires an engine-specific input deck, executable/build/environment identity, output, applicable reference, convergence study and independently reviewed interpretation.

## Statistical mechanics context

For an equilibrium canonical ensemble with fixed particle number $N$, volume $V$ and temperature $T>0$, define

$$
\beta=\frac{1}{k_BT},\qquad
Z=\sum_i e^{-\beta E_i},\qquad
p_i=\frac{e^{-\beta E_i}}{Z},\qquad
F=-k_BT\ln Z.
$$

Here $E_i$ is a state energy, $k_B$ is Boltzmann's constant and $\beta E_i$ is dimensionless. Energies and $k_BT$ need the same energy basis; $p_i$ normalizes over the specified states. These are theoretical context from [David Tong's statistical-physics notes, canonical ensemble and free energy](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S1.html), not an implemented partition-function or free-energy engine in this package. They explain why a calculation contract must state its ensemble, state space, model and observable before a numerical result can be interpreted.

For the implemented ideal-chain limit, write $\mathbf R=\sum_{j=1}^N\mathbf b_j$. Independent isotropic segments with $\langle\mathbf b_j\rangle=0$ and $\langle|\mathbf b_j|^2\rangle=b^2$ give $\langle R^2\rangle=Nb^2$. The code checks the trace of $\operatorname{Cov}(\mathbf R)=(Nb^2/3)\mathbf I_3$. Excluded volume, segment correlation and finite-chain chemistry require a different physical model. Neither a covariance identity nor a small final-pair difference establishes equilibrium sampling.

This distinction also applies to uncertainty: statistical, model and numerical contributions describe different questions. The implemented independent-component norm combines admitted standard uncertainties; it does not estimate those components from trajectories or decide whether a model discrepancy is random. Correlation, bias and missing mechanisms need explicit scientific treatment.

## Performance admission

[`WorkloadSample`](../tsao_computation/performance/model.py) and [`profile_workload(s)`](../tsao_computation/performance/runner.py) separate admitted evidence values from measured execution behavior. Defaults are `repeats=7`, `warmups=1`; they are defaults, not proof of a statistically adequate benchmark.

| Boundary | Actual behavior | Limit |
|---|---|---|
| Sample wall/CPU time | Shared finite-scalar conversion; nonnegative; boolean, nonfinite, overflow and nonzero-to-zero conversion rejected | Representable numeric strings/bytes/Decimal/Fraction, signed zero and subnormals remain admissible |
| `peak_bytes`, `operations` | True integer checks; peak nonnegative, operations positive; bool rejected | Valid large integers are preserved; no blanket $2^{53}$ restriction |
| Repeats/warmups/count | Integer checks before setup or operation; repeats/count positive, warmups nonnegative; operation count must also convert to finite float for throughput arithmetic | This is a count contract, not general metadata/callability validation |
| Batch preparation | Materialize the iterable, then validate all selected static counts before any workload setup or operation | Iterating the input may have its own effects; arbitrary iterable behavior is not prevalidated |
| Measured throughput | $q=n_{ops}/\operatorname{median}(t_{wall})$ for positive median; finite-scalar check on the computed quotient | A finite numerator can overflow for a small observed duration; rejection occurs after operations have run |
| Zero observed median | Existing finite `float(sys.maxsize)` fallback | Timer resolution or a tiny workload cannot establish infinite speed |

The finite check does not undo side effects or convert a failed performance record into a successful one. Keep original failure evidence. Warmups run outside the captured sample series; setup is outside measured intervals. Wall time and process CPU time are distinct. `tracemalloc` reports Python allocation, not total native or GPU memory. P95 uses the implemented nearest-rank selection. The workload input hash binds declared workload metadata; the profile hash and environment record bind the emitted payload. These records are not a universal speedup claim or proof that an external solver ran. [Focused scalar/count regressions](../tests/test_performance_evidence_scalar_contract.py).

A useful optimization proposal identifies the actual costly path first. Compare the same source and workload on the same host with declared cache/warmup policy; then check behavior and numerical equivalence before interpreting time. Caching, fewer filesystem passes, bounded task parallelism or an engine-supported GPU route may be appropriate, but require measurements for the specific workload. Do not parallelize competing heavy benchmarks and then attribute contention to the implementation.

## Native build and qualification

The optional [C++20 core](../native/README.md) exposes a versioned C ABI, read-only CPU/OpenMP/optional CUDA Runtime discovery and a Python `ctypes` bridge. HIP and SYCL capability bits are reserved for separately built and validated backends. CUDA Runtime discovery is optional; neither a toolkit nor a visible device proves numerical compatibility or acceleration.

From the repository root:

```bash
cmake -S native -B build/native -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build/native --config Release --parallel
ctest --test-dir build/native -C Release --output-on-failure
python scripts/verify_native_core.py
```

For an explicit CPU build:

```bash
cmake -S native -B build/native-cpu \
  -DTSAO_NATIVE_ENABLE_CUDA_RUNTIME=OFF \
  -DTSAO_NATIVE_ENABLE_OPENMP=ON
```

Set `TSAO_NATIVE_LIBRARY` to the intended shared-library path when it is not in the loader search path. Keep the C ABI stable. A future numerical kernel needs shape/ownership/precision contracts, a reference implementation, bounds and nonfinite behavior, numerical/convergence/physical equivalence, memory checks, CPU fallback and matched end-to-end performance evidence. [Native architecture and phased plan](accelerated-native-backend.md).

## Verification profiles and maintenance

The original [verification driver](../scripts/verify_all.py) remains the authority for gate composition. `--profile all` runs the existing quality, core and package work; the root README lists native, benchmark, performance and large-parser commands separately. Keep the original 95% overall coverage threshold, critical-module thresholds, controlled mutations, scientific references, registry/schema checks, derived-file fixed points and reproducible source/wheel builds. A local subset does not replace them or the permanent Windows/Linux CI matrix.

[`refresh-current-main-readme.mjs`](../scripts/refresh-current-main-readme.mjs) retains the original **text-only source-index** sections and deterministic historical output. It does not inject an inline SVG gallery into the current main README. The historical SVGs remain unmodified, apart from the two hero paths that now contain whole-image accessibility wrappers. The four current illustrations are recorded in the [AI asset manifest](assets/ai-generated/manifest.json); exact prompts and model-ID availability are recorded without guessing a model version.

Historical reports are snapshots. Rebuild source-derived reports with the original generators after source changes, inspect differences, then run the required profiles on the exact candidate. Keep failures and actual return codes. The supported delivery platforms are Windows and Linux; external engines and their own platform qualifications remain independent.
