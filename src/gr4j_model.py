import numpy as np
import pandas as pd

class GR4J:
    """
    GR4J hydrological model (4 parameters)
    
    Parameters:
    - X1: Production store capacity (mm)
    - X2: Groundwater exchange coefficient (mm)
    - X3: Routing store capacity (mm)
    - X4: Unit hydrograph time base (days)
    """
    
    def __init__(self, X1=350, X2=0, X3=90, X4=1.7):
        self.X1 = X1
        self.X2 = X2
        self.X3 = X3
        self.X4 = X4
        
    def run(self, precip, evap):
        """
        Run GR4J model
        
        Parameters:
        - precip: array of precipitation (mm/day)
        - evap: array of potential evapotranspiration (mm/day)
        
        Returns:
        - Q: simulated streamflow (mm/day)
        """
        
        n = len(precip)
        
        # Initialize states
        S = self.X1 * 0.5  # Production store (50% full)
        R = self.X3 * 0.5  # Routing store (50% full)
        
        # Initialize outputs
        Q = np.zeros(n)
        
        # Unit hydrograph ordinates
        UH1, UH2 = self._compute_unit_hydrographs()
        
        # Stores for routing
        UH1_stores = np.zeros(len(UH1))
        UH2_stores = np.zeros(len(UH2))
        
        for t in range(n):
            # Net precipitation and evaporation
            if precip[t] >= evap[t]:
                Pn = precip[t] - evap[t]
                En = 0
                
                # Calculate Ps (part going to production store)
                capacity_ratio = S / self.X1
                Ps = self.X1 * (1 - capacity_ratio**2) * np.tanh(Pn / self.X1)
                Ps = Ps / (1 + capacity_ratio * np.tanh(Pn / self.X1))
                
                Es = 0
            else:
                Pn = 0
                En = evap[t] - precip[t]
                
                # Calculate Es (evaporation from store)
                capacity_ratio = S / self.X1
                Es = S * (2 - capacity_ratio) * np.tanh(En / self.X1)
                Es = Es / (1 + (1 - capacity_ratio) * np.tanh(En / self.X1))
                
                Ps = 0
            
            # Update production store
            S = S - Es + Ps
            S = np.clip(S, 0, self.X1)
            
            # Percolation from production store
            perc_ratio = S / self.X1
            perc = S * (1 - (1 + (perc_ratio / 2.25)**4)**(-0.25))
            S = S - perc
            
            # Total water for routing
            Pr = perc + (precip[t] - Ps)
            
            # Split for routing (90% to UH1, 10% to UH2)
            Pr9 = 0.9 * Pr
            Pr1 = 0.1 * Pr
            
            # Route through unit hydrographs
            UH1_stores = np.roll(UH1_stores, 1)
            UH1_stores[0] = Pr9
            Q9 = np.sum(UH1_stores * UH1)
            
            UH2_stores = np.roll(UH2_stores, 1)
            UH2_stores[0] = Pr1
            Q1 = np.sum(UH2_stores * UH2)
            
            # Groundwater exchange
            F = self.X2 * (R / self.X3)**3.5
            
            # Update routing store
            R = max(0, R + Q9 + F)
            
            # Outflow from routing store
            routing_ratio = R / self.X3
            Qr = R * (1 - (1 + (routing_ratio / 2.25)**4)**(-0.25))
            R = R - Qr
            
            # Total flow
            Qd = max(0, Qr + Q1)
            Q[t] = Qd
        
        return Q
    
    def _compute_unit_hydrographs(self):
        """Compute unit hydrograph ordinates"""
        
        # UH1 ordinates (time base = X4)
        nUH1 = int(np.ceil(self.X4))
        UH1 = np.zeros(nUH1)
        
        for t in range(nUH1):
            if t < self.X4:
                UH1[t] = ((t + 1) / self.X4)**2.5
        
        # Normalize
        if nUH1 > 1:
            UH1[1:] = UH1[1:] - UH1[:-1]
        
        # UH2 ordinates (time base = 2*X4)
        nUH2 = int(np.ceil(2 * self.X4))
        UH2 = np.zeros(nUH2)
        
        for t in range(nUH2):
            if t < self.X4:
                UH2[t] = 0.5 * ((t + 1) / self.X4)**2.5
            elif t < 2 * self.X4:
                ratio = 2 - (t + 1) / self.X4
                if ratio > 0:  # Fix: avoid negative power
                    UH2[t] = 1 - 0.5 * ratio**2.5
                else:
                    UH2[t] = 1
        
        # Normalize
        if nUH2 > 1:
            UH2[1:] = UH2[1:] - UH2[:-1]
        
        return UH1, UH2


def calculate_nse(observed, simulated):
    """Calculate Nash-Sutcliffe Efficiency"""
    obs_mean = np.mean(observed)
    numerator = np.sum((observed - simulated)**2)
    denominator = np.sum((observed - obs_mean)**2)
    nse = 1 - (numerator / denominator)
    return nse


if __name__ == "__main__":
    print("Testing GR4J Model...")
    
    # Load calibration data
    df = pd.read_csv("data/processed/calibration_data.csv", parse_dates=['date'], index_col='date')
    
    # Prepare inputs
    precip = df['precipitation_mm'].values
    
    # Estimate potential evapotranspiration from temperature (simple method)
    temp = df['temperature_c'].values
    evap = 0.0023 * (temp + 17.8) * np.sqrt(np.abs(temp - (-5))) * 2.5  # Hargreaves simplified
    evap = np.maximum(evap, 0)
    
    # Observed streamflow (convert from cfs to mm/day)
    # Assuming basin area of 2000 km^2
    basin_area_km2 = 2000
    cfs_to_mm = 86400 / (basin_area_km2 * 1e6) * 0.0283168 * 1000
    obs_flow = df['streamflow_cfs'].values * cfs_to_mm
    
    # Run model with default parameters
    model = GR4J(X1=350, X2=0, X3=90, X4=1.7)
    sim_flow = model.run(precip, evap)
    
    # Calculate performance
    nse = calculate_nse(obs_flow, sim_flow)
    
    print(f"\n✓ Model ran successfully")
    print(f"  Timesteps: {len(sim_flow)}")
    print(f"  NSE: {nse:.3f}")
    print(f"  Mean observed flow: {obs_flow.mean():.2f} mm/day")
    print(f"  Mean simulated flow: {sim_flow.mean():.2f} mm/day")