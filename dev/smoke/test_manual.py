#!/usr/bin/env python3

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from split import split_into_chunks

def test_case(length, n):
    """Test a single case"""
    items = list(range(length))
    result = split_into_chunks(items, n)
    
    # Requirement 1: exactly n lists
    assert len(result) == n, f"Expected {n} chunks, got {len(result)}"
    
    # Requirement 2: all elements preserved in order
    flattened = [item for chunk in result for item in chunk]
    assert flattened == items, f"Elements not preserved: {flattened} != {items}"
    
    # Requirement 3: chunk sizes differ by at most 1
    sizes = [len(chunk) for chunk in result]
    assert max(sizes) - min(sizes) <= 1, f"Chunk sizes differ by more than 1: {sizes}"
    
    return True

def test_empty_cases():
    """Test empty input cases"""
    # Requirement 4: empty items returns n empty lists
    for n in [1, 2, 5]:
        result = split_into_chunks([], n)
        expected = [[] for _ in range(n)]
        assert result == expected, f"Empty case failed for n={n}: {result} != {expected}"
    
    return True

# Test cases from the test file
CASES = [
    (0, 1),
    (0, 3),
    (1, 1),
    (1, 4),
    (3, 5),
    (4, 3),
    (5, 4),
    (7, 3),
    (9, 3),
    (10, 3),
    (10, 4),
    (100, 7),
]

print("Testing split_into_chunks implementation...")

# Test all cases
all_passed = True
for length, n in CASES:
    try:
        test_case(length, n)
        print(f"✓ Case ({length}, {n}) passed")
    except Exception as e:
        print(f"✗ Case ({length}, {n}) failed: {e}")
        all_passed = False

# Test empty cases
try:
    test_empty_cases()
    print("✓ Empty cases passed")
except Exception as e:
    print(f"✗ Empty cases failed: {e}")
    all_passed = False

if all_passed:
    print("\n✓ All tests passed!")
    sys.exit(0)
else:
    print("\n✗ Some tests failed!")
    sys.exit(1)
