import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score
import pickle

print("=" * 60)
print("TRAINING ML MODEL (XGBoost)")
print("=" * 60)

# Load calibration data
df_cal = pd.read_csv("data/processed/calibration_data.csv", parse_dates=['date'], index_col='date')

# Prepare features for ML
features = ['precipitation_mm', 'temperature_c', 'precip_7day', 'temp_7day']
X_train = df_cal[features].values

# Target: streamflow
basin_area_km2 = 2000
cfs_to_mm = 86400 / (basin_area_km2 * 1e6) * 0.0283168 * 1000
y_train = df_cal['streamflow_cfs'].values * cfs_to_mm

print(f"\nTraining data:")
print(f"  Samples: {len(X_train)}")
print(f"  Features: {features}")

# Train XGBoost model
print("\nTraining XGBoost...")

model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)

model.fit(X_train, y_train)

# Predictions on training data
y_pred_train = model.predict(X_train)

# Calculate metrics
rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
r2_train = r2_score(y_train, y_pred_train)

print(f"\nTraining Performance:")
print(f"  RMSE: {rmse_train:.3f} mm/day")
print(f"  R²:   {r2_train:.3f}")

# Validate on validation set
df_val = pd.read_csv("data/processed/validation_data.csv", parse_dates=['date'], index_col='date')

X_val = df_val[features].values
y_val = df_val['streamflow_cfs'].values * cfs_to_mm

y_pred_val = model.predict(X_val)

rmse_val = np.sqrt(mean_squared_error(y_val, y_pred_val))
r2_val = r2_score(y_val, y_pred_val)

print(f"\nValidation Performance:")
print(f"  RMSE: {rmse_val:.3f} mm/day")
print(f"  R²:   {r2_val:.3f}")

# Feature importance
importance = model.feature_importances_
print(f"\nFeature Importance:")
for feat, imp in zip(features, importance):
    print(f"  {feat:20s}: {imp:.3f}")

# Save model
with open('models/xgboost_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print(f"\n✓ Saved model to models/xgboost_model.pkl")

# Save predictions
results = pd.DataFrame({
    'date': df_val.index,
    'observed': y_val,
    'predicted_ml': y_pred_val
})
results.to_csv('data/processed/ml_predictions.csv', index=False)

print(f"✓ Saved predictions to data/processed/ml_predictions.csv")
print("\n" + "=" * 60)
print("ML MODEL TRAINING COMPLETE")
print("=" * 60)