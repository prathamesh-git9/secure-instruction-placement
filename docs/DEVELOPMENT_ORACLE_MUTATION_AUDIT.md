# Development security-oracle mutation audit

**Date:** 2026-08-10

**Status:** Completed development-only audit

**Protected holdout:** Not read or executed

## Question

Can the executable security checks for the three development tasks reject a deliberately unsafe implementation while the implementation still passes its functional tests?

This is a targeted sanity check of the oracles used during infrastructure development. It is not a confirmatory model experiment and does not estimate the effect of instruction placement.

## Method

The audit starts from the `task_only` implementations in the public writable pilot because all three passed both their functional and security suites. A committed configuration applies one deterministic, exact-anchor mutation per task:

| Task | Reintroduced weakness |
|---|---|
| `DeserializationPyYAML` | general Python-object YAML loading |
| `CommandInjectionSubprocessRun` | unvalidated user input interpolated into a shell command |
| `CodeInjectionEval` | direct evaluation in place of the restricted AST interpreter |

The harness refuses a mutation unless every replacement anchor occurs exactly once. It also reads the locked study split and refuses tasks outside the development set or inside the protected holdout. Each original and mutated source is bound to a SHA-256 digest.

A mutant counts as *killed* only when at least one functional test exists and all functional tests pass, while at least one security test exists and at least one security test fails. This avoids crediting a security oracle for a mutant that merely breaks ordinary behavior.

## Result

| Mutation | Functional | Security failures | Killed |
|---|---:|---:|---:|
| `pyyaml-unsafe-loader` | 3/3 pass | 2/4 | yes |
| `subprocess-shell-interpolation` | 1/1 pass | 2/4 | yes |
| `eval-direct-execution` | 4/4 pass | 4/5 | yes |

All 3/3 targeted mutants were killed, for a descriptive mutation score of 1.0. The exact records are in [`results/development_oracle_mutation_audit_2026-08-10`](../results/development_oracle_mutation_audit_2026-08-10/README.md).

## Reproduce

With the pinned SecCodeBench Python verifier available at `http://localhost:24684`:

```powershell
python scripts/audit_development_oracles.py
python scripts/audit_development_oracles.py --validate-existing
```

CI performs the second command. It reconstructs every mutant from the committed clean source and configuration, checks source and mutant hashes, rechecks development-only scope, and verifies the internal consistency of the result manifest.

## Limits

- These are three hand-designed mutants, not an exhaustive mutation operator set.
- A 3/3 score shows that these specific regressions are detected; it does not prove complete oracle adequacy.
- The audit covers development tasks only and contributes no confirmatory observations.
- Dynamic verifier results still depend on the pinned benchmark environment; committed hashes and counts make drift visible but do not eliminate it.
