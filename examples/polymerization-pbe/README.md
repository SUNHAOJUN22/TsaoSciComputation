# Polymerization microkinetic and population-balance workflow

This is a preparation and validation example for `polymerization`. It does not claim that any external solver, license, database, cluster, or production calculation is available or has run.

## Registered methods and study details

The `methods` field uses registered orchestration identifiers: `numerical-integration`, `process-simulation`. These select method families; they do not implement or execute the detailed engine operations.

The original study-specific method descriptions are retained in `model_object.method_details`:

- Eyring or fitted rate constants
- ODE microkinetics
- population balance or moments

## Use

```bash
python -m tsao_computation validate-contract examples/polymerization-pbe/contract.json --strict
python -m tsao_computation plan examples/polymerization-pbe/contract.json --strict
python -m tsao_computation probe
```

Replace every project-specific value with traceable data, complete the environment preflight, and retain native evidence. Input generation or normal program exit is not scientific acceptance.
