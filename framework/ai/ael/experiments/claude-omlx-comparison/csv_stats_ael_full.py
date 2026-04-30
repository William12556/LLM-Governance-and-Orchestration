#!/usr/bin/env python3
"""CSV statistics computation tool."""

import csv
import statistics
import argparse
import sys


def load_csv(path: str) -> tuple[list[str], list[dict]]:
    """Open CSV with DictReader. Return headers and rows.
    
    Args:
        path: Path to CSV file
        
    Returns:
        Tuple of (headers, rows) where headers is list of column names
        and rows is list of dictionaries mapping column names to values
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is empty (no rows)
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if headers is None:
                raise ValueError("CSV file has no headers")
            
            rows = list(reader)
            if not rows:
                raise ValueError("CSV file has no data rows")
            
            return headers, rows
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")


def compute_stats(headers, rows) -> dict[str, dict[str, float]]:
    """Compute statistics for numeric columns.
    
    Args:
        headers: List of column names
        rows: List of dictionaries containing the data
        
    Returns:
        Dictionary mapping column name to statistics dictionary
        with keys: 'mean', 'median', 'stdev'
        
    Note:
        Columns with no convertible numeric values are skipped.
    """
    stats = {}
    
    for col in headers:
        try:
            # Extract values and convert to float
            values = []
            for row in rows:
                try:
                    value = float(row[col])
                    values.append(value)
                except (ValueError, TypeError):
                    # Skip non-convertible values
                    continue
            
            # Only add stats if we have at least one valid value
            if values:
                mean = statistics.mean(values)
                median = statistics.median(values)
                stdev = statistics.pstdev(values)  # Population standard deviation
                
                stats[col] = {
                    'mean': mean,
                    'median': median,
                    'stdev': stdev
                }
        except Exception:
            # Skip columns that cause any errors
            continue
    
    return stats


def write_report(stats, output_path, row_count) -> None:
    """Write plain-text statistics report.
    
    Args:
        stats: Dictionary of statistics from compute_stats
        output_path: Path to write the report file
        row_count: Number of rows processed
        
    Raises:
        OSError: If file cannot be written
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header with row count
            f.write(f"CSV Statistics Report - {row_count} rows processed\n")
            f.write("=" * 60 + "\n\n")
            
            # Write statistics for each column
            for col, col_stats in stats.items():
                f.write(f"Column: {col}\n")
                f.write(f"  Mean:   {col_stats['mean']:.4f}\n")
                f.write(f"  Median: {col_stats['median']:.4f}\n")
                f.write(f"  Stdev:  {col_stats['stdev']:.4f}\n")
                f.write("\n")
    except OSError as e:
        raise OSError(f"Failed to write report to {output_path}: {e}")


def main():
    """Main entry point with argument parsing and error handling."""
    parser = argparse.ArgumentParser(
        description="Compute statistics for numeric columns in a CSV file"
    )
    parser.add_argument('--input', required=True, help='Path to input CSV file')
    parser.add_argument('--output', required=True, help='Path to output report file')
    
    args = parser.parse_args()
    
    try:
        # Load CSV data
        headers, rows = load_csv(args.input)
        row_count = len(rows)
        
        # Compute statistics
        stats = compute_stats(headers, rows)
        
        # Check if any numeric columns were found
        if not stats:
            raise RuntimeError("no numeric columns found")
        
        # Write report
        write_report(stats, args.output, row_count)
        
        # Print success summary
        col_count = len(stats)
        print(f"Successfully processed {row_count} rows, computed statistics for {col_count} columns")
        
    except (FileNotFoundError, ValueError, RuntimeError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
