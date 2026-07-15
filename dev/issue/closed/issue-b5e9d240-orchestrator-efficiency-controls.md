Created: 2026 July 15

# Issue b5e9d240 — Orchestrator lacks opt-in controls for output cap, tool-result size, and brief strictness

```yaml
issue_info:
  id: "issue-b5e9d240"
  title: "Orchestrator lacks opt-in controls for output-token cap, tool-result size, and tactical_brief strictness"
  date: "2026-07-15"
  reporter: ""
  status: "closed"
  severity: "low"
  type: "performance"
  iteration: 1
  coupled_docs:
    change_ref: "change-b5e9d240"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/reports/report-omlx-ael-efficiency-2026-07-15.md"
  description: >
    Efficiency investigation (report section 5.0, items 2, 4, 7) identified three absent
    controls in the AEL orchestrator. None is a defect; each is an opt-in efficiency or
    robustness knob currently unavailable.

affected_scope:
  components:
    - name: "_completion_with_retry"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "run_phase"
      file_path: "ai/ael/src/orchestrator.py"
    - name: "extract_tactical_brief"
      file_path: "ai/ael/src/orchestrator.py"
  designs:
    - design_ref: "dev/design/design-ael-orchestrator.md"
  version: ""

behavior:
  expected: >
    Operators can optionally (a) cap completion output tokens, (b) bound the size of tool
    results appended to context, and (c) require a tactical_brief for ael-profile runs instead
    of silently falling back to the raw document.
  actual: >
    The completion call sets no max_tokens; tool results are appended untruncated; a missing
    tactical_brief warns and falls back to the full raw document.
  impact: >
    Unbounded worst-case output latency; monotonic in-phase context growth; silent, expensive
    raw-document fallback when a brief is omitted.
  workaround: "None; behaviours are currently fixed."

analysis:
  root_cause: "The three controls were never implemented; the orchestrator exposes no configuration for them."
  technical_notes: >
    All three can be added as config-gated, default-off options so existing behaviour is
    unchanged unless an operator opts in. Character-based truncation avoids a tokenizer
    dependency. Brief strictness must be opt-in to preserve raw-document workflows.

resolution:
  approach: "Add three opt-in, config-gated, default-off controls. See change-b5e9d240."
  change_ref: "change-b5e9d240"

traceability:
  design_refs:
    - "dev/design/design-ael-orchestrator.md"
  change_refs:
    - "change-b5e9d240"
  test_refs:
    - "dev/reports/report-omlx-ael-efficiency-2026-07-15.md"

notes: >
  Related report items not in this triple: item 3 (tool-schema deduplication) is
  investigation-first; item 5 (reviewer downsizing) is a runtime flag (--reviewer-model),
  no code change; item 6 (speculative decoding) is deferred pending a compatible model.

loop_context:
  was_loop_execution: false

version_history:
  - version: "1.0"
    date: "2026-07-15"
    author: ""
    changes:
      - "Initial issue"
  - version: "1.1"
    date: "2026-07-15"
    author: ""
    changes:
      - "Closed: three controls implemented and verified in orchestrator.py and config.yaml; triple moved to closed/"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright (c) 2026 William Watson. MIT License.
