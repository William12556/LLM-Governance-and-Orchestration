Created: 2026 July 16

```yaml
issue_info:
  id: "issue-d7f4a1c8"
  title: "Ralph Loop reviewer can issue SHIP without inspecting deliverables"
  date: "2026-07-16"
  reporter: "William Watson"
  status: "open"
  severity: "high"
  type: "defect"
  iteration: 1
  coupled_docs:
    change_ref: "change-d7f4a1c8"
    change_iteration: 1

source:
  origin: "monitoring"
  description: >
    Observed during concurrent model-routing testing: the reviewer (Magistral)
    emitted a verdict without evaluating the actual worker output. In the ralph
    (non-audit) loop nothing requires the reviewer to read the deliverable files
    before SHIP. The verdict is derived solely from the reviewer's final-message
    token (_normalize_verdict), so a confabulated SHIP with zero read calls is
    accepted. The audit path already gates SHIP on coverage; the ralph path has
    no equivalent evidence gate.

affected_scope:
  components:
    - name: "orchestrator (run_phase, run_loop)"
      file_path: "ai/ael/src/orchestrator.py"
  version: "current"

reproduction:
  prerequisites: "Ralph Loop (--mode loop), reviewer that emits SHIP without issuing read calls."
  steps:
    - "Worker completes; work-summary.txt lists deliverable files"
    - "Reviewer final message begins with SHIP but the phase issued no read/read_file/read_text_file calls on those files"
    - "run_loop normalises the verdict to SHIP and exits; deliverables never inspected"
  frequency: "intermittent"
  reproducibility_conditions: "Depends on reviewer model behaviour; more likely with a heterogeneous reviewer that under-uses tools."
  error_output: "SHIPPED panel with no reviewer reads of deliverables in the .LOG."

behavior:
  expected: >
    SHIP is accepted only when the reviewer has actually read each deliverable
    named in work-summary.txt. An unfounded SHIP is overridden to REVISE.
  actual: >
    SHIP is accepted from the final-message token regardless of whether the
    reviewer read any deliverable.
  impact: "Loop can emit unfounded approvals; defective or absent output ships undetected."
  workaround: "Manual post-SHIP code review (P08) — outside the loop."

analysis:
  root_cause: >
    Verdict acceptance in run_loop depends only on _normalize_verdict of the
    reviewer output. run_phase tracks read-family calls in _read_counts but does
    not surface them to run_loop, and no gate cross-checks reads against the
    deliverable set. The reviewer recipe instructs reading (procedure step 3) but
    instruction is not enforcement.
  technical_notes: >
    Add a deterministic, orchestrator-side gate mirroring the existing audit
    SHIP-gate override: before accepting SHIP in the non-audit loop, require that
    the reviewer read each deliverable file (from work-summary.txt) that exists on
    disk; otherwise override to REVISE naming the unread file(s).
  related_issues:
    - issue_ref: "issue-a1d4f7e2"
      relationship: "related"
    - issue_ref: "issue-e2b8046c"
      relationship: "related"

resolution:
  approach: >
    Orchestrator read-evidence gate on the ralph SHIP path. Deliverable set from
    work-summary.txt; reviewer read set from run_phase; override SHIP->REVISE on
    any unread deliverable. Audit path unaffected.

verification:
  verification_steps:
    - "Reviewer SHIP with zero reads of a deliverable is overridden to REVISE; feedback names the file"
    - "Reviewer SHIP after reading all deliverables ships"
    - "Empty/unresolvable deliverable set -> gate no-op (SHIP allowed), logged"
    - "Absolute vs relative path forms do not produce a false REVISE"
    - "Audit loop coverage gate behaviour unchanged"

notes: >
  Tier 1 of the reviewer-confabulation analysis. Tier 2 (grounded citation) and
  Tier 3 (heterogeneous reviewer, change-a7d3f8b1) are out of scope here. Source
  change.

loop_context:
  was_loop_execution: false
  failure_mode: "critical_error"

version_history:
  - version: "1.0"
    date: "2026-07-16"
    changes:
      - "Initial issue"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```
