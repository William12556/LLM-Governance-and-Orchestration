[AEL RUNTIME CONTEXT]
state_dir (full absolute path): /Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration/framework/.ael/ralph
project_root (full absolute path): /Users/williamwatson/Documents/GitHub/LLM-Governance-and-Orchestration/framework
Do not use 'state_dir' or 'project_root' as literal path components.
[END RUNTIME CONTEXT]

Create framework/ai/ael/experiments/claude-omlx-comparison/csv_stats.py

Standard library only (csv, statistics, argparse, sys). Python 3.11.

Implement four functions with docstrings:
- load_csv(path: str) -> tuple[list[str], list[dict]]
    Open CSV with DictReader. Return headers and rows.
    Raise FileNotFoundError if missing. Raise ValueError if no rows.
- compute_stats(headers, rows) -> dict[str, dict[str, float]]
    For each column, attempt float conversion of all values.
    Skip columns with no convertible values.
    Return {col: {mean: float, median: float, stdev: float}} using statistics module.
    stdev = pstdev (population).
- write_report(stats, output_path, row_count) -> None
    Write plain-text report. Header line with row count.
    Each column: name, mean, median, stdev to 4 d.p.
- main()
    argparse: --input (required), --output (required).
    Call load_csv, compute_stats, write_report in sequence.
    Catch FileNotFoundError, ValueError, RuntimeError, OSError — print to stderr, exit 1.
    If compute_stats returns empty dict, raise RuntimeError("no numeric columns found").
    On success, print one-line summary to stdout: rows read, columns processed.

Deliverable: single file csv_stats.py at the path above. No other files.

Success criteria:
- File exists and is syntactically valid Python.
- All four functions present with docstrings.
- No third-party imports.
- Error exits handled for missing file, empty file, no numeric columns, write failure.