import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gr4j_model import GR4J, calculate_nse

print("=" * 60)
print("VALIDATING GR4J MODEL")
print("=" * 60)

# Load calibrated parameters
params = pd.read_csv("data/processed/calibrated_parameters.csv")
X1 = params[params['parameter'] == 'X1']['value'].values[0]
X2 = params[params['parameter'] == 'X2']['value'].values[0]
X3 = params[params['parameter'] == 'X3']['value'].values[0]
X4 = params[params['parameter'] == 'X4']['value'].values[0]

print(f"\nUsing calibrated parameters:")
print(f"  X1 = {X1:.2f} mm")
print(f"  X2 = {X2:.2f} mm")
print(f"  X3 = {X3:.2f} mm")
print(f"  X4 = {X4:.2f} days")

# Load validation data
df_val = pd.read_csv("data/processed/validation_data.csv", parse_dates=['date'], index_col='date')

# Prepare inputs
precip = df_val['precipitation_mm'].values
temp = df_val['temperature_c'].values
evap = 0.0023 * (temp + 17.8) * np.sqrt(np.abs(temp - (-5))) * 2.5
evap = np.maximum(evap, 0)

# Observed flow
basin_area_km2 = 2000
cfs_to_mm = 86400 / (basin_area_km2 * 1e6) * 0.0283168 * 1000
obs_flow = df_val['streamflow_cfs'].values * cfs_to_mm

# Run model
model = GR4J(X1=X1, X2=X2, X3=X3, X4=X4)
sim_flow = model.run(precip, evap)

# Calculate metrics
nse = calculate_nse(obs_flow, sim_flow)
rmse = np.sqrt(np.mean((obs_flow - sim_flow)**2))
bias = np.mean(sim_flow - obs_flow)

print(f"\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)
print(f"\nPerformance Metrics:")
print(f"  NSE:  {nse:.3f}")
print(f"  RMSE: {rmse:.3f} mm/day")
print(f"  Bias: {bias:.3f} mm/day")

# Save results
results = pd.DataFrame({
    'date': df_val.index,
    'observed': obs_flow,
    'simulated': sim_flow,
    'precipitation': precip
})
results.to_csv("data/processed/validation_results.csv", index=False)

print(f"\n✓ Saved results to data/processed/validation_results.csv")

# Create plot
plt.figure(figsize=(12, 6))
plt.plot(df_val.index, obs_flow, label='Observed', linewidth=1.5, alpha=0.7)
plt.plot(df_val.index, sim_flow, label='Simulated', linewidth=1.5, alpha=0.7)
plt.xlabel('Date')
plt.ylabel('Streamflow (mm/day)')
plt.title(f'GR4J Model Validation (NSE = {nse:.3f})')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('data/processed/validation_plot.png', dpi=150)

print(f"✓ Saved plot to data/processed/validation_plot.png")
print("\nValidation complete!")