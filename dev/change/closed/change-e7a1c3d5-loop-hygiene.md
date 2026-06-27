Created: 2026 June 26

```yaml
change_info:
  id: "change-e7a1c3d5"
  title: "Loop hygiene: stall detection, distinct timeout outcome, completion-call retry"
  date: "2026-06-26"
  author: "William Watson"
  status: "proposed"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-e7a1c3d5"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-e7a1c3d5"
  description: >
    Remediate proposal-f9a2c41b findings F12, F10, F14: no stall detection,
    timeout reported as success, and no error handling around the completion call.

scope:
  summary: >
    Add stall detection to run_loop, make the duration-limit exit distinct from
    SHIP, and wrap the completion call with bounded retry/backoff.
  affected_components:
    - name: "orchestrator (run_loop, duration-limit branch, completion call)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  out_of_scope:
    - "Reviewer decision handling (change-a1d4f7e2)"
    - "Stale-signal handling (change-d2f6b8c4)"

rational:
  problem_statement: >
    F12: no mechanism detects repeated identical feedback, so a stall consumes
    every iteration without BLOCK. F10: the duration-limit branch writes
    .ralph-complete and returns 0, so a timeout is indistinguishable from SHIP.
    F14: the completion call is unguarded, so a transient endpoint error aborts
    the loop.
  proposed_solution: >
    F12: hash review-feedback.txt per cycle; if unchanged for N consecutive
    cycles, write RALPH-BLOCKED.md and stop. F10: return a distinct non-zero code
    and a different sentinel (e.g. .ralph-timeout). F14: bounded retry/backoff on
    the completion call; BLOCK cleanly on persistent failure.
  benefits:
    - "Stalls terminate instead of burning iterations and inference cost"
    - "Callers (including ael-mcp) can distinguish timeout from SHIP"
    - "Transient endpoint errors no longer abort the loop"
  risks:
    - risk: "Stall threshold N too low — premature BLOCK"
      mitigation: "Make N configurable; default conservative"
    - risk: "New timeout exit code breaks a caller that assumes 0/non-zero binary"
      mitigation: "Document the code; keep 0 = SHIP and reserve a specific code for timeout"

technical_details:
  current_behavior: >
    run_loop has no stall detection. The duration-limit branch writes
    .ralph-complete and returns 0. client.chat.completions.create has no
    surrounding try/except.
  proposed_behavior: >
    run_loop detects N consecutive identical review-feedback hashes and BLOCKs.
    The duration-limit exit returns a distinct non-zero code and writes
    .ralph-timeout. The completion call retries with backoff and BLOCKs on
    persistent failure.
  implementation_approach: >
    Add per-cycle feedback hashing and a consecutive-unchanged counter (F12);
    change the duration-limit return code and sentinel (F10); wrap the completion
    call in bounded retry/backoff (F14). Threshold, backoff policy, and exit code
    decided in implementation.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "F12 stall detection in run_loop; F10 distinct timeout code + .ralph-timeout sentinel; F14 retry/backoff around the completion call"
      functions_affected:
        - "run_loop"
        - "run_phase"
        - "main_async"

testing_requirements:
  test_cases:
    - scenario: "N consecutive identical REVISE feedbacks"
      expected_result: "RALPH-BLOCKED.md written; loop stops"
    - scenario: "Duration limit reached"
      expected_result: "Non-zero exit code; .ralph-timeout written; no .ralph-complete"
    - scenario: "Transient completion error then recovery"
      expected_result: "Retry succeeds; loop continues"
    - scenario: "Persistent completion error"
      expected_result: "Clean BLOCK; no uncaught exception"
  validation_criteria:
    - "SHIP path still returns 0"
    - "Distinct feedback across cycles does not trigger stall BLOCK"

implementation:
  implementation_steps:
    - step: "Claude Code implements per T04 prompt-e7a1c3d5; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py to prior version"

notes: >
  Execution path: Claude Code. Groups F12 (medium), F10 (medium), F14 (medium).
  F12 stall detection relates to the over-looping class observed in
  issue-e2b8046c. All source changes.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
