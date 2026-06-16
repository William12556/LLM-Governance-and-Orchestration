# T04 Prompt — CSV Statistics Calculator

Created: 2026 April 28

---

```yaml
prompt_info:
  id: "prompt-e1a2b3c4"
  task_type: code_generation
  source_ref: "experiment-claude-omlx-comparison"
  date: "2026-04-28"
  iteration: 1
  coupled_docs:
    change_ref: "change-e1a2b3c4"
    change_iteration: 1

context:
  purpose: >
    Standalone CSV statistics calculator. Reads a CSV file, computes per-column
    descriptive statistics, writes a plain-text summary report.
  integration: >
    Self-contained experiment artefact. No project integration required.
    Located in framework/ai/ael/experiments/claude-omlx-comparison/.
  knowledge_references: []
  constraints:
    - Python standard library only. No third-party packages.
    - Python 3.11 compatible.
    - Must handle files that do not exist or are malformed.

specification:
  description: >
    Implement csv_stats.py: a command-line program that reads a CSV file and
    computes mean, median, and standard deviation for each numeric column.
    Writes results to a plain-text report file.
  requirements:
    functional:
      - Accept input CSV path and output report path as command-line arguments.
      - Detect and process all numeric columns. Skip non-numeric columns silently.
      - Compute mean, median, and population standard deviation per numeric column.
      - Write report to output path. Report lists each numeric column with its three statistics.
      - Print a one-line summary to stdout on completion (columns processed, rows read).
    technical:
      language: Python
      version: "3.11"
      standards:
        - Standard library only (csv, statistics, argparse, sys, os).
        - Error handling for missing file, empty file, no numeric columns.
        - Docstrings on all functions.
        - No global state.

design:
  architecture: Single-module procedural script with three pure functions and a main().
  components:
    - name: load_csv
      type: function
      purpose: Read CSV file, return header list and list of row dicts.
      interface:
        inputs:
          - name: path
            type: str
            description: Path to input CSV file.
        outputs:
          type: "tuple[list[str], list[dict]]"
          description: headers, rows
        raises:
          - FileNotFoundError
          - ValueError (empty file)
      logic:
        - Open path with csv.DictReader.
        - Return fieldnames and list of row dicts.
        - Raise ValueError if file has no rows.

    - name: compute_stats
      type: function
      purpose: Compute mean, median, std dev for each numeric column.
      interface:
        inputs:
          - name: headers
            type: "list[str]"
            description: Column names.
          - name: rows
            type: "list[dict]"
            description: Row dicts from load_csv.
        outputs:
          type: "dict[str, dict[str, float]]"
          description: >
            Mapping of column name to dict with keys mean, median, stdev.
            Only numeric columns included.
        raises: []
      logic:
        - For each column, attempt float conversion of all values.
        - Skip column if fewer than one convertible value.
        - Compute statistics.mean, statistics.median, statistics.pstdev.
        - Return results dict.

    - name: write_report
      type: function
      purpose: Write plain-text statistics report to output path.
      interface:
        inputs:
          - name: stats
            type: "dict[str, dict[str, float]]"
            description: Output of compute_stats.
          - name: output_path
            type: str
            description: Path to write report file.
          - name: row_count
            type: int
            description: Number of data rows read.
        outputs:
          type: None
          description: Writes file, returns nothing.
        raises:
          - OSError
      logic:
        - Write header line with row count.
        - For each column in stats, write column name and three statistics (4 d.p.).

    - name: main
      type: function
      purpose: CLI entry point. Parses args, calls load_csv, compute_stats, write_report.
      logic:
        - argparse: --input (required), --output (required).
        - Call load_csv; catch and print FileNotFoundError, ValueError, exit 1.
        - Call compute_stats; exit 1 with message if no numeric columns found.
        - Call write_report; catch OSError, exit 1.
        - Print completion summary to stdout.

  dependencies:
    internal: []
    external: []

error_handling:
  strategy: Catch at main(), print human-readable message to stderr, exit 1.
  exceptions:
    - exception: FileNotFoundError
      condition: Input CSV path does not exist.
      handling: Print "Error: file not found: <path>", exit 1.
    - exception: ValueError
      condition: CSV file exists but contains no data rows.
      handling: Print "Error: CSV file is empty", exit 1.
    - exception: RuntimeError
      condition: No numeric columns detected.
      handling: Print "Error: no numeric columns found", exit 1.
    - exception: OSError
      condition: Cannot write output report.
      handling: Print "Error: cannot write report: <msg>", exit 1.
  logging:
    level: NONE
    format: "stderr print statements only"

deliverable:
  format_requirements:
    - Save generated code directly to specified path.
  files:
    - path: framework/ai/ael/experiments/claude-omlx-comparison/csv_stats.py
      content: "Implement as specified above."

success_criteria:
  - csv_stats.py exists at the specified path.
  - File is syntactically valid Python 3.11.
  - load_csv, compute_stats, write_report, main functions are present with docstrings.
  - Standard library only — no import of third-party packages.
  - Error paths for missing file, empty file, no numeric columns are handled.

element_registry:
  source: "N/A — experiment artefact, no project registry"
  entries:
    modules:
      - name: csv_stats
        path: framework/ai/ael/experiments/claude-omlx-comparison/csv_stats.py
    functions:
      - name: load_csv
        module: csv_stats
        signature: "load_csv(path: str) -> tuple[list[str], list[dict]]"
      - name: compute_stats
        module: csv_stats
        signature: "compute_stats(headers: list[str], rows: list[dict]) -> dict[str, dict[str, float]]"
      - name: write_report
        module: csv_stats
        signature: "write_report(stats: dict, output_path: str, row_count: int) -> None"
      - name: main
        module: csv_stats
        signature: "main() -> None"
```

---

```yaml
tactical_brief: |
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
```
