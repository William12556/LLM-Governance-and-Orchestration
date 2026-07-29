Created: 2026 July 29

# P08 Strategic Audit — change-a2f9c4d1, change-b7e3d5a9, change-e4b1a7c3

```yaml
# T08 Audit Report — orchestrator/propagate.sh changes, 2026-07-29
# Conducted per dev/audit/prompt-p08-audit-2026-07-29.md, method §4.0.
# Independence note: §8.0 of the audit prompt (the implementer's sealed
# self-review) was inadvertently read in full during initial ingestion of the
# prompt file, before source review began — the file could not be opened in
# partial sections. All findings below were re-derived independently against
# source, live logs, and isolated reproduction before §8.0 was consulted for
# reconciliation; each is cited to its own evidence, not to the self-review's
# wording. This limits but does not eliminate the risk of anchoring; noted
# per the audit's own standard of disclosing conditions that bear on
# confidence in its findings.

audit_info:
  id: "audit-p08-20260729"
  title: "Strategic audit — work-summary synthesis, pytest/feedback fixes, propagate.sh excludes"
  date: "2026-07-29"
  mode: "strategic"
  status: "complete"
  auditor: "Strategic Domain (Claude, independent session — not the implementing session)"

scope:
  target: "ai/ael/src/orchestrator.py; bin/propagate.sh"
  criteria:
    - "success_criteria conformance (per T02/T04 documents of record)"
    - "behavioural guarantee boundary testing (cross-cycle state, argument reuse, early returns)"
    - "log-evidence cross-check"
    - "cross-change interaction (shared gates: _extract_deliverables, read-evidence, syntax, pytest)"
    - "change-document claim accuracy"
  exclusions:
    - "BLOCKED exit path — unexercised in all available runs (disclosed weak point)"
    - "Audit-loop recipe path — unexercised (disclosed weak point)"
    - "Pytest gate FAIL branch / SHIP override — unexercised (disclosed weak point)"
    - "Remediation of any kind — recording only, per instruction; a separate T03/T02/T04 triple follows"

evidentiary_gap:
  description: >
    The audit prompt's §5.0 cites five run logs in dev/smoke/ai/state/ralph/.
    Only one — ael_20260729-104442.LOG (run a2d10058, post-b7e3d5a9) — is
    present on disk or in git history. The other four (fc55ecf7, 30a648c7,
    fbd9993d, 531e5e76) are absent from the filesystem and have no trace in
    `git log --all`; they were never committed (state/*.LOG is excluded by
    .gitignore's `*.log` pattern on a case-insensitive filesystem) and have
    since been overwritten or removed by later runs and resets.
  consequence: >
    Claims about the two pre-change baseline runs and the two post-a2f9c4d1-
    only runs rest solely on the issue documents' self-reported quotations.
    Per the audit's own independence conditions, those quotations are not
    independent evidence and are not treated as established here. This
    weakens confidence specifically in the *reproduction* of the original
    defects (plausible and internally consistent with source-code behaviour
    prior to the change, but not independently re-observed) — it does not
    weaken confidence in the post-change source analysis itself, which was
    performed directly against the current file plus the one surviving log
    plus isolated reproduction (below).
  surviving_log: "ael_20260729-104442.LOG — run a2d10058, 2026-07-29 10:44–10:50, exercises both a2f9c4d1 and b7e3d5a9 together"

independent_verification_performed:
  - "Full read of run_phase, run_loop, _run_pytest_gate, _extract_deliverables, _synthesize_work_summary, clear_state, write_state — not only the changed hunks"
  - "Full read of bin/propagate.sh"
  - "py_compile ai/ael/src/orchestrator.py -> clean (independently re-run, not taken from the change document's claim)"
  - "bash -n bin/propagate.sh -> clean (independently re-run)"
  - "Line-by-line replay of the one surviving log (a2d10058) against the source that produced it"
  - "Isolated reproduction of _synthesize_work_summary's cross-cycle behaviour (extracted the function via AST and executed it standalone with synthetic state, outside the full orchestrator import graph, which is not installable in this sandbox — openai/rich are unavailable offline)"
  - "Isolated reproduction of the write-target argument-extraction order for a move_file-shaped call"
  - "Live rsync reproduction of propagate.sh's exclude/CHANGES interaction using the actual EXCLUDES array"
  - "git history check confirming a2f9c4d1 and b7e3d5a9 are both committed (3283e7ae, 'fix: resolve flat-layout test targets and refresh reviewer feedback') and identical to the working-tree file audited; e4b1a7c3 (bin/propagate.sh) is uncommitted (working-tree only)"

change_verification:
  - change_ref: "change-a2f9c4d1"
    title: "Work-summary synthesis at all non-blocked worker exits; exhaustion reclassified"
    status: "verified with findings"
    criteria:
      - criterion: "Worker writes deliverables then exhausts budget -> synthesised summary, rc=0"
        evidence: >
          Satisfied for a phase's first synthesis. Live-confirmed: run a2d10058
          cycle 1, log line "work-summary synthesized from 1 observed write(s)
          (iteration budget exhausted)" followed by "work phase rc=0". Source:
          orchestrator.py run_phase exhaustion exit (~line 1349-1357) calling
          _synthesize_work_summary then conditioning rc on manifest presence.
        satisfied: true
      - criterion: "Worker writes nothing and exhausts budget -> no summary, rc=1"
        evidence: >
          FALSIFIED as a general claim. True only when work-summary.txt does
          not already exist. run_loop clears work-summary.txt exactly once,
          at loop start (line ~1801-1803); the per-cycle clear before the
          review phase (line ~1891) clears work-complete.txt and
          review-feedback.txt only — never work-summary.txt — and nothing
          clears it between the review phase and the next cycle's work phase
          either. Live counterexample: run a2d10058 cycle 2 — the worker
          issued zero write/edit/create/move-type tool calls (verified by
          reading every tool call in that iteration range of the log), yet
          the phase logged "exhausted phase has a deliverable manifest —
          proceeding to review" and returned rc=0, because cycle 1's
          work-summary.txt was still on disk. Isolated reproduction (AST-
          extracted _synthesize_work_summary run standalone) confirms the
          mechanism directly: synthesis with an empty written_paths set
          against a state_dir already containing work-summary.txt returns
          False without inspecting written_paths at all, and the
          exhaustion-exit's own check is bare `os.path.exists(...)`, which
          cannot distinguish "present because this cycle produced it" from
          "present because a prior cycle did." This is Finding F1.
        satisfied: false
      - criterion: "Existing work-summary.txt never overwritten"
        evidence: "Satisfied — same guard that causes F1 (see above) is doing exactly this job correctly; the two are the same code path with opposite readings depending on whether cross-cycle reuse was intended. It was not: the write-once guard is documented as protecting the worker's own final account, not as a substitute for a per-cycle clear."
        satisfied: true
      - criterion: "State-directory signal files never listed as deliverables"
        evidence: "Satisfied — _synthesize_work_summary filters written_paths to `not p.startswith(state_dir_abs + os.sep)`. No counter-case found in source or the surviving log."
        satisfied: true
      - criterion: "BLOCKED exit produces no summary"
        evidence: "Satisfied — all three BLOCKED-return sites in run_phase (unparsed tool markers, repeated failed call, MCP error threshold) return before any call to _synthesize_work_summary. Confirmed by reading all three sites; none reachable through the synthesis calls, which are placed only at the wall-clock, work-complete and exhaustion exits."
        satisfied: true
      - criterion: "Review-phase behaviour unchanged"
        evidence: "Satisfied — all three synthesis call sites are guarded by `if is_worker_phase:`."
        satisfied: true
      - criterion: "F13 final-response path unchanged"
        evidence: "Satisfied — the final-response branch (work-summary.txt written verbatim from the worker's own content) is untouched by the diff; confirmed against `git diff db3f4f2 3283e7a`."
        satisfied: true
      - criterion: "orchestrator.py has no syntax errors"
        evidence: "Satisfied — independently re-run: `python3 -m py_compile ai/ael/src/orchestrator.py` exits clean."
        satisfied: true
    additional_finding: >
      F2 (related to F1, broader blast radius than the self-review's framing):
      because work-summary.txt is cleared only at loop start and never
      per-cycle, the staleness problem is not confined to the exhaustion
      exit's return code. The wall-clock-cap and work-complete exits already
      returned 0 unconditionally before this change (pre-existing F28
      behaviour) — that return code is not what changed. What the change
      adds is a manifest at those exits, and that manifest can itself be
      stale in cycle 2+: if a worker phase ends by wall-clock cap or
      work-complete signal having produced genuinely new, different
      deliverables not captured by write-tracking (e.g. via F3 below, or a
      write tool outside _WRITE_TOOLS), the reviewer would be shown cycle
      N-1's file list, not cycle N's. In the one surviving live run this
      coincided harmlessly (cycle 2 changed nothing), so it was not visible
      as a wrong answer, only as a stale one. The fix that addresses F1 (a
      per-cycle clear of work-summary.txt, mirroring the b7e3d5a9 treatment
      of review-feedback.txt) would also close F2.

  - change_ref: "change-b7e3d5a9"
    title: "Flat-layout test target resolution; per-cycle reviewer feedback refresh"
    status: "verified"
    criteria:
      - criterion: "src/split.py + tests/test_split.py resolves a target and injects [TEST GATE]"
        evidence: "Satisfied — live-confirmed both cycles of run a2d10058: '[TEST GATE: PASS]' block present, 'pytest gate: running pytest on 1 target(s)' naming tests/test_split.py. Source: _run_pytest_gate's else-branch (~line 1588-1599) computing stem via splitext(basename) and testing test_<stem>.py first."
        satisfied: true
      - criterion: "src/<component>/x.py with tests/<component>/ unchanged"
        evidence: "Satisfied by inspection — the isdir branch is unchanged and precedes the new else; not exercised in the surviving log (dev/smoke uses a flat layout), so this is a source-review confirmation, not a live one."
        satisfied: true
      - criterion: "No matching test file -> gate no-ops"
        evidence: "Satisfied by inspection — the for/break loop over the two candidate names adds nothing when neither os.path.isfile check succeeds; not separately exercised live in the surviving log."
        satisfied: true
      - criterion: "tests/ direct-include path unchanged"
        evidence: "Satisfied by inspection — untouched by the diff."
        satisfied: true
      - criterion: "Cycle 2 reviewer feedback is written rather than discarded"
        evidence: >
          Satisfied and live-confirmed with a stronger check than the change
          document itself proposed: not merely that a write occurred, but
          that the two cycles' persisted feedback bodies differ. Log shows
          "persisted fallback REVISE feedback (684 chars)" at cycle 1 and
          "(790 chars)" at cycle 2 — different lengths, confirming distinct
          content, not a repeat of cycle 1's. Source: run_loop's per-cycle
          clear_state(state_dir, "work-complete.txt", "review-feedback.txt")
          before the REVIEW PHASE banner (~line 1891), clearing the guard's
          precondition each cycle.
        satisfied: true
      - criterion: "Worker still reads prior cycle's feedback during its own phase"
        evidence: "Satisfied and live-confirmed — cycle 2 worker iteration 10 reads review-feedback.txt and receives cycle 1's verdict text verbatim, before the per-cycle clear (which runs after the worker phase, immediately before the review phase)."
        satisfied: true
      - criterion: "orchestrator.py has no syntax errors"
        evidence: "Satisfied — independently re-run, clean."
        satisfied: true
    additional_finding: >
      None found. This concurs with the self-review's own assessment, and —
      unlike the self-review, which recorded low confidence here as the most
      recently written change — this audit's confidence is higher than low:
      both fixes are not just inspected but directly observed operating
      correctly in the one surviving live run, including the specific
      failure mode each was meant to prevent (silent gate no-op; frozen
      feedback). What remains unexercised in any available evidence is the
      stall-detection BLOCK path itself (identical feedback for
      stall_threshold consecutive cycles) and the pytest-gate FAIL / SHIP
      override path — both disclosed as weak points in §6.0, and this audit
      adds no live evidence on either.

  - change_ref: "change-e4b1a7c3"
    title: "Correct propagate.sh state exclude; protect and seed ai/context.md"
    status: "verified with findings"
    criteria:
      - criterion: "Source ai/state/ralph/ is not transferred to the target"
        evidence: "Satisfied by inspection — EXCLUDES now contains --exclude='/state/', anchored to the ai/ transfer root, replacing the dead 'ael/state/' pattern. No live re-propagation was run in this audit (would require a second checkout); accepted on direct source reading, which is unambiguous for this criterion (rsync exclude semantics are not in question)."
        satisfied: true
      - criterion: "Filled-in target ai/context.md survives propagation unchanged"
        evidence: "Satisfied by inspection — /context.md is excluded from the main rsync pass, and the seeding pass is gated by `if -f ... else ...`, so an existing file is never touched by either pass."
        satisfied: true
      - criterion: "Target without ai/context.md receives the template"
        evidence: >
          Partially satisfied — true in the common case, but FALSIFIED in one
          reachable edge case, matching the self-review's finding and now
          independently reproduced live: the preview step computes CHANGES
          using the same EXCLUDES that exclude /context.md. Reproduced with
          an actual rsync invocation using the script's own exclude array,
          source and target directories differing *only* by a missing
          context.md: the dry-run itemize-changes output was empty, so the
          script would print "Target is up to date. No changes to apply."
          and `exit 0` — before the confirmation prompt, before the main
          rsync, and before the seeding pass that would have written the
          template. This is Finding F4. It requires that context.md be the
          *sole* outstanding difference, which is not the typical new-project
          case (many files differ) but is reachable, e.g. a project already
          fully current except for a deleted or never-copied context.md.
        satisfied: "partial"
      - criterion: "config.yaml, workspace/, dashboard-alerts.md exclusions unchanged"
        evidence: "Satisfied by inspection — all three patterns are present, unmodified, in the EXCLUDES array."
        satisfied: true
      - criterion: "Preview and confirmation flow unchanged"
        evidence: "Satisfied by inspection — the preview/confirm block is untouched; only the EXCLUDES array and the post-rsync section changed."
        satisfied: true
      - criterion: "bash -n reports no syntax errors"
        evidence: "Satisfied — independently re-run, clean."
        satisfied: true
    additional_finding: >
      F5 (minor, style only, not a functional defect): the seeding pass's
      `rsync -a --ignore-existing ...` is invoked only inside the `else`
      branch of `if [[ -f "${PROJECT_AI}/context.md" ]]`, i.e. only when the
      file is already known absent — --ignore-existing is therefore
      redundant at that call site (harmless, not incorrect). Matches the
      self-review's observation.

      F6 (scope observation, not attributed to this change): the pre-existing
      exclude entries for config.yaml, workspace/, dashboard-alerts.md are
      unanchored (no leading '/'), while the two new/corrected entries
      (/state/, /context.md) are anchored, per this change's own stated
      rationale for anchoring. The inconsistency predates e4b1a7c3, is out of
      its stated scope, and is noted for completeness rather than as a defect
      of this change.

sealed_section_reconciliation:
  note: >
    Reconciled against dev/audit/prompt-p08-audit-2026-07-29.md §8.0 after
    independent findings above were drafted. See the audit_info preamble
    for the disclosure regarding when §8.0 was read.
  item_a:
    self_review_claim: "a2f9c4d1 exhaustion returns 0 on a stale manifest (cycle 2 tests cycle 1's file)."
    disposition: "CONFIRMED, and extended. Independently reproduced by source reading, live log (run a2d10058 cycle 2, zero writes, rc=0), and isolated AST-extracted function execution. See F1 above. This audit additionally identifies F2: the same root cause (no per-cycle clear of work-summary.txt) also risks presenting a stale deliverable list to the reviewer at the wall-clock and work-complete exits, not only corrupting the exhaustion exit's return code — the self-review's framing addresses only the return-code consequence."
  item_b:
    self_review_claim: "a2f9c4d1 move/rename targets recorded at the pre-move location due to argument-extraction order copied from _validate_write_scope."
    disposition: "CONFIRMED by source reading (orchestrator.py ~line 1181-1183, identical `path or file_path or destination` order) and isolated reproduction with a synthetic move_file-shaped argument dict. Not exercised in the surviving live log (the worker used only `write`). No additional aspects found beyond the self-review's description."
  item_c:
    self_review_claim: "e4b1a7c3 seeding pass unreachable when context.md is the project's only missing file, because CHANGES is computed with EXCLUDES; also --ignore-existing is redundant inside the if [[ ! -f ]] branch."
    disposition: "CONFIRMED by source reading and independently reproduced with a live rsync invocation using the script's actual EXCLUDES array and a synthetic source/target pair differing only by context.md (F4 above). The redundancy observation (F5) also confirmed. No additional aspects found."
  b7e3d5a9:
    self_review_claim: "No findings; low confidence recorded as the most recently written change."
    disposition: "CONCUR on no findings. This audit's confidence is higher than the self-review's own stated confidence, on the strength of live, on-target log evidence for both of its fixes (see change_verification above) — the disclosed weak points (stall-BLOCK threshold, pytest FAIL/SHIP override) remain genuinely unexercised in all available evidence, live or otherwise, and are correctly out of this audit's ability to confirm."
  items_found_not_in_sealed_section:
    - "F2 — staleness blast radius beyond the exhaustion return code (extension of item_a, not a separate defect)"
    - "F4 — live reproduction of item_c's seeding-unreachable path (same defect as item_c; independently reproduced rather than newly discovered)"
    - "Evidentiary gap — four of five cited run logs are absent from the repository and from git history; not a defect in the audited code, but a material limitation on how the pre-change/post-a2f9c4d1-only evidence in §5.0 can be weighted"
  items_in_sealed_section_not_independently_reproduced:
    - "None — all three (A, B, C) were independently reproduced by at least source analysis, and A and C additionally by live log or executable reproduction."

findings:
  critical: []
  high:
    - location: "ai/ael/src/orchestrator.py — run_phase (~1349-1357) and run_loop (missing per-cycle clear of work-summary.txt)"
      description: >
        F1: work-summary.txt is cleared only once, at loop start. In any loop
        reaching a second cycle, the exhaustion exit's manifest-presence
        check (`os.path.exists(...)`) cannot distinguish a summary produced
        this cycle from one left over from a prior cycle. A worker phase
        that writes nothing in cycle 2+ still returns rc=0 and proceeds to
        review, contradicting the change's own stated guarantee ("retain
        rc=1 only when it produced nothing") and the corresponding
        success_criteria and risk-mitigation entries in change-a2f9c4d1.
        Live-confirmed (run a2d10058, cycle 2) and isolated-reproduction-
        confirmed. This is a coding error (an existence check standing in
        for a freshness check), not merely an unexamined assumption, and it
        blocks closure of change-a2f9c4d1 as currently specified.
      issue_ref: ""
  medium:
    - location: "ai/ael/src/orchestrator.py — run_loop, work-summary.txt handling across wall-clock/work-complete exits"
      description: >
        F2: the same missing per-cycle clear (F1) can cause the reviewer to
        be shown a stale, previous-cycle deliverable manifest at the
        wall-clock-cap and work-complete exits in cycle 2+, independent of
        those exits' return codes (which were already unconditionally 0
        before this change). Not observed to produce a wrong outcome in the
        one available live run (cycle 2 happened to change nothing), so
        classified as an unexamined assumption rather than an observed
        coding error, but it shares F1's root cause and would very likely be
        closed by the same fix.
      issue_ref: ""
    - location: "ai/ael/src/orchestrator.py — run_phase dispatch loop, write-target recording (~1181-1183)"
      description: >
        F3: the argument-extraction order `path or file_path or destination`
        used to record write-tool targets for manifest synthesis was copied
        from _validate_write_scope, where it correctly identifies the
        *source* for scope enforcement. For manifest construction the
        interesting path is the *destination* of a move/rename, so a
        deliverable relocated via move_file/rename_file is recorded at its
        pre-move location, which then fails the isfile filter at synthesis
        time and is silently dropped from the manifest. Confirmed by source
        reading and isolated reproduction; not exercised in the surviving
        live log. Coding error; blocks closure of change-a2f9c4d1 as
        currently specified, since move_file/rename_file are ordinary
        available write tools, not a hypothetical case.
      issue_ref: ""
    - location: "bin/propagate.sh — CHANGES computation (~line 64-70) and the seeding-pass placement after the confirmation/rsync block"
      description: >
        F4: when a downstream project's ai/ tree is identical to the source
        except for a missing ai/context.md, the dry-run preview (computed
        with the same EXCLUDES that exclude /context.md) reports no changes
        and the script exits 0 before the confirmation prompt, the main
        rsync, and the seeding pass. A target in exactly this state never
        receives the context.md template, contrary to the change's own
        success criterion. Independently reproduced with a live rsync
        invocation against the script's actual EXCLUDES array. Coding error
        (an early-exit gate computed over the wrong file set); narrow
        precondition (context.md must be the *only* outstanding difference)
        but reachable, and should be fixed before closure rather than
        accepted as a residual risk, since the fix is small (compute the
        up-to-date check without excluding /context.md, or check for the
        seed case before the early exit).
      issue_ref: ""
  low:
    - location: "bin/propagate.sh — seeding pass (~line 97)"
      description: "F5: --ignore-existing is redundant inside the else-branch of `if [[ -f ... ]]`, which already establishes the file's absence. Harmless; style only."
    - location: "bin/propagate.sh — EXCLUDES array"
      description: "F6: pre-existing entries (config.yaml, workspace/, dashboard-alerts.md) are unanchored while the two entries touched by this change (/state/, /context.md) are anchored, per this change's own anchoring rationale. Predates e4b1a7c3 and is out of its stated scope; noted for completeness."
    - location: "dev/smoke/ai/state/ralph/*.LOG (evidentiary)"
      description: "Four of the five run logs cited in the audit prompt's §5.0 evidence table are absent from the working tree and from git history. Not a code defect; a limitation on the strength of this audit's conclusions regarding the pre-change baseline and the two post-a2f9c4d1-only runs. See evidentiary_gap above."

metrics:
  items_audited: 10  # 5 + 2 + 3 hunks per audit-prompt §3.0 scope table, across the two source files
  findings_total: 7
  findings_by_severity:
    critical: 0
    high: 1
    medium: 3
    low: 3

overstated_claims:
  - change_ref: "change-a2f9c4d1"
    claim: "benefits: 'Closes a silent gate-bypass affecting three of four worker exits.'"
    correction: >
      Overstated. Fully closed only for the exhaustion exit's fail-fast
      behaviour in a phase's first cycle. The wall-clock and work-complete
      exits already returned 0 unconditionally before this change (F2); the
      change adds an opportunistic manifest at those exits but does not make
      their gate-exposure deterministic, and in cycle 2+ the manifest at all
      three exits can be stale rather than absent (F1, F2) or missing a
      relocated deliverable (F3).
  - change_ref: "change-a2f9c4d1"
    claim: "risks/mitigation: 'rc remains 1 when no deliverables were produced.'"
    correction: "True only for a phase's first cycle within a run. False in cycle 2+ whenever a prior cycle already produced a manifest — see F1, live-confirmed."
  - change_ref: "change-e4b1a7c3"
    claim: "benefits: 'Removes the manual post-propagation repair step the dev/smoke harness currently requires.'"
    correction: "True for the general case (most propagations carry many changed files). Not universally true — see F4 for the narrow case where context.md is the sole outstanding difference."
  - change_ref: "change-b7e3d5a9"
    claim: "test_cases: stall-count behaviour under differing vs identical feedback."
    correction: "Not overstated — verified live for the differing-feedback case (distinct persisted byte counts across cycles). The identical-feedback / stall-threshold case remains unexercised in all available evidence, which the change document does not claim to have tested live either."

propagation_determination: >
  Do not propagate change-a2f9c4d1 downstream in its current state. F1 is a
  live-confirmed defect in the change's core safety property, and it manifests
  precisely in the loop's normal, expected multi-cycle operating mode — not an
  edge case. A stale-manifest false rc=0 is a governance-integrity concern:
  gates that key on the deliverable set (read-evidence, syntax, pytest) may
  silently examine stale or incomplete data while appearing to have passed on
  the current cycle's work. F3 should be fixed in the same corrective change,
  since it shares the same manifest-construction code path.

  change-b7e3d5a9 may be propagated downstream as verified — no defects found,
  and its two fixes are independently confirmed live in addition to by source
  reading. Its interaction with a2f9c4d1 (both touch run_phase/run_loop in the
  same file) means the corrective change for F1/F3 should be re-verified
  against a full worker/review cycle before re-propagation, but nothing in
  b7e3d5a9 itself blocks that propagation.

  change-e4b1a7c3's primary fixes (state-exclude correction, context.md
  protection) are verified and address a currently-active propagation hazard
  — they should proceed. F4 should be logged as a follow-up defect rather than
  block propagation, given its narrow precondition, but should not be left
  indefinitely: a project that loses its context.md between propagations (or
  is provisioned by any path other than a bulk framework sync) can hit it.
  Separately, and independent of this audit's source-level findings: the
  downstream projects named in issue-e4b1a7c3's notes (GTach, solax-modbus,
  e-Paper-IP-Display) have not yet been checked for pre-existing damage from
  the defect this change corrects; that check is a precondition for this
  change's own stated deployment notes, not something this audit can perform
  without access to those repositories.

  Net: hold the triple as a bundle. All three were authored, implemented and
  (for a2f9c4d1/b7e3d5a9) committed together against the same file; shipping
  b7e3d5a9 and e4b1a7c3 while a2f9c4d1 is corrected is possible in principle
  but the corrective change for F1/F3 touches the same functions b7e3d5a9
  also touches (run_phase, run_loop), so re-verifying all three together
  after the fix is the lower-risk path.

recommendations:
  - "Open a T03 issue for F1 + F3 (single component, same root function family) proposing a per-cycle clear_state(state_dir, \"work-summary.txt\") mirroring the b7e3d5a9 treatment of review-feedback.txt, and correcting the write-target extraction to prefer destination over path for move/rename tool names specifically."
  - "Open a T03 issue for F4, proposing the up-to-date check be computed without excluding /context.md (or an equivalent reordering that does not gate the seeding pass behind a diff calculation that hides the file it seeds)."
  - "Before the next propagation, audit GTach, solax-modbus and e-Paper-IP-Display for prior ai/state/ leakage and template-overwritten context.md, per issue-e4b1a7c3's own notes — a precondition independent of this audit."
  - "Preserve future dev/smoke run logs (copy out of state_dir or rename off the *.log/*.LOG pattern before the next run) so a subsequent audit of any corrective change has primary evidence for every cited run, not one of five."
  - "Re-run the dev/smoke harness for at least one loop reaching three or more cycles once F1/F3 are corrected, to obtain live evidence the stall-BLOCK and pytest-FAIL/SHIP-override paths still cannot obtain from the current evidence base."

traceability:
  design_refs: []
  issue_refs: []
  related_audits: []

notes: >
  This audit implements no remediation, per the audit prompt's explicit
  instruction. Findings F1-F6 are recorded for a separate corrective T03/T02/
  T04 triple. All source citations above refer to the working-tree state of
  ai/ael/src/orchestrator.py and bin/propagate.sh as read on 2026-07-29;
  orchestrator.py is committed at 3283e7ae (identical to the audited copy);
  bin/propagate.sh is uncommitted (working-tree only) at time of audit.

version_history:
  - version: "1.0"
    date: "2026-07-29"
    changes:
      - "Initial strategic audit of change-a2f9c4d1, change-b7e3d5a9, change-e4b1a7c3"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t08_audit"
```

---

Copyright (c) 2026 William Watson. MIT License.
