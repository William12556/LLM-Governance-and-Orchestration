# LLM Governance and Orchestration

## Purpose

This repository provides a governance framework for AI-assisted software development using Claude Desktop and Claude Code. The framework coordinates planning, design, and code generation through structured protocols and human-in-the-loop approval gates.

## Overview

`governance.md` establishes a dual-domain architecture separating strategic coordination (Claude Desktop/Domain 1) from tactical implementation (Claude Code/Domain 2). The framework uses MCP filesystem-based communication, YAML templates, and systematic documentation to maintain human authority while leveraging AI capabilities for code generation.

## Key Characteristics

- **Protocol-driven workflow**: Eleven protocols (P00-P10) govern requirements capture, project initialization, three-tier design hierarchy, change management, issue resolution, traceability, testing, quality assurance, audit, prompting, and requirements management
- **Human approval gates**: Strategic checkpoints requiring explicit human authorization before proceeding through requirements baseline, design tiers, code generation, or baseline modifications
- **Three-tier design decomposition**: Master (system) → Domain (functional) → Component (implementation) with validation gates between tiers
- **UUID-based document coupling**: 8-character hex identifiers with iteration-based synchronization through debug cycles
- **Document lifecycle management**: Active/closed states with immutable archival and closure criteria for issues, changes, prompts, tests, results, and audits
- **Bidirectional traceability**: Requirements ↔ Design ↔ Code ↔ Test linkages enabling forward and backward navigation
- **Template-based documentation**: Seven YAML templates (T01-T07) optimized for token efficiency and LLM communication

## Getting Started

Copy `ai/governance.md` folder to the root of your github project. the Review `ai/governance.md` for complete framework specification. Begin with Protocol P00 (Governance) and follow the workflow flowchart in section 2.0.

## Important Notice

This framework is experimental in nature, serving as a learning exercise in prompt engineering, AI-assisted development workflows, protocol-driven project management, and cross-platform embedded systems development. **Actual fitness for purpose is not guaranteed.**

This project represents a first attempt at AI-supported software development using Claude Desktop and Claude Code from anthropic.com. The objective is to establish a sort of AI orchestration framework to guide software development. A kind of AI wrangler if you will.

It is loosely based on https://governance.md but directed towards AI.

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
