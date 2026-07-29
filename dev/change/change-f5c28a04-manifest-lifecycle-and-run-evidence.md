Created: 2026 July 29

```yaml
change_info:
  id: "change-f5c28a04"
  title: "Per-cycle manifest lifetime; exhaustion return code from phase outcome; move/rename destination recording; reset idempotency; opt-in run-log archive"
  date: "2026-07-29"
  author: "William Watson"
  status: "implemented"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-f5c28a04"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-f5c28a04"
  description: >
    Complete the work-summary manifest lifecycle that change-a2f9c4d1
    introduced, so that each cycle is adjudicated on its own output, and correct
    that document's two overstated claims.

scope:
  summary: >
    Five edits to orchestrator.py and two to config.yaml. (1) Clear
    work-summary.txt at the top of each loop cycle. (2) Track manifest
    production within the phase and derive the exhaustion return code from it
    rather than from file existence. (3) Record the destination path for
    move/rename write targets. (4) Return 0 from reset_state when the state
    directory is absent. (5) Add an opt-in log_archive_dir that copies prior run
    logs out of state_dir before each run. Configuration: point reviewer_model
    at the 8-bit Magistral actually in use, and add its context-window entry.
  affected_components:
    - name: "orchestrator (run_loop per-cycle clear)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (run_phase exhaustion exit, _manifest_written tracking)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (write-target recording)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (reset_state)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "orchestrator (archive_prior_logs, new function)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "AEL canonical configuration"
      file_path: "ai/ael/config.yaml"
      change_type: "modify"
    - name: "Repository ignore rules (re-include ai/logs/)"
      file_path: ".gitignore"
      change_type: "modify"
    - name: "change-a2f9c4d1 (claim corrections, §1.5)"
      file_path: "dev/change/change-a2f9c4d1-work-summary-synthesis.md"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "Reviewer verdict parsing — separate triple, change-3b9e6d72; a prerequisite for verifying this change end-to-end"
    - "bin/propagate.sh seeding and exclude anchoring — separate triple, change-8c1a4f5e"
    - "The stale deployed ael-mcp build (backlog §2.2) — an operational redeploy, not a source defect; ael-mcp/server.py already specifies ai/state/ralph"
    - "Grammar-constrained decoding via guided_grammar — considered under change-3b9e6d72, not adopted"
    - "Migrating state_dir out of gitignored territory — log archiving addresses the evidence loss without relocating runtime state"

rational:
  problem_statement: >
    change-a2f9c4d1 attached manifest synthesis to phase exit but left the
    manifest's lifetime at run scope. Because synthesis never overwrites an
    existing summary, a manifest that outlives its cycle suppresses the
    mechanism intended to replace it, and the exhaustion exit — which derives its
    return code from that file's presence — returns 0 for a cycle that produced
    nothing. The gates then re-adjudicate the previous cycle's deliverables. The
    vacuous-pass condition a2f9c4d1 set out to close therefore persisted from
    cycle 2 onward.
  proposed_solution: >
    Give the manifest a cycle lifetime, and decide the exhaustion return code
    from what the phase itself did rather than from what is on disk. The two are
    independently sufficient; implementing both leaves the return code correct
    even if a future caller clears differently.
  alternatives_considered:
    - option: "Clear work-summary.txt before the review phase, alongside review-feedback.txt, as the remediation backlog proposed"
      reason_rejected: >
        The reviewer and all three gates read work-summary.txt. Clearing it at
        that point would remove the manifest they exist to check, converting a
        stale-evidence defect into a no-evidence one. review-feedback.txt is
        safe to clear there only because the worker has already consumed it.
    - option: "Clear per cycle and leave the exhaustion exit testing os.path.exists"
      reason_rejected: >
        Correct as written, but the return code would remain coupled to a
        clearing step in a different function. Tracking production within the
        phase makes each exit self-sufficient.
    - option: "Timestamp the manifest and compare against cycle start"
      reason_rejected: >
        Introduces clock dependence and a comparison window for no benefit over
        a boolean tracked in the phase that writes it.
    - option: "Prefer 'destination' unconditionally in write-target recording"
      reason_rejected: >
        Some write tools accept a destination argument with non-move semantics.
        Branching on the move/rename tool names keeps the change surgical and
        leaves every other tool's recording untouched.
    - option: "Write run logs outside state_dir by default"
      reason_rejected: >
        state_dir's self-containment is a design property, and the change would
        propagate to every downstream project. An opt-in archive preserves
        evidence where wanted and changes nothing where not.
  benefits:
    - "Each cycle is adjudicated on its own output; the read-evidence, syntax and pytest gates receive only this cycle's deliverables"
    - "An unproductive cycle again returns rc=1, restoring the fail-fast property change-a2f9c4d1 intended but did not deliver"
    - "Deliverables produced by move_file or rename_file are no longer silently dropped from the manifest"
    - "reset is idempotent, so ael-mcp's reset_ael no longer reports failure on a project that has not yet run"
    - "Run evidence survives between sessions where configured"
  risks:
    - risk: "A worker that legitimately writes its manifest early and produces nothing further now has that manifest cleared at the next cycle boundary"
      mitigation: "That is the intent — the manifest describes one cycle's work. A worker with nothing to add produces no manifest and the phase correctly returns rc=1."
    - risk: "Branching write-target recording on tool name misses a move-like tool named differently"
      mitigation: "The branch covers the four names in _WRITE_TOOLS with move semantics. An unlisted tool falls through to the prior behaviour, which is no worse than before."
    - risk: "log_archive_dir accumulates logs without bound"
      mitigation: "Copies only; state_dir is still the working location and is still reset normally. Pruning is left to the operator, consistent with the framework's treatment of ai/workspace/."
    - risk: "The .gitignore re-inclusion of ai/logs/ commits run logs that may contain project paths"
      mitigation: "Logs already record absolute paths in state_dir and are reviewed before commit like any other artefact. The archive is opt-in."

technical_details:
  current_behavior: >
    run_loop clears work-summary.txt once, at loop start (~line 1801). The
    exhaustion exit in run_phase synthesises a manifest and then tests
    os.path.exists(work-summary.txt) to choose between rc=0 and rc=1 (~1354).
    Write targets are recorded as `path or file_path or destination` (~1181).
    reset_state returns 1 when state_dir is absent (~507). Run logs are written
    only into state_dir.
  proposed_behavior: >
    work-summary.txt is cleared at the top of each loop cycle, before the work
    phase. run_phase tracks a phase-scoped _manifest_written flag, set when the
    worker writes work-summary.txt via a write tool or via the F13
    final-response path; the exhaustion exit returns 0 when synthesis wrote a
    manifest now or that flag is set, else 1. Write-target recording prefers
    destination for move/rename tools. reset_state returns 0 for an absent
    directory. archive_prior_logs copies *.log and *.LOG from state_dir to
    loop.log_archive_dir before each run, skipping files already present.
  implementation_approach: >
    1. run_loop: add clear_state(state_dir, "work-summary.txt") immediately
    after the iteration.txt write, with a comment recording why the clear sits
    before the work phase and not before the review phase.
    2. run_phase: declare _manifest_written: bool = False alongside
    _written_paths; set it in the F13 final-response branch and in the
    write-target recording block when the target resolves to
    state_dir/work-summary.txt.
    3. run_phase exhaustion exit: capture the return value of
    _synthesize_work_summary and return 0 when it or _manifest_written is true.
    4. Write-target recording: branch on move/rename tool names to prefer
    destination, then new_path, then path, then file_path.
    5. reset_state: return 0 with a "nothing to clear" message when state_dir is
    absent.
    6. New archive_prior_logs(state_dir, archive_dir) -> int near setup_logging;
    call it in main_async before setup_logging, reading loop.log_archive_dir.
    7. config.yaml: add loop.log_archive_dir; correct omlx.reviewer_model to the
    8-bit Magistral and add its model_context_windows entry, retaining the 6-bit
    entry as a valid alternative selection.
    8. .gitignore: re-include ai/logs/ and note the case-insensitive *.log
    collision.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: >
        Per-cycle work-summary.txt clear in run_loop; _manifest_written tracking
        and exhaustion return code in run_phase; destination-preferring
        write-target recording; idempotent reset_state; new archive_prior_logs
        called from main_async.
      functions_affected:
        - "run_loop"
        - "run_phase"
        - "reset_state"
        - "archive_prior_logs (new)"
        - "main_async"
      classes_affected: []
    - component: "AEL configuration"
      file: "ai/ael/config.yaml"
      change_summary: "Added loop.log_archive_dir; reviewer_model corrected to Magistral-Small-2509-MLX-8bit with matching context-window entry."
      functions_affected: []
      classes_affected: []
  data_changes:
    - "work-summary.txt lifetime narrowed from run scope to cycle scope"
    - "New optional output directory ai/logs/ containing copied run logs"
  interface_changes:
    - "New optional config key loop.log_archive_dir; null or absent preserves existing behaviour"
    - "reset_state / --mode reset now exits 0 for an absent state directory (previously 1)"

dependencies:
  internal:
    - component: "_synthesize_work_summary"
      impact: "Return value now consumed at the exhaustion exit; function itself unchanged"
    - component: "_extract_deliverables and the read-evidence, syntax and pytest gates"
      impact: "Unchanged; now receive only the current cycle's manifest"
    - component: "clear_state"
      impact: "Reused as-is"
    - component: "ael-mcp reset_ael"
      impact: "Stops reporting failure for projects with no state directory; no change required in that repository"
  external: []
  required_changes:
    - "change-3b9e6d72 must be in place before this change can be verified end-to-end, as no SHIP is otherwise reachable"

testing_requirements:
  test_approach: >
    Static verification and targeted direct exercise of the new helper.
    End-to-end verification deferred to a live Ralph Loop run of three or more
    cycles, which is blocked on change-3b9e6d72.
  test_cases:
    - scenario: "Cycle 1 produces deliverables; cycle 2 produces none and exhausts its budget"
      expected_result: "Cycle 2 returns rc=1; the gates never see cycle 1's manifest again"
    - scenario: "Worker writes work-summary.txt itself, then exhausts the budget"
      expected_result: "Phase returns 0; the worker's own manifest is preserved verbatim"
    - scenario: "Worker reaches a normal final response"
      expected_result: "F13 path unchanged; _manifest_written set; summary is the worker's final message"
    - scenario: "Deliverable created via move_file"
      expected_result: "Recorded at the destination; survives the isfile filter; appears in the manifest"
    - scenario: "--mode reset against a project with no state directory"
      expected_result: "Exit code 0, 'nothing to clear'"
    - scenario: "log_archive_dir unset"
      expected_result: "No archiving; behaviour identical to before"
    - scenario: "log_archive_dir set, run repeated"
      expected_result: "Prior logs copied once; re-runs copy nothing further; non-log files untouched"
  regression_scope:
    - "F13 final-response summary write unchanged in content"
    - "Wall-clock and work-complete exits unchanged apart from now acting on a cycle-scoped manifest"
    - "BLOCKED path unchanged — no synthesis, rc=1"
    - "Review-phase behaviour unchanged; synthesis remains guarded by is_worker_phase"
    - "Write-target recording unchanged for every tool outside the move/rename set"
  validation_criteria:
    - "ai/ael/src/orchestrator.py has no syntax errors"
    - "ai/ael/config.yaml parses and retains every pre-existing key"
    - "No change to review-phase behaviour"
    - "No change to the BLOCKED path"

implementation:
  effort_estimate: ""
  implementation_steps:
    - step: "Claude Desktop implements directly via file tools (no Claude Code, no AEL) per William Watson's instruction, 2026-07-29"
      owner: "Claude Desktop (Opus 5)"
  rollback_procedure: "git revert the commit; ai/logs/ may be deleted independently as it is additive."
  deployment_notes: >
    Downstream propagation via bin/propagate.sh after change-8c1a4f5e is in
    place. config.yaml is excluded from propagation, so downstream projects
    wanting log archiving must add loop.log_archive_dir to their own config.

verification:
  implemented_date: "2026-07-29"
  implemented_by: "Claude Desktop (Opus 5)"
  verification_date: "2026-07-29"
  verified_by: "Claude Desktop (Opus 5) — static only"
  test_results: >
    orchestrator.py parses. config.yaml parses with reviewer_model
    Magistral-Small-2509-MLX-8bit and log_archive_dir ai/logs.
    archive_prior_logs exercised against a scratch directory: 0 copied when
    unconfigured; 2 copied (.LOG and .log) when configured; 0 on re-run;
    non-log files excluded; 0 and no exception when state_dir is absent.
  issues_found:
    - "End-to-end behaviour unverified. Blocked on change-3b9e6d72; a three-cycle live run is required before closure."

traceability:
  design_updates: []
  related_changes:
    - change_ref: "change-a2f9c4d1"
      relationship: "corrects and completes — this change closes the gate-bypass a2f9c4d1 narrowed, and corrects two claims in that document per remediation §1.5"
    - change_ref: "change-3b9e6d72"
      relationship: "prerequisite for end-to-end verification"
    - change_ref: "change-e4b1a7c3"
      relationship: "related — propagated stale state was one route by which a manifest outlived its cycle"
  related_issues:
    - issue_ref: "issue-f5c28a04"
      relationship: "resolves"
    - issue_ref: "issue-a2f9c4d1"
      relationship: "completes"

notes: >
  Implemented directly by the Strategic Domain at William Watson's instruction,
  as was change-a2f9c4d1. Given that a2f9c4d1 was accepted on inline review and
  left three defects a two-cycle run would have exposed, an independent P08
  audit and a live run are both recommended before closure.

version_history:
  - version: "1.0"
    date: "2026-07-29"
    author: "William Watson"
    changes:
      - "Initial change document — implemented directly from dev/remediation-2026-07-29.md §1.1, §1.2, §1.3, §1.5, §2.3, §3.1, §4.2"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
