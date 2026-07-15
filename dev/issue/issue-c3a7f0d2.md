Created: 2026 July 15

# Issue c3a7f0d2 — F25 system-message mutation defeats oMLX prefix cache

```yaml
issue_info:
  id: "issue-c3a7f0d2"
  title: "F25 system-message mutation defeats oMLX prefix cache in run_phase"
  date: "2026-07-15"
  reporter: ""
  status: "open"
  severity: "medium"
  type: "performance"
  iteration: 1
  coupled_docs:
    change_ref: "change-c3a7f0d2"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/reports/procedure-omlx-prompt-cache-behaviour.md"
  description: >
    Empirical prompt-cache testing (procedure section 9.0) established that oMLX
    performs block-granular cross-request prefix KV caching, and that mutating the
    system message each iteration forfeits that reuse for all tokens after the first
    cache block.

affected_scope:
  components:
    - name: "run_phase"
      file_path: "ai/ael/src/orchestrator.py"
  designs:
    - design_ref: "dev/design/design-ael-orchestrator.md"
  version: ""

reproduction:
  prerequisites: "oMLX server with prefix caching; a worker or reviewer phase running more than one iteration."
  steps:
    - "Run any multi-iteration phase via orchestrator.py."
    - "Observe messages[0]['content'] is reassigned each iteration with the ITERATION STATUS suffix (F25 block)."
    - "Inspect usage.prompt_tokens_details.cached_tokens across iterations."
  frequency: "always"
  reproducibility_conditions: "Any phase with more than one iteration."
  error_output: ""

behavior:
  expected: "Stable prompt prefix across iterations so oMLX reuses the prefix KV cache; only new tail tokens are prefilled."
  actual: "The system message changes every iteration; divergence at messages[0] forces recompute of all tokens after the first cache block."
  impact: "Inflated per-iteration prefill latency; the recomputed region grows with accumulated tool output across iterations."
  workaround: "None."

environment:
  python_version: "3.11+"
  os: "macOS 14+ (Apple Silicon)"
  domain: ""

analysis:
  root_cause: >
    The F25 block in run_phase reassigns messages[0]['content'] = system_prompt + status
    each iteration to surface an iteration countdown, placing volatile content ahead of the
    accumulated conversation and moving the prefix divergence point to the system message.
  technical_notes: >
    oMLX caches in ~256-token blocks. Divergence at messages[0] caps cached_tokens at the
    first block. The trailing-message alternative is precluded because a user message after a
    tool message is rejected by the oMLX/Mistral conversation structure.

resolution:
  approach: "Option A: remove the per-iteration system-message mutation; state the iteration budget once in the static system prompt. See change-c3a7f0d2."
  change_ref: "change-c3a7f0d2"

traceability:
  design_refs:
    - "dev/design/design-ael-orchestrator.md"
  change_refs:
    - "change-c3a7f0d2"
  test_refs:
    - "dev/reports/procedure-omlx-prompt-cache-behaviour.md"

notes: >
  Evidence (procedure section 9.3): identical 554-token chat payload, status in the system
  message vs. as a trailing message -> cached_tokens 256 vs 512, total_time 2.84 s vs 1.05 s
  (63% prefill reduction).

loop_context:
  was_loop_execution: false

version_history:
  - version: "1.0"
    date: "2026-07-15"
    author: ""
    changes:
      - "Initial issue"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright (c) 2026 William Watson. MIT License.
