Created: 2026 July 29

```yaml
prompt_info:
  id: "prompt-e4b1a7c3"
  task_type: "debug"
  source_ref: "change-e4b1a7c3"
  date: "2026-07-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-e4b1a7c3"
    change_iteration: 1

context:
  purpose: >
    Stop bin/propagate.sh copying the source repository's AEL runtime state
    into every downstream project, and stop it overwriting project-specific
    ai/context.md, without regressing new-project provisioning.
  integration: >
    bin/propagate.sh — the EXCLUDES array and the propagation section that
    follows the confirmation prompt.
  constraints:
    - "Do not change the preview or confirmation flow"
    - "Do not change existing config.yaml, workspace/ or dashboard-alerts.md exclusions"
    - "Do not leave the obsolete ael/state/ pattern in place"
    - "Anchor the state exclude so it does not match at arbitrary depth"
    - "New projects must still receive the context.md template"
    - "Verify with bash -n after edit"

specification:
  description: >
    Correct the state exclude to the post-restructure path, exclude
    context.md from the main pass, and seed context.md only when absent.
  requirements:
    functional:
      - "Replace --exclude='ael/state/' with --exclude='/state/'"
      - "Add --exclude='/context.md' classified alongside config.yaml as project-specific"
      - "After the main rsync, run a second pass copying ai/context.md with --ignore-existing"
      - "Report whether the seeding pass created the file or left an existing one untouched"
    technical:
      language: "bash"
      version: ""
      standards:
        - "Preserve set -euo pipefail"
        - "Match existing comment and section-header style"

design:
  architecture: "Two exclude-list edits plus one additional rsync invocation after the main transfer"
  components:
    - name: "EXCLUDES"
      type: "module"
      purpose: "Protect runtime state and project-specific context"
      logic:
        - "/state/ anchored to the transfer root (ai/)"
        - "/context.md anchored to the transfer root"
    - name: "context seeding pass"
      type: "module"
      purpose: "Provide the template to new projects without overwriting existing copies"
      logic:
        - "rsync -av --ignore-existing ai/context.md target/ai/"
        - "Report seeded vs preserved"
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
      content: "Corrected excludes and context.md seeding pass per design"

success_criteria:
  - "Source ai/state/ralph/ is not transferred to the target"
  - "A filled-in target ai/context.md survives propagation unchanged"
  - "A target without ai/context.md receives the template"
  - "config.yaml, workspace/ and dashboard-alerts.md exclusions unchanged"
  - "Preview and confirmation flow unchanged"
  - "bash -n reports no syntax errors"

tactical_brief: |
  File: bin/propagate.sh. Read the EXCLUDES array and the propagation section before editing.
  Defect 1: --exclude='ael/state/' is a pre-restructure path. AEL state now lives at ai/state/, which nothing matches, so live Ralph state propagates into every project. A stale work-summary.txt there suppresses change-a2f9c4d1 synthesis; a stale audit-index.md would switch recipe selection.
  Defect 2: ai/context.md is project-specific like config.yaml but is not excluded, so propagation overwrites downstream copies with the unfilled template.
  Fix: replace 'ael/state/' with '/state/'; add '/context.md'; after the main rsync add a second pass, rsync -av --ignore-existing "${AI_SRC}/context.md" "${PROJECT_AI}/", reporting seeded vs preserved.
  Constraints: keep preview/confirmation flow; keep other excludes; anchor both new patterns; new projects must still get the template; verify bash -n.

notes: >
  Execution: Claude Desktop (Opus 5), direct implementation via Filesystem MCP
  at William Watson's instruction. P08 strategic audit by an independent
  session remains outstanding; the implementer cannot supply it.
```
