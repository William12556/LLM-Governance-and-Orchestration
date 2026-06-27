Created: 2026 June 17

```yaml
prompt_info:
  id: "prompt-b4e8c012"
  task_type: "code_generation"
  source_ref: "change-b4e8c012"
  date: "2026-06-17"
  iteration: 1
  coupled_docs:
    change_ref: "change-b4e8c012"
    change_iteration: 1

context:
  purpose: >
    Automate archiving of audit-index.md and audit-report.md to
    ai/workspace/audit/ after a successful audit loop SHIP.
  integration: >
    orchestrator.py — loop mode main_async post-SHIP path.
  constraints:
    - "No new external dependencies. shutil is stdlib."
    - "No regression to standard Ralph Loop path."
    - "archive function must be a no-op when audit-report.md is absent."

specification:
  description: >
    Four changes to ai/ael/src/orchestrator.py.
  requirements:
    functional:
      - "After run_loop returns rc=0 in loop mode, auto-archive audit artifacts"
      - "Detect audit mode by presence of audit-report.md in state_dir"
      - "Extract UUID from --task basename via re.search(r'[0-9a-f]{8}', ...)"
      - "Fall back to datetime.datetime.now().strftime('%Y%m%d') if UUID absent"
      - "Create ai/workspace/audit/ if it does not exist"
      - "Copy audit-index.md -> audit-<uid>-index.md (skip if absent, log warning)"
      - "Copy audit-report.md -> audit-<uid>-report.md"
      - "Console output: [green][ael] audit archived: <path>[/green] per file"
      - "Console output: [green][ael] N audit artifact(s) archived to <dir>[/green]"
      - "Add audit-index.md and audit-report.md to _RESET_FILES"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Use shutil.copy2 for file copy"
        - "Use os.makedirs(output_dir, exist_ok=True)"
        - "Log all operations via existing log.info / log.warning"

design:
  architecture: "Standalone helper function + call site in main_async"
  components:
    - name: "_archive_audit_artifacts"
      type: "function"
      purpose: "Copy audit artifacts from state_dir to ai/workspace/audit/ with canonical names"
      interface:
        inputs:
          - name: "state_dir"
            type: "str"
            description: "Absolute path to AEL state directory"
          - name: "task_path"
            type: "str | None"
            description: "Value of args.task; may be a file path or bare string"
          - name: "log"
            type: "logging.Logger"
            description: "AEL logger"
        outputs:
          type: "None"
          description: "Side effects only: file copies and console/log output"
      logic:
        - "report_src = os.path.join(state_dir, 'audit-report.md')"
        - "Return early (no-op) if report_src does not exist"
        - "index_src = os.path.join(state_dir, 'audit-index.md')"
        - "Extract uid: re.search(r'[0-9a-f]{8}', os.path.basename(task_path or ''));"
        - "  if no match: uid = datetime.datetime.now().strftime('%Y%m%d'); log.warning"
        - "output_dir = os.path.join(os.getcwd(), 'ai', 'workspace', 'audit')"
        - "os.makedirs(output_dir, exist_ok=True)"
        - "For each (src, suffix) in [(index_src, 'index'), (report_src, 'report')]:"
        - "  if src exists: shutil.copy2(src, os.path.join(output_dir, f'audit-{uid}-{suffix}.md'))"
        - "  else: log.warning(...)"
        - "Console summary: N artifact(s) archived"
  dependencies:
    internal:
      - "console (Rich Console instance)"
      - "log (logging.Logger)"
    external:
      - "shutil (stdlib)"
      - "os (stdlib)"
      - "re (stdlib — already imported)"
      - "datetime (stdlib — already imported)"

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "See implementation steps below"

success_criteria:
  - "import shutil present in stdlib imports block"
  - "audit-index.md and audit-report.md present in _RESET_FILES list"
  - "_archive_audit_artifacts function defined with correct signature"
  - "Call to _archive_audit_artifacts present in main_async loop branch after rc==0"
  - "ai/ael/src/orchestrator.py has no syntax errors"
```

---

## Implementation Steps

### Step 1 — Add `import shutil`

In the stdlib imports block (after `import re`, before `import subprocess`), insert:

```python
import shutil
```

### Step 2 — Extend `_RESET_FILES`

Current:
```python
_RESET_FILES = [
    "task.md",
    "iteration.txt",
    "work-summary.txt",
    "work-complete.txt",
    "review-result.txt",
    "review-feedback.txt",
    ".ralph-complete",
    "RALPH-BLOCKED.md",
]
```

Replace with:
```python
_RESET_FILES = [
    "task.md",
    "iteration.txt",
    "work-summary.txt",
    "work-complete.txt",
    "review-result.txt",
    "review-feedback.txt",
    ".ralph-complete",
    "RALPH-BLOCKED.md",
    "audit-index.md",
    "audit-report.md",
]
```

### Step 3 — Add `_archive_audit_artifacts()`

Insert the following function immediately before `load_yaml`:

```python
def _archive_audit_artifacts(state_dir: str, task_path: str | None, log: logging.Logger) -> None:
    """
    Copy audit-index.md and audit-report.md from state_dir to ai/workspace/audit/
    with canonical naming: audit-<uuid>-index.md and audit-<uuid>-report.md.
    Called after a successful audit loop SHIP. No-op if audit-report.md is absent.
    UUID is extracted from the task file path basename (first 8-hex substring).
    Falls back to yyyymmdd timestamp if UUID cannot be determined.
    """
    report_src = os.path.join(state_dir, "audit-report.md")
    if not os.path.exists(report_src):
        return  # not an audit run

    index_src = os.path.join(state_dir, "audit-index.md")

    uid = None
    if task_path:
        m = re.search(r"[0-9a-f]{8}", os.path.basename(task_path))
        uid = m.group(0) if m else None
    if not uid:
        uid = datetime.datetime.now().strftime("%Y%m%d")
        log.warning("archive audit: UUID not found in task path — using date fallback: %s", uid)

    output_dir = os.path.join(os.getcwd(), "ai", "workspace", "audit")
    os.makedirs(output_dir, exist_ok=True)

    archived = 0
    for src, suffix in [(index_src, "index"), (report_src, "report")]:
        if os.path.exists(src):
            dst = os.path.join(output_dir, f"audit-{uid}-{suffix}.md")
            shutil.copy2(src, dst)
            archived += 1
            log.info("archive audit: %s -> %s", src, dst)
            console.print(f"[green][ael] audit archived: {escape(dst)}[/green]")
        else:
            log.warning("archive audit: %s not found — skipping", src)

    if archived:
        console.print(
            f"[green][ael] {archived} audit artifact(s) archived to {escape(output_dir)}[/green]"
        )
```

### Step 4 — Call site in `main_async`

In `main_async`, locate the `else:  # loop` branch. After the `rc = await run_loop(...)` call, add the archive call:

Current:
```python
        else:  # loop
            worker_model   = args.worker_model   or model
            reviewer_model = args.reviewer_model or model
            rc = await run_loop(client, mcp, worker_model, reviewer_model,
                                work_recipe, rev_recipe, task, max_iter, phase_max_iter,
                                state_dir, log,
                                context_window=context_window,
                                budget_warn_pct=budget_warn,
                                budget_abort_pct=budget_abort,
                                mcp_error_threshold=mcp_error_thresh,
                                max_tool_calls_per_iter=max_tool_calls,
                                preflight_check=do_preflight,
                                deadline=deadline)
```

Replace with:
```python
        else:  # loop
            worker_model   = args.worker_model   or model
            reviewer_model = args.reviewer_model or model
            rc = await run_loop(client, mcp, worker_model, reviewer_model,
                                work_recipe, rev_recipe, task, max_iter, phase_max_iter,
                                state_dir, log,
                                context_window=context_window,
                                budget_warn_pct=budget_warn,
                                budget_abort_pct=budget_abort,
                                mcp_error_threshold=mcp_error_thresh,
                                max_tool_calls_per_iter=max_tool_calls,
                                preflight_check=do_preflight,
                                deadline=deadline)
            if rc == 0:
                _archive_audit_artifacts(state_dir, args.task, log)
```

---

```yaml
tactical_brief: |
  File: ai/ael/src/orchestrator.py
  Read the file before making any edits.

  Change 1 — add import shutil to stdlib imports block (after import re):
    insert: import shutil

  Change 2 — extend _RESET_FILES constant:
    append two entries: "audit-index.md" and "audit-report.md"

  Change 3 — add function _archive_audit_artifacts(state_dir, task_path, log):
    insert immediately before def load_yaml.
    Full implementation in Implementation Steps §Step 3.

  Change 4 — add archive call in main_async loop branch:
    after: rc = await run_loop(...) in the else: # loop branch
    insert: if rc == 0:\n        _archive_audit_artifacts(state_dir, args.task, log)

  Constraints:
    - No other changes to orchestrator.py
    - Verify no syntax errors after edit
    - shutil.copy2 for file copy
    - os.makedirs(output_dir, exist_ok=True)
    - Function is a no-op when audit-report.md absent in state_dir
```
