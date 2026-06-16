#!/usr/bin/env python3
"""CSV Statistics Calculator

Reads a CSV file and computes descriptive statistics (mean, median, standard
deviation) for each numeric column. Writes results to a plain-text report file.
"""

import argparse
import csv
import sys
from statistics import mean, median, pstdev


def load_csv(path: str) -> tuple[list[str], list[dict]]:
    """Read CSV file and return headers and rows."""
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if headers is None:
            raise ValueError("CSV file is empty")
        rows = list(reader)
        if not rows:
            raise ValueError("CSV file is empty")
    return list(headers), rows


def compute_stats(headers: list[str], rows: list[dict]) -> dict[str, dict[str, float]]:
    """Compute mean, median, and standard deviation for each numeric column."""
    results = {}
    for col in headers:
        values = []
        for row in rows:
            try:
                value = float(row[col])
                values.append(value)
            except (ValueError, TypeError, KeyError):
                continue
        if values:
            results[col] = {
                'mean': mean(values),
                'median': median(values),
                'stdev': pstdev(values)
            }
    return results


def write_report(stats: dict[str, dict[str, float]], output_path: str, row_count: int) -> None:
    """Write plain-text statistics report to output file."""
    with open(output_path, 'w') as f:
        f.write(f"CSV Statistics Report\n")
        f.write(f"Rows processed: {row_count}\n")
        f.write(f"\n")
        for col, stat_dict in stats.items():
            f.write(f"Column: {col}\n")
            f.write(f"  Mean:   {stat_dict['mean']:.4f}\n")
            f.write(f"  Median: {stat_dict['median']:.4f}\n")
            f.write(f"  Stdev:  {stat_dict['stdev']:.4f}\n")
            f.write(f"\n")


def main() -> None:
    """CLI entry point. Parse arguments and orchestrate statistics computation."""
    parser = argparse.ArgumentParser(
        description='Compute statistics for numeric columns in a CSV file'
    )
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output report file path')
    args = parser.parse_args()

    try:
        headers, rows = load_csv(args.input)
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Error: CSV file is empty", file=sys.stderr)
        sys.exit(1)

    try:
        stats = compute_stats(headers, rows)
        if not stats:
            raise RuntimeError("no numeric columns found")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        write_report(stats, args.output, len(rows))
    except OSError as e:
        print(f"Error: cannot write report: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Processed {len(rows)} rows, {len(stats)} numeric columns")


if __name__ == '__main__':
    main()
