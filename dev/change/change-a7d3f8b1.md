Created: 2026 July 15

# Change a7d3f8b1 — Config-driven per-role worker/reviewer model resolution

```yaml
change_info:
  id: "change-a7d3f8b1"
  title: "Add config-driven per-role model resolution; set Magistral as default reviewer"
  date: "2026-07-15"
  author: ""
  status: "proposed"
  priority: "low"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-a7d3f8b1"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-a7d3f8b1"
  description: "No persistent per-role reviewer/worker model from config (issue-a7d3f8b1)."

scope:
  summary: >
    Add optional omlx.worker_model and omlx.reviewer_model config keys, read in main_async
    between the CLI flag and default_model. Set reviewer_model to Magistral and add its context
    window override.
  affected_components:
    - name: "main_async"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "config"
      file_path: "ai/ael/config.yaml"
      change_type: "modify"
  affected_designs:
    - design_ref: "dev/design/design-ael-orchestrator.md"
      sections: []
  out_of_scope:
    - "Model-swap / eviction management between worker and reviewer phases."
    - "Any change to worker default (already set via omlx.default_model)."

rational:
  problem_statement: >
    main_async resolves both roles from a single default_model; a standing heterogeneous
    worker/reviewer pairing cannot be configured without a per-run CLI flag.
  proposed_solution: >
    Insert a config tier into per-role resolution: worker_model = args.worker_model or
    omlx_cfg.get('worker_model') or model; reviewer_model = args.reviewer_model or
    omlx_cfg.get('reviewer_model') or model. Precedence CLI > config > default_model.
    Populate omlx.reviewer_model with Magistral and add its context-window override.
  alternatives_considered:
    - option: "Runtime --reviewer-model flag only."
      reason_rejected: "Does not persist the choice; must be repeated every invocation."
    - option: "Replace default_model semantics with explicit worker/reviewer keys only."
      reason_rejected: "Breaks backward compatibility; default_model remains the single-model fallback."
  benefits:
    - "Persistent heterogeneous worker/reviewer configuration."
    - "Backward compatible; absent keys reproduce current behaviour."
  risks:
    - risk: "Magistral native tool-calling for the reviewer role is not yet exercised end-to-end."
      mitigation: "mistral3 family (as Devstral, confirmed working); confirm on the first real review phase. Reversible via config."

technical_details:
  current_behavior: >
    model = args.model or omlx_cfg['default_model']; worker_model = args.worker_model or model;
    reviewer_model = args.reviewer_model or model.
  proposed_behavior: >
    worker_model = args.worker_model or omlx_cfg.get('worker_model') or model;
    reviewer_model = args.reviewer_model or omlx_cfg.get('reviewer_model') or model.
    With omlx.reviewer_model set, the loop uses Magistral for review and default_model (Devstral)
    for work, absent CLI overrides.
  implementation_approach: >
    Modify the two resolution lines in main_async. Add omlx.reviewer_model and a
    model_context_windows entry for Magistral (131072) to config.yaml. worker_model key is
    supported by the code but left unset (worker uses default_model).
  code_changes:
    - component: "main_async"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "Insert omlx_cfg.get('worker_model'/'reviewer_model') as the middle precedence tier in per-role resolution."
      functions_affected:
        - "main_async"
      classes_affected: []
    - component: "config"
      file: "ai/ael/config.yaml"
      change_summary: "Add omlx.reviewer_model: Magistral-Small-2509-MLX-6bit; add model_context_windows entry 131072 for Magistral."
      functions_affected: []
      classes_affected: []
  interface_changes:
    - interface: "config.yaml omlx section"
      change_type: "addition"
      details: "Optional worker_model / reviewer_model keys; reviewer_model populated with Magistral."
      backward_compatible: "yes"

testing_requirements:
  test_approach: >
    Verify precedence (CLI > config > default_model). With omlx.reviewer_model set and no CLI
    override, run_loop uses Magistral for review and Devstral for work. Absent keys reproduce
    current behaviour. Confirm py_compile clean and a real review phase parses a verdict.
  test_cases:
    - scenario: "reviewer_model set in config, no CLI override."
      expected_result: "Review phase uses Magistral; work phase uses default_model (Devstral)."
    - scenario: "worker_model and reviewer_model both absent."
      expected_result: "Both roles use default_model (unchanged behaviour)."
    - scenario: "--reviewer-model passed on CLI."
      expected_result: "CLI value wins over config."
  regression_scope:
    - "Single-model runs with no per-role keys must be unchanged."
  validation_criteria:
    - "Precedence CLI > config > default_model holds."
    - "py_compile passes on orchestrator.py."

implementation:
  effort_estimate: "< 1 hour"
  implementation_steps:
    - step: "Edit the two per-role resolution lines in main_async."
      owner: "Tactical Domain (Claude Code / AEL)"
    - step: "Add reviewer_model and Magistral context-window entry to config.yaml."
      owner: "Tactical Domain (Claude Code / AEL)"
  rollback_procedure: "Revert the commit; remove the config keys."

traceability:
  related_issues:
    - issue_ref: "issue-a7d3f8b1"
      relationship: "resolves"

notes: >
  Magistral reviewer verdict path verified this session (clean SHIP/REVISE, no reasoning
  leakage); context window 131072 from the model config.json. Native tool-calling to be
  confirmed on the first real review phase.

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
