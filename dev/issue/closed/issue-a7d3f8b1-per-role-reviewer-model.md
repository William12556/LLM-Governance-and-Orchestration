Created: 2026 July 15

# Issue a7d3f8b1 — No persistent per-role reviewer/worker model from config

```yaml
issue_info:
  id: "issue-a7d3f8b1"
  title: "Orchestrator cannot set a persistent per-role reviewer or worker model from config"
  date: "2026-07-15"
  reporter: ""
  status: "closed"
  severity: "low"
  type: "enhancement"
  iteration: 1
  coupled_docs:
    change_ref: "change-a7d3f8b1"
    change_iteration: 1

source:
  origin: "code_review"
  test_ref: "dev/reports/report-omlx-ael-efficiency-2026-07-15.md"
  description: >
    A heterogeneous worker/reviewer setup (Devstral worker, Magistral reviewer) cannot be
    configured persistently. main_async derives both worker_model and reviewer_model from a
    single omlx.default_model; only the --reviewer-model / --worker-model CLI flags override
    per run.

affected_scope:
  components:
    - name: "main_async"
      file_path: "ai/ael/src/orchestrator.py"
  designs:
    - design_ref: "dev/design/design-ael-orchestrator.md"
  version: ""

behavior:
  expected: >
    Config can set a standing reviewer model (and, optionally, worker model) distinct from the
    default, so a heterogeneous loop runs without a per-invocation CLI flag.
  actual: >
    main_async sets model = args.model or omlx_cfg['default_model'], then both
    worker_model and reviewer_model fall back to that same model. No config key exists for
    either role.
  impact: >
    Running Magistral as reviewer requires passing --reviewer-model on every invocation; the
    choice cannot be persisted.
  workaround: "Pass --reviewer-model Magistral-Small-2509-MLX-6bit on each run."

analysis:
  root_cause: "Per-role model resolution reads only the CLI flag and the single default_model; no config tier exists between them."
  technical_notes: >
    Add a config tier between CLI and default_model: args.X or omlx_cfg.get('X') or model.
    Backward compatible — absent keys reproduce current behaviour. Reviewer verdict parsing for
    Magistral (mistral3) was verified this session (clean SHIP/REVISE, no reasoning leakage);
    context window is 131072 (model config.json). Native tool-calling for Magistral is expected
    (mistral3 family, as Devstral) and is to be confirmed on the first real review phase.

resolution:
  approach: "Add config-driven per-role model resolution (worker_model, reviewer_model). See change-a7d3f8b1."
  change_ref: "change-a7d3f8b1"

traceability:
  design_refs:
    - "dev/design/design-ael-orchestrator.md"
  change_refs:
    - "change-a7d3f8b1"
  test_refs:
    - "dev/reports/report-omlx-ael-efficiency-2026-07-15.md"

notes: >
  Worker default (Devstral 8bit) was already set via omlx.default_model in a prior config edit;
  this issue concerns the reviewer role and the general per-role capability.

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
      - "Closed: config-driven per-role resolution and Magistral reviewer config implemented and verified in orchestrator.py and config.yaml; triple moved to closed/"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t03_issue"
```

---

Copyright (c) 2026 William Watson. MIT License.
