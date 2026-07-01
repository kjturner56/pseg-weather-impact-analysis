# LLM Prompts Log

This document records all interactions with the LLM used throughout the project. Each entry includes the prompt, its purpose, and how the resulting output was evaluated and incorporated into the project.

---

## Prompt 1 – Pipeline Design Review (Required LLM Use #1)

**Date:** June 29, 2026

### Objective

Review the proposed data analysis pipeline to ensure it satisfies the project requirements and follows good software engineering practices.

### Prompt

Review the proposed pipeline for a project analyzing the relationship between weather conditions and electricity demand within the PJM Interconnection. Suggest improvements to the pipeline design, component organization, data cleaning strategy, and overall workflow.

### Outcome

The recommendations were reviewed and selectively incorporated into the project. Suggestions that improved the organization, modularity, and clarity of the pipeline were adopted, while the overall pipeline design, research direction, and implementation decisions remained under the control of the project author.

### Notes

The LLM was used as a design review and brainstorming tool rather than as the primary designer. Final decisions regarding the pipeline architecture, project organization, data processing strategy, and implementation approach were made by the project author after evaluating the recommendations.

### Validation

**Design Review:** Pass

- The recommendations were reviewed against the project requirements and pipeline objectives.

**Project Alignment:** Pass

- Accepted recommendations improved organization and modularity while preserving the original research direction.

### Reflection

The LLM served as a design review assistant rather than the primary designer. Recommendations were evaluated individually and incorporated only when they aligned with the project objectives, software engineering principles, and course requirements.

---

## Prompt 2 – Clean Data Component

**Date:** June 30, 2026

### Objective

Generate code for the data cleaning component only. This component should prepare the EIA and NOAA CSV files for later merging and analysis.

### Prompt

Create a Python script called clean_data.py for a project analyzing the relationship between PJM electricity demand and Newark weather conditions. The script should only handle data cleaning, not merging, metrics, visualization, or final orchestration.

Inputs:
- data/pjm_daily_2025.csv
- data/newark_weather_2025.csv

Requirements:
- Load both CSV files.
- Convert date fields to datetime.
- Convert numeric fields to numeric data types.
- For NOAA weather data, calculate TAVG as (TMAX + TMIN) / 2 if TAVG is missing or blank.
- Standardize column names.
- Check and report missing values.
- Save cleaned outputs as:
  - data/pjm_daily_2025_clean.csv
  - data/newark_weather_2025_clean.csv

Use pandas. Include clear comments and basic error handling.

### Outcome

The script was generated, reviewed, and tested successfully. It loaded both CSV files, standardized column names, converted dates and numeric fields, calculated missing NOAA average temperature values, reported missing values, sorted both datasets by date, and saved cleaned outputs.

### Notes

The output showed one missing PJM forecast value and 47 missing interchange values. These were not imputed during cleaning because they are not required for the core weather-demand analysis. NOAA TAVG was fully missing, but this was expected and was calculated using TMAX and TMIN.

### Validation

**Syntax:** Pass

- Script executed successfully without runtime errors.

**Semantics:** Pass

- Verified after testing against the project datasets.

**Software Engineering:** Pass

- Reviewed for readability, modularity, variable naming, comments, and basic error handling.

### Reflection

The generated code provided a solid starting point for the component. The implementation was reviewed against the pipeline specification, tested using the project datasets, and accepted after confirming that it produced the expected outputs. Final responsibility for verifying correctness remained with the project author.

---

## Prompt 3 – Merge Data Component

**Date:** July 1, 2026

### Objective

Generate code for the data integration component only. This component should merge the cleaned EIA and NOAA datasets into a single dataset for later analysis.

### Prompt

Create a Python script called `merge_data.py` for a project analyzing the relationship between PJM electricity demand and Newark weather conditions.

This script should only perform dataset integration. Do not include data cleaning, metrics, visualization, dashboard logic, or final orchestration.

Inputs:
- `data/pjm_daily_2025_clean.csv`
- `data/newark_weather_2025_clean.csv`

Output:
- `data/merged_data.csv`

Requirements:
- Use pandas.
- Load both cleaned datasets.
- Merge the datasets using the `date` field with an inner join.
- Verify that the merged dataset contains 365 rows.
- Report any dates that do not successfully merge.
- Display the merged column names.
- Save the merged dataset.
- Include clear comments, basic error handling, and console output confirming the merge results.

Only create `merge_data.py`.

### Outcome

The script was generated, reviewed, and tested successfully. It loaded the cleaned PJM and NOAA datasets, verified date alignment, merged both datasets using an inner join on the date field, validated the expected record count, displayed the merged schema, and saved the merged dataset for downstream analysis.

### Notes

The merge produced the expected 365 records with no unmatched dates between the two datasets. The merged dataset contains electricity demand, forecast, generation, interchange, and weather observations required for subsequent metrics and visualization components.

### Validation

**Syntax:** Pass

- Script executed successfully without runtime errors.

**Semantics:** Pass

- Successfully merged 365 records using an inner join.
- No unmatched dates were detected.
- Saved merged_data.csv with the expected schema.

**Software Engineering:** Pass

- Reviewed for readability, modularity, meaningful variable names, comments, validation messages, and basic error handling.

### Reflection

The generated implementation closely matched the project requirements and required only a review before execution. The component was validated against the pipeline specification and project datasets before being accepted. Final responsibility for verifying correctness remained with the project author.