# sim/model_parameters_bme.py

# --- Core Token Supply & Emission Parameters (BME Based) ---
BME_MAX_SUPPLY_DRIA = 1_000_000_000  # Same as Dria cap
BME_INITIAL_CIRCULATING_SUPPLY = 1_000_000  # Example: small initial supply

# --- BME Emission Parameters ---
BME_FIXED_EMISSION_PER_MONTH = 2_000_000  # Example: 2M DRIA emitted per month as node rewards (tunable)
BME_EMISSION_PERIOD_MONTHS = 120  # 10 years

# --- Burn Mechanism ---
BME_BURN_PERCENT_OF_USD_INCOME = 1.0  # 100% of USD income is used to buy and burn DRIA
BME_BURN_PERCENT_OF_DRIA_FEES = 0.5   # 50% of DRIA service fees are burned (tunable)

# --- Node & Demand Parameters (from Dria utility narrative) ---
BME_INITIAL_NODE_COUNT = 30000
BME_AVG_NODE_OPERATING_COST_USD_MONTHLY = 50
BME_MIN_MONTHLY_PROFIT_USD_FOR_GROWTH = 100
BME_MAX_MONTHLY_NODE_GROWTH_RATE = 0.2
BME_MAX_MONTHLY_NODE_DECLINE_RATE = 0.1
BME_NODE_COUNT_ADJUSTMENT_LAG_MONTHS = 3

# --- Demand-Side Drivers ---
BME_INITIAL_USD_CREDIT_PURCHASE_PER_MONTH = 100_000
BME_INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH = 200_000
BME_USD_DEMAND_GROWTH_RATE_MONTHLY = 0.01
BME_DRIA_DEMAND_GROWTH_RATE_MONTHLY = 0.01

# --- Price Simulation ---
BME_INITIAL_DRIA_PRICE_USD = 0.50
BME_PRICE_ADJUSTMENT_SENSITIVITY = 0.01
BME_MIN_DRIA_PRICE_USD = 0.001

# --- Simulation Control ---
BME_SIMULATION_YEARS = 10
BME_SIMULATION_TIMESTEP_MONTHS = 1
BME_TOTAL_TIMESTEPS = BME_SIMULATION_YEARS * 12

print("BME model parameters loaded.") 