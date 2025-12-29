import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
import csv

# --- STEP 1: AUTO-DETECT HEADER ROW ---
filename = 'persons_of_concern.csv'
header_row_index = None

# Open file as plain text first to find where the data starts
with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        # We look for the line that contains "Year" and "Country"
        if "Year" in line and "Country" in line:
            header_row_index = i
            break

if header_row_index is None:
    print("CRITICAL ERROR: Could not find the header row in the CSV.")
    print("Here are the first 5 lines of your file to help debug:")
    for l in lines[:5]: print(l)
    exit()

print(f"SUCCESS: Found headers on line {header_row_index}. Loading data...")

# --- STEP 2: LOAD DATA CORRECTLY ---
df = pd.read_csv(filename, skiprows=header_row_index)

# --- STEP 3: FIND THE "REFUGEES" COLUMN ---
# Look for *any* column that looks like it contains refugee counts
possible_cols = [c for c in df.columns if 'Refugees' in c or 'REFUGEES' in c]

if not possible_cols:
    # Fallback: If no "Refugees" column, maybe it's named "Total displaced"?
    # Let's print all columns so you can see them if this fails
    print("ERROR: Still can't find a 'Refugees' column.")
    print("Available columns are:", df.columns.tolist())
    exit()

target_col = possible_cols[0] # Take the first matching column
print(f"Using column '{target_col}' for analysis.")

# --- STEP 4: CLEAN & ANALYZE ---
# Convert numbers (remove text/commas)
df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0)

# Group by Year
yearly_data = df.groupby('Year')[target_col].sum().reset_index()

# --- STEP 5: PREDICT & PLOT ---
X = yearly_data['Year'].values.reshape(-1, 1)
y = yearly_data[target_col].values

model = LinearRegression()
model.fit(X, y)

future_years = np.array([[2025], [2026], [2027]])
predictions = model.predict(future_years)

# Plot
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")
plt.plot(yearly_data['Year'], yearly_data[target_col], marker='o', label='Historical Data', color='#0072BC')
plt.plot(future_years, predictions, marker='x', linestyle='--', label='AI Forecast (2027)', color='red')

plt.title('Global Refugee Displacement (Auto-Detected)', fontsize=14)
plt.xlabel('Year')
plt.ylabel('Displaced People')
plt.legend()
plt.grid(True, alpha=0.3)

# Formatting Millions
current_values = plt.gca().get_yticks()
plt.gca().set_yticklabels(['{:,.0f}M'.format(x/1000000) for x in current_values])

plt.show()