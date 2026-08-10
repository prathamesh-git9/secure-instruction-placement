# Confirmatory holdout and analysis plan

**Status:** Draft awaiting independent human review, exact agent selection, and a budget ceiling. No holdout model run is permitted while the design remains in this state.

## Leakage control

The three tasks used in live pilots are permanently designated development tasks. Their outputs may inform infrastructure fixes but cannot contribute to confirmatory effect estimates. Two tasks that failed benchmark eligibility checks remain excluded. The remaining eight tasks were locked as an untouched holdout before any project-model output was generated for them.

The holdout spans five weakness families: SSRF, SSTI, deserialization, SQL injection, and command injection.

## Design

- Eight holdout tasks
- Four instruction-placement conditions
- Three repetitions per task-condition cell
- Ninety-six planned runs per frozen agent configuration
- Three complete repetition blocks, independently shuffled using the committed seed
- One fresh workspace and immutable record directory per run

The committed schedule is operational metadata, not permission to execute. The design validator refuses a frozen state until independent review, exact agents, and a positive budget ceiling are recorded.

## Primary outcome and estimand

The primary outcome is joint success: the run completed and the generated implementation passed both the functional and security suites.

The primary estimand is the task-instruction factorial main effect on joint pass rate. Every condition rate is first averaged across repetitions within a task. Effects are then averaged across tasks, so repeated runs are not treated as independent tasks.

Secondary estimands are the repository-instruction main effect, task-by-repository interaction, and each reminder condition versus control.

## Uncertainty

- 95% task-cluster bootstrap percentile intervals with 10,000 resamples
- Exact task-level sign-flip tests
- Per-task effects retained in machine-readable output
- No claim based only on a pooled run-level percentage

With only eight holdout tasks, inference will be imprecise. Effect size and uncertainty take priority over a significance threshold. Findings cannot be generalized beyond the frozen tasks, model/agent versions, and context mechanism.

## Failure handling

Timeouts, agent errors, missing target files, and verifier errors do not silently disappear. Under the primary estimand they fail joint success, while failure categories are also reported separately. Any infrastructure rerun needs a predeclared rule and a new immutable run identifier.

## Integrity rule

Pilot observations must not become new confirmatory hypotheses. Any post-result subgroup, failure-mechanism, or source-code analysis is exploratory and labelled accordingly. The design, schedule, agent configuration, budget, and analysis code must receive a frozen Git tag before the first holdout model run.

