Created: 2026 March 06

# Implementation Profile: Apple Silicon + MLX

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

This profile maps governance abstract placeholders to Apple Silicon MLX-based local model tooling via Goose. It requires Apple M-series hardware.

| Concern | Implementation |
|---|---|
| Strategic Domain | Claude Desktop (preferred) |
| Tactical Domain | Devstral Q8 via oMLX + Goose |
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

**Implementation:** Devstral Small 2507 Q8 via oMLX and Goose

**Hardware requirement:** Apple M-series chip; 24 GB unified memory minimum (Q8 quantisation).

**Inference server:**

```bash
omlx serve --model-dir /path/to/ai-models
```

The server exposes an OpenAI-compatible endpoint at `http://localhost:8000/v1`.

Note: The HuggingFace repository name contains a typo (`Devstral-Samll-2507-8bit`). Use the exact string shown above.

**Model download:**

```python
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="mlx-community/Devstral-Samll-2507-8bit",
    local_dir="/path/to/ai-models/mlx-community/devstral-q8"
)
```

Use Python 3.11+. The `huggingface-cli` may be unreliable on some macOS configurations.

**Goose provider configuration** (`~/.config/goose/profiles.yaml`):

```yaml
mlx:
  provider: openai
  model: devstral-small
  base_url: http://localhost:8000/v1
  api_key: local
```

Or via `~/.config/goose/config.yaml`:

```yaml
GOOSE_PROVIDER: openai
GOOSE_MODEL: devstral-small
OPENAI_BASE_URL: http://localhost:8000/v1
OPENAI_API_KEY: local
```

The Goose provider name for this configuration is `MLX OpenAI` (custom OpenAI-compatible provider).

[Return to Table of Contents](<#table of contents>)

---

## Tool-Calling Behaviour

Devstral Small 2507 Q8 via oMLX supports tool calling. Observed behaviour is consistent with the OLLama profile: autonomous tool invocation may require explicit imperative phrasing in recipe prompts.

**Mitigation — imperative phrasing:**

| Avoid | Prefer |
|---|---|
| `You can use the grep tool to search` | `Use the mcp-grep__grep tool to search` |
| `Search for X in the directory` | `Call mcp-grep__grep with pattern X and path Y` |

**Mitigation — explicit tool reference in prompts:**

Name the tool explicitly in each recipe prompt step. Refer to the OLLama profile for detailed examples.

[Return to Table of Contents](<#table of contents>)

---

## Autonomous Execution Loop

**Implementation:** Goose / Ralph Loop

State directory: `.goose/ralph/` (ephemeral, per-task)

**Prerequisites:**
- oMLX running on `localhost:8000`
- Goose installed and configured with MLX OpenAI provider
- Ralph Loop recipes: `recipes/ralph-loop.sh`, `recipes/ralph-work.yaml`, `recipes/ralph-review.yaml`

**Invocation:**

```bash
RALPH_WORKER_PROVIDER="openai" RALPH_WORKER_MODEL="devstral-small" \
RALPH_REVIEWER_PROVIDER="openai" RALPH_REVIEWER_MODEL="devstral-small" \
recipes/ralph-loop.sh ./workspace/prompt/prompt-<uuid>-<n>.md
```

Worker and reviewer roles are differentiated by prompt engineering within the same model, not by separate model binaries.

[Return to Table of Contents](<#table of contents>)

---

## Model Selection

| Role | Model | Quantisation | Approx. VRAM |
|---|---|---|---|
| Worker | Devstral Small 2507 | Q8 | ~24 GB |
| Reviewer | Devstral Small 2507 | Q8 | ~24 GB |

BF16 may be used on hardware with 48 GB+ unified memory for higher fidelity.

[Return to Table of Contents](<#table of contents>)

---

## Project Setup

**.gitignore additions:**

```
# MLX profile - Tactical Domain
.goosehints.local
.goose/ralph/
```

**Directory structure additions (within `<project name>/`):**

```
├── .goose/
│   └── recipes/
├── .goosehints          # or AGENTS.md
```

**Setup guide:** See `framework/ai/doc/examples/` and [Apple Silicon + MLX Setup Guide](../../../docs/setup-apple-silicon-mlx.md).

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-06 | Initial document |
| 1.1 | 2026-03-06 | Replaced mlx_lm.server with oMLX as primary inference server; updated port references to 8000 |
| 1.2 | 2026-03-06 | Corrected API key values: oMLX requires authentication for all requests; updated api_key and OPENAI_API_KEY to `local` |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
