Created: 2026 July 29

```yaml
prompt_info:
  id: "prompt-3b9e6d72"
  task_type: "debug"
  source_ref: "change-3b9e6d72"
  target_profile: "claude-desktop-direct"
  date: "2026-07-29"
  iteration: 1
  coupled_docs:
    change_ref: "change-3b9e6d72"
    change_iteration: 1

context:
  purpose: >
    Make a reviewer verdict readable wherever the model places it, so a SHIP is
    reachable and the Ralph Loop can terminate on success.
  integration: >
    ai/ael/src/orchestrator.py — _normalize_verdict and the fallback REVISE
    feedback persistence inside run_loop.
  constraints:
    - "REVISE must remain the default for empty, whitespace-only and verdict-free input"
    - "No input that previously returned SHIP may now return REVISE"
    - "Do not change the review-result.txt precedence path"
    - "Do not change any SHIP gate"
    - "A verdict word inside a sentence must not be treated as a declaration"
    - "Verify with python -m py_compile after edit"

specification:
  description: >
    Rewrite verdict parsing as two ordered passes and correct the feedback
    extraction that shares its leading-token assumption.
  requirements:
    functional:
      - "Add _is_verdict_line(line) returning SHIP or REVISE when the line reduces to exactly that token under non-alphabetic stripping, else None"
      - "Pass 1 of _normalize_verdict scans lines for isolated verdict declarations and returns the last one found"
      - "Pass 2 retains the existing leading-token rule and is reached only when pass 1 finds nothing"
      - "Add _strip_verdict(text) removing isolated verdict lines, falling back to dropping the leading token when none is present"
      - "run_loop's fallback REVISE persistence uses _strip_verdict instead of an inline split"
    technical:
      language: "python"
      version: "3.11"
      standards:
        - "PEP 8; type hints on both new functions"
        - "Docstrings matching the existing module convention"
        - "Document why pass 1 exists and why REVISE remains the default"

design:
  architecture: >
    Discrimination moves from position to isolation. A line containing nothing
    but a verdict token is a declaration; a verdict word within prose is not.
    The last declaration wins, matching the conclusion-at-the-end form. The
    prior positional rule survives as a fallback so the single-line form is
    unaffected.
  components:
    - name: "_is_verdict_line"
      type: "function"
      purpose: "Decide whether one line is a bare verdict declaration"
      logic:
        - "Strip every non-alphabetic character; uppercase"
        - "Return the token when it is exactly SHIP or REVISE, else None"
    - name: "_normalize_verdict"
      type: "function"
      purpose: "Resolve a reviewer message to SHIP or REVISE"
      logic:
        - "Pass 1: iterate lines, retain the last _is_verdict_line match, return it if any"
        - "Pass 2: leading token of the message, stripped and uppercased, SHIP on exact match"
        - "Default REVISE"
    - name: "_strip_verdict"
      type: "function"
      purpose: "Produce a feedback body with the verdict declaration removed"
      logic:
        - "Drop every isolated verdict line when at least one is present"
        - "Otherwise drop the leading whitespace-delimited token"
  dependencies:
    internal:
      - "run_loop verdict resolution — consumer, otherwise unchanged"
    external:
      - "re (already imported)"

deliverable:
  format_requirements:
    - "Edit ai/ael/src/orchestrator.py in place"
    - "Run python -m py_compile on the edited file"
  files:
    - path: "ai/ael/src/orchestrator.py"
      content: "_is_verdict_line and _strip_verdict added; _normalize_verdict rewritten; fallback feedback extraction switched"

success_criteria:
  - "ai/ael/src/orchestrator.py compiles with no syntax errors"
  - "Multi-line reasoning ending in a bare SHIP resolves to SHIP"
  - "'SHIP: the code looks good' still resolves to SHIP"
  - "'I considered whether to SHIP this but the tests fail.' resolves to REVISE"
  - "A message stating REVISE early and SHIP as its final isolated line resolves to SHIP"
  - "Empty, whitespace-only and verdict-free input resolve to REVISE"
  - "A trailing-verdict REVISE yields a feedback body with the verdict line removed and the prose intact"

tactical_brief: |
  File: ai/ael/src/orchestrator.py. Read _normalize_verdict and run_loop's fallback REVISE persistence before editing.
  Defect: _normalize_verdict reads only the leading whitespace-delimited token. A reviewer that reasons before concluding — the ordinary form — has its verdict read as the first word of its prose, so it always returns REVISE and no SHIP is reachable. Observed in both cycles of run a2d10058: 'The worker has implemented the ...' -> 'REVISE' while the message concluded SHIP.
  Fix: add _is_verdict_line(line), returning SHIP or REVISE when the line reduces to exactly that token under non-alphabetic stripping. Rewrite _normalize_verdict as pass 1, last isolated verdict line wins; pass 2, the existing leading-token rule; default REVISE. Add _strip_verdict(text) which drops isolated verdict lines when present and otherwise drops the leading token, and use it for the fallback feedback body.
  Constraints: REVISE stays the default for unparseable input; a verdict word inside a sentence must not count; do not touch the review-result.txt path or any SHIP gate. Verify with py_compile.

notes: >
  Execution: Claude Desktop (Opus 5), direct implementation via file tools at
  William Watson's instruction — no Claude Code and no AEL. This prompt records
  the specification implemented rather than dispatching it to a Tactical Domain
  executor. Option 2 of the three in dev/remediation-2026-07-29.md §2.1,
  selected by William Watson; option 3, grammar-constrained decoding, is
  recorded as deferred in change-3b9e6d72.
```
