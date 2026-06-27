Created: 2026 June 26

```yaml
change_info:
  id: "change-b9d2f4a7"
  title: "Orchestrator-run syntax gate, corrected budget estimate, interpreter/tool portability"
  date: "2026-06-26"
  author: "William Watson"
  status: "verified"
  priority: "medium"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-b9d2f4a7"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-b9d2f4a7"
  description: >
    Remediate proposal-f9a2c41b findings F6, F8, F9: the reviewer syntax gate is
    unexecutable, the token budget is undercounted, and interpreter/tool
    invocations assume an environment.

scope:
  summary: >
    Move the syntax gate into the orchestrator, include tool schema and system
    prompt in the budget estimate, and use sys.executable with guarded external
    tools.
  affected_components:
    - name: "orchestrator (estimate_tokens, main_async, py_compile call, run_preflight_check)"
      file_path: "ai/ael/src/orchestrator.py"
      change_type: "modify"
    - name: "ralph-review recipe"
      file_path: "ai/ael/recipes/ralph-review.yaml"
      change_type: "modify"
  out_of_scope:
    - "Context-window resolution (change-f1c8a3e6, F18)"

rational:
  problem_statement: >
    F6: ralph-review.yaml instructs the reviewer to run py_compile, but the
    reviewer has no shell, so the gate is skipped or fabricated. F8:
    estimate_tokens omits the tool schema and zeroes the system prompt, so the
    abort threshold can be passed without warning. F9: py_compile runs via PATH
    'python' not sys.executable, and grep is assumed present.
  proposed_solution: >
    F6: the orchestrator runs py_compile on modified .py files at review time and
    injects the result; remove the reviewer-run instruction from
    ralph-review.yaml. F8: include serialized tool-schema length and the rendered
    system prompt in estimate_tokens. F9: use sys.executable; guard external tools.
  benefits:
    - "Syntax gate is actually executed and trustworthy"
    - "Budget estimate reflects real request size; warnings fire in time"
    - "Checks work under venv/PATH variance and absent grep"
  risks:
    - risk: "Orchestrator-run py_compile changes review timing/flow"
      mitigation: "Run on modified .py files only; inject result into reviewer context"
    - risk: "Including tool schema changes existing budget headroom assumptions"
      mitigation: "Re-baseline warn/abort percentages against the corrected estimate"

technical_details:
  current_behavior: >
    The reviewer is told to run py_compile but cannot (F6). estimate_tokens sums
    message content only and main_async zeroes the system prompt (F8). py_compile
    runs as ['python','-m',...] on PATH; grep assumed present (F9).
  proposed_behavior: >
    The orchestrator compiles modified .py files and injects the result; the
    recipe no longer instructs the reviewer to compile. estimate_tokens includes
    the tool schema and rendered system prompt. py_compile uses sys.executable;
    external tools are guarded.
  implementation_approach: >
    Add an orchestrator-side py_compile step over modified .py files with result
    injection (F6); extend estimate_tokens and the initial main_async estimate
    (F8); switch to sys.executable and guard grep (F9). Detection of "modified
    .py files" and injection format decided in implementation.
  code_changes:
    - component: "orchestrator"
      file: "ai/ael/src/orchestrator.py"
      change_summary: "F6 orchestrator-run syntax gate with result injection; F8 tool-schema + system-prompt token accounting; F9 sys.executable and guarded grep"
      functions_affected:
        - "estimate_tokens"
        - "main_async"
        - "run_phase"
        - "run_preflight_check"
    - component: "ralph-review recipe"
      file: "ai/ael/recipes/ralph-review.yaml"
      change_summary: "F6 — remove the reviewer-run py_compile instruction; rely on injected result"

testing_requirements:
  test_cases:
    - scenario: "Modified .py with a syntax error"
      expected_result: "Orchestrator detects it and the result is available to the reviewer"
    - scenario: "Budget estimate with 18 tool schemas"
      expected_result: "Estimate includes schema and system prompt; warn/abort thresholds fire correctly"
    - scenario: "venv where PATH python differs from the running interpreter"
      expected_result: "py_compile uses sys.executable; no misbehaviour"
    - scenario: "grep absent"
      expected_result: "Guarded; no unhandled error"
  validation_criteria:
    - "Reviewer no longer instructed to run a shell command"
    - "Corrected estimate does not regress normal runs into false aborts"

implementation:
  implementation_steps:
    - step: "Claude Code implements per T04 prompt-b9d2f4a7; human reviews"
      owner: "Claude Code"
  rollback_procedure: "git revert orchestrator.py and ralph-review.yaml to prior version"

notes: >
  Execution path: Claude Code. Groups F6 (medium), F8 (medium), F9 (medium). All
  source changes. Re-baselining of budget warn/abort percentages may follow the
  corrected estimate.

version_history:
  - version: "1.0"
    date: "2026-06-26"
    changes:
      - "Initial change document"
  - version: "1.1"
    date: "2026-06-26"
    changes:
      - "Implemented and verified against source; change closed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
