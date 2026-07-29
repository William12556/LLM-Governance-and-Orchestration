#!/usr/bin/env python3
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and test
from split import split_into_chunks

def test_basic():
    # Test case: split 10 items into 3 chunks
    items = list(range(10))
    result = split_into_chunks(items, 3)
    print(f"Input: {items}")
    print(f"Result: {result}")
    print(f"Number of chunks: {len(result)}")
    print(f"Chunk sizes: {[len(chunk) for chunk in result]}")
    
    # Verify requirements
    assert len(result) == 3, f"Expected 3 chunks, got {len(result)}"
    
    # Check all elements are present and in order
    flattened = [item for chunk in result for item in chunk]
    assert flattened == items, f"Elements not preserved: {flattened} != {items}"
    
    # Check chunk sizes differ by at most 1
    sizes = [len(chunk) for chunk in result]
    assert max(sizes) - min(sizes) <= 1, f"Chunk sizes differ by more than 1: {sizes}"
    
    print("✓ All basic tests passed!")

def test_empty():
    # Test empty input
    result = split_into_chunks([], 3)
    print(f"Empty input result: {result}")
    assert result == [[], [], []], f"Expected [[], [], []], got {result}"
    print("✓ Empty input test passed!")

if __name__ == "__main__":
    test_basic()
    test_empty()