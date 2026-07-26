# README visual assets

This directory contains original, repository-local SVG illustrations created for the TsaoSciComputation documentation.

## Design and trust policy

- Every asset is self-contained SVG with an accessible `<title>` and `<desc>`.
- Assets use no external fonts, scripts, raster images, network resources, event handlers, or tracking elements.
- Diagrams explain architecture and scientific boundaries; they are not solver screenshots or claims of live third-party execution.
- Text labels are intentionally concise and must remain consistent with registries, workflows, and machine-readable evidence.
- README references use relative paths so visuals remain available in repository clones and source archives.

## Asset set

- `hero-multiscale.svg` — electron-to-process architecture
- `agent-orchestration.svg` — governed AI scientific agent
- `capability-landscape.svg` — capability, workflow, validation and governance layers
- `quantum-to-md.svg` — electronic-structure to molecular-dynamics handoff
- `electronic-structure-landscape.svg` — DFT density, self-consistency, energy and observable gates
- `free-energy-sampling.svg` — enhanced sampling, overlap, reconstruction and uncertainty
- `reaction-kinetics-network.svg` — reaction pathways, rate evidence and reactor handoff
- `ml-potential-active-learning.svg` — reference data, uncertainty and active learning
- `polymer-process.svg` — polymer-to-process multiscale transfer
- `mesoscale-phase-field.svg` — coarse-graining, phase evolution and morphology evidence
- `continuum-multiphysics.svg` — CFD, FEM, heat, mechanics and field coupling
- `process-optimization-uq.svg` — flowsheet optimization, sensitivity, UQ and reviewed decisions
- `uncertainty-sensitivity.svg` — uncertainty propagation, sensitivity ranking and decision limits
- `electrochemical-interface.svg` — electrode/electrolyte interfaces, transport and observables
- `spectroscopy-observables.svg` — state models, simulated spectra and evidence-based assignment
- `transport-degradation.svg` — coupled charge, heat, species transport and lifetime evidence
- `inverse-design-loop.svg` — constrained inverse design and multi-objective Pareto validation
- `data-model-governance.svg` — data lineage, model versioning and release governance
- `reactor-safety-control.svg` — reactor digital twin, control and independent protection layers
- `hpc-execution-provenance.svg` — bounded execution, scheduler boundaries and provenance
- `engine-ecosystem.svg` — external solver adapter ecosystem
- `evidence-loop.svg` — fail-closed scientific acceptance loop
- `confidence-ladder.svg` — C0–C5 confidence model
- `digital-thread.svg` — reproducibility and supply-chain evidence
- `periodic-materials-stability.svg` — periodic relaxation, defects, phonons and stability
- `catalysis-microkinetics.svg` — active sites, elementary steps and microkinetic evidence
- `polymerization-population-balance.svg` — chain events, moments, PBEs and molecular distributions
- `extrusion-rheology-window.svg` — constitutive rheology, flow history and processing windows
- `digital-twin-drift.svg` — state estimation, online updates and drift-aware decisions
- `fem-verification-convergence.svg` — weak forms, discretization convergence and balance checks
- `scale-multifidelity-plan.svg` — problem decomposition, scale selection and multi-fidelity planning
- `quantum-chemistry-thermochemistry.svg` — molecular structures, frequencies, energies and thermochemical acceptance
- `molecular-dynamics-transport.svg` — equilibration, production sampling, transport and trajectory convergence
- `polymer-composite-topology.svg` — interfaces, localization, percolation and structure-property evidence
- `flowsheet-convergence-balances.svg` — property packages, recycle convergence and balance closure
- `multiscale-handoff-uncertainty.svg` — cross-scale contracts, uncertainty propagation and applicability

Run `python -m pytest tests/test_readme_visuals.py -q` to validate the asset inventory and bilingual README references.
