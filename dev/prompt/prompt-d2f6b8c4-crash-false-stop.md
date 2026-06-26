Created: 2026 June 26

```yaml
prompt_info:
  id: "prompt-d2f6b8c4"
  task_type: "debug"
  source_ref: "change-d2f6b8c4"
  date: "2026-06-26"
  iteration: 1
  coupled_docs:
    change_ref: "change-d2f6b8c4"
    change_iteration: 1

context:
  purpose: >
    Fix three correctness defects: tool-call truncation that produces an invalid
    conversation, substring-based error misclassification, and stale-signal false
    completion in single-phase modes.
  integration: >
    ai/ael/src/orchestrator.py — run_phase (tool-call handling), _is_mcp_error and
    the malformed-final guard, single-phase modes in main_async.
  constraints:
    - "Genuine MCP errors must still be classified and counted"
    - "Loop-mode behavior unchanged"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Correctness fixes (F3, F7, F11 from proposal-f9a2c41b).
  requirements:
    functional:
      - "F3: ensure the conversation never contains assistant tool_call ids without matching tool results — truncate before building the assistant message, or append only the retained calls"
      - "F7: classify MCP errors and malformed-final on structured signals (tool-result status, finish_reason) rather than substring scans of content"
      - "F11: clear orchestrator-managed phase signal files at the start of single --mode worker/reviewer, or warn on a stale work-complete.txt"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions"
        - "Comprehensive error handling"

design:
  architecture: "Targeted edits to run_phase, _is_mcp_error, and single-phase startup in main_async"
  components:
    - name: "run_phase (tool-call handling)"
      type: "function"
      purpose: "Valid conversation under truncation (F3)"
      logic:
        - "Apply max_tool_calls_per_iter before constructing the assistant message, or append only retained tool_calls"
        - "Ensure every retained tool_call has a matching tool result; none orphaned"
    - name: "_is_mcp_error and malformed-final guard"
      type: "function"
      purpose: "Structured-signal classification (F7)"
      logic:
        - "Use tool-result status / finish_reason instead of substring matches in content"
        - "A benign result/summary containing 'Input validation error' or '[TOOL_CALLS]' must not be misclassified"
    - name: "main_async (single-phase startup)"
      type: "function"
      purpose: "Clear or warn on stale phase signals (F11)"
      logic:
        - "On single --mode worker/reviewer, clear orchestrator-managed phase signal files (or warn on a stale work-complete.txt) before the phase runs"
  dependencies:
    internal:
      - "Existing state-file clear helpers (clear_state)"
      - "_RESET_FILES / phase signal set"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Implement F3/F7/F11 per design"

success_criteria:
  - "A model turn with >10 tool calls does not raise; the conversation remains valid"
  - "A benign result/summary containing 'Input validation error' or '[TOOL_CALLS]' is not misclassified"
  - "Single --mode worker/reviewer with a stale work-complete.txt does not return complete on iteration 1"
  - "Genuine MCP errors are still classified and counted"
  - "ai/ael/src/orchestrator.py has no syntax errors"

tactical_brief: |
  File: ai/ael/src/orchestrator.py. Read before editing.
  F3: truncate tool calls before building the assistant message (or append only retained calls); no orphaned tool_call ids.
  F7: classify MCP errors and malformed-final on structured signals (tool-result status, finish_reason), not substring scans.
  F11: clear orchestrator-managed phase signals at the start of single --mode worker/reviewer, or warn on stale work-complete.txt.
  Constraints: genuine errors still counted; loop mode unchanged; verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Claude Code consumes this full document; the
  tactical_brief is retained for schema/govwatch compliance. No AEL/oMLX
  context-budget gate applies.
```
