# Security

Report vulnerabilities privately to the repository owner. Do not include secrets or proprietary datasets in issues.

Security invariants:

- paths are confined to declared roots;
- subprocesses use argv lists, `shell=False`, bounded timeouts, and controlled environments;
- archives must be hash-bound and safely extracted;
- unknown output is not promoted to convergence or validation;
- credentials, licenses, and proprietary solver files are never bundled;
- automation does not write to DCS/SIS or bypass safety systems.
