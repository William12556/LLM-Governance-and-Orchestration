#!/usr/bin/env python3
"""
CSV Statistics Calculator

A command-line program that reads a CSV file and computes descriptive statistics
for each numeric column. Writes results to a plain-text report file.

Requirements:
- Standard library only (csv, statistics, argparse, sys, os)
- Python 3.11 compatible
- Handle missing files, empty files, and no numeric columns
- Four functions: load_csv, compute_stats, write_report, main

Usage:
    python csv_stats.py --input <input_csv> --output <output_report>
"""

import csv
import statistics
import argparse
import sys
from typing import Dict, List, Tuple


def load_csv(path: str) -> Tuple[List[str], List[Dict]]:
    """
    Read CSV file and return headers and row data.

    Args:
        path: Path to input CSV file

    Returns:
        Tuple containing:
        - List of header strings
        - List of dictionaries representing rows (column: value)

    Raises:
        FileNotFoundError: If the specified path does not exist
        ValueError: If the CSV file is empty (no data rows)
    """
    try:
        with open(path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames

            if headers is None:
                headers = []

            rows = list(reader)

            if not rows:
                raise ValueError("CSV file is empty")

            return headers, rows

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")


def compute_stats(headers: List[str], rows: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Compute mean, median, and standard deviation for each numeric column.

    Args:
        headers: List of column names
        rows: List of row dictionaries from load_csv

    Returns:
        Dictionary mapping column name to statistics dictionary with keys:
        - mean: arithmetic mean
        - median: median value
        - stdev: population standard deviation

        Only numeric columns are included in the result.
    """
    stats = {}

    if not headers or not rows:
        return stats

    for column in headers:
        values = []

        # Collect all convertible numeric values for this column
        for row in rows:
            try:
                value = float(row[column])
                values.append(value)
            except (ValueError, TypeError, KeyError):
                # Skip non-numeric values
                continue

        # Only include columns with at least one numeric value
        if len(values) == 0:
            continue

        # Compute statistics
        column_stats = {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.pstdev(values)  # Population standard deviation
        }

        stats[column] = column_stats

    return stats


def write_report(stats: Dict[str, Dict[str, float]], output_path: str, row_count: int) -> None:
    """
    Write plain-text statistics report to output file.

    Args:
        stats: Statistics dictionary from compute_stats
        output_path: Path to write the report file
        row_count: Number of data rows processed

    Raises:
        OSError: If unable to write to the output path
    """
    try:
        with open(output_path, 'w') as report_file:
            # Write header with row count
            report_file.write(f"CSV Statistics Report (processed {row_count} rows)\n")
            report_file.write("=" * 60 + "\n\n")

            # Write statistics for each column
            for column, column_stats in stats.items():
                report_file.write(f"Column: {column}\n")
                report_file.write(f"  Mean:     {column_stats['mean']:.4f}\n")
                report_file.write(f"  Median:   {column_stats['median']:.4f}\n")
                report_file.write(f"  Std Dev:  {column_stats['stdev']:.4f}\n")
                report_file.write("\n")

    except OSError as e:
        raise OSError(f"Cannot write report: {str(e)}")


def main() -> None:
    """
    CLI entry point. Parses command-line arguments and orchestrates the workflow.
    """
    parser = argparse.ArgumentParser(
        description="Compute statistics for numeric columns in a CSV file"
    )
    parser.add_argument('--input', required=True, help='Path to input CSV file')
    parser.add_argument('--output', required=True, help='Path to output report file')

    args = parser.parse_args()

    try:
        headers, rows = load_csv(args.input)
        stats = compute_stats(headers, rows)
        if not stats:
            raise RuntimeError("no numeric columns found")
        write_report(stats, args.output, len(rows))
        num_columns = len(stats)
        print(f"Processed {len(rows)} rows, {num_columns} numeric column(s)")
    except FileNotFoundError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
