Created: 2026 June 26

```yaml
prompt_info:
  id: "prompt-e7a1c3d5"
  task_type: "debug"
  source_ref: "change-e7a1c3d5"
  date: "2026-06-26"
  iteration: 1
  coupled_docs:
    change_ref: "change-e7a1c3d5"
    change_iteration: 1

context:
  purpose: >
    Improve loop hygiene: detect stalls, make a duration-limit exit distinct from
    SHIP, and survive transient completion-call errors.
  integration: >
    ai/ael/src/orchestrator.py — run_loop (stall detection, duration-limit
    branch) and the completion call in run_phase.
  constraints:
    - "SHIP path still returns 0"
    - "Distinct feedback across cycles must not trigger a stall BLOCK"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Loop-hygiene changes (F12, F10, F14 from proposal-f9a2c41b).
  requirements:
    functional:
      - "F12: hash review-feedback.txt per cycle; if unchanged for N consecutive cycles, write RALPH-BLOCKED.md and stop; N configurable with a conservative default"
      - "F10: the duration-limit exit returns a distinct non-zero code and writes a distinct sentinel (e.g. .ralph-timeout) instead of .ralph-complete"
      - "F14: wrap the completion call in bounded retry/backoff; on persistent failure, BLOCK cleanly (no uncaught exception)"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions"
        - "Comprehensive error handling with traceback logging on persistent failure"

design:
  architecture: "Stall counter in run_loop; revised duration-limit branch; retry wrapper around the completion call"
  components:
    - name: "run_loop (stall detection)"
      type: "function"
      purpose: "Detect no-progress and BLOCK (F12)"
      logic:
        - "Hash review-feedback.txt each cycle"
        - "Track consecutive-unchanged count; at N, write RALPH-BLOCKED.md and stop"
        - "Reset the counter when feedback changes"
    - name: "run_loop (duration-limit branch)"
      type: "function"
      purpose: "Distinguish timeout from SHIP (F10)"
      logic:
        - "On deadline reached, write .ralph-timeout (not .ralph-complete) and return a distinct non-zero code"
    - name: "completion call wrapper"
      type: "function"
      purpose: "Survive transient endpoint errors (F14)"
      logic:
        - "Bounded retry with backoff around client.chat.completions.create"
        - "On persistent failure, BLOCK cleanly and log the traceback"
  dependencies:
    internal:
      - "Existing sentinel/state-file writes"
      - "Deadline handling"
    external: []

data_schema:
  entities:
    - name: "stall_threshold"
      attributes:
        - name: "N"
          type: "int"
          constraints: "configurable; conservative default"

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Implement F12/F10/F14 per design"

success_criteria:
  - "N consecutive identical REVISE feedbacks produce RALPH-BLOCKED.md and stop the loop"
  - "A duration-limit exit returns a distinct non-zero code and writes .ralph-timeout, not .ralph-complete"
  - "A transient completion error retries and recovers; a persistent one BLOCKs without an uncaught exception"
  - "SHIP path still returns 0; distinct feedback does not trigger a stall BLOCK"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  File: ai/ael/src/orchestrator.py (run_loop, completion call). Read before editing.
  F12: hash review-feedback.txt per cycle; N consecutive unchanged -> write RALPH-BLOCKED.md and stop; N configurable, conservative default.
  F10: duration-limit exit returns a distinct non-zero code and writes .ralph-timeout, not .ralph-complete.
  F14: bounded retry/backoff around the completion call; persistent failure -> clean BLOCK.
  Constraints: SHIP still returns 0; distinct feedback must not BLOCK; verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Claude Code consumes this full document; the
  tactical_brief is retained for schema/govwatch compliance. F10's new exit code
  is consumed by callers including ael-mcp. No AEL/oMLX context-budget gate applies.
```
