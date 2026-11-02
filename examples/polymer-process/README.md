# DWSIM/IDAES polymer-process workflow

This is a preparation and validation example for `process-simulation`. It does not claim that any external solver, license, database, cluster, or production calculation is available or has run.

## Registered methods and study details

The `methods` field uses registered orchestration identifiers: `process-simulation`, `nonlinear-optimization`. These select method families; they do not implement or execute the detailed engine operations.

The original study-specific method descriptions are retained in `model_object.method_details`:

- DWSIM or IDAES/Pyomo
- property-package qualification
- steady-state optimization

## Use

```bash
python -m tsao_computation validate-contract examples/polymer-process/contract.json --strict
python -m tsao_computation plan examples/polymer-process/contract.json --strict
python -m tsao_computation probe
```

Replace every project-specific value with traceable data, complete the environment preflight, and retain native evidence. Input generation or normal program exit is not scientific acceptance.
