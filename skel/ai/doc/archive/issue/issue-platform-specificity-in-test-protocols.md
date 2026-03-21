# Governance Framework Issue: Platform-Specific Requirements

**Issue Type:** Framework Design Limitation  
**Severity:** Medium  
**Component:** P06 Test Protocol, Section 1.7.17

## Problem Statement

The governance framework hardcodes platform-specific deployment assumptions (Raspberry Pi + Debian Linux) in P06 1.7.17 "Test Execution Platforms". This creates inappropriate context bleed across projects with different deployment targets.

## Current Implementation (Lines 580-595)

```markdown
- Unit tests: Development platform (MacOS) with comprehensive mocking
- Integration tests: Target platform (Raspberry Pi) with actual subsystems
- System tests: Target platform (Raspberry Pi) exclusively
- Acceptance tests: Target platform (Raspberry Pi) with stakeholder validation
- Regression tests: Development platform (primary), target platform (validation)
- Performance tests: Target platform (Raspberry Pi) for accurate measurements
Mocking requirements:
  - Development platform: Mock all external dependencies (nmcli, systemd, sockets)
  - Target platform: Use actual system services where integration testing required
```

## Impact

1. **Context Contamination**: LLM applies Raspberry Pi assumptions to unrelated projects (e.g., MCP server development)
2. **Inflexibility**: Framework forces specific platform narrative regardless of actual deployment target
3. **Maintenance Burden**: Platform-specific details require editing for each project type

## Example Manifestation

In mcp-sed-awk project (MCP server with no embedded deployment):
- LLM incorrectly assumed Raspberry Pi deployment
- Suggested platform-specific testing strategies inappropriate for the project
- Required manual correction and clarification

## Recommended Solution

**Option A: Parameterized Platform References**

Replace hardcoded platforms with variables:

```markdown
- Unit tests: Development platform (${DEV_PLATFORM}) with comprehensive mocking
- Integration tests: Target platform (${TARGET_PLATFORM}) with actual subsystems
- System tests: Target platform (${TARGET_PLATFORM}) exclusively
```

Projects define platform values in project-specific configuration.

**Option B: Generic Platform Language**

Remove specific platform references entirely:

```markdown
- Unit tests: Development platform with comprehensive mocking
- Integration tests: Target deployment platform with actual subsystems
- System tests: Target deployment platform exclusively
- Mocking requirements:
  - Development: Mock all external dependencies
  - Target: Use actual system services where integration testing required
```

**Option C: Conditional Sections**

Make platform-specific guidance optional/conditional based on project type:

```markdown
<platform_specific_guidance>
For embedded/IoT projects:
  - Development: Desktop OS (MacOS/Linux/Windows)
  - Target: Embedded platform (specify in project docs)
  
For server/service projects:
  - Development: Local workstation
  - Target: Production environment (cloud/on-premise)
  
For desktop applications:
  - Development: Target OS
  - Target: Same as development
</platform_specific_guidance>
```

## Preferred Solution

**Option B** - Generic platform language with project-specific elaboration in design documents. Maintains framework flexibility while allowing detailed platform specifications where needed.

## Implementation

1. Update P06 1.7.17 to use generic "development platform" and "target platform" terminology
2. Remove specific technology references (nmcli, systemd, sockets) - these belong in project designs
3. Add guidance: "Define specific platforms and their characteristics in project design documents"
4. Update version history with rationale

## Benefits

- Framework applicable to any project type (embedded, server, desktop, mobile)
- Reduces LLM context confusion across projects
- Simplifies framework maintenance
- Preserves testing rigor without platform lock-in

---

**Submitted by:** William Watson  
**Date:** 2025-12-12  
**Related Project:** mcp-sed-awk (where issue was discovered)
