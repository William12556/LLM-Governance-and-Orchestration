Created: 2026 July 02

```yaml
change_info:
  id: "change-713437bc"
  title: "Conditional target_profile and source-lineage requirements in T04 schema, P09/P03 text, and govwatch compliance checks"
  date: "2026-07-02"
  status: "verified"
  priority: "high"
  iteration: 1
  coupled_docs:
    issue_ref: "issue-713437bc"
    issue_iteration: 1

source:
  type: "issue"
  reference: "issue-713437bc"
  description: >
    Resolve two root-cause contradictions (AEL-exclusivity, change-document
    exclusivity) identified in report-p09-t04-contradictions-2026-07-01.md,
    plus two independently verified unconditional govwatch violations.

scope:
  summary: >
    Two work streams. Stream A (source code): govwatch.py parse_document /
    ComplianceEngine — add source_ref and target_profile extraction,
    condition FR-02-03 and FR-02-10 on the new fields. Stream B
    (documents): ai/templates/T04-prompt.md (schema conditional
    requirements, prompt_info.target_profile field, wording fixes),
    ai/governance.md (P09 §1.10.2, P03 §1.4.1 cross-reference), ai/primer.md
    (§3.0, §7.0 rescoped to AEL-targeted prompts).
  affected_components:
    - name: "govwatch"
      file_path: "ai/src/govwatch.py"
      change_type: "modify"
    - name: "T04 Prompt template and schema"
      file_path: "ai/templates/T04-prompt.md"
      change_type: "modify"
    - name: "P09 Prompt protocol"
      file_path: "ai/governance.md"
      change_type: "modify"
    - name: "Strategic Domain Primer"
      file_path: "ai/primer.md"
      change_type: "modify"
  affected_designs: []
  out_of_scope:
    - "New Tactical Domain profiles beyond ael / claude_code / claude_omlx"
    - "F7 (output_format / deliverable.documentation schema drift) and F8 (stale version labels) — batched only if trivial within Stream B, otherwise deferred"
    - "Retrofitting target_profile / re-deriving lineage on closed or in-flight prompt documents"
    - "T02 / T03 / T05 / T06 coupled_docs pattern — unaffected; only T04 conditioned"

rational:
  problem_statement: >
    T04 schema requires tactical_brief and coupled_docs.change_ref
    unconditionally. Neither requirement holds for manual-profile prompts
    (Claude Code, claude-omlx) or design-sourced initial-implementation
    prompts (P03 §1.4.1). govwatch enforces both unconditionally
    (FR-02-10, FR-02-03), independent of and in addition to the schema.
  proposed_solution: >
    Add prompt_info.target_profile (enum: ael, claude_code, claude_omlx).
    Condition tactical_brief requirement and context-budget directives on
    target_profile == ael. Condition coupled_docs requirement on
    source_ref prefix (^change- vs ^design-), reusing the existing field
    rather than adding a new one. Extend govwatch to read both fields and
    suppress FR-02-10 / FR-02-03 accordingly.
  alternatives_considered:
    - option: "A2 — tactical_brief globally optional, no target_profile field (report's low-cost option)"
      reason_rejected: >
        Does not address govwatch FR-02-10, which is unconditional on
        cls == prompt with no profile signal to condition on. Leaves every
        manual-profile prompt permanently flagged.
    - option: "B2 — add a separate design_ref field alongside change_ref"
      reason_rejected: >
        source_ref already carries a design-<uuid>/change-<uuid>
        discriminator (F4); a second field duplicates information already
        present and creates a second place that can drift.
  benefits:
    - "Removes false compliance violations for manual Tactical Domain profiles"
    - "Removes false compliance violations for design-sourced initial-implementation prompts"
    - "No behavior change for existing AEL / change-sourced prompts"
  risks:
    - risk: "target_profile absent on prompt documents authored before this change"
      mitigation: >
        govwatch treats missing target_profile as ael (current behavior)
        for backward compatibility; schema does not assert a default.
    - risk: "Two independent conditionals in one schema increase authoring surface"
      mitigation: >
        Each conditional is a single if/then block; P09 text states both
        as two short rules, not a matrix.

technical_details:
  current_behavior: >
    T04 schema: tactical_brief required (minLength 1) for every prompt;
    coupled_docs.change_ref required (pattern ^change-[0-9a-f]{8}$) for
    every prompt. govwatch.py: FR-02-10 flags any prompt lacking a valid
    tactical_brief as VIOLATION; FR-02-03 flags any prompt with no
    coupled change sharing filename UUID as VIOLATION. Neither check
    inspects prompt_info for a profile or lineage signal.
  proposed_behavior: >
    T04 schema: tactical_brief required only if prompt_info.target_profile
    == "ael". coupled_docs required only if prompt_info.source_ref matches
    ^change-. govwatch.py: parse_document extracts prompt_info.target_profile
    and prompt_info.source_ref for cls == "prompt"; FR-02-10 suppressed
    when target_profile is present and != "ael"; FR-02-03 suppressed when
    source_ref matches ^design-.
  implementation_approach: >
    Stream A (govwatch.py, Claude Code via T04 prompt): extend
    DocumentRecord with target_profile: Optional[str] and
    is_design_sourced: bool; populate both in parse_document from the
    prompt_info block already being read; add the two conditionals to
    _tier2 (FR-02-10) and _tier1 (FR-02-03) guarding the existing alert
    append calls.
    Stream B (documents, Strategic Domain direct edit — no triple,
    consistent with repo precedent for governance/primer/template edits):
    T04-prompt.md template body adds target_profile: "" under prompt_info
    with an enum comment; schema adds target_profile property and two
    allOf/if/then blocks; source_ref field comment clarified. governance.md
    P09 §1.10.2: tactical_brief and context-budget bullets prefixed "When
    target_profile is ael:"; prompt-creation clause changed to "from
    design documents (initial implementation, §1.4.1) or from change
    documents (corrective/enhancement cycle)". primer.md §3.0/§7.0: "every
    T04 prompt" -> "every AEL-targeted T04 prompt".
  code_changes:
    - component: "govwatch"
      file: "ai/src/govwatch.py"
      change_summary: >
        Add target_profile and is_design_sourced fields to DocumentRecord;
        populate from prompt_info in parse_document; condition FR-02-03
        and FR-02-10 alert emission on the new fields.
      functions_affected:
        - "parse_document"
        - "ComplianceEngine._tier1"
        - "ComplianceEngine._tier2"
      classes_affected:
        - "DocumentRecord"
  interface_changes:
    - interface: "T04 prompt_info schema"
      change_type: "schema"
      details: >
        New optional field target_profile (enum: ael, claude_code,
        claude_omlx). coupled_docs required-ness becomes conditional on
        source_ref prefix instead of unconditional.
      backward_compatible: "yes"

dependencies:
  internal:
    - component: "T02 / T03 / T05 / T06 templates"
      impact: "None — coupled_docs pattern in other document classes unaffected"
  external: []
  required_changes: []

testing_requirements:
  test_approach: >
    Stream A verified against source (govwatch.py) after Claude Code
    implementation, per repo precedent. Stream B verified by direct
    re-read of edited sections.
  test_cases:
    - scenario: "T04 prompt, target_profile: ael, tactical_brief populated"
      expected_result: "Schema valid; govwatch: no FR-02-10 alert"
    - scenario: "T04 prompt, target_profile: claude_code, tactical_brief absent"
      expected_result: "Schema valid; govwatch: no FR-02-10 alert"
    - scenario: "T04 prompt, target_profile absent, tactical_brief absent"
      expected_result: "govwatch treats as ael (default) -> FR-02-10 alert (unchanged current behavior)"
    - scenario: "T04 prompt, source_ref: design-<uuid>, coupled_docs absent"
      expected_result: "Schema valid; govwatch: no FR-02-03 alert"
    - scenario: "T04 prompt, source_ref: change-<uuid>, coupled_docs absent"
      expected_result: "Schema invalid; govwatch: FR-02-03 alert (unchanged current behavior)"
  regression_scope:
    - "Existing AEL / change-sourced T04 prompts (dev/prompt/*.md) parse identically"
  validation_criteria:
    - "ai/src/govwatch.py has no syntax errors after edit"
    - "T04 schema remains valid YAML / JSON Schema"

implementation:
  implementation_steps:
    - step: "Stream B: Strategic Domain edits T04-prompt.md, governance.md, primer.md directly"
      owner: "Claude Desktop"
    - step: "Stream A: Strategic Domain authors T04 prompt for the govwatch.py fix; Tactical Domain (Claude Code) implements"
      owner: "Claude Code"
  rollback_procedure: "Revert affected files via git"

traceability:
  related_issues:
    - issue_ref: "issue-713437bc"
      relationship: "resolves"

notes: >
  Stream split follows repo precedent (change-7c1d9a4e: governance/primer/
  template document edits handled directly, no triple; source code changes
  via T04 + Tactical Domain). Correction to prior-turn assessment:
  T04-prompt.md, governance.md, and primer.md do not require the full
  T03/T02/T04 workflow under this repo's established practice or under
  the standing instruction limiting full protocol to source-code changes;
  only govwatch.py (Stream A) does. Issue-713437bc already bundles both
  streams; this change document formalizes the split without a separate
  issue.

verification:
  implemented_date: "2026-07-02"
  implemented_by: "Claude Code (Stream A); Claude Desktop (Stream B)"
  verification_date: "2026-07-08"
  test_results: >
    Verified against source: govwatch.py DocumentRecord/parse_document/
    _tier1/_tier2 changes present and correct; T04-prompt.md v1.10 and
    governance.md v9.10 wording changes present and correct.

version_history:
  - version: "1.0"
    date: "2026-07-02"
    changes:
      - "Initial change document; two-stream resolution (govwatch.py via T04/Tactical Domain, documents via direct Strategic Domain edit)"
  - version: "1.1"
    date: "2026-07-08"
    changes:
      - "Implemented and verified against source; change closed"

metadata:
  copyright: "Copyright (c) 2026 William Watson. MIT License."
  template_version: "1.0"
  schema_type: "t02_change"
```
