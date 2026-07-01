"""
clean_data.py
-------------
Data cleaning module for PJM electricity demand and Newark weather analysis.
Scope: loading, standardizing, cleaning, and saving. No merging, metrics, or visualization.

Inputs:
    data/pjm_daily_2025.csv
    data/newark_weather_2025.csv

Outputs:
    data/pjm_daily_2025_clean.csv
    data/newark_weather_2025_clean.csv
"""

import pandas as pd
import os
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = "data"

PJM_INPUT  = os.path.join(DATA_DIR, "pjm_daily_2025.csv")
PJM_OUTPUT = os.path.join(DATA_DIR, "pjm_daily_2025_clean.csv")

WEATHER_INPUT  = os.path.join(DATA_DIR, "newark_weather_2025.csv")
WEATHER_OUTPUT = os.path.join(DATA_DIR, "newark_weather_2025_clean.csv")

# Fields that should be cast to numeric for each dataset
PJM_NUMERIC_FIELDS     = ["demand", "forecast", "generation", "interchange"]
WEATHER_NUMERIC_FIELDS = ["prcp", "tmax", "tmin", "tavg"]


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and lowercase all column names."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def report_missing(df: pd.DataFrame, label: str, stage: str) -> None:
    """Print a missing-value summary for the given dataframe."""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print(f"  [{label} | {stage}] No missing values detected.")
    else:
        print(f"  [{label} | {stage}] Missing values:")
        for col, count in missing.items():
            pct = 100 * count / len(df)
            print(f"    {col}: {count} rows ({pct:.1f}%)")


def to_numeric_coerce(df: pd.DataFrame, fields: list, label: str) -> pd.DataFrame:
    """
    Cast each field to numeric. Values that cannot be converted become NaN.
    Prints a warning for each field where coercion introduced NaNs.
    """
    for field in fields:
        if field not in df.columns:
            print(f"  WARNING [{label}] Expected field '{field}' not found. Skipping.")
            continue
        before_nulls = df[field].isnull().sum()
        df[field] = pd.to_numeric(df[field], errors="coerce")
        after_nulls = df[field].isnull().sum()
        introduced = after_nulls - before_nulls
        if introduced > 0:
            print(f"  WARNING [{label}] '{field}': {introduced} non-numeric value(s) coerced to NaN.")
    return df


# ---------------------------------------------------------------------------
# PJM cleaning
# ---------------------------------------------------------------------------

def clean_pjm(path: str) -> pd.DataFrame:
    """
    Load and clean the PJM daily demand CSV.

    Steps:
      1. Load CSV.
      2. Standardize column names.
      3. Convert date field to datetime.
      4. Convert numeric fields (demand, forecast, generation, interchange).
      5. Report missing values before and after cleaning.
      6. Sort by date ascending.
    """
    label = "PJM"

    # 1. Load
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"ERROR [{label}] File not found: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR [{label}] Could not load file: {e}")
        sys.exit(1)

    print(f"\n[{label}] Loaded {len(df)} rows from '{path}'.")

    # 2. Standardize column names
    df = standardize_columns(df)
    print(f"  Columns after standardization: {list(df.columns)}")

    # 3. Convert date field
    if "date" not in df.columns:
        print(f"ERROR [{label}] 'date' column not found after standardization. "
              f"Available columns: {list(df.columns)}")
        sys.exit(1)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    invalid_dates = df["date"].isnull().sum()
    if invalid_dates > 0:
        print(f"  WARNING [{label}] {invalid_dates} row(s) had unparseable date values.")

    # 4. Report missing BEFORE numeric cleaning
    report_missing(df, label, "before cleaning")

    # 5. Convert numeric fields
    df = to_numeric_coerce(df, PJM_NUMERIC_FIELDS, label)

    # 6. Report missing AFTER numeric cleaning
    report_missing(df, label, "after cleaning")

    # 7. Sort by date
    df = df.sort_values("date").reset_index(drop=True)
    print(f"  [{label}] Sorted by date ascending.")

    return df


# ---------------------------------------------------------------------------
# Weather cleaning
# ---------------------------------------------------------------------------

def clean_weather(path: str) -> pd.DataFrame:
    """
    Load and clean the Newark NOAA daily weather CSV.

    Steps:
      1. Load CSV.
      2. Standardize column names.
      3. Convert date field to datetime.
      4. Convert numeric fields (prcp, tmax, tmin, tavg).
      5. Impute TAVG where missing: TAVG = (TMAX + TMIN) / 2.
      6. Report missing values before and after cleaning.
      7. Sort by date ascending.
    """
    label = "WEATHER"

    # 1. Load
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"ERROR [{label}] File not found: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR [{label}] Could not load file: {e}")
        sys.exit(1)

    print(f"\n[{label}] Loaded {len(df)} rows from '{path}'.")

    # 2. Standardize column names
    df = standardize_columns(df)
    print(f"  Columns after standardization: {list(df.columns)}")

    # 3. Convert date field
    if "date" not in df.columns:
        print(f"ERROR [{label}] 'date' column not found after standardization. "
              f"Available columns: {list(df.columns)}")
        sys.exit(1)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    invalid_dates = df["date"].isnull().sum()
    if invalid_dates > 0:
        print(f"  WARNING [{label}] {invalid_dates} row(s) had unparseable date values.")

    # 4. Report missing BEFORE numeric cleaning
    report_missing(df, label, "before cleaning")

    # 5. Convert numeric fields (including tavg before imputation)
    df = to_numeric_coerce(df, WEATHER_NUMERIC_FIELDS, label)

    # 6. Impute TAVG where missing or blank
    if "tavg" in df.columns:
        tavg_missing_mask = df["tavg"].isnull()
        tavg_missing_count = tavg_missing_mask.sum()

        if tavg_missing_count > 0:
            # Only impute rows where both TMAX and TMIN are available
            can_impute = tavg_missing_mask & df["tmax"].notnull() & df["tmin"].notnull()
            imputed_count = can_impute.sum()

            df.loc[can_impute, "tavg"] = (
                (df.loc[can_impute, "tmax"] + df.loc[can_impute, "tmin"]) / 2
            )

            still_missing = df["tavg"].isnull().sum()
            print(f"  [{label}] TAVG: {tavg_missing_count} missing. "
                  f"Imputed {imputed_count} via (TMAX + TMIN) / 2. "
                  f"{still_missing} remain missing (insufficient TMAX/TMIN).")
        else:
            print(f"  [{label}] TAVG: No missing values. No imputation needed.")
    else:
        print(f"  WARNING [{label}] 'tavg' column not found. Skipping imputation.")

    # 7. Report missing AFTER cleaning and imputation
    report_missing(df, label, "after cleaning")

    # 8. Sort by date
    df = df.sort_values("date").reset_index(drop=True)
    print(f"  [{label}] Sorted by date ascending.")

    return df


# ---------------------------------------------------------------------------
# Save output
# ---------------------------------------------------------------------------

def save_csv(df: pd.DataFrame, path: str, label: str) -> None:
    """Save dataframe to CSV, creating the output directory if needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
        print(f"  [{label}] Saved {len(df)} rows to '{path}'.")
    except Exception as e:
        print(f"ERROR [{label}] Could not save file: {e}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("clean_data.py -- Data Cleaning Module")
    print("=" * 60)

    # Clean PJM dataset
    pjm_clean = clean_pjm(PJM_INPUT)
    save_csv(pjm_clean, PJM_OUTPUT, "PJM")

    # Clean weather dataset
    weather_clean = clean_weather(WEATHER_INPUT)
    save_csv(weather_clean, WEATHER_OUTPUT, "WEATHER")

    print("\n" + "=" * 60)
    print("Cleaning complete.")
    print(f"  PJM output    : {PJM_OUTPUT}")
    print(f"  Weather output: {WEATHER_OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()