# AEL — Autonomous Execution Loop

---

## Table of Contents

- [Overview](<#overview>)
- [Structure](<#structure>)
- [Requirements](<#requirements>)
- [Installation](<#installation>)
- [Configuration](<#configuration>)
- [Usage](<#usage>)
- [Recipes](<#recipes>)
- [Testing](<#testing>)
- [Version History](<#version history>)

---

## Overview

The AEL orchestrator is a standalone Python tool loop implementing the Ralph Loop pattern. It connects directly to MCP servers, sends tool definitions to an oMLX inference endpoint, parses model tool calls in both OpenAI and Mistral plain-text formats, dispatches tools, injects results into message history, and iterates until the model produces a response containing no tool calls.

This component replaces Goose as the Autonomous Execution Loop (AEL) for the oMLX/Devstral stack. It addresses the tool dispatch failure present in oMLX and other inference servers by owning the full tool loop externally.

[Return to Table of Contents](<#table of contents>)

---

## Structure

```
ael/
├── config.yaml          # Inference endpoint, MCP server definitions, loop control
├── requirements.txt     # Python dependencies
├── recipes/
│   ├── ralph-work.yaml  # Worker role system prompt
│   └── ralph-review.yaml # Reviewer role system prompt
└── src/
    ├── orchestrator.py  # Main loop and CLI entry point (--mode worker|reviewer|loop)
    ├── mcp_client.py    # MCP stdio connection and tool dispatch
    └── parser.py        # Mistral [TOOL_CALLS] plain-text parser
```

[Return to Table of Contents](<#table of contents>)

---

## Requirements

- Python 3.11+
- oMLX running on `http://127.0.0.1:8000`
- MCP servers configured in `config.yaml`

[Return to Table of Contents](<#table of contents>)

---

## Installation

Install dependencies into the project virtual environment:

```bash
pip install -r ai/ael/requirements.txt
```

[Return to Table of Contents](<#table of contents>)

---

## Configuration

Edit `ai/ael/config.yaml`:

```yaml
omlx:
  base_url: "http://127.0.0.1:8000/v1"
  api_key: "local"
  default_model: "<model-name>"

mcp_servers:
  filesystem:
    command: "/usr/local/bin/npx"
    args:
      - "-y"
      - "@j0hanz/filesystem-mcp@latest"
      - "<allowed-path>"
    env:
      PATH: "/opt/homebrew/opt/node@24/bin:/usr/local/bin:/usr/bin:/bin"

loop:
  max_iterations: 10
  state_dir: ".ael/ralph"
```

[Return to Table of Contents](<#table of contents>)

---

## Usage

```bash
# Single worker pass
python ai/ael/src/orchestrator.py --mode worker --task workspace/prompt/prompt-abc123.md

# Single reviewer pass
python ai/ael/src/orchestrator.py --mode reviewer --task workspace/prompt/prompt-abc123.md

# Full Ralph Loop (worker + reviewer cycle)
python ai/ael/src/orchestrator.py --mode loop --task workspace/prompt/prompt-abc123.md
python ai/ael/src/orchestrator.py --mode loop --task "implement the login module"
```

| Flag | Purpose |
|---|---|
| `--mode` | `worker` \| `reviewer` \| `loop` (default: `loop`) |
| `--task` | Task string or path to task file |
| `--model` | Model for all phases (overrides config default) |
| `--worker-model` | Model for work phase only (loop mode) |
| `--reviewer-model` | Model for review phase only (loop mode) |
| `--max-iterations` | Iteration limit override |
| `--config` | Path to config.yaml |

[Return to Table of Contents](<#table of contents>)

---

## Recipes

Recipes are YAML files providing role-specific system prompts. The `instructions` field is injected as the system prompt for each inference call.

| Recipe | Role | Purpose |
|---|---|---|
| `ralph-work.yaml` | Worker | Makes incremental progress on the task |
| `ralph-review.yaml` | Reviewer | Evaluates work and outputs `SHIP` or `REVISE` |

State files are written to `.ael/ralph/` in the project root during loop execution. This directory is ephemeral and excluded from git.

[Return to Table of Contents](<#table of contents>)

---

## Testing

Tests are in `ael/tests/`. Two files:

| File | Coverage | External deps |
|---|---|---|
| `test_parser.py` | Layer 1 — Mistral parser unit tests | None |
| `test_integration.py` | Layers 2–4 — oMLX smoke, tool dispatch, full loop | oMLX + MCP |

Integration tests skip automatically if oMLX is not reachable on `127.0.0.1:8000`.

### Prerequisites

```bash
python3.11 -m pip install pytest
# Dependencies already installed via requirements.txt
```

### Run all tests

```bash
cd /Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration
python3.11 -m pytest framework/ai/ael/tests/ -v
```

### Run unit tests only (no oMLX required)

```bash
python3.11 -m pytest framework/ai/ael/tests/test_parser.py -v
```

### Run integration tests only

```bash
python3.11 -m pytest framework/ai/ael/tests/test_integration.py -v
```

### Run a specific test

```bash
python3.11 -m pytest framework/ai/ael/tests/test_integration.py::test_full_loop_creates_file -v
```

### Expected output (oMLX running)

```
tests/test_parser.py                          PASSED  [unit]
tests/test_integration.py::test_omlx_models_endpoint          PASSED
tests/test_integration.py::test_simple_completion_no_tools    PASSED
tests/test_integration.py::test_completion_writes_work_summary PASSED
tests/test_integration.py::test_mcp_connect_and_catalogue     PASSED
tests/test_integration.py::test_tool_dispatch_filesystem_list PASSED
tests/test_integration.py::test_worker_uses_tool              PASSED
tests/test_integration.py::test_full_loop_creates_file        PASSED
```

### Expected output (oMLX not running)

```
tests/test_parser.py                          PASSED  [unit]
tests/test_integration.py                     SKIPPED [oMLX not reachable]
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-11 | Initial implementation; replaces Goose AEL; direct MCP + oMLX tool loop |
| 1.1 | 2026-03-11 | Merged ralph-loop.sh into orchestrator.py; added --mode worker\|reviewer\|loop; removed shell script |
| 1.2 | 2026-03-11 | Added tests/ directory: test_parser.py (unit), test_integration.py (Layers 2–4); added Testing section |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
