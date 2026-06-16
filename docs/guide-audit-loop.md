Created: 2026 June 02

# Audit Loop Guide

---

## Table of Contents

[1.0 Overview](<#1.0 overview>)
[2.0 How It Works](<#2.0 how it works>)
[3.0 Prerequisites](<#3.0 prerequisites>)
[4.0 Running an Audit](<#4.0 running an audit>)
[5.0 Interpreting Results](<#5.0 interpreting results>)
[6.0 Post-Run Workflow](<#6.0 post-run workflow>)
[Version History](<#version history>)

---

## 1.0 Overview

The AEL audit loop is a read-only codebase quality analysis tool. It uses the Tactical Domain to systematically inspect source files and accumulate structured findings, without writing to any source file. The loop runs until all target items have been inspected, a wall-clock time limit is reached, or the iteration ceiling is hit.

The audit tool is available to downstream projects that use the AEL profile. It requires no modifications to the target codebase.

[Return to Table of Contents](<#table of contents>)

---

## 2.0 How It Works

The audit loop uses two dedicated recipes in place of the standard Ralph recipes:

- `audit-work.yaml` — worker reads one source item per iteration and appends findings to `audit-report.md`
- `audit-review.yaml` — reviewer checks finding quality and verifies coverage against `audit-index.md`

**Per-iteration flow:**

```
Worker reads audit-index.md → selects next unchecked item
Worker reads source file → analyses against six criteria
Worker appends findings to audit-report.md
Worker marks item [x] in audit-index.md
Reviewer reads work-summary.txt and audit-report.md
Reviewer assesses finding quality → REVISE or continue
All items [x] → SHIP
```

**Audit criteria assessed per item:**

| Criterion | What is checked |
|---|---|
| Style | Naming conventions, formatting, docstring quality |
| Complexity | Function length, nesting depth, cyclomatic complexity |
| Error handling | Bare excepts, swallowed exceptions, missing error paths |
| Security | Hardcoded credentials, unsafe input handling, injection risks |
| Conformance | Adherence to project design and governance conventions |
| Dead code | Unreachable branches, unused imports, unused variables |

**Termination conditions:**

| Condition | Outcome |
|---|---|
| All items in `audit-index.md` marked `[x]` | Reviewer issues `SHIP` |
| `--duration` wall-clock limit reached | Loop exits with `DURATION_LIMIT` marker |
| `max_iterations` exhausted | Loop exits; partial results valid |
| Worker writes `RALPH-BLOCKED.md` | Loop blocked; review manually |

[Return to Table of Contents](<#table of contents>)

---

## 3.0 Prerequisites

- AEL profile configured and operational (see [guide-profile-selection.md](guide-profile-selection.md))
- oMLX running with Devstral loaded
- Target project's `src/` accessible via the Filesystem MCP server

[Return to Table of Contents](<#table of contents>)

---

## 4.0 Running an Audit

Full operational instructions are in `ai/doc/guide-audit-loop.md`. A summary follows.

**1. Pre-audit preparation (Strategic Domain):**

The Strategic Domain generates two files and places them in `ai/state/ralph/` before launching:

- `audit-index.md` — ordered list of files and functions to audit, one item per line in `[ ] path :: name` format
- `audit-uml.md` — optional Mermaid class diagram of the target codebase for structural context

**2. Configure `config.yaml`:**

Set `max_iterations` to at least the number of items in `audit-index.md`:

```yaml
loop:
  max_iterations: 200
```

**3. Author a T04 brief** specifying the target codebase path, read-only constraint, and audit scope.

**4. Launch:**

```bash
python ai/ael/src/orchestrator.py --mode loop \
  --task ai/workspace/prompt/<uuid>-audit.md \
  --duration 12
```

Omit `--duration` to run until coverage is complete.

[Return to Table of Contents](<#table of contents>)

---

## 5.0 Interpreting Results

Findings are written to `ai/state/ralph/audit-report.md` in a structured format:

```markdown
## src/module.py :: function_name  [iteration N]
- **Type:** error-handling
- **Location:** line 47
- **Description:** Exception caught bare; original error context is lost.
- **Severity:** high
```

Severity levels:

| Severity | Meaning |
|---|---|
| high | Likely to cause failure, security risk, or significant conformance violation |
| medium | Degraded quality; should be addressed in normal development cycle |
| low | Minor style or documentation issue |

[Return to Table of Contents](<#table of contents>)

---

## 6.0 Post-Run Workflow

1. Read `audit-report.md` — review all findings
2. High and critical severity findings → create T03 issues via P04, referencing the audit run
3. Medium findings → record in a tracking issue or schedule for next development cycle
4. Low findings → discretionary; may be addressed in passing or deferred
5. Move `audit-report.md` to `ai/workspace/audit/` and rename per naming convention
6. When remediation is complete, close the audit document per P08 §1.9.8

[Return to Table of Contents](<#table of contents>)

---

## Version History

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-06-02 | Initial document |
| 1.1 | 2026-06-14 | Relocated paths under ai/: state → ai/state/ralph/, workspace/ → ai/workspace/ |
| 1.2 | 2026-06-16 | Updated guide reference: framework/ai/doc/ → ai/doc/ |
| 1.3 | 2026-06-16 | Updated §6.0 cross-reference: P08 §1.9.7 → §1.9.8, following governance.md merge of duplicate Audit Closure sections |

---

Copyright (c) 2026 William Watson. MIT License.
