"""
final_project.py
----------------
Pipeline orchestration for PJM electricity demand and Newark weather analysis.
Scope: validating component scripts, executing them in sequence, reporting results.

No cleaning, merging, metrics, visualization, or report logic lives here.
Each component script is responsible for its own work.

Component execution order:
    1. scripts/clean_data.py
    2. scripts/merge_data.py
    3. scripts/metrics.py
    4. scripts/visualize.py
"""

import subprocess
import sys
import os
import time


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Component scripts executed in pipeline order
PIPELINE_STEPS = [
    {"label": "Clean Data",    "script": os.path.join("scripts", "clean_data.py")},
    {"label": "Merge Data",    "script": os.path.join("scripts", "merge_data.py")},
    {"label": "Metrics",       "script": os.path.join("scripts", "metrics.py")},
    {"label": "Visualize",     "script": os.path.join("scripts", "visualize.py")},
]

# All files the completed pipeline is expected to produce
EXPECTED_OUTPUTS = [
    # Cleaned datasets
    os.path.join("data",   "pjm_daily_2025_clean.csv"),
    os.path.join("data",   "newark_weather_2025_clean.csv"),
    # Merged dataset
    os.path.join("data",   "merged_data.csv"),
    # Metric summaries
    os.path.join("output", "monthly_summary.csv"),
    os.path.join("output", "category_summary.csv"),
    os.path.join("output", "correlation_summary.csv"),
    os.path.join("output", "metrics_summary.csv"),
    # Charts
    os.path.join("output", "demand_vs_temperature.png"),
    os.path.join("output", "monthly_demand.png"),
    os.path.join("output", "monthly_temperature.png"),
    os.path.join("output", "forecast_error.png"),
    os.path.join("output", "category_comparison.png"),
]

# Separator width for console output formatting
SEPARATOR_WIDTH = 60


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_component_scripts(steps: list) -> None:
    """
    Confirm that every component script file exists before the pipeline starts.
    Reports all missing scripts at once and exits if any are absent.
    This prevents the pipeline from starting and failing mid-run on a missing file.
    """
    missing = [step["script"] for step in steps if not os.path.isfile(step["script"])]

    if missing:
        print("ERROR The following component scripts were not found:")
        for path in missing:
            print(f"  {path}")
        print("\nPipeline aborted. Resolve missing scripts before running.")
        sys.exit(1)

    print("Component script validation passed.")
    for step in steps:
        print(f"  Found: {step['script']}")


def validate_output_files(expected: list) -> bool:
    """
    Check that every expected output file was produced by the pipeline.
    Returns True if all files are present, False if any are missing.
    Prints a full missing-file report before returning.
    """
    missing = [path for path in expected if not os.path.isfile(path)]

    if missing:
        print(f"\nWARNING {len(missing)} expected output file(s) not found:")
        for path in missing:
            print(f"  MISSING: {path}")
        return False

    print(f"\nOutput validation passed. All {len(expected)} expected files present:")
    for path in expected:
        size_kb = os.path.getsize(path) / 1024
        print(f"  {path}  ({size_kb:.1f} KB)")
    return True


# ---------------------------------------------------------------------------
# Step execution
# ---------------------------------------------------------------------------

def run_step(step_number: int, total_steps: int, label: str, script: str) -> None:
    """
    Execute a single pipeline component script using subprocess.run().

    Prints progress banners before and after execution.
    Streams stdout and stderr directly to the console.
    Exits the pipeline with a non-zero status code if the script fails.

    Parameters
    ----------
    step_number : int
        Current step index (1-based) for progress display.
    total_steps : int
        Total number of pipeline steps for progress display.
    label : str
        Human-readable name for this step.
    script : str
        Path to the Python script to execute.
    """
    print(f"\n{'=' * SEPARATOR_WIDTH}")
    print(f"Step {step_number} of {total_steps}: {label}")
    print(f"Script: {script}")
    print("=" * SEPARATOR_WIDTH)

    step_start = time.perf_counter()

    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,   # Stream output directly to console in real time
        text=True,
    )

    elapsed = time.perf_counter() - step_start

    if result.returncode != 0:
        print(f"\nERROR Step {step_number} ({label}) failed with exit code {result.returncode}.")
        print(f"  Script : {script}")
        print(f"  Elapsed: {elapsed:.2f}s")
        print(f"\nPipeline halted at step {step_number}. Subsequent steps were not executed.")
        sys.exit(result.returncode)

    print(f"\nStep {step_number} ({label}) completed successfully in {elapsed:.2f}s.")


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

def run_pipeline(steps: list) -> None:
    """
    Execute all pipeline steps in sequence.
    Stops immediately if any step fails.
    """
    total = len(steps)
    for index, step in enumerate(steps, start=1):
        run_step(
            step_number=index,
            total_steps=total,
            label=step["label"],
            script=step["script"],
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    pipeline_start = time.perf_counter()

    print("=" * SEPARATOR_WIDTH)
    print("final_project.py -- Pipeline Orchestrator")
    print("PJM Electricity Demand and Newark Weather Analysis")
    print("=" * SEPARATOR_WIDTH)

    # Pre-flight: confirm all component scripts are present
    print("\nValidating component scripts...")
    validate_component_scripts(PIPELINE_STEPS)

    # Execute each component script in order
    print(f"\nStarting pipeline ({len(PIPELINE_STEPS)} steps)...")
    run_pipeline(PIPELINE_STEPS)

    # Post-run: confirm all expected outputs were produced
    print("\n" + "=" * SEPARATOR_WIDTH)
    print("Pipeline execution complete. Validating outputs...")
    outputs_valid = validate_output_files(EXPECTED_OUTPUTS)

    # Final status report
    total_elapsed = time.perf_counter() - pipeline_start

    print("\n" + "=" * SEPARATOR_WIDTH)
    if outputs_valid:
        print("PIPELINE COMPLETE -- All steps succeeded. All outputs verified.")
    else:
        print("PIPELINE COMPLETE WITH WARNINGS -- Steps succeeded but outputs are missing.")
        print("Review the warnings above before using pipeline results.")
    print(f"Total execution time: {total_elapsed:.2f}s")
    print("=" * SEPARATOR_WIDTH)

    if not outputs_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()