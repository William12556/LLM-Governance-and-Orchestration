Created: 2026 June 02

# Getting Started

---

## Table of Contents

[1.0 Overview](<#1.0 overview>)
[2.0 Prerequisites](<#2.0 prerequisites>)
[3.0 Clone and Initialise](<#3.0 clone and initialise>)
[4.0 Select a Profile](<#4.0 select a profile>)
[5.0 Configure AEL](<#5.0 configure ael>)
[6.0 First Run](<#6.0 first run>)
[7.0 Next Steps](<#7.0 next steps>)
[Version History](<#version history>)

---

## 1.0 Overview

This guide covers the steps from cloning the repository to running the first AEL loop in a downstream project. It assumes Apple Silicon hardware and the AEL profile. For other profiles see [guide-profile-selection.md](guide-profile-selection.md).

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Prerequisites

### 2.1 Hardware

| Item | Minimum | Recommended |
|---|---|---|
| Chip | Apple M1 | Apple M3 / M4 |
| Unified memory | 24 GB | 64 GB |
| Storage | 30 GB free | 60 GB free |
| macOS | 14.0 (Sonoma) | Latest stable |

### 2.2 Software

| Item | Requirement |
|---|---|
| Python | 3.11+ |
| Git | Any recent version |
| Node.js | 18+ (for Filesystem MCP server) |
| Claude Desktop | Current release — Strategic Domain |
| oMLX | Current release — Tactical Domain inference server |
| MCP servers | `Filesystem` (`@j0hanz/filesystem-mcp`) and `mcp-grep` configured in Claude Desktop |

Install oMLX and download Devstral before proceeding. See [setup-apple-silicon-mlx.md](setup-apple-silicon-mlx.md).

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Clone and Initialise

### 3.1 Clone the framework repository

```bash
git clone https://github.com/William12556/LLM-Governance-and-Orchestration.git
cd LLM-Governance-and-Orchestration
```

### 3.2 Create a new project from skel/

```bash
cp -r skel/ /path/to/your/projects/<project-name>
cd /path/to/your/projects/<project-name>
```

The `skel/` directory is a minimal deployable skeleton containing governance documents, templates, profiles, and AEL configuration. It is the starting point for all downstream projects.

### 3.3 Create a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r ai/ael/requirements.txt
```

### 3.4 Initialise git

```bash
git init
git add .
git commit -m "init: project from framework skel"
```

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Select a Profile

Three implementation profiles are available. For a full comparison see [guide-profile-selection.md](guide-profile-selection.md).

| Profile | Tactical Domain | Best for |
|---|---|---|
| `mlx_devstral_small_2_2512_Q8.md` | AEL + Devstral (local) | Automated loops on Apple Silicon |
| `claude.md` | Claude Code (Anthropic API) | Manual execution, no local GPU required |
| `claude-omlx.md` | Claude Code CLI + Devstral (local) | Manual execution on Apple Silicon |

Profile documents are in `ai/profiles/`. Read the selected profile before proceeding.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Configure AEL

### 5.1 Edit config.yaml

Open `ai/ael/config.yaml` and update:

```yaml
omlx:
  base_url: "http://127.0.0.1:8000/v1"
  api_key: "local"                          # match your oMLX API key
  default_model: "<model-id>"               # model ID as reported by oMLX /v1/models

mcp_servers:
  filesystem:
    command: "/usr/local/bin/npx"
    args:
      - "-y"
      - "@j0hanz/filesystem-mcp@latest"
      - "/path/to/your/projects"            # allowed root path for MCP filesystem access
    env:
      PATH: "/opt/homebrew/opt/node@24/bin:/usr/local/bin:/usr/bin:/bin"

  mcp-grep:
    command: "/path/to/mcp-grep-env/bin/python"
    args:
      - "-m"
      - "mcp_grep.server"

context:
  models_dir: "/path/to/your/ai-models"    # directory containing downloaded MLX models
```

To find the model ID, query oMLX with your configured API key:

```bash
curl -s http://localhost:8000/v1/models -H "Authorization: Bearer local"
```

### 5.2 Generate context budget

Run once after setup and after any model change:

```bash
python ai/ael/src/budget.py
```

This writes `.ael/ralph/context-budget.md`. The Strategic Domain reads this file before authoring T04 prompts.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 First Run

### 6.1 Verify connectivity

```bash
# Confirm oMLX is responding
curl -s http://localhost:8000/v1/models -H "Authorization: Bearer local"

# Confirm AEL can reach the model
python ai/ael/src/orchestrator.py --mode worker --task "Reply with the single word: OK"
```

A response of `OK` confirms end-to-end connectivity.

### 6.2 Read governance.md

Ask the Strategic Domain (Claude Desktop) to read `ai/governance.md` and initialise the project per P01 (§1.2 Project Initialization). The Strategic Domain will guide the workflow from that point.

### 6.3 Follow the workflow

The framework workflow is defined in `ai/workflow.md` and governed by `ai/governance.md`. The sequence is:

```
P10 Requirements → P02 Design → P09 T04 Prompt → AEL → P06 Test → P00 Close
```

The Strategic Domain coordinates each step. Human approval gates are required before requirements baseline, design tier transitions, and code generation.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Next Steps

- [guide-profile-selection.md](guide-profile-selection.md) — compare profiles in detail
- [guide-audit-loop.md](guide-audit-loop.md) — run a codebase quality audit
- [setup-apple-silicon-mlx.md](setup-apple-silicon-mlx.md) — oMLX and Devstral setup
- `ai/governance.md` — authoritative protocol reference
- `ai/workflow.md` — workflow flowchart

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-02 | Initial document |

---

Copyright (c) 2026 William Watson. MIT License.
