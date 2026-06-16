#!/usr/bin/env python3
"""Test script for csv_stats.py functionality"""

import sys
import os

# Add the current directory to sys.path so we can import csv_stats
sys.path.insert(0, '/Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration/framework/ai/ael/experiments/claude-omlx-comparison')

from csv_stats import load_csv, compute_stats, write_report

def test_load_csv():
    """Test loading a CSV file"""
    print("Testing load_csv...")
    headers, rows = load_csv('test_data.csv')
    print(f"  Headers: {headers}")
    print(f"  Rows: {len(rows)}")
    assert len(headers) == 4
    assert len(rows) == 5
    print("  ✓ load_csv test passed")

def test_compute_stats():
    """Test computing statistics"""
    print("Testing compute_stats...")
    headers, rows = load_csv('test_data.csv')
    stats = compute_stats(headers, rows)
    print(f"  Computed stats for {len(stats)} columns")
    
    # Should have stats for numeric columns only
    assert 'name' not in stats  # name is string
    assert 'age' in stats
    assert 'height' in stats
    assert 'salary' in stats
    
    # Check stats structure
    for col, col_stats in stats.items():
        assert 'mean' in col_stats
        assert 'median' in col_stats
        assert 'stdev' in col_stats
    
    print("  ✓ compute_stats test passed")

def test_write_report():
    """Test writing report"""
    print("Testing write_report...")
    headers, rows = load_csv('test_data.csv')
    stats = compute_stats(headers, rows)
    write_report(stats, 'test_output.txt', len(rows))
    
    # Verify file was created and has content
    assert os.path.exists('test_output.txt')
    with open('test_output.txt', 'r') as f:
        content = f.read()
        assert len(content) > 0
        assert "age" in content
        assert "mean" in content
    
    print("  ✓ write_report test passed")

def test_error_conditions():
    """Test error handling"""
    print("Testing error conditions...")
    
    # Test missing file
    try:
        load_csv('nonexistent.csv')
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError:
        print("  ✓ FileNotFoundError test passed")
    
    # Test empty CSV
    with open('empty.csv', 'w') as f:
        f.write('')
    try:
        load_csv('empty.csv')
        assert False, "Should have raised ValueError"
    except ValueError:
        print("  ✓ Empty file test passed")
    
    # Clean up
    os.remove('empty.csv')

if __name__ == "__main__":
    test_load_csv()
    test_compute_stats()
    test_write_report()
    test_error_conditions()
    print("\n✓ All tests passed!")