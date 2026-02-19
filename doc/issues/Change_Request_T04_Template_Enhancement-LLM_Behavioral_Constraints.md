# Change Request: T04 Template Enhancement - LLM Behavioral Constraints

## Request Overview

**Objective**: Extend T04 Prompt Template to include standardized LLM behavioral constraints, enabling consistent agent behavior across autonomous governance workflows while maintaining model-agnostic design principles.

**Context**: Ralph Loop autonomous systems require behavioral consistency without relying on model-specific memory features. Current T04 template lacks explicit behavioral instruction injection point, forcing behavior specification into ad-hoc system prompts or external configuration.

**Scope**: Template modification only - no code changes required.

---

## Background

### Current State

T04 template contains:
- `mcp_config.system_prompt` (optional field for model-specific configuration)
- No dedicated behavioral constraints section
- No separation between technical requirements and communication preferences

### Problem Statement

Autonomous agents require:
1. **Behavioral Consistency**: Deterministic communication patterns across iterations
2. **Project Neutrality**: Preferences applicable to any technical domain
3. **Governance Alignment**: File-based state vs. model-specific memory systems

Without explicit behavioral constraints in T04, each autonomous loop iteration may exhibit:
- Communication style drift
- Inconsistent decision-making patterns
- Tool usage variability

---

## Proposed Solution

### Add New Top-Level Section: `behavioral_constraints`

Insert after `mcp_config` section, before `context`:
```yaml
behavioral_constraints:
  communication:
    style: ""  # laconic, verbose, technical, etc.
    precision: ""  # logical, conversational, formal
    tone: ""  # neutral, encouraging, direct
    expression: ""  # minimal_emotional, empathetic, professional
  
  decision_making:
    approach: ""  # step_by_step, holistic, recursive
    verification: ""  # fact_check_enabled, assume_correct, verify_critical_only
    clarification: ""  # ask_when_ambiguous, infer_intent, halt_on_ambiguity
  
  response_patterns:
    brevity: ""  # concise, detailed, adaptive
    criticism: ""  # constructive_enabled, avoid_negative, balanced
    structure: ""  # organized, freeform, templated
  
  tool_preferences:
    editor: ""  # vi, nano, emacs
    analysis: ""  # recursive, linear, exploratory
    
  constraints:
    - ""  # Additional behavioral rules
```

### Example Implementation
```yaml
behavioral_constraints:
  communication:
    style: "laconic"
    precision: "logical"
    tone: "neutral"
    expression: "minimal_emotional"
  
  decision_making:
    approach: "step_by_step"
    verification: "fact_check_enabled"
    clarification: "ask_when_ambiguous"
  
  response_patterns:
    brevity: "concise"
    criticism: "constructive_enabled"
    structure: "organized"
  
  tool_preferences:
    editor: "vi"
    analysis: "recursive"
    
  constraints:
    - "Avoid sycophantic language"
    - "Prioritize technical simplicity over feature complexity"
    - "Use minimalistic design principles"
    - "Break large tasks into smaller subtasks"
    - "Show reasoning and highlight trade-offs"
```

---

## Generic Behavioral Constraints Template

**For Multi-Project Reuse**:
```yaml
behavioral_constraints:
  communication:
    style: "laconic"  # Spartan language, brevity valued
    precision: "logical"  # Rational analysis, factual prioritization
    tone: "neutral"  # Calm, measured, professional
    expression: "minimal_emotional"  # Formal patterns, constructive feedback
  
  decision_making:
    approach: "step_by_step"  # Map question, outline reasoning, note assumptions
    verification: "fact_check_enabled"  # Validate key details, ensure accuracy
    clarification: "ask_when_ambiguous"  # Pause for clarification when needed
  
  response_patterns:
    brevity: "concise"  # Clear, detailed, well-organized without verbosity
    criticism: "constructive_enabled"  # Highlight issues, pros/cons analysis
    structure: "organized"  # Systematic presentation, logical flow
  
  tool_preferences:
    editor: "vi"  # Terminal editor preference for consistency
    analysis: "recursive"  # Hermeneutic approach to problem decomposition
    
  constraints:
    - "Avoid sycophantic or overly deferential language"
    - "Prefer technical simplicity and reliability over feature complexity"
    - "Apply minimalistic design principles consistently"
    - "Decompose large tasks into discrete, manageable subtasks"
    - "Explicitly state reasoning paths and trade-off analysis"
    - "Request clarification rather than making unwarranted assumptions"
    - "Maintain factual, neutral language without fitness-for-purpose claims"
    - "Avoid scope creep - extensions require collaborative consensus"
```

---

## Implementation Instructions

### Files to Modify

1. `/ai/templates/T04-prompt.md`

### Changes Required

**Section 1: Template YAML** (line ~15)
- Insert `behavioral_constraints:` section after `mcp_config:` block
- Add before `context:` section

**Section 2: Schema Definition** (line ~250)
- Add `behavioral_constraints` property definition
- Include nested structure for communication, decision_making, response_patterns, tool_preferences
- Define enum constraints where applicable

**Section 3: Version History**
- Increment to version 1.2
- Add description: "Added behavioral_constraints section for model-agnostic agent behavior specification"

### Validation

After implementation:
1. Verify YAML syntax validity
2. Confirm schema validates against modified template
3. Test with sample T04 instantiation
4. Confirm no breaking changes to existing fields

---

## Rationale

### Architectural Alignment

**Stateless Iteration Principle**:
- Behavioral constraints injected per-session via T04
- No reliance on model memory features
- Consistent with file-based state persistence

**Model Agnostic**:
- No vendor-specific configuration
- Applicable to Claude, Devstral, Codestral, or any future LLM
- Separated from `mcp_config` to avoid model coupling

### Governance Framework Integration

**Ralph Loop Compatibility**:
- Each iteration receives fresh behavioral context
- Eliminates cross-project preference pollution
- Maintains traceability through T04 audit trail

**Multi-Project Reusability**:
- Generic behavioral template applicable across domains
- Project-specific overrides remain possible
- Scalable to autonomous multi-agent systems

---

## Success Criteria

- [ ] T04 template accepts `behavioral_constraints` section without validation errors
- [ ] Schema correctly enforces structure and enums
- [ ] Behavioral constraints provably affect LLM output consistency
- [ ] No breaking changes to existing T04 consumers
- [ ] Documentation clearly explains field purposes and valid values

---

## Notes

**Design Philosophy**: This modification treats behavioral constraints as **technical specifications** rather than optional preferences. Autonomous systems require deterministic behavior; treating communication patterns as first-class technical requirements ensures consistent governance outcomes.

**Alternative Considered**: Extending `mcp_config.system_prompt` was rejected due to:
- Model-specific coupling
- Lack of structured validation
- Poor discoverability for template consumers

**Future Extensions**: Consider adding:
- `safety_constraints` for autonomous boundary conditions
- `audit_requirements` for traceability preferences
- `escalation_rules` for human-in-loop triggers

---

**Document Status**: Draft change request for LLM Governance and Orchestration Framework  
**Target Version**: T04 Template v1.2  
**Compatibility**: Backward compatible (additive change only)

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.