# README visual assets

This directory contains original, repository-local SVG illustrations created for the TsaoSciComputation documentation.

## Design and trust policy

- Every asset is self-contained SVG with an accessible `<title>` and `<desc>`.
- Assets use no external fonts, scripts, raster images, network resources, or tracking elements.
- Diagrams explain architecture and scientific boundaries; they are not solver screenshots or claims of live third-party execution.
- Text labels are intentionally concise and must remain consistent with the registries, workflows, and machine-readable verification evidence.
- README references use relative paths so visuals remain available in repository clones and source archives.

## Asset set

- `hero-multiscale.svg` — electron-to-process architecture
- `agent-orchestration.svg` — governed AI scientific agent
- `capability-landscape.svg` — capability, workflow, validation, and governance layers
- `quantum-to-md.svg` — electronic-structure to molecular-dynamics handoff
- `electronic-structure-landscape.svg` — DFT density, self-consistency, energy and observable gates
- `polymer-process.svg` — polymer-to-process multiscale transfer
- `continuum-multiphysics.svg` — CFD, FEM, heat, mechanics and field coupling
- `process-optimization-uq.svg` — flowsheet optimization, sensitivity, UQ and reviewed decisions
- `engine-ecosystem.svg` — external solver adapter ecosystem
- `evidence-loop.svg` — fail-closed scientific acceptance loop
- `confidence-ladder.svg` — C0–C5 confidence model
- `digital-thread.svg` — reproducibility and supply-chain evidence

Run `python -m pytest tests/test_readme_visuals.py -q` to validate the asset inventory and README references.
