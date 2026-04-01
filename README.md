# LLM Governance and Orchestration

## Purpose

This repository provides a model-agnostic governance framework for AI-assisted software development. The framework coordinates requirements capture, design, and code generation through structured protocols and human-in-the-loop approval gates.

The framework was motivated by a practical observation: language models lose coherence when navigating large, complex projects — a known consequence of context window constraints [1][2]. Structured documentation provides a compact, navigable project representation that mitigates this. The protocol-driven workflow achieves this by decomposing work into discrete, bounded steps — each providing the model with only the structured context relevant to the current task.

## Governance

`ai/governance.md` defines a dual-domain architecture separating strategic coordination (Strategic Domain) from tactical implementation (Tactical Domain). Communication between domains uses MCP filesystem-based message passing. The framework is independent of any specific AI model or toolchain; implementation profiles map abstract framework concepts to concrete tooling.

- **Protocol-driven workflow**: Eleven protocols (P00–P10) govern requirements capture, project initialization, three-tier design hierarchy, change management, issue resolution, traceability, testing, quality assurance, audit, prompting, and requirements management
- **Human approval gates**: Explicit human authorization required before requirements baseline, design tier transitions, code generation, and baseline modifications
- **Three-tier design decomposition**: Master (system) → Domain (functional) → Component (implementation) with validation gates between tiers
- **Model-agnostic architecture**: Strategic and Tactical Domain roles fulfilled by any capable LLM; implementation profiles provided for Apple Silicon MLX (primary) and Claude Code (optional)
- **UUID-based document coupling**: 8-character hex identifiers with iteration synchronization through debug cycles
- **Document lifecycle management**: Active/closed states with immutable archival and closure criteria across all document classes
- **Bidirectional traceability**: Requirements ↔ Design ↔ Code ↔ Test linkages
- **Template-based documentation**: Seven YAML templates (T01–T07) for all document classes

## Orchestration

The Autonomous Execution Loop (AEL) implements the Ralph Loop: a worker/reviewer cycle in which the same model fulfills both roles, differentiated by prompt engineering. The loop runs iteratively until the reviewer emits `SHIP` (task complete) or `BLOCKED` (boundary exceeded). Based on Geoffrey Huntley's Ralph Wiggum techniques.

`orchestrator.py` is the AEL entry point. It connects to configured MCP servers, sends tool definitions to the inference endpoint, dispatches tool calls, injects results, and iterates until no tool calls remain. It supports four execution modes:

| Mode | Description |
|---|---|
| `loop` | Full worker/reviewer Ralph Loop cycle (standard invocation) |
| `worker` | Single work phase pass |
| `reviewer` | Single review phase pass |
| `reset` | Clear state directory after human acceptance |

**Configuration** — `ai/ael/config.yaml`:

| Section | Purpose |
|---|---|
| `omlx` | Inference endpoint URL and default model |
| `mcp_servers` | MCP server command and argument definitions |
| `loop` | `max_iterations` (outer Ralph cycles), `phase_max_iterations` (inner tool-call iterations per phase), MCP error threshold, tool call cap |
| `context` | Model directory path, context window size (or `null` to resolve from model `config.json`), warn/abort budget thresholds |

**State directory** — `.ael/ralph/` (ephemeral, per-task):

| File | Signal |
|---|---|
| `task.md` | Task description loaded from T04 prompt |
| `iteration.txt` | Current Ralph Loop cycle number |
| `work-summary.txt` | Worker phase output |
| `work-complete.txt` | Worker completion signal |
| `review-result.txt` | `SHIP` or `REVISE` decision |
| `review-feedback.txt` | Reviewer notes for next worker iteration |
| `.ralph-complete` | Success marker |
| `RALPH-BLOCKED.md` | Failure details; seeds T03 Issue |

**Invocation** (from project root, after human approval of T04 prompt):

```bash
python ai/ael/src/orchestrator.py --mode loop \
  --task workspace/prompt/prompt-<uuid>-<n>.md
```

## Repository Structure

| Directory                              | Purpose                                                                       |
| -------------------------------------- | ----------------------------------------------------------------------------- |
| `framework/`                           | Canonical framework — governance, templates, profiles, AEL orchestrator       |
| `framework/ai/governance.md`           | Master governance document                                                    |
| `framework/ai/profiles/`               | Implementation profiles (claude-desktop, claude, mlx)                         |
| `framework/ai/templates/`              | Document templates T01–T07                                                    |
| `framework/ai/ael/`                    | Python AEL orchestrator (orchestrator, mcp_client, parser, recipes)           |
| `skel/`                                | Minimal deployable skeleton — copy to initialize a new project                |
| `skel/ai/`                             | Governance, templates, profiles, and recipes for deployed projects            |
| `skel/workspace/`                      | Pre-scaffolded workspace directories (design, prompt, test, trace, etc.)      |
| `skel/src/` `skel/tests/` `skel/docs/` | Standard project directories                                                  |
| `dev/`                                 | Framework development artefacts (requirements, design, issues, changes)       |
| `dev/requirements/`                    | Framework-level requirements documents                                        |
| `dev/design/`                          | Framework-level design documents                                              |
| `docs/`                                | User-facing operational documentation                                         |
| `docs/claude/`                         | Strategic Domain operational documents (instructions, guidelines, context)    |
| `docs/setup-apple-silicon-mlx.md`      | Apple Silicon + MLX inference setup guide                                     |
| `docs/software-testing-guidance.md`    | Software testing reference for framework adopters                             |

## Requirements

### Common

| Item | Requirement |
|---|---|
| Operating system | macOS 14+ (Sonoma) required (Apple Silicon) |
| Python | 3.11+ |
| Git | Any recent version |
| Strategic Domain | Claude Desktop (or equivalent frontier LLM with MCP support) |
| MCP servers | `Filesystem` and `mcp-grep` configured in the Strategic Domain tool |
| Python MCP SDK | `pip install -r ai/ael/requirements.txt` — required for AEL orchestrator |

### Apple Silicon + MLX

Required for the MLX inference backend (Tactical Domain on Apple Silicon).

| Item           | Requirement                                                |
| -------------- | ---------------------------------------------------------- |
| Chip           | Apple M-series (M1 or later)                               |
| Unified memory | 24 GB minimum (Q8); 48 GB+ for BF16                        |
| `mlx_lm`       | 0.21+ — required dependency of oMLX (`pip install mlx_lm`) |
| `omlx`         | Required inference server (`pip install omlx`)             |
| Model          | Devstral Small 2 (2512) Q8                                 |

Devstral Small 2 is the required Tactical Domain model. It is purpose-built for agentic coding and multi-file editing. The AEL parser (`parser.py`) is tuned to Mistral's tool-call format, which Devstral uses natively.

Full setup instructions: [Apple Silicon + MLX Setup Guide](docs/setup-apple-silicon-mlx.md)

---

## Getting Started

### Prerequisites

- MCP servers: Filesystem and mcp-grep configured in your Strategic Domain tool
- Git and GitHub Desktop (or equivalent)
- Tooling per selected implementation profile (see `framework/ai/profiles/`)

### Initialization

1. Copy `skel/` to the desired parent directory and rename it to your project name
2. Select an implementation profile from `skel/ai/profiles/` and follow its setup instructions
3. Ask your Strategic Domain model to read `ai/governance.md` and initialize the project per P01 (§1.2 Project Initialization)
4. Begin with P00 (Governance) and follow the workflow flowchart in section 2.0

### Implementation Profiles

| Profile     | Tactical Domain        | AEL                |
| ----------- | ---------------------- | ------------------ |
| `claude.md` | Claude Code (optional) | Manual — human invokes per task |
| `mlx_devstral_small_2_2512_Q8.md` | MLX + Devstral Small 2 2512 (primary) | AEL / Ralph Loop |

## Important Notice

This framework is experimental, serving as a learning exercise in prompt engineering, AI-assisted development workflows, and protocol-driven project management. **Actual fitness for purpose is not guaranteed.**

---

## References

HUNTLEY, G., 2026. *Everything is a ralph loop* [online]. Available from: https://ghuntley.com/loop/ [Accessed 4 March 2026].

[1] FACTORY.AI, 2025. *The Context Window Problem: Scaling Agents Beyond Token Limits* [online]. Available from: https://factory.ai/news/context-window-problem [Accessed 20 March 2026].

[2] REDIS, 2026. *LLM context windows: what they are & how they work* [online]. Available from: https://redis.io/blog/llm-context-windows/ [Accessed 20 March 2026].

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-04 | Initial README; repository restructured to framework/ and skel/ |
| 1.1 | 2026-03-04 | Added Ralph Loop / Geoffrey Huntley attribution to Overview, AEL description, and References section |
| 1.2 | 2026-03-04 | Renamed ai/implementation-profiles/ → ai/profiles/; renamed profile-*.md files to claude-desktop.md, claude.md, ollama.md |
| 1.3 | 2026-03-05 | Expanded Repository Structure to reflect actual directory contents; removed duplicate Ralph Loop attribution from Overview; added framework/ai/doc/examples/ entry |
| 1.4 | 2026-03-05 | Added Requirements section; created docs/ directory with setup guides for Goose, Apple Silicon + MLX, and OLLama + LM Studio |
| 1.5 | 2026-03-05 | Added omlx as optional Apple Silicon + MLX requirement for TTL-based memory management |
| 1.6 | 2026-03-06 | Added mlx.md to Implementation Profiles table |
| 1.7 | 2026-03-06 | Promoted oMLX to required inference server; updated mlx_lm to dependency role |
| 1.8 | 2026-03-11 | Replaced Goose with Python AEL orchestrator; updated repository structure, requirements, and implementation profiles table |
| 1.9 | 2026-03-11 | Narrowed scope to Apple Silicon + MLX; deprecated Goose, OLLama, and LM Studio docs and profiles; moved to deprecated/ |
| 2.0 | 2026-03-12 | Added Devstral Small 2 (2512) as supported model in Requirements |
| 2.1 | 2026-03-20 | Added motivation paragraph to Purpose; added references [1] and [2] |
| 2.2 | 2026-03-20 | Extended motivation paragraph with workflow rationale |
| 2.3 | 2026-03-26 | Revised Repository Structure: removed stale framework/ai/doc/examples/ and framework/ai/knowledge/ entries; added dev/, dev/requirements/, dev/design/, docs/claude/; updated skel/ description; added docs/ subdirectory entries |
| 2.4 | 2026-03-27 | Replaced Overview and Key Characteristics with Governance and Orchestration sections; Orchestration covers AEL/Ralph Loop, orchestrator.py modes, config.yaml, state directory, and invocation |
| 2.5 | 2026-03-31 | Added Devstral model rationale note to Apple Silicon + MLX Requirements |
| 2.6 | 2026-03-31 | Updated Implementation Profiles table; deprecated mlx_devstral_small_2507_Q8.md; reinstated claude.md as optional Claude Code profile; updated model-agnostic architecture bullet |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
