# LLM Governance and Orchestration

## Purpose

This repository provides a model-agnostic governance framework for AI-assisted software development. The framework coordinates requirements capture, design, and code generation through structured protocols and human-in-the-loop approval gates. 

## Overview

`ai/governance.md` defines a dual-domain architecture separating strategic coordination (Strategic Domain) from tactical implementation (Tactical Domain). Communication between domains uses MCP filesystem-based message passing. The framework is independent of any specific AI model or toolchain; implementation profiles map abstract framework concepts to concrete tooling.

## Key Characteristics

- **Protocol-driven workflow**: Eleven protocols (P00-P10) govern requirements capture, project initialization, three-tier design hierarchy, change management, issue resolution, traceability, testing, quality assurance, audit, prompting, and requirements management
- **Model-agnostic architecture**: Strategic and Tactical Domain roles fulfilled by any capable LLM; implementation profiles provided for Claude Code and Apple Silicon MLX
- **Human approval gates**: Explicit human authorization required before requirements baseline, design tier transitions, code generation, and baseline modifications
- **Three-tier design decomposition**: Master (system) → Domain (functional) → Component (implementation) with validation gates between tiers
- **Autonomous Execution Loop (AEL)**: Optional worker/reviewer cycle via Ralph Loop for iterative code generation within governed boundaries. Based on Geoffrey Huntley's Ralph Wiggum techniques.
- **UUID-based document coupling**: 8-character hex identifiers with iteration synchronization through debug cycles
- **Document lifecycle management**: Active/closed states with immutable archival and closure criteria across all document classes
- **Bidirectional traceability**: Requirements ↔ Design ↔ Code ↔ Test linkages
- **Template-based documentation**: Seven YAML templates (T01-T07) for all document classes

## Repository Structure

| Directory                              | Purpose                                                                       |
| -------------------------------------- | ----------------------------------------------------------------------------- |
| `framework/`                           | Governance framework development (canonical source)                           |
| `framework/ai/governance.md`           | Master governance document                                                    |
| `framework/ai/profiles/`               | Implementation profiles (claude-desktop, claude, mlx)                         |
| `framework/ai/templates/`              | Document templates T01–T07                                                    |
| `framework/ai/knowledge/`              | AI-consumed operational reference documents                                   |
| `framework/ai/ael/`                    | Python AEL orchestrator (orchestrator, mcp_client, parser, recipes)           |
| `framework/ai/doc/examples/`           | Human-facing reference material for framework adopters                        |
| `skel/`                                | Deployable project skeleton — copy to initialize a new project                |
| `skel/ai/`                             | Governance, templates, profiles, knowledge, and recipes for deployed projects |
| `skel/workspace/`                      | Pre-scaffolded workspace directories (design, prompt, test, trace, etc.)      |
| `skel/src/` `skel/tests/` `skel/docs/` | Standard project directories                                                  |

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

| Item | Requirement |
|---|---|
| Chip | Apple M-series (M1 or later) |
| Unified memory | 24 GB minimum (Q8); 48 GB+ for BF16 |
| `mlx_lm` | 0.21+ — required dependency of oMLX (`pip install mlx_lm`) |
| `omlx` | Required inference server (`pip install omlx`) |
| Model | Devstral Small 2507 Q8 or BF16; Devstral Small 2 (2512) Q8 |

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
| `claude.md` | Claude Code + Devstral | AEL / Ralph Loop |
| `mlx.md`    | MLX + Devstral         | AEL / Ralph Loop |

## Important Notice

This framework is experimental, serving as a learning exercise in prompt engineering, AI-assisted development workflows, and protocol-driven project management. **Actual fitness for purpose is not guaranteed.**

---

## References

HUNTLEY, G., 2026. *Everything is a ralph loop* [online]. Available from: https://ghuntley.com/loop/ [Accessed 4 March 2026].

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

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
