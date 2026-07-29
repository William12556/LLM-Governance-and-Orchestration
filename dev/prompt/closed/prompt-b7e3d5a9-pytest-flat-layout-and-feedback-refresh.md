Created: 2026 July 29

```yaml
prompt_info:
  id: "prompt-b7e3d5a9"
  task_type: "debug"
  source_ref: "change-b7e3d5a9"
  date: "2026-07-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-b7e3d5a9"
    change_iteration: 1

context:
  purpose: >
    Make the pytest SHIP gate effective for flat src/ layouts, and stop the
    worker receiving frozen cycle-1 reviewer feedback. The gate currently
    resolves no targets when a deliverable is src/<name>.py, so it enforces
    nothing while appearing active. Separately, review-feedback.txt is cleared
    only at loop start, so later reviewers' feedback is discarded and F12 stall
    detection compares the file to itself.
  integration: >
    ai/ael/src/orchestrator.py — _run_pytest_gate target-resolution loop
    (the src/ branch); run_loop, the per-cycle clear_state call immediately
    preceding the REVIEW PHASE banner.
  constraints:
    - "Do not introduce a whole-suite fallback — resolution stays deliverable-scoped"
    - "Do not change the tests/ direct-include path"
    - "Do not change the src/<component>/ -> tests/<component>/ mapping where it resolves"
    - "Do not remove the `if not existing_feedback:` guard"
    - "Do not clear review-feedback.txt before or during the worker phase — the worker reads it there"
    - "Add no new imports"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Add a flat-module fallback to pytest target resolution, and clear
    review-feedback.txt once per cycle immediately before the review phase.
  requirements:
    functional:
      - "In the src/ branch of _run_pytest_gate, retain the existing tests/<component>/ directory mapping as the first attempt"
      - "When that directory does not exist, derive the module stem from the deliverable basename"
      - "Test tests/test_<stem>.py then tests/<stem>_test.py; add the first that exists as a target"
      - "Add nothing when neither exists — the gate must still no-op cleanly"
      - "Add review-feedback.txt to the clear_state call that precedes the REVIEW PHASE banner"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging conventions"
        - "Reuse os.path helpers already in use in this function"

design:
  architecture: "One additional else-branch in target resolution; one additional argument to an existing clear_state call"
  components:
    - name: "_run_pytest_gate"
      type: "function"
      purpose: "Resolve test targets for flat module layouts"
      logic:
        - "If tests/<component>/ is a directory, add it (existing behaviour)"
        - "Otherwise compute stem = splitext(basename(rel_path))[0]"
        - "For candidate in (test_<stem>.py, <stem>_test.py): if isfile, add and stop"
    - name: "run_loop"
      type: "function"
      purpose: "Refresh reviewer feedback each cycle"
      logic:
        - "Clear review-feedback.txt alongside work-complete.txt before the review phase begins"
  dependencies:
    internal:
      - "clear_state, _extract_deliverables"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
    - "Run py_compile on the edited file"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Flat-layout target fallback and per-cycle feedback clear per design"

success_criteria:
  - "Deliverable src/split.py with tests/test_split.py present resolves a target and injects a [TEST GATE] block"
  - "Deliverable src/<component>/x.py with tests/<component>/ present behaves exactly as before"
  - "Deliverable with no matching test file resolves no target and the gate no-ops"
  - "tests/ direct-include path unchanged"
  - "In a two-cycle loop, cycle 2's reviewer feedback is written rather than discarded"
  - "The worker still reads the prior cycle's feedback during its phase"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  File: ai/ael/src/orchestrator.py. Read _run_pytest_gate and the run_loop review-phase block before editing.
  Defect 1: for a deliverable src/<name>.py, parts[1] is "<name>.py" so the gate tests isdir("tests/<name>.py"), which never holds. No target resolves; the pytest gate silently enforces nothing on flat layouts.
  Defect 2: review-feedback.txt is cleared only at loop start, and fallback persistence is guarded by `if not existing_feedback:`, so cycle 1's feedback is frozen for the run. Stall detection then compares the file to itself and will false-BLOCK at stall_threshold.
  Fix 1: in the src/ branch, keep the tests/<component>/ isdir mapping; in its else, try tests/test_<stem>.py then tests/<stem>_test.py where stem = splitext(basename)[0], adding the first that is a file.
  Fix 2: add "review-feedback.txt" to the clear_state call immediately before the REVIEW PHASE banner (currently clears work-complete.txt only).
  Constraints: no whole-suite fallback; do not alter the tests/ direct path or a resolving component mapping; keep the existing guard; never clear feedback before the worker phase; no new imports; verify py_compile.

notes: >
  Execution: Claude Desktop (Opus 5), direct implementation via Filesystem MCP
  at William Watson's instruction — not delegated to Claude Code or AEL. This
  document is the specification of record. P08 strategic audit by an
  independent session remains outstanding; the implementer cannot supply it.
```
