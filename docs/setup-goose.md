Created: 2026 March 05

# Goose Setup Guide

---

## Table of Contents

- [Overview](<#overview>)
- [Installation](<#installation>)
- [Provider Configuration](<#provider configuration>)
  - [MLX Backend](<#mlx backend>)
  - [OLLama Backend](<#ollama backend>)
  - [LM Studio Backend](<#lm studio backend>)
- [Ralph Loop Setup](<#ralph loop setup>)
- [Verification](<#verification>)
- [Version History](<#version history>)

---

## Overview

Goose is an open-source AI agent developed by Block. It serves as the Autonomous Execution Loop (AEL) orchestrator — the Tactical Domain shell for the Ralph Loop worker/reviewer cycle.

This guide covers Goose installation and provider configuration for three inference backends: MLX (Apple Silicon), OLLama, and LM Studio.

References:
- Goose documentation: https://block.github.io/goose/
- Ralph Loop concept: HUNTLEY, G., 2026. *Everything is a ralph loop* [online]. https://ghuntley.com/loop/

[Return to Table of Contents](<#table of contents>)

---

## Installation

**Recommended:** install via `pipx` to isolate dependencies.

```bash
pipx install goose-ai
```

Alternative:

```bash
pip install goose-ai
```

Verify:

```bash
goose --version
```

> For platform-specific installation options refer to the [Goose documentation](https://block.github.io/goose/).

[Return to Table of Contents](<#table of contents>)

---

## Provider Configuration

Goose is configured via `~/.config/goose/config.yaml`. The `GOOSE_PROVIDER` and `GOOSE_MODEL` keys set the active provider and model.

Run `goose configure` to set up providers interactively, or edit `config.yaml` directly.

---

### MLX Backend

**Prerequisite:** oMLX running on `localhost:8000`. See [Apple Silicon + MLX Setup](setup-apple-silicon-mlx.md).

In Goose, configure a custom OpenAI-compatible provider named `MLX OpenAI` pointing to `http://localhost:8000/v1`. oMLX requires authentication for all API requests.

Example `config.yaml` fragment:

```yaml
GOOSE_PROVIDER: mlx_openai
GOOSE_MODEL: mlx-community/Devstral-Samll-2507-8bit
OPENAI_API_KEY: local
```

> The provider name `mlx_openai` and its `base_url` must be registered via `goose configure` or the profiles config. Refer to Goose documentation for custom OpenAI-compatible provider registration syntax.

Invoke `goose configure` and select `Add provider` → `OpenAI-compatible` → enter `http://localhost:8000/v1` as the base URL and `local` as the API key (matching the value in `~/.omlx/settings.json`).

The custom provider JSON at `~/.config/goose/custom_providers/custom_mlx_openai.json` must include the `Authorization` header and `requires_auth: true`:

```json
{
  "api_key_env": "OPENAI_API_KEY",
  "headers": {"Authorization": "Bearer local"},
  "requires_auth": true
}
```

Replace `local` with your configured API key if different.

[Return to Table of Contents](<#table of contents>)

---

### OLLama Backend

**Prerequisite:** OLLama installed and running. See [OLLama + LM Studio Setup](setup-ollama-lmstudio.md).

```yaml
GOOSE_PROVIDER: ollama
GOOSE_MODEL: devstral:24b-small-2505-q8_0
OLLAMA_HOST: http://localhost:11434
```

> Always use the full model tag. Short tags (e.g., `devstral:24b`) may not resolve correctly.

[Return to Table of Contents](<#table of contents>)

---

### LM Studio Backend

**Prerequisite:** LM Studio running with server mode enabled. See [OLLama + LM Studio Setup](setup-ollama-lmstudio.md).

LM Studio exposes an OpenAI-compatible API on `localhost:1234` by default.

Configure a custom OpenAI-compatible provider pointing to `http://localhost:1234/v1`.

```yaml
GOOSE_PROVIDER: lmstudio
GOOSE_MODEL: <model-identifier>
```

> The model identifier must match the model name as displayed in the LM Studio interface. Use `lm-studio` as a placeholder API key if the field is required.

[Return to Table of Contents](<#table of contents>)

---

## Ralph Loop Setup

The Ralph Loop recipes must be accessible to Goose. By default the loop script looks for recipes in `~/.config/goose/recipes/`. The `RALPH_RECIPE_DIR` environment variable overrides this path.

Copy the recipes from the framework repository to the Goose recipes directory:

```bash
mkdir -p ~/.config/goose/recipes
cp framework/ai/goose/recipes/ralph-loop.sh ~/.config/goose/recipes/
cp framework/ai/goose/recipes/ralph-work.yaml ~/.config/goose/recipes/
cp framework/ai/goose/recipes/ralph-review.yaml ~/.config/goose/recipes/
chmod +x ~/.config/goose/recipes/ralph-loop.sh
```

**Invoke the Ralph Loop:**

```bash
RALPH_WORKER_PROVIDER=<provider> RALPH_WORKER_MODEL=<model> \
RALPH_REVIEWER_PROVIDER=<provider> RALPH_REVIEWER_MODEL=<model> \
~/.config/goose/recipes/ralph-loop.sh ./workspace/prompt/prompt-<uuid>-<n>.md
```

Replace `<provider>` and `<model>` with values for the selected backend:

| Backend | Provider value | Model value |
|---|---|---|
| MLX | `mlx_openai` | `mlx-community/Devstral-Samll-2507-8bit` |
| OLLama | `ollama` | `devstral:24b-small-2505-q8_0` |
| LM Studio | `lmstudio` | model name from LM Studio UI |

The loop prompts interactively for provider/model values if environment variables are not set.

[Return to Table of Contents](<#table of contents>)

---

## Verification

Confirm provider connectivity:

```bash
goose run --text "Reply with the single word: OK"
```

A response of `OK` confirms that the provider is reachable and the model is responding. If the command hangs or errors, verify that the inference server is running and the provider configuration matches the active backend.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-05 | Initial document |
| 1.1 | 2026-03-06 | Updated MLX backend prerequisite from mlx_lm.server to oMLX; updated port references to 8000 |
| 1.2 | 2026-03-06 | Corrected API key scope: oMLX requires authentication for all requests; updated MLX backend configuration; documented custom provider JSON auth fields |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
