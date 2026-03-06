Created: 2026 March 05

# Apple Silicon + MLX Setup Guide

---

## Table of Contents

- [Overview](<#overview>)
- [Hardware Requirements](<#hardware requirements>)
- [Software Prerequisites](<#software prerequisites>)
- [Install mlx_lm](<#install mlx_lm>)
- [Download Devstral](<#download devstral>)
  - [Q8 Quantised Model](<#q8 quantised model>)
  - [BF16 Full Precision Model](<#bf16 full precision model>)
- [Start the Inference Server](<#start the inference server>)
- [omlx — Optional Memory Management](<#omlx  optional memory management>)
- [Configure Goose](<#configure goose>)
- [Verification](<#verification>)
- [Version History](<#version history>)

---

## Overview

This guide covers running Devstral on Apple Silicon using the MLX framework. The `mlx_lm` server exposes an OpenAI-compatible API consumed by Goose as the Tactical Domain inference backend.

Model: **Devstral Small 2507** (Apache 2.0 licence)
Quantisation: Q8 recommended; BF16 available for systems with sufficient unified memory.

[Return to Table of Contents](<#table of contents>)

---

## Hardware Requirements

| Item | Minimum | Recommended |
|---|---|---|
| Chip | Apple M1 | Apple M3 / M4 |
| Unified memory | 24 GB (Q8) | 48 GB+ (BF16) |
| Storage | 30 GB free | 60 GB free |
| macOS | 14.0 (Sonoma) | Latest stable |

> Devstral Small 2507 is a 22B-parameter model. Q8 quantisation requires approximately 24 GB unified memory. BF16 requires approximately 44 GB.

[Return to Table of Contents](<#table of contents>)

---

## Software Prerequisites

- **Python 3.11+** — verify with `python3 --version`. Install via [Homebrew](https://brew.sh): `brew install python@3.11`
- **pip** — included with Python 3.11
- **Goose** — see [Goose Setup Guide](setup-goose.md)
- **huggingface_hub** — installed in the step below

[Return to Table of Contents](<#table of contents>)

---

## Install mlx_lm

```bash
pip install mlx_lm huggingface_hub
```

Verify:

```bash
python -m mlx_lm.server --help
```

[Return to Table of Contents](<#table of contents>)

---

## Download Devstral

Choose Q8 or BF16 based on available unified memory.

### Q8 Quantised Model

Approximately 24 GB unified memory required.

```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='mlx-community/Devstral-Samll-2507-8bit',
    local_dir='~/ai-models/mlx-community/devstral-q8'
)
"
```

> Note: the HuggingFace repository name contains a known typo — `Devstral-Samll-2507-8bit` (not `Small`). Use the name exactly as shown.

[Return to Table of Contents](<#table of contents>)

---

### BF16 Full Precision Model

Approximately 44 GB unified memory required. BF16 provides full model precision at the cost of higher memory consumption.

Locate the BF16 variant on the [mlx-community HuggingFace page](https://huggingface.co/mlx-community) and substitute the `repo_id` and `local_dir` accordingly:

```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='mlx-community/<bf16-repo-name>',
    local_dir='~/ai-models/mlx-community/devstral-bf16'
)
"
```

> Replace `<bf16-repo-name>` with the current BF16 repository name from mlx-community. Repository names may change between model releases.

[Return to Table of Contents](<#table of contents>)

---

## Start the Inference Server

Start the `mlx_lm` server on port 8080:

**Q8:**

```bash
python -m mlx_lm.server \
  --model ~/ai-models/mlx-community/devstral-q8 \
  --port 8080
```

**BF16:**

```bash
python -m mlx_lm.server \
  --model ~/ai-models/mlx-community/devstral-bf16 \
  --port 8080
```

The server exposes an OpenAI-compatible API at `http://localhost:8080/v1`. No API key is required.

The server process must remain running while Goose is active. Run it in a separate terminal or as a background process.

[Return to Table of Contents](<#table of contents>)

---

## omlx — Optional Memory Management

`omlx` is an alternative inference server built on `mlx-lm`. It adds TTL-based model unloading: the model is evicted from unified memory after a configurable idle period, freeing resources for other workloads. The server remains running and reloads the model automatically on the next request.

This is the recommended configuration when the M4 Mac Mini runs workloads other than inference.

### Install

```bash
pip install omlx
```

Verify:

```bash
omlx --help
```

### Configure

Create a configuration file (for example, `~/.config/omlx/config.toml`):

During the 3-step startup wizard, omlx requires an API key to be set. This key is used solely to authenticate access to the admin dashboard at `http://localhost:8000/admin/dashboard`. It is not required for inference requests from Goose.

Set any string of your choosing as the key, for example:

```
local
```

This value is stored in `~/.omlx/settings.json` and persists across restarts.

### Configure Model Directory

Point omlx at the directory containing your MLX models. omlx discovers models from subdirectories automatically:

```bash
omlx serve --model-dir ~/ai-models/mlx-community
```

Run this once to persist the setting to `~/.omlx/settings.json`. Subsequent starts will use the saved value.

### Start

```bash
omlx serve
```

Or as a managed background service via Homebrew:

```bash
brew services start omlx
```

The server exposes an OpenAI-compatible API at `http://localhost:8000/v1`. The admin dashboard is available at `http://localhost:8000/admin/dashboard` — enter your API key to authenticate.

> **Note:** omlx defaults to port `8000`, not `8080`. Update your Goose provider configuration accordingly. Do not run omlx and `mlx_lm.server` simultaneously.

Goose provider configuration when using omlx:

| Field | Value |
|---|---|
| Provider name | `MLX OpenAI` |
| Base URL | `http://localhost:8000/v1` |
| API key | *(leave empty)* |
| Model | `mlx-community/Devstral-Samll-2507-8bit` |

[Return to Table of Contents](<#table of contents>)

---

## Configure Goose

With the `mlx_lm` server running, configure Goose to use it as an OpenAI-compatible provider.

Run `goose configure` and register a provider with:

| Field | Value |
|---|---|
| Provider name | `MLX OpenAI` |
| Base URL | `http://localhost:8080/v1` |
| API key | `none` |
| Model | `mlx-community/Devstral-Samll-2507-8bit` |

Refer to [Goose Setup Guide — MLX Backend](setup-goose.md#mlx-backend) for the full configuration procedure.

[Return to Table of Contents](<#table of contents>)

---

## Verification

**1. Confirm the server is responding:**

```bash
curl http://localhost:8080/v1/models
```

A JSON response listing the loaded model confirms the server is operational.

**2. Confirm Goose can reach the model:**

```bash
goose run --text "Reply with the single word: OK"
```

A response of `OK` confirms end-to-end connectivity.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-03-05 | Initial document |
| 1.1 | 2026-03-05 | Added omlx optional memory management section |
| 1.2 | 2026-03-05 | Corrected omlx configuration: API key is for admin dashboard auth only; corrected default port from 8080 to 8000; added Goose provider table; added Homebrew service start |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
