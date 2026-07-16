Created: 2026 July 16

```yaml
prompt_info:
  id: "prompt-d7f4a1c8"
  task_type: "debug"
  source_ref: "change-d7f4a1c8"
  target_profile: "claude_code"
  date: "2026-07-16"
  iteration: 1
  coupled_docs:
    change_ref: "change-d7f4a1c8"
    change_iteration: 1

context:
  purpose: >
    Add a deterministic read-evidence gate so the ralph loop accepts SHIP only
    when the reviewer read each deliverable named in work-summary.txt.
  integration: >
    ai/ael/src/orchestrator.py - run_phase (surface review-phase read set) and
    run_loop (SHIP gate on the non-audit path).
  constraints:
    - "Non-audit (ralph) path only; do not alter the audit SHIP/coverage gate"
    - "No change to worker-phase behaviour"
    - "Normalise paths (os.path.abspath) before comparison"
    - "Empty/unresolvable deliverable set -> no-op, not a block"
    - "read/read_file/read_text_file count as inspection; grep/search do not"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Deterministic SHIP gate cross-checking reviewer reads against the deliverable
    set, mirroring the existing audit SHIP-gate override.
  requirements:
    functional:
      - "Surface the review-phase read path set (read/read_file/read_text_file) from run_phase to run_loop"
      - "Compute the deliverable set: files referenced in work-summary.txt that exist on disk (reuse the extraction used by _run_syntax_gate)"
      - "On a ralph-path SHIP, if any deliverable was not read, override to REVISE, write review-feedback.txt naming the unread file(s), and continue the loop"
      - "When the deliverable set is empty, the gate is a no-op (SHIP allowed), logged at debug/info"
      - "Guard the gate to the non-audit recipe set; leave the audit path unchanged"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions"
        - "Comprehensive error handling"

design:
  architecture: "Read-set surfacing from run_phase; a gate block in run_loop before SHIP acceptance, structured like the audit SHIP-gate override"
  components:
    - name: "run_phase"
      type: "function"
      purpose: "Expose the review-phase read path set (already tracked in _read_counts)"
      logic:
        - "Collect read-family call paths during the review phase"
        - "Make the set available to run_loop (return value or phase-scoped collector - implementer's choice)"
    - name: "run_loop"
      type: "function"
      purpose: "Read-evidence SHIP gate on the non-audit path"
      logic:
        - "After verdict resolves to SHIP and after the audit scope/coverage checks, and only when recipe_set is not audit"
        - "Compute deliverable set from work-summary.txt (existing-on-disk files)"
        - "abspath-normalise deliverable paths and reviewer read paths"
        - "If any deliverable is unread: override to REVISE, write review-feedback.txt naming unread file(s), clear signals, continue"
        - "If deliverable set empty: log and allow SHIP"
    - name: "deliverable extraction helper"
      type: "function"
      purpose: "Shared work-summary file extraction (refactor from _run_syntax_gate or a sibling helper)"
      logic:
        - "Extract path-like tokens from work-summary.txt; keep those that exist on disk; dedupe preserving order"
  dependencies:
    internal:
      - "existing state-file helpers; _read_counts; audit SHIP-gate override as structural model"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Implement read-set surfacing and the read-evidence SHIP gate per design"

success_criteria:
  - "Reviewer SHIP with zero reads of a deliverable is overridden to REVISE; feedback names the file"
  - "Reviewer SHIP after reading all deliverables ships"
  - "Empty/unresolvable deliverable set: gate is a no-op, SHIP allowed"
  - "Deliverable read via absolute path while work-summary uses a relative path does not cause a false REVISE"
  - "Audit loop coverage gate behaviour is unchanged"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  File: ai/ael/src/orchestrator.py (run_phase, run_loop). Read before editing.
  Goal: ralph-loop SHIP accepted only if the reviewer read each deliverable.
  1. Surface the review-phase read set (read/read_file/read_text_file paths) from run_phase to run_loop.
  2. Deliverable set = files in work-summary.txt that exist on disk (reuse _run_syntax_gate extraction).
  3. On a non-audit SHIP, if any deliverable unread -> override to REVISE, write review-feedback.txt naming it, continue. Mirror the audit SHIP-gate override block.
  4. abspath-normalise both path sets. Empty set -> no-op. Audit path unchanged.
  Verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md 5.0). Claude Code consumes the full document; the
  tactical_brief is retained for schema/govwatch compliance and as a summary. No
  AEL/oMLX context-budget gate applies.
```
