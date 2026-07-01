"""
merge_data.py
-------------
Dataset integration module for PJM electricity demand and Newark weather analysis.
Scope: loading cleaned files, merging on date, validating row count, saving output.
No cleaning, metrics, visualization, or orchestration.

Inputs:
    data/pjm_daily_2025_clean.csv
    data/newark_weather_2025_clean.csv

Output:
    data/merged_data.csv
"""

import pandas as pd
import os
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = "data"

PJM_INPUT     = os.path.join(DATA_DIR, "pjm_daily_2025_clean.csv")
WEATHER_INPUT = os.path.join(DATA_DIR, "newark_weather_2025_clean.csv")
MERGED_OUTPUT = os.path.join(DATA_DIR, "merged_data.csv")

EXPECTED_ROWS = 365


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def load_csv(path: str, label: str, date_col: str = "date") -> pd.DataFrame:
    """
    Load a cleaned CSV and parse the date column.
    Exits on file-not-found or missing date column.
    """
    try:
        df = pd.read_csv(path, parse_dates=[date_col])
    except FileNotFoundError:
        print(f"ERROR [{label}] File not found: {path}")
        sys.exit(1)
    except ValueError as e:
        # parse_dates will raise ValueError if the column is absent
        print(f"ERROR [{label}] Could not parse date column '{date_col}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR [{label}] Could not load file: {e}")
        sys.exit(1)

    if date_col not in df.columns:
        print(f"ERROR [{label}] Expected column '{date_col}' not found. "
              f"Available columns: {list(df.columns)}")
        sys.exit(1)

    # Normalize to date-only (drop any time component) for a clean join key
    df[date_col] = pd.to_datetime(df[date_col]).dt.normalize()

    print(f"[{label}] Loaded {len(df)} rows from '{path}'.")
    print(f"  Date range: {df[date_col].min().date()} to {df[date_col].max().date()}")
    print(f"  Columns: {list(df.columns)}")

    return df


# ---------------------------------------------------------------------------
# Diagnostics before merge
# ---------------------------------------------------------------------------

def report_date_alignment(pjm: pd.DataFrame, weather: pd.DataFrame) -> None:
    """
    Compare date sets between the two datasets and report any mismatches.
    These are dates that will be dropped by the inner join.
    """
    pjm_dates     = set(pjm["date"])
    weather_dates = set(weather["date"])

    only_in_pjm     = sorted(pjm_dates - weather_dates)
    only_in_weather = sorted(weather_dates - pjm_dates)

    if not only_in_pjm and not only_in_weather:
        print("\n  Date alignment: All dates match across both datasets.")
    else:
        if only_in_pjm:
            print(f"\n  WARNING Dates in PJM only (will be dropped by inner join): "
                  f"{len(only_in_pjm)} date(s)")
            for d in only_in_pjm:
                print(f"    {d.date()}")

        if only_in_weather:
            print(f"\n  WARNING Dates in Weather only (will be dropped by inner join): "
                  f"{len(only_in_weather)} date(s)")
            for d in only_in_weather:
                print(f"    {d.date()}")


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------

def merge_datasets(pjm: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """
    Inner join on 'date'. Column name conflicts (excluding 'date') get
    _pjm and _weather suffixes to preserve traceability.
    """
    merged = pd.merge(
        pjm,
        weather,
        on="date",
        how="inner",
        suffixes=("_pjm", "_weather")
    )

    # Sort chronologically
    merged = merged.sort_values("date").reset_index(drop=True)

    return merged


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_row_count(df: pd.DataFrame, expected: int) -> None:
    """
    Warn if the merged row count does not match the expected full-year count.
    Does not exit; the caller decides whether to proceed.
    """
    actual = len(df)
    if actual == expected:
        print(f"  Row count validation PASSED: {actual} rows (expected {expected}).")
    else:
        delta = expected - actual
        print(f"  WARNING Row count validation FAILED: {actual} rows found, "
              f"expected {expected}. {delta} day(s) missing from the merged dataset.")


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def save_csv(df: pd.DataFrame, path: str) -> None:
    """Save merged dataframe to CSV, creating directories as needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        print(f"  Saved {len(df)} rows to '{path}'.")
    except Exception as e:
        print(f"ERROR Could not save merged file: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("merge_data.py -- Dataset Integration Module")
    print("=" * 60)

    # Load both cleaned datasets
    pjm     = load_csv(PJM_INPUT,     label="PJM")
    weather = load_csv(WEATHER_INPUT, label="WEATHER")

    # Report date alignment before merging
    print("\nDate alignment check:")
    report_date_alignment(pjm, weather)

    # Merge
    print("\nMerging datasets on 'date' (inner join)...")
    merged = merge_datasets(pjm, weather)

    # Validate row count
    print("\nValidation:")
    validate_row_count(merged, EXPECTED_ROWS)

    # Report merged columns
    print(f"\nMerged columns ({len(merged.columns)} total):")
    for col in merged.columns:
        print(f"  {col}")

    # Save
    print("\nSaving merged dataset...")
    save_csv(merged, MERGED_OUTPUT)

    print("\n" + "=" * 60)
    print("Merge complete.")
    print(f"  Output: {MERGED_OUTPUT}")
    print(f"  Rows  : {len(merged)}")
    print(f"  Cols  : {len(merged.columns)}")
    print("=" * 60)


if __name__ == "__main__":
    main()