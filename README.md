# LLM Governance and Orchestration

## Purpose

This repository provides a model-agnostic governance framework for AI-assisted software development. The framework coordinates requirements capture, design, and code generation through structured protocols and human-in-the-loop approval gates.

## Overview

`ai/governance.md` defines a dual-domain architecture separating strategic coordination (Strategic Domain) from tactical implementation (Tactical Domain). Communication between domains uses MCP filesystem-based message passing. The framework is independent of any specific AI model or toolchain; implementation profiles map abstract framework concepts to concrete tooling.

## Key Characteristics

- **Protocol-driven workflow**: Eleven protocols (P00-P10) govern requirements capture, project initialization, three-tier design hierarchy, change management, issue resolution, traceability, testing, quality assurance, audit, prompting, and requirements management
- **Model-agnostic architecture**: Strategic and Tactical Domain roles fulfilled by any capable LLM; implementation profiles provided for Claude Code and OLLama via Goose
- **Human approval gates**: Explicit human authorization required before requirements baseline, design tier transitions, code generation, and baseline modifications
- **Three-tier design decomposition**: Master (system) → Domain (functional) → Component (implementation) with validation gates between tiers
- **Autonomous Execution Loop (AEL)**: Optional worker/reviewer cycle via Goose/Ralph Loop for iterative code generation within governed boundaries
- **UUID-based document coupling**: 8-character hex identifiers with iteration synchronization through debug cycles
- **Document lifecycle management**: Active/closed states with immutable archival and closure criteria across all document classes
- **Bidirectional traceability**: Requirements ↔ Design ↔ Code ↔ Test linkages
- **Template-based documentation**: Seven YAML templates (T01-T07) for all document classes

## Getting Started

### Prerequisites

- MCP servers: Filesystem and mcp-grep configured in your Strategic Domain tool
- Git and GitHub Desktop (or equivalent)
- Tooling per selected implementation profile (see `ai/implementation-profiles/`)

### Initialization

1. Copy `ai/` to the root of your project repository
2. Select an implementation profile from `ai/implementation-profiles/` and follow its setup instructions
3. Ask your Strategic Domain model to read `ai/governance.md` and initialize the project per P01 (§1.2 Project Initialization)
4. Begin with P00 (Governance) and follow the workflow flowchart in section 2.0

### Implementation Profiles

| Profile | Tactical Domain | AEL |
|---|---|---|
| `profile-claude.md` | Claude Code | Goose / Ralph Loop |
| `profile-ollama.md` | OLLama via Goose | Goose / Ralph Loop |

## Important Notice

This framework is experimental, serving as a learning exercise in prompt engineering, AI-assisted development workflows, and protocol-driven project management. **Actual fitness for purpose is not guaranteed.**

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
