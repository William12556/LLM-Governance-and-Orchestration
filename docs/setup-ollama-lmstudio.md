Created: 2026 March 05

# OLLama and LM Studio Setup Guide

---

## Table of Contents

- [Overview](<#overview>)
- [Hardware Requirements](<#hardware requirements>)
- [OLLama](<#ollama>)
  - [Install OLLama](<#install ollama>)
  - [Pull Devstral](<#pull devstral>)
  - [Configure Goose for OLLama](<#configure goose for ollama>)
  - [Verify OLLama](<#verify ollama>)
- [LM Studio](<#lm studio>)
  - [Install LM Studio](<#install lm studio>)
  - [Download Devstral in LM Studio](<#download devstral in lm studio>)
  - [Configure Goose for LM Studio](<#configure goose for lm studio>)
  - [Verify LM Studio](<#verify lm studio>)
- [Model Notes](<#model notes>)
- [Version History](<#version history>)

---

## Overview

OLLama and LM Studio are alternative local inference platforms. They are suitable for non-Apple Silicon hardware or where MLX is not available. Both expose an OpenAI-compatible API consumed by Goose.

Model: **Devstral Small 2507** (Apache 2.0 licence). OLLama and LM Studio support GGUF-format models; Q8 quantisation is recommended where memory allows.

[Return to Table of Contents](<#table of contents>)

---

## Hardware Requirements

| Item | Minimum | Recommended |
|---|---|---|
| RAM | 24 GB | 48 GB+ |
| GPU VRAM (if GPU-accelerated) | 24 GB | 48 GB+ |
| Storage | 30 GB free | 60 GB free |
| OS | macOS 13 / Ubuntu 22.04 / Windows 11 | Latest stable |

> Devstral Small 2507 is a 22B-parameter model. Q8 quantisation requires approximately 24 GB of memory (system RAM or GPU VRAM). BF16 requires approximately 44 GB. On systems without a compatible GPU, inference runs on CPU — performance will be significantly lower.

[Return to Table of Contents](<#table of contents>)

---

## OLLama

### Install OLLama

**macOS / Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:** download the installer from https://ollama.com/download.

Start the OLLama server:

```bash
ollama serve
```

The server runs on `http://localhost:11434` by default.

[Return to Table of Contents](<#table of contents>)

---

### Pull Devstral

```bash
ollama pull devstral:24b-small-2505-q8_0
```

> Always use the full model tag. Short tags may not resolve correctly.

Confirm the model is available:

```bash
ollama list
```

[Return to Table of Contents](<#table of contents>)

---

### Configure Goose for OLLama

Edit `~/.config/goose/config.yaml`:

```yaml
GOOSE_PROVIDER: ollama
GOOSE_MODEL: devstral:24b-small-2505-q8_0
OLLAMA_HOST: http://localhost:11434
```

Refer to [Goose Setup Guide — OLLama Backend](setup-goose.md#ollama-backend) for the full configuration procedure.

[Return to Table of Contents](<#table of contents>)

---

### Verify OLLama

Confirm the server is responding:

```bash
curl http://localhost:11434/api/tags
```

Confirm Goose can reach the model:

```bash
goose run --text "Reply with the single word: OK"
```

[Return to Table of Contents](<#table of contents>)

---

## LM Studio

LM Studio provides a graphical interface for downloading, managing, and serving local models. It exposes an OpenAI-compatible server API.

### Install LM Studio

Download from https://lmstudio.ai and install per platform instructions.

[Return to Table of Contents](<#table of contents>)

---

### Download Devstral in LM Studio

1. Open LM Studio.
2. Search for `devstral` in the model browser.
3. Select the Q8 variant for Devstral Small 2507. Choose BF16 if sufficient RAM is available (see [Model Notes](<#model notes>)).
4. Download the model.

[Return to Table of Contents](<#table of contents>)

---

### Configure Goose for LM Studio

1. In LM Studio, load the Devstral model and start the local server (default: `http://localhost:1234/v1`).
2. Note the model identifier displayed in LM Studio — it is required for the Goose configuration.

Run `goose configure` and register a provider with:

| Field | Value |
|---|---|
| Provider name | `LM Studio` |
| Base URL | `http://localhost:1234/v1` |
| API key | `lm-studio` (placeholder; field is required) |
| Model | model identifier from LM Studio UI |

Refer to [Goose Setup Guide — LM Studio Backend](setup-goose.md#lm-studio-backend) for the full configuration procedure.

[Return to Table of Contents](<#table of contents>)

---

### Verify LM Studio

Confirm the server is responding:

```bash
curl http://localhost:1234/v1/models
```

Confirm Goose can reach the model:

```bash
goose run --text "Reply with the single word: OK"
```

[Return to Table of Contents](<#table of contents>)

---

## Model Notes

**Quantisation choice:**

| Variant | Memory | Notes |
|---|---|---|
| Q8 | ~24 GB | Recommended baseline; minimal quality loss vs BF16 |
| BF16 | ~44 GB | Full precision; prefer if 48 GB+ RAM is available |

**Tool-calling requirement:** Goose requires tool-calling support for developer workflows. Devstral Small 2507 supports tool calling. Verify tool-calling capability before substituting an alternative model.

**OLLama vs LM Studio:** Both platforms produce equivalent results for the same model and quantisation. OLLama is command-line oriented; LM Studio provides a graphical interface. The choice is operational preference.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-05 | Initial document |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
