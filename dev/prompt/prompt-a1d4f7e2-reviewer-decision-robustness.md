Created: 2026 June 26

```yaml
prompt_info:
  id: "prompt-a1d4f7e2"
  task_type: "debug"
  source_ref: "change-a1d4f7e2"
  date: "2026-06-26"
  iteration: 1
  coupled_docs:
    change_ref: "change-a1d4f7e2"
    change_iteration: 1

context:
  purpose: >
    Make the Ralph Loop reviewer decision robust: recognise SHIP/REVISE whether
    written to review-result.txt or stated in the reviewer final message,
    tolerant of casing and decoration, and stop the review phase overwriting
    work-summary.txt.
  integration: >
    ai/ael/src/orchestrator.py — run_phase (shared terminal branch) and run_loop
    (review phase, SHIP comparison). ai/ael/recipes/ralph-review.yaml — verdict
    emission guidance.
  constraints:
    - "review-result.txt takes precedence when present; final-message parse is a fallback only"
    - "Do not change worker-phase behavior"
    - "Out of scope: stall detection, reviewer tool scope"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Three defect fixes in the review path (F1, F2, F13 from proposal-f9a2c41b).
  requirements:
    functional:
      - "F1: in review phase, when review-result.txt is absent, parse the decision from the reviewer final message; require a leading SHIP/REVISE token"
      - "F2: normalise the SHIP comparison — uppercase, strip non-alphanumerics, test the leading token against an explicit SHIP set (e.g. 'SHIP.', '**SHIP**', 'ship' all resolve to SHIP)"
      - "F13: make the run_phase terminal-write target phase-specific so the review phase does not write or overwrite work-summary.txt"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions"
        - "Comprehensive error handling"

design:
  architecture: "Targeted edits to the review-phase paths of run_phase and run_loop; recipe alignment"
  components:
    - name: "run_phase"
      type: "function"
      purpose: "Phase-specific terminal-write target (F13) and review-phase final-message decision capture (F1)"
      logic:
        - "Identify the phase within run_phase (worker vs review)"
        - "In the terminal branch, write the worker summary only in worker phase; do not overwrite work-summary.txt in review phase"
        - "In review phase, make the final message text available for fallback decision parsing"
    - name: "run_loop"
      type: "function"
      purpose: "Normalised SHIP detection and final-message fallback (F1, F2)"
      logic:
        - "Read review-result.txt when present (precedence)"
        - "When absent, derive the decision from the reviewer final message"
        - "Normalise: uppercase, strip non-alphanumerics, test the leading token against the SHIP set; otherwise REVISE"
    - name: "ralph-review recipe"
      type: "module"
      purpose: "Verdict emission guidance consistent with normalised matching (F2)"
      logic:
        - "Confirm the reviewer is instructed to emit a leading SHIP/REVISE token"
  dependencies:
    internal:
      - "run_phase / run_loop existing state-file helpers"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
    - "Edit ai/ael/recipes/ralph-review.yaml in place if verdict guidance requires alignment"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Implement F1/F2/F13 per design"
    - path: "ai/ael/recipes/ralph-review.yaml"
      content: "Align verdict emission guidance with normalised matching"

success_criteria:
  - "A prose SHIP verdict with no review-result.txt resolves to SHIP"
  - "'SHIP.', '**SHIP**', and 'ship' all resolve to SHIP"
  - "After a review phase, work-summary.txt retains the worker content unmodified"
  - "review-result.txt still takes precedence when present"
  - "A genuinely incomplete task still REVISEs"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  Files: ai/ael/src/orchestrator.py (run_phase, run_loop); ai/ael/recipes/ralph-review.yaml.
  Read both before editing.
  F1: in review phase, when review-result.txt is absent, parse SHIP/REVISE from the reviewer final message (leading token).
  F2: normalise SHIP comparison — uppercase, strip non-alphanumerics, test the leading token against a SHIP set.
  F13: phase-specific terminal-write target; review phase must not write work-summary.txt.
  Constraints: review-result.txt takes precedence; no worker-phase change; verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Claude Code consumes this full document; the
  tactical_brief is retained for schema/govwatch compliance and as a summary. No
  AEL/oMLX context-budget gate applies.
```
