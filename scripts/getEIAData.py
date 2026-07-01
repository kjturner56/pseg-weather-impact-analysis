import requests
import pandas as pd

# ============================================================
# Component 1 - Retrieve PJM Daily Electricity Data from EIA
# ============================================================

# ------------------------------------------------------------------
# EIA API Key
# ------------------------------------------------------------------
API_KEY = "dja9FehbWPywXQODPzn1TBpISa8VUVocadZ8LMHw"

# ------------------------------------------------------------------
# API Endpoint
# ------------------------------------------------------------------
url = "https://api.eia.gov/v2/electricity/rto/daily-region-data/data/"

# ------------------------------------------------------------------
# Query Parameters
# ------------------------------------------------------------------
params = {
    "api_key": API_KEY,
    "frequency": "daily",
    "data[0]": "value",
    "facets[respondent][]": "PJM",
    "facets[timezone][]": "Eastern",
    "start": "2025-01-01",
    "end": "2025-12-31",
    "sort[0][column]": "period",
    "sort[0][direction]": "asc",
    "offset": 0,
    "length": 5000
}

print("Connecting to the EIA API...")

# ------------------------------------------------------------------
# Retrieve Data
# ------------------------------------------------------------------
response = requests.get(url, params=params)

print(f"HTTP Status: {response.status_code}")

if response.status_code != 200:
    print(response.text)
    response.raise_for_status()

# ------------------------------------------------------------------
# Convert JSON to DataFrame
# ------------------------------------------------------------------
json_data = response.json()
data = json_data["response"]["data"]

df = pd.DataFrame(data)

print(f"\nRetrieved {len(df)} records.")

# ------------------------------------------------------------------
# Save Raw Dataset
# ------------------------------------------------------------------
raw_file = "eia_pjm_daily_2025_raw.csv"
df.to_csv(raw_file, index=False)

print(f"Raw dataset saved to: {raw_file}")

# ------------------------------------------------------------------
# Transform Long Format to Wide Format
# ------------------------------------------------------------------
pivot_df = (
    df.pivot(
        index="period",
        columns="type",
        values="value"
    )
    .reset_index()
)

# Rename columns
pivot_df = pivot_df.rename(columns={
    "D": "Demand",
    "DF": "Forecast",
    "NG": "Generation",
    "TI": "Interchange"
})

# ------------------------------------------------------------------
# Data Cleaning
# ------------------------------------------------------------------

# Convert date
pivot_df["period"] = pd.to_datetime(pivot_df["period"])

# Convert numeric columns
numeric_columns = [
    "Demand",
    "Forecast",
    "Generation",
    "Interchange"
]

for column in numeric_columns:
    pivot_df[column] = pd.to_numeric(pivot_df[column])

# Sort chronologically
pivot_df = pivot_df.sort_values("period")

# Rename date column
pivot_df = pivot_df.rename(columns={
    "period": "Date"
})

# ------------------------------------------------------------------
# Save Clean Dataset
# ------------------------------------------------------------------
clean_file = "pjm_daily_2025.csv"

pivot_df.to_csv(clean_file, index=False)

print(f"Clean dataset saved to: {clean_file}")

# ------------------------------------------------------------------
# Display Summary
# ------------------------------------------------------------------
print("\n==============================")
print("DATA SUMMARY")
print("==============================")

print(f"Raw Records: {len(df)}")
print(f"Daily Records: {len(pivot_df)}")

print("\nColumns")
print(pivot_df.columns.tolist())

print("\nFirst Five Records")
print(pivot_df.head())

print("\nData Types")
print(pivot_df.dtypes)

print("\nMissing Values")
print(pivot_df.isnull().sum())

print("\nComponent 1 Complete!")