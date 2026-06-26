Created: 2026 June 26

```yaml
prompt_info:
  id: "prompt-b9d2f4a7"
  task_type: "debug"
  source_ref: "change-b9d2f4a7"
  date: "2026-06-26"
  iteration: 1
  coupled_docs:
    change_ref: "change-b9d2f4a7"
    change_iteration: 1

context:
  purpose: >
    Make the reviewer syntax gate executable by the orchestrator, correct the
    token-budget estimate, and remove interpreter/tool environment assumptions.
  integration: >
    ai/ael/src/orchestrator.py — estimate_tokens, main_async initial estimate,
    py_compile invocation, run_preflight_check. ai/ael/recipes/ralph-review.yaml —
    remove the reviewer-run py_compile instruction.
  constraints:
    - "Reviewer is no longer instructed to run a shell command"
    - "Corrected estimate must not regress normal runs into false aborts"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Accuracy/portability fixes (F6, F8, F9 from proposal-f9a2c41b).
  requirements:
    functional:
      - "F6: the orchestrator runs py_compile on modified .py files at review time and injects the result into the reviewer context; remove the reviewer-run py_compile instruction from ralph-review.yaml"
      - "F8: estimate_tokens includes the serialized tool-schema length and the rendered system prompt; the main_async initial estimate no longer zeroes the system prompt"
      - "F9: py_compile uses sys.executable rather than PATH 'python'; external tools (grep in run_preflight_check) are guarded for presence"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Use sys.executable for interpreter invocation"
        - "Guard external tool availability before use"
        - "Preserve existing logging and console output conventions"

design:
  architecture: "Orchestrator-side syntax gate with result injection; corrected token accounting; portable interpreter/tool calls"
  components:
    - name: "syntax gate (orchestrator-run)"
      type: "function"
      purpose: "Execute py_compile and inject result (F6)"
      logic:
        - "Determine modified .py files for the iteration"
        - "Run py_compile via sys.executable on each"
        - "Inject the pass/fail result into the reviewer context"
    - name: "estimate_tokens"
      type: "function"
      purpose: "Account for tool schema and system prompt (F8)"
      logic:
        - "Add serialized tools-schema length to the estimate"
        - "Include the rendered system prompt"
    - name: "main_async (initial estimate)"
      type: "function"
      purpose: "Stop zeroing the system prompt in the initial estimate (F8)"
      logic:
        - "Use the actual system prompt length in the initial estimate"
    - name: "py_compile / run_preflight_check"
      type: "function"
      purpose: "Portable interpreter and guarded external tools (F9)"
      logic:
        - "Invoke py_compile with sys.executable"
        - "Check grep availability before use; degrade gracefully if absent"
    - name: "ralph-review recipe"
      type: "module"
      purpose: "Remove the reviewer-run syntax-gate instruction (F6)"
      logic:
        - "Reviewer relies on the injected syntax result; no shell instruction"
  dependencies:
    internal:
      - "Existing budget warn/abort percentage handling"
    external:
      - "sys (stdlib)"
      - "py_compile / subprocess (stdlib)"

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
    - "Edit ai/ael/recipes/ralph-review.yaml in place"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Implement F6/F8/F9 per design"
    - path: "ai/ael/recipes/ralph-review.yaml"
      content: "Remove reviewer-run py_compile instruction"

success_criteria:
  - "A modified .py with a syntax error is detected by the orchestrator and the result is available to the reviewer"
  - "estimate_tokens includes tool-schema and system-prompt contributions; warn/abort thresholds fire correctly"
  - "py_compile uses sys.executable; a venv without PATH 'python' is handled"
  - "Absent grep is guarded with no unhandled error"
  - "ralph-review.yaml no longer instructs the reviewer to run a shell command"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  Files: ai/ael/src/orchestrator.py (estimate_tokens, main_async, py_compile, run_preflight_check); ai/ael/recipes/ralph-review.yaml.
  Read both before editing.
  F6: orchestrator runs py_compile on modified .py files and injects the result; remove the reviewer-run py_compile instruction from the recipe.
  F8: estimate_tokens includes serialized tool-schema length and the rendered system prompt; main_async stops zeroing the system prompt.
  F9: use sys.executable for py_compile; guard grep availability.
  Constraints: reviewer no longer runs a shell command; corrected estimate must not cause false aborts; verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Claude Code consumes this full document; the
  tactical_brief is retained for schema/govwatch compliance. Re-baselining of
  budget warn/abort percentages may follow the corrected estimate. No AEL/oMLX
  context-budget gate applies.
```
