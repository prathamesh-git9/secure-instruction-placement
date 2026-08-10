# Secure Instruction Placement for AI Coding Agents

[![Tests](https://github.com/prathamesh-git9/secure-instruction-placement/actions/workflows/tests.yml/badge.svg)](https://github.com/prathamesh-git9/secure-instruction-placement/actions/workflows/tests.yml)

An open, reproducible research artifact for studying whether the **location** of an identical secure-coding instruction changes the security and functional correctness of AI coding-agent outputs.

## Status

**Research in progress.** The protocol, schemas, audit tools, experiment runner, and unit tests are public. Confirmatory agent runs have not yet been completed, so this repository claims no experimental effect and is not a published or accepted paper.

The first [four-condition infrastructure pilot](results/pilot_2026-08-10_deserialization_pyyaml/README.md) is public with generated sources, run records, hashes, and executable test outcomes. It is explicitly non-confirmatory and uses a read-only output adapter.

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
```

The agent runner refuses to execute while `configs/agents.json` is marked `draft-not-frozen`. This prevents accidental paid or non-reproducible runs. The separate `configs/agents.pilot.json` is frozen only for explicitly labelled non-confirmatory pilots; invoke the runner with `--pilot-only` so those records cannot be presented as confirmatory evidence.

For environments that prohibit nested agents from writing, the pilot-only `--allow-output-extraction` adapter can verify the final fenced code block. The runner refuses this adapter unless `--pilot-only` is also present. Results from that transport do not support confirmatory claims about a file-editing coding agent.

## Reproducibility policy

- Freeze task inclusion, exclusions, model, agent version, reasoning setting, conditions, repetitions, and analysis before confirmatory runs.
- Preserve raw JSONL output and configuration/content hashes.
- Never silently repair a benchmark after inspecting confirmatory outputs.
- Report null findings, infrastructure failures, exclusions, and security-correctness trade-offs.
- Treat supplied-source pilots as engineering checks, never experimental results.

## Research integrity

See [AI_USE.md](AI_USE.md). AI tools assisted with implementation and drafting. They are not authors. The human researcher must understand, verify, and take responsibility for any released result or manuscript.

## Licence and citation

Original code and documentation in this repository are released under the [MIT License](LICENSE). Third-party benchmarks retain their own licences and are not redistributed here. Citation metadata is available in [CITATION.cff](CITATION.cff).
