Created: 2026 June 17

```yaml
change_info:
  id: "change-b4e8c012"
  title: "Auto-archive audit artifacts on SHIP in orchestrator"
  date: "2026-06-17"
  status: "approved"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b4e8c012"
    issue_iteration: 1

source:
  type: "enhancement"
  reference: "issue-b4e8c012"
  description: >
    Automate archiving of audit-index.md and audit-report.md to
    ai/workspace/audit/ after a successful audit loop SHIP.

scope:
  summary: >
    Add _archive_audit_artifacts() to orchestrator.py. Extend _RESET_FILES.
    Call archive function from main_async after loop mode SHIP.
  affected_components:
    - name: "orchestrator"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  out_of_scope:
    - "Recipe files"
    - "config.yaml"
    - "audit-uml.md archiving"
    - "worker and reviewer modes (loop mode only)"

rational:
  problem_statement: >
    Manual archiving of audit output is error-prone and inconsistent with
    the automated nature of the AEL.
  proposed_solution: >
    On loop SHIP, detect audit mode by presence of audit-report.md in
    state_dir; copy both audit files to ai/workspace/audit/ with canonical
    names derived from the --task UUID.
  benefits:
    - "Eliminates manual cp step from post-run workflow"
    - "Enforces naming convention automatically"
    - "audit-index.md added to _RESET_FILES — cleanup now complete"
  risks:
    - risk: "UUID not present in --task filename (e.g. bare string task)"
      mitigation: "Fallback to yyyymmdd timestamp; logged as warning"
    - risk: "ai/workspace/audit/ does not exist"
      mitigation: "os.makedirs(..., exist_ok=True)"

technical_details:
  current_behavior: >
    run_loop returns 0 on SHIP. No archiving occurs. audit-report.md remains
    in state_dir until manual intervention.
  proposed_behavior: >
    After run_loop returns 0 in loop mode, _archive_audit_artifacts() is
    called. If audit-report.md is present in state_dir, both artifacts are
    copied to ai/workspace/audit/. Console and log output confirms each copy.
  implementation_approach: >
    Four changes to orchestrator.py:
    1. Add import shutil (stdlib)
    2. Extend _RESET_FILES with "audit-index.md" and "audit-report.md"
    3. Add _archive_audit_artifacts(state_dir, task_path, log) function
    4. Call _archive_audit_artifacts in main_async after run_loop rc==0
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "Add shutil import; extend _RESET_FILES; add _archive_audit_artifacts(); add call in main_async loop branch"
      functions_affected:
        - "main_async"
        - "_RESET_FILES (module-level constant)"
      classes_affected: []

testing_requirements:
  test_cases:
    - scenario: "Audit loop SHIPs with valid --task <uuid> path"
      expected_result: "audit-<uuid>-index.md and audit-<uuid>-report.md appear in ai/workspace/audit/"
    - scenario: "Audit loop SHIPs with --task as bare string (no UUID)"
      expected_result: "Files archived with yyyymmdd fallback name; warning logged"
    - scenario: "--mode reset after audit"
      expected_result: "audit-index.md and audit-report.md cleared from state_dir"
    - scenario: "Standard Ralph Loop (no audit-index.md in state_dir)"
      expected_result: "No archive attempt; no console output"
  validation_criteria:
    - "No regression on standard Ralph Loop path"
    - "archive function is a no-op when audit-report.md absent"

implementation:
  implementation_steps:
    - step: "Tactical Domain implements changes per T04 prompt"
      owner: "AEL"
  rollback_procedure: "Revert orchestrator.py to prior version via git"

notes: "shutil.copy2 preferred — preserves file metadata."

version_history:
  - version: "1.0"
    date: "2026-06-17"
    changes:
      - "Initial change document"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
