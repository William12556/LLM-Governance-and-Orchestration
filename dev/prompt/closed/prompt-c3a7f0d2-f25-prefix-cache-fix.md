Created: 2026 July 15

# Prompt c3a7f0d2 — Remove F25 system-message mutation in run_phase

```yaml
prompt_info:
  id: "prompt-c3a7f0d2"
  task_type: "optimization"
  source_ref: "change-c3a7f0d2"
  target_profile: "claude_code"
  date: "2026-07-15"
  iteration: 1
  coupled_docs:
    change_ref: "change-c3a7f0d2"
    change_iteration: 1

context:
  purpose: "Preserve the oMLX prefix cache by keeping the system message static across run_phase iterations."
  integration: "orchestrator.py run_phase; applies to both worker and reviewer phases."
  knowledge_references: []
  constraints:
    - "Do not introduce a trailing status message — a user message after a tool message is rejected by oMLX/Mistral."
    - "Do not change any other loop behaviour."

specification:
  description: >
    Remove the per-iteration reassignment of messages[0]['content'] in run_phase (the F25
    ITERATION STATUS injection). The system message must remain the static system_prompt for
    the whole phase.
  requirements:
    functional:
      - "messages[0]['content'] is set once (pre-loop) and never reassigned inside the iteration loop."
      - "Optionally append a single static line to system_prompt before the loop stating the phase iteration budget (max_iterations)."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Comprehensive error handling"
        - "Professional docstrings"

design:
  architecture: "Single-function surgical edit."
  components:
    - name: "run_phase"
      type: "function"
      purpose: "Execute one worker or reviewer phase loop."
      logic:
        - "Delete the block that computes _remaining and _status and reassigns messages[0]['content'] within the for-iteration loop."
        - "Retain the pre-loop messages initialisation as the only system-message assignment."
        - "Optionally, before the loop, append one static sentence to system_prompt noting the iteration budget."
  dependencies:
    internal:
      - "ai/ael/src/orchestrator.py"
    external: []

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: ""

success_criteria:
  - "ai/ael/src/orchestrator.py contains no reassignment of messages[0] inside the run_phase loop."
  - "ai/ael/src/orchestrator.py has no syntax errors (py_compile passes)."

tactical_brief: |
  In ai/ael/src/orchestrator.py, function run_phase: remove the F25 block inside the
  `for iteration in range(1, max_iterations + 1)` loop that computes `_remaining` and
  `_status` and reassigns `messages[0]["content"]` to `system_prompt` plus the status
  suffix. The system message must remain the static `system_prompt` value set before the
  loop; it must not be reassigned inside the loop.

  Do NOT add a trailing status message: a user message after a tool message is rejected by
  the oMLX/Mistral conversation structure.

  Optionally, before the loop, append a single static sentence to `system_prompt` stating
  the phase iteration budget (the max_iterations count). Change nothing else in the loop.

  Deliverable: ai/ael/src/orchestrator.py.
  Success: messages[0]["content"] is invariant across all iterations; py_compile is clean.

notes: "Resolves issue-c3a7f0d2 via change-c3a7f0d2. Evidence: dev/reports/procedure-omlx-prompt-cache-behaviour.md section 9.0."
```

---

Copyright (c) 2026 William Watson. MIT License.
