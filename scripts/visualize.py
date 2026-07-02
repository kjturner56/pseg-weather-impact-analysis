"""
visualize.py
------------
Chart generation module for PJM electricity demand and Newark weather analysis.
Scope: loading precomputed CSVs, generating charts, saving as PNG files.
No cleaning, merging, metrics calculation, or dashboard logic.

Inputs:
    data/merged_data.csv
    output/monthly_summary.csv
    output/category_summary.csv
    output/correlation_summary.csv
    output/metrics_summary.csv

Outputs:
    output/demand_vs_temperature.png
    output/monthly_demand.png
    output/monthly_temperature.png
    output/forecast_error.png
    output/category_comparison.png
"""

# Use the non-interactive Agg backend before importing pyplot.
# This allows the script to run in environments with no graphical display.
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import os
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_DIR = "output"

# Input files
MERGED_INPUT      = os.path.join("data",    "merged_data.csv")
MONTHLY_INPUT     = os.path.join(OUTPUT_DIR, "monthly_summary.csv")
CATEGORY_INPUT    = os.path.join(OUTPUT_DIR, "category_summary.csv")
CORRELATION_INPUT = os.path.join(OUTPUT_DIR, "correlation_summary.csv")
METRICS_INPUT     = os.path.join(OUTPUT_DIR, "metrics_summary.csv")

# Output files
DEMAND_VS_TEMP_OUTPUT   = os.path.join(OUTPUT_DIR, "demand_vs_temperature.png")
MONTHLY_DEMAND_OUTPUT   = os.path.join(OUTPUT_DIR, "monthly_demand.png")
MONTHLY_TEMP_OUTPUT     = os.path.join(OUTPUT_DIR, "monthly_temperature.png")
FORECAST_ERROR_OUTPUT   = os.path.join(OUTPUT_DIR, "forecast_error.png")
CATEGORY_COMPARE_OUTPUT = os.path.join(OUTPUT_DIR, "category_comparison.png")

# Chart style defaults
FIGURE_SIZE_WIDE   = (12, 5)
FIGURE_SIZE_SQUARE = (8, 6)
DPI                = 150

# Temperature category order for consistent bar chart sequencing
TEMP_CATEGORY_ORDER = ["Very Cold", "Cold", "Mild", "Warm", "Hot"]

# Color palette keyed by temperature category
TEMP_CATEGORY_COLORS = {
    "Very Cold": "#4393c3",
    "Cold":      "#92c5de",
    "Mild":      "#a6d96a",
    "Warm":      "#fdae61",
    "Hot":       "#d73027",
}


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------

def validate_input_files(paths: list) -> None:
    """
    Check that all required input files exist before loading any of them.
    Reports all missing files at once and exits if any are absent.
    """
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        print("ERROR The following required input files were not found:")
        for path in missing:
            print(f"  {path}")
        sys.exit(1)
    print("[VALIDATION] All required input files found.")


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_csv(path: str, label: str, date_cols: list = None) -> pd.DataFrame:
    """Load a CSV file with optional date parsing and basic confirmation."""
    try:
        kwargs = {"parse_dates": date_cols} if date_cols else {}
        df = pd.read_csv(path, **kwargs)
    except Exception as e:
        print(f"ERROR [{label}] Could not load '{path}': {e}")
        sys.exit(1)

    df.columns = df.columns.str.strip().str.lower()
    print(f"[{label}] Loaded {len(df)} rows from '{path}'.")
    return df


# ---------------------------------------------------------------------------
# Save helper
# ---------------------------------------------------------------------------

def save_figure(path: str, label: str) -> None:
    """
    Apply tight layout, save the current figure, and close it.
    Always closes the figure even if saving fails to prevent resource leaks.
    """
    try:
        plt.tight_layout()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        plt.savefig(path, dpi=DPI, bbox_inches="tight")
        print(f"  [{label}] Saved to '{path}'.")
    except Exception as e:
        print(f"ERROR [{label}] Could not save figure: {e}")
    finally:
        plt.close()


# ---------------------------------------------------------------------------
# Chart 1: Scatter -- Demand vs Average Temperature
# ---------------------------------------------------------------------------

def chart_demand_vs_temperature(metrics: pd.DataFrame) -> None:
    """
    Scatter plot of daily electricity demand against average temperature (TAVG).
    Each point represents one day. Color-coded by temperature category
    where available, grey otherwise.

    Source: metrics_summary.csv
    Output: output/demand_vs_temperature.png
    """
    required = ["tavg", "demand"]
    missing  = [col for col in required if col not in metrics.columns]
    if missing:
        print(f"  WARNING [DEMAND VS TEMP] Missing columns {missing}. Skipping chart.")
        return

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)

    # Plot by category if the column exists; fall back to a single color
    if "temp_category" in metrics.columns:
        for category in TEMP_CATEGORY_ORDER:
            subset = metrics[metrics["temp_category"] == category]
            if subset.empty:
                continue
            ax.scatter(
                subset["tavg"],
                subset["demand"],
                label=category,
                color=TEMP_CATEGORY_COLORS.get(category, "#888888"),
                alpha=0.65,
                s=30,
                edgecolors="none",
            )
        ax.legend(title="Temperature Category", loc="upper left", fontsize=9)
    else:
        ax.scatter(
            metrics["tavg"],
            metrics["demand"],
            color="#4393c3",
            alpha=0.65,
            s=30,
            edgecolors="none",
        )

    ax.set_title("Daily Electricity Demand vs Average Temperature (2025)", fontsize=13)
    ax.set_xlabel("Average Temperature (°F)", fontsize=11)
    ax.set_ylabel("Electricity Demand (MWh)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)

    save_figure(DEMAND_VS_TEMP_OUTPUT, "DEMAND VS TEMP")


# ---------------------------------------------------------------------------
# Chart 2: Line -- Monthly Average Demand
# ---------------------------------------------------------------------------

def chart_monthly_demand(monthly: pd.DataFrame) -> None:
    """
    Line chart of monthly average electricity demand across the year.

    Source: monthly_summary.csv
    Output: output/monthly_demand.png
    """
    required = ["month", "avg_demand"]
    missing  = [col for col in required if col not in monthly.columns]
    if missing:
        print(f"  WARNING [MONTHLY DEMAND] Missing columns {missing}. Skipping chart.")
        return

    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)

    ax.plot(
        monthly["month"],
        monthly["avg_demand"],
        marker="o",
        linewidth=2,
        markersize=6,
        color="#2166ac",
        label="Avg Demand",
    )

    # Annotate each data point with its value
    for _, row in monthly.iterrows():
        ax.annotate(
            f"{row['avg_demand']:,.0f}",
            xy=(row["month"], row["avg_demand"]),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            color="#2166ac",
        )

    ax.set_title("Monthly Average Electricity Demand (2025)", fontsize=13)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Average Demand (MWh)", fontsize=11)
    ax.set_xticks(monthly["month"])
    ax.set_xticklabels(
        [month_labels[int(m) - 1] for m in monthly["month"]],
        fontsize=9
    )
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}")
    )
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=9)

    save_figure(MONTHLY_DEMAND_OUTPUT, "MONTHLY DEMAND")


# ---------------------------------------------------------------------------
# Chart 3: Line -- Monthly Average Temperature
# ---------------------------------------------------------------------------

def chart_monthly_temperature(monthly: pd.DataFrame) -> None:
    """
    Line chart of monthly average TAVG, TMAX, and TMIN across the year.
    Plots all three temperature series where available.

    Source: monthly_summary.csv
    Output: output/monthly_temperature.png
    """
    required = ["month", "avg_tavg"]
    missing  = [col for col in required if col not in monthly.columns]
    if missing:
        print(f"  WARNING [MONTHLY TEMP] Missing columns {missing}. Skipping chart.")
        return

    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)

    # Define each temperature series: (column, display label, color)
    series_config = [
        ("avg_tmax", "Avg High (TMAX)", "#d73027"),
        ("avg_tavg", "Avg Temp (TAVG)", "#f46d43"),
        ("avg_tmin", "Avg Low (TMIN)",  "#4393c3"),
    ]

    for col, label, color in series_config:
        if col not in monthly.columns:
            print(f"  WARNING [MONTHLY TEMP] Column '{col}' not found. Skipping series.")
            continue
        ax.plot(
            monthly["month"],
            monthly[col],
            marker="o",
            linewidth=2,
            markersize=5,
            color=color,
            label=label,
        )

    # Shade the band between TMIN and TMAX for visual context
    if "avg_tmin" in monthly.columns and "avg_tmax" in monthly.columns:
        ax.fill_between(
            monthly["month"],
            monthly["avg_tmin"],
            monthly["avg_tmax"],
            alpha=0.08,
            color="#f46d43",
        )

    ax.axhline(y=32, color="#888888", linestyle=":", linewidth=1, label="Freezing (32°F)")
    ax.axhline(y=65, color="#a6d96a", linestyle=":", linewidth=1, label="Comfort baseline (65°F)")

    ax.set_title("Monthly Average Temperature (2025)", fontsize=13)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Temperature (°F)", fontsize=11)
    ax.set_xticks(monthly["month"])
    ax.set_xticklabels(
        [month_labels[int(m) - 1] for m in monthly["month"]],
        fontsize=9
    )
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=9)

    save_figure(MONTHLY_TEMP_OUTPUT, "MONTHLY TEMP")


# ---------------------------------------------------------------------------
# Chart 4: Line -- Daily Forecast Error
# ---------------------------------------------------------------------------

def chart_forecast_error(metrics: pd.DataFrame) -> None:
    """
    Line chart of daily forecast error (demand minus forecast) across the year.
    A horizontal zero line separates over-forecasts from under-forecasts.
    The area above/below zero is shaded to make the direction visible at a glance.

    Source: metrics_summary.csv
    Output: output/forecast_error.png
    """
    required = ["date", "forecast_error"]
    missing  = [col for col in required if col not in metrics.columns]
    if missing:
        print(f"  WARNING [FORECAST ERROR] Missing columns {missing}. Skipping chart.")
        return

    # Sort by date for a clean time-series line
    plot_data = metrics[["date", "forecast_error"]].dropna().sort_values("date")

    if plot_data.empty:
        print("  WARNING [FORECAST ERROR] No valid data after dropping nulls. Skipping chart.")
        return

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)

    ax.plot(
        plot_data["date"],
        plot_data["forecast_error"],
        linewidth=1,
        color="#4d4d4d",
        alpha=0.8,
        label="Forecast Error (Demand - Forecast)",
    )

    # Shade positive errors (under-forecast) and negative errors (over-forecast)
    ax.fill_between(
        plot_data["date"],
        plot_data["forecast_error"],
        0,
        where=(plot_data["forecast_error"] >= 0),
        alpha=0.3,
        color="#d73027",
        label="Under-forecast (demand exceeded forecast)",
    )
    ax.fill_between(
        plot_data["date"],
        plot_data["forecast_error"],
        0,
        where=(plot_data["forecast_error"] < 0),
        alpha=0.3,
        color="#4393c3",
        label="Over-forecast (forecast exceeded demand)",
    )

    ax.axhline(y=0, color="#333333", linewidth=0.8, linestyle="--")

    ax.set_title("Daily Electricity Forecast Error (2025)", fontsize=13)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Forecast Error (MWh)", fontsize=11)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}")
    )
    fig.autofmt_xdate(rotation=30, ha="right")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=9)

    save_figure(FORECAST_ERROR_OUTPUT, "FORECAST ERROR")


# ---------------------------------------------------------------------------
# Chart 5: Bar -- Average Demand by Temperature Category
# ---------------------------------------------------------------------------

def chart_category_comparison(category: pd.DataFrame) -> None:
    """
    Horizontal bar chart of average electricity demand by temperature category.
    Categories are ordered from Very Cold to Hot.
    Bars are color-coded to match the scatter plot palette.

    Source: category_summary.csv
    Output: output/category_comparison.png
    """
    required = ["temp_category", "avg_demand"]
    missing  = [col for col in required if col not in category.columns]
    if missing:
        print(f"  WARNING [CATEGORY COMPARE] Missing columns {missing}. Skipping chart.")
        return

    # Reorder to match logical temperature progression
    category = category.copy()
    category["temp_category"] = pd.Categorical(
        category["temp_category"],
        categories=TEMP_CATEGORY_ORDER,
        ordered=True,
    )
    category = category.sort_values("temp_category").reset_index(drop=True)

    if category.empty:
        print("  WARNING [CATEGORY COMPARE] No data after ordering. Skipping chart.")
        return

    colors = [
        TEMP_CATEGORY_COLORS.get(cat, "#888888")
        for cat in category["temp_category"]
    ]

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_SQUARE)

    bars = ax.barh(
        category["temp_category"],
        category["avg_demand"],
        color=colors,
        edgecolor="white",
        height=0.55,
    )

    # Label each bar with the demand value and day count
    for bar, (_, row) in zip(bars, category.iterrows()):
        days_label = f"  {row['avg_demand']:,.0f} MWh"
        if "day_count" in row:
            days_label += f"  ({int(row['day_count'])} days)"
        ax.text(
            bar.get_width() + (category["avg_demand"].max() * 0.005),
            bar.get_y() + bar.get_height() / 2,
            days_label,
            va="center",
            fontsize=9,
            color="#333333",
        )

    ax.set_title("Average Electricity Demand by Temperature Category (2025)", fontsize=13)
    ax.set_xlabel("Average Demand (MWh)", fontsize=11)
    ax.set_ylabel("Temperature Category", fontsize=11)
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}")
    )

    # Add a small buffer on the right so bar labels do not clip
    x_max = category["avg_demand"].max()
    ax.set_xlim(0, x_max * 1.25)
    ax.grid(True, axis="x", linestyle="--", alpha=0.4)
    ax.invert_yaxis()  # Very Cold at top, Hot at bottom

    save_figure(CATEGORY_COMPARE_OUTPUT, "CATEGORY COMPARE")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("visualize.py -- Chart Generation Module")
    print("=" * 60)

    # Validate all required input files before attempting any loads
    required_inputs = [
        MERGED_INPUT,
        MONTHLY_INPUT,
        CATEGORY_INPUT,
        CORRELATION_INPUT,
        METRICS_INPUT,
    ]
    validate_input_files(required_inputs)

    # Load required datasets
    print("\nLoading input files...")
    monthly  = load_csv(MONTHLY_INPUT,  label="MONTHLY",  date_cols=None)
    category = load_csv(CATEGORY_INPUT, label="CATEGORY", date_cols=None)
    metrics  = load_csv(METRICS_INPUT,  label="METRICS",  date_cols=["date"])

    # Generate charts
    print("\nGenerating charts...")

    print("\n  Chart 1: Demand vs Average Temperature (scatter)")
    chart_demand_vs_temperature(metrics)

    print("\n  Chart 2: Monthly Average Demand (line)")
    chart_monthly_demand(monthly)

    print("\n  Chart 3: Monthly Average Temperature (line)")
    chart_monthly_temperature(monthly)

    print("\n  Chart 4: Daily Forecast Error (line)")
    chart_forecast_error(metrics)

    print("\n  Chart 5: Average Demand by Temperature Category (bar)")
    chart_category_comparison(category)

    print("\n" + "=" * 60)
    print("Visualization complete.")
    print(f"  demand_vs_temperature : {DEMAND_VS_TEMP_OUTPUT}")
    print(f"  monthly_demand        : {MONTHLY_DEMAND_OUTPUT}")
    print(f"  monthly_temperature   : {MONTHLY_TEMP_OUTPUT}")
    print(f"  forecast_error        : {FORECAST_ERROR_OUTPUT}")
    print(f"  category_comparison   : {CATEGORY_COMPARE_OUTPUT}")
    print("=" * 60)


if __name__ == "__main__":
    main()