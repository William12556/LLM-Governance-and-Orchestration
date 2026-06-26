Created: 2026 June 26

```yaml
change_info:
  id: "change-c8b3e9a1"
  title: "Scope containment: read-only reviewer toolset and project-root write confinement"
  date: "2026-06-26"
  author: "William Watson"
  status: "proposed"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-c8b3e9a1"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-c8b3e9a1"
  description: >
    Remediate proposal-f9a2c41b findings F4, F5: ordinary Ralph Loop runs have no
    write-target enforcement, and the reviewer receives the full mutating toolset.

scope:
  summary: >
    Pass a read-only tool subset to the review phase; confine writes to the
    project root via narrowed MCP allowed dirs and optional write-path validation.
  affected_components:
    - name: "orchestrator (phase tool exposure, tool dispatch)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "mcp_client (tool exposure)"
      file_path: "ai/ael/src/mcp_client.py"
      change_type: "modify"
    - name: "AEL config (allowed dirs)"
      file_path: "ai/ael/config.yaml"
      change_type: "modify"
  out_of_scope:
    - "Audit-run scope enforcement (_check_audit_scope unchanged)"
    - "Reviewer decision handling (change-a1d4f7e2)"

rational:
  problem_statement: >
    The orchestrator dispatches any model-called tool without write-target
    validation; scope enforcement exists only for audit runs (F4). Both phases
    receive the full tool schema, so the reviewer can mutate source (F5).
  proposed_solution: >
    F5: expose a read-only tool subset (read/list/grep) to the review phase. F4:
    narrow MCP allowed dirs to the project root in config.yaml; optionally
    validate each write path against the project root and REVISE on out-of-scope
    writes.
  benefits:
    - "Worker/reviewer separation enforced"
    - "Eliminates silent cross-repository scope drift"
    - "Reviewer cannot 'fix' rather than report"
  risks:
    - risk: "Read-only subset omits a tool the reviewer legitimately needs"
      mitigation: "Include read, list, and grep; verify against ralph-review.yaml expectations"
    - risk: "Write-path validation rejects a legitimate in-project write"
      mitigation: "Validate against the resolved project root; treat config.yaml allowed-dirs as the boundary"

technical_details:
  current_behavior: >
    Both phases receive mcp.get_openai_tools() (full toolset). Write targets are
    unvalidated outside audit runs. Allowed dirs span the GitHub/ClaudeProjects tree.
  proposed_behavior: >
    Review phase receives a read-only subset. Allowed dirs are the project root.
    Optional write-path validation rejects or REVISEs out-of-scope writes.
  implementation_approach: >
    Derive a read-only tool list for the review phase (F5). Set allowed dirs to
    the project root in config.yaml (F4, configuration). Optionally add write-path
    validation in the dispatch path (F4, source). Exact subset and validation
    policy decided in implementation.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "F5 read-only tool subset for review phase; F4 optional write-path validation in tool dispatch"
      functions_affected:
        - "run_phase"
        - "run_loop"
    - component: "mcp_client"
      file: "ai/ael/src/mcp_client.py"
      change_summary: "F5 — support returning a read-only tool subset (read/list/grep)"
    - component: "AEL config"
      file: "ai/ael/config.yaml"
      change_summary: "F4 — narrow filesystem MCP allowed dirs to the project root"

testing_requirements:
  test_cases:
    - scenario: "Reviewer attempts write/edit/move/delete"
      expected_result: "No mutating tool exposed; action impossible"
    - scenario: "Worker write targets a path outside the project root"
      expected_result: "Rejected or REVISEd"
    - scenario: "Audit run"
      expected_result: "Existing _check_audit_scope behavior unchanged"
  validation_criteria:
    - "Worker retains full toolset within the project root"
    - "Read-only subset still permits read/list/grep for review"

implementation:
  implementation_steps:
    - step: "Claude Code implements per T04 prompt-c8b3e9a1; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py, mcp_client.py, and config.yaml to prior version"

notes: >
  Execution path: Claude Code. Groups F4 (high) and F5 (high). The config.yaml
  allowed-dirs change applies to this repository's own AEL runs; config.yaml is
  excluded from propagation, so downstream projects set their own boundary. F4
  allowed-dirs is configuration; F4 validation and F5 subset are source changes.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
