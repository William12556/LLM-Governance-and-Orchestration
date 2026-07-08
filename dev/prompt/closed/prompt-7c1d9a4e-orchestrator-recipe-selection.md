Created: 2026 June 28

```yaml
prompt_info:
  id: "prompt-7c1d9a4e"
  task_type: "code_generation"
  source_ref: "change-7c1d9a4e"
  date: "2026-06-28"
  iteration: 1
  coupled_docs:
    change_ref: "change-7c1d9a4e"
    change_iteration: 1

context:
  purpose: >
    Select the AEL recipe pair on presence of audit-index.md in the state
    directory, replacing the hard-coded Ralph recipe load.
  integration: >
    ai/ael/src/orchestrator.py — main_async, recipe load block immediately
    before the readiness/MCP setup.
  constraints:
    - "Implementation target: Claude Code (framework source), not the AEL."
    - "No new external dependencies (os already imported)."
    - "No new CLI flag or config key."
    - "Leave the recipe_dir line unchanged; replace only the two load lines."
    - "Retain variable name rev_recipe."

specification:
  description: >
    One edit in main_async: branch recipe loading on audit-index.md presence and
    emit a startup recipe-set line.
  requirements:
    functional:
      - "If audit-index.md exists in state_dir, load audit-work.yaml and audit-review.yaml"
      - "Otherwise load ralph-work.yaml and ralph-review.yaml"
      - "Set recipe_set label ('audit' or 'ralph')"
      - "console.print the selected recipe set; log.info the selected recipe set"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Use os.path.exists / os.path.join"
        - "Use existing module-global console and the local log"

design:
  architecture: "In-place branch in main_async recipe load block"
  components:
    - name: "main_async"
      type: "function"
      purpose: "Recipe pair selection by state-directory signal"
  dependencies:
    internal:
      - "console (Rich Console instance)"
      - "log (logging.Logger)"
      - "state_dir (in scope)"
    external:
      - "os (stdlib — already imported)"

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "See Implementation Steps below"

success_criteria:
  - "audit-index.md present -> audit-work.yaml / audit-review.yaml loaded"
  - "audit-index.md absent -> ralph-work.yaml / ralph-review.yaml loaded"
  - "Startup prints and logs the selected recipe set"
  - "recipe_dir line unchanged; rev_recipe variable name retained"
  - "ai/ael/src/orchestrator.py has no syntax errors"
```

---

## Implementation Steps

### Step 1 — Replace the two recipe load lines in `main_async`

Locate (leave the `recipe_dir` line above them unchanged):

```python
    work_recipe = load_yaml(os.path.join(recipe_dir, "ralph-work.yaml"))
    rev_recipe  = load_yaml(os.path.join(recipe_dir, "ralph-review.yaml"))
```

Replace with:

```python
    # Recipe selection: audit-index.md in the state directory selects the audit
    # recipe pair; otherwise the standard Ralph Loop pair. Same signal the audit
    # scope/SHIP/archive logic keys on — mode detection is single-sourced.
    if os.path.exists(os.path.join(state_dir, "audit-index.md")):
        recipe_set = "audit"
        work_recipe = load_yaml(os.path.join(recipe_dir, "audit-work.yaml"))
        rev_recipe  = load_yaml(os.path.join(recipe_dir, "audit-review.yaml"))
    else:
        recipe_set = "ralph"
        work_recipe = load_yaml(os.path.join(recipe_dir, "ralph-work.yaml"))
        rev_recipe  = load_yaml(os.path.join(recipe_dir, "ralph-review.yaml"))
    console.print(f"[blue][ael] recipe set: {recipe_set}[/blue]")
    log.info("recipe set: %s", recipe_set)
```

---

```yaml
tactical_brief: |
  File: ai/ael/src/orchestrator.py
  Read the file before editing.

  In main_async, find the two lines that load ralph-work.yaml and
  ralph-review.yaml into work_recipe and rev_recipe. Leave the recipe_dir
  assignment above them unchanged. Replace only those two lines with an
  if/else on os.path.exists(os.path.join(state_dir, "audit-index.md")):
    - present: recipe_set = "audit"; load audit-work.yaml / audit-review.yaml
    - absent:  recipe_set = "ralph"; load ralph-work.yaml / ralph-review.yaml
  After the branch, add:
    console.print(f"[blue][ael] recipe set: {recipe_set}[/blue]")
    log.info("recipe set: %s", recipe_set)

  Constraints:
    - Retain variable name rev_recipe
    - No other changes to orchestrator.py
    - Verify no syntax errors after edit
```
