```yaml
# T03 Issue Document
# P03 No Trivial Change Exemption

issue_info:
  id: "issue-d5a8e2f4"
  title: "P03 has no exemption for trivial, surgical source code changes"
  date: "2026-03-18"
  reporter: "William Watson"
  status: "closed"
  severity: "low"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-d5a8e2f4"
    change_iteration: 1

source:
  origin: "requirement_change"
  test_ref: ""
  description: >
    Identified during solax-modbus project development (2026-03-18). Strategic
    Domain implemented a trivial argparse fix directly without T03/T02/T04/AEL,
    then identified the resulting protocol gap. P03 §1.4.1 is binary: all source
    code changes require the full workflow. No threshold exists for trivial,
    surgical fixes. This produces disproportionate overhead and discourages
    protocol compliance for small work.

affected_scope:
  components:
    - name: "governance.md"
      file_path: "framework/ai/governance.md"
    - name: "skel/ai/governance.md"
      file_path: "skel/ai/governance.md"
  designs: []
  version: "7.8"

reproduction:
  prerequisites: "P03 §1.4.1 in force with no exemption clause"
  steps:
    - "Identify a trivial, surgical source code fix (e.g. adding argparse to a single function)"
    - "Observe that P03 §1.4.1 requires T03 + T02 + T04 + AEL for all source code changes"
    - "Note the overhead is disproportionate to the scope of the fix"
  frequency: "always"
  reproducibility_conditions: "Any trivial, surgical fix under the framework"
  preconditions: ""
  test_data: ""
  error_output: ""

behavior:
  expected: >
    A narrow exemption exists permitting Strategic Domain to implement trivial,
    surgical fixes directly after human approval, without full workflow overhead.
  actual: >
    No such exemption exists. All source code changes require T03, T02, T04,
    and AEL execution regardless of scope.
  impact: >
    Disproportionate overhead for trivial fixes; discourages protocol compliance
    for small work; creates compliance gap when Strategic Domain acts directly.
  workaround: "Strategic Domain implements directly, creating an undocumented protocol bypass."

environment:
  python_version: ""
  os: ""
  dependencies: []
  domain: ""

analysis:
  root_cause: >
    P03 §1.4.1 was designed for substantive source code changes. No lower bound
    was defined. The §1.4.11 precedent (workspace/ document exemption) was not
    extended to cover trivial src/ changes.
  technical_notes: >
    §1.4.11 already establishes the exemption pattern for workspace/ documents.
    §1.4.12 extends this pattern narrowly to src/ changes satisfying both the
    trivial and surgical definitions and all five enumerated criteria.
  related_issues: []

resolution:
  assigned_to: "William Watson"
  target_date: "2026-03-18"
  approach: >
    Add §1.4.12 Trivial Change Exemption to P03 in both framework/ai/governance.md
    and skel/ai/governance.md. Define trivial and surgical, enumerate five
    jointly-necessary criteria. Full workflow bypass (T03/T02/T04/AEL) when all
    criteria met and human approval obtained. Git history is sole audit record.
  change_ref: "change-d5a8e2f4"
  resolved_date: "2026-03-18"
  resolved_by: "William Watson"
  fix_description: >
    §1.4.12 added to both governance.md files at framework v7.9. Defines trivial
    and surgical, five criteria, full workflow bypass, git history as audit record.

verification:
  verified_date: "2026-03-18"
  verified_by: "William Watson"
  test_results: >
    Human review confirmed §1.4.12 present in both governance.md copies with
    trivial/surgical definitions, all five criteria, and explicit T03/T02/T04/AEL
    bypass statement.
  closure_notes: "Change document change-d5a8e2f4 implemented and closed same date."

prevention:
  preventive_measures: >
    §1.4.12 formalises the exemption, eliminating the compliance gap for future
    trivial fixes.
  process_improvements: >
    When §1.4.11-style exemptions are introduced, evaluate whether a parallel
    exemption for src/ trivial changes is warranted at the same time.

verification_enhanced:
  verification_steps:
    - "Confirm §1.4.12 present in framework/ai/governance.md after §1.4.11"
    - "Confirm §1.4.12 present in skel/ai/governance.md after §1.4.11"
    - "Confirm trivial and surgical definitions present"
    - "Confirm all five criteria enumerated"
    - "Confirm explicit statement that T03/T02/T04/AEL are not required"
    - "Confirm human approval gate stated"
    - "Confirm version history updated to v7.9 in both files"
  verification_results: "All steps passed. governance.md v7.9 in both framework/ and skel/."

traceability:
  design_refs: []
  change_refs:
    - "change-d5a8e2f4"
  test_refs: []

notes: >
  Origin: solax-modbus project. Strategic Domain implemented emulator --port
  argparse fix directly without T04/AEL, then identified the protocol gap and
  raised this issue for the framework.

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""
  last_review_feedback: ""

version_history:
  - version: "1.0"
    date: "2026-03-18"
    author: "William Watson"
    changes:
      - "Initial issue document — created and closed same date"
      - "Issue identified, change implemented, verified, and closed in single session"

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
