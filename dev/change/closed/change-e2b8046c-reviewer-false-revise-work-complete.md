Created: 2026 June 27

```yaml
change_info:
  id: "change-e2b8046c"
  title: "Worker excludes orchestrator-managed signal files from work-summary (e2b8046c Option B)"
  date: "2026-06-26"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-e2b8046c"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-e2b8046c"
  description: >
    Remediate issue-e2b8046c: the reviewer issued false REVISE every cycle
    because the worker named work-complete.txt in work-summary.txt and the
    reviewer then tried to verify a file run_loop had already cleared. Resolved
    via the issue's Option B (worker recipe), which requires no Python source
    change.

scope:
  summary: >
    Instruct the worker, in ralph-work.yaml, to exclude orchestrator-managed
    signal files from the work-summary deliverable list so the reviewer never
    attempts to verify a cleared signal file.
  affected_components:
    - name: "ralph-work recipe"
      file_path: "ai/ael/recipes/ralph-work.yaml"
      change_type: "modify"
  out_of_scope:
    - "run_loop signal-clearing behavior (unchanged; Option C not pursued)"
    - "ralph-review.yaml verification instruction (unchanged; Option A not pursued)"

rational:
  problem_statement: >
    run_loop clears work-complete.txt before the review phase; the worker listed
    work-complete.txt in work-summary.txt; the reviewer verified every named
    file, found it absent, and issued REVISE, preventing convergence.
  proposed_solution: >
    Option B: the worker's WORK SUMMARY instruction excludes orchestrator-managed
    signal files (work-complete.txt, iteration.txt, review-*.txt, .ralph-*,
    RALPH-BLOCKED.md) from the deliverable list. The reviewer then verifies only
    task outputs.
  alternatives_considered:
    - option: "Option A — reviewer recipe ignores signal files"
      reason_rejected: "Option B places the exclusion at the source of the summary; reviewer recipe left unchanged"
    - option: "Option C — defer/suppress clearing work-complete.txt in run_loop"
      reason_rejected: "Requires Python source change; recipe-level fix is sufficient and lower risk"
  benefits:
    - "Loop converges to SHIP for one-pass tasks"
    - "No Python source change"
    - "Model-agnostic"
  risks:
    - risk: "Worker still names a signal file despite the instruction"
      mitigation: "Instruction is explicit and enumerated; reviewer SHIP gate remains for genuine gaps"

technical_details:
  current_behavior: >
    Worker WORK SUMMARY listed all created files, including work-complete.txt.
    Reviewer verified each, failing on the cleared signal file.
  proposed_behavior: >
    Worker WORK SUMMARY lists only task outputs; orchestrator-managed signal
    files are explicitly excluded.
  implementation_approach: >
    Add an exclusion clause to the WORK SUMMARY section of ralph-work.yaml
    instructions.
  code_changes:
    - component: "ralph-work recipe"
      file: "ai/ael/recipes/ralph-work.yaml"
      change_summary: "WORK SUMMARY: do not list orchestrator-managed signal files as deliverables; list only task outputs"

testing_requirements:
  test_cases:
    - scenario: "One-pass-completable loop task"
      expected_result: "SHIP within 1-2 iterations"
    - scenario: "Reviewer feedback inspection"
      expected_result: "No reference to work-complete.txt"
    - scenario: "Genuinely incomplete task"
      expected_result: "REVISE (SHIP gate not regressed)"
  validation_criteria:
    - "Worker summary lists only task outputs"

implementation:
  implementation_steps:
    - step: "Implemented in ralph-work.yaml v1.4.0"
      owner: "Claude Code"
  rollback_procedure: "git revert ralph-work.yaml to prior version"

verification:
  implemented_date: "2026-06-26"
  implemented_by: "Claude Code"
  verification_date: "2026-06-26"
  verified_by: "William Watson"
  test_results: >
    Verified against source: ralph-work.yaml v1.4.0 WORK SUMMARY section excludes
    orchestrator-managed signal files; version history records "Supports
    issue-e2b8046c resolution".

notes: >
  Execution path: Claude Code. Recipe-level fix (Option B); no Python source
  change. Change document authored retroactively to record the implemented fix
  and restore issue-change-prompt coupling.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Authored to document implemented Option B fix (ralph-work.yaml v1.4.0); verified against source; change closed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
