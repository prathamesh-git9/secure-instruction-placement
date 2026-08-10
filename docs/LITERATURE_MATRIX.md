# Literature matrix

This matrix is paired with [NOVELTY_SEARCH_LOG.md](NOVELTY_SEARCH_LOG.md), which records the 10 August 2026 structured rapid review. A final systematic update and citation-chain search remain required before submission.

## Closest work

| Work | Main contribution | Implication for Project 01 |
|---|---|---|
| [Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://arxiv.org/abs/2602.11988) (2026) | Tests generated and developer-written context files on real tasks; reports increased exploration/cost and often lower success, while agents tend to respect instructions. | Closest independent-variable precedent. We must isolate security-specific policy content and executable security outcomes, not repeat general task-success evaluation. |
| [Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250) (2026) | Controlled two-agent ablation on real repositories; finds no measurable correctness benefit in its setting. | Motivates equivalence/uncertainty analysis and agent-specific effects. Very recent; must be deeply compared before novelty is claimed. |
| [Agent READMEs: An Empirical Study of Context Files for Agentic Coding](https://arxiv.org/abs/2511.12884) (2025) | Analyses 2,303 context files; security instructions occur in only 14.5% and are identified as an important non-functional gap. | Strong motivation for studying security guidance, but it characterises files rather than testing causal security outcomes. |
| [On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents](https://arxiv.org/abs/2601.20404) (2026) | Compares 124 pull-request runs with and without `AGENTS.md`, focusing on runtime and token use. | Motivates explicit cost outcomes; it does not hold file content constant or evaluate security. |
| [BaxBench](https://arxiv.org/abs/2502.11844) (2025) | 392 backend tasks with functional tests and executable exploits; compares no reminder, generic security reminders, and vulnerability-specific prompt information. | Directly defeats a broad novelty claim about security prompting. Our wording-controlled placement comparison must add knowledge beyond this task-prompt experiment. |
| [SecRepoBench](https://arxiv.org/abs/2504.21205) (2025) | Repository-level secure code-generation benchmark. | Benchmark/design reference; our contribution cannot merely be another secure-code benchmark. |
| [SecCodeBench repository](https://github.com/alibaba/sec-code-bench) / technical report (2026) | 98 cases, 22 CWEs, five languages, generation and repair modes; Apache-2.0. | Candidate licensed task source and baseline, subject to leakage and adaptation review. |
| [SecureAgentBench v1](https://arxiv.org/abs/2509.22097v1) (2025) | 105 realistic repository tasks; appends one generic sentence to the task prompt for one agent/model setting and reports no increase in secure resolutions plus more resource-limit failures. | Closest direct baseline. Reuse its sentence for an independent replication and extend it to repository placement, two agents, repeated runs, and cost measurement. The experiment was removed from the current v5/SecureVibeBench manuscript, so cite the version explicitly. |
| [Poster: Rethinking Security in LLM Code Generation through Real-World Risk Scenarios](https://arxiv.org/abs/2607.23088) (2026) | 2,700 cases across three risk scenarios and nine languages; scenario-specific security-aware task prompting reduces vulnerability labels substantially. | Reinforces that task prompting itself is not a gap. Uses model completions and static analysis/expert labels rather than repository context, coding agents, or joint executable oracles. |
| [SoK: AI Secure Code Generation](https://arxiv.org/abs/2606.25195) (2026) | Organises secure generation around principle understanding, actuation, and their gap; reports saturation of generic reminders. | Motivates measuring whether an instruction is acted on rather than merely repeated, and preserving executable joint outcomes. |
| [Prompting Techniques for Secure Code Generation: A Systematic Investigation](https://arxiv.org/abs/2407.07064) (2024/2025) | Evaluates a range of prompt strategies for secure function-level code generation. | Shows that another generic prompting comparison would be incremental; persistent instruction placement is the differentiator. |
| [CVE-Bench](https://aclanthology.org/2025.naacl-long.212/) (NAACL 2025) | Executable environment for repairing real CVEs. | Strong standard for real-world repair and execution-based evaluation; likely too expensive as the sole first-project dataset. |
| [Security and Quality in LLM-Generated Code](https://arxiv.org/abs/2502.01853) (2025) | Multi-language, multi-model analysis across 200 tasks. | Shows the space is already crowded; novelty must come from the controlled instruction intervention. |
| [Purple Llama CyberSecEval](https://arxiv.org/abs/2312.04724) (2023) | Unified benchmark including insecure code generation and cyber-assistance risk. | Established metric/tool reference; current repository status and licence must be checked before reuse. |
| [Exploring Prompt Patterns for Effective Vulnerability Repair](https://www.nist.gov/publications/exploring-prompt-patterns-effective-vulnerability-repair-real-world-code-large-language) (2025) | Studies prompt patterns for LLM vulnerability repair. | We must distinguish persistent repository policy from task-level repair prompts and avoid trivial prompt-engineering claims. |
| [Red-Teaming Coding Agents from a Tool-Invocation Perspective](https://conf.researchr.org/details/issta-2026/issta-2026-research-papers/176/Red-Teaming-Coding-Agents-from-a-Tool-Invocation-Perspective-An-Empirical-Security-A) (ISSTA 2026) | Evaluates tool-invocation attacks against six coding agents. | Defines adjacent agent-security risk but a different threat model from insecure generated patches. |

## Fast-moving adjacent evidence

- Large-scale agent-authored pull-request work now covers modification patterns, failures, human review, security-related PRs, and test coverage. A generic “AI versus human PR quality” study is no longer a clean gap.
- Context-file effectiveness changed from “unexplored” to contested during 2026. The paper must cite the newest work and narrowly specify the intervention.
- Static analyzers alone are noisy security oracles. The design should prioritise executable exploit tests plus functional tests and use SAST as triangulation.

## Defensible provisional gap statement

> Existing research separately evaluates general repository context files and secure-coding reminders appended to immediate task prompts. We independently replicate a published generic-reminder condition, then hold that sentence constant while estimating whether task placement, persistent repository placement, or both changes executable security, correctness, and cost outcomes for coding agents.

Do not put “first” in the paper until a systematic search immediately before submission supports that wording.
