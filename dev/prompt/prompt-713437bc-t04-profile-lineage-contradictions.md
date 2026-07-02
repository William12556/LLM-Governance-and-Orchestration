Created: 2026 July 02

```yaml
prompt_info:
  id: "prompt-713437bc"
  task_type: "code_generation"
  source_ref: "change-713437bc"
  target_profile: "claude_code"
  date: "2026-07-02"
  iteration: 1
  coupled_docs:
    change_ref: "change-713437bc"
    change_iteration: 1

context:
  purpose: >
    Suppress two govwatch compliance checks (FR-02-03, FR-02-10) for prompt
    documents where the unconditional assumption they encode does not apply:
    design-sourced prompts (no change document exists to couple to) and
    non-ael Tactical Domain profiles (tactical_brief has no consumer).
  integration: >
    ai/src/govwatch.py — DocumentRecord dataclass, parse_document,
    ComplianceEngine._tier1, ComplianceEngine._tier2.
  constraints:
    - "Implementation target: Claude Code (framework source), not the AEL."
    - "No new external dependencies."
    - "Read the file before editing; verify exact current line context matches before replacing."
    - "No change to CLASS_DIRS, filename regex, or any other check (FR-02-01, 02, 04-09)."

specification:
  description: >
    Two new DocumentRecord fields (target_profile, is_design_sourced),
    populated in parse_document from prompt_info already being read, then
    referenced as guards in the existing FR-02-03 and FR-02-10 alert
    conditions. No new alert codes; existing codes gain a bypass condition.
  requirements:
    functional:
      - "DocumentRecord gains target_profile: Optional[str] = None and is_design_sourced: bool = False"
      - "parse_document populates target_profile from prompt_info.target_profile when cls == 'prompt' and the value is a non-empty, non-placeholder string"
      - "parse_document sets is_design_sourced = True when prompt_info.source_ref is a string starting with 'design-'"
      - "FR-02-03 (_tier1) does not fire when doc.is_design_sourced is True"
      - "FR-02-10 (_tier2) does not fire when doc.target_profile is a non-None value other than 'ael'"
      - "FR-02-10 continues to fire when target_profile is None (absent) or 'ael' — backward-compatible default"
    technical:
      language: "Python"
      version: "3.9+"
      standards:
        - "Follow existing _is_placeholder-style guarding for target_profile (empty string or '#'-prefixed treated as absent)"
        - "No behavior change to any other Alert code"

design:
  architecture: "Two new dataclass fields populated in the existing prompt_info parse block; two existing alert conditions gain an additional boolean guard"
  components:
    - name: "DocumentRecord"
      type: "class"
      purpose: "Add target_profile and is_design_sourced fields"
    - name: "parse_document"
      type: "function"
      purpose: "Populate the two new fields from prompt_info for cls == 'prompt'"
    - name: "ComplianceEngine._tier1"
      type: "function"
      purpose: "Guard FR-02-03 on is_design_sourced"
    - name: "ComplianceEngine._tier2"
      type: "function"
      purpose: "Guard FR-02-10 on target_profile"
  dependencies:
    internal:
      - "Optional (already imported from typing)"
    external: []

deliverable:
  format_requirements:
    - "Edit ai/src/govwatch.py in place"
  files:
    - path: "ai/src/govwatch.py"
      content: "See Implementation Steps below"

success_criteria:
  - "Prompt with source_ref: design-<uuid> and no coupled change -> no FR-02-03 alert"
  - "Prompt with source_ref: change-<uuid> and no coupled change -> FR-02-03 alert (unchanged)"
  - "Prompt with target_profile: claude_code or claude_omlx and no tactical_brief -> no FR-02-10 alert"
  - "Prompt with target_profile: ael (or absent) and no tactical_brief -> FR-02-10 alert (unchanged)"
  - "ai/src/govwatch.py has no syntax errors"
```

---

## Implementation Steps

### Step 1 — Add two fields to `DocumentRecord`

Locate:

```python
    has_tactical_brief: bool = False
    """True if a yaml block contains a valid non-placeholder tactical_brief."""
    required_fields_present: bool = True
    """False if any required field is absent, empty, or a placeholder."""
    missing_fields: list[str] = field(default_factory=list)
    """Names of required fields that are absent or placeholder."""
```

Replace with:

```python
    has_tactical_brief: bool = False
    """True if a yaml block contains a valid non-placeholder tactical_brief."""
    required_fields_present: bool = True
    """False if any required field is absent, empty, or a placeholder."""
    missing_fields: list[str] = field(default_factory=list)
    """Names of required fields that are absent or placeholder."""
    target_profile: Optional[str] = None
    """prompt_info.target_profile value (ael, claude_code, claude_omlx), or None if absent."""
    is_design_sourced: bool = False
    """True if prompt_info.source_ref matches the design-<uuid> pattern."""
```

### Step 2 — Populate the two fields in `parse_document`

Locate (inside the `if info_block and root_key:` / `if isinstance(info, dict):` block, immediately after the "Coupled reference" sub-block and before "Required-field validation"):

```python
                # Required-field validation
                if cls == "change":
```

Insert immediately before it (same indentation level as `# Coupled reference` / `# Required-field validation`):

```python
                # Prompt profile and lineage (cls == "prompt" only)
                if cls == "prompt":
                    tp = info.get("target_profile")
                    if isinstance(tp, str) and tp and not tp.startswith("#"):
                        record.target_profile = tp
                    src_ref = info.get("source_ref")
                    if isinstance(src_ref, str) and src_ref.startswith("design-"):
                        record.is_design_sourced = True

                # Required-field validation
                if cls == "change":
```

### Step 3 — Guard FR-02-03 in `_tier1`

Locate:

```python
            # FR-02-03: prompt with no coupled change sharing UUID → VIOLATION
            for doc in grp_docs:
                if doc.cls == "prompt" and "change" not in grp_cls:
                    alerts.append(Alert(
                        severity="violation",
                        code="FR-02-03",
                        message="Prompt document has no coupled change with matching UUID",
                        document=os.path.basename(doc.path),
                    ))
```

Replace with:

```python
            # FR-02-03: prompt with no coupled change sharing UUID → VIOLATION
            # (skipped for design-sourced prompts — §1.4.1 exception, no change document exists)
            for doc in grp_docs:
                if doc.cls == "prompt" and "change" not in grp_cls and not doc.is_design_sourced:
                    alerts.append(Alert(
                        severity="violation",
                        code="FR-02-03",
                        message="Prompt document has no coupled change with matching UUID",
                        document=os.path.basename(doc.path),
                    ))
```

### Step 4 — Guard FR-02-10 in `_tier2`

Locate:

```python
            # FR-02-10: prompt missing valid tactical_brief → VIOLATION
            if doc.cls == "prompt" and not doc.has_tactical_brief:
                alerts.append(Alert(
                    severity="violation",
                    code="FR-02-10",
                    message=(
                        "Prompt missing valid tactical_brief "
                        "(absent, empty, or placeholder)"
                    ),
                    document=os.path.basename(doc.path),
                ))
```

Replace with:

```python
            # FR-02-10: prompt missing valid tactical_brief → VIOLATION
            # (only when target_profile is ael, or absent — default assumes ael
            # for prompts predating the target_profile field, §1.10.2)
            if (
                doc.cls == "prompt"
                and not doc.has_tactical_brief
                and doc.target_profile in (None, "ael")
            ):
                alerts.append(Alert(
                    severity="violation",
                    code="FR-02-10",
                    message=(
                        "Prompt missing valid tactical_brief "
                        "(absent, empty, or placeholder)"
                    ),
                    document=os.path.basename(doc.path),
                ))
```

### Step 5 — Verify

Confirm `Optional` is already imported (it is — `from typing import Optional`, top of file). Confirm no syntax errors after edit (e.g. `python3 -m py_compile ai/src/govwatch.py`).

Note: `target_profile: "claude_code"` above — per the revised T04 schema (this change), `tactical_brief` is not required for this profile and is intentionally omitted from this prompt.
