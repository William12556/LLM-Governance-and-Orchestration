Created: 2026 June 26

```yaml
prompt_info:
  id: "prompt-f1c8a3e6"
  task_type: "debug"
  source_ref: "change-f1c8a3e6"
  date: "2026-06-26"
  iteration: 1
  coupled_docs:
    change_ref: "change-f1c8a3e6"
    change_iteration: 1

context:
  purpose: >
    Resolve four lower-severity defects: continue-prompt off-by-one, inconsistent
    reviewer framing, inconsistent audit item counting, and arbitrary
    context-window resolution.
  integration: >
    ai/ael/src/orchestrator.py — continue prompt and review_task in run_loop,
    audit item counting, resolve_context_window. ai/ael/recipes/ralph-review.yaml
    — review instruction. ai/ael/config.yaml — optional context override.
  constraints:
    - "No regression to standard loop iteration counting"
    - "Absent context override falls back to the detected value"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Minor fixes (F15, F16, F17, F18 from proposal-f9a2c41b).
  requirements:
    functional:
      - "F15: correct the continue-prompt accounting so that after 'y' the loop delivers exactly the promised additional cycles"
      - "F16: prepend the [AEL RUNTIME CONTEXT] header to review_task and use a consistent review instruction across loop and single --mode reviewer"
      - "F17: use a single shared parser for audit-index items so snapshot/scope checks and the unchecked-item gate count identically"
      - "F18: match the exact model directory in resolve_context_window (not an arbitrary glob match) and allow a per-model supported-context override in config.yaml"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions"
        - "Comprehensive error handling"

design:
  architecture: "Targeted edits to run_loop, audit counting, and resolve_context_window; recipe and config alignment"
  components:
    - name: "run_loop (continue prompt)"
      type: "function"
      purpose: "Correct iteration accounting (F15)"
      logic:
        - "Fix the bound-check/compensation so no iteration number is skipped after 'y'"
    - name: "run_loop (review_task)"
      type: "function"
      purpose: "Consistent reviewer framing (F16)"
      logic:
        - "Prepend the [AEL RUNTIME CONTEXT] header to review_task"
        - "Use a review instruction (not the worker task text) in single --mode reviewer"
    - name: "audit item parser"
      type: "function"
      purpose: "Single shared item-counting parser (F17)"
      logic:
        - "Extract one parser used by both snapshot/scope checks and the unchecked-item gate"
    - name: "resolve_context_window"
      type: "function"
      purpose: "Exact-directory resolution with config override (F18)"
      logic:
        - "Match the exact model directory rather than glob(...)[0]"
        - "Read an optional per-model supported-context override from config.yaml; fall back to the detected value when absent"
  dependencies:
    internal:
      - "Existing config loading"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
    - "Edit ai/ael/recipes/ralph-review.yaml and ai/ael/config.yaml in place"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Implement F15/F16/F17/F18 per design"
    - path: "ai/ael/recipes/ralph-review.yaml"
      content: "Consistent review instruction referencing the runtime header"
    - path: "ai/ael/config.yaml"
      content: "Optional per-model supported-context override field"

success_criteria:
  - "After 'y', the loop delivers exactly the promised additional cycles"
  - "Reviewer framing includes the runtime header in both loop and single mode"
  - "Audit snapshot/scope and the unchecked-item gate count identically across formatting variations"
  - "resolve_context_window matches the exact model directory; a config override is honoured and absent override falls back to the detected value"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  Files: ai/ael/src/orchestrator.py (continue prompt, review_task, audit counting, resolve_context_window); ai/ael/recipes/ralph-review.yaml; ai/ael/config.yaml.
  Read all before editing.
  F15: fix continue-prompt accounting so 'y' delivers exactly the promised cycles.
  F16: prepend [AEL RUNTIME CONTEXT] to review_task; consistent review instruction across modes.
  F17: single shared parser for audit-index items.
  F18: match exact model directory in resolve_context_window; optional per-model context override in config.yaml with detected-value fallback.
  Constraints: no loop-counting regression; verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Claude Code consumes this full document; the
  tactical_brief is retained for schema/govwatch compliance. The config.yaml
  override is excluded from propagation. No AEL/oMLX context-budget gate applies.
```
