# Experiment scale and budget gate

Status: planning ranges only. The final sample size requires pilot estimates,
budget, agent access, and mentor review.

## Run-count scenarios

The full design has four placement conditions. A run is one clean task-condition-
agent-repetition cell.

| Stage | Tasks | Agents | Repeats | Total runs | Purpose |
|---|---:|---:|---:|---:|---|
| Infrastructure pilots | 3-5 | 1 | 1 | 12-20 | Find harness, timeout, oracle, and cost failures; never confirmatory |
| Narrow short paper | 12 | 2 | 3 | 288 | Minimum current target if task diversity and budget are credible |
| Better task coverage | 16 | 2 | 3 | 384 | More CWE/task coverage and moderately tighter estimates |
| Broad short paper | 24 | 2 | 3 | 576 | Stronger coverage but likely incompatible with the first deadline/budget |

At a hypothetical mean cost of `C` per run, reserve at least `1.25 * runs * C`
to cover retries that are demonstrably infrastructure failures. Do not rerun
ordinary model failures merely to improve outcomes. At a mean token use of `T`,
the corresponding token budget is `runs * T`, plus the same operational reserve.

## Why three repeats

Agent outputs are stochastic even when exposed temperature is zero. Three repeats
do not eliminate uncertainty, but they allow the study to observe within-cell
variation and match the repeated design used by the closest 2026 context-delivery
study. Repetitions are clustered within tasks and must not be treated as fully
independent tasks.

## Precision warning

Pooling two agents gives 72 observations per condition in the 12-task design,
96 in the 16-task design, and 144 in the 24-task design. A simple binomial 95%
interval around a 50% rate has approximate half-widths of 11.5, 10.0, and 8.2
percentage points respectively. These are optimistic because task and repeated-run
clustering reduce effective information. The study should therefore emphasize
paired task-level effects and intervals, not a bare leaderboard percentage.

## Freeze procedure

1. Select 3-5 non-confirmatory pilot tasks that will not enter the main set.
2. Measure per-run tokens, cost, wall time, timeout frequency, and outcome rates.
3. Estimate task/repeat clustering and simulate power for the preregistered
   placement effects and interaction.
4. Declare the smallest effect of practical interest before inspecting main-task
   condition results.
5. Choose the largest balanced design affordable with a 25% infrastructure
   reserve.
6. Freeze task IDs, exclusions, agents, versions, models, reasoning settings,
   timeouts, repetitions, condition hashes, and the analysis commit.
7. Randomize run order in task blocks and execute without outcome-dependent
   stopping.

## Current hard gate

`configs/agents.json` intentionally contains null model and reasoning fields and
has status `draft-not-frozen`. The experimental runner refuses to execute in this
state. The candidate must supply a maximum budget and available agent accounts;
an experienced reviewer should approve the final scale before the configuration
is changed to `frozen`.

