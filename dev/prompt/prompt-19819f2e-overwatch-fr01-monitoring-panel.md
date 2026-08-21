Created: 2026 August 21

```yaml
prompt_info:
  id: "prompt-19819f2e"
  task_type: "code_generation"
  source_ref: "design-project-overwatch"
  target_profile: "claude_code"
  date: "2026-08-21"
  iteration: 1
  # coupled_docs omitted: source_ref references a design document, not a
  # change document (initial implementation, governance P03 §1.4.1 exception).

context:
  purpose: >
    Deliver Project Overwatch FR-01: port govwatch's three existing panels
    (Workflow State, Compliance Alerts, Document Registry) from a Textual TUI
    to a self-contained, browser-rendered HTML file, reusing govwatch's data
    layer unmodified. This is the first of ten incremental phases
    (design-project-overwatch.md §9.2) and the parity gate that govwatch.py's
    eventual retirement is conditioned on (design §14.0, OQ-09). No other
    phase's functionality (task board, config panel, diff viewer, etc.) is in
    scope for this prompt.
  integration: >
    New file ai/src/overwatch.py, coexisting with the unmodified
    ai/src/govwatch.py in the same directory (design §3.3, §14.0). Both
    propagate together via bin/propagate.sh; no script changes required.
  knowledge_references: []
  constraints:
    - "Do not modify ai/src/govwatch.py in any way"
    - "Copy ProjectPaths, DocumentRecord, AelState, BudgetState, Alert, Snapshot, Scanner, PhaseInference, ComplianceEngine, AlertWriter, and their supporting helpers/constants (parse_filename, _extract_yaml_blocks, _find_block_with_key, _is_placeholder, _extract_hex8, parse_document, validate_project, CLASS_DIRS) from ai/src/govwatch.py into ai/src/overwatch.py verbatim — read govwatch.py in full first"
    - "Do not import or depend on textual or rich anywhere in overwatch.py"
    - "Do not extend Snapshot with tasks/configs/stages fields — those belong to later phases (design §4.0) and are out of scope here"
    - "The only files this program may write are ./overwatch.html and ./dashboard-alerts.md, both at the project root — read-only elsewhere (design NFR-01, §3.1 clarification)"
    - "No new dependency beyond pyyaml, already required by the copied code"

specification:
  description: >
    A new module, ai/src/overwatch.py, that on a timer (same default interval
    and --interval/--project CLI arguments as govwatch.py) scans the project,
    builds a Snapshot using the copied Scanner/PhaseInference/ComplianceEngine,
    writes dashboard-alerts.md via the copied AlertWriter unchanged, and
    additionally renders a single self-contained overwatch.html file to the
    project root containing the same three panels govwatch's TUI shows today.
  requirements:
    functional:
      - "CLI: python ai/src/overwatch.py [--project PATH] [--interval N], identical semantics to govwatch.py"
      - "Startup: call validate_project(); on failure print a clear message and exit non-zero before entering the scan loop, matching govwatch's FR-05-04 behaviour"
      - "Loop: every --interval seconds, run Scanner.scan() to produce a Snapshot, run PhaseInference and ComplianceEngine over it, then call AlertWriter.write() and HtmlRenderer.write()"
      - "HtmlRenderer.render(snapshot) returns a complete HTML document as a string: inline <style>, inline <script>, a <meta http-equiv=\"refresh\" content=\"{interval}\"> in <head>, and a <script type=\"application/json\" id=\"snapshot\"> block containing the JSON-serialised Snapshot"
      - "JSON serialisation must handle dataclasses and pathlib.Path values (Path -> str); write a small helper rather than assuming dataclasses.asdict() handles Path"
      - "Rendered body has three sections in this order: Workflow State (phase string, AEL status + iteration, budget status), Compliance Alerts (each alert's severity, code, message, document — grouped or sorted by severity), Document Registry (documents grouped by UUID, showing class, filename, iteration, coupled/uncoupled status)"
      - "Severity styling: CSS classes .severity-violation (red), .severity-warning (yellow), .severity-ok (green), applied via server-rendered class attributes, not client-side logic"
      - "HtmlRenderer.write(snapshot) renders and overwrites ./overwatch.html at the project root every cycle (not append), consistent with govwatch's dashboard-alerts.md overwrite convention (FR-04-04 precedent)"
      - "No clipboard button, no client-side interactivity beyond the meta-refresh reload — those belong to later phases (FR-09) and are explicitly out of scope"
    technical:
      language: "Python"
      version: "3.11"
      standards:
        - "Comprehensive error handling: a write failure for either output file is caught, logged to stderr, and does not crash the loop (govwatch NFR-04/design §10.0 pattern)"
        - "Professional docstrings on all new classes/functions"
        - "No subprocess spawning in this phase (design §7.8's git subprocess use is a later phase)"

design:
  architecture: >
    Single-file module, internal separation by class (design §3.3). Data flow:
    filesystem -> Scanner -> Snapshot -> {PhaseInference, ComplianceEngine} ->
    {AlertWriter -> dashboard-alerts.md, HtmlRenderer -> overwatch.html}.
    Mirrors govwatch's own architecture (design-govwatch.md §3.0) with the
    Textual App replaced by a plain synchronous loop.
  components:
    - name: "HtmlRenderer"
      type: "class"
      purpose: "Serialise a Snapshot to JSON and render the single-file HTML document"
      interface:
        inputs:
          - name: "snapshot"
            type: "Snapshot"
            description: "Current scan result"
        outputs:
          type: "str"
          description: "Complete HTML document"
        raises: []
      logic:
        - "render(snapshot) -> str: build the JSON payload via a Path-aware encoder, then interpolate it plus the three panel sections into a single HTML template string"
        - "write(snapshot, project_root, interval) -> None: call render(), write result to project_root/overwatch.html, catch and log write failures without raising"
    - name: "main"
      type: "function"
      purpose: "CLI entry point: argument parsing, startup validation, scan loop"
      logic:
        - "argparse: --project (default cwd), --interval (default 5), matching govwatch.py's main()"
        - "Resolve ProjectPaths, call validate_project(); exit non-zero with a clear message on failure"
        - "Loop: Scanner().scan() -> PhaseInference -> ComplianceEngine -> AlertWriter.write() -> HtmlRenderer.write() -> sleep(interval)"
  dependencies:
    internal: []
    external:
      - "pyyaml (already required by the copied govwatch code)"

data_schema:
  entities:
    - name: "Snapshot (unmodified from govwatch.py for this phase)"
      attributes:
        - name: "documents"
          type: "list[DocumentRecord]"
          constraints: "open documents only, excluding closed/ subtrees"
        - name: "ael_state"
          type: "AelState"
          constraints: ""
        - name: "budget"
          type: "BudgetState"
          constraints: ""
        - name: "phase"
          type: "str"
          constraints: "project-wide phase per PhaseInference"
        - name: "alerts"
          type: "list[Alert]"
          constraints: ""
        - name: "scan_time"
          type: "datetime"
          constraints: "must be JSON-serialised as ISO 8601 string"
      validation:
        - "All fields copied verbatim from govwatch.py; no new fields added in this phase"

error_handling:
  strategy: "Per-write try/except; a failure in either output write is logged and does not abort the loop, matching the reused Scanner/ComplianceEngine's existing per-document graceful-degradation pattern"
  exceptions:
    - exception: "OSError (or subclass) during overwatch.html or dashboard-alerts.md write"
      condition: "Filesystem write failure"
      handling: "Log to stderr with the failing path; continue to next scan cycle"
  logging:
    level: "WARNING"
    format: "plain text to stderr, consistent with govwatch's existing conventions"

testing:
  unit_tests:
    - scenario: "HtmlRenderer.render() on a hand-built Snapshot fixture"
      expected: "Returned string contains the meta-refresh tag with the correct interval, one <script type=\"application/json\" id=\"snapshot\"> block, and section markers for Workflow State, Compliance Alerts, and Document Registry"
    - scenario: "JSON block round-trip"
      expected: "json.loads() on the embedded snapshot script's contents succeeds and its 'phase' field matches the fixture Snapshot's phase"
    - scenario: "Severity CSS classes"
      expected: "A fixture Alert with severity 'violation' produces an element with class severity-violation; 'warning' and 'ok' likewise"
    - scenario: "HtmlRenderer.write() failure handling"
      expected: "Given an unwritable project_root (e.g. a read-only directory fixture), write() logs and returns without raising"
  edge_cases:
    - "Empty Snapshot (no documents, no alerts, AEL idle, budget unknown) renders all three sections with an explicit empty state, not a blank/broken section"
  validation:
    - "python -m py_compile ai/src/overwatch.py"
    - "pytest tests/overwatch/ -v"

deliverable:
  format_requirements:
    - "Save generated code directly to the specified paths"
    - "Execute pytest suite for tests/overwatch/ on completion; report pass/fail summary"
    - "Do not modify any file outside the paths listed below"
  files:
    - path: "ai/src/overwatch.py"
      content: "Data layer copied verbatim from govwatch.py per constraints, plus new HtmlRenderer class and new main(), per design above"
    - path: "ai/src/requirements-overwatch.txt"
      content: "pyyaml"
    - path: "tests/overwatch/test_overwatch.py"
      content: "Unit tests per the testing section above, using fixture Snapshot/DocumentRecord/Alert instances constructed directly rather than a real project tree"

success_criteria:
  - "ai/src/govwatch.py is byte-for-byte unchanged"
  - "ai/src/overwatch.py has no import of textual or rich"
  - "python ai/src/overwatch.py --project <fixture> --interval 1, run briefly, produces both overwatch.html and dashboard-alerts.md at the fixture project root"
  - "overwatch.html opens in a browser and displays all three panels without a console error"
  - "All tests/overwatch/ tests pass"
  - "py_compile succeeds on ai/src/overwatch.py"

element_registry:
  source: "dev/design/design-project-overwatch.md#12.0-element-registry"
  entries:
    modules:
      - name: "overwatch"
        path: "ai/src/overwatch.py"
    classes:
      - name: "ProjectPaths"
        module: "overwatch"
      - name: "DocumentRecord"
        module: "overwatch"
      - name: "AelState"
        module: "overwatch"
      - name: "BudgetState"
        module: "overwatch"
      - name: "Alert"
        module: "overwatch"
      - name: "Snapshot"
        module: "overwatch"
      - name: "Scanner"
        module: "overwatch"
      - name: "PhaseInference"
        module: "overwatch"
      - name: "ComplianceEngine"
        module: "overwatch"
      - name: "AlertWriter"
        module: "overwatch"
      - name: "HtmlRenderer"
        module: "overwatch"
    functions:
      - name: "main"
        module: "overwatch"
        signature: "main() -> None"
      - name: "render"
        module: "overwatch"
        signature: "HtmlRenderer.render(snapshot: Snapshot) -> str"
      - name: "write"
        module: "overwatch"
        signature: "HtmlRenderer.write(snapshot: Snapshot, project_root: Path, interval: int) -> None"
    constants: []

tactical_brief: ""
# Omitted: target_profile is claude_code, not ael (T04 schema allOf/if-then;
# tactical_brief is not consumed by claude_code).

notes: >
  Execution: Claude Code (target_profile claude_code), per governance P09
  §1.10.3 Option C. Design-sourced initial implementation under P03 §1.4.1 —
  no issue or change document exists or is required for this phase; the
  corrective T03->T02->T04 loop applies only if execution fails or tests
  fail. Framework-development context: this prompt resides in dev/prompt/
  rather than ai/workspace/prompt/, per the dev/-substitutes-ai/workspace
  convention already in use for requirements-project-overwatch.md and
  design-project-overwatch.md. On completion, close this prompt document
  (move to dev/prompt/closed/) and write a completion report to
  dev/reports/. govwatch.py retirement is NOT triggered by this prompt's
  completion alone — design §14.0/OQ-09 additionally requires a manual
  side-by-side validation session and explicit human sign-off.
```
