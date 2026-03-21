Created: 2025 February 13

# Behavioral Standards - README

## Quick Start

This directory contains example behavioral standards configuration for autonomous LLM execution within the governance framework.

## Files

- **behavioral-standards.yaml** - YAML configuration defining behavioral constraints
- **behavioral-standards.schema.json** - JSON Schema for validation
- **scripts/validate-behavioral-standards.py** - Python validation script
- **BEHAVIORAL_STANDARDS_GUIDE.md** - Complete implementation guide

## Usage

### 1. Copy to Your Project

```bash
# Copy files to your project's workspace/knowledge/ directory
cp behavioral-standards.yaml <project>/workspace/knowledge/
cp behavioral-standards.schema.json <project>/workspace/knowledge/
cp scripts/validate-behavioral-standards.py <project>/scripts/
```

### 2. Validate Configuration

```bash
cd <project>
./scripts/validate-behavioral-standards.py
```

### 3. Reference in T04 Prompts

```yaml
tactical_execution:
  behavioral_standards:
    source: "workspace/knowledge/behavioral-standards.yaml"
    enforcement_level: "strict"
```

## Purpose

Provides deterministic behavioral constraints for:
- Ralph Loop autonomous execution
- Multi-model worker/reviewer coordination
- Divergence detection and escalation
- Model-agnostic behavioral specification

## Documentation

See [BEHAVIORAL_STANDARDS_GUIDE.md](<BEHAVIORAL_STANDARDS_GUIDE.md>) for complete implementation details.

## Integration

Part of Phase 2 governance refactoring for Ralph Loop integration with OLLama+MacOS autonomous execution framework.

---

Copyright (c) 2025 William Watson. This work is licensed under the MIT License.
