Created: 2026 July 15

# Change c3a7f0d2 — Preserve oMLX prefix cache in run_phase

```yaml
change_info:
  id: "change-c3a7f0d2"
  title: "Preserve oMLX prefix cache: remove per-iteration system-message mutation in run_phase"
  date: "2026-07-15"
  author: ""
  status: "proposed"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-c3a7f0d2"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-c3a7f0d2"
  description: "F25 system-message mutation forfeits oMLX prefix caching (issue-c3a7f0d2)."

scope:
  summary: >
    Keep messages[0] static across iterations in run_phase so oMLX reuses the prefix KV
    cache; drop the per-iteration ITERATION STATUS mutation (Option A).
  affected_components:
    - name: "run_phase"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
  affected_designs:
    - design_ref: "dev/design/design-ael-orchestrator.md"
      sections: []
  out_of_scope:
    - "Tool-schema deduplication (compact signatures vs native tools= parameter)."
    - "Tool-result truncation or compression."
    - "Speculative decoding; reviewer-model downsizing."
    - "Option C (embedding the countdown in tool-result content)."

rational:
  problem_statement: >
    run_phase reassigns messages[0]['content'] = system_prompt + status each iteration. This
    moves prefix divergence ahead of the accumulated conversation, forfeiting oMLX prefix-cache
    reuse for all tokens after the first cache block.
  proposed_solution: >
    Option A: set messages[0] once to the static system_prompt and never mutate it inside the
    loop. If an iteration-budget signal is desired, state it once as a static line within
    system_prompt before the loop. Remove the dynamic countdown and the low-budget nudge.
  alternatives_considered:
    - option: "Option B — deliver status as a trailing message each iteration."
      reason_rejected: "A user message after a tool message is rejected by the oMLX/Mistral conversation structure; breaks on iteration >= 2."
    - option: "Option C — embed the countdown in tool-result content at append time."
      reason_rejected: "Status appears only when tool calls occur and its semantics shift; added complexity for marginal benefit."
  benefits:
    - "Restores prefix-cache reuse; ~63% prefill-time reduction on the measured payload, growing with accumulated context."
    - "Simpler loop; removes per-iteration prompt mutation."
  risks:
    - risk: "Loss of the live iteration countdown and the 'budget running low' nudge."
      mitigation: "max_iterations hard stop and the F28 phase wall-clock cap continue to bound the phase; an optional static budget line retains the iteration count."

technical_details:
  current_behavior: >
    Each iteration computes _remaining and _status from iteration/max_iterations and executes
    messages[0]['content'] = system_prompt + status. Divergence at messages[0] caps
    cached_tokens at the first block.
  proposed_behavior: >
    messages[0]['content'] equals system_prompt for the entire phase (invariant); no
    per-iteration reassignment. Optional one-time static budget line appended to system_prompt
    before the loop.
  implementation_approach: >
    Remove the F25 block inside the run_phase iteration loop that reassigns
    messages[0]['content']. Leave the pre-loop messages initialisation as the sole assignment.
    Optionally add a single static sentence to system_prompt stating the phase iteration budget.
  code_changes:
    - component: "run_phase"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "Delete the per-iteration messages[0] reassignment (F25 status injection); keep the system message static."
      functions_affected:
        - "run_phase"
      classes_affected: []
  interface_changes:
    - interface: "AEL model prompt (system message)"
      change_type: "contract"
      details: "System message no longer carries a per-iteration ITERATION STATUS line."
      backward_compatible: "n/a"

testing_requirements:
  test_approach: >
    Verify messages[0]['content'] is invariant across iterations; confirm py_compile clean;
    optionally confirm cached_tokens exceeds the first block on iteration >= 2 against a live
    oMLX endpoint.
  test_cases:
    - scenario: "Multi-iteration phase run."
      expected_result: "messages[0]['content'] identical on every iteration."
  regression_scope:
    - "Any test asserting the [ITERATION STATUS] string is injected into the system message."
  validation_criteria:
    - "No reassignment of messages[0] within the run_phase loop."
    - "py_compile passes on orchestrator.py."

implementation:
  effort_estimate: "< 1 hour"
  implementation_steps:
    - step: "Remove the F25 block from the run_phase loop."
      owner: "Tactical Domain (Claude Code / AEL)"
    - step: "Optionally append a static budget line to system_prompt before the loop."
      owner: "Tactical Domain (Claude Code / AEL)"
  rollback_procedure: "Revert the commit; restore the F25 block."

traceability:
  related_issues:
    - issue_ref: "issue-c3a7f0d2"
      relationship: "resolves"

notes: "Evidence in dev/reports/procedure-omlx-prompt-cache-behaviour.md section 9.0."

version_history:
  - version: "1.0"
    date: "2026-07-15"
    author: ""
    changes:
      - "Initial change proposal"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```

---

Copyright (c) 2026 William Watson. MIT License.
