import pandas as pd
from pathlib import Path

print("Processing hydrological data...")

# Load raw data
df = pd.read_csv("data/raw/hydro_data.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

# Calculate additional features for ML
df['precip_7day'] = df['precipitation_mm'].rolling(7).mean()  # Antecedent precipitation
df['temp_7day'] = df['temperature_c'].rolling(7).mean()       # 7-day avg temp

# Remove NaN from rolling calculations
df = df.dropna()

# Split into calibration and validation
split_date = '2012-01-01'
df_cal = df[df.index < split_date]
df_val = df[df.index >= split_date]

# Save processed data
Path("data/processed").mkdir(parents=True, exist_ok=True)

df.to_csv("data/processed/complete_data.csv")
df_cal.to_csv("data/processed/calibration_data.csv")
df_val.to_csv("data/processed/validation_data.csv")

print(f"\n✓ Processed data saved")
print(f"  Total records: {len(df)}")
print(f"  Calibration: {len(df_cal)} ({df_cal.index.min()} to {df_cal.index.max()})")
print(f"  Validation: {len(df_val)} ({df_val.index.min()} to {df_val.index.max()})")