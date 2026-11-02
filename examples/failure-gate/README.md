# Failure classification, bounded recovery, and human-approval workflow

This is a preparation and validation example for `hpc-execution`. It does not claim that any external solver, license, database, cluster, or production calculation is available or has run.

## Registered methods and study details

The `methods` field uses registered orchestration identifiers: `hpc-execution`. These select method families; they do not implement or execute the detailed engine operations.

The original study-specific method descriptions are retained in `model_object.method_details`:

- deterministic failure classifier
- bounded recovery policy
- human approval gate

## Use

```bash
python -m tsao_computation validate-contract examples/failure-gate/contract.json --strict
python -m tsao_computation plan examples/failure-gate/contract.json --strict
python -m tsao_computation probe
```

Replace every project-specific value with traceable data, complete the environment preflight, and retain native evidence. Input generation or normal program exit is not scientific acceptance.
