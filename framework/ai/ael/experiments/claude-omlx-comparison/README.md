# claude-omlx-comparison

Created: 2026 April 28

---

## Table of Contents

- [1.0 Purpose](<#1.0 purpose>)
- [2.0 Structure](<#2.0 structure>)
- [3.0 Task](<#3.0 task>)
- [4.0 Run Procedure](<#4.0 run procedure>)
- [5.0 Evaluation](<#5.0 evaluation>)
- [Version History](<#version history>)

---

## 1.0 Purpose

Qualitative comparison of code output between two Tactical Domain execution approaches using an identical task specification:

- **AEL Ralph Loop** — `orchestrator.py` governing Devstral via oMLX
- **claude-omlx** — Claude Code CLI redirected to oMLX (`ANTHROPIC_BASE_URL=http://localhost:8000`)

Each approach is run twice: once with the full T04 prompt, once with the tactical brief only. This yields four runs against the same deliverable specification.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Structure

```
claude-omlx-comparison/
├── README.md               # This file
├── prompt-full-T04.md      # Full T04 prompt (common input)
├── prompt-brief.md         # Tactical brief only (common input)
└── csv_stats.py            # Deliverable — written by each approach in turn
```

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Task

Implement `csv_stats.py`: a CLI program that reads a CSV file and computes mean, median, and population standard deviation for each numeric column. Writes a plain-text report. Standard library only. Full specification in `prompt-full-T04.md`.

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Run Procedure

For each run, delete `csv_stats.py` before starting so each approach produces a clean output.

### 4.1 Run 1 — AEL, full T04

```bash
cd /Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration
python framework/ai/ael/src/orchestrator.py --mode loop \
  --task framework/ai/ael/experiments/claude-omlx-comparison/prompt-full-T04.md \
  --config framework/ai/ael/config.yaml
```

Save output as `csv_stats_ael_full.py` for comparison.

### 4.2 Run 2 — AEL, brief

```bash
python framework/ai/ael/src/orchestrator.py --mode loop \
  --task framework/ai/ael/experiments/claude-omlx-comparison/prompt-brief.md \
  --config framework/ai/ael/config.yaml
```

Save output as `csv_stats_ael_brief.py`.

### 4.3 Run 3 — claude-omlx, full T04

```bash
claude-omlx --print "$(cat framework/ai/ael/experiments/claude-omlx-comparison/prompt-full-T04.md)"
```

Save output as `csv_stats_omlx_full.py`.

### 4.4 Run 4 — claude-omlx, brief

```bash
claude-omlx --print "$(cat framework/ai/ael/experiments/claude-omlx-comparison/prompt-brief.md)"
```

Save output as `csv_stats_omlx_brief.py`.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Evaluation

Assess each output against the following criteria. No scoring rubric — qualitative judgement only.

| Criterion | Description |
|-----------|-------------|
| Correctness | All four functions present; logic is correct |
| Scope discipline | No unrequested additions or omissions |
| Error handling | All four error paths implemented |
| Code style | Clarity, simplicity, docstrings present |
| Standard library compliance | No third-party imports |

Record observations in notes alongside the saved files.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2026-04-28 | Initial experiment setup |

---

Copyright (c) 2026 William Watson. MIT License.
