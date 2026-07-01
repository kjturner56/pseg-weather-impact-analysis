# PSEG Weather Impact Analysis

## Overview

This project analyzes the relationship between weather conditions and electricity demand within the PJM Interconnection using data from the U.S. Energy Information Administration (EIA) and the National Oceanic and Atmospheric Administration (NOAA).

The project implements an AI-assisted data analysis pipeline that cleans, integrates, analyzes, and visualizes electricity and weather data to provide operational insights relevant to utility companies such as PSEG.

---

## Project Structure

```
FINAL_PROJECT/
│
├── data/
│   ├── eia_pjm_daily_2025_raw.csv
│   ├── pjm_daily_2025.csv
│   └── newark_weather_2025.csv
│
├── docs/
│   ├── Final_Project_Report.docx
│   ├── pipeline.md
│   └── prompts.md
│
├── output/
│
├── scripts/
│   ├── clean_data.py
│   ├── getEIAData.py
│   ├── merge_data.py
│   ├── metrics.py
│   └── visualize.py
│
└── final_project.py
```

---

## Script Descriptions

### getEIAData.py

**Purpose**

One-time utility script used to retrieve electricity data from the EIA Open Data API.

**Output**

- eia_pjm_daily_2025_raw.csv
- pjm_daily_2025.csv

---

### clean_data.py

**Purpose**

Prepares both datasets for analysis.

**Inputs**

- pjm_daily_2025.csv
- newark_weather_2025.csv

**Tasks**

- Convert date fields
- Convert numeric fields
- Calculate average temperature (TAVG)
- Handle missing values
- Standardize column names

**Output**

- Cleaned EIA dataset
- Cleaned NOAA dataset

---

### merge_data.py

**Purpose**

Combines the cleaned electricity and weather datasets.

**Inputs**

- Clean EIA dataset
- Clean NOAA dataset

**Task**

- Merge datasets on Date

**Output**

- merged_data.csv

---

### metrics.py

**Purpose**

Calculates analytical metrics used throughout the project.

**Input**

- merged_data.csv

**Calculations**

- Daily demand
- Monthly average demand
- Forecast error
- Average temperature
- Correlation coefficients
- Normalized metrics

**Output**

- Metrics tables

---

### visualize.py

**Purpose**

Creates visualizations used in the final report.

**Input**

- merged_data.csv

**Output**

Charts saved to the **output/** folder.

Examples include:

- demand_vs_temperature.png
- monthly_demand.png
- forecast_error.png
- correlation_heatmap.png

---

### final_project.py

**Purpose**

Main application that executes the complete analysis pipeline.

**Pipeline**

```
Load Data
      ↓
Clean Data
      ↓
Merge Data
      ↓
Generate Metrics
      ↓
Create Visualizations
      ↓
Save Results
```

---

## Data Sources

- U.S. Energy Information Administration (EIA)
- National Oceanic and Atmospheric Administration (NOAA)

---

## Research Question

**How do extreme weather conditions influence electricity demand within the PJM Interconnection, and what operational insights can PSEG derive to improve energy planning?**

## AI-Assisted Development Process

Each component of the pipeline was developed independently using an AI-assisted workflow:

1. Define the component
2. Generate one component using an LLM
3. Review the generated code
4. Test the component
5. Validate syntax, semantics, and software engineering quality
6. Document the prompt and development notes
7. Integrate only after successful validation

This approach follows the course guidance for responsible AI-assisted software development.