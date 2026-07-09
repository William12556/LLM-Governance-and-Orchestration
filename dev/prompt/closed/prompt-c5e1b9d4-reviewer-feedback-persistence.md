Created: 2026 June 28

```yaml
prompt_info:
  id: "prompt-c5e1b9d4"
  task_type: "debug"
  source_ref: "change-c5e1b9d4"
  date: "2026-06-28"
  iteration: 1
  coupled_docs:
    change_ref: "change-c5e1b9d4"
    change_iteration: 1

context:
  purpose: >
    Restore the Ralph Loop REVISE feedback channel. The read-only reviewer cannot
    write review-feedback.txt, and the verdict fallback captures only the leading
    SHIP/REVISE token. Persist the reviewer feedback body so the worker receives
    it and F12 stall detection becomes effective.
  integration: >
    ai/ael/src/orchestrator.py — run_loop, review-result handling block (the
    section that reads review-result.txt, falls back to reviewer_final_msg, then
    reads review-feedback.txt and runs stall detection).
    ai/ael/recipes/ralph-review.yaml — OUTPUT and VERDICT FORMAT guidance.
  constraints:
    - "Reviewer remains read-only — do not restore write tools"
    - "review-result.txt retains precedence when present"
    - "Do not overwrite a non-empty review-feedback.txt"
    - "Do not change worker-phase behaviour"
    - "Verify no syntax errors after edit"

specification:
  description: >
    On a fallback REVISE verdict, persist the reviewer final-message body to
    review-feedback.txt; reconcile the reviewer recipe with the read-only toolset.
  requirements:
    functional:
      - "In run_loop, when the verdict is derived from reviewer_final_msg (review-result.txt absent) and resolves to REVISE, write the message body to STATE_DIR/review-feedback.txt"
      - "Strip only the leading verdict token (the first whitespace-delimited token when it normalises to SHIP/REVISE); persist the remainder verbatim as feedback"
      - "Synthesise feedback only when review-feedback.txt is absent or empty; never overwrite existing non-empty feedback"
      - "Place the persistence step before the feedback read, the REVISE panel, and the F12 stall-detection block so the worker and stall detector observe it"
      - "Recipe: instruct the reviewer to emit the verdict as the leading token of the final message followed by the feedback body; remove the 'use write tool' OUTPUT block"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions"
        - "Reuse existing state-file helpers (read_state, write_state)"

design:
  architecture: "Targeted edit to the review-result handling block of run_loop; recipe OUTPUT alignment"
  components:
    - name: "run_loop"
      type: "function"
      purpose: "Persist fallback REVISE feedback body to review-feedback.txt"
      logic:
        - "After verdict resolution, if verdict is REVISE and review-result.txt was absent (verdict came from reviewer_final_msg)"
        - "Read current review-feedback.txt; if absent or empty, derive feedback = reviewer_final_msg with the leading verdict token removed"
        - "Write the derived feedback to STATE_DIR/review-feedback.txt"
        - "Proceed to the existing feedback read, REVISE panel, and stall detection unchanged"
    - name: "ralph-review recipe"
      type: "module"
      purpose: "Match reviewer output guidance to the read-only toolset"
      logic:
        - "VERDICT FORMAT: verdict as the leading token of the final response, followed by feedback body"
        - "Remove the OUTPUT block instructing use of the write tool for review-result.txt / review-feedback.txt"
  dependencies:
    internal:
      - "read_state, write_state, _normalize_verdict"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
    - "Edit ai/ael/recipes/ralph-review.yaml in place"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Persist fallback REVISE feedback in run_loop per design"
    - path: "ai/ael/recipes/ralph-review.yaml"
      content: "Reconcile OUTPUT/VERDICT FORMAT with read-only reviewer"

success_criteria:
  - "After a loop REVISE, review-feedback.txt contains the reviewer reasoning (non-empty)"
  - "The leading SHIP/REVISE token is not duplicated into the feedback body"
  - "A non-empty review-feedback.txt is never overwritten"
  - "Identical feedback for stall_threshold cycles triggers the F12 stall BLOCK"
  - "A first-pass-correct task still SHIPs"
  - "review-result.txt precedence unchanged; worker-phase behaviour unchanged"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  Files: ai/ael/src/orchestrator.py (run_loop, review-result handling block);
  ai/ael/recipes/ralph-review.yaml. Read both before editing.
  Defect: read-only reviewer cannot write review-feedback.txt; verdict fallback keeps only the token, so REVISE feedback is lost.
  Fix run_loop: on fallback REVISE (verdict from reviewer_final_msg, review-result.txt absent), if review-feedback.txt is absent/empty, write reviewer_final_msg minus the leading verdict token to review-feedback.txt — before the feedback read and stall detection.
  Fix recipe: verdict as leading token + feedback body in the final message; remove the 'use write tool' OUTPUT block.
  Constraints: reviewer stays read-only; review-result.txt precedence; do not overwrite existing feedback; no worker-phase change; verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Claude Code consumes this full document; the
  tactical_brief is retained for schema/govwatch compliance and as a summary. No
  AEL/oMLX context-budget gate applies.
```
