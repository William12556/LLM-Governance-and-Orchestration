"""Requirement oracle for split_into_chunks.

Each test maps to one numbered requirement in task.md. These assertions are
the objective ground truth for the smoke test: they are independent of any
model's opinion about whether the implementation is correct.

Path insertion is explicit rather than relying on pytest rootdir behaviour,
so the suite runs identically from any working directory.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from split import split_into_chunks  # noqa: E402


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


def _items(length):
    return list(range(length))


@pytest.mark.parametrize("length,n", CASES)
def test_returns_exactly_n_lists(length, n):
    """Requirement 1: exactly n lists."""
    result = split_into_chunks(_items(length), n)
    assert isinstance(result, list)
    assert len(result) == n, f"expected {n} chunks, got {len(result)}"
    assert all(isinstance(chunk, list) for chunk in result)


@pytest.mark.parametrize("length,n", CASES)
def test_preserves_all_elements_in_order(length, n):
    """Requirement 2: every element exactly once, original order."""
    items = _items(length)
    result = split_into_chunks(items, n)
    flattened = [element for chunk in result for element in chunk]
    assert flattened == items


@pytest.mark.parametrize("length,n", CASES)
def test_chunk_sizes_differ_by_at_most_one(length, n):
    """Requirement 3: sizes differ by at most 1."""
    result = split_into_chunks(_items(length), n)
    sizes = [len(chunk) for chunk in result]
    assert max(sizes) - min(sizes) <= 1, f"sizes {sizes} differ by more than 1"


@pytest.mark.parametrize("n", [1, 2, 5])
def test_empty_input_returns_n_empty_lists(n):
    """Requirement 4: empty items returns n empty lists."""
    result = split_into_chunks([], n)
    assert result == [[] for _ in range(n)]
