Created: 2026 February 18

# Claude References Inventory — governance.md

## Table of Contents

1. [Purpose](<#1-purpose>)
2. [Classification Key](<#2-classification-key>)
3. [Reference Inventory](<#3-reference-inventory>)
4. [Summary](<#4-summary>)
5. [Version History](<#5-version-history>)

---

## 1. Purpose

This document inventories all references to Claude-specific tooling in `ai/governance.md`. Each reference is classified to support reconciliation under Option B (Implementation Profile Pattern), distinguishing content that belongs in the governance abstraction layer from content that belongs in implementation profiles.

[Return to Table of Contents](<#table-of-contents>)

---

## 2. Classification Key

| Class | Label | Meaning |
|---|---|---|
| A | **ABSTRACT** | Protocol-level. Model-agnostic. Retain in governance.md |
| P-C | **PROFILE-CLAUDE** | Claude Code / Claude Desktop specific. Move to profile-claude.md |
| P-B | **PROFILE-BOTH** | Applies to both profiles but requires profile-specific mapping |
| R | **RENAME** | Concept is valid; name is Claude-specific. Rename to generic equivalent |

---

## 3. Reference Inventory

### §1.1.4 Architecture — Line 53

```
Implementation options: Claude Desktop, local LLM via Goose, API-based LLM
```
**Class: P-C / A** — "Claude Desktop" is a profile-specific example. The *options list* pattern is abstract. Retain the options list in governance.md but remove "Claude Desktop" as a named example; delegate named implementations to profiles.

---

### §1.1.4 Architecture — Lines 55, 58 (duplicate)

```
Implementation options: Ralph Loop (Goose), Tactical Domain, custom agents
```
**Class: A** — Ralph Loop and Goose are the shared loop mechanism for both profiles. "Ralph Loop (Goose)" is an abstract reference acceptable at the governance layer. The duplicate line is a defect to be removed.

---

### §1.1.11 Ralph Loop Integration — Lines 117–131

```
§1.1.11 Ralph Loop Integration
Ralph Loop provides autonomous iterative code generation within governance boundaries
Loop State Directory: `.goose/ralph/` (ephemeral, per-task)
Loop Entry / Loop Execution / Loop Exit
State Files: task.md, iteration.txt, work-summary.txt, work-complete.txt,
             review-result.txt, review-feedback.txt, .ralph-complete, RALPH-BLOCKED.md
Boundary Conditions: MAX_ITERATIONS, TOKEN_BUDGET, TIME_LIMIT, DIVERGENCE
Traceability: Loop summary captured in T06 Result document
```
**Class: A** — The entire AEL (Autonomous Execution Loop) protocol — state file contract, boundary conditions, entry/exit criteria, traceability — is model-agnostic. Goose and Ralph Loop are the shared mechanism. Retain in governance.md. The section heading "Ralph Loop Integration" may be renamed "Autonomous Execution Loop (AEL)" with a note that the reference implementation is Ralph Loop via Goose. See Summary.

---

### §1.1.19 Skills Management — Lines 226, 232

```
Tactical Domain: Utilizes skills from .claude/skills/ for reusable workflows
Personal skills: ~/.claude/skills/ for individual workflow preferences
```
**Class: P-C** — `.claude/skills/` is a Claude Code filesystem convention. The *concept* of reusable skills is abstract; the path is Claude-specific. governance.md should reference a generic skill directory path; profiles map it to `.claude/skills/` (Claude) or equivalent (OLLama).

---

### §1.1.19 Skills Management — Lines 226–235 (hook configuration references)

```
governance/validate-design.md, testing/generate-pytest.md,
validation/coupling-check.md, audit/protocol-compliance.md
```
**Class: A** — Skill filenames and categories are model-agnostic. Retain.

---

### §1.1.20 Context Optimization — Lines 239–253

```
CLAUDE.md location: Project root
CLAUDE.local.md: Personal preferences
Content specification [full list]
Update frequency: Modify via # key during Tactical Domain sessions
Team coordination: Review CLAUDE.md changes during git commits
Auto-generation: Strategic Domain creates initial CLAUDE.md
```
**Class: P-C** — `CLAUDE.md` and `CLAUDE.local.md` are Claude Code conventions. The *concept* — a project context file consumed by the Tactical Domain — is abstract. governance.md should reference a generic "Tactical Domain context file"; profiles map it to `CLAUDE.md` (Claude) or equivalent (OLLama). The `# key` update mechanism is Claude Code-specific.

---

### P01 §1.2.2 .gitignore — Lines 301–302

```
CLAUDE.local.md
.claude/settings.json
```
**Class: P-C** — These are Claude Code artefacts. A profile-agnostic .gitignore should use a generic comment; profiles supply the specific filenames.

---

### P01 §1.2.6 Project Folder Structure — Lines 325, 332

```
.claude/                  # Tactical Domain configuration
CLAUDE.md                 # Tactical Domain context (team shared)
```
**Class: P-C** — `.claude/` directory and `CLAUDE.md` are Claude Code conventions. governance.md folder structure should reference generic equivalents; profiles supply actual names.

---

### P06 §1.7.15 Validation Hooks — Line 711

```
Hook configuration: Defined in .claude/skills/validation/
```
**Class: P-C** — Path is Claude Code-specific. Concept (hook configuration location) is abstract.

---

### P07 §1.8.7 Hook-Based Auditing — Line 769

```
Hook configuration: Defined in .claude/skills/audit/
```
**Class: P-C** — Same as above.

---

### P09 §1.10.3 Human Handoff — Lines 870–872

```
Strategic Domain: Verifies CLAUDE.md exists at project root before providing command
Strategic Domain: If CLAUDE.md absent, generates initial CLAUDE.md with project context
Strategic Domain: Generated CLAUDE.md requires human approval before proceeding
```
**Class: P-C** — `CLAUDE.md` is Claude Code-specific. The *concept* — verify and generate a Tactical Domain context file before handoff — is abstract. governance.md should reference "Tactical Domain context file"; profiles supply the filename.

---

### Version History — Lines 1081, 1085

```
| 6.0 | Added Tactical Domain 2.1.0 integration Phase 1: ... .claude/ directory structure, CLAUDE.md requirement ...
| 6.4 | ... Ralph Loop Integration ...
```
**Class: A** — Version history is a record. No action required.

---

[Return to Table of Contents](<#table-of-contents>)

---

## 4. Summary

### Retain in governance.md (Class A)

| Reference | Action |
|---|---|
| Ralph Loop (Goose) in §1.1.4 Tactical Domain options | Retain — shared mechanism |
| §1.1.11 Ralph Loop Integration (full section) | Retain; optionally rename heading to "Autonomous Execution Loop (AEL)" |
| AEL state file contract (.goose/ralph/ schema) | Retain — shared protocol |
| AEL boundary conditions | Retain |
| Skill filenames and categories | Retain |
| Version history entries | Retain |

### Move / Rename for profiles (Class P-C)

| Reference | Section | Action |
|---|---|---|
| `Claude Desktop` as named example | §1.1.4 | Remove from governance.md; add to profile-claude.md |
| `.claude/skills/` path | §1.1.19 | Replace with generic `<skills_dir>/`; profiles map to actual path |
| `CLAUDE.md` / `CLAUDE.local.md` | §1.1.20, P09 §1.10.3 | Replace with "Tactical Domain context file"; profiles name the file |
| `# key` update mechanism | §1.1.20 | Remove from governance.md; add to profile-claude.md |
| `CLAUDE.local.md` in .gitignore | P01 §1.2.2 | Replace with generic comment; profiles supply filenames |
| `.claude/settings.json` in .gitignore | P01 §1.2.2 | Same as above |
| `.claude/` in folder structure | P01 §1.2.6 | Replace with `<tactical_config>/`; profiles name the directory |
| `CLAUDE.md` in folder structure | P01 §1.2.6 | Replace with generic label; profiles name the file |
| `.claude/skills/validation/` hook path | P06 §1.7.15 | Replace with `<skills_dir>/validation/` |
| `.claude/skills/audit/` hook path | P07 §1.8.7 | Replace with `<skills_dir>/audit/` |

### Defects identified

| Location | Issue |
|---|---|
| §1.1.4 Lines 55 and 58 | Duplicate "Implementation options" line for Tactical Domain |

[Return to Table of Contents](<#table-of-contents>)

---

## 5. Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2026-02-18 | Initial inventory of Claude references in governance.md with classification for Option B profile reconciliation |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
