#!/usr/bin/env python3
import py_compile
import sys

try:
    py_compile.compile('/Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration/framework/ai/ael/experiments/claude-omlx-comparison/csv_stats.py', doraise=True)
    print("✓ Python syntax is valid")
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error: {e}")
    sys.exit(1)