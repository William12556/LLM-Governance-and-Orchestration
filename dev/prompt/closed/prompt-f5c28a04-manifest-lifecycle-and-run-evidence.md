Created: 2026 July 29

```yaml
prompt_info:
  id: "prompt-f5c28a04"
  task_type: "debug"
  source_ref: "change-f5c28a04"
  target_profile: "claude-desktop-direct"
  date: "2026-07-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-f5c28a04"
    change_iteration: 1

context:
  purpose: >
    Give work-summary.txt a cycle lifetime rather than a run lifetime, so each
    Ralph Loop cycle is adjudicated on its own output; decide the worker
    phase's iteration-exhaustion return code from what that phase produced
    rather than from what is on disk; record move/rename deliverables at their
    destination; make reset idempotent; and preserve run logs between sessions.
  integration: >
    ai/ael/src/orchestrator.py — run_loop cycle preamble, run_phase write-target
    recording and exhaustion exit, reset_state, and a new archive_prior_logs
    helper invoked from main_async. ai/ael/config.yaml — one new loop key and
    the reviewer model correction. .gitignore — re-include ai/logs/.
  constraints:
    - "Do not alter review-phase behaviour; synthesis stays guarded by is_worker_phase"
    - "Do not alter the BLOCKED exit — a malformed phase must not present a manifest"
    - "Do not alter the F13 final-response summary content"
    - "Do not change write-target recording for any tool outside the move/rename set"
    - "log_archive_dir must be a no-op when null or absent, so downstream projects are unaffected"
    - "Preserve every existing config.yaml key"
    - "Verify with python -m py_compile after edit"

specification:
  description: >
    Five edits to orchestrator.py, two to config.yaml, one to .gitignore, and
    corrections to two claims in change-a2f9c4d1.
  requirements:
    functional:
      - "Clear work-summary.txt at the top of each run_loop cycle, before the work phase"
      - "Track a phase-scoped _manifest_written flag set when the worker writes work-summary.txt, whether via a write tool or the F13 final-response path"
      - "At the exhaustion exit, return 0 when synthesis wrote a manifest now or _manifest_written is set, else 1"
      - "For move, rename, move_file and rename_file, record the destination argument as the write target"
      - "reset_state returns 0 when the state directory is absent"
      - "archive_prior_logs copies *.log and *.LOG out of state_dir before each run, skipping files already present at the destination"
      - "config.yaml gains loop.log_archive_dir; reviewer_model becomes Magistral-Small-2509-MLX-8bit with a matching model_context_windows entry"
      - "change-a2f9c4d1's gate-bypass benefit and rc=1 mitigation are corrected in place, with the correction recorded in its version history"
    technical:
      language: "python"
      version: "3.11"
      standards:
        - "PEP 8; type hints on the new function"
        - "Docstrings matching the existing module convention"
        - "Comment each edit with the change id and the reasoning, as the surrounding change-a2f9c4d1 and F-number comments do"

design:
  architecture: >
    The manifest's lifetime is narrowed at its owner (run_loop), and each phase
    exit is made self-sufficient by tracking production within the phase. The
    two are independently sufficient; both are implemented so the return code
    stays correct if a future caller clears differently.
  components:
    - name: "run_loop cycle preamble"
      type: "function"
      purpose: "Narrow the manifest lifetime to one cycle"
      logic:
        - "clear_state(state_dir, 'work-summary.txt') immediately after the iteration.txt write"
        - "Placed before the work phase, not before the review phase: the reviewer and all three gates read this file"
    - name: "run_phase manifest tracking"
      type: "function"
      purpose: "Make the exhaustion return code reflect this phase's own outcome"
      logic:
        - "_manifest_written: bool = False declared alongside _written_paths"
        - "Set in the F13 final-response branch"
        - "Set when a successful write tool targets state_dir/work-summary.txt"
        - "Exhaustion exit returns 0 when _synthesize_work_summary returned True or _manifest_written is set"
    - name: "write-target recording"
      type: "function"
      purpose: "Record the path at which a deliverable actually exists"
      logic:
        - "move/rename tools: destination, then new_path, then path, then file_path"
        - "All other tools: unchanged — path, then file_path, then destination"
    - name: "archive_prior_logs"
      type: "function"
      purpose: "Preserve run evidence outside transient state"
      logic:
        - "No-op when archive_dir is falsy or state_dir is absent"
        - "Copy each *.log / *.LOG not already present at the destination"
        - "Never raise; report per-file failures and continue"
  dependencies:
    internal:
      - "_synthesize_work_summary — return value now consumed"
      - "clear_state, write_state, _WRITE_TOOLS — reused unchanged"
    external:
      - "shutil (already imported)"

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py, ai/ael/config.yaml, .gitignore and dev/change/change-a2f9c4d1-work-summary-synthesis.md in place"
    - "Run python -m py_compile on the orchestrator"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "Per-cycle clear, manifest tracking, destination recording, idempotent reset, archive_prior_logs"
    - path: "ai/ael/config.yaml"
      content: "loop.log_archive_dir; reviewer_model and context-window correction"
    - path: ".gitignore"
      content: "Re-include ai/logs/ with a note on the case-insensitive *.log collision"
    - path: "dev/change/change-a2f9c4d1-work-summary-synthesis.md"
      content: "Two corrected claims, a version-history entry, and a related_changes link to change-f5c28a04"

success_criteria:
  - "ai/ael/src/orchestrator.py compiles with no syntax errors"
  - "ai/ael/config.yaml parses and retains every pre-existing key"
  - "A cycle in which the worker writes nothing returns rc=1 even when an earlier cycle produced deliverables"
  - "A worker that wrote its own work-summary.txt and then exhausted its budget returns rc=0 with that summary intact"
  - "A deliverable created via move_file appears in the manifest at its destination"
  - "--mode reset against a project with no state directory exits 0"
  - "With log_archive_dir unset, no archiving occurs and behaviour is unchanged"
  - "Review-phase behaviour and the BLOCKED path are unchanged"

tactical_brief: |
  File: ai/ael/src/orchestrator.py. Read run_loop, run_phase and reset_state before editing.
  Defect F1/F2: work-summary.txt is cleared once at loop start, so from cycle 2 a prior cycle's manifest survives. Synthesis never overwrites an existing summary, so it is suppressed; the exhaustion exit tests os.path.exists and therefore returns 0 for a cycle that produced nothing. The gates re-adjudicate the previous cycle's deliverables.
  Fix: clear work-summary.txt at the top of each run_loop cycle, before the work phase (not before the review phase — the reviewer and all three gates read it). Add a phase-scoped _manifest_written flag, set in the F13 final-response branch and when a write tool targets state_dir/work-summary.txt; return 0 at the exhaustion exit only when synthesis wrote a manifest now or that flag is set.
  Defect F3: write targets use `path or file_path or destination`, copied from _validate_write_scope where the source is correct. For move/rename the destination is what exists afterwards, so the deliverable fails the isfile filter and is dropped. Fix: branch on move/rename/move_file/rename_file to prefer destination.
  Also: reset_state returns 0 for an absent state directory; add archive_prior_logs(state_dir, archive_dir) copying *.log/*.LOG out of state_dir before each run, driven by a new null-default loop.log_archive_dir.
  Constraints: no change to review-phase behaviour, the BLOCKED path, or non-move write recording. Verify with py_compile.

notes: >
  Execution: Claude Desktop (Opus 5), direct implementation via file tools at
  William Watson's instruction — no Claude Code and no AEL. This prompt is a
  record of the specification implemented, authored alongside the work rather
  than dispatched to a Tactical Domain executor. A P08 strategic audit by an
  independent session, and a live three-cycle run once change-3b9e6d72 is in
  place, both remain outstanding.
```
