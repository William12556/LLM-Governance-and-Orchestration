Created: 2026 July 15

# Change b5e9d240 — Add opt-in efficiency controls to the AEL orchestrator

```yaml
change_info:
  id: "change-b5e9d240"
  title: "Add opt-in, config-gated controls: output-token cap, tool-result truncation, tactical_brief strictness"
  date: "2026-07-15"
  author: ""
  status: "proposed"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b5e9d240"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-b5e9d240"
  description: "Three absent opt-in efficiency/robustness controls (issue-b5e9d240; report section 5.0 items 2, 4, 7)."

scope:
  summary: >
    Add three independent, config-gated, default-off controls to orchestrator.py, plus the
    corresponding config.yaml keys. When unset, behaviour is identical to today.
  affected_components:
    - name: "_completion_with_retry"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "run_phase"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "extract_tactical_brief"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "config"
      file_path: "ai/ael/config.yaml"
      change_type: "modify"
  affected_designs:
    - design_ref: "dev/design/design-ael-orchestrator.md"
      sections: []
  out_of_scope:
    - "Item 3 — tool-schema deduplication (investigation-first, no change yet)."
    - "Item 5 — reviewer downsizing (runtime --reviewer-model flag; no code change)."
    - "Item 6 — speculative decoding (deferred; model incompatibility)."
    - "Context-window tier-ordering redesign."

rational:
  problem_statement: >
    The orchestrator cannot cap completion output, bound appended tool-result size, or require a
    tactical_brief for ael-profile runs. See issue-b5e9d240.
  proposed_solution: >
    Add three config keys (all default null/false) and the minimal code to honour them:
    max_completion_tokens, max_tool_result_chars, strict_tactical_brief. Each is independent
    and off by default, so the change is backward compatible.
  alternatives_considered:
    - option: "Token-based tool-result truncation."
      reason_rejected: "Requires a tokenizer dependency; character-based truncation is simpler and deterministic."
    - option: "Make the tactical_brief guard fail-fast by default."
      reason_rejected: "Would break intentional raw-document workflows; strictness must be opt-in."
    - option: "Hard-code a max_tokens value."
      reason_rejected: "A fixed cap risks truncating legitimate output; operator-set config with a null default is safer."
  benefits:
    - "Bounds worst-case output latency (opt-in)."
    - "Bounds in-phase context growth (opt-in)."
    - "Prevents silent, expensive raw-document fallback (opt-in)."
  risks:
    - risk: "A too-low max_completion_tokens or max_tool_result_chars could truncate needed output/context."
      mitigation: "Both default to null (disabled); operators choose values deliberately."

technical_details:
  current_behavior: >
    create() is called without max_tokens; tool-result content is appended to messages in full;
    a missing/malformed tactical_brief warns and falls back to the raw document.
  proposed_behavior: >
    When set: max_completion_tokens is passed as max_tokens to create(); tool-result content
    longer than max_tool_result_chars is head/tail truncated with an elision marker before
    append; with strict_tactical_brief true and target_profile ael, an absent/malformed brief
    fails fast with a clear error instead of falling back.
  implementation_approach: >
    Read the three keys from config with safe defaults. Apply each at its site:
    _completion_with_retry (cap), run_phase tool-result append (truncation), extract_tactical_brief
    or its caller (strict guard). Add the three keys to config.yaml under the existing execution
    section with null/false defaults and explanatory comments.
  code_changes:
    - component: "_completion_with_retry"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "Pass max_tokens=max_completion_tokens to create() when the config value is non-null."
      functions_affected:
        - "_completion_with_retry"
      classes_affected: []
    - component: "run_phase"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "Head/tail truncate tool-result content exceeding max_tool_result_chars before appending to messages."
      functions_affected:
        - "run_phase"
      classes_affected: []
    - component: "extract_tactical_brief"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "When strict_tactical_brief is true and profile is ael, fail fast on missing/malformed brief instead of raw fallback."
      functions_affected:
        - "extract_tactical_brief"
      classes_affected: []
    - component: "config"
      file: "ai/ael/config.yaml"
      change_summary: "Add max_completion_tokens (null), max_tool_result_chars (null), strict_tactical_brief (false) with comments."
      functions_affected: []
      classes_affected: []
  interface_changes:
    - interface: "config.yaml execution section"
      change_type: "addition"
      details: "Three new optional keys; all default to disabled."
      backward_compatible: "yes"

testing_requirements:
  test_approach: >
    Verify defaults preserve current behaviour (no max_tokens sent; no truncation; brief warn+fallback).
    Verify each control activates when its key is set. Confirm py_compile clean.
  test_cases:
    - scenario: "All keys unset."
      expected_result: "Behaviour identical to pre-change: no max_tokens, no truncation, warn+fallback on missing brief."
    - scenario: "max_tool_result_chars set below a large tool result."
      expected_result: "Appended content is head/tail truncated with an elision marker."
    - scenario: "strict_tactical_brief true, ael profile, brief absent."
      expected_result: "Fails fast with a clear error; no raw-document fallback."
  regression_scope:
    - "AEL runs with default config must be unchanged."
  validation_criteria:
    - "Defaults disabled; current behaviour preserved."
    - "py_compile passes on orchestrator.py."

implementation:
  effort_estimate: "1-2 hours"
  implementation_steps:
    - step: "Add the three config keys with disabled defaults and comments."
      owner: "Tactical Domain (Claude Code / AEL)"
    - step: "Wire each key at its site with a safe default when the key is absent."
      owner: "Tactical Domain (Claude Code / AEL)"
  rollback_procedure: "Revert the commit; remove the three keys and their call sites."

traceability:
  related_issues:
    - issue_ref: "issue-b5e9d240"
      relationship: "resolves"

notes: "Evidence and routing: dev/reports/report-omlx-ael-efficiency-2026-07-15.md section 5.0."

version_history:
  - version: "1.0"
    date: "2026-07-15"
    author: ""
    changes:
      - "Initial change proposal"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

Copyright (c) 2026 William Watson. MIT License.
