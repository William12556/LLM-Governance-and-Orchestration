Created: 2026 July 15

# Prompt b5e9d240 — Opt-in efficiency controls in the AEL orchestrator

```yaml
prompt_info:
  id: "prompt-b5e9d240"
  task_type: "optimization"
  source_ref: "change-b5e9d240"
  target_profile: "claude_code"
  date: "2026-07-15"
  iteration: 1
  coupled_docs:
    change_ref: "change-b5e9d240"
    change_iteration: 1

context:
  purpose: "Add three opt-in, config-gated, default-off efficiency/robustness controls to the AEL orchestrator."
  integration: "ai/ael/src/orchestrator.py and ai/ael/config.yaml."
  knowledge_references: []
  constraints:
    - "All three controls MUST default to disabled; with default config, behaviour is unchanged."
    - "Do not add external dependencies; truncation is character-based, not token-based."
    - "Keep each control independent; do not couple them."

specification:
  description: >
    Add config keys max_completion_tokens (null), max_tool_result_chars (null), and
    strict_tactical_brief (false), and the minimal code to honour each.
  requirements:
    functional:
      - "max_completion_tokens: when non-null, pass it as max_tokens to client.chat.completions.create() in _completion_with_retry; when null, omit max_tokens (current behaviour)."
      - "max_tool_result_chars: when non-null, before appending a tool result to messages in run_phase, if the content length exceeds the value, replace it with a head portion + an elision marker noting the omitted character count + a tail portion; when null, append in full (current behaviour)."
      - "strict_tactical_brief: when true and target_profile is ael and the tactical_brief is absent or malformed, fail fast with a clear error and non-zero exit instead of falling back to the raw document; when false, retain the current warn-and-fallback behaviour."
      - "Add the three keys to config.yaml under the existing execution section with null/false defaults and explanatory comments."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Comprehensive error handling"
        - "Professional docstrings"

design:
  architecture: "Three independent, config-gated guards applied at their existing call sites."
  components:
    - name: "_completion_with_retry"
      type: "function"
      purpose: "Issue a completion with retry."
      logic:
        - "Read max_completion_tokens from config (default null)."
        - "If non-null, include max_tokens in the create() call; else omit it."
    - name: "run_phase"
      type: "function"
      purpose: "Execute a worker/reviewer phase."
      logic:
        - "Read max_tool_result_chars from config (default null)."
        - "Before appending a tool-result message, if non-null and len(content) > value, head/tail truncate with an elision marker; else append unchanged."
    - name: "extract_tactical_brief"
      type: "function"
      purpose: "Resolve the tactical_brief for ael runs."
      logic:
        - "Read strict_tactical_brief from config (default false)."
        - "If true and profile is ael and no valid brief is found, raise a clear error / exit non-zero instead of returning None for raw fallback."
  dependencies:
    internal:
      - "ai/ael/src/orchestrator.py"
      - "ai/ael/config.yaml"
    external: []

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: ""
    - path: "ai/ael/config.yaml"
      content: ""

success_criteria:
  - "With default config (all three disabled), AEL behaviour is unchanged: no max_tokens sent, no truncation, warn-and-fallback on missing brief."
  - "Each control activates only when its config key is set."
  - "config.yaml contains the three new keys with disabled defaults and comments."
  - "py_compile passes on ai/ael/src/orchestrator.py."

tactical_brief: |
  Add three opt-in, config-gated, default-off controls to the AEL orchestrator. All must be
  disabled by default so a default-config run behaves exactly as today.

  1. Output cap. In ai/ael/src/orchestrator.py, function _completion_with_retry: read
     config key max_completion_tokens (default null). When non-null, pass it as max_tokens to
     the client.chat.completions.create() call; when null, do not pass max_tokens.

  2. Tool-result truncation. In run_phase, where a tool result is appended to the messages
     list: read config key max_tool_result_chars (default null). When non-null and the result
     content length exceeds the value, replace the content with a head slice + an elision marker
     stating the number of characters omitted + a tail slice, then append; when null, append the
     full content. Character-based only; no tokenizer.

  3. Brief strictness. In extract_tactical_brief (or its caller): read config key
     strict_tactical_brief (default false). When true and the target profile is ael and no
     valid tactical_brief is found, fail fast with a clear error message and a non-zero exit
     instead of falling back to the raw document. When false, keep the current warn-and-fallback.

  Also add the three keys to ai/ael/config.yaml under the existing execution section (the one
  containing max_iterations), with defaults null / null / false and a short comment on each.

  Deliverables: ai/ael/src/orchestrator.py and ai/ael/config.yaml.
  Success: default config reproduces current behaviour exactly; each control activates only when
  its key is set; py_compile clean.

notes: "Resolves issue-b5e9d240 via change-b5e9d240. Report: dev/reports/report-omlx-ael-efficiency-2026-07-15.md section 5.0 (items 2, 4, 7)."
```

---

Copyright (c) 2026 William Watson. MIT License.
