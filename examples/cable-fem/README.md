# Cable thermo-electro-mechanical finite-element workflow

This is a preparation and validation example for `multiphysics`. It does not claim that any external solver, license, database, cluster, or production calculation is available or has run.

## Registered methods and study details

The `methods` field uses registered orchestration identifiers: `finite-element`, `multiphysics`. These select method families; they do not implement or execute the detailed engine operations.

The original study-specific method descriptions are retained in `model_object.method_details`:

- finite element
- electro-thermal coupling
- thermo-mechanical coupling

## Use

```bash
python -m tsao_computation validate-contract examples/cable-fem/contract.json --strict
python -m tsao_computation plan examples/cable-fem/contract.json --strict
python -m tsao_computation probe
```

Replace every project-specific value with traceable data, complete the environment preflight, and retain native evidence. Input generation or normal program exit is not scientific acceptance.
