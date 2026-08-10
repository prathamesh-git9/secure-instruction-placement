# Development security-oracle mutation audit

This directory contains machine-readable evidence for the 2026-08-10 development-only mutation audit.

- `audit.json` is the canonical manifest with scope, hashes, test counts, and outcome flags.
- `audit.csv` is the same per-mutant evidence in tabular form.
- [`configs/development_oracle_mutations.json`](../../configs/development_oracle_mutations.json) defines the deterministic mutations.
- [`scripts/audit_development_oracles.py`](../../scripts/audit_development_oracles.py) reconstructs, executes, and validates the audit.

All three mutants preserved the original functional behavior and were rejected by their security suites. The protected eight-task holdout was not read or executed. See the [method and limitations](../../docs/DEVELOPMENT_ORACLE_MUTATION_AUDIT.md).
