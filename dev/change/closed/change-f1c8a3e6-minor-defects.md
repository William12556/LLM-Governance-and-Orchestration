Created: 2026 June 26

```yaml
change_info:
  id: "change-f1c8a3e6"
  title: "Minor orchestrator fixes: continue off-by-one, reviewer framing, audit counting, context-window resolution"
  date: "2026-06-26"
  author: "William Watson"
  status: "verified"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-f1c8a3e6"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-f1c8a3e6"
  description: >
    Remediate proposal-f9a2c41b findings F15, F16, F17, F18: continue-prompt
    off-by-one, inconsistent reviewer framing, inconsistent audit item counting,
    and arbitrary context-window resolution.

scope:
  summary: >
    Correct the continue-prompt iteration accounting, make reviewer framing
    consistent with the runtime header, unify audit item counting, and resolve
    the context window to the exact model directory with a config override.
  affected_components:
    - name: "orchestrator (continue prompt, review_task, audit counting, resolve_context_window)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
      change_type: "modify"
    - name: "AEL config (context override)"
      file_path: "ai/ael/config.yaml"
      change_type: "modify"
  out_of_scope:
    - "Budget estimate correction (change-b9d2f4a7, F8)"
    - "Reviewer decision handling (change-a1d4f7e2)"

rational:
  problem_statement: >
    F15: the post-'y' compensation increments past one iteration number, so the
    loop delivers one fewer cycle than promised. F16: review_task omits the [AEL
    RUNTIME CONTEXT] header and single-mode reuses the worker task text. F17:
    audit snapshot/scope counting and the unchecked-item gate use different
    expressions. F18: resolve_context_window returns an arbitrary glob match and
    config.json overstates the usable window.
  proposed_solution: >
    F15: fix the bound-check/compensation. F16: prepend the runtime header to
    review_task and use a consistent review instruction across modes. F17: use a
    single shared parser for audit-index items. F18: match the exact model
    directory and allow a per-model supported-context override in config.yaml.
  benefits:
    - "Continue prompt delivers the promised cycle count"
    - "Consistent reviewer framing across loop and single modes"
    - "Audit counts agree across formatting variations"
    - "Context window reflects the vendor-supported value"
  risks:
    - risk: "Context override misconfigured per model"
      mitigation: "Document the config field; fall back to detected value when override absent"

technical_details:
  current_behavior: >
    Post-'y' compensation skips an iteration number (F15). review_task lacks the
    runtime header; single-mode reviewer gets worker task text (F16). Two
    different audit item-counting expressions (F17). resolve_context_window
    returns glob(...)[0]; config.json overstates the window (F18).
  proposed_behavior: >
    The continue prompt delivers exactly the promised cycles. Reviewer framing
    includes the runtime header in both modes. One shared parser counts audit
    items. The context window resolves to the exact model directory with a config
    override.
  implementation_approach: >
    Fix the continue accounting (F15); prepend the runtime header and unify the
    review instruction (F16); extract a shared audit item parser (F17); match the
    exact model directory and add a config override field (F18). Exact field name
    and matching logic decided in implementation.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "F15 continue accounting; F16 reviewer framing/runtime header; F17 shared audit item parser; F18 exact-dir context resolution + config override read"
      functions_affected:
        - "run_loop"
        - "resolve_context_window"
    - component: "ralph-review recipe"
      file: "ai/ael/recipes/ralph-review.yaml"
      change_summary: "F16 — consistent review instruction referencing the runtime header"
    - component: "AEL config"
      file: "ai/ael/config.yaml"
      change_summary: "F18 — optional per-model supported-context override field"

testing_requirements:
  test_cases:
    - scenario: "User answers 'y' to continue"
      expected_result: "Exactly the promised additional cycles run"
    - scenario: "Review in loop mode and single mode"
      expected_result: "Runtime header present in both; review instruction consistent"
    - scenario: "Audit-index items with varied indentation/formatting"
      expected_result: "Snapshot/scope and unchecked-item counts agree"
    - scenario: "Context override set for a model"
      expected_result: "Override honoured; exact model directory matched"
  validation_criteria:
    - "Absent override falls back to detected value"
    - "No regression to standard loop iteration counting"

implementation:
  implementation_steps:
    - step: "Claude Code implements per T04 prompt-f1c8a3e6; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py, ralph-review.yaml, and config.yaml to prior version"

notes: >
  Execution path: Claude Code. Groups F15 (low), F16 (low), F17 (low), F18 (low).
  The config.yaml override is configuration and is excluded from propagation; F18
  exact-dir match, F15, F16, and F17 are source changes.

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
