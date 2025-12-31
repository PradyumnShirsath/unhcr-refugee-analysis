import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
DATA_FILE = 'persons_of_concern.csv'
OUTPUT_IMAGE = 'displacement_forecast_model.png'
SIMULATIONS = 2000          # Number of parallel universes to simulate
YEARS_TO_FORECAST = 5       # How far into the future (2025-2030)
CAPACITY_THRESHOLD = 1.10   # The "Crisis Line" (e.g., 10% increase overwhelms infrastructure)

def load_and_prep_data(filepath):
    """
    Robust data loader that finds columns automatically based on keywords.
    Handles different UNHCR CSV formats.
    """
    try:
        # 1. Read the CSV (skip first few rows if they contain metadata text)
        # We try reading normally first.
        df = pd.read_csv(filepath)
        
        # 2. Clean Column Names (remove spaces, make lowercase for searching)
        df.columns = df.columns.str.strip()
        
        print("   📂 analyzing CSV columns...")
        
        # 3. Smart Column Selector
        # Instead of hardcoding names, we look for keywords
        keywords = ['Refugees', 'Asylum', 'IDP', 'Stateless', 'Others']
        selected_cols = []
        
        for col in df.columns:
            # Check if this column matches any of our keywords
            for key in keywords:
                if key.lower() in col.lower():
                    selected_cols.append(col)
                    break
        
        if not selected_cols:
            print("   ⚠️ No displacement data columns found. Checking for header skip...")
            # Fallback: Try skipping the first few rows (common in UNHCR downloads)
            df = pd.read_csv(filepath, skiprows=3)
            df.columns = df.columns.str.strip()
            for col in df.columns:
                for key in keywords:
                    if key.lower() in col.lower():
                        selected_cols.append(col)
                        break

        print(f"   ✅ Found relevant columns: {selected_cols}")
        
        # 4. Process the Data
        # Ensure year is numeric
        if 'Year' not in df.columns:
             # Try to find a year column
            year_col = [c for c in df.columns if 'Year' in c or 'year' in c]
            if year_col:
                df.rename(columns={year_col[0]: 'Year'}, inplace=True)
            else:
                raise ValueError("Could not find a 'Year' column.")

        # Convert data to numeric (coercing errors) and fill NaNs
        for col in selected_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        # Sum rows to get 'Total_Displaced'
        df['Total_Displaced'] = df[selected_cols].sum(axis=1)
        
        # Group by Year
        yearly_data = df.groupby('Year')['Total_Displaced'].sum().reset_index()
        
        # Filter out years with 0 displacement (bad data)
        yearly_data = yearly_data[yearly_data['Total_Displaced'] > 0]
        
        return yearly_data

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        # Debugging aid: Print the columns found to help user
        try:
            temp = pd.read_csv(filepath)
            print(f"   (Debug) Columns in your CSV: {list(temp.columns)}")
        except:
            pass
        return None

def monte_carlo_simulation(historical_data):
    """
    Runs stochastic simulations based on historical volatility.
    Model: N(t+1) = N(t) * exp(mu + sigma * epsilon)
    """
    # 1. Calculate historical Log Returns (Growth Rates)
    historical_data['pct_change'] = np.log(historical_data['Total_Displaced'] / historical_data['Total_Displaced'].shift(1))
    
    # 2. Extract drift (mu) and volatility (sigma)
    mu = historical_data['pct_change'].mean()
    sigma = historical_data['pct_change'].std()
    
    last_year = historical_data['Year'].max()
    last_val = historical_data['Total_Displaced'].iloc[-1]
    
    # 3. Initialize Simulation Matrix [Simulations x Forecast Years]
    # We add +1 to include the starting year
    simulation_results = np.zeros((SIMULATIONS, YEARS_TO_FORECAST + 1))
    simulation_results[:, 0] = last_val
    
    # 4. Run the Random Walk
    for t in range(1, YEARS_TO_FORECAST + 1):
        # Generate random shocks for all 2000 simulations at once
        random_shocks = np.random.normal(0, 1, SIMULATIONS)
        
        # Update populations
        # New = Old * e^(drift + volatility * shock)
        simulation_results[:, t] = simulation_results[:, t-1] * np.exp(mu + sigma * random_shocks)
        
    forecast_years = np.arange(last_year, last_year + YEARS_TO_FORECAST + 1)
    return forecast_years, simulation_results

def plot_cone_of_uncertainty(history, years, simulations):
    """Generates the UN-style 'Early Warning' visualization."""
    plt.figure(figsize=(12, 7))
    
    # A. Plot Historical Data (The "Truth")
    plt.plot(history['Year'], history['Total_Displaced'] / 1e6, 
             color='black', linewidth=2, label='Historical Data (UNHCR)')
    
    # B. Calculate Confidence Intervals
    median_forecast = np.median(simulations, axis=0)
    upper_bound = np.percentile(simulations, 95, axis=0) # 95th percentile
    lower_bound = np.percentile(simulations, 5, axis=0)  # 5th percentile
    
    # C. Plot the "Cone of Uncertainty"
    plt.fill_between(years, lower_bound / 1e6, upper_bound / 1e6, 
                     color='#0072BC', alpha=0.3, label='90% Confidence Interval (Volatility)')
    
    plt.plot(years, median_forecast / 1e6, 
             color='#0072BC', linestyle='--', linewidth=2, label='Median Forecast')
    
    # D. Plot the "Capacity Threshold" (Hypothetical Crisis Line)
    # We set this at 10% above current levels just to demonstrate the concept
    capacity_limit = history['Total_Displaced'].iloc[-1] * CAPACITY_THRESHOLD / 1e6
    plt.axhline(y=capacity_limit, color='red', linestyle=':', linewidth=2, label='Host Infrastructure Capacity Limit')

    # Styling
    plt.title('Project Rescue: Stochastic Forecast of Global Displacement (2025-2030)', fontsize=14, fontweight='bold')
    plt.ylabel('Displaced Population (Millions)', fontsize=12)
    plt.xlabel('Year', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Save
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"✅ Simulation Complete. Forecast graph saved to {OUTPUT_IMAGE}")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("🔹 Starting Project Rescue Analysis...")
    
    # 1. Load Data
    data = load_and_prep_data(DATA_FILE)
    
    if data is not None:
        print(f"   Loaded {len(data)} years of historical data.")
        
        # 2. Run Simulations
        print(f"   Running {SIMULATIONS} Monte Carlo scenarios...")
        f_years, f_sims = monte_carlo_simulation(data)
        
        # 3. Generate Visualization
        plot_cone_of_uncertainty(data, f_years, f_sims)
        
    else:
        print("❌ Failed to load data. Check CSV filename.")