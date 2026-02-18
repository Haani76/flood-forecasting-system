# 🌊 Basin-Scale Hydrological Simulation and Validation System

A comprehensive hydrological modeling framework integrating physics-based (GR4J) and machine learning (XGBoost) approaches for streamflow simulation, with NetCDF climate data processing capabilities.

---

## 📋 Project Overview

### Objective
Develop and validate coupled hydrological models for daily streamflow simulation, demonstrating model calibration, uncertainty assessment, and climate data processing workflows applicable to water resources management.

### Scope
This project implements a **simulation and validation framework** (not real-time forecasting) to:
- Calibrate conceptual rainfall-runoff models against historical observations
- Compare physics-based and data-driven modeling approaches
- Process gridded climate data in NetCDF format
- Provide interactive visualization for decision support

---

## 🎯 Study Area

**Basin Characteristics:**
- **Basin Name:** Synthetic test basin (representative of semi-arid climate)
- **Drainage Area:** 2,000 km²
- **Climate Type:** Semi-arid with seasonal precipitation
- **Elevation Range:** Not specified (synthetic data)
- **Study Period:** 2005-2014 (10 years)
  - Calibration: 2005-2011 (7 years)
  - Validation: 2012-2014 (3 years)

**Note:** This project uses synthetic data for demonstration purposes. The methodology is transferable to real basins with observed data.

---

## 🔬 Methodology

### 1. Hydrological Model: GR4J

**Model Description:**
GR4J (Génie Rural à 4 paramètres Journalier) is a lumped, conceptual rainfall-runoff model developed by CEMAGREF (now INRAE), France.

**Model Structure:**
```
Precipitation (P) + Evapotranspiration (E)
          ↓
  Production Store (X1)
          ↓
    Percolation
          ↓
  ┌───────┴────────┐
  ↓                ↓
Unit Hydrograph  Routing Store (X3)
  (90%)            (10%)
  ↓                ↓
  └────→ Streamflow ←────┘
```

**Parameters:**

| Parameter | Description | Units | Typical Range | Calibrated Value |
|-----------|-------------|-------|---------------|------------------|
| **X1** | Production store capacity | mm | 100-1200 | 1199.90 |
| **X2** | Groundwater exchange coefficient | mm/day | -5 to +3 | -4.98 |
| **X3** | Routing store capacity | mm | 20-300 | 131.30 |
| **X4** | Unit hydrograph time base | days | 1.1-2.9 | 2.00 |

**Model Physics:**
- **Production Store (X1):** Represents soil moisture accounting with non-linear storage-discharge relationship
- **Groundwater Exchange (X2):** Simulates inter-basin transfers or deep percolation (positive = loss, negative = gain)
- **Routing Store (X3):** Handles slow groundwater/baseflow component
- **Unit Hydrograph (X4):** Routes surface runoff with time lag using two unit hydrographs (UH1: 90%, UH2: 10%)

---

### 2. Machine Learning Model: XGBoost

**Model Type:** Gradient Boosting Regression Trees

**Input Features:**
- Precipitation (mm/day)
- Temperature (°C)
- 7-day antecedent precipitation (mm)
- 7-day average temperature (°C)

**Hyperparameters:**
- Number of estimators: 100
- Maximum depth: 6
- Learning rate: 0.1
- Objective: Minimize squared error

**Feature Importance:**
| Feature | Importance |
|---------|-----------|
| 7-day avg temperature | 0.861 |
| Temperature | 0.051 |
| Precipitation | 0.044 |
| 7-day antecedent precip | 0.044 |

---

## 📊 Input/Output Parameters

### Inputs

**Meteorological Forcing:**
- **Precipitation** (mm/day): Daily rainfall depth
- **Temperature** (°C): Daily mean air temperature
- **Potential Evapotranspiration** (mm/day): Calculated from temperature using simplified Hargreaves equation

**Basin Attributes:**
- Drainage area: 2,000 km²
- (In real applications: soil type, land cover, elevation, slope)

### Outputs

**Streamflow:**
- **Unit:** mm/day (basin average) and cubic feet per second (cfs)
- **Temporal Resolution:** Daily
- **Conversion:** cfs to mm/day using basin area

**Performance Metrics:**
- Nash-Sutcliffe Efficiency (NSE)
- Root Mean Square Error (RMSE)
- Bias (mean error)
- R² (coefficient of determination)

---

## 🔧 Model Calibration & Validation

### Calibration Process

**Algorithm:** Differential Evolution (Global Optimization)
- **Objective Function:** Maximize Nash-Sutcliffe Efficiency (NSE)
- **Parameter Bounds:** See table above
- **Population Size:** 10
- **Iterations:** 50
- **Seed:** 42 (for reproducibility)

**Calibration Period:** 2005-2011 (2,550 days)

**Optimization Progress:**
```
Initial NSE: -128.636 (default parameters)
Final NSE:   -0.074 (optimized parameters)
```

### Validation Process

**Validation Period:** 2012-2014 (1,096 days)

**Independent Testing:** Model parameters fixed from calibration; no re-tuning on validation data.

---

## 📈 Model Performance

### GR4J Performance

| Metric | Calibration (2005-2011) | Validation (2012-2014) |
|--------|-------------------------|------------------------|
| **NSE** | -0.074 | -0.185 |
| **RMSE** | N/A | 0.466 mm/day |
| **Bias** | N/A | -0.006 mm/day |

### XGBoost Performance

| Metric | Training | Validation |
|--------|----------|------------|
| **RMSE** | 0.162 mm/day | 0.263 mm/day |
| **R²** | 0.850 | 0.622 |

**Interpretation:**
- XGBoost outperforms GR4J on this synthetic dataset (R² = 0.622 vs NSE = -0.185)
- Negative NSE for GR4J indicates synthetic data does not perfectly match model assumptions
- With real basin data, GR4J typically achieves NSE > 0.6-0.8
- Low bias (-0.006 mm/day) indicates minimal systematic error

---

## 🗂️ NetCDF Data Processing


### Operations Performed:
1. **NetCDF Creation:** Generated gridded climate data (10×10 spatial grid, 1096 timesteps)
2. **Metadata Handling:** CF-1.8 convention compliance
3. **Spatial Operations:**
   - Point extraction (nearest grid cell to basin centroid)
   - Spatial averaging across grid cells
   - Subsetting by lat/lon bounds
4. **Temporal Operations:**
   - Daily to monthly aggregation
   - Climatology calculation (monthly averages)
   - Anomaly detection (deviations from climatology)
5. **Format Conversion:** NetCDF ↔ CSV for interoperability

**Tools Used:**
- `xarray`: High-level NetCDF operations
- `netCDF4`: Low-level file I/O
- Demonstrated skills transferable to ERA5, CHIRPS, CMIP6 datasets

---

## 🛠️ Tech Stack

**Programming & Libraries:**
- Python 3.9+
- NumPy, Pandas (data processing)
- SciPy (optimization algorithms)
- xarray, netCDF4 (geospatial data)

**Machine Learning:**
- XGBoost 2.0+
- scikit-learn (preprocessing, metrics)

**Visualization:**
- Matplotlib (static plots)
- Plotly (interactive charts)
- Streamlit (web dashboard)

**Version Control:**
- Git/GitHub

---

## 📁 Project Structure
```
Basin-Scale Hydrological Simulation and Validation System/
├── data/
│   ├── raw/
│   │   ├── hydro_data.csv              # Synthetic streamflow & climate
│   │   └── climate_data.nc             # NetCDF gridded data
│   └── processed/
│       ├── calibration_data.csv        # Training dataset
│       ├── validation_data.csv         # Test dataset
│       ├── calibrated_parameters.csv   # Optimized GR4J params
│       ├── validation_results.csv      # GR4J outputs
│       ├── ml_predictions.csv          # XGBoost outputs
│       └── climate_monthly.nc          # Aggregated NetCDF
├── src/
│   ├── download_data.py                # Data generation
│   ├── process_data.py                 # Preprocessing pipeline
│   ├── gr4j_model.py                   # GR4J implementation
│   ├── calibrate_model.py              # Parameter optimization
│   ├── validate_model.py               # Model testing
│   ├── ml_model.py                     # XGBoost training
│   └── netcdf_processor.py             # NetCDF workflows
├── models/
│   └── xgboost_model.pkl               # Trained ML model
├── dashboard/
│   └── app.py                          # Streamlit web app
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/Haani76/basin-scale-hydrological-simulation.git
cd https://github.com/Haani76/basin-scale-hydrological-simulation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Data
```bash
python src/download_data.py
python src/process_data.py
```

### 3. Run Hydrological Model
```bash
python src/calibrate_model.py  # Optimize parameters
python src/validate_model.py   # Test on validation period
```

### 4. Train ML Model
```bash
python src/ml_model.py
```

### 5. Process NetCDF Data
```bash
python src/netcdf_processor.py
```

### 6. Launch Dashboard
```bash
streamlit run dashboard/app.py
```
**Live Demo:** [Your Streamlit URL]

---

## ⚠️ Limitations

### Current Limitations:

1. **Synthetic Data:** Uses generated data for demonstration; not calibrated to real basin
2. **Lumped Model:** GR4J treats basin as single unit (no spatial distribution)
3. **No Real-Time Capability:** Simulation only; does not ingest live forecasts
4. **Single Basin:** Methodology not tested across multiple basins
5. **Simplified PET:** Uses temperature-based evapotranspiration (not full Penman-Monteith)
6. **No Data Assimilation:** Does not update states with real-time observations
7. **Model Uncertainty:** No ensemble or probabilistic forecasts

### Data Limitations:

- Synthetic precipitation/temperature lack realistic spatial variability
- No snow/glacier melt component
- Assumes stationary climate (no trends)

---

## 🔬 Applications in Water Resources Engineering

This framework is applicable to:

✅ **Water Availability Assessment**
- Estimate mean annual runoff and seasonal patterns
- Identify renewable water resources for allocation

✅ **Low-Flow Analysis**
- Calculate 7-day low flows (Q7) for environmental flow requirements
- Drought frequency analysis

✅ **Climate Change Impact Studies**
- Modify inputs with GCM projections (temperature/precipitation scenarios)
- Assess future water scarcity

✅ **Ungauged Basin Prediction**
- Transfer calibrated parameters to similar basins
- Regionalization studies

✅ **Operational Hydrology Training**
- Educational tool for understanding rainfall-runoff processes
- Benchmarking ML vs. physics-based models

---

## 📚 Skills Demonstrated

✅ Conceptual hydrological modeling (GR4J)  
✅ Parameter calibration & uncertainty assessment  
✅ Machine learning for time-series prediction  
✅ NetCDF/gridded climate data processing  
✅ Model validation & performance metrics  
✅ Scientific Python programming  
✅ Data visualization & dashboard development  
✅ Version control & reproducible research  

---

## 🔮 Future Enhancements

**Planned Improvements:**

1. **Real Basin Integration**
   - USGS/GRDC observed streamflow data
   - CAMELS basin attributes dataset

2. **Real-Time Forecasting**
   - Ingest GFS/ECMWF weather forecasts
   - 7-10 day ahead streamflow predictions

3. **Ensemble Uncertainty Quantification**
   - Monte Carlo parameter sampling
   - Probabilistic forecast bands

4. **Deep Learning**
   - LSTM recurrent neural network
   - Sequence-to-sequence architecture

5. **Operational Deployment**
   - Docker containerization
   - REST API for external access
   - Automated daily updates

6. **Advanced Features**
   - Data assimilation (Kalman filter)
   - Multi-objective calibration (NSE + volume error + peak timing)
   - Spatial distribution (semi-distributed model)

---

## 📖 References

**GR4J Model:**
- Perrin, C., Michel, C., & Andréassian, V. (2003). *Improvement of a parsimonious model for streamflow simulation.* Journal of Hydrology, 279(1-4), 275-289.

**Model Evaluation:**
- Nash, J. E., & Sutcliffe, J. V. (1970). *River flow forecasting through conceptual models.* Journal of Hydrology, 10(3), 282-290.

**Machine Learning in Hydrology:**
- Kratzert, F., et al. (2019). *Towards learning universal, regional, and local hydrological behaviors via machine learning.* Water Resources Research, 55(12), 5364-5377.

---

## 📧 Contact

**Haani Shafiq Siddiqui**  
GitHub: [@Haani76](https://github.com/Haani76)  
Project: [flood-forecasting-system](https://github.com/Haani76/flood-forecasting-system)  
Live Demo: [Streamlit Dashboard](https://flood-forecasting-system-guj7kmtw4r6zqxndspxue8.streamlit.app/)

---

## 📄 License

MIT License - Free to use for educational and research purposes.

---

**Note:** This is a demonstration/portfolio project. For operational water resources applications, use validated basin data and conduct thorough uncertainty analysis.