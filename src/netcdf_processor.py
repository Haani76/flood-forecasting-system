import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

print("=" * 60)
print("NETCDF DATA PROCESSING MODULE")
print("=" * 60)

# Create a sample NetCDF file with climate data
def create_sample_netcdf():
    """
    Create a sample NetCDF file with gridded precipitation and temperature
    This demonstrates NetCDF handling skills
    """
    
    print("\nCreating sample NetCDF dataset...")
    
    # Create spatial grid (10x10 grid covering basin area)
    lat = np.linspace(31.5, 33.0, 10)
    lon = np.linspace(-111.5, -110.0, 10)
    
    # Create time dimension (daily for 2012-2014)
    time = pd.date_range('2012-01-01', '2014-12-31', freq='D')
    
    # Generate realistic gridded data
    np.random.seed(42)
    
    # Precipitation (mm/day) - 3D array (time, lat, lon)
    precip = np.random.gamma(2, 2, size=(len(time), len(lat), len(lon)))
    precip = np.clip(precip, 0, 100)
    
    # Temperature (Celsius) - 3D array (time, lat, lon)
    temp_base = 15
    temp_seasonal = 10 * np.sin(2 * np.pi * np.arange(len(time)) / 365.25)
    temp = temp_base + temp_seasonal[:, np.newaxis, np.newaxis] + np.random.normal(0, 3, size=(len(time), len(lat), len(lon)))
    
    # Create xarray Dataset
    ds = xr.Dataset(
        {
            'precipitation': (['time', 'lat', 'lon'], precip, {
                'units': 'mm/day',
                'long_name': 'Daily precipitation',
                'standard_name': 'precipitation_amount'
            }),
            'temperature': (['time', 'lat', 'lon'], temp, {
                'units': 'degrees_C',
                'long_name': 'Daily mean temperature',
                'standard_name': 'air_temperature'
            })
        },
        coords={
            'time': time,
            'lat': lat,
            'lon': lon
        },
        attrs={
            'title': 'Gridded Climate Data for Hydrological Modeling',
            'institution': 'Flood Forecasting System',
            'source': 'Synthetic data for demonstration',
            'history': 'Created for NetCDF processing demonstration',
            'conventions': 'CF-1.8'
        }
    )
    
    # Save to NetCDF
    Path('data/raw').mkdir(parents=True, exist_ok=True)
    nc_file = 'data/raw/climate_data.nc'
    ds.to_netcdf(nc_file)
    
    print(f"✓ Created NetCDF file: {nc_file}")
    print(f"  Dimensions: {dict(ds.dims)}")
    print(f"  Variables: {list(ds.data_vars)}")
    print(f"  Time range: {ds.time.min().values} to {ds.time.max().values}")
    
    return ds

def extract_basin_average(nc_file, basin_lat=32.22, basin_lon=-110.97):
    """
    Extract basin-averaged time series from NetCDF grid
    Demonstrates spatial averaging and NetCDF operations
    """
    
    print(f"\nExtracting basin average from NetCDF...")
    
    # Open NetCDF file
    ds = xr.open_dataset(nc_file)
    
    print(f"  Loaded dataset: {nc_file}")
    print(f"  Grid size: {len(ds.lat)} x {len(ds.lon)}")
    print(f"  Timesteps: {len(ds.time)}")
    
    # Select nearest grid point to basin center
    basin_point = ds.sel(lat=basin_lat, lon=basin_lon, method='nearest')
    
    # Extract time series
    precip_ts = basin_point['precipitation'].values
    temp_ts = basin_point['temperature'].values
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': ds.time.values,
        'precip_netcdf': precip_ts,
        'temp_netcdf': temp_ts
    })
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    
    # Calculate spatial statistics (demonstrate NetCDF processing)
    precip_spatial_mean = ds['precipitation'].mean(dim=['lat', 'lon']).values
    precip_spatial_std = ds['precipitation'].std(dim=['lat', 'lon']).values
    
    df['precip_spatial_mean'] = precip_spatial_mean
    df['precip_spatial_std'] = precip_spatial_std
    
    print(f"\n✓ Extracted basin time series")
    print(f"  Records: {len(df)}")
    print(f"  Mean precipitation: {df['precip_netcdf'].mean():.2f} mm/day")
    print(f"  Mean temperature: {df['temp_netcdf'].mean():.2f} °C")
    
    ds.close()
    
    return df

def demonstrate_netcdf_operations(ds):
    """
    Demonstrate advanced NetCDF operations
    """
    
    print("\n" + "=" * 60)
    print("ADVANCED NETCDF OPERATIONS")
    print("=" * 60)
    
    # 1. Temporal aggregation
    monthly_precip = ds['precipitation'].resample(time='1M').sum()
    print(f"\n1. Temporal Aggregation:")
    print(f"   Daily → Monthly precipitation")
    print(f"   Shape: {monthly_precip.shape}")
    
    # 2. Spatial subsetting
    subset = ds.sel(lat=slice(32, 33), lon=slice(-111, -110.5))
    print(f"\n2. Spatial Subsetting:")
    print(f"   Original: {ds.dims}")
    print(f"   Subset: {subset.dims}")
    
    # 3. Calculate climatology
    climatology = ds.groupby('time.month').mean('time')
    print(f"\n3. Climatology (monthly averages):")
    print(f"   Months: {len(climatology.month)}")
    
    # 4. Anomalies
    anomalies = ds.groupby('time.month') - climatology
    print(f"\n4. Anomalies calculated")
    print(f"   Mean anomaly: {anomalies['precipitation'].mean().values:.2f} mm/day")
    
    # Save processed NetCDF
    output_file = 'data/processed/climate_monthly.nc'
    monthly_precip.to_netcdf(output_file)
    print(f"\n✓ Saved processed NetCDF: {output_file}")
    
    return monthly_precip

def netcdf_metadata_report(nc_file):
    """
    Generate metadata report from NetCDF file
    """
    
    print("\n" + "=" * 60)
    print("NETCDF METADATA REPORT")
    print("=" * 60)
    
    ds = xr.open_dataset(nc_file)
    
    print(f"\nFile: {nc_file}")
    print(f"\nDimensions:")
    for dim, size in ds.dims.items():
        print(f"  {dim}: {size}")
    
    print(f"\nCoordinates:")
    for coord in ds.coords:
        print(f"  {coord}: {ds.coords[coord].shape}")
    
    print(f"\nVariables:")
    for var in ds.data_vars:
        print(f"  {var}:")
        print(f"    Shape: {ds[var].shape}")
        print(f"    Units: {ds[var].attrs.get('units', 'N/A')}")
        print(f"    Long name: {ds[var].attrs.get('long_name', 'N/A')}")
    
    print(f"\nGlobal Attributes:")
    for attr, value in ds.attrs.items():
        print(f"  {attr}: {value}")
    
    ds.close()

if __name__ == "__main__":
    
    # Step 1: Create sample NetCDF
    ds = create_sample_netcdf()
    
    # Step 2: Extract basin average
    df = extract_basin_average('data/raw/climate_data.nc')
    
    # Step 3: Save extracted data
    output_file = 'data/processed/netcdf_extracted_data.csv'
    df.to_csv(output_file)
    print(f"\n✓ Saved extracted data: {output_file}")
    
    # Step 4: Demonstrate advanced operations
    monthly_data = demonstrate_netcdf_operations(ds)
    
    # Step 5: Generate metadata report
    netcdf_metadata_report('data/raw/climate_data.nc')
    
    print("\n" + "=" * 60)
    print("NETCDF PROCESSING COMPLETE!")
    print("=" * 60)
    print("\nThis demonstrates:")
    print("  ✓ Creating NetCDF files with xarray")
    print("  ✓ Reading and parsing NetCDF data")
    print("  ✓ Spatial subsetting and point extraction")
    print("  ✓ Temporal aggregation (daily → monthly)")
    print("  ✓ Climatology and anomaly calculations")
    print("  ✓ Metadata handling and CF conventions")