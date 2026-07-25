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
- `quantum-to-md.svg` — electronic-structure to molecular-dynamics handoff
- `polymer-process.svg` — polymer-to-process multiscale transfer
- `evidence-loop.svg` — fail-closed scientific acceptance loop
- `confidence-ladder.svg` — C0–C5 confidence model
- `engine-ecosystem.svg` — external solver adapter ecosystem
- `digital-thread.svg` — reproducibility and supply-chain evidence
- `capability-landscape.svg` — capability, workflow, validation, and governance layers

Run `python -m pytest tests/test_readme_visuals.py -q` to validate the asset inventory and README references.
