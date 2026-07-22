---
name: finite-element
description: Finite-element analysis workflow with explicit contracts, convergence, physical validation, uncertainty, and acceptance gates.
---

# Finite-element analysis

Route a scientific request to `finite-element` only when its scale, observables, boundary conditions, and evidence requirements are explicit. A completed process is not automatically converged, validated, or accepted.

Required gates: contract, preflight, completion, convergence, physical_validation, uncertainty, acceptance.
