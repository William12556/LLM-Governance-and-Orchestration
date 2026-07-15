Created: 2026 July 15

# Prompt a7d3f8b1 — Config-driven per-role worker/reviewer model resolution

```yaml
prompt_info:
  id: "prompt-a7d3f8b1"
  task_type: "enhancement"
  source_ref: "change-a7d3f8b1"
  target_profile: "claude_code"
  date: "2026-07-15"
  iteration: 1
  coupled_docs:
    change_ref: "change-a7d3f8b1"
    change_iteration: 1

context:
  purpose: "Allow a persistent per-role worker/reviewer model via config, and set Magistral as the default reviewer."
  integration: "main_async in ai/ael/src/orchestrator.py; ai/ael/config.yaml."
  knowledge_references: []
  constraints:
    - "Precedence must be CLI flag > config key > default_model."
    - "Backward compatible: absent config keys reproduce current behaviour exactly."
    - "Do not change worker default (already set via omlx.default_model)."

specification:
  description: >
    Insert a config tier into per-role model resolution and populate the reviewer model and its
    context window.
  requirements:
    functional:
      - "In main_async, resolve worker_model = args.worker_model or omlx_cfg.get('worker_model') or model."
      - "In main_async, resolve reviewer_model = args.reviewer_model or omlx_cfg.get('reviewer_model') or model."
      - "Where model = args.model or omlx_cfg['default_model'] (unchanged)."
      - "Add omlx.reviewer_model: 'Magistral-Small-2509-MLX-6bit' to config.yaml."
      - "Add a model_context_windows entry 'Magistral-Small-2509-MLX-6bit': 131072 to config.yaml."
    technical:
      language: "Python"
      version: "3.11+"
      standards:
        - "Comprehensive error handling"
        - "Professional docstrings"

design:
  architecture: "Two-line resolution change plus config additions."
  components:
    - name: "main_async"
      type: "function"
      purpose: "Resolve models and dispatch the loop."
      logic:
        - "Add omlx_cfg.get('worker_model') as the middle term of worker_model resolution."
        - "Add omlx_cfg.get('reviewer_model') as the middle term of reviewer_model resolution."
        - "Leave model = args.model or omlx_cfg['default_model'] unchanged."
  dependencies:
    internal:
      - "ai/ael/src/orchestrator.py"
      - "ai/ael/config.yaml"
    external: []

deliverable:
  format_requirements:
    - "Save generated code directly to specified paths"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: ""
    - path: "ai/ael/config.yaml"
      content: ""

success_criteria:
  - "With omlx.reviewer_model set and no CLI override, the loop uses Magistral for review and default_model (Devstral) for work."
  - "With no per-role config keys, both roles use default_model (unchanged behaviour)."
  - "A CLI --reviewer-model / --worker-model value overrides the config key."
  - "py_compile passes on ai/ael/src/orchestrator.py."

tactical_brief: |
  In ai/ael/src/orchestrator.py, function main_async, update the two per-role model
  resolution lines so a config key sits between the CLI flag and the default model:

      worker_model   = args.worker_model   or omlx_cfg.get("worker_model")   or model
      reviewer_model = args.reviewer_model or omlx_cfg.get("reviewer_model") or model

  Leave `model = args.model or omlx_cfg["default_model"]` unchanged. Precedence must be
  CLI flag > config key > default_model. Absent config keys must reproduce current behaviour.

  Then in ai/ael/config.yaml:
    - Under the omlx: section add:  reviewer_model: "Magistral-Small-2509-MLX-6bit"
      (worker_model is supported by the code but should be left unset; the worker uses
       default_model, which is already the Devstral 8bit.)
    - Under context.model_context_windows add:
        "Magistral-Small-2509-MLX-6bit": 131072

  Deliverables: ai/ael/src/orchestrator.py and ai/ael/config.yaml.
  Success: heterogeneous loop (Devstral work, Magistral review) runs with no CLI flag;
  absent keys reproduce current behaviour; py_compile clean.

notes: "Resolves issue-a7d3f8b1 via change-a7d3f8b1. Magistral verdict path verified; context window 131072 from model config.json. Confirm native tool-calling on the first real review phase."
```

---

Copyright (c) 2026 William Watson. MIT License.
