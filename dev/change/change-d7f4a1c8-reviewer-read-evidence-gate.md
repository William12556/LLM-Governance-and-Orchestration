Created: 2026 July 16

```yaml
change_info:
  id: "change-d7f4a1c8"
  title: "Reviewer read-evidence gate: require deliverable reads before SHIP"
  date: "2026-07-16"
  author: "William Watson"
  status: "proposed"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-d7f4a1c8"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-d7f4a1c8"
  description: >
    Prevent the ralph loop accepting SHIP when the reviewer did not inspect the
    deliverables, by adding a deterministic orchestrator-side gate.

scope:
  summary: >
    In run_loop, before accepting a ralph-path SHIP, verify the reviewer read
    each deliverable file named in work-summary.txt; override SHIP->REVISE on any
    unread deliverable. Surface reviewer read paths from run_phase.
  affected_components:
    - name: "orchestrator (run_phase, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  out_of_scope:
    - "Audit-path SHIP gate (retains its own coverage gate)"
    - "Worker-phase behaviour"
    - "Tier 2 grounded-citation validation"
    - "Tier 3 heterogeneous reviewer model (change-a7d3f8b1)"
    - "Counting grep/search as inspection evidence"

rational:
  problem_statement: >
    Verdict acceptance depends only on the reviewer's final-message token. A
    reviewer that reads nothing can still SHIP. Instruction in ralph-review.yaml
    is not enforcement.
  proposed_solution: >
    Deterministic gate: deliverable set = files referenced in work-summary.txt
    that exist on disk; reviewer read set = read/read_file/read_text_file paths
    from the review phase. If verdict is SHIP and any deliverable is unread,
    override to REVISE and write feedback naming the unread file(s). Normalise
    paths before comparison. No-op when the deliverable set is empty.
  benefits:
    - "Confabulated SHIP without inspection is caught deterministically"
    - "Reuses the audit SHIP-gate override pattern (low risk, familiar shape)"
    - "Model-independent - not defeated by a reviewer ignoring recipe instructions"
  risks:
    - risk: "Path-form mismatch (absolute vs relative) causes false REVISE"
      mitigation: "os.path.abspath-normalise both sets before comparison"
    - risk: "Deliverable extraction misses a file, weakening the gate"
      mitigation: "Reuse the proven work-summary path extraction from _run_syntax_gate; on empty set, no-op rather than block"
    - risk: "Reviewer inspects via grep only and is failed"
      mitigation: "Accepted by design - read-family inspection required; conservative per 'err toward REVISE'"

technical_details:
  current_behavior: >
    run_phase tracks read-family calls in _read_counts but does not return them.
    run_loop accepts SHIP from _normalize_verdict with no deliverable cross-check
    on the ralph path.
  proposed_behavior: >
    run_phase surfaces the review-phase read path set. run_loop computes the
    deliverable set and, on a ralph-path SHIP, overrides to REVISE if any
    deliverable was unread; otherwise ships.
  implementation_approach: >
    Exact surfacing mechanism left to implementation (return value or phase-scoped
    collector). Gate block mirrors the existing audit SHIP-gate override in
    run_loop and is guarded to the non-audit recipe set.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "Surface reviewer read set from run_phase; add read-evidence SHIP gate in run_loop (non-audit path); shared deliverable-extraction helper"
      functions_affected:
        - "run_phase"
        - "run_loop"

testing_requirements:
  test_cases:
    - scenario: "SHIP, deliverable never read"
      expected_result: "Overridden to REVISE; feedback names the file"
    - scenario: "SHIP, all deliverables read"
      expected_result: "Ships"
    - scenario: "Deliverable set empty/unresolvable"
      expected_result: "Gate no-op; SHIP allowed; logged"
    - scenario: "Deliverable read via absolute path, summary uses relative"
      expected_result: "No false REVISE"
    - scenario: "Audit loop SHIP"
      expected_result: "Existing coverage gate unchanged"
  validation_criteria:
    - "No change to worker-phase behaviour"
    - "Audit path unaffected"

implementation:
  implementation_steps:
    - step: "Claude Code implements per prompt-d7f4a1c8; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py to prior version"

notes: >
  Execution path: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md 5.0). Tier 1 only. Exact surfacing mechanism left to
  implementation; no scope beyond the documented approach.

version_history:
  - version: "1.0"
    date: "2026-07-16"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
