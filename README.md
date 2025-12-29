# UNHCR Refugee Displacement Analysis 🌍

## Project Overview
This project analyzes over 10 years of **UNHCR refugee statistics** to identify global displacement trends. It utilizes **Python (Pandas)** for data cleaning and **Linear Regression (Scikit-Learn)** to forecast future displacement numbers for 2025-2027.

## Key Features
* **Automated ETL Pipeline:** Cleans raw UNHCR CSV data, handling missing values and inconsistent headers.
* **Statistical Forecasting:** Uses a linear regression model to predict future displacement trends.
* **Visualization:** Generates trend graphs to visualize the growth of displaced populations.

## How to Run
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the analysis script:
   ```bash
   python refugee_displacement_analysis.py
   ```

## Data Source
* **Source:** [UNHCR Refugee Data Finder](https://www.unhcr.org/refugee-statistics/download/)
* **Dataset:** Persons of Concern (Refugees, Asylum Seekers, IDPs).