Created: 2026 July 17

```yaml
change_info:
  id: "change-5bdc2d9b"
  title: "Orchestrator-native pytest SHIP gate for AEL (ael target profile)"
  date: "2026-07-17"
  author: "William Watson"
  status: "proposed"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-5bdc2d9b"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-5bdc2d9b"
  description: >
    Add deterministic, orchestrator-native pytest execution and SHIP
    enforcement for the ael target profile, mirroring the existing
    _run_syntax_gate subprocess/injection mechanism and the read-evidence
    gate's deterministic SHIP override (issue-d7f4a1c8/change-d7f4a1c8).

scope:
  summary: >
    Add _run_pytest_gate(state_dir, log, project_root) to orchestrator.py,
    modeled on _run_syntax_gate: derives test targets from
    _extract_deliverables(), runs pytest via subprocess before the review
    phase, and injects a [TEST GATE: PASS/FAIL] block into review_task.
    Unlike _run_syntax_gate (context-injection only), this gate additionally
    adds a deterministic SHIP->REVISE override in run_loop when the gate
    reports FAIL, regardless of the reviewer's own verdict — closing the
    same instruction-is-not-enforcement gap the read-evidence gate closed
    for deliverable reads.
  affected_components:
    - name: "orchestrator (_run_pytest_gate new function, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "claude_code / claude_omlx target profiles — already addressed via the PostToolUse hook (ai/skills/validation/run-tests.md, governance 9.12); Claude Code's own harness executes pytest natively, no orchestrator involvement"
    - "Linter or other static-analysis gates (ruff, etc.) — considered and explicitly deferred; no follow-on issue opened per 2026-07-17 decision"
    - "Promoting _run_syntax_gate itself to a blocking (SHIP-overriding) gate — it currently shares this change's premise (informs but does not enforce) but is a separate, pre-existing gap not introduced by this change"
    - "Audit-path (tactical-led audit loop) SHIP gate — retains its own coverage/scope gate, unaffected"
    - "Test target resolution beyond the tests/<component>/ layout convention (governance P06 §1.7.3/§1.7.7) — same heuristic and same limitation as the Claude Code hook script"
    - "Full-suite (iteration-level) validation — this gate is file/deliverable-scoped (targeted), matching governance P06 §1.7.15's file-level vs iteration-level distinction"

rational:
  problem_statement: >
    AEL has no test-execution capability in any form. Neither worker nor
    reviewer can invoke pytest — the only registered MCP servers for the ael
    profile are filesystem and mcp-ripgrep (ai/ael/config.yaml). T04 v1.11
    and governance P06 §1.7.15 now require pytest execution on completion,
    but nothing enforces this for target_profile: ael specifically.
  proposed_solution: >
    Do not grant the model execution capability at all. The orchestrator
    already has a precedent for exactly this shape of work: _run_syntax_gate
    runs py_compile via subprocess and injects a result block for the
    reviewer, with no MCP tool and no model involvement. Add
    _run_pytest_gate following the same shape, and additionally make it
    enforce (SHIP override on FAIL) rather than merely inform, using the
    read-evidence gate's override pattern as the enforcement precedent.
  alternatives_considered:
    - option: "General shell/exec MCP tool granted to the AEL worker and/or reviewer"
      reason_rejected: >
        Expands model-controlled attack surface; AEL's current
        filesystem+ripgrep-only toolset appears to be a deliberate
        containment boundary (bounded autonomy), not an oversight. Also
        remains model-discretionary — the same instruction-is-not-enforcement
        gap as the original problem, since the model must still choose to
        call it.
    - option: "Narrow pytest-only MCP server (constrained exec, no arbitrary commands)"
      reason_rejected: >
        Smaller attack surface than general exec, but still a new server to
        build, sandbox, and maintain, and still model-invoked/discretionary.
        The orchestrator can already run subprocess deterministically without
        granting the model anything, per the _run_syntax_gate precedent — no
        new server closes a gap that already has a zero-new-surface solution.
    - option: "Fold a linter gate (e.g. ruff) into this change alongside pytest"
      reason_rejected: >
        Deferred by decision (2026-07-17). Distinct design questions
        (ruleset, blocking vs advisory) without governance precedent yet;
        keeps this change narrowly scoped per project convention (see
        change-d7f4a1c8's explicit out-of-scope precedent).
  benefits:
    - "Deterministic — not dependent on the reviewer choosing to run or honor a test result"
    - "Zero new model-controlled capability or attack surface"
    - "Reuses two already-proven patterns (subprocess/injection mechanism; SHIP-override mechanism) rather than introducing a third"
    - "Architectural symmetry with claude_code/claude_omlx: every target profile now gets harness-executed, non-model-discretionary pytest validation, implemented natively to each harness"
  risks:
    - risk: "_extract_deliverables()-derived test target misses a modified test-relevant file"
      mitigation: "No-op (not block) when no test-relevant deliverables resolve — same conservative default as the read-evidence gate's empty-set no-op; logged at WARNING, not silently skipped"
    - risk: "pytest run adds wall-clock cost to every loop iteration touching tests/ or src/"
      mitigation: "Targeted invocation only (resolved test dir/file, not full suite) keeps cost bounded; scoped to target_profile: ael"
    - risk: "pytest not installed, or project has no tests/ directory"
      mitigation: "Wrapped in try/except mirroring _run_syntax_gate's per-file exception handling; treated as UNCHECKED/no-op, never as a blocking FAIL"
    - risk: "False REVISE from a flaky or environment-dependent test unrelated to the actual change"
      mitigation: "Accepted by design, consistent with the read-evidence gate's 'err toward REVISE' conservative default (issue-d7f4a1c8); flagged here as a known limitation, not solved by this change"

technical_details:
  current_behavior: >
    orchestrator.py has no test-execution mechanism for any profile.
    _run_syntax_gate demonstrates the subprocess+injection mechanism but
    only for py_compile, and only as reviewer context — a FAIL block is
    shown to the reviewer but nothing prevents SHIP despite it.
  proposed_behavior: >
    _run_pytest_gate runs pytest against deliverable-derived test targets
    before the review phase and injects a [TEST GATE: PASS/FAIL] block into
    review_task, at the same call site as _run_syntax_gate. Additionally, a
    new override in run_loop sets the verdict to REVISE (with the gate's
    output as feedback) whenever the gate reports FAIL, regardless of the
    reviewer's own verdict — the enforcement step _run_syntax_gate itself
    still lacks (out of scope here; see scope.out_of_scope).
  implementation_approach: >
    1. Add _run_pytest_gate(state_dir, log, project_root) near
    _run_syntax_gate: call _extract_deliverables(state_dir, log); resolve
    test targets using the tests/* direct / src/<component>/*→tests/<component>/
    heuristic (same as ai/skills/validation/run-tests.md §4.0); if no targets
    resolve, return "" (no-op). Otherwise run
    subprocess.run([sys.executable, "-m", "pytest", *targets, "-q"],
    capture_output=True, text=True, cwd=project_root) wrapped in try/except;
    build a [TEST GATE: PASS/FAIL/UNCHECKED] block from returncode and a
    truncated stdout/stderr tail, following _run_syntax_gate's
    result-formatting convention.
    2. Call _run_pytest_gate at the same site as _run_syntax_gate (before
    REVIEW PHASE begins) and prepend/append its block to review_task
    alongside _syntax_result.
    3. In run_loop, alongside the existing read-evidence gate block, add: if
    verdict == SHIP and the pytest gate status is FAIL, override to REVISE
    and write feedback containing the gate's output, naming the failing
    target(s).
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: >
        New _run_pytest_gate function (subprocess/injection pattern
        mirroring _run_syntax_gate); call site added alongside the existing
        _run_syntax_gate call; new SHIP->REVISE override in run_loop keyed
        on pytest gate FAIL status, structured alongside the existing
        read-evidence gate override.
      functions_affected:
        - "_run_pytest_gate (new)"
        - "run_loop"
      classes_affected: []
  data_changes: []
  interface_changes: []

dependencies:
  internal:
    - component: "_extract_deliverables"
      impact: "Reused as-is (no signature change) to derive the deliverable file set for test-target resolution"
  external:
    - library: "pytest"
      version_change: "none — assumed already a project dev dependency; gate treats absence as UNCHECKED, not FAIL"
      impact: "none"
  required_changes: []

testing_requirements:
  test_approach: >
    Inline code review against source (P08 strategic audit), consistent with
    the verification approach used for change-d7f4a1c8. No runtime Ralph
    Loop execution required for verification, though a live-run smoke test
    is recommended before closing given this is the first gate to combine
    subprocess execution with SHIP override in one function.
  test_cases:
    - scenario: "Deliverables include tests/<component>/test_x.py; pytest passes"
      expected_result: "[TEST GATE: PASS] injected into review_task; no SHIP override"
    - scenario: "Deliverables include src/<component>/x.py with an existing tests/<component>/; pytest fails"
      expected_result: "[TEST GATE: FAIL] injected; SHIP overridden to REVISE with gate output as feedback"
    - scenario: "No test-relevant deliverables in work-summary.txt"
      expected_result: "Gate no-op (empty string); no injection; no SHIP override"
    - scenario: "pytest not installed, or resolved target path does not exist"
      expected_result: "Gate reports UNCHECKED, not FAIL; no SHIP override; WARNING logged"
    - scenario: "Reviewer emits SHIP despite a [TEST GATE: FAIL] block present in its own context"
      expected_result: "Orchestrator override still applies — deterministic, independent of whether the reviewer honored the injected block"
    - scenario: "Audit-path (tactical-led audit) loop"
      expected_result: "Gate/override unaffected — scoped to the non-audit (ralph) path only, matching the read-evidence gate's audit_original_count is None guard"
    - scenario: "claude_code / claude_omlx target profile task"
      expected_result: "Unaffected — orchestrator.py's run_loop is the ael execution path only"
  regression_scope:
    - "Existing _run_syntax_gate behaviour and call site unchanged"
    - "Existing read-evidence gate unchanged"
    - "Audit SHIP/coverage/scope gates unchanged"
  validation_criteria:
    - "No change to worker-phase behaviour"
    - "No change to claude_code/claude_omlx execution paths"
    - "py_compile syntax errors introduced by this change: none (independently confirmed via py_compile)"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Claude Code implements per T04 prompt (target_profile: claude_code, manual single pass, per ai/profiles/claude.md \u00a75.0 human review gate)"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py to prior version"
  deployment_notes: >
    No downstream propagation impact beyond the normal ai/ propagation path
    (bin/propagate.sh) once verified and closed.

verification:
  implemented_date: ""
  implemented_by: ""
  verification_date: ""
  verified_by: ""
  test_results: ""
  issues_found: []

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-d7f4a1c8"
      relationship: "precedent (SHIP-override pattern reused)"
  related_issues:
    - issue_ref: "issue-5bdc2d9b"
      relationship: "resolves"
    - issue_ref: "issue-d7f4a1c8"
      relationship: "related"

notes: >
  Companion to T04 v1.11 (deliverable.format_requirements pytest instruction)
  and governance 9.12 (P06 §1.7.15 mandatory PostToolUse pytest hook,
  ai/skills/validation/run-tests.md) — those address claude_code/claude_omlx;
  this change addresses the remaining ael target profile gap. Linter/static-
  analysis gate explicitly deferred, no follow-on issue opened (2026-07-17
  decision). _run_syntax_gate's own non-blocking (informational only) design
  is a related but separate pre-existing gap, noted for possible future
  attention, not addressed here.

version_history:
  - version: "1.0"
    date: "2026-07-17"
    author: "William Watson"
    changes:
      - "Initial change document — proposed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
