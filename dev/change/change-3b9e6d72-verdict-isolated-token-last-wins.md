Created: 2026 July 29

```yaml
change_info:
  id: "change-3b9e6d72"
  title: "Verdict parsing accepts an isolated SHIP/REVISE line, last occurrence winning; leading-token rule retained as fallback"
  date: "2026-07-29"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-3b9e6d72"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-3b9e6d72"
  description: >
    Make a reviewer verdict readable wherever the model naturally places it, so
    that a SHIP is reachable at all.

scope:
  summary: >
    Rewrite _normalize_verdict as two ordered passes: an isolated-verdict-line
    scan preferring the last match, then the existing leading-token rule as a
    fallback. Add _is_verdict_line and _strip_verdict helpers, and switch the
    fallback REVISE feedback extraction from an unconditional leading-token drop
    to _strip_verdict.
  affected_components:
    - name: "orchestrator (_normalize_verdict, _is_verdict_line, _strip_verdict)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (run_loop fallback feedback persistence)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Grammar-constrained decoding via guided_grammar — see alternatives_considered; deferred, not rejected"
    - "ralph-review.yaml verdict-format wording — the parser is being widened to accept what models emit, so tightening the instruction is not required"
    - "Reviewer criterion 6 calibration — remediation §5.3, correctly deferred until this defect no longer confounds the evidence"
    - "review-result.txt handling — that path already carries a bare verdict and is unaffected"

rational:
  problem_statement: >
    _normalize_verdict reads the leading token only. A reviewer that explains
    before concluding has its verdict read as the first word of its prose and
    downgraded to REVISE, so no such reviewer can ever ship. Every end-to-end
    verification path in the framework sits behind a reachable SHIP.
  proposed_solution: >
    Discriminate on isolation rather than on position. A line that is nothing
    but a verdict token, once decoration is stripped, is a declaration; a
    verdict word inside a sentence is not. Prefer the last such line, which is
    where a conclusion appears. Keep the leading-token rule as a second pass so
    the single-line 'SHIP: ...' form continues to work.
  alternatives_considered:
    - option: "Accept a trailing verdict token as well as a leading one (backlog option 1)"
      reason_rejected: >
        Cheapest, but reintroduces exactly the ambiguity the leading-token rule
        was designed to prevent: a review ending '...otherwise I would say SHIP'
        would ship. Isolation is a stronger discriminator than position at
        comparable cost.
    - option: "Grammar-constrained decoding via guided_grammar (backlog option 3)"
      reason_rejected: >
        The durable answer, and the one consistent with the framework's
        preference for enforcement over instruction — it makes a malformed
        verdict impossible rather than recoverable. Deferred rather than
        rejected: guided_grammar_enabled and guided_grammar exist in the oMLX
        config but are unset and unexercised, and adopting them now would couple
        a loop-termination fix to an unvalidated inference-layer feature at the
        moment the loop cannot be tested. Revisit once a SHIP is reachable and
        the smoke harness can demonstrate the difference.
    - option: "Take the first isolated verdict line rather than the last"
      reason_rejected: >
        A review that restates the prior cycle's REVISE before giving its own
        conclusion would then return the wrong verdict. The conclusion is at the
        end.
    - option: "Require the verdict on the final non-empty line"
      reason_rejected: >
        Brittle against trailing whitespace, sign-off lines and markdown rules.
        Last-match is the same intent without the fragility.
  benefits:
    - "A SHIP becomes reachable, unblocking every end-to-end verification path in the framework"
    - "REVISE feedback bodies are no longer mangled by an inapplicable leading-token strip"
    - "Reviewer-quality evidence is no longer confounded by parse failures presenting as judgement failures"
    - "Failure direction preserved: anything unparseable still yields REVISE, so the change cannot cause a spurious ship"
  risks:
    - risk: "A reviewer quotes a bare 'SHIP' on its own line while arguing against shipping"
      mitigation: >
        Possible in principle. The isolation test requires a line containing
        nothing else, which quoting conventions (blockquote markers aside) rarely
        produce, and the reviewer's own concluding verdict would follow it and
        win as the last match.
    - risk: "Markdown headings such as '## SHIP' are now read as verdicts"
      mitigation: "Intended — a heading of that form is a declaration in every observed case."
    - risk: "The last-match rule reverses a reviewer that concludes early and then elaborates"
      mitigation: "Not observed. Reviewers place the verdict last, which is the form that motivated this change."

technical_details:
  current_behavior: >
    _normalize_verdict strips non-alphabetic characters from the first
    whitespace-delimited token, uppercases it, and returns SHIP on an exact
    match, REVISE otherwise. The fallback feedback path splits the reviewer
    message once on whitespace and treats everything after the first token as
    the feedback body.
  proposed_behavior: >
    Pass 1 scans lines; any line reducing to exactly SHIP or REVISE under
    non-alphabetic stripping is a verdict declaration, and the last one wins.
    Pass 2, reached only when pass 1 finds nothing, applies the existing
    leading-token rule. REVISE remains the default for empty, whitespace-only
    and verdict-free input. _strip_verdict removes isolated verdict lines when
    present and otherwise falls back to dropping the leading token.
  implementation_approach: >
    1. Add _is_verdict_line(line) -> str | None returning the token when a line
    reduces to exactly SHIP or REVISE.
    2. Rewrite _normalize_verdict as the two passes above, documenting why pass
    1 exists and why REVISE remains the default.
    3. Add _strip_verdict(text) -> str removing isolated verdict lines, falling
    back to the leading-token drop when none is present.
    4. In run_loop's fallback REVISE persistence, replace the inline
    split(None, 1) with _strip_verdict.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: >
        _is_verdict_line and _strip_verdict added; _normalize_verdict rewritten
        as two ordered passes; fallback feedback extraction switched to
        _strip_verdict.
      functions_affected:
        - "_is_verdict_line (new)"
        - "_normalize_verdict"
        - "_strip_verdict (new)"
        - "run_loop"
      classes_affected: []
  data_changes: []
  interface_changes:
    - "review-feedback.txt written by the fallback path no longer has its first word removed when the verdict was stated on its own line"

dependencies:
  internal:
    - component: "run_loop verdict resolution and the audit / read-evidence / pytest SHIP gates"
      impact: "Unchanged. They now receive an accurate verdict and can therefore run at all."
    - component: "F12 stall detection"
      impact: "Indirectly corrected — it was comparing successive mangled feedback bodies"
  external: []
  required_changes: []

testing_requirements:
  test_approach: >
    Direct exercise of the extracted helpers across the observed and adversarial
    forms, followed by a live Ralph Loop run once available.
  test_cases:
    - scenario: "'SHIP', 'ship', '**SHIP**', 'SHIP.'"
      expected_result: "SHIP"
    - scenario: "'SHIP: the code looks good' (leading-token form)"
      expected_result: "SHIP — pass 2"
    - scenario: "Multi-line reasoning ending in a bare SHIP (run a2d10058 form)"
      expected_result: "SHIP — pass 1"
    - scenario: "Multi-line reasoning ending in a bare REVISE"
      expected_result: "REVISE"
    - scenario: "'I considered whether to SHIP this but the tests fail.'"
      expected_result: "REVISE — no isolated line, leading token is 'I'"
    - scenario: "'First pass said REVISE.' then a later isolated SHIP"
      expected_result: "SHIP — last isolated line wins"
    - scenario: "Empty, whitespace-only, or no verdict present"
      expected_result: "REVISE"
    - scenario: "_strip_verdict on trailing-verdict REVISE"
      expected_result: "Verdict line removed; body intact"
    - scenario: "_strip_verdict on 'REVISE: fix the import'"
      expected_result: "'fix the import'"
  regression_scope:
    - "review-result.txt precedence path unchanged"
    - "Default-to-REVISE behaviour unchanged for every input that previously produced it, except the trailing-verdict SHIP this change exists to correct"
    - "SHIP gates unchanged"
  validation_criteria:
    - "ai/ael/src/orchestrator.py has no syntax errors"
    - "No input that previously returned SHIP now returns REVISE"
    - "Unparseable input still returns REVISE"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Claude Desktop implements directly via file tools (no Claude Code, no AEL) per William Watson's instruction, 2026-07-29"
      owner: "Claude Desktop (Opus 5)"
  rollback_procedure: "git revert the commit."
  deployment_notes: >
    Downstream propagation via bin/propagate.sh. This change should reach
    downstream projects before any further AEL run there, as it is the reason
    those runs cannot terminate on SHIP.

verification:
  implemented_date: "2026-07-29"
  implemented_by: "Claude Desktop (Opus 5)"
  verification_date: "2026-07-29"
  verified_by: "Claude Desktop (Opus 5) — unit-level"
  test_results: >
    Fifteen cases exercised against the extracted helpers, all passing,
    including the exact reviewer opening from run a2d10058 and the adversarial
    mid-sentence mention. _strip_verdict verified on both verdict placements.
  issues_found:
    - "Not verified against a live model. A run reaching an actual SHIP remains outstanding and is the gating verification for this change and for change-f5c28a04."

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-f5c28a04"
      relationship: "unblocks — end-to-end verification of that change requires a reachable SHIP"
  related_issues:
    - issue_ref: "issue-3b9e6d72"
      relationship: "resolves"

notes: >
  Option 2 of three, selected by William Watson on 2026-07-29. Option 3,
  grammar-constrained decoding, remains the durable answer and is recorded in
  alternatives_considered as deferred rather than rejected; it should be
  reconsidered once the smoke harness can demonstrate a terminating loop.

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial change document — implemented directly from dev/remediation-2026-07-29.md §2.1, option 2"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
