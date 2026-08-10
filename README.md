# Secure Instruction Placement for AI Coding Agents

[![Tests](https://github.com/prathamesh-git9/secure-instruction-placement/actions/workflows/tests.yml/badge.svg)](https://github.com/prathamesh-git9/secure-instruction-placement/actions/workflows/tests.yml)

An open, reproducible research artifact for studying whether the **location** of an identical secure-coding instruction changes the security and functional correctness of AI coding-agent outputs.

## Status

**Research in progress.** The protocol, schemas, audit tools, experiment runner, and unit tests are public. Confirmatory agent runs have not yet been completed, so this repository claims no experimental effect and is not a published or accepted paper.

Two public non-confirmatory pilots now exist. The first [four-condition infrastructure pilot](results/pilot_2026-08-10_deserialization_pyyaml/README.md) uses a read-only output adapter. The second [three-task writable-agent pilot](results/pilot_2026-08-10_writable_three_task/README.md) contains 12 direct file-editing runs with generated sources, records, hashes, and executable outcomes. The artifact currently has 34 unit tests plus a two-version CI matrix.

## Design

The study uses a 2 x 2 factorial design:

| Condition | Task instruction | Repository instruction |
|---|---:|---:|
| `control` | absent | absent |
| `task_only` | present | absent |
| `repository_only` | absent | present |
| `task_and_repository` | present | present |

The security sentence is held constant. The planned primary outcome is joint functional-and-security success under executable tests. Secondary outcomes include separate functional and security success, agent/infrastructure failures, elapsed time, and resource use.

## Why this repository exists

The artifact makes research decisions inspectable before results exist. It records:

- the exact security wording and placement conditions;
- task, source, licence, and verifier contracts;
- benchmark seed and generation-contract audits;
- a fail-closed agent runner with immutable raw records;
- analysis code for rates and Wilson intervals;
- unit tests and continuous integration.

## Repository layout

```text
configs/       condition and draft agent configurations
docs/          protocol, literature map, and publication plan
examples/      non-confirmatory example task
schemas/       task and run-record JSON schemas
scripts/       audit, materialisation, execution, and analysis tools
tests/         standard-library unit tests
```

Third-party benchmark source and private/raw run data are intentionally not committed.

## Run the checks

Requires Python 3.11 or later and no third-party Python packages for the unit tests.

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/validate_dataset.py examples
python scripts/validate_task_subset.py configs/task_subset.json
```

The agent runner refuses to execute while `configs/agents.json` is marked `draft-not-frozen`. This prevents accidental paid or non-reproducible runs. The separate `configs/agents.pilot.json` is frozen only for explicitly labelled non-confirmatory pilots; invoke the runner with `--pilot-only` so those records cannot be presented as confirmatory evidence.

For environments that prohibit nested agents from writing, the pilot-only `--allow-output-extraction` adapter can verify the final fenced code block. The runner refuses this adapter unless `--pilot-only` is also present. Results from that transport do not support confirmatory claims about a file-editing coding agent.

The writable pilot configuration uses Codex automatic review in a fresh, disposable workspace. The runner permits this mode only when it is explicitly declared and rejects any dangerous sandbox-bypass argument. Automatic review and an explicit `--sandbox` flag cannot be combined by the CLI, so the configuration records the effective approval mode instead.

## Reproducibility policy

- Freeze task inclusion, exclusions, model, agent version, reasoning setting, conditions, repetitions, and analysis before confirmatory runs.
- Preserve raw JSONL output and configuration/content hashes.
- Never silently repair a benchmark after inspecting confirmatory outputs.
- Report null findings, infrastructure failures, exclusions, and security-correctness trade-offs.
- Treat supplied-source pilots as engineering checks, never experimental results.

The current audited-draft subset contains 11 included tasks across six weakness families and two predeclared exclusions. See `configs/task_subset.json`. It is not confirmatory-frozen yet.

## Research integrity

See [AI_USE.md](AI_USE.md). AI tools assisted with implementation and drafting. They are not authors. The human researcher must understand, verify, and take responsibility for any released result or manuscript.

An [independent methods review is publicly requested](docs/INDEPENDENT_REVIEW_REQUEST.md) before confirmatory execution.

The [confirmatory analysis plan](docs/CONFIRMATORY_ANALYSIS_PLAN.md) locks three pilot tasks as development data and protects eight untouched tasks as a holdout. A 96-run-per-agent randomized schedule and task-clustered factorial analysis implementation are committed, but execution remains gated on review, exact agent selection, and a budget ceiling.

`configs/design_draft.sha256` binds the current task subset, development/holdout split, conditions, design, schedule, and analysis implementation into one reviewable draft snapshot.

## Licence and citation

Original code and documentation in this repository are released under the [MIT License](LICENSE). Third-party benchmarks retain their own licences and are not redistributed here. Citation metadata is available in [CITATION.cff](CITATION.cff).
