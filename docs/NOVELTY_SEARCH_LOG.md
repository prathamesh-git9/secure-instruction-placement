# Project 01 structured rapid novelty review

Search date: 10 August 2026  
Coverage window: January 2023 to 10 August 2026  
Status: reproducible rapid review, not a completed systematic literature review

## Review question

Has an empirical study held secure-coding guidance constant while comparing its
placement in an immediate coding task, a persistent repository context file, and
both locations, using executable functional and security outcomes from coding
agents?

## Inclusion criteria

- empirical work on AI code generation or coding agents;
- at least one of: secure-code prompting, repository context files, instruction
  delivery, executable security evaluation, or secure-and-correct outcomes;
- English-language paper, preprint, or proceedings record with enough method
  detail to distinguish the intervention and outcome;
- published or publicly posted by the search date.

## Exclusion criteria

- coding-agent security where the outcome is prompt injection, tool compromise,
  or autonomous exploitation rather than security of generated code;
- repository retrieval or code completion without an instruction intervention;
- opinion/vendor material without an empirical method;
- duplicate or superseded versions, except where a removed experiment is
  directly relevant and the version is identified explicitly.

## Search interfaces and exact queries

The web search interface was queried with:

1. `site:arxiv.org coding agents repository context file security instructions AGENTS.md CLAUDE.md secure code`
2. `site:arxiv.org AI coding agents secure code generation prompt security reminder repository-level instructions`
3. `site:dl.acm.org coding agent context files security instructions generated code empirical study`
4. `site:semanticscholar.org coding agents repository instructions security code generation context file`
5. `site:arxiv.org "security instructions" "coding agents"`
6. `site:arxiv.org "secure-coding" "AGENTS.md" OR "CLAUDE.md"`
7. `site:arxiv.org "instruction placement" code generation security prompt`
8. `site:arxiv.org repository context files coding agents security outcomes`

Crossref's API was queried for works from 2023 onward with:

- `AGENTS.md coding agents`
- `secure code generation prompting`
- `repository context coding agents`

DBLP's publication API was queried with:

- `AGENTS.md coding agents`
- `secure code generation prompt`
- `coding agent context files`

The arXiv export API was also attempted for `AGENTS.md`, `secure code
generation`, `security instructions AND coding agents`, and `repository context
AND coding agents`. These calls returned HTTP 429 or timed out, so arXiv records
were instead verified from direct abstract/PDF pages. This limitation prevents a
PRISMA-style claim about exhaustive database counts.

For the closest papers, PDFs were downloaded from arXiv and searched in full
text for `AGENTS.md`, `CLAUDE.md`, repository-level instruction, security-aware
prompt, security instruction, generic security, system prompt, and user prompt.

## Decisive studies

| Study | Intervention | Outcome | Relation to proposed study |
|---|---|---|---|
| [BaxBench](https://arxiv.org/abs/2502.11844) | No reminder vs generic task-prompt reminder vs vulnerability-specific task-prompt reminder | Functional and executable security tests | Establishes that a broad "do reminders help?" claim is not novel. Does not compare task versus repository placement. |
| [SecureAgentBench v1](https://arxiv.org/abs/2509.22097v1) | One generic sentence appended to the task prompt, evaluated with SWE-agent + DeepSeek-V3.1 | Functional tests, PoC and SAST; secure count unchanged and resource-limit failures increased | Closest direct baseline. The proposed study can be an independent multi-agent replication plus a placement extension. The experiment is not present in the current v5/SecureVibeBench manuscript, so the version must be cited explicitly. |
| [Rethinking Security in LLM Code Generation](https://arxiv.org/abs/2607.23088) | Scenario-specific security-aware task-prompt transformations | Static analysis and expert-reviewed security labels across 2,700 cases | Shows substantial gains from richer task-prompt guidance, but does not use coding agents, repository context placement, or executable functional/security oracles. |
| [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) | No context vs generated/developer repository context files | Task success and cost | Establishes repository-context effects, but content is general rather than a wording-controlled security policy and security is not the outcome. |
| [Do Context Files Help Coding Agents?](https://arxiv.org/abs/2607.27250) | None vs always-on context vs selectively retrieved context, two agents and three repeats | Gold-test correctness and efficiency | Closest design precedent. It varies delivery strategy and, in part, content corpus; it does not test secure-code policy or executable security outcomes. |
| [On the Impact of AGENTS.md Files](https://arxiv.org/abs/2601.20404) | With vs without root `AGENTS.md` for Codex on 124 pull requests | Runtime and token consumption | Motivates cost measurement but does not assess security or controlled wording. |
| [Agent READMEs](https://arxiv.org/abs/2511.12884) | Observational analysis of 2,303 context files | Content/maintenance taxonomy | Finds security guidance uncommon; motivates the intervention but provides no causal outcome. |
| [Prompting Techniques for Secure Code Generation](https://arxiv.org/abs/2407.07064) | Multiple prompt strategies for function-level generation | Static-analysis security findings | Confirms a mature prompt-engineering literature; does not study persistent repository instructions. |
| [SoK: AI Secure Code Generation](https://arxiv.org/abs/2606.25195) | Principle understanding and security-aware prompting across models/agents | Functional, security, and joint outcomes | Frames a knowledge-to-actuation gap and warns that generic reminders saturate; strengthens the need for mechanism and executable outcomes. |

## Screening notes

- The Crossref query returned several weakly indexed SSRN or non-archival items.
  They were not used to support novelty without corroborating methods/artifacts.
- Work on malicious tools, prompt injection, coding-agent exploitation, and MCP
  attacks was excluded because its dependent variable is agent/system compromise,
  not security of generated code.
- SecureAgentBench changed substantially between arXiv v1 and v5: the title became
  SecureVibeBench and the explicit-reminder experiment disappeared. Results from
  that experiment must be attributed to v1, not silently to the current version.

## Backward and forward citation checks

Backward chains were inspected in the full texts of BaxBench, SecureAgentBench
v1/v5, the three context-file evaluations, the secure-prompting investigation,
the July 2026 risk-scenario poster, and the June 2026 secure-generation SoK. The
security-generation chain recovered LLMSecEval, CodeLMSec, CyberSecEval,
CWEval, SecRepoBench, SecCodeBench, SafeGenBench, SecureAgentBench/SecureVibeBench,
and prompt-strategy work. The context-file chain recovered the observational
Agent READMEs study and the three empirical `AGENTS.md`/context-delivery studies.
No referenced work combined the two chains with the proposed wording-controlled
placement factorial.

Forward chains were attempted through Semantic Scholar and OpenAlex. Semantic
Scholar returned HTTP 429 for the closest records. OpenAlex indexed one citing
work for BaxBench, a general AI-for-software-engineering position paper, and no
citing work for `Evaluating AGENTS.md` at the search date. The newest 2026
preprints were incomplete or absent in OpenAlex. Exact-title web searches were
therefore also used. This is weak evidence for absence, especially for papers
posted in the preceding weeks; forward citation searches must be repeated before
submission.

## Review conclusion

The broad question of whether secure-code prompting helps is already well
studied. Repository context files are also now an active empirical literature.
Within this rapid review, no located paper performs the exact 2 x 2 intervention
of task-prompt placement by persistent repository-context placement while holding
the security sentence constant and measuring executable secure-and-correct
outcomes for coding agents.

The contribution should therefore be described as a **replication and controlled
placement extension**, not as the first study of security prompting. A final
database refresh, repeated forward citation check, and experienced researcher's
review are still required immediately before submission.
