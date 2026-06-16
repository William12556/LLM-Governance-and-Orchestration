#!/usr/bin/env python3
"""
CSV Statistics Calculator

A command-line tool to compute basic statistics (mean, median, standard deviation)
from numeric columns in a CSV file.
"""

import csv
import statistics
import argparse
import sys


def load_csv(path: str) -> tuple[list[str], list[dict]]:
    """
    Open CSV with DictReader. Return headers and rows.
    
    Args:
        path: Path to the CSV file
        
    Returns:
        tuple: (headers, rows) where headers is list of column names,
               rows is list of dictionaries mapping headers to values
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file is empty (no rows)
    """
    try:
        with open(path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                raise ValueError("CSV file has no data rows")
            headers = reader.fieldnames or []
            return headers, rows
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")


def compute_stats(headers: list[str], rows: list[dict]) -> dict[str, dict[str, float]]:
    """
    Compute statistics for numeric columns.
    
    Args:
        headers: List of column names from CSV
        rows: List of dictionaries containing row data
        
    Returns:
        Dictionary mapping column names to their statistics.
        Format: {col: {"mean": float, "median": float, "stdev": float}}
    """
    stats = {}
    
    for col in headers:
        try:
            # Extract numeric values from the column
            values = []
            for row in rows:
                try:
                    val = float(row.get(col, ""))
                    values.append(val)
                except (ValueError, TypeError):
                    continue
            
            # Skip columns with no valid numeric values
            if not values:
                continue
            
            # Compute statistics
            mean_val = statistics.mean(values)
            median_val = statistics.median(values)
            stdev_val = statistics.pstdev(values)
            
            stats[col] = {
                "mean": mean_val,
                "median": median_val,
                "stdev": stdev_val
            }
        
        except Exception:
            # Skip columns that cause any errors
            continue
    
    return stats


def write_report(stats: dict[str, dict[str, float]], output_path: str, row_count: int) -> None:
    """
    Write plain-text statistics report.
    
    Args:
        stats: Dictionary of statistics from compute_stats
        output_path: Path to write the report
        row_count: Number of data rows processed
    """
    try:
        with open(output_path, 'w') as f:
            # Write header with row count
            f.write(f"CSV Statistics Report - {row_count} rows processed\n")
            f.write("=" * 50 + "\n\n")
            
            # Write statistics for each column
            for col, col_stats in stats.items():
                f.write(f"Column: {col}\n")
                f.write(f"  Mean:     {col_stats['mean']:.4f}\n")
                f.write(f"  Median:   {col_stats['median']:.4f}\n")
                f.write(f"  Stdev:    {col_stats['stdev']:.4f}\n")
                f.write("\n")
    
    except (IOError, OSError) as e:
        raise OSError(f"Failed to write report to {output_path}: {e}")


def main():
    """
    Main entry point for the CSV statistics calculator.
    
    Parses command-line arguments and orchestrates the processing pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Compute statistics from CSV files"
    )
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output statistics report")
    
    args = parser.parse_args()
    
    try:
        # Load CSV data
        headers, rows = load_csv(args.input)
        
        # Compute statistics
        stats = compute_stats(headers, rows)
        
        # Check if any numeric columns were found
        if not stats:
            raise RuntimeError("no numeric columns found")
        
        # Write report
        write_report(stats, args.output, len(rows))
        
        # Print success summary
        print(f"Processed {len(rows)} rows, {len(stats)} columns")
        
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
