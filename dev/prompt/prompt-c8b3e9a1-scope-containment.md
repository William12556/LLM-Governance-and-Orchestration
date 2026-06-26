Created: 2026 June 26

```yaml
prompt_info:
  id: "prompt-c8b3e9a1"
  task_type: "refactor"
  source_ref: "change-c8b3e9a1"
  date: "2026-06-26"
  iteration: 1
  coupled_docs:
    change_ref: "change-c8b3e9a1"
    change_iteration: 1

context:
  purpose: >
    Enforce Tactical Domain scope containment: give the reviewer a read-only tool
    subset and confine writes to the project root.
  integration: >
    ai/ael/src/orchestrator.py (phase tool exposure, tool dispatch),
    ai/ael/src/mcp_client.py (tool exposure), ai/ael/config.yaml (allowed dirs).
  constraints:
    - "Worker retains the full toolset within the project root"
    - "Audit-run scope enforcement (_check_audit_scope) unchanged"
    - "Read-only subset must still permit read, list, and grep"
    - "Verify no syntax errors after edit"

specification:
  description: >
    Scope-containment changes (F4, F5 from proposal-f9a2c41b).
  requirements:
    functional:
      - "F5: expose a read-only tool subset (read/list/grep) to the review phase; the reviewer cannot call write/edit/move/delete"
      - "F4: narrow filesystem MCP allowed dirs to the project root in config.yaml"
      - "F4 (optional): validate each write path against the project root in the tool-dispatch path; reject or REVISE out-of-scope writes"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Preserve existing logging and console output conventions"
        - "Comprehensive error handling"

design:
  architecture: "Read-only tool subset for the review phase; project-root allowed dirs; optional dispatch-time write-path validation"
  components:
    - name: "mcp_client.get_openai_tools (or new variant)"
      type: "function"
      purpose: "Return a read-only tool subset (F5)"
      logic:
        - "Provide a way to obtain only read/list/grep tools"
        - "Leave the full toolset available to the worker phase"
    - name: "run_phase / run_loop"
      type: "function"
      purpose: "Pass the read-only subset to the review phase (F5); optional write-path validation (F4)"
      logic:
        - "Worker phase: full toolset"
        - "Review phase: read-only subset"
        - "Optional: validate write/edit/delete target paths against the resolved project root; out-of-scope -> reject or REVISE"
    - name: "config.yaml"
      type: "module"
      purpose: "Narrow filesystem MCP allowed dirs to the project root (F4)"
      logic:
        - "Set allowed dirs to the project root for this repository's AEL runs"
  dependencies:
    internal:
      - "MCP tool exposure path"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py and ai/ael/src/mcp_client.py in place"
    - "Edit ai/ael/config.yaml in place"
  files:
    - path: "ai/ael/src/mcp_client.py"
      content: "Support a read-only tool subset"
    - path: "ai/ael/src/orchestrator.py"
      content: "Pass read-only subset to review phase; optional write-path validation"
    - path: "ai/ael/config.yaml"
      content: "Narrow allowed dirs to the project root"

success_criteria:
  - "Reviewer has no write/edit/move/delete tool exposed"
  - "Read-only subset still permits read, list, and grep"
  - "Worker retains the full toolset within the project root"
  - "A worker write outside the project root is rejected or REVISEd (if validation implemented)"
  - "Audit-run scope behavior unchanged"
  - "ai/ael/src/orchestrator.py and mcp_client.py have no syntax errors"

tactical_brief: |
  Files: ai/ael/src/orchestrator.py, ai/ael/src/mcp_client.py, ai/ael/config.yaml.
  Read all before editing.
  F5: review phase receives a read-only tool subset (read/list/grep only); worker keeps full toolset.
  F4: narrow filesystem MCP allowed dirs to the project root in config.yaml; optionally validate write paths against the project root in dispatch.
  Constraints: _check_audit_scope unchanged; verify no syntax errors.

notes: >
  Execution: Claude Code (manual single pass; human review gate per
  ai/profiles/claude.md §5.0). Claude Code consumes this full document; the
  tactical_brief is retained for schema/govwatch compliance. config.yaml is
  excluded from propagation, so downstream projects set their own boundary. No
  AEL/oMLX context-budget gate applies.
```
