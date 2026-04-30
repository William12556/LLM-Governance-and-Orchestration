#!/usr/bin/env python3
"""CSV Statistics Calculator - Compute mean, median, and standard deviation for CSV columns."""

import argparse
import csv
import statistics
import sys
from typing import Dict, List, Tuple


def load_csv(path: str) -> Tuple[List[str], List[Dict]]:
    """Open CSV with DictReader. Return headers and rows."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                raise ValueError(f"No rows found in {path}")
            headers = reader.fieldnames if reader.fieldnames else []
            return headers, rows
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")


def compute_stats(headers: List[str], rows: List[Dict]) -> Dict[str, Dict[str, float]]:
    """For each column, attempt float conversion of all values. Skip columns with no convertible values."""
    stats = {}
    for col in headers:
        values = []
        for row in rows:
            try:
                value = float(row.get(col, ''))
                values.append(value)
            except (ValueError, TypeError, AttributeError):
                continue
        if values:
            stats[col] = {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'stdev': statistics.pstdev(values)
            }
    return stats


def write_report(stats: Dict[str, Dict[str, float]], output_path: str, row_count: int) -> None:
    """Write plain-text report."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Report (rows={row_count})\n")
        for col, values in stats.items():
            f.write(f"\n{col}\n")
            f.write(f"  mean  = {values['mean']:.4f}\n")
            f.write(f"  median = {values['median']:.4f}\n")
            f.write(f"  stdev = {values['stdev']:.4f}\n")


def main():
    """Main entry point with argparse setup and error handling."""
    parser = argparse.ArgumentParser(description='CSV Statistics Calculator')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', required=True, help='Output report file path')
    args = parser.parse_args()
    try:
        headers, rows = load_csv(args.input)
        stats = compute_stats(headers, rows)
        if not stats:
            raise RuntimeError("no numeric columns found")
        write_report(stats, args.output, len(rows))
        print(f"Processed {len(rows)} rows, {len(stats)} columns")
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
