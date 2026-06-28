Created: 2026 June 28

```yaml
change_info:
  id: "change-7c1d9a4e"
  title: "Auto-select recipe pair on audit-index.md presence in orchestrator"
  date: "2026-06-28"
  status: "proposed"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-7c1d9a4e"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-7c1d9a4e"
  description: >
    Replace the hard-coded Ralph recipe load in main_async with selection keyed
    on the presence of audit-index.md in the state directory.

scope:
  summary: >
    In main_async, branch recipe loading: audit-index.md present -> audit-*.yaml,
    absent -> ralph-*.yaml. Log and print the selected recipe set at startup.
  affected_components:
    - name: "orchestrator"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  out_of_scope:
    - "Explicit --mode audit CLI flag (rejected — keeps orchestrator mode-agnostic)"
    - "config.yaml recipe key"
    - "Recipe file contents"
    - "worker / reviewer / reset mode behaviour (selection runs before the mode branch; reset returns earlier)"
    - "P08 / primer / guide / template documents (Stream B, separate)"

rational:
  problem_statement: >
    Tactical-audit mode requires a manual two-line source edit before launch
    because recipe selection is hard-coded.
  proposed_solution: >
    Detect audit mode by the same signal the existing audit gates use
    (audit-index.md in state_dir) and load the matching recipe pair.
  alternatives_considered:
    - option: "Explicit --mode audit flag"
      reason_rejected: >
        Adds operator surface and a second source of truth that can diverge from
        the state already present.
    - option: "config.yaml recipe key"
      reason_rejected: "Persistent stateful config requiring set/unset per run."
  benefits:
    - "Removes the only manual step from the tactical-audit path"
    - "Single-sourced mode detection (consistent with scope-lock / SHIP gate / archive)"
    - "No new CLI or config surface"
  risks:
    - risk: "Implicit selection (file presence) is invisible to the operator"
      mitigation: "Print and log the selected recipe set at startup"

technical_details:
  current_behavior: >
    main_async loads recipe_dir/ralph-work.yaml and recipe_dir/ralph-review.yaml
    unconditionally before the mode branch.
  proposed_behavior: >
    If audit-index.md exists in state_dir, load audit-work.yaml /
    audit-review.yaml; otherwise load the ralph pair. A startup line reports the
    selected set. reset mode is unaffected (returns before recipe load).
  implementation_approach: >
    Replace the two load lines (leaving the recipe_dir line intact) with an
    if/else on os.path.exists(os.path.join(state_dir, "audit-index.md")), set a
    recipe_set label, then console.print and log.info the label. state_dir, log,
    and console are all in scope at that point.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: >
        Replace fixed ralph recipe load with audit-index.md-gated selection plus
        startup recipe-set log line.
      functions_affected:
        - "main_async"
      classes_affected: []

testing_requirements:
  test_cases:
    - scenario: "audit-index.md present in state_dir, --mode loop"
      expected_result: "audit-work.yaml / audit-review.yaml loaded; startup prints 'recipe set: audit'"
    - scenario: "audit-index.md absent, --mode loop"
      expected_result: "ralph-work.yaml / ralph-review.yaml loaded; startup prints 'recipe set: ralph'"
    - scenario: "--mode worker / reviewer with audit-index.md present"
      expected_result: "audit recipe applied (selection precedes mode branch)"
    - scenario: "--mode reset"
      expected_result: "No recipe load; behaviour unchanged"
  validation_criteria:
    - "No regression on standard Ralph Loop path when audit-index.md absent"
    - "ai/ael/src/orchestrator.py has no syntax errors"

implementation:
  implementation_steps:
    - step: "Claude Code implements per T04 prompt"
      owner: "Claude Code"
  rollback_procedure: "Revert orchestrator.py to prior version via git"

notes: >
  Variable name rev_recipe retained (matches existing code, not review_recipe).

version_history:
  - version: "1.0"
    date: "2026-06-28"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
