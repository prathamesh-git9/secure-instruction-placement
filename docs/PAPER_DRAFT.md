# Where Should Secure-Coding Instructions Live?

## Replicating and Extending a Security Reminder Across Task and Repository Contexts

**Status:** Internal methods draft. Not a publication, submission, preprint, or completed study. Results and author details intentionally absent.

## Abstract

AI coding agents receive instructions through both immediate task prompts and persistent repository context. Prior work has evaluated task-level security reminders, but the effect of instruction placement requires controlled replication. We design a 2 x 2 experiment that holds secure-coding wording constant while placing it in the task, repository guidance, both, or neither. We evaluate generated changes using executable functional and security tests and record failures and resource use. **Results are pending; no abstract claim should be added until the confirmatory analysis is frozen, executed, and independently checked.** The intended contribution is evidence about instruction placement and its security-correctness trade-offs, together with a reproducible evaluation artifact and documented benchmark audit.

## 1. Introduction

AI coding agents can inspect repositories, modify files, and run tools, but functionally plausible changes may introduce exploitable weaknesses. Security guidance is often added to a task prompt or a persistent repository instruction file. These locations differ in proximity, persistence, and competition with other context. Without a controlled comparison, it is unclear whether they have equivalent effects.

Existing secure-code-generation studies establish that prompting and feedback can affect security, while recent agent studies show that repository context shapes behaviour. This study asks a narrower question: when the exact security sentence is held constant, does its location affect executable security and correctness?

We make no claim that instruction placement alone solves secure code generation. We instead conduct an independent replication of a published security reminder and extend it with a controlled repository-context factor. The study is designed to report null, negative, and heterogeneous effects as first-class outcomes.

The planned contributions are:

1. a 2 x 2 comparison of task-level and repository-level secure-coding guidance;
2. executable functional and security evaluation with predeclared exclusions;
3. analysis of security-correctness trade-offs, failures, and resource use; and
4. a reproducible artifact with a versioned benchmark audit.

## 2. Background and related work

Cover four groups of evidence without overstating novelty:

1. secure code generation and vulnerability benchmarks;
2. generic and scenario-specific security prompting;
3. coding-agent repository context and instruction files;
4. benchmark and oracle reliability.

Use the verified literature matrix and version-specific citations. Distinguish the earlier SecureAgentBench version containing the reminder experiment from later versions in which the paper title and reported experiment changed.

## 3. Research questions

- **RQ1:** How does security-instruction placement affect executable security success?
- **RQ2:** How does placement affect functional correctness and the joint secure-and-functional outcome?
- **RQ3:** How do effects vary by weakness family and task?
- **RQ4:** How does placement affect failures, tokens, cost, and elapsed time?

## 4. Method

### 4.1 Design

Describe the four conditions, identical clause, context-file mechanism, task materialisation, randomisation or pairing, repetitions, and contamination controls.

### 4.2 Agents and models

Insert only after freeze: provider, exact model identifier, agent version, reasoning setting, date window, command contract, and any provider-side reproducibility limitation.

### 4.3 Tasks and benchmark audit

Report the pinned benchmark release and commit, licence, inclusion criteria, excluded tasks, oracle audit, generation-contract audit, and any disclosed overlay. Do not quietly repair tasks after seeing model outputs.

### 4.4 Outcomes

Define functional success, security success, joint success, infrastructure failure, resource-limit failure, cost, tokens, and time. State how errors and missing observations are handled.

### 4.5 Analysis

Predeclare primary contrasts, effect measures, uncertainty intervals, task/model structure, multiplicity handling, sensitivity analyses, and exploratory subgroup labels. Avoid treating repeated runs on the same task as independent tasks.

### 4.6 Reproducibility and integrity

Describe raw JSONL capture, prompt/configuration hashes, immutable run directories, environment versions, exclusion log, artifact licence, and AI-use disclosure.

## 5. Results

Do not draft numerical prose until the locked analysis produces verified tables. Include:

- task and run flow diagram;
- outcome counts by condition;
- primary effect estimates with uncertainty;
- joint security/correctness trade-off;
- weakness-family heterogeneity;
- failure and resource-use analysis;
- sensitivity analysis.

## 6. Discussion

Interpret effect size and uncertainty, not only significance. Separate observed evidence from mechanism speculation. Discuss implications for repository guidance, benchmark designers, agent developers, and researchers. Explain what a null result would rule out and what it would not.

## 7. Threats to validity

- benchmark representativeness and oracle errors;
- model and agent version drift;
- non-independence across tasks and repeated trials;
- context-window and instruction-order effects;
- security-test false positives and false negatives;
- limited languages, weaknesses, models, and repository realism;
- researcher decisions made after pilot observations.

## 8. Conclusion

Write only after results are final. Restate the bounded finding, uncertainty, and artifact availability; do not generalise beyond the evaluated models, tasks, and context mechanism.

## Author and submission declarations

- Author list and contribution statement: pending real contributions.
- Conflicts of interest: pending.
- Funding: pending.
- Data/code availability: pending release review.
- AI-assistance disclosure: follow the selected venue's current policy.
- Ethics/security disclosure: pending final artifact review.

