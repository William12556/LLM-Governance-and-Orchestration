# Phase B fixture — defective implementation.
#
# Produced verbatim by mistralai_Devstral-Small-2-24B-Instruct-2512-MLX-8Bit
# against task.md on 2026-07-29. Retained unmodified so the reviewer
# comparison runs against real model output rather than a hand-written bug.
#
# Known requirement violations:
#   R1  items=[0..4], n=4  -> returns 3 lists, not 4
#   R3  items=[0..9], n=3  -> sizes 4/4/2, differ by 2
#   R4  items=[],     n=3  -> range step 0, raises ValueError
#
# Copy to src/split.py before running Phase B.


def split_into_chunks(items, n):
    chunk_size = (len(items) + n - 1) // n
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
