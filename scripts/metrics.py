"""
metrics.py
----------
Analytical metrics module for PJM electricity demand and Newark weather analysis.
Scope: loading merged data, computing metrics, saving summary tables.
No cleaning, merging, visualization, or orchestration.

Input:
    data/merged_data.csv

Outputs:
    output/monthly_summary.csv
    output/category_summary.csv
    output/correlation_summary.csv
    output/metrics_summary.csv
"""

import pandas as pd
import numpy as np
import os
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MERGED_INPUT = os.path.join("data", "merged_data.csv")

OUTPUT_DIR             = "output"
MONTHLY_OUTPUT         = os.path.join(OUTPUT_DIR, "monthly_summary.csv")
CATEGORY_OUTPUT        = os.path.join(OUTPUT_DIR, "category_summary.csv")
CORRELATION_OUTPUT     = os.path.join(OUTPUT_DIR, "correlation_summary.csv")
METRICS_SUMMARY_OUTPUT = os.path.join(OUTPUT_DIR, "metrics_summary.csv")

# Temperature category bins and labels (Fahrenheit)
TEMP_BINS   = [-np.inf, 32, 50, 65, 80, np.inf]
TEMP_LABELS = ["Very Cold", "Cold", "Mild", "Warm", "Hot"]

# Comfort baseline used for temperature stress calculation
COMFORT_BASELINE_F = 65.0

# Required columns for this module to run
REQUIRED_COLUMNS = ["date", "demand", "forecast", "tavg", "tmax", "tmin"]


# ---------------------------------------------------------------------------
# Load and validate
# ---------------------------------------------------------------------------

def load_merged(path: str) -> pd.DataFrame:
    """
    Load the merged dataset and parse the date column.
    Validates that all required columns are present.
    Exits on file-not-found or missing columns.
    """
    try:
        df = pd.read_csv(path, parse_dates=["date"])
    except FileNotFoundError:
        print(f"ERROR Could not find input file: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR Could not load input file: {e}")
        sys.exit(1)

    # Normalize column names to lowercase for consistent access
    df.columns = df.columns.str.strip().str.lower()

    print(f"[LOAD] {len(df)} rows loaded from '{path}'.")
    print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"  Columns: {list(df.columns)}")

    # Validate required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        print(f"ERROR Missing required columns: {missing_cols}")
        sys.exit(1)

    # Warn on any nulls in key fields before proceeding
    for col in REQUIRED_COLUMNS:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            print(f"  WARNING '{col}' has {null_count} null value(s). "
                  f"Affected rows will produce NaN metrics.")

    return df


# ---------------------------------------------------------------------------
# Forecast error
# ---------------------------------------------------------------------------

def add_forecast_error(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate daily forecast error and forecast error percentage.

    forecast_error     = demand - forecast
    forecast_error_pct = (forecast_error / demand) * 100

    Rows where demand is zero or null produce NaN for the percentage
    to avoid division by zero or misleading results.
    """
    df = df.copy()

    df["forecast_error"] = df["demand"] - df["forecast"]

    # Guard against zero demand before percentage calculation
    df["forecast_error_pct"] = np.where(
        df["demand"].isnull() | (df["demand"] == 0),
        np.nan,
        (df["forecast_error"] / df["demand"]) * 100
    )

    error_rows = df["forecast_error"].notnull().sum()
    print(f"[FORECAST ERROR] Calculated for {error_rows} rows.")

    return df


# ---------------------------------------------------------------------------
# Temperature stress
# ---------------------------------------------------------------------------

def add_temperature_stress(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate temperature stress and demand per degree of temperature stress.

    temperature_stress         = abs(TAVG - 65)
    demand_per_stress_degree   = demand / temperature_stress

    Days where TAVG == 65 (stress == 0) produce NaN for the ratio
    to avoid division by zero. These are true comfort-baseline days
    where the metric is undefined, not a data error.
    """
    df = df.copy()

    df["temperature_stress"] = (df["tavg"] - COMFORT_BASELINE_F).abs()

    # Use NaN where stress is zero to avoid division by zero
    df["demand_per_stress_degree"] = np.where(
        df["temperature_stress"].isnull() | (df["temperature_stress"] == 0),
        np.nan,
        df["demand"] / df["temperature_stress"]
    )

    zero_stress_days = (df["temperature_stress"] == 0).sum()
    if zero_stress_days > 0:
        print(f"[TEMP STRESS] {zero_stress_days} day(s) with TAVG == 65°F "
              f"set to NaN for demand_per_stress_degree (undefined at baseline).")

    return df


# ---------------------------------------------------------------------------
# Temperature category classification
# ---------------------------------------------------------------------------

def add_temperature_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify each day into a temperature category based on TAVG (Fahrenheit).

    Very Cold : TAVG < 32
    Cold      : 32 <= TAVG < 50
    Mild      : 50 <= TAVG < 65
    Warm      : 65 <= TAVG < 80
    Hot       : TAVG >= 80

    Rows with null TAVG are classified as NaN and excluded from category summaries.
    """
    df = df.copy()

    df["temp_category"] = pd.cut(
        df["tavg"],
        bins=TEMP_BINS,
        labels=TEMP_LABELS,
        right=False       # intervals are [left, right)
    )

    print(f"[TEMP CATEGORY] Distribution:")
    counts = df["temp_category"].value_counts().reindex(TEMP_LABELS, fill_value=0)
    for category, count in counts.items():
        print(f"    {category}: {count} day(s)")

    uncategorized = df["temp_category"].isnull().sum()
    if uncategorized > 0:
        print(f"  WARNING {uncategorized} row(s) could not be categorized (null TAVG).")

    return df


# ---------------------------------------------------------------------------
# Monthly summary
# ---------------------------------------------------------------------------

def compute_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate key metrics by calendar month.

    Columns produced:
        year, month, avg_demand, avg_forecast_error,
        avg_forecast_error_pct, avg_tavg, avg_tmax, avg_tmin, day_count
    """
    df = df.copy()
    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month

    monthly = (
        df.groupby(["year", "month"], sort=True)
        .agg(
            avg_demand              = ("demand",              "mean"),
            avg_forecast_error      = ("forecast_error",      "mean"),
            avg_forecast_error_pct  = ("forecast_error_pct",  "mean"),
            avg_tavg                = ("tavg",                "mean"),
            avg_tmax                = ("tmax",                "mean"),
            avg_tmin                = ("tmin",                "mean"),
            day_count               = ("date",                "count"),
        )
        .reset_index()
    )

    # Round for readability
    numeric_cols = [
        "avg_demand", "avg_forecast_error", "avg_forecast_error_pct",
        "avg_tavg", "avg_tmax", "avg_tmin"
    ]
    monthly[numeric_cols] = monthly[numeric_cols].round(2)

    print(f"[MONTHLY SUMMARY] {len(monthly)} month(s) computed.")
    return monthly


# ---------------------------------------------------------------------------
# Category summary
# ---------------------------------------------------------------------------

def compute_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate demand and forecast error statistics by temperature category.

    Columns produced:
        temp_category, day_count, avg_demand,
        avg_forecast_error, avg_forecast_error_pct
    """
    category = (
        df.groupby("temp_category", observed=True, sort=False)
        .agg(
            day_count               = ("date",                "count"),
            avg_demand              = ("demand",              "mean"),
            avg_forecast_error      = ("forecast_error",      "mean"),
            avg_forecast_error_pct  = ("forecast_error_pct",  "mean"),
        )
        .reset_index()
    )

    # Reorder rows to match logical temperature progression
    category["temp_category"] = pd.Categorical(
        category["temp_category"], categories=TEMP_LABELS, ordered=True
    )
    category = category.sort_values("temp_category").reset_index(drop=True)

    numeric_cols = ["avg_demand", "avg_forecast_error", "avg_forecast_error_pct"]
    category[numeric_cols] = category[numeric_cols].round(2)

    print(f"[CATEGORY SUMMARY] {len(category)} category(ies) computed.")
    return category


# ---------------------------------------------------------------------------
# Correlation summary
# ---------------------------------------------------------------------------

def compute_correlation_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Pearson correlations between demand and each temperature field.

    Columns produced:
        temperature_field, pearson_correlation, sample_size
    """
    temp_fields = ["tavg", "tmax", "tmin"]
    records = []

    for field in temp_fields:
        # Drop rows where either column is null before computing correlation
        pair = df[["demand", field]].dropna()
        n    = len(pair)

        if n < 2:
            print(f"  WARNING Not enough data to correlate demand with '{field}' "
                  f"({n} valid rows). Skipping.")
            corr = np.nan
        else:
            corr = pair["demand"].corr(pair[field], method="pearson")

        records.append({
            "temperature_field":   field,
            "pearson_correlation": round(corr, 4) if not np.isnan(corr) else np.nan,
            "sample_size":         n,
        })

        print(f"  Demand vs {field}: r = {corr:.4f} (n = {n})")

    correlation_df = pd.DataFrame(records)
    print(f"[CORRELATION] {len(correlation_df)} correlation(s) computed.")
    return correlation_df


# ---------------------------------------------------------------------------
# Metrics summary (row-level derived fields for downstream use)
# ---------------------------------------------------------------------------

def compute_metrics_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Produce a flat, row-level summary of all derived metrics.
    Useful as a single enriched dataset for downstream steps.

    Columns included:
        date, demand, forecast, forecast_error, forecast_error_pct,
        tavg, tmax, tmin, temp_category,
        temperature_stress, demand_per_stress_degree
    """
    output_cols = [
        "date",
        "demand",
        "forecast",
        "forecast_error",
        "forecast_error_pct",
        "tavg",
        "tmax",
        "tmin",
        "temp_category",
        "temperature_stress",
        "demand_per_stress_degree",
    ]

    # Only include columns that were successfully created
    available_cols = [col for col in output_cols if col in df.columns]
    missing_from_output = set(output_cols) - set(available_cols)
    if missing_from_output:
        print(f"  WARNING These expected metrics columns are absent and will be "
              f"excluded from metrics_summary: {sorted(missing_from_output)}")

    summary = df[available_cols].copy()

    # Round float columns for readability
    float_cols = summary.select_dtypes(include="float64").columns
    summary[float_cols] = summary[float_cols].round(4)

    print(f"[METRICS SUMMARY] {len(summary)} rows, {len(summary.columns)} columns.")
    return summary


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

def save_csv(df: pd.DataFrame, path: str, label: str) -> None:
    """Save a dataframe to CSV, creating the output directory if needed."""
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
    print("metrics.py -- Analytical Metrics Module")
    print("=" * 60)

    # Load merged dataset
    print("\nLoading merged dataset...")
    df = load_merged(MERGED_INPUT)

    # Compute derived daily fields
    print("\nCalculating forecast error...")
    df = add_forecast_error(df)

    print("\nCalculating temperature stress...")
    df = add_temperature_stress(df)

    print("\nClassifying temperature categories...")
    df = add_temperature_category(df)

    # Compute summary tables
    print("\nComputing monthly summary...")
    monthly_summary = compute_monthly_summary(df)

    print("\nComputing category summary...")
    category_summary = compute_category_summary(df)

    print("\nComputing correlations...")
    correlation_summary = compute_correlation_summary(df)

    print("\nAssembling metrics summary...")
    metrics_summary = compute_metrics_summary(df)

    # Save all outputs
    print("\nSaving outputs...")
    save_csv(monthly_summary,     MONTHLY_OUTPUT,         "MONTHLY")
    save_csv(category_summary,    CATEGORY_OUTPUT,        "CATEGORY")
    save_csv(correlation_summary, CORRELATION_OUTPUT,     "CORRELATION")
    save_csv(metrics_summary,     METRICS_SUMMARY_OUTPUT, "METRICS")

    print("\n" + "=" * 60)
    print("Metrics complete.")
    print(f"  Monthly summary     : {MONTHLY_OUTPUT}")
    print(f"  Category summary    : {CATEGORY_OUTPUT}")
    print(f"  Correlation summary : {CORRELATION_OUTPUT}")
    print(f"  Metrics summary     : {METRICS_SUMMARY_OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()