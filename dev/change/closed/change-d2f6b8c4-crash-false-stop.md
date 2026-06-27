Created: 2026 June 26

```yaml
change_info:
  id: "change-d2f6b8c4"
  title: "Fix tool-call truncation crash, substring error misclassification, and stale-signal false completion"
  date: "2026-06-26"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-d2f6b8c4"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-d2f6b8c4"
  description: >
    Remediate proposal-f9a2c41b findings F3, F7, F11: truncation ordering that
    produces an invalid conversation and aborts the phase; substring error
    classification yielding false BLOCKs; stale signal file yielding false
    immediate completion in single-phase modes.

scope:
  summary: >
    Correct tool-call truncation ordering, replace substring error classification
    with structured signals, and clear/warn on stale signal files in single-phase
    modes.
  affected_components:
    - name: "orchestrator (run_phase, _is_mcp_error, single-phase modes)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  out_of_scope:
    - "Loop-mode signal clearing (already present in run_loop)"
    - "Completion-call retry (change-e7a1c3d5)"

rational:
  problem_statement: >
    F3: the assistant message is appended with all tool_calls before
    max_tool_calls_per_iter truncation, so retained tool results leave orphaned
    tool_call ids and the next API call raises. F7: _is_mcp_error and the
    malformed-final guard match substrings anywhere in content, misclassifying
    benign output. F11: single --mode worker/reviewer does not clear a stale
    work-complete.txt, causing a no-op iteration-1 completion.
  proposed_solution: >
    F3: truncate before building the assistant message, or append only retained
    calls. F7: classify on structured signals (tool-result status, finish_reason).
    F11: clear phase signal files at the start of single-phase modes, or warn on
    work-complete.txt.
  benefits:
    - "Eliminates a hard crash on high tool-call turns"
    - "Removes false BLOCKs and false malformed-final flags"
    - "Single-phase modes no longer report no-op completion"
  risks:
    - risk: "Structured classification misses an error the substring scan caught"
      mitigation: "Map known MCP error shapes to structured fields; retain a conservative fallback"
    - risk: "Clearing signals in single mode hides a deliberately staged state"
      mitigation: "Clear only orchestrator-managed phase signals; document the behavior"

technical_details:
  current_behavior: >
    Truncation occurs after the all-tool_calls assistant message is built (F3).
    _is_mcp_error and the malformed guard match substrings in content (F7).
    Single-phase modes do not clear work-complete.txt; startup warns only on
    .ralph-complete (F11).
  proposed_behavior: >
    The conversation never contains orphaned tool_call ids. Error and
    malformed-final classification use structured signals. Single-phase modes
    start from a cleared signal state or warn on a stale signal.
  implementation_approach: >
    Reorder truncation relative to assistant-message construction (F3); replace
    substring checks with structured-field checks (F7); add single-mode signal
    clearing or a startup warning (F11). Exact structured signals decided in
    implementation.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "F3 truncation reorder; F7 structured error/malformed classification; F11 single-mode signal clearing/warning"
      functions_affected:
        - "run_phase"
        - "_is_mcp_error"
        - "main_async"

testing_requirements:
  test_cases:
    - scenario: "Model turn issues >10 tool calls"
      expected_result: "No API rejection; conversation valid; phase continues"
    - scenario: "Benign result/summary contains 'Input validation error' or '[TOOL_CALLS]'"
      expected_result: "Not misclassified as error or malformed"
    - scenario: "Single --mode worker/reviewer with stale work-complete.txt"
      expected_result: "No false completion on iteration 1"
  validation_criteria:
    - "Genuine MCP errors still classified and counted"
    - "Loop-mode behavior unchanged"

implementation:
  implementation_steps:
    - step: "Claude Code implements per T04 prompt-d2f6b8c4; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py to prior version"

notes: >
  Execution path: Claude Code. Groups F3 (high), F7 (medium), F11 (medium). All
  source changes.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-06-26"
    changes:
      - "Implemented and verified against source; change closed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
