Created: 2026 June 27

```yaml
prompt_info:
  id: "prompt-e2b8046c"
  task_type: "debug"
  source_ref: "change-e2b8046c"
  date: "2026-06-26"
  iteration: 1
  coupled_docs:
    change_ref: "change-e2b8046c"
    change_iteration: 1

context:
  purpose: >
    Resolve the reviewer false-REVISE non-convergence by stopping the worker from
    listing orchestrator-managed signal files as deliverables in work-summary.txt.
  integration: >
    ai/ael/recipes/ralph-work.yaml — WORK SUMMARY section of the worker
    instructions.
  constraints:
    - "Recipe-level change only; no Python source change"
    - "Do not alter run_loop signal clearing or the reviewer recipe"
    - "SHIP gate for genuinely incomplete work must not regress"

specification:
  description: >
    Issue-e2b8046c Option B: exclude orchestrator-managed signal files from the
    worker's work-summary deliverable list.
  requirements:
    functional:
      - "In the WORK SUMMARY section, instruct the worker to NOT list orchestrator-managed signal files (work-complete.txt, iteration.txt, review-*.txt, .ralph-*, RALPH-BLOCKED.md) as deliverables"
      - "Instruct the worker to list only task outputs"
    technical:
      language: "YAML (recipe)"
      version: "n/a"
      standards:
        - "Preserve existing recipe structure and tone"
        - "Record the change in the recipe version history"

design:
  architecture: "Worker recipe instruction amendment"
  components:
    - name: "ralph-work.yaml WORK SUMMARY"
      type: "module"
      purpose: "Exclude signal files from the deliverable list"
      logic:
        - "Append an explicit exclusion clause enumerating the signal files"
        - "State that only task outputs are listed"
        - "Add a version-history line referencing issue-e2b8046c"
  dependencies:
    internal: []
    external: []

deliverable:
  format_requirements:
    - "Edit ai/ael/recipes/ralph-work.yaml in place"
  files:
    - path: "ai/ael/recipes/ralph-work.yaml"
      content: "Add signal-file exclusion clause to WORK SUMMARY; bump version history"

success_criteria:
  - "WORK SUMMARY instructs exclusion of work-complete.txt, iteration.txt, review-*.txt, .ralph-*, RALPH-BLOCKED.md"
  - "WORK SUMMARY instructs listing only task outputs"
  - "Recipe version history records the change referencing issue-e2b8046c"
  - "A one-pass loop task SHIPs within 1-2 iterations with no reference to work-complete.txt in reviewer feedback"

tactical_brief: |
  File: ai/ael/recipes/ralph-work.yaml. Read before editing.
  In the WORK SUMMARY section, add: do NOT list orchestrator-managed signal files
  (work-complete.txt, iteration.txt, review-*.txt, .ralph-*, RALPH-BLOCKED.md) as
  deliverables; list only task outputs.
  Add a version-history line referencing issue-e2b8046c.
  Constraints: recipe-only change; do not alter run_loop or the reviewer recipe.

notes: >
  Execution: Claude Code. Recipe-level fix (Option B). Prompt authored
  retroactively to document the implemented change (ralph-work.yaml v1.4.0) and
  restore issue-change-prompt coupling; no AEL/oMLX context-budget gate applies.
```
