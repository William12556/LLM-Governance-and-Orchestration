Created: 2026 March 05

# Apple Silicon + MLX Setup Guide

---

## Table of Contents

- [Overview](<#overview>)
- [Hardware Requirements](<#hardware requirements>)
- [Software Prerequisites](<#software prerequisites>)
- [Install oMLX](<#install omlx>)
- [Download Devstral](<#download devstral>)
  - [Q8 Quantised Model](<#q8 quantised model>)
  - [BF16 Full Precision Model](<#bf16 full precision model>)
- [Start oMLX](<#start omlx>)
- [Configure Goose](<#configure goose>)
- [Verification](<#verification>)
- [Version History](<#version history>)

---

## Overview

This guide covers running Devstral on Apple Silicon using the MLX framework. oMLX exposes an OpenAI-compatible API consumed by Goose as the Tactical Domain inference backend.

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

## Install oMLX

oMLX depends on `mlx_lm`. Install both:

```bash
pip install mlx_lm omlx huggingface_hub
```

Verify:

```bash
omlx --help
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

## Start oMLX

oMLX adds TTL-based model unloading: the model is evicted from unified memory after a configurable idle period, freeing resources for other workloads. The server remains running and reloads automatically on the next request.

### Configure

During the first-run startup wizard, oMLX requires an API key. This key authenticates all API requests — including inference — and the admin dashboard at `http://localhost:8000/admin/dashboard`.

Set any string of your choosing, for example:

```
local
```

This value is stored in `~/.omlx/settings.json` and persists across restarts.

### Configure Model Directory

Point oMLX at the directory containing your MLX models. Models are auto-detected from subdirectories:

```bash
omlx serve --model-dir ~/ai-models/mlx-community
```

Run this once to persist the setting. Subsequent starts use the saved value.

### Start

```bash
omlx serve
```

Or as a managed background service via Homebrew:

```bash
brew services start omlx
```

The server exposes an OpenAI-compatible API at `http://localhost:8000/v1`. The admin dashboard is at `http://localhost:8000/admin/dashboard` — enter your API key to authenticate.

Goose provider configuration:

| Field | Value |
|---|---|
| Provider name | `MLX OpenAI` |
| Base URL | `http://localhost:8000/v1` |
| API key | `local` (value from `~/.omlx/settings.json`) |
| Model | `mlx-community/Devstral-Samll-2507-8bit` |

[Return to Table of Contents](<#table of contents>)

---

## Configure Goose

With oMLX running, configure Goose to use it as an OpenAI-compatible provider.

Run `goose configure` and register a provider with:

| Field | Value |
|---|---|
| Provider name | `MLX OpenAI` |
| Base URL | `http://localhost:8000/v1` |
| API key | `local` (value from `~/.omlx/settings.json`) |
| Model | `mlx-community/Devstral-Samll-2507-8bit` |

Refer to [Goose Setup Guide — MLX Backend](setup-goose.md#mlx-backend) for the full configuration procedure.

[Return to Table of Contents](<#table of contents>)

---

## Verification

**1. Confirm the server is responding:**

```bash
curl http://localhost:8000/v1/models -H "Authorization: Bearer local"
```

A JSON response listing the loaded model confirms the server is operational. Replace `local` with your configured API key if different.

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
| 1.3 | 2026-03-06 | Promoted oMLX to primary inference server; removed mlx_lm.server; updated all port references to 8000 |
| 1.4 | 2026-03-06 | Corrected API key scope: oMLX requires authentication for all requests, not admin dashboard only; updated tables and verification curl |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
