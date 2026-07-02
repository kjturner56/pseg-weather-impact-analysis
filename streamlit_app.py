"""
streamlit_app.py
----------------
Dashboard for PSEG Weather Impact Analysis.
Reads existing pipeline outputs only.
No cleaning, merging, metrics calculation, or chart generation.

Inputs (all from completed pipeline):
    output/monthly_summary.csv
    output/category_summary.csv
    output/correlation_summary.csv
    output/metrics_summary.csv
    output/demand_vs_temperature.png
    output/monthly_demand.png
    output/monthly_temperature.png
    output/forecast_error.png
    output/category_comparison.png
"""

import streamlit as st
import pandas as pd
import os


# ---------------------------------------------------------------------------
# Page configuration -- must be first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="PSEG Weather Impact Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

OUTPUT_DIR = "output"

CSV_FILES = {
    "monthly":     os.path.join(OUTPUT_DIR, "monthly_summary.csv"),
    "category":    os.path.join(OUTPUT_DIR, "category_summary.csv"),
    "correlation": os.path.join(OUTPUT_DIR, "correlation_summary.csv"),
    "metrics":     os.path.join(OUTPUT_DIR, "metrics_summary.csv"),
}

IMAGE_FILES = {
    "demand_vs_temperature": os.path.join(OUTPUT_DIR, "demand_vs_temperature.png"),
    "monthly_demand":        os.path.join(OUTPUT_DIR, "monthly_demand.png"),
    "monthly_temperature":   os.path.join(OUTPUT_DIR, "monthly_temperature.png"),
    "forecast_error":        os.path.join(OUTPUT_DIR, "forecast_error.png"),
    "category_comparison":   os.path.join(OUTPUT_DIR, "category_comparison.png"),
}

TEMP_CATEGORY_ORDER = ["Very Cold", "Cold", "Mild", "Warm", "Hot"]


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

def apply_styles() -> None:
    """
    Inject custom CSS.

    Design intent: utility-first dashboard palette built around PJM/energy
    domain conventions. Navy anchor (#0a2342), amber signal (#f5a623) for
    highlights, and a cool slate sidebar. KPI cards use a subtle left-border
    accent instead of colored backgrounds to keep the grid readable at a glance.
    Monospace data labels throughout to keep numeric columns from jumping.
    """
    st.markdown(
        """
        <style>
        /* ---- Global ---------------------------------------------------- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* ---- Page header ------------------------------------------------ */
        .dash-header {
            background: linear-gradient(135deg, #0a2342 0%, #1a3a5c 100%);
            border-radius: 10px;
            padding: 28px 36px 22px 36px;
            margin-bottom: 28px;
        }
        .dash-header h1 {
            color: #ffffff;
            font-size: 1.85rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin: 0 0 6px 0;
        }
        .dash-header p {
            color: #a8c4e0;
            font-size: 0.92rem;
            margin: 0;
            line-height: 1.5;
        }
        .dash-header .badge {
            display: inline-block;
            background: #f5a623;
            color: #0a2342;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            border-radius: 4px;
            padding: 2px 8px;
            margin-bottom: 10px;
        }

        /* ---- KPI cards -------------------------------------------------- */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 28px;
        }
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #f5a623;
            border-radius: 8px;
            padding: 18px 20px 14px 20px;
        }
        .kpi-label {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.6rem;
            font-weight: 700;
            color: #0a2342;
            line-height: 1;
        }
        .kpi-sub {
            font-size: 0.72rem;
            color: #94a3b8;
            margin-top: 5px;
        }

        /* ---- Section labels --------------------------------------------- */
        .section-label {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #f5a623;
            margin-bottom: 6px;
        }
        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0a2342;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e2e8f0;
        }

        /* ---- Chart containers ------------------------------------------- */
        .chart-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
        }
        .chart-title {
            font-size: 0.82rem;
            font-weight: 600;
            color: #475569;
            margin-bottom: 12px;
            letter-spacing: 0.01em;
        }

        /* ---- Correlation badge ------------------------------------------ */
        .corr-row {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 16px;
            border-radius: 6px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            margin-bottom: 8px;
        }
        .corr-field {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            color: #0a2342;
            width: 60px;
        }
        .corr-bar-wrap {
            flex: 1;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
        }
        .corr-bar {
            height: 100%;
            border-radius: 4px;
            background: linear-gradient(90deg, #0a2342, #f5a623);
        }
        .corr-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            font-weight: 700;
            color: #0a2342;
            width: 52px;
            text-align: right;
        }

        /* ---- Missing file notice ---------------------------------------- */
        .missing-notice {
            background: #fef3c7;
            border: 1px solid #f5a623;
            border-left: 4px solid #f5a623;
            border-radius: 6px;
            padding: 14px 18px;
            font-size: 0.85rem;
            color: #78350f;
            margin-bottom: 10px;
        }

        /* ---- Streamlit overrides ---------------------------------------- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            border-bottom: 2px solid #e2e8f0;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px 6px 0 0;
            font-size: 0.83rem;
            font-weight: 600;
            padding: 8px 18px;
            color: #64748b;
        }
        .stTabs [aria-selected="true"] {
            background: #0a2342 !important;
            color: #ffffff !important;
        }
        div[data-testid="stExpander"] summary {
            font-size: 0.85rem;
            font-weight: 600;
            color: #0a2342;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------

def check_files(paths: dict) -> tuple[dict, list]:
    """
    Check which files exist and which are missing.
    Returns a dict of {key: True/False} and a list of missing paths.
    """
    status  = {key: os.path.isfile(path) for key, path in paths.items()}
    missing = [path for key, path in paths.items() if not status[key]]
    return status, missing


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

@st.cache_data
def load_csv(path: str) -> pd.DataFrame | None:
    """Load a CSV with caching. Returns None on failure."""
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Could not load `{path}`: {e}")
        return None


# ---------------------------------------------------------------------------
# KPI computation (display-level only, no new analytical metrics)
# ---------------------------------------------------------------------------

def compute_kpis(metrics: pd.DataFrame) -> dict:
    """
    Derive simple display-level KPIs from the metrics summary CSV.
    All values come directly from the precomputed file.
    """
    kpis = {
        "total_days":        None,
        "avg_demand":        None,
        "avg_temp":          None,
        "avg_forecast_error": None,
    }

    if metrics is None or metrics.empty:
        return kpis

    kpis["total_days"] = len(metrics)

    if "demand" in metrics.columns:
        kpis["avg_demand"] = metrics["demand"].mean()

    if "tavg" in metrics.columns:
        kpis["avg_temp"] = metrics["tavg"].mean()

    if "forecast_error" in metrics.columns:
        kpis["avg_forecast_error"] = metrics["forecast_error"].mean()

    return kpis


# ---------------------------------------------------------------------------
# UI components
# ---------------------------------------------------------------------------

def render_header() -> None:
    st.markdown(
        """
        <div class="dash-header">
            <div class="badge">⚡ Energy Analytics</div>
            <h1>PSEG Weather Impact Analysis</h1>
            <p>
                Analyzing the relationship between PJM electricity demand and
                Newark, NJ weather conditions across 2025. All data sourced from
                EIA demand forecasts and NOAA daily observations.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_missing_notice(missing: list) -> None:
    if not missing:
        return
    paths_html = "".join(f"<li><code>{p}</code></li>" for p in missing)
    st.markdown(
        f"""
        <div class="missing-notice">
            <strong>Pipeline outputs not found.</strong>
            Run the full pipeline before launching this dashboard.<br>
            <ul style="margin: 8px 0 0 0; padding-left: 18px;">{paths_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(kpis: dict) -> None:
    """Render the four KPI cards as a CSS grid."""
    def fmt_number(val, fmt):
        return fmt.format(val) if val is not None else "N/A"

    cards_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">Days Analyzed</div>
            <div class="kpi-value">{fmt_number(kpis["total_days"], "{:,}")}</div>
            <div class="kpi-sub">calendar days in dataset</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Daily Demand</div>
            <div class="kpi-value">{fmt_number(kpis["avg_demand"], "{:,.0f}")}</div>
            <div class="kpi-sub">MWh per day</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Temperature</div>
            <div class="kpi-value">{fmt_number(kpis["avg_temp"], "{:.1f}°F")}</div>
            <div class="kpi-sub">TAVG across all days</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Avg Forecast Error</div>
            <div class="kpi-value">{fmt_number(kpis["avg_forecast_error"], "{:+,.0f}")}</div>
            <div class="kpi-sub">MWh (demand minus forecast)</div>
        </div>
    </div>
    """
    st.markdown(cards_html, unsafe_allow_html=True)


def render_chart(image_path: str, caption: str, img_status: dict, key: str) -> None:
    """Render a PNG chart or a friendly missing-file notice."""
    if img_status.get(key):
        st.image(image_path, width="stretch")
    else:
        st.markdown(
            f'<div class="missing-notice">Chart not found: <code>{image_path}</code></div>',
            unsafe_allow_html=True,
        )


def render_correlation_bars(correlation: pd.DataFrame) -> None:
    """
    Render Pearson correlation values as inline bar rows.
    Visual encoding makes it immediately clear which temperature
    field has the strongest linear relationship with demand.
    """
    if correlation is None or correlation.empty:
        st.info("Correlation data not available.")
        return

    required = ["temperature_field", "pearson_correlation"]
    if not all(col in correlation.columns for col in required):
        st.warning(f"Correlation table missing expected columns: {required}")
        return

    field_labels = {"tavg": "TAVG", "tmax": "TMAX", "tmin": "TMIN"}

    for _, row in correlation.iterrows():
        field = str(row["temperature_field"])
        val   = row["pearson_correlation"]

        try:
            r       = float(val)
            bar_pct = abs(r) * 100
            sign    = "+" if r >= 0 else ""
        except (ValueError, TypeError):
            r       = None
            bar_pct = 0
            sign    = ""

        label    = field_labels.get(field.lower(), field.upper())
        val_str  = f"{sign}{r:.4f}" if r is not None else "N/A"
        n_str    = f"n = {int(row['sample_size'])}" if "sample_size" in row else ""

        st.markdown(
            f"""
            <div class="corr-row">
                <div class="corr-field">{label}</div>
                <div class="corr-bar-wrap">
                    <div class="corr-bar" style="width: {bar_pct:.1f}%;"></div>
                </div>
                <div class="corr-val">{val_str}</div>
                <div style="font-size:0.72rem;color:#94a3b8;width:60px;">{n_str}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_category_table(category: pd.DataFrame) -> None:
    """Display the category summary table with ordered rows."""
    if category is None or category.empty:
        st.info("Category data not available.")
        return

    if "temp_category" in category.columns:
        category = category.copy()
        cat_col  = pd.Categorical(
            category["temp_category"],
            categories=TEMP_CATEGORY_ORDER,
            ordered=True,
        )
        category["temp_category"] = cat_col
        category = category.sort_values("temp_category").reset_index(drop=True)

    st.dataframe(category, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Main dashboard layout
# ---------------------------------------------------------------------------

def main():
    apply_styles()
    render_header()

    # ---- Validate all files before rendering anything data-dependent ----
    csv_status,   csv_missing   = check_files(CSV_FILES)
    img_status,   img_missing   = check_files(IMAGE_FILES)
    all_missing   = csv_missing + img_missing

    if all_missing:
        render_missing_notice(all_missing)

    # ---- Load CSVs (cached) ----
    metrics     = load_csv(CSV_FILES["metrics"])     if csv_status["metrics"]     else None
    monthly     = load_csv(CSV_FILES["monthly"])     if csv_status["monthly"]     else None
    category    = load_csv(CSV_FILES["category"])    if csv_status["category"]    else None
    correlation = load_csv(CSV_FILES["correlation"]) if csv_status["correlation"] else None

    # ---- KPI row ----
    kpis = compute_kpis(metrics)
    render_kpis(kpis)

    # ---- Main content: tabs ----
    st.markdown('<div class="section-label">Analysis</div>', unsafe_allow_html=True)

    tab_demand, tab_temp, tab_error, tab_category, tab_correlation = st.tabs([
        "Demand Overview",
        "Temperature",
        "Forecast Error",
        "Temperature Categories",
        "Correlations",
    ])

    # ---- Tab 1: Demand Overview ----
    with tab_demand:
        st.markdown('<div class="section-title">Electricity Demand</div>', unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1], gap="medium")

        with col_left:
            st.markdown('<div class="chart-title">Daily Demand vs Average Temperature</div>', unsafe_allow_html=True)
            render_chart(
                IMAGE_FILES["demand_vs_temperature"],
                "Each point is one calendar day, color-coded by temperature category.",
                img_status, "demand_vs_temperature",
            )

        with col_right:
            st.markdown('<div class="chart-title">Monthly Average Demand</div>', unsafe_allow_html=True)
            render_chart(
                IMAGE_FILES["monthly_demand"],
                "Average daily demand aggregated by month.",
                img_status, "monthly_demand",
            )

        with st.expander("Monthly summary table"):
            if monthly is not None and not monthly.empty:
                st.dataframe(monthly, use_container_width=True, hide_index=True)
            else:
                st.info("Monthly summary not available.")

    # ---- Tab 2: Temperature ----
    with tab_temp:
        st.markdown('<div class="section-title">Temperature Conditions</div>', unsafe_allow_html=True)

        st.markdown('<div class="chart-title">Monthly Average Temperature (TAVG, TMAX, TMIN)</div>', unsafe_allow_html=True)
        render_chart(
            IMAGE_FILES["monthly_temperature"],
            "Shaded band shows the range between monthly average high and low.",
            img_status, "monthly_temperature",
        )

        with st.expander("Monthly temperature data"):
            if monthly is not None and not monthly.empty:
                temp_cols = [c for c in ["month", "avg_tavg", "avg_tmax", "avg_tmin", "day_count"] if c in monthly.columns]
                st.dataframe(monthly[temp_cols], use_container_width=True, hide_index=True)
            else:
                st.info("Monthly temperature data not available.")

    # ---- Tab 3: Forecast Error ----
    with tab_error:
        st.markdown('<div class="section-title">Forecast Accuracy</div>', unsafe_allow_html=True)

        st.markdown(
            "Forecast error is defined as **demand minus forecast**. "
            "Positive values indicate the actual demand exceeded the forecast (under-forecast). "
            "Negative values indicate the forecast exceeded actual demand (over-forecast)."
        )

        st.markdown('<div class="chart-title">Daily Forecast Error (2025)</div>', unsafe_allow_html=True)
        render_chart(
            IMAGE_FILES["forecast_error"],
            "Red shading: demand exceeded forecast. Blue shading: forecast exceeded demand.",
            img_status, "forecast_error",
        )

        with st.expander("Daily forecast error data"):
            if metrics is not None and not metrics.empty:
                error_cols = [c for c in ["date", "demand", "forecast", "forecast_error", "forecast_error_pct"] if c in metrics.columns]
                st.dataframe(metrics[error_cols].sort_values("date") if "date" in metrics.columns else metrics[error_cols],
                             use_container_width=True, hide_index=True)
            else:
                st.info("Forecast error data not available.")

    # ---- Tab 4: Temperature Categories ----
    with tab_category:
        st.markdown('<div class="section-title">Demand by Temperature Category</div>', unsafe_allow_html=True)

        col_chart, col_table = st.columns([3, 2], gap="medium")

        with col_chart:
            st.markdown('<div class="chart-title">Average Demand by Temperature Category</div>', unsafe_allow_html=True)
            render_chart(
                IMAGE_FILES["category_comparison"],
                "Categories: Very Cold (<32°F), Cold (32–49°F), Mild (50–64°F), Warm (65–79°F), Hot (≥80°F).",
                img_status, "category_comparison",
            )

        with col_table:
            st.markdown('<div class="chart-title">Category Summary</div>', unsafe_allow_html=True)
            render_category_table(category)

    # ---- Tab 5: Correlations ----
    with tab_correlation:
        st.markdown('<div class="section-title">Temperature-Demand Correlations</div>', unsafe_allow_html=True)

        st.markdown(
            "Pearson correlation between daily electricity demand and each temperature measure. "
            "A value near +1 or -1 indicates a strong linear relationship. "
            "Values near 0 indicate little linear association."
        )

        st.markdown("#### Pearson r -- Demand vs Temperature")
        render_correlation_bars(correlation)

        with st.expander("Full correlation table"):
            if correlation is not None and not correlation.empty:
                st.dataframe(correlation, use_container_width=True, hide_index=True)
            else:
                st.info("Correlation data not available.")

        st.markdown("---")
        st.markdown(
            "**Interpretation note.** Pearson r measures linear association only. "
            "The demand-temperature relationship is typically U-shaped (high demand at "
            "both temperature extremes), which can suppress r values even when a strong "
            "real-world relationship exists. Review the scatter plot in the Demand Overview "
            "tab alongside these values."
        )

    # ---- Footer ----
    st.markdown("---")
    st.markdown(
        "<p style='font-size:0.75rem;color:#94a3b8;text-align:center;'>"
        "PSEG Weather Impact Analysis &nbsp;|&nbsp; "
        "Data: EIA (PJM demand) and NOAA (Newark weather) &nbsp;|&nbsp; 2025"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
