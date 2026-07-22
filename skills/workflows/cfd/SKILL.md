---
name: cfd
description: Computational fluid dynamics workflow with explicit contracts, convergence, physical validation, uncertainty, and acceptance gates.
---

# Computational fluid dynamics

Route a scientific request to `cfd` only when its scale, observables, boundary conditions, and evidence requirements are explicit. A completed process is not automatically converged, validated, or accepted.

Required gates: contract, preflight, completion, convergence, physical_validation, uncertainty, acceptance.
