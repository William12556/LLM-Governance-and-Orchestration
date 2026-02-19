Created: 2025 February 13

# Filesystem Architecture

## Table of Contents

- [Directory Structure](#directory-structure)
- [File Lifecycle](#file-lifecycle)
- [Version History](#version-history)

---

## Directory Structure
```
project-root/
├── ai/
│   ├── governance.md              # Framework specification
│   ├── templates/                 # T01-T07 YAML templates
│   └── instructions.md            # Domain-specific guidance
├── workspace/
│   ├── requirements/              # T07 Requirements documents
│   ├── design/                    # T01 Design documents (3-tier)
│   ├── change/                    # T02 Change requests
│   ├── issue/                     # T03 Issue tracking
│   ├── prompt/                    # T04 Prompts (loop entry)
│   ├── test/                      # T05 Test specifications
│   ├── result/                    # T06 Results (loop exit)
│   └── trace/                     # Traceability matrices
├── .goose/
│   └── ralph/                     # Loop state (ephemeral)
│       ├── task.md                # Current task
│       ├── iteration.txt          # Cycle counter
│       ├── work-summary.txt       # Worker output
│       ├── work-complete.txt      # Completion signal
│       ├── review-result.txt      # SHIP/REVISE decision
│       ├── review-feedback.txt    # Reviewer notes
│       ├── .ralph-complete        # Success marker
│       └── RALPH-BLOCKED.md       # Failure details
└── src/                           # Generated code
```

[Return to Table of Contents](#table-of-contents)

---

## File Lifecycle

### Governance Artifacts (Permanent)
- Created with UUID identifiers
- Stored in `workspace/` subdirectories
- Immutable once closed
- Cross-linked via traceability

### Loop State (Ephemeral)
- Created per task in `.goose/ralph/`
- Cleared between tasks
- Not version controlled
- Summary persists in T06 Result

[Return to Table of Contents](#table-of-contents)

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2025-02-13 | Initial filesystem architecture documentation |

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
