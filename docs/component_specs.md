# Component Specifications

---

# clean_data.py

**Status:** Complete

### Purpose

Prepare the EIA and NOAA datasets for analysis.

### Input

- data/pjm_daily_2025.csv
- data/newark_weather_2025.csv

### Output

- data/pjm_daily_2025_clean.csv
- data/newark_weather_2025_clean.csv

### Responsibilities

- Load CSV files
- Convert dates
- Convert numeric fields
- Calculate TAVG
- Report missing values
- Save cleaned datasets

---

# merge_data.py

**Status:** Complete

### Purpose

Merge the cleaned EIA and NOAA datasets.

### Input

- data/pjm_daily_2025_clean.csv
- data/newark_weather_2025_clean.csv

### Output

- data/merged_data.csv

### Responsibilities

- Load cleaned datasets
- Verify date alignment
- Merge on date
- Validate row count
- Save merged dataset

---

# metrics.py

**Status:** In Progress

### Purpose

Calculate analytical metrics used throughout the project.

### Input

- data/merged_data.csv

### Output

- output/monthly_summary.csv
- output/category_summary.csv
- output/correlation_summary.csv
- output/metrics_summary.csv

### Responsibilities

- Calculate forecast error
- Calculate forecast error percentage
- Calculate monthly average demand
- Calculate monthly average temperature
- Calculate Pearson correlations
- Classify temperature categories
- Calculate category statistics
- Calculate Temperature Stress
- Calculate normalized demand
- Save summary tables

### Temperature Categories

- Very Cold: TAVG < 32°F
- Cold: 32°F–49°F
- Mild: 50°F–64°F
- Warm: 65°F–79°F
- Hot: TAVG >= 80°F

### Normalized Metric

- Temperature Stress = abs(TAVG - 65)
- Demand per Degree of Temperature Stress = Demand / Temperature Stress
- Handle zero temperature stress to avoid division by zero

---

# visualize.py

**Status:** Not Started

### Purpose

Generate charts and figures that communicate the analytical results produced by the metrics component.

### Input

- data/merged_data.csv
- output/monthly_summary.csv
- output/category_summary.csv
- output/correlation_summary.csv
- output/metrics_summary.csv

### Output

- output/demand_vs_temperature.png
- output/monthly_demand.png
- output/monthly_temperature.png
- output/forecast_error.png
- output/category_comparison.png

### Responsibilities

- Load summary tables
- Generate labeled charts
- Include titles, axis labels, and legends where appropriate
- Save figures to the output folder

---

# final_project.py

**Status:** Not Started

### Purpose

Execute the complete data analysis pipeline from start to finish.

### Input

- Raw EIA dataset
- Raw NOAA dataset

### Output

- Clean datasets
- Merged dataset
- Summary tables
- Visualizations

### Responsibilities

- Execute clean_data.py
- Execute merge_data.py
- Execute metrics.py
- Execute visualize.py
- Report pipeline completion