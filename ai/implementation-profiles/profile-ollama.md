Created: 2026 February 18

# Implementation Profile: OLLama

---

## Table of Contents

- [Overview](<#overview>)
- [Placeholder Mappings](<#placeholder mappings>)
- [Strategic Domain](<#strategic domain>)
- [Tactical Domain](<#tactical domain>)
- [Tool-Calling Behaviour](<#tool-calling behaviour>)
- [Autonomous Execution Loop](<#autonomous execution loop>)
- [Model Selection](<#model selection>)
- [Project Setup](<#project setup>)
- [Version History](<#version history>)

---

## Overview

This profile maps governance abstract placeholders to OLLama-based local model tooling via Goose.

| Concern | Implementation |
|---|---|
| Strategic Domain | Claude Desktop (preferred) |
| Tactical Domain | OLLama model via Goose |
| AEL mechanism | Goose / Ralph Loop |

[Return to Table of Contents](<#table of contents>)

---

## Placeholder Mappings

| Placeholder | Resolved Value |
|---|---|
| `<tactical_config>/` | `~/.config/goose/` |
| `<skills_dir>/` | `recipes/` (within `~/.config/goose/` or `.goose/`) |
| `<tactical_context>` | `.goosehints` or `AGENTS.md` |
| Local context file | Not applicable (`.goosehints` is already project-scoped) |

Context file priority order (Goose): `AGENTS.md` → `.goosehints` → `~/.config/goose/.goosehints`. Override via `CONTEXT_FILE_NAMES` environment variable.

[Return to Table of Contents](<#table of contents>)

---

## Strategic Domain

**Preferred implementation:** Claude Desktop

Any frontier model with sufficient reasoning capability may substitute. The Strategic Domain role requires: planning, governance interpretation, design creation, prompt authoring, and validation.

[Return to Table of Contents](<#table of contents>)

---

## Tactical Domain

**Implementation:** OLLama model via Goose

Configuration directory: `~/.config/goose/`

Project recipes: `.goose/recipes/`

Context file: `.goosehints` or `AGENTS.md` at project root.

**Prerequisites:**
- OLLama installed and running: `ollama serve`
- Goose installed: per [Goose documentation](https://block.github.io/goose/)
- Selected model pulled: `ollama pull <model-name>`

**Goose provider configuration** (`~/.config/goose/config.yaml`):
```yaml
GOOSE_PROVIDER: ollama
GOOSE_MODEL: <model-name>
OLLAMA_HOST: http://localhost:11434
```

**Tool-calling requirement:** Goose requires tool-calling capability for developer workflows. Verified compatible models include: `qwen2.5-coder`, `codestral`, `devstral`, `llama3.3`, `hermes3`.

[Return to Table of Contents](<#table of contents>)

---

## Tool-Calling Behaviour

OLLama models exhibit inconsistent autonomous tool invocation. The following patterns are documented from observed operation with `devstral:24b-small-2505-q8_0` via Goose.

**Observed issue:** When instructed to use a specific MCP tool (e.g., `mcp-grep__grep`), the model may respond with a hallucinated text answer rather than invoking the tool. On explicit re-instruction, the tool call succeeds. This is a model behaviour characteristic, not an infrastructure failure.

**Mitigation — imperative phrasing:**

Use direct, unambiguous imperatives in recipe instructions and prompts. Avoid indirect phrasing.

| Avoid | Prefer |
|---|---|
| `You can use the grep tool to search` | `Use the mcp-grep__grep tool to search` |
| `Search for X in the directory` | `Call mcp-grep__grep with pattern X and path Y` |
| `Check if the file exists` | `Run: ls -la .goose/ralph/task.md` |

**Mitigation — explicit tool reference in prompts:**

Name the tool explicitly in the prompt step. Example recipe prompt step:

```yaml
prompt: |
  Step 1: Read the task file.
  Run: cat .goose/ralph/task.md
  
  Step 2: Search for acceptance criteria.
  Use the mcp-grep__grep tool: pattern="acceptance", path=".goose/ralph/task.md"
```

**Mitigation — model selection:**

Devstral (`devstral:24b-small-2505-q8_0`) is preferred over Codestral for review and any task requiring tool invocation. Codestral does not support tool calling.

**Known model tags (current installation):**

| Model | Full Tag | Tool-Calling |
|---|---|---|
| devstral | `devstral:24b-small-2505-q8_0` | Yes |
| codestral | `codestral:22b-v0.1-q8_0` | No |

Always use the full model tag in `config.yaml` and `profiles.yaml`. Short tags (e.g., `devstral:24b`) may not resolve correctly.

[Return to Table of Contents](<#table of contents>)

---

## Autonomous Execution Loop

**Implementation:** Goose / Ralph Loop

State directory: `.goose/ralph/` (ephemeral, per-task)

**Prerequisites:**
- Goose installed
- Ralph Loop recipe: `~/.config/goose/recipes/ralph-loop.sh`

**Invocation with explicit model selection:**
```bash
RALPH_WORKER_PROVIDER="ollama" RALPH_WORKER_MODEL="codestral" \
RALPH_REVIEWER_PROVIDER="ollama" RALPH_REVIEWER_MODEL="devstral" \
~/.config/goose/recipes/ralph-loop.sh ./workspace/prompt/prompt-<uuid>-<n>.md
```

[Return to Table of Contents](<#table of contents>)

---

## Model Selection

Recommended model pairs for worker/reviewer pattern:

| Role | Recommended Model | Notes |
|---|---|---|
| Worker | `codestral` | Strong code generation |
| Reviewer | `devstral` | Strong code review |
| General | `qwen2.5-coder` | Good all-round alternative |

Model availability and capability varies. Verify tool-calling support before use.

[Return to Table of Contents](<#table of contents>)

---

## Project Setup

**.gitignore additions:**
```
# OLLama profile - Tactical Domain
.goosehints.local
.goose/ralph/
```

**Directory structure additions (within `<project name>/`):**
```
├── .goose/
│   └── recipes/
├── .goosehints          # or AGENTS.md
```

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-02-18 | Initial document |
| 1.1 | 2026-02-18 | Added Tool-Calling Behaviour section: observed devstral tool invocation issue, imperative phrasing mitigation, explicit tool reference patterns, known model tags |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
