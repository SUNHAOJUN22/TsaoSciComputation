<div align="center">

<img src="assets/visuals/hero-multiscale.svg" alt="TsaoSciComputation evidence-governed multiscale architecture" width="100%">

# TsaoSciComputation

**Evidence-governed scientific-computation orchestration from equations and solver identity to reproducible delivery.**

![version](https://img.shields.io/badge/version-3.0.4-2563eb) ![capabilities](https://img.shields.io/badge/capabilities-164-7c3aed) ![adapters](https://img.shields.io/badge/adapters-27-ea580c) ![workflows](https://img.shields.io/badge/workflows-20-0891b2) ![tests](https://img.shields.io/badge/tests-845%20passed-16a34a) ![coverage](https://img.shields.io/badge/coverage-95.25%25-0891b2)

[中文说明](README.zh-CN.md) · [Root Skill](SKILL.md) · [Capabilities](capability-index/README.md) · [Visual atlas](assets/visuals/README.md) · [Validation](docs/scientific-validation.md) · [Architecture](docs/architecture.md) · [Delivery prompt](docs/autonomous-software-hardening-prompt.md)

</div>

## Delivery status

The current software baseline is suitable for repository-level delivery and acceptance:

- **164 capabilities**, **27 external adapters** and **20 machine-readable workflows**;
- **845 deterministic tests passed** with **95.25% total coverage**;
- Ruff, Mypy, Bandit, repository security scanning, controlled mutation, Schema, Manifest, reproducible source/Wheel, isolated installation, SBOM and native C ABI verification passed;
- the repository keeps **`main` as the sole authoritative branch**;
- live third-party solver qualification remains **`EXTERNAL_HOLD`** until real binaries, licenses, fixed inputs, hardware fingerprints, reference results and scientific tolerances are supplied.

This distinction is deliberate: software delivery is complete; external scientific execution is evidence-dependent.

## What the repository is

TsaoSciComputation converts a scientific question into a governed calculation program:

```text
question → contract → method/scale route → preflight → bounded execution
         → parse → convergence → numerical/physical validation
         → uncertainty/applicability → accept, reject or hold
```

It is a **control plane and qualification framework**, not a bundled DFT, MD, CFD, FEM or process simulator. Python owns contracts, routing, policy, provenance and acceptance. External numerical engines remain separately installed, licensed and scientifically qualified. Profiled software hotspots may cross a versioned C ABI into C++20/OpenMP or an optional solver-native accelerator path.

### What it does not claim

- no fabricated VASP, Quantum ESPRESSO, Gaussian, GROMACS, OpenFOAM, Aspen or commercial-solver execution;
- no GPU/MPI numerical-equivalence claim without a trusted CPU reference;
- no production speedup claim from repository-local orchestration benchmarks;
- no scientific acceptance from process exit code alone.

## Quick start

```bash
git clone https://github.com/SUNHAOJUN22/TsaoSciComputation.git
cd TsaoSciComputation
python -m pip install -e '.[validation,quality,security]'

python -m tsao_computation route \
  "Plan a DFT-to-MD study of an interface with explicit uncertainty gates"

python -m tsao_computation validate-contract \
  templates/calculation-contract.json --strict

python -m tsao_computation probe
python scripts/verify_all.py --profile all
python scripts/verify_native_core.py
```

External execution is intentionally separate:

```bash
python -m tsao_computation probe-solver gromacs \
  --output .tsao-computation/gromacs-capability-evidence.json

python -m tsao_computation plan-acceleration gromacs \
  --solver-evidence .tsao-computation/gromacs-capability-evidence.json \
  --require-solver-evidence
```

A complete fingerprint can reach `version-probed-unqualified`; it still does not prove numerical correctness, convergence, license availability or accelerator equivalence.

<!-- SUPER_SKILL_ORCHESTRATION:START -->
## Capability and execution model

The repository exposes **164 capabilities**, **23 computation methods**, **9 invocation types**, **7 trusted local functions**, **27 external adapters**, **20 workflows**, **13 acceleration strategies** and a **9-stage orchestration plan**.

| Invocation mode | Default behavior |
|---|---|
| Registered trusted local function | Execute only after payload validation and request/result hashing |
| External solver or adapter | Probe and build a command plan; execution requires separate authorization |
| Python module, CLI, API, container, scheduler or Skill | Produce a declarative handoff until runtime, identity and evidence conditions are satisfied |

Execution is fail-closed. Relative executables and inputs are resolved from normalized `CommandPlan.cwd`. Bare command names are resolved once against a sanitized immutable `PATH`, converted to absolute paths, hashed and rebound immediately before launch. The authorized normalized working directory is the directory actually passed to the process runner.
<!-- SUPER_SKILL_ORCHESTRATION:END -->

## Architecture at a glance

<table>
<tr>
<td width="50%"><img src="assets/visuals/agent-orchestration.svg" alt="Governed scientific agent orchestration" width="100%"></td>
<td width="50%"><img src="assets/visuals/capability-landscape.svg" alt="Contract, capability, workflow and evidence landscape" width="100%"></td>
</tr>
<tr>
<td align="center"><strong>Governed scientific agent</strong></td>
<td align="center"><strong>Contract-based capability system</strong></td>
</tr>
</table>

### Control plane, native plane and external engines

| Layer | Responsibility | Acceptance boundary |
|---|---|---|
| Python control plane | contracts, routing, evidence, provenance, policy, parsers, UQ and decisions | deterministic repository qualification |
| Native interoperability plane | C++20/OpenMP discovery and measured kernels through a versioned C ABI | ABI, build, CTest and equivalence gates |
| External solver plane | DFT/MD/CFD/FEM/process execution | real installation, license, fixed input, reference and tolerance evidence |

## Mathematical operating model

The mathematics below describes the repository's actual control logic. It is not decoration and does not substitute for a solver's governing equations.

### 1. Calculation contract as a constrained state

A governed calculation can be represented as

$$
\mathcal{C}=(Q,M,D,R,E,V,U,A),
$$

where $Q$ is the scientific question, $M$ the selected method, $D$ the declared data and inputs, $R$ the resource request, $E$ the execution evidence, $V$ the validation specification, $U$ the uncertainty model and $A$ the acceptance authority. A route is admissible only if the required predicates are satisfied:

$$
\operatorname{admit}(\mathcal{C})=
\mathbf{1}_{\text{schema}}
\mathbf{1}_{\text{identity}}
\mathbf{1}_{\text{inputs}}
\mathbf{1}_{\text{resources}}
\mathbf{1}_{\text{policy}}.
$$

One failed predicate yields zero admission; missing evidence is not treated as success.

### 2. Reproducible identity binding

The execution bundle is bound by a canonical digest:

$$
H_{\text{bundle}}=
\operatorname{SHA256}(B_{\text{solver}}\parallel B_{\text{inputs}}
\parallel B_{\text{env}}\parallel B_{\text{contract}}
\parallel B_{\text{reference}}).
$$

Changing the executable, input bytes, normalized environment, contract or reference evidence changes the bundle identity. Authorization for one identity cannot silently authorize another.

### 3. Convergence and stopping rules

A generic iterative convergence condition is

$$
\lVert x_{k+1}-x_k\rVert
\leq \varepsilon_{\mathrm{abs}}
+\varepsilon_{\mathrm{rel}}\lVert x_k\rVert.
$$

TsaoSciComputation keeps convergence distinct from process completion:

```text
completed ≠ parsed ≠ converged ≠ validated ≠ accepted
```

A zero exit code can establish only process completion. Convergence requires an explicit observable, norm and tolerance.

### 4. Numerical equivalence

For a candidate backend and trusted reference,

$$
\delta_{\mathrm{rel}}=
\frac{|y_{\mathrm{candidate}}-y_{\mathrm{reference}}|}
{\max(|y_{\mathrm{reference}}|,\epsilon)}.
$$

Backend equivalence is accepted only when all governed observables satisfy their declared limits:

$$
\max_j \delta_{\mathrm{rel},j}\leq \tau_{\mathrm{eq}}.
$$

This is why the qualification order is fixed:

$$
\text{Identity}\rightarrow
\text{CPU correctness}\rightarrow
\text{GPU/MPI equivalence}\rightarrow
\text{performance qualification}.
$$

### 5. Conservation and physical residuals

For a steady balance,

$$
R_{\mathrm{cons}}=
\left|\sum_i F_i^{\mathrm{in}}
-\sum_j F_j^{\mathrm{out}}
+S\right|,
$$

where $S$ is a declared generation or consumption term. Acceptance requires

$$
R_{\mathrm{cons}}\leq \tau_{\mathrm{cons}}.
$$

The internal reference suite applies analytical, conservation and invariant checks to heat transfer, fluid flow, reaction engineering, molecular dynamics, statistical mechanics, electrostatics and multiphysics fixtures.

### 6. Uncertainty propagation and applicability

For $y=f(x_1,\ldots,x_n)$ with independent input uncertainties,

$$
u_y^2\approx
\sum_i\left(\frac{\partial f}{\partial x_i}\right)^2u_{x_i}^2.
$$

A result is not accepted solely because $u_y$ is small. The applicability predicate must also hold:

$$
A_{\mathrm{domain}}=
\mathbf{1}(x\in\Omega_{\mathrm{validated}})
\mathbf{1}(\text{model assumptions hold}).
$$

### 7. Resource broker admission

For license, binary, hardware, inputs and policy predicates,

$$
A_{\mathrm{resource}}=
\mathbf{1}(L)\mathbf{1}(B)\mathbf{1}(H)
\mathbf{1}(I)\mathbf{1}(P).
$$

For a host capacity vector $c=(c_{\mathrm{CPU}},c_{\mathrm{GPU}},c_{\mathrm{license}})$ and plan claims $r_p$, concurrent plans are feasible only if

$$
\sum_{p\in\mathcal{P}_{\mathrm{active}}}r_p\preceq c.
$$

The broker rejects CPU oversubscription, exclusive-GPU collisions, inconsistent CUDA/HIP/ROCR visibility and license-token over-allocation.

## Qualification and delivery diagrams

The following AI-assisted information designs are deterministic, repository-owned SVG sources. They explain software logic and do not depict fabricated solver output.

<img src="assets/visuals/uncertainty-sensitivity.svg" alt="Correctness-first external execution qualification ladder" width="100%">
<img src="assets/visuals/acceleration-opportunity-pipeline.svg" alt="Fail-closed solver evidence state machine" width="100%">
<img src="assets/visuals/hpc-execution-provenance.svg" alt="Resource broker admission barriers and escalation" width="100%">
<img src="assets/visuals/process-optimization-uq.svg" alt="Reproducible build, evidence and delivery feedback loop" width="100%">

<!-- V13_VISUAL_SYSTEM:START -->
The repository contains **43 self-contained SVGs** using **Scientific Research Console V13**. The root READMEs showcase **12 representative diagrams**; the complete searchable inventory is in [`assets/visuals/README.md`](assets/visuals/README.md), with design and trust rules in [`assets/visuals/DESIGN_SYSTEM.md`](assets/visuals/DESIGN_SYSTEM.md).
<!-- V13_VISUAL_SYSTEM:END -->

## Usage strategies

### Strategy A — scientific planning without solver access

Use `route`, contract validation and capability/workflow inspection to design a defensible calculation program. Keep the result as a plan or `EXTERNAL_HOLD`; do not invent runtime evidence.

### Strategy B — onboarding an external solver

Prepare a minimum evidence package:

```text
qualification-bundle/
├── solver-identity.json        # path, size, SHA-256, version output
├── environment.json            # OS, runtime, libraries, scheduler, devices
├── inputs/                     # fixed canonical inputs
├── references/                 # trusted CPU or analytical references
├── tolerances.json             # observable-specific numerical limits
├── license-evidence.json       # availability and authorization boundary
└── provenance.json             # bundle hash and review authority
```

Then qualify identity, correctness, equivalence and performance in that order.

### Strategy C — edge deployment

- pre-package registries, Schemas, templates and visual/documentation assets;
- use CPU-only mode unless the edge accelerator is explicitly fingerprinted;
- cap workers and memory; prefer local deterministic functions and declarative handoffs;
- transfer only hash-bound evidence bundles to a larger solver host.

### Strategy D — shared HPC deployment

- map immutable plan claims to scheduler CPU/GPU/license requests;
- separate scratch, checkpoint and final evidence directories;
- bind scheduler metadata, executable identity and environment to provenance;
- retry only classified transient failures; never reinterpret non-convergence as infrastructure failure.

### Strategy E — acceleration work

1. inventory the code and profile a real workload;
2. distinguish orchestration overhead from numerical-kernel cost;
3. prefer solver-native parallelism and libraries before custom kernels;
4. establish CPU correctness and deterministic references;
5. prove GPU/MPI equivalence using declared observables and tolerances;
6. measure performance on the same qualified problem and report uncertainty.

### Strategy F — acceptance and audit

Treat every claim as a tuple

$$
\text{claim}=(\text{observable},\text{reference},\text{tolerance},
\text{evidence},\text{authority}).
$$

If any element is absent, downgrade the claim or keep it on hold.

## Multiscale scientific visual map

<img src="assets/visuals/quantum-to-md.svg" alt="Electronic-structure to molecular-dynamics handoff" width="100%">
<img src="assets/visuals/reaction-kinetics-network.svg" alt="Reaction pathways, kinetic evidence and reactor handoff" width="100%">
<img src="assets/visuals/polymer-process.svg" alt="Polymer multiscale transfer from molecular architecture to processing" width="100%">
<img src="assets/visuals/continuum-multiphysics.svg" alt="Continuum multiphysics coupling" width="100%">

## Acceleration and native interoperability

Python remains the control plane. A hotspot should move to C++/OpenMP/CUDA only when profiling demonstrates material value and the boundary can be tested independently.

<img src="assets/visuals/hpc-failure-recovery.svg" alt="HPC checkpointing and bounded recovery" width="100%">

```bash
python scripts/build_acceleration_audits.py
python -m tsao_computation audit-acceleration \
  --root . --scope production --limit 50 --min-score 40 \
  --output reports/ACCELERATION_OPPORTUNITIES_PRODUCTION_V4.json
python -m tsao_computation profile-performance \
  --workload routing-hot --workload acceleration-plan \
  --repeats 7 --warmups 1 \
  --output .tsao-computation/performance-profile.json
```

<!-- ACCELERATION_AUDIT_SUMMARY:START -->
The governed audit inventories **170 Python files** and **3 native-language files**. Production and full-tree reports remain source-hash-bound and `unprofiled` until runtime evidence exists; neither report claims external-solver or GPU speedup.
<!-- ACCELERATION_AUDIT_SUMMARY:END -->

Architecture, CUDA-X selection rules and C++ migration gates: [`docs/accelerated-native-backend.md`](docs/accelerated-native-backend.md). Native verification: `python scripts/verify_native_core.py`.

## Verification and acceptance evidence

```bash
python -m pip install -e '.[validation,quality,security]'
python scripts/verify_all.py --profile all
python scripts/verify_native_core.py
python scripts/verify_all.py --profile benchmark
```

`all` covers quality, linting, formatting, typing, security, tests, coverage, controlled mutation, scientific reference fixtures, Schema/registry checks, generated-file consistency, reproducible source/Wheel builds, isolated installation, SBOMs, checksums and release manifests. `benchmark` reports environment-dependent orchestration telemetry and is not external solver performance evidence.

<!-- CURRENT_MAIN_VERIFICATION:START -->
### Current deliverable baseline

| Qualification item | Result |
|---|---:|
| Version | 3.0.4 |
| Capabilities / adapters / workflows | 164 / 27 / 20 |
| Tests | 845 passed, 0 failed |
| Total coverage | 95.25% (required: 95.00%) |
| Ruff / Mypy / Bandit | PASS / 105 source files / PASS |
| Controlled mutation probes | 64/64 killed |
| Scientific reference benchmarks | 8/8 passed |
| Repository security findings | 0 |
| Source archives / Wheel | reproducible / byte-identical + isolated install |
| C++20 C ABI / CTest / Python bridge | PASS / 1 of 1 / PASS |
| Scientific visual assets | 43 self-contained SVGs / 12 featured |
| Remote branches | `main` only |

The qualification boundary covers repository software, deterministic fixtures and native interoperability. External solver correctness, licenses, accelerator equivalence and production performance remain `EXTERNAL_HOLD` until real evidence is supplied.
<!-- CURRENT_MAIN_VERIFICATION:END -->

## Trust boundaries

| State | Meaning |
|---|---|
| `candidate-only` | registry candidate; no executable detected |
| `detected-incomplete` | executable detected but required evidence is incomplete |
| `fingerprinted-unqualified` | exact binary identity recorded; no numerical qualification |
| `version-probed-unqualified` | bounded version output recorded; still scientifically unqualified |
| `evidence-bound-unqualified` | evidence is bound into a plan; correctness/equivalence still pending |
| `EXTERNAL_HOLD` | a required external fact or artifact is missing |

## Platform and repository policy

- Windows is a core supported workflow; Linux is CI-validated.
- `main` is the sole authoritative remote branch.
- No external solver, commercial license or private dataset is bundled.
- Releases include reproducible artifacts, SPDX/CycloneDX SBOMs, SHA-256 checksums and provenance.

## License and citation

MIT licensed. Citation metadata is in [`CITATION.cff`](CITATION.cff); third-party boundaries are documented in [`THIRD_PARTY.md`](THIRD_PARTY.md).
