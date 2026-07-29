Created: 2026 July 29

```yaml
change_info:
  id: "change-b7e3d5a9"
  title: "Flat-layout test target resolution; per-cycle reviewer feedback refresh"
  date: "2026-07-29"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b7e3d5a9"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-b7e3d5a9"
  description: >
    Extend _run_pytest_gate target resolution to the flat src/<name>.py
    convention, and clear review-feedback.txt at the start of each review
    phase so later reviewers' feedback reaches the worker.

scope:
  summary: >
    Two independent edits to orchestrator.py. (1) In _run_pytest_gate, when the
    src/<component>/ -> tests/<component>/ directory mapping does not resolve,
    fall back to the flat-module convention: src/<name>.py -> tests/test_<name>.py
    or tests/<name>_test.py, included only when the file exists. (2) Add
    review-feedback.txt to the existing per-cycle clear_state call that runs
    immediately before the review phase.
  affected_components:
    - name: "orchestrator (_run_pytest_gate, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Whole-suite fallback when no per-deliverable target resolves — contradicts change-5bdc2d9b's deliberate file-scoped design (governance P06 §1.7.15 file-level vs iteration-level distinction)"
    - "Removing the `if not existing_feedback:` guard — the per-cycle clear achieves the fix while preserving the guard's intra-cycle purpose"
    - "pytest discovery conventions beyond test_<name>.py and <name>_test.py"
    - "Reviewer calibration under 'Err toward REVISE when uncertain' — separate prompt-engineering question, not a code defect"
    - "F12 stall detection logic itself — it behaves correctly once fed non-stale input"

rational:
  problem_statement: >
    The pytest SHIP gate appears active but silently enforces nothing on flat
    src/ layouts. Separately, reviewer feedback is frozen at cycle 1, so the
    worker never receives later guidance and stall detection compares a file to
    itself, guaranteeing a false BLOCK at stall_threshold iterations.
  proposed_solution: >
    Add one conservative fallback branch to target resolution, and one file
    name to an existing clear_state call. Both are minimal and neither changes
    behaviour where the current logic already resolves correctly.
  alternatives_considered:
    - option: "Run the entire tests/ directory whenever any src/ deliverable is present"
      reason_rejected: >
        Simpler and more robust, but reverses change-5bdc2d9b's explicit
        targeted-scope decision and raises per-iteration wall-clock cost on
        every loop. Rejected as scope reversal, not on technical merit.
    - option: "Remove the `if not existing_feedback:` guard so each cycle overwrites"
      reason_rejected: >
        Achieves the same end but discards the guard's protection within a
        cycle, where an orchestrator gate may already have written specific
        feedback (audit scope, read-evidence, pytest) before the fallback path
        runs. Clearing per cycle is more surgical.
    - option: "Clear review-feedback.txt at the start of the worker phase instead"
      reason_rejected: >
        The worker reads that file during its phase (ralph-work.yaml PROCEDURE
        step 4). Clearing there would destroy the feedback before it is
        consumed.
  benefits:
    - "Pytest enforcement becomes real for flat-layout projects rather than nominally present"
    - "Worker receives current feedback, so the loop can converge on later reviewer guidance"
    - "F12 stall detection measures reviewer repetition rather than orchestrator staleness"
    - "Both edits are additive; no existing resolution path changes behaviour"
  risks:
    - risk: "A project using a different test-file convention still resolves no target"
      mitigation: "Gate no-ops as before; no regression. Conventions beyond the two added are explicitly out of scope."
    - risk: "Clearing feedback per cycle loses the record of what cycle N-1 said"
      mitigation: "The full reviewer message is logged at DEBUG and echoed to console each cycle; state files are working memory, not an audit trail."
    - risk: "A newly-enforcing pytest gate produces REVISE on projects that previously shipped"
      mitigation: "Intended. A gate that silently passes is worse than one that blocks. Failures reflect real test failures."

technical_details:
  current_behavior: >
    _run_pytest_gate maps src/<component>/... to tests/<component>/ via
    parts[1] and os.path.isdir. For src/<name>.py, parts[1] is "<name>.py" and
    the isdir test always fails, so no target resolves and the gate returns "".
    review-feedback.txt is cleared only by the loop-start clear_state at line
    ~1789; the per-cycle clear before the review phase covers only
    work-complete.txt.
  proposed_behavior: >
    When the component-directory mapping does not resolve, the gate additionally
    tests tests/test_<stem>.py and tests/<stem>_test.py, adding whichever
    exists. The per-cycle clear before the review phase also clears
    review-feedback.txt, so each cycle's fallback persistence writes fresh.
  implementation_approach: >
    1. In _run_pytest_gate's src/ branch, wrap the existing isdir mapping in an
    if/else; in the else, derive stem via os.path.splitext(os.path.basename(...))
    and add the first matching candidate file.
    2. Change clear_state(state_dir, "work-complete.txt") immediately before the
    REVIEW PHASE banner to also clear "review-feedback.txt".
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: >
        Flat-layout fallback branch in _run_pytest_gate target resolution;
        review-feedback.txt added to the per-cycle pre-review clear_state call.
      functions_affected:
        - "_run_pytest_gate"
        - "run_loop"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal:
    - component: "_extract_deliverables"
      impact: "Unchanged"
    - component: "clear_state"
      impact: "Reused as-is with an additional argument"
  external: []
  required_changes: []

testing_requirements:
  test_approach: >
    Live Ralph Loop execution against dev/smoke, which reproduces both defects
    deterministically, plus py_compile and isolated resolution testing.
  test_cases:
    - scenario: "Deliverable src/split.py with tests/test_split.py present"
      expected_result: "Target resolves; [TEST GATE: PASS] injected into reviewer task"
    - scenario: "Deliverable src/<component>/x.py with tests/<component>/ present"
      expected_result: "Unchanged — directory mapping resolves as before, fallback not reached"
    - scenario: "Deliverable src/orphan.py with no matching test file"
      expected_result: "No target; gate no-ops as before"
    - scenario: "Deliverable already under tests/"
      expected_result: "Unchanged — direct include"
    - scenario: "Two-cycle loop with differing reviewer feedback"
      expected_result: "Cycle 2 worker reads cycle 1 feedback; cycle 2 review writes its own; stall count does not increment on differing feedback"
    - scenario: "Two-cycle loop with genuinely identical reviewer feedback"
      expected_result: "Stall detection increments correctly — measuring the reviewer, not the file"
  regression_scope:
    - "tests/ direct-include path unchanged"
    - "src/<component>/ directory mapping unchanged"
    - "SHIP override on [TEST GATE: FAIL] unchanged"
    - "Worker-phase reading of review-feedback.txt unchanged (clear happens after the worker phase)"
  validation_criteria:
    - "No change where the component-directory mapping already resolved"
    - "Worker still receives feedback in the cycle following a REVISE"
    - "ai/ael/src/orchestrator.py has no syntax errors"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Claude Desktop implements directly via Filesystem MCP (no Claude Code, no AEL) per William Watson's instruction, 2026-07-29"
      owner: "Claude Desktop (Opus 5)"
  rollback_procedure: "git revert ai/ael/src/orchestrator.py to prior version"
  deployment_notes: >
    Downstream propagation via bin/propagate.sh once verified. The propagate
    exclude-list defects logged in issue-a2f9c4d1 remain unaddressed and are a
    known propagation hazard.

verification:
  implemented_date: "2026-07-29"
  implemented_by: "Claude Desktop (Opus 5)"
  verification_date: "2026-07-29"
  verified_by: "Claude Desktop (independent P08 audit session) — audit-p08-20260729"
  test_results: >
    Verified live and independently, in addition to source inspection. Run
    a2d10058, both loop cycles: '[TEST GATE: PASS]' present in the reviewer
    task with 'pytest gate: running pytest on 1 target(s)' naming
    tests/test_split.py, confirming the flat-module fallback resolves and
    executes for a deliverable src/split.py. Persisted fallback feedback
    differed in length between cycle 1 (684 chars) and cycle 2 (790 chars),
    confirming the per-cycle clear delivers fresh content rather than a
    repeat. The worker's read of the prior cycle's feedback, before the clear
    removes it, was separately confirmed. No defects found against either of
    this change's two fixes.
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-5bdc2d9b"
      relationship: "extends (completes target resolution)"
    - change_ref: "change-c5e1b9d4"
      relationship: "corrects (guard interaction across cycles)"
    - change_ref: "change-a2f9c4d1"
      relationship: "predecessor (enabled the run that surfaced these)"
  related_issues:
    - issue_ref: "issue-b7e3d5a9"
      relationship: "resolves"

notes: >
  Implemented directly by the Strategic Domain rather than delegated, at
  William Watson's instruction. P08 strategic audit by an independent session
  remains outstanding and is required before closure.

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial change document — approved for direct implementation"
  - version: "1.1"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Independently verified by P08 audit audit-p08-20260729 (status: verified, no findings against this change); status approved → verified; change closed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
