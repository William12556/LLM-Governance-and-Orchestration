Created: 2026 July 29

```yaml
prompt_info:
  id: "prompt-8c1a4f5e"
  task_type: "debug"
  source_ref: "change-8c1a4f5e"
  target_profile: "claude-desktop-direct"
  date: "2026-07-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-8c1a4f5e"
    change_iteration: 1

context:
  purpose: >
    Make the context.md seeding pass reachable when a missing context.md is the
    only difference between framework and target, and correct two latent
    defects in the same region of the script.
  integration: >
    bin/propagate.sh — the EXCLUDES array, the preview and its early exit, and
    the seeding pass that follows the main transfer.
  constraints:
    - "Do not change the main rsync invocation or the confirmation flow"
    - "Do not change the /state/ or /context.md exclusions"
    - "A filled-in downstream ai/context.md must still never be overwritten"
    - "Preserve set -euo pipefail"
    - "Match the existing comment and section-header style"
    - "Verify with bash -n after edit"

specification:
  description: >
    Evaluate the seed condition before the preview's early exit, surface it in
    the preview, key the seeding branch on it, and anchor the three unanchored
    path-specific excludes.
  requirements:
    functional:
      - "Set NEEDS_SEED from [[ -f \"${PROJECT_AI}/context.md\" ]] before CHANGES is computed"
      - "Exit early only when CHANGES is empty and NEEDS_SEED is false"
      - "Print CHANGES when non-empty, otherwise a '(no framework files differ)' note"
      - "Print a seed line in the preview when NEEDS_SEED is true"
      - "Key the seeding branch on NEEDS_SEED and remove --ignore-existing"
      - "Anchor config.yaml to /ael/config.yaml, workspace/ to /workspace/, dashboard-alerts.md to /dashboard-alerts.md"
    technical:
      language: "bash"
      version: ""
      standards:
        - "Preserve set -euo pipefail"
        - "Comment why the remaining unanchored patterns stay unanchored"

design:
  architecture: >
    The seed decision is made from the target's own state rather than inferred
    from rsync's change detection, which cannot see an excluded file. Moving the
    test above the early exit is sufficient; the transfer itself is untouched.
  components:
    - name: "EXCLUDES"
      type: "module"
      purpose: "Protect runtime state and project-specific files at their actual locations"
      logic:
        - "Path-specific patterns anchored with a leading / relative to ai/"
        - "Editor and interpreter droppings left unanchored deliberately"
    - name: "preview"
      type: "module"
      purpose: "State every pending action before the confirmation prompt"
      logic:
        - "NEEDS_SEED computed first"
        - "Early exit requires both an empty CHANGES and NEEDS_SEED false"
        - "Seed reported as its own line"
    - name: "seeding pass"
      type: "module"
      purpose: "Give new projects the template without overwriting existing copies"
      logic:
        - "Branch on NEEDS_SEED"
        - "Plain rsync -a; absence already established"
  dependencies:
    internal: []
    external:
      - "rsync"

deliverable:
  format_requirements:
    - "Edit bin/propagate.sh in place"
    - "Run bash -n on the edited file"
  files:
    - path: "bin/propagate.sh"
      content: "NEEDS_SEED hoisted above the early exit, preview seed reporting, anchored excludes, redundant flag removed"

success_criteria:
  - "bash -n reports no syntax errors"
  - "A target current except for a missing ai/context.md reports a pending seed rather than 'up to date', and receives the template on confirmation"
  - "A fully current target still reports 'Target is up to date' and exits 0"
  - "An empty target reports the full file list plus the pending seed"
  - "A re-run immediately after seeding reports up to date"
  - "A filled-in target ai/context.md survives propagation unchanged"
  - "Declining at the confirmation prompt applies neither transfer nor seed"

tactical_brief: |
  File: bin/propagate.sh. Read the EXCLUDES array, the preview section and the seeding pass before editing.
  Defect F4: CHANGES is computed with EXCLUDES, which contains /context.md, so a target differing only by a missing context.md reports no changes and exits before the seeding pass — unreachable in the case it exists for. Fix: compute NEEDS_SEED from [[ -f "${PROJECT_AI}/context.md" ]] before CHANGES; make the early exit require both an empty CHANGES and NEEDS_SEED false; report the pending seed in the preview; key the seeding branch on NEEDS_SEED.
  F5: that branch's rsync carries --ignore-existing inside an absence guard, so the flag cannot affect the outcome. Remove it.
  F6: config.yaml, workspace/ and dashboard-alerts.md are unanchored while /state/ and /context.md are anchored, so they match at any depth. Anchor them to /ael/config.yaml, /workspace/ and /dashboard-alerts.md; leave .DS_Store, __pycache__/, *.pyc and *.pyo unanchored and say why.
  Constraints: do not touch the main rsync or the confirmation flow; a filled-in downstream context.md must still never be overwritten; keep set -euo pipefail; verify bash -n.

notes: >
  Execution: Claude Desktop (Opus 5), direct implementation via file tools at
  William Watson's instruction — no Claude Code and no AEL. This prompt records
  the specification implemented rather than dispatching it to a Tactical Domain
  executor.
```
