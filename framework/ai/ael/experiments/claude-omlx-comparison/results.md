# Experiment Results — claude-omlx-comparison

Created: 2026 April 30

---

## Table of Contents

- [1.0 Objective](<#1.0 objective>)
- [2.0 Setup](<#2.0 setup>)
- [3.0 Runs](<#3.0 runs>)
- [4.0 Elapsed Time](<#4.0 elapsed time>)
- [5.0 Code Output Analysis](<#5.0 code output analysis>)
- [6.0 Findings](<#6.0 findings>)
- [7.0 Infrastructure Observations](<#7.0 infrastructure observations>)
- [Version History](<#version history>)

---

## 1.0 Objective

Qualitative comparison of code output from three Tactical Domain execution approaches against an identical task specification, using two prompt variants (full T04 and tactical brief).

Approaches compared:

- **AEL** — Ralph Loop (`orchestrator.py` → oMLX → Devstral 6bit)
- **claude-omlx** — Claude Code CLI (`env -i` invocation → oMLX → Devstral 6bit)
- **Claude Code** — Claude Code CLI (Anthropic API → Claude Sonnet 4.5)

[Return to Table of Contents](<#table of contents>)

---

## 2.0 Setup

**Task:** Implement `csv_stats.py` — a CLI program computing mean, median, and population standard deviation for numeric columns in a CSV file. Standard library only, Python 3.11, four functions with docstrings.

**Prompts:**
- `prompt-full-T04.md` — full T04 YAML specification (~400 tokens)
- `prompt-brief.md` — tactical brief only (~200 tokens)

**Models:**
- AEL and claude-omlx: `mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-6Bit` via oMLX at `http://127.0.0.1:8000`
- Claude Code: Claude Sonnet 4.5 via Anthropic API

**Hardware:** M4 Mac Mini, 64GB unified memory. Both models ran sequentially; no concurrent inference.

**Note on model change:** Initial runs used Devstral Q8. Memory pressure (both pinned models consuming ~49.8GB of 56GB limit) caused oMLX crashes. Switched to 6bit quantisation for all Devstral runs to provide adequate KV headroom.

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Runs

| Run | Approach | Prompt | Output file | Status |
|-----|----------|--------|-------------|--------|
| 1 | AEL | Full T04 | `csv_stats_ael_full.py` | ✓ SHIPPED |
| 2 | AEL | Brief | `csv_stats_ael_brief.py` | ✓ written (rc=1 on teardown) |
| 3 | claude-omlx | Full T04 | `csv_stats_omlx_full.py` | ✓ complete |
| 4 | claude-omlx | Brief | `csv_stats_omlx_brief.py` | ✓ complete |
| 5 | Claude Code | Full T04 | `csv_stats_claude_full.py` | ✓ complete |
| 6 | Claude Code | Brief | `csv_stats_claude_brief.py` | ✓ complete |

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Elapsed Time

Elapsed time for AEL runs is derived from `mcp-run.json` start time and output file creation timestamp. Times for claude-omlx and Claude Code were not recorded.

| Run | Approach | Prompt | Elapsed |
|-----|----------|--------|---------|
| 1 | AEL | Full T04 | ~33 min |
| 2 | AEL | Brief | ~2.5 min |
| 3 | claude-omlx | Full T04 | not recorded |
| 4 | claude-omlx | Brief | not recorded |
| 5 | Claude Code | Full T04 | not recorded |
| 6 | Claude Code | Brief | not recorded |

The AEL full T04 run took ~33 minutes due to scope creep — the worker generated unrequested artefacts (`test_data.csv`, `test_csv_stats.py`, `test_empty.csv`, `test_report.txt`, `test_simple.py`) before completing the primary deliverable. Each extra artefact consumed additional inference cycles. The AEL brief run completed in ~2.5 minutes with no scope creep, demonstrating that the full T04 specification induced significantly more autonomous behaviour in the worker.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Code Output Analysis

### 5.1 Correctness

All six outputs are functionally correct. All four specified functions are present with docstrings. Standard library only in all cases.

### 5.2 Criterion Assessment

| Criterion | AEL full | AEL brief | oMLX full | oMLX brief | Claude full | Claude brief |
|-----------|:--------:|:---------:|:---------:|:----------:|:-----------:|:------------:|
| Scope discipline | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Error message format matches spec | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Python 3.11 typing style | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| Granular exception handling in main() | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ |
| write_report OSError handling | ✓ | ✓ | ✓ | ✗ | bare open | bare open |
| Full/brief output consistency | — | — | — | — | ✓ identical | ✓ identical |

### 5.3 Per-Approach Notes

**AEL (Devstral 6bit via orchestrator.py)**

Full and brief outputs are structurally near-identical — same model, same behaviour pattern. The full T04 run created five unrequested files; the brief run did not. Both use broad exception catching in `main()` (`except (FileNotFoundError, ValueError, RuntimeError, OSError)`). Error messages do not match spec format. Python 3.11 built-in generics used correctly (no `from typing import`).

**claude-omlx (Devstral 6bit via Claude Code → oMLX)**

Outputs consistent with AEL — same model produces similar code regardless of execution wrapper. `from typing import Dict, List, Tuple` is redundant in Python 3.11. The brief run's `write_report` has no OSError handling — a spec gap not present in the full T04 run, suggesting the full specification provided enough context to implement it correctly. Error messages do not match spec format.

**Claude Code (Sonnet 4.5 via Anthropic API)**

Full and brief outputs are logically identical — prompt length had no effect on output quality or consistency. Error message format exactly matches the spec (`"Error: file not found: <path>"`, `"Error: CSV file is empty"`, etc.). Uses `from statistics import mean, median, pstdev` — most idiomatic Python 3.11 import style. `main()` uses individual exception catches per error type, matching the spec's error handling strategy. No scope creep in either run. `write_report` uses bare `open()` without try/except — OSError propagates to `main()` where it is caught, which is correct but differs from the spec's intent of catching at the function level.

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Findings

**Model is the primary determinant of output quality.** The difference between AEL and claude-omlx outputs is negligible — both use Devstral 6bit and produce structurally similar code. The execution wrapper (orchestrator vs Claude Code CLI) had no observable effect on code quality for the same model.

**Claude Sonnet produces more specification-adherent output.** Error message format, typing style, and exception handling structure all align more closely with the spec. Output is deterministic across prompt variants.

**Prompt length affects Devstral behaviour more than Sonnet.** The full T04 specification induced scope creep in the AEL run (33 min, five extra files) while the brief prompt did not (2.5 min, no extras). Sonnet was unaffected by prompt length.

**The brief prompt is sufficient for Devstral.** The brief run produced equivalent or better output (no scope creep) at a fraction of the time. The detailed T04 specification adds governance value (traceability, element registry, change coupling) but does not improve Devstral output quality — it may degrade it by providing context that encourages autonomous elaboration.

**The brief prompt is redundant for Sonnet.** Sonnet produced identical output from both prompts, suggesting it extracts only what it needs regardless of context volume.

[Return to Table of Contents](<#table of contents>)

---

## 7.0 Infrastructure Observations

The following issues were encountered during the experiment and are noted separately from the code quality findings.

**MCP stdio teardown crash (issue-e3f1a2b4):** All AEL runs initially failed with `asyncio.CancelledError` / `RuntimeError: Attempted to exit cancel scope in a different task` during MCP client teardown. Fixed by skipping `ctx.__aexit__()` in `mcp_client.py close()` — stdio subprocesses are reaped by the OS on process exit. Fix applied to `framework/ai/ael/src/mcp_client.py`.

**config.yaml model name:** `default_model` updated from `Devstral-Small-2-24B-Instruct-2512` to `mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-6Bit` to match oMLX-served model name after quantisation change.

**Memory pressure:** Both models pinned simultaneously consumed ~49.8GB of the 56GB process limit, leaving insufficient KV cache headroom. Resolved by unpinning both models and allowing on-demand loading. Quantisation downgrade from Q8 to 6bit also reduced peak memory by ~5GB per model.

**claude-omlx auth:** `ANTHROPIC_AUTH_TOKEN=` (empty string) did not suppress the persisted claude.ai session token. Resolution: `env -i HOME="$HOME" PATH="$PATH"` to start Claude Code in a clean environment without the inherited session.

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2026-04-30 | Initial results document |

---

Copyright (c) 2026 William Watson. MIT License.
