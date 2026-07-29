Created: 2026 July 29

```yaml
prompt_info:
  id: "prompt-d1f4a83b"
  task_type: "debug"
  source_ref: "change-d1f4a83b"
  target_profile: "claude-desktop-direct"
  date: "2026-07-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-d1f4a83b"
    change_iteration: 1

context:
  purpose: >
    Ensure the review gates receive a manifest of the current cycle's actual
    output at the worker's final-response exit; enforce path containment on
    every argument a write tool carries; confine the leading-token strip to an
    actual verdict; and stop a detached run blocking on a terminal prompt.
  integration: >
    ai/ael/src/orchestrator.py only — a new helper beside
    _synthesize_work_summary, its call site in run_phase's F13 branch, and
    one-condition corrections in _validate_write_scope, _strip_verdict and
    run_loop's max-iterations prompt.
  constraints:
    - "Never overwrite or alter the worker's own final response — append only"
    - "Append only when observed deliverables exist and the worker's text names none of them"
    - "Do not modify _synthesize_work_summary or the three exits it serves"
    - "Do not modify _normalize_verdict"
    - "Do not extend scope validation to non-write tools"
    - "A terminal-launched run must still receive the continue prompt"
    - "Verify with python3 -m py_compile after edit"

specification:
  description: >
    Four edits to ai/ael/src/orchestrator.py, closing findings N1-N4 of
    issue-d1f4a83b.
  requirements:
    functional:
      - "N1: after the F13 write of the worker's final response, append a labelled manifest of observed writes when the response names none of them"
      - "N1: filter observed writes by the same two rules _synthesize_work_summary uses — outside state_dir, and os.path.isfile"
      - "N1: suppress the append when any deliverable basename appears in the response text"
      - "N2: _validate_write_scope tests every present string value among path, file_path, destination and new_path, returning on the first outside project_root"
      - "N3: _strip_verdict drops the leading token only when _is_verdict_line accepts it; otherwise the text is returned unchanged"
      - "N4: run_loop takes the max-iterations continue prompt only when sys.stdin.isatty(); otherwise it logs, declines, and returns 1"
    technical:
      language: "python"
      version: "3.11"
      standards:
        - "PEP 8; type hints on the new function"
        - "Docstrings matching the existing module convention"
        - "Comment each edit with the change id and the reasoning, as the surrounding change-a2f9c4d1 / f5c28a04 / 3b9e6d72 comments do"

design:
  architecture: >
    The worker's account and the machine-readable manifest are separated at the
    one exit that conflated them, by extension rather than replacement. The
    other three edits each add a single missing condition at the point the wrong
    assumption is made, leaving the surrounding logic untouched.
  components:
    - name: "_append_observed_manifest"
      type: "function"
      purpose: "Supply the gates with this cycle's deliverables when the worker's final response does not"
      logic:
        - "Filter written_paths: not under state_dir, and isfile"
        - "Return False when the filtered set is empty"
        - "Return False when any deliverable basename appears in content"
        - "Append a labelled 'Files written:' section to work-summary.txt"
        - "Never raise; log and return False on OSError"
    - name: "run_phase F13 branch"
      type: "function"
      purpose: "Invoke the append after the worker's response is persisted"
      logic:
        - "write_state, then _manifest_written = True, then _append_observed_manifest"
    - name: "_validate_write_scope"
      type: "function"
      purpose: "Make containment an obligation on every path in the call"
      logic:
        - "Collect present string values for path, file_path, destination, new_path"
        - "Return None when none is present"
        - "Return a scope violation on the first value outside project_root"
    - name: "_strip_verdict fallback"
      type: "function"
      purpose: "Leave verdict-free text intact"
      logic:
        - "If no isolated verdict line was removed and the leading token is not a verdict, return text.strip()"
    - name: "run_loop continue prompt"
      type: "function"
      purpose: "Terminate a detached run on its own budget"
      logic:
        - "if not sys.stdin.isatty(): log, print the declined default, answer 'n'"
        - "else: the existing prompt and try/except"
  dependencies:
    internal:
      - "_is_verdict_line — reused by the _strip_verdict guard"
      - "write_state, _WRITE_TOOLS, _extract_deliverables — reused unchanged"
    external:
      - "sys, os (already imported)"

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
    - "Run python3 -m py_compile on the orchestrator"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "_append_observed_manifest and its F13 call site; full-argument scope validation; guarded _strip_verdict fallback; non-interactive continue prompt"

success_criteria:
  - "ai/ael/src/orchestrator.py compiles with no syntax errors"
  - "A cycle whose worker writes a deliverable and ends on a final response naming no file yields a non-empty _extract_deliverables result"
  - "A worker final response that does name its deliverable produces no appended section"
  - "A phase with no observed deliverables produces no appended section"
  - "move_file with an in-project path and an out-of-project destination is rejected"
  - "rename_file with an in-project path and an out-of-project new_path is rejected"
  - "A write wholly inside project_root is still allowed, and non-write tools are still unvalidated"
  - "_strip_verdict leaves a verdict-free message unchanged and is otherwise unchanged"
  - "A detached run reaching max_iterations logs the non-interactive decline and exits rather than blocking"

tactical_brief: |
  File: ai/ael/src/orchestrator.py. Read run_phase's final-response branch, _validate_write_scope, _strip_verdict and run_loop's max-iterations block before editing.
  N1: F13 writes the worker's final message verbatim as work-summary.txt. _extract_deliverables parses that file, and the syntax, pytest and read-evidence gates act on the result, so a final message that is a sentence rather than a manifest silently disables all three. Fix: add _append_observed_manifest(state_dir, written_paths, content, log) beside _synthesize_work_summary, filtering written_paths to paths outside state_dir that are files, returning False when the set is empty or when any basename already appears in content, and otherwise appending a labelled 'Files written:' section. Call it in the F13 is_worker_phase branch after write_state. Never overwrite the worker's own text.
  N2: _validate_write_scope tests `path or file_path or destination` — one value. A move supplying source as path and destination as destination is validated on the source only, so a move out of the project root passes. Fix: test every present value among path, file_path, destination, new_path.
  N3: _strip_verdict's fallback drops the first token even when the message carries no verdict, which happens because _normalize_verdict defaults to REVISE. Fix: guard the fallback with _is_verdict_line on that token.
  N4: run_loop's continue prompt calls input(); under ael-mcp stdin is neither a terminal nor closed, so it blocks forever. Fix: prompt only when sys.stdin.isatty().
  Constraints: do not touch _synthesize_work_summary, _normalize_verdict, or non-write scope validation. Verify with py_compile.

notes: >
  Execution: Claude (Cowork session, Opus 5), direct implementation via file
  tools per dev/cowork-remediation-prompt-2026-07-29.md §7.0 — no Claude Code
  and no AEL. This prompt records the specification implemented, authored
  alongside the work rather than dispatched to a Tactical Domain executor.
  Independent verification remains outstanding and is the stated precondition
  for closing the triple.
```
