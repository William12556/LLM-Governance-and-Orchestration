Created: 2026 July 17

```yaml
prompt_info:
  id: "prompt-5bdc2d9b"
  task_type: "debug"
  source_ref: "change-5bdc2d9b"
  target_profile: "claude_code"
  date: "2026-07-17"
  iteration: 1
  coupled_docs:
    change_ref: "change-5bdc2d9b"
    change_iteration: 1

context:
  purpose: >
    Add a deterministic pytest gate for the ael target profile: the
    orchestrator runs pytest itself (no MCP tool, no model involvement)
    against deliverable-derived test targets before the review phase, and
    overrides SHIP to REVISE when the gate reports FAIL — closing the gap
    where AEL has no test-execution capability and no enforcement of T04's
    pytest-on-completion instruction.
  integration: >
    ai/ael/src/orchestrator.py - new _run_pytest_gate function (modeled on
    the existing _run_syntax_gate) plus a SHIP override in run_loop (modeled
    on the existing read-evidence gate).
  knowledge_references: []
  constraints:
    - "Non-audit (ralph) path only; do not alter the audit SHIP/coverage/scope gate"
    - "No change to worker-phase behaviour"
    - "No new MCP server, no new tool exposed to worker or reviewer — subprocess call is orchestrator-native only, mirroring _run_syntax_gate exactly"
    - "Reuse _extract_deliverables(state_dir, log) as-is; do not change its signature or behaviour"
    - "Test target resolution: for each deliverable path, if it is under tests/, include it directly; if it is under src/<component>/, include tests/<component>/ only if that directory exists on disk. If no targets resolve, the gate is a no-op (return empty string, no SHIP override) — do not treat 'no targets' as failure"
    - "pytest invocation must be targeted (resolved targets only), never the full suite"
    - "Wrap the subprocess call in try/except mirroring _run_syntax_gate's per-file exception handling; treat a missing pytest executable or any exception as UNCHECKED, not FAIL — UNCHECKED must not trigger the SHIP override"
    - "SHIP override applies only when gate status is FAIL (a completed pytest run with nonzero exit code on a non-empty target set); write the override feedback to review-feedback.txt naming the failing target(s), matching the read-evidence gate's feedback-writing pattern"
    - "This repository (ai/ael) currently has no tests/ directory of its own — the gate will be a no-op for its own deliverables in this task. Do not add a tests/ directory as part of this task; that is out of scope"
    - "Verify no syntax errors after edit (py_compile)"

specification:
  description: >
    New _run_pytest_gate(state_dir, log, project_root) function called at the
    same call site as _run_syntax_gate (before REVIEW PHASE begins), whose
    result is both injected into review_task (like _syntax_result) and used
    to deterministically override SHIP to REVISE in run_loop when the gate
    reports FAIL.
  requirements:
    functional:
      - "_run_pytest_gate derives test targets from _extract_deliverables(state_dir, log) using the tests/ direct / src/<component>/ -> tests/<component>/ heuristic described in constraints"
      - "When no targets resolve, return '' (empty string) — no injection, no override"
      - "When targets resolve, run subprocess.run([sys.executable, '-m', 'pytest', *targets, '-q'], capture_output=True, text=True, cwd=project_root)"
      - "Build a status of PASS (returncode == 0), FAIL (returncode != 0), or UNCHECKED (exception raised, e.g. pytest not installed) and format a '[TEST GATE: <status>]' block containing a truncated stdout/stderr tail, following _run_syntax_gate's result-block formatting convention (see [SYNTAX GATE] block for style)"
      - "Call _run_pytest_gate at the same site as the existing '# F6: Run syntax gate and inject result into reviewer task' call; prepend/append its block to review_task alongside _syntax_result, following the existing 'if _syntax_result: review_task = _syntax_result + ...' pattern"
      - "In run_loop, add a SHIP override: when the reviewer verdict normalizes to SHIP and the pytest gate status for this iteration is FAIL, override the verdict to REVISE, write review-feedback.txt with the gate's failure block as feedback (naming the failing target path(s)), clear the appropriate state signals, and continue the loop — mirror the existing read-evidence gate override block's structure (clear_state calls, console output, log.warning) as closely as possible"
      - "The override must apply regardless of whether the reviewer's own message referenced or acknowledged the [TEST GATE: FAIL] block already present in its context"
      - "Guard the override to the non-audit (ralph) recipe path only, using the same guard condition already used by the read-evidence gate override"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions (console.print styles, log.debug/info/warning usage matching _run_syntax_gate and the read-evidence gate)"
        - "Comprehensive error handling — subprocess call wrapped in try/except, never allowed to raise out of _run_pytest_gate"
        - "Debug logging with traceback on unexpected exceptions"
        - "Professional docstrings, matching _run_syntax_gate's docstring style ('F6: Run py_compile on modified .py files and return a summary for the reviewer.')"

design:
  architecture: >
    Two additions, each mirroring an existing pattern in the same file:
    (1) a new gate function mirroring _run_syntax_gate's subprocess +
    result-block-injection mechanism, and (2) a new SHIP-override block in
    run_loop mirroring the existing read-evidence gate's override mechanism.
    No new classes, no new MCP tools, no new external dependencies.
  components:
    - name: "_run_pytest_gate"
      type: "function"
      purpose: "Deterministically run pytest against deliverable-derived test targets and produce a status block, without granting the model any execution capability"
      interface:
        inputs:
          - name: "state_dir"
            type: "str"
            description: "AEL state directory, passed through to _extract_deliverables"
          - name: "log"
            type: "logging.Logger"
            description: "Logger, matching _run_syntax_gate's signature convention"
          - name: "project_root"
            type: "str"
            description: "Absolute project root, used as subprocess cwd"
        outputs:
          type: "str"
          description: "A '[TEST GATE: PASS|FAIL|UNCHECKED]' block, or '' if no test-relevant targets resolved"
        raises: []
      logic:
        - "Call _extract_deliverables(state_dir, log) to get the deliverable file set"
        - "Resolve test targets: direct include for tests/ paths; map src/<component>/ paths to tests/<component>/ if that directory exists"
        - "If targets is empty, return ''"
        - "try: subprocess.run([sys.executable, '-m', 'pytest', *targets, '-q'], capture_output=True, text=True, cwd=project_root) with a reasonable timeout; except Exception: status = UNCHECKED"
        - "On successful run: status = PASS if returncode == 0 else FAIL"
        - "Format and return the '[TEST GATE: <status>]' block with a truncated stdout/stderr tail and '[END TEST GATE]' marker, matching _run_syntax_gate's block style"
        - "Log at info (PASS), warning (FAIL or UNCHECKED)"
    - name: "run_loop (pytest SHIP override)"
      type: "function (existing, extended)"
      purpose: "Deterministically override SHIP to REVISE when the pytest gate reports FAIL"
      logic:
        - "Capture the _run_pytest_gate result at the same point _syntax_result is captured, before the review phase call"
        - "After verdict normalization and the existing read-evidence gate check, and only on the non-audit path: if verdict == SHIP and the captured pytest gate status is FAIL, override verdict to REVISE"
        - "Write review-feedback.txt with the gate's failure block as feedback"
        - "console.print and log.warning following the read-evidence gate override's existing style"
        - "continue the loop as the existing override paths do"
  dependencies:
    internal:
      - "_extract_deliverables (reused unmodified)"
      - "_run_syntax_gate (structural model, not called by the new function)"
      - "read-evidence gate override block (structural model for the new SHIP override)"
    external:
      - "pytest (assumed available in the execution environment; absence is handled as UNCHECKED, not FAIL)"

error_handling:
  strategy: >
    All subprocess and filesystem interaction inside _run_pytest_gate is
    wrapped in try/except; no exception may propagate out of the function.
    Any failure to execute pytest itself (missing executable, resolution
    error, timeout) is UNCHECKED, distinct from a completed run that reports
    test failures (FAIL). Only FAIL triggers the SHIP override.
  exceptions:
    - exception: "FileNotFoundError / subprocess errors (pytest not installed or not on PATH)"
      condition: "subprocess.run raises when resolving the interpreter/module"
      handling: "Caught; status = UNCHECKED; logged at WARNING; no SHIP override"
    - exception: "subprocess.TimeoutExpired (if a timeout is set)"
      condition: "pytest run exceeds the configured timeout"
      handling: "Caught; status = UNCHECKED; logged at WARNING; no SHIP override"
  logging:
    level: "INFO for PASS; WARNING for FAIL or UNCHECKED"
    format: "Match existing orchestrator.py log.* call conventions (structured %s/%d args, not f-strings, per surrounding code)"

testing:
  unit_tests:
    - scenario: "Deliverables include tests/<component>/test_x.py; pytest passes"
      expected: "[TEST GATE: PASS] injected into review_task; no SHIP override"
    - scenario: "Deliverables include src/<component>/x.py with an existing tests/<component>/; pytest fails"
      expected: "[TEST GATE: FAIL] injected; reviewer SHIP overridden to REVISE with gate output as feedback"
    - scenario: "No test-relevant deliverables (e.g. this task's own deliverable, ai/ael/src/orchestrator.py, with no ai/ael/tests/ directory)"
      expected: "_run_pytest_gate returns ''; no injection; no SHIP override"
    - scenario: "pytest not installed, or resolved target path does not exist at run time"
      expected: "Status UNCHECKED, not FAIL; no SHIP override; WARNING logged"
    - scenario: "Reviewer emits SHIP despite a [TEST GATE: FAIL] block present in its own context"
      expected: "Override still applies — deterministic, independent of reviewer behaviour"
    - scenario: "Audit-path (tactical-led audit) loop"
      expected: "Gate/override unaffected — guarded to the non-audit path only, same guard condition as the read-evidence gate"
  edge_cases:
    - "Deliverable set contains both tests/ and src/<component>/ paths — targets should be deduped"
    - "src/<component>/ path whose tests/<component>/ directory does not exist — excluded, not an error"
  validation:
    - "No change to worker-phase behaviour"
    - "No change to _run_syntax_gate's existing call site or behaviour"
    - "Audit SHIP/coverage/scope gates unmodified"
    - "claude_code/claude_omlx execution paths unaffected (orchestrator.py's run_loop is the ael path only)"

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
    - "Execute pytest suite for affected test paths on completion; report pass/fail summary"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Add _run_pytest_gate per design; call it alongside _run_syntax_gate; add the SHIP override in run_loop per design"

success_criteria:
  - "_run_pytest_gate returns '' (no-op) when no test-relevant deliverables resolve"
  - "_run_pytest_gate returns a [TEST GATE: PASS] block when resolved targets pass"
  - "_run_pytest_gate returns a [TEST GATE: FAIL] block when resolved targets fail, with output tail included"
  - "_run_pytest_gate returns [TEST GATE: UNCHECKED] rather than raising or reporting FAIL when pytest cannot be run"
  - "run_loop overrides SHIP to REVISE when the pytest gate status is FAIL, writing review-feedback.txt naming the failing target(s), on the non-audit path only"
  - "run_loop does not override SHIP when the pytest gate status is PASS or UNCHECKED, or when no gate result was produced"
  - "Audit-path SHIP/coverage/scope gate behaviour is unchanged"
  - "_run_syntax_gate's existing call site, behaviour, and non-blocking (informational-only) character are unchanged"
  - "ai/ael/src/orchestrator.py has no syntax errors (py_compile)"

tactical_brief: |
  File: ai/ael/src/orchestrator.py. Read before editing.
  Goal: deterministic pytest SHIP gate for the ael (ralph, non-audit) loop.
  1. Add _run_pytest_gate(state_dir, log, project_root), modeled directly on
     the existing _run_syntax_gate (same file): reuse _extract_deliverables()
     for the deliverable set; map to test targets (tests/ paths direct;
     src/<component>/ -> tests/<component>/ if that dir exists); if no
     targets, return "". Otherwise run
     subprocess.run([sys.executable, "-m", "pytest", *targets, "-q"],
     capture_output=True, text=True, cwd=project_root) in a try/except
     (exceptions -> UNCHECKED, never FAIL); build a
     "[TEST GATE: PASS|FAIL|UNCHECKED]" block with truncated output,
     matching _run_syntax_gate's block style.
  2. Call it at the same site as _run_syntax_gate (before REVIEW PHASE);
     inject its block into review_task alongside _syntax_result.
  3. In run_loop, add: on the non-audit path, if verdict == SHIP and the
     pytest gate status is FAIL, override to REVISE, write
     review-feedback.txt naming the failing target(s), mirroring the
     existing read-evidence gate override's structure exactly.
  Constraints: no new MCP tool; no change to worker-phase behaviour; no
  change to the audit path; UNCHECKED and empty-target-set must never
  trigger the override — only a completed FAIL run does.
  Verify no syntax errors (py_compile).

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0), consistent with change-d7f4a1c8's precedent
  for orchestrator.py source changes. Claude Code consumes the full
  document; tactical_brief is retained for schema/govwatch compliance and as
  a summary, though not required for target_profile: claude_code. No
  AEL/oMLX context-budget gate applies. This repository has no ai/ael/tests/
  directory of its own, so _run_pytest_gate will be a no-op for this task's
  own deliverable — that is expected, not a defect; verification is via
  py_compile plus inline code review (P08 strategic audit), consistent with
  change-d7f4a1c8's verification approach. A live Ralph Loop smoke test
  against a project that does have tests/ is recommended before closing this
  change, per change-5bdc2d9b's testing_requirements.test_approach.

execution:
  status: "complete"
  date: "2026-07-17"
  executor: "Claude Code (Opus 4.5)"
  commit: "a9173f2"
  result: >
    All success criteria met. _run_pytest_gate added with subprocess/injection
    pattern; call site alongside _run_syntax_gate; SHIP override in non-audit
    path keyed on [TEST GATE: FAIL]. py_compile verified no syntax errors.
    Gate is no-op for this repository (no ai/ael/tests/) as expected.
```
