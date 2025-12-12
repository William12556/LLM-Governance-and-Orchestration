# Governance Issue Report: Test Directory Structure

## Issue Summary

**Protocol Affected:** P01 Project Initialization (Section 1.2.6)  
**Current State:** Specifies `src/tests/` for test files  
**Problem:** Python import mechanism causes ModuleNotFoundError when tests are in `src/tests/`  
**Impact:** Tests cannot execute, blocking P06 workflow

## Root Cause Analysis

When pytest collects test files from `src/tests/`, it imports test modules before the package is installed in sys.path. This causes:

```
ModuleNotFoundError: No module named 'sed_awk_mcp.security'
```

Even with:
- Package installed via `pip install -e '.[dev]'`
- conftest.py attempting sys.path manipulation
- PYTHONPATH environment variable set

The issue: pytest's import machinery loads test files as modules before conftest.py executes, and the `src/` namespace conflicts with the installed package namespace.

## Solution

Move tests to root-level `tests/` directory. This is Python ecosystem standard and resolves import conflicts.

## Required Governance Changes

### 1. Update P01 Section 1.2.6 Project Folder Structure

**Current:**
```
    └── <project name>/
        ├── src/                      # Source code
        │   └── tests/
```

**Change to:**
```
    └── <project name>/
        ├── tests/                    # Test files (root level)
        ├── src/                      # Source code
```

### 2. Update P01 Section 1.2.2 .gitignore

**Add:**
```
.pytest_cache/
```

(Already present, but verify)

### 3. Update P06 Section 1.7.3 Test Script Creation

**Current:**
```
- Claude Desktop: Generates executable test scripts in src/tests/
- Claude Desktop: Creates unit tests for components in subdirectories (src/tests/<component>/)
```

**Change to:**
```
- Claude Desktop: Generates executable test scripts in tests/
- Claude Desktop: Creates unit tests for components in subdirectories (tests/<component>/)
```

### 4. Update Tool Pytest Configuration in pyproject.toml Template

**Current (P01 Section 1.2.8):**
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

This is already correct - no change needed.

### 5. Update P06 Section 1.7.11 Test Lifecycle Management

**Current:**
```
- Claude Desktop: Maintains permanent tests in component subdirectories
```

**Change to:**
```
- Claude Desktop: Maintains permanent tests in tests/<component>/ subdirectories
```

## Supporting Evidence

### Test Execution Results

**Failed with src/tests/ structure:**
- 0 tests collected
- 4 ModuleNotFoundError during collection
- All conftest.py attempts failed

**Succeeded with tests/ structure:**
- 40 tests collected
- 30 passed, 10 failed (actual test logic failures, not import errors)
- Coverage: 47% overall

### Industry Standards

Root-level `tests/` is standard in Python ecosystem:
- pytest documentation recommends `tests/` at project root
- Python Packaging Authority (PyPA) sample projects use `tests/`
- Avoids namespace conflicts with installed packages

## Impact Assessment

**Low Risk:**
- Standard Python convention
- Improves maintainability
- No functional changes to generated code
- Only affects test organization

**Benefits:**
- Tests execute successfully
- Standard pytest discovery works
- No sys.path manipulation required
- Better separation of concerns

## Implementation Notes

When creating test files, Claude Desktop should:
1. Create `tests/` directory at project root (not in `src/`)
2. Organize tests by component: `tests/<component>/test_*.py`
3. Ensure root-level `conftest.py` exists if needed
4. Reference tests via `pytest tests/` in commands

## Verification

After governance update, verify:
1. P01 folder structure shows `tests/` at root
2. P06 directives reference `tests/` not `src/tests/`
3. pyproject.toml template has `testpaths = ["tests"]`
4. Example commands use `pytest tests/` not `pytest src/tests/`

---

**Recommendation:** Approve changes and update master governance.md
