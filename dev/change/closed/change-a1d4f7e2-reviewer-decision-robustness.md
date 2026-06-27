Created: 2026 June 26

```yaml
change_info:
  id: "change-a1d4f7e2"
  title: "Reviewer decision robustness: final-message fallback, normalised SHIP, phase-specific terminal write"
  date: "2026-06-26"
  author: "William Watson"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-a1d4f7e2"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-a1d4f7e2"
  description: >
    Remediate proposal-f9a2c41b findings F1, F2, F13: reviewer verdict lost as a
    prose final message, exact-string SHIP brittleness, and the shared
    terminal-write path clobbering work-summary.txt during review.

scope:
  summary: >
    Modify run_phase and run_loop in orchestrator.py so the reviewer decision is
    recognised from review-result.txt or the final message, tolerant of casing
    and decoration, and the review phase does not write work-summary.txt.
  affected_components:
    - name: "orchestrator (run_phase, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
      change_type: "modify"
  out_of_scope:
    - "Worker-phase decision handling"
    - "Stall detection (change-e7a1c3d5)"
    - "Reviewer tool scope (change-c8b3e9a1)"

rational:
  problem_statement: >
    A reviewer verdict stated in prose produces no review-result.txt and is read
    as not-SHIP (F1); decorated/case-variant SHIP fails result == 'SHIP' (F2);
    the shared terminal-write path overwrites work-summary.txt during review
    (F13). Each drives non-converging REVISE.
  proposed_solution: >
    In review phase, parse SHIP/REVISE from the final message as a fallback when
    review-result.txt is absent; normalise the SHIP comparison (uppercase, strip
    non-alphanumerics, test the leading token); make the terminal-write target
    phase-specific so review does not write work-summary.txt.
  benefits:
    - "Effective approvals converge instead of looping"
    - "Worker artifact under review is preserved"
    - "Reviewer output form (prose or file) no longer blocks SHIP"
  risks:
    - risk: "Fallback parser mis-reads an ambiguous final message"
      mitigation: "Prefer review-result.txt when present; fallback only on absence; require a leading SHIP/REVISE token"
    - risk: "Normalisation accepts an unintended token"
      mitigation: "Match only the leading token against an explicit SHIP/REVISE set"

technical_details:
  current_behavior: >
    run_phase terminal branch writes the model text to work-summary.txt and
    returns regardless of phase. SHIP detected by result == 'SHIP' after strip().
  proposed_behavior: >
    Review phase: if review-result.txt is absent, the decision is parsed from the
    reviewer final message; SHIP comparison is normalised; the terminal-write
    target is phase-specific (review does not write work-summary.txt).
  implementation_approach: >
    Exact parsing/normalisation decided in implementation. Changes confined to the
    review-phase paths of run_phase and run_loop, plus any SHIP/REVISE emission
    guidance in ralph-review.yaml.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "F1 final-message fallback parse in review phase; F2 normalised SHIP comparison; F13 phase-specific terminal-write target"
      functions_affected:
        - "run_phase"
        - "run_loop"
    - component: "ralph-review recipe"
      file: "ai/ael/recipes/ralph-review.yaml"
      change_summary: "F2 — confirm reviewer verdict emission guidance is consistent with normalised matching"

testing_requirements:
  test_cases:
    - scenario: "Reviewer states SHIP in prose, no review-result.txt"
      expected_result: "Loop SHIPs"
    - scenario: "Reviewer writes 'SHIP.', '**SHIP**', or 'ship'"
      expected_result: "Resolves to SHIP"
    - scenario: "Review phase completes via final message"
      expected_result: "work-summary.txt unchanged"
    - scenario: "Genuinely incomplete task"
      expected_result: "REVISE (no SHIP-gate regression)"
  validation_criteria:
    - "review-result.txt still takes precedence when present"
    - "No change to worker-phase behavior"

implementation:
  implementation_steps:
    - step: "Claude Code implements per T04 prompt-a1d4f7e2; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py and ralph-review.yaml to prior version"

notes: >
  Execution path: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Groups F1 (high), F2 (high), F13 (medium).
  Distinct from issue-e2b8046c. Exact parsing/normalisation left to
  implementation; no scope beyond the documented approach.

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
