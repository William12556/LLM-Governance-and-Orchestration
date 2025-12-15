# LLM Governance and Orchestration

## Purpose

This repository provides a governance framework for AI-assisted software development using Claude Desktop and Claude Code. The framework coordinates planning, design, and code generation through structured protocols and human-in-the-loop approval gates.

## Overview

`governance.md` establishes a dual-domain architecture separating strategic coordination (Claude Desktop/Domain 1) from tactical implementation (Claude Code/Domain 2). The framework uses filesystem-based communication, YAML templates, and systematic documentation to maintain human authority while leveraging AI capabilities for code generation.

## Key Characteristics

- **Protocol-driven workflow**: Nine protocols (P00-P09) govern project initialization, design, change management, issue resolution, testing, quality assurance, and audit
- **Human approval gates**: Strategic checkpoints requiring explicit human authorization before proceeding to code generation or baseline modifications
- **Bidirectional traceability**: Requirements ↔ Design ↔ Code ↔ Test linkages enabling forward and backward navigation
- **Template-based documentation**: Five YAML templates (T01-T05) optimized for token efficiency and LLM communication

## Getting Started

Review `governance.md` for complete framework specification. Begin with Protocol P00 (Governance) and follow the workflow flowchart in section 2.0.

## Important Notice

This framework is experimental in nature, serving as a learning exercise in prompt engineering, AI-assisted development workflows, protocol-driven project management, and cross-platform embedded systems development. **Actual fitness for purpose is not guaranteed.**

This project represents a first attempt at AI-supported software development using Claude Desktop and Claude Code from anthropic.com. The objective is to establish a sort of AI orchestration framework to guide software development. A kind of AI wrangler if you will.

It is loosely based on https://governance.md but directed towards AI.

---

Copyright: Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
