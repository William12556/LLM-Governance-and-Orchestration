# T03 Issue Template

Created: 2025-12-12

---

## Table of Contents

- [Template](#template)
- [Schema](#schema)
- [Version History](<#version history>)

---

## Template

```yaml
# T03 Issue Template v1.0 - YAML Format
# Optimized for LM code generation context efficiency

issue_info:
  id: ""  # issue-<uuid> format
  title: ""
  date: ""
  reporter: ""
  status: ""  # open, investigating, resolved, verified, closed, deferred
  severity: ""  # critical, high, medium, low
  type: ""  # bug, defect, error, performance, security
  iteration: 1  # Increments with each debug cycle
  coupled_docs:
    change_ref: ""  # change-<uuid> when created
    change_iteration: null  # Matches change.iteration

source:
  origin: ""  # test_result, user_report, code_review, monitoring
  test_ref: ""  # Link to test result if applicable
  description: ""

affected_scope:
  components:
    - name: ""
      file_path: ""
  designs:
    - design_ref: ""
  version: ""  # Code version where issue found

reproduction:
  prerequisites: ""  # Required conditions before issue can occur
  steps:
    - ""
  frequency: ""  # always, intermittent, once
  reproducibility_conditions: ""  # Specific conditions when issue manifests
  preconditions: ""
  test_data: ""
  error_output: ""  # Error messages, stack traces

behavior:
  expected: ""
  actual: ""
  impact: ""  # Functional impact description
  workaround: ""  # Available workaround if any

environment:
  python_version: ""
  os: ""
  dependencies:
    - library: ""
      version: ""
  domain: ""  # domain_1, domain_2

analysis:
  root_cause: ""
  technical_notes: ""
  related_issues:
    - issue_ref: ""
      relationship: ""  # duplicate, related, blocks, blocked_by

resolution:
  assigned_to: ""
  target_date: ""
  approach: ""
  change_ref: ""  # Link to change document
  resolved_date: ""
  resolved_by: ""
  fix_description: ""

verification:
  verified_date: ""
  verified_by: ""
  test_results: ""
  closure_notes: ""

prevention:
  preventive_measures: ""
  process_improvements: ""

verification_enhanced:
  verification_steps:
    - ""
  verification_results: ""

traceability:
  design_refs:
    - ""
  change_refs:
    - ""
  test_refs:
    - ""

notes: ""

loop_context:
  was_loop_execution: false
  blocked_at_iteration: 0
  failure_mode: ""  # boundary_exceeded, divergence, critical_error
  last_review_feedback: ""

version_history:
  - version: ""
    date: ""
    author: ""
    changes:
      - ""

metadata:
  copyright: "Copyright (c) 2025 William Watson. This work is licensed under the MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

## Schema

```yaml
# T03 Issue Schema v1.0
$schema: http://json-schema.org/draft-07/schema#
type: object
required:
  - issue_info
  - source
  - affected_scope
  - behavior

properties:
  issue_info:
    type: object
    required: [id, title, date, status, severity, type, iteration]
    properties:
      id:
        type: string
        pattern: "^issue-[0-9a-f]{8}$"
      status:
        type: string
        enum: [open, investigating, resolved, verified, closed, deferred]
      severity:
        type: string
        enum: [critical, high, medium, low]
      type:
        type: string
        enum: [bug, defect, error, performance, security]
      iteration:
        type: integer
        minimum: 1
      coupled_docs:
        type: object
        properties:
          change_ref:
            type: string
            pattern: "^change-[0-9a-f]{8}$"
          change_iteration:
            type: integer
            minimum: 1

  loop_context:
    type: object
    properties:
      was_loop_execution:
        type: boolean
      blocked_at_iteration:
        type: integer
      failure_mode:
        type: string
        enum: [boundary_exceeded, divergence, critical_error]
      last_review_feedback:
        type: string

  metadata:
    type: object
    required: [template_version, schema_type]
    properties:
      schema_type:
        type: string
        enum: [t03_issue]
```

---

## Version History

| Version | Date       | Description                          |
| ------- | ---------- | ------------------------------------ |
| 1.0     | 2025-12-12 | Split from governance.md into separate file |
| 1.1     | 2025-12-12 | UUID pattern migration |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
