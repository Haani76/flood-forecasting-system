import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution
from gr4j_model import GR4J, calculate_nse

print("=" * 60)
print("CALIBRATING GR4J MODEL")
print("=" * 60)

# Load calibration data
df = pd.read_csv("data/processed/calibration_data.csv", parse_dates=['date'], index_col='date')

# Prepare inputs
precip = df['precipitation_mm'].values
temp = df['temperature_c'].values
evap = 0.0023 * (temp + 17.8) * np.sqrt(np.abs(temp - (-5))) * 2.5
evap = np.maximum(evap, 0)

# Observed streamflow
basin_area_km2 = 2000
cfs_to_mm = 86400 / (basin_area_km2 * 1e6) * 0.0283168 * 1000
obs_flow = df['streamflow_cfs'].values * cfs_to_mm

# Objective function to minimize (negative NSE)
def objective(params):
    X1, X2, X3, X4 = params
    
    model = GR4J(X1=X1, X2=X2, X3=X3, X4=X4)
    sim_flow = model.run(precip, evap)
    
    nse = calculate_nse(obs_flow, sim_flow)
    
    return -nse  # Minimize negative NSE = maximize NSE

# Parameter bounds
bounds = [
    (100, 1200),   # X1: Production store capacity
    (-5, 3),       # X2: Groundwater exchange
    (20, 300),     # X3: Routing store capacity
    (1.1, 2.9)     # X4: Unit hydrograph time base
]

print("\nStarting optimization...")
print("This will take 2-3 minutes...\n")

# Run optimization
result = differential_evolution(
    objective,
    bounds,
    maxiter=50,
    popsize=10,
    seed=42,
    disp=True
)

# Best parameters
X1_opt, X2_opt, X3_opt, X4_opt = result.x
nse_opt = -result.fun

print("\n" + "=" * 60)
print("CALIBRATION COMPLETE")
print("=" * 60)
print(f"\nOptimized Parameters:")
print(f"  X1 (Production store):  {X1_opt:.2f} mm")
print(f"  X2 (Groundwater exch.): {X2_opt:.2f} mm")
print(f"  X3 (Routing store):     {X3_opt:.2f} mm")
print(f"  X4 (Time base):         {X4_opt:.2f} days")
print(f"\nPerformance:")
print(f"  NSE: {nse_opt:.3f}")

# Save parameters
params_df = pd.DataFrame({
    'parameter': ['X1', 'X2', 'X3', 'X4', 'NSE'],
    'value': [X1_opt, X2_opt, X3_opt, X4_opt, nse_opt]
})
params_df.to_csv("data/processed/calibrated_parameters.csv", index=False)

print(f"\n✓ Saved parameters to data/processed/calibrated_parameters.csv")